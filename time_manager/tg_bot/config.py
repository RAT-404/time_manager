from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str
    API_PORT: int
    API_URL: str


def get_settings():
    return Settings()