from aiogram.fsm.state import StatesGroup, State


class DateOperations(StatesGroup):
    choosing_event_name = State()
    choosing_date = State()
    choosing_time = State()
    choosing_timezone = State()

    choosing_rt_id = State()

