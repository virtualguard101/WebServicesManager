#!/usr/bin/env python3

from src.services import *
import logging
import colorlog

# Initialize color logging
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - %(levelname)s - %(message)s',
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'bold_red',
    }
))

logger = colorlog.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)


# nginx = Service(tag="sys", name="nginx")
# minecraft = Service(tag="sys", name="minecraft", path="~/web/minecraftService")
# homepage = Service(tag="docker", name="docker", path="~/web/homepageService")
# status = Service(tag="docker", name="status", path="~/web/statusService")
# gitea = Service(tag="docker", name="gitea", path="~/web/giteaService")

class Manager:
    """Interface set of services management operations.

    Attributes:
        service_list (list): List use for storing service instances.
    """

    def __init__(self):
       """Initialize the Manager with an empty services list."""
       self.services_list = []

    def append_service(self, service_instance: Service) -> None:
        """Append a service instance to the services list.
        
        Args:
            service_instance (Service): The service instance to append.
        """
        self.services_list.append(service_instance)

    def register_service(self, service_tag: str, service_name: str, service_path=None) -> Service:
        """Register a new service.

        Args:
            service_tag ('sys' | 'docker'): The tag that marks the service instance to use which way to deploy ('sys' or 'docker').
            service_name (str): The name of the service instance.
            service_path (str): The configuration and data path of the service instance.

        Returns:
            service: A web service instance.
        """

        if service_tag == "docker":
            assert service_path != None, """Can not leave a empty path while you register a docker-deploy service."""
            if not os.path.exists(service_path):
                raise ValueError(f"Invalid service path: {service_path}")
            service = Service(tag=service_tag, name=service_name, path=service_path)
            # service.code = len(self.services_list) + 1
            self.append_service(service_instance=service)
            return service
        service = Service(tag=service_tag, name=service_name)
        # service.code = len(self.services_list) + 1
        self.append_service(service_instance=service)
        return service

    def list_services(self) -> None:
        """Method use for count the num of service instances and list the names of them.

        """

        sum_of_service = 0
        service_name_list = []
        for services in self.services_list:
            service_name_list.append(services.name)
            sum_of_service += 1
        logger.info(f"The manager has registered {sum_of_service} services: {', '.join(service_name_list)}")
