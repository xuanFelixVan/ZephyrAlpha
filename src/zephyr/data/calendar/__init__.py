# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.calendar
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.calendar.{base,ashare,crypto}
# [CONSUMERS] 装配层（scheduler/fusion/pit_query/回测装配 按市场注入）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] get_market_calendar返回无状态共享单例; 市场判断集中于工厂一处（业务代码禁if/else判市场）
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/94_crypto_quant_expansion.md §4.1
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 未知市场名→ValueError
# [TESTS] tests/zephyr/data/calendar/test_market_calendar.py
# [A_module] module_id=MOD-L00-004 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""市场日历包（market_calendar，CAND-CRYPTO-001 / 94号 §4.1）。

导出：MarketCalendar 抽象接口 + ASHare/Crypto 双实现 + get_market_calendar
装配工厂。市场判断集中于工厂一处——业务代码只接收注入实例，禁止 if/else 判市场。
"""

from __future__ import annotations

from functools import lru_cache
from typing import Final

from zephyr.data.calendar.ashare import ASHareCalendar
from zephyr.data.calendar.base import KlineAggRule, MarketCalendar
from zephyr.data.calendar.crypto import CryptoCalendar

__all__: Final = [
    "ASHareCalendar",
    "CryptoCalendar",
    "KlineAggRule",
    "MarketCalendar",
    "get_market_calendar",
]

_REGISTRY: Final = {
    "ashare": ASHareCalendar,
    "crypto": CryptoCalendar,
}


@lru_cache(maxsize=None)
def get_market_calendar(market: str) -> MarketCalendar:
    """装配层注入入口：按市场名取日历单例（无状态共享）。

    Args:
        market: 市场名（"ashare"/"crypto"）。

    Returns:
        对应市场的 MarketCalendar 单例。

    Raises:
        ValueError: 未知市场名。
    """
    cls = _REGISTRY.get(market)
    if cls is None:
        raise ValueError(f"未知市场: {market!r}（合法: {tuple(_REGISTRY)}）")
    return cls()
