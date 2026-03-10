from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Cleaning Schedule Generator API"
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/cleaning_schedule"
    default_cleaning_duration_minutes: int = 120
    default_open_window_hours: int = 24

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
