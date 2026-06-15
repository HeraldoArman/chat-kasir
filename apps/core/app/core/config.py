from pathlib import Path

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings

ROOT_DIR = Path(__file__).resolve().parent.parent.parent


class LLMConfig(BaseSettings):
    provider: str = "deepinfra"
    model: str = "deepseek-ai/DeepSeek-V4-Flash"
    base_url: str = "https://api.deepinfra.com/v1/openai"
    temperature: float = 0.7
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


class GoogleOAuthConfig(BaseSettings):
    client_id: str = Field(default="", validation_alias="GOOGLE_OAUTH_CLIENT_ID")
    client_secret: str = Field(default="", validation_alias="GOOGLE_OAUTH_CLIENT_SECRET")
    redirect_uri: str = Field(default="", validation_alias="GOOGLE_OAUTH_REDIRECT_URI")


class JWTConfig(BaseSettings):
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    expire_hours: int = 24


class DatabaseConfig(BaseSettings):
    url: str = "postgresql+asyncpg://user:password@host/dbname"


class RAGConfig(BaseSettings):
    enabled: bool = False
    qdrant_url: str = Field(default="", validation_alias="QDRANT_URL")
    qdrant_api_key: str = Field(default="", validation_alias="QDRANT_API_KEY")
    collection_name: str = "documents"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    chunk_size: int = 500
    chunk_overlap: int = 50


class AppConfig(BaseSettings):
    llm: LLMConfig = Field(default_factory=LLMConfig)
    mem0: Mem0Config = Field(default_factory=Mem0Config)
    server: ServerConfig = Field(default_factory=ServerConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    jwt: JWTConfig = Field(default_factory=JWTConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    google_oauth: GoogleOAuthConfig = Field(default_factory=GoogleOAuthConfig)
    rag: RAGConfig = Field(default_factory=RAGConfig)


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
