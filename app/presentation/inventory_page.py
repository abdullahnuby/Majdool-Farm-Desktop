from PySide6.QtWidgets import QTableWidget,QTableWidgetItem,QMessageBox,QInputDialog
from app.presentation.ui_theme import PageShell,Toolbar,button,setup_table
from app.infrastructure.inventory_repository import InventoryRepository
class InventoryPage(PageShell):
    def __init__(self):
        super().__init__("المخازن والمخزون","الأصناف، الأرصدة وحركات الصرف.")
        self.repo=InventoryRepository()
        tb=Toolbar("ابحث بالكود أو اسم الصنف…"); self.search=tb.search; self.content.addWidget(tb)
        self.table=QTableWidget(0,5); self.table.setHorizontalHeaderLabels(["الكود","الصنف","التصنيف","الوحدة","الرصيد"]); setup_table(self.table); self.content.addWidget(self.table,1)
        for text,fn,kind in [("＋ مخزن جديد",self.warehouse,"normal"),("＋ صنف جديد",self.item,"normal"),("تعديل الصنف",self.edit_item,"normal"),("حذف الصنف",self.delete_item,"danger"),("صرف مخزون",self.issue,"primary")]:
            self.actions.addWidget(button(text,kind,fn))
        self.search.textChanged.connect(self.filter_rows); self.refresh()
    def refresh(self):
        items=self.repo.items(); wh=self.repo.warehouses()
        if not wh: self.repo.add_warehouse("MAIN","المخزن الرئيسي"); wh=self.repo.warehouses()
        self._items=items; self._warehouses=wh
        self._rows=[]
        for x in items:self._rows.append([x.code,x.name,x.category,x.unit,self.repo.balance(x.id,wh[0].id)])
        self._visible_items=items
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
        c,ok=QInputDialog.getText(self,"مخزن جديد","الكود:"); 
        if ok:
            n,ok=QInputDialog.getText(self,"مخزن جديد","الاسم:")
            if ok and c.strip() and n.strip():
                try:self.repo.add_warehouse(c,n);self.refresh()
                except Exception as e:QMessageBox.warning(self,"تعذر الحفظ",str(e))
    def item(self):
        c,ok=QInputDialog.getText(self,"صنف جديد","الكود:")
        if ok:
            n,ok=QInputDialog.getText(self,"صنف جديد","الاسم:")
            if ok and c.strip() and n.strip():
                try:self.repo.add_item(c,n);self.refresh()
                except Exception as e:QMessageBox.warning(self,"تعذر الحفظ",str(e))
    def issue(self):
        row=self.table.currentRow()
        if row < 0 or row >= len(self._visible_items):
            QMessageBox.information(self,"اختر صنفاً","حدد صنفاً من الجدول أولاً."); return
        x=self._visible_items[row]; wh=self._warehouses
        if not wh:return
        bal=self.repo.balance(x.id,wh[0].id)
        q,ok=QInputDialog.getDouble(self,"صرف مخزون",f"الكمية — الرصيد الحالي {bal}",1,0.01,10000000,2)
        if ok:
            try:self.repo.issue(x.id,wh[0].id,q);self.refresh()
            except Exception as e:QMessageBox.warning(self,"تعذر الصرف",str(e))

    def selected_item(self):
        row=self.table.currentRow()
        if row<0 or row>=len(self._visible_items):
            QMessageBox.information(self,"اختر صنفاً","حدد صنفاً من الجدول أولاً.");return None
        return self._visible_items[row]

    def edit_item(self):
        item=self.selected_item()
        if not item:return
        name,ok=QInputDialog.getText(self,"تعديل الصنف","الاسم:",text=item.name)
        if not ok:return
        minimum,ok=QInputDialog.getDouble(self,"تعديل الصنف","حد إعادة الطلب:",item.min_stock,0,100000000,2)
        if ok:
            try:self.repo.update_item(item.id,name,item.category,item.unit,minimum);self.refresh()
            except Exception as error:QMessageBox.warning(self,"تعذر التعديل",str(error))

    def delete_item(self):
        item=self.selected_item()
        if not item:return
        if QMessageBox.question(self,"تأكيد الحذف",f"حذف الصنف {item.name}؟")==QMessageBox.StandardButton.Yes:
            try:self.repo.delete_item(item.id);self.refresh()
            except Exception as error:QMessageBox.warning(self,"تعذر الحذف",str(error))
