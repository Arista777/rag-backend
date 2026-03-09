from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"


class Settings(BaseSettings):
    app_name: str = "RAG Assistant API"
    app_env: str = "development"
    app_debug: bool = True
    api_v1_prefix: str = "/api/v1"

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_chat_model: str = Field(default="gpt-4o-mini", alias="OPENAI_CHAT_MODEL")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small", alias="OPENAI_EMBEDDING_MODEL"
    )

    allowed_origins: str = Field(default="http://localhost:3000", alias="ALLOWED_ORIGINS")

    sqlite_path: Path = Field(default=DATA_DIR / "assistant.db", alias="SQLITE_PATH")
    vector_index_path: Path = Field(default=DATA_DIR / "vector.index", alias="VECTOR_INDEX_PATH")
    vector_meta_path: Path = Field(default=DATA_DIR / "vector_meta.json", alias="VECTOR_META_PATH")
    upload_dir: Path = Field(default=DATA_DIR / "uploads", alias="UPLOAD_DIR")

    retrieval_k: int = Field(default=6, alias="RETRIEVAL_K")
    max_chunk_size: int = Field(default=800, alias="MAX_CHUNK_SIZE")
    chunk_overlap: int = Field(default=120, alias="CHUNK_OVERLAP")
    max_upload_mb: int = Field(default=10, alias="MAX_UPLOAD_MB")
    max_chunks_per_upload: int = Field(default=400, alias="MAX_CHUNKS_PER_UPLOAD")
    embedding_batch_size: int = Field(default=32, alias="EMBEDDING_BATCH_SIZE")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    return settings
