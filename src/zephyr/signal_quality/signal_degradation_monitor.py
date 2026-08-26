# [BLUEPRINT] MOD-SIGQC-004 | docs/03_modules/_domain_signal_quality/signal_degradation_monitor/blueprint.md
# [MODULE] zephyr.signal_quality.signal_degradation_monitor
# [DOMAIN] D_SIGQC
# [DEPENDENCIES] 无（监控核心纯内存；clock/alert_router/mark_sink 全注入）
# [CONSUMERS] 运行时装配批（信号消费端降权联动 / 告警接 alert 路由）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 命中率/IC/衰减三指标滚动窗(maxlen有界); 阈值判定worst-of分级(NONE/MILD/MODERATE/SEVERE); 样本不足不判定不告警; 降级即告警+降权标记,恢复清除标记; 监控不阻断流水线(质量降级不抛,回调异常仅记日志); 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_signal_quality/signal_degradation_monitor/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] SignalDegradationError(占位 ZA-SIGQC-UNREGISTERED-SIGNAL-DEGRADATION)——空signal_id/IC越界/hit非bool/非法窗长阈值/未知信号评估时抛（质量降级本身不抛）
# [TESTS] tests/signal_quality/test_signal_degradation_monitor.py
# [A_module] module_id=MOD-SIGQC-004 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""SignalDegradationMonitor — 信号质量退化监控器（MOD-SIGQC-004）。

B13-04309（AUD-DRAFT-001-DIGEST P2 波 P2-W15，CAND-SIGQC-003，A3
D-SIGNAL-156）：质量指标（命中率/IC/衰减）滚动窗跟踪 + 阈值判定 + 自动告
警（注入 alert_router）+ 降级信号标记（联动消费端降权语义）+ 不阻断流水
线——实现 DegradationMonitorBase 的 DEG 语义（仅通知降权，不阻断）。

查重分工（蓝图 §0）：degradation_detector（MOD-SIGQC-001）=多维滑窗基线
对比检测器（IC衰减/覆盖率骤降/方向漂移，绑定 D-DATA-112 alerter 与
signal_audit 设施）；本件=轻量三指标滚动窗阈值监控器，alert_router 与
mark_sink 全回调注入，不绑具体设施，消费端凭 weight_hint 降权。
"""

from __future__ import annotations

import datetime
import logging
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "DegradationAlert",
    "DegradationLevel",
    "DegradationReport",
    "QualityObservation",
    "SignalDegradationError",
    "SignalDegradationMonitor",
]

#: 零均值判定精度
_EPS: Final[float] = 1e-12


class SignalDegradationError(Exception):
    """退化监控输入非法（Fail-Closed；质量降级本身不抛）。

    未登记错误码-申请中：占位 ZA-SIGQC-UNREGISTERED-SIGNAL-DEGRADATION。
    """


class DegradationLevel(str, Enum):
    """降级分级（对齐 DEG 基类语义：NONE/MILD/MODERATE/SEVERE）。"""

    NONE = "NONE"
    MILD = "MILD"
    MODERATE = "MODERATE"
    SEVERE = "SEVERE"


#: 分级序号（worst-of 合成取大者）
_LEVEL_RANK: Final[dict[DegradationLevel, int]] = {
    DegradationLevel.NONE: 0,
    DegradationLevel.MILD: 1,
    DegradationLevel.MODERATE: 2,
    DegradationLevel.SEVERE: 3,
}


@dataclass(frozen=True)
class QualityObservation:
    """单条信号质量观测（frozen）。hit=是否命中；ic=当期信息系数 [-1,1]。"""

    signal_id: str
    hit: bool
    ic: float
    observed_at: datetime.datetime


@dataclass(frozen=True)
class DegradationAlert:
    """自动告警载荷（注入 alert_router）。"""

    signal_id: str
    level: DegradationLevel
    reasons: tuple[str, ...]
    raised_at: datetime.datetime


@dataclass(frozen=True)
class DegradationReport:
    """滚动窗评估报告（frozen；degraded ⇔ level != NONE）。"""

    signal_id: str
    level: DegradationLevel
    sample_size: int
    hit_rate: float
    ic_mean: float
    decay: float
    reasons: tuple[str, ...]
    assessed_at: datetime.datetime

    @property
    def degraded(self) -> bool:
        """是否降级（level != NONE）。"""
        return self.level is not DegradationLevel.NONE


class SignalDegradationMonitor:
    """三指标滚动窗退化监控器（纯内存/DI，不阻断流水线）。

    - 指标：命中率（hit 均值）/ IC 均值 / 衰减（窗内前半 IC 均值相对后半的
      回落占比，|前半均值|≈0 时退化为 0）。
    - 判定（worst-of）：命中率 < floor → MODERATE，< floor/2 → SEVERE；
      IC 均值 < floor → MODERATE，≤ 0 → SEVERE；衰减 ≥ warn → MILD，
      ≥ severe → MODERATE。样本不足 min_samples → NONE 不告警。
    - 联动：降级 → alert_router 告警 + mark_sink 降权标记（weight_hint）；
      恢复 NONE → 清除标记并通知。回调异常仅记日志，不阻断。
    """

    def __init__(
        self,
        *,
        window_size: int = 20,
        min_samples: int = 5,
        hit_rate_floor: float = 0.4,
        ic_floor: float = 0.02,
        decay_warn: float = 0.5,
        decay_severe: float = 0.8,
        degraded_weight: float = 0.5,
        clock: Callable[[], datetime.datetime] | None = None,
        alert_router: Callable[[DegradationAlert], None] | None = None,
        mark_sink: Callable[[str, DegradationLevel, float], None] | None = None,
    ) -> None:
        if window_size < 2:
            raise SignalDegradationError(f"window_size 须 ≥2，实际 {window_size!r}")
        if not 1 <= min_samples <= window_size:
            raise SignalDegradationError(
                f"min_samples 须在 [1, window_size]，实际 {min_samples!r}"
            )
        if not 0.0 < hit_rate_floor <= 1.0:
            raise SignalDegradationError(f"hit_rate_floor 须在 (0,1]，实际 {hit_rate_floor!r}")
        if not 0.0 < ic_floor <= 1.0:
            raise SignalDegradationError(f"ic_floor 须在 (0,1]，实际 {ic_floor!r}")
        if not 0.0 < decay_warn <= decay_severe:
            raise SignalDegradationError(
                f"衰减阈值须 0 < warn ≤ severe，实际 warn={decay_warn!r} severe={decay_severe!r}"
            )
        if not 0.0 <= degraded_weight < 1.0:
            raise SignalDegradationError(f"degraded_weight 须在 [0,1)，实际 {degraded_weight!r}")
        self._window_size = window_size
        self._min_samples = min_samples
        self._hit_rate_floor = float(hit_rate_floor)
        self._ic_floor = float(ic_floor)
        self._decay_warn = float(decay_warn)
        self._decay_severe = float(decay_severe)
        self._degraded_weight = float(degraded_weight)
        self._clock = clock or datetime.datetime.now
        self._alert_router = alert_router
        self._mark_sink = mark_sink
        self._obs: dict[str, deque[QualityObservation]] = {}
        self._marked: dict[str, DegradationLevel] = {}

    # ── 内部 ─────────────────────────────────────────────────────────────

    @staticmethod
    def _metrics(window: deque[QualityObservation]) -> tuple[float, float, float]:
        hits = [1.0 if o.hit else 0.0 for o in window]
        ics = [o.ic for o in window]
        hit_rate = sum(hits) / len(hits)
        ic_mean = sum(ics) / len(ics)
        half = len(ics) // 2
        early = ics[:half] or ics[:1]
        recent = ics[half:] or ics[-1:]
        early_mean = sum(early) / len(early)
        recent_mean = sum(recent) / len(recent)
        if abs(early_mean) > _EPS:
            decay = max(0.0, (early_mean - recent_mean) / abs(early_mean))
        else:
            decay = 0.0
        return hit_rate, ic_mean, decay

    def _judge(
        self, hit_rate: float, ic_mean: float, decay: float
    ) -> tuple[DegradationLevel, tuple[str, ...]]:
        level = DegradationLevel.NONE
        reasons: list[str] = []

        def _raise(candidate: DegradationLevel, reason: str) -> None:
            nonlocal level
            if _LEVEL_RANK[candidate] > _LEVEL_RANK[level]:
                level = candidate
            reasons.append(reason)

        if hit_rate < self._hit_rate_floor / 2:
            _raise(
                DegradationLevel.SEVERE,
                f"命中率崩塌 {hit_rate:.2f} < {self._hit_rate_floor / 2:.2f}",
            )
        elif hit_rate < self._hit_rate_floor:
            _raise(
                DegradationLevel.MODERATE,
                f"命中率低于阈值 {hit_rate:.2f} < {self._hit_rate_floor:.2f}",
            )
        if ic_mean <= 0.0:
            _raise(DegradationLevel.SEVERE, f"IC 均值符号翻转 {ic_mean:.4f} ≤ 0")
        elif ic_mean < self._ic_floor:
            _raise(
                DegradationLevel.MODERATE,
                f"IC 均值低于阈值 {ic_mean:.4f} < {self._ic_floor:.2f}",
            )
        if decay >= self._decay_severe:
            _raise(
                DegradationLevel.MODERATE,
                f"IC 衰减 {decay:.2f} ≥ {self._decay_severe:.2f}",
            )
        elif decay >= self._decay_warn:
            _raise(DegradationLevel.MILD, f"IC 衰减 {decay:.2f} ≥ {self._decay_warn:.2f}")
        return level, tuple(reasons)

    def _alert(self, report: DegradationReport) -> None:
        _log.warning(
            "信号降级: %s %s (%s)", report.signal_id, report.level.value, ";".join(report.reasons)
        )
        if self._alert_router is not None:
            try:
                self._alert_router(
                    DegradationAlert(
                        signal_id=report.signal_id,
                        level=report.level,
                        reasons=report.reasons,
                        raised_at=report.assessed_at,
                    )
                )
            except Exception:  # noqa: BLE001 — 告警不阻断流水线（蓝图 §1）
                _log.exception("alert_router 告警失败: %s", report.signal_id)

    def _mark(self, signal_id: str, level: DegradationLevel, weight: float) -> None:
        if self._mark_sink is not None:
            try:
                self._mark_sink(signal_id, level, weight)
            except Exception:  # noqa: BLE001 — 标记不阻断流水线
                _log.exception("mark_sink 标记失败: %s", signal_id)

    def _sync_mark(self, report: DegradationReport) -> None:
        prev = self._marked.get(report.signal_id)
        if report.degraded:
            self._alert(report)
            if prev is not report.level:
                self._marked[report.signal_id] = report.level
                self._mark(report.signal_id, report.level, self._degraded_weight)
        elif prev is not None:
            del self._marked[report.signal_id]
            self._mark(report.signal_id, DegradationLevel.NONE, 1.0)

    # ── 观测登记 ──────────────────────────────────────────────────────────

    def observe(self, obs: QualityObservation) -> None:
        """登记质量观测（非法输入 Fail-Closed；登记本身不做判定）。"""
        if not isinstance(obs, QualityObservation):
            raise SignalDegradationError(f"非法观测类型: {type(obs)!r}")
        if not obs.signal_id:
            raise SignalDegradationError("signal_id 为空")
        if not isinstance(obs.hit, bool):
            raise SignalDegradationError(f"hit 须为 bool，实际 {obs.hit!r}")
        if not -1.0 <= obs.ic <= 1.0:
            raise SignalDegradationError(f"ic 须在 [-1,1]，实际 {obs.ic!r}")
        if not isinstance(obs.observed_at, datetime.datetime):
            raise SignalDegradationError("observed_at 须为 datetime")
        window = self._obs.get(obs.signal_id)
        if window is None:
            window = deque(maxlen=self._window_size)
            self._obs[obs.signal_id] = window
        window.append(obs)

    # ── 评估（不阻断） ─────────────────────────────────────────────────────

    def evaluate(self, signal_id: str) -> DegradationReport:
        """评估单信号：样本不足 → NONE；降级 → 告警+降权标记（不阻断）。"""
        if not signal_id:
            raise SignalDegradationError("signal_id 为空")
        window = self._obs.get(signal_id)
        if window is None:
            raise SignalDegradationError(f"未知信号: {signal_id!r}（无观测）")
        hit_rate, ic_mean, decay = self._metrics(window)
        now = self._clock()
        if len(window) < self._min_samples:
            return DegradationReport(
                signal_id=signal_id,
                level=DegradationLevel.NONE,
                sample_size=len(window),
                hit_rate=hit_rate,
                ic_mean=ic_mean,
                decay=decay,
                reasons=(f"样本不足 {len(window)}/{self._min_samples}",),
                assessed_at=now,
            )
        level, reasons = self._judge(hit_rate, ic_mean, decay)
        report = DegradationReport(
            signal_id=signal_id,
            level=level,
            sample_size=len(window),
            hit_rate=hit_rate,
            ic_mean=ic_mean,
            decay=decay,
            reasons=reasons,
            assessed_at=now,
        )
        self._sync_mark(report)
        return report

    # ── 降权联动查询 ───────────────────────────────────────────────────────

    def is_degraded(self, signal_id: str) -> bool:
        """信号当前是否带降级标记。"""
        return signal_id in self._marked

    def weight_hint(self, signal_id: str) -> float:
        """消费端降权建议：降级 → degraded_weight；否则 1.0。"""
        return self._degraded_weight if signal_id in self._marked else 1.0

    def marked_signals(self) -> list[str]:
        """当前全部降级标记信号（确定性排序）。"""
        return sorted(self._marked)
