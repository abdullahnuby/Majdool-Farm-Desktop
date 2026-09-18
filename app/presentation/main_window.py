# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (
    QMainWindow,QWidget,QHBoxLayout,QListWidget,QListWidgetItem,QStackedWidget,
    QLabel,QVBoxLayout,QFrame,QToolButton,QLineEdit
)
from PySide6.QtCore import Qt
from app.presentation.ui_theme import APP_QSS

from app.presentation.dashboard_page import DashboardPage
from app.presentation.farm_structure_page import FarmStructurePage
from app.presentation.agriculture_page import AgriculturePage
from app.presentation.inventory_page import InventoryPage
from app.presentation.operations_page import OperationsPage
from app.presentation.crop_page import CropPage
from app.presentation.sales_page import SalesPage
from app.presentation.hr_page import HRPage
from app.presentation.consultants_page import ConsultantsPage
from app.presentation.purchases_page import PurchasesPage
from app.presentation.assets_page import AssetsPage
from app.presentation.reports_page import ReportsPage
from app.presentation.settings_page import SettingsPage

from app.logging_config import logger

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("مدير مزرعة المجدول")
        self.setMinimumSize(1180, 720)
        self.resize(1500, 900)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet(APP_QSS)
        self._build()

    def _build(self):
        root=QWidget(); self.setCentralWidget(root)
        layout=QHBoxLayout(root); layout.setContentsMargins(0,0,0,0); layout.setSpacing(0)

        sidebar=QFrame(); sidebar.setObjectName("Sidebar"); sidebar.setFixedWidth(250)
        sl=QVBoxLayout(sidebar); sl.setContentsMargins(10,18,10,14); sl.setSpacing(4)

        brand=QFrame(); brand.setObjectName("Brand")
        bl=QVBoxLayout(brand); bl.setContentsMargins(12,4,12,16); bl.setSpacing(2)
        title=QLabel("مُدير مزرعة المجدول"); title.setObjectName("BrandTitle")
        sub=QLabel("نظام إدارة المزرعة • V12"); sub.setObjectName("BrandSub")
        bl.addWidget(title); bl.addWidget(sub); sl.addWidget(brand)

        sec=QLabel("الرئيسية"); sec.setObjectName("SectionLabel"); sl.addWidget(sec)
        self.menu=QListWidget(); self.menu.setObjectName("Nav"); self.menu.setSpacing(2)
        items=[
            ("▦","لوحة التحكم"),("⌂","هيكل المزرعة"),("◉","الري والتسميد"),
            ("▤","المخازن"),("◫","المشتريات"),("⚙","العمليات والصيانة"),
            ("◌","المحصول والحصاد"),("▣","المبيعات والعملاء"),("▰","الأصول والمعدات"),
            ("♙","الموظفون والرواتب"),("✦","الاستشاريون"),("▥","التقارير"),("⚙","الإعدادات")
        ]
        for icon,name in items:
            item=QListWidgetItem(f"  {icon}   {name}")
            item.setSizeHint(item.sizeHint()); self.menu.addItem(item)
        sl.addWidget(self.menu,1)

        footer=QFrame(); fl=QVBoxLayout(footer); fl.setContentsMargins(12,8,12,0)
        sync=QLabel("●  قاعدة البيانات المحلية تعمل"); sync.setStyleSheet("color:#86efac;font-size:11px;")
        fl.addWidget(sync); sl.addWidget(footer)
        layout.addWidget(sidebar)

        right=QWidget(); rl=QVBoxLayout(right); rl.setContentsMargins(0,0,0,0); rl.setSpacing(0)
        top=QFrame(); top.setObjectName("Topbar"); tl=QHBoxLayout(top); tl.setContentsMargins(24,10,24,10); tl.setSpacing(10)
        context=QVBoxLayout(); context.setSpacing(0)
        top_title=QLabel("مركز إدارة المزرعة"); top_title.setObjectName("TopbarTitle"); context.addWidget(top_title)
        self.breadcrumb=QLabel("لوحة التحكم"); self.breadcrumb.setObjectName("Breadcrumb"); context.addWidget(self.breadcrumb)
        tl.addLayout(context)
        tl.addStretch()
        search=QLineEdit(); search.setObjectName("GlobalSearch"); search.setPlaceholderText("ابحث في المزرعة..."); search.setClearButtonEnabled(True); search.setFixedWidth(250); tl.addWidget(search)
        user=QLabel("مدير المزرعة  •  الإدارة"); user.setStyleSheet("font-weight:700;color:#334155;")
        tl.addWidget(user); rl.addWidget(top)

        self.pages=QStackedWidget()
        pages=[
            DashboardPage(), FarmStructurePage(), AgriculturePage(), InventoryPage(),
            PurchasesPage(), OperationsPage(), CropPage(), SalesPage(),
            AssetsPage(),
            HRPage(), ConsultantsPage(),
            ReportsPage(),
            SettingsPage()
        ]
        for p in pages: self.pages.addWidget(p)
        rl.addWidget(self.pages,1); layout.addWidget(right,1)

        self.menu.currentRowChanged.connect(self._navigate)
        self.menu.setCurrentRow(0)

    def _placeholder(self,title,subtitle):
        from app.presentation.ui_theme import PageShell, empty_state
        p=PageShell(title,subtitle); p.content.addWidget(empty_state("هذه الوحدة جاهزة للواجهة وسيتم توصيل وظائفها مع طبقة البيانات دون تغييرها.")); return p

    def _navigate(self,index):
        self.pages.setCurrentIndex(index)
        item=self.menu.item(index)
        if item: self.breadcrumb.setText(item.text().strip())
        page=self.pages.currentWidget()
        if hasattr(page,"refresh"):
            try: page.refresh()
            except Exception: logger.exception("تعذر تحديث الصفحة")
