from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase,sessionmaker
from app.config import DATABASE_URL
engine=create_engine(DATABASE_URL,future=True)
SessionLocal=sessionmaker(bind=engine,autoflush=False,expire_on_commit=False)
class Base(DeclarativeBase): pass
def init_db():
 from app.domain import models
 Base.metadata.create_all(engine)
