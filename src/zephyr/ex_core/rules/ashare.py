# [A_module] module_id=MOD-EX-RULES-001 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-EX-RULES-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.rules.ashare
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.board_lot; zephyr.ex_core.price_cage; zephyr.ex_core.rules.base
# [CONSUMERS] zephyr.ex_core.rules
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 全方法委托board_lot/price_cage真源=行为零变化; 无状态可共享单例
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/94_crypto_quant_expansion.md §4.3
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 与真源一致
# [TESTS] tests/ex_core/rules/
# [TTL] permanent
"""
A股交易规则包实现（94号 §4.3：A股实现=现有规则收编）。

收编方式=薄封装委托：lot_rule 委托 board_lot.get_board_lot_rule 真源；
price_cage_rule 委托 price_cage._get_cage_params 真源；真源本体一行不动。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: ashare.py
# 层: 算法
# - id: A1
#   name_zh: ① AshareRulePack
#   name_en: AshareRulePack
#   intro: A股交易规则包（T+1、整手100股、涨跌停±10%/20%）。
#   desc: A股交易规则包（T+1、整手100股、涨跌停±10%/20%）。 无状态（全部委托真源），可安全共享单例。；公共方法（定义序）: lot_rule, price_cage_rule, settlement_cycle,…
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: AshareRulePack
#   downstream: zephyr.ex_core.rules
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from decimal import Decimal
from typing import Final

from zephyr.ex_core import board_lot as _bl
from zephyr.ex_core import price_cage as _pc
from zephyr.ex_core.rules.base import LotRule, PriceCageRule, TradingRulePack

__all__: Final = ["AshareRulePack"]


class AshareRulePack(TradingRulePack):
    """A股交易规则包（T+1、整手100股、涨跌停±10%/20%）。

    无状态（全部委托真源），可安全共享单例。
    """

    market: str = "ashare"

    def lot_rule(self, symbol: str) -> LotRule:
        """委托 board_lot.get_board_lot_rule 真源。"""
        rule = _bl.get_board_lot_rule(symbol)
        return LotRule(
            min_unit=Decimal(rule.min_unit),
            increment=Decimal(rule.increment),
        )

    def price_cage_rule(self, symbol: str) -> PriceCageRule:
        """委托 price_cage._get_cage_params 真源。"""
        pct, floor_yuan = _pc._get_cage_params(symbol)
        return PriceCageRule(pct=pct, floor_yuan=floor_yuan)

    @property
    def settlement_cycle(self) -> int:
        """A股 T+1。"""
        return 1

    @property
    def price_tick(self) -> Decimal:
        """A股最小价格变动单位 0.01。"""
        return _pc.PRICE_TICK
