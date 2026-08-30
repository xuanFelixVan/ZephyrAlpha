# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] zephyr.factor.technical_indicators.indicator_base
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] pandas(pip); numpy(pip)
# [CONSUMERS] zephyr.factor.technical_indicators.{trend,momentum,volatility,volume,reversal}; zephyr.data.implementations.internal_compute_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 技术指标基类 compute→DataFrame 多列输出（区别于 FactorBase 单 Series）；纯自实现无第三方 TA 库依赖
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] compute 输入空 DataFrame→返回空 DataFrame 不抛；输入缺列→ValueError
# [TESTS] tests/zephyr/factor/technical_indicators/test_indicator_base.py
# [A_module] module_id=MOD-L02-TI-BASE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
技术指标基类与注册表（#ARCH-DATA-TI-001，骨架先行 2026-08-10）。

核心组件：
  - TechnicalIndicatorMeta：技术指标元数据（indicator_id/name/category/output_columns/input_columns/params）
  - TechnicalIndicatorBase：抽象基类，compute(data) → DataFrame（多列输出）
  - TechnicalIndicatorRegistry：全局注册表（register/get/list_all/list_by_category）
  - autodiscover_technical_indicators：自动发现 5 类指标模块

与 FactorBase 的区别：
  - FactorBase.compute() → pd.Series（单列因子值）
  - TechnicalIndicatorBase.compute() → pd.DataFrame（多列指标值，如 KDJ→K/D/J 三列）

用法示例：
    @TechnicalIndicatorRegistry.register
    class KDJ(TechnicalIndicatorBase):
        meta = TechnicalIndicatorMeta(
            indicator_id="kdj",
            name="随机指标",
            category="momentum",
            output_columns=["kdj_k", "kdj_d", "kdj_j"],
            input_columns=["high", "low", "close"],
            params={"period": 9, "k_smooth": 3, "d_smooth": 3},
        )

        def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
            # 纯自实现 pandas/numpy 计算
            ...
            return pd.DataFrame({"kdj_k": k, "kdj_d": d, "kdj_j": j}, index=data.index)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: package_path 参数
#   fields: 参数 package_path，类型注解 str | None
#   code: indicator_base.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① TechnicalIndicatorBase
#   name_en: TechnicalIndicatorBase
#   intro: 所有技术指标的抽象基类。
#   desc: 所有技术指标的抽象基类。 核心区别于 FactorBase： - FactorBase.compute() → pd.Series（单列） - TechnicalIndicato…；公共方法（定义序）: compute…
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② TechnicalIndicatorRegistry
#   name_en: TechnicalIndicatorRegistry
#   intro: 技术指标全局注册表（单例）。
#   desc: 技术指标全局注册表（单例）。 注册表提供： - @TechnicalIndicatorRegistry.register 装饰器自动注册 - get(indicator_id)…；公共方法（定义序）: register…
#   inputs: 无参数
#   outputs: 返回值
# - id: A3
#   name_zh: ③ autodiscover_technical_indicators
#   name_en: autodiscover_technical_indicators
#   intro: 扫描 technical_indicators/ 目录，自动 import 所有指标模块。
#   desc: 扫描 technical_indicators/ 目录，自动 import 所有指标模块。 每个模块只要包含 @TechnicalIndicatorRegistry.regist…；源码 L295-L329
#   inputs: package_path
#   outputs: 返回值
#   （注：A3 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: TechnicalIndicatorBase, TechnicalIndicatorRegistry, autodiscover_technical_indi…
#   downstream: zephyr.factor.technical_indicators.{trend,momentum,volatility,volume,reversal};…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import ClassVar

import pandas as pd

# ---------------------------------------------------------------------------
# TechnicalIndicatorMeta — 技术指标元数据
# ---------------------------------------------------------------------------


@dataclass
class TechnicalIndicatorMeta:
    """技术指标注册元数据。每个指标类必须定义 meta 类属性。

    与 FactorMeta 的区别：
      - 增加 category 字段（trend/momentum/volatility/volume/reversal）
      - 增加 output_columns 字段（多列输出名清单，用于 DDL 列映射）
      - 增加 input_columns 字段（输入数据所需列清单，用于校验）
      - 增加 params 字段（默认参数字典，如 {"period": 14}）
    """

    indicator_id: str
    """全局唯一指标 ID，如 'kdj' / 'macd' / 'rsi'。"""

    name: str
    """人类可读名称，如 '随机指标'。"""

    category: str
    """所属类别：'trend' / 'momentum' / 'volatility' / 'volume' / 'reversal'。"""

    output_columns: list[str]
    """输出列名清单，如 ['kdj_k', 'kdj_d', 'kdj_j']。用于 DDL 列映射。"""

    input_columns: list[str]
    """输入数据所需列清单，如 ['high', 'low', 'close']。用于校验。"""

    params: dict = field(default_factory=dict)
    """默认参数字典，如 {"period": 14, "k_smooth": 3}。"""

    version: str = "0.1.0"
    """语义版本号。骨架先行阶段为 0.1.0，算法实现后升 1.0.0。"""

    description: str = ""
    """指标说明。"""


# ---------------------------------------------------------------------------
# TechnicalIndicatorBase — 技术指标抽象基类
# ---------------------------------------------------------------------------


class TechnicalIndicatorBase(abc.ABC):
    """所有技术指标的抽象基类。

    核心区别于 FactorBase：
      - FactorBase.compute() → pd.Series（单列）
      - TechnicalIndicatorBase.compute() → pd.DataFrame（多列）

    用法示例：
        @TechnicalIndicatorRegistry.register
        class MACD(TechnicalIndicatorBase):
            meta = TechnicalIndicatorMeta(
                indicator_id="macd",
                name="异同移动平均",
                category="trend",
                output_columns=["macd_dif", "macd_dea", "macd_hist"],
                input_columns=["close"],
                params={"fast": 12, "slow": 26, "signal": 9},
            )

            def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
                ...
    """

    meta: ClassVar[TechnicalIndicatorMeta]
    """指标元数据，子类必须定义为类属性。"""

    @abc.abstractmethod
    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """计算技术指标值。

        Args:
            data: 输入行情数据，index 为 datetime，columns 至少包含 meta.input_columns。
            **kwargs: 可覆盖 meta.params 中的默认参数。

        Returns:
            pd.DataFrame，index 与 data 对齐，columns 为 meta.output_columns。
            预热期（前 N-1 行无足够数据）的值为 NaN。
        """

    def validate(self, data: pd.DataFrame) -> bool:
        """校验输入数据是否满足本指标的计算前提。

        默认实现：非空且包含 meta.input_columns 中所有列即通过。
        子类可覆盖以增加业务校验（如最低数据量要求）。
        """
        if data is None or data.empty:
            return False
        required = set(self.meta.input_columns)
        actual = set(data.columns)
        missing = required - actual
        if missing:
            raise ValueError(
                f"指标 '{self.meta.indicator_id}' 输入数据缺少列: {missing}。 需要: {required}，实际: {actual}。"
            )
        return True

    def get_params(self, **overrides) -> dict:
        """获取合并后的参数（meta.params + kwargs 覆盖）。"""
        params = dict(self.meta.params)
        params.update(overrides)
        return params

    def __repr__(self) -> str:
        return f"<TechnicalIndicator id={self.meta.indicator_id} category={self.meta.category} v={self.meta.version}>"


# ---------------------------------------------------------------------------
# TechnicalIndicatorRegistry — 技术指标注册表
# ---------------------------------------------------------------------------


class TechnicalIndicatorRegistry:
    """技术指标全局注册表（单例）。

    注册表提供：
      - @TechnicalIndicatorRegistry.register 装饰器自动注册
      - get(indicator_id) 按 ID 查询
      - list_all() 列出全部指标元数据
      - list_by_category(category) 按类别过滤（trend/momentum/volatility/volume/reversal）
      - list_output_columns() 汇总全部输出列名（用于 DDL 列映射）
      - clear() 测试用，清空注册表
    """

    _registry: ClassVar[dict[str, type[TechnicalIndicatorBase]]] = {}

    @classmethod
    def register(cls, indicator_cls: type[TechnicalIndicatorBase]) -> type[TechnicalIndicatorBase]:
        """装饰器：将指标类注册到注册表。

        使用方式：
            @TechnicalIndicatorRegistry.register
            class KDJ(TechnicalIndicatorBase): ...
        """
        if not hasattr(indicator_cls, "meta"):
            raise AttributeError(
                f"{indicator_cls.__name__} 缺少 meta 属性，注册失败。"
                " 请在类中定义 meta = TechnicalIndicatorMeta(indicator_id=..., ...)"
            )
        indicator_id = indicator_cls.meta.indicator_id
        if indicator_id in cls._registry:
            raise ValueError(
                f"指标 ID '{indicator_id}' 已注册（{cls._registry[indicator_id].__name__}），"
                f"无法重复注册 {indicator_cls.__name__}。"
            )
        cls._registry[indicator_id] = indicator_cls
        return indicator_cls

    @classmethod
    def get(cls, indicator_id: str) -> type[TechnicalIndicatorBase]:
        """按 ID 获取指标类，未找到时抛 KeyError。"""
        if indicator_id not in cls._registry:
            raise KeyError(f"指标 '{indicator_id}' 未在注册表中找到。 已注册指标：{list(cls._registry.keys())}")
        return cls._registry[indicator_id]

    @classmethod
    def list_all(cls) -> list[TechnicalIndicatorMeta]:
        """返回所有已注册指标的 TechnicalIndicatorMeta 列表。"""
        return [ic.meta for ic in cls._registry.values()]

    @classmethod
    def list_by_category(cls, category: str) -> list[TechnicalIndicatorMeta]:
        """按类别过滤，返回 TechnicalIndicatorMeta 列表。

        Args:
            category: 'trend' / 'momentum' / 'volatility' / 'volume' / 'reversal'
        """
        return [ic.meta for ic in cls._registry.values() if ic.meta.category == category]

    @classmethod
    def list_output_columns(cls) -> list[str]:
        """汇总全部已注册指标的输出列名（用于 DDL 列映射校验）。"""
        columns = []
        for meta in cls.list_all():
            columns.extend(meta.output_columns)
        return columns

    @classmethod
    def clear(cls) -> None:
        """清空注册表（仅供测试使用）。"""
        cls._registry.clear()

    def __len__(self) -> int:
        return len(self._registry)


# ---------------------------------------------------------------------------
# autodiscover_technical_indicators — 自动发现
# ---------------------------------------------------------------------------


def autodiscover_technical_indicators(package_path: str | None = None) -> None:
    """扫描 technical_indicators/ 目录，自动 import 所有指标模块。

    每个模块只要包含 @TechnicalIndicatorRegistry.register 装饰的类，
    import 时就会自动触发注册，无需手工维护列表。

    Args:
        package_path: 可选，指定扫描目录。默认扫描本模块同级目录（technical_indicators/）。

    注：此函数在 technical_indicators 初始化时调用一次即可。
    """
    import importlib
    import os
    import pkgutil
    import sys

    if package_path is None:
        package_path = os.path.dirname(__file__)

    # 确保 package 在 sys.path 中
    parent = os.path.dirname(package_path)
    if parent not in sys.path:
        sys.path.insert(0, parent)

    package_name = os.path.basename(package_path)
    for _, module_name, _ in pkgutil.iter_modules([package_path]):
        if module_name.startswith("_") or module_name == "base":
            continue
        full_name = f"zephyr.factor.technical_indicators.{module_name}"
        try:
            importlib.import_module(full_name)
        except Exception as e:  # noqa: BLE001
            import logging

            logging.getLogger(__name__).warning("自动发现技术指标模块 %s 失败: %s", full_name, e)
