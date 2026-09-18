from datetime import date
from sqlalchemy import String,Integer,Float,Date,Text,ForeignKey,Boolean
from sqlalchemy.orm import Mapped,mapped_column
from app.database.db import Base

class Supplier(Base):
    __tablename__="suppliers"
    id:Mapped[int]=mapped_column(primary_key=True)
    code:Mapped[str]=mapped_column(String(60),unique=True)
    name:Mapped[str]=mapped_column(String(150))
    phone:Mapped[str|None]=mapped_column(String(50))
    address:Mapped[str|None]=mapped_column(String(250))
    tax_number:Mapped[str|None]=mapped_column(String(80))
    notes:Mapped[str|None]=mapped_column(Text)
    active:Mapped[bool]=mapped_column(Boolean,default=True)

class PurchaseInvoice(Base):
    __tablename__="purchase_invoices"
    id:Mapped[int]=mapped_column(primary_key=True)
    number:Mapped[str]=mapped_column(String(60),unique=True)
    supplier_id:Mapped[int]=mapped_column(ForeignKey("suppliers.id"))
    invoice_date:Mapped[date]=mapped_column(Date)
    status:Mapped[str]=mapped_column(String(40),default="مسودة")
    subtotal:Mapped[float]=mapped_column(Float,default=0)
    discount:Mapped[float]=mapped_column(Float,default=0)
    tax:Mapped[float]=mapped_column(Float,default=0)
    total:Mapped[float]=mapped_column(Float,default=0)
    paid:Mapped[float]=mapped_column(Float,default=0)
    notes:Mapped[str|None]=mapped_column(Text)

class PurchaseLine(Base):
    __tablename__="purchase_lines"
    id:Mapped[int]=mapped_column(primary_key=True)
    invoice_id:Mapped[int]=mapped_column(ForeignKey("purchase_invoices.id"))
    item_name:Mapped[str]=mapped_column(String(150))
    category:Mapped[str]=mapped_column(String(80),default="عام")
    quantity:Mapped[float]=mapped_column(Float)
    unit:Mapped[str]=mapped_column(String(30),default="وحدة")
    unit_price:Mapped[float]=mapped_column(Float)
    line_total:Mapped[float]=mapped_column(Float)

class SupplierPayment(Base):
    __tablename__="supplier_payments"
    id:Mapped[int]=mapped_column(primary_key=True)
    supplier_id:Mapped[int]=mapped_column(ForeignKey("suppliers.id"))
    invoice_id:Mapped[int|None]=mapped_column(ForeignKey("purchase_invoices.id"))
    payment_date:Mapped[date]=mapped_column(Date)
    amount:Mapped[float]=mapped_column(Float)
    payment_method:Mapped[str]=mapped_column(String(40),default="نقدي")
    reference:Mapped[str|None]=mapped_column(String(100))
    notes:Mapped[str|None]=mapped_column(Text)
