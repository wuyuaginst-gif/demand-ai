from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""
    ollama_base_url: str = "http://host.docker.internal:11434"
    model_name: str = "qwen2.5:7b"
    embedding_model: str = "qwen2.5:7b"
    chroma_persist_dir: str = "/app/data/chroma_db"
    chroma_collection_name: str = "demands"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
