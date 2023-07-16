from redis import Redis
from redis.asyncio import Redis as AsyncRedis

from src.conf.config import settings


def get_redis_client():
    redis_client = Redis(host=settings.redis_host, port=settings.redis_port, db=0)
    return redis_client


async def get_async_redis_client():
    async_redis_client = await AsyncRedis(host=settings.redis_host, port=settings.redis_port, db=0)
    return async_redis_client

