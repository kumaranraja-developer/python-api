# app/config.py
from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = "your-secret"

    class Config:
        env_file = ".env"

settings = Settings()
