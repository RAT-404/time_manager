from pydantic import BaseModel
from datetime import datetime, date, time


class RemainderTimeBase(BaseModel):
    event_id: int
    date_to_remaind: date
    time_to_remaind: time
    
    class Config:
        from_attributes = True


class RemainderTimeCreate(RemainderTimeBase):
    pass


class RemainderTime(RemainderTimeBase):
    id: int


class EventBase(BaseModel):
    chat_id: str
    event_name: str
    date_start: date
    time_start: time
    date_end: date | None = None
    time_end: time | None = None

    class Config:
        from_attributes = True


class EventCreate(EventBase):
    pass


class Event(EventBase):
    id: int

    created_at: datetime = None
    updated_at: datetime = None

    remainder_times: list[RemainderTime] = []
