import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram_dialog import setup_dialogs
from redis.asyncio import Redis

from app.booking.dialog import booking_dialog
from config import settings
from user.router import router as user_router
from admin.router import router as admin_router

from middleware import DBSessionMiddleware, UserEnsureMiddleware
from db import get_db
from db import async_session_maker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Запуск Telegram-бота...")

    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    redis = Redis.from_url(settings.get_redis_url())
    storage = RedisStorage(redis=redis, key_builder=DefaultKeyBuilder(with_destiny=True))
    dp = Dispatcher(storage=storage, key_builder= DefaultKeyBuilder(with_destiny=True))
    dp.update.middleware(DBSessionMiddleware(lambda: async_session_maker()))
    dp.update.middleware(UserEnsureMiddleware())

    setup_dialogs(dp)
    dp.include_router(booking_dialog)
    dp.include_router(user_router)
    dp.include_router(admin_router)



    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.exception("Ошибка при запуске бота")
    finally:
        await bot.session.close()
        logger.info("Бот завершён")
        await redis.close()


if __name__ == "__main__":
    asyncio.run(main())