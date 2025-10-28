"""Configuration management module."""

import os
from pathlib import Path


class Config:
    """Centralized configuration management."""

    # Telegram configuration
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHANNEL_ID: str = os.getenv("TELEGRAM_CHANNEL_ID", "")

    # AI translation configuration
    ENABLE_AI_TRANSLATION: bool = os.getenv("ENABLE_AI_TRANSLATION", "false").lower() == "true"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    TRANSLATION_TARGET_LANG: str = os.getenv("TRANSLATION_TARGET_LANG", "Chinese")

    # Bot behavior configuration
    CHECK_INTERVAL: int = int(os.getenv("CHECK_INTERVAL", "3600"))  # seconds

    # Storage configuration
    DATA_DIR: str = os.getenv("DATA_DIR", "data")
    ARCHIVE_DIR: str = os.getenv("ARCHIVE_DIR", f"{DATA_DIR}/archive")

    # Message formatting constants
    MAX_ABSTRACT_LENGTH_WITH_IMAGE: int = 500
    MAX_ABSTRACT_LENGTH_WITHOUT_IMAGE: int = 1000
    MAX_MESSAGE_LENGTH_WITH_IMAGE: int = 1000  # Telegram caption limit
    MAX_MESSAGE_LENGTH_WITHOUT_IMAGE: int = 4000  # Telegram message limit

    # Request delays and limits
    REQUEST_DELAY: float = 0.5  # seconds between requests
    SEND_DELAY: int = 2  # seconds between sending messages

    # Display limits
    MAX_AUTHORS_DISPLAY: int = 5

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration."""
        if not cls.TELEGRAM_BOT_TOKEN or cls.TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
            raise ValueError("TELEGRAM_BOT_TOKEN must be set")
        if not cls.TELEGRAM_CHANNEL_ID or cls.TELEGRAM_CHANNEL_ID == "@your_channel":
            raise ValueError("TELEGRAM_CHANNEL_ID must be set")

        if cls.ENABLE_AI_TRANSLATION and not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY must be set when AI translation is enabled")

    @classmethod
    def get_data_dir(cls) -> Path:
        """Get data directory as Path object."""
        return Path(cls.DATA_DIR)

    @classmethod
    def get_archive_dir(cls) -> Path:
        """Get archive directory as Path object."""
        return Path(cls.ARCHIVE_DIR)
