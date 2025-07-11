from src.manager import *
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

service_manager = Manager()

def start_menu():
    logger.info(f"=======================================")
    logger.info(f"========== Services Manager ===========")
    logger.info(f"=======================================")
    logger.info(f"Please choose a operation to carry out:")
    logger.info(f"=====> 1. Register a new service <=====")
    logger.info(f"=====> 2. Manage exsist services <=====")
    logger.info(f"=====> c. Count the number of services")
    logger.info(f"=====> q. Quit ")

def main():
    while True:
        start_menu()

        start_choice = input()
        if start_choice == '1':
            service_tag = input("Please input the deploy way of service you want to register('docker' | 'sys'): ")
            service_name = input("Please input the name of the service: ")
            if service_tag == "docker":
                service_path = input("Please input the config path of the service where 'docker-compose.yml' located: ")
                service_manager.register_service(service_tag, service_name, service_path)
            service_manager.register_service(service_tag, service_name)
        if start_choice == '2':
            if len(service_manager.services_list) == 0:
                raise ValueError("There has no service registered")
            while True:
                # TODO: Manage the feature which use for managing exsist services.
                logger.info(f"=====> Exsist Services Management <=====")
                service_code = 1
                for service in service_manager.services_list:
                    logger.info(f"=====> {service_code}: {service._name}")
                    service_code += 1
                # logger.info("=====> a. Select All")
                logger.info("=====> q. Quit")

                manage_choice = input(f"Please select a chioce to carry out: ")
                if manage_choice == 'q':
                    logger.info("Exit main manager")
                    break
                # if manage_choice == 'a':
                #     pass
                while int(manage_choice):
                    code = int(manage_choice)
                    service_manager.services_list[code].service_operation()
                    break
        if start_choice == 'c':
            service_manager.list_services()
        if start_choice == 'q':
            logger.info(f"Exit the manager process")
            break
