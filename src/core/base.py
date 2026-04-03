"""
核心基础类
定义清风量化交易系统的核心数据结构

主要类:
    Result - 统一返回格式

向后兼容导入:
    Signal, Order, Position - 从 trading_entities 模块导入
"""
from dataclasses import dataclass, field
from typing import Any, Optional, Dict


@dataclass
class Result:
    """
    统一返回格式
    
    用于函数返回值封装，提供成功/失败状态、数据和错误信息。
    这是系统中最基础的通用数据结构，所有模块都应使用此类封装返回值。
    
    属性:
        success: 操作是否成功
        data: 返回的数据 (任意类型)
        error: 错误信息 (失败时提供)
        metadata: 元数据字典 (可选的附加信息)
    
    设计理念:
        - 统一返回格式，简化错误处理
        - 支持链式调用和流畅接口
        - 提供便捷的成功/失败检查方法
    
    示例:
        >>> # 成功返回
        >>> result = Result(success=True, data={"price": 100.0})
        >>> if result.is_success:
        ...     print(f"价格: {result.data['price']}")
        价格: 100.0
        
        >>> # 失败返回
        >>> result = Result(success=False, error="数据加载失败")
        >>> if result.is_failure:
        ...     print(f"错误: {result.error}")
        错误: 数据加载失败
        
        >>> # 带元数据
        >>> result = Result(
        ...     success=True,
        ...     data={"items": [1, 2, 3]},
        ...     metadata={"count": 3, "source": "database"}
        ... )
    
    最佳实践:
        - 成功时: Result(success=True, data=...)
        - 失败时: Result(success=False, error="错误描述")
        - 使用 is_success 和 is_failure 属性检查状态
        - 在 metadata 中存储额外信息 (如时间戳、来源等)
    
    注意:
        - 不要同时设置 data 和 error
        - metadata 应该只包含辅助信息，不应包含核心数据
        - 建议在 metadata 中包含时间戳、来源、版本等信息
    """
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

    def __post_init__(self):
        """初始化后处理"""
        if self.metadata is None:
            self.metadata = {}

    @property
    def is_success(self) -> bool:
        """
        检查操作是否成功
        
        返回:
            bool: True表示成功，False表示失败
        """
        return self.success

    @property
    def is_failure(self) -> bool:
        """
        检查操作是否失败
        
        返回:
            bool: True表示失败，False表示成功
        """
        return not self.success

    def get_data(self, key: str = None, default: Any = None) -> Any:
        """
        获取数据
        
        参数:
            key: 数据键名 (如果data是字典)
            default: 默认值
        
        返回:
            Any: 数据值或默认值
        
        示例:
            >>> result = Result(success=True, data={"price": 100.0})
            >>> result.get_data("price", 0.0)
            100.0
            >>> result.get_data("volume", 0)
            0
        """
        if not self.success:
            return default
        
        if key is None:
            return self.data
        
        if isinstance(self.data, dict):
            return self.data.get(key, default)
        
        return default

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        获取元数据
        
        参数:
            key: 元数据键名
            default: 默认值
        
        返回:
            Any: 元数据值或默认值
        
        示例:
            >>> result = Result(
            ...     success=True,
            ...     data={"price": 100.0},
            ...     metadata={"source": "api", "timestamp": "2026-04-02"}
            ... )
            >>> result.get_metadata("source", "unknown")
            'api'
        """
        return self.metadata.get(key, default)

    @classmethod
    def ok(cls, data: Any = None, **metadata) -> 'Result':
        """
        创建成功结果 (类方法)
        
        参数:
            data: 返回数据
            **metadata: 元数据键值对
        
        返回:
            Result: 成功的结果对象
        
        示例:
            >>> result = Result.ok({"price": 100.0}, source="api")
            >>> result.is_success
            True
        """
        return cls(success=True, data=data, metadata=metadata)

    @classmethod
    def fail(cls, error: str, **metadata) -> 'Result':
        """
        创建失败结果 (类方法)
        
        参数:
            error: 错误信息
            **metadata: 元数据键值对
        
        返回:
            Result: 失败的结果对象
        
        示例:
            >>> result = Result.fail("数据加载失败", code=500)
            >>> result.is_failure
            True
        """
        return cls(success=False, error=error, metadata=metadata)


# 向后兼容导入
# 为了保持向后兼容性，从 trading_entities 模块导入这些类
# 新代码应直接从 src.core.trading_entities 导入
from src.core.trading_entities import Signal, Order, Position

__all__ = ['Result', 'Signal', 'Order', 'Position']
