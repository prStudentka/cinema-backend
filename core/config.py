from typing import Literal

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    MODE: Literal["DEV", "TEST"]

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    SECRET_KEY: str
    JWT_ALGORYTHM: str
    JWT_EXPIRE_MINUTES: int

    S3_ENDPOINT: str
    S3_SECRET_KEY: str
    S3_ACCESS_KEY: str
    S3_SECURE: bool = False
    S3_BUCKET_NAME: str

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    DB_TEST_HOST: str
    DB_TEST_PORT: int
    DB_TEST_USER: str
    DB_TEST_PASS: str
    DB_TEST_NAME: str

    @property
    def TEST_DATABASE_URL(self):
        return (f"postgresql+asyncpg://{self.DB_TEST_USER}:{self.DB_TEST_PASS}@{self.DB_TEST_HOST}:"
                f"{self.DB_TEST_PORT}/{self.DB_TEST_NAME}")

    class Config:
        env_file = '.env'


config = Config()
