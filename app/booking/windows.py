from datetime import date, timedelta, timezone
from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Group, ScrollingGroup, Select, Calendar, CalendarConfig, Back, Cancel, \
    Row
from aiogram_dialog.widgets.text import Const, Format

from app.booking.getters import get_all_tables, get_all_available_slots, get_confirmed_data
from app.booking.handlers import (process_add_count_capacity, on_table_selected,
                                      process_date_selected, process_slots_selected, on_confirmation, cancel_logic)
from app.booking.state import BookingState
from aiogram_dialog.widgets.media import StaticMedia
from aiogram.types import FSInputFile



def get_capacity_window() -> Window:
    """Окно выбора количества гостей."""
    return Window(
        Const("Выберите кол-во гостей:"),
        Group(
            *[Button(
                text=Const(str(i)),
                id=str(i),
                on_click=process_add_count_capacity
            ) for i in range(1, 7)],
            Cancel(Const("Отмена"), on_click=cancel_logic),
            width=2
        ),
        state=BookingState.count
    )


def get_table_window() -> Window:
    return Window(
        Const("📍 Выберите столик по схеме ниже:"),
        StaticMedia(
            path="static/kafe1.png",  # ✅ проверь, что файл по этому пути реально есть
            type="photo"

        ),
        Group(
            Row(
                *[
                    Button(
                        Const(str(i)),
                        id=f"table_{i}",
                        on_click=on_table_selected
                    ) for i in range(1, 10)  # ⚠️ укажи количество столов по схеме
                ],
            ),
            width=4,  # по 4 кнопки в ряд
        ),
        Group(
            Back(Const("Назад")),
            Cancel(Const("Отмена"), on_click=cancel_logic),
            width=2
        ),
        state=BookingState.table,
    )


def get_date_window() -> Window:
    """Окно выбора даты."""
    return Window(
        Const("На какой день бронируем столик?"),
        Calendar(
            id="cal",
            on_click=process_date_selected,
            config=CalendarConfig(
                firstweekday=0,
                timezone=timezone(timedelta(hours=3)),
                min_date=date.today()
            )
        ),
        Back(Const("Назад")),
        Cancel(Const("Отмена"), on_click=cancel_logic),
        state=BookingState.booking_date,
    )


def get_slots_window() -> Window:
    """Окно выбора слота."""
    return Window(
        Format("{text_slots}"),
        ScrollingGroup(
            Select(
                Format("{item[start_time]} до {item[end_time]}"),
                id="slotes_select",
                item_id_getter=lambda item: str(item["id"]),
                items="slots",
                on_click=process_slots_selected,
            ),
            id="slotes_scrolling",
            width=2,
            height=3,
        ),
        Back(Const("Назад")),
        Cancel(Const("Отмена"), on_click=cancel_logic),
        getter=get_all_available_slots,
        state=BookingState.booking_time,
    )


def get_confirmed_windows():
    return Window(
        Format("{confirmed_text}"),
        Group(
            Button(Const("Все верно"), id="confirm", on_click=on_confirmation),
            Back(Const("Назад")),
            Cancel(Const("Отмена"), on_click=cancel_logic),
        ),
        state=BookingState.confirmation,
        getter=get_confirmed_data
    )