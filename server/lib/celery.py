from server import REDIS_URL

from celery import Celery

def create_celery(broker_url=REDIS_URL):
    return Celery(__name__, broker=broker_url, backend=broker_url)

celery = create_celery()