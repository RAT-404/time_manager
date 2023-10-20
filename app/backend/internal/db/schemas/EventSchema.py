from pydantic import BaseModel
from datetime import datetime, date, time


class RemainderTimeBase(BaseModel):
    date_to_remaind: str
    time_to_remaind: str
    event_id: int | None = None


class RemainderTimeCreate(RemainderTimeBase):
    pass


class RemainderTime(RemainderTimeBase):
    id: int

    class Config:
        from_attributes = True



class EventBase(BaseModel):
    event_name: str
    date_start: str
    time_start: str
    date_end: str | None = None
    time_end: str | None = None


class EventCreate(EventBase):
    pass


class Event(EventBase):
    id: int

    created_at: str
    updated_at: str

    remainder_times: list[RemainderTime] = []

    class Config:
        from_attributes = True