from datetime import date
from sqlalchemy import select,func
from app.database.db import SessionLocal
from app.domain.models_hr import Employee,Attendance,EmployeeAssignment,EmployeeAdvance,PayrollDeduction,Payroll

class HRRepository:
    def employees(self):
        with SessionLocal() as s: return s.scalars(select(Employee).order_by(Employee.name)).all()
    def add_employee(self,code,name,job="عامل",daily_rate=0,monthly_salary=0,phone=""):
        with SessionLocal() as s:
            if s.scalar(select(Employee).where(Employee.code==code)): raise ValueError("كود الموظف مستخدم بالفعل.")
            x=Employee(code=code,name=name,job_title=job,daily_rate=daily_rate,monthly_salary=monthly_salary,phone=phone or None)
            s.add(x);s.commit();s.refresh(x);return x
    def mark_attendance(self,employee_id,day,status="حاضر",check_in="",check_out=""):
        with SessionLocal() as s:
            if s.scalar(select(Attendance).where(Attendance.employee_id==employee_id,Attendance.attendance_date==day)):
                raise ValueError("يوجد تسجيل حضور لهذا الموظف في نفس اليوم.")
            x=Attendance(employee_id=employee_id,attendance_date=day,status=status,check_in=check_in or None,check_out=check_out or None)
            s.add(x);s.commit();return x
    def add_assignment(self,employee_id,day,work_type,quantity,block_id=None):
        if quantity<=0: raise ValueError("كمية العمل يجب أن تكون أكبر من صفر.")
        with SessionLocal() as s:
            e=s.get(Employee,employee_id)
            if not e: raise ValueError("الموظف غير موجود.")
            x=EmployeeAssignment(employee_id=employee_id,block_id=block_id,assignment_date=day,work_type=work_type,quantity=quantity,cost=quantity*(e.daily_rate or 0))
            s.add(x);s.commit();return x
    def add_advance(self,employee_id,amount):
        if amount<=0: raise ValueError("السلفة يجب أن تكون أكبر من صفر.")
        with SessionLocal() as s:
            x=EmployeeAdvance(employee_id=employee_id,advance_date=date.today(),amount=amount);s.add(x);s.commit();return x
    def add_deduction(self,employee_id,period,amount,reason):
        if amount<=0: raise ValueError("الخصم يجب أن يكون أكبر من صفر.")
        with SessionLocal() as s:
            x=PayrollDeduction(employee_id=employee_id,period=period,amount=amount,reason=reason);s.add(x);s.commit();return x
    def create_payroll(self,employee_id,period):
        with SessionLocal() as s:
            e=s.get(Employee,employee_id)
            if not e: raise ValueError("الموظف غير موجود.")
            d=s.scalar(select(func.coalesce(func.sum(PayrollDeduction.amount),0)).where(PayrollDeduction.employee_id==employee_id,PayrollDeduction.period==period)) or 0
            a=s.scalar(select(func.coalesce(func.sum(EmployeeAdvance.amount-EmployeeAdvance.recovered),0)).where(EmployeeAdvance.employee_id==employee_id,EmployeeAdvance.status=="مفتوحة")) or 0
            base=e.monthly_salary or 0
            net=max(0,base-d-a)
            x=Payroll(employee_id=employee_id,period=period,base_amount=base,deductions=d,advances=a,net_amount=net)
            s.add(x);s.commit();s.refresh(x);return x
