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
    pdf_dir : Path
        Root directory scanned recursively for selectable sample PDFs.
    configs_dir : Path
        Directory holding the processing-config presets seeded into Redis.
    pdf_store_dir : Path
        Shared directory where source PDFs are written for the worker to read.
        Kept outside pdf_dir so the store is never scanned as a sample source.

    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str | None = None
    redis_db: int = 0

    pdf_dir: Path = _ROOT / "data"
    configs_dir: Path = _ROOT / "configs"
    pdf_store_dir: Path = _ROOT / ".pdf_store"


settings = Settings()
