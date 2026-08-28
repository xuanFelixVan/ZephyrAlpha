# [A_module] module_id=MOD-EX-RULES-001 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-EX-RULES-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.rules
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.rules.base; zephyr.ex_core.rules.ashare; zephyr.ex_core.rules.crypto
# [CONSUMERS] 装配层（TradingSession/PreExecutionChecker/回测装配 按市场注入）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] get_trading_rule_pack返回无状态共享单例; 市场判断集中于工厂一处（业务代码禁if/else判市场）
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/94_crypto_quant_expansion.md §4.3
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 未知市场名→ValueError
# [TESTS] tests/ex_core/rules/
# [TTL] permanent
"""交易规则包（Trading Rule Packs，CAND-CRYPTO-006 / 94号 §4.3）。

每市场一份规则包，订单校验时按标的所属市场加载。
A股实现=现有 board_lot/price_cage 函数委托收编（零行为变化）；
币实现=骨架（step_size/tick_size 元数据接口预留，T+0 规则）。
"""

from __future__ import annotations

from functools import lru_cache
from typing import Final

from zephyr.ex_core.rules.ashare import AshareRulePack
from zephyr.ex_core.rules.base import TradingRulePack
from zephyr.ex_core.rules.crypto import CryptoRulePack

__all__: Final = [
    "AshareRulePack",
    "CryptoRulePack",
    "TradingRulePack",
    "get_trading_rule_pack",
]

_REGISTRY: Final = {
    "ashare": AshareRulePack,
    "crypto": CryptoRulePack,
}


@lru_cache(maxsize=None)
def get_trading_rule_pack(market: str) -> TradingRulePack:
    """装配层注入入口：按市场名取规则包单例（无状态共享）。

    Args:
        market: 市场名（"ashare"/"crypto"）。

    Returns:
        对应市场的 TradingRulePack 单例。

    Raises:
        ValueError: 未知市场名。
    """
    cls = _REGISTRY.get(market)
    if cls is None:
        raise ValueError(f"未知市场: {market!r}（合法: {tuple(_REGISTRY)}）")
    return cls()
