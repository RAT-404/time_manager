from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    BOT_TOKEN: str
    API_URL: str


def get_settings():
    return Settings()