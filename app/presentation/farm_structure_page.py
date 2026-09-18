from PySide6.QtWidgets import QMessageBox, QTreeWidget, QTreeWidgetItem, QDialog, QLabel, QFrame, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt

from app.infrastructure.repositories import FarmRepository, StructureRepository
from app.logging_config import logger
from app.presentation.ui_theme import PageShell, Toolbar, button, setup_table, FormDialog


class FarmStructurePage(PageShell):
    def __init__(self):
        super().__init__("هيكل المزرعة", "المزارع والقطاعات والبلوكات.")
        self.f = FarmRepository()
        self.s = StructureRepository()
        toolbar = Toolbar("بحث في هيكل المزرعة…")
        self.search = toolbar.search
        self.content.addWidget(toolbar)

        layout=QHBoxLayout(); layout.setSpacing(14)
        self.tree=QTreeWidget(); self.tree.setHeaderLabels(["هيكل المزرعة","الكود","الحالة"]); self.tree.setColumnWidth(0,300); self.tree.setMinimumWidth(520)
        self.detail=QFrame(); self.detail.setObjectName("Card"); detail_layout=QVBoxLayout(self.detail); detail_layout.setContentsMargins(20,18,20,18); detail_layout.setSpacing(10)
        self.detail_title=QLabel("اختر عنصرًا من الشجرة"); self.detail_title.setStyleSheet("font-size:19px;font-weight:800;color:#17352c;"); detail_layout.addWidget(self.detail_title)
        self.detail_body=QLabel("ستظهر هنا بيانات المزرعة أو القطاع أو البلوك."); self.detail_body.setWordWrap(True); self.detail_body.setObjectName("PageSubtitle"); detail_layout.addWidget(self.detail_body); detail_layout.addStretch()
        layout.addWidget(self.tree, 2); layout.addWidget(self.detail, 1); self.content.addLayout(layout,1)

        for label, func_name, style in [
            ("＋ مزرعة", self.add_farm, "primary"),
            ("＋ قطاع", self.add_sector, "normal"),
            ("＋ بلوك", self.add_block, "normal"),
            ("تعديل", self.edit_selected, "normal"),
            ("حذف", self.delete_selected, "danger"),
        ]:
            self.actions.addWidget(button(label, style, func_name))

        self.search.textChanged.connect(self.filter_rows)
        self.tree.itemSelectionChanged.connect(self._show_detail)
        self._rows = []
        self._visible_rows = []
        self.refresh()

    def _load_entries(self):
        entries = []
        for farm in self.f.list():
            entries.append(("مزرعة", farm, None, ["مزرعة", farm.id, farm.name, "نشطة"]))
            for sec in self.s.sectors(farm.id):
                entries.append(("قطاع", sec, farm, ["قطاع", sec.id, sec.name, "نشط"]))
                for block in self.s.blocks(sec.id):
                    entries.append(("بلوك", block, sec, ["بلوك", block.code, block.name, "نشط"]))
        return entries

    def refresh(self):
        try:
            self._rows = self._load_entries()
        except Exception:
            logger.exception("تعذر تحميل هيكل المزرعة")
            self._rows = []
        self.filter_rows(self.search.text())

    def filter_rows(self, text):
        query = text.strip().lower()
        self.tree.clear(); self._visible_rows=[]
        for farm in self.f.list():
            farm_match=not query or query in f"مزرعة {farm.name}".lower()
            farm_item=QTreeWidgetItem([farm.name,"", "نشطة"]); farm_item.setData(0,Qt.ItemDataRole.UserRole,("مزرعة",farm,None)); self.tree.addTopLevelItem(farm_item)
            for sec in self.s.sectors(farm.id):
                sec_match=not query or query in f"قطاع {sec.name}".lower()
                sec_item=QTreeWidgetItem([sec.name,"", "نشط"]); sec_item.setData(0,Qt.ItemDataRole.UserRole,("قطاع",sec,farm)); farm_item.addChild(sec_item)
                for block in self.s.blocks(sec.id):
                    block_match=not query or query in f"بلوك {block.code} {block.name}".lower()
                    if not query or farm_match or sec_match or block_match:
                        block_item=QTreeWidgetItem([block.name,block.code,"نشط"]); block_item.setData(0,Qt.ItemDataRole.UserRole,("بلوك",block,sec)); sec_item.addChild(block_item)
                sec_item.setHidden(bool(query) and not (sec_match or any(not sec.child(i).isHidden() for i in range(sec_item.childCount()))))
            farm_item.setExpanded(bool(query) or farm_match); farm_item.setHidden(bool(query) and not (farm_match or any(not farm_item.child(i).isHidden() for i in range(farm_item.childCount()))))
        self.tree.expandAll() if query else None

    def selected_row(self, show_message=True):
        items=self.tree.selectedItems()
        if not items:
            if show_message: QMessageBox.information(self, "اختر سجلًا", "حدد سجلًا من الشجرة أولاً.")
            return None
        return items[0].data(0,Qt.ItemDataRole.UserRole)

    def _show_detail(self):
        entry=self.selected_row(show_message=False)
        if not entry:return
        kind,entity,parent=entry; self.detail_title.setText(f"{kind}: {entity.name}")
        if kind=="مزرعة": body=f"الموقع: {entity.location or '-'}\nالمساحة: {entity.area:g} {entity.area_unit}\nالقطاعات: {len(self.s.sectors(entity.id))}"
        elif kind=="قطاع": body=f"المزرعة: {parent.name}\nالبلوكات: {len(self.s.blocks(entity.id))}"
        else: body=f"القطاع: {parent.name}\nالكود: {entity.code}\nالمساحة: {entity.area:g}\nعدد النخيل: {entity.palm_count}"
        self.detail_body.setText(body)

    def selected_entry(self):
        return self.selected_row()

    def add_farm(self):
        dialog = FormDialog("إضافة مزرعة", [("اسم المزرعة", "text", ""),("الموقع", "text", ""),("المساحة", "number", 0),("وحدة المساحة", "text", "فدان"),("ملاحظات", "text", "")], self)
        if dialog.exec() != dialog.Accepted:
            return
        values=dialog.values(); name = values["اسم المزرعة"]
        if name.strip():
            try:
                self.f.create(name.strip(),values["الموقع"],values["المساحة"],values["وحدة المساحة"],values["ملاحظات"])
                self.refresh()
            except Exception as error:
                QMessageBox.warning(self, "تعذر الحفظ", str(error))

    def add_sector(self):
        entry=self.selected_row()
        if not entry or entry[0]!="مزرعة":
            QMessageBox.information(self, "اختر المزرعة", "حدد مزرعة من الشجرة أولاً لإضافة قطاع.")
            return
        farm = entry[1]
        dialog = FormDialog("إضافة قطاع", [("اسم القطاع", "text", ""),("ملاحظات", "text", "")], self)
        if dialog.exec() != dialog.Accepted:
            return
        values=dialog.values(); name = values["اسم القطاع"]
        if name.strip():
            try:
                self.s.create_sector(farm.id, name.strip(),values["ملاحظات"])
                self.refresh()
            except Exception as error:
                QMessageBox.warning(self, "تعذر الحفظ", str(error))

    def add_block(self):
        entry=self.selected_row()
        if not entry or entry[0]!="قطاع":
            QMessageBox.information(self, "اختر القطاع", "حدد قطاعًا من الشجرة أولاً لإضافة بلوك.")
            return
        sector = entry[1]
        dialog = FormDialog("إضافة بلوك", [("كود البلوك", "text", ""), ("اسم البلوك", "text", ""),("المساحة", "number", 0),("عدد النخيل", "int", 0),("ملاحظات", "text", "")], self)
        if dialog.exec() != dialog.Accepted:
            return
        values = dialog.values()
        if values["كود البلوك"].strip() and values["اسم البلوك"].strip():
            try:
                self.s.create_block(sector.id, values["كود البلوك"].strip(), values["اسم البلوك"].strip(),values["المساحة"],values["عدد النخيل"],values["ملاحظات"])
                self.refresh()
            except Exception as error:
                QMessageBox.warning(self, "تعذر الحفظ", str(error))

    def edit_selected(self):
        entry = self.selected_entry()
        if not entry:
            return
        kind, entity, parent = entry
        try:
            if kind == "مزرعة":
                dialog = FormDialog("تعديل مزرعة", [("اسم المزرعة", "text", entity.name),("الموقع", "text", entity.location or ""),("المساحة", "number", entity.area),("وحدة المساحة", "text", entity.area_unit),("ملاحظات", "text", entity.notes or "")], self)
                if dialog.exec() != dialog.Accepted:
                    return
                values=dialog.values(); name = values["اسم المزرعة"]
                if name.strip():
                    self.f.update_farm(entity.id,name.strip(),values["الموقع"],values["المساحة"],values["وحدة المساحة"],values["ملاحظات"])
                    self.refresh()
            elif kind == "قطاع":
                dialog = FormDialog("تعديل قطاع", [("اسم القطاع", "text", entity.name),("ملاحظات", "text", entity.notes or "")], self)
                if dialog.exec() != dialog.Accepted:
                    return
                values=dialog.values(); name = values["اسم القطاع"]
                if name.strip():
                    self.s.update_sector(entity.id,name.strip(),values["ملاحظات"])
                    self.refresh()
            elif kind == "بلوك":
                dialog = FormDialog("تعديل بلوك", [("كود البلوك", "text", entity.code), ("اسم البلوك", "text", entity.name),("المساحة", "number", entity.area),("عدد النخيل", "int", entity.palm_count),("ملاحظات", "text", entity.notes or "")], self)
                if dialog.exec() != dialog.Accepted:
                    return
                values = dialog.values()
                if values["كود البلوك"].strip() and values["اسم البلوك"].strip():
                    self.s.update_block(entity.id,values["كود البلوك"].strip(),values["اسم البلوك"].strip(),values["المساحة"],values["عدد النخيل"],values["ملاحظات"])
                    self.refresh()
        except Exception as error:
            QMessageBox.warning(self, "تعذر التعديل", str(error))

    def delete_selected(self):
        entry = self.selected_entry()
        if not entry:
            return
        kind, entity, parent = entry
        label = {
            "مزرعة": f"المزرعة {entity.name}",
            "قطاع": f"القطاع {entity.name}",
            "بلوك": f"البلوك {entity.name}",
        }.get(kind, "هذا السجل")
        answer = QMessageBox.question(self, "تأكيد الحذف", f"هل تريد حذف {label}؟")
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            if kind == "مزرعة":
                self.f.delete_farm(entity.id)
            elif kind == "قطاع":
                self.s.delete_sector(entity.id)
            elif kind == "بلوك":
                self.s.delete_block(entity.id)
            self.refresh()
        except Exception as error:
            QMessageBox.warning(self, "تعذر الحذف", str(error))

