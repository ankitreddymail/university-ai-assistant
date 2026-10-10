"""Configuration settings for University AI Assistant.

Reads configuration from environment variables or uses safe defaults.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root directory (two levels up from this file)
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # Model configuration
    model_name: str = "qwen2.5:7b"
    ollama_base_url: str = "http://localhost:11434"
    embedding_model_name: str = "all-MiniLM-L6-v2"

    # Persistent storage paths
    sqlite_db_path: str = str(BASE_DIR / "data" / "students" / "university.db")
    chroma_persist_dir: str = str(BASE_DIR / "data" / "chroma")
    documents_dir: str = str(BASE_DIR / "data" / "documents")

    # API configuration
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    backend_url: str = "http://127.0.0.1:8000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Cached singleton settings instance
settings = Settings()
