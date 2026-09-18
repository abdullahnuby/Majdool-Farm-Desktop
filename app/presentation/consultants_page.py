from PySide6.QtWidgets import QTableWidget,QTableWidgetItem,QInputDialog,QMessageBox
from app.presentation.ui_theme import PageShell,Toolbar,button,setup_table
from app.infrastructure.consultant_repository import ConsultantRepository
class ConsultantsPage(PageShell):
    def __init__(self):
        super().__init__("الاستشاريون","الزيارات والتقارير والتوصيات الزراعية.")
        self.repo=ConsultantRepository();self.content.addWidget(Toolbar("بحث في الزيارات…"))
        self.table=QTableWidget(0,4);self.table.setHorizontalHeaderLabels(["الزيارة","التاريخ","الاستشاري","نوع الزيارة"]);setup_table(self.table);self.content.addWidget(self.table,1)
        for t,f,k in [("＋ استشاري",self.consultant,"primary"),("زيارة جديدة",self.visit,"normal"),("تقرير زراعي",self.report,"normal")]:self.actions.addWidget(button(t,k,f))
        self.refresh()
    def refresh(self):
        rows=self.repo.visits();cs={x.id:x.name for x in self.repo.consultants()};self.table.setRowCount(len(rows))
        for i,x in enumerate(rows):
            for j,v in enumerate([x.visit_number,x.visit_date,cs.get(x.consultant_id,"-"),x.visit_type]):self.table.setItem(i,j,QTableWidgetItem(str(v)))
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
