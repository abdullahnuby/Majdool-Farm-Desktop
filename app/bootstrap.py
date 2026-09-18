from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from app.database.db import init_db
from app.logging_config import setup_logging
from app.presentation.main_window import MainWindow

def run():
    setup_logging()
    init_db()
    app=QApplication([])
    app.setApplicationName("مدير مزرعة المجدول")
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    w=MainWindow()
    w.show()
    app.exec()
