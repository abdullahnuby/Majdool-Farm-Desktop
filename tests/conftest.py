"""قاعدة بيانات مؤقتة لكل اختبار — الاختبارات مابتلمسش قاعدة المستخدم الحقيقية أبداً."""
import os
import shutil
import tempfile

_TMP = tempfile.mkdtemp(prefix="medjool_test_")
os.environ["MEDJOOL_APP_DIR"] = _TMP  # لازم قبل أي import للتطبيق

import pytest  # noqa: E402
from app.database.db import Base, engine  # noqa: E402
from app.domain import models  # noqa: E402,F401


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield


def pytest_sessionfinish(session, exitstatus):
    engine.dispose()
    shutil.rmtree(_TMP, ignore_errors=True)
