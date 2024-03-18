from datetime import datetime

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext

from additional_functions import (
    update_event, 
    get_events_on_month, 
    delete_event, 
    get_local_datetime_start, 
    get_utc_datetime, 
    create_event,
    get_remainder_times_for_event,
    update_remainder_time,
    delete_rmt,
    create_remainder_time,
    get_user_locale
    )

from schemas import EventAct, EventCallback, SimpleCalendarCallback, SimpleCalAct, RemainderAct, RemainderCallback
from api_request import APIRequest
from states import EventOperations, RemainderTimeOperations
from modifaed_calendar import SimpleCalendar


router = Router()


cancel_rmt_kb = InlineKeyboardMarkup(row_width=1, inline_keyboard=[[InlineKeyboardButton(text='Отмена', callback_data=RemainderCallback(act=RemainderAct.cancel).pack())]]) 
cancel_event_kb = InlineKeyboardMarkup(row_width=1, inline_keyboard=[[InlineKeyboardButton(text='Отмена', callback_data=EventCallback(act=EventAct.cancel).pack())]])
 

@router.message(Command('cancel'))
async def cancel_operation(msg: Message, state: FSMContext):
    await state.clear()
    await view_all_events(msg, state)

@router.message(Command('start'))
async def get_all_events(msg: Message, state: FSMContext):
    await msg.answer('Привет, рад, что ты решил воспользоваться моим time manager`ом, основная команда - /all')
    await view_all_events(msg, state)


@router.message(Command('all'))
async def view_all_events(msg: Message | CallbackQuery, state: FSMContext):
    calendar = SimpleCalendar(locale=await get_user_locale(msg.from_user))

    if isinstance(msg, CallbackQuery):
        msg = msg.message
    await msg.answer(
        'События: ',
        reply_markup=await calendar.start_calendar(chat_id=msg.chat.id)
    )


@router.callback_query(SimpleCalendarCallback.filter(F.act != SimpleCalAct.select_new_event_date), 
                       SimpleCalendarCallback.filter(F.act != SimpleCalAct.select_rm_date),
                       SimpleCalendarCallback.filter(F.act != SimpleCalAct.select_new_rm_date))
async def process_event_calendar(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    calendar = SimpleCalendar(
        locale=await get_user_locale(callback_query.from_user), show_alerts=True
    )
    actual_datetime = datetime.now()
    actual_year, actual_month = actual_datetime.year, actual_datetime.month
    calendar.set_dates_range(datetime(actual_year - 1, 1, 1), datetime(actual_year + 3, 12, 31))

    
    selected, date = await calendar.process_selection(callback_query, callback_data)
    
    if selected:
        events_on_month = await get_events_on_month(callback_query.message.chat.id, date.year, date.month)

        kb = [[InlineKeyboardButton(
                    text=event.get('event_name'),
                    callback_data=EventCallback(act=EventAct.change_event,
                                                id=str(event.get('id'))).pack())] 
                for event in events_on_month.get('events') 
                if datetime.strptime(get_local_datetime_start(event.get('date_start'), event.get('time_start'))[0], 
                                     '%Y-%m-%d').day == date.day]


        cancel_row = [
                [InlineKeyboardButton(
                    text='Добавить', 
                    callback_data=EventCallback(act=EventAct.append).pack()
                ),
                InlineKeyboardButton(
                    text='Отмена', 
                    callback_data=EventCallback(act=EventAct.cancel).pack()
                )]
            ]
        kb += cancel_row
        kb = InlineKeyboardMarkup(row_width=1, inline_keyboard=kb)

    
        await state.update_data(date_start=str(date.date()))
        await callback_query.message.edit_reply_markup(
            str(callback_query.message.message_id),
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
        event_id, event_name, date_start, time_start_utc = str(event.get('id')), event.get('event_name'), event.get('date_start'), event.get('time_start')
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
                    callback_data=EventCallback(act=EventAct.change_event_name, id=event_id).pack()
                )],
                [InlineKeyboardButton(
                    text=date_start, 
                    callback_data=EventCallback(act=EventAct.change_event_date, id=event_id).pack()
                )],
                [InlineKeyboardButton(
                    text=time_start, 
                    callback_data=EventCallback(act=EventAct.change_event_time, id=event_id).pack()
                )],
                [InlineKeyboardButton(
                    text='Напоминания', 
                    callback_data=RemainderCallback(act=RemainderAct.select_rm, event_id=event_id).pack()
                )],
                [
                    InlineKeyboardButton(
                        text='Удалить', 
                        callback_data=EventCallback(act=EventAct.delete, id=event_id).pack()
                    ),
                    InlineKeyboardButton(
                        text='Отмена', 
                        callback_data=EventCallback(act=EventAct.cancel, id=event_id).pack()
                    )
                ]
            ]
            
            kb = InlineKeyboardMarkup(row_width=1, inline_keyboard=kb)
            
            await callback_query.message.edit_text(
                'Событие: ',
                inline_message_id=str(callback_query.message.message_id),
                reply_markup=kb
            )    


#change event name
@router.callback_query(EventCallback.filter(F.act==EventAct.change_event_name))
async def change_event_name_callback(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    await state.set_state(EventOperations.change_event_name)
    await callback_query.message.edit_text('Введите новое название события: ',
                                           inline_message_id=str(callback_query.message.message_id),
                                           reply_markup=cancel_event_kb)


@router.message(EventOperations.change_event_name)
async def change_event_name(msg: Message, state: FSMContext):
    data = (await state.get_data()).get('event_data')
    data['event_name'] = msg.text.lower()

    try:
        utc_date, utc_time = get_utc_datetime(data.get('date_start'), data.get('time_start'))
        data['date_start'] = utc_date
        data['time_start'] = utc_time
        print(data)
        await update_event(data, msg)
    except Exception as e:
        await msg.answer(text='Что то пошло не так')
    else:
        await state.clear()
        await msg.answer("Название события обновлена")
    finally:
        await view_all_events(msg, state)


#change event date
@router.callback_query(EventCallback.filter(F.act==EventAct.change_event_date))
async def change_event_date_callback(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    await state.set_state(EventOperations.change_event_date)
    msg = callback_query.message
    calendar = SimpleCalendar(locale=await get_user_locale(callback_query.from_user))
    await msg.edit_text(
        "Выберите новую дату: ",
        inline_message_id=str(msg.message_id),
        reply_markup=await calendar.start_calendar(chat_id=msg.chat.id, day_selection_act=SimpleCalAct.select_new_event_date)
    )


@router.callback_query(SimpleCalendarCallback.filter(F.act == SimpleCalAct.select_new_event_date))
async def change_event_date(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    data = (await state.get_data()).get('event_data')
    msg = callback_query.message

    day_selection_act = SimpleCalAct.select_new_event_date

    try:
        calendar = SimpleCalendar(
            locale=await get_user_locale(callback_query.from_user), show_alerts=True
        )

        actual_datetime = datetime.now()
        actual_year = actual_datetime.year
        calendar.set_dates_range(datetime(actual_year - 1, 1, 1), datetime(actual_year + 3, 12, 31))
        
        selected, date = await calendar.process_selection(callback_query, callback_data, day_selection_act)

        if selected:
            new_event_date = str(date.date())
            utc_date, utc_time = get_utc_datetime(new_event_date, data.get('time_start'))
            data['date_start'] = utc_date
            data['time_start'] = utc_time
            await update_event(data, msg)
            
    except (TypeError, ValueError) as e:
        await msg.answer(text='Что то пошло не так, возможно ошибка на стороне сервера')
    else:
        await state.clear()
        await callback_query.message.answer("Дата события обновлена")
    finally:
        await view_all_events(callback_query, state)


#delete event
@router.callback_query(EventCallback.filter(F.act==EventAct.delete))
async def delete_event_callback(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    event_id = (await state.get_data()).get('event_data').get('event_id')
    await delete_event(event_id, callback_query.message)
    await state.clear()
    await callback_query.message.edit_text('Событие успешно удалено', inline_message_id=str(callback_query.message.message_id))
    await view_all_events(callback_query, state)


#change event time
@router.callback_query(EventCallback.filter(F.act==EventAct.change_event_time))
async def change_event_time_callback(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    await state.set_state(EventOperations.change_event_time)
    await callback_query.message.edit_text('Напишите новое время для события в формате ЧАСЫ:МИНУТЫ (например 15:32): ',
                                           inline_message_id=str(callback_query.message.message_id),
                                           reply_markup=cancel_event_kb)


@router.message(EventOperations.change_event_time)
async def change_event_time(msg: Message, state: FSMContext):
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
        await state.clear()
        await msg.answer('Время события обновлено')
    finally:
        await view_all_events(msg, state)
    

# create new event
@router.callback_query(EventCallback.filter(F.act==EventAct.append))
async def append_event_callback(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    await state.set_state(EventOperations.append_event_name)
    await callback_query.message.answer('Напишите название нового события: \nДля отмены операции введите /cancel')


@router.message(EventOperations.append_event_name)
async def append_event_name(msg: Message, state: FSMContext):
    await state.update_data(event_name=msg.text.lower())
    await state.set_state(EventOperations.append_event_time)
    await msg.answer('Напишите новое время для события в формате ЧАСЫ:МИНУТЫ (например 15:32): \nДля отмены операции введите /cancel')
    

@router.message(EventOperations.append_event_time)
async def append_event_time(msg: Message, state: FSMContext):
    data = await state.get_data()
    event_date = data.get('date_start')
    event_time = msg.text.lower() + ':00'
    
    try:
        print(event_date, event_time)
        utc_date, utc_time = get_utc_datetime(event_date, event_time)
        data['date_start'] = utc_date
        data['time_start'] = utc_time  
        
        await create_event(data, msg)    
    except ValueError:
        await msg.answer('Время написано в неправильном формате, попробуйте еще раз')
    else:
        await state.clear()
        await msg.answer('Событие создано успешно')
    finally:
        await view_all_events(msg, state)













# start rmt selection ( calendar with rmt for current event )
@router.callback_query(RemainderCallback.filter(F.act==RemainderAct.select_rm))
async def view_all_rmt(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    msg = callback_query.message
    event_id = callback_data.event_id
    
    calendar = SimpleCalendar(locale=await get_user_locale(callback_query.from_user))

    await state.update_data(event_id=event_id)
    await msg.edit_text(
        'Напоминания: ',
        inline_message_id=str(msg.message_id),
        reply_markup=await calendar.start_calendar(chat_id=msg.chat.id, day_selection_act=SimpleCalAct.select_rm_date, event_id=event_id)
    )


# select date for rmt for current event
@router.callback_query(SimpleCalendarCallback.filter(F.act == SimpleCalAct.select_rm_date))
async def select_rmt_date_callback(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    calendar = SimpleCalendar(
        locale=await get_user_locale(callback_query.from_user), show_alerts=True
    )
    actual_datetime = datetime.now()
    actual_year, actual_month = actual_datetime.year, actual_datetime.month
    calendar.set_dates_range(datetime(actual_year - 1, 1, 1), datetime(actual_year + 3, 12, 31))
    
    day_selection_act = SimpleCalAct.select_rm_date
    selected, date = await calendar.process_selection(callback_query, callback_data, day_selection_act)
    
    rmt_by_event = await get_remainder_times_for_event(callback_query.message.chat.id, callback_data.event_id)
    
    if selected:
        kb = [[InlineKeyboardButton(text=get_local_datetime_start(rmt.get('date_to_remaind'), rmt.get('time_to_remaind'))[1],
                                    callback_data=RemainderCallback(act=RemainderAct.change_rm, event_id=str(rmt.get('event_id')), id=str(rmt.get('id'))).pack())]

                for rmt in rmt_by_event.get('remainder_times') if datetime.strptime(get_local_datetime_start(rmt.get('date_to_remaind'), rmt.get('time_to_remaind'))[0],
                                                                                     '%Y-%m-%d').day == date.day
            ]


        cancel_row = [
                [InlineKeyboardButton(
                    text='Добавить', 
                    callback_data=RemainderCallback(act=RemainderAct.append).pack()
                ),
                InlineKeyboardButton(
                    text='Отмена', 
                    callback_data=RemainderCallback(act=RemainderAct.cancel).pack()
                )]
            ]
        kb += cancel_row
        kb = InlineKeyboardMarkup(row_width=1, inline_keyboard=kb)

        await state.update_data(date_to_remaind=str(date.date()))
        await callback_query.message.edit_text(
            'Напоминания: ',
            inline_message_id=str(callback_query.message.message_id),
            reply_markup=kb
        )


# show full info about current rmt
@router.callback_query(RemainderCallback.filter(F.act == RemainderAct.change_rm))
async def process_select_rmt(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    event_id = str(callback_data.event_id)
    rmt_id = callback_data.id
    rmt, status_code = await APIRequest(url_params=f'get-remainder-time/{rmt_id}').get_events_json()
    
    try:
        rmt = rmt.get('remainder_time')[0]
    except (IndexError, TypeError):
        await callback_query.message.answer('Напоминание не обнаружено, возможно оно было удалено ранее')
    else:
        date_to_remaind, time_to_remaind = rmt.get('date_to_remaind'), rmt.get('time_to_remaind')
        date_to_remaind, time_to_remaind = get_local_datetime_start(date_to_remaind, time_to_remaind)

        rmt_data = {
            'id': rmt_id,
            'event_id': event_id,
            'date_to_remaind': date_to_remaind, 
            'time_to_remaind': time_to_remaind
        }

        time_to_remaind = time_to_remaind.split('+')[0]
        
        try:
            date_to_remaind = datetime.strftime(datetime.strptime(date_to_remaind, '%Y-%m-%d'), '%d-%m-%Y')
        except ValueError:
            await callback_query.message.answer('Что то пошло не так, попробуйте еще раз')
        else:
            await state.update_data(rmt_data=rmt_data)
            
            kb = [
                [InlineKeyboardButton(
                    text=date_to_remaind, 
                    callback_data=RemainderCallback(act=RemainderAct.change_rm_date, id=str(rmt_id), event_id=event_id).pack()
                )],
                [InlineKeyboardButton(
                    text=time_to_remaind, 
                    callback_data=RemainderCallback(act=RemainderAct.change_rm_time, id=str(rmt_id), event_id=event_id).pack()
                )],
                [
                    InlineKeyboardButton(
                        text='Удалить', 
                        callback_data=RemainderCallback(act=RemainderAct.delete, id=str(rmt_id), event_id=event_id).pack()
                    ),
                    InlineKeyboardButton(
                        text='Отмена', 
                        callback_data=RemainderCallback(act=RemainderAct.cancel, id=str(rmt_id), event_id=event_id).pack()
                    )
                ]
            ]
            
            kb = InlineKeyboardMarkup(row_width=1, inline_keyboard=kb)
            
            await callback_query.message.edit_text(
                'Напоминание: ',
                inline_message_id=str(callback_query.message.message_id),
                reply_markup=kb
            )    


# delete rmt
@router.callback_query(RemainderCallback.filter(F.act==RemainderAct.delete))
async def delete_rmt_callback(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    await delete_rmt(int(callback_data.id), callback_query.message)
    await state.clear()
    await callback_query.message.answer('Напоминание успешно удалено')
    await view_all_events(callback_query, state)


# change rmt time
@router.callback_query(RemainderCallback.filter(F.act==RemainderAct.change_rm_time))
async def change_event_time_callback(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    await state.set_state(RemainderTimeOperations.change_rmt_time)
    await callback_query.message.edit_text('Напишите новое время для события в формате ЧАСЫ:МИНУТЫ (например 15:32): ',
                                           inline_message_id=str(callback_query.message.message_id),
                                           reply_markup=cancel_rmt_kb)


@router.message(RemainderTimeOperations.change_rmt_time)
async def change_event_time(msg: Message, state: FSMContext):
    data = (await state.get_data()).get('rmt_data')
    rmt_date = data.get('date_to_remaind')
    rmt_time = msg.text.lower() + ':00'

    try:
        utc_date, utc_time = get_utc_datetime(rmt_date, rmt_time)
        data['date_to_remaind'] = utc_date
        data['time_to_remaind'] = utc_time
        await update_remainder_time(data, msg)
    except ValueError:
        await msg.answer('Время написано в неправильном формате, попробуйте еще раз')
    except AttributeError:
        await msg.answer('Не корректный поряд выполнения запросов')
    else:
        await state.clear()
        await msg.answer('Время напоминаня обновлено')
    finally:
        await view_all_events(msg, state)


# change rmt date
@router.callback_query(RemainderCallback.filter(F.act==RemainderAct.change_rm_date))
async def change_rmt_date_callback(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    await state.set_state(RemainderTimeOperations.change_rmt_date)
    msg = callback_query.message
    event_id = callback_data.event_id
    calendar = SimpleCalendar(locale=await get_user_locale(callback_query.from_user))
    await msg.edit_text(
        "Выберите новую дату: ",
        inline_message_id=str(msg.message_id),
        reply_markup=await calendar.start_calendar(chat_id=msg.chat.id, day_selection_act=SimpleCalAct.select_new_rm_date, event_id=event_id)
    )


@router.callback_query(SimpleCalendarCallback.filter(F.act == SimpleCalAct.select_new_rm_date))
async def change_event_date(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    rmt_data = (await state.get_data()).get('rmt_data')
    day_selection_act = SimpleCalAct.select_new_rm_date

    try:
        calendar = SimpleCalendar(
            locale=await get_user_locale(callback_query.from_user), show_alerts=True
        )
        actual_datetime = datetime.now()
        actual_year = actual_datetime.year
        calendar.set_dates_range(datetime(actual_year - 1, 1, 1), datetime(actual_year + 3, 12, 31))
        
        selected, date = await calendar.process_selection(callback_query, callback_data, day_selection_act)

        if selected:
            new_event_date = str(date.date())
            utc_date, utc_time = get_utc_datetime(new_event_date, rmt_data.get('time_to_remaind'))
            rmt_data['date_to_remaind'] = utc_date
            rmt_data['time_to_remaind'] = utc_time
            await update_remainder_time(rmt_data, callback_query.message)
            
    except Exception as e:
        await callback_query.message.answer(text='Что то пошло не так, возможно ошибка на стороне сервера')
    else:
        await state.clear()
        await callback_query.message.answer("Дата напоминания обновлена")
    finally:
        await view_all_events(callback_query, state)
        

# create new rmt
@router.callback_query(RemainderCallback.filter(F.act==RemainderAct.append))
async def append_rmt_callback(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    await state.set_state(RemainderTimeOperations.append_rmt_time)
    await callback_query.message.edit_text('Напишите новое время для напоминания в формате ЧАСЫ:МИНУТЫ (например 15:32): \nДля отмены операции введите /cancel')


@router.message(RemainderTimeOperations.append_rmt_time)
async def append_rmt_time(msg: Message, state: FSMContext):
    data = await state.get_data()
    rmt_date = data.get('date_to_remaind')
    rmt_time = msg.text.lower() + ':00'
    
    try:
        utc_date, utc_time = get_utc_datetime(rmt_date, rmt_time)
        data['date_to_remaind'] = utc_date
        data['time_to_remaind'] = utc_time
    
        await create_remainder_time(data, msg)    
    except ValueError:
        await msg.answer('Время написано в неправильном формате, попробуйте еще раз')
    else:
        await state.clear()
        await msg.answer('Напоминание создано успешно')
    finally:
        await view_all_events(msg, state)


#cancel choose event
@router.callback_query(EventCallback.filter(F.act == EventAct.cancel))
async def cancel_choosing_event(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    await cancel_choose(callback_query, callback_data, state)
    
    
#cancel choose rmt
@router.callback_query(RemainderCallback.filter(F.act == RemainderAct.cancel))
async def cancel_choosing_rmt(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    await cancel_choose(callback_query, callback_data, state)


async def cancel_choose(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    await state.clear()
    calendar = SimpleCalendar(locale=await get_user_locale(callback_query.from_user))
    
    msg = callback_query.message
    await msg.edit_text(
        'События: ',
        inline_message_id=str(msg.message_id),
        reply_markup=await calendar.start_calendar(chat_id=msg.chat.id)
    )


@router.message()
async def stub_answer(msg: Message):
    await msg.answer('Не корректный запрос')

