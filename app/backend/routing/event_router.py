from fastapi import APIRouter, Query, Body, Path, Depends, Response

from typing import Annotated

from internal.db.schemas import EventSchema as ES
from internal.db.database import AsyncSession, get_async_session
from internal.db import models

from internal.buisness_logic.change_record_statement import DBRecord
from internal.buisness_logic.getting_events import Event

from datetime import datetime


event_router = APIRouter(
    prefix='/event', 
    tags=['event']
)


@event_router.get('/{chat_id}')
async def get_event(chat_id: Annotated[str, Path()],
                    datetime: Annotated[str | None, Query()] = None,
                    name: Annotated[str | None, Query()] = None,
                    session: AsyncSession = Depends(get_async_session),
                    optional: str | None = None) -> dict[str, list[ES.Event]]:

    event = Event(chat_id, models.Event, session, datetime)
    
    if datetime:
        match(optional):
            case 'H':
                result = await event.get_events_by_hour()
            case 'D':
                result = await event.get_events_by_date()
            case _:
                result = await event.get_event_by_current_time()
        
        return result

    elif name:
        result = await event.get_events_by_name(name)
        return result
    
    result = await event.get_events_by_query()
    
    return result


@event_router.get('/{chat_id}/get-month-events')
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
async def get_event_by_id(chat_id: Annotated[str, Path()],
                          event_id: Annotated[int, Path()],
                          session: AsyncSession = Depends(get_async_session)) -> dict[str, list[ES.Event]]:

    result = await Event(chat_id, models.Event, session).get_event_by_id(event_id)    
    return result

  
@event_router.post('/create-event')
async def create_event(event: Annotated[ES.EventCreate, Body()], session: AsyncSession = Depends(get_async_session)) -> Response:
    await DBRecord(session, models.Event, event).create_record()
    return Response(status_code=200)
    

@event_router.post('/create-remainder-times')
async def create_remainder_time(remainder_time_list: Annotated[list[ES.RemainderTimeCreate], Body()],
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
                                      remainder_time_params: Annotated[ES.RemainderTimeCreate, Body()],
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


