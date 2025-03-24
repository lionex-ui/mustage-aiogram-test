from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        enable_decoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
