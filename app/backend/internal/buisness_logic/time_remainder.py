from sqlalchemy import select
import asyncio

from fastapi import Depends

from typing import Annotated
from datetime import datetime, time, timedelta
from threading import Thread
from pytz import timezone
from dateutil import tz

import aiohttp

from ..db.models import RemainderTime, Event
from ..db.database import AsyncSession, get_async_session
from tg_bot.config import get_settings
    
# TODO need refactoring
async def start_timer(session):
    remainder_time_table = RemainderTime.__table__.c
    event_table = Event.__table__.c

    bot_token = get_settings().BOT_TOKEN

    while True:
        current_datetime = datetime.now(tz=timezone('Europe/Moscow'))
        time_ = current_datetime.time()
        t = time(hour=time_.hour, minute=time_.minute, second=time_.second, tzinfo=tz.tzoffset(None, 3*60*60)) # TODO tzinfo=tz.tzoffset(None, 3*60*60)
        query = select(event_table['chat_id', 'event_name'], remainder_time_table['date_to_remaind', 'time_to_remaind']
                       ).filter(event_table.id == remainder_time_table.event_id
                            ).where(remainder_time_table.date_to_remaind == current_datetime.date()
                                    ).filter(t <= remainder_time_table.time_to_remaind)
        

        remainder_times = sorted((await session.execute(query)).all())
        if remainder_times:
            chat_id, event_name, date_to_remaind, time_to_remaind = remainder_times[0]
            seconds_to_remaind = int((datetime.combine(date_to_remaind, time_to_remaind) - current_datetime).total_seconds())
            if 0 <= seconds_to_remaind <= 60:
                await asyncio.sleep(int(seconds_to_remaind))
                message = f'НАПОМИНАНИЕ О СОБЫТИИ: {event_name}'
                async with aiohttp.ClientSession() as web_session:
                    async with web_session.get(url=f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}') as resp:
                        status_code = resp.status  # TODO тут отправляется оповещение боту в тг +- так в голове у меня (отправляется id события, в другой таблице ищется чат с этим событием, туда летит напоминание)
                        # logging status code

        await asyncio.sleep(60)
  

