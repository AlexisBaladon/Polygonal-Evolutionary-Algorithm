from flask_cors import CORS

def declare_cors_policy(app):
    CORS(app, resources={r"/socket.io/*": {"origins": "*"}})