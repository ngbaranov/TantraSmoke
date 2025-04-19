from aiogram_dialog import DialogManager


async def get_all_tables(dialog_manager: DialogManager, **kwargs):
    """Получение списка столов с учетом выбранной вместимости."""
    tables = dialog_manager.dialog_data['tables']
    capacity = dialog_manager.dialog_data['capacity']
    return {
        "tables": tables,
        "text_table": (
            f'Всего для {capacity} человек найдено {len(tables)} столов. '
            'Выберите нужный по описанию'
        )
    }


async def get_all_available_slots(dialog_manager: DialogManager, **kwargs):
    """Получение списка доступных временных слотов для выбранного стола и даты."""
    selected_table = dialog_manager.dialog_data['selected_table']
    slots = dialog_manager.dialog_data['slots']
    table_id = selected_table['id']
    text_slots = (
        f'Для стола №{table_id} найдено {len(slots)} '
        f'{"свободных слотов" if len(slots) != 1 else "свободный слот"}. '
        'Выберите удобное время'
    )
    return {
        "slots": slots,
        "text_slots": text_slots
    }


async def get_confirmed_data(dialog_manager: DialogManager, **kwargs):
    """Формирование текста подтверждения бронирования."""
    selected_table = dialog_manager.dialog_data['selected_table']
    booking_date = dialog_manager.dialog_data['booking_date']
    selected_slot = dialog_manager.dialog_data.get("selected_slot")
    if not selected_slot:
        return {"confirmed_text": "❌ Ошибка: слот не выбран. Пожалуйста, вернитесь и выберите слот."}

    confirmed_text = (
        "<b>📅 Подтверждение бронирования</b>\n\n"
        f"<b>📆 Дата:</b> {booking_date}\n\n"
        f"<b>🍴 Информация о столике:</b>\n"
        f"  - 📝 Описание: {selected_table['description']}\n"
        f"  - 👥 Кол-во мест: {selected_table['capacity']}\n"
        f"  - 📍 Номер столика: {selected_table['id']}\n\n"
        f"<b>⏰ Время бронирования:</b>\n"
        f"  - С <i>{selected_slot['start_time']}</i> до <i>{selected_slot['end_time']}</i>\n\n"
        "✅ Все ли верно?"
    )
    return {"confirmed_text": confirmed_text}
