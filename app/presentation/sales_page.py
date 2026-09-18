from PySide6.QtWidgets import QTableWidget,QTableWidgetItem,QInputDialog,QMessageBox
from datetime import date
from app.presentation.ui_theme import PageShell,Toolbar,button,setup_table
from app.infrastructure.sales_repository import SalesRepository
class SalesPage(PageShell):
    def __init__(self):
        super().__init__("المبيعات والعملاء","الفواتير، بنود البيع والتحصيل.")
        self.repo=SalesRepository(); tb=Toolbar("بحث برقم الفاتورة أو العميل…"); self.content.addWidget(tb)
        self.table=QTableWidget(0,6); self.table.setHorizontalHeaderLabels(["الفاتورة","التاريخ","العميل","الحالة","قبل الخصم","الإجمالي"]); setup_table(self.table); self.content.addWidget(self.table,1)
        for t,f,k in [("＋ عميل جديد",self.customer,"normal"),("＋ فاتورة جديدة",self.invoice,"primary"),("إضافة بند",self.line,"normal"),("تأكيد الفاتورة",self.confirm,"normal"),("تحصيل",self.receipt,"normal")]:self.actions.addWidget(button(t,k,f))
        self.refresh()
    def refresh(self):
        rows=self.repo.invoices(); self._rows=[]
        for x in rows:self._rows.append([x.number,x.invoice_date,x.customer_id,x.status,x.subtotal,x.total])
        self._render(self._rows)
    def _render(self,rows):
        self.table.setRowCount(len(rows))
        for i,r in enumerate(rows):
            for j,v in enumerate(r):self.table.setItem(i,j,QTableWidgetItem(str(v)))
    def customer(self):
        c,ok=QInputDialog.getText(self,"عميل جديد","الكود:")
        if not ok:return
        n,ok=QInputDialog.getText(self,"عميل جديد","الاسم:")
        if ok and c.strip() and n.strip():
            try:self.repo.add_customer(c,n);self.refresh()
            except Exception as e:QMessageBox.warning(self,"خطأ",str(e))
    def invoice(self):
        cs=self.repo.customers()
        if not cs:QMessageBox.information(self,"تنبيه","أنشئ عميلاً أولاً.");return
        try:self.repo.create_invoice(cs[0].id,date.today(),0,0);self.refresh()
        except Exception as e:QMessageBox.warning(self,"خطأ",str(e))
    def line(self):
        inv=self.repo.invoices()
        if not inv:return
        bid,ok=QInputDialog.getInt(self,"بند بيع","رقم دفعة الحصاد:",1,1,100000)
        if not ok:return
        q,ok=QInputDialog.getDouble(self,"الكمية","الكمية كجم:",1,0.01,100000,2)
        if not ok:return
        p,ok=QInputDialog.getDouble(self,"السعر","سعر الكجم:",1,0,100000,2)
        if ok:
            try:self.repo.add_line(inv[0].id,bid,"درجة أولى",q,p);self.refresh()
            except Exception as e:QMessageBox.warning(self,"خطأ",str(e))
    def confirm(self):
        inv=self.repo.invoices()
        if inv:
            try:self.repo.confirm(inv[0].id);self.refresh()
            except Exception as e:QMessageBox.warning(self,"خطأ",str(e))
    def receipt(self):
        inv=self.repo.invoices()
        if not inv:return
        q,ok=QInputDialog.getDouble(self,"تحصيل","المبلغ:",1,0.01,100000000,2)
        if ok:
            try:self.repo.add_receipt(inv[0].customer_id,inv[0].id,q)
            except Exception as e:QMessageBox.warning(self,"خطأ",str(e))
