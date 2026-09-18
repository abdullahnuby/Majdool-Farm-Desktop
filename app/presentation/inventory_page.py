from PySide6.QtWidgets import QTableWidget,QTableWidgetItem,QMessageBox,QDialog,QComboBox,QLabel,QFrame,QHBoxLayout,QVBoxLayout
from app.presentation.ui_theme import PageShell,Toolbar,button,setup_table,FormDialog
from app.infrastructure.inventory_repository import InventoryRepository
class InventoryPage(PageShell):
    def __init__(self):
        super().__init__("المخازن والمخزون","الأصناف، الأرصدة وحركات الصرف.")
        self.repo=InventoryRepository()
        tb=Toolbar("ابحث بالكود أو اسم الصنف…"); self.search=tb.search; self.content.addWidget(tb)
        self.warehouse_select=QComboBox(); self.warehouse_select.setMinimumWidth(190); tb.right.addWidget(QLabel("المخزن")); tb.right.addWidget(self.warehouse_select)
        summary=QHBoxLayout(); summary.setSpacing(12)
        self.item_count=self._summary_card("الأصناف", "0")
        self.low_count=self._summary_card("تحت الحد الأدنى", "0")
        self.total_quantity=self._summary_card("إجمالي الوحدات", "0")
        for card in (self.item_count,self.low_count,self.total_quantity): summary.addWidget(card, 1)
        self.content.addLayout(summary)
        self.table=QTableWidget(0,6); self.table.setHorizontalHeaderLabels(["الكود","الصنف","التصنيف","الوحدة","الرصيد","الحالة"]); setup_table(self.table); self.content.addWidget(self.table,1)
        for text,fn,kind in [("＋ مخزن جديد",self.warehouse,"normal"),("＋ صنف جديد",self.item,"normal"),("تعديل الصنف",self.edit_item,"normal"),("حذف الصنف",self.delete_item,"danger"),("صرف مخزون",self.issue,"primary")]:
            self.actions.addWidget(button(text,kind,fn))
        self.search.textChanged.connect(self.filter_rows); self.warehouse_select.currentIndexChanged.connect(self.refresh); self.refresh()

    def _summary_card(self, label, value):
        card=QFrame(); card.setObjectName("Card")
        layout=QVBoxLayout(card); layout.setContentsMargins(16,12,16,12); layout.setSpacing(2)
        title=QLabel(label); title.setObjectName("CardLabel"); layout.addWidget(title)
        number=QLabel(value); number.setObjectName("CardValue"); layout.addWidget(number)
        card.value_label=number
        return card

    def _set_summary(self, card, value):
        card.value_label.setText(str(value))

    def refresh(self):
        items=self.repo.items(); wh=self.repo.warehouses()
        if not wh: self.repo.add_warehouse("MAIN","المخزن الرئيسي"); wh=self.repo.warehouses()
        current_id=self.warehouse_select.currentData()
        self.warehouse_select.blockSignals(True); self.warehouse_select.clear()
        for warehouse in wh:self.warehouse_select.addItem(warehouse.name, warehouse.id)
        if current_id is not None:
            index=self.warehouse_select.findData(current_id)
            if index >= 0:self.warehouse_select.setCurrentIndex(index)
        self.warehouse_select.blockSignals(False)
        warehouse_id=self.warehouse_select.currentData() or wh[0].id
        self._items=items; self._warehouses=wh; self._warehouse_id=warehouse_id
        self._rows=[]
        low_count=0; total_quantity=0
        for x in items:
            balance=self.repo.balance(x.id,warehouse_id); is_low=balance <= x.min_stock
            if is_low:low_count += 1
            total_quantity += balance
            self._rows.append([x.code,x.name,x.category,x.unit,balance,"يحتاج توريد" if is_low else "متوفر"])
        self._visible_items=items
        self._set_summary(self.item_count,len(items)); self._set_summary(self.low_count,low_count); self._set_summary(self.total_quantity,total_quantity)
        self._render(self._rows)
    def _render(self,rows):
        self.table.setRowCount(len(rows))
        for i,row in enumerate(rows):
            for j,v in enumerate(row):self.table.setItem(i,j,QTableWidgetItem(str(v)))
    def filter_rows(self,t):
        matches=[(item,row) for item,row in zip(self._items,self._rows) if not t.strip() or t.lower() in " ".join(map(str,row)).lower()]
        self._visible_items=[item for item,row in matches]
        self._render([row for item,row in matches])
    def warehouse(self):
        dialog = FormDialog("مخزن جديد", [("الكود", "text", ""), ("الاسم", "text", "")], self)
        if dialog.exec() != dialog.Accepted:
            return
        values = dialog.values()
        if values["الكود"].strip() and values["الاسم"].strip():
            try:self.repo.add_warehouse(values["الكود"], values["الاسم"]);self.refresh()
            except Exception as e:QMessageBox.warning(self,"تعذر الحفظ",str(e))
    def item(self):
        dialog = FormDialog("صنف جديد", [("الكود", "text", ""), ("الاسم", "text", "")], self)
        if dialog.exec() != dialog.Accepted:
            return
        values = dialog.values()
        if values["الكود"].strip() and values["الاسم"].strip():
            try:self.repo.add_item(values["الكود"], values["الاسم"]);self.refresh()
            except Exception as e:QMessageBox.warning(self,"تعذر الحفظ",str(e))
    def issue(self):
        row=self.table.currentRow()
        if row < 0 or row >= len(self._visible_items):
            QMessageBox.information(self,"اختر صنفاً","حدد صنفاً من الجدول أولاً."); return
        x=self._visible_items[row]; warehouse_id=self._warehouse_id
        dialog = FormDialog("صرف مخزون", [("الكمية", "number", 1)], self)
        if dialog.exec() != dialog.Accepted:
            return
        quantity = dialog.values()["الكمية"]
        try:self.repo.issue(x.id,warehouse_id,quantity);self.refresh()
        except Exception as e:QMessageBox.warning(self,"تعذر الصرف",str(e))

    def selected_item(self):
        row=self.table.currentRow()
        if row<0 or row>=len(self._visible_items):
            QMessageBox.information(self,"اختر صنفاً","حدد صنفاً من الجدول أولاً.");return None
        return self._visible_items[row]

    def edit_item(self):
        item=self.selected_item()
        if not item:return
        dialog = FormDialog("تعديل الصنف", [("الاسم", "text", item.name), ("حد إعادة الطلب", "number", item.min_stock)], self)
        if dialog.exec() != dialog.Accepted:
            return
        values = dialog.values()
        try:self.repo.update_item(item.id, values["الاسم"], item.category, item.unit, values["حد إعادة الطلب"]);self.refresh()
        except Exception as error:QMessageBox.warning(self,"تعذر التعديل",str(error))

    def delete_item(self):
        item=self.selected_item()
        if not item:return
        if QMessageBox.question(self,"تأكيد الحذف",f"حذف الصنف {item.name}؟")==QMessageBox.StandardButton.Yes:
            try:self.repo.delete_item(item.id);self.refresh()
            except Exception as error:QMessageBox.warning(self,"تعذر الحذف",str(error))
