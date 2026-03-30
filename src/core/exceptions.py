"""
异常定义模块
定义清风量化交易系统的所有异常类型

异常层次结构:
    SystemException (基类)
    ├── DataException (数据异常)
    ├── FactorException (因子异常)
    ├── StrategyException (策略异常)
    ├── RiskException (风险异常)
    └── ExecutionException (执行异常)
"""


class SystemException(Exception):
    """系统异常基类

    所有自定义异常的基类，提供统一的异常处理接口。

    属性:
        message: 错误消息
        code: 错误码 (可选)
    """

    def __init__(self, message: str, code: int = None):
        self.message = message
        self.code = code
        super().__init__(self.message)

    def __repr__(self) -> str:
        if self.code is not None:
            return f"{self.__class__.__name__}(code={self.code}, message='{self.message}')"
        return f"{self.__class__.__name__}(message='{self.message}')"


class DataException(SystemException):
    """数据异常

    数据获取、清洗、存储过程中的异常。

    常见场景:
        - 数据源连接失败
        - 数据格式错误
        - 数据缺失
        - 数据校验失败
    """

    def __init__(self, message: str, code: int = 1001):
        super().__init__(message, code)


class FactorException(SystemException):
    """因子异常

    因子计算、因子注册过程中的异常。

    常见场景:
        - 因子计算失败
        - 因子参数无效
        - 因子不存在
        - 因子重复注册
    """

    def __init__(self, message: str, code: int = 2001):
        super().__init__(message, code)


class StrategyException(SystemException):
    """策略异常

    策略执行、策略验证过程中的异常。

    常见场景:
        - 策略信号生成失败
        - 策略参数无效
        - 策略回测失败
        - 策略资金不足
    """

    def __init__(self, message: str, code: int = 3001):
        super().__init__(message, code)


class RiskException(SystemException):
    """风险异常

    风险控制、风控规则触发过程中的异常。

    常见场景:
        - 风控规则触发
        - 仓位超限
        - 止损触发
        - 风险敞口超限
    """

    def __init__(self, message: str, code: int = 4001):
        super().__init__(message, code)


class ExecutionException(SystemException):
    """执行异常

    订单执行、交易执行过程中的异常。

    常见场景:
        - 订单提交失败
        - 订单成交失败
        - 交易所连接失败
        - 持仓更新失败
    """

    def __init__(self, message: str, code: int = 5001):
        super().__init__(message, code)


class ConfigurationException(SystemException):
    """配置异常

    配置文件加载、验证过程中的异常。

    常见场景:
        - 配置文件不存在
        - 配置文件格式错误
        - 配置项缺失
        - 配置项值无效
    """

    def __init__(self, message: str, code: int = 6001):
        super().__init__(message, code)


class ValidationException(SystemException):
    """验证异常

    数据验证、输入验证过程中的异常。

    常见场景:
        - 输入参数校验失败
        - 数据范围校验失败
        - 格式校验失败
    """

    def __init__(self, message: str, code: int = 7001):
        super().__init__(message, code)
