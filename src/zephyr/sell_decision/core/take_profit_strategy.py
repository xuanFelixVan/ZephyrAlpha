# [BLUEPRINT] MOD-SELL-004 | docs/03_modules/_domain_sell_decision/take_profit_strategy/blueprint.md
# [MODULE] zephyr.sell_decision.core.take_profit_strategy
# [DOMAIN] D_SELL_DECISION
# [DEPENDENCIES] zephyr.shared.foundation.errors ; zephyr.sell_decision.core.stop_loss_strategy
# [CONSUMERS] MOD-SELL-007(融合引擎) ; D-POSITION
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 盈利超1×ATR→profit phase(紧M=2.0); 统一Chandelier公式不维护两套%参数; ATR缺失降级固定%
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidTakeProfitInputError
# [TESTS] tests/sell_decision/test_take_profit_strategy.py
# [A_module] module_id=MOD-SELL-004 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Take Profit Strategy — 止盈策略族 (MOD-SELL-004)

Chandelier Exit 统一止盈: 盈利区用紧 trailing(M=2.0, N=22) 锁定利润,
与止损共用同一公式, 不维护两套独立%参数。

设计说明:
    - compute_exit_price: 复用 MOD-SELL-005 Chandelier 核心,
      自动判定 phase(盈利超1×ATR→profit, 否则loss), 是005的"消费者"层
    - 盈利超1×ATR切换点: 高波动股ATR大→阈值自动抬高(防过早锁利),
      低波动股ATR小→阈值自动降低(快速进入保护)
    - 移动止盈与移动止损统一(42号 §3.4): 盈利后的trailing既是止盈(锁定利润)
      也是止损(保护盈利), 不封顶上涨空间
    - 固定/分批/时间加权止盈待 G04 策略类型校准后差异化(42号 §3.4 待裁定表)
    - 分批退出(simple_scaling_out三步法)归 MOD-SELL-017, MVP降级一次性退出
      (42号 §3.7), 不在本模块范围

依据: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/42_sell_flow.md §3.4
SSoT: depgraph MOD-SELL-004
Version: 0.1.0

# [ALGO_FLOW] external: docs/03_modules/_domain_sell_decision/algo_flow/take_profit_strategy.yaml
"""

from __future__ import annotations

import logging
from typing import Callable, Final

from zephyr.sell_decision.core.position_triage import SellPositionSnapshot
from zephyr.sell_decision.core.stop_loss_strategy import (
    PositionPhase,
    StopLossStrategy,
    validate_position_snapshot,
)
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "TakeProfitStrategy",
    "InvalidTakeProfitInputError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidTakeProfitInputError(ZephyrBaseError):
    """止盈策略输入数据非法(如价格≤0、回调不可调用)。"""

    error_code = "ZA-SELL-0004"


# ──────────────────────────────────────────────────────────────────────────────
# 算法
# ──────────────────────────────────────────────────────────────────────────────


class TakeProfitStrategy:
    """止盈策略族——统一 Chandelier Exit 退出价位计算。"""

    @staticmethod
    def compute_exit_price(
        position: SellPositionSnapshot,
        atr_value: float | None,
        highest_close_fn: Callable[[int], float],
    ) -> float:
        """统一止盈止损价位计算(自动判定phase, 42号 §3.4)。

        与 MOD-SELL-005 compute_stop_loss 的分工:
        - 本函数自动判定 phase(盈利超1×ATR→profit紧trailing, 否则loss宽trailing)
        - 005 由调用方显式传入 phase(适用于调用方已持有phase上下文的场景)

        亏损区: Chandelier(N=10, M=3.0)——宽trailing, 锚10日最高收盘价
        盈利超1×ATR: Chandelier(N=22, M=2.0)——紧trailing, 锚22日最高收盘价

        Args:
            position: 持仓快照
            atr_value: ATR(14), None时降级固定%
            highest_close_fn: 回调函数, 传入回看N日→最高收盘价

        Returns:
            退出价位(float)

        Raises:
            InvalidTakeProfitInputError: 输入非法
        """
        try:
            validate_position_snapshot(position)
        except Exception as exc:
            raise InvalidTakeProfitInputError(str(exc)) from exc
        if not callable(highest_close_fn):
            raise InvalidTakeProfitInputError("highest_close_fn 必须可调用")

        # ATR缺失降级: 委托005统一降级逻辑(真源唯一, 42号 §3.4对齐§3.3)
        # phase在降级路径不生效(005内部固定%分支不读phase), 传LOSS占位
        if atr_value is None or atr_value <= 0:
            logger.debug(
                "ATR缺失, symbol=%s 降级固定%%退出价(委托005)",
                position.symbol,
            )
            return StopLossStrategy.compute_stop_loss(position, None, highest_close_fn, PositionPhase.LOSS)

        # 自动判定phase: 盈利超1×ATR → profit(紧trailing锁定利润)
        unrealized_pnl_pct = (position.current_price - position.entry_price) / position.entry_price
        atr_pct = atr_value / position.entry_price

        phase = PositionPhase.PROFIT if unrealized_pnl_pct >= atr_pct else PositionPhase.LOSS

        # 委托005 Chandelier核心(真源唯一)
        return StopLossStrategy.compute_stop_loss(position, atr_value, highest_close_fn, phase)
