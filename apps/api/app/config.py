"""Environment-driven configuration."""
from __future__ import annotations

from pathlib import Path
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    model_provider: str = "mock"
    model_name: str = "mock-extractor"
    max_retries: int = 2
    temperature: float = 0.0
    max_concurrency: int = 3
    database_url: str = "sqlite:///./data/app.db"
    upload_dir: str = "./storage/uploads"
    export_dir: str = "./storage/exports"
    backend_cors_origins: str = "http://localhost:3000"

    openai_api_key: str = ""
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-6"

    max_upload_bytes: int = 25 * 1024 * 1024
    allowed_upload_extensions: List[str] = Field(default_factory=lambda: [".xlsx", ".csv"])

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def _strip(cls, v: str | List[str]) -> str:
        if isinstance(v, list):
            return ",".join(str(x).strip() for x in v)
        return v

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.backend_cors_origins.split(",") if o.strip()]

    @property
    def upload_path(self) -> Path:
        return Path(self.upload_dir).resolve()

    @property
    def export_path(self) -> Path:
        return Path(self.export_dir).resolve()

    def ensure_dirs(self) -> None:
        self.upload_path.mkdir(parents=True, exist_ok=True)
        self.export_path.mkdir(parents=True, exist_ok=True)
        if self.database_url.startswith("sqlite:///"):
            db_file = Path(self.database_url.replace("sqlite:///", "")).resolve()
            db_file.parent.mkdir(parents=True, exist_ok=True)


settings = Settings()
