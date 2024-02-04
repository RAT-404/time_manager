from aiogram.types import CallbackQuery

from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

from auxiliary_functions import *
from schemas import *
from api_request import *
from states import *
from common import GenericEvent

from enum import Enum
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery

from aiogram_calendar.schemas import SimpleCalendarCallback, SimpleCalAct, highlight, superscript

import calendar
from datetime import datetime, timedelta


class EventAct(str, Enum):
    ignore = 'IGNORE'
    change_event = 'CHANGE_EVENT'
    append = 'APPEND'
    cancel = 'CANCEL'


class EventChoose(GenericEvent):
    async def start_choose(
        self,
        year: int = datetime.now().year,
        month: int = datetime.now().month,
        chat_id = None,
        events = None
    ) -> InlineKeyboardMarkup:
        
        today = datetime.now()
        now_month, now_year, now_day = today.month, today.year, today.day

        if chat_id and not(events):
            events = await get_events_on_month(chat_id, now_year, now_month)

        kb = [[InlineKeyboardButton(
                text=event.get('event_name'),
                callback_data=EventCallback(act=EventAct.change_event,
                                            date_start=event.get('date_start'), 
                                            id=str(event.get('id'))).pack())] 
            for event in events.get('events')]


        # cancel_row = [
        #     InlineKeyboardButton(
        #         text=self._labels.cancel_caption, 
        #         callback_data=EventCallback(act=EventAct.cancel, date_start='', id='').pack()
        #     ),
        #     InlineKeyboardButton(
        #         text=self._labels.append_caption, 
        #         callback_data=EventCallback(act=EventAct.append, date_start='', id='').pack()
        #     )
        # ]
        # kb += cancel_row
        return InlineKeyboardMarkup(row_width=1, inline_keyboard=kb)

    async def _update_events(self, query: CallbackQuery, with_date: datetime):
        chat_id = query.message.chat.id
        events = await get_events_on_month(chat_id, with_date.year, with_date.month)
        await query.message.edit_reply_markup(
            reply_markup=await self.start_calendar(int(with_date.year), int(with_date.month), chat_id=chat_id, events=events)
        )

    async def process_selection(self, args: dict) -> tuple:
        query = args.get('callback_query')
        data = args.get('callback_data')

        event_on_month = args.get('calendar_events_dates')
        actual_datetime = args.get('actual_datetime')
        year, month, day = actual_datetime.year, actual_datetime.month, actual_datetime.day
        
        return_data = (False, None)

        if data.act == SimpleCalAct.ignore:
            await query.answer(cache_time=60)
            return return_data

        if data.act == SimpleCalAct.append:
            print('YES YES YES')
            return return_data        

        if data.act == SimpleCalAct.cancel:
            await query.message.delete_reply_markup()
        
        return return_data