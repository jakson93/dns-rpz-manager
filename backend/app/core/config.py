from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/dns_rpz_manager"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # SMTP (optional)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: Optional[str] = None

    # Telegram (optional)
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None

    # Teams (optional)
    TEAMS_WEBHOOK_URL: Optional[str] = None

    # Bind RPZ
    BIND_RPZ_PATH: str = "/var/cache/bind/rpz.zone.db"
    BIND_CHECKZONE_PATH: str = "/usr/sbin/named-checkzone"
    RNDC_PATH: str = "/usr/sbin/rndc"
    RPZ_ZONE_NAME: str = "rpz"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
