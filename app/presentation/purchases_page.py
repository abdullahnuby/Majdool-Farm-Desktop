from PySide6.QtWidgets import QInputDialog,QMessageBox,QTabWidget,QTableWidget,QTableWidgetItem
from app.presentation.ui_theme import PageShell,Toolbar,button,setup_table
from app.infrastructure.purchase_repository import PurchaseRepository
class PurchasesPage(PageShell):
    def __init__(self):
        super().__init__("المشتريات والموردون","دورة الشراء من الفاتورة حتى الاستلام والسداد.")
        self.repo=PurchaseRepository(); tb=Toolbar("بحث في فواتير الشراء…"); self.search=tb.search; self.content.addWidget(tb)
        self.table=QTableWidget(0,6); self.table.setHorizontalHeaderLabels(["الفاتورة","التاريخ","المورد","الحالة","الإجمالي","المستحق"]); setup_table(self.table)
        self.supplier_table=QTableWidget(0,3);self.supplier_table.setHorizontalHeaderLabels(["الكود","المورد","الهاتف"]);setup_table(self.supplier_table)
        self.tabs=QTabWidget();self.tabs.addTab(self.table,"الفواتير");self.tabs.addTab(self.supplier_table,"الموردون");self.content.addWidget(self.tabs,1)
        for t,f,k in [("＋ مورد جديد",self.supplier,"normal"),("تعديل المورد",self.edit_supplier,"normal"),("حذف المورد",self.delete_supplier,"danger"),("＋ فاتورة شراء",self.invoice,"primary"),("إضافة صنف",self.line,"normal"),("تأكيد",self.confirm,"normal"),("سداد",self.pay,"normal")]:self.actions.addWidget(button(t,k,f))
        self.search.textChanged.connect(self.filter_rows)
        self._rows=[];self._visible_invoices=[]
        self.refresh()
    def refresh(self):
        rows=self.repo.invoices(); self._invoices=rows; sup={x.id:x.name for x in self.repo.suppliers()}; self._rows=[]
        for x in rows:self._rows.append([x.number,x.invoice_date,sup.get(x.supplier_id,"-"),x.status,x.total,self.repo.outstanding(x.id)])
        self.filter_rows(self.search.text());self._suppliers=self.repo.suppliers();self._render_suppliers()
    def _render(self,rows):
        self.table.setRowCount(len(rows))
        for i,r in enumerate(rows):
            for j,v in enumerate(r):self.table.setItem(i,j,QTableWidgetItem(str(v)))
    def _render_suppliers(self):
        self.supplier_table.setRowCount(len(self._suppliers))
        for i,supplier in enumerate(self._suppliers):
            for j,value in enumerate([supplier.code,supplier.name,supplier.phone or "-"]):self.supplier_table.setItem(i,j,QTableWidgetItem(str(value)))
    def filter_rows(self,text):
        query=text.strip().lower(); matches=[(invoice,row) for invoice,row in zip(self._invoices,self._rows) if not query or query in " ".join(map(str,row)).lower()]
        self._visible_invoices=[invoice for invoice,row in matches];self._render([row for invoice,row in matches])
    def supplier(self):
        c,ok=QInputDialog.getText(self,"مورد جديد","الكود:")
        if not ok:return
        n,ok=QInputDialog.getText(self,"مورد جديد","الاسم:")
        if ok and c.strip() and n.strip():
            try:self.repo.add_supplier(c,n);self.refresh()
            except Exception as e:QMessageBox.warning(self,"خطأ",str(e))
    def first(self):
        xs=self.repo.suppliers()
        if not xs:QMessageBox.information(self,"تنبيه","أضف مورداً أولاً.");return None
        return xs[0]
    def invoice(self):
        s=self.first()
        if s:
            try:self.repo.create_invoice(s.id);self.refresh()
            except Exception as e:QMessageBox.warning(self,"خطأ",str(e))
    def line(self):
        inv=self.selected_invoice()
        if not inv:return
        n,ok=QInputDialog.getText(self,"إضافة صنف","اسم الصنف:")
        if not ok:return
        q,ok=QInputDialog.getDouble(self,"الكمية","الكمية:",1,0.01,10000000,2)
        if not ok:return
        p,ok=QInputDialog.getDouble(self,"السعر","السعر:",1,0,10000000,2)
        if ok:
            try:self.repo.add_line(inv.id,n,q,p);self.refresh()
            except Exception as e:QMessageBox.warning(self,"خطأ",str(e))
    def confirm(self):
        inv=self.selected_invoice()
        if inv:
            try:self.repo.confirm(inv.id);self.refresh()
            except Exception as e:QMessageBox.warning(self,"خطأ",str(e))
    def pay(self):
        inv=self.selected_invoice()
        if not inv:return
        q,ok=QInputDialog.getDouble(self,"سداد","المبلغ:",100,0.01,100000000,2)
        if ok:
            try:self.repo.pay(inv.supplier_id,inv.id,q);self.refresh()
            except Exception as e:QMessageBox.warning(self,"خطأ",str(e))

    def selected_invoice(self):
        row=self.table.currentRow()
        if row < 0 or row >= len(self._visible_invoices):
            QMessageBox.information(self,"اختر فاتورة","حدد فاتورة من الجدول أولاً."); return None
        return self._visible_invoices[row]
    def selected_supplier(self):
        row=self.supplier_table.currentRow()
        if row<0 or row>=len(self._suppliers):QMessageBox.information(self,"اختر مورداً","حدد مورداً من تبويب الموردين أولاً.");return None
        return self._suppliers[row]
    def edit_supplier(self):
        supplier=self.selected_supplier()
        if not supplier:return
        name,ok=QInputDialog.getText(self,"تعديل المورد","الاسم:",text=supplier.name)
        if ok:
            try:self.repo.update_supplier(supplier.id,name);self.refresh()
            except Exception as error:QMessageBox.warning(self,"تعذر التعديل",str(error))
    def delete_supplier(self):
        supplier=self.selected_supplier()
        if not supplier:return
        if QMessageBox.question(self,"تأكيد الحذف",f"حذف المورد {supplier.name}؟")==QMessageBox.StandardButton.Yes:
            try:self.repo.delete_supplier(supplier.id);self.refresh()
            except Exception as error:QMessageBox.warning(self,"تعذر الحذف",str(error))
