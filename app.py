from server import app, router, config

from server.lib.celery.celery import celery
from server.lib.broker import broker

router.initialize()

if __name__ == "__main__":
    assert not config.production, "This file should not be executed in production"
    app.run(host="0.0.0.0:5000", debug=True)