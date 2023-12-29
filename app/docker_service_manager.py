"""Module to manage docker containers."""
import os
import logging
import docker
from docker.errors import ImageNotFound, APIError

from app.models import Service

logger = logging.getLogger(__name__)


class DockerServiceManager:
    """Class to manage docker containers"""

    def __init__(self):
        self.client = docker.from_env()

    def find_container(self, service) -> docker.models.containers.Container:
        """Find a container by service definition.

        Args:
            service (Service): The service to find the container for.

        Returns:
            docker.models.containers.Container: The container object.
            str: An error message if the container was not found.
        """
        try:
            target_container = None
            if service.docker_container_id:
                try:
                    logger.debug(
                        "Searching for existing container %s",
                        service.docker_container_id,
                    )
                    target_container = self.client.containers.get(
                        service.docker_container_id
                    )
                except docker.errors.NotFound:
                    logger.debug(
                        "Container not found. Updating state and searching by image name."
                    )
                    service.update_state(False, None)
                    target_container = self.find_container(service)

                if target_container:
                    logger.debug("Found existing container %s", target_container)
                else:
                    logger.debug(
                        "Container recorded in database not found. Updating state and searching by image name."
                    )
                    service.update_state(False, None)
                    target_container = self.find_container(service)
            else:
                # If the container ID is not set, try to find it by image name
                containers = self.client.containers.list()
                logger.debug(
                    "No container ID found. Searching by image name %s:%s",
                    service.docker_image,
                    service.docker_image_tag,
                )
                for container in containers:
                    logger.debug("Container image: %s", container.image.tags[0])
                    if (
                        container.image.tags[0]
                        == service.docker_image + ":" + service.docker_image_tag
                    ):
                        target_container = container
                        break

            logger.debug("Target container: %s", target_container)
            if target_container:
                service.update_state(
                    target_container.status == "running", target_container.id
                )
            return target_container
        except docker.errors.NotFound as e:
            logger.warning("Container not found: %s", e)
            raise ServiceContainerNotFound() from e
        except docker.errors.APIError as e:
            logger.error("API error occurred: %s", e)
            raise

    def listen_for_events(self, app) -> None:
        """Listen for Docker events."""
        event_filters = {
            "type": ["container"],
            "event": ["start", "stop", "die", "destroy"],
        }

        for event in self.client.events(filters=event_filters, decode=True):
            logger.debug(
                "Docker event: %s for container %s",
                event.get("status"),
                event.get("id"),
            )
            # Extract the container id and event info
            container_id = event["id"]
            status = event["status"]
            container = self.client.containers.get(container_id)

            # Handle the event
            with app.app_context():
                Service.handle_docker_event(app, container, status)

    def start_service(self, service) -> docker.models.containers.Container:
        """Start a container from a service definition."""
        try:
            # Search for an existing container
            container = self.find_container(service)
            if container:
                # If the container isn't running but already exists, start it
                if not container.status == "running":
                    container.start()
                return container, None

            # Time values are stored in seconds but need to be in nanoseconds for docker-py
            if service.docker_healthcheck:
                healthcheck = {
                    "test": service.docker_healthcheck.test,
                    "interval": service.docker_healthcheck.interval * 1_000_000_000,
                    "timeout": service.docker_healthcheck.timeout * 1_000_000_000,
                    "retries": service.docker_healthcheck.retries,
                    "start_period": service.docker_healthcheck.start_period
                    * 1_000_000_000,
                }
            else:
                healthcheck = None

            container = self.client.containers.run(
                image=service.docker_image,
                volumes=get_volume_mappings(service),
                ports={
                    f"{port.container_port}/tcp": port.host_port
                    for port in service.docker_ports
                },
                healthcheck=healthcheck,
                devices=[
                    f"{device.host_path}:{device.container_path}:{device.cgroup_permissions}"
                    for device in service.docker_devices
                ],
                labels={label.key: label.value for label in service.docker_labels},
                restart_policy={"Name": "unless-stopped"},
                detach=True,
            )
            return container
        except docker.errors.ImageNotFound as e:
            logger.warning("Image not found: %s", service.docker_image)
            raise ServiceImageNotFound() from e
        except docker.errors.APIError as e:
            logger.error("API error occurred: %s", e)
            raise

    def stop_service(self, service) -> bool:
        """Stop a container from a service definition."""
        container = self.find_container(service)
        if container:
            container.stop()
            container.remove()
            return True
        return False

    def restart_service(self, service) -> docker.models.containers.Container:
        """Restart a container from a service definition."""
        container_id = service.docker_container_id
        if not container_id:
            return self.start_service(service)

        try:
            container = self.find_container(service)
            if container:
                container.restart()
                return container
        except ServiceContainerNotFound:
            return self.start_service(service)

    def stream_container_logs(self, service) -> str:
        """Stream logs from a container."""
        container = self.find_container(service)
        try:
            if container:
                for line in container.logs(stream=True, follow=True):
                    yield line.decode("utf-8")
            else:
                yield "warning: Container not found"
        except docker.errors.APIError as e:
            logger.error("API error occurred: %s", e)
            raise

    def stream_container_stats(self, service) -> dict:
        """Get container stats from a container."""
        container = self.find_container(service)
        try:
            if container:
                for stats in container.stats(stream=True, decode=True):
                    cpu_usage = calculate_cpu_percent(stats)
                    memory_usage = stats["memory_stats"]["usage"]
                    disk_usage_list = stats["blkio_stats"]["io_service_bytes_recursive"]
                    disk_usage = disk_usage_list[0]["value"] if disk_usage_list else 0

                    yield {
                        "cpu_usage": cpu_usage,
                        "memory_usage": memory_usage,
                        "disk_usage": disk_usage,
                    }
            else:
                yield {
                    "cpu_usage": "Container not found",
                    "memory_usage": "Container not found",
                    "disk_usage": "Container not found",
                }
        except docker.errors.APIError as e:
            logger.error("API error occurred: %s", e)
            raise

    def handle_daemons(self) -> bool:
        """All is_daemon services are handled here."""
        daemon_services = Service.query.filter_by(
            is_daemon=True, is_disabled=False
        ).all()
        for service in daemon_services:
            logger.debug("Checking daemon service %s", service.name)
            container = self.find_container(service)
            if container:
                logger.debug(
                    "Found container %s for service %s", container, service.name
                )
                if service.is_running:
                    logger.debug("Daemon service %s is running. Restarting...", service.name)
                    container.restart()
                    return True
            logger.debug("Daemon service %s is not running. Starting...", service.name)
            container = self.start_service(service)
            if container:
                logger.debug("Daemon service %s started successfully", service.name)
                return True
            logger.debug("Daemon service %s failed to start", service.name)
            return False

    def cache_images(self) -> bool:
        """Cache all images in the database."""
        services = (
            Service.query.filter_by(is_disabled=False).order_by(Service.is_daemon).all()
        )
        logger.info("Caching images...")
        logger.info("Found %s services", len(services))
        for service in services:
            logger.debug(
                "Caching image %s:%s for %s",
                service.docker_image,
                service.docker_image_tag,
                service.name,
            )
            self.get_or_pull_image(service.docker_image)
            logger.debug(
                "Image %s:%s cached", service.docker_image, service.docker_image_tag
            )
        logger.info("Image caching complete.")
        return True

    def get_or_pull_image(self, image_name, tag="latest") -> docker.models.images.Image:
        """
        Checks if an image is available locally, pulls it if not.

        Args:
            image_name (str): The name of the image.
            tag (str): The tag of the image, defaults to 'latest'.

        Returns:
            docker.models.images.Image: The Docker image object.
        """
        full_image_name = f"{image_name}:{tag}"

        try:
            logger.debug("Checking for image: %s", full_image_name)
            return self.client.images.get(full_image_name)
        except ImageNotFound:
            logger.debug("Image not found locally. Pulling %s...", full_image_name)
            return self.client.images.pull(image_name, tag=tag)
        except APIError as e:
            logger.debug("An error occurred while pulling the image: %s", e)
            raise


##### Static methods #####
@staticmethod
def get_volume_mappings(service) -> dict:
    """Get a dictionary of volume mappings from a service definition."""
    volume_mappings = {}
    for volume in service.docker_volumes:
        absolute_host_path = os.path.abspath(volume.host_path)
        volume_mappings[absolute_host_path] = {
            "bind": volume.container_path,
            "mode": "rw",
        }
    return volume_mappings


@staticmethod
def calculate_cpu_percent(stat) -> float:
    """Calculate the CPU percentage from a container stat object."""
    try:
        cpu_delta = stat["cpu_stats"]["cpu_usage"]["total_usage"]
        if (
            "precpu_stats" in stat
            and "cpu_usage" in stat["precpu_stats"]
            and "total_usage" in stat["precpu_stats"]["cpu_usage"]
        ):
            cpu_delta -= stat["precpu_stats"]["cpu_usage"]["total_usage"]

        system_cpu_usage = stat["cpu_stats"].get("system_cpu_usage")
        online_cpus = stat["cpu_stats"].get(
            "online_cpus", len(stat["cpu_stats"]["cpu_usage"]["percpu_usage"])
        )

        # Ensure we have all needed data to calculate CPU usage
        if system_cpu_usage and cpu_delta is not None and online_cpus:
            return round((cpu_delta / system_cpu_usage) * online_cpus * 100.0, 2)
        else:
            logger.warning("Unable to calculate CPU usage: Missing data.")
            return None
    except KeyError as e:
        logger.error("KeyError in calculate_cpu_percent %s", e)
        return None


class ServiceContainerNotFound(Exception):
    """Exception raised when a container is not found."""

    def __init__(self, message="Container not found"):
        self.message = message
        super().__init__(self.message)


class ServiceImageNotFound(Exception):
    """Exception raised when an image is not found."""

    def __init__(self, message="Image not found"):
        self.message = message
        super().__init__(self.message)
