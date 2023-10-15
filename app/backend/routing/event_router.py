from fastapi import APIRouter, Query, Body, Depends
from sqlalchemy import select

from typing import Annotated
import pytz
from datetime import datetime as dt, date as d, time as t, timedelta as tl

from backend.internal.db.schemas import EventSchema
from backend.internal.db.database import SessionLocal
from backend.internal.db import models


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


event_router = APIRouter(
    prefix='/event', 
    tags=['event'],
)


@event_router.get('/')
def get_event(datetime: Annotated[str | None, Query()] = None,
              name: Annotated[str | None, Query()] = None,
              session = Depends(get_session)):
    
    event = models.Event
    query_fields = ('event_name', 'date_start', 'time_start', 'date_end', 'time_end')
    
    if datetime:
        date_format = '%d-%m-%Y'
        time_format = '%H:%M:%S%z'
        datetime_format = f'{date_format}T{time_format}'

        if datetime[-1] == 'H': # если на конце H то надо крч искать все события в этом часу
            
            datetime = datetime[:-1]
            
            datetime = dt.strptime(datetime.replace(' ', '+'), datetime_format)
            
            date = datetime.date()
            time = datetime.time()

            
            time_with_upper_error = t(time.hour + 1, time.minute, time.second, tzinfo=pytz.timezone('Europe/Moscow'))
            time_with_down_error = t(time.hour, time.minute, time.second, tzinfo=pytz.timezone('Europe/Moscow'))
            
            query_fields_ = (event.event_name, event.date_start, event.time_start, event.date_end, event.time_end)
            query = select(*query_fields_
                       ).where(event.date_start == date
                                ).where(time_with_down_error <= event.time_start
                                ).where(event.time_start <= time_with_upper_error)

            events = [EventSchema.EventCreate(**dict(zip(query_fields, row))) for row in session.execute(query)]

            return {'events': events}

        
        datetime = dt.strptime(datetime.replace(' ', '+'), datetime_format)
        
        date = datetime.date()
        time = datetime.time()

        
        time_with_upper_error = t(time.hour, time.minute + 1, time.second, tzinfo=pytz.timezone('Europe/Moscow'))
        time_with_down_error = t(time.hour, time.minute - 1, time.second, tzinfo=pytz.timezone('Europe/Moscow'))

        query_fields_ = (event.event_name, event.date_start, event.time_start, event.date_end, event.time_end)
        query = select(*query_fields_
                       ).where(event.date_start == date
                                ).where(time_with_down_error <= event.time_start
                                ).where(event.time_start <= time_with_upper_error)
        
        events = [EventSchema.EventCreate(**dict(zip(query_fields, row))) for row in session.execute(query)]

        return {'events': events}
        
    elif name:
        print(name)
        query_fields_ = (event.event_name, event.date_start, event.time_start, event.date_end, event.time_end)
        query = select(*query_fields_).where(event.event_name == name)

        events = [EventSchema.EventCreate(**dict(zip(query_fields, row))) for row in session.execute(query)]

        return {'events': events}
    
    query = select(event.event_name, event.date_start, event.date_end)
    
    events = [EventSchema.EventCreate(**dict(zip(query_fields, row))) for row in session.execute(query)]
    return {'events' : events}


@event_router.post('/create')
def create_event(event: Annotated[EventSchema.EventCreate, Body()], 
                 remaind_time: Annotated[EventSchema.RemainderTimeCreate, Body()],
                 session = Depends(get_session)):
    pass

@event_router.patch('/update-info')
def create_event(event: Annotated[EventSchema.EventCreate, Body()], 
                 remaind_time: Annotated[EventSchema.RemainderTimeCreate, Body()],
                 session = Depends(get_session)):
    pass

@event_router.delete('/delete')
def delete_event_by_id(event_id: Annotated[int, Query()],
                       session = Depends(get_session)):
    pass


