from PySide6.QtWidgets import QHBoxLayout,QGridLayout,QLabel,QFrame,QVBoxLayout
from app.presentation.ui_theme import PageShell,StatCard
from app.infrastructure.repositories import StructureRepository
from app.infrastructure.operations_repository import OperationsRepository
from app.infrastructure.crop_repository import CropRepository
from app.infrastructure.sales_repository import SalesRepository

class DashboardPage(PageShell):
    def __init__(self):
        super().__init__("لوحة التحكم","نظرة تشغيلية سريعة على المزرعة والمخزون والمبيعات.")
        self.st=StructureRepository(); self.op=OperationsRepository(); self.crop=CropRepository(); self.sales=SalesRepository()
        grid=QGridLayout(); grid.setSpacing(12)
        self.cards=[]
        data=[("المزارع","0","كيان إداري"),("البلوكات","0","ضمن هيكل المزرعة"),("النخيل","0","إجمالي الأشجار"),
              ("صيانة مفتوحة","0","تحتاج متابعة"),("دفعات حصاد","0","مسجلة"),("فواتير بيع","0","كل الحالات"),("العملاء","0","قاعدة العملاء")]
        for i,(a,b,c) in enumerate(data):
            card=StatCard(a,b,c,["⌂","▦","◉","⚠","◌","▣","♙"][i]); self.cards.append(card); grid.addWidget(card,i//4,i%4)
        self.content.addLayout(grid)
        panel=QFrame(); panel.setObjectName("Card"); pl=QVBoxLayout(panel); pl.setContentsMargins(18,16,18,16)
        h=QLabel("مؤشرات المتابعة"); h.setStyleSheet("font-size:16px;font-weight:800;"); pl.addWidget(h)
        for txt in ["تابع المخزون منخفض الرصيد قبل بدء عمليات جديدة.","راجع دفعات الحصاد والمبيعات المرتبطة بها.","أغلق عمليات الصيانة المفتوحة في موعدها."]:
            x=QLabel("•  "+txt); x.setStyleSheet("color:#475569;padding:6px;"); pl.addWidget(x)
        self.content.addWidget(panel); self.refresh()
    def refresh(self):
        try:
            a,b,c,d=self.st.stats()
            vals=[a,c,d,self.op.open_orders_count(),len(self.crop.batches()),len(self.sales.invoices()),len(self.sales.customers())]
            for card,v in zip(self.cards,vals): card.set_value(f"{v:,}")
        except Exception:
            pass
