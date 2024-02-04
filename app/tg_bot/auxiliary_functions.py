from datetime import datetime
from handlers import Message
from aiogram.fsm.context import FSMContext
from api_request import APIRequest

from schemas import *
from api_request import *


def highlight_event_day(text):
    return f'{text}\n*'


async def get_events_on_month(chat_id, year: str, month: str):
    events, *_ = await APIRequest(chat_id=chat_id, url_params=f'get-month-events/?date={year}-{month}').get_events_json()
    return events


async def create_event(data: dict, msg: Message):
    try:
        data['time_start'] += data['chat_timezone']
        data['chat_id'] = str(msg.chat.id)
    except (TypeError, ValueError) as error_message:
        await msg.answer(str(error_message))
    else:
        event_data = Event(**data).model_dump()
        status_code = await APIRequest(url_params=f'create-event/').create_event(event_data)
        await check_status_code(status_code, msg, 'событие создано')


async def update_event(data: dict, msg: Message):
    try:
        data['time_start'] += data['chat_timezone']
        data['chat_id'] = str(msg.chat.id)

        chat_id = msg.chat.id
        event_name = data['event_name']

        event = (await APIRequest(chat_id=chat_id, url_params=f'?name={event_name.strip()}').get_events_json())[0].get('events')[0]
        event_id = event.get('id')
    except (TypeError, ValueError) as error_message:
        await msg.answer(str(error_message))
    else:
        event_data = Event(**data).model_dump()
        status_code = await APIRequest(url_params=f'update-event/').update_event(event_id, event_data)
        await check_status_code(status_code, msg, 'событие обновлено')


async def delete_event(data: dict, msg: Message):
    chat_id = msg.chat.id
    event_name = data.get('event_name')
    events = (await APIRequest(chat_id=chat_id, url_params=f'?name={event_name}').get_events_json())[0].get('events')
    event_id = events[0].get('id')

    status_code = await APIRequest(url_params=f'delete-event/').delete_event(event_id)
    await check_status_code(status_code, msg, 'событие удалено')


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

