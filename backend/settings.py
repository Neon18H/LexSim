"""Application configuration utilities for LexSim backend."""
from functools import lru_cache
from typing import List

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, BaseSettings, Field, validator


load_dotenv()


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    openrouter_api_key: str = Field(..., env="OPENROUTER_API_KEY")
    openrouter_base_url: AnyHttpUrl = Field(
        "https://openrouter.ai/api/v1/chat/completions",
        env="OPENROUTER_BASE_URL",
    )
    openrouter_model: str = Field(
        "mistralai/mistral-7b-instruct:free", env="OPENROUTER_MODEL"
    )
    openrouter_fallbacks: List[str] = Field(
        default_factory=lambda: [
            "Qwen/Qwen2.5-7B-Instruct:free",
            "google/gemma-2-9b-it:free",
            "meta-llama/llama-3.1-8b-instruct:free",
        ],
        env="OPENROUTER_FALLBACKS",
    )
    host: str = Field("0.0.0.0", env="HOST")
    port: int = Field(8000, env="PORT")
    cors_origins: List[AnyHttpUrl] = Field(
        default_factory=lambda: ["http://localhost:8080"], env="CORS_ORIGINS"
    )
    temperature: float = Field(0.7, env="TEMPERATURE")
    max_tokens: int = Field(3000, env="MAX_TOKENS")
    rate_limit_per_minute: int = Field(30, env="RATE_LIMIT_PER_MINUTE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("openrouter_fallbacks", pre=True)
    def split_fallbacks(cls, value):  # type: ignore[override]
        """Allow comma separated fallbacks from environment variables."""

        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @validator("cors_origins", pre=True)
    def split_cors(cls, value):  # type: ignore[override]
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings()


__all__ = ["Settings", "get_settings"]
