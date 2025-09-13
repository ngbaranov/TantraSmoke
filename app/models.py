from datetime import time
from datetime import datetime
from sqlalchemy import BigInteger, String
from app.db import Base
from sqlalchemy import Integer, Date, ForeignKey, Time
from sqlalchemy.orm import relationship, Mapped, mapped_column


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None]
    first_name: Mapped[str | None]
    last_name: Mapped[str | None]
    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="user")


class Table(Base):
    __tablename__ = "tables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    capacity: Mapped[int]
    description: Mapped[str | None]
    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="table")


class TimeSlot(Base):
    __tablename__ = "time_slots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)

    bookings: Mapped[list["Booking"]] = relationship(
        "Booking",
        back_populates="time_slot",
        cascade="all, delete-orphan")

    def __repr__(self):
        return f"TimeSlot(id={self.id}, start_time={self.start_time}, end_time={self.end_time})"


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    table_id: Mapped[int] = mapped_column(Integer, ForeignKey("tables.id"))
    time_slot_id: Mapped[int] = mapped_column(Integer, ForeignKey("time_slots.id"))
    date: Mapped[datetime] = mapped_column(Date)
    status: Mapped[str]
    user: Mapped["User"] = relationship("User", back_populates="bookings")
    table: Mapped["Table"] = relationship("Table", back_populates="bookings")
    time_slot: Mapped["TimeSlot"] = relationship("TimeSlot", back_populates="bookings")
