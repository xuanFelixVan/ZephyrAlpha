"""
异常定义单元测试
"""
import pytest

from src.core.exceptions import (
    SystemException,
    DataException,
    FactorException,
    StrategyException,
    RiskException,
    ExecutionException,
    ConfigurationException,
    ValidationException,
)


class TestSystemException:
    """测试 SystemException 基类"""

    def test_basic_exception(self):
        """测试基本异常"""
        exc = SystemException("Test error")
        assert exc.message == "Test error"
        assert exc.code is None

    def test_with_code(self):
        """测试带错误码的异常"""
        exc = SystemException("Test error", code=100)
        assert exc.message == "Test error"
        assert exc.code == 100

    def test_repr(self):
        """测试字符串表示"""
        exc = SystemException("Test error", code=100)
        assert "SystemException" in repr(exc)
        assert "100" in repr(exc)

    def test_repr_without_code(self):
        """测试无错误码的字符串表示"""
        exc = SystemException("Test error")
        assert "SystemException" in repr(exc)
        assert "code=" not in repr(exc)

    def test_str(self):
        """测试字符串转换"""
        exc = SystemException("Test error")
        assert str(exc) == "Test error"

    def test_inheritance(self):
        """测试继承"""
        assert issubclass(SystemException, Exception)


class TestDataException:
    """测试 DataException"""

    def test_default_code(self):
        """测试默认错误码"""
        exc = DataException("Data error")
        assert exc.code == 1001

    def test_custom_code(self):
        """测试自定义错误码"""
        exc = DataException("Data error", code=1002)
        assert exc.code == 1002

    def test_inheritance(self):
        """测试继承"""
        assert issubclass(DataException, SystemException)


class TestFactorException:
    """测试 FactorException"""

    def test_default_code(self):
        """测试默认错误码"""
        exc = FactorException("Factor error")
        assert exc.code == 2001

    def test_custom_code(self):
        """测试自定义错误码"""
        exc = FactorException("Factor error", code=2002)
        assert exc.code == 2002

    def test_inheritance(self):
        """测试继承"""
        assert issubclass(FactorException, SystemException)


class TestStrategyException:
    """测试 StrategyException"""

    def test_default_code(self):
        """测试默认错误码"""
        exc = StrategyException("Strategy error")
        assert exc.code == 3001

    def test_custom_code(self):
        """测试自定义错误码"""
        exc = StrategyException("Strategy error", code=3002)
        assert exc.code == 3002

    def test_inheritance(self):
        """测试继承"""
        assert issubclass(StrategyException, SystemException)


class TestRiskException:
    """测试 RiskException"""

    def test_default_code(self):
        """测试默认错误码"""
        exc = RiskException("Risk error")
        assert exc.code == 4001

    def test_custom_code(self):
        """测试自定义错误码"""
        exc = RiskException("Risk error", code=4002)
        assert exc.code == 4002

    def test_inheritance(self):
        """测试继承"""
        assert issubclass(RiskException, SystemException)


class TestExecutionException:
    """测试 ExecutionException"""

    def test_default_code(self):
        """测试默认错误码"""
        exc = ExecutionException("Execution error")
        assert exc.code == 5001

    def test_custom_code(self):
        """测试自定义错误码"""
        exc = ExecutionException("Execution error", code=5002)
        assert exc.code == 5002

    def test_inheritance(self):
        """测试继承"""
        assert issubclass(ExecutionException, SystemException)


class TestConfigurationException:
    """测试 ConfigurationException"""

    def test_default_code(self):
        """测试默认错误码"""
        exc = ConfigurationException("Config error")
        assert exc.code == 6001

    def test_custom_code(self):
        """测试自定义错误码"""
        exc = ConfigurationException("Config error", code=6002)
        assert exc.code == 6002

    def test_inheritance(self):
        """测试继承"""
        assert issubclass(ConfigurationException, SystemException)


class TestValidationException:
    """测试 ValidationException"""

    def test_default_code(self):
        """测试默认错误码"""
        exc = ValidationException("Validation error")
        assert exc.code == 7001

    def test_custom_code(self):
        """测试自定义错误码"""
        exc = ValidationException("Validation error", code=7002)
        assert exc.code == 7002

    def test_inheritance(self):
        """测试继承"""
        assert issubclass(ValidationException, SystemException)


class TestExceptionCodeRanges:
    """测试异常错误码范围"""

    def test_data_exception_code_range(self):
        """测试 DataException 错误码范围"""
        exc = DataException("test")
        assert 1000 <= exc.code < 2000

    def test_factor_exception_code_range(self):
        """测试 FactorException 错误码范围"""
        exc = FactorException("test")
        assert 2000 <= exc.code < 3000

    def test_strategy_exception_code_range(self):
        """测试 StrategyException 错误码范围"""
        exc = StrategyException("test")
        assert 3000 <= exc.code < 4000

    def test_risk_exception_code_range(self):
        """测试 RiskException 错误码范围"""
        exc = RiskException("test")
        assert 4000 <= exc.code < 5000

    def test_execution_exception_code_range(self):
        """测试 ExecutionException 错误码范围"""
        exc = ExecutionException("test")
        assert 5000 <= exc.code < 6000

    def test_configuration_exception_code_range(self):
        """测试 ConfigurationException 错误码范围"""
        exc = ConfigurationException("test")
        assert 6000 <= exc.code < 7000

    def test_validation_exception_code_range(self):
        """测试 ValidationException 错误码范围"""
        exc = ValidationException("test")
        assert 7000 <= exc.code < 8000


class TestExceptionCatching:
    """测试异常捕获"""

    def test_catch_system_exception(self):
        """测试捕获 SystemException"""
        with pytest.raises(SystemException):
            raise SystemException("Test")

    def test_catch_data_exception_as_system(self):
        """测试将 DataException 作为 SystemException 捕获"""
        with pytest.raises(SystemException):
            raise DataException("Data error")

    def test_catch_all_quant_exceptions(self):
        """测试捕获所有量化异常"""
        exceptions = [
            DataException("test"),
            FactorException("test"),
            StrategyException("test"),
            RiskException("test"),
            ExecutionException("test"),
        ]

        for exc in exceptions:
            with pytest.raises(SystemException):
                raise exc
