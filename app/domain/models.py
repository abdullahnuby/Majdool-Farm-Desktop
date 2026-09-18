from datetime import date, datetime, timezone
from sqlalchemy import String,Integer,Float,Date,DateTime,ForeignKey,Text,Boolean
from sqlalchemy.orm import Mapped,mapped_column
from app.database.db import Base
class Farm(Base):
 __tablename__="farms";id:Mapped[int]=mapped_column(primary_key=True);name:Mapped[str]=mapped_column(String(150),unique=True);location:Mapped[str|None]=mapped_column(String(250));area:Mapped[float]=mapped_column(Float,default=0);area_unit:Mapped[str]=mapped_column(String(20),default="فدان");notes:Mapped[str|None]=mapped_column(Text);active:Mapped[bool]=mapped_column(Boolean,default=True)
class Sector(Base):
 __tablename__="sectors";id:Mapped[int]=mapped_column(primary_key=True);farm_id:Mapped[int]=mapped_column(ForeignKey("farms.id"));name:Mapped[str]=mapped_column(String(100));notes:Mapped[str|None]=mapped_column(Text)
class Block(Base):
 __tablename__="blocks";id:Mapped[int]=mapped_column(primary_key=True);sector_id:Mapped[int]=mapped_column(ForeignKey("sectors.id"));code:Mapped[str]=mapped_column(String(50));name:Mapped[str]=mapped_column(String(100));area:Mapped[float]=mapped_column(Float,default=0);palm_count:Mapped[int]=mapped_column(Integer,default=0);notes:Mapped[str|None]=mapped_column(Text)
class FarmRow(Base):
 __tablename__="farm_rows";id:Mapped[int]=mapped_column(primary_key=True);block_id:Mapped[int]=mapped_column(ForeignKey("blocks.id"));name:Mapped[str]=mapped_column(String(100));palm_count:Mapped[int]=mapped_column(Integer,default=0)
class Palm(Base):
 __tablename__="palms";id:Mapped[int]=mapped_column(primary_key=True);row_id:Mapped[int]=mapped_column(ForeignKey("farm_rows.id"));code:Mapped[str]=mapped_column(String(80),unique=True);variety:Mapped[str]=mapped_column(String(80),default="مجدول");planting_date:Mapped[date|None]=mapped_column(Date);status:Mapped[str]=mapped_column(String(50),default="سليمة");productive:Mapped[bool]=mapped_column(Boolean,default=False);notes:Mapped[str|None]=mapped_column(Text)
class AuditLog(Base):
 __tablename__="audit_logs";id:Mapped[int]=mapped_column(primary_key=True);action:Mapped[str]=mapped_column(String(100));entity:Mapped[str]=mapped_column(String(100));entity_id:Mapped[int|None]=mapped_column(Integer);details:Mapped[str|None]=mapped_column(Text);created_at:Mapped[datetime]=mapped_column(DateTime,default=lambda: datetime.now(timezone.utc))
class CropSeason(Base):
 __tablename__="crop_seasons";id:Mapped[int]=mapped_column(primary_key=True);name:Mapped[str]=mapped_column(String(100),unique=True);start_date:Mapped[date]=mapped_column(Date);end_date:Mapped[date|None]=mapped_column(Date);status:Mapped[str]=mapped_column(String(40),default="مفتوح");notes:Mapped[str|None]=mapped_column(Text)
class HarvestBatch(Base):
 __tablename__="harvest_batches";id:Mapped[int]=mapped_column(primary_key=True);number:Mapped[str]=mapped_column(String(60),unique=True);season_id:Mapped[int]=mapped_column(ForeignKey("crop_seasons.id"));block_id:Mapped[int]=mapped_column(ForeignKey("blocks.id"));harvest_date:Mapped[date]=mapped_column(Date);variety:Mapped[str]=mapped_column(String(80),default="مجدول");palm_count:Mapped[int]=mapped_column(Integer,default=0);workers:Mapped[int]=mapped_column(Integer,default=0);gross_kg:Mapped[float]=mapped_column(Float,default=0);boxes:Mapped[int]=mapped_column(Integer,default=0);labor_cost:Mapped[float]=mapped_column(Float,default=0);responsible:Mapped[str|None]=mapped_column(String(120));notes:Mapped[str|None]=mapped_column(Text)
class SortLine(Base):
 __tablename__="sort_lines";id:Mapped[int]=mapped_column(primary_key=True);batch_id:Mapped[int]=mapped_column(ForeignKey("harvest_batches.id"));grade:Mapped[str]=mapped_column(String(50));quantity_kg:Mapped[float]=mapped_column(Float,default=0)
class PackingBatch(Base):
 __tablename__="packing_batches";id:Mapped[int]=mapped_column(primary_key=True);number:Mapped[str]=mapped_column(String(60),unique=True);batch_id:Mapped[int]=mapped_column(ForeignKey("harvest_batches.id"));packing_date:Mapped[date]=mapped_column(Date);package_type:Mapped[str]=mapped_column(String(80));package_weight_kg:Mapped[float]=mapped_column(Float,default=0);package_count:Mapped[int]=mapped_column(Integer,default=0);total_kg:Mapped[float]=mapped_column(Float,default=0);packing_cost:Mapped[float]=mapped_column(Float,default=0);responsible:Mapped[str|None]=mapped_column(String(120))
class CropMovement(Base):
 __tablename__="crop_movements";id:Mapped[int]=mapped_column(primary_key=True);batch_id:Mapped[int]=mapped_column(ForeignKey("harvest_batches.id"));movement_type:Mapped[str]=mapped_column(String(40));quantity_kg:Mapped[float]=mapped_column(Float);movement_date:Mapped[datetime]=mapped_column(DateTime,default=lambda: datetime.now(timezone.utc));reference_type:Mapped[str|None]=mapped_column(String(60));reference_id:Mapped[int|None]=mapped_column(Integer);notes:Mapped[str|None]=mapped_column(Text)
class Customer(Base):
 __tablename__="customers";id:Mapped[int]=mapped_column(primary_key=True);code:Mapped[str]=mapped_column(String(60),unique=True);name:Mapped[str]=mapped_column(String(150));phone:Mapped[str|None]=mapped_column(String(50));email:Mapped[str|None]=mapped_column(String(120));address:Mapped[str|None]=mapped_column(String(250));tax_number:Mapped[str|None]=mapped_column(String(80));credit_limit:Mapped[float]=mapped_column(Float,default=0);notes:Mapped[str|None]=mapped_column(Text);active:Mapped[bool]=mapped_column(Boolean,default=True)
class SalesInvoice(Base):
 __tablename__="sales_invoices";id:Mapped[int]=mapped_column(primary_key=True);number:Mapped[str]=mapped_column(String(60),unique=True);customer_id:Mapped[int]=mapped_column(ForeignKey("customers.id"));invoice_date:Mapped[date]=mapped_column(Date);status:Mapped[str]=mapped_column(String(40),default="مسودة");discount:Mapped[float]=mapped_column(Float,default=0);tax:Mapped[float]=mapped_column(Float,default=0);subtotal:Mapped[float]=mapped_column(Float,default=0);total:Mapped[float]=mapped_column(Float,default=0);notes:Mapped[str|None]=mapped_column(Text)
class SalesInvoiceLine(Base):
 __tablename__="sales_invoice_lines";id:Mapped[int]=mapped_column(primary_key=True);invoice_id:Mapped[int]=mapped_column(ForeignKey("sales_invoices.id"));batch_id:Mapped[int]=mapped_column(ForeignKey("harvest_batches.id"));grade:Mapped[str]=mapped_column(String(50));quantity_kg:Mapped[float]=mapped_column(Float);unit_price:Mapped[float]=mapped_column(Float);line_total:Mapped[float]=mapped_column(Float)
class Receipt(Base):
 __tablename__="receipts";id:Mapped[int]=mapped_column(primary_key=True);number:Mapped[str]=mapped_column(String(60),unique=True);customer_id:Mapped[int]=mapped_column(ForeignKey("customers.id"));invoice_id:Mapped[int|None]=mapped_column(ForeignKey("sales_invoices.id"));receipt_date:Mapped[date]=mapped_column(Date);amount:Mapped[float]=mapped_column(Float);payment_method:Mapped[str]=mapped_column(String(40),default="نقدي");reference:Mapped[str|None]=mapped_column(String(100));notes:Mapped[str|None]=mapped_column(Text)

class AgriculturalOperation(Base):
 __tablename__="agricultural_operations";id:Mapped[int]=mapped_column(primary_key=True);operation_type:Mapped[str]=mapped_column(String(80));operation_date:Mapped[date]=mapped_column(Date);block_id:Mapped[int|None]=mapped_column(ForeignKey("blocks.id"));status:Mapped[str]=mapped_column(String(40),default="مفتوح");responsible:Mapped[str|None]=mapped_column(String(120));cost:Mapped[float]=mapped_column(Float,default=0);notes:Mapped[str|None]=mapped_column(Text)

class Asset(Base):
 __tablename__="assets";id:Mapped[int]=mapped_column(primary_key=True);code:Mapped[str]=mapped_column(String(60),unique=True);name:Mapped[str]=mapped_column(String(150));asset_type:Mapped[str]=mapped_column(String(80),default="معدات");status:Mapped[str]=mapped_column(String(40),default="متاح");purchase_date:Mapped[date|None]=mapped_column(Date);notes:Mapped[str|None]=mapped_column(Text)

class MaintenanceOrder(Base):
 __tablename__="maintenance_orders";id:Mapped[int]=mapped_column(primary_key=True);asset_id:Mapped[int|None]=mapped_column(ForeignKey("assets.id"));title:Mapped[str]=mapped_column(String(150));opened_date:Mapped[date]=mapped_column(Date);status:Mapped[str]=mapped_column(String(40),default="مفتوح");priority:Mapped[str]=mapped_column(String(40),default="متوسطة");cost:Mapped[float]=mapped_column(Float,default=0);notes:Mapped[str|None]=mapped_column(Text)

class IrrigationRecord(Base):
 __tablename__="irrigation_records";id:Mapped[int]=mapped_column(primary_key=True);block_id:Mapped[int|None]=mapped_column(ForeignKey("blocks.id"));irrigation_date:Mapped[date]=mapped_column(Date);method:Mapped[str]=mapped_column(String(80),default="تنقيط");quantity:Mapped[float]=mapped_column(Float);unit:Mapped[str]=mapped_column(String(30),default="متر مكعب");status:Mapped[str]=mapped_column(String(40),default="منفذ");responsible:Mapped[str|None]=mapped_column(String(120));notes:Mapped[str|None]=mapped_column(Text)

class FertilizationRecord(Base):
 __tablename__="fertilization_records";id:Mapped[int]=mapped_column(primary_key=True);block_id:Mapped[int|None]=mapped_column(ForeignKey("blocks.id"));fertilization_date:Mapped[date]=mapped_column(Date);product:Mapped[str]=mapped_column(String(120));quantity:Mapped[float]=mapped_column(Float);unit:Mapped[str]=mapped_column(String(30),default="كجم");status:Mapped[str]=mapped_column(String(40),default="منفذ");responsible:Mapped[str|None]=mapped_column(String(120));notes:Mapped[str|None]=mapped_column(Text)

from app.domain.models_hr import Employee,Attendance,EmployeeAssignment,EmployeeAdvance,PayrollDeduction,Payroll

from app.domain.models_consultants import Consultant,FarmVisit,AgriculturalReport

from app.domain.models_purchases import Supplier,PurchaseInvoice,PurchaseLine,SupplierPayment

from app.domain.models_inventory import Warehouse,InventoryItem,InventoryMovement
