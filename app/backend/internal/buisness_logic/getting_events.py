from sqlalchemy import select
from fuzzywuzzy import fuzz

import pytz
from datetime import datetime as dt, time
from typing import Any

from backend.internal.db.schemas import EventSchema as ES
from backend.internal.db.database import AsyncSession
from backend.internal.db import models


class Event:
    def __init__(self, event: models.Event, session: AsyncSession, datetime: str | None = None,  query_fields: tuple[str] | None = None):
        self.session = session
        self.query_fields = query_fields if query_fields else ('event_name', 'date_start', 'time_start', 'date_end', 'time_end')
        self.event = event

        if datetime:
            self.__create_datetime(datetime)
        

    async def get_events_by_query(self, query: Any | None = None) -> dict[str, list[ES.EventBase]]:
        query = query if query else select(self.event.__table__.c[*self.query_fields])
        events = await self.session.execute(query)
        events = [ES.EventBase(**dict(zip(self.query_fields, row))) for row in events]
        return {'events': events}


    async def get_events_by_hour(self):
        get_time = self.__get_time_with_error(self.time)
        
        result = await self.__get_events(get_time(hour=self.time.hour + 1), get_time())
        return result


    async def get_event_by_current_time(self) -> dict[str, list[ES.EventBase]]:
        get_time = self.__get_time_with_error(self.time)

        result = await self.__get_events(get_time(minute=self.time.minute + self.minutes_error), get_time(minute=self.time.minute - self.minutes_error))
        return result


    async def get_events_by_date(self) -> dict[str, list[ES.EventBase]]:
        event = self.event.__table__.c
        query = select(event[*self.query_fields]).where(event.date_start == self.date)
        result = await self.get_events_by_query(query)
        return result


    async def get_events_by_name(self, name: str, verbal_error: int = 80) -> dict[str, list[ES.EventBase]]:
        query = select(self.event.__table__.c[*self.query_fields])
        db_result = await self.get_events_by_query(query)
        
        result = []
        for event in db_result.get('events'):
            if fuzz.ratio(event.model_dump().get('event_name', ''), name) >= verbal_error:
                result.append(event)

        return {'events': result}
    

    def __get_time_with_error(self, current_time: time):
        def wrap(hour: int = current_time.hour, minute: int = current_time.minute, second: int = current_time.second, tzinfo: pytz.timezone = pytz.timezone('Europe/Moscow')) -> time:
            return time(hour=hour, minute=minute, second=second, tzinfo=tzinfo)
        return wrap
    

    async def __get_events(self, time_with_upper_error, time_with_down_error) -> dict[str, list[ES.EventBase]]:
        event = self.event.__table__.c
        
        query = select(event[*self.query_fields]
                    ).where(event.date_start == self.date
                            ).where(time_with_down_error <= event.time_start
                            ).where(event.time_start <= time_with_upper_error)

        result = await self.get_events_by_query(query)
        return result
    

    def __create_datetime(self, datetime: str):
        self.datetime = datetime
        self.date_format = '%d-%m-%Y'
        self.time_format = '%H:%M:%S%z'
        self.datetime_format = f'{self.date_format}T{self.time_format}'
        datetime = dt.strptime(self.datetime.replace(' ', '+'), self.datetime_format)
        
        self.date, self.time = (datetime.date(), datetime.time())
        self.minutes_error = 1