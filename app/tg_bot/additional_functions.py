from datetime import datetime, timedelta
import locale
import os
import requests

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, User

import schemas
from api_request import APIRequest


async def get_user_locale(from_user: User) -> str:
    return ''
    # loc = from_user.language_code
    # user_locale = locale.locale_alias[loc]
    
    # if os.name == 'nt':
    #     user_locale = user_locale.split(".")[0]
    
    # return user_locale


def highlight_event_day(event_day: str) -> str:
    return f'*{event_day}*'


def highlight_rm_day(rm_day: str) -> str:
    return f'<{rm_day}>'


def get_utc_datetime(date: str, new_time: str) -> tuple[str, str]:
    utc_date = date
    date_format = '%Y-%m-%d'
    time_format = '%H:%M:%S'
    timezone_offset = get_timezone(get_string=False)
    new_datetime = f'{date} {new_time}'
    
    rmt_day = datetime.strptime(date, date_format).day
    utc_datetime = datetime.strptime(new_datetime, f'{date_format} {time_format}') - timezone_offset
    utc_time = str(utc_datetime.time()) + get_timezone()
    if utc_datetime.date().day != rmt_day:
        utc_date = utc_datetime.date()
        
    return (str(utc_date), str(utc_time))


def get_local_datetime_start(date_start: str, time_start_utc: str) -> tuple[str, str]:
    datetime_start = datetime.strptime(f'{date_start} {time_start_utc}', '%Y-%m-%d %H:%M:%S%z')
    
    time_start_utc = datetime.strptime(time_start_utc, '%H:%M:%S%z')
    time_offset = time_start_utc.tzinfo.utcoffset(datetime.now())
    
    local_time_start = str((time_start_utc + time_offset).time())
    local_date = str((datetime_start + time_offset).date())
    return local_date, local_time_start


async def unpack_state(state: FSMContext) -> tuple:
    event_data = (await state.get_data()).get('event_data')
    event_id, event_name, date_start, time_start = event_data.get('event_id'), event_data.get('event_name'), event_data.get('date_start'), event_data.get('time_start')
    return (event_id, event_name, date_start, time_start)


def get_timezone(get_string: bool = True) -> str | timedelta:
    dt = datetime.now()
    offset = dt.astimezone().tzinfo.utcoffset(dt)
    if get_string:
        offset = str(offset).split(':')[0]
        offset = f'+0{offset}00' if len(offset) == 1 else f'+{offset}00'
    return offset


async def get_events_on_month(chat_id, year: str, month: str):
    events, *_ = await APIRequest(chat_id=chat_id, url_params=f'get-month-events?date={year}-{month}').get_events_json()
    return events
    


async def get_remainder_times_for_event(chat_id: str, event_id: str):
    event, *_ = await APIRequest(chat_id=chat_id, url_params=f'get-event/{event_id}').get_events_json()
    remainder_times = event.get('events')[0]

    return remainder_times


async def create_event(data: dict, msg: Message):
    try:
        data['chat_id'] = str(msg.chat.id)
    except (TypeError, ValueError) as error_message:
        await msg.answer(str(error_message))
    else:
        event_data = schemas.Event(**data).model_dump()
        
        status_code = await APIRequest(url_params=f'create-event/').create_event(event_data)
        if status_code in (404, 422):
            raise Exception('Unprocessable Entity')
        

async def update_event(data: dict, msg: Message):
    event_data = schemas.Event(**data).model_dump()
    await APIRequest(url_params=f'update-event/').update_event(data.get('event_id'), event_data)


async def delete_event(event_id: str, msg: Message):
    await APIRequest(url_params=f'delete-event/').delete_event(event_id)


async def create_remainder_time(data: dict, msg: Message):
    remainder_time_data = [schemas.RemainderTime(**data).model_dump()]
    await APIRequest(url_params=f'create-remainder-times/').create_remainder_times(remainder_time_data)


async def update_remainder_time(data: dict, msg: Message): 
    rmt_data = schemas.RemainderTime(**data).model_dump()
    await APIRequest(url_params=f'update-remainder-time/').update_rmt(str(data.get('id')), rmt_data)


async def delete_rmt(rmt_id: int, msg: Message):
    try:
        status_code = await APIRequest(url_params=f'delete-remainder-time/').delete_remainder_times(rmt_id)
        if status_code >= 400:
            raise ValueError()
    except ValueError:
        await msg.answer('Что то пошло не так, возможно ошибка на стороне сервера')