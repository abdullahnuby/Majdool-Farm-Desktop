from PySide6.QtWidgets import QHBoxLayout,QGridLayout,QLabel,QFrame,QVBoxLayout
from app.presentation.ui_theme import PageShell,StatCard,button
from app.infrastructure.repositories import StructureRepository
from app.infrastructure.operations_repository import OperationsRepository
from app.infrastructure.crop_repository import CropRepository
from app.infrastructure.sales_repository import SalesRepository

from app.logging_config import logger

class DashboardPage(PageShell):
    def __init__(self):
        super().__init__("لوحة التحكم","نظرة تشغيلية سريعة على المزرعة والمخزون والمبيعات.")
        self.actions.addWidget(button("تحديث البيانات", "normal", self.refresh))
        self.st=StructureRepository(); self.op=OperationsRepository(); self.crop=CropRepository(); self.sales=SalesRepository()
        grid=QGridLayout(); grid.setSpacing(12)
        self.cards=[]
        data=[("المزارع","0","كيان إداري"),("البلوكات","0","ضمن هيكل المزرعة"),("النخيل","0","إجمالي الأشجار"),
              ("صيانة مفتوحة","0","تحتاج متابعة"),("دفعات حصاد","0","مسجلة"),("فواتير بيع","0","كل الحالات"),("العملاء","0","قاعدة العملاء")]
        for i,(a,b,c) in enumerate(data):
            card=StatCard(a,b,c,["⌂","▦","◉","⚠","◌","▣","♙"][i]); self.cards.append(card); grid.addWidget(card,i//4,i%4)
        self.content.addLayout(grid)
        panels=QHBoxLayout(); panels.setSpacing(12)
        attention=QFrame(); attention.setObjectName("Card"); attention_layout=QVBoxLayout(attention); attention_layout.setContentsMargins(18,16,18,16); attention_layout.setSpacing(8)
        attention_title=QLabel("يحتاج انتباهك"); attention_title.setStyleSheet("font-size:16px;font-weight:800;"); attention_layout.addWidget(attention_title)
        for txt in ["تابع المخزون منخفض الرصيد قبل بدء عمليات جديدة.","راجع دفعات الحصاد والمبيعات المرتبطة بها.","أغلق عمليات الصيانة المفتوحة في موعدها."]:
            row=QLabel("•  "+txt); row.setStyleSheet("color:#52675a;padding:5px;"); attention_layout.addWidget(row)
        attention_layout.addStretch()
        panels.addWidget(attention, 1)

        focus=QFrame(); focus.setObjectName("Card"); focus_layout=QVBoxLayout(focus); focus_layout.setContentsMargins(18,16,18,16); focus_layout.setSpacing(8)
        focus_title=QLabel("ملخص التشغيل"); focus_title.setStyleSheet("font-size:16px;font-weight:800;"); focus_layout.addWidget(focus_title)
        for label, value in [("الحالة الحالية", "قاعدة البيانات المحلية متصلة"), ("نطاق العرض", "كل المزارع والمواسم"), ("آخر تحديث", "عند فتح الشاشة أو الضغط على تحديث")]:
            row=QHBoxLayout(); key=QLabel(label); key.setObjectName("CardLabel"); val=QLabel(value); val.setStyleSheet("font-weight:700;color:#315342;"); row.addWidget(key); row.addStretch(); row.addWidget(val); focus_layout.addLayout(row)
        focus_layout.addStretch()
        panels.addWidget(focus, 1)
        self.content.addLayout(panels)
        self.refresh()
    def refresh(self):
        try:
            a,b,c,d=self.st.stats()
            vals=[a,c,d,self.op.open_orders_count(),len(self.crop.batches()),len(self.sales.invoices()),len(self.sales.customers())]
            for card,v in zip(self.cards,vals): card.set_value(f"{v:,}")
        except Exception:
            logger.exception("تعذر تحديث مؤشرات لوحة التحكم")
