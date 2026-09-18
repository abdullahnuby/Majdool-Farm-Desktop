from datetime import date
from sqlalchemy import select,func
from app.database.db import SessionLocal
from app.domain.models_purchases import Supplier,PurchaseInvoice,PurchaseLine,SupplierPayment
from app.domain.models_inventory import Warehouse,InventoryItem,InventoryMovement

class PurchaseRepository:
    def suppliers(self):
        with SessionLocal() as s:return s.scalars(select(Supplier).order_by(Supplier.name)).all()
    def invoices(self):
        with SessionLocal() as s:return s.scalars(select(PurchaseInvoice).order_by(PurchaseInvoice.invoice_date.desc())).all()
    def lines(self,invoice_id):
        with SessionLocal() as s:return s.scalars(select(PurchaseLine).where(PurchaseLine.invoice_id==invoice_id)).all()
    def add_supplier(self,code,name,phone=""):
        with SessionLocal() as s:
            if s.scalar(select(Supplier).where(Supplier.code==code)):raise ValueError("كود المورد مستخدم بالفعل.")
            x=Supplier(code=code,name=name,phone=phone or None);s.add(x);s.commit();s.refresh(x);return x
    def update_supplier(self,supplier_id,name,phone=""):
        if not name.strip():raise ValueError("اسم المورد مطلوب.")
        with SessionLocal() as s:
            x=s.get(Supplier,supplier_id)
            if not x:raise ValueError("المورد غير موجود.")
            x.name=name.strip();x.phone=phone or None;s.commit();s.refresh(x);return x
    def delete_supplier(self,supplier_id):
        with SessionLocal() as s:
            x=s.get(Supplier,supplier_id)
            if not x:raise ValueError("المورد غير موجود.")
            if s.scalar(select(PurchaseInvoice).where(PurchaseInvoice.supplier_id==supplier_id)) or s.scalar(select(SupplierPayment).where(SupplierPayment.supplier_id==supplier_id)):raise ValueError("لا يمكن حذف مورد مرتبط بفواتير أو سداد.")
            s.delete(x);s.commit()
    def create_invoice(self,supplier_id):
        with SessionLocal() as s:
            n=f"PI-{date.today().strftime('%Y%m%d')}-{(s.scalar(select(func.count(PurchaseInvoice.id))) or 0)+1:04d}"
            x=PurchaseInvoice(number=n,supplier_id=supplier_id,invoice_date=date.today());s.add(x);s.commit();s.refresh(x);return x
    def add_line(self,invoice_id,name,qty,price,unit="وحدة",category="عام"):
        if qty<=0 or price<0:raise ValueError("الكمية والسعر غير صحيحين.")
        with SessionLocal() as s:
            inv=s.get(PurchaseInvoice,invoice_id)
            if not inv or inv.status=="مؤكدة":raise ValueError("لا يمكن تعديل فاتورة مؤكدة.")
            s.add(PurchaseLine(invoice_id=invoice_id,item_name=name,category=category,quantity=qty,unit=unit,unit_price=price,line_total=qty*price))
            s.flush();lines=s.scalars(select(PurchaseLine).where(PurchaseLine.invoice_id==invoice_id)).all()
            inv.subtotal=sum(x.line_total for x in lines);inv.total=inv.subtotal-inv.discount+inv.tax;s.commit()
    def confirm(self,invoice_id,warehouse_id=None):
        with SessionLocal() as s:
            inv=s.get(PurchaseInvoice,invoice_id)
            if not inv:raise ValueError("الفاتورة غير موجودة.")
            if inv.status=="مؤكدة":return inv
            lines=s.scalars(select(PurchaseLine).where(PurchaseLine.invoice_id==invoice_id)).all()
            if not lines:raise ValueError("الفاتورة بلا بنود.")
            wh=s.get(Warehouse,warehouse_id) if warehouse_id else s.scalar(select(Warehouse).order_by(Warehouse.id))
            if not wh:
                wh=Warehouse(code="MAIN",name="المخزن الرئيسي");s.add(wh);s.flush()
            for line in lines:
                item=s.scalar(select(InventoryItem).where(InventoryItem.name==line.item_name))
                if not item:
                    count=(s.scalar(select(func.count(InventoryItem.id))) or 0)+1
                    item=InventoryItem(code=f"IT-{count:05d}",name=line.item_name,category=line.category,unit=line.unit)
                    s.add(item);s.flush()
                exists=s.scalar(select(InventoryMovement).where(
                    InventoryMovement.reference_type=="purchase_invoice",InventoryMovement.reference_id==invoice_id,
                    InventoryMovement.item_id==item.id,InventoryMovement.warehouse_id==wh.id,
                    InventoryMovement.movement_type=="استلام_شراء"))
                if not exists:
                    s.add(InventoryMovement(item_id=item.id,warehouse_id=wh.id,movement_type="استلام_شراء",
                        quantity=line.quantity,unit_cost=line.unit_price,reference_type="purchase_invoice",reference_id=invoice_id))
            inv.status="مؤكدة";s.commit();return inv
    def pay(self,supplier_id,invoice_id,amount,method="نقدي"):
        if amount<=0:raise ValueError("مبلغ السداد يجب أن يكون أكبر من صفر.")
        with SessionLocal() as s:
            inv=s.get(PurchaseInvoice,invoice_id)
            if inv:
                paid=s.scalar(select(func.coalesce(func.sum(SupplierPayment.amount),0)).where(SupplierPayment.invoice_id==invoice_id)) or 0
                if paid+amount>inv.total:raise ValueError("السداد أكبر من المستحق.")
            x=SupplierPayment(supplier_id=supplier_id,invoice_id=invoice_id,payment_date=date.today(),amount=amount,payment_method=method)
            s.add(x);s.commit();return x
    def outstanding(self,invoice_id):
        with SessionLocal() as s:
            inv=s.get(PurchaseInvoice,invoice_id)
            if not inv:return 0
            paid=s.scalar(select(func.coalesce(func.sum(SupplierPayment.amount),0)).where(SupplierPayment.invoice_id==invoice_id)) or 0
            return max(0,inv.total-paid)
