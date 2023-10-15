from fastapi import FastAPI

from backend.internal.db import engine, Base
from backend.routing.event_router import event_router


Base.metadata.create_all(bind=engine)

app = FastAPI(title='time_manager')


@app.get('/')
def main():
    return {'message': 'hello'}


app.include_router(event_router)