from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Configuración de base de datos
    DB_USER: str = Field(...)
    DB_PASSWORD: str = Field(default="")
    DB_HOST: str = Field(default="localhost")
    DB_PORT: int = Field(default=3306)
    DB_SCHEMA: str = Field(...)

    # Configuración del correo
    MAIL_HOST: str = Field(default="smtp.gmail.com")
    MAIL_PORT: int = Field(default=587)
    MAIL_USER: str = Field(...)
    MAIL_PASS: str = Field(...)

    class Config:
        env_file = ".env"

settings = Settings()

