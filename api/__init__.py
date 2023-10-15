from flask import Flask

from api import config

def create_app(development=False):
    app = Flask(__name__, 
                template_folder='modules', 
                static_url_path='/static')
    
    app.config['DEBUG'] = development
    app.config['SECRET_KEY'] = 'secret'
    return app

app = create_app(development=not config.production)

from api import modules