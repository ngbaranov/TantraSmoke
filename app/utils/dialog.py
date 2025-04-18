from aiogram_dialog import DialogManager
from sqlalchemy.ext.asyncio import AsyncSession


def get_session(manager: DialogManager) -> AsyncSession:
    session = manager.middleware_data.get("session_with_commit")
    if not isinstance(session, AsyncSession):
        raise ValueError("AsyncSession не передана через middleware или имеет неверный тип")
    return session