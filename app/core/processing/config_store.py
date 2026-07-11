"""Seed and read processing-config presets in Redis."""

from pathlib import Path

import redis

from app.core.processing.types import ProcessingConfig

_PREFIX = "procconfig:"


def seed_configs(client: redis.Redis, configs_dir: Path) -> list[str]:
    """Load every preset JSON in configs_dir into Redis, overwriting existing keys.

    Parameters
    ----------
    client : redis.Redis
        A Redis client.
    configs_dir : Path
        Directory of preset JSON files; each file stem becomes a mode name.

    Returns
    -------
    list[str]
        The seeded mode names.

    """
    names: list[str] = []
    for path in sorted(configs_dir.glob("*.json")):
        config = ProcessingConfig.model_validate_json(path.read_text())
        client.set(f"{_PREFIX}{path.stem}", config.model_dump_json())
        names.append(path.stem)
    return names


def load_config(client: redis.Redis, mode: str) -> ProcessingConfig:
    """Read a preset from Redis by mode name.

    Parameters
    ----------
    client : redis.Redis
        A Redis client with decode_responses enabled.
    mode : str
        The preset name, for example fast or accurate.

    Returns
    -------
    ProcessingConfig
        The stored preset.

    Raises
    ------
    KeyError
        If no preset is stored for the given mode.

    """
    raw = client.get(f"{_PREFIX}{mode}")
    if raw is None:
        raise KeyError(f"Unknown processing mode: {mode}")
    return ProcessingConfig.model_validate_json(raw)
