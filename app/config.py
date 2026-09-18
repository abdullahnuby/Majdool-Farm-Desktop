from pathlib import Path
import os


def _resolve_app_dir() -> Path:
    """مجلد بيانات التطبيق. يمكن تغييره بمتغير البيئة MEDJOOL_APP_DIR (يستخدمه الاختبار)."""
    override = os.getenv("MEDJOOL_APP_DIR")
    if override:
        return Path(override)
    return Path(os.getenv("LOCALAPPDATA", Path.home())) / "MedjoolFarmManager"


APP_DIR = _resolve_app_dir()
APP_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_URL = f"sqlite:///{APP_DIR/'medjool_farm.db'}"
