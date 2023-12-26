# run.py
from app import create_app
from app.socket_events import socketio

app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True)
