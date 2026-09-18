import csv
from PySide6.QtWidgets import QFileDialog,QMessageBox,QTableWidget,QTableWidgetItem
from app.presentation.ui_theme import PageShell,Toolbar,button,setup_table
from app.infrastructure.repositories import FarmRepository,StructureRepository
from app.infrastructure.operations_repository import OperationsRepository
from app.infrastructure.crop_repository import CropRepository
from app.infrastructure.sales_repository import SalesRepository
from app.infrastructure.inventory_repository import InventoryRepository
from app.infrastructure.purchase_repository import PurchaseRepository
from app.infrastructure.hr_repository import HRRepository


class ReportsPage(PageShell):
    def __init__(self):
        super().__init__("التقارير","ملخصات تشغيلية من بيانات النظام الحالية.")
        self.repositories=[FarmRepository(),StructureRepository(),OperationsRepository(),CropRepository(),SalesRepository(),InventoryRepository(),PurchaseRepository(),HRRepository()]
        toolbar=Toolbar("بحث في التقارير…")
        self.search=toolbar.search
        self.content.addWidget(toolbar)
        self.table=QTableWidget(0,2)
        self.table.setHorizontalHeaderLabels(["المؤشر","القيمة"])
        setup_table(self.table)
        self.content.addWidget(self.table,1)
        self.actions.addWidget(button("تصدير CSV","normal",self.export_csv))
        self.search.textChanged.connect(self.filter_rows)
        self._rows=[]
        self.refresh()

    def refresh(self):
        farms,structure,operations,crop,sales,inventory,purchases,hr=self.repositories
        rows=[
            ["عدد المزارع",len(farms.list())],
            ["عدد القطاعات",sum(len(structure.sectors(farm.id)) for farm in farms.list())],
            ["أوامر الصيانة المفتوحة",operations.open_orders_count()],
            ["دفعات الحصاد",len(crop.batches())],
            ["المواسم",len(crop.seasons())],
            ["فواتير المبيعات",len(sales.invoices())],
            ["العملاء",len(sales.customers())],
            ["الأصناف",len(inventory.items())],
            ["فواتير المشتريات",len(purchases.invoices())],
            ["الموظفون",len(hr.employees())],
        ]
        self._rows=rows
        self.filter_rows(self.search.text())

    def filter_rows(self,text):
        query=text.strip().lower()
        rows=[row for row in self._rows if not query or query in " ".join(map(str,row)).lower()]
        self.table.setRowCount(len(rows))
        for row_index,row in enumerate(rows):
            for column,value in enumerate(row):
                self.table.setItem(row_index,column,QTableWidgetItem(str(value)))

    def export_csv(self):
        target,_=QFileDialog.getSaveFileName(self,"تصدير التقرير","farm_report.csv","CSV (*.csv)")
        if not target:return
        try:
            with open(target,"w",newline="",encoding="utf-8-sig") as file:
                writer=csv.writer(file);writer.writerow(["المؤشر","القيمة"]);writer.writerows(self._rows)
            QMessageBox.information(self,"تم التصدير",f"تم حفظ التقرير في:\n{target}")
        except OSError as error:
            QMessageBox.warning(self,"تعذر التصدير",str(error))
