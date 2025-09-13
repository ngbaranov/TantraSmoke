from aiogram_dialog import Dialog
from app.booking.windows import (get_capacity_window, get_table_window, get_date_window,
                                     get_slots_window, get_confirmed_windows)
"""
Файл определяет последовательность окон (состояний) в диалоге бронирования столика в ресторане.
"""
booking_dialog = Dialog(
    get_capacity_window(),
    get_table_window(),
    get_date_window(),
    get_slots_window(),
    get_confirmed_windows()
)
