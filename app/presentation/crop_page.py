from PySide6.QtWidgets import QTableWidget,QTableWidgetItem
from app.presentation.ui_theme import PageShell,Toolbar,setup_table
from app.infrastructure.crop_repository import CropRepository
class CropPage(PageShell):
    def __init__(self):
        super().__init__("المحصول والحصاد","دفعات الحصاد والكميات الجاهزة للبيع.")
        self.r=CropRepository();self.content.addWidget(Toolbar("بحث برقم الدفعة أو البلوك…"))
        self.t=QTableWidget(0,4);self.t.setHorizontalHeaderLabels(["رقم الدفعة","التاريخ","البلوك","الإجمالي كجم"]);setup_table(self.t);self.content.addWidget(self.t,1);self.refresh()
    def refresh(self):
        rows=self.r.batches();self.t.setRowCount(len(rows))
        for i,x in enumerate(rows):
            for j,v in enumerate([x.number,x.harvest_date,x.block_id,x.gross_kg]):self.t.setItem(i,j,QTableWidgetItem(str(v)))
