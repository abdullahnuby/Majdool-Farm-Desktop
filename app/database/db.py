import sqlite3
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def _database_file_path(database_url: str = DATABASE_URL) -> Path:
    prefix = "sqlite:///"
    if database_url.startswith(prefix):
        return Path(database_url[len(prefix):])
    return Path(database_url)


def backup_database(destination: str | Path) -> Path:
    """ينشئ نسخة احتياطية من قاعدة البيانات الحالية بشكل آمن عبر SQLite backup API."""
    source_path = _database_file_path()
    dest_path = Path(destination)
    if not source_path.exists():
        raise FileNotFoundError(f"قاعدة البيانات غير موجودة: {source_path}")
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    if dest_path.exists():
        dest_path.unlink()
    with sqlite3.connect(str(source_path)) as source_conn, sqlite3.connect(str(dest_path)) as dest_conn:
        source_conn.backup(dest_conn)
    return dest_path


def restore_database(source: str | Path, destination: str | Path | None = None) -> Path:
    """يستعيد قاعدة بيانات من نسخة احتياطية في ملف جديد أو ملف الهدف المحدد."""
    source_path = Path(source)
    if not source_path.exists():
        raise FileNotFoundError(f"ملف النسخة الاحتياطية غير موجود: {source_path}")
    target_path = Path(destination) if destination is not None else _database_file_path()
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if target_path.exists() and target_path.resolve() != source_path.resolve():
        target_path.unlink()
    with sqlite3.connect(str(source_path)) as source_conn, sqlite3.connect(str(target_path)) as target_conn:
        source_conn.backup(target_conn)
    return target_path


class Base(DeclarativeBase):
    pass


@event.listens_for(engine, "connect")
def _sqlite_on_connect(dbapi_connection, _record):
    # نمسك التحكم في المعاملات بدل السلوك الافتراضي لـ pysqlite (اللي بيبدأ المعاملة متأخر).
    dbapi_connection.isolation_level = None
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")   # SQLite بيتجاهل المفاتيح الأجنبية لو مش مفعّلة
    cursor.execute("PRAGMA busy_timeout=5000")  # استنى 5 ثواني بدل الفشل الفوري لو القاعدة مشغولة
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()


@event.listens_for(engine, "begin")
def _sqlite_on_begin(connection):
    # BEGIN IMMEDIATE: أي "افحص ثم اكتب" (رصيد، تكرار...) بيتنفذ كوحدة واحدة ومحدّش يدخل بينهم.
    connection.exec_driver_sql("BEGIN IMMEDIATE")


def init_db():
    from app.domain import models  # noqa: F401  (يسجّل كل الجداول)
    Base.metadata.create_all(engine)
