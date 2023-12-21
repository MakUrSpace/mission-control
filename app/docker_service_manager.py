"""Module to manage docker containers."""
import os
import logging
import docker

logger = logging.getLogger(__name__)

class DockerServiceManager:
    """Class to manage docker containers"""

    def __init__(self):
        self.client = docker.from_env()

    def get_container(self, container_id) -> (docker.models.containers.Container, str):
        """Get a container by ID.

        Args:
            container_id (str): ID of the container to get.

        Returns:
            docker.models.containers.Container: The container object.
            str: An error message if the container was not found.
        """
        try:
            container = self.client.containers.get(container_id)
            return container, None
        except docker.errors.NotFound as e:
            logger.error("Container not found: %s", e)
            return None, "Container not found"
        except docker.errors.APIError as e:
            logger.error("API error occurred: %s", e)
            return None, "Docker API error"

    def start_service(self, service):
        """Start a container from a service definition."""
        try:
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
            return container, None
        except docker.errors.ImageNotFound:
            err_msg = f"Error: Image {service.docker_image} not found."
            logger.error(err_msg)
            return None, err_msg
        except docker.errors.APIError as e:
            logger.error("API error occurred: %s", e)
            return None, "Docker API error"

    def stop_service(self, service) -> (bool, str):
        """Stop a container from a service definition."""
        container, error = self.get_container(service.docker_container_id)
        if container:
            container.stop()
            container.remove()
            return True, None
        return False, error

    def restart_service(self, service) -> (docker.models.containers.Container, str):
        """Restart a container from a service definition."""
        container_id = service.docker_container_id
        if not container_id:
            return self.start_service(service), None

        container, error = self.get_container(container_id)
        if container:
            container.restart()
            return container, None
        return None, error

    def stream_container_logs(self, service):
        """Stream logs from a container."""
        container, error = self.get_container(service.docker_container_id)
        try:
            if container:
                for line in container.logs(stream=True, follow=True):
                    yield line.decode("utf-8")
            else:
                yield error
        except docker.errors.APIError as e:
            logger.error("API error occurred: %s", e)
            yield "Docker API error"

    def stream_container_stats(self, service):
        """Get container stats from a container."""
        container, error = self.get_container(service.docker_container_id)
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
                yield {"error": error}
        except docker.errors.APIError as e:
            logger.error("API error occurred: %s", e)
            yield {"error": "Docker API error"}

##### Static methods #####
@staticmethod
def get_volume_mappings(service):
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
def calculate_cpu_percent(stat):
    """Calculate the CPU percentage from a container stat object."""
    try:
        cpu_delta = stat["cpu_stats"]["cpu_usage"]["total_usage"]
        if "precpu_stats" in stat and "cpu_usage" in stat["precpu_stats"] and "total_usage" in stat["precpu_stats"]["cpu_usage"]:
            cpu_delta -= stat["precpu_stats"]["cpu_usage"]["total_usage"]

        system_cpu_usage = stat["cpu_stats"].get("system_cpu_usage")
        online_cpus = stat["cpu_stats"].get("online_cpus", len(stat["cpu_stats"]["cpu_usage"]["percpu_usage"]))

        # Ensure we have all needed data to calculate CPU usage
        if system_cpu_usage and cpu_delta is not None and online_cpus:
            return round((cpu_delta / system_cpu_usage) * online_cpus * 100.0, 2)
        else:
            logger.warning("Unable to calculate CPU usage: Missing data.")
            return None
    except KeyError as e:
        logger.error("KeyError in calculate_cpu_percent %s", e)
        return None
