from PySide6.QtWidgets import QComboBox,QMessageBox,QTabWidget,QTableWidget,QTableWidgetItem,QDialog
from app.presentation.ui_theme import PageShell,Toolbar,button,setup_table,FormDialog
from app.infrastructure.operations_repository import OperationsRepository
class OperationsPage(PageShell):
    def __init__(self):
        super().__init__("العمليات الزراعية والصيانة","أوامر العمل، الصيانة وتكلفة التنفيذ.")
        self.repo=OperationsRepository()
        toolbar=Toolbar("بحث في العمليات والأصول والصيانة…")
        self.search=toolbar.search
        self.content.addWidget(toolbar)
        self.tabs=QTabWidget()
        self.operations_table=self._table(["النوع","التاريخ","المسؤول","التكلفة","الحالة"])
        self.assets_table=self._table(["الكود","الأصل","النوع","الحالة"])
        self.orders_table=self._table(["العنوان","تاريخ الفتح","الأولوية","الحالة"])
        self.tabs.addTab(self.operations_table,"العمليات الزراعية")
        self.tabs.addTab(self.assets_table,"الأصول")
        self.tabs.addTab(self.orders_table,"أوامر الصيانة")
        self.content.addWidget(self.tabs,1)
        self.actions.addWidget(button("＋ عملية زراعية","primary",self.add_operation))
        self.actions.addWidget(button("＋ أصل", "normal", self.add_asset))
        self.actions.addWidget(button("＋ أمر صيانة", "normal", self.add_order))
        self.actions.addWidget(button("تحديث حالة الأمر", "normal", self.update_order_status))
        self.search.textChanged.connect(self.filter_rows)
        self._rows={}
        self.refresh()

    def _table(self,headers):
        table=QTableWidget(0,len(headers)); table.setHorizontalHeaderLabels(headers); setup_table(table); return table

    def refresh(self):
        orders=self.repo.orders();self._orders=orders
        self._rows={
            "operations":[[x.operation_type,x.operation_date,x.responsible or "-",x.cost,x.status] for x in self.repo.operations()],
            "assets":[[x.code,x.name,x.asset_type,x.status] for x in self.repo.assets()],
            "orders":[[x.title,x.opened_date,x.priority,x.status] for x in orders],
        }
        self.filter_rows(self.search.text())

    def filter_rows(self,text):
        query=text.strip().lower()
        for key,table in [("operations",self.operations_table),("assets",self.assets_table),("orders",self.orders_table)]:
            rows=[row for row in self._rows.get(key,[]) if not query or query in " ".join(map(str,row)).lower()]
            table.setRowCount(len(rows))
            for i,row in enumerate(rows):
                for j,value in enumerate(row):table.setItem(i,j,QTableWidgetItem(str(value)))
            self._visible_orders=[order for order,row in zip(self._orders,self._rows.get("orders",[])) if not query or query in " ".join(map(str,row)).lower()]

    def add_operation(self):
        dialog = FormDialog("عملية زراعية", [("نوع العملية", "text", ""), ("التكلفة", "number", 0)], self)
        if dialog.exec() != dialog.Accepted:
            return
        values = dialog.values()
        if values["نوع العملية"].strip():
            try:self.repo.add_operation(values["نوع العملية"], cost=values["التكلفة"]);self.refresh()
            except Exception as error:QMessageBox.warning(self,"تعذر الحفظ",str(error))

    def add_asset(self):
        dialog = FormDialog("أصل جديد", [("الكود", "text", ""), ("الاسم", "text", "")], self)
        if dialog.exec() != dialog.Accepted:
            return
        values = dialog.values()
        if values["الكود"].strip() and values["الاسم"].strip():
            try:self.repo.add_asset(values["الكود"], values["الاسم"]);self.refresh()
            except Exception as error:QMessageBox.warning(self,"تعذر الحفظ",str(error))

    def add_order(self):
        dialog = FormDialog("أمر صيانة", [("عنوان الأمر", "text", "")], self)
        if dialog.exec() != dialog.Accepted:
            return
        title = dialog.values()["عنوان الأمر"]
        if title.strip():
            try:self.repo.add_order(title);self.refresh()
            except Exception as error:QMessageBox.warning(self,"تعذر الحفظ",str(error))

    def update_order_status(self):
        row=self.orders_table.currentRow()
        if row<0 or row>=len(self._visible_orders):
            QMessageBox.information(self,"اختر أمرًا","حدد أمر صيانة من تبويب أوامر الصيانة أولاً.");return
        dialog = FormDialog("حالة الأمر", [("الحالة", "combo", "مفتوح", [("مفتوح", "مفتوح"), ("قيد التنفيذ", "قيد التنفيذ"), ("مكتمل", "مكتمل"), ("ملغي", "ملغي")])], self)
        if dialog.exec() != dialog.Accepted:
            return
        status = dialog.values()["الحالة"]
        try:self.repo.update_order_status(self._visible_orders[row].id,status);self.refresh()
        except Exception as error:QMessageBox.warning(self,"تعذر التحديث",str(error))
