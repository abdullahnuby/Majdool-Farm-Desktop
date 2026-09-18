from PySide6.QtWidgets import QTableWidget,QTableWidgetItem,QInputDialog,QMessageBox
from datetime import date
from app.presentation.ui_theme import PageShell,Toolbar,button,setup_table
from app.infrastructure.hr_repository import HRRepository
class HRPage(PageShell):
    def __init__(self):
        super().__init__("الموظفون والرواتب","الحضور والسلف والخصومات وكشوف الرواتب.")
        self.repo=HRRepository();toolbar=Toolbar("بحث عن موظف…");self.search=toolbar.search;self.content.addWidget(toolbar)
        self.table=QTableWidget(0,5);self.table.setHorizontalHeaderLabels(["الكود","الموظف","الوظيفة","الأجر اليومي","الحالة"]);setup_table(self.table);self.content.addWidget(self.table,1)
        for t,f,k in [("＋ موظف جديد",self.employee,"primary"),("تعديل الموظف",self.edit_employee,"normal"),("حذف الموظف",self.delete_employee,"danger"),("حضور اليوم",self.attendance,"normal"),("سلفة",self.advance,"normal"),("خصم",self.deduction,"normal"),("إنشاء راتب",self.payroll,"normal")]:self.actions.addWidget(button(t,k,f))
        self.search.textChanged.connect(self.filter_rows)
        self.refresh()
    def refresh(self):
        rows=self.repo.employees();self._all_employees=rows;self.filter_rows(self.search.text())

    def filter_rows(self,text):
        query=text.strip().lower()
        self._employees=[x for x in getattr(self,"_all_employees",[]) if not query or query in f"{x.code} {x.name} {x.job_title}".lower()]
        self.table.setRowCount(len(self._employees))
        rows=self._employees
        for i,x in enumerate(rows):
            for j,v in enumerate([x.code,x.name,x.job_title,x.daily_rate,x.status]):self.table.setItem(i,j,QTableWidgetItem(str(v)))
    def first(self):
        row=self.table.currentRow()
        if row < 0 or row >= len(self._employees):
            QMessageBox.information(self,"اختر موظفاً","حدد موظفاً من الجدول أولاً."); return None
        return self._employees[row]
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
            try:self.repo.add_advance(e.id,q);self.refresh()
            except Exception as ex:QMessageBox.warning(self,"خطأ",str(ex))
    def deduction(self):
        e=self.first()
        if not e:return
        q,ok=QInputDialog.getDouble(self,"خصم","المبلغ:",100,0.01,100000000,2)
        if ok:
            try:self.repo.add_deduction(e.id,date.today().strftime("%Y-%m"),q,"خصم إداري");self.refresh()

            except Exception as ex:QMessageBox.warning(self,"خطأ",str(ex))
    def payroll(self):
        e=self.first()
        if e:
            try:
                x=self.repo.create_payroll(e.id,date.today().strftime("%Y-%m"));QMessageBox.information(self,"تم",f"صافي الراتب: {x.net_amount:,.2f}")
            except Exception as ex:QMessageBox.warning(self,"خطأ",str(ex))
    def edit_employee(self):
        employee=self.first()
        if not employee:return
        name,ok=QInputDialog.getText(self,"تعديل الموظف","الاسم:",text=employee.name)
        if not ok:return
        daily,ok=QInputDialog.getDouble(self,"تعديل الموظف","الأجر اليومي:",employee.daily_rate,0,100000000,2)
        if ok:
            try:self.repo.update_employee(employee.id,name,employee.job_title,daily,employee.monthly_salary,employee.status);self.refresh()
            except Exception as error:QMessageBox.warning(self,"تعذر التعديل",str(error))
    def delete_employee(self):
        employee=self.first()
        if not employee:return
        if QMessageBox.question(self,"تأكيد الحذف",f"حذف الموظف {employee.name}؟")==QMessageBox.StandardButton.Yes:
            try:self.repo.delete_employee(employee.id);self.refresh()
            except Exception as error:QMessageBox.warning(self,"تعذر الحذف",str(error))
