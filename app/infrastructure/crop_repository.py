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
 def add_season(self,name,start_date=None):
    if not name.strip():raise ValueError("اسم الموسم مطلوب.")
    with SessionLocal() as s:
     if s.scalar(select(CropSeason).where(CropSeason.name==name.strip())):raise ValueError("اسم الموسم مستخدم بالفعل.")
     x=CropSeason(name=name.strip(),start_date=start_date or date.today());s.add(x);s.commit();s.refresh(x);return x
 def add_batch(self,season_id,block_id,gross_kg,variety="مجدول",palm_count=0,workers=0):
    if season_id<=0 or block_id<=0:raise ValueError("الموسم والبلوك مطلوبان.")
    if gross_kg<=0:raise ValueError("كمية الحصاد يجب أن تكون أكبر من صفر.")
    if palm_count<0 or workers<0:raise ValueError("أعداد النخيل والعمال لا يمكن أن تكون سالبة.")
    with SessionLocal() as s:
     number=f"HB-{date.today().strftime('%Y%m%d')}-{(s.scalar(select(func.count(HarvestBatch.id))) or 0)+1:04d}"
     batch=HarvestBatch(number=number,season_id=season_id,block_id=block_id,harvest_date=date.today(),variety=variety.strip() or "مجدول",palm_count=palm_count,workers=workers,gross_kg=gross_kg)
     s.add(batch);s.flush()
     s.add(CropMovement(batch_id=batch.id,movement_type="استلام_حصاد",quantity_kg=gross_kg,reference_type="harvest_batch",reference_id=batch.id))
     s.commit();s.refresh(batch);return batch
