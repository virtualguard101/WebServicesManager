#!/usr/bin/env python3

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

def manage_service(name, command_template):
    logger.info(f"===== {name} 管理 =====")
    logger.info("0. 停止")
    logger.info("1. 启动")
    op = get_operation()
    if op == 'q':
        return False
    action = 'down' if op == 0 else 'up -d'
    cmd = command_template.format(action=action)
    try:
        subprocess.run(cmd, shell=True, check=True)
        logger.info(f"{name} {('停止' if op == 0 else '重启')} 完成")
    except subprocess.CalledProcessError as e:
        logger.error(f"{name} 管理失败: {e}")
    return True

def nginx_manager():
    logger.info("===== Nginx 管理 =====")
    logger.info("0. 停止")
    logger.info("1. 重启")
    op = get_operation()
    if op == 'q':
        return False
    action = 'stop' if op == 0 else 'restart'
    cmd = f"sudo systemctl {action} nginx"
    try:
        subprocess.run(cmd, shell=True, check=True)
        logger.info(f"Nginx {('停止' if op == 0 else '重启')} 完成")
    except subprocess.CalledProcessError as e:
        logger.error(f"Nginx 管理失败: {e}")
    return True

def homepage_manager():
    path = os.path.expanduser("~/web/homepageService")
    return manage_service("Homepage", f"cd {path} && docker compose {{action}}")

def status_manager():
    path = os.path.expanduser("~/web/statusService")
    return manage_service("Status", f"cd {path} && docker compose {{action}}")

def gitea_manager():
    path = os.path.expanduser("~/web/giteaService")
    return manage_service("Gitea", f"cd {path} && docker compose {{action}}")

def main():
    services = {
        0: ("Nginx", nginx_manager),
        1: ("Homepage", homepage_manager),
        2: ("Status", status_manager),
        3: ("Gitea", gitea_manager),
    }

    while True:
        logger.info("=== 服务管理 ===")
        for key, (name, _) in services.items():
            logger.info(f"{key}. {name}")
        logger.info("a. 全部")
        logger.info("q. 退出")

        choice = input("请选择要管理的服务或 a 全部: ").strip().lower()
        if choice == 'q':
            logger.info("退出程序")
            break
        if choice == 'a':
            logger.info("=== 批量操作: 全部服务 ===")
            logger.info("0. 停止")
            logger.info("1. 重启")
            op = get_operation()
            if op == 'q':
                continue
            action_nginx = 'stop' if op == 0 else 'restart'
            action_others = 'down' if op == 0 else 'restart'
            commands = [
                ("Nginx", f"sudo systemctl {action_nginx} nginx"),
                ("Homepage", f"cd {os.path.expanduser('~/web/homepageService')} && docker compose {action_others}"),
                ("Status", f"cd {os.path.expanduser('~/web/statusService')} && docker compose {action_others}"),
                ("Gitea", f"cd {os.path.expanduser('~/web/giteaService')} && docker compose {action_others}"),
            ]
            for name, cmd in commands:
                try:
                    logger.info(f"{name} 开始 {('停止' if op==0 else '重启')}")
                    subprocess.run(cmd, shell=True, check=True)
                    logger.info(f"{name} 完成")
                except subprocess.CalledProcessError as e:
                    logger.error(f"{name} 操作失败: {e}")
            continue

        try:
            idx = int(choice)
            if idx in services:
                cont = services[idx][1]()
                if cont is False:
                    continue
            else:
                logger.warning("无效选项")
        except ValueError:
            logger.warning("无效输入，请输入数字或 q")

    return 0

if __name__ == "__main__":
    sys.exit(main())
