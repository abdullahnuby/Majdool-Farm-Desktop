from PySide6.QtWidgets import QTableWidget,QTableWidgetItem,QInputDialog,QMessageBox,QLabel
from app.presentation.ui_theme import PageShell,Toolbar,button,setup_table
from app.infrastructure.repositories import FarmRepository,StructureRepository
class FarmStructurePage(PageShell):
    def __init__(self):
        super().__init__("هيكل المزرعة","المزارع والقطاعات والبلوكات.")
        self.f=FarmRepository();self.s=StructureRepository()
        toolbar=Toolbar("بحث في هيكل المزرعة…");self.search=toolbar.search;self.content.addWidget(toolbar)
        self.table=QTableWidget(0,4);self.table.setHorizontalHeaderLabels(["النوع","الكود","الاسم","الحالة"]);setup_table(self.table);self.content.addWidget(self.table,1)
        for t,f,k in [("＋ مزرعة",self.add,"primary"),("＋ قطاع",self.sector,"normal"),("＋ بلوك",self.block,"normal")]:self.actions.addWidget(button(t,k,f))
        self.search.textChanged.connect(self.filter_rows)
        self._rows=[]
        self.refresh()
    def refresh(self):
        rows=[]
        try:
            for farm in self.f.list():
                rows.append(["مزرعة",farm.id,getattr(farm,"name","-"),"نشطة"])
                for sec in self.s.sectors(farm.id):
                    rows.append(["قطاع",sec.id,getattr(sec,"name","-"),"نشط"])
                    for block in self.s.blocks(sec.id):
                        rows.append(["بلوك",block.code,getattr(block,"name","-"),"نشط"])
        except Exception:pass
        self._rows=rows;self.filter_rows(self.search.text())
    def filter_rows(self,text):
        query=text.strip().lower()
        rows=[row for row in self._rows if not query or query in " ".join(map(str,row)).lower()]
        self.table.setRowCount(len(rows))
        for i,row in enumerate(rows):
            for j,value in enumerate(row):self.table.setItem(i,j,QTableWidgetItem(str(value)))
    def add(self):
        n,ok=QInputDialog.getText(self,"إضافة مزرعة","اسم المزرعة:")
        if ok and n.strip():self.f.create(n);self.refresh()
    def sector(self):
        fs=self.f.list()
        if not fs:QMessageBox.information(self,"تنبيه","أضف مزرعة أولاً.");return
        n,ok=QInputDialog.getText(self,"إضافة قطاع","اسم القطاع:")
        if ok and n.strip():self.s.create_sector(fs[0].id,n);self.refresh()
    def block(self):
        fs=self.f.list()
        if not fs:return
        ss=self.s.sectors(fs[0].id)
        if not ss:QMessageBox.information(self,"تنبيه","أضف قطاعاً أولاً.");return
        c,ok=QInputDialog.getText(self,"إضافة بلوك","كود البلوك:")
        if ok and c.strip():self.s.create_block(ss[0].id,c,c);self.refresh()
