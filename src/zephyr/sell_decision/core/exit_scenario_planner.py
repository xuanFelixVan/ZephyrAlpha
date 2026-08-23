# [BLUEPRINT] MOD-SELL-013 | docs/03_modules/MOD-SELL-013/
# [MODULE] zephyr.sell_decision.core.exit_scenario_planner
# [DOMAIN] D_SELL_DECISION
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] MOD-SELL-017(分批卖出架构) ; MOD-SELL-018(做T协调) ; D-EX-CORE(执行)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 止损触发或紧迫≥0.8→IMMEDIATE; 0.5~0.8→SCALED; >0但<0.5→CONDITIONAL_HOLD; 0→HOLD; T+1内生(立即离场量=可卖权重,当日买入部分顺延提示); 情景按优先级确定性排序; 纯函数可单测
# [MODIFY-GUARD] docs/03_modules/MOD-SELL-013/
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidExitPlanInputError(ZA-SELL-0022)
# [TESTS] tests/sell_decision/test_exit_scenario_planner.py
# [A_module] module_id=MOD-SELL-013 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Exit Scenario Planner — 离场情景规划器 (MOD-SELL-013)

给一个持仓生成候选离场情景集并给出推荐：

  - IMMEDIATE_EXIT（立即离场）：止损触发或紧迫度 ≥0.8——
    动作量 = T+1 可卖权重（当日买入部分顺延，约束内生）；
  - SCALED_EXIT（分批离场）：紧迫度 0.5~0.8——首批减一半可卖量，
    降低单点冲击与"卖飞"懊悔；
  - CONDITIONAL_HOLD（条件持有）：紧迫度 (0,0.5)——持有但守止损线；
  - HOLD（继续持有）：紧迫度 0。

输出是"情景菜单 + 推荐"，不是下单指令——具体执行方式（how）由
执行域决定，本模块与选股策略（what）零耦合（三维解耦）。

纪律：纯函数、无 IO；紧迫度/止损状态由调用方注入（MOD-SELL-009/
MOD-SELL-014 产出可直插）。
Version: 1.0.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Final

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "ExitPlanningInput",
    "ExitScenario",
    "ExitScenarioOption",
    "ExitScenarioPlan",
    "InvalidExitPlanInputError",
    "plan_exit_scenarios",
]

_URGENT_THRESHOLD: Final = 0.8
_MID_THRESHOLD: Final = 0.5
# 分批离场首批比例
_SCALED_FIRST_BATCH: Final = 0.5


class ExitScenario(str, Enum):
    """离场情景。"""

    IMMEDIATE_EXIT = "IMMEDIATE_EXIT"  # 立即离场（可卖量内全出）
    SCALED_EXIT = "SCALED_EXIT"  # 分批离场
    CONDITIONAL_HOLD = "CONDITIONAL_HOLD"  # 条件持有（守止损线）
    HOLD = "HOLD"  # 继续持有


class InvalidExitPlanInputError(ZephyrBaseError):
    """离场情景规划输入非法（权重/紧迫度/可卖口径矛盾）。"""

    error_code = "ZA-SELL-0022"


@dataclass(frozen=True)
class ExitPlanningInput:
    """离场规划输入（>4 参数收 dataclass）。

    Attributes:
        symbol: 标的代码
        weight: 当前持仓权重 ≥0
        sellable_weight: T+1 可卖权重 ∈[0, weight]
        pnl_pct: 浮动盈亏
        days_held: 已持有天数 ≥0
        urgency: 紧迫度 ∈[0,1]（MOD-SELL-009 口径）
        stop_triggered: 止损是否触发（MOD-SELL-014 口径）
        stop_reason: 止损原因（留痕）
    """

    symbol: str
    weight: float
    sellable_weight: float
    pnl_pct: float
    days_held: int
    urgency: float
    stop_triggered: bool
    stop_reason: str = ""


@dataclass(frozen=True)
class ExitScenarioOption:
    """单个离场情景选项。

    Attributes:
        scenario: 情景
        priority: 优先级（0=推荐）
        action_weight: 本情景即时动作权重（HOLD 类=0）
        rationale: 人类可读理由
    """

    scenario: ExitScenario
    priority: int
    action_weight: float
    rationale: str


@dataclass(frozen=True)
class ExitScenarioPlan:
    """离场情景规划（frozen 不可变）。

    Attributes:
        symbol: 标的
        recommended: 推荐情景
        scenarios: 候选情景（按优先级升序）
        constraints: 约束提示（T+1 顺延等）
    """

    symbol: str
    recommended: ExitScenario
    scenarios: tuple[ExitScenarioOption, ...]
    constraints: tuple[str, ...] = field(default_factory=tuple)


def plan_exit_scenarios(intent: ExitPlanningInput) -> ExitScenarioPlan:
    """规划离场情景（纯函数）。

    Raises:
        InvalidExitPlanInputError: 输入非法
    """
    if not intent.symbol:
        raise InvalidExitPlanInputError("symbol 为空")
    for name, v in (("weight", intent.weight), ("sellable_weight", intent.sellable_weight)):
        if not math.isfinite(v) or v < 0.0:
            raise InvalidExitPlanInputError(f"{name} 非法（须为有限非负值），got {v}")
    if intent.sellable_weight > intent.weight + 1e-12:
        raise InvalidExitPlanInputError(
            f"可卖权重 {intent.sellable_weight} 超持仓权重 {intent.weight}（口径矛盾）"
        )
    if not math.isfinite(intent.urgency) or not (0.0 <= intent.urgency <= 1.0):
        raise InvalidExitPlanInputError(f"urgency 非法（须 ∈[0,1]），got {intent.urgency}")
    if intent.days_held < 0:
        raise InvalidExitPlanInputError(f"days_held 非法（须 ≥0），got {intent.days_held}")

    # 推荐裁定
    if intent.stop_triggered or intent.urgency >= _URGENT_THRESHOLD:
        recommended = ExitScenario.IMMEDIATE_EXIT
    elif intent.urgency >= _MID_THRESHOLD:
        recommended = ExitScenario.SCALED_EXIT
    elif intent.urgency > 0.0:
        recommended = ExitScenario.CONDITIONAL_HOLD
    else:
        recommended = ExitScenario.HOLD

    constraints: list[str] = []
    deferred = intent.weight - intent.sellable_weight
    if recommended is ExitScenario.IMMEDIATE_EXIT and deferred > 1e-12:
        constraints.append(
            f"T+1 约束：持仓 {intent.weight:.4f} 中 {deferred:.4f} 为当日买入冻结，顺延至次日可卖"
        )

    sellable = intent.sellable_weight
    options: list[ExitScenarioOption] = [
        ExitScenarioOption(
            scenario=ExitScenario.IMMEDIATE_EXIT,
            priority=0 if recommended is ExitScenario.IMMEDIATE_EXIT else 1,
            action_weight=sellable,
            rationale=(
                f"立即离场：止损触发({intent.stop_reason})" if intent.stop_triggered
                else f"立即离场：紧迫度 {intent.urgency:.2f} ≥ {_URGENT_THRESHOLD}"
            ),
        ),
        ExitScenarioOption(
            scenario=ExitScenario.SCALED_EXIT,
            priority=0 if recommended is ExitScenario.SCALED_EXIT else 1,
            action_weight=min(sellable * _SCALED_FIRST_BATCH, sellable),
            rationale=f"分批离场：首批 {_SCALED_FIRST_BATCH:.0%} 可卖量，降冲击与卖飞风险",
        ),
        ExitScenarioOption(
            scenario=ExitScenario.CONDITIONAL_HOLD,
            priority=0 if recommended is ExitScenario.CONDITIONAL_HOLD else 2,
            action_weight=0.0,
            rationale="条件持有：暂守止损线，触发即走",
        ),
        ExitScenarioOption(
            scenario=ExitScenario.HOLD,
            priority=0 if recommended is ExitScenario.HOLD else 3,
            action_weight=0.0,
            rationale="继续持有：无紧迫信号",
        ),
    ]
    options.sort(key=lambda o: (o.priority, o.scenario.value))

    return ExitScenarioPlan(
        symbol=intent.symbol,
        recommended=recommended,
        scenarios=tuple(options),
        constraints=tuple(constraints),
    )
