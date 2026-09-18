"""فتح كل الشاشات في وضع offscreen. أي خطأ بيتسجّل عبر logger.exception يفشّل الاختبار."""
import os
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    return app


def test_all_pages_open_and_refresh_without_swallowed_errors(qapp, monkeypatch):
    from app import logging_config
    errors = []
    monkeypatch.setattr(logging_config.logger, "exception", lambda *a, **k: errors.append(a))
    from app.presentation.main_window import MainWindow
    window = MainWindow()
    window.show()
    for index in range(window.menu.count()):
        window._navigate(index)
    assert window.menu.count() >= 13
    assert errors == [], f"شاشات رمت أخطاء اتبلعت: {errors}"


def test_sales_and_purchase_pages_require_explicit_selection(qapp):
    from app.presentation.sales_page import SalesPage
    from app.presentation.purchases_page import PurchasesPage

    sales_page = SalesPage()
    purchases_page = PurchasesPage()

    with pytest.raises(ValueError, match="اختيار العميل"):
        sales_page._resolve_invoice_customer()

    with pytest.raises(ValueError, match="اختيار المورد"):
        purchases_page._resolve_invoice_supplier()
