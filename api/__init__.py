from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__, 
            template_folder='modules', 
            static_url_path='/static')
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app, async_mode="threading")

from api import modules