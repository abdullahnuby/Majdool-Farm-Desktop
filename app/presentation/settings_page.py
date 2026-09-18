from pathlib import Path
import shutil
from PySide6.QtWidgets import QFileDialog,QLabel,QMessageBox,QPushButton
from app.config import DATABASE_URL
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
        self.content.addWidget(backup)
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
            shutil.copy2(self.database_path,target)
            QMessageBox.information(self,"تم الحفظ",f"تم إنشاء النسخة الاحتياطية في:\n{target}")
        except OSError as error:
            QMessageBox.warning(self,"تعذر الحفظ",str(error))
