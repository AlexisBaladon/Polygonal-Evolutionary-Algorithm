from flask import Flask

from server import config
from src.lib.deap_config import DeapConfig

def create_app(development=False):
    app = Flask(__name__, 
                template_folder='modules', 
                static_url_path='/static')
    
    app.config['DEBUG'] = development
    app.config['SECRET_KEY'] = config.secret_key
    app.config['CELERY_CONFIG'] = config.celery_config
    app.config['REDIS_URL'] = config.REDIS_URL
    return app

DeapConfig.register_fitness() #DEAP CONFIGURATION MUST BE OUTSIDE OF MAIN WHEN USING PARALLELISM
app = create_app(development=not config.production)

from server import modules