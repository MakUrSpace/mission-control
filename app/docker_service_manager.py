"""Module to manage docker containers."""
import docker
import os

class DockerServiceManager:
    """Class to manage docker containers"""

    def __init__(self):
        self.client = docker.from_env()

    def get_container(self, container_id):
        """Get a container by ID."""
        try:
            return self.client.containers.get(container_id)
        except docker.errors.NotFound:
            return None

    def start_service(self, service):
        """Start a container from a service definition."""
        try:
            # Time values are stored in seconds but need to be in nanoseconds for docker-py
            if service.docker_healthcheck:
                healthcheck = {
                    'test': service.docker_healthcheck.test,
                    'interval': service.docker_healthcheck.interval * 1_000_000_000,
                    'timeout': service.docker_healthcheck.timeout * 1_000_000_000,
                    'retries': service.docker_healthcheck.retries,
                    'start_period': service.docker_healthcheck.start_period * 1_000_000_000
                }
            else:
                healthcheck = None

            container = self.client.containers.run(
                image=service.docker_image,
                volumes=get_volume_mappings(service),
                ports={f"{port.container_port}/tcp": port.host_port
                       for port in service.docker_ports},
                healthcheck=healthcheck,
                devices=[f"{device.host_path}:{device.container_path}:{device.cgroup_permissions}" for device in service.docker_devices],
                labels={label.key: label.value for label in service.docker_labels},
                detach=True,
                restart_policy={"Name": "unless-stopped"}
            )
            return container
        except docker.errors.ImageNotFound:
            print(f"Error: Image {service.docker_image} not found.")
        except docker.errors.APIError as e:
            print(f"API error: {e.explanation}")

    def stop_service(self, service):
        """Stop a container from a service definition."""
        container = self.get_container(service.docker_container_id)
        if container:
            container.stop()
            container.remove()
            return True
        return False

    def restart_service(self, service):
        """Restart a container from a service definition."""
        container_id = service.docker_container_id
        if not container_id:
            return self.start_service(service)

        container = self.get_container(container_id)
        if container:
            container.restart()
            return container
        return None

##### Static methods #####
@staticmethod
def get_volume_mappings(service):
    volume_mappings = {}
    for volume in service.docker_volumes:
        absolute_host_path = os.path.abspath(volume.host_path)
        volume_mappings[absolute_host_path] = {'bind': volume.container_path, 'mode': 'rw'}
    return volume_mappings
