from pydantic import BaseModel
from datetime import date, time


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