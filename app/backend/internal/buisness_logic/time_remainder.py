from sqlalchemy import select
import asyncio

from datetime import datetime, time
from pytz import timezone
from dateutil import tz

import aiohttp

from internal.db import models, config
    

async def start_timer(session):
    remainder_time = models.RemainderTime.__table__.c
    event = models.Event.__table__.c

    bot_token = config.get_settings().BOT_TOKEN

    while True:
        current_datetime = datetime.utcnow()
        time_ = current_datetime.time()
        t = time(hour=time_.hour, minute=time_.minute, second=time_.second, tzinfo=tz.tzoffset(None, 3*60*60))
        query = select(event['chat_id', 'event_name'], remainder_time['date_to_remaind', 'time_to_remaind']
                       ).filter(event.id == remainder_time.event_id
                            ).where(remainder_time.date_to_remaind == current_datetime.date())
                                    # ).filter(t <= remainder_time.time_to_remaind)
        

        remainder_times = sorted((await session.execute(query)).all())

        rmts = []
        if remainder_times:
            
            for rmt in remainder_times:
                local_datetime = current_datetime
                chat_id, event_name, date_to_remaind, time_to_remaind = rmt
                
                local_datetime += time_to_remaind.tzinfo.utcoffset(current_datetime)
                
                time_to_remaind = (datetime.combine(date_to_remaind, time_to_remaind) + time_to_remaind.tzinfo.utcoffset(current_datetime)).time()
                time_to_remaind = time_to_remaind.replace(microsecond=0)

                if local_datetime.time() <= time_to_remaind:
                    seconds_to_remaind = int((datetime.combine(date_to_remaind, time_to_remaind) - local_datetime).total_seconds())
                    rmts.append((chat_id, event_name, date_to_remaind, time_to_remaind, seconds_to_remaind))
            
            try:
                chat_id, event_name, date_to_remaind, time_to_remaind, seconds_to_remaind = rmts[0]
            except IndexError:
                await asyncio.sleep(60)
            else:
                if 0 <= seconds_to_remaind <= 60:
                    await asyncio.sleep(int(seconds_to_remaind))
                    
                    date_to_remaind = datetime.strftime(date_to_remaind, '%d-%m-%Y')
                    message = f'НАПОМИНАНИЕ О СОБЫТИИ: {event_name} {date_to_remaind}'
                    async with aiohttp.ClientSession() as web_session:
                        async with web_session.get(url=f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}') as resp:
                            status_code = resp.status

  

