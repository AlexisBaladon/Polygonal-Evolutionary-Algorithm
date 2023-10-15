from flask_socketio import SocketIO

from server import app, config

def create_socket_app(development=False):
    if development:
        socketio = SocketIO(app, cors_allowed_origins="*")
    else:
        socketio = SocketIO(app, async_mode='threading')
    return socketio

socketio = create_socket_app(development=not config.production)

def emit(id: str, message: bytes = None):
    if message is not None:
        socketio.emit(id, message)
    else:
        socketio.emit(id)