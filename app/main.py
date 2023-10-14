from fastapi import FastAPI

from backend.internal.db import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title='time_manager')


@app.get('/')
def main():
    return {'message': 'hello'}