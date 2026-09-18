from datetime import date
from sqlalchemy import select,func
from app.database.db import SessionLocal
from app.domain.models_consultants import Consultant,FarmVisit,AgriculturalReport

class ConsultantRepository:
    def consultants(self):
        with SessionLocal() as s:return s.scalars(select(Consultant).order_by(Consultant.name)).all()
    def visits(self):
        with SessionLocal() as s:return s.scalars(select(FarmVisit).order_by(FarmVisit.visit_date.desc())).all()
    def reports(self):
        with SessionLocal() as s:return s.scalars(select(AgriculturalReport).order_by(AgriculturalReport.report_date.desc())).all()
    def add_consultant(self,code,name,specialty="زراعي",phone=""):
        with SessionLocal() as s:
            if s.scalar(select(Consultant).where(Consultant.code==code)):raise ValueError("كود الاستشاري مستخدم بالفعل.")
            x=Consultant(code=code,name=name,specialty=specialty,phone=phone or None);s.add(x);s.commit();s.refresh(x);return x
    def update_consultant(self,consultant_id,name,specialty):
        if not name.strip():raise ValueError("اسم الاستشاري مطلوب.")
        with SessionLocal() as s:
            x=s.get(Consultant,consultant_id)
            if not x:raise ValueError("الاستشاري غير موجود.")
            x.name=name.strip();x.specialty=specialty.strip() or "زراعي";s.commit();s.refresh(x);return x
    def delete_consultant(self,consultant_id):
        with SessionLocal() as s:
            x=s.get(Consultant,consultant_id)
            if not x:raise ValueError("الاستشاري غير موجود.")
            if s.scalar(select(FarmVisit).where(FarmVisit.consultant_id==consultant_id)):raise ValueError("لا يمكن حذف استشاري مرتبط بزيارات.")
            s.delete(x);s.commit()
    def add_visit(self,consultant_id=None,block_id=None,visit_type="زيارة دورية",purpose="",observations="",recommendations=""):
        with SessionLocal() as s:
            n=f"VIS-{date.today().strftime('%Y%m%d')}-{(s.scalar(select(func.count(FarmVisit.id))) or 0)+1:04d}"
            x=FarmVisit(visit_number=n,visit_date=date.today(),consultant_id=consultant_id,block_id=block_id,visit_type=visit_type,purpose=purpose or None,observations=observations or None,recommendations=recommendations or None)
            s.add(x);s.commit();s.refresh(x);return x
    def add_report(self,visit_id,title,findings,recommendations,priority="متوسطة"):
        with SessionLocal() as s:
            n=f"AGR-{date.today().strftime('%Y%m%d')}-{(s.scalar(select(func.count(AgriculturalReport.id))) or 0)+1:04d}"
            x=AgriculturalReport(report_number=n,report_date=date.today(),visit_id=visit_id,title=title,findings=findings,recommendations=recommendations,priority=priority)
            s.add(x);s.commit();s.refresh(x);return x
