from fastapi import APIRouter, Query, Body, Depends, Response
from sqlalchemy import select, insert, update, delete

from typing import Annotated

from backend.internal.db.schemas import EventSchema as ES
from backend.internal.db.database import AsyncSession, get_async_session
from backend.internal.db import models

from backend.internal.buisness_logic import * 


event_router = APIRouter(
    prefix='/event', 
    tags=['event'],
)


@event_router.get('/')
async def get_event(datetime: Annotated[str | None, Query()] = None,
                    name: Annotated[str | None, Query()] = None,
                    session: AsyncSession = Depends(get_async_session),
                    optional: str | None = None) -> dict[str, list[ES.EventBase]]:
 
    event = Event(models.Event, session, datetime)
    
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

  
@event_router.post('/create')
async def create_event(event: Annotated[ES.EventCreate, Body()],
                        remaind_time_list: Annotated[list[ES.RemainderTimeCreate] | None, Body()] = None,
                        session: AsyncSession = Depends(get_async_session)):
    event_id = await create_db_event(session, event)

    if remaind_time_list:
        await create_remainder_time(session, remaind_time_list, event_id)

    return Response(status_code=200)



@event_router.patch('/update-info')
async def create_event(event: Annotated[ES.EventCreate, Body()], 
                 remaind_time: Annotated[ES.RemainderTimeCreate, Body()],
                 session = Depends(get_async_session)):
    pass

@event_router.delete('/delete')
async def delete_event_by_id(event_id: Annotated[int, Query()],
                       session = Depends(get_async_session)):
    pass


