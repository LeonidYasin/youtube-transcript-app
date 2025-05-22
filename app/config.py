"""
Application configuration settings.
"""

import os
from pathlib import Path
from typing import List, Optional, Union
from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "YouTube Transcript API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS settings
    CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = ["*"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/youtube_transcript.log"
    
    # Application settings
    DEFAULT_LANGUAGE: str = "ru"
    FALLBACK_LANGUAGE: str = "en"
    
    # Create logs directory if it doesn't exist
    @property
    def LOG_DIR(self) -> Path:
        log_file_path = Path(self.LOG_FILE)
        log_dir = log_file_path.parent.absolute()
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir
    
    # Pydantic v2 config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# Create settings instance
settings = Settings()
