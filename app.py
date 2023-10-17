from server import app, router, config

#from server.lib.sockets import socketio
from server.lib.celery.celery import celery
from server.lib.broker import broker

from src.lib.deap_config import DeapConfig

router.initialize()

if __name__ == "__main__":
    production = config.production
    port = 5000 # TODO: Get from env
    host = "0.0.0.0"

    # if production:
    #     socketio.run(app, host=host, port=port, debug=False)
    # else:
    #     socketio.run(app, host=host, port=port, debug=True)

