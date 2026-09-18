from PySide6.QtWidgets import QTableWidget,QTableWidgetItem,QInputDialog,QMessageBox
from datetime import date
from app.presentation.ui_theme import PageShell,Toolbar,button,setup_table
from app.infrastructure.hr_repository import HRRepository
class HRPage(PageShell):
    def __init__(self):
        super().__init__("الموظفون والرواتب","الحضور والسلف والخصومات وكشوف الرواتب.")
        self.repo=HRRepository();self.content.addWidget(Toolbar("بحث عن موظف…"))
        self.table=QTableWidget(0,5);self.table.setHorizontalHeaderLabels(["الكود","الموظف","الوظيفة","الأجر اليومي","الحالة"]);setup_table(self.table);self.content.addWidget(self.table,1)
        for t,f,k in [("＋ موظف جديد",self.employee,"primary"),("حضور اليوم",self.attendance,"normal"),("سلفة",self.advance,"normal"),("خصم",self.deduction,"normal"),("إنشاء راتب",self.payroll,"normal")]:self.actions.addWidget(button(t,k,f))
        self.refresh()
    def refresh(self):
        rows=self.repo.employees();self.table.setRowCount(len(rows))
        for i,x in enumerate(rows):
            for j,v in enumerate([x.code,x.name,x.job_title,x.daily_rate,x.status]):self.table.setItem(i,j,QTableWidgetItem(str(v)))
    def first(self):
        xs=self.repo.employees()
        if not xs:QMessageBox.information(self,"تنبيه","أضف موظفاً أولاً.");return None
        return xs[0]
    def employee(self):
        c,ok=QInputDialog.getText(self,"موظف جديد","الكود:")
        if not ok:return
        n,ok=QInputDialog.getText(self,"موظف جديد","الاسم:")
        if ok:
            try:self.repo.add_employee(c,n);self.refresh()
            except Exception as e:QMessageBox.warning(self,"خطأ",str(e))
    def attendance(self):
        e=self.first()
        if e:
            try:self.repo.mark_attendance(e.id,date.today());self.refresh()
            except Exception as ex:QMessageBox.warning(self,"خطأ",str(ex))
    def advance(self):
        e=self.first()
        if not e:return
        q,ok=QInputDialog.getDouble(self,"سلفة","المبلغ:",100,0.01,100000000,2)
        if ok:
            try:self.repo.add_advance(e.id,q)
            except Exception as ex:QMessageBox.warning(self,"خطأ",str(ex))
    def deduction(self):
        e=self.first()
        if not e:return
        q,ok=QInputDialog.getDouble(self,"خصم","المبلغ:",100,0.01,100000000,2)
        if ok:
            try:self.repo.add_deduction(e.id,date.today().strftime("%Y-%m"),q,"خصم إداري")
            except Exception as ex:QMessageBox.warning(self,"خطأ",str(ex))
    def payroll(self):
        e=self.first()
        if e:
            try:
                x=self.repo.create_payroll(e.id,date.today().strftime("%Y-%m"));QMessageBox.information(self,"تم",f"صافي الراتب: {x.net_amount:,.2f}")
            except Exception as ex:QMessageBox.warning(self,"خطأ",str(ex))
