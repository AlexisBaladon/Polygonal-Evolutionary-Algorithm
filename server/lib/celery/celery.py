from server import app

from flask import Flask
from celery import Celery, Task

def celery_init_app(app: Flask, include=["server.lib.celery.tasks"]) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask, include=include)
    celery_app.config_from_object(app.config["CELERY_CONFIG"])
    app.extensions["celery"] = celery_app
    celery_app.conf.broker_url = app.config["REDIS_URL"]
    celery_app.set_default()
    return celery_app

celery = celery_init_app(app)
app.app_context().push()