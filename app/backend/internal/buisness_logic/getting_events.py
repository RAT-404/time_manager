from sqlalchemy import select
from fuzzywuzzy import fuzz

import pytz
from datetime import datetime as dt, time, timedelta
from typing import Any
from dateutil import tz

from internal.db.schemas import EventSchema as ES
from internal.db import database
from internal.db import models


class Event:
    def __init__(self, chat_id: str, event: models.Event, session: database.AsyncSession, datetime: str | None = None,  query_fields: tuple[str] | None = None):
        self.session = session
        self.event = event
        self.chat_id = chat_id

        self.date_format = '%Y-%m-%d'
        self.time_format = '%H:%M:%S%z'
        self.datetime_format = f'{self.date_format}T{self.time_format}'
        self.tzoffset = tz.tzoffset(None, 3*60*60) # TODO refactoring!! pydantic-settings

        self.__create_datetime(datetime if datetime else str(dt.now(tz=self.tzoffset).strftime(self.datetime_format)))
        

    async def get_events_by_query(self, query: Any | None = None) -> dict[str, list[ES.Event]]:
        query = query if query is not None else select(self.event).where(self.event.chat_id == self.chat_id).where(self.event.date_start >= self.date)
        events = await self.session.execute(query)
        

        # TODO refactoring
        schema_events = []

        for row in events:
            row = row[0]
            schema_event = ES.Event(**row.__dict__)
            rem_time = models.RemainderTime
            rem_times = await self.session.execute(select(rem_time).where(rem_time.event_id == row.id))
            schema_event.remainder_times += [ES.RemainderTime(**rem_time_row[0].__dict__) for rem_time_row in rem_times]
            schema_events.append(schema_event)

        return {'events': schema_events}


    async def get_events_by_hour(self):
        get_time = self.__get_time_with_error(self.time)
        
        result = await self.__get_events(get_time(hour=self.time.hour + 1), get_time())
        return result
    
    async def get_event_by_month(self):
        min_date = self.datetime
        max_date = self.datetime + timedelta(days=31)
        days = max_date.date().day
        max_date -= timedelta(days=days)

        query = select(self.event
                    ).where(self.event.chat_id == self.chat_id
                            ).where(self.event.date_start <= max_date
                                ).where(self.event.date_start >= min_date)
        
        result = await self.get_events_by_query(query)
        return result


    async def get_event_by_current_time(self) -> dict[str, list[ES.EventBase]]:
        get_time = self.__get_time_with_error(self.time)
        
        max_time_range = self.time.minute + self.minutes_error if self.time.minute + self.minutes_error <= 59 else 0
        min_time_range = self.time.minute - self.minutes_error if self.time.minute - self.minutes_error >= 0 else 0
        
        result = await self.__get_events(get_time(minute=max_time_range), get_time(minute=min_time_range))
        return result


    async def get_events_by_date(self) -> dict[str, list[ES.EventBase]]:
        query = select(self.event).where(self.event.chat_id == self.chat_id).where(self.event.date_start == self.date)
        result = await self.get_events_by_query(query)
        return result


    async def get_events_by_name(self, name: str, verbal_error: int = 80) -> dict[str, list[ES.EventBase]]:
        query = select(self.event).where(self.event.chat_id == self.chat_id)
        db_result = await self.get_events_by_query(query)
        
        result = []
        for event in db_result.get('events'):
            if fuzz.ratio(event.model_dump().get('event_name', ''), name) >= verbal_error:
                result.append(event)

        return {'events': result}
    

    def __get_time_with_error(self, current_time: time):
        def wrap(hour: int = current_time.hour, minute: int = current_time.minute, second: int = current_time.second, tzinfo: pytz.timezone = pytz.timezone('Europe/Moscow')) -> time:
            return time(hour=hour, minute=minute, second=second, tzinfo=self.tzoffset)
        return wrap
    

    async def __get_events(self, time_with_upper_error, time_with_down_error) -> dict[str, list[ES.EventBase]]:
        query = select(self.event
                    ).where(self.event.chat_id == self.chat_id
                            ).where(self.event.date_start == self.date
                                ).where(time_with_down_error <= self.event.time_start
                                    ).where(self.event.time_start <= time_with_upper_error)

        result = await self.get_events_by_query(query)
        return result
    

    def __create_datetime(self, datetime: str):
        self.datetime = datetime
        self.datetime = self.datetime.replace(' ', '+')
        if '+' not in self.datetime:
            self.datetime += '+0300'
        
        self.datetime = dt.strptime(self.datetime, self.datetime_format)
        
        self.date, self.time = (self.datetime.date(), self.datetime.time())
        self.minutes_error = 1