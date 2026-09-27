"""Application settings, loaded from environment / .env via pydantic-settings."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Repo root = three parents up from this file (src/specradar/config.py).
REPO_ROOT = Path(__file__).resolve().parents[2]
TAXONOMY_DIR = REPO_ROOT / "taxonomy"


class Settings(BaseSettings):
    """Typed settings. Secrets never carry defaults beyond empty strings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- LLM ---
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    llm_model: str = Field(default="claude-opus-4-8", alias="SPECRADAR_LLM_MODEL")

    # --- BigQuery ---
    google_cloud_project: str = Field(default="", alias="GOOGLE_CLOUD_PROJECT")
    bq_dataset: str = Field(default="specradar", alias="BQ_DATASET")
    gcp_sa_key_path: str = Field(default="", alias="GCP_SA_KEY_PATH")

    # --- Search ---
    search_api_key: str = Field(default="", alias="SEARCH_API_KEY")
    search_engine_id: str = Field(default="", alias="SEARCH_ENGINE_ID")

    # --- App ---
    env: str = Field(default="dev", alias="SPECRADAR_ENV")
    log_level: str = Field(default="INFO", alias="SPECRADAR_LOG_LEVEL")
    allow_playwright: bool = Field(default=False, alias="SPECRADAR_ALLOW_PLAYWRIGHT")

    taxonomy_dir: Path = TAXONOMY_DIR


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
