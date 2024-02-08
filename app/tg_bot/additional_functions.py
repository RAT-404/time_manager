from datetime import datetime, timedelta
from handlers import Message
from aiogram.fsm.context import FSMContext
from api_request import APIRequest
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram_calendar import get_user_locale

from modifaed_calendar import SimpleCalendar
import schemas
from api_request import APIRequest, RemainderTime


def get_utc_datetime(event_date: str, new_event_time: str) -> tuple[str, str]:
    utc_event_date = event_date
    date_format = '%Y-%m-%d'
    time_format = '%H:%M:%S'
    timezone_offset = get_timezone(get_string=False)
    new_event_datetime = f'{event_date} {new_event_time}'

    event_day = datetime.strptime(event_date, date_format).day
    utc_datetime = datetime.strptime(new_event_datetime, f'{date_format} {time_format}') - timezone_offset
    utc_event_time = str(utc_datetime.time()) + get_timezone()
    if utc_datetime.date().day != event_day:
        utc_event_date = utc_datetime.date()
        
    return (str(utc_event_date), str(utc_event_time))


def get_local_datetime_start(date_start, time_start_utc: str) -> str:
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


def highlight_event_day(text):
    return f'{text}\n*'


async def get_events_on_month(chat_id, year: str, month: str):
    events, *_ = await APIRequest(chat_id=chat_id, url_params=f'get-month-events/?date={year}-{month}').get_events_json()
    return events


async def create_event(data: dict, msg: Message):
    try:
        data['time_start'] += get_timezone()
        data['chat_id'] = str(msg.chat.id)
    except (TypeError, ValueError) as error_message:
        await msg.answer(str(error_message))
    else:
        event_data = schemas.Event(**data).model_dump()
        status_code = await APIRequest(url_params=f'create-event/').create_event(event_data)
        await check_status_code(status_code, msg, 'событие создано')


async def update_event(data: dict, msg: Message):
    try:
        event_id = data.get('event_id')
    except (TypeError, ValueError) as error_message:
        await msg.answer(str(error_message))
    else:
        event_data = schemas.Event(**data).model_dump()
        status_code = await APIRequest(url_params=f'update-event/').update_event(event_id, event_data)
        await check_status_code(status_code, msg, 'Cобытие обновлено')


async def delete_event(data: dict, msg: Message):
    status_code = await APIRequest(url_params=f'delete-event/').delete_event(data.get('event_id'))
    await check_status_code(status_code, msg, 'Событие удалено')


async def create_rt(data: dict, msg: Message):
    chat_id = msg.chat.id
    event_name = data['event_name']

    event = (await APIRequest(chat_id=chat_id, url_params=f'?name={event_name}').get_events_json())[0].get('events')[0]
    event_id = event.get('id')

    data['event_id'] = event_id
    data['time_to_remaind'] += data['chat_timezone']
    remainder_time_data = [RemainderTime(**data).model_dump()]
    print(remainder_time_data)
    status_code = await APIRequest(url_params=f'create-remainder-times/').create_remainder_times(remainder_time_data)
    await check_status_code(status_code, msg, 'напоминание создано')


async def delete_rt(remainder_time_id: int, msg: Message):
    status_code = await APIRequest(url_params=f'delete-remainder-time/').delete_remainder_times(remainder_time_id)
    await check_status_code(status_code, msg, 'напоминане удалено')



def validate_time(time_start: str) -> bool:
    try:
        time_start = str(datetime.strptime(time_start, '%H:%M').time())
    except ValueError:
        raise ValueError('неправильный формат')
    else:
        return time_start  


async def check_status_code(status_code: int, msg: Message, answer: str):
    if status_code in (200, ):
        await msg.answer(answer)
    else:
        await msg.answer('что то пошло не так, попробуйте еще раз, возможно ошибка на стороне сервера')

