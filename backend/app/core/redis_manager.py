import redis.asyncio as redis
from app.core.config import get_settings
from app.core.logger import log
from typing import Callable, Any, Dict
import json

settings = get_settings()

class RedisManager:
    """
    Singleton Redis pub/sub manager for event-driven agent communication.
    Agents publish events, other agents subscribe and react.
    """

    def __init__(self):
        self.redis: redis.Redis | None = None
        self.pubsub = None

    async def connect(self):
        """Connect to Redis."""
        try:
            self.redis = await redis.from_url(settings.redis_url)
            await self.redis.ping()
            log.info("Redis connected")
        except Exception as e:
            log.error("Redis connection failed", error=str(e))
            raise

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
            log.info("Redis disconnected")

    async def publish(self, channel: str, data: Dict[str, Any]) -> None:
        """
        Publish an event to a Redis channel.
        data is automatically JSON-encoded.
        """
        if not self.redis:
            log.warning("Redis not connected, event not published")
            return

        message = json.dumps(data)
        await self.redis.publish(channel, message)
        log.info("Event published", channel=channel, data=data)

    async def subscribe(self, channel: str, callback: Callable) -> None:
        """
        Subscribe to a Redis channel and call callback on each message.
        callback(data: dict) is called with the decoded JSON.
        """
        if not self.redis:
            log.warning("Redis not connected, cannot subscribe")
            return

        pubsub = self.redis.pubsub()
        await pubsub.subscribe(channel)

        log.info("Agent subscribed", channel=channel)

        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        await callback(data)
                    except json.JSONDecodeError:
                        log.error("Failed to decode message", message=message)
        except Exception as e:
            log.error("Subscription error", channel=channel, error=str(e))
        finally:
            await pubsub.close()


# Global instance
redis_manager = RedisManager()