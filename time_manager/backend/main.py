import asyncio
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from routing.event_router import event_router
from internal.db import database, config
from internal.buisness_logic import time_remainder


async def startup_timer():
    async_session_generate = database.get_async_session()
    async for session in async_session_generate:
        session = session
        break
    
    await time_remainder.start_timer(session)


app = FastAPI(title='time_manager')


@app.on_event("startup")
async def startup():
    redis = aioredis.from_url(str(config.get_settings().REDIS_URL), encoding='utf-8', decode_response=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    asyncio.create_task(startup_timer())
    

@app.get('/')
async def main():
    return RedirectResponse('/event')


app.include_router(event_router)








