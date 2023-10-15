from flask import Flask

from server import config

def create_app(development=False):
    app = Flask(__name__, 
                template_folder='modules', 
                static_url_path='/static')
    
    app.config['DEBUG'] = development
    app.config['SECRET_KEY'] = config.secret_key
    return app

app = create_app(development=not config.production)

from server import modules