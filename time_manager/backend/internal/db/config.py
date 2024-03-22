from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, field_validator, RedisDsn
from functools import lru_cache

    
class Settings(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_USER : str
    POSTGRES_PASSWORD : str
    POSTGRES_PORT : int
    POSTGRES_HOST : str

    REDIS_PORT : int
    REDIS_HOST : str

    BOT_TOKEN : str
    API_URL : str

    SQLALCHEMY_URL: PostgresDsn | None = None
    REDIS_URL: RedisDsn | None = None

    @field_validator('SQLALCHEMY_URL')
    def get_sqlalchemy_url(cls, v, data):
        if isinstance(v, str):
            return v

        data = data.data
        return PostgresDsn.build(
            scheme='postgresql+asyncpg',
            host=data.get('POSTGRES_HOST'),
            username=data.get('POSTGRES_USER'),
            password=data.get('POSTGRES_PASSWORD'),
            port=data.get("POSTGRES_PORT"),
            path=f"{data.get('POSTGRES_DB')}"
        )
    
    @field_validator('REDIS_URL')
    def get_redis_url(cls, v, data):
        if isinstance(v, str):
            return v
        
        data = data.data
        return RedisDsn.build(
            scheme='redis',
            host=data.get('REDIS_HOST'),
            port=data.get('REDIS_PORT'),
        )


@lru_cache
def get_settings():
    return Settings()


if __name__ == '__main__':
    print(str(get_settings().SQLALCHEMY_URL))
    print(str(get_settings().REDIS_URL))