"""Application configuration module."""
from functools import lru_cache

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Runtime configuration for the backend service."""

    app_name: str = Field(default="LexSim Backend", env="APP_NAME")
    version: str = Field(default="0.1.0")
    llm_model_name: str = Field(default="lexsim-mini", env="LLM_MODEL_NAME")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Return a cached settings instance."""

    return Settings()


__all__ = ["Settings", "get_settings"]
