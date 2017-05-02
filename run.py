from flask import Flask
from flask_socketio import SocketIO
from config import Config as config

app = Flask(__name__)
socketio = SocketIO(app)

@socketio.on('authenticate')
def handle_authenticate(API_KEY):
    print('received API_KEY: ' + API_KEY)

if __name__ == '__main__':
    socketio.run(app)
