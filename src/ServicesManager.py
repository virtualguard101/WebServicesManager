import subprocess
import sys
import os
import logging
import colorlog

# init color log
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
        choice = input("请选择操作 (0 停止, 1 重启, q 退出): ").strip().lower()
        if choice == 'q':
            return 'q'
        try:
            op = int(choice)
            if op in (0, 1):
                return op
        except ValueError:
            pass
        logger.warning("无效输入，请输入 0、1 或 q。")


class Service:
    """A template of webservices 

    Attributes:
        tag (str): The tag that mark the service instance use which way to deploy.
        name (str): The name of the service instance.
        dir (str): The configuration & data directory of the service instance.
    """

    def __init__(self, tag: str, name: str, dir: str):
        self.tag = tag
        self.name = name
        self.dir = dir

    def command_gen(self):
        """Generate services's management commands according to services's tag

        """
        system_services_command = "sudo systemctl"
        docker_services_command = f"cd {os.path.expanduser(f'{self.dir}')} && docker compose"
        if self.tag == "sys":
            return system_services_command
        elif self.tag == "docker":
            return docker_services_command
        else:
            raise ValueError("The service tag {self.tag} was not included")
