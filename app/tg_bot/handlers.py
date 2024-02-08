from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext

from aiogram_calendar import get_user_locale

from aiogram.types import CallbackQuery


from datetime import datetime

from additional_functions import update_event, get_events_on_month, delete_event, get_timezone, get_local_datetime_start, get_utc_datetime
from schemas import EventAct, EventCallback, SimpleCalendarCallback, SimpleCalAct
from api_request import APIRequest
from states import EventOperations

from modifaed_calendar import SimpleCalendar


router = Router()      


# timezone_buttons = [[KeyboardButton(text=f'+{i}') for i in range(0, 6)],
#                     [KeyboardButton(text=f'+{i}') for i in range(6, 12)]]

# command_buttons = [[KeyboardButton(text='/create_event'), KeyboardButton(text='/update_event'), KeyboardButton(text='/delete_event')],
#                    [KeyboardButton(text='/create_rt'), KeyboardButton(text='/delete_rt'), KeyboardButton(text='/all')]]

# timezone_kb = ReplyKeyboardMarkup(keyboard=timezone_buttons, resize_keyboard=True)      
# start_kb = ReplyKeyboardMarkup(keyboard=command_buttons, resize_keyboard=True)


@router.message(Command('help'))
async def get_all_events(msg: Message):
    await msg.answer('Привет, рад, что ты решил воспользоваться моим time manager`ом, для начала напиши /all')


# @router.message(Command('start'))
# async def start(msg: Message):
#     await msg.answer(text='Выберите следующее действие и следуйте инструкциям', reply_markup=start_kb)


@router.message(Command('all'))
async def view_all_events(msg: Message, state: FSMContext):
    await state.set_state(EventOperations.choose_event)
    calendar = SimpleCalendar(locale=await get_user_locale(msg.from_user))
    await msg.answer(
        "События: ",
        reply_markup=await calendar.start_calendar(chat_id=msg.chat.id)
    )


@router.callback_query(SimpleCalendarCallback.filter(F.act != SimpleCalAct.select_new_event_date))
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    calendar = SimpleCalendar(
        locale=await get_user_locale(callback_query.from_user), show_alerts=True
    )
    actual_datetime = datetime.now()
    actual_year, actual_month = actual_datetime.year, actual_datetime.month
    calendar.set_dates_range(datetime(actual_year - 1, 1, 1), datetime(actual_year + 3, 12, 31))
    
    selected, date = await calendar.process_selection(callback_query, callback_data)

    events_on_month = await get_events_on_month(callback_query.message.chat.id, actual_year, actual_month)
    
    if date:
        kb = [[InlineKeyboardButton(
                    text=event.get('event_name'),
                    callback_data=EventCallback(act=EventAct.change_event,
                                                id=str(event.get('id'))).pack())] 
                for event in events_on_month.get('events') if datetime.strptime(event.get('date_start'), '%Y-%m-%d').day == date.day]


        cancel_row = [
                [InlineKeyboardButton(
                    text='append', 
                    callback_data=EventCallback(act=EventAct.append).pack()
                ),
                InlineKeyboardButton(
                    text='cancel', 
                    callback_data=EventCallback(act=EventAct.cancel).pack()
                )]
            ]
        kb += cancel_row
        kb = InlineKeyboardMarkup(row_width=1, inline_keyboard=kb)

    if selected:        
        await callback_query.message.answer(
            "События: ",
            reply_markup=kb
        )

 

@router.callback_query(EventCallback.filter(F.act == EventAct.change_event))
async def process_select_event(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    chat_id = callback_query.message.chat.id
    
    event, status_code = await APIRequest(chat_id, url_params=f'get-event/{callback_data.id}').get_events_json()
    
    try:
        event = event.get('events')[0]
    except IndexError:
        await callback_query.message.answer('Событие не обнаружено, возможно оно было удалено ранее')
    else:
        event_id, event_name, date_start, time_start_utc = event.get('id'), event.get('event_name'), event.get('date_start'), event.get('time_start')
        date_start, time_start = get_local_datetime_start(date_start, time_start_utc)

        event_data = {
            'event_id': event_id,
            'chat_id': str(callback_query.message.chat.id), 
            'event_name': event_name, 
            'date_start': date_start, 
            'time_start': time_start
        }

        time_start = time_start.split('+')[0]
        
        try:
            date_start = datetime.strftime(datetime.strptime(date_start, '%Y-%m-%d'), '%d-%m-%Y')
        except ValueError:
            await callback_query.message.answer('Что то пошло не так, попробуйте еще раз')
        else:
            await state.update_data(event_data=event_data)
            
            kb = [
                [InlineKeyboardButton(
                    text=event_name, 
                    callback_data=EventCallback(act=EventAct.change_event_name, id=str(event_id)).pack()
                )],
                [InlineKeyboardButton(
                    text=date_start, 
                    callback_data=EventCallback(act=EventAct.change_event_date, id=str(event_id)).pack()
                )],
                [InlineKeyboardButton(
                    text=time_start, 
                    callback_data=EventCallback(act=EventAct.change_event_time, id=str(event_id)).pack()
                )],
                [
                    InlineKeyboardButton(
                        text='delete', 
                        callback_data=EventCallback(act=EventAct.delete, id=str(event_id)).pack()
                    ),
                    InlineKeyboardButton(
                        text='cancel', 
                        callback_data=EventCallback(act=EventAct.cancel, id=str(event_id)).pack()
                    )
                ]
            ]
            
            kb = InlineKeyboardMarkup(row_width=1, inline_keyboard=kb)

            await callback_query.message.answer(
                "События: ",
                reply_markup=kb
            )    


#change event name
@router.callback_query(EventCallback.filter(F.act==EventAct.change_event_name))
async def change_event_name_callback(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    await state.set_state(EventOperations.change_event_name)
    await callback_query.message.answer(text='Введите новое название события: ')


@router.message(EventOperations.change_event_name)
async def change_event_name(msg: Message, state: FSMContext):
    data = (await state.get_data()).get('event_data')
    data['event_name'] = msg.text.lower()
    
    try:
        await update_event(data, msg)
    except Exception as e:
        await msg.answer(text='Что то пошло не так')
        

#change event date
@router.callback_query(EventCallback.filter(F.act==EventAct.change_event_date))
async def change_event_date_callback(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    await state.set_state(EventOperations.change_event_date)
    msg = callback_query.message
    calendar = SimpleCalendar(locale=await get_user_locale(callback_query.from_user))
    await msg.answer(
        "Выберите новую дату: ",
        reply_markup=await calendar.start_calendar(chat_id=msg.chat.id, day_selection_act=SimpleCalAct.select_new_event_date)
    )


@router.callback_query(SimpleCalendarCallback.filter(F.act == SimpleCalAct.select_new_event_date))
async def change_event_date(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    data = (await state.get_data()).get('event_data')
    msg = callback_query.message

    try:
        calendar = SimpleCalendar(
            locale=await get_user_locale(callback_query.from_user), show_alerts=True
        )
        actual_datetime = datetime.now()
        actual_year = actual_datetime.year
        calendar.set_dates_range(datetime(actual_year - 1, 1, 1), datetime(actual_year + 3, 12, 31))
        
        selected, date = await calendar.process_selection(callback_query, callback_data)

        if selected:
            new_event_date = str(date.date())
            utc_date, utc_time = get_utc_datetime(new_event_date, data.get('time_start'))
            data['date_start'] = utc_date
            data['time_start'] = utc_time
            await update_event(data, msg)
            
    except Exception as e:
        await msg.answer(text='Что то пошло не так, возможно ошибка на стороне сервера')
    else:
        await callback_query.message.answer("Дата события обновлена")
        await state.clear()


#delete event
@router.callback_query(EventCallback.filter(F.act==EventAct.delete))
async def pr(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    data = (await state.get_data()).get('event_data')
    await delete_event(data, callback_query.message)
    await callback_query.message.answer(text='delete')


#change event time
@router.callback_query(EventCallback.filter(F.act==EventAct.change_event_time))
async def change_event_time_callback(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    await state.set_state(EventOperations.change_event_time)
    msg = callback_query.message
    await msg.answer("Напишите новое время для события в формате ЧАСЫ:МИНУТЫ (например 15:32) ")


@router.message(EventOperations.change_event_time)
async def change_event_name(msg: Message, state: FSMContext):
    data = (await state.get_data()).get('event_data')
    event_date = data.get('date_start')
    event_time = msg.text.lower() + ':00'
    
    try:
        utc_date, utc_time = get_utc_datetime(event_date, event_time)
        data['date_start'] = utc_date
        data['time_start'] = utc_time  
        await update_event(data, msg)
    except ValueError:
        await msg.answer('Время написано в неправильном формате, попробуйте еще раз')
    else:
        await msg.answer('Время обновлено')
        await state.clear()
    

#cancel event choose
@router.callback_query(EventCallback.filter(F.act==EventAct.cancel))
async def cancel_choosing_events(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    await state.clear()


@router.callback_query(EventCallback.filter(F.act==EventAct.append))
async def append_event_callback(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    await callback_query.message.answer(text='Введите новое название события')



# @router.message(Command('create_event'))
# async def start_create_event(msg: Message, state: FSMContext):
#     await msg.answer(
#         "Выберите дату: ",
#         reply_markup=await SimpleCalendar(locale=await get_user_locale(msg.from_user)).start_calendar()
#     )
#     await state.update_data(operation_type='create_event')
#     await state.set_state(DateOperations.choosing_date)

# @router.message(Command('update_event'))
# async def delete_event(msg: Message, state: FSMContext):
#     await msg.answer(
#         "Выберите новую дату: ",
#         reply_markup=await SimpleCalendar(locale=await get_user_locale(msg.from_user)).start_calendar()
#     )
#     await state.update_data(operation_type='update_event')
#     await state.set_state(DateOperations.choosing_date)


# @router.message(Command('delete_event'))
# async def delete_event(msg: Message, state: FSMContext):
#     await msg.answer('Введите название события, которое хотите удалить')
#     await state.update_data(operation_type='delete_event')
#     await state.set_state(DateOperations.choosing_date)


# @router.message(Command('create_rt'))
# async def start_create_event(msg: Message, state: FSMContext):
#     await msg.answer(
#         "Выберите дату для напоминания: ",
#         reply_markup=await SimpleCalendar(locale=await get_user_locale(msg.from_user)).start_calendar()
#     )
#     await state.update_data(operation_type='create_rt')
#     await state.set_state(DateOperations.choosing_date)


# @router.message(Command('delete_rt'))
# async def delete_event(msg: Message, state: FSMContext):
#     await msg.answer('Введите номер напоминание, которое хочешь удалить, оно указано в (скобочка) при выхове команды all')
#     await state.update_data(operation_type='delete_rt')
#     await state.set_state(DateOperations.choosing_rt_id)
 

# @router.message(DateOperations.choosing_date)
# @router.callback_query(SimpleCalendarCallback.filter())
# async def process_simple_calendar(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
#     calendar = SimpleCalendar(
#         locale=await get_user_locale(callback_query.from_user), show_alerts=True
#     )
#     actual_year = datetime.now().year
#     calendar.set_dates_range(datetime(actual_year - 1, 1, 1), datetime(actual_year + 3, 12, 31))
#     selected, date = await calendar.process_selection(callback_query, callback_data, callback_query.message.chat.id)
#     if selected:
#         data = await state.get_data()
#         date_ = date.strftime('%Y-%m-%d')
#         if data.get('operation_type') in ('create_rt', ):
#             await state.update_data(date_to_remaind=date_)    
#         else:
#             await state.update_data(date_start=date_)

#         await state.set_state(DateOperations.choosing_time)
#         await callback_query.message.answer(
#             f'Вы выбрали {date.strftime("%d-%m-%Y")}\nТеперь напишите время в формате часы:минуты'
#         )


# @router.message(DateOperations.choosing_time)
# async def choosing_event_time_start(msg: Message, state: FSMContext):
#     try:
#         time_start = validate_time(msg.text.lower())
#     except ValueError as error_message:
#         await msg.answer(str(error_message))
#     else:
#         data = await state.get_data()
#         if data.get('operation_type') in ('create_rt', ):
#             await state.update_data(time_to_remaind=time_start)    
#         else:
#             await state.update_data(time_start=time_start)

#         await msg.answer('Выберите вашу временную зону', reply_markup=timezone_kb)
#         await state.set_state(DateOperations.choosing_timezone)
    

# @router.message(DateOperations.choosing_timezone)
# async def choosing_event_timezone(msg: Message, state: FSMContext):
#     try:
#         timezone = msg.text.lower().replace('+', '')
#         tz = int(timezone)
#         if not(0 <= tz <= 12):
#             raise ValueError('Неверный тип временной зоны, временная зона должна быть в диапозоне от 0 до 12')
#     except ValueError as error_message:
#         await msg.answer(str(error_message))
#     else:
#         if len(timezone) == 1:
#             timezone = '0' + timezone
#         timezone = f'+{timezone}00'
#         await msg.answer(f'Временной сдвиг успешно установлен: {timezone}')
#         await state.update_data(chat_timezone=timezone)

#         data = await state.get_data()
#         text = 'Выберите название нового события'
#         op_type = data.get('operation_type')
#         if op_type in ['update_event']:
#             text = 'Выберите название события, которое хотите изменить'
#         elif op_type in ['create_rt']:
#             text = 'Выберите название события, к которому хотите создать напоминание'
#         await state.set_state(DateOperations.choosing_event_name)
#         await msg.answer(text)


# @router.message(DateOperations.choosing_rt_id)
# async def choosing_rt_id(msg: Message):
#     remainder_time_id = msg.text.lower()
    
#     try:
#         rt_id = int(remainder_time_id)
#         if rt_id <= 0:
#             ValueError('Не правильно')
#     except ValueError:
#         await msg.answer('Необходимо ввести число, целочисленно, то что указано в (скобках)')
#     else:
#         await delete_rt(remainder_time_id, msg)


# @router.message(DateOperations.choosing_event_name)
# async def choosing_event_name(msg: Message, state: FSMContext):
#     await state.update_data(event_name=msg.text.lower())
    
#     data = await state.get_data()
#     operation_type = data.get('operation_type')    
#     match operation_type:
#         case 'create_event':
#             await create_event(data, msg)
#         case 'update_event':
#             await update_event(data, msg)
#         case 'delete_event':
#             await delete_event(data, msg)
#         case 'create_rt':
#             await create_rt(data, msg)
#         case _:
#             await msg.answer('Что то пошло не так')

#     await state.clear()


@router.message()
async def stub_answer(msg: Message):
    await msg.answer('Не корректный запрос')

