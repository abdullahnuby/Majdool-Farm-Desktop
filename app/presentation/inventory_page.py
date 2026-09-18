from PySide6.QtWidgets import QTableWidget,QTableWidgetItem,QMessageBox,QInputDialog
from app.presentation.ui_theme import PageShell,Toolbar,button,setup_table
from app.infrastructure.inventory_repository import InventoryRepository
class InventoryPage(PageShell):
    def __init__(self):
        super().__init__("المخازن والمخزون","الأصناف، الأرصدة وحركات الصرف.")
        self.repo=InventoryRepository()
        tb=Toolbar("ابحث بالكود أو اسم الصنف…"); self.search=tb.search; self.content.addWidget(tb)
        self.table=QTableWidget(0,5); self.table.setHorizontalHeaderLabels(["الكود","الصنف","التصنيف","الوحدة","الرصيد"]); setup_table(self.table); self.content.addWidget(self.table,1)
        for text,fn,kind in [("＋ مخزن جديد",self.warehouse,"normal"),("＋ صنف جديد",self.item,"normal"),("صرف مخزون",self.issue,"primary")]:
            self.actions.addWidget(button(text,kind,fn))
        self.search.textChanged.connect(self.filter_rows); self.refresh()
    def refresh(self):
        items=self.repo.items(); wh=self.repo.warehouses()
        if not wh: self.repo.add_warehouse("MAIN","المخزن الرئيسي"); wh=self.repo.warehouses()
        self._rows=[]
        for x in items:self._rows.append([x.code,x.name,x.category,x.unit,self.repo.balance(x.id,wh[0].id)])
        self._render(self._rows)
    def _render(self,rows):
        self.table.setRowCount(len(rows))
        for i,row in enumerate(rows):
            for j,v in enumerate(row):self.table.setItem(i,j,QTableWidgetItem(str(v)))
    def filter_rows(self,t): self._render([r for r in self._rows if not t.strip() or t.lower() in " ".join(map(str,r)).lower()])
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
        items=self.repo.items(); wh=self.repo.warehouses()
        if not items or not wh:return
        x=items[0]; bal=self.repo.balance(x.id,wh[0].id)
        q,ok=QInputDialog.getDouble(self,"صرف مخزون",f"الكمية — الرصيد الحالي {bal}",1,0.01,10000000,2)
        if ok:
            try:self.repo.issue(x.id,wh[0].id,q);self.refresh()
            except Exception as e:QMessageBox.warning(self,"تعذر الصرف",str(e))
