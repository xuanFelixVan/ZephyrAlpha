# [BLUEPRINT] MOD-SELL-017 | docs/03_modules/MOD-SELL-017/
# [MODULE] zephyr.sell_decision.core.scaling_out_architect
# [DOMAIN] D_SELL_DECISION
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] MOD-SELL-013(离场情景SCALED_EXIT落地) ; D-EX-CORE(批次执行)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 紧迫度→节奏映射(≥0.8前重/0.5~0.8均匀/<0.5后重); 批次分数和=1; 首批IMMEDIATE且≤T+1可卖(超出顺延留痕); 后续批次带触发条件(反弹/破位/时间); 与既有scaling_out.py分工(本件规划批次结构,彼件单步状态机); 纯函数可单测
# [MODIFY-GUARD] docs/03_modules/MOD-SELL-017/
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidScalingPlanInputError(ZA-SELL-0023)
# [TESTS] tests/sell_decision/test_scaling_out_architect.py
# [A_module] module_id=MOD-SELL-017 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
Scaling Out Architect — 分批卖出架构师 (MOD-SELL-017)

设计分批离场的**批次结构**（几批、每批多少、什么触发），与既有
scaling_out.py（三步法单步状态机：SELL/MOVE_STOP/HOLD）分工：
本件出"计划"，彼件出"下一步动作"。

节奏由紧迫度决定（消费 MOD-SELL-009 口径）：
  - urgency ≥0.8 → FRONT_LOADED 前重后轻（几何序列 1/2, 1/4, …归一）——
    紧急时先出大头；
  - 0.5 ≤ urgency <0.8 → EVEN 均匀；
  - 0 < urgency <0.5 → BACK_LOADED 前轻后重——给反弹留仓位。

T+1 内生：首批（IMMEDIATE）动作量 ≤ T+1 可卖权重，冻结超出部分记入
t1_deferred_weight 顺延。

与选股策略零耦合（三维解耦）：只认权重/紧迫度，不认识信号来源。

纪律：纯函数、无 IO。
Version: 1.0.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: total_weight 参数
#   fields: 参数 total_weight（无注解）
#   code: scaling_out_architect.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: sellable_weight 参数
#   fields: 参数 sellable_weight（无注解）
#   code: scaling_out_architect.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: urgency 参数
#   fields: 参数 urgency（无注解）
#   code: scaling_out_architect.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: tranche_count 参数
#   fields: 参数 tranche_count（无注解）
#   code: scaling_out_architect.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① design_scaling_plan
#   name_en: design_scaling_plan
#   intro: 设计分批卖出计划（纯函数）。
#   desc: 设计分批卖出计划（纯函数）。 Args: total_weight: 计划卖出总权重 >0 sellable_weight: T+1 可卖权重 ∈[0, total_weight…；源码 L188-L271
#   inputs: total_weight sellable_weight urgency tranche_count
#   outputs: ScalingPlan
#   （注：A1 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: ScalingPlan
#   name_en: ScalingPlan
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-SELL-013(离场情景SCALED_EXIT落地) ; D-EX-CORE(批次执行)
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

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Final

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "InvalidScalingPlanInputError",
    "PacingStyle",
    "ScalingPlan",
    "Tranche",
    "TrancheTrigger",
    "design_scaling_plan",
]

_URGENT_THRESHOLD: Final = 0.8
_MID_THRESHOLD: Final = 0.5
_MIN_TRANCHES: Final = 2
_MAX_TRANCHES: Final = 5
_DEFAULT_TRANCHES: Final = 3


class PacingStyle(str, Enum):
    """分批节奏。"""

    FRONT_LOADED = "FRONT_LOADED"  # 前重后轻（紧急）
    EVEN = "EVEN"  # 均匀
    BACK_LOADED = "BACK_LOADED"  # 前轻后重（从容）


class TrancheTrigger(str, Enum):
    """批次触发条件。"""

    IMMEDIATE = "IMMEDIATE"  # 即时执行（首批）
    ON_REBOUND = "ON_REBOUND"  # 反弹至均价/压力位执行
    ON_BREAK = "ON_BREAK"  # 跌破次级支撑执行
    ON_TIME = "ON_TIME"  # 时间到期执行（次日/下个交易窗口）


class InvalidScalingPlanInputError(ZephyrBaseError):
    """分批卖出规划输入非法（权重/紧迫度/批次数越界）。"""

    error_code = "ZA-SELL-0023"


@dataclass(frozen=True)
class Tranche:
    """单个批次。

    Attributes:
        index: 批次序号（0=首批）
        fraction: 占总计划比例 ∈(0,1]
        weight: 本批权重
        trigger: 触发条件
        cumulative_fraction: 累计比例（含本批）
    """

    index: int
    fraction: float
    weight: float
    trigger: TrancheTrigger
    cumulative_fraction: float


@dataclass(frozen=True)
class ScalingPlan:
    """分批卖出计划（frozen 不可变）。

    Attributes:
        total_weight: 计划卖出总权重
        urgency: 输入紧迫度
        pacing: 节奏
        tranches: 批次（按 index 升序）
        t1_deferred_weight: T+1 冻结顺延权重（首批想卖但不可卖的部分）
    """

    total_weight: float
    urgency: float
    pacing: PacingStyle
    tranches: tuple[Tranche, ...]
    t1_deferred_weight: float
    notes: tuple[str, ...] = field(default_factory=tuple)


def _pacing_for_urgency(urgency: float) -> PacingStyle:
    if urgency >= _URGENT_THRESHOLD:
        return PacingStyle.FRONT_LOADED
    if urgency >= _MID_THRESHOLD:
        return PacingStyle.EVEN
    return PacingStyle.BACK_LOADED


def _fractions(pacing: PacingStyle, n: int) -> list[float]:
    """节奏 → 批次分数（和=1）。"""
    if pacing is PacingStyle.EVEN:
        return [1.0 / n] * n
    # 几何序列：前重=2^(n-1-i)，后重=反转
    weights = [2.0 ** (n - 1 - i) for i in range(n)]
    if pacing is PacingStyle.BACK_LOADED:
        weights.reverse()
    total = sum(weights)
    return [w / total for w in weights]


def design_scaling_plan(
    *,
    total_weight: float,
    sellable_weight: float,
    urgency: float,
    tranche_count: int = _DEFAULT_TRANCHES,
) -> ScalingPlan:
    """设计分批卖出计划（纯函数）。

    Args:
        total_weight: 计划卖出总权重 >0
        sellable_weight: T+1 可卖权重 ∈[0, total_weight]
        urgency: 紧迫度 ∈[0,1]（0 也允许——从容退出亦可规划）
        tranche_count: 批次数 ∈[2,5]（默认 3）

    Returns:
        ScalingPlan

    Raises:
        InvalidScalingPlanInputError: 输入非法
    """
    if not math.isfinite(total_weight) or total_weight <= 0.0:
        raise InvalidScalingPlanInputError(f"total_weight 非法（须为正有限值），got {total_weight}")
    if not math.isfinite(sellable_weight) or sellable_weight < 0.0:
        raise InvalidScalingPlanInputError(f"sellable_weight 非法（须为有限非负值），got {sellable_weight}")
    if sellable_weight > total_weight + 1e-12:
        raise InvalidScalingPlanInputError(f"可卖权重 {sellable_weight} 超计划总权重 {total_weight}（口径矛盾）")
    if not math.isfinite(urgency) or not (0.0 <= urgency <= 1.0):
        raise InvalidScalingPlanInputError(f"urgency 非法（须 ∈[0,1]），got {urgency}")
    if not (_MIN_TRANCHES <= tranche_count <= _MAX_TRANCHES):
        raise InvalidScalingPlanInputError(
            f"tranche_count 非法（须 ∈[{_MIN_TRANCHES},{_MAX_TRANCHES}]），got {tranche_count}"
        )

    pacing = _pacing_for_urgency(urgency)
    fractions = _fractions(pacing, tranche_count)

    # 触发条件：首批即时；后续按节奏——前重/均匀用 ON_BREAK 保护，
    # 后重用 ON_REBOUND 等反弹；末批 ON_TIME 兜底（时间到必清）
    tranches: list[Tranche] = []
    cumulative = 0.0
    for i, frac in enumerate(fractions):
        cumulative += frac
        if i == 0:
            trigger = TrancheTrigger.IMMEDIATE
        elif i == tranche_count - 1:
            trigger = TrancheTrigger.ON_TIME
        elif pacing is PacingStyle.BACK_LOADED:
            trigger = TrancheTrigger.ON_REBOUND
        else:
            trigger = TrancheTrigger.ON_BREAK
        tranches.append(
            Tranche(
                index=i,
                fraction=frac,
                weight=total_weight * frac,
                trigger=trigger,
                cumulative_fraction=cumulative,
            )
        )

    # T+1：首批即时动作 ≤ 可卖；冻结超出部分顺延（附加到次批ON_TIME提示）
    first = tranches[0]
    deferred = max(0.0, first.weight - sellable_weight)
    notes: list[str] = []
    if deferred > 1e-12:
        capped_first = Tranche(
            index=first.index,
            fraction=first.fraction,
            weight=sellable_weight,
            trigger=first.trigger,
            cumulative_fraction=first.cumulative_fraction,
        )
        tranches[0] = capped_first
        notes.append(f"T+1 约束：首批计划 {first.weight:.4f} 中 {deferred:.4f} 当日买入冻结，顺延至后续批次")

    return ScalingPlan(
        total_weight=total_weight,
        urgency=urgency,
        pacing=pacing,
        tranches=tuple(tranches),
        t1_deferred_weight=deferred,
        notes=tuple(notes),
    )
