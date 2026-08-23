# [BLUEPRINT] MOD-POS-018 | docs/03_modules/MOD-POS-018/
# [MODULE] zephyr.position.core.intraday_position_constraint
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.position.core.t1_sellable ; zephyr.shared.foundation.errors
# [CONSUMERS] D-EX-CORE(执行前盘中校验) ; MOD-SELL-018(做T协调器) ; D_RISK
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] T+1内生(当日买入不可卖,卖出≤昨仓−今日已卖,复用t1_sellable口径); 盘后投影=昨仓+今买+拟买−今卖−拟卖(负值兜底0); 单标的/总仓位上限Fail-Closed(违规→allowed=False不静默放行); 纯函数可单测
# [MODIFY-GUARD] docs/03_modules/MOD-POS-018/
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidIntradayConstraintInputError(ZA-POS-0023)
# [TESTS] tests/position/test_intraday_position_constraint.py
# [A_module] module_id=MOD-POS-018 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Intraday Position Constraint — 盘中仓位约束 (MOD-POS-018，T+1 配套)

盘中实时校验交易意图是否满足仓位约束（宪章 §2 约束四 T+1 交割内生）：

  1. **T+1 冻结**（T1_FROZEN）：卖出意图 ≤ T+1 可卖量（昨仓 − 今日已卖，
     复用 MOD-POS t1_sellable 口径）；当日买入部分 T+1 前不可卖；
  2. **单标的上限**（SINGLE_CAP）：盘后投影权重 ≤ max_single_weight；
  3. **总仓位上限**（TOTAL_CAP）：盘后投影总权重 ≤ max_total_weight。

Fail-Closed：任何一条违规 → allowed=False + 结构化 violations 留痕，
绝不静默放行；输入非法 → InvalidIntradayConstraintInputError。

与选股/执行解耦：本模块只回答"这笔意图在仓位约束下能不能做"，
不决定"买什么"（what）与"怎么下单"（how）。

纪律：纯函数、无 IO；所有仓位/意图由调用方注入。
Version: 1.0.0
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Final

from zephyr.position.core.t1_sellable import t1_sellable_weights
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "IntradayConstraintInput",
    "IntradayConstraintResult",
    "ConstraintViolation",
    "InvalidIntradayConstraintInputError",
    "ViolationCode",
    "check_intraday_constraints",
]


class ViolationCode(str, Enum):
    """盘中约束违规代码。"""

    T1_FROZEN = "T1_FROZEN"  # T+1 冻结：卖出超可卖量
    SINGLE_CAP = "SINGLE_CAP"  # 单标的权重上限
    TOTAL_CAP = "TOTAL_CAP"  # 总仓位上限


class InvalidIntradayConstraintInputError(ZephyrBaseError):
    """盘中仓位约束输入非法（负意图/上限越界/非有限值）。"""

    error_code = "ZA-POS-0023"


@dataclass(frozen=True)
class IntradayConstraintInput:
    """盘中约束校验输入（>4 参数收 dataclass）。

    Attributes:
        last_session_weights: {symbol: 昨仓权重}（T-1 收盘）
        today_bought_weights: {symbol: 今日已买权重}（T+1 冻结，不可卖）
        today_sold_weights: {symbol: 今日已卖权重}
        intended_sells: {symbol: 本次拟卖权重}
        intended_buys: {symbol: 本次拟买权重}
        max_single_weight: 单标的权重上限 ∈(0,1]
        max_total_weight: 总仓位上限 ∈(0,1]，须 ≥ max_single_weight
    """

    last_session_weights: Mapping[str, float]
    today_bought_weights: Mapping[str, float]
    today_sold_weights: Mapping[str, float]
    intended_sells: Mapping[str, float]
    intended_buys: Mapping[str, float]
    max_single_weight: float
    max_total_weight: float


@dataclass(frozen=True)
class ConstraintViolation:
    """单条约束违规（结构化留痕）。

    Attributes:
        code: 违规代码
        symbol: 相关标的（TOTAL_CAP 为 ""）
        message: 人类可读描述（禁含 session_id）
        limit: 触发上限值
        actual: 实际值
    """

    code: ViolationCode
    symbol: str
    message: str
    limit: float
    actual: float


@dataclass(frozen=True)
class IntradayConstraintResult:
    """盘中约束校验结果（frozen 不可变）。

    Attributes:
        allowed: 是否全部合规（False=Fail-Closed 拦截）
        violations: 违规明细（按发现顺序）
        t1_sellable: T+1 可卖权重口径（复用 t1_sellable 计算，供下游）
        post_trade_weights: 盘后投影权重（意图全部成交后）
    """

    allowed: bool
    violations: tuple[ConstraintViolation, ...]
    t1_sellable: dict[str, float]
    post_trade_weights: dict[str, float] = field(default_factory=dict)


def _validate_weights(name: str, weights: Mapping[str, float], *, allow_zero_only: bool = False) -> None:
    for sym, w in weights.items():
        if not math.isfinite(w) or w < 0.0:
            raise InvalidIntradayConstraintInputError(
                f"{name} 标的 {sym} 权重非法（须为有限非负值），got {w}"
            )


def check_intraday_constraints(
    intent: IntradayConstraintInput,
) -> IntradayConstraintResult:
    """盘中仓位约束校验（纯函数，Fail-Closed）。

    Args:
        intent: IntradayConstraintInput（昨仓/今买/今卖/拟买卖/上限）

    Returns:
        IntradayConstraintResult（allowed=False 时 violations 非空）

    Raises:
        InvalidIntradayConstraintInputError: 输入非法
    """
    _validate_weights("昨仓", intent.last_session_weights)
    _validate_weights("今日已买", intent.today_bought_weights)
    _validate_weights("今日已卖", intent.today_sold_weights)
    _validate_weights("拟卖", intent.intended_sells)
    _validate_weights("拟买", intent.intended_buys)

    for name, cap in (("max_single_weight", intent.max_single_weight), ("max_total_weight", intent.max_total_weight)):
        if not math.isfinite(cap) or cap <= 0.0 or cap > 1.0:
            raise InvalidIntradayConstraintInputError(f"{name} 非法（须 ∈(0,1]），got {cap}")
    if intent.max_single_weight > intent.max_total_weight:
        raise InvalidIntradayConstraintInputError(
            f"max_single_weight({intent.max_single_weight}) 不可超过 max_total_weight({intent.max_total_weight})"
        )

    # ① T+1 可卖口径（昨仓 − 今日已卖）
    sellable = t1_sellable_weights(
        dict(intent.last_session_weights), dict(intent.today_sold_weights)
    )

    violations: list[ConstraintViolation] = []

    # ② T1_FROZEN：拟卖 ≤ 可卖
    for sym in sorted(intent.intended_sells):
        sell_qty = intent.intended_sells[sym]
        avail = sellable.get(sym, 0.0)
        if sell_qty > avail + 1e-12:
            violations.append(
                ConstraintViolation(
                    code=ViolationCode.T1_FROZEN,
                    symbol=sym,
                    message=f"标的 {sym} 拟卖 {sell_qty:.4f} 超 T+1 可卖 {avail:.4f}（当日买入冻结不可卖）",
                    limit=avail,
                    actual=sell_qty,
                )
            )

    # ③ 盘后投影：昨仓 + 今买 + 拟买 − 今卖 − 拟卖（负值兜底 0）
    post: dict[str, float] = dict(intent.last_session_weights)
    for src in (intent.today_bought_weights, intent.intended_buys):
        for sym, w in src.items():
            post[sym] = post.get(sym, 0.0) + w
    for src in (intent.today_sold_weights, intent.intended_sells):
        for sym, w in src.items():
            post[sym] = max(0.0, post.get(sym, 0.0) - w)

    # ④ SINGLE_CAP
    for sym in sorted(post):
        w = post[sym]
        if w > intent.max_single_weight + 1e-12:
            violations.append(
                ConstraintViolation(
                    code=ViolationCode.SINGLE_CAP,
                    symbol=sym,
                    message=f"标的 {sym} 盘后投影权重 {w:.4f} 超单标的上限 {intent.max_single_weight:.4f}",
                    limit=intent.max_single_weight,
                    actual=w,
                )
            )

    # ⑤ TOTAL_CAP
    total = sum(post.values())
    if total > intent.max_total_weight + 1e-12:
        violations.append(
            ConstraintViolation(
                code=ViolationCode.TOTAL_CAP,
                symbol="",
                message=f"盘后投影总仓 {total:.4f} 超总仓上限 {intent.max_total_weight:.4f}",
                limit=intent.max_total_weight,
                actual=total,
            )
        )

    return IntradayConstraintResult(
        allowed=not violations,
        violations=tuple(violations),
        t1_sellable=sellable,
        post_trade_weights={s: post[s] for s in sorted(post)},
    )
