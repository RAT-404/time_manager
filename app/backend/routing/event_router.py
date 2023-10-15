from fastapi import APIRouter, Query, Body, Depends
from sqlalchemy import select

from typing import Annotated
import pytz

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
def get_event(date: Annotated[str | None, Query()] = None,
              name: Annotated[str | None, Query()] = None,
              session = Depends(get_session)):
    
    event = models.Event.__table__
    
    if date:
        return 
    if name:
        return
    
    query_fields = ('event_name', 'date_start', 'date_end')
    query = select(event.c[*query_fields])
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


