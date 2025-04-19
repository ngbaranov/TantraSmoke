from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.kbs import main_admin_kb, admin_back_kb
from config import settings
from app.dao.dao import UserDAO, BookingDAO

router = Router()


@router.callback_query(F.data == "admin_panel")
async def admin_start(call: CallbackQuery):
    if str(call.from_user.id) not in settings.ADMIN_IDS_RAW:
        await call.answer("⛔ У вас нет доступа к админ-панели", show_alert=True)
        return

    await call.answer("Доступ в админ-панель разрешен!")
    await call.message.answer("Выберите действие:", reply_markup=main_admin_kb())


@router.callback_query(F.data == "admin_users_stats")
async def admin_users_stats(call: CallbackQuery, session: AsyncSession):
    if str(call.from_user.id) not in settings.ADMIN_IDS_RAW:
        await call.answer("⛔ У вас нет доступа к админ-панели", show_alert=True)
        return
    await call.answer("Статистика пользователей")
    users_stats = await UserDAO(session).count()
    await call.message.edit_text(f'Всего в базе данных {users_stats} пользователей.', reply_markup=admin_back_kb())


@router.callback_query(F.data == "admin_bookings_stats")
async def admin_bookings_stats(call: CallbackQuery, session: AsyncSession):
    """
    Обработчик callback-запроса для отображения статистики бронирований администраторам.
    """
    if str(call.from_user.id) not in settings.ADMIN_IDS_RAW:
        await call.answer("⛔ У вас нет доступа к админ-панели", show_alert=True)
        return
    await call.answer("Загружаю статистику...")
    bookings_stats = await BookingDAO(session).book_count()
    booked_count = bookings_stats.get("booked", 0)
    completed_count = bookings_stats.get("completed", 0)
    canceled_count = bookings_stats.get("canceled", 0)
    total_count = bookings_stats.get("total", 0)
    message = (
        "<b>📊 Статистика бронирований:</b>\n\n"
        f"<i>Всего бронирований:</i> <b>{total_count}</b>\n"
        f"✅ <i>Забронировано:</i> <b>{booked_count}</b>\n"
        f"☑️ <i>Завершено:</i> <b>{completed_count}</b>\n"
        f"🚫 <i>Отменено:</i> <b>{canceled_count}</b>"
    )
    await call.message.edit_text(message, reply_markup=admin_back_kb())