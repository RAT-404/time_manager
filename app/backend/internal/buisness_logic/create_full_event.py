from sqlalchemy import insert

from backend.internal.db.schemas import EventSchema as ES
from backend.internal.db import models
from backend.internal.db.database import AsyncSession


async def create_db_event(session: AsyncSession, event: ES.EventCreate) -> int:
    db_event = models.Event
    query = insert(db_event).values(**event.model_dump()).returning(db_event.id)
    event_query = await session.execute(query)

    event_id = list(event_query)[0][0]
    return event_id


async def create_remainder_time(session: AsyncSession, remaind_time_list: list[ES.RemainderTimeCreate], event_id: int):
    db_reminad_time = models.RemainderTime

    json_remaind_time_list = [remaind_time.model_dump() for remaind_time in remaind_time_list]
    for time in json_remaind_time_list:
        time.update({'event_id': event_id})
    
    query = insert(db_reminad_time).values(json_remaind_time_list)
    await session.execute(query)