from sqlalchemy import select
from fuzzywuzzy import fuzz

import pytz
from datetime import datetime as dt, date, time

from backend.internal.db.schemas import EventSchema
from backend.internal.db.database import SessionLocal
from backend.internal.db import models


def get_datetime_config(datetime, session, query_fields, event) -> tuple:
    date_format = '%d-%m-%Y'
    time_format = '%H:%M:%S%z'
    datetime_format = f'{date_format}T{time_format}'
    datetime_config = (datetime, session, query_fields, datetime_format, event)
    return datetime_config


def __get_date_and_time(str_datetime: str, datetime_format) -> tuple[date, time]:
    datetime = dt.strptime(str_datetime.replace(' ', '+'), datetime_format)
    
    return (datetime.date(), datetime.time())


def __get_time_with_error(current_time: time):
    def wrap(hour: int = current_time.hour, minute: int = current_time.minute, second: int = current_time.second, tzinfo: pytz.timezone=pytz.timezone('Europe/Moscow')) -> time:
        return time(hour=hour, minute=minute, second=second, tzinfo=tzinfo)
    return wrap


def get_events(query, query_fields, session: SessionLocal) -> dict[str, list[EventSchema.EventCreate]]:
    events = [EventSchema.EventCreate(**dict(zip(query_fields, row))) for row in session.execute(query)]
    return {'events': events}


def __get_events(datetime: str, 
    session: SessionLocal, 
    query_fields: tuple[str], 
    datetime_format: str, 
    event: models.Event.__table__,
    time_with_upper_error,
    time_with_down_error
    ):

    date_, _ = __get_date_and_time(datetime, datetime_format)
    

    query = select(event.c[*query_fields]
                ).where(event.c.date_start == date_
                        ).where(time_with_down_error <= event.c.time_start
                        ).where(event.c.time_start <= time_with_upper_error)

    return get_events(query, query_fields, session)


def get_events_by_hour(datetime: str, 
                       session: SessionLocal, 
                       query_fields: tuple[str], 
                       datetime_format: str, 
                       event: models.Event.__table__
                    ):
    datetime = datetime[:-1]
            
    _, time_ = __get_date_and_time(datetime, datetime_format)

    one_hour = 59
    minutes_error = time_.minute + (one_hour - time_.minute)
    
    get_time = __get_time_with_error(time_)
    

    return __get_events(datetime, session, query_fields, datetime_format, event, get_time(minute=minutes_error), get_time())


def get_events_by_date(datetime: str, 
                       session: SessionLocal, 
                       query_fields: tuple[str], 
                       datetime_format: str, 
                       event: models.Event.__table__):
    datetime = datetime[:-1]

    date_, _ = __get_date_and_time(datetime, datetime_format)

    query = select(event.c[*query_fields]).where(event.c.date_start == date_)

    return get_events(query, query_fields, session)


def get_event_by_current_time(datetime: str, 
                              session: SessionLocal, 
                              query_fields: tuple[str], 
                              datetime_format: str, 
                              event: models.Event.__table__
                              ) -> dict[str, list[EventSchema.EventCreate]]:
    
    _, time_ = __get_date_and_time(datetime, datetime_format)

    get_time = __get_time_with_error(time_)
    
    minutes_error = 1 # 1 minute

    return __get_events(datetime, session, query_fields, datetime_format, event, get_time(minute=time_.minute + minutes_error), get_time(minute=time_.minute - minutes_error))


def get_events_by_name(query_fields, event, session, name, verbal_error=80):
    query = select(*query_fields).where(fuzz.ratio(event.event_name, name) >= verbal_error)

    return get_events(query, query_fields, session)