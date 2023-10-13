from api import socketio

def emit(id: str, message: bytes):
    socketio.emit(id, message)