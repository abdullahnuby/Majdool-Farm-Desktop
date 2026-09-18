from datetime import date
from sqlalchemy import select,func
from app.database.db import SessionLocal
from app.domain.models import AgriculturalOperation,Asset,MaintenanceOrder
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
 def add_order(self,title,asset_id=None,priority="متوسطة"):
    if not title.strip():raise ValueError("عنوان أمر الصيانة مطلوب.")
    with SessionLocal() as s:
     x=MaintenanceOrder(title=title.strip(),asset_id=asset_id,opened_date=date.today(),priority=priority);s.add(x);s.commit();s.refresh(x);return x
