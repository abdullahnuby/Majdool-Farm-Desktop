from PySide6.QtWidgets import QMessageBox,QTabWidget,QTableWidget,QTableWidgetItem,QDialog,QLabel,QFrame,QHBoxLayout,QVBoxLayout
from datetime import date
from PySide6.QtWidgets import QWidget
from app.presentation.ui_theme import PageShell,Toolbar,button,setup_table,FormDialog,InvoiceLineEditor
from app.infrastructure.sales_repository import SalesRepository
from app.infrastructure.crop_repository import CropRepository
class SalesPage(PageShell):
    def __init__(self):
        super().__init__("المبيعات والعملاء","الفواتير، بنود البيع والتحصيل.")
        self.repo=SalesRepository(); self.crop_repo=CropRepository(); tb=Toolbar("بحث برقم الفاتورة أو العميل…"); self.search=tb.search; self.content.addWidget(tb)
        summary=QHBoxLayout(); summary.setSpacing(12)
        self.invoice_count=self._summary_card("الفواتير", "0")
        self.open_count=self._summary_card("قيد المتابعة", "0")
        self.sales_total=self._summary_card("إجمالي المبيعات", "0")
        for card in (self.invoice_count,self.open_count,self.sales_total): summary.addWidget(card, 1)
        self.content.addLayout(summary)
        self.table=QTableWidget(0,6); self.table.setHorizontalHeaderLabels(["الفاتورة","التاريخ","العميل","الحالة","قبل الخصم","الإجمالي"]); setup_table(self.table)
        self.line_table=QTableWidget(0,5); self.line_table.setHorizontalHeaderLabels(["دفعة الحصاد","الدرجة","الكمية (كجم)","سعر الوحدة","الإجمالي"]); setup_table(self.line_table); self.line_table.setMinimumHeight(180)
        invoice_view=QWidget(); invoice_layout=QVBoxLayout(invoice_view); invoice_layout.setContentsMargins(0,0,0,0); invoice_layout.setSpacing(10)
        invoice_layout.addWidget(self.table, 3); invoice_layout.addWidget(QLabel("بنود الفاتورة المحددة"), 0); invoice_layout.addWidget(self.line_table, 2)
        self.customer_table=QTableWidget(0,6);self.customer_table.setHorizontalHeaderLabels(["الكود","العميل","الهاتف","إجمالي الفواتير","المدفوع","المتبقي"]);setup_table(self.customer_table)
        self.tabs=QTabWidget();self.tabs.addTab(invoice_view,"الفواتير");self.tabs.addTab(self.customer_table,"العملاء");self.content.addWidget(self.tabs,1)
        for t,f,k in [("＋ عميل جديد",self.customer,"normal"),("تعديل العميل",self.edit_customer,"normal"),("حذف العميل",self.delete_customer,"danger"),("＋ فاتورة جديدة",self.invoice,"primary"),("تعديل الفاتورة",self.edit_invoice,"normal"),("إضافة بند",self.line,"normal"),("حذف البند المحدد",self.delete_line,"danger"),("تأكيد الفاتورة",self.confirm,"normal"),("تحصيل",self.receipt,"normal"),("حذف/إلغاء الفاتورة",self.delete_or_cancel,"danger")]:self.actions.addWidget(button(t,k,f))
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

    def refresh(self):
        rows=self.repo.invoices(); self._invoices=rows; self._rows=[]
        self._customers=self.repo.customers(); self._customer_names={customer.id:customer.name for customer in self._customers}
        for x in rows:self._rows.append([x.number,x.invoice_date,self._customer_names.get(x.customer_id,"عميل غير معروف"),x.status,x.subtotal,x.total])
        open_count=sum(1 for invoice in rows if invoice.status not in ("مدفوعة", "ملغاة"))
        total=sum((invoice.total or 0) for invoice in rows)
        self._set_summary(self.invoice_count,len(rows)); self._set_summary(self.open_count,open_count); self._set_summary(self.sales_total,total)
        self._customer_financials={}
        for customer in self._customers:
            customer_invoices=[invoice for invoice in rows if invoice.customer_id == customer.id]
            invoiced=sum((invoice.total or 0) for invoice in customer_invoices)
            paid=sum((self.repo.paid_for(invoice.id) or 0) for invoice in customer_invoices)
            self._customer_financials[customer.id]=(invoiced,paid,max(0,invoiced-paid))
        self.filter_rows(self.search.text());self._render_customers()
    def _render(self,rows):
        self.table.setRowCount(len(rows))
        for i,r in enumerate(rows):
            for j,v in enumerate(r):self.table.setItem(i,j,QTableWidgetItem(str(v)))
    def _render_customers(self):
        self.customer_table.setRowCount(len(self._customers))
        for i,customer in enumerate(self._customers):
            invoiced,paid,outstanding=self._customer_financials.get(customer.id,(0,0,0))
            values=[customer.code,customer.name,customer.phone or "-",invoiced,paid,outstanding]
            for j,value in enumerate(values):self.customer_table.setItem(i,j,QTableWidgetItem(str(value)))

    def _render_selected_lines(self):
        invoice=self.selected_invoice(show_message=False)
        if not invoice:
            self.line_table.setRowCount(0)
            return
        lines=self.repo.lines(invoice.id); batches={batch.id:batch.number for batch in self.crop_repo.batches()}
        self._visible_lines=lines
        self.line_table.setRowCount(len(lines))
        for row,line in enumerate(lines):
            values=[batches.get(line.batch_id, f"دفعة {line.batch_id}"),line.grade,line.quantity_kg,line.unit_price,line.line_total]
            for column,value in enumerate(values):self.line_table.setItem(row,column,QTableWidgetItem(str(value)))
    def filter_rows(self,text):
        query=text.strip().lower(); matches=[(invoice,row) for invoice,row in zip(self._invoices,self._rows) if not query or query in " ".join(map(str,row)).lower()]
        self._visible_invoices=[invoice for invoice,row in matches];self._render([row for invoice,row in matches])
        self._render_selected_lines()
    def _resolve_invoice_customer(self):
        row = self.customer_table.currentRow()
        if row < 0 or row >= len(self._customers):
            raise ValueError("اختيار العميل مطلوب.")
        return self._customers[row]

    def customer(self):
        dialog = FormDialog("عميل جديد", [("الكود", "text", ""), ("الاسم", "text", "")], self)
        if dialog.exec() != dialog.Accepted:
            return
        values = dialog.values()
        code = values["الكود"]
        name = values["الاسم"]
        if code and name:
            try:self.repo.add_customer(code,name);self.refresh()
            except Exception as e:QMessageBox.warning(self,"خطأ",str(e))
    def invoice(self):
        if not self._customers:
            QMessageBox.information(self,"تنبيه","أنشئ عميلاً أولاً."); return
        batches=[(f"{batch.number}  •  متاح {self.crop_repo.ready_kg(batch.id):g} كجم", batch.id) for batch in self.crop_repo.batches() if self.crop_repo.ready_kg(batch.id) > 0]
        if not batches:
            QMessageBox.information(self,"لا توجد دفعات متاحة","أنشئ دفعة حصاد برصيد قابل للبيع أولًا."); return
        editor=InvoiceLineEditor("فاتورة بيع جديدة", [
            ("دفعة الحصاد", "combo", batches[0][1], batches), ("الدرجة", "text", "أولى"),
            ("الكمية (كجم)", "number", 1), ("سعر الوحدة", "number", 1),
        ], ["دفعة الحصاد", "الدرجة", "الكمية", "سعر الوحدة", "الإجمالي"], "إجمالي البند", self,
        [("دفعة الحصاد", "دفعة الحصاد"), ("الدرجة", "الدرجة"), ("الكمية", "الكمية (كجم)"), ("سعر الوحدة", "سعر الوحدة"), ("الإجمالي", "إجمالي البند")],
        lambda values: values["الكمية (كجم)"] * values["سعر الوحدة"],
        [("العميل", "combo", self._customers[0].id, [(c.name, c.id) for c in self._customers]), ("تاريخ الفاتورة", "date", date.today()), ("الخصم", "number", 0), ("الضريبة", "number", 0)])
        if editor.exec() != editor.Accepted:return
        values=editor.header_values()
        try:
            invoice=self.repo.create_invoice(values["العميل"],values["تاريخ الفاتورة"],values["الخصم"],values["الضريبة"])
            for line in editor.lines:self.repo.add_line(invoice.id, line["دفعة الحصاد"], line["الدرجة"], line["الكمية (كجم)"], line["سعر الوحدة"])
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
        batches=[(f"{batch.number}  •  متاح {self.crop_repo.ready_kg(batch.id):g} كجم",batch.id) for batch in self.crop_repo.batches() if self.crop_repo.ready_kg(batch.id)>0]
        editor=InvoiceLineEditor("تعديل فاتورة البيع",[("دفعة الحصاد","combo",batches[0][1],batches),("الدرجة","text","أولى"),("الكمية (كجم)","number",1),("سعر الوحدة","number",1)], ["دفعة الحصاد","الدرجة","الكمية","سعر الوحدة","الإجمالي"],"إجمالي البند",self,[("دفعة الحصاد","دفعة الحصاد"),("الدرجة","الدرجة"),("الكمية","الكمية (كجم)"),("سعر الوحدة","سعر الوحدة"),("الإجمالي","إجمالي البند")],lambda v:v["الكمية (كجم)"]*v["سعر الوحدة"],[("العميل","combo",invoice.customer_id,[(c.name,c.id) for c in self._customers]),("تاريخ الفاتورة","date",invoice.invoice_date),("الخصم","number",invoice.discount),("الضريبة","number",invoice.tax)])
        editor.set_lines([{"دفعة الحصاد":l.batch_id,"الدرجة":l.grade,"الكمية (كجم)":l.quantity_kg,"سعر الوحدة":l.unit_price,"إجمالي البند":l.line_total} for l in self.repo.lines(invoice.id)])
        if editor.exec()!=editor.Accepted:return
        v=editor.header_values()
        try:self.repo.update_draft(invoice.id,v["العميل"],v["تاريخ الفاتورة"],v["الخصم"],v["الضريبة"],[(l["دفعة الحصاد"],l["الدرجة"],l["الكمية (كجم)"],l["سعر الوحدة"]) for l in editor.lines]);self.refresh();self._select_invoice(invoice.id)
        except Exception as error:QMessageBox.warning(self,"تعذر تعديل الفاتورة",str(error))

    def _edit_new_invoice(self, invoice):
        batches=[]
        for batch in self.crop_repo.batches():
            balance=self.crop_repo.ready_kg(batch.id)
            if balance > 0:batches.append((f"{batch.number}  •  متاح {balance:g} كجم", batch.id))
        if not batches:
            QMessageBox.information(self,"لا توجد دفعات متاحة","أنشئ دفعة حصاد برصيد قابل للبيع أولًا.")
            return
        editor=InvoiceLineEditor("تفاصيل فاتورة البيع", [
            ("دفعة الحصاد", "combo", batches[0][1], batches),
            ("الدرجة", "text", "أولى"),
            ("الكمية (كجم)", "number", 1),
            ("سعر الوحدة", "number", 1),
        ], ["دفعة الحصاد", "الدرجة", "الكمية", "سعر الوحدة", "الإجمالي"], "إجمالي البند", self,
        [("دفعة الحصاد", "دفعة الحصاد"), ("الدرجة", "الدرجة"), ("الكمية", "الكمية (كجم)"), ("سعر الوحدة", "سعر الوحدة"), ("الإجمالي", "إجمالي البند")],
        lambda values: values["الكمية (كجم)"] * values["سعر الوحدة"])
        if editor.exec() != editor.Accepted:return
        try:
            for line in editor.lines:
                self.repo.add_line(invoice.id, line["دفعة الحصاد"], line["الدرجة"], line["الكمية (كجم)"], line["سعر الوحدة"])
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

    def delete_or_cancel(self):
        invoice=self.selected_invoice()
        if not invoice:return
        if invoice.status == "مسودة":
            action="حذف المسودة"
        elif invoice.status == "مؤكدة":
            action="إلغاء الفاتورة"
        else:
            QMessageBox.information(self,"الفاتورة ملغاة","هذه الفاتورة ملغاة بالفعل."); return
        if QMessageBox.question(self,"تأكيد العملية",f"هل تريد {action} {invoice.number}؟") != QMessageBox.StandardButton.Yes:return
        try:
            if invoice.status == "مسودة":self.repo.delete_draft(invoice.id)
            else:self.repo.cancel(invoice.id)
            self.refresh()
        except Exception as error:QMessageBox.warning(self,"تعذر تنفيذ العملية",str(error))
    def receipt(self):
        inv=self.selected_invoice()
        if not inv:return
        dialog = FormDialog("تحصيل", [("المبلغ", "number", 1)], self)
        if dialog.exec() != dialog.Accepted:
            return
        amount = dialog.values()["المبلغ"]
        try:self.repo.add_receipt(inv.customer_id,inv.id,amount);self.refresh()
        except Exception as e:QMessageBox.warning(self,"خطأ",str(e))

    def selected_invoice(self, show_message=True):
        row=self.table.currentRow()
        if row < 0 or row >= len(self._visible_invoices):
            if show_message:QMessageBox.information(self,"اختر فاتورة","حدد فاتورة من الجدول أولاً.")
            return None
        return self._visible_invoices[row]
    def selected_customer(self, show_message=True):
        row=self.customer_table.currentRow()
        if row<0 or row>=len(self._customers):
            if show_message:QMessageBox.information(self,"اختر عميلاً","حدد عميلاً من تبويب العملاء أولاً.")
            return None
        return self._customers[row]
    def edit_customer(self):
        customer=self.selected_customer()
        if not customer:return
        dialog = FormDialog("تعديل العميل", [("الاسم", "text", customer.name)], self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        name = dialog.values()["الاسم"]
        try:self.repo.update_customer(customer.id,name);self.refresh()
        except Exception as error:QMessageBox.warning(self,"تعذر التعديل",str(error))
    def delete_customer(self):
        customer=self.selected_customer()
        if not customer:return
        if QMessageBox.question(self,"تأكيد الحذف",f"حذف العميل {customer.name}؟")==QMessageBox.StandardButton.Yes:
            try:self.repo.delete_customer(customer.id);self.refresh()
            except Exception as error:QMessageBox.warning(self,"تعذر الحذف",str(error))
