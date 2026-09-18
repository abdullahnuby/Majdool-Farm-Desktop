from datetime import date
from sqlalchemy import String,Integer,Date,Text,ForeignKey
from sqlalchemy.orm import Mapped,mapped_column
from app.database.db import Base

class Consultant(Base):
    __tablename__="consultants"
    id:Mapped[int]=mapped_column(primary_key=True)
    code:Mapped[str]=mapped_column(String(60),unique=True)
    name:Mapped[str]=mapped_column(String(150))
    specialty:Mapped[str]=mapped_column(String(120),default="زراعي")
    phone:Mapped[str|None]=mapped_column(String(50))
    organization:Mapped[str|None]=mapped_column(String(150))
    notes:Mapped[str|None]=mapped_column(Text)

class FarmVisit(Base):
    __tablename__="farm_visits"
    id:Mapped[int]=mapped_column(primary_key=True)
    visit_number:Mapped[str]=mapped_column(String(60),unique=True)
    visit_date:Mapped[date]=mapped_column(Date)
    consultant_id:Mapped[int|None]=mapped_column(ForeignKey("consultants.id"))
    block_id:Mapped[int|None]=mapped_column(ForeignKey("blocks.id"))
    visit_type:Mapped[str]=mapped_column(String(100),default="زيارة دورية")
    purpose:Mapped[str|None]=mapped_column(Text)
    observations:Mapped[str|None]=mapped_column(Text)
    recommendations:Mapped[str|None]=mapped_column(Text)
    status:Mapped[str]=mapped_column(String(40),default="مفتوحة")

class AgriculturalReport(Base):
    __tablename__="agricultural_reports"
    id:Mapped[int]=mapped_column(primary_key=True)
    report_number:Mapped[str]=mapped_column(String(60),unique=True)
    report_date:Mapped[date]=mapped_column(Date)
    visit_id:Mapped[int|None]=mapped_column(ForeignKey("farm_visits.id"))
    title:Mapped[str]=mapped_column(String(200))
    findings:Mapped[str|None]=mapped_column(Text)
    recommendations:Mapped[str|None]=mapped_column(Text)
    priority:Mapped[str]=mapped_column(String(30),default="متوسطة")
    status:Mapped[str]=mapped_column(String(40),default="جديد")
