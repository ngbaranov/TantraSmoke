import json
from datetime import time
from sqlalchemy.ext.asyncio import AsyncSession
from config import settings
from app.dao.dao import TableDAO, TimeSlotUserDAO
from app.db import async_session_maker
from pydantic import BaseModel, field_validator


class TableBase(BaseModel):
    capacity: int
    description: str


class TimeSlotBase(BaseModel):
    start_time: str
    end_time: str

    @field_validator('start_time', 'end_time')
    @classmethod
    def parse_time(cls, v):
        """Преобразует строку времени в объект time."""
        if isinstance(v, str):
            hour, minute = map(int, v.split(':'))
            return time(hour, minute)
        return v


async def add_tables_to_db(session: AsyncSession):
    with open(settings.TABLES_JSON, 'r', encoding='utf-8') as file:
        tables_data = json.load(file)
    await TableDAO(session).add_many([TableBase(**table) for table in tables_data])


async def add_time_slots_to_db(session: AsyncSession):
    with open(settings.SLOTS_JSON, 'r', encoding='utf-8') as file:
        tables_data = json.load(file)
    await TimeSlotUserDAO(session).add_many([TimeSlotBase(**table) for table in tables_data])


async def init_db():
    async with async_session_maker() as session:
        await add_tables_to_db(session)
        await add_time_slots_to_db(session)
        await session.commit()
