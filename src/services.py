#!/usr/bin/env python3

import subprocess
import os
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


def get_operation():
    while True:
        choice = input("Please select an operation (0 to stop, 1 to restart, q to quit): ").strip().lower()
        if choice == 'q':
            return 'q'
        try:
            op = int(choice)
            if op in (0, 1):
                return op
        except ValueError:
            pass
        logger.warning("Invalid input, please enter 0, 1, or q.")


class Service:
    """A template management for web services

    Attributes:
        tag ('sys' | 'docker'): The tag that marks the service instance to use which way to deploy.
        name (str): The name of the service instance.
        path (str): The configuration and data path of the service instance.
    """

    def __init__(self, tag: str, name: str, path=None):
        self._tag = tag
        self._name = name
        self._path = path

    def command_gen(self):
        """Generate service management commands based on the service's tag.

        """

        system_services_command = "sudo systemctl"
        docker_services_command = f"cd {os.path.expanduser(f'{self._path}')} && docker compose"
        if self._tag == "sys":
            return system_services_command
        elif self._tag == "docker":
            return docker_services_command
        else:
            raise ValueError(f"The service tag {self._tag} was not included.")

    def service_operation(self):
        """Manage the service based on user input.

        """

        operation = get_operation()
        if operation == 'q':
            logger.info("User chose to quit the service management.")
            return
        
        command = self.command_gen()
        full_command = None  # Initialize full_command
        
        if self._tag == "sys":
            if operation == 0:
                # Stop the service
                full_command = f"{command} stop {self._name}"
                logger.info(f"Stopping service: {self._name}")
            elif operation == 1:
                # Restart the service
                full_command = f"{command} restart {self._name}"
                logger.info(f"Restarting service: {self._name}")
            else:
                logger.warning("Invalid operation; no service management executed.")
                return  # Exit if the operation is invalid
        if self._tag == "docker":
            if operation == 0:
                # Stop the service
                full_command = f"{command} down"
                logger.info(f"Stopping service: {self._name}")
            elif operation == 1:
                # Restart the service
                full_command = f"{command} up -d"
                logger.info(f"Restarting service: {self._name}")
            else:
                logger.warning("Invalid operation; no service management executed.")
                return  # Exit if the operation is invalid
        
        if full_command:  # Ensure full_command is defined
            try:
                subprocess.run(full_command, check=True, shell=True)
                logger.info(f"Service {self._name} operation completed successfully.")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to manage service {self._name}: {e}")

# Example call
if __name__ == "__main__":
    service = Service(tag="docker", name="homepage", path="~/web/homepageService")
    service.service_operation()
