from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[2]
TAXONOMY_DIR = REPO_ROOT / "taxonomy"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    llm_model: str = Field(default="claude-opus-4-8", alias="SPECRADAR_LLM_MODEL")

    search_api_key: str = Field(default="", alias="SEARCH_API_KEY")
    search_engine_id: str = Field(default="", alias="SEARCH_ENGINE_ID")

    env: str = Field(default="dev", alias="SPECRADAR_ENV")
    log_level: str = Field(default="INFO", alias="SPECRADAR_LOG_LEVEL")

    taxonomy_dir: Path = TAXONOMY_DIR


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
