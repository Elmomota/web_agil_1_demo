from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_SCHEMA: str
    MAIL_HOST: str
    MAIL_PORT: int
    MAIL_USER: str
    MAIL_PASS: str

    class Config:
        env_file = ".env"

settings = Settings()
