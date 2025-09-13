from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.kbs import admin_back_kb
from app.dao.dao import TableDAO
from app.user.schemas import STableCreate
from config import settings

router = Router()

# Данные столов для инициализации
TABLES_DATA = [
    STableCreate(id=1, capacity=2, description="Столик для двоих у окна"),
    STableCreate(id=2, capacity=4, description="Семейный столик на 4 персоны"),
    STableCreate(id=3, capacity=6, description="Большой стол для компании"),
    STableCreate(id=4, capacity=2, description="Уютный столик в углу"),
    STableCreate(id=5, capacity=8, description="VIP стол для больших компаний"),
    STableCreate(id=6, capacity=4, description="Столик у стены"),
    STableCreate(id=7, capacity=2, description="Романтический столик"),
    STableCreate(id=8, capacity=10, description="Большой банкетный стол"),
    STableCreate(id=9, capacity=3, description="Удобный столик для троих"),
    STableCreate(id=10, capacity=5, description="Столик для небольшой компании"),
]

@router.callback_query(F.data == "admin_init_tables")
async def admin_init_tables(call: CallbackQuery, session: AsyncSession):
    if str(call.from_user.id) not in settings.ADMIN_IDS_RAW:
        await call.answer("⛔ У вас нет доступа к админ-панели", show_alert=True)
        return

    await call.answer()

    table_dao = TableDAO(session)
    existing_tables = await table_dao.count()
    if existing_tables > 0:
        await call.message.edit_text(
            f"⚠️ В базе уже есть {existing_tables} столов.\nПродолжить добавление?",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Да", callback_data="admin_force_init_tables")],
                [InlineKeyboardButton(text="❌ Нет", callback_data="admin_panel")]
            ])
        )
        return

    created_count = 0
    for table_data in TABLES_DATA:
        try:
            await table_dao.add(table_data)
            created_count += 1
        except Exception as e:
            print(f"Ошибка создания стола {table_data.id}: {e}")

    await session.commit()
    await call.message.edit_text(
        f"✅ Создано {created_count} столов из {len(TABLES_DATA)}",
        reply_markup=admin_back_kb()
    )

@router.callback_query(F.data == "admin_force_init_tables")
async def admin_force_init_tables(call: CallbackQuery, session: AsyncSession):
    if str(call.from_user.id) not in settings.ADMIN_IDS_RAW:
        await call.answer("⛔ У вас нет доступа к админ-панели", show_alert=True)
        return

    await call.answer()

    created_count = 0
    table_dao = TableDAO(session)

    for table_data in TABLES_DATA:
        try:
            existing_table = await table_dao.find_one_or_none_by_id(table_data.id)
            if existing_table:
                print(f"Стол с ID {table_data.id} уже существует, пропускаем")
                continue

            await table_dao.add(table_data)
            created_count += 1
        except Exception as e:
            print(f"Ошибка создания стола {table_data.id}: {e}")

    await session.commit()
    await call.message.edit_text(
        f"✅ Создано {created_count} новых столов из {len(TABLES_DATA)}",
        reply_markup=admin_back_kb()
    )
