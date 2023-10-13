from flask import Blueprint

from api import app, socketio, router
from src.lib.deap_config import DeapConfig

DeapConfig.register_fitness() #DEAP CONFIGURATION MUST BE OUTSIDE OF MAIN WHEN USING PARALLELISM

main_blueprint = Blueprint('main', __name__)
router.register_blueprint(main_blueprint)

@app.route("/")
def index():
    return f"Hi :)"

if __name__ == "__main__":
    socketio.run(app, debug=True)

