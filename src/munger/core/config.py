"""Application configuration."""

from pathlib import Path
from typing import Literal

from platformdirs import user_data_dir
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_prefix="MUNGER_",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # Data storage
    data_dir: Path = Field(
        default_factory=lambda: Path(user_data_dir("munger", "munger")),
        description="Directory for storing all application data",
    )

    # Database
    db_name: str = Field(default="munger.db", description="SQLite database filename")

    # Vector store
    vector_store_name: str = Field(
        default="munger_wisdom", description="ChromaDB collection name"
    )
    embedding_model: str = Field(
        default="all-MiniLM-L6-v2", description="Sentence transformer model for embeddings"
    )

    # LLM settings
    llm_provider: Literal["openai", "anthropic", "kimi", "siliconflow"] = Field(
        default="openai", description="LLM provider to use"
    )
    openai_api_key: str | None = Field(default=None, description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o", description="OpenAI model to use")
    anthropic_api_key: str | None = Field(default=None, description="Anthropic API key")
    anthropic_model: str = Field(
        default="claude-sonnet-4-20250514", description="Anthropic model to use"
    )
    kimi_api_key: str | None = Field(default=None, description="Kimi (Moonshot AI) API key")
    kimi_model: str = Field(default="kimi-k2-turbo-preview", description="Kimi model to use")
    siliconflow_api_key: str | None = Field(default=None, description="SiliconFlow API key")
    siliconflow_model: str = Field(default="deepseek-ai/DeepSeek-V3", description="SiliconFlow model to use")

    # Language settings
    language: Literal["english", "chinese"] = Field(
        default="english", description="Output language (english or chinese)"
    )

    # Retrieval settings
    retrieval_top_k: int = Field(
        default=5, description="Number of documents to retrieve for RAG"
    )

    @property
    def db_path(self) -> Path:
        """Full path to SQLite database."""
        return self.data_dir / self.db_name

    @property
    def vector_store_path(self) -> Path:
        """Full path to ChromaDB storage."""
        return self.data_dir / "chroma"

    def ensure_data_dir(self) -> None:
        """Create data directory if it doesn't exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
