from datetime import date
from sqlalchemy import String,Integer,Float,Date,Text,ForeignKey
from sqlalchemy.orm import Mapped,mapped_column
from app.database.db import Base

class Employee(Base):
    __tablename__="employees"
    id:Mapped[int]=mapped_column(primary_key=True)
    code:Mapped[str]=mapped_column(String(60),unique=True)
    name:Mapped[str]=mapped_column(String(150))
    job_title:Mapped[str]=mapped_column(String(100),default="عامل")
    phone:Mapped[str|None]=mapped_column(String(50))
    hire_date:Mapped[date|None]=mapped_column(Date)
    monthly_salary:Mapped[float]=mapped_column(Float,default=0)
    daily_rate:Mapped[float]=mapped_column(Float,default=0)
    status:Mapped[str]=mapped_column(String(40),default="نشط")
    notes:Mapped[str|None]=mapped_column(Text)

class Attendance(Base):
    __tablename__="attendance"
    id:Mapped[int]=mapped_column(primary_key=True)
    employee_id:Mapped[int]=mapped_column(ForeignKey("employees.id"))
    attendance_date:Mapped[date]=mapped_column(Date)
    check_in:Mapped[str|None]=mapped_column(String(10))
    check_out:Mapped[str|None]=mapped_column(String(10))
    status:Mapped[str]=mapped_column(String(40),default="حاضر")
    notes:Mapped[str|None]=mapped_column(Text)

class EmployeeAssignment(Base):
    __tablename__="employee_assignments"
    id:Mapped[int]=mapped_column(primary_key=True)
    employee_id:Mapped[int]=mapped_column(ForeignKey("employees.id"))
    block_id:Mapped[int|None]=mapped_column(ForeignKey("blocks.id"))
    assignment_date:Mapped[date]=mapped_column(Date)
    work_type:Mapped[str]=mapped_column(String(100))
    quantity:Mapped[float]=mapped_column(Float,default=0)
    unit:Mapped[str]=mapped_column(String(30),default="يوم")
    cost:Mapped[float]=mapped_column(Float,default=0)
    notes:Mapped[str|None]=mapped_column(Text)

class EmployeeAdvance(Base):
    __tablename__="employee_advances"
    id:Mapped[int]=mapped_column(primary_key=True)
    employee_id:Mapped[int]=mapped_column(ForeignKey("employees.id"))
    advance_date:Mapped[date]=mapped_column(Date)
    amount:Mapped[float]=mapped_column(Float)
    recovered:Mapped[float]=mapped_column(Float,default=0)
    status:Mapped[str]=mapped_column(String(40),default="مفتوحة")
    notes:Mapped[str|None]=mapped_column(Text)

class PayrollDeduction(Base):
    __tablename__="payroll_deductions"
    id:Mapped[int]=mapped_column(primary_key=True)
    employee_id:Mapped[int]=mapped_column(ForeignKey("employees.id"))
    period:Mapped[str]=mapped_column(String(20))
    amount:Mapped[float]=mapped_column(Float)
    reason:Mapped[str]=mapped_column(String(200))
    notes:Mapped[str|None]=mapped_column(Text)

class Payroll(Base):
    __tablename__="payrolls"
    id:Mapped[int]=mapped_column(primary_key=True)
    employee_id:Mapped[int]=mapped_column(ForeignKey("employees.id"))
    period:Mapped[str]=mapped_column(String(20))
    base_amount:Mapped[float]=mapped_column(Float)
    additions:Mapped[float]=mapped_column(Float,default=0)
    deductions:Mapped[float]=mapped_column(Float,default=0)
    advances:Mapped[float]=mapped_column(Float,default=0)
    net_amount:Mapped[float]=mapped_column(Float)
    status:Mapped[str]=mapped_column(String(40),default="مسودة")
    notes:Mapped[str|None]=mapped_column(Text)
