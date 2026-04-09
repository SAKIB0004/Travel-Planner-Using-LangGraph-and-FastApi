from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="Travel Planner API", alias="APP_NAME")
    app_env: Literal["dev", "test", "prod"] = Field(default="dev", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    groq_model: str = Field(default="openai/gpt-oss-20b", alias="GROQ_MODEL")
    use_mock_llm: bool = Field(default=True, alias="USE_MOCK_LLM")
    use_mock_weather: bool = Field(default=True, alias="USE_MOCK_WEATHER")

    open_meteo_base_url: str = Field(default="https://api.open-meteo.com/v1/forecast", alias="OPEN_METEO_BASE_URL")
    default_session_ttl_minutes: int = Field(default=120, alias="DEFAULT_SESSION_TTL_MINUTES")

    search_provider: str = Field(default="duckduckgo", alias="SEARCH_PROVIDER")
    enable_wikipedia_tool: bool = Field(default=True, alias="ENABLE_WIKIPEDIA_TOOL")
    enable_search_tool: bool = Field(default=True, alias="ENABLE_SEARCH_TOOL")

    streamlit_api_url: str = Field(default="http://localhost:8000/api/v1/travel/plan", alias="STREAMLIT_API_URL")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
