from sqlalchemy import insert

from backend.internal.db.schemas import EventSchema as ES
from backend.internal.db import models
from backend.internal.db.database import SessionLocal


def create_db_event(session: SessionLocal, event: ES.EventCreate) -> int:
    db_event = models.Event
    event_query = session.execute(insert(db_event
                                      ).values(**event.model_dump()
                                               ).returning(db_event.id)
                                )
    
    session.commit()

    event_id = list(event_query)[0][0]
    return event_id


def create_remainder_time(session, remaind_time_list: list[ES.RemainderTimeCreate], event_id: int):
    db_reminad_time = models.RemainderTime

    json_remaind_time_list = [remaind_time.model_dump() for remaind_time in remaind_time_list]
    for time in json_remaind_time_list:
        time.update({'event_id': event_id})
    print(json_remaind_time_list)
    
    query = insert(db_reminad_time).values(json_remaind_time_list)
    session.execute(query)
    session.commit()