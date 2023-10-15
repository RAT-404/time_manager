from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, mapped_column, as_declarative

from .config import get_settings


sqlalchemy_url = str(get_settings().SQLALCHEMY_URL)

engine = create_engine(url=sqlalchemy_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@as_declarative()
class Base():
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

