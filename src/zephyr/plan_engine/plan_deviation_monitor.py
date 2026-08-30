# [BLUEPRINT] MOD-PLAN-022 | docs/03_modules/_domain_plan_engine/plan_deviation_monitor/blueprint.md
# [MODULE] zephyr.plan_engine.plan_deviation_monitor
# [DOMAIN] D_PLAN
# [DEPENDENCIES] 无（监控核心纯内存；留痕回调/时钟全注入）
# [CONSUMERS] 运行时装配批（盘中监控循环装配 / 留痕落 state_store / 计划外信号评审闸）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 偏差=实际-计划; z=偏差/σ(σ>0); |z|>2σ判定偏离(严格>); 有利偏差持有(z>0→hold_deviation)/不利纠错(z<0→correct_to_plan); 计划外强信号三重闸(z>3σ且E>0.5%且计划外仓位≤20%,前两者严格>); 每次评估必留痕(sink异常不阻断如实记录); 金额/比率Decimal-only拒绝float; 报告frozen; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_plan_engine/plan_deviation_monitor/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] PlanDeviationError(占位 ZA-PLAN-UNREGISTERED-PLAN-DEVIATION)——空标的/空信号/非Decimal/σ非正/阈值非法/仓位比越界时抛
# [TESTS] tests/plan_engine/test_plan_deviation_monitor.py
# [A_module] module_id=MOD-PLAN-022 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
PlanDeviationMonitor — 计划偏差检测与机会评估（MOD-PLAN-022）。

B10-01479（AUD-DRAFT-001-DIGEST P2 波 P2-W09，CAND-PLAN-016，A1 模块38）：

① 盘中计划偏差实时监控：实际收益 vs 盘前计划收益，偏差 = 实际 − 计划，
   z = 偏差/σ，|z| > 2σ 判定偏离（严格大于）；z > 0 = **有利偏差持有**
   （hold_deviation），z < 0 = **不利纠错**（correct_to_plan）；
② 计划外强信号评估：**三重闸**——z > 3σ 且 预期收益 E > 0.5% 且 计划外
   仓位 ≤ 20%（前两者严格大于，仓位含等号），全过才 passed；
③ 评估记录留痕：每次评估落记录（内存序列 + record_sink 回调，sink 异常
   不阻断如实记录）。

查重分工（蓝图 §0）：execution_deviation_attributor=执行偏差的**事后归因**
（滑点/时滞分解）；本件=**盘中实时**偏差监控与计划外机会三重闸评估，不
做事后归因。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: deviation_z_threshold 参数
#   fields: 参数 deviation_z_threshold（无注解）
#   code: plan_deviation_monitor.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: strong_signal_z 参数
#   fields: 参数 strong_signal_z（无注解）
#   code: plan_deviation_monitor.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: min_expected_return 参数
#   fields: 参数 min_expected_return（无注解）
#   code: plan_deviation_monitor.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: max_offplan_position_ratio 参数
#   fields: 参数 max_offplan_position_ratio（无注解）
#   code: plan_deviation_monitor.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① PlanDeviationMonitor
#   name_en: PlanDeviationMonitor
#   intro: 盘中计划偏差监控与计划外机会评估器（纯内存确定性，留痕/时钟注入）。
#   desc: 盘中计划偏差监控与计划外机会评估器（纯内存确定性，留痕/时钟注入）。；公共方法（定义序）: assess_deviation, assess_offplan_signal, records；源码 L158-L282
#   inputs: deviation_z_threshold strong_signal_z min_expected_return max_offplan…
#   outputs: 返回值
#   （注：A1 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: PlanDeviationMonitor
#   downstream: 运行时装配批（盘中监控循环装配 / 留痕落 state_store / 计划外信号评审闸）
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

import datetime
import logging
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "ACTION_CORRECT",
    "ACTION_HOLD",
    "ACTION_NONE",
    "DeviationAssessment",
    "DeviationKind",
    "OffplanSignalAssessment",
    "PlanDeviationError",
    "PlanDeviationMonitor",
]

ACTION_NONE: Final = "none"
ACTION_HOLD: Final = "hold_deviation"
ACTION_CORRECT: Final = "correct_to_plan"


class PlanDeviationError(Exception):
    """计划偏差监控输入/配置非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-PLAN-UNREGISTERED-PLAN-DEVIATION。
    """


class DeviationKind(str, Enum):
    """偏差分类。"""

    NONE = "none"  # 未越 2σ
    FAVORABLE = "favorable"  # 有利偏差持有
    ADVERSE = "adverse"  # 不利纠错


@dataclass(frozen=True)
class DeviationAssessment:
    """计划偏差评估记录（frozen）。"""

    symbol: str
    planned_return: Decimal
    actual_return: Decimal
    deviation: Decimal
    sigma: Decimal
    z_score: Decimal
    breached: bool
    kind: DeviationKind
    action: str
    assessed_at: datetime.datetime


@dataclass(frozen=True)
class OffplanSignalAssessment:
    """计划外强信号三重闸评估记录（frozen）。"""

    signal_id: str
    z_score: Decimal
    expected_return: Decimal
    offplan_position_ratio: Decimal
    gate_z: bool
    gate_expected: bool
    gate_position: bool
    passed: bool
    assessed_at: datetime.datetime


def _require_decimal(name: str, value: object) -> Decimal:
    if not isinstance(value, Decimal):
        raise PlanDeviationError(f"{name} 须为 Decimal（Decimal-only，拒绝 float 隐式转换）: {type(value).__name__}")
    if not value.is_finite():
        raise PlanDeviationError(f"{name} 非有限: {value!r}")
    return value


class PlanDeviationMonitor:
    """盘中计划偏差监控与计划外机会评估器（纯内存确定性，留痕/时钟注入）。"""

    def __init__(
        self,
        *,
        deviation_z_threshold: Decimal = Decimal("2"),
        strong_signal_z: Decimal = Decimal("3"),
        min_expected_return: Decimal = Decimal("0.005"),
        max_offplan_position_ratio: Decimal = Decimal("0.2"),
        record_sink: Callable[[object], None] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        _require_decimal("deviation_z_threshold", deviation_z_threshold)
        if deviation_z_threshold <= 0:
            raise PlanDeviationError(f"deviation_z_threshold 须为正: {deviation_z_threshold!r}")
        _require_decimal("strong_signal_z", strong_signal_z)
        if strong_signal_z <= 0:
            raise PlanDeviationError(f"strong_signal_z 须为正: {strong_signal_z!r}")
        _require_decimal("min_expected_return", min_expected_return)
        if min_expected_return < 0:
            raise PlanDeviationError(f"min_expected_return 须非负: {min_expected_return!r}")
        _require_decimal("max_offplan_position_ratio", max_offplan_position_ratio)
        if not (Decimal("0") < max_offplan_position_ratio <= Decimal("1")):
            raise PlanDeviationError(f"max_offplan_position_ratio 须在(0,1]: {max_offplan_position_ratio!r}")
        self._deviation_z_threshold = deviation_z_threshold
        self._strong_signal_z = strong_signal_z
        self._min_expected_return = min_expected_return
        self._max_offplan_position_ratio = max_offplan_position_ratio
        self._record_sink = record_sink
        self._clock = clock or datetime.datetime.now
        self._records: list[object] = []

    # ── 内部：留痕 ────────────────────────────────────────────────────────

    def _record(self, assessment: object) -> None:
        self._records.append(assessment)
        if self._record_sink is not None:
            try:
                self._record_sink(assessment)
            except Exception:  # noqa: BLE001 — 留痕不阻断（蓝图 §1）
                _log.exception("record_sink 留痕失败")

    # ── 计划偏差监控 ──────────────────────────────────────────────────────

    def assess_deviation(
        self, *, symbol: str, planned_return: Decimal, actual_return: Decimal, sigma: Decimal
    ) -> DeviationAssessment:
        """实际 vs 计划偏离评估：|z|>2σ 判定，有利持有/不利纠错。"""
        if not isinstance(symbol, str) or not symbol:
            raise PlanDeviationError("symbol 为空")
        _require_decimal("planned_return", planned_return)
        _require_decimal("actual_return", actual_return)
        _require_decimal("sigma", sigma)
        if sigma <= 0:
            raise PlanDeviationError(f"sigma 须为正: {sigma!r}")
        deviation = actual_return - planned_return
        z_score = deviation / sigma
        breached = abs(z_score) > self._deviation_z_threshold
        if not breached:
            kind, action = DeviationKind.NONE, ACTION_NONE
        elif z_score > 0:
            kind, action = DeviationKind.FAVORABLE, ACTION_HOLD
        else:
            kind, action = DeviationKind.ADVERSE, ACTION_CORRECT
        assessment = DeviationAssessment(
            symbol=symbol,
            planned_return=planned_return,
            actual_return=actual_return,
            deviation=deviation,
            sigma=sigma,
            z_score=z_score,
            breached=breached,
            kind=kind,
            action=action,
            assessed_at=self._clock(),
        )
        self._record(assessment)
        if breached:
            _log.warning("计划偏差越2σ: %s z=%s kind=%s", symbol, z_score, kind.value)
        return assessment

    # ── 计划外强信号评估 ──────────────────────────────────────────────────

    def assess_offplan_signal(
        self,
        *,
        signal_id: str,
        z_score: Decimal,
        expected_return: Decimal,
        offplan_position_ratio: Decimal,
    ) -> OffplanSignalAssessment:
        """计划外强信号三重闸：z>3σ 且 E>0.5% 且 计划外仓位≤20%。"""
        if not isinstance(signal_id, str) or not signal_id:
            raise PlanDeviationError("signal_id 为空")
        _require_decimal("z_score", z_score)
        _require_decimal("expected_return", expected_return)
        _require_decimal("offplan_position_ratio", offplan_position_ratio)
        if not (Decimal("0") <= offplan_position_ratio <= Decimal("1")):
            raise PlanDeviationError(f"offplan_position_ratio 须在[0,1]: {offplan_position_ratio!r}")
        gate_z = z_score > self._strong_signal_z
        gate_expected = expected_return > self._min_expected_return
        gate_position = offplan_position_ratio <= self._max_offplan_position_ratio
        passed = gate_z and gate_expected and gate_position
        assessment = OffplanSignalAssessment(
            signal_id=signal_id,
            z_score=z_score,
            expected_return=expected_return,
            offplan_position_ratio=offplan_position_ratio,
            gate_z=gate_z,
            gate_expected=gate_expected,
            gate_position=gate_position,
            passed=passed,
            assessed_at=self._clock(),
        )
        self._record(assessment)
        if passed:
            _log.info("计划外强信号三重闸通过: %s", signal_id)
        return assessment

    # ── 留痕查询 ──────────────────────────────────────────────────────────

    def records(self) -> tuple[object, ...]:
        """评估记录快照（按评估顺序，确定性）。"""
        return tuple(self._records)
