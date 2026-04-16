"""
引擎工厂类
负责创建和管理不同交易引擎实例
"""

from typing import Dict, Any, Type
import logging

from .base import BaseEngineAdapter, EngineConfig
from .backtesting_adapter import BacktestingPyAdapter


logger = logging.getLogger(__name__)


class EngineFactory:
    """引擎工厂

    支持引擎类型：
    - backtesting: backtesting.py轻量级回测引擎
    - vnpy: vn.py生产级交易引擎
    - rqalpha: RQAlpha专业回测引擎
    - backtrader: Backtrader功能补充引擎
    - qmt: 迅投QMT券商官方引擎

    使用示例：
        config = EngineConfig(engine_type="backtesting", config={...})
        engine = EngineFactory.create_engine(config)
    """

    # 引擎类型到适配器类的映射
    _engine_registry: Dict[str, Type[BaseEngineAdapter]] = {
        "backtesting": BacktestingPyAdapter,
        # 其他引擎占位符（待实现）
        "vnpy": None,      # VnPyAdapter (待实现)
        "rqalpha": None,   # RQAlphaAdapter (待实现)
        "backtrader": None, # BacktraderAdapter (待实现)
        "qmt": None,       # QMTAdapter (待实现)
    }

    @classmethod
    def register_engine(cls, engine_type: str, adapter_class: Type[BaseEngineAdapter]):
        """注册新的引擎类型"""
        if engine_type in cls._engine_registry:
            logger.warning(f"引擎类型 {engine_type} 已存在，将被覆盖")
        cls._engine_registry[engine_type] = adapter_class
        logger.info(f"引擎类型 {engine_type} 注册成功")

    @classmethod
    def create_engine(cls, config: EngineConfig) -> BaseEngineAdapter:
        """创建引擎实例

        Args:
            config: 引擎配置

        Returns:
            引擎适配器实例

        Raises:
            ValueError: 不支持的引擎类型
            ImportError: 引擎依赖未安装
        """
        engine_type = config.engine_type.lower()

        # 检查引擎类型是否支持
        if engine_type not in cls._engine_registry:
            raise ValueError(f"不支持的引擎类型: {engine_type}。"
                           f"支持的类型: {list(cls._engine_registry.keys())}")

        # 获取适配器类
        adapter_class = cls._engine_registry[engine_type]
        if adapter_class is None:
            raise NotImplementedError(f"引擎类型 {engine_type} 的适配器尚未实现")

        try:
            # 创建引擎实例
            engine = adapter_class(config)
            logger.info(f"引擎 {engine_type} 创建成功")
            return engine

        except ImportError as e:
            logger.error(f"引擎 {engine_type} 依赖未安装: {e}")
            raise ImportError(f"请安装 {engine_type} 引擎的依赖包") from e
        except Exception as e:
            logger.error(f"创建引擎 {engine_type} 失败: {e}")
            raise

    @classmethod
    def get_supported_engines(cls) -> Dict[str, Dict[str, Any]]:
        """获取支持的引擎信息"""
        engine_info = {}
        for engine_type, adapter_class in cls._engine_registry.items():
            if adapter_class is None:
                status = "未实现"
            else:
                try:
                    # 尝试创建临时实例检查可用性
                    temp_config = EngineConfig(engine_type=engine_type, config={})
                    engine = adapter_class(temp_config)
                    status = "可用"
                    ashare_compatible = engine.is_ashare_compatible()
                except ImportError:
                    status = "依赖未安装"
                    ashare_compatible = False
                except Exception:
                    status = "初始化失败"
                    ashare_compatible = False

            engine_info[engine_type] = {
                "status": status,
                "ashare_compatible": ashare_compatible,
                "description": cls._get_engine_description(engine_type),
            }

        return engine_info

    @classmethod
    def _get_engine_description(cls, engine_type: str) -> str:
        """获取引擎描述"""
        descriptions = {
            "backtesting": "轻量级向量化回测引擎，适合快速策略验证",
            "vnpy": "生产级A股交易引擎，支持实盘和模拟",
            "rqalpha": "专业回测引擎，避免未来函数，支持多因子",
            "backtrader": "功能全面的回测框架，支持多资产和复杂策略",
            "qmt": "迅投券商官方引擎，支持A股实盘交易",
        }
        return descriptions.get(engine_type, "未知引擎类型")

    @classmethod
    def create_multi_engine_orchestrator(cls, configs: Dict[str, Dict[str, Any]]):
        """创建多引擎协调器

        Args:
            configs: 引擎配置字典 {engine_id: {engine_type: ..., config: ...}}

        Returns:
            多引擎协调器实例
        """
        # TODO: 实现多引擎协调器
        raise NotImplementedError("多引擎协调器尚未实现")


def create_backtesting_engine(initial_capital: float = 1000000.0,
                             commission_rate: float = 0.0003,
                             **kwargs) -> BacktestingPyAdapter:
    """快速创建backtesting.py引擎的便捷函数"""
    config = EngineConfig(
        engine_type="backtesting",
        config=kwargs,
        initial_capital=initial_capital,
        commission_rate=commission_rate,
    )
    return EngineFactory.create_engine(config)
