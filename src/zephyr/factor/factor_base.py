# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] zephyr.factor.factor_base
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.shared.contracts.errors.factor_computation_error
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_factor_base | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: factor
# category: factor_engine
# status: active
# created: "2026-05-04"
# ---
"""
ZephyrAlpha — D_FACTOR Alpha Factor Layer
OCP Extension Point: FactorBase + FactorRegistry

锁定文件（🔒）：任何修改必须先建 KB 决策记录。
参见：KBG-0004 §4（决策范围）

设计原则（Open-Closed Principle）：
  - 扩展方式：继承 FactorBase，实现 compute()，用 @FactorRegistry.register 注册
  - 禁止方式：直接修改本文件中已有的抽象接口
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import ClassVar

import pandas as pd

# ---------------------------------------------------------------------------
# FactorMeta — 因子元数据
# ---------------------------------------------------------------------------


@dataclass
class FactorMeta:
    """因子注册元数据。每个因子类必须定义 meta 类属性。"""

    factor_id: str
    """全局唯一因子 ID，如 'momentum_20d'。"""

    name: str
    """人类可读名称，如 '20日动量因子'。"""

    domain: str
    """所属域，如 'technical' / 'fundamental' / 'alternative' / 'macro'。"""

    version: str = "1.0.0"
    """语义版本号。"""

    description: str = ""
    """因子说明。"""

    dependencies: list[str] = field(default_factory=list)
    """依赖的其他因子 ID 列表（用于计算顺序排序）。"""

    tags: list[str] = field(default_factory=list)
    """标签，如 ['short-term', 'price-action']。"""


# ---------------------------------------------------------------------------
# FactorBase — 因子抽象基类
# ---------------------------------------------------------------------------


class FactorBase(abc.ABC):
    """
    所有 Alpha 因子的抽象基类。

    用法示例：
        @FactorRegistry.register
        class Momentum20d(FactorBase):
            meta = FactorMeta(
                factor_id="momentum_20d",
                name="20日动量因子",
                domain="technical",
            )

            def compute(self, data: pd.DataFrame, **kwargs) -> pd.Series:
                return data["close"].pct_change(20)
    """

    meta: ClassVar[FactorMeta]
    """因子元数据，子类必须定义为类属性。"""

    @abc.abstractmethod
    def compute(self, data: pd.DataFrame, **kwargs) -> pd.Series:
        """
        计算因子值。

        Args:
            data: 输入行情数据，index 为 datetime，columns 至少包含 OHLCV。
            **kwargs: 扩展参数（如自定义窗口期等）。

        Returns:
            pd.Series，index 与 data 对齐，值为因子截面得分。
        """

    def validate(self, data: pd.DataFrame) -> bool:
        """
        （可选覆盖）校验输入数据是否满足本因子的计算前提。

        默认实现：非空即通过。子类可覆盖以增加业务校验。
        """
        return data is not None and not data.empty

    def __repr__(self) -> str:
        return f"<Factor id={self.meta.factor_id} v={self.meta.version}>"


# ---------------------------------------------------------------------------
# FactorRegistry — 因子注册表
# ---------------------------------------------------------------------------


class FactorRegistry:
    """
    因子全局注册表（单例）。

    注册表提供：
      - @FactorRegistry.register 装饰器自动注册
      - get(factor_id) 按 ID 查询
      - list_all() 列出全部因子元数据
      - list_by_domain(domain) 按域过滤
      - clear() 测试用，清空注册表
    """

    _registry: ClassVar[dict[str, type[FactorBase]]] = {}

    @classmethod
    def register(cls, factor_cls: type[FactorBase]) -> type[FactorBase]:
        """
        装饰器：将因子类注册到注册表。

        使用方式：
            @FactorRegistry.register
            class MyFactor(FactorBase): ...
        """
        if not hasattr(factor_cls, "meta"):
            raise AttributeError(
                f"{factor_cls.__name__} 缺少 meta 属性，注册失败。"
                " 请在类中定义 meta = FactorMeta(factor_id=..., name=..., domain=...)"
            )
        factor_id = factor_cls.meta.factor_id
        if factor_id in cls._registry:
            raise ValueError(
                f"因子 ID '{factor_id}' 已注册（{cls._registry[factor_id].__name__}），"
                f"无法重复注册 {factor_cls.__name__}。"
            )
        cls._registry[factor_id] = factor_cls
        return factor_cls

    @classmethod
    def get(cls, factor_id: str) -> type[FactorBase]:
        """按 ID 获取因子类，未找到时抛 KeyError。"""
        if factor_id not in cls._registry:
            raise KeyError(f"因子 '{factor_id}' 未在注册表中找到。 已注册因子：{list(cls._registry.keys())}")
        return cls._registry[factor_id]

    @classmethod
    def list_all(cls) -> list[FactorMeta]:
        """返回所有已注册因子的 FactorMeta 列表。"""
        return [fc.meta for fc in cls._registry.values()]

    @classmethod
    def list_by_domain(cls, domain: str) -> list[FactorMeta]:
        """按域过滤，返回 FactorMeta 列表。"""
        return [fc.meta for fc in cls._registry.values() if fc.meta.domain == domain]

    @classmethod
    def clear(cls) -> None:
        """清空注册表（仅供测试使用）。"""
        cls._registry.clear()

    def __len__(self) -> int:
        # 5.90.1 修复：@classmethod 装饰 __len__ 会导致 type(obj).__len__(obj) 调用时
        # cls 绑定为类本身，传入的 obj 变成多余参数触发 TypeError。改为实例方法。
        return len(self._registry)


# ---------------------------------------------------------------------------
# autodiscover_factors — 自动发现
# ---------------------------------------------------------------------------


def autodiscover_factors(package_path: str | None = None) -> None:
    """
    扫描 factor/factors/ 目录，自动 import 所有因子模块。

    每个模块只要包含 @FactorRegistry.register 装饰的类，
    import 时就会自动触发注册，无需手工维护列表。

    Args:
        package_path: 可选，指定扫描目录。默认扫描本模块同级 factors/ 目录。

    注：此函数在 factor 初始化时（factor/__init__.py）调用一次即可。
    """
    import importlib
    import os
    import pkgutil
    import sys

    if package_path is None:
        package_path = os.path.join(os.path.dirname(__file__), "factors")

    if not os.path.isdir(package_path):
        return

    for finder, module_name, _ in pkgutil.iter_modules([package_path]):
        full_name = f"zephyr.factor.{module_name}"
        try:
            if full_name in sys.modules:
                importlib.reload(sys.modules[full_name])
            else:
                importlib.import_module(full_name)
        except Exception as exc:
            import warnings

            warnings.warn(f"autodiscover_factors: 加载 {full_name} 失败：{exc}")
