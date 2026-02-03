from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_VERSION: str
    GATEWAY_API_KEY: str
    GATEWAY_URL: str
    GATEWAY_JSON_REQUEST_ENDPOINT: str = "/gateway/request"
    GATEWAY_HTML_REQUEST_ENDPOINT: str = "/gateway/html"
    GATEWAY_SESSION_ID: str
    REQUEST_TIMEOUT: float = 30.0

    LOGS_LEVEL: str = "INFO"
    DEBUG_HTTP: bool

    TIMETABLE_PERIOD_IN_MONTH: float = 2.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # noqa


settings = get_settings()
