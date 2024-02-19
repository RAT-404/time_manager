from sqlalchemy import select

from datetime import datetime as dt, timedelta
from typing import Any

from internal.db.schemas import EventSchema as ES, RemainderTimeSchema as RT
from internal.db import database
from internal.db import models


class Event:
    def __init__(self, chat_id: str, event: models.Event, session: database.AsyncSession, datetime: str | None = None):
        self.session = session
        self.event = event
        self.chat_id = chat_id

        self.date_format = '%Y-%m-%d'
        self.time_format = '%H:%M:%S'
        self.datetime_format = f'{self.date_format}T{self.time_format}'

        self.datetime = dt.strptime(datetime, self.datetime_format) if datetime else dt.utcnow()
        self.date = self.datetime.date()

    async def __get_events_by_query(self, query: Any | None = None) -> dict[str, list[ES.Event]]:
        query = query if query is not None else select(self.event).where(self.event.chat_id == self.chat_id)
        events = await self.session.execute(query)
        
        schema_events = []

        for row in events:
            row = row[0]
            schema_event = ES.Event(**row.__dict__)
            rem_time = models.RemainderTime
            rem_times = await self.session.execute(select(rem_time).where(rem_time.event_id == row.id))
            schema_event.remainder_times += [RT.RemainderTime(**rem_time_row[0].__dict__) for rem_time_row in rem_times]
            schema_events.append(schema_event)

        return {'events': schema_events}
    
    async def get_event_by_month(self):
        min_date = self.datetime
        max_date = self.datetime + timedelta(days=31)
        days = max_date.date().day
        max_date -= timedelta(days=days)

        query = select(self.event
                    ).where(self.event.chat_id == self.chat_id
                            ).where(self.event.date_start <= max_date
                                ).where(self.event.date_start >= min_date)
        
        result = await self.__get_events_by_query(query)
        return result

    async def get_events_by_date(self) -> dict[str, list[ES.EventBase]]:
        query = select(self.event).where(self.event.chat_id == self.chat_id).where(self.event.date_start == self.date)
        result = await self.__get_events_by_query(query)
        return result

    async def get_event_by_id(self, event_id: int) -> dict[str, list[ES.EventBase]]:
        query = select(self.event).where(self.event.chat_id == self.chat_id).where(self.event.id == event_id)
        result = await self.__get_events_by_query(query)
        return result
    