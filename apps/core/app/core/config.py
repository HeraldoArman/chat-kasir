from pathlib import Path

import yaml
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent.parent


class LLMConfig(BaseSettings):
    provider: str = "openai"
    model: str = "gpt-5.4-mini"
    base_url: str = "https://api.openai.com/v1"
    temperature: float = 0.3
    max_tokens: int = 4096
    timeout: int = 120


class Mem0Config(BaseSettings):
    persistence_enabled: bool = False
    limit: int = 10


class ServerConfig(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    workers: int = 1


class LoggingConfig(BaseSettings):
    level: str = "INFO"
    format: str = "json"


class JWTConfig(BaseSettings):
    model_config = SettingsConfigDict(populate_by_name=True)

    secret_key: str = Field(validation_alias="JWT_SECRET_KEY")
    algorithm: str = "HS256"
    expire_hours: int = 24

    @field_validator("secret_key", mode="after")
    @classmethod
    def _validate_secret_key(cls, value: str) -> str:
        if len(value.strip()) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters")
        return value


class CORSConfig(BaseSettings):
    model_config = SettingsConfigDict(populate_by_name=True)

    origins: list[str] = Field(default=["http://localhost:3001"], validation_alias="CORS_ORIGINS")

    @field_validator("origins", mode="before")
    @classmethod
    def _parse_origins(cls, value: object) -> list[str]:
        if isinstance(value, list):
            return [str(origin).strip() for origin in value if str(origin).strip()]
        if isinstance(value, str):
            if not value.strip():
                return ["http://localhost:3001"]
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return ["http://localhost:3001"]


class DatabaseConfig(BaseSettings):
    url: str = "postgresql+asyncpg://user:password@host/dbname"


class RAGConfig(BaseSettings):
    model_config = SettingsConfigDict(populate_by_name=True)

    enabled: bool = True
    qdrant_url: str = Field(default="http://localhost:6333", validation_alias="QDRANT_URL")
    qdrant_api_key: str = Field(default="", validation_alias="QDRANT_API_KEY")
    collection_name: str = "documents"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    chunk_size: int = 500
    chunk_overlap: int = 50


class GoWAConfig(BaseSettings):
    base_url: str = Field(default="http://localhost:8080", validation_alias="GOWA_BASE_URL")
    device_id: str = Field(default="", validation_alias="GOWA_DEVICE_ID")
    webhook_secret: str = Field(default="", validation_alias="GOWA_WEBHOOK_SECRET")


class AppConfig(BaseSettings):
    llm: LLMConfig = Field(default_factory=LLMConfig)
    mem0: Mem0Config = Field(default_factory=Mem0Config)
    server: ServerConfig = Field(default_factory=ServerConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    jwt: JWTConfig = Field(default_factory=JWTConfig)
    cors: CORSConfig = Field(default_factory=CORSConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    rag: RAGConfig = Field(default_factory=RAGConfig)
    gowa: GoWAConfig = Field(default_factory=GoWAConfig)


_config_cache: AppConfig | None = None


def get_config() -> AppConfig:
    global _config_cache
    if _config_cache is None:
        config_path = ROOT_DIR / "config.yaml"
        if config_path.exists():
            with open(config_path) as f:
                config_data = yaml.safe_load(f)
            _config_cache = AppConfig(**config_data)
        else:
            _config_cache = AppConfig()
    return _config_cache
