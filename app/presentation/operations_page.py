from PySide6.QtWidgets import QComboBox,QInputDialog,QMessageBox,QTabWidget,QTableWidget,QTableWidgetItem
from app.presentation.ui_theme import PageShell,Toolbar,button,setup_table
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
        value,ok=QInputDialog.getText(self,"عملية زراعية","نوع العملية:")
        if not ok or not value.strip():return
        cost,ok=QInputDialog.getDouble(self,"عملية زراعية","التكلفة:",0,0,100000000,2)
        if ok:
            try:self.repo.add_operation(value,cost=cost);self.refresh()
            except Exception as error:QMessageBox.warning(self,"تعذر الحفظ",str(error))

    def add_asset(self):
        code,ok=QInputDialog.getText(self,"أصل جديد","الكود:")
        if not ok:return
        name,ok=QInputDialog.getText(self,"أصل جديد","الاسم:")
        if ok and code.strip() and name.strip():
            try:self.repo.add_asset(code,name);self.refresh()
            except Exception as error:QMessageBox.warning(self,"تعذر الحفظ",str(error))

    def add_order(self):
        title,ok=QInputDialog.getText(self,"أمر صيانة","عنوان الأمر:")
        if ok and title.strip():
            try:self.repo.add_order(title);self.refresh()
            except Exception as error:QMessageBox.warning(self,"تعذر الحفظ",str(error))

    def update_order_status(self):
        row=self.orders_table.currentRow()
        if row<0 or row>=len(self._visible_orders):
            QMessageBox.information(self,"اختر أمرًا","حدد أمر صيانة من تبويب أوامر الصيانة أولاً.");return
        status,ok=QInputDialog.getItem(self,"حالة الأمر","الحالة:",["مفتوح","قيد التنفيذ","مكتمل","ملغي"],editable=False)
        if ok:
            try:self.repo.update_order_status(self._visible_orders[row].id,status);self.refresh()
            except Exception as error:QMessageBox.warning(self,"تعذر التحديث",str(error))
