from sqlalchemy import select, func

from app.database.db import SessionLocal
from app.domain.models import (
    AgriculturalOperation,
    EmployeeAssignment,
    Farm,
    FarmRow,
    FertilizationRecord,
    HarvestBatch,
    IrrigationRecord,
    Sector,
    Block,
    FarmVisit,
)
from app.infrastructure.errors import db_errors


@db_errors
class FarmRepository:
    def list(self):
        with SessionLocal() as s:
            return s.scalars(select(Farm).order_by(Farm.name)).all()

    def create(self, name, location="", area=0, unit="فدان", notes=""):
        if not name.strip():
            raise ValueError("اسم المزرعة مطلوب.")
        with SessionLocal() as s:
            x = Farm(name=name.strip(), location=location.strip() or None, area=area, area_unit=unit.strip() or "فدان", notes=notes.strip() or None)
            s.add(x)
            s.commit()
            s.refresh(x)
            return x

    def get(self, farm_id):
        with SessionLocal() as s:
            return s.get(Farm, farm_id)

    def update_farm(self, farm_id, name, location="", area=0, unit="فدان", notes=""):
        if not name.strip():
            raise ValueError("اسم المزرعة مطلوب.")
        with SessionLocal() as s:
            x = s.get(Farm, farm_id)
            if not x:
                raise ValueError("المزرعة غير موجودة.")
            x.name = name.strip()
            x.location = location.strip() or None
            x.area = area
            x.area_unit = unit.strip() or "فدان"
            x.notes = notes.strip() or None
            s.commit()
            s.refresh(x)
            return x

    def delete_farm(self, farm_id):
        with SessionLocal() as s:
            x = s.get(Farm, farm_id)
            if not x:
                raise ValueError("المزرعة غير موجودة.")
            if s.scalar(select(Sector.id).where(Sector.farm_id == farm_id).limit(1)):
                raise ValueError("لا يمكن حذف مزرعة تحتوي على قطاعات.")
            s.delete(x)
            s.commit()


@db_errors
class StructureRepository:
    def sectors(self, farm_id):
        with SessionLocal() as s:
            return s.scalars(select(Sector).where(Sector.farm_id == farm_id).order_by(Sector.name)).all()

    def blocks(self, sector_id):
        with SessionLocal() as s:
            return s.scalars(select(Block).where(Block.sector_id == sector_id).order_by(Block.code)).all()

    def get_sector(self, sector_id):
        with SessionLocal() as s:
            return s.get(Sector, sector_id)

    def get_block(self, block_id):
        with SessionLocal() as s:
            return s.get(Block, block_id)

    def create_sector(self, farm_id, name, notes=""):
        if not name.strip():
            raise ValueError("اسم القطاع مطلوب.")
        with SessionLocal() as s:
            if not s.get(Farm, farm_id):
                raise ValueError("المزرعة غير موجودة.")
            x = Sector(farm_id=farm_id, name=name.strip(), notes=notes.strip() or None)
            s.add(x)
            s.commit()
            s.refresh(x)
            return x

    def update_sector(self, sector_id, name, notes=""):
        if not name.strip():
            raise ValueError("اسم القطاع مطلوب.")
        with SessionLocal() as s:
            x = s.get(Sector, sector_id)
            if not x:
                raise ValueError("القطاع غير موجود.")
            x.name = name.strip()
            x.notes = notes.strip() or None
            s.commit()
            s.refresh(x)
            return x

    def delete_sector(self, sector_id):
        with SessionLocal() as s:
            x = s.get(Sector, sector_id)
            if not x:
                raise ValueError("القطاع غير موجود.")
            if s.scalar(select(Block.id).where(Block.sector_id == sector_id).limit(1)):
                raise ValueError("لا يمكن حذف قطاع يحتوي على بلوكات.")
            s.delete(x)
            s.commit()

    def create_block(self, sector_id, code, name, area=0, palm_count=0, notes=""):
        code_text = code.strip()
        name_text = name.strip()
        if not code_text or not name_text:
            raise ValueError("كود واسم البلوك مطلوبان.")
        with SessionLocal() as s:
            if not s.get(Sector, sector_id):
                raise ValueError("القطاع غير موجود.")
            if s.scalar(select(Block.id).where(Block.sector_id == sector_id, Block.code == code_text).limit(1)):
                raise ValueError("كود البلوك مستخدم في نفس القطاع.")
            x = Block(sector_id=sector_id, code=code_text, name=name_text, area=area, palm_count=palm_count, notes=notes.strip() or None)
            s.add(x)
            s.commit()
            s.refresh(x)
            return x

    def update_block(self, block_id, code, name, area=0, palm_count=0, notes=""):
        code_text = code.strip()
        name_text = name.strip()
        if not code_text or not name_text:
            raise ValueError("كود واسم البلوك مطلوبان.")
        with SessionLocal() as s:
            x = s.get(Block, block_id)
            if not x:
                raise ValueError("البلوك غير موجود.")
            if s.scalar(select(Block.id).where(Block.sector_id == x.sector_id, Block.code == code_text, Block.id != block_id).limit(1)):
                raise ValueError("كود البلوك مستخدم في نفس القطاع.")
            x.code = code_text
            x.name = name_text
            x.area = area
            x.palm_count = palm_count
            x.notes = notes.strip() or None
            s.commit()
            s.refresh(x)
            return x

    def delete_block(self, block_id):
        with SessionLocal() as s:
            x = s.get(Block, block_id)
            if not x:
                raise ValueError("البلوك غير موجود.")
            related = [
                (FarmRow, "block_id"),
                (HarvestBatch, "block_id"),
                (AgriculturalOperation, "block_id"),
                (IrrigationRecord, "block_id"),
                (FertilizationRecord, "block_id"),
                (EmployeeAssignment, "block_id"),
                (FarmVisit, "block_id"),
            ]
            for model, col_name in related:
                if s.scalar(select(model.id).where(getattr(model, col_name) == block_id).limit(1)):
                    raise ValueError("لا يمكن حذف بلوك مرتبط بسجلات أو عمليات أخرى.")
            s.delete(x)
            s.commit()

    def stats(self):
        with SessionLocal() as s:
            return tuple(
                (s.scalar(q) or 0)
                for q in [
                    select(func.count(Farm.id)),
                    select(func.count(Sector.id)),
                    select(func.count(Block.id)),
                    select(func.coalesce(func.sum(Block.palm_count), 0)),
                ]
            )

