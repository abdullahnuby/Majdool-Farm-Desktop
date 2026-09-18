from datetime import date
from sqlalchemy import select,func
from app.database.db import SessionLocal
from app.domain.models import CropSeason,HarvestBatch,SortLine,PackingBatch,CropMovement
class CropRepository:
 def seasons(self):
  with SessionLocal() as s:return s.scalars(select(CropSeason).order_by(CropSeason.start_date.desc())).all()
 def batches(self):
  with SessionLocal() as s:return s.scalars(select(HarvestBatch).order_by(HarvestBatch.harvest_date.desc())).all()
 def ready_kg(self,batch_id):
  with SessionLocal() as s:
   m=s.scalars(select(CropMovement).where(CropMovement.batch_id==batch_id)).all()
   return sum(x.quantity_kg if x.movement_type in ["استلام_حصاد","إضافة","إرجاع"] else -x.quantity_kg for x in m)
