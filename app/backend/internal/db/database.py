from sqlalchemy.orm import sessionmaker, Mapped, mapped_column, as_declarative
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.exc import SQLAlchemyError

from fastapi import HTTPException

from .config import get_settings


class SessionManager:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls.__instance, cls):
            cls.__instance = super().__new__(cls)
        return cls.__instance
    
    def __init__(self):
        self.__sqlalchemy_url = str(get_settings().SQLALCHEMY_URL)
        self.engine = create_async_engine(url=self.__sqlalchemy_url)
        self.async_session = sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)

    def get_session(self) -> AsyncSession:
        return self.async_session
    

async def get_async_session():
    async_session = SessionManager().get_session()
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except (SQLAlchemyError, HTTPException) as exc:
            # TODO logging 
            await session.rollback()
            print(exc)
            # raise exc
        finally:
            await session.close()



@as_declarative()
class Base():
    id: Mapped[int] = mapped_column(primary_key=True, index=True)


