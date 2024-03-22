from enum import Enum

from pydantic import BaseModel
from aiogram.filters.callback_data import CallbackData

from aiogram_calendar.schemas import CalendarCallback



class SimpleCalAct(str, Enum):
    ignore = 'IGNORE'
    prev_y = 'P-Y'
    next_y = 'N-Y'
    prev_m = 'P-M'
    next_m = 'N-M'
    cancel = 'CANCEL'
    today = 'TODAY'
    day = 'DAY'

    select_new_event_date = 'SNED'
    
    select_rm_date = 'SRD'
    select_new_rm_date = 'SNRD'


class SimpleCalendarCallback(CalendarCallback, prefix="simple_calendar"):
    act: SimpleCalAct
    event_id: str | None = None
    day_selection_act: str | None = None


class EventAct(str, Enum):
    change_event = 'CE'
    change_event_name = 'CEN'
    change_event_date = 'CED'
    change_event_time = 'CET'
    delete = 'DELETE'
    
    append = 'APPEND'
    cancel = 'CANCEL'


class EventCallback(CallbackData, prefix='event'):
    act: str
    id: str | None = None
    event_name: str | None = None
    date_start: str | None = None
    time_start: str | None = None


class RemainderAct(str, Enum):
    select_rm = 'SR'
    change_rm = 'CR'
    change_rm_date = 'CRD'
    change_rm_time = 'CRT'
    delete = 'DELETE'
    
    append = 'APPEND'
    cancel = 'CANCEL'


class RemainderCallback(CallbackData, prefix='remainder'):
    act: str
    id: str | None = None
    event_id: str | None = None
    date_start: str | None = None
    time_start: str | None = None


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