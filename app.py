from server import app, config
from server.lib import cors
from server.modules.transform import transform_controller

from server.lib.sockets import socketio
from src.lib.deap_config import DeapConfig

DeapConfig.register_fitness() #DEAP CONFIGURATION MUST BE OUTSIDE OF MAIN WHEN USING PARALLELISM
cors.declare_cors_policy(app)

if __name__ == "__main__":
    production = config.production
    port = 5000 # TODO: Get from env
    host = "0.0.0.0"

    if production:
        socketio.run(app, host=host, port=port, debug=False)
    else:
        socketio.run(app, host=host, port=port, debug=True)

