from sqlalchemy import select
import asyncio

from datetime import datetime, time
from pytz import timezone
from dateutil import tz

import aiohttp

from internal.db import models, config
    

# TODO refactoring
async def start_timer(session):
    remainder_time_table = models.RemainderTime.__table__.c
    event_table = models.Event.__table__.c

    bot_token = config.get_settings().BOT_TOKEN

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
                message = f'НАПОМИНАНИЕ О СОБЫТИИ: {event_name} {date_to_remaind}'
                async with aiohttp.ClientSession() as web_session:
                    async with web_session.get(url=f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}') as resp:
                        status_code = resp.status
                        # TODO logging status code

        await asyncio.sleep(60)
  

