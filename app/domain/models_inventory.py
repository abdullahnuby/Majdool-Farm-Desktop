from sqlalchemy import String,Integer,Float,ForeignKey,Boolean,DateTime,Text
from sqlalchemy.orm import Mapped,mapped_column
from datetime import datetime, timezone
from app.database.db import Base

class Warehouse(Base):
    __tablename__="warehouses"
    id:Mapped[int]=mapped_column(primary_key=True)
    code:Mapped[str]=mapped_column(String(50),unique=True)
    name:Mapped[str]=mapped_column(String(120))
    location:Mapped[str|None]=mapped_column(String(200))
    active:Mapped[bool]=mapped_column(Boolean,default=True)
    notes:Mapped[str|None]=mapped_column(Text)

class InventoryItem(Base):
    __tablename__="inventory_items"
    id:Mapped[int]=mapped_column(primary_key=True)
    code:Mapped[str]=mapped_column(String(60),unique=True)
    name:Mapped[str]=mapped_column(String(150))
    category:Mapped[str]=mapped_column(String(80),default="عام")
    unit:Mapped[str]=mapped_column(String(30),default="وحدة")
    min_stock:Mapped[float]=mapped_column(Float,default=0)
    active:Mapped[bool]=mapped_column(Boolean,default=True)
    notes:Mapped[str|None]=mapped_column(Text)

class InventoryMovement(Base):
    __tablename__="inventory_movements"
    id:Mapped[int]=mapped_column(primary_key=True)
    item_id:Mapped[int]=mapped_column(ForeignKey("inventory_items.id"))
    warehouse_id:Mapped[int]=mapped_column(ForeignKey("warehouses.id"))
    movement_type:Mapped[str]=mapped_column(String(50))
    quantity:Mapped[float]=mapped_column(Float)
    unit_cost:Mapped[float]=mapped_column(Float,default=0)
    movement_date:Mapped[datetime]=mapped_column(DateTime,default=lambda: datetime.now(timezone.utc))
    reference_type:Mapped[str|None]=mapped_column(String(60))
    reference_id:Mapped[int|None]=mapped_column(Integer)
    notes:Mapped[str|None]=mapped_column(Text)
