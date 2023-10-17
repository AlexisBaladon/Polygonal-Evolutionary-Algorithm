import json

from flask_redis import FlaskRedis
from server import app

def create_broker():
    return FlaskRedis(app)

broker = create_broker()

def set(key: str, value, object=True):
    if object:
        value = json.dumps(value)

    broker.set(key, value)
    return

def get(key: str, object=True):
    value = broker.get(key)

    if object and value is not None:
        value = json.loads(value)

    return value

def get_added_image_key(user_id: str, i: int):
    return f"added_image/{user_id}/{i}"

def get_last_connection_key(user_id: str):
    return f"last_connection/{user_id}"