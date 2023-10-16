import pickle #TODO: Pickle is unsafe

from flask_redis import FlaskRedis
from server import app

def create_redis():
    return FlaskRedis(app)

redis = create_redis()

def set(key: str, value, object=True):
    if object:
        value = pickle.dumps(value)

    redis.set(key, value)
    return

def get(key: str, object=True):
    value = redis.get(key)

    if object:
        value = pickle.loads(value)

    return value
