#!/usr/bin/env python3

import argparse
import json
import os
from src.manager import ServiceFactory, ServiceRepository, Manager
from src.services import DockerServiceStrategy, SystemServiceStrategy

def main():
    parser = argparse.ArgumentParser(description="=====> Web Services Manager <=====")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # 注册服务命令
    register_parser = subparsers.add_parser("register", help="Register a new service")
    register_parser.add_argument("tag", choices=["sys", "docker"], help="Tag of the service")
    register_parser.add_argument("name", help="Name of the service")
    register_parser.add_argument("--path", help="Config/Data path of the service where the 'docker-compose.yml' located (docker-based services only)")
    
    # 列出服务命令
    subparsers.add_parser("list", help="List all services")
    
    # 执行操作命令
    operate_parser = subparsers.add_parser("operate", help="Service operations to carry out")
    operate_parser.add_argument("index", type=int, help="Index of the service, which is a integer")
    
    # 移除服务命令
    remove_parser = subparsers.add_parser("remove", help="Remove a service")
    remove_parser.add_argument("index", type=int, help="Index of the service to remove")
    
    args = parser.parse_args()
    
    # 初始化仓库和管理器
    # 确保 data 目录存在
    os.makedirs("data", exist_ok=True)
    repo = ServiceRepository("data/services.json")
    manager = Manager(repo)
    
    if args.command == "register":
        # 创建服务
        service = manager.register_service(args.tag, args.name, args.path)
        print(f"Register a new service successfully: {service.name}")
        
    elif args.command == "list":
        # 列出所有服务
        services = manager.list_services()
        for i, service in enumerate(services):
            print(f"{i}: [{service.tag}] {service.name} {f'(path: {service.path})' if service.path else ''}")
            
    elif args.command == "operate":
        # 执行服务操作
        try:
            manager.execute_service_operation(args.index)
            print("Operation success!")
        except IndexError:
            print("Error: invalid index")
        except Exception as e:
            print(f"Operation failed: {str(e)}")
            
    elif args.command == "remove":
        try:
            manager.remove_service(args.index)
            print(f"Service at index {args.index} removed successfully")
        except IndexError:
            print("Error: invalid index")
        except Exception as e:
            print(f"Remove failed: {str(e)}")

if __name__ == "__main__":
    main()
