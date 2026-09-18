from collections import defaultdict
from datetime import date
from sqlalchemy import select, func
from app.database.db import SessionLocal
from app.domain.models import Customer, SalesInvoice, SalesInvoiceLine, Receipt, CropMovement, HarvestBatch
from app.application.sales_service import SalesService
from app.infrastructure.errors import db_errors
from app.infrastructure.stock import crop_balance

DRAFT, CONFIRMED, CANCELLED = "مسودة", "مؤكدة", "ملغاة"
_EPS = 1e-6


def _net_receipts(s, invoice_id) -> float:
    return s.scalar(select(func.coalesce(func.sum(Receipt.amount), 0)).where(Receipt.invoice_id == invoice_id)) or 0


def _recalculate(s, inv):
    lines = s.scalars(select(SalesInvoiceLine).where(SalesInvoiceLine.invoice_id == inv.id)).all()
    inv.subtotal = sum(x.line_total for x in lines)
    inv.total = inv.subtotal - inv.discount + inv.tax


def _check_stock(s, quantities: dict):
    """يفحص الرصيد بعد تجميع كل الكميات لنفس الدفعة (مش بند بند)."""
    for batch_id, needed in quantities.items():
        if needed > crop_balance(s, batch_id) + _EPS:
            raise ValueError(f"الرصيد غير كافٍ للدفعة {batch_id}.")


@db_errors
class SalesRepository:
    def customers(self):
        with SessionLocal() as s:
            return s.scalars(select(Customer).order_by(Customer.name)).all()

    def invoices(self):
        with SessionLocal() as s:
            return s.scalars(select(SalesInvoice).order_by(SalesInvoice.invoice_date.desc())).all()

    def lines(self, invoice_id):
        with SessionLocal() as s:
            return s.scalars(select(SalesInvoiceLine).where(SalesInvoiceLine.invoice_id == invoice_id)).all()

    def add_customer(self, code, name, phone=""):
        with SessionLocal() as s:
            if s.scalar(select(Customer).where(Customer.code == code)):
                raise ValueError("كود العميل مستخدم بالفعل.")
            x = Customer(code=code, name=name, phone=phone or None)
            s.add(x); s.commit(); s.refresh(x); return x

    def update_customer(self, customer_id, name, phone=""):
        if not name.strip():
            raise ValueError("اسم العميل مطلوب.")
        with SessionLocal() as s:
            x = s.get(Customer, customer_id)
            if not x:
                raise ValueError("العميل غير موجود.")
            x.name = name.strip(); x.phone = phone or None
            s.commit(); s.refresh(x); return x

    def delete_customer(self, customer_id):
        with SessionLocal() as s:
            x = s.get(Customer, customer_id)
            if not x:
                raise ValueError("العميل غير موجود.")
            if s.scalar(select(SalesInvoice).where(SalesInvoice.customer_id == customer_id)) or \
               s.scalar(select(Receipt).where(Receipt.customer_id == customer_id)):
                raise ValueError("لا يمكن حذف عميل مرتبط بفواتير أو تحصيلات.")
            s.delete(x); s.commit()

    def create_invoice(self, customer_id, day, discount, tax):
        if discount < 0 or tax < 0:
            raise ValueError("الخصم أو الضريبة غير صحيحة.")
        with SessionLocal() as s:
            if not s.get(Customer, customer_id):
                raise ValueError("العميل غير موجود.")
            n = f"SI-{day.strftime('%Y%m%d')}-{(s.scalar(select(func.count(SalesInvoice.id))) or 0) + 1:04d}"
            x = SalesInvoice(number=n, customer_id=customer_id, invoice_date=day, discount=discount, tax=tax)
            s.add(x); s.commit(); s.refresh(x); return x

    def add_line(self, invoice_id, batch_id, grade, qty, price):
        SalesService.line_total(qty, price)  # يرفض السالب
        if qty <= 0:
            raise ValueError("كمية البيع يجب أن تكون أكبر من صفر.")
        if not grade.strip():
            raise ValueError("درجة الصنف مطلوبة.")
        with SessionLocal() as s:
            inv = s.get(SalesInvoice, invoice_id)
            if not inv:
                raise ValueError("الفاتورة غير موجودة.")
            if inv.status != DRAFT:
                raise ValueError("لا يمكن تعديل فاتورة مؤكدة أو ملغاة.")
            if not s.get(HarvestBatch, batch_id):
                raise ValueError("دفعة الحصاد غير موجودة.")
            existing = s.scalars(select(SalesInvoiceLine).where(SalesInvoiceLine.invoice_id == invoice_id)).all()
            already = sum(x.quantity_kg for x in existing if x.batch_id == batch_id)
            _check_stock(s, {batch_id: already + qty})
            line = SalesInvoiceLine(invoice_id=invoice_id, batch_id=batch_id, grade=grade.strip(),
                                    quantity_kg=qty, unit_price=price, line_total=qty * price)
            s.add(line); s.flush()
            _recalculate(s, inv)
            s.commit(); return line

    def delete_line(self, invoice_id, line_id):
        with SessionLocal() as s:
            inv=s.get(SalesInvoice, invoice_id)
            line=s.get(SalesInvoiceLine, line_id)
            if not inv or not line or line.invoice_id != invoice_id:
                raise ValueError("بند الفاتورة غير موجود.")
            if inv.status != DRAFT:
                raise ValueError("لا يمكن تعديل فاتورة مؤكدة أو ملغاة.")
            s.delete(line); s.flush(); _recalculate(s, inv); s.commit()

    def update_draft(self, invoice_id, customer_id, day, discount, tax, lines):
        if discount < 0 or tax < 0 or not lines: raise ValueError("بيانات الفاتورة غير مكتملة.")
        with SessionLocal() as s:
            inv=s.get(SalesInvoice, invoice_id)
            if not inv or inv.status != DRAFT: raise ValueError("لا يمكن تعديل هذه الفاتورة.")
            if not s.get(Customer, customer_id): raise ValueError("العميل غير موجود.")
            inv.customer_id=customer_id; inv.invoice_date=day; inv.discount=discount; inv.tax=tax
            for old in s.scalars(select(SalesInvoiceLine).where(SalesInvoiceLine.invoice_id==invoice_id)).all(): s.delete(old)
            needed={}
            for batch_id, grade, qty, price in lines:
                if qty <= 0 or not grade.strip(): raise ValueError("بيانات بند البيع غير صحيحة.")
                needed[batch_id]=needed.get(batch_id,0)+qty
                s.add(SalesInvoiceLine(invoice_id=invoice_id,batch_id=batch_id,grade=grade.strip(),quantity_kg=qty,unit_price=price,line_total=qty*price))
            _check_stock(s, needed)
            s.flush(); _recalculate(s, inv); s.commit()

    def confirm(self, invoice_id):
        with SessionLocal() as s:
            inv = s.get(SalesInvoice, invoice_id)
            if not inv:
                raise ValueError("الفاتورة غير موجودة.")
            if inv.status == CONFIRMED:
                return inv
            if inv.status == CANCELLED:
                raise ValueError("الفاتورة ملغاة ولا يمكن تأكيدها.")
            lines = s.scalars(select(SalesInvoiceLine).where(SalesInvoiceLine.invoice_id == invoice_id)).all()
            if not lines:
                raise ValueError("الفاتورة بلا بنود.")
            _recalculate(s, inv)
            SalesService.invoice_total(inv.subtotal, inv.discount, inv.tax)  # الخصم ≤ الإجمالي
            needed = defaultdict(float)
            for line in lines:
                needed[line.batch_id] += line.quantity_kg
            _check_stock(s, needed)
            for line in lines:
                s.add(CropMovement(batch_id=line.batch_id, movement_type="صرف_للبيع", quantity_kg=line.quantity_kg,
                                   reference_type="sales_invoice", reference_id=inv.id))
            inv.status = CONFIRMED
            s.commit(); s.refresh(inv); return inv

    def cancel(self, invoice_id):
        """إلغاء فاتورة: المسودة تتلغي، والمؤكدة بترجّع الكميات بحركة عكسية (مفيش حذف)."""
        with SessionLocal() as s:
            inv = s.get(SalesInvoice, invoice_id)
            if not inv:
                raise ValueError("الفاتورة غير موجودة.")
            if inv.status == CANCELLED:
                return inv
            if abs(_net_receipts(s, invoice_id)) > _EPS:
                raise ValueError("عليها تحصيلات. اعكس التحصيلات أولاً ثم ألغِ الفاتورة.")
            if inv.status == CONFIRMED:
                for line in s.scalars(select(SalesInvoiceLine).where(SalesInvoiceLine.invoice_id == invoice_id)).all():
                    s.add(CropMovement(batch_id=line.batch_id, movement_type="إرجاع", quantity_kg=line.quantity_kg,
                                       reference_type="sales_invoice_cancel", reference_id=inv.id))
            inv.status = CANCELLED
            s.commit(); s.refresh(inv); return inv

    def delete_draft(self, invoice_id):
        with SessionLocal() as s:
            inv = s.get(SalesInvoice, invoice_id)
            if not inv:
                raise ValueError("الفاتورة غير موجودة.")
            if inv.status != DRAFT:
                raise ValueError("لا يمكن حذف فاتورة مؤكدة أو ملغاة.")
            for line in s.scalars(select(SalesInvoiceLine).where(SalesInvoiceLine.invoice_id == invoice_id)).all():
                s.delete(line)
            s.delete(inv)
            s.commit()

    def add_receipt(self, customer_id, invoice_id, amount, method="نقدي"):
        if amount <= 0:
            raise ValueError("مبلغ التحصيل يجب أن يكون أكبر من صفر.")
        with SessionLocal() as s:
            if not s.get(Customer, customer_id):
                raise ValueError("العميل غير موجود.")
            if invoice_id:
                inv = s.get(SalesInvoice, invoice_id)
                if not inv:
                    raise ValueError("الفاتورة غير موجودة.")
                if inv.status != CONFIRMED:
                    raise ValueError("التحصيل يكون على فاتورة مؤكدة فقط.")
                if inv.customer_id != customer_id:
                    raise ValueError("الفاتورة دي مش بتاعة العميل ده.")
                if _net_receipts(s, invoice_id) + amount > inv.total + _EPS:
                    raise ValueError("التحصيل أكبر من الرصيد المستحق.")
            n = f"RC-{(s.scalar(select(func.count(Receipt.id))) or 0) + 1:06d}"
            x = Receipt(number=n, customer_id=customer_id, invoice_id=invoice_id, receipt_date=date.today(),
                        amount=amount, payment_method=method)
            s.add(x); s.commit(); s.refresh(x); return x

    def reverse_receipt(self, receipt_id, reason=""):
        """عكس تحصيل بقيد سالب مرتبط بيه (السجل الأصلي يفضل كما هو)."""
        with SessionLocal() as s:
            orig = s.get(Receipt, receipt_id)
            if not orig:
                raise ValueError("الإيصال غير موجود.")
            if orig.amount <= 0:
                raise ValueError("لا يمكن عكس قيد عكسي.")
            marker = f"REV:{orig.number}"
            if s.scalar(select(Receipt).where(Receipt.reference == marker)):
                raise ValueError("الإيصال ده اتعكس قبل كده.")
            n = f"RC-{(s.scalar(select(func.count(Receipt.id))) or 0) + 1:06d}"
            x = Receipt(number=n, customer_id=orig.customer_id, invoice_id=orig.invoice_id, receipt_date=date.today(),
                        amount=-orig.amount, payment_method=orig.payment_method, reference=marker,
                        notes=reason or None)
            s.add(x); s.commit(); s.refresh(x); return x

    def paid_for(self, invoice_id):
        with SessionLocal() as s:
            return _net_receipts(s, invoice_id)

    def outstanding(self, invoice_id):
        with SessionLocal() as s:
            inv = s.get(SalesInvoice, invoice_id)
            return 0 if not inv else max(0, inv.total - _net_receipts(s, invoice_id))
