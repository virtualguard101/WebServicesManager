#!/usr/bin/env python3

import subprocess
import os
import logging
import colorlog
from abc import ABC, abstractmethod
from typing import Optional, Tuple, List, Callable

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


def get_operation() -> Optional[int]:
    """Get service operation from user input.
    
    Returns:
        0: stop, 1: restart, None: quit
    """
    while True:
        choice = input("Please select an operation (0 to stop, 1 to restart, q to quit): ").strip().lower()
        if choice == 'q':
            return None
        try:
            op = int(choice)
            if op in (0, 1):
                return op
        except ValueError:
            pass
        logger.warning("Invalid input, please enter 0, 1, or q.")


class ServiceStrategy(ABC):
    """Abstract base class for service operation strategies."""
    
    @abstractmethod
    def generate_command(self, operation: int, service_name: str, path: Optional[str] = None) -> List[str]:
        """Generate command for service operation.
        
        Args:
            operation: 0=stop, 1=restart
            service_name: Name of the service
            path: Service path (for docker)
            
        Returns:
            Command list for subprocess
        """
        pass
    
    @abstractmethod
    def execute(self, command: List[str]) -> None:
        """Execute the service command.
        
        Args:
            command: Command to execute
            
        Raises:
            subprocess.CalledProcessError: If command fails
        """
        pass


class SystemServiceStrategy(ServiceStrategy):
    """Strategy for systemd services."""
    
    def __init__(self, path: Optional[str] = None):
        pass
    
    def generate_command(self, operation: int, service_name: str, path: Optional[str] = None) -> List[str]:
        if operation == 0:
            return ["sudo", "systemctl", "stop", service_name]
        elif operation == 1:
            return ["sudo", "systemctl", "restart", service_name]
        raise ValueError(f"Invalid operation for system service: {operation}")
    
    def execute(self, command: List[str]) -> None:
        subprocess.run(command, check=True)


class DockerServiceStrategy(ServiceStrategy):
    """Strategy for docker-compose services."""
    
    def __init__(self, path: str):
        self.path = path
    
    def generate_command(self, operation: int, service_name: str, path: Optional[str] = None) -> List[str]:
        if not self.path:
            raise ValueError("Docker service requires a path")
        
        expanded_path = os.path.expanduser(self.path)
        if not os.path.exists(expanded_path):
            raise FileNotFoundError(f"Docker path not found: {expanded_path}")
        if not os.path.isdir(expanded_path):
            raise NotADirectoryError(f"Docker path must be a directory: {expanded_path}")
        
        if operation == 0:
            return ["docker", "compose", "down"]
        elif operation == 1:
            return ["docker", "compose", "up", "-d"]
        raise ValueError(f"Invalid operation for docker service: {operation}")
    
    def execute(self, command: List[str]) -> None:
        expanded_path = os.path.expanduser(self.path)
        if not os.path.exists(expanded_path):
            raise FileNotFoundError(f"Path not found: {expanded_path}")
        if not os.path.isdir(expanded_path):
            raise NotADirectoryError(f"Docker path must be directory: {expanded_path}")
        subprocess.run(command, check=True, cwd=expanded_path)


class Service:
    """Management interface for web services.
    
    Attributes:
        tag: Service type ('sys' or 'docker')
        name: Service name
        path: Configuration path (for docker services)
        strategy: Service operation strategy
    """

    STRATEGIES = {
        'sys': SystemServiceStrategy,
        'docker': DockerServiceStrategy
    }

    def __init__(self, tag: str, name: str, path: Optional[str] = None):
        """Initialize a service instance.
        
        Args:
            tag: Service type ('sys' or 'docker')
            name: Service name
            path: Configuration path (required for docker)
            
        Raises:
            ValueError: For invalid tag
        """
        if tag not in self.STRATEGIES:
            raise ValueError(f"Invalid service tag: {tag}")
        
        self.tag = tag
        self.name = name
        self.path = path
        self.strategy = self.STRATEGIES[tag](path=self.path)
        logger.info(f"Initialized {tag} service: {name}")
        
    def to_dict(self) -> dict:
        """Return dictionary representation of the service."""
        return {
            "tag": self.tag,
            "name": self.name,
            "path": self.path
        }

    def service_operation(self) -> None:
        """Perform service operation based on user input.
        
        """
        operation = get_operation()
        if operation is None:
            logger.info("Operation cancelled by user")
            return
        
        try:
            # Generate and execute command
            if self.path is not None:
                command = self.strategy.generate_command(operation, self.name, self.path)
            else:
                command = self.strategy.generate_command(operation, self.name)
            logger.info(f"Executing: {' '.join(command)}")
            self.strategy.execute(command)
            logger.info(f"Service {self.name} operation completed")
        except (ValueError, FileNotFoundError, NotADirectoryError, subprocess.CalledProcessError) as e:
            logger.error(f"Service operation failed: {str(e)}")

# Example usage
if __name__ == "__main__":
    try:
        service = Service(tag="docker", name="homepage", path="~/projects/webservices/homepage")
        service.service_operation()
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
