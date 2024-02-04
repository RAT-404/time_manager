from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter

from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext

from aiogram_calendar import SimpleCalendarCallback, get_user_locale

from auxiliary_functions import *
from schemas import *
from api_request import *
from states import *


router = Router()      


timezone_buttons = [[KeyboardButton(text=f'+{i}') for i in range(0, 6)],
                    [KeyboardButton(text=f'+{i}') for i in range(6, 12)]]

command_buttons = [[KeyboardButton(text='/create_event'), KeyboardButton(text='/update_event'), KeyboardButton(text='/delete_event')],
                   [KeyboardButton(text='/create_rt'), KeyboardButton(text='/delete_rt'), KeyboardButton(text='/all')]]

timezone_kb = ReplyKeyboardMarkup(keyboard=timezone_buttons, resize_keyboard=True)      
start_kb = ReplyKeyboardMarkup(keyboard=command_buttons, resize_keyboard=True)


from aiogram.types import CallbackQuery

from aiogram_calendar.schemas import SimpleCalendarCallback

from datetime import datetime
from modified_simple_calendar import SimpleCalendar
from ChooseEvent import EventChoose


@router.message(Command('help'))
async def get_all_events(msg: Message):
    await msg.answer('Привет, рад, что ты решил воспользоваться моим time manager`ом, для начала напиши /start')


@router.message(Command('start'))
async def start(msg: Message):
    await msg.answer(text='Выберите следующее действие и следуйте инструкциям', reply_markup=start_kb)


@router.message(Command('all'))
async def view_all_events(msg: Message):    # , state: FSMContext
    request = APIRequest(chat_id=msg.chat.id)
    response_text, status_code = await request.get_events()
    if not response_text:
        response_text = 'На данный момент предстоящие события не обнаружены'
    else:
        calendar = SimpleCalendar(locale=await get_user_locale(msg.from_user))
        await msg.answer(
            "События: ",
            reply_markup=await calendar.start_calendar(chat_id=msg.chat.id)
        )    

    await check_status_code(status_code, msg, response_text)


@router.callback_query(SimpleCalendarCallback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    calendar = SimpleCalendar(
        locale=await get_user_locale(callback_query.from_user), show_alerts=True
    )
    actual_datetime = datetime.now()
    actual_year, actual_month, actual_day = actual_datetime.year, actual_datetime.month, actual_datetime.day
    calendar.set_dates_range(datetime(actual_year - 1, 1, 1), datetime(actual_year + 3, 12, 31))
    
    events_on_month = await get_events_on_month(callback_query.message.chat.id, actual_year, actual_month)
    
    args = {
        'callback_query': callback_query,
        'callback_data': callback_data,
        'actual_datetime': actual_datetime,
        'calendar_events_dates': events_on_month
    }

    selected, date = await calendar.process_selection(args)
    
    if selected:
        print(events_on_month.get('events'), type(events_on_month))
        event_names_kb = []
        for event in events_on_month.get('events'):
            event_names_kb.append(InlineKeyboardButton(text=event.get('event_name')))
        
        data = await state.get_data()
        date_ = date.strftime('%Y-%m-%d')
        if data.get('operation_type') in ('create_rt', ):
            await state.update_data(date_to_remaind=date_)    
        else:
            await state.update_data(date_start=date_)

        await state.set_state(DateOperations.choosing_time)
        event = EventChoose()
        await callback_query.message.answer(
            "События: ",
            reply_markup=await event.start_choose(chat_id=callback_query.message.chat.id)
        )    





@router.message(Command('create_event'))
async def start_create_event(msg: Message, state: FSMContext):
    await msg.answer(
        "Выберите дату: ",
        reply_markup=await SimpleCalendar(locale=await get_user_locale(msg.from_user)).start_calendar()
    )
    await state.update_data(operation_type='create_event')
    await state.set_state(DateOperations.choosing_date)

@router.message(Command('update_event'))
async def delete_event(msg: Message, state: FSMContext):
    await msg.answer(
        "Выберите новую дату: ",
        reply_markup=await SimpleCalendar(locale=await get_user_locale(msg.from_user)).start_calendar()
    )
    await state.update_data(operation_type='update_event')
    await state.set_state(DateOperations.choosing_date)


@router.message(Command('delete_event'))
async def delete_event(msg: Message, state: FSMContext):
    await msg.answer('Введите название события, которое хотите удалить')
    await state.update_data(operation_type='delete_event')
    await state.set_state(DateOperations.choosing_date)


@router.message(Command('create_rt'))
async def start_create_event(msg: Message, state: FSMContext):
    await msg.answer(
        "Выберите дату для напоминания: ",
        reply_markup=await SimpleCalendar(locale=await get_user_locale(msg.from_user)).start_calendar()
    )
    await state.update_data(operation_type='create_rt')
    await state.set_state(DateOperations.choosing_date)


@router.message(Command('delete_rt'))
async def delete_event(msg: Message, state: FSMContext):
    await msg.answer('Введите номер напоминание, которое хочешь удалить, оно указано в (скобочка) при выхове команды all')
    await state.update_data(operation_type='delete_rt')
    await state.set_state(DateOperations.choosing_rt_id)
 

@router.message(DateOperations.choosing_date)
@router.callback_query(SimpleCalendarCallback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    calendar = SimpleCalendar(
        locale=await get_user_locale(callback_query.from_user), show_alerts=True
    )
    actual_year = datetime.now().year
    calendar.set_dates_range(datetime(actual_year - 1, 1, 1), datetime(actual_year + 3, 12, 31))
    selected, date = await calendar.process_selection(callback_query, callback_data, callback_query.message.chat.id)
    if selected:
        data = await state.get_data()
        date_ = date.strftime('%Y-%m-%d')
        if data.get('operation_type') in ('create_rt', ):
            await state.update_data(date_to_remaind=date_)    
        else:
            await state.update_data(date_start=date_)

        await state.set_state(DateOperations.choosing_time)
        await callback_query.message.answer(
            f'Вы выбрали {date.strftime("%d-%m-%Y")}\nТеперь напишите время в формате часы:минуты'
        )


@router.message(DateOperations.choosing_time)
async def choosing_event_time_start(msg: Message, state: FSMContext):
    try:
        time_start = validate_time(msg.text.lower())
    except ValueError as error_message:
        await msg.answer(str(error_message))
    else:
        data = await state.get_data()
        if data.get('operation_type') in ('create_rt', ):
            await state.update_data(time_to_remaind=time_start)    
        else:
            await state.update_data(time_start=time_start)

        await msg.answer('Выберите вашу временную зону', reply_markup=timezone_kb)
        await state.set_state(DateOperations.choosing_timezone)
    

@router.message(DateOperations.choosing_timezone)
async def choosing_event_timezone(msg: Message, state: FSMContext):
    try:
        timezone = msg.text.lower().replace('+', '')
        tz = int(timezone)
        if not(0 <= tz <= 12):
            raise ValueError('Неверный тип временной зоны, временная зона должна быть в диапозоне от 0 до 12')
    except ValueError as error_message:
        await msg.answer(str(error_message))
    else:
        if len(timezone) == 1:
            timezone = '0' + timezone
        timezone = f'+{timezone}00'
        await msg.answer(f'Временной сдвиг успешно установлен: {timezone}')
        await state.update_data(chat_timezone=timezone)

        data = await state.get_data()
        text = 'Выберите название нового события'
        op_type = data.get('operation_type')
        if op_type in ['update_event']:
            text = 'Выберите название события, которое хотите изменить'
        elif op_type in ['create_rt']:
            text = 'Выберите название события, к которому хотите создать напоминание'
        await state.set_state(DateOperations.choosing_event_name)
        await msg.answer(text)


@router.message(DateOperations.choosing_rt_id)
async def choosing_rt_id(msg: Message):
    remainder_time_id = msg.text.lower()
    
    try:
        rt_id = int(remainder_time_id)
        if rt_id <= 0:
            ValueError('Не правильно')
    except ValueError:
        await msg.answer('Необходимо ввести число, целочисленно, то что указано в (скобках)')
    else:
        await delete_rt(remainder_time_id, msg)


@router.message(DateOperations.choosing_event_name)
async def choosing_event_name(msg: Message, state: FSMContext):
    await state.update_data(event_name=msg.text.lower())
    
    data = await state.get_data()
    operation_type = data.get('operation_type')    
    match operation_type:
        case 'create_event':
            await create_event(data, msg)
        case 'update_event':
            await update_event(data, msg)
        case 'delete_event':
            await delete_event(data, msg)
        case 'create_rt':
            await create_rt(data, msg)
        case _:
            await msg.answer('Что то пошло не так')

    await state.clear()


@router.message()
async def stub_answer(msg: Message):
    await msg.answer('Не корректный запрос')

