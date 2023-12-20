"""Flask SocketIO events"""
import logging
from flask_socketio import emit, SocketIO
from flask import current_app as app
from app.models.service.service import Service

socketio = SocketIO(logger=logging, engineio_logger=logging)


##### SocketIO events #####
@socketio.on_error_default
def error_handler(e):
    """Handle socket errors."""
    logging.error("Socket error: %s", e)

@socketio.on("connect")
def handle_connect():
    """Handle a client connection."""
    emit("response", {"data": "Connected"})

@socketio.on("disconnect")
def handle_disconnect():
    """Handle a client disconnection."""
    logging.info("Client disconnected")

##### Service events #####
@socketio.on("get_logs", namespace="/service")
def handle_get_logs(service_id):
    """Handle a client request for service logs."""
    logging.info("Client requested logs for service %s", service_id)
    service = Service.query.get(service_id)
    if service and service.docker_container_id:
        try:    
            for log_line in app.docker_manager.stream_container_logs(service):
                emit("log_message", {"log": log_line, "service_id": service_id})
        except Exception as e:
            logging.error("Error streaming logs: %s", e)
            emit("log_message", {"log": "Error streaming logs"})
    else:
        logging.error("Service %s not found", service_id)
        emit("log_message", {"log": "Service not found"})

##### SocketIO test events #####
@socketio.on("message", namespace="/test")
def handle_message(message):
    """Handle a client message."""
    emit("response", {"data": message["data"]})

@socketio.on("json", namespace="/test")
def handle_json(json):
    """Handle a client JSON message."""
    emit("response", json)
