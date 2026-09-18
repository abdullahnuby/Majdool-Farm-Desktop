from PySide6.QtWidgets import QInputDialog,QMessageBox,QTabWidget,QTableWidget,QTableWidgetItem
from app.presentation.ui_theme import PageShell,Toolbar,button,setup_table
from app.infrastructure.crop_repository import CropRepository
class CropPage(PageShell):
    def __init__(self):
        super().__init__("المحصول والحصاد","دفعات الحصاد والكميات الجاهزة للبيع.")
        self.r=CropRepository();toolbar=Toolbar("بحث في المواسم ودفعات الحصاد…");self.search=toolbar.search;self.content.addWidget(toolbar)
        self.tabs=QTabWidget();self.seasons_table=self._table(["الموسم","البداية","النهاية","الحالة"]);self.batches_table=self._table(["رقم الدفعة","التاريخ","البلوك","الإجمالي كجم","المتاح كجم"])
        self.tabs.addTab(self.seasons_table,"المواسم");self.tabs.addTab(self.batches_table,"دفعات الحصاد");self.content.addWidget(self.tabs,1)
        self.actions.addWidget(button("＋ موسم","normal",self.add_season));self.actions.addWidget(button("＋ دفعة حصاد","primary",self.add_batch))
        self.search.textChanged.connect(self.filter_rows);self._rows={};self.refresh()
    def _table(self,headers):
        table=QTableWidget(0,len(headers));table.setHorizontalHeaderLabels(headers);setup_table(table);return table
    def refresh(self):
        self._rows={"seasons":[[x.name,x.start_date,x.end_date or "-",x.status] for x in self.r.seasons()],"batches":[[x.number,x.harvest_date,x.block_id,x.gross_kg,self.r.ready_kg(x.id)] for x in self.r.batches()]};self.filter_rows(self.search.text())
    def filter_rows(self,text):
        query=text.strip().lower()
        for key,table in [("seasons",self.seasons_table),("batches",self.batches_table)]:
            rows=[row for row in self._rows.get(key,[]) if not query or query in " ".join(map(str,row)).lower()];table.setRowCount(len(rows))
            for i,row in enumerate(rows):
                for j,value in enumerate(row):table.setItem(i,j,QTableWidgetItem(str(value)))
    def add_season(self):
        name,ok=QInputDialog.getText(self,"موسم جديد","اسم الموسم:")
        if ok and name.strip():
            try:self.r.add_season(name);self.refresh()
            except Exception as error:QMessageBox.warning(self,"تعذر الحفظ",str(error))
    def add_batch(self):
        season_id,ok=QInputDialog.getInt(self,"دفعة حصاد","رقم الموسم:",1,1,100000)
        if not ok:return
        block_id,ok=QInputDialog.getInt(self,"دفعة حصاد","رقم البلوك:",1,1,100000)
        if not ok:return
        quantity,ok=QInputDialog.getDouble(self,"دفعة حصاد","الإجمالي كجم:",1,0,100000000,2)
        if ok:
            try:self.r.add_batch(season_id,block_id,quantity);self.refresh()
            except Exception as error:QMessageBox.warning(self,"تعذر الحفظ",str(error))
