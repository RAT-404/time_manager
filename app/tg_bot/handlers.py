from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from auxiliary_functions import *
from schemas import *
from api_request import *


router = Router()      


@router.message(Command('help'))
async def start_handler(msg: Message):
    await msg.answer('''Привет, вот правила, по которым работает бот:\n\t\tесть несколько команд, все они работают при наличии некоторых символов в начале сообщения:\n\t\tall (выводит все грядущие события), если нужна подробная информация по конкретному событию, то\nse (search event) и в следующей строке введите его название\n\t\tce (create event) --- crt (create reminder time)\n\t\tue (update event) --- urt (update reminder time)\n\t\tde (delete event) --- drt (delete reminder time)\n\t\tза более подробной информацией обращайтесь к команадам с сисволом /\n\t\tнапример /ce_help выведет подробную информацию по созданию отдельного события''')
    

@router.message(Command('ce_help'))
async def create_event_help(msg: Message):
    await msg.answer('''ce (create event) указывается в первой строке\n\t\tпри создании нового события, во второй строке указывается его название\n\t\tв третьей дата начала, пример (2023-12-03)\nв четвертой время начала события, пример (22:15:00)\n\t\tкаждый новый параметр указывается с новой строки и в требуемом формате, иначе будет выведена ошибка''')

@router.message(Command('ue_help'))
async def update_event_help(msg: Message):
    await msg.answer('''ue (update event) указывается в первой строке\n\t\tпри обновлении данных о событии, во второй строке указывается его нынешнее название и через знач > новое, если название не надо менять, можете не ставить >\n\t\tв третьей новая дата начала, пример (2023-12-03) или . в случае, если дату не надо изменять\n\t\tв четвертой новаое время начала события, пример (22:15:00) или . в случае, если дату не надо изменять\n\t\tкаждый новый параметр указывается с новой строки и в требуемом формате, иначе будет выведена ошибка''')
    

@router.message(Command('de_help'))
async def delete_event_help(msg: Message):
    await msg.answer('''de (delete event) указывается в первой строке\nдля удаления события необходимо написать его название во второй строке\n\t\tкаждый новый параметр указывается с новой строки и в требуемом формате, иначе будет выведена ошибка''')


@router.message(Command('crt_help'))
async def create_event_help(msg: Message):
    await msg.answer('''crt (create remainder) указывается в первой строке\n\t\tпри создании нового напоминания, во второй строке указывается название событие, для которого создается напоминание\n\t\tв третьей дата напоминания, пример (2023-12-03)\n\t\tв четвертой время напоминания, пример (22:15:00)\n\t\tкаждый новый параметр указывается с новой строки и в требуемом формате, иначе будет выведена ошибка''')



@router.message(F.text.startswith('all'))
async def get_all_events(msg: Message):
    response_text, status_code = await APIRequest(chat_id=msg.chat.id).get_events()
    
    if status_code in (200, ):
        await msg.answer(response_text)
    else:
        await msg.answer('что то пошло не так, попробуйте еще раз, возможно ошибка на стороне сервера')


@router.message(F.text.startswith('se'))
async def search_event_by_name(msg: Message):
    event_name = [i for i in msg.text.strip().split()][1:]
    chat_id = msg.chat.id
    response_text, status_code = await APIRequest(chat_id=chat_id, url_params=f'?event_name={event_name}').get_events()
    
    await check_status_code(status_code, msg, response_text)


@router.message(F.text.startswith('ce'))
async def create_event(msg: Message):
    lst = [i for i in msg.text.strip().split('\n')][1:]
    try:
        event_json = validate_event_args(lst)
        event_json['chat_id'] = str(msg.chat.id)
    except TypeError as error_message:
        await msg.answer(str(error_message))
    else:
        event_data = Event(**event_json).model_dump()
        status_code = await APIRequest(url_params=f'create-event/').create_event(event_data)
        await check_status_code(status_code, msg, 'событие создано')



@router.message(F.text.startswith('ue'))
async def update_event(msg: Message):
    chat_id = msg.chat.id
    event_name, *lst = [i for i in msg.text.strip().split('\n')][1:]
    
    if '>' in event_name:
        event_name, new_event_name = event_name.split('>', 1)
        new_event_name = new_event_name.strip()
    new_event_name = event_name.strip()
    
    events_by_name, *_ = await APIRequest(chat_id=chat_id, url_params=f'?name={event_name.strip()}').get_events_json()
    event_by_name = events_by_name.get('events')[0]
    event_id = event_by_name.get('id')
    
    lst = [new_event_name] + lst
    try:
        event_json = validate_event_args(lst)
        for key in event_json.keys():
            if event_json[key] != '.':
                event_by_name[key] = event_json[key]

        event_json['chat_id'] = str(msg.chat.id)
    except TypeError as error_message:
        await msg.answer(str(error_message))
    else:
        event_data = Event(**event_by_name).model_dump()
        status_code = await APIRequest(url_params=f'update-event/').update_event(event_id, event_data)
        await check_status_code(status_code, msg, 'событие обновлено')


@router.message(F.text.startswith('de'))
async def delete_event(msg: Message):
    chat_id = msg.chat.id
    event_name = msg.text.strip().split('\n')[1]
    events_by_name, *args = await APIRequest(chat_id=chat_id, url_params=f'?name={event_name}').get_events_json()
    events: list = events_by_name.get('events')
    event_id = events[0].get('id')
    
    status_code = await APIRequest(url_params=f'delete-event/').delete_event(event_id)
    await check_status_code(status_code, msg, 'событие удалено')


@router.message(F.text.startswith('crt'))
async def create_remainder_time(msg: Message):
    lst = [i for i in msg.text.strip().split('\n')][1:]
    event_name = lst[0]
    chat_id = msg.chat.id
    events_by_name, *_ = await APIRequest(chat_id=chat_id, url_params=f'?name={event_name.strip()}').get_events_json()
    event_by_name = events_by_name.get('events')[0]
    event_id = event_by_name.get('id')
    
    try:
        remainder_time_json = validate_remainder_time_args(lst)
        remainder_time_json['event_id'] = event_id
    except TypeError as error_message:
        await msg.answer(str(error_message))
    else:
        remainder_time_data = [RemainderTime(**remainder_time_json).model_dump()]
        status_code = await APIRequest(url_params=f'create-remainder-times/').create_remainder_times(remainder_time_data)
        await check_status_code(status_code, msg, 'напоминание создано')


@router.message(F.text.startswith('drt'))
async def delete_remainder_time(msg: Message):
    lst = [i for i in msg.text.strip().split('\n')][1:]
    event_name = lst[0]
    chat_id = msg.chat.id
    events_by_name, *_ = await APIRequest(chat_id=chat_id, url_params=f'?name={event_name.strip()}').get_events_json()
    event_by_name = events_by_name.get('events')[0]
    remainder_time_by_event = event_by_name.get('remainder_times')

    status_code = 404
    try:
        remainder_time_json = validate_remainder_time_args(lst)
        remainder_time_id = None
        for remainder_time in remainder_time_by_event:
            dates_equale = remainder_time.get('date_to_remaind') == remainder_time_json.get('date_to_remaind')
            times_equale = remainder_time.get('time_to_remaind')[:-3] == remainder_time_json.get('time_to_remaind')[:-2]
            if dates_equale and times_equale:
                remainder_time_id = remainder_time.get('id')
        
        
        if remainder_time_id:
            status_code = await APIRequest(url_params=f'delete-remainder-time/').delete_remainder_times(remainder_time_id)
    except TypeError as error_message:
        await msg.answer(str(error_message))
    else:
        await check_status_code(status_code, msg, 'напоминане удалено')


@router.message()
async def stub_answer(msg: Message):
    await msg.answer('Не корректный запрос')

