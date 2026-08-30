# [BLUEPRINT] MOD-DATA_ENG | docs/03_modules/_domain_data_eng/incremental_update_engine/blueprint.md
# [MODULE] zephyr.data_eng.incremental_update_engine
# [DOMAIN] D_DATA_ENG
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] zephyr.data.scheduler（MOD-L00-004，运行时装配批挂调度）; zephyr.factor.factor_base（incremental_compute 窗口状态供给）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 变更检测三通道确定性(水位线/updated_at/行数哈希); 抽样对账偏差超容差必告警(不静默); alert_sink异常不阻断; 注册表幂等(重复注册不覆盖窗口状态); 快照往返无损(to_snapshot/from_snapshot); occurred/updated时间串由调用方注入(不读墙钟)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] IncrementalUpdateError(ZA-DE-0001); InvalidIncrementalInputError
# [TESTS] tests/zephyr/data/test_incremental_update_engine.py
# [A_module] module_id=MOD-DATA_ENG | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: ChangeSignal(source_id/watermark/updated_at_max/row_count/row_hash)——源侧统一变更观测(三通道)
# I2: incremental/full 抽样行映射——增量结果与全量重算抽样对账输入
# I3: register/update_window_state——增量因子窗口状态登记(incremental_compute 挂调度前置)
# F1: detect_change(prev,curr)——统一变更检测: 三通道任一前进/变化→changed+reasons
# F2: SamplingReconciler.reconcile()——抽样对账: 匹配/差异/缺失计数→deviation_ratio>容差→告警(不静默)
# F3: IncrementalFactorRegistry——因子注册+窗口状态更新+快照持久化往返
# A1: 输入非法/未知因子/tolerance<0→Fail-Closed; sink 异常仅日志不阻断
# O1: ChangeVerdict / SampleReconcileResult / FactorWindowState(快照可持久化)
# [/ALGO_FLOW]
"""
D_DATA_ENG — Incremental Update Engine（91 增量更新协调引擎，§1 子模块清单）。

增量更新**协调层**（不重写同步逻辑）。与既有件边界：
  - data/scheduler（MOD-L00-004，D_DATA）：增量同步执行器（incremental+
    断点续传 progress_store）——本件复用其执行，不重复同步逻辑。
  - factor_base.incremental_compute（D_FACTOR）：因子滑动窗口增量计算——
    本件注册表为其提供窗口状态登记与持久化快照（挂调度前置）。
  - data_eng 既有 cleaning_anomaly_engine / expectation_governance：清洗与
    期望治理族，无增量协调件（D_DATA_ENG 增量族缺口）。

三大协调职责（TSV 裁定）：
  1. 统一变更检测：水位线/updated_at/行数哈希三通道（任一变化→变更）；
  2. 增量结果抽样全量对账：deviation_ratio 超容差→偏差告警（不静默）；
  3. 增量因子注册表：窗口状态登记+快照持久化（to_snapshot/from_snapshot）。

设计真源：B1-00635 / CAND-DATENG-003（AUD-DRAFT-001-DIGEST P1 波 W-P1-23）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: previous 参数
#   fields: 参数 previous，类型注解 ChangeSignal | None
#   code: incremental_update_engine.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: current 参数
#   fields: 参数 current，类型注解 ChangeSignal
#   code: incremental_update_engine.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① detect_change
#   name_en: detect_change
#   intro: 统一变更检测：三通道任一前进/变化即判变更（确定性，Fail-Closed）。
#   desc: 统一变更检测：三通道任一前进/变化即判变更（确定性，Fail-Closed）。 reasons 取值：FIRST_OBSERVATION / WATERMARK_ADVANCED…；源码 L147-L168
#   inputs: previous current
#   outputs: ChangeVerdict
# - id: A2
#   name_zh: ② SamplingReconciler
#   name_en: SamplingReconciler
#   intro: 增量结果抽样全量对账器（偏差告警不静默；sink 异常不阻断）。
#   desc: 增量结果抽样全量对账器（偏差告警不静默；sink 异常不阻断）。 alert_sink：注入式告警出口（装配批接 alerter）；缺失仅记 WARNING 日志。；公共方法（定义序）: reconcile…
#   inputs: tolerance_ratio alert_sink
#   outputs: 返回值
# - id: A3
#   name_zh: ③ IncrementalFactorRegistry
#   name_en: IncrementalFactorRegistry
#   intro: 增量因子注册表（incremental_compute 挂调度前置协调）。
#   desc: 增量因子注册表（incremental_compute 挂调度前置协调）。 窗口状态持久化：to_snapshot()/from_snapshot() 往返无损；运行时由调用方…；公共方法（定义序）: register…
#   inputs: 无参数
#   outputs: 返回值
# - id: A4
#   name_zh: ④ IncrementalUpdateEngine
#   name_en: IncrementalUpdateEngine
#   intro: 增量更新协调引擎门面：统一变更检测 + 抽样全量对账 + 增量因子注册表。
#   desc: 增量更新协调引擎门面：统一变更检测 + 抽样全量对账 + 增量因子注册表。 三职责单一入口（装配批挂调度）；各子件亦可独立使用。；公共方法（定义序）: detect_change, reconcile_sample；源…
#   inputs: tolerance_ratio alert_sink
#   outputs: 返回值
#   （注：A4 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: ChangeVerdict
#   name_en: ChangeVerdict
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.data.scheduler（MOD-L00-004，运行时装配批挂调度）; zephyr.factor.factor_base（increme…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping

from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)


class IncrementalUpdateError(ZephyrBaseError):
    """增量更新协调引擎基类异常。"""

    error_code = "ZA-DE-0001"


class InvalidIncrementalInputError(IncrementalUpdateError):
    """协调层输入非法——source_id 不一致/tolerance<0/未知因子/空键。"""

    error_code = "ZA-DE-0002"


@dataclass(frozen=True)
class ChangeSignal:
    """源侧统一变更观测（三通道：水位线/updated_at/行数哈希）。"""

    source_id: str
    watermark: str
    updated_at_max: str
    row_count: int
    row_hash: str
    schema_version: str = "1.0"


@dataclass(frozen=True)
class ChangeVerdict:
    """变更检测结论（changed + 触发原因清单）。"""

    source_id: str
    changed: bool
    reasons: tuple[str, ...] = field(default_factory=tuple)
    schema_version: str = "1.0"


def detect_change(previous: ChangeSignal | None, current: ChangeSignal) -> ChangeVerdict:
    """统一变更检测：三通道任一前进/变化即判变更（确定性，Fail-Closed）。

    reasons 取值：FIRST_OBSERVATION / WATERMARK_ADVANCED / UPDATED_AT_ADVANCED /
    ROW_COUNT_CHANGED / ROW_HASH_CHANGED。
    """
    if not current.source_id:
        raise InvalidIncrementalInputError("source_id 不能为空")
    if previous is None:
        return ChangeVerdict(source_id=current.source_id, changed=True, reasons=("FIRST_OBSERVATION",))
    if previous.source_id != current.source_id:
        raise InvalidIncrementalInputError(f"source_id 不一致: {previous.source_id} vs {current.source_id}")
    reasons: list[str] = []
    if current.watermark != previous.watermark:
        reasons.append("WATERMARK_ADVANCED")
    if current.updated_at_max != previous.updated_at_max:
        reasons.append("UPDATED_AT_ADVANCED")
    if current.row_count != previous.row_count:
        reasons.append("ROW_COUNT_CHANGED")
    if current.row_hash != previous.row_hash:
        reasons.append("ROW_HASH_CHANGED")
    return ChangeVerdict(source_id=current.source_id, changed=bool(reasons), reasons=tuple(reasons))


@dataclass(frozen=True)
class SampleReconcileResult:
    """增量结果抽样全量对账结论。"""

    matched: int
    mismatched: int
    missing_in_incremental: int
    missing_in_full: int
    deviation_ratio: float
    alerted: bool
    schema_version: str = "1.0"


class SamplingReconciler:
    """增量结果抽样全量对账器（偏差告警不静默；sink 异常不阻断）。

    alert_sink：注入式告警出口（装配批接 alerter）；缺失仅记 WARNING 日志。
    """

    def __init__(
        self,
        tolerance_ratio: float = 0.0,
        alert_sink: Callable[[str], None] | None = None,
    ) -> None:
        if tolerance_ratio < 0:
            raise InvalidIncrementalInputError("tolerance_ratio 不能为负")
        self._tolerance = tolerance_ratio
        self._alert_sink = alert_sink

    def reconcile(
        self,
        *,
        incremental: Mapping[Any, Any],
        full: Mapping[Any, Any],
    ) -> SampleReconcileResult:
        """抽样对账：按键对齐逐值比较，偏差率=差异数/全量键数。"""
        matched = 0
        mismatched = 0
        for key, full_value in full.items():
            if key not in incremental:
                continue
            if incremental[key] == full_value:
                matched += 1
            else:
                mismatched += 1
        missing_in_incremental = sum(1 for key in full if key not in incremental)
        missing_in_full = sum(1 for key in incremental if key not in full)
        denominator = len(full) if full else 0
        deviation = (mismatched + missing_in_incremental) / denominator if denominator else 0.0
        alerted = deviation > self._tolerance
        if alerted:
            self._alert(
                f"增量抽样对账偏差告警: deviation_ratio={deviation:.4f} "
                f"> tolerance={self._tolerance} (mismatched={mismatched}, "
                f"missing_in_incremental={missing_in_incremental})"
            )
        return SampleReconcileResult(
            matched=matched,
            mismatched=mismatched,
            missing_in_incremental=missing_in_incremental,
            missing_in_full=missing_in_full,
            deviation_ratio=deviation,
            alerted=alerted,
        )

    def _alert(self, message: str) -> None:
        if self._alert_sink is None:
            _logger.warning("增量对账偏差告警（无 sink，仅日志）: %s", message)
            return
        try:
            self._alert_sink(message)
        except Exception:  # noqa: BLE001 — sink 异常不阻断（记日志不静默）
            _logger.warning("incremental alert_sink 异常（不阻断对账）: %s", message, exc_info=True)


@dataclass(frozen=True)
class FactorWindowState:
    """增量因子窗口状态（滑动窗口+断点；快照可持久化）。"""

    factor_id: str
    window: int
    last_key: str = ""
    updated_at: str = ""
    schema_version: str = "1.0"


class IncrementalFactorRegistry:
    """增量因子注册表（incremental_compute 挂调度前置协调）。

    窗口状态持久化：to_snapshot()/from_snapshot() 往返无损；运行时由调用方
    （scheduler progress_store 等）落盘，本件不直接 IO。
    """

    def __init__(self) -> None:
        self._states: dict[str, FactorWindowState] = {}

    def register(self, factor_id: str, *, window: int) -> FactorWindowState:
        """幂等注册：重复注册返回既有状态（不覆盖窗口断点）。"""
        if not factor_id:
            raise InvalidIncrementalInputError("factor_id 不能为空")
        if window <= 0:
            raise InvalidIncrementalInputError("window 必须为正整数")
        existing = self._states.get(factor_id)
        if existing is not None:
            return existing
        state = FactorWindowState(factor_id=factor_id, window=window)
        self._states[factor_id] = state
        return state

    def update_window_state(self, factor_id: str, *, last_key: str, updated_at: str) -> FactorWindowState:
        """窗口状态前进（last_key/updated_at 由调用方注入，不读墙钟）。"""
        state = self._states.get(factor_id)
        if state is None:
            raise InvalidIncrementalInputError(f"未注册因子: {factor_id}")
        if not last_key:
            raise InvalidIncrementalInputError("last_key 不能为空")
        migrated = FactorWindowState(
            factor_id=state.factor_id,
            window=state.window,
            last_key=last_key,
            updated_at=updated_at,
        )
        self._states[factor_id] = migrated
        return migrated

    def get(self, factor_id: str) -> FactorWindowState | None:
        """按 factor_id 取窗口状态（不存在返回 None）。"""
        return self._states.get(factor_id)

    def to_snapshot(self) -> dict[str, dict[str, Any]]:
        """窗口状态快照（纯数据，调用方持久化）。"""
        return {
            factor_id: {
                "window": state.window,
                "last_key": state.last_key,
                "updated_at": state.updated_at,
                "schema_version": state.schema_version,
            }
            for factor_id, state in self._states.items()
        }

    @classmethod
    def from_snapshot(cls, snapshot: Mapping[str, Mapping[str, Any]]) -> IncrementalFactorRegistry:
        """快照恢复（与 to_snapshot 往返无损）。"""
        registry = cls()
        for factor_id, payload in snapshot.items():
            registry._states[factor_id] = FactorWindowState(
                factor_id=factor_id,
                window=int(payload["window"]),
                last_key=str(payload.get("last_key", "")),
                updated_at=str(payload.get("updated_at", "")),
            )
        return registry


class IncrementalUpdateEngine:
    """增量更新协调引擎门面：统一变更检测 + 抽样全量对账 + 增量因子注册表。

    三职责单一入口（装配批挂调度）；各子件亦可独立使用。
    """

    def __init__(
        self,
        tolerance_ratio: float = 0.0,
        alert_sink: Callable[[str], None] | None = None,
    ) -> None:
        self.reconciler = SamplingReconciler(tolerance_ratio=tolerance_ratio, alert_sink=alert_sink)
        self.factor_registry = IncrementalFactorRegistry()

    @staticmethod
    def detect_change(previous: ChangeSignal | None, current: ChangeSignal) -> ChangeVerdict:
        """统一变更检测（委托模块级 detect_change）。"""
        return detect_change(previous, current)

    def reconcile_sample(
        self,
        *,
        incremental: Mapping[Any, Any],
        full: Mapping[Any, Any],
    ) -> SampleReconcileResult:
        """增量结果抽样全量对账（委托 SamplingReconciler）。"""
        return self.reconciler.reconcile(incremental=incremental, full=full)


__all__ = [
    "ChangeSignal",
    "ChangeVerdict",
    "FactorWindowState",
    "IncrementalFactorRegistry",
    "IncrementalUpdateEngine",
    "IncrementalUpdateError",
    "InvalidIncrementalInputError",
    "SampleReconcileResult",
    "SamplingReconciler",
    "detect_change",
]
