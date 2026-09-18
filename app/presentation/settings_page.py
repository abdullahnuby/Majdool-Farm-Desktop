from pathlib import Path
from PySide6.QtWidgets import QFileDialog,QLabel,QMessageBox,QPushButton
from app.config import DATABASE_URL
from app.database.db import backup_database, restore_database
from app.presentation.ui_theme import PageShell,button


class SettingsPage(PageShell):
    def __init__(self):
        super().__init__("الإعدادات","إعدادات التشغيل المحلي والنسخ الاحتياطي.")
        self.database_path=self._database_path()
        path_label=QLabel(f"مسار قاعدة البيانات المحلية:\n{self.database_path}")
        path_label.setObjectName("PageSubtitle")
        self.content.addWidget(path_label)
        status=QLabel("الحالة: متاحة" if self.database_path.exists() else "الحالة: لم تُنشأ بعد")
        status.setObjectName("PageSubtitle")
        self.content.addWidget(status)
        backup=button("إنشاء نسخة احتياطية","primary",self.backup)
        restore=button("استعادة نسخة احتياطية","normal",self.restore)
        self.content.addWidget(backup)
        self.content.addWidget(restore)
        self.content.addStretch()

    def _database_path(self):
        prefix="sqlite:///"
        value=DATABASE_URL[len(prefix):] if DATABASE_URL.startswith(prefix) else DATABASE_URL
        return Path(value)

    def backup(self):
        if not self.database_path.exists():
            QMessageBox.information(self,"لا توجد قاعدة بيانات","شغّل النظام وأنشئ بيانات قبل أخذ نسخة احتياطية.")
            return
        target,_=QFileDialog.getSaveFileName(self,"حفظ النسخة الاحتياطية","medjool_farm_backup.db","SQLite Database (*.db)")
        if not target:
            return
        try:
            backup_database(target)
            QMessageBox.information(self,"تم الحفظ",f"تم إنشاء النسخة الاحتياطية في:\n{target}")
        except Exception as error:
            QMessageBox.warning(self,"تعذر الحفظ",str(error))

    def restore(self):
        source,_=QFileDialog.getOpenFileName(self,"اختر نسخة احتياطية","", "SQLite Database (*.db)")
        if not source:
            return
        confirm = QMessageBox.question(self,"تأكيد الاستعادة","سيتم استبدال قاعدة البيانات الحالية بنسخة احتياطية محددة. هل تريد المتابعة؟")
        if confirm != QMessageBox.StandardButton.Yes:
            return
        try:
            restore_database(source, self.database_path)
            QMessageBox.information(self,"تمت الاستعادة","تم استعادة قاعدة البيانات بنجاح. أعد تشغيل التطبيق لعرض البيانات الحالية.")
        except Exception as error:
            QMessageBox.warning(self,"تعذر الاستعادة",str(error))
