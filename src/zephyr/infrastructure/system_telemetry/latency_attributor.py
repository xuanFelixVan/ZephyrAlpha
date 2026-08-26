# [BLUEPRINT] MOD-INF-084 | docs/03_modules/_domain_infrastructure_operations/latency_attributor/blueprint.md
# [MODULE] zephyr.infrastructure.system_telemetry.latency_attributor
# [DOMAIN] D_INFRA_TELEMETRY
# [DEPENDENCIES] 无（纯内存；span 序列/慢阈/环形容量全注入，不触网）
# [CONSUMERS] 运行时装配批（Tick→信号→订单链路巡检 / 周报聚合消费）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 占比按 (-duration_ms, stage) 确定性降序; top_stage=最大贡献阶段; 慢样本环形缓冲容量固定（默认100）先进先出覆盖; 周报 P50/P95 最近秩法确定性; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_infrastructure_operations/latency_attributor/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] LatencyAttributorError(占位 ZA-INF-UNREGISTERED-LATENCY-ATTRIBUTOR)——空trace_id/空span序列/空stage/负时长/零总时长/非法容量/非法慢阈时抛
# [TESTS] tests/infrastructure/test_latency_attributor.py
# [A_module] module_id=MOD-INF-084 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""LatencyAttributor — 延迟归因器（MOD-INF-084）。

B14-04702（AUD-DRAFT-001-DIGEST P2 波 P2-W01，CAND-INFRATEL-004，A9运维架构
§8.3.11）：基于注入 Span 序列对 Tick→信号→订单链路分段统计，各阶段占比排序
并定位最大贡献阶段；慢链路样本环形缓冲（容量注入，默认 100）留存 + 周报聚合
（按阶段 P50/P95/max 字典）。Dapper 式归因纯内存版。

查重分工（蓝图 §0）：performance_monitor=实时性能计数（本件为离线归因聚合，
不重建实时计数）；latency_budget_allocator=预算分配（本件只做归因统计，零交
集）。
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Final, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "AttributionReport",
    "LatencyAttributor",
    "LatencyAttributorError",
    "SlowSample",
    "StageShare",
    "StageSpan",
]

#: 慢链路样本环形缓冲默认容量
_DEFAULT_CAPACITY: Final[int] = 100
#: 默认慢链路阈值（毫秒）
_DEFAULT_SLOW_THRESHOLD_MS: Final[float] = 1000.0


class LatencyAttributorError(Exception):
    """延迟归因输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-INF-UNREGISTERED-LATENCY-ATTRIBUTOR。
    """


@dataclass(frozen=True)
class StageSpan:
    """链路阶段耗时（注入 span 序列单元，frozen）。"""

    stage: str
    duration_ms: float


@dataclass(frozen=True)
class StageShare:
    """阶段占比（frozen）。"""

    stage: str
    duration_ms: float
    share: float


@dataclass(frozen=True)
class AttributionReport:
    """单链路归因报告（占比降序 + 最大贡献阶段，frozen）。"""

    trace_id: str
    total_ms: float
    shares: tuple[StageShare, ...]
    top_stage: str


@dataclass(frozen=True)
class SlowSample:
    """慢链路样本（环形缓冲留存单元，frozen）。"""

    trace_id: str
    total_ms: float
    top_stage: str


def _percentile(sorted_vals: Sequence[float], pct: int) -> float:
    """最近秩百分位（确定性）：rank=ceil(pct/100*n)，1 起。"""
    rank = max(1, math.ceil(pct / 100.0 * len(sorted_vals)))
    return sorted_vals[rank - 1]


class LatencyAttributor:
    """延迟归因器（占比归因 + 慢样本环形缓冲 + 周报聚合）。"""

    def __init__(
        self,
        *,
        slow_threshold_ms: float = _DEFAULT_SLOW_THRESHOLD_MS,
        capacity: int = _DEFAULT_CAPACITY,
    ) -> None:
        if slow_threshold_ms < 0:
            raise LatencyAttributorError(f"slow_threshold_ms 非法: {slow_threshold_ms!r}")
        if not isinstance(capacity, int) or capacity <= 0:
            raise LatencyAttributorError(f"capacity 非法: {capacity!r}")
        self._slow_threshold = float(slow_threshold_ms)
        self._capacity = capacity
        self._ring: list[SlowSample | None] = [None] * capacity
        self._ring_next = 0
        self._ring_count = 0
        self._stage_durations: dict[str, list[float]] = {}

    # ── 归因 ─────────────────────────────────────────────────────────────

    def attribute(self, trace_id: str, spans: Sequence[StageSpan]) -> AttributionReport:
        """归因：各阶段占比降序 + 最大贡献阶段；超慢阈样本入环形缓冲。"""
        if not trace_id:
            raise LatencyAttributorError("trace_id 为空")
        if not spans:
            raise LatencyAttributorError("span 序列为空")
        for span in spans:
            if not span.stage:
                raise LatencyAttributorError("stage 为空")
            if span.duration_ms < 0:
                raise LatencyAttributorError(
                    f"duration_ms 负值: {span.stage}={span.duration_ms!r}"
                )
        total = sum(s.duration_ms for s in spans)
        if total <= 0:
            raise LatencyAttributorError(f"总时长为零，无法归因: {trace_id!r}")

        shares = tuple(sorted(
            (StageShare(stage=s.stage, duration_ms=s.duration_ms,
                        share=s.duration_ms / total) for s in spans),
            key=lambda s: (-s.duration_ms, s.stage),
        ))
        report = AttributionReport(
            trace_id=trace_id,
            total_ms=total,
            shares=shares,
            top_stage=shares[0].stage,
        )
        for span in spans:
            self._stage_durations.setdefault(span.stage, []).append(span.duration_ms)
        if total >= self._slow_threshold:
            sample = SlowSample(trace_id=trace_id, total_ms=total, top_stage=report.top_stage)
            self._ring[self._ring_next] = sample
            self._ring_next = (self._ring_next + 1) % self._capacity
            self._ring_count = min(self._ring_count + 1, self._capacity)
            _log.info("慢链路样本留存: %s total=%.1fms top=%s",
                      trace_id, total, report.top_stage)
        return report

    # ── 慢链路样本 ────────────────────────────────────────────────────────

    def slow_samples(self) -> tuple[SlowSample, ...]:
        """慢样本按留存先后（环形缓冲先进先出覆盖语义）。"""
        if self._ring_count < self._capacity:
            return tuple(s for s in self._ring[: self._ring_count] if s is not None)
        return tuple(
            s for s in (self._ring[self._ring_next:] + self._ring[: self._ring_next])
            if s is not None
        )

    # ── 周报聚合 ──────────────────────────────────────────────────────────

    def weekly_report(self) -> dict[str, dict[str, float]]:
        """周报：按阶段 P50/P95/max/count（键按阶段名排序，确定性）。"""
        out: dict[str, dict[str, float]] = {}
        for stage in sorted(self._stage_durations):
            vals = sorted(self._stage_durations[stage])
            out[stage] = {
                "count": float(len(vals)),
                "p50": _percentile(vals, 50),
                "p95": _percentile(vals, 95),
                "max": vals[-1],
            }
        return out
