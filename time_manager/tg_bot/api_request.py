import json
import aiohttp

from schemas import RemainderTime
from config import get_settings


class APIRequest:
    def __init__(self, chat_id: str = '', api_url: str = get_settings().API_URL, url_params: str = ''):
        self.api_url = f'{api_url}{url_params}' if not chat_id else f'{api_url}{chat_id}/{url_params}'
        
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
            
    async def update_rmt(self, rmt_id: str, rmt_data):
         async with aiohttp.ClientSession() as session:
            async with session.patch(url=f'{self.api_url}{rmt_id}', json=rmt_data) as resp:
                return resp.status

    
    