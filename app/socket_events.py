"""Flask SocketIO events"""
import functools
import logging
from flask_socketio import emit, SocketIO, disconnect
from flask_login import current_user
from flask import current_app as app
from app.models.service.service import Service

socketio = SocketIO()
logger = logging.getLogger(__name__)

# Streaming status for each service
streaming_status = {}

def set_streaming_status(service_id, status):
    streaming_status[service_id] = status

def get_streaming_status(service_id):
    return streaming_status.get(service_id, False)


##### SocketIO Auth #####
def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)

    return wrapped


@socketio.on_error_default
def error_handler(e):
    """Handle socket errors."""
    logger.error("Socket error: %s", e)


@socketio.on("connect")
def handle_connect():
    """Handle a client connection."""
    if current_user.is_authenticated:
        logger.info("Client connected as %s", current_user.username)
        emit(
            "connect_response",
            {"data": f"Connected as {current_user.username}"},
        )
    else:
        logger.info("Client connection refused for unauthenticated user")
        emit(
            "connect_response",
            {"data": "Connection refused. You must be logged in to connect."},
        )
        disconnect()
        return False


@socketio.on("disconnect")
def handle_disconnect():
    """Handle a client disconnection."""
    logger.info("Client disconnected")
    disconnect()


##### Service events #####
@socketio.on("get_logs", namespace="/service")
@authenticated_only
def handle_get_logs(data):
    """Handle a client request for service logs."""
    service_id = int(data.get("serviceId"))
    command = data.get("command")
    logger.info("Client requested to %s streaming logs for service %s", command, service_id)
    service = Service.query.get(service_id)
    if command == "start":
        set_streaming_status(service_id, True)
        if service and service.docker_container_id:
            try:
                for log_line in app.docker_manager.stream_container_logs(service):
                    if not get_streaming_status(service_id):
                        break
                    emit("log_message", {"service_id": service_id, "log": log_line})
            except Exception as e:
                logger.error("Error streaming logs: %s", e)
                emit(
                    "get_logs_failed",
                    {
                        "service_id": service_id,
                        "error": "Error streaming logs",
                        "message": "Error streaming logs; is the service running?",
                    },
                )
    elif command == "stop":
        set_streaming_status(service_id, False)
    else:
        if service.is_running:
            logger.error("Service %s is running but has no container ID", service_id)
            emit(
                "get_logs_failed",
                {
                    "service_id": service_id,
                    "error": "Service is running but has no container ID",
                    "message": "Service is in a bad state; please restart it",
                },
            )
        else:
            logger.info("Service %s is not running; no logs to fetch", service_id)

@socketio.on("get_stats", namespace="/service")
@authenticated_only
def handle_get_stats(data):
    """Handle a client request for service stats."""
    service_id = int(data.get("serviceId"))
    command = data.get("command")
    logger.info("Client requested to %s streaming stats for service %s", command, service_id)
    service = Service.query.get(service_id)
    if command == "start":
        set_streaming_status(service_id, True)
        if service and service.docker_container_id:
            try:
                for stats in app.docker_manager.stream_container_stats(service):
                    if not get_streaming_status(service_id):
                        break
                    emit("stats_message", {"service_id": service_id, "stats": stats})
            except Exception as e:
                logger.error("Error streaming stats: %s", e)
                emit(
                    "get_stats_failed",
                    {
                        "service_id": service_id,
                        "error": "Error streaming stats",
                        "message": "Error streaming stats; is the service running?",
                    },
                )
        elif command == "stop":
            set_streaming_status(service_id, False)
        else:
            if service.is_running:
                logger.error("Service %s is running but has no container ID", service_id)
                emit(
                    "get_stats_failed",
                    {
                        "service_id": service_id,
                        "error": "Service is running but has no container ID",
                        "message": "Service is in a bad state; please restart it",
                    },
                )
            else:
                logger.info("Service %s is not running; no stats to fetch", service_id)

@socketio.on("start_service", namespace="/service")
@authenticated_only
def handle_start_service(service_id):
    """Handle a client request to start a service."""
    logger.info("Client requested to start service %s", service_id)
    service = Service.query.get(service_id)
    if service:
        result, error = service.start()
        if result:
            logger.info("Service %s started", service_id)
            emit(
                "service_started",
                {"service_id": service_id, "message": "Service started successfully"},
            )
        else:
            logger.error("Error starting service %s: %s", service_id, error)
            emit(
                "service_start_failed",
                {
                    "service_id": service_id,
                    "message": "Error starting service",
                    "error": error,
                },
            )
    else:
        logger.error("Service %s not found", service_id)
        emit(
            "service_start_failed",
            {
                "service_id": service_id,
                "message": "Service not found",
                "error": f"Service not found for service_id={service_id}",
            },
        )


@socketio.on("stop_service", namespace="/service")
@authenticated_only
def handle_stop_service(service_id):
    """Handle a client request to stop a service."""
    logger.info("Client requested to stop service %s", service_id)
    service = Service.query.get(service_id)
    if service:
        result, error = service.stop()
        if result:
            logger.info("Service %s stopped", service_id)
            emit(
                "service_stopped",
                {"service_id": service_id, "message": "Service stopped successfully"},
            )
        else:
            logger.error("Error starting service %s: %s", service_id, error)
            emit(
                "service_stop_failed",
                {
                    "service_id": service_id,
                    "message": "Error stopping service",
                    "error": error,
                },
            )
    else:
        logger.error("Service %s not found", service_id)
        emit(
            "service_stop_failed",
            {
                "service_id": service_id,
                "message": "Service not found",
                "error": f"Service not found for service_id={service_id}",
            },
        )


@socketio.on("restart_service", namespace="/service")
@authenticated_only
def handle_restart_service(service_id):
    """Handle a client request to restart a service."""
    logger.info("Client requested to restart service %s", service_id)
    service = Service.query.get(service_id)
    if service:
        result, error = service.restart()
        if result:
            logger.info("Service %s restarted", service_id)
            emit(
                "service_restarted",
                {"service_id": service_id, "message": "Service restarted successfully"},
            )
        else:
            logger.error("Error starting service %s: %s", service_id, error)
            emit(
                "service_restart_failed",
                {
                    "service_id": service_id,
                    "message": "Error restarting service",
                    "error": error,
                },
            )
    else:
        logger.error("Service %s not found", service_id)
        emit(
            "service_restart_failed",
            {
                "service_id": service_id,
                "message": "Service not found",
                "error": f"Service not found for service_id={service_id}",
            },
        )

##### SocketIO test events #####
@socketio.on("message", namespace="/test")
def handle_message(message):
    """Handle a client message."""
    logger.info("Client sent message: %s", message)
    emit("response", {"data": message["data"]})


@socketio.on("json", namespace="/test")
def handle_json(json):
    """Handle a client JSON message."""
    logger.info("Client sent JSON: %s", json)
    emit("response", json)
