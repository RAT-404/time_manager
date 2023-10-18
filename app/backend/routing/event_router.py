from fastapi import APIRouter, Query, Body, Depends
from sqlalchemy import select

from typing import Annotated

from backend.internal.db.schemas import EventSchema
from backend.internal.db.database import SessionLocal
from backend.internal.db import models

from backend.internal.buisness_logic import * 


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
    
    event = models.Event.__table__
    query_fields = ('event_name', 'date_start', 'time_start', 'date_end', 'time_end')

    query = select(event.c[*query_fields])

    if datetime:
        datetime_config = get_datetime_config(datetime, session, query_fields, event)
        
        match(datetime[-1]):
            case 'H':
                return get_events_by_hour(*datetime_config)
            case 'D':
                return get_events_by_date(*datetime_config)
            case _:
                return get_event_by_current_time(*datetime_config)
        
    elif name:
        return get_events_by_name(query_fields, event, session, name)
    
    return get_events(query, query_fields, session)


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


