from api import app, socketio, router
from src.lib.deap_config import DeapConfig

DeapConfig.register_fitness() #DEAP CONFIGURATION MUST BE OUTSIDE OF MAIN WHEN USING PARALLELISM

router.initialize()

if __name__ == "__main__":
    socketio.run(app, debug=True)

