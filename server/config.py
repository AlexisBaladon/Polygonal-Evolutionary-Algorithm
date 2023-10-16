import os
import dotenv

dotenv.load_dotenv()

production = os.environ.get("PRODUCTION", True)
secret_key = os.environ.get("SECRET_KEY", "secret")
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")