import logging
import os

from requests_cache import install_cache

logger = logging.getLogger("fairproxy_api.cache")


def setup_cache() -> None:
    """
    Initializes requests-cache globally using environment variables.
    Supported backends:
      - 'memory': stores requests in RAM (default)
      - 'sqlite': stores requests in a local SQLite file (persistable)
      - 'sqlalchemy' / 'postgres' / 'postgresql': stores requests in PostgreSQL database
    """
    backend = os.getenv("REQUEST_CACHE_BACKEND", "memory").lower()
    connection = os.getenv("REQUEST_CACHE_CONNECTION")
    expire_after = int(os.getenv("REQUEST_CACHE_EXPIRE", "3600"))

    logger.info(f"Initializing requests-cache with backend: {backend}")

    if backend in ("sqlite", "sqlite3"):
        # Default SQLite path inside a directory that can be mounted/externalized
        cache_path = connection or "/app/cache/http_cache.sqlite"

        # Ensure the containing directory exists
        try:
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        except Exception as err:
            logger.warning(
                f"Could not create cache directory for {cache_path}: {err}. Defaulting to current directory."
            )
            cache_path = "http_cache.sqlite"

        install_cache(
            cache_name=cache_path,
            backend="sqlite",
            expire_after=expire_after,
        )
        logger.info(f"SQLite cache initialized at: {cache_path}")

    elif backend in ("sqlalchemy", "postgres", "postgresql"):
        if not connection:
            logger.error(
                "REQUEST_CACHE_CONNECTION is missing for 'sqlalchemy/postgres' backend! Defaulting to 'memory'."
            )
            install_cache(backend="memory", expire_after=expire_after)
            return

        install_cache(
            cache_name="http_cache",
            backend="sqlalchemy",
            connection=connection,
            expire_after=expire_after,
        )
        logger.info("SQLAlchemy/Postgres cache initialized.")

    else:
        # Default fallback: in-memory cache
        install_cache(
            cache_name="http_cache",
            backend="memory",
            expire_after=expire_after,
        )
        logger.info("In-memory cache initialized.")
