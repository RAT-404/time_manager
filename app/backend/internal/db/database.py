from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, mapped_column

from config import get_settings


sqlalchemy_url = str(get_settings().SQLALCHEMY_URL)

engine = create_engine(url=sqlalchemy_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

