from PySide6.QtWidgets import QMessageBox,QTabWidget,QTableWidget,QTableWidgetItem,QDialog
from app.presentation.ui_theme import PageShell,Toolbar,button,setup_table,FormDialog
from app.infrastructure.crop_repository import CropRepository
class CropPage(PageShell):
    def __init__(self):
        super().__init__("المحصول والحصاد","دفعات الحصاد والكميات الجاهزة للبيع.")
        self.r=CropRepository();toolbar=Toolbar("بحث في المواسم ودفعات الحصاد…");self.search=toolbar.search;self.content.addWidget(toolbar)
        self.tabs=QTabWidget();self.seasons_table=self._table(["الموسم","البداية","النهاية","الحالة"]);self.batches_table=self._table(["رقم الدفعة","التاريخ","البلوك","الإجمالي كجم","المتاح كجم"]);self.sort_table=self._table(["الدفعة","الدرجة","الكمية كجم"]);self.packing_table=self._table(["الرقم","الدفعة","العبوة","العدد","الإجمالي كجم"])
        self.tabs.addTab(self.seasons_table,"المواسم");self.tabs.addTab(self.batches_table,"دفعات الحصاد");self.tabs.addTab(self.sort_table,"الفرز");self.tabs.addTab(self.packing_table,"التعبئة");self.content.addWidget(self.tabs,1)
        self.actions.addWidget(button("＋ موسم","normal",self.add_season));self.actions.addWidget(button("＋ دفعة حصاد","primary",self.add_batch));self.actions.addWidget(button("＋ فرز","normal",self.add_sort));self.actions.addWidget(button("＋ تعبئة","normal",self.add_packing))
        self.search.textChanged.connect(self.filter_rows);self._rows={};self.refresh()
    def _table(self,headers):
        table=QTableWidget(0,len(headers));table.setHorizontalHeaderLabels(headers);setup_table(table);return table
    def refresh(self):
        batches=self.r.batches();self._batches=batches;self._rows={"seasons":[[x.name,x.start_date,x.end_date or "-",x.status] for x in self.r.seasons()],"batches":[[x.number,x.harvest_date,x.block_id,x.gross_kg,self.r.ready_kg(x.id)] for x in batches],"sort":[[x.batch_id,x.grade,x.quantity_kg] for x in self.r.sort_lines()],"packing":[[x.number,x.batch_id,x.package_type,x.package_count,x.total_kg] for x in self.r.packing_batches()]};self.filter_rows(self.search.text())
    def filter_rows(self,text):
        query=text.strip().lower()
        self._visible_batches=[batch for batch,row in zip(self._batches,self._rows.get("batches",[])) if not query or query in " ".join(map(str,row)).lower()]
        for key,table in [("seasons",self.seasons_table),("batches",self.batches_table),("sort",self.sort_table),("packing",self.packing_table)]:
            rows=[row for row in self._rows.get(key,[]) if not query or query in " ".join(map(str,row)).lower()];table.setRowCount(len(rows))
            for i,row in enumerate(rows):
                for j,value in enumerate(row):table.setItem(i,j,QTableWidgetItem(str(value)))
    def add_season(self):
        dialog = FormDialog("موسم جديد", [("اسم الموسم", "text", "")], self)
        if dialog.exec() != dialog.Accepted:
            return
        name = dialog.values()["اسم الموسم"]
        if name.strip():
            try:self.r.add_season(name);self.refresh()
            except Exception as error:QMessageBox.warning(self,"تعذر الحفظ",str(error))
    def selected_batch(self):
        row=self.batches_table.currentRow()
        if row<0 or row>=len(self._visible_batches):QMessageBox.information(self,"اختر دفعة","حدد دفعة حصاد من الجدول أولاً.");return None
        return self._visible_batches[row]
    def add_sort(self):
        batch=self.selected_batch()
        if not batch:return
        dialog = FormDialog("فرز المحصول", [("درجة الفرز", "text", "أولى"), ("الكمية", "number", 1)], self)
        if dialog.exec() != dialog.Accepted:
            return
        values = dialog.values()
        try:self.r.add_sort_line(batch.id, values["درجة الفرز"], values["الكمية"]);self.refresh()
        except Exception as error:QMessageBox.warning(self,"تعذر الحفظ",str(error))
    def add_packing(self):
        batch=self.selected_batch()
        if not batch:return
        dialog = FormDialog("تعبئة المحصول", [("نوع العبوة", "text", "كرتونة"), ("وزن العبوة", "number", 5), ("عدد العبوات", "int", 1)], self)
        if dialog.exec() != dialog.Accepted:
            return
        values = dialog.values()
        try:self.r.add_packing(batch.id, values["نوع العبوة"], values["وزن العبوة"], values["عدد العبوات"]);self.refresh()
        except Exception as error:QMessageBox.warning(self,"تعذر الحفظ",str(error))
    def add_batch(self):
        seasons = self.r.seasons()
        if not seasons:
            QMessageBox.information(self, "تنبيه", "أنشئ موسماً أولاً."); return
        blocks = self.r.batches()
        dialog = FormDialog("دفعة حصاد", [
            ("الموسم", "combo", seasons[0].id, [(s.name, s.id) for s in seasons]),
            ("البلوك", "combo", 1 if not blocks else blocks[0].block_id, []),
            ("الإجمالي كجم", "number", 1),
        ], self)
        if dialog.exec() != dialog.Accepted:
            return
        values = dialog.values()
        try:self.r.add_batch(values["الموسم"], values["البلوك"], values["الإجمالي كجم"]);self.refresh()
        except Exception as error:QMessageBox.warning(self,"تعذر الحفظ",str(error))
