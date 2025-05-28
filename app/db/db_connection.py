import mysql.connector
from app.core.config import settings

def get_connection():
    return mysql.connector.connect(
        host=settings.DB_HOST,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        port=settings.DB_PORT,
        database=settings.DB_SCHEMA
    )
