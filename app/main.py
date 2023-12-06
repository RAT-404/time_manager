from fastapi import FastAPI
from fastapi.responses import RedirectResponse

import asyncio
from contextlib import asynccontextmanager
from typing import Annotated

from backend.internal.db import Base, SessionManager
from backend.routing.event_router import event_router
from backend.internal.db.database import AsyncSession, get_async_session

from backend.internal.buisness_logic.time_remainder import start_timer


async def startup_timer():
    async_session_generate = get_async_session()
    async for i in async_session_generate:
        session = i
        break
    await start_timer(session)


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(startup_timer())
    yield


app = FastAPI(title='time_manager', lifespan=lifespan)


@app.get('/')
async def main():
    return RedirectResponse('/event')


app.include_router(event_router)


