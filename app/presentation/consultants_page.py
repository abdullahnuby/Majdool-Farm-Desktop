from PySide6.QtWidgets import QInputDialog,QMessageBox,QTabWidget,QTableWidget,QTableWidgetItem
from app.presentation.ui_theme import PageShell,Toolbar,button,setup_table
from app.infrastructure.consultant_repository import ConsultantRepository
class ConsultantsPage(PageShell):
    def __init__(self):
        super().__init__("الاستشاريون","الزيارات والتقارير والتوصيات الزراعية.")
        self.repo=ConsultantRepository();self.content.addWidget(Toolbar("بحث في الزيارات والاستشاريين…"))
        self.table=QTableWidget(0,4);self.table.setHorizontalHeaderLabels(["الزيارة","التاريخ","الاستشاري","نوع الزيارة"]);setup_table(self.table)
        self.consultant_table=QTableWidget(0,3);self.consultant_table.setHorizontalHeaderLabels(["الكود","الاستشاري","التخصص"]);setup_table(self.consultant_table)
        self.tabs=QTabWidget();self.tabs.addTab(self.table,"الزيارات");self.tabs.addTab(self.consultant_table,"الاستشاريون");self.content.addWidget(self.tabs,1)
        for t,f,k in [("＋ استشاري",self.consultant,"primary"),("تعديل الاستشاري",self.edit_consultant,"normal"),("حذف الاستشاري",self.delete_consultant,"danger"),("زيارة جديدة",self.visit,"normal"),("تقرير زراعي",self.report,"normal")]:self.actions.addWidget(button(t,k,f))
        self.refresh()
    def refresh(self):
        rows=self.repo.visits();self._consultants=self.repo.consultants();cs={x.id:x.name for x in self._consultants};self.table.setRowCount(len(rows));self.consultant_table.setRowCount(len(self._consultants))
        for i,x in enumerate(rows):
            for j,v in enumerate([x.visit_number,x.visit_date,cs.get(x.consultant_id,"-"),x.visit_type]):self.table.setItem(i,j,QTableWidgetItem(str(v)))
        for i,x in enumerate(self._consultants):
            for j,v in enumerate([x.code,x.name,x.specialty]):self.consultant_table.setItem(i,j,QTableWidgetItem(str(v)))
    def consultant(self):
        c,ok=QInputDialog.getText(self,"استشاري جديد","الكود:")
        if not ok:return
        n,ok=QInputDialog.getText(self,"استشاري جديد","الاسم:")
        if ok and c.strip() and n.strip():
            try:self.repo.add_consultant(c,n);self.refresh()
            except Exception as e:QMessageBox.warning(self,"خطأ",str(e))
    def visit(self):
        cs=self.repo.consultants()
        if not cs:return
        try:self.repo.add_visit(consultant_id=cs[0].id);self.refresh()
        except Exception as e:QMessageBox.warning(self,"خطأ",str(e))
    def report(self):
        vs=self.repo.visits()
        if not vs:return
        title,ok=QInputDialog.getText(self,"تقرير زراعي","العنوان:")
        if not ok:return
        findings,ok=QInputDialog.getText(self,"تقرير زراعي","الملاحظات:")
        if not ok:return
        rec,ok=QInputDialog.getText(self,"تقرير زراعي","التوصيات:")
        if ok:
            try:self.repo.add_report(vs[0].id,title,findings,rec)
            except Exception as e:QMessageBox.warning(self,"خطأ",str(e))
    def selected_consultant(self):
        row=self.consultant_table.currentRow()
        if row<0 or row>=len(self._consultants):QMessageBox.information(self,"اختر استشارياً","حدد استشارياً من تبويب الاستشاريين أولاً.");return None
        return self._consultants[row]
    def edit_consultant(self):
        consultant=self.selected_consultant()
        if not consultant:return
        name,ok=QInputDialog.getText(self,"تعديل الاستشاري","الاسم:",text=consultant.name)
        if ok:
            try:self.repo.update_consultant(consultant.id,name,consultant.specialty);self.refresh()
            except Exception as error:QMessageBox.warning(self,"تعذر التعديل",str(error))
    def delete_consultant(self):
        consultant=self.selected_consultant()
        if not consultant:return
        if QMessageBox.question(self,"تأكيد الحذف",f"حذف الاستشاري {consultant.name}؟")==QMessageBox.StandardButton.Yes:
            try:self.repo.delete_consultant(consultant.id);self.refresh()
            except Exception as error:QMessageBox.warning(self,"تعذر الحذف",str(error))
