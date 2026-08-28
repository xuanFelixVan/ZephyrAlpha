# [A_module] module_id=MOD-EX-RULES-001 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-EX-RULES-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.rules.crypto
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.rules.base
# [CONSUMERS] zephyr.ex_core.rules
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 骨架实现零外部依赖; 行为完全确定; step_size/tick_size 预留注入接口
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/94_crypto_quant_expansion.md §4.3
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无异常约定
# [TESTS] tests/ex_core/rules/
# [TTL] permanent
"""数字货币交易规则包实现（94号 §4.3：币实现=骨架，元数据接口预留）。

7×24 连续市场：T+0 结算、无涨跌停（MVP 默认无价格笼子）、
step_size/tick_size 按交易对各异（MVP 使用默认兜底，CAND-CRYPTO-002 行情接入后
可通过 RulePackMetadata 注入具体元数据）。

骨架纪律：MVP 阶段只提供默认兜底值，具体交易对元数据等 CAND-CRYPTO-002 落地后
由装配层注入（get_trading_rule_pack(metadata=...)）。
"""

from __future__ import annotations

from decimal import Decimal
from typing import Final

from zephyr.ex_core.rules.base import LotRule, PriceCageRule, TradingRulePack

__all__: Final = ["CryptoRulePack"]


class CryptoRulePack(TradingRulePack):
    """数字货币交易规则包（T+0、无涨跌停、step_size/tick_size 按交易对各异）。

    MVP 骨架：提供默认兜底值（BTC/ETH 现货常见口径），具体交易对元数据
    等 CAND-CRYPTO-002 行情接入后由装配层注入。
    """

    market: str = "crypto"

    #: 默认最小申报单位（BTC 现货常见 0.00001，MVP 兜底）
    _DEFAULT_MIN_UNIT: Final = Decimal("0.00001")
    #: 默认递增步进
    _DEFAULT_INCREMENT: Final = Decimal("0.00001")
    #: 默认最小价格变动单位（BTC/USDT 常见 0.01，MVP 兜底）
    _DEFAULT_PRICE_TICK: Final = Decimal("0.01")

    def lot_rule(self, symbol: str) -> LotRule:
        """MVP 骨架：返回默认兜底规则。

        TODO: CAND-CRYPTO-002 行情接入后，通过交易所 exchangeInfo 元数据
        按交易对注入具体 step_size。
        """
        return LotRule(
            min_unit=self._DEFAULT_MIN_UNIT,
            increment=self._DEFAULT_INCREMENT,
        )

    def price_cage_rule(self, symbol: str) -> PriceCageRule:
        """MVP 骨架：无价格笼子（pct=1.0=100%，无限制）。

        TODO: 部分交易所有短时价格保护带，等 CAND-CRYPTO-002 元数据接入后
        可按交易对配置。
        """
        return PriceCageRule(pct=Decimal("1.0"), floor_yuan=None)

    @property
    def settlement_cycle(self) -> int:
        """币 T+0。"""
        return 0

    @property
    def price_tick(self) -> Decimal:
        """MVP 骨架：默认最小价格变动单位。

        TODO: CAND-CRYPTO-002 元数据接入后按交易对返回具体 tick_size。
        """
        return self._DEFAULT_PRICE_TICK
