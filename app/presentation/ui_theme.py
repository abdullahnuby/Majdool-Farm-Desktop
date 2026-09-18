# -*- coding: utf-8 -*-
"""Shared visual system for the Arabic-first desktop application."""
APP_QSS = """
* { font-family: "Cairo", "Segoe UI"; }
QWidget { color: #17211b; font-size: 13px; }
QMainWindow, QDialog { background: #f3f5f1; }
QFrame#Sidebar { background: #17352c; border: none; }
QFrame#Brand { background: transparent; }
QLabel#BrandTitle { color: #f5f7ee; font-size: 19px; font-weight: 800; }
QLabel#BrandSub { color: #aac5b6; font-size: 11px; }
QLabel#SectionLabel { color: #9fc0ae; font-size: 11px; font-weight: 700; padding: 8px 14px 4px; }
QListWidget#Nav { background: transparent; border: none; outline: none; padding: 8px; }
QListWidget#Nav::item { color: #d4e4da; padding: 12px 14px; margin: 2px 0; border-radius: 8px; }
QListWidget#Nav::item:hover { background: #245143; color: white; }
QListWidget#Nav::item:selected { background: #d4a64a; color: #17352c; font-weight: 800; }
QFrame#Topbar { background: #ffffff; border-bottom: 1px solid #dfe7df; }
QLabel#TopbarTitle { color: #17352c; font-size: 16px; font-weight: 800; }
QLabel#Breadcrumb { color: #708277; font-size: 12px; }
QLabel#PageTitle { color: #17352c; font-size: 26px; font-weight: 800; }
QLabel#PageSubtitle { color: #708277; font-size: 12px; }
QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox, QSpinBox {
 background: white; border: 1px solid #d5e0d8; border-radius: 7px; padding: 9px 11px; min-height: 18px;
}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus { border: 1px solid #2f8064; }
QLineEdit#GlobalSearch { background: #f3f7f3; border: 1px solid #e0e9e1; border-radius: 16px; padding: 7px 14px; }
QPushButton { background: #f1f5f1; border: 1px solid #d5e0d8; border-radius: 7px; padding: 9px 14px; font-weight: 600; }
QPushButton:hover { background: #e5eee7; }
QPushButton#Primary { background: #2f8064; color: white; border: 1px solid #2f8064; }
QPushButton#Primary:hover { background: #266b53; }
QPushButton#Danger { background: #fff1ef; color: #b63b2f; border: 1px solid #f2c9c2; }
QPushButton#Ghost { background: transparent; border: none; color: #64748b; }
QToolButton#TopbarAction { background: #f5f8f5; color: #315342; border: 1px solid #e0e9e1; border-radius: 7px; padding: 7px 10px; }
QToolButton#TopbarAction:hover { background: #e8f1e9; }
QFrame#Card { background: white; border: 1px solid #e0e9e1; border-radius: 10px; }
QLabel#CardLabel { color: #708277; font-size: 12px; }
QLabel#CardValue { color: #17352c; font-size: 23px; font-weight: 800; }
QLabel#CardHint { color: #9aaba0; font-size: 11px; }
QFrame#Toolbar { background: white; border: 1px solid #e0e9e1; border-radius: 9px; }
QTableWidget { background: white; border: 1px solid #e0e9e1; border-radius: 9px; gridline-color: #edf2ee; alternate-background-color: #fafcf9; selection-background-color: #dceee2; selection-color: #17352c; }
QHeaderView::section { background: #f5f8f5; color: #61756a; border: none; border-bottom: 1px solid #e0e9e1; padding: 10px; font-weight: 700; }
QScrollBar:vertical { background: transparent; width: 8px; margin: 3px; }
QScrollBar::handle:vertical { background: #cbd5e1; border-radius: 4px; min-height: 30px; }
QStatusBar { background: white; color: #708277; border-top: 1px solid #dfe7df; }
QMessageBox { background: white; }
"""

from PySide6.QtWidgets import (
    QFrame, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QToolButton,
    QDialog, QDialogButtonBox, QFormLayout, QComboBox, QDoubleSpinBox,
    QSpinBox, QDateEdit
)
from PySide6.QtCore import Qt, QDate

def button(text, kind="normal", callback=None):
    b = QPushButton(text)
    if kind in ("primary", "danger", "ghost"):
        b.setObjectName({"primary":"Primary","danger":"Danger","ghost":"Ghost"}[kind])
    if callback: b.clicked.connect(callback)
    return b

class StatCard(QFrame):
    def __init__(self, label, value="0", hint="", icon=""):
        super().__init__()
        self.setObjectName("Card")
        lay=QVBoxLayout(self); lay.setContentsMargins(16,14,16,14); lay.setSpacing(4)
        top=QHBoxLayout()
        a=QLabel(label); a.setObjectName("CardLabel"); top.addWidget(a); top.addStretch()
        if icon:
            ic=QLabel(icon); ic.setStyleSheet("font-size:18px;"); top.addWidget(ic)
        lay.addLayout(top)
        self.value=QLabel(value); self.value.setObjectName("CardValue"); lay.addWidget(self.value)
        h=QLabel(hint); h.setObjectName("CardHint"); lay.addWidget(h)
    def set_value(self, value): self.value.setText(str(value))

class PageShell(QFrame):
    def __init__(self, title, subtitle=""):
        super().__init__()
        outer=QVBoxLayout(self); outer.setContentsMargins(28,24,28,24); outer.setSpacing(16)
        head=QHBoxLayout()
        box=QVBoxLayout(); box.setSpacing(2)
        t=QLabel(title); t.setObjectName("PageTitle"); box.addWidget(t)
        if subtitle:
            s=QLabel(subtitle); s.setObjectName("PageSubtitle"); box.addWidget(s)
        head.addLayout(box); head.addStretch()
        self.actions=QHBoxLayout(); self.actions.setSpacing(8); head.addLayout(self.actions)
        outer.addLayout(head)
        self.content=QVBoxLayout(); self.content.setSpacing(14); outer.addLayout(self.content,1)

class Toolbar(QFrame):
    def __init__(self, placeholder="بحث..."):
        super().__init__(); self.setObjectName("Toolbar")
        l=QHBoxLayout(self); l.setContentsMargins(10,8,10,8); l.setSpacing(8)
        self.search=QLineEdit(); self.search.setPlaceholderText(placeholder); self.search.setClearButtonEnabled(True)
        l.addWidget(self.search,1); self.right=QHBoxLayout(); l.addLayout(self.right)

def setup_table(table):
    table.setAlternatingRowColors(True)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setStretchLastSection(True)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    table.setMinimumHeight(330)

class FormDialog(QDialog):
    Accepted = QDialog.DialogCode.Accepted

    def __init__(self, title, fields, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setMinimumWidth(420)
        self.fields = fields
        self._widgets = {}
        self._field_types = {}
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setFormAlignment(Qt.AlignmentFlag.AlignTop)
        for field_name, field_type, default_value, *extra in fields:
            widget = self._make_widget(field_type, default_value, extra[0] if extra else None)
            self._widgets[field_name] = widget
            self._field_types[field_name] = field_type
            form.addRow(field_name, widget)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _make_widget(self, field_type, default_value, options=None):
        if field_type == "text":
            widget = QLineEdit(str(default_value or ""))
        elif field_type == "number":
            widget = QDoubleSpinBox(); widget.setRange(-1000000000, 1000000000); widget.setDecimals(2); widget.setValue(float(default_value or 0))
        elif field_type == "int":
            widget = QSpinBox(); widget.setRange(-1000000000, 1000000000); widget.setValue(int(default_value or 0))
        elif field_type == "date":
            widget = QDateEdit(); widget.setDisplayFormat("yyyy-MM-dd"); widget.setDate(QDate.fromString(str(default_value or ""), "yyyy-MM-dd") if default_value else QDate.currentDate())
        elif field_type == "combo":
            widget = QComboBox();
            for label, value in (options or []):
                widget.addItem(label, value)
            if default_value is not None:
                for idx in range(widget.count()):
                    if widget.itemData(idx) == default_value:
                        widget.setCurrentIndex(idx); break
            elif widget.count():
                widget.setCurrentIndex(0)
        else:
            widget = QLineEdit(str(default_value or ""))
        return widget

    def values(self):
        result = {}
        for field_name, widget in self._widgets.items():
            field_type = self._field_types[field_name]
            if field_type == "text":
                result[field_name] = widget.text().strip()
            elif field_type == "number":
                result[field_name] = widget.value()
            elif field_type == "int":
                result[field_name] = widget.value()
            elif field_type == "date":
                result[field_name] = widget.date().toPython()
            elif field_type == "combo":
                result[field_name] = widget.currentData()
            else:
                result[field_name] = widget.text().strip()
        return result


class InvoiceLineEditor(QDialog):
    """Reusable line editor for invoices and other multi-row documents."""

    Accepted = QDialog.DialogCode.Accepted

    def __init__(self, title, fields, headers, line_total_key, parent=None, display_fields=None, total_calculator=None, header_fields=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setMinimumSize(760, 520)
        self.fields = fields
        self.line_total_key = line_total_key
        self.display_fields = display_fields or [(field[0], field[0]) for field in fields]
        self.total_calculator = total_calculator
        self.header_fields = header_fields or []
        self.lines = []
        layout = QVBoxLayout(self)
        self._header_widgets = {}
        if self.header_fields:
            header_form = QFormLayout()
            header_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
            for name, field_type, default_value, *extra in self.header_fields:
                widget = FormDialog._make_widget(self, field_type, default_value, extra[0] if extra else None)
                self._header_widgets[name] = widget
                header_form.addRow(name, widget)
            layout.addLayout(header_form)
        heading = QLabel("بنود المستند")
        heading.setStyleSheet("font-size:18px;font-weight:800;color:#17352c;")
        layout.addWidget(heading)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self._widgets = {}
        for name, field_type, default_value, *extra in fields:
            widget = FormDialog._make_widget(self, field_type, default_value, extra[0] if extra else None)
            self._widgets[name] = widget
            form.addRow(name, widget)
        add_row = QHBoxLayout()
        add_row.addLayout(form, 1)
        add_button = button("إضافة البند", "primary", self._add_line)
        add_row.addWidget(add_button)
        layout.addLayout(add_row)

        self.table = QTableWidget(0, len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        setup_table(self.table)
        self.table.setMinimumHeight(210)
        layout.addWidget(self.table, 1)
        remove_button = button("حذف البند المحدد", "danger", self._remove_line)
        layout.addWidget(remove_button, 0, Qt.AlignmentFlag.AlignLeft)

        footer = QHBoxLayout()
        self.error = QLabel("")
        self.error.setStyleSheet("color:#b63b2f;font-weight:600;")
        footer.addWidget(self.error)
        footer.addStretch()
        self.total = QLabel("الإجمالي: 0")
        self.total.setStyleSheet("font-size:18px;font-weight:800;color:#17352c;")
        footer.addWidget(self.total)
        layout.addLayout(footer)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _values(self):
        values = {}
        for name, widget in self._widgets.items():
            if isinstance(widget, QComboBox):
                values[name] = widget.currentData()
            elif isinstance(widget, QDoubleSpinBox):
                values[name] = widget.value()
            elif isinstance(widget, QSpinBox):
                values[name] = widget.value()
            else:
                values[name] = widget.text().strip()
        return values

    def header_values(self):
        values = {}
        for name, widget in self._header_widgets.items():
            if isinstance(widget, QComboBox): values[name] = widget.currentData()
            elif isinstance(widget, QDoubleSpinBox): values[name] = widget.value()
            elif isinstance(widget, QSpinBox): values[name] = widget.value()
            elif isinstance(widget, QDateEdit): values[name] = widget.date().toPython()
            else: values[name] = widget.text().strip()
        return values

    def _add_line(self):
        values = self._values()
        try:
            if self.total_calculator:
                values[self.line_total_key] = self.total_calculator(values)
            if not values.get(self.line_total_key, 0) > 0:
                raise ValueError("قيمة البند يجب أن تكون أكبر من صفر.")
            self.lines.append(values)
            self._render()
            self.error.clear()
        except (TypeError, ValueError) as error:
            self.error.setText(str(error))

    def set_lines(self, lines):
        self.lines = list(lines)
        self._render()

    def _render(self):
        self.table.setRowCount(len(self.lines))
        names = [key for _, key in self.display_fields]
        for row, values in enumerate(self.lines):
            for column, name in enumerate(names):
                value=values.get(name, "")
                self.table.setItem(row, column, QTableWidgetItem(f"{value:,.2f}" if isinstance(value, float) else str(value)))
        total = sum(float(line.get(self.line_total_key, 0) or 0) for line in self.lines)
        self.total.setText(f"الإجمالي: {total:,.2f}")

    def _remove_line(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self.lines):
            self.error.setText("حدد بندًا من الجدول أولًا.")
            return
        self.lines.pop(row)
        self._render()
        self.error.clear()

    def _accept(self):
        if not self.lines:
            self.error.setText("أضف بندًا واحدًا على الأقل قبل الحفظ.")
            return
        self.accept()


def empty_state(text):
    f=QFrame(); f.setObjectName("Card"); l=QVBoxLayout(f); l.setContentsMargins(24,30,24,30)
    a=QLabel("لا توجد بيانات"); a.setStyleSheet("font-size:17px;font-weight:800;"); a.setAlignment(Qt.AlignmentFlag.AlignCenter)
    b=QLabel(text); b.setObjectName("PageSubtitle"); b.setAlignment(Qt.AlignmentFlag.AlignCenter)
    l.addWidget(a); l.addWidget(b); return f
