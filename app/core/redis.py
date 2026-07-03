import redis.asyncio as aioredis
from app.core.config import settings
from app.utils.logger import logger

# Global Redis client instance
redis_client: aioredis.Redis | None = None

async def init_redis_client() -> None:
    """Initialize Redis connection pool."""
    global redis_client
    try:
        logger.info(f"Initializing Redis client at {settings.REDIS_URL}...")
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_timeout=5.0, # Fail fast on connection timeout
        )
        # Ping connection to verify it is active
        await redis_client.ping()
        logger.info("✅ Redis client connected successfully.")
    except Exception as e:
        logger.error(f"❌ Failed to connect to Redis at {settings.REDIS_URL}: {e}")
        # Keep client as None, system will fallback to in-memory mode
        redis_client = None

async def close_redis_client() -> None:
    """Close Redis client connection pool."""
    global redis_client
    if redis_client:
        try:
            logger.info("Closing Redis client...")
            await redis_client.aclose()
            logger.info("✅ Redis client closed.")
        except Exception as e:
            logger.error(f"Error closing Redis client: {e}")
        finally:
            redis_client = None

async def get_redis() -> aioredis.Redis | None:
    """Safe getter for redis client."""
    return redis_client
