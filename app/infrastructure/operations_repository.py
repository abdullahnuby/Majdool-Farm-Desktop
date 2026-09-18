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
