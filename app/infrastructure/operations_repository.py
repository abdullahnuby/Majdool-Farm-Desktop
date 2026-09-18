from datetime import date
from sqlalchemy import select,func
from app.database.db import SessionLocal
from app.infrastructure.errors import db_errors
from app.domain.models import AgriculturalOperation,Asset,MaintenanceOrder
@db_errors
class OperationsRepository:
 def operations(self):
  with SessionLocal() as s:return s.scalars(select(AgriculturalOperation).order_by(AgriculturalOperation.operation_date.desc())).all()
 def assets(self):
  with SessionLocal() as s:return s.scalars(select(Asset).order_by(Asset.name)).all()
 def orders(self):
  with SessionLocal() as s:return s.scalars(select(MaintenanceOrder).order_by(MaintenanceOrder.opened_date.desc())).all()
 def open_orders_count(self):
  with SessionLocal() as s:return s.scalar(select(func.count(MaintenanceOrder.id)).where(MaintenanceOrder.status.in_(["مفتوح","قيد التنفيذ"]))) or 0
 def add_operation(self,operation_type,operation_date=None,responsible="",cost=0,notes=""):
    if not operation_type.strip():raise ValueError("نوع العملية مطلوب.")
    if cost<0:raise ValueError("التكلفة لا يمكن أن تكون سالبة.")
    with SessionLocal() as s:
     x=AgriculturalOperation(operation_type=operation_type.strip(),operation_date=operation_date or date.today(),responsible=responsible or None,cost=cost,notes=notes or None)
     s.add(x);s.commit();s.refresh(x);return x
 def add_asset(self,code,name,asset_type="معدات"):
    if not code.strip() or not name.strip():raise ValueError("كود واسم الأصل مطلوبان.")
    with SessionLocal() as s:
     if s.scalar(select(Asset).where(Asset.code==code.strip())):raise ValueError("كود الأصل مستخدم بالفعل.")
     x=Asset(code=code.strip(),name=name.strip(),asset_type=asset_type.strip() or "معدات");s.add(x);s.commit();s.refresh(x);return x
 def update_asset(self,asset_id,name,asset_type,status):
   if not name.strip():raise ValueError("اسم الأصل مطلوب.")
   with SessionLocal() as s:
    x=s.get(Asset,asset_id)
    if not x:raise ValueError("الأصل غير موجود.")
    x.name=name.strip();x.asset_type=asset_type.strip() or "معدات";x.status=status.strip() or "متاح";s.commit();s.refresh(x);return x
 def delete_asset(self,asset_id):
   with SessionLocal() as s:
    x=s.get(Asset,asset_id)
    if not x:raise ValueError("الأصل غير موجود.")
    if s.scalar(select(MaintenanceOrder).where(MaintenanceOrder.asset_id==asset_id)):raise ValueError("لا يمكن حذف أصل مرتبط بأمر صيانة.")
    s.delete(x);s.commit()
 def add_order(self,title,asset_id=None,priority="متوسطة"):
    if not title.strip():raise ValueError("عنوان أمر الصيانة مطلوب.")
    with SessionLocal() as s:
     x=MaintenanceOrder(title=title.strip(),asset_id=asset_id,opened_date=date.today(),priority=priority);s.add(x);s.commit();s.refresh(x);return x
 def update_order_status(self,order_id,status):
  if status not in ["مفتوح","قيد التنفيذ","مكتمل","ملغي"]:raise ValueError("حالة أمر الصيانة غير صحيحة.")
  with SessionLocal() as s:
   x=s.get(MaintenanceOrder,order_id)
   if not x:raise ValueError("أمر الصيانة غير موجود.")
   x.status=status;s.commit();s.refresh(x);return x
