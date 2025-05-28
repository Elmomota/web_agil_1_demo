from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Configuración de base de datos
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str 
    DB_PORT: int
    DB_SCHEMA: str

    # Configuración del correo
    MAIL_HOST: str
    MAIL_PORT: int
    MAIL_USER: str
    MAIL_PASS: str

    class Config:
        env_file = ".env"

settings = Settings()

