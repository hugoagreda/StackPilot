from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Rental Price Estimator API"
    app_env: str = "dev"
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/rental_estimator"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
