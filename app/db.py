from typing import AsyncGenerator, Any

from sqlalchemy import Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from config import settings

from contextlib import asynccontextmanager


DATABASE_URL = settings.get_db_url()

# Создаем асинхронный движок для работы с базой данных
engine = create_async_engine(url=DATABASE_URL, echo=True)
# Создаем фабрику сессий для взаимодействия с базой данных
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def get_db() -> AsyncGenerator[Any, Any]:
    async with async_session_maker() as session:
        yield session


# Базовый класс для всех моделей
class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True
