# -*- coding: utf-8 -*-
"""Visual system for Medjool Farm Manager V12."""
APP_QSS = """
* { font-family: "Segoe UI"; }
QWidget { color: #18212f; font-size: 13px; }
QMainWindow, QDialog { background: #f5f7fb; }
QFrame#Sidebar { background: #0f172a; border: none; }
QFrame#Brand { background: transparent; }
QLabel#BrandTitle { color: white; font-size: 19px; font-weight: 800; }
QLabel#BrandSub { color: #94a3b8; font-size: 11px; }
QLabel#SectionLabel { color: #64748b; font-size: 11px; font-weight: 700; padding: 8px 14px 4px; }
QListWidget#Nav { background: transparent; border: none; outline: none; padding: 8px; }
QListWidget#Nav::item { color: #cbd5e1; padding: 12px 14px; margin: 2px 0; border-radius: 9px; }
QListWidget#Nav::item:hover { background: #1e293b; color: white; }
QListWidget#Nav::item:selected { background: #2563eb; color: white; font-weight: 700; }
QFrame#Topbar { background: white; border-bottom: 1px solid #e5e7eb; }
QLabel#Breadcrumb { color: #64748b; font-size: 12px; }
QLabel#PageTitle { color: #0f172a; font-size: 26px; font-weight: 800; }
QLabel#PageSubtitle { color: #64748b; font-size: 12px; }
QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox, QSpinBox {
 background: white; border: 1px solid #dbe2ea; border-radius: 8px; padding: 9px 11px; min-height: 18px;
}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus { border: 1px solid #2563eb; }
QPushButton { background: #eef2f7; border: 1px solid #dbe2ea; border-radius: 8px; padding: 9px 14px; font-weight: 600; }
QPushButton:hover { background: #e2e8f0; }
QPushButton#Primary { background: #2563eb; color: white; border: 1px solid #2563eb; }
QPushButton#Primary:hover { background: #1d4ed8; }
QPushButton#Danger { background: #fff1f2; color: #be123c; border: 1px solid #fecdd3; }
QPushButton#Ghost { background: transparent; border: none; color: #64748b; }
QFrame#Card { background: white; border: 1px solid #e6eaf0; border-radius: 12px; }
QLabel#CardLabel { color: #64748b; font-size: 12px; }
QLabel#CardValue { color: #0f172a; font-size: 23px; font-weight: 800; }
QLabel#CardHint { color: #94a3b8; font-size: 11px; }
QFrame#Toolbar { background: white; border: 1px solid #e6eaf0; border-radius: 10px; }
QTableWidget { background: white; border: 1px solid #e6eaf0; border-radius: 10px; gridline-color: #eef2f6; alternate-background-color: #fafbfc; selection-background-color: #dbeafe; selection-color: #0f172a; }
QHeaderView::section { background: #f8fafc; color: #64748b; border: none; border-bottom: 1px solid #e6eaf0; padding: 10px; font-weight: 700; }
QScrollBar:vertical { background: transparent; width: 8px; margin: 3px; }
QScrollBar::handle:vertical { background: #cbd5e1; border-radius: 4px; min-height: 30px; }
QStatusBar { background: white; color: #64748b; border-top: 1px solid #e5e7eb; }
QMessageBox { background: white; }
"""

from PySide6.QtWidgets import (
    QFrame, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QLineEdit,
    QTableWidget, QHeaderView, QAbstractItemView, QToolButton
)
from PySide6.QtCore import Qt

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

def empty_state(text):
    f=QFrame(); f.setObjectName("Card"); l=QVBoxLayout(f); l.setContentsMargins(24,30,24,30)
    a=QLabel("لا توجد بيانات"); a.setStyleSheet("font-size:17px;font-weight:800;"); a.setAlignment(Qt.AlignmentFlag.AlignCenter)
    b=QLabel(text); b.setObjectName("PageSubtitle"); b.setAlignment(Qt.AlignmentFlag.AlignCenter)
    l.addWidget(a); l.addWidget(b); return f
