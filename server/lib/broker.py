import pickle #TODO: Pickle is unsafe

from flask_redis import FlaskRedis
from server import app

def create_broker():
    return FlaskRedis(app)

broker = create_broker()

def set(key: str, value, object=True, broker=broker):
    if object:
        value = pickle.dumps(value)

    broker.set(key, value)
    return

def get(key: str, object=True, broker=broker):
    value = broker.get(key)

    if object and value is not None:
        value = pickle.loads(value)

    return value