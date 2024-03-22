from aiogram.fsm.state import StatesGroup, State


class EventOperations(StatesGroup):
    select_event = State()
    
    change_event_name = State()
    change_event_date = State()
    change_event_time = State()
    
    append_event_name = State()
    append_event_date = State()
    append_event_time = State()



class RemainderTimeOperations(StatesGroup):
    select_rmt = State()

    change_rmt_date = State()
    change_rmt_time = State()

    append_rmt_date = State()
    append_rmt_time = State()

