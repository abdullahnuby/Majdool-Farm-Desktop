import logging
import sys
from logging.handlers import RotatingFileHandler
from app.config import APP_DIR

logger = logging.getLogger("medjool")


def setup_logging() -> None:
    """ملف لوج دوّار في مجلد بيانات التطبيق + التقاط أي استثناء غير متوقع."""
    if logger.handlers:
        return
    log_dir = APP_DIR / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(log_dir / "app.log", maxBytes=1_000_000, backupCount=5, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    def _excepthook(exc_type, exc, tb):
        logger.error("Unhandled exception", exc_info=(exc_type, exc, tb))
        try:
            from PySide6.QtWidgets import QMessageBox, QApplication
            if QApplication.instance():
                QMessageBox.critical(None, "خطأ غير متوقع",
                    f"حصل خطأ غير متوقع وتم تسجيله في:\n{log_dir / 'app.log'}\n\n{exc}")
        except Exception:
            pass
        sys.__excepthook__(exc_type, exc, tb)

    sys.excepthook = _excepthook
