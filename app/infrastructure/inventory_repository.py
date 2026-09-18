from sqlalchemy import select,func
from app.database.db import SessionLocal
from app.domain.models_inventory import Warehouse,InventoryItem,InventoryMovement
from app.application.inventory_service import InventoryService

class InventoryRepository:
    def warehouses(self):
        with SessionLocal() as s:return s.scalars(select(Warehouse).order_by(Warehouse.name)).all()
    def items(self):
        with SessionLocal() as s:return s.scalars(select(InventoryItem).order_by(InventoryItem.name)).all()
    def add_warehouse(self,code,name,location=""):
        with SessionLocal() as s:
            if s.scalar(select(Warehouse).where(Warehouse.code==code)):raise ValueError("كود المخزن مستخدم.")
            x=Warehouse(code=code,name=name,location=location or None);s.add(x);s.commit();s.refresh(x);return x
    def add_item(self,code,name,category="عام",unit="وحدة",min_stock=0):
        if min_stock<0:raise ValueError("الحد الأدنى لا يمكن أن يكون سالباً.")
        with SessionLocal() as s:
            if s.scalar(select(InventoryItem).where(InventoryItem.code==code)):raise ValueError("كود الصنف مستخدم.")
            x=InventoryItem(code=code,name=name,category=category,unit=unit,min_stock=min_stock);s.add(x);s.commit();s.refresh(x);return x
    def update_item(self,item_id,name,category,unit,min_stock):
        if not name.strip():raise ValueError("اسم الصنف مطلوب.")
        if min_stock<0:raise ValueError("الحد الأدنى لا يمكن أن يكون سالباً.")
        with SessionLocal() as s:
            x=s.get(InventoryItem,item_id)
            if not x:raise ValueError("الصنف غير موجود.")
            x.name=name.strip();x.category=category.strip() or "عام";x.unit=unit.strip() or "وحدة";x.min_stock=min_stock;s.commit();s.refresh(x);return x
    def delete_item(self,item_id):
        with SessionLocal() as s:
            x=s.get(InventoryItem,item_id)
            if not x:raise ValueError("الصنف غير موجود.")
            if s.scalar(select(InventoryMovement).where(InventoryMovement.item_id==item_id)):raise ValueError("لا يمكن حذف صنف له حركات مخزون.")
            s.delete(x);s.commit()
    def find_or_create_item(self,name,category="عام",unit="وحدة"):
        with SessionLocal() as s:
            x=s.scalar(select(InventoryItem).where(InventoryItem.name==name))
            if x:return x
            count=(s.scalar(select(func.count(InventoryItem.id))) or 0)+1
            x=InventoryItem(code=f"IT-{count:05d}",name=name,category=category,unit=unit);s.add(x);s.commit();s.refresh(x);return x
    def balance(self,item_id,warehouse_id):
        with SessionLocal() as s:
            ms=s.scalars(select(InventoryMovement).where(InventoryMovement.item_id==item_id,InventoryMovement.warehouse_id==warehouse_id)).all()
            return InventoryService.balance(ms)
    def receive_purchase(self,item_id,warehouse_id,quantity,unit_cost,invoice_id):
        if quantity<=0:raise ValueError("كمية الاستلام غير صحيحة.")
        with SessionLocal() as s:
            existing=s.scalar(select(InventoryMovement).where(
                InventoryMovement.reference_type=="purchase_invoice",
                InventoryMovement.reference_id==invoice_id,
                InventoryMovement.item_id==item_id,
                InventoryMovement.warehouse_id==warehouse_id,
                InventoryMovement.movement_type=="استلام_شراء"))
            if existing:return existing
            x=InventoryMovement(item_id=item_id,warehouse_id=warehouse_id,movement_type="استلام_شراء",
                quantity=quantity,unit_cost=unit_cost,reference_type="purchase_invoice",reference_id=invoice_id)
            s.add(x);s.commit();s.refresh(x);return x
    def issue(self,item_id,warehouse_id,quantity,notes=""):
        if quantity<=0:raise ValueError("كمية الصرف غير صحيحة.")
        with SessionLocal() as s:
            ms=s.scalars(select(InventoryMovement).where(InventoryMovement.item_id==item_id,InventoryMovement.warehouse_id==warehouse_id)).all()
            if not InventoryService.can_issue(InventoryService.balance(ms),quantity):
                raise ValueError("الرصيد غير كافٍ للصرف.")
            x=InventoryMovement(item_id=item_id,warehouse_id=warehouse_id,movement_type="صرف",
                quantity=quantity,reference_type="manual",notes=notes or None)
            s.add(x);s.commit();s.refresh(x);return x
