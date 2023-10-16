import os
import dotenv

dotenv.load_dotenv()

production = os.environ.get("PRODUCTION", True)
secret_key = os.environ.get("SECRET_KEY", "secret")
REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379")
celery_config = {
    "broker_url": REDIS_URL,
    "result_backend": REDIS_URL,
}