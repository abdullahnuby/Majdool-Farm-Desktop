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
        self.actions.addWidget(button("＋ أصل جديد","primary",self.add_asset));self.actions.addWidget(button("تعديل","normal",self.edit_asset));self.actions.addWidget(button("حذف","danger",self.delete_asset))
        self.search.textChanged.connect(self.filter_rows)
        self._rows=[];self._visible_assets=[]
        self.refresh()

    def refresh(self):
        self._assets=self.repo.assets();self._rows=[[x.code,x.name,x.asset_type,x.status] for x in self._assets]
        self.filter_rows(self.search.text())

    def filter_rows(self,text):
        query=text.strip().lower()
        matches=[(asset,row) for asset,row in zip(self._assets,self._rows) if not query or query in " ".join(map(str,row)).lower()]
        self._visible_assets=[asset for asset,row in matches];rows=[row for asset,row in matches]
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

    def selected_asset(self):
        row=self.table.currentRow()
        if row<0 or row>=len(self._visible_assets):
            QMessageBox.information(self,"اختر أصلًا","حدد أصلًا من الجدول أولاً.");return None
        return self._visible_assets[row]

    def edit_asset(self):
        asset=self.selected_asset()
        if not asset:return
        name,ok=QInputDialog.getText(self,"تعديل أصل","الاسم:",text=asset.name)
        if not ok:return
        status,ok=QInputDialog.getText(self,"تعديل أصل","الحالة:",text=asset.status)
        if ok:
            try:self.repo.update_asset(asset.id,name,asset.asset_type,status);self.refresh()
            except Exception as error:QMessageBox.warning(self,"تعذر التعديل",str(error))

    def delete_asset(self):
        asset=self.selected_asset()
        if not asset:return
        answer=QMessageBox.question(self,"تأكيد الحذف",f"حذف الأصل {asset.name}؟")
        if answer==QMessageBox.StandardButton.Yes:
            try:self.repo.delete_asset(asset.id);self.refresh()
            except Exception as error:QMessageBox.warning(self,"تعذر الحذف",str(error))
