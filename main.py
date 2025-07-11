#!/usr/bin/env python3

import argparse
import json
import os
from src.manager import ServiceFactory, ServiceRepository, Manager
from src.services import DockerServiceStrategy, SystemServiceStrategy

def main():
    parser = argparse.ArgumentParser(description="服务管理工具")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # 注册服务命令
    register_parser = subparsers.add_parser("register", help="注册新服务")
    register_parser.add_argument("tag", choices=["sys", "docker"], help="服务类型")
    register_parser.add_argument("name", help="服务名称")
    register_parser.add_argument("--path", help="Docker服务路径（仅docker类型需要）")
    
    # 列出服务命令
    subparsers.add_parser("list", help="列出所有服务")
    
    # 执行操作命令
    operate_parser = subparsers.add_parser("operate", help="执行服务操作")
    operate_parser.add_argument("index", type=int, help="服务索引")
    
    args = parser.parse_args()
    
    # 初始化仓库和管理器
    # 确保 data 目录存在
    os.makedirs("data", exist_ok=True)
    repo = ServiceRepository("data/services.json")
    manager = Manager(repo)
    
    if args.command == "register":
        # 创建服务
        service = manager.register_service(args.tag, args.name, args.path)
        print(f"服务注册成功: {service.name}")
        
    elif args.command == "list":
        # 列出所有服务
        services = manager.list_services()
        for i, service in enumerate(services):
            print(f"{i}: [{service.tag}] {service.name} {f'(path: {service.path})' if service.path else ''}")
            
    elif args.command == "operate":
        # 执行服务操作
        try:
            manager.execute_service_operation(args.index)
            print("操作执行成功")
        except IndexError:
            print("错误：无效的服务索引")
        except Exception as e:
            print(f"操作失败: {str(e)}")

if __name__ == "__main__":
    main()
