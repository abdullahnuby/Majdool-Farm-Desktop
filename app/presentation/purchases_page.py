from datetime import date
from PySide6.QtWidgets import QMessageBox,QTabWidget,QTableWidget,QTableWidgetItem,QDialog,QLabel,QFrame,QHBoxLayout,QVBoxLayout,QWidget
from app.presentation.ui_theme import PageShell,Toolbar,button,setup_table,FormDialog,InvoiceLineEditor
from app.infrastructure.purchase_repository import PurchaseRepository
class PurchasesPage(PageShell):
    def __init__(self):
        super().__init__("المشتريات والموردون","دورة الشراء من الفاتورة حتى الاستلام والسداد.")
        self.repo=PurchaseRepository(); tb=Toolbar("بحث في فواتير الشراء…"); self.search=tb.search; self.content.addWidget(tb)
        summary=QHBoxLayout(); summary.setSpacing(12)
        self.invoice_count=self._summary_card("فواتير الشراء", "0")
        self.open_count=self._summary_card("قيد السداد", "0")
        self.purchase_total=self._summary_card("إجمالي المشتريات", "0")
        for card in (self.invoice_count,self.open_count,self.purchase_total): summary.addWidget(card, 1)
        self.content.addLayout(summary)
        self.table=QTableWidget(0,6); self.table.setHorizontalHeaderLabels(["الفاتورة","التاريخ","المورد","الحالة","الإجمالي","المستحق"]); setup_table(self.table)
        self.line_table=QTableWidget(0,5); self.line_table.setHorizontalHeaderLabels(["الصنف","الكمية","الوحدة","سعر الوحدة","الإجمالي"]); setup_table(self.line_table); self.line_table.setMinimumHeight(180)
        invoice_view=QWidget(); invoice_layout=QVBoxLayout(invoice_view); invoice_layout.setContentsMargins(0,0,0,0); invoice_layout.setSpacing(10)
        invoice_layout.addWidget(self.table, 3); invoice_layout.addWidget(QLabel("أصناف الفاتورة المحددة"), 0); invoice_layout.addWidget(self.line_table, 2)
        self.supplier_table=QTableWidget(0,6);self.supplier_table.setHorizontalHeaderLabels(["الكود","المورد","الهاتف","إجمالي الفواتير","المدفوع","المتبقي"]);setup_table(self.supplier_table)
        self.tabs=QTabWidget();self.tabs.addTab(invoice_view,"الفواتير");self.tabs.addTab(self.supplier_table,"الموردون");self.content.addWidget(self.tabs,1)
        for t,f,k in [("＋ مورد جديد",self.supplier,"normal"),("تعديل المورد",self.edit_supplier,"normal"),("حذف المورد",self.delete_supplier,"danger"),("＋ فاتورة شراء",self.invoice,"primary"),("تعديل الفاتورة",self.edit_invoice,"normal"),("إضافة صنف",self.line,"normal"),("حذف البند المحدد",self.delete_line,"danger"),("تأكيد",self.confirm,"normal"),("سداد",self.pay,"normal"),("حذف المسودة",self.delete_draft,"danger")]:self.actions.addWidget(button(t,k,f))
        self.search.textChanged.connect(self.filter_rows)
        self.table.itemSelectionChanged.connect(self._render_selected_lines)
        self._rows=[];self._visible_invoices=[]
        self.refresh()

    def _summary_card(self, label, value):
        card=QFrame(); card.setObjectName("Card")
        layout=QVBoxLayout(card); layout.setContentsMargins(16,12,16,12); layout.setSpacing(2)
        title=QLabel(label); title.setObjectName("CardLabel"); layout.addWidget(title)
        number=QLabel(value); number.setObjectName("CardValue"); layout.addWidget(number)
        card.value_label=number
        return card

    def _set_summary(self, card, value):
        card.value_label.setText(str(value))

    def _render_selected_lines(self):
        invoice=self.selected_invoice(show_message=False)
        if not invoice:
            self.line_table.setRowCount(0)
            return
        lines=self.repo.lines(invoice.id)
        self._visible_lines=lines
        self.line_table.setRowCount(len(lines))
        for row,line in enumerate(lines):
            values=[line.item_name,line.quantity,line.unit,line.unit_price,line.line_total]
            for column,value in enumerate(values):self.line_table.setItem(row,column,QTableWidgetItem(str(value)))

    def refresh(self):
        rows=self.repo.invoices(); self._invoices=rows; self._suppliers=self.repo.suppliers(); sup={x.id:x.name for x in self._suppliers}; self._rows=[]
        for x in rows:self._rows.append([x.number,x.invoice_date,sup.get(x.supplier_id,"-"),x.status,x.total,self.repo.outstanding(x.id)])
        open_count=sum(1 for invoice in rows if invoice.status not in ("مدفوعة", "ملغاة") and self.repo.outstanding(invoice.id) > 0)
        total=sum((invoice.total or 0) for invoice in rows)
        self._set_summary(self.invoice_count,len(rows)); self._set_summary(self.open_count,open_count); self._set_summary(self.purchase_total,total)
        self._supplier_financials={}
        for supplier in self._suppliers:
            supplier_invoices=[invoice for invoice in rows if invoice.supplier_id == supplier.id]
            invoiced=sum((invoice.total or 0) for invoice in supplier_invoices)
            outstanding=sum((self.repo.outstanding(invoice.id) or 0) for invoice in supplier_invoices)
            self._supplier_financials[supplier.id]=(invoiced,invoiced-outstanding,outstanding)
        self.filter_rows(self.search.text());self._render_suppliers()
    def _render(self,rows):
        self.table.setRowCount(len(rows))
        for i,r in enumerate(rows):
            for j,v in enumerate(r):self.table.setItem(i,j,QTableWidgetItem(str(v)))
    def _render_suppliers(self):
        self.supplier_table.setRowCount(len(self._suppliers))
        for i,supplier in enumerate(self._suppliers):
            invoiced,paid,outstanding=self._supplier_financials.get(supplier.id,(0,0,0))
            values=[supplier.code,supplier.name,supplier.phone or "-",invoiced,paid,outstanding]
            for j,value in enumerate(values):self.supplier_table.setItem(i,j,QTableWidgetItem(str(value)))
    def filter_rows(self,text):
        query=text.strip().lower(); matches=[(invoice,row) for invoice,row in zip(self._invoices,self._rows) if not query or query in " ".join(map(str,row)).lower()]
        self._visible_invoices=[invoice for invoice,row in matches];self._render([row for invoice,row in matches])
        self._render_selected_lines()
    def supplier(self):
        dialog = FormDialog("مورد جديد", [("الكود", "text", ""), ("الاسم", "text", "")], self)
        if dialog.exec() != dialog.Accepted:
            return
        values = dialog.values()
        code = values["الكود"]
        name = values["الاسم"]
        if code and name:
            try:self.repo.add_supplier(code,name);self.refresh()
            except Exception as e:QMessageBox.warning(self,"خطأ",str(e))
    def _resolve_invoice_supplier(self):
        row = self.supplier_table.currentRow()
        if row < 0 or row >= len(self._suppliers):
            raise ValueError("اختيار المورد مطلوب.")
        return self._suppliers[row]

    def invoice(self):
        if not self._suppliers:
            QMessageBox.information(self,"تنبيه","أضف مورداً أولاً."); return
        editor=InvoiceLineEditor("فاتورة شراء جديدة", [("اسم الصنف", "text", ""), ("الكمية", "number", 1), ("السعر", "number", 1)], ["الصنف", "الكمية", "السعر", "الإجمالي"], "إجمالي البند", self,
        [("الصنف", "اسم الصنف"), ("الكمية", "الكمية"), ("السعر", "السعر"), ("الإجمالي", "إجمالي البند")], lambda values: values["الكمية"] * values["السعر"],
        [("المورد", "combo", self._suppliers[0].id, [(s.name, s.id) for s in self._suppliers]), ("تاريخ الفاتورة", "date", date.today())])
        if editor.exec() != editor.Accepted:return
        values=editor.header_values()
        try:
            invoice=self.repo.create_invoice(values["المورد"], values["تاريخ الفاتورة"])
            for line in editor.lines:self.repo.add_line(invoice.id, line["اسم الصنف"], line["الكمية"], line["السعر"])
            self.refresh()
            self._select_invoice(invoice.id)
        except Exception as e:QMessageBox.warning(self,"خطأ",str(e))

    def _select_invoice(self, invoice_id):
        for row,invoice in enumerate(self._visible_invoices):
            if invoice.id == invoice_id:
                self.table.selectRow(row)
                return
    def line(self):
        inv=self.selected_invoice()
        if not inv:return
        self._edit_new_invoice(inv)

    def edit_invoice(self):
        invoice=self.selected_invoice()
        if not invoice:return
        if invoice.status != "مسودة": QMessageBox.information(self,"الفاتورة مؤكدة","تعديل الفاتورة متاح للمسودات فقط."); return
        editor=InvoiceLineEditor("تعديل فاتورة الشراء",[("اسم الصنف","text",""),("الكمية","number",1),("السعر","number",1)],["الصنف","الكمية","السعر","الإجمالي"],"إجمالي البند",self,[("الصنف","اسم الصنف"),("الكمية","الكمية"),("السعر","السعر"),("الإجمالي","إجمالي البند")],lambda v:v["الكمية"]*v["السعر"],[("المورد","combo",invoice.supplier_id,[(s.name,s.id) for s in self._suppliers]),("تاريخ الفاتورة","date",invoice.invoice_date)])
        editor.set_lines([{"اسم الصنف":l.item_name,"الكمية":l.quantity,"السعر":l.unit_price,"إجمالي البند":l.line_total} for l in self.repo.lines(invoice.id)])
        if editor.exec()!=editor.Accepted:return
        v=editor.header_values()
        try:self.repo.update_draft(invoice.id,v["المورد"],v["تاريخ الفاتورة"],[(l["اسم الصنف"],l["الكمية"],l["السعر"]) for l in editor.lines]);self.refresh();self._select_invoice(invoice.id)
        except Exception as error:QMessageBox.warning(self,"تعذر تعديل الفاتورة",str(error))

    def _edit_new_invoice(self, invoice):
        editor=InvoiceLineEditor("تفاصيل فاتورة الشراء", [
            ("اسم الصنف", "text", ""),
            ("الكمية", "number", 1),
            ("السعر", "number", 1),
        ], ["الصنف", "الكمية", "السعر", "الإجمالي"], "إجمالي البند", self,
        [("الصنف", "اسم الصنف"), ("الكمية", "الكمية"), ("السعر", "السعر"), ("الإجمالي", "إجمالي البند")],
        lambda values: values["الكمية"] * values["السعر"])
        if editor.exec() != editor.Accepted:return
        try:
            for line in editor.lines:
                self.repo.add_line(invoice.id, line["اسم الصنف"], line["الكمية"], line["السعر"])
            self.refresh(); self._select_invoice(invoice.id)
        except Exception as error:QMessageBox.warning(self,"تعذر حفظ البنود",str(error))
    def confirm(self):
        inv=self.selected_invoice()
        if inv:
            try:self.repo.confirm(inv.id);self.refresh()
            except Exception as e:QMessageBox.warning(self,"خطأ",str(e))

    def delete_line(self):
        invoice=self.selected_invoice()
        row=self.line_table.currentRow()
        if not invoice or row < 0 or row >= len(self._visible_lines):
            QMessageBox.information(self,"اختر بندًا","حدد بندًا من تفاصيل الفاتورة أولًا."); return
        if invoice.status != "مسودة":
            QMessageBox.information(self,"الفاتورة مؤكدة","لا يمكن تعديل بنود فاتورة مؤكدة."); return
        if QMessageBox.question(self,"حذف البند","هل تريد حذف البند المحدد؟") != QMessageBox.StandardButton.Yes:return
        try:self.repo.delete_line(invoice.id,self._visible_lines[row].id);self.refresh();self._select_invoice(invoice.id)
        except Exception as error:QMessageBox.warning(self,"تعذر حذف البند",str(error))

    def delete_draft(self):
        invoice=self.selected_invoice()
        if not invoice:return
        if invoice.status != "مسودة":
            QMessageBox.information(self,"لا يمكن الحذف","لا يمكن حذف فاتورة شراء مؤكدة لأنها مرتبطة بحركة المخزون."); return
        if QMessageBox.question(self,"حذف المسودة",f"هل تريد حذف المسودة {invoice.number}؟") != QMessageBox.StandardButton.Yes:return
        try:self.repo.delete_draft(invoice.id);self.refresh()
        except Exception as error:QMessageBox.warning(self,"تعذر حذف المسودة",str(error))
    def pay(self):
        inv=self.selected_invoice()
        if not inv:return
        dialog = FormDialog("سداد المورد", [("المبلغ", "number", 100)], self)
        if dialog.exec() != dialog.Accepted:
            return
        amount = dialog.values()["المبلغ"]
        try:self.repo.pay(inv.supplier_id,inv.id,amount);self.refresh()
        except Exception as e:QMessageBox.warning(self,"خطأ",str(e))

    def selected_invoice(self, show_message=True):
        row=self.table.currentRow()
        if row < 0 or row >= len(self._visible_invoices):
            if show_message:QMessageBox.information(self,"اختر فاتورة","حدد فاتورة من الجدول أولاً.")
            return None
        return self._visible_invoices[row]
    def selected_supplier(self, show_message=True):
        row=self.supplier_table.currentRow()
        if row<0 or row>=len(self._suppliers):
            if show_message:QMessageBox.information(self,"اختر مورداً","حدد مورداً من تبويب الموردين أولاً.")
            return None
        return self._suppliers[row]
    def edit_supplier(self):
        supplier=self.selected_supplier()
        if not supplier:return
        dialog = FormDialog("تعديل المورد", [("الاسم", "text", supplier.name)], self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        name = dialog.values()["الاسم"]
        try:self.repo.update_supplier(supplier.id,name);self.refresh()
        except Exception as error:QMessageBox.warning(self,"تعذر التعديل",str(error))
    def delete_supplier(self):
        supplier=self.selected_supplier()
        if not supplier:return
        if QMessageBox.question(self,"تأكيد الحذف",f"حذف المورد {supplier.name}؟")==QMessageBox.StandardButton.Yes:
            try:self.repo.delete_supplier(supplier.id);self.refresh()
            except Exception as error:QMessageBox.warning(self,"تعذر الحذف",str(error))
