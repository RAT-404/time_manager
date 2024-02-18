from sqlalchemy import select
from fuzzywuzzy import fuzz
import pytz
from datetime import datetime as dt, time, timedelta
from typing import Any
from dateutil import tz

from internal.db.schemas import EventSchema as ES
from internal.db import database
from internal.db import models


class RemainderTime:
    def __init__(self, rmt: models.RemainderTime, session: database.AsyncSession):
        self.session = session
        self.rmt = rmt

    async def __get_rmt_by_query(self, query: Any | None = None) -> dict[str, list[ES.RemainderTime]]:
        if query is None:
            return {'remainder_times': None}
        
        rmt = await self.session.execute(query)
        schema_rmt = [ES.RemainderTime(**row[0].__dict__) for row in rmt]

        return {'remainder_time': schema_rmt}
    
    async def get_rmt_by_id(self, rmt_id: int) -> dict[str, list[ES.EventBase]]:
        query = select(self.rmt).where(self.rmt.id == rmt_id)
        result = await self.__get_rmt_by_query(query)
        return result

    