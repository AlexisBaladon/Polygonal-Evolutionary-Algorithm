from api import socketio

def emit(id: str, message: bytes = None):
    if message is not None:
        socketio.emit(id, message)
    else:
        socketio.emit(id)