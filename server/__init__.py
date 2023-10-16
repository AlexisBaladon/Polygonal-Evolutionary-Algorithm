from flask import Flask

from server import config

REDIS_URL = "redis://localhost:6379/0"

def create_app(development=False):
    app = Flask(__name__, 
                template_folder='modules', 
                static_url_path='/static')
    
    app.config['DEBUG'] = development
    app.config['SECRET_KEY'] = config.secret_key
    return app

app = create_app(development=not config.production)
app.config.from_mapping(
    CELERY=dict(
        broker_url=REDIS_URL,
        result_backend=REDIS_URL,
        task_ignore_result=True
    )
)

from server import modules