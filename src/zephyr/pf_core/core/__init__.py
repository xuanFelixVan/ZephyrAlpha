# NOTE(2026-08-25 P1W21): scaffold 注册器斜杠非法 import 变种复发×4（同 #ARCH-228 族），
# 按可逆模式归一；并采仓内 PEP 562 惰性重导出惯例（ml_train/pf_core 包级 __init__ 同款），
# 避免包门面 eager import 把未完工兄弟模块的缺失放大为全包导入失败。
_LAZY_P1W21_EXPORTS = {
    "StrategyFactory": "zephyr.pf_core.core.strategy_factory",
    "FunnelPortfolioAdjudicator": "zephyr.pf_core.core.funnel_portfolio_adjudicator",
    "ExposureManager": "zephyr.pf_core.core.exposure_manager",
    "StrategyCapacityEstimator": "zephyr.pf_core.core.strategy_capacity_estimator",
}
# [TTL] permanent
# pf_core/core

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包导入请求（import zephyr.pf_core.core）
#   fields: 无参数，纯包初始化触发
#   code: core/__init__.py L1
# 层: 算法
# - id: A1
#   name_zh: ① 空包标记初始化
#   name_en: __init__ (empty package marker)
#   intro: 仅声明空 __all__，不做任何再导出、零副作用
#   desc: L1-3：仅一行包注释 + __all__ = []；子模块 constraint_solver（MOD-PF-006）须经显式路径导入
#   inputs: I1
#   outputs: 空包命名空间
# 层: 输出
# - id: O1
#   name_zh: 空包命名空间
#   name_en: zephyr.pf_core.core namespace
#   intro: 只提供包路径占位，不暴露任何符号
#   downstream: 无下游/内部使用（unmanaged 文件，无 [CONSUMERS] 头）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__: list[str] = []

__all__.append("StrategyFactory")

__all__.append("FunnelPortfolioAdjudicator")

__all__.append("ExposureManager")

__all__.append("StrategyCapacityEstimator")


def __getattr__(name: str):
    target = _LAZY_P1W21_EXPORTS.get(name)
    if target is not None:
        import importlib

        return getattr(importlib.import_module(target), name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
