"""Application settings, loaded from the environment with sane defaults."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Runtime configuration.

    Attributes
    ----------
    redis_host : str
        Redis Stack host.
    redis_port : int
        Redis Stack port.
    redis_password : str | None
        Redis Stack password, or None if the instance is unauthenticated.
    redis_db : int
        Redis logical database number.
    benchmark_dir : Path
        Directory holding the precomputed Docling mock JSON files.
    pdf_dir : Path
        Directory holding the source PDFs matched to the mocks.

    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str | None = None
    redis_db: int = 0

    benchmark_dir: Path = _ROOT / "benchmark" / "out"
    pdf_dir: Path = _ROOT / "data" / "tech_doc_examples"


settings = Settings()
