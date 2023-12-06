from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from functools import lru_cache


class Settings(BaseSettings):
    BOT_TOKEN: str
    API_URL: str


@lru_cache
def get_settings():
    load_dotenv()
    return Settings()