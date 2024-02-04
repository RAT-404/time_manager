from fastapi import FastAPI
from fastapi.responses import RedirectResponse

import asyncio
from contextlib import asynccontextmanager

from routing.event_router import event_router
from internal.db import database

from internal.buisness_logic import time_remainder


async def startup_timer():
    async_session_generate = database.get_async_session()
    async for i in async_session_generate:
        session = i
        break
    await time_remainder.start_timer(session)


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(startup_timer())
    yield


app = FastAPI(title='time_manager', lifespan=lifespan)


@app.get('/')
async def main():
    return RedirectResponse('/event')


app.include_router(event_router)


