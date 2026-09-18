from datetime import date
from sqlalchemy import select
from app.database.db import SessionLocal
from app.domain.models import IrrigationRecord,FertilizationRecord


class AgricultureRepository:
    def irrigations(self):
        with SessionLocal() as session:
            return session.scalars(select(IrrigationRecord).order_by(IrrigationRecord.irrigation_date.desc())).all()

    def fertilizations(self):
        with SessionLocal() as session:
            return session.scalars(select(FertilizationRecord).order_by(FertilizationRecord.fertilization_date.desc())).all()

    def add_irrigation(self,quantity,method="تنقيط",unit="متر مكعب",block_id=None,responsible=""):
        if quantity <= 0:
            raise ValueError("كمية الري يجب أن تكون أكبر من صفر.")
        if not method.strip():
            raise ValueError("طريقة الري مطلوبة.")
        with SessionLocal() as session:
            record=IrrigationRecord(block_id=block_id,irrigation_date=date.today(),method=method.strip(),quantity=quantity,unit=unit.strip() or "متر مكعب",responsible=responsible or None)
            session.add(record);session.commit();session.refresh(record);return record

    def add_fertilization(self,product,quantity,unit="كجم",block_id=None,responsible=""):
        if not product.strip():
            raise ValueError("اسم السماد مطلوب.")
        if quantity <= 0:
            raise ValueError("كمية السماد يجب أن تكون أكبر من صفر.")
        with SessionLocal() as session:
            record=FertilizationRecord(block_id=block_id,fertilization_date=date.today(),product=product.strip(),quantity=quantity,unit=unit.strip() or "كجم",responsible=responsible or None)
            session.add(record);session.commit();session.refresh(record);return record