"""حساب رصيد الدفعة (كجم) من حركات المحصول — مصدر واحد للحقيقة."""
from sqlalchemy import select, func
from app.domain.models import CropMovement

CROP_IN = ("استلام_حصاد", "إضافة", "إرجاع")


def crop_balance(session, batch_id: int) -> float:
    rows = session.execute(
        select(CropMovement.movement_type, func.coalesce(func.sum(CropMovement.quantity_kg), 0))
        .where(CropMovement.batch_id == batch_id)
        .group_by(CropMovement.movement_type)
    ).all()
    return sum(q if t in CROP_IN else -q for t, q in rows)
