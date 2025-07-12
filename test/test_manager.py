import unittest
from unittest.mock import patch, MagicMock
from src.manager import ServiceFactory, ServiceRepository, Manager
import os
import json
import tempfile

class TestServiceFactory(unittest.TestCase):
    def test_create_valid_service(self):
        """测试创建有效的服务"""
        factory = ServiceFactory()
        service = factory.create_service("sys", "nginx")
        self.assertEqual(service.tag, "sys")
        self.assertEqual(service.name, "nginx")
        self.assertIsNone(service.path)

    def test_create_invalid_tag(self):
        """测试创建无效标签的服务"""
        factory = ServiceFactory()
        with self.assertRaises(ValueError):
            factory.create_service("invalid", "invalid_service")

class TestServiceRepository(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        # 在临时目录下创建 data 子目录
        data_dir = os.path.join(self.temp_dir.name, "data")
        os.makedirs(data_dir, exist_ok=True)
        self.repo_path = os.path.join(data_dir, "services.json")
        self.repo = ServiceRepository(self.repo_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_save_and_load(self):
        """测试服务保存和加载"""
        # 创建模拟服务
        mock_service = MagicMock()
        mock_service.to_dict.return_value = {
            "tag": "sys",
            "name": "nginx",
            "path": None
        }
        
        # 保存服务
        self.repo.save(mock_service)
        
        # 加载服务
        services = self.repo.load_all()
        
        # 验证加载结果
        self.assertEqual(len(services), 1)
        self.assertEqual(services[0]["tag"], "sys")
        self.assertEqual(services[0]["name"], "nginx")

    def test_load_invalid_file(self):
        """测试加载无效JSON文件"""
        with open(self.repo_path, "w") as f:
            f.write("invalid json")
        
        services = self.repo.load_all()
        self.assertEqual(len(services), 0)
        
    def test_remove_service_success(self):
        """测试正常移除服务"""
        # 添加测试服务
        mock_service = MagicMock()
        mock_service.to_dict.return_value = {
            "tag": "sys",
            "name": "nginx",
            "path": None
        }
        self.repo.save(mock_service)
        
        # 移除服务
        self.repo.remove("nginx")
        
        # 验证服务已被移除
        services = self.repo.load_all()
        self.assertEqual(len(services), 0)
        
    def test_remove_service_case_insensitive(self):
        """测试大小写不敏感移除"""
        # 添加测试服务
        mock_service = MagicMock()
        mock_service.to_dict.return_value = {
            "tag": "sys",
            "name": "Nginx",
            "path": None
        }
        self.repo.save(mock_service)
        
        # 使用小写名称移除
        self.repo.remove("nginx")
        
        # 验证服务已被移除
        services = self.repo.load_all()
        self.assertEqual(len(services), 0)
        
    def test_remove_service_whitespace(self):
        """测试移除带空格的服务名"""
        # 添加测试服务
        mock_service = MagicMock()
        mock_service.to_dict.return_value = {
            "tag": "sys",
            "name": " nginx ",
            "path": None
        }
        self.repo.save(mock_service)
        
        # 使用带空格名称移除
        self.repo.remove("  nginx  ")
        
        # 验证服务已被移除
        services = self.repo.load_all()
        self.assertEqual(len(services), 0)
        
    def test_remove_nonexistent_service(self):
        """测试移除不存在的服务"""
        with self.assertRaises(ValueError):
            self.repo.remove("nonexistent")

class TestManager(unittest.TestCase):
    @patch("src.manager.ServiceRepository")
    @patch("src.manager.ServiceFactory")
    def test_register_service(self, mock_factory, mock_repo):
        """测试服务注册"""
        # 准备模拟对象
        mock_service = MagicMock()
        mock_factory.return_value.create_service.return_value = mock_service
        mock_repo_instance = MagicMock()
        
        # 创建管理器
        manager = Manager(mock_repo.return_value)
        
        # 注册服务
        service = manager.register_service("sys", "nginx")
        
        # 验证调用
        mock_factory.return_value.create_service.assert_called_with("sys", "nginx", None)
        mock_repo.return_value.save.assert_called_with(mock_service)
        self.assertEqual(service, mock_service)

    @patch("src.manager.ServiceRepository")
    def test_list_services(self, mock_repo):
        """测试服务列表"""
        # 准备模拟服务
        mock_service1 = MagicMock()
        mock_service1.name = "nginx"
        mock_service2 = MagicMock()
        mock_service2.name = "postgres"
        
        # 创建管理器
        manager = Manager(mock_repo.return_value)
        mock_repo.return_value.load_all.return_value = [
            {"tag": "sys", "name": "nginx", "path": None},
            {"tag": "docker", "name": "postgres", "path": "/path/to/docker"}
        ]
        
        # 获取服务列表
        services = manager.list_services()
        
        # 验证结果
        # 修复预期服务数量
        self.assertEqual(len(services), 2)
        self.assertEqual(services[0].name, "nginx")
        self.assertEqual(services[1].name, "postgres")
        
    @patch("src.manager.ServiceRepository")
    @patch("src.manager.Service")
    @patch("src.services.get_operation", return_value=1)
    def test_execute_service_operation(self, mock_get_operation, mock_service, mock_repo):
        """测试服务操作执行"""
        # 准备模拟对象
        manager = Manager(mock_repo.return_value)
        mock_service_instance = MagicMock()
        mock_service.return_value = mock_service_instance
        
        # 模拟服务列表
        with patch.object(manager, 'list_services', return_value=[mock_service_instance]):
            # 执行服务操作
            manager.execute_service_operation(0)  # 执行索引0的服务
        
        # 验证调用
        mock_service_instance.service_operation.assert_called_once()
        
    def test_register_invalid_service(self):
        """测试注册无效服务"""
        manager = Manager(MagicMock())
        with self.assertRaises(ValueError):
            manager.register_service("invalid", "invalid_service")
            
    @patch("src.manager.ServiceRepository")
    def test_remove_service_success(self, mock_repo):
        """测试正常移除服务"""
        manager = Manager(mock_repo.return_value)
        service_name = "nginx"
        
        # 调用remove_service
        manager.remove_service(service_name)
        
        # 验证ServiceRepository的remove方法被正确调用
        mock_repo.return_value.remove.assert_called_once_with(service_name)
        
    @patch("src.manager.ServiceRepository")
    def test_remove_service_case_insensitive(self, mock_repo):
        """测试大小写不敏感移除"""
        manager = Manager(mock_repo.return_value)
        
        # 使用混合大小写
        manager.remove_service("NgInX")
        
        # 验证调用时使用原始大小写
        mock_repo.return_value.remove.assert_called_once_with("NgInX")
        
    @patch("src.manager.ServiceRepository")
    def test_remove_service_nonexistent(self, mock_repo):
        """测试移除不存在的服务"""
        # 设置remove方法抛出ValueError
        mock_repo.return_value.remove.side_effect = ValueError("Service not found")
        manager = Manager(mock_repo.return_value)
        
        with self.assertRaises(ValueError):
            manager.remove_service("nonexistent")
            
    @patch("src.manager.ServiceRepository")
    def test_remove_service_file_not_found(self, mock_repo):
        """测试文件不存在时的错误处理"""
        # 设置remove方法抛出FileNotFoundError
        mock_repo.return_value.remove.side_effect = FileNotFoundError
        manager = Manager(mock_repo.return_value)
        
        with self.assertRaises(FileNotFoundError):
            manager.remove_service("nginx")
            
    @patch("src.manager.ServiceRepository")
    def test_remove_service_invalid_json(self, mock_repo):
        """测试无效JSON文件时的异常处理"""
        # 设置remove方法抛出JSONDecodeError
        mock_repo.return_value.remove.side_effect = json.JSONDecodeError("Expecting value", "", 0)
        manager = Manager(mock_repo.return_value)
        
        with self.assertRaises(json.JSONDecodeError):
            manager.remove_service("nginx")
            
    @patch("src.manager.ServiceRepository")
    @patch("src.manager.logger")
    def test_execute_service_operation_invalid_index(self, mock_logger, mock_repo):
        """测试无效服务索引"""
        manager = Manager(mock_repo.return_value)
        
        # 模拟空服务列表
        with patch.object(manager, 'list_services', return_value=[]):
            with self.assertRaises(IndexError):
                manager.execute_service_operation(0)
                
        # 验证错误日志记录
        mock_logger.error.assert_called_with("Invalid service index: 0")
            

if __name__ == "__main__":
    unittest.main()