import json
import aiohttp
from schemas import RemainderTime
from config import get_settings


class APIRequest:
    def __init__(self, chat_id: str = '', api_url: str = get_settings().API_URL, url_params: str = ''):
        self.api_url = f'{api_url}{url_params}' if not chat_id else f'{api_url}{chat_id}/{url_params}'
        
    async def get_events(self):
        api_json, status_code = await self.get_events_json()
        return (self.__parse_json_to_pretty_str(api_json), status_code)
    
    async def get_events_json(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_url) as response:
                status_code = response.status
                resp = await response.text()
                api_json = json.loads(resp)
                return (api_json, status_code)
            
    async def create_event(self, event_data):
        async with aiohttp.ClientSession() as session:
            async with session.post(url=self.api_url, json=event_data) as resp:
                return resp.status
            
    async def delete_event(self, event_id: str):
        async with aiohttp.ClientSession() as session:
            async with session.delete(url=f'{self.api_url}{event_id}') as resp:
                return resp.status
    
    async def update_event(self, event_id: str, data):
        async with aiohttp.ClientSession() as session:
            async with session.patch(url=f'{self.api_url}{event_id}', json=data) as resp:
                return resp.status
    
    async def create_remainder_times(self, remainder_times: list[RemainderTime]):
        async with aiohttp.ClientSession() as session:
            async with session.post(url=self.api_url, json=remainder_times) as resp:
                return resp.status
    
    async def delete_remainder_times(self, remainder_time_id: int):
        async with aiohttp.ClientSession() as session:
            async with session.delete(url=f'{self.api_url}{remainder_time_id}') as resp:
                return resp.status

    def __parse_json_to_pretty_str(self,
                                   api_json: str,
                                   parse_remainder_times: bool = True) -> str:        
        finally_str = ''
        events: list[dict] = api_json.get('events', False)
        if events:
            for event in events:
                event_date, event_time = event.get('date_start'), event.get('time_start')
                event_name = event.get('event_name')

                if parse_remainder_times:
                    remainder_times = event.get('remainder_times', [])
                    if remainder_times == []:
                        remainder_times = '\n----У данного события нет напоминаний'
                    else:
                        remainder_times = [f"\n----{rm.get('date_to_remaind')} {rm.get('time_to_remaind').split('+')[0]} ({rm.get('id')})" for rm in remainder_times]
                        remainder_times = ''.join(remainder_times)
                else:
                    remainder_times = ''
                event_time = event_time.split('+', 1)[0]
                finally_str += f'{event_name} {event_date} {event_time}{remainder_times}\n'
                
        return finally_str  