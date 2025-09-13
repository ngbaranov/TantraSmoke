from collections import defaultdict

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.kbs import main_admin_kb, admin_back_kb
from config import settings
from app.dao.dao import UserDAO, BookingDAO
from app.utils.text_parts import chunk_text

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
async def admin_bookings_stats(call: CallbackQuery, bot: Bot, session: AsyncSession):
    if str(call.from_user.id) not in settings.ADMIN_IDS_RAW:
        await call.answer("⛔ У вас нет доступа к админ-панели", show_alert=True)
        return

    await call.answer()

    bookings = await BookingDAO(session).get_all_bookings_with_details()

    if not bookings:
        await call.message.edit_text("❌ Нет активных бронирований.", reply_markup=admin_back_kb())
        return

    # Группируем бронирования по дате
    grouped = defaultdict(list)
    for b in bookings:
        grouped[b.date].append(b)

    # Строим текст
    parts = []
    for date, bookings_list in sorted(grouped.items()):
        parts.append(f"📅 <b>{date}</b>")
        for b in bookings_list:
            user = b.user
            table = b.table
            slot = b.time_slot
            start = slot.start_time if isinstance(slot.start_time, str) else slot.start_time.strftime("%H:%M")
            end = slot.end_time if isinstance(slot.end_time, str) else slot.end_time.strftime("%H:%M")
            if b.status == "booked":
                cancel = True
                status_text = "Забронирован"
            elif b.status == "canceled":
                status_text = "Отменен"
            else:
                status_text = "Завершен"
            parts.append(
                f"👤 {user.first_name or ''} {user.last_name or ''} (@{user.username or '—'})\n"
                f"🍽️ Стол #{table.id}, {start}–{end} - <b>{status_text}</b>"
            )
        parts.append("➖" * 10)

    full_text = "\n".join(parts)

    # Разбиваем если текст слишком длинный
    chunks = chunk_text(full_text)

    # Первое сообщение редактируем
    await call.message.edit_text(chunks[0], reply_markup=admin_back_kb())

    # Остальные отправляем
    for chunk in chunks[1:]:
        await bot.send_message(chat_id=call.message.chat.id, text=chunk)