"""Application settings and configuration."""

import os
import logging
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Loads from environment variables first (Docker, system env),
    then falls back to .env file if present (local development).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,  # Ignore if .env doesn't exist
        case_sensitive=False,
        extra="ignore",
    )

    # AWS Bedrock Credentials (Optional to allow graceful initialization)
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"

    @model_validator(mode='after')
    def validate_aws_credentials(self):
        """Validate AWS credentials after initialization."""
        if not self.aws_access_key_id or not self.aws_secret_access_key:
            logger.warning(
                "⚠️  AWS Bedrock credentials not configured. "
                "INDRA agent will not function. "
                "Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in environment or config.env"
            )
        else:
            logger.debug(f"AWS credentials configured for region: {self.aws_region}")
        return self

    # Optional API Keys
    iqair_api_key: Optional[str] = None
    writer_api_key: Optional[str] = None

    # Application Settings
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

    # INDRA Settings
    # Network Search API for entity grounding and resolution
    indra_base_url: str = "https://network.indra.bio"
    indra_timeout: int = 30
    indra_cache_ttl: int = 3600  # 1 hour

    # Agent Settings (AWS Bedrock Model ID)
    agent_model: str = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    agent_temperature: float = 0.0

    @property
    def is_iqair_configured(self) -> bool:
        """Check if IQAir API key is configured."""
        return self.iqair_api_key is not None and len(self.iqair_api_key) > 0

    @property
    def is_writer_configured(self) -> bool:
        """Check if Writer API key is configured."""
        return self.writer_api_key is not None and len(self.writer_api_key) > 0


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create settings instance.

    Returns:
        Settings: Application settings
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Reload settings from environment.

    Returns:
        Settings: Fresh settings instance
    """
    global _settings
    _settings = Settings()
    return _settings
