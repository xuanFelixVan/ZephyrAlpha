# [A_module] module_id=MOD-EX-RULES-001 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-EX-RULES-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.rules.base
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] stdlib (abc/dataclasses/decimal)
# [CONSUMERS] zephyr.ex_core.rules.ashare; zephyr.ex_core.rules.crypto; zephyr.ex_core.rules
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 接口纯定义零IO; settlement_cycle>=0; 价格笼子幅度>0
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/94_crypto_quant_expansion.md §4.3
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 纯接口无异常约定
# [TESTS] tests/ex_core/rules/
# [TTL] permanent
"""交易规则包抽象接口（Trading Rule Pack，CAND-CRYPTO-006 / 94号 §4.3）。

每市场一份规则包，订单校验时按标的所属市场加载。
纪律：
- 业务代码禁止 if/else 判市场——市场差异只走"按市场注入实现"（策略模式）；
- A股现有逻辑零行为变化（A股实现=board_lot/price_cage 真源委托收编）。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Final

__all__: Final = ["LotRule", "PriceCageRule", "TradingRulePack"]


@dataclass(frozen=True)
class LotRule:
    """最小申报单位规则。

    Attributes:
        min_unit: 最小买入申报数量（起买量）
        increment: 超过 min_unit 后的递增单位
    """

    min_unit: Decimal
    increment: Decimal


@dataclass(frozen=True)
class PriceCageRule:
    """价格笼子规则参数。

    Attributes:
        pct: 笼子幅度（百分比，如 Decimal("0.02")=±2%）
        floor_yuan: 元兜底（如 Decimal("0.10")=0.1元；None=无兜底）
    """

    pct: Decimal
    floor_yuan: Decimal | None


class TradingRulePack(ABC):
    """交易规则包策略对象（抽象接口）。

    属性：
        market: 市场标签（"ashare"/"crypto"，治理闸市场标注用）。
    """

    market: str = ""

    @abstractmethod
    def lot_rule(self, symbol: str) -> LotRule:
        """获取标的对应的最小申报单位规则。

        Args:
            symbol: 标的代码

        Returns:
            LotRule: 最小申报单位和递增步进
        """

    @abstractmethod
    def price_cage_rule(self, symbol: str) -> PriceCageRule:
        """获取标的对应的价格笼子规则参数。

        Args:
            symbol: 标的代码

        Returns:
            PriceCageRule: 笼子百分比和兜底金额
        """

    @property
    @abstractmethod
    def settlement_cycle(self) -> int:
        """结算周期（T+0=0, T+1=1）。

        A股=1；币=0。
        """

    @property
    @abstractmethod
    def price_tick(self) -> Decimal:
        """最小价格变动单位。

        A股=0.01；币按交易对各异（MVP 默认 0.01）。
        """

    def has_price_cage(self, symbol: str) -> bool:
        """该市场是否实行价格笼子限制。

        默认实现：pct>=1.0 视为无价格笼子（100%=无限制）。
        """
        rule = self.price_cage_rule(symbol)
        return rule.pct < Decimal("1")
