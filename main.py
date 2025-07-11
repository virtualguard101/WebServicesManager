#!/usr/bin/env python3

from src.manager import *
import logging
import colorlog
import sys

def initialize_logger():
    """Initialize and return a color logger."""
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
    return logger

def initialize_service_manager():
    """Initialize and return the service manager."""
    return Manager()

logger = initialize_logger()
service_manager = initialize_service_manager()

def start_menu():
    logger.info(f"=======================================")
    logger.info(f"========== Services Manager ===========")
    logger.info(f"=======================================")
    logger.info(f"Please choose a operation to carry out:")
    logger.info(f"=====> 1. Register a new service <=====")
    logger.info(f"=====> 2. Manage exsist services <=====")
    logger.info(f"=====> c. Count the number of services")
    logger.info(f"=====> q. Quit ")

def main_menu():
    """Display the main menu and handle user input."""

    while True:
        start_menu()

        start_choice = input("Enter your choice: ").strip()
        if start_choice == '1':
            service_tag = input("Please input the deploy way of service you want to register('docker' | 'sys'): ")
            service_name = input("Please input the name of the service: ")
            if service_tag == "docker":
                service_path = input("Please input the config path of the service where 'docker-compose.yml' located: ")
                service_manager.register_service(service_tag, service_name, service_path)
            else:
                service_manager.register_service(service_tag, service_name)
        if start_choice == '2':
            if not service_manager.services_list:
                logger.error("No services registered.")
                continue
            while True:
                logger.info(f"=====> Exsist Services Management <=====")
                service_code = 1
                for service in service_manager.services_list:
                    logger.info(f"=====> {service_code}: {service._name}")
                    service_code += 1
                # logger.info("=====> a. Select All")
                logger.info("=====> q. Quit")

                manage_choice = input("Please select a choice to carry out: ").strip()
                if manage_choice == 'q':
                    logger.info("Exit main manager")
                    break
                # if manage_choice == 'a':
                #     pass
                try:
                    code = int(manage_choice)
                    if 0 <= code < len(service_manager.services_list):
                        service_manager.services_list[code].service_operation()
                    else:
                        logger.error("Invalid service code.")
                except ValueError:
                    logger.error("Please enter a valid number.")
        if start_choice == 'c':
            service_manager.list_services()
        if start_choice == 'q':
            logger.info(f"Exit the manager process")
            break

if __name__ == '__main__':
    sys.exit(main_menu())
