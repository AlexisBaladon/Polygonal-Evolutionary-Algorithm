import os
import dotenv

dotenv.load_dotenv()

production = os.environ.get("PRODUCTION", False)
secret_key = os.environ.get("SECRET_KEY", "secret")