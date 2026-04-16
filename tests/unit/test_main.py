"""
主模块单元测试
"""
import pytest
import sys
from unittest.mock import patch
from io import StringIO

from src.main import main


class TestMain:
    """测试主入口函数"""

    def test_main_returns_result(self):
        """测试main函数返回Result对象"""
        result = main()

        assert result.success is True
        assert result.data == {"version": "5.0.0"}
        assert result.error is None

    def test_main_output(self, capsys):
        """测试main函数输出内容"""
        main()
        captured = capsys.readouterr()
        output = captured.out

        # 检查标题和版本信息
        assert "清风量化交易系统 v5.1" in output
        assert "=" * 60 in output

        # 检查模块列表
        assert "factor_calculator" in output
        assert "risk_manager" in output
        assert "alert_manager" in output

        # 检查文档引用
        assert "System_Manifest.md" in output

    def test_main_module_import(self):
        """测试模块导入时不执行main函数"""
        # 导入模块本身不应执行main函数
        # 这个测试验证模块可以正常导入
        import src.main
        assert hasattr(src.main, 'main')
        assert callable(src.main.main)

    @patch('sys.stdout', new_callable=StringIO)
    def test_main_stdout_redirect(self, mock_stdout):
        """测试main函数输出到stdout"""
        main()
        output = mock_stdout.getvalue()

        assert "清风量化交易系统 v5.1" in output
        assert len(output) > 100  # 确保有足够的输出内容

    def test_main_path_setup(self):
        """测试模块导入时的路径设置"""
        # 验证sys.path设置
        import src.main
        # 检查项目根目录是否在sys.path中
        project_root = str(src.main.project_root)
        assert project_root in sys.path
        # 检查它在列表的开头（索引0）
        assert sys.path[0] == project_root
