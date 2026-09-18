from PySide6.QtWidgets import QInputDialog,QMessageBox,QTableWidget,QTableWidgetItem
from app.presentation.ui_theme import PageShell,Toolbar,button,setup_table
from app.infrastructure.operations_repository import OperationsRepository


class AssetsPage(PageShell):
    def __init__(self):
        super().__init__("الأصول والمعدات","الأصول المسجلة وحالتها التشغيلية.")
        self.repo=OperationsRepository()
        toolbar=Toolbar("بحث بكود الأصل أو اسمه…")
        self.search=toolbar.search
        self.content.addWidget(toolbar)
        self.table=QTableWidget(0,4)
        self.table.setHorizontalHeaderLabels(["الكود","الأصل","النوع","الحالة"])
        setup_table(self.table)
        self.content.addWidget(self.table,1)
        self.actions.addWidget(button("＋ أصل جديد","primary",self.add_asset))
        self.search.textChanged.connect(self.filter_rows)
        self._rows=[]
        self.refresh()

    def refresh(self):
        self._rows=[[x.code,x.name,x.asset_type,x.status] for x in self.repo.assets()]
        self.filter_rows(self.search.text())

    def filter_rows(self,text):
        query=text.strip().lower()
        rows=[row for row in self._rows if not query or query in " ".join(map(str,row)).lower()]
        self.table.setRowCount(len(rows))
        for row_index,row in enumerate(rows):
            for column,value in enumerate(row):
                self.table.setItem(row_index,column,QTableWidgetItem(str(value)))

    def add_asset(self):
        code,ok=QInputDialog.getText(self,"أصل جديد","الكود:")
        if not ok:
            return
        name,ok=QInputDialog.getText(self,"أصل جديد","الاسم:")
        if ok and code.strip() and name.strip():
            try:
                self.repo.add_asset(code,name)
                self.refresh()
            except Exception as error:
                QMessageBox.warning(self,"تعذر الحفظ",str(error))
