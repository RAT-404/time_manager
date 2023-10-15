from pydantic import BaseModel
from datetime import datetime, date, time


class RemainderTimeBase(BaseModel):
    time_to_remaind: str


class RemainderTimeCreate(RemainderTimeBase):
    pass


class RemainderTime(RemainderTimeBase):
    id: int

    event_id: int
    current_event: "Event"

    class Config:
        from_attributes = True



class EventBase(BaseModel):
    event_name: str
    date_start: date
    time_start: time
    date_end: date | None
    time_end: time | None


class EventCreate(EventBase):
    pass


class Event(EventBase):
    id: int

    created_at: str
    updated_at: str

    remainder_times: list[RemainderTime] = []

    class Config:
        from_attributes = True