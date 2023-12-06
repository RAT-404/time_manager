from datetime import datetime
from handlers import Message


def validate_datetime(date_: str, time_: str):
    time_format = '%H:%M:%S%z'
    date_format = '%Y-%m-%d'

    time_format = time_ if time_ == '.' else time_format
    date_format = date_ if date_ == '.' else date_format

    time_ += '+0300' if time_ != '.' else ''

    datetime_format = f'{date_format}T{time_format}'

    try:
        datetime.strptime(f'{date_}T{time_}', datetime_format)
    except ValueError as e:
        raise TypeError(f'Неправильный формат дата или времени: {e}')

    return date_, time_

def validate_remainder_time_args(params: list[str]):
    if len(params) == 3:
        _, date_to_remaind, time_to_remaind, *_ = params
        date_to_remaind, time_to_remaind = validate_datetime(date_to_remaind, time_to_remaind)
    
    else:
        raise TypeError('не корректное количество аргументов для создания события (должно быть 3)')
    return {
            'date_to_remaind': date_to_remaind,
            'time_to_remaind': time_to_remaind,
        }

def validate_event_args(params: list[str]):
    if len(params) >= 3:
        event_name, date_start, time_start, *datetime_end = params
        date_start, time_start = validate_datetime(date_start, time_start)
        

        date_end, time_end = validate_datetime(*datetime_end) if len(datetime_end) == 2 else (None, None)        

    else:
        raise TypeError('не корректное количество аргументов для создания события (должно быть 3-5)')
    return {
            'event_name': event_name,
            'date_start': date_start,
            'time_start': time_start,
            'date_end': date_end,
            'time_end': time_end
        }


async def check_status_code(status_code: int, msg: Message, answer: str):
    if status_code in (200, ):
        await msg.answer(answer)
    else:
        await msg.answer('что то пошло не так, попробуйте еще раз, возможно ошибка на стороне сервера')
