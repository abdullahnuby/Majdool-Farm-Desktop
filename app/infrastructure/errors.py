"""ترجمة أخطاء قاعدة البيانات لرسائل عربي مفهومة.

الواجهة بتعرض str(error) لأي Exception، فتحويل IntegrityError إلى ValueError
بنص عربي كفاية إن المستخدم يشوف رسالة مفهومة بدل traceback.
"""
import functools
import inspect
from sqlalchemy.exc import IntegrityError, OperationalError

_UNIQUE_LABELS = {
    "farms.name": "اسم المزرعة مستخدم بالفعل.",
    "palms.code": "كود النخلة مستخدم بالفعل.",
    "crop_seasons.name": "اسم الموسم مستخدم بالفعل.",
    "harvest_batches.number": "رقم دفعة الحصاد مستخدم بالفعل.",
    "packing_batches.number": "رقم دفعة التعبئة مستخدم بالفعل.",
    "customers.code": "كود العميل مستخدم بالفعل.",
    "sales_invoices.number": "رقم فاتورة البيع مستخدم بالفعل.",
    "receipts.number": "رقم الإيصال مستخدم بالفعل.",
    "suppliers.code": "كود المورد مستخدم بالفعل.",
    "purchase_invoices.number": "رقم فاتورة الشراء مستخدم بالفعل.",
    "employees.code": "كود الموظف مستخدم بالفعل.",
    "consultants.code": "كود الاستشاري مستخدم بالفعل.",
    "warehouses.code": "كود المخزن مستخدم بالفعل.",
    "inventory_items.code": "كود الصنف مستخدم بالفعل.",
    "assets.code": "كود الأصل مستخدم بالفعل.",
    "payrolls.employee_id, payrolls.period": "تم إنشاء راتب لهذا الموظف في هذه الفترة بالفعل.",
    "attendance.employee_id, attendance.attendance_date": "يوجد تسجيل حضور لهذا الموظف في نفس اليوم.",
}


def translate(error: Exception) -> str | None:
    """يرجّع رسالة عربي للأخطاء المعروفة، أو None لو الخطأ غير متوقع (يتعامل معه كخطأ برمجي)."""
    message = str(getattr(error, "orig", error))
    if isinstance(error, IntegrityError):
        if "UNIQUE constraint failed" in message:
            key = message.split("UNIQUE constraint failed:", 1)[1].strip()
            return _UNIQUE_LABELS.get(key, "القيمة مكررة ومستخدمة بالفعل.")
        if "FOREIGN KEY constraint failed" in message:
            return "السجل مرتبط ببيانات غير موجودة، أو مستخدم في سجلات أخرى."
        if "NOT NULL constraint failed" in message:
            return "فيه حقل مطلوب فاضي."
        return "البيانات المدخلة مخالفة لقواعد قاعدة البيانات."
    if isinstance(error, OperationalError) and "locked" in message.lower():
        return "قاعدة البيانات مشغولة حالياً، حاول مرة تانية بعد ثواني."
    return None


def _wrap(function):
    @functools.wraps(function)
    def inner(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except (IntegrityError, OperationalError) as error:
            text = translate(error)
            if text is None:
                raise
            raise ValueError(text) from error
    return inner


def db_errors(cls):
    """Class decorator: يلفّ كل الدوال العامة في الـ repository بترجمة الأخطاء."""
    for name, member in list(vars(cls).items()):
        if not name.startswith("_") and inspect.isfunction(member):
            setattr(cls, name, _wrap(member))
    return cls
