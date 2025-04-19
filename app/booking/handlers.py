from datetime import date
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from loguru import logger

from app.booking.schemas import SCapacity, SNevBooking
from app.user.kbs import main_user_kb
# from app.config import broker
from app.dao.dao import BookingDAO, TimeSlotUserDAO, TableDAO
from app.utils.dialog import get_session


async def cancel_logic(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await callback.answer("Сценарий бронирования отменен!")
    await callback.message.answer(
        "Вы отменили сценарий бронирования.",
        reply_markup=main_user_kb(callback.from_user.id)
    )


async def process_add_count_capacity(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    """Обработчик выбора количества гостей."""
    session = get_session(dialog_manager)
    selected_capacity = int(button.widget_id)
    dialog_manager.dialog_data["capacity"] = selected_capacity
    # Загружаем только необходимые поля вместо ORM-объектов
    tables = await TableDAO(session).find_all(SCapacity(capacity=selected_capacity))
    dialog_manager.dialog_data['tables'] = [
        {"id": t.id, "capacity": t.capacity, "description": t.description}
        for t in tables
    ]
    await callback.answer(f"Выбрано {selected_capacity} гостей")
    await dialog_manager.next()


async def on_table_selected(callback: CallbackQuery, widget, dialog_manager: DialogManager, item_id: str):
    """Обработчик выбора стола."""
    session = get_session(dialog_manager)
    table_id = int(item_id)
    # Получаем и сериализуем только простые данные
    table = await TableDAO(session).find_one_or_none_by_id(table_id)
    dialog_manager.dialog_data["selected_table"] = {
        "id": table.id,
        "capacity": table.capacity,
        "description": table.description,
    }
    await callback.answer(f"Выбран стол №{table_id} на {table.capacity} мест")
    await dialog_manager.next()


async def process_date_selected(callback: CallbackQuery, widget, dialog_manager: DialogManager, selected_date: date):
    """Обработчик выбора даты."""
    session = get_session(dialog_manager)

    dialog_manager.dialog_data["booking_date"] = selected_date.isoformat()

    table_data = dialog_manager.dialog_data["selected_table"]
    slots = await BookingDAO(session).get_available_time_slots(
        table_id=table_data["id"],
        booking_date=selected_date
    )

    if slots:
        await callback.answer(f"Выбрана дата: {selected_date}")
        dialog_manager.dialog_data["slots"] = [
            {"id": s.id, "start_time": s.start_time, "end_time": s.end_time}
            for s in slots
        ]
        await dialog_manager.next()  # ✅ теперь всё уже готово
    else:
        await callback.answer(
            f"Нет мест на {selected_date} для стола №{table_data['id']}!"
        )
        await dialog_manager.back()



async def process_slots_selected(callback: CallbackQuery, widget, dialog_manager: DialogManager, item_id: str):
    """Обработчик выбора слота."""
    session = get_session(dialog_manager)
    slot_id = int(item_id)
    slot = await TimeSlotUserDAO(session).find_one_or_none_by_id(slot_id)
    dialog_manager.dialog_data['selected_slot'] = {
        "id": slot.id,
        "start_time": slot.start_time,
        "end_time": slot.end_time,
    }
    await callback.answer(
        f"Выбрано время с {slot.start_time} до {slot.end_time}"
    )
    await dialog_manager.next()


async def on_confirmation(callback: CallbackQuery, widget, dialog_manager: DialogManager, **kwargs):
    logger.info("📦 on_confirmation() вызван")
    """Обработчик подтверждения бронирования."""
    session = get_session(dialog_manager)

    # Получаем выбранные данные из сериализованных словарей
    table_data = dialog_manager.dialog_data['selected_table']
    slot_data = dialog_manager.dialog_data['selected_slot']
    booking_date = date.fromisoformat(dialog_manager.dialog_data['booking_date'])
    user_id = callback.from_user.id

    check = await BookingDAO(session).check_available_bookings(
        table_id=table_data['id'],
        time_slot_id=slot_data['id'],
        booking_date=booking_date
    )
    if check:
        await callback.answer("Приступаю к сохранению")
        add_model = SNevBooking(
            user_id=user_id,
            table_id=table_data['id'],
            time_slot_id=slot_data['id'],
            date=booking_date,
            status="booked"
        )
        await BookingDAO(session).add(add_model)
        await session.commit()
        await callback.answer("Бронирование успешно создано!")
        text = (
            "Бронь успешно сохранена🔢🍴 "
            "Со списком своих броней можно ознакомиться в меню 'МОИ БРОНИ'"
        )
        await callback.message.answer(text, reply_markup=main_user_kb(user_id))

        admin_text = (
            f"Внимание! Пользователь с ID {user_id} забронировал столик №{table_data['id']} "
            f"на {booking_date}. Время брони с {slot_data['start_time']} до {slot_data['end_time']}"
        )
        # await broker.publish(admin_text, "admin_msg")
        # await broker.publish(callback.from_user.id, "noti_user")
        await dialog_manager.done()
    else:
        await callback.answer("Места на этот слот уже заняты!")
        await dialog_manager.back()
