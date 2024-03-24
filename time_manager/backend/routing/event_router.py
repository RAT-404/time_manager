from fastapi import APIRouter, Query, Body, Path, Depends, Response

from typing import Annotated
from datetime import datetime


import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from internal.db.schemas import EventSchema as ES, RemainderTimeSchema as RT
from internal.db.database import AsyncSession, get_async_session
from internal.db import models

from internal.buisness_logic.change_record_statement import DBRecord
from internal.buisness_logic.getting_events import Event
from internal.buisness_logic.getting_remainder_time import RemainderTime

from fastapi_cache.decorator import cache

event_router = APIRouter(
    prefix='/event', 
    tags=['event']
)


@event_router.get('/{chat_id}/get-month-events')
@cache(expire=5*60, namespace='event')
async def get_event(chat_id: Annotated[str, Path()],
                    date: Annotated[str | None, Query()] = None,
                    session: AsyncSession = Depends(get_async_session)) -> dict[str, list[ES.Event]]:

    if date:
        try:
            date = str(datetime.strptime(date, '%Y-%m')).replace(' ', 'T')
        except ValueError:
            return Response(content={'error': 'wrong date pattern'}, status_code=400)

    result = await Event(chat_id, models.Event, session, date).get_event_by_month()    
    return result


@event_router.get('/{chat_id}/get-event/{event_id}')
@cache(expire=5*60, namespace='event')
async def get_event_by_id(chat_id: Annotated[str, Path()],
                          event_id: Annotated[int, Path()],
                          session: AsyncSession = Depends(get_async_session)) -> dict[str, list[ES.Event]]:

    result = await Event(chat_id, models.Event, session).get_event_by_id(event_id)    
    return result


@event_router.get('/get-remainder-time/{rmt_id}')
@cache(expire=30, namespace='remainder_time')
async def get_rmt_by_id(rmt_id: Annotated[int, Path()],
                        session: AsyncSession = Depends(get_async_session)) -> dict[str, list[RT.RemainderTime]]:
    result = await RemainderTime(models.RemainderTime, session).get_rmt_by_id(rmt_id)   
    return result

  
@event_router.post('/create-event')
async def create_event(event: Annotated[ES.EventCreate, Body()], session: AsyncSession = Depends(get_async_session)) -> Response:
    await DBRecord(session, models.Event, event).create_record()
    return Response(status_code=200)
    

@event_router.post('/create-remainder-times')
async def create_remainder_time(remainder_time_list: Annotated[list[RT.RemainderTimeCreate], Body()],
                                session: AsyncSession = Depends(get_async_session)) -> Response:
    await DBRecord(session, models.RemainderTime).create_record(remainder_time_list)
    return Response(status_code=200)


@event_router.patch('/update-event/{event_id}')
async def update_event_by_id(event_id: Annotated[int, Path()],
                             new_event_params: Annotated[ES.EventCreate, Body()],
                             session = Depends(get_async_session)) -> Response:
    await DBRecord(session, models.Event, new_event_params).patch_record(event_id)
    return Response(status_code=200)


@event_router.patch('/update-remainder-time/{remainder_time_id}')
async def update_remainder_time_by_id(remainder_time_id: Annotated[int, Path()],
                                      remainder_time_params: Annotated[RT.RemainderTimeCreate, Body()],
                                      session = Depends(get_async_session)) -> Response:
    
    await DBRecord(session, models.RemainderTime, remainder_time_params).patch_record(remainder_time_id)
    return Response(status_code=200)


@event_router.delete('/delete-event/{event_id}')
async def delete_event_by_id(event_id: Annotated[int, Path()], session = Depends(get_async_session)) -> Response:
    await DBRecord(session, models.Event).delete_record(event_id)
    return Response(status_code=200)


@event_router.delete('/delete-remainder-time/{remainder_time_id}')
async def delete_remainder_time_by_id(remainder_time_id: Annotated[int, Path()], session = Depends(get_async_session)) -> Response:
    await DBRecord(session, models.RemainderTime).delete_record(remainder_time_id)
    return Response(status_code=200)


