from enum import Enum
from aiogram.filters.callback_data import CallbackData
from aiogram_calendar.schemas import CalendarCallback

from pydantic import BaseModel


class SimpleCalAct(str, Enum):
    ignore = 'IGNORE'
    prev_y = 'PREV-YEAR'
    next_y = 'NEXT-YEAR'
    prev_m = 'PREV-MONTH'
    next_m = 'NEXT-MONTH'
    cancel = 'CANCEL'
    today = 'TODAY'
    day = 'DAY'

    select_new_event_date = 'SELECT_NEW_EVENT_DATE'


class SimpleCalendarCallback(CalendarCallback, prefix="simple_calendar"):
    act: SimpleCalAct


class EventAct(str, Enum):
    change_event = 'CHANGE_EVENT'
    change_event_name = 'CHANGE_EVENT_NAME'
    change_event_date = 'CHANGE_EVENT_DATE'
    change_event_time = 'CHANGE_EVENT_TIME'
    delete = 'DELETE'
    
    append = 'APPEND'
    cancel = 'CANCEL'


class EventCallback(CallbackData, prefix='event'):
    act: str
    id: str | None = None
    event_name: str | None = None
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