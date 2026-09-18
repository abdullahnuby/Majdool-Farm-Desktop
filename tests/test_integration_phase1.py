"""كل اختبار هنا بيعيد عطل اتأكد منه فعلياً قبل الإصلاح. لو العطل رجع، الاختبار يفشل."""
from datetime import date
import pytest
from sqlalchemy import text
from app.database.db import engine, SessionLocal, backup_database, restore_database
from app.domain.models import CropMovement, InventoryMovement, Customer
from app.infrastructure.repositories import FarmRepository
from app.infrastructure.crop_repository import CropRepository
from app.infrastructure.sales_repository import SalesRepository
from app.infrastructure.purchase_repository import PurchaseRepository
from app.infrastructure.inventory_repository import InventoryRepository
from app.infrastructure.hr_repository import HRRepository
from tests.helpers import *


# ---- 1) المفاتيح الأجنبية مفعّلة ------------------------------------------------
def test_foreign_keys_pragma_is_on():
    with engine.connect() as c:
        assert c.execute(text("PRAGMA foreign_keys")).scalar() == 1


def test_database_backup_and_restore_round_trip(tmp_path):
    repo = SalesRepository()
    customer = repo.add_customer("C-RESTORE", "عميل نسخة احتياطية")
    backup_file = tmp_path / "medjool_backup.db"
    restored_file = tmp_path / "medjool_restored.db"

    backup_database(backup_file)
    restore_database(backup_file, restored_file)

    with SessionLocal() as s:
        assert s.query(Customer).filter_by(id=customer.id).count() == 1

    with sqlite3.connect(restored_file) as conn:
        assert conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0] == 1


def test_batch_on_missing_block_is_rejected():
    season = CropRepository().add_season("م")
    with pytest.raises(ValueError, match="البلوك غير موجود"):
        CropRepository().add_batch(season.id, 9999, 100)


def test_sales_line_on_missing_batch_is_rejected():
    inv = draft_invoice(make_customer().id)
    with pytest.raises(ValueError, match="دفعة الحصاد غير موجودة"):
        SalesRepository().add_line(inv.id, 9999, "أولى", 10, 5)


def test_raw_fk_violation_is_blocked_by_database():
    from sqlalchemy.exc import IntegrityError
    with pytest.raises(IntegrityError):
        with SessionLocal() as s:
            s.add(CropMovement(batch_id=424242, movement_type="إضافة", quantity_kg=1))
            s.commit()


# ---- 2) تأكيد البيع بيجمّع الكميات لنفس الدفعة -------------------------------------
def test_confirm_blocks_oversell_across_two_lines_same_batch():
    batch = make_batch(1000)
    repo = SalesRepository()
    inv = draft_invoice(make_customer().id)
    repo.add_line(inv.id, batch.id, "أولى", 600, 10)
    # كان بيتقبل 800+800 على 1000؛ دلوقتي البند التاني نفسه بيترفض
    with pytest.raises(ValueError, match="الرصيد غير كافٍ"):
        repo.add_line(inv.id, batch.id, "أولى", 500, 10)
    assert CropRepository().ready_kg(batch.id) == 1000  # مفيش حاجة اتخصمت من مسودة


def test_confirm_checks_aggregate_even_if_lines_bypass_add_line():
    """لو بنود اتضافت بأي طريقة، التأكيد نفسه بيفحص المجموع."""
    from app.domain.models import SalesInvoiceLine
    batch = make_batch(1000)
    inv = draft_invoice(make_customer().id)
    with SessionLocal() as s:
        for _ in range(2):
            s.add(SalesInvoiceLine(invoice_id=inv.id, batch_id=batch.id, grade="أولى",
                                   quantity_kg=800, unit_price=1, line_total=800))
        s.commit()
    with pytest.raises(ValueError, match="الرصيد غير كافٍ"):
        SalesRepository().confirm(inv.id)
    assert CropRepository().ready_kg(batch.id) == 1000


# ---- 3) الفاتورة المؤكدة مقفولة ----------------------------------------------------
def test_confirmed_invoice_rejects_new_lines():
    batch = make_batch(1000)
    repo = SalesRepository()
    inv = draft_invoice(make_customer().id)
    repo.add_line(inv.id, batch.id, "أولى", 100, 10)
    repo.confirm(inv.id)
    with pytest.raises(ValueError, match="لا يمكن تعديل فاتورة مؤكدة"):
        repo.add_line(inv.id, batch.id, "أولى", 50, 10)
    assert [i.total for i in repo.invoices()] == [1000]


def test_confirm_is_idempotent_no_double_deduction():
    batch = make_batch(1000)
    repo = SalesRepository()
    inv = draft_invoice(make_customer().id)
    repo.add_line(inv.id, batch.id, "أولى", 100, 10)
    repo.confirm(inv.id); repo.confirm(inv.id)
    assert CropRepository().ready_kg(batch.id) == 900


def test_cancel_confirmed_invoice_restores_stock_with_reversal_movement():
    batch = make_batch(1000)
    repo = SalesRepository()
    inv = draft_invoice(make_customer().id)
    repo.add_line(inv.id, batch.id, "أولى", 100, 10)
    repo.confirm(inv.id)
    repo.cancel(inv.id)
    assert CropRepository().ready_kg(batch.id) == 1000
    with SessionLocal() as s:  # الحركة الأصلية لسه موجودة (مفيش حذف)
        types = sorted(m.movement_type for m in s.query(CropMovement).all())
    assert types == ["إرجاع", "استلام_حصاد", "صرف_للبيع"]
    with pytest.raises(ValueError, match="ملغاة"):
        repo.confirm(inv.id)


# ---- 4) الخصم لا يتعدى الإجمالي -----------------------------------------------------
def test_discount_larger_than_subtotal_blocked_on_confirm():
    batch = make_batch(1000)
    repo = SalesRepository()
    inv = draft_invoice(make_customer().id, discount=500)
    repo.add_line(inv.id, batch.id, "أولى", 10, 1)  # إجمالي 10 والخصم 500
    with pytest.raises(ValueError, match="الخصم"):
        repo.confirm(inv.id)
    assert CropRepository().ready_kg(batch.id) == 1000


def test_negative_discount_or_tax_rejected():
    cid = make_customer().id
    with pytest.raises(ValueError):
        draft_invoice(cid, discount=-1)
    with pytest.raises(ValueError):
        draft_invoice(cid, tax=-1)


# ---- 5) الفرز والتعبئة لا يتجاوزوا كمية الحصاد ---------------------------------------
def test_sorting_cannot_exceed_harvest_cumulatively():
    batch = make_batch(1000)
    crop = CropRepository()
    crop.add_sort_line(batch.id, "أولى", 700)
    with pytest.raises(ValueError, match="مجموع الفرز"):
        crop.add_sort_line(batch.id, "ثانية", 400)  # 700+400 > 1000
    crop.add_sort_line(batch.id, "ثانية", 300)       # 1000 بالظبط مسموح


def test_packing_cannot_exceed_harvest_cumulatively():
    batch = make_batch(1000)
    crop = CropRepository()
    crop.add_packing(batch.id, "كرتونة", 5, 150)  # 750 كجم
    with pytest.raises(ValueError, match="مجموع التعبئة"):
        crop.add_packing(batch.id, "كرتونة", 5, 60)   # 750+300 > 1000


# ---- 6) الرواتب والسلف -------------------------------------------------------------
def test_advance_is_actually_recovered_and_not_deducted_again():
    emp = make_employee(monthly=5000)
    hr = HRRepository()
    hr.add_advance(emp.id, 2000)
    p1 = hr.create_payroll(emp.id, "2026-09")
    assert (p1.advances, p1.net_amount) == (2000, 3000)
    p2 = hr.create_payroll(emp.id, "2026-10")   # كان بيخصم نفس السلفة تاني
    assert (p2.advances, p2.net_amount) == (0, 5000)


def test_advance_larger_than_salary_is_recovered_in_installments():
    emp = make_employee(monthly=1000)
    hr = HRRepository()
    hr.add_advance(emp.id, 2500)
    a = hr.create_payroll(emp.id, "2026-09")
    b = hr.create_payroll(emp.id, "2026-10")
    c = hr.create_payroll(emp.id, "2026-11")
    assert [x.advances for x in (a, b, c)] == [1000, 1000, 500]
    assert [x.net_amount for x in (a, b, c)] == [0, 0, 500]


def test_duplicate_payroll_for_same_period_rejected():
    emp = make_employee(monthly=3000)
    hr = HRRepository()
    hr.create_payroll(emp.id, "2026-09")
    with pytest.raises(ValueError, match="بالفعل"):
        hr.create_payroll(emp.id, "2026-09")


def test_daily_worker_paid_by_attendance_days():
    emp = make_employee(daily=200)   # مرتب شهري = 0 → كان صافيه صفر
    hr = HRRepository()
    for day in (1, 2, 3):
        hr.mark_attendance(emp.id, date(2026, 9, day))
    hr.mark_attendance(emp.id, date(2026, 8, 31))  # خارج الفترة
    p = hr.create_payroll(emp.id, "2026-09")
    assert (p.base_amount, p.net_amount) == (600, 600)


def test_payroll_rejects_bad_period():
    emp = make_employee(monthly=1000)
    with pytest.raises(ValueError, match="YYYY-MM"):
        HRRepository().create_payroll(emp.id, "سبتمبر")


# ---- 7) السداد والتحصيل ------------------------------------------------------------
def _confirmed_purchase(total_qty=4, price=100):
    sup = make_supplier()
    repo = PurchaseRepository()
    inv = repo.create_invoice(sup.id)
    repo.add_line(inv.id, "سماد", total_qty, price)
    repo.confirm(inv.id)
    return sup, inv


def test_supplier_payment_updates_paid_and_is_capped():
    sup, inv = _confirmed_purchase()          # 400
    repo = PurchaseRepository()
    repo.pay(sup.id, inv.id, 150)
    assert next(i for i in repo.invoices() if i.id == inv.id).paid == 150
    with pytest.raises(ValueError, match="أكبر من المستحق"):
        repo.pay(sup.id, inv.id, 300)
    assert repo.outstanding(inv.id) == 250


def test_supplier_payment_must_match_supplier_and_confirmed_invoice():
    sup, inv = _confirmed_purchase()
    other = PurchaseRepository().add_supplier("S2", "مورد تاني")
    with pytest.raises(ValueError, match="مش بتاعة المورد"):
        PurchaseRepository().pay(other.id, inv.id, 10)
    draft = PurchaseRepository().create_invoice(sup.id)
    with pytest.raises(ValueError, match="مؤكدة"):
        PurchaseRepository().pay(sup.id, draft.id, 10)
    with pytest.raises(ValueError, match="المورد غير موجود"):
        PurchaseRepository().pay(999, None, 10)


def test_receipt_only_on_confirmed_invoice_of_same_customer_and_capped():
    batch = make_batch(1000)
    repo = SalesRepository()
    c1, c2 = make_customer("C1"), make_customer("C2")
    inv = draft_invoice(c1.id)
    repo.add_line(inv.id, batch.id, "أولى", 10, 100)   # 1000
    with pytest.raises(ValueError, match="مؤكدة"):
        repo.add_receipt(c1.id, inv.id, 100)
    repo.confirm(inv.id)
    with pytest.raises(ValueError, match="مش بتاعة العميل"):
        repo.add_receipt(c2.id, inv.id, 100)
    repo.add_receipt(c1.id, inv.id, 600)
    with pytest.raises(ValueError, match="أكبر من الرصيد"):
        repo.add_receipt(c1.id, inv.id, 500)
    assert repo.outstanding(inv.id) == 400


def test_receipt_reversal_is_a_counter_entry_and_unblocks_cancel():
    batch = make_batch(1000)
    repo = SalesRepository()
    c = make_customer()
    inv = draft_invoice(c.id)
    repo.add_line(inv.id, batch.id, "أولى", 10, 100)
    repo.confirm(inv.id)
    rc = repo.add_receipt(c.id, inv.id, 300)
    with pytest.raises(ValueError, match="تحصيلات"):
        repo.cancel(inv.id)
    repo.reverse_receipt(rc.id, "خطأ في المبلغ")
    assert repo.paid_for(inv.id) == 0
    with pytest.raises(ValueError, match="اتعكس"):
        repo.reverse_receipt(rc.id)
    repo.cancel(inv.id)


# ---- 8) رسائل الأخطاء العربي بدل IntegrityError -----------------------------------
def test_duplicate_farm_name_gives_arabic_message_not_integrity_error():
    FarmRepository().create("مزرعة")
    with pytest.raises(ValueError, match="اسم المزرعة مستخدم بالفعل"):
        FarmRepository().create("مزرعة")


def test_purchase_confirmation_still_prevents_double_receipt():
    sup, inv = _confirmed_purchase()
    PurchaseRepository().confirm(inv.id)  # تأكيد تاني
    with SessionLocal() as s:
        assert s.query(InventoryMovement).count() == 1
