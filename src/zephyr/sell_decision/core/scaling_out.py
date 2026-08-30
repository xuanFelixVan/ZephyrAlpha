# [BLUEPRINT] MOD-SELL-017 | docs/03_modules/_domain_sell_decision/blueprint.md
# [MODULE] zephyr.sell_decision.core.scaling_out
# [DOMAIN] D_SELL_DECISION
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] 卖出决策层(42号§3.7 分批退出 80/20 过渡); MOD-SELL-007 融合引擎(装配批次接线)
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] 三步法状态机(1/3止盈→保本→trailing, 42号§3.7 arrowalgo 2026-03 实证 85% 收益捕获); 状态显式入参(无隐藏状态, 幂等可重放); trailing=Chandelier 统一公式(盈利区 N=22 M=2.0, 42号§3.3); ATR 缺失降级固定 8% 回撤线; 输入非正拒绝
# [MODIFY-GUARD] 42_sell_flow.md §3.7/§3.3
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidScalingOutInputError(ZA-SELL-0010)
# [TESTS] tests/sell_decision/test_scaling_out.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: ScalingOutPositionView(quantity/entry_price/risk_reward) + ScalingOutState(first_tranche_sold/stop_at_breakeven) + atr_value + highest_close_fn(回看N日最高收盘价回调)
# F1: Step1 未卖首批且 risk_reward≥1.0 → SELL 1/3 仓位(TAKE_PROFIT_1)
# F2: Step2 首批已卖且未保本 → MOVE_STOP 至 entry_price(BREAKEVEN, 剩余零风险)
# F3: Step3 其余 → HOLD_WITH_TRAILING(highest_close(22) - 2.0×ATR; ATR 缺失降级 highest×0.92)
# O1: ScalingOutAction(action/quantity/price/reason) -> 卖出执行层
# [/ALGO_FLOW]
"""
D_SELL_DECISION — MOD-SELL-017 分批退出 simple_scaling_out 三步法（42 号 §3.7）。

MVP→阶段 2 的 80/20 过渡（arrowalgo 2026-03 实证：三步法捕获完整分批退出 85%
收益，只需 1 个函数而非 4 模式状态机）：1/3 止盈 → 保本 → 剩余 trailing。

工程修正（对 42 号 §3.7 伪代码）：原伪代码 Step1/Step2 同判
`risk_reward >= 1.0` 且 Step1 先行 return，Step2 永不可达。本实现把
"首批是否已卖/是否已保本"显式化为 ScalingOutState 入参（无隐藏状态、
幂等可重放），三步按状态机推进。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: position 参数
#   fields: 参数 position，类型注解 ScalingOutPositionView
#   code: scaling_out.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: state 参数
#   fields: 参数 state，类型注解 ScalingOutState
#   code: scaling_out.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: atr_value 参数
#   fields: 参数 atr_value，类型注解 Decimal | None
#   code: scaling_out.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: highest_close_fn 参数
#   fields: 参数 highest_close_fn，类型注解 Callable[[int], float]
#   code: scaling_out.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① simple_scaling_out
#   name_en: simple_scaling_out
#   intro: 简单三步分批退出：1/3 止盈 → 保本 → 剩余 trailing（42 号 §3.7）。
#   desc: 简单三步分批退出：1/3 止盈 → 保本 → 剩余 trailing（42 号 §3.7）。 Args: position: 持仓视图（数量/入场价/风险回报比）。 state:…；源码 L136-L202
#   inputs: position state atr_value highest_close_fn
#   outputs: ScalingOutAction
#   （注：A1 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: ScalingOutAction
#   name_en: ScalingOutAction
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 卖出决策层(42号§3.7 分批退出 80/20 过渡); MOD-SELL-007 融合引擎(装配批次接线)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Callable, Final

from zephyr.shared.foundation.errors import ZephyrBaseError

#: 盈利区 Chandelier 参数（42 号 §3.3：N=22, M=2.0 紧 trailing 锁定利润）
_TRAILING_LOOKBACK: Final[int] = 22
_TRAILING_M: Final[Decimal] = Decimal("2.0")
#: ATR 缺失降级固定回撤线（42 号 §3.3：中长线 8%）
_FALLBACK_TRAILING_PCT: Final[Decimal] = Decimal("0.08")
#: 首批止盈比例（1/3）
_FIRST_TRANCHE_RATIO: Final[Decimal] = Decimal("0.33")


class InvalidScalingOutInputError(ZephyrBaseError):
    """分批退出输入非法——非正数量/入场价/最高收盘价等。"""

    error_code = "ZA-SELL-0010"


class ScalingOutActionType(str, Enum):
    """分批退出动作类型。"""

    SELL = "SELL"
    MOVE_STOP = "MOVE_STOP"
    HOLD_WITH_TRAILING = "HOLD_WITH_TRAILING"


@dataclass(frozen=True)
class ScalingOutPositionView:
    """持仓视图（调用方从持仓快照映射）。"""

    quantity: Decimal
    entry_price: Decimal
    risk_reward: float  # (current_price - entry) / (entry - initial_stop)，42 号 §3.7 口径


@dataclass(frozen=True)
class ScalingOutState:
    """三步法状态（显式入参，无隐藏状态）。"""

    first_tranche_sold: bool = False
    stop_at_breakeven: bool = False


@dataclass(frozen=True)
class ScalingOutAction:
    """分批退出动作。"""

    action: ScalingOutActionType
    quantity: Decimal | None  # SELL 时为本批卖出量
    price: Decimal | None  # MOVE_STOP / HOLD_WITH_TRAILING 时为止损线
    reason: str  # TAKE_PROFIT_1 / BREAKEVEN / TRAILING


def simple_scaling_out(
    position: ScalingOutPositionView,
    state: ScalingOutState,
    atr_value: Decimal | None,
    highest_close_fn: Callable[[int], float],
) -> ScalingOutAction:
    """简单三步分批退出：1/3 止盈 → 保本 → 剩余 trailing（42 号 §3.7）。

    Args:
        position: 持仓视图（数量/入场价/风险回报比）。
        state: 三步法状态（首批是否已卖/止损是否已保本）。
        atr_value: ATR(14)；None 降级固定 8% trailing（42 号 §3.3 降级口径）。
        highest_close_fn: Callable[[int], float]，传入回看 N 日返回最高收盘价
            （调用方注入 K 线数据，42 号 §3.3 compute_stop_loss 签名约定）。

    Returns:
        ScalingOutAction（SELL 首批 1/3 / MOVE_STOP 保本 / HOLD_WITH_TRAILING）。

    Raises:
        InvalidScalingOutInputError: 数量/入场价非正、最高收盘价非正。
    """
    if position.quantity <= 0:
        raise InvalidScalingOutInputError(
            "持仓数量必须为正",
            details={"quantity": str(position.quantity)},
        )
    if position.entry_price <= 0:
        raise InvalidScalingOutInputError(
            "入场价必须为正",
            details={"entry_price": str(position.entry_price)},
        )

    # Step 1: 1:1 风险回报时卖出 1/3 锁定利润
    if not state.first_tranche_sold and position.risk_reward >= 1.0:
        return ScalingOutAction(
            action=ScalingOutActionType.SELL,
            quantity=position.quantity * _FIRST_TRANCHE_RATIO,
            price=None,
            reason="TAKE_PROFIT_1",
        )

    # Step 2: 首批已卖 → 止损上移至保本价，剩余仓位零风险
    if state.first_tranche_sold and not state.stop_at_breakeven:
        return ScalingOutAction(
            action=ScalingOutActionType.MOVE_STOP,
            quantity=None,
            price=position.entry_price,
            reason="BREAKEVEN",
        )

    # Step 3: 剩余仓位 Chandelier trailing（盈利区 N=22 M=2.0 统一公式）
    highest = Decimal(str(highest_close_fn(_TRAILING_LOOKBACK)))
    if highest <= 0:
        raise InvalidScalingOutInputError(
            "最高收盘价必须为正",
            details={"lookback": _TRAILING_LOOKBACK, "highest_close": str(highest)},
        )
    if atr_value is not None and atr_value > 0:
        trailing = highest - _TRAILING_M * atr_value
    else:
        trailing = highest * (Decimal("1") - _FALLBACK_TRAILING_PCT)  # ATR 缺失降级
    return ScalingOutAction(
        action=ScalingOutActionType.HOLD_WITH_TRAILING,
        quantity=None,
        price=trailing,
        reason="TRAILING",
    )


__all__ = [
    "InvalidScalingOutInputError",
    "ScalingOutAction",
    "ScalingOutActionType",
    "ScalingOutPositionView",
    "ScalingOutState",
    "simple_scaling_out",
]
