import os
from typing import List

from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List


class Settings(BaseSettings):
    BOT_TOKEN: str

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int

    ADMIN_IDS_RAW: Optional[str] = ""

    # Пути к JSON файлам для инициализации данных
    TABLES_JSON: str = "app/dao/tables.json"
    SLOTS_JSON: str = "app/dao/slots.json"

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    )

    def get_db_url(self):
        return (f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")

    def get_redis_url(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    def get_admin_ids(self) -> List[int]:
        if not self.ADMIN_IDS_RAW:
            return []
        return [int(x.strip()) for x in self.ADMIN_IDS_RAW.split(",") if x.strip().isdigit()]


settings = Settings()

# Настройка логгера
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log.txt")
logger.add(log_file_path, format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}", level="INFO", rotation="10 MB")