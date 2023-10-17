from server import app, router, config

from server.lib.celery.celery import celery
from server.lib.broker import broker

from src.lib.deap_config import DeapConfig

router.initialize()