import calendar
from datetime import datetime, timedelta

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from aiogram_calendar import SimpleCalendar
from aiogram_calendar.schemas import SimpleCalendarCallback, highlight, superscript

import additional_functions
from schemas import SimpleCalAct, SimpleCalendarCallback


class SimpleCalendar(SimpleCalendar):

    async def start_calendar(
        self,
        year: int = datetime.now().year,
        month: int = datetime.now().month,
        chat_id = None,
        events = None,
        day_selection_act: str = SimpleCalAct.day
    ) -> InlineKeyboardMarkup:
        
        today = datetime.now()
        now_weekday = self._labels.days_of_week[today.weekday()]
        now_month, now_year, now_day = today.month, today.year, today.day

        if chat_id and not(events):
            events = await additional_functions.get_events_on_month(chat_id, now_year, now_month)  
        
        event_dates = await self._get_events_dates(events, now_year, now_month, now_day,)

        def highlight_month():
            month_str = self._labels.months[month - 1]
            if now_month == month and now_year == year:
                return highlight(month_str)
            return month_str

        def highlight_weekday():
            if now_month == month and now_year == year and now_weekday == weekday:
                return highlight(weekday)
            return weekday

        def format_day_string():
            date_to_check = datetime(year, month, day)
            if self.min_date and date_to_check < self.min_date:
                return superscript(str(day))
            elif self.max_date and date_to_check > self.max_date:
                return superscript(str(day))
            return str(day)

        def highlight_day():
            day_string = format_day_string()
            if day_string in event_dates:                
                return f'*{day_string}*'

            if now_month == month and now_year == year and now_day == day:
                return highlight(day_string)
            return day_string


        # building a calendar keyboard
        kb = []

        # inline_kb = InlineKeyboardMarkup(row_width=7)
        # First row - Year
        years_row = []
        years_row.append(InlineKeyboardButton(
            text="<<",
            callback_data=SimpleCalendarCallback(act=SimpleCalAct.prev_y, year=year, month=month, day=1).pack()
        ))
        years_row.append(InlineKeyboardButton(
            text=str(year) if year != now_year else highlight(year),
            callback_data=self.ignore_callback
        ))
        years_row.append(InlineKeyboardButton(
            text=">>",
            callback_data=SimpleCalendarCallback(act=SimpleCalAct.next_y, year=year, month=month, day=1).pack()
        ))
        kb.append(years_row)

        # Month nav Buttons
        month_row = []
        month_row.append(InlineKeyboardButton(
            text="<",
            callback_data=SimpleCalendarCallback(act=SimpleCalAct.prev_m, year=year, month=month, day=1).pack()
        ))
        month_row.append(InlineKeyboardButton(
            text=highlight_month(),
            callback_data=self.ignore_callback
        ))
        month_row.append(InlineKeyboardButton(
            text=">",
            callback_data=SimpleCalendarCallback(act=SimpleCalAct.next_m, year=year, month=month, day=1).pack()
        ))
        kb.append(month_row)

        # Week Days
        week_days_labels_row = []
        for weekday in self._labels.days_of_week:
            week_days_labels_row.append(
                InlineKeyboardButton(text=highlight_weekday(), callback_data=self.ignore_callback)
            )
        kb.append(week_days_labels_row)

        # Calendar rows - Days of month
        month_calendar = calendar.monthcalendar(year, month)
        
        if not(day_selection_act):
            day_selection_act = SimpleCalAct.day
        
        for week in month_calendar:
            days_row = []
            for day in week:
                if day == 0:
                    days_row.append(InlineKeyboardButton(text=" ", callback_data=self.ignore_callback))
                    continue
                
                days_row.append(InlineKeyboardButton(
                    text=highlight_day(),
                    callback_data=SimpleCalendarCallback(act=day_selection_act, year=year, month=month, day=day).pack()
                ))
            kb.append(days_row)

        # nav today & cancel button
        cancel_row = [InlineKeyboardButton(
            text='Отмена',
            callback_data=SimpleCalendarCallback(act=SimpleCalAct.cancel, year=year, month=month, day=day).pack()
        )]

        kb.append(cancel_row)        
        return InlineKeyboardMarkup(row_width=7, inline_keyboard=kb)

    async def _update_calendar(self, query: CallbackQuery, with_date: datetime):
        chat_id = query.message.chat.id
        events = await additional_functions.get_events_on_month(chat_id, with_date.year, with_date.month)
        await query.message.edit_reply_markup(
            reply_markup=await self.start_calendar(int(with_date.year), int(with_date.month), chat_id=chat_id, events=events)
        )
    
    async def _get_events_dates(self, events, now_year, now_month, now_day) -> list[str]: 
        event_dates = []
        if events:
            events = events.get('events')
            for event in events:
                event_date = datetime.strptime(event.get('date_start'), '%Y-%m-%d')
                if (event_date.month == now_month and event_date.day >= now_day) or (event_date.month > now_month and event_date.year >= now_year):
                    event_dates.append(str(event_date.day))

        return event_dates

    async def process_selection(self, query, data) -> tuple:        
        return_data = (False, None)

        # processing empty buttons, answering with no action
        if data.act == SimpleCalAct.ignore:
            await query.answer(cache_time=60)
            return return_data

        temp_date = datetime(int(data.year), int(data.month), 1)

        # user picked a day button, return date
        if data.act in (SimpleCalAct.day, SimpleCalAct.select_new_event_date, SimpleCalAct.append_new_event_date):
            return_data = await self.process_day_select(data, query)
            return return_data

        # user navigates to previous year, editing message with new calendar
        if data.act == SimpleCalAct.prev_y:
            prev_date = datetime(int(data.year) - 1, int(data.month), 1)
            await self._update_calendar(query, prev_date)
        # user navigates to next year, editing message with new calendar
        if data.act == SimpleCalAct.next_y:
            next_date = datetime(int(data.year) + 1, int(data.month), 1)
            await self._update_calendar(query, next_date)
        # user navigates to previous month, editing message with new calendar
        if data.act == SimpleCalAct.prev_m:
            prev_date = temp_date - timedelta(days=1)
            await self._update_calendar(query, prev_date)
        # user navigates to next month, editing message with new calendar
        if data.act == SimpleCalAct.next_m:
            next_date = temp_date + timedelta(days=31)
            await self._update_calendar(query, next_date)
        if data.act == SimpleCalAct.cancel:
            await query.message.delete_reply_markup()
        # at some point user clicks DAY button, returning date
        return return_data