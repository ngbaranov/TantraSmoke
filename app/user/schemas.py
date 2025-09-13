from pydantic import BaseModel


class SUser(BaseModel):
    id: int
    username: str | None
    first_name: str | None
    last_name: str | None


class STableCreate(BaseModel):
    id: int | None = None
    capacity: int
    description: str | None = None
