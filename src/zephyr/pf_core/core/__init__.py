# NOTE(2026-08-25 P1W21): scaffold 注册器斜杠非法 import 变种复发×4（同 #ARCH-228 族），
# 按可逆模式归一；并采仓内 PEP 562 惰性重导出惯例（ml_train/pf_core 包级 __init__ 同款），
# 避免包门面 eager import 把未完工兄弟模块的缺失放大为全包导入失败。
"""


# [ALGO_FLOW] external: docs/03_modules/_domain_portfolio_core/algo_flow/core__init__.yaml
"""

_LAZY_P1W21_EXPORTS = {
    "StrategyFactory": "zephyr.pf_core.core.strategy_factory",
    "FunnelPortfolioAdjudicator": "zephyr.pf_core.core.funnel_portfolio_adjudicator",
    "ExposureManager": "zephyr.pf_core.core.exposure_manager",
    "StrategyCapacityEstimator": "zephyr.pf_core.core.strategy_capacity_estimator",
}
# [TTL] permanent
# pf_core/core

"""


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
