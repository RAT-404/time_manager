from aiogram.fsm.state import StatesGroup, State


class EventOperations(StatesGroup):
    select_event = State()
    
    change_event_name = State()
    change_event_date = State()
    change_event_time = State()
    

    choose_event = State()
    choose_date = State()
    choose_time = State()

    choosing_timezone = State()

    choosing_rt_id = State()

