"""Flask SocketIO events"""
import logging
from flask_socketio import emit, SocketIO

socketio = SocketIO(logger=logging, engineio_logger=logging)


@socketio.on_error_default
def error_handler(e):
    """Handle socket errors."""
    logging.error("Socket error: %s", e)

@socketio.on("connect", namespace="/test")
def handle_connect():
    """Handle a client connection."""
    emit("response", {"data": "Connected"})

@socketio.on("disconnect")
def handle_disconnect():
    """Handle a client disconnection."""
    logging.info("Client disconnected")

@socketio.on("message")
def handle_message(message):
    """Handle a client message."""
    emit("response", {"data": message["data"]})

@socketio.on("json")
def handle_json(json):
    """Handle a client JSON message."""
    emit("response", json)
