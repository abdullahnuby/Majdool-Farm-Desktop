from datetime import date
from sqlalchemy import select,func
from app.database.db import SessionLocal
from app.infrastructure.errors import db_errors
from app.domain.models_hr import Employee,Attendance,EmployeeAssignment,EmployeeAdvance,PayrollDeduction,Payroll

@db_errors
class HRRepository:
    def employees(self):
        with SessionLocal() as s: return s.scalars(select(Employee).order_by(Employee.name)).all()
    def add_employee(self,code,name,job="عامل",daily_rate=0,monthly_salary=0,phone=""):
        with SessionLocal() as s:
            if s.scalar(select(Employee).where(Employee.code==code)): raise ValueError("كود الموظف مستخدم بالفعل.")
            x=Employee(code=code,name=name,job_title=job,daily_rate=daily_rate,monthly_salary=monthly_salary,phone=phone or None)
            s.add(x);s.commit();s.refresh(x);return x
    def update_employee(self,employee_id,name,job,daily_rate,monthly_salary,status):
        if not name.strip():raise ValueError("اسم الموظف مطلوب.")
        if daily_rate<0 or monthly_salary<0:raise ValueError("الأجر لا يمكن أن يكون سالباً.")
        with SessionLocal() as s:
            x=s.get(Employee,employee_id)
            if not x:raise ValueError("الموظف غير موجود.")
            x.name=name.strip();x.job_title=job.strip() or "عامل";x.daily_rate=daily_rate;x.monthly_salary=monthly_salary;x.status=status.strip() or "نشط";s.commit();s.refresh(x);return x
    def delete_employee(self,employee_id):
        with SessionLocal() as s:
            x=s.get(Employee,employee_id)
            if not x:raise ValueError("الموظف غير موجود.")
            related=[Attendance,EmployeeAssignment,EmployeeAdvance,PayrollDeduction,Payroll]
            if any(s.scalar(select(model).where(model.employee_id==employee_id)) for model in related):raise ValueError("لا يمكن حذف موظف له سجلات مالية أو حضور.")
            s.delete(x);s.commit()
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
        """راتب واحد لكل موظف/فترة (YYYY-MM).
        الأساس: المرتب الشهري لو موجود، وإلا (الأجر اليومي × أيام الحضور في الفترة).
        السلف بتتخصم فعلياً وبتتسجل كمسدّدة (FIFO) بحد أقصى المتاح بعد الخصومات."""
        try:
            year,month=(int(x) for x in period.split("-"))
            first=date(year,month,1)
        except Exception:
            raise ValueError("الفترة لازم تكون بالشكل YYYY-MM.")
        last=date(year+(month==12),month%12+1,1)
        with SessionLocal() as s:
            e=s.get(Employee,employee_id)
            if not e: raise ValueError("الموظف غير موجود.")
            if s.scalar(select(Payroll).where(Payroll.employee_id==employee_id,Payroll.period==period)):
                raise ValueError("تم إنشاء راتب لهذا الموظف في هذه الفترة بالفعل.")
            if e.monthly_salary and e.monthly_salary>0:
                base=e.monthly_salary
            else:
                days=s.scalar(select(func.count(Attendance.id)).where(Attendance.employee_id==employee_id,Attendance.status=="حاضر",Attendance.attendance_date>=first,Attendance.attendance_date<last)) or 0
                base=days*(e.daily_rate or 0)
            d=s.scalar(select(func.coalesce(func.sum(PayrollDeduction.amount),0)).where(PayrollDeduction.employee_id==employee_id,PayrollDeduction.period==period)) or 0
            available=max(0,base-d)
            recovered_now=0
            for adv in s.scalars(select(EmployeeAdvance).where(EmployeeAdvance.employee_id==employee_id,EmployeeAdvance.status=="مفتوحة").order_by(EmployeeAdvance.advance_date,EmployeeAdvance.id)).all():
                if available-recovered_now<=0:break
                part=min(adv.amount-adv.recovered,available-recovered_now)
                if part<=0:continue
                adv.recovered+=part;recovered_now+=part
                if adv.amount-adv.recovered<=1e-9:adv.status="مسددة"
            net=base-d-recovered_now
            x=Payroll(employee_id=employee_id,period=period,base_amount=base,deductions=d,advances=recovered_now,net_amount=max(0,net))
            s.add(x);s.commit();s.refresh(x);return x
