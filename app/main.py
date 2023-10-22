from fastapi import FastAPI
import asyncio

from backend.internal.db import Base, SessionManager
from backend.routing.event_router import event_router


# Base.metadata.create_all(bind=SessionManager().engine)


app = FastAPI(title='time_manager')


@app.get('/')
async def main():
    return {'message': 'hello'}


app.include_router(event_router)


