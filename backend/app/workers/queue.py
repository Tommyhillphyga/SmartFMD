from redis import Redis
from rq import Queue

from app.core.config import get_settings

settings = get_settings()
redis_connection = Redis.from_url(settings.redis_url)
notification_queue = Queue("smartfmd", connection=redis_connection)

