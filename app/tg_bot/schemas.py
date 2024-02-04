from datetime import date, time

from aiogram.filters.callback_data import CallbackData

from pydantic import BaseModel


class EventCallback(CallbackData, prefix='event'):
    id: str
    act: str
    date_start: str


class Event(BaseModel):
    chat_id: str
    event_name: str
    date_start: str
    time_start: str
    date_end: str | None = None
    time_end: str | None = None


class RemainderTime(BaseModel):
    event_id: int
    date_to_remaind: str
    time_to_remaind: str