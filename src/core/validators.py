"""
验证器模块
提供数据验证工具函数

主要功能:
    - 交易方向验证
    - 订单类型验证
    - 订单状态验证
    - 数值范围验证
"""
from typing import Tuple, Optional


class ValidationError(Exception):
    """验证错误异常"""
    pass


def validate_direction(direction: str, allowed: Tuple[str, ...]) -> str:
    """
    验证交易方向
    
    参数:
        direction: 待验证的方向字符串
        allowed: 允许的方向元组，如 ('long', 'short') 或 ('buy', 'sell')
    
    返回:
        str: 验证通过的方向字符串
    
    抛出:
        ValidationError: 方向不在允许范围内
    
    示例:
        >>> validate_direction('long', ('long', 'short'))
        'long'
        >>> validate_direction('buy', ('buy', 'sell'))
        'buy'
    """
    if direction not in allowed:
        allowed_str = ', '.join(f"'{d}'" for d in allowed)
        raise ValidationError(
            f"direction must be one of {allowed_str}, got '{direction}'"
        )
    return direction


def validate_order_type(order_type: str) -> str:
    """
    验证订单类型
    
    参数:
        order_type: 订单类型字符串
    
    返回:
        str: 验证通过的订单类型
    
    抛出:
        ValidationError: 订单类型无效
    
    示例:
        >>> validate_order_type('market')
        'market'
        >>> validate_order_type('limit')
        'limit'
    """
    allowed = ('market', 'limit')
    if order_type not in allowed:
        raise ValidationError(
            f"order_type must be 'market' or 'limit', got '{order_type}'"
        )
    return order_type


def validate_order_status(status: str) -> str:
    """
    验证订单状态
    
    参数:
        status: 订单状态字符串
    
    返回:
        str: 验证通过的订单状态
    
    抛出:
        ValidationError: 订单状态无效
    
    示例:
        >>> validate_order_status('pending')
        'pending'
        >>> validate_order_status('filled')
        'filled'
    """
    allowed = ('pending', 'filled', 'cancelled', 'rejected')
    if status not in allowed:
        raise ValidationError(f"Invalid status: {status}")
    return status


def validate_positive(value: float, field_name: str) -> float:
    """
    验证正数
    
    参数:
        value: 待验证的数值
        field_name: 字段名称（用于错误信息）
    
    返回:
        float: 验证通过的数值
    
    抛出:
        ValidationError: 数值不是正数
    
    示例:
        >>> validate_positive(100.0, 'price')
        100.0
        >>> validate_positive(100, 'quantity')
        100
    """
    if value <= 0:
        raise ValidationError(
            f"{field_name} must be positive, got {value}"
        )
    return value


def validate_range(
    value: float,
    min_val: float,
    max_val: float,
    field_name: str
) -> float:
    """
    验证数值范围
    
    参数:
        value: 待验证的数值
        min_val: 最小值
        max_val: 最大值
        field_name: 字段名称（用于错误信息）
    
    返回:
        float: 验证通过的数值
    
    抛出:
        ValidationError: 数值不在范围内
    
    示例:
        >>> validate_range(0.5, 0.0, 1.0, 'strength')
        0.5
    """
    if not min_val <= value <= max_val:
        raise ValidationError(
            f"{field_name} must be between {min_val} and {max_val}, got {value}"
        )
    return value


def validate_stock_code(stock_code: str) -> str:
    """
    验证股票代码格式
    
    参数:
        stock_code: 股票代码字符串
    
    返回:
        str: 验证通过的股票代码
    
    抛出:
        ValidationError: 股票代码格式无效
    
    示例:
        >>> validate_stock_code('000001.SZ')
        '000001.SZ'
        >>> validate_stock_code('600000.SH')
        '600000.SH'
    """
    if not stock_code or not isinstance(stock_code, str):
        raise ValidationError(f"Invalid stock code: {stock_code}")
    
    # 基本格式检查：6位数字 + 交易所后缀
    parts = stock_code.split('.')
    if len(parts) != 2:
        raise ValidationError(
            f"stock_code must be in format 'XXXXXX.EXCHANGE', got '{stock_code}'"
        )
    
    code, exchange = parts
    if not code.isdigit() or len(code) != 6:
        raise ValidationError(
            f"stock code must be 6 digits, got '{code}'"
        )
    
    valid_exchanges = ('SZ', 'SH', 'BJ')
    if exchange.upper() not in valid_exchanges:
        raise ValidationError(
            f"exchange must be one of {valid_exchanges}, got '{exchange}'"
        )
    
    return stock_code
