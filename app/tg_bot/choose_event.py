import additional_functions
from schemas import EventCallback, EventAct
from additional_functions import get_events_on_month 
from common import GenericEvent

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from datetime import datetime


class EventChoose(GenericEvent):
    async def start_choose(
        self,
        chat_id = None,
        events = None
    ) -> InlineKeyboardMarkup:
        
        today = datetime.now()
        now_month, now_year = today.month, today.year

        if chat_id and not(events):
            events = await additional_functions.get_events_on_month(chat_id, now_year, now_month)

        kb = [[InlineKeyboardButton(
                text=event.get('event_name'),
                callback_data=EventCallback(act=EventAct.change_event,
                                            id=str(event.get('id'))).pack())] 
            for event in events.get('events')]


        cancel_row = [
            [InlineKeyboardButton(
                text=self._labels.cancel_caption, 
                callback_data=EventCallback(act=EventAct.append).pack()
            ),
            InlineKeyboardButton(
                text=self._labels.append_caption, 
                callback_data=EventCallback(act=EventAct.cancel).pack()
            )]
        ]
        kb += cancel_row
        return InlineKeyboardMarkup(row_width=1, inline_keyboard=kb)

    async def _update_events(self, query: CallbackQuery, with_date: datetime):
        chat_id = query.message.chat.id
        events = await get_events_on_month(chat_id, with_date.year, with_date.month)
        await query.message.edit_reply_markup(
            reply_markup=await self.start_calendar(int(with_date.year), int(with_date.month), chat_id=chat_id, events=events)
        )

    async def process_selection(self, query, data) -> tuple:

        return_data = (False, None)

        if data.act == EventAct.ignore:
            await query.answer(cache_time=60)
            return return_data

        if data.act == EventAct.append:
            print('append option selected')
            return return_data        

        if data.act == EventAct.change_event:
            print(data)
            return_data = (data, None)
            return return_data

        if data.act == EventAct.cancel:
            await query.message.delete_reply_markup()
        
        return return_data