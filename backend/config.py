from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./taskflow.db"
    JWT_SECRET_KEY: str = "dev-secret"
    JWT_ALGORITHM: str = "HS256"
    CORS_ORIGINS: str = "http://localhost:8000,http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]


settings = Settings()
