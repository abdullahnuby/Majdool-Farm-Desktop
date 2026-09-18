from sqlalchemy import select,func
from app.database.db import SessionLocal
from app.domain.models import Farm,Sector,Block
class FarmRepository:
 def list(self):
  with SessionLocal() as s:return s.scalars(select(Farm).order_by(Farm.name)).all()
 def create(self,name,location="",area=0,unit="فدان",notes=""):
  with SessionLocal() as s:x=Farm(name=name,location=location or None,area=area,area_unit=unit,notes=notes or None);s.add(x);s.commit();return x
class StructureRepository:
 def sectors(self,farm_id):
  with SessionLocal() as s:return s.scalars(select(Sector).where(Sector.farm_id==farm_id)).all()
 def blocks(self,sector_id):
  with SessionLocal() as s:return s.scalars(select(Block).where(Block.sector_id==sector_id)).all()
 def create_sector(self,farm_id,name):
  with SessionLocal() as s:x=Sector(farm_id=farm_id,name=name);s.add(x);s.commit();return x
 def create_block(self,sector_id,code,name):
  with SessionLocal() as s:x=Block(sector_id=sector_id,code=code,name=name);s.add(x);s.commit();return x
 def stats(self):
  with SessionLocal() as s:return tuple((s.scalar(q) or 0) for q in [select(func.count(Farm.id)),select(func.count(Sector.id)),select(func.count(Block.id)),select(func.coalesce(func.sum(Block.palm_count),0))])
