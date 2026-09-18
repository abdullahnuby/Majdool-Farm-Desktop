from PySide6.QtWidgets import QMessageBox,QTabWidget,QTableWidget,QTableWidgetItem,QDialog
from app.presentation.ui_theme import PageShell,Toolbar,button,setup_table,FormDialog
from app.infrastructure.agriculture_repository import AgricultureRepository
class AgriculturePage(PageShell):
    def __init__(self):
        super().__init__("الري والتسميد","خطط الري والتسميد ومتابعة التنفيذ.")
        self.repo=AgricultureRepository()
        toolbar=Toolbar("بحث في سجلات الري والتسميد…");self.search=toolbar.search;self.content.addWidget(toolbar)
        self.tabs=QTabWidget()
        self.irrigation_table=self._table(["التاريخ","الطريقة","الكمية","الوحدة","الحالة"])
        self.fertilization_table=self._table(["التاريخ","السماد","الكمية","الوحدة","الحالة"])
        self.tabs.addTab(self.irrigation_table,"الري")
        self.tabs.addTab(self.fertilization_table,"التسميد")
        self.content.addWidget(self.tabs,1)
        self.actions.addWidget(button("＋ سجل ري","primary",self.add_irrigation))
        self.actions.addWidget(button("＋ سجل تسميد","normal",self.add_fertilization))
        self.search.textChanged.connect(self.filter_rows)
        self._rows={};self.refresh()

    def _table(self,headers):
        table=QTableWidget(0,len(headers));table.setHorizontalHeaderLabels(headers);setup_table(table);return table

    def refresh(self):
        self._rows={
            "irrigation":[[x.irrigation_date,x.method,x.quantity,x.unit,x.status] for x in self.repo.irrigations()],
            "fertilization":[[x.fertilization_date,x.product,x.quantity,x.unit,x.status] for x in self.repo.fertilizations()],
        }
        self.filter_rows(self.search.text())

    def filter_rows(self,text):
        query=text.strip().lower()
        for key,table in [("irrigation",self.irrigation_table),("fertilization",self.fertilization_table)]:
            rows=[row for row in self._rows.get(key,[]) if not query or query in " ".join(map(str,row)).lower()]
            table.setRowCount(len(rows))
            for i,row in enumerate(rows):
                for j,value in enumerate(row):table.setItem(i,j,QTableWidgetItem(str(value)))

    def add_irrigation(self):
        dialog = FormDialog("سجل ري", [("طريقة الري", "text", "تنقيط"), ("الكمية", "number", 1)], self)
        if dialog.exec() != dialog.Accepted:
            return
        values = dialog.values()
        try:self.repo.add_irrigation(values["الكمية"], method=values["طريقة الري"]);self.refresh()
        except Exception as error:QMessageBox.warning(self,"تعذر الحفظ",str(error))

    def add_fertilization(self):
        dialog = FormDialog("سجل تسميد", [("اسم السماد", "text", ""), ("الكمية", "number", 1)], self)
        if dialog.exec() != dialog.Accepted:
            return
        values = dialog.values()
        try:self.repo.add_fertilization(values["اسم السماد"], values["الكمية"]);self.refresh()
        except Exception as error:QMessageBox.warning(self,"تعذر الحفظ",str(error))
