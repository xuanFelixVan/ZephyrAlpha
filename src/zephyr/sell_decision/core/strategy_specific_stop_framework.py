# [BLUEPRINT] MOD-SELL-014 | docs/03_modules/MOD-SELL-014/
# [MODULE] zephyr.sell_decision.core.strategy_specific_stop_framework
# [DOMAIN] D_SELL_DECISION
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] MOD-SELL-013(离场情景规划) ; MOD-SELL-017(分批卖出架构) ; MOD-SELL-001(信号源)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 策略风格画像→止损参数映射(趋势宽/均值回归紧); 移动止损与保本线在浮盈≥breakeven_trigger后激活; 有效止损价=max(初始,移动,保本)最紧优先; 触发归因按TRAILING>BREAKEVEN>INITIAL; 画像=风格枚举非具体策略名(三维解耦红线); 纯函数可单测
# [MODIFY-GUARD] docs/03_modules/MOD-SELL-014/
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidStopFrameworkInputError(ZA-SELL-0021)
# [TESTS] tests/sell_decision/test_strategy_specific_stop_framework.py
# [A_module] module_id=MOD-SELL-014 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
Strategy Specific Stop Framework — 策略特异止损框架 (MOD-SELL-014)

不同策略**风格**适用不同止损结构（趋势策略给宽止损留喘息、均值回归
给紧止损快认错）。框架提供"风格画像 → 止损参数"映射与统一止损状态
计算，输出四类触发：

  - INITIAL_STOP：现价 ≤ 入场价×(1−initial_stop_pct)（硬止损）；
  - TRAILING_STOP：浮盈曾达 breakeven_trigger 后，现价 ≤
    持仓内最高价×(1−trailing_stop_pct)（移动止盈止损）；
  - BREAKEVEN_STOP：浮盈曾达 trigger 后回落至入场价之下（不亏为底）；
  - TIME_STOP：持有天数 > time_stop_days（时间止损）。

有效止损价 = max(初始线, 移动线, 保本线)（最紧优先）；移动线与保本线
在浮盈 ≥ breakeven_trigger_pct 后才激活。

红线（三维解耦）：StrategyProfile 是**风格画像**（趋势/均值回归/突破/
波段的通用止损结构特征），不是具体选股策略名——止损框架不认识任何
具体策略，策略侧只需声明自己的风格画像。

纪律：纯函数、无 IO；价格/持有期由调用方注入。
Version: 1.0.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: profile 参数
#   fields: 参数 profile，类型注解 StrategyProfile
#   code: strategy_specific_stop_framework.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: position 参数
#   fields: 参数 position，类型注解 StopPositionInput
#   code: strategy_specific_stop_framework.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: overrides 参数
#   fields: 参数 overrides（无注解）
#   code: strategy_specific_stop_framework.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① default_stop_params
#   name_en: default_stop_params
#   intro: 取风格画像的默认止损参数。
#   desc: 取风格画像的默认止损参数。；源码 L219-L221
#   inputs: profile
#   outputs: StopParams
# - id: A2
#   name_zh: ② compute_stop_state
#   name_en: compute_stop_state
#   intro: 计算持仓止损状态（纯函数）。
#   desc: 计算持仓止损状态（纯函数）。 Args: position: 入场价/现价/入场后最高价/持有天数 profile: 策略风格画像 overrides: 参数覆写（缺省用画像默认…；源码 L236-L315
#   inputs: position profile overrides
#   outputs: StopEvaluation
#   （注：A2 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: StopParams
#   name_en: StopParams
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-SELL-013(离场情景规划) ; MOD-SELL-017(分批卖出架构) ; MOD-SELL-001(信号源)
# - id: O2
#   name_zh: StopEvaluation
#   name_en: StopEvaluation
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-SELL-013(离场情景规划) ; MOD-SELL-017(分批卖出架构) ; MOD-SELL-001(信号源)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Final

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "InvalidStopFrameworkInputError",
    "StopEvaluation",
    "StopParams",
    "StopPositionInput",
    "StopReason",
    "StrategyProfile",
    "compute_stop_state",
    "default_stop_params",
]


class StrategyProfile(str, Enum):
    """策略风格画像（止损结构维度，非具体策略名——三维解耦红线）。"""

    TREND_FOLLOWING = "TREND_FOLLOWING"  # 趋势跟踪（宽止损/长时预算）
    MEAN_REVERSION = "MEAN_REVERSION"  # 均值回归（紧止损/短时预算）
    BREAKOUT = "BREAKOUT"  # 突破（中紧止损/快速认错）
    SWING = "SWING"  # 波段（中止损/中时预算）


class StopReason(str, Enum):
    """止损触发原因。"""

    NONE = "NONE"
    INITIAL_STOP = "INITIAL_STOP"
    TRAILING_STOP = "TRAILING_STOP"
    BREAKEVEN_STOP = "BREAKEVEN_STOP"
    TIME_STOP = "TIME_STOP"


class InvalidStopFrameworkInputError(ZephyrBaseError):
    """止损框架输入非法（价格非正/高点异常/参数越界）。"""

    error_code = "ZA-SELL-0021"


@dataclass(frozen=True)
class StopParams:
    """止损参数集。

    Attributes:
        initial_stop_pct: 初始止损幅度 ∈(0,1)（入场价×(1−x)=硬止损线）
        trailing_stop_pct: 移动止损幅度 ∈(0,1)（最高价×(1−x)=移动线）
        time_stop_days: 时间止损天数 ≥1
        breakeven_trigger_pct: 保本/移动止损激活浮盈 ∈(0,1)
    """

    initial_stop_pct: float
    trailing_stop_pct: float
    time_stop_days: int
    breakeven_trigger_pct: float


# 风格画像 → 默认止损参数（经验基线，可经 overrides 覆写）
_PROFILE_DEFAULTS: Final = {
    StrategyProfile.TREND_FOLLOWING: StopParams(
        initial_stop_pct=0.12,
        trailing_stop_pct=0.08,
        time_stop_days=60,
        breakeven_trigger_pct=0.05,
    ),
    StrategyProfile.MEAN_REVERSION: StopParams(
        initial_stop_pct=0.05,
        trailing_stop_pct=0.03,
        time_stop_days=10,
        breakeven_trigger_pct=0.03,
    ),
    StrategyProfile.BREAKOUT: StopParams(
        initial_stop_pct=0.06,
        trailing_stop_pct=0.04,
        time_stop_days=15,
        breakeven_trigger_pct=0.04,
    ),
    StrategyProfile.SWING: StopParams(
        initial_stop_pct=0.08,
        trailing_stop_pct=0.05,
        time_stop_days=30,
        breakeven_trigger_pct=0.06,
    ),
}


@dataclass(frozen=True)
class StopPositionInput:
    """止损计算输入。

    Attributes:
        entry_price: 入场价（>0）
        current_price: 现价（>0）
        highest_since_entry: 入场后最高价（≥entry_price）
        days_held: 已持有天数（≥0）
    """

    entry_price: float
    current_price: float
    highest_since_entry: float
    days_held: int


@dataclass(frozen=True)
class StopEvaluation:
    """止损评估结果（frozen 不可变）。

    Attributes:
        should_stop: 是否触发任一止损
        reason: 触发原因（NONE=未触发）
        active_stop_price: 当前有效止损价（最紧）
        params: 实际使用的参数（含覆写）
        profile: 风格画像
    """

    should_stop: bool
    reason: StopReason
    active_stop_price: float
    params: StopParams
    profile: StrategyProfile


def default_stop_params(profile: StrategyProfile) -> StopParams:
    """取风格画像的默认止损参数。"""
    return _PROFILE_DEFAULTS[profile]


def _validate_params(p: StopParams) -> None:
    for name, v in (
        ("initial_stop_pct", p.initial_stop_pct),
        ("trailing_stop_pct", p.trailing_stop_pct),
        ("breakeven_trigger_pct", p.breakeven_trigger_pct),
    ):
        if not math.isfinite(v) or v <= 0.0 or v >= 1.0:
            raise InvalidStopFrameworkInputError(f"{name} 非法（须 ∈(0,1)），got {v}")
    if p.time_stop_days < 1:
        raise InvalidStopFrameworkInputError(f"time_stop_days 非法（须 ≥1），got {p.time_stop_days}")


def compute_stop_state(
    position: StopPositionInput,
    profile: StrategyProfile,
    *,
    overrides: StopParams | None = None,
) -> StopEvaluation:
    """计算持仓止损状态（纯函数）。

    Args:
        position: 入场价/现价/入场后最高价/持有天数
        profile: 策略风格画像
        overrides: 参数覆写（缺省用画像默认）

    Returns:
        StopEvaluation

    Raises:
        InvalidStopFrameworkInputError: 输入/参数非法
    """
    for name, v in (
        ("entry_price", position.entry_price),
        ("current_price", position.current_price),
        ("highest_since_entry", position.highest_since_entry),
    ):
        if not math.isfinite(v) or v <= 0.0:
            raise InvalidStopFrameworkInputError(f"{name} 非法（须为正有限值），got {v}")
    if position.highest_since_entry < position.entry_price:
        raise InvalidStopFrameworkInputError(
            f"入场后最高价 {position.highest_since_entry} 低于入场价 {position.entry_price}（数据异常）"
        )
    if position.days_held < 0:
        raise InvalidStopFrameworkInputError(f"days_held 非法（须 ≥0），got {position.days_held}")

    params = overrides if overrides is not None else default_stop_params(profile)
    _validate_params(params)

    initial_line = position.entry_price * (1.0 - params.initial_stop_pct)

    # 浮盈曾达 trigger → 激活移动止损线与保本线
    activated = position.highest_since_entry >= position.entry_price * (1.0 + params.breakeven_trigger_pct)
    trailing_line = position.highest_since_entry * (1.0 - params.trailing_stop_pct) if activated else None
    breakeven_line = position.entry_price if activated else None

    # 有效止损价=最紧（最高）线；归因优先级 TRAILING > BREAKEVEN > INITIAL
    lines: list[tuple[float, StopReason]] = [(initial_line, StopReason.INITIAL_STOP)]
    if breakeven_line is not None:
        lines.append((breakeven_line, StopReason.BREAKEVEN_STOP))
    if trailing_line is not None:
        lines.append((trailing_line, StopReason.TRAILING_STOP))
    _PRIORITY: Final = {
        StopReason.INITIAL_STOP: 0,
        StopReason.BREAKEVEN_STOP: 1,
        StopReason.TRAILING_STOP: 2,
    }
    active_price, _ = max(lines, key=lambda x: x[0])
    active_reason = max(lines, key=lambda x: (x[0], _PRIORITY[x[1]]))[1]

    if position.current_price <= active_price:
        return StopEvaluation(
            should_stop=True,
            reason=active_reason,
            active_stop_price=active_price,
            params=params,
            profile=profile,
        )
    if position.days_held > params.time_stop_days:
        return StopEvaluation(
            should_stop=True,
            reason=StopReason.TIME_STOP,
            active_stop_price=active_price,
            params=params,
            profile=profile,
        )
    return StopEvaluation(
        should_stop=False,
        reason=StopReason.NONE,
        active_stop_price=active_price,
        params=params,
        profile=profile,
    )
