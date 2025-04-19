from aiogram import BaseMiddleware
from typing import Callable, Awaitable, Any
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from loguru import logger


from app.dao.dao import UserDAO
from app.user.schemas import SUser


class DBSessionMiddleware(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker[AsyncSession]):
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any]
    ) -> Any:
        async with self.session_pool() as session:
            data["session_with_commit"] = session
            data["session"] = session  # ✅ это нужно для других middleware
            return await handler(event, data)


class UserEnsureMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any]
    ) -> Any:
        logger.info("✅ MIDDLEWARE: UserEnsureMiddleware активен")

        session: AsyncSession = data.get("session")
        if session is None:
            logger.warning("⚠️ session is None")
            return await handler(event, data)

        # Универсально получаем user
        user = getattr(event, "from_user", None)
        if user is None:
            message = getattr(event, "message", None)
            if message:
                user = getattr(message, "from_user", None)

        if user is None:
            logger.warning("⚠️ Не удалось извлечь from_user из события: {}", event)
            return await handler(event, data)

        logger.info("🔍 Проверка пользователя: {} (@{})", user.id, user.username)
        dao = UserDAO(session)
        exists = await dao.find_one_or_none_by_id(user.id)
        if not exists:
            logger.info("📥 Добавление нового пользователя в БД: {}", user.id)
            await dao.add(SUser(
                id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
            ))
            await session.commit()
            logger.info("✅ Пользователь успешно добавлен: {}", user.id)

        return await handler(event, data)
