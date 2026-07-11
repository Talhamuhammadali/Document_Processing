"""Shared synchronous Redis client factory built from application settings."""

import redis

from app.core.config import settings


def redis_client(decode_responses: bool = True) -> redis.Redis:
    """Return a Redis client configured from settings.

    Parameters
    ----------
    decode_responses : bool
        Whether string responses are decoded to str.

    Returns
    -------
    redis.Redis
        A configured Redis client.

    """
    return redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password,
        db=settings.redis_db,
        decode_responses=decode_responses,
    )
