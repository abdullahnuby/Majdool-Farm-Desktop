from datetime import date
from sqlalchemy import select,func
from app.database.db import SessionLocal
from app.domain.models import Customer,SalesInvoice,SalesInvoiceLine,Receipt,CropMovement
class SalesRepository:
 def customers(self):
  with SessionLocal() as s:return s.scalars(select(Customer).order_by(Customer.name)).all()
 def invoices(self):
  with SessionLocal() as s:return s.scalars(select(SalesInvoice).order_by(SalesInvoice.invoice_date.desc())).all()
 def add_customer(self,code,name,phone=""):
  with SessionLocal() as s:
   if s.scalar(select(Customer).where(Customer.code==code)):raise ValueError("كود العميل مستخدم بالفعل.")
   x=Customer(code=code,name=name,phone=phone or None);s.add(x);s.commit();s.refresh(x);return x
 def create_invoice(self,customer_id,day,discount,tax):
  with SessionLocal() as s:
   n=f"SI-{day.strftime('%Y%m%d')}-{(s.scalar(select(func.count(SalesInvoice.id))) or 0)+1:04d}"
   x=SalesInvoice(number=n,customer_id=customer_id,invoice_date=day,discount=discount,tax=tax);s.add(x);s.commit();s.refresh(x);return x
 def add_line(self,invoice_id,batch_id,grade,qty,price):
  if qty<=0:raise ValueError("كمية البيع يجب أن تكون أكبر من صفر.")
  with SessionLocal() as s:
   inv=s.get(SalesInvoice,invoice_id);line=SalesInvoiceLine(invoice_id=invoice_id,batch_id=batch_id,grade=grade,quantity_kg=qty,unit_price=price,line_total=qty*price);s.add(line);s.flush()
   subtotal=sum(x.line_total for x in s.scalars(select(SalesInvoiceLine).where(SalesInvoiceLine.invoice_id==invoice_id)).all())
   inv.subtotal=subtotal;inv.total=subtotal-inv.discount+inv.tax;s.commit();return line
 def confirm(self,invoice_id):
  with SessionLocal() as s:
   inv=s.get(SalesInvoice,invoice_id)
   if not inv:raise ValueError("الفاتورة غير موجودة.")
   if inv.status=="مؤكدة":return inv
   lines=s.scalars(select(SalesInvoiceLine).where(SalesInvoiceLine.invoice_id==invoice_id)).all()
   if not lines:raise ValueError("الفاتورة بلا بنود.")
   for line in lines:
    movements=s.scalars(select(CropMovement).where(CropMovement.batch_id==line.batch_id)).all()
    balance=sum(m.quantity_kg if m.movement_type in ["استلام_حصاد","إضافة","إرجاع"] else -m.quantity_kg for m in movements)
    if balance<line.quantity_kg:raise ValueError(f"الرصيد غير كافٍ للدفعة {line.batch_id}.")
   for line in lines:
    s.add(CropMovement(batch_id=line.batch_id,movement_type="صرف_للبيع",quantity_kg=line.quantity_kg,reference_type="sales_invoice",reference_id=inv.id))
   inv.status="مؤكدة";s.commit();s.refresh(inv);return inv
 def add_receipt(self,customer_id,invoice_id,amount,method="نقدي"):
  if amount<=0:raise ValueError("مبلغ التحصيل يجب أن يكون أكبر من صفر.")
  with SessionLocal() as s:
   inv=s.get(SalesInvoice,invoice_id) if invoice_id else None
   if inv:
    paid=s.scalar(select(func.coalesce(func.sum(Receipt.amount),0)).where(Receipt.invoice_id==invoice_id)) or 0
    if paid+amount>inv.total:raise ValueError("التحصيل أكبر من الرصيد المستحق.")
   n=f"RC-{(s.scalar(select(func.count(Receipt.id))) or 0)+1:06d}"
   x=Receipt(number=n,customer_id=customer_id,invoice_id=invoice_id,receipt_date=date.today(),amount=amount,payment_method=method);s.add(x);s.commit();return x
 def paid_for(self,invoice_id):
  with SessionLocal() as s:return s.scalar(select(func.coalesce(func.sum(Receipt.amount),0)).where(Receipt.invoice_id==invoice_id)) or 0
