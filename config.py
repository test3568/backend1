from typing import Tuple, Type

from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource, SettingsConfigDict
)


class Settings(BaseSettings):
    def __init__(self):
        super().__init__()

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    DJANGO_SECRET_KEY: str
    DJANGO_DEBUG: bool

    POSTGIS_HOST: str
    POSTGIS_USER: str
    POSTGIS_PASSWORD: str
    POSTGIS_PORT: int

    REDIS_HOST: str
    REDIS_PORT: int

    AMQP_HOST: str
    AMQP_PORT: int
    AMQP_USER: str
    AMQP_PASSWORD: str

    KAFKA_HOST: str
    KAFKA_PORT: int

    GDAL_LIBRARY_PATH: str | None = None
    GEOS_LIBRARY_PATH: str | None = None

    KAFKA_CONSUMER_TOPIC: str
    KAFKA_PRODUCER_TOPIC: str

    CORS_ORIGIN_WHITELIST: list[str]
    CSRF_TRUSTED_ORIGINS: list[str]

    DJANGO_LOG_LEVEL: str
    APP_LOG_LEVEL: str

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            env_settings,
            dotenv_settings
        )

Config = Settings()
