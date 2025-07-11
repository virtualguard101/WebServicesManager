import unittest
from unittest.mock import patch, MagicMock
from src.services import Service, SystemServiceStrategy, DockerServiceStrategy, get_operation
import os
import subprocess

class TestService(unittest.TestCase):
    def test_service_initialization(self):
        """测试服务初始化"""
        service = Service(tag="sys", name="nginx")
        self.assertEqual(service.tag, "sys")
        self.assertEqual(service.name, "nginx")
        self.assertIsNone(service.path)

    def test_docker_service_initialization(self):
        """测试Docker服务初始化"""
        service = Service(tag="docker", name="homepage", path="/path/to/docker")
        self.assertEqual(service.tag, "docker")
        self.assertEqual(service.name, "homepage")
        self.assertEqual(service.path, "/path/to/docker")

    def test_invalid_tag(self):
        """测试无效标签"""
        with self.assertRaises(ValueError):
            Service(tag="invalid", name="invalid")

    def test_to_dict(self):
        """测试字典转换"""
        service = Service(tag="sys", name="nginx")
        result = service.to_dict()
        self.assertEqual(result, {
            "tag": "sys",
            "name": "nginx",
            "path": None
        })

class TestSystemServiceStrategy(unittest.TestCase):
    def test_generate_stop_command(self):
        """测试生成停止命令"""
        strategy = SystemServiceStrategy()
        command = strategy.generate_command(0, "nginx")
        self.assertEqual(command, ["sudo", "systemctl", "stop", "nginx"])

    def test_generate_restart_command(self):
        """测试生成重启命令"""
        strategy = SystemServiceStrategy()
        command = strategy.generate_command(1, "nginx")
        self.assertEqual(command, ["sudo", "systemctl", "restart", "nginx"])

    def test_invalid_operation(self):
        """测试无效操作"""
        strategy = SystemServiceStrategy()
        with self.assertRaises(ValueError):
            strategy.generate_command(2, "nginx")

    @patch("subprocess.run")
    def test_execute_command(self, mock_run):
        """测试命令执行"""
        strategy = SystemServiceStrategy()
        command = ["sudo", "systemctl", "stop", "nginx"]
        strategy.execute(command)
        mock_run.assert_called_with(command, check=True)

class TestDockerServiceStrategy(unittest.TestCase):
    def setUp(self):
        self.path = "/path/to/docker"
        self.strategy = DockerServiceStrategy(self.path)
        os.path.exists = MagicMock(return_value=True)
        os.path.isdir = MagicMock(return_value=True)

    def test_generate_down_command(self):
        """测试生成停止命令"""
        command = self.strategy.generate_command(0, "homepage")
        self.assertEqual(command, ["docker", "compose", "down"])

    def test_generate_up_command(self):
        """测试生成启动命令"""
        command = self.strategy.generate_command(1, "homepage")
        self.assertEqual(command, ["docker", "compose", "up", "-d"])

    def test_missing_path(self):
        """测试路径为空字符串"""
        strategy = DockerServiceStrategy("")
        with self.assertRaises(ValueError):
            strategy.generate_command(0, "homepage")

    @patch("os.path.exists", return_value=False)
    def test_path_not_found(self, mock_exists):
        """测试路径不存在"""
        with self.assertRaises(FileNotFoundError):
            self.strategy.generate_command(0, "homepage")

    @patch("subprocess.run")
    @patch("os.path.exists", return_value=True)
    @patch("os.path.isdir", return_value=True)
    def test_execute_command(self, mock_isdir, mock_exists, mock_run):
        """测试命令执行"""
        command = ["docker", "compose", "down"]
        self.strategy.execute(command)
        mock_run.assert_called_with(command, check=True, cwd="/path/to/docker")

class TestServiceOperation(unittest.TestCase):
    @patch("builtins.input", side_effect=["0"])
    def test_get_operation_stop(self, mock_input):
        """测试获取停止操作"""
        result = get_operation()
        self.assertEqual(result, 0)

    @patch("builtins.input", side_effect=["1"])
    def test_get_operation_restart(self, mock_input):
        """测试获取重启操作"""
        result = get_operation()
        self.assertEqual(result, 1)

    @patch("builtins.input", side_effect=["q"])
    def test_get_operation_quit(self, mock_input):
        """测试退出操作"""
        result = get_operation()
        self.assertIsNone(result)

    @patch("builtins.input", side_effect=["invalid", "0"])
    @patch("src.services.logger.warning")
    def test_invalid_input(self, mock_warning, mock_input):
        """测试无效输入"""
        result = get_operation()
        self.assertEqual(result, 0)
        mock_warning.assert_called()

    @patch("src.services.get_operation", return_value=0)
    @patch("src.services.SystemServiceStrategy.generate_command", return_value=["sudo", "systemctl", "stop", "nginx"])
    @patch("src.services.SystemServiceStrategy.execute")
    @patch("src.services.logger.info")
    @patch("src.services.SystemServiceStrategy.execute")
    @patch("src.services.SystemServiceStrategy.generate_command")
    @patch("src.services.get_operation", return_value=0)
    def test_service_operation(self, mock_get_operation, mock_generate, mock_execute, mock_info):
        """测试服务操作流程"""
        service = Service(tag="sys", name="nginx")
        service.service_operation()
        
        # 修复：generate_command 需要 self 参数
        mock_generate.assert_called_with(0, "nginx", None)
        mock_execute.assert_called_with(["sudo", "systemctl", "stop", "nginx"])
        mock_info.assert_any_call("Executing: sudo systemctl stop nginx")
        mock_info.assert_any_call("Service nginx operation completed")
        mock_info.assert_any_call("Executing: sudo systemctl stop nginx")
        mock_info.assert_any_call("Service nginx operation completed")

if __name__ == "__main__":
    unittest.main()