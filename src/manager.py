#!/usr/bin/env python3

from src.services import Service
import logging
import json
import os
import colorlog
from typing import Optional, List, Dict

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


class ServiceFactory:
    """Factory for creating Service instances based on tag.
    
    """
    
    @staticmethod
    def create_service(tag: str, name: str, path: Optional[str] = None) -> Service:
        """Create a Service instance with validation.
        
        Args:
            tag: Service type ('sys' or 'docker')
            name: Service name
            path: Configuration path (required for docker services)
            
        Returns:
            Service instance
            
        Raises:
            ValueError: For invalid inputs
        """
        if tag == "docker":
            if not path:
                raise ValueError("Path is required for docker services")
            if not os.path.exists(path):
                raise ValueError(f"Invalid service path: {path}")
            if not os.path.isdir(path):
                raise ValueError(f"Service path must be a directory: {path}")
            logger.info(f"Validated docker service path: {path}")
        return Service(tag=tag, name=name, path=path)


class ServiceRepository:
    """Repository for service persistence.

    """
    
    def __init__(self, file_path: str = 'data/services.json'):
        self.file_path = file_path
        # Make sure the path has existed
        dir_path = os.path.dirname(file_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
    def save(self, service: Service) -> None:
        """Save a service to the repository.
        
        Args:
            service: Service instance to save
        """
        # Load existing services
        services = self.load_all()
        
        # Add new service
        services.append(service.to_dict())
        
        # Save back to file
        with open(self.file_path, 'w') as file:
            json.dump(services, file, indent=4)
        logger.info(f"Saved service to repository: {service.name}")
            
    def load_all(self) -> List[Dict]:
        """Load all services from repository.
        
        Returns:
            List of service dictionaries
        """
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as file:
                    return json.load(file)
            except (json.JSONDecodeError, FileNotFoundError):
                logger.warning("Service repository file corrupted or missing")
                return []
        logger.info("Service repository file not found, starting fresh")
        return []
        
    def remove(self, service_name: str) -> None:
        """Remove a service by name.
        
        Args:
            service_name: Name of the service to remove
            
        Raises:
            ValueError: If service not found
        """
        try:
            # Load all servives
            services = self.load_all()
            
            # Search for matching services (case insensitive)
            original_count = len(services)
            services = [s for s in services
                       if s['name'].strip().lower() != service_name.strip().lower()]
            
            # Check and remove
            if len(services) == original_count:
                raise ValueError(f"Service '{service_name}' not found")
            
            # Update services,json
            with open(self.file_path, 'w') as file:
                json.dump(services, file, indent=4)
                
            logger.info(f"Removed service: {service_name}")
            
        except FileNotFoundError:
            logger.warning("Services file not found, nothing to remove")
            raise ValueError("Services file does not exist")
        except json.JSONDecodeError:
            logger.error("Invalid JSON format in services file")
            raise ValueError("Invalid services data format")
        except PermissionError:
            logger.error("Permission denied when writing services file")
            raise
        except Exception as e:
            logger.error(f"Error removing service: {str(e)}")
            raise


class Manager:
    """Interface for services management operations.
    
    """
    
    def __init__(self,
                 repository: Optional[ServiceRepository] = None,
                 factory: Optional[ServiceFactory] = None):
        """Initialize Manager with dependencies.
        
        Args:
            repository: Service repository instance (optional)
            factory: Service factory instance (optional)
        """
        self.repository = repository or ServiceRepository()
        self.factory = factory or ServiceFactory()
        logger.info("Manager initialized")

    def register_service(self,
                         service_tag: str,
                         service_name: str,
                         service_path: Optional[str] = None) -> Service:
        """Register and persist a new service.
        
        Args:
            service_tag: Service type ('sys' or 'docker')
            service_name: Service name
            service_path: Configuration path (required for docker)
            
        Returns:
            Registered service instance
            
        Raises:
            ValueError: If service registration fails
        """
        try:
            # Create service via factory
            service = self.factory.create_service(service_tag, service_name, service_path)
            
            # Persist service
            self.repository.save(service)
            
            logger.info(f"Successfully registered service: {service_name} ({service_tag})")
            return service
            
        except ValueError as e:
            logger.error(f"Service registration failed: {str(e)}")
            raise

    def remove_service(self, index: int) -> None:
        """Remove a service by index.
        
        Args:
            index: Index of the service to remove
            
        Raises:
            IndexError: If index is out of bounds
            ValueError: If service not found
        """
        services = self.list_services()
        if index < 0 or index >= len(services):
            raise IndexError(f"Invalid service index: {index}")
        service_name = services[index].name
        self.repository.remove(service_name)

    def list_services(self) -> List[Service]:
        """List all registered services.
        
        Returns:
            List of Service objects
        """
        services_data = self.repository.load_all()
        if not services_data:
            logger.info("No services registered")
            return []
            
        services = []
        for s in services_data:
            try:
                service = Service(tag=s["tag"], name=s["name"], path=s["path"])
                services.append(service)
            except Exception as e:
                logger.error(f"Invalid service data: {s}, error: {str(e)}")
                
        service_names = [s.name for s in services]
        logger.info(f"Registered services ({len(services)}): {', '.join(service_names)}")
        return services
        
    def execute_service_operation(self, index: int) -> None:
        """Execute service operation for the service at the given index.
        
        Args:
            index: Index of the service in the list returned by list_services()
            
        Raises:
            IndexError: If index is out of bounds
        """
        services = self.list_services()
        if index < 0 or index >= len(services):
            logger.error(f"Invalid service index: {index}")
            raise IndexError(f"Invalid service index: {index}")
            
        service = services[index]
        service.service_operation()

if __name__ == "__main__":
    # 测试服务移除功能
    manager = Manager()
    try:
        # 注册测试服务
        test_service = manager.register_service("sys", "test-service")
        print("Registered test service")
        
        # 移除测试服务（索引0）
        manager.remove_service(0)
        print("Successfully removed test service")
        
        # 尝试移除不存在的服务（索引越界）
        try:
            manager.remove_service(100)
        except IndexError as e:
            print(f"Expected error: {str(e)}")
            
    except Exception as e:
        print(f"Test failed: {str(e)}")
