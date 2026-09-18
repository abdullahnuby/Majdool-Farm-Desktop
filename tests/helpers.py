"""أدوات بناء بيانات للاختبارات التكاملية (قاعدة فعلية مؤقتة)."""
from datetime import date
from app.infrastructure.repositories import FarmRepository, StructureRepository
from app.infrastructure.crop_repository import CropRepository
from app.infrastructure.sales_repository import SalesRepository
from app.infrastructure.purchase_repository import PurchaseRepository
from app.infrastructure.hr_repository import HRRepository


def make_block():
    farm = FarmRepository().create("مزرعة الاختبار")
    sector = StructureRepository().create_sector(farm.id, "قطاع 1")
    return StructureRepository().create_block(sector.id, "B1", "بلوك 1")


def make_batch(gross_kg=1000):
    block = make_block()
    crop = CropRepository()
    season = crop.add_season("موسم 2026")
    return crop.add_batch(season.id, block.id, gross_kg)


def make_customer(code="C1"):
    return SalesRepository().add_customer(code, "عميل اختبار")


def make_supplier(code="S1"):
    return PurchaseRepository().add_supplier(code, "مورد اختبار")


def make_employee(code="E1", monthly=0, daily=0):
    return HRRepository().add_employee(code, "موظف اختبار", daily_rate=daily, monthly_salary=monthly)


def draft_invoice(customer_id, discount=0, tax=0):
    return SalesRepository().create_invoice(customer_id, date.today(), discount, tax)
