from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, field_validator
from dotenv import load_dotenv
from functools import lru_cache


class Settings(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_USER : str
    POSTGRES_PASSWORD : str
    POSTGRES_PORT : int
    POSTGRES_HOST : str

    SQLALCHEMY_URL: PostgresDsn | None = None

    @field_validator('SQLALCHEMY_URL')
    @classmethod
    def get_sqlalchemy_url(cls, v, info):
        if isinstance(v, str):
            return v
        
        data = info.data
        return PostgresDsn.build(
            scheme='postgresql+asyncpg',
            host=data.get('POSTGRES_HOST'),
            username=data.get('POSTGRES_USER'),
            password=data.get('POSTGRES_PASSWORD'),
            port=int(data.get("POSTGRES_PORT")),
            path=f"{data.get('POSTGRES_DB')}"
        )
    

@lru_cache
def get_settings():
    load_dotenv()
    return Settings()


if __name__ == '__main__':
    print(str(get_settings().SQLALCHEMY_URL))