# [BLUEPRINT] MOD-RPT-033 | docs/03_modules/_domain_reporting/decision_trace_chain/blueprint.md
# [MODULE] zephyr.reporting.decision_trace_chain
# [DOMAIN] D_REPORTING
# [DEPENDENCIES] 无（协议核心纯内存；segment_store/factor_contributions/quantile_confidence/clock 全注入）
# [CONSUMERS] 运行时装配批（决策链四段落痕 / 全链反查 / 因子贡献摘要 / 密度感知置信度调整）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 段词表闭合(signal|plan|order|fill); decision_id 非空; 全链反查按段生命周期序+recorded_at 确定性排序; 因子贡献摘要按 |贡献度|降序+名称升序确定性排序; 密度感知置信度=分位数→置信度分桶映射(未注入/越界 Fail-Closed); 段存储副作用全注入(异常包装 Fail-Closed 不旁路); 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_reporting/decision_trace_chain/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] DecisionTraceError(占位 ZA-RPT-UNREGISTERED-DECISION-TRACE)——空decision_id/非法段/未知decision_id反查/贡献度或置信度映射未注入/分位数越界/存储异常时抛
# [TESTS] tests/reporting/test_decision_trace_chain.py
# [A_module] module_id=MOD-RPT-033 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
DecisionTraceChain — 决策溯源链（MOD-RPT-033）。

B1-00220（AUD-DRAFT-001-DIGEST P2 波 P2-W10，CAND-RPT-008，C2 C-030）：
决策链 ID 贯穿**信号→计划→订单→成交**四段（段记录注入存储，append-only
内存视图 + 注入落盘回调）+ **全链反查**（按 decision_id 聚合，段生命周期
序确定性排序）+ **因子贡献摘要**（注入贡献度，按 |贡献度| 降序+名称升序
排序）+ **密度感知置信度调整**（分位数→置信度分桶映射注入训练器语义）。

边界：decision_snapshot（signal_fundamental/audit）=决策快照采集点（本件
不重复采集，仅消费四段落痕记录）；训练器=分位数语义来源（本件仅消费注入
映射，不做密度估计）；本件纯内存/DI，不触网不落盘。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: segment_store 参数
#   fields: 参数 segment_store（无注解）
#   code: decision_trace_chain.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: factor_contributions 参数
#   fields: 参数 factor_contributions（无注解）
#   code: decision_trace_chain.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: quantile_confidence 参数
#   fields: 参数 quantile_confidence（无注解）
#   code: decision_trace_chain.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: decision_trace_chain.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① DecisionTraceChain
#   name_en: DecisionTraceChain
#   intro: 决策溯源链协议件（四段落痕 + 全链反查 + 因子摘要 + 置信度调整）。
#   desc: 决策溯源链协议件（四段落痕 + 全链反查 + 因子摘要 + 置信度调整）。；公共方法（定义序）: record_segment, segments_of, factor_summary, adjusted_confid…
#   inputs: segment_store factor_contributions quantile_confidence clock
#   outputs: 返回值
#   （注：A1 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（6 定义）
#   name_en: public defs
#   intro: DecisionTraceChain
#   downstream: 运行时装配批（决策链四段落痕 / 全链反查 / 因子贡献摘要 / 密度感知置信度调整）
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
from enum import Enum
from typing import Callable, Final, Mapping, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "DecisionTrace",
    "DecisionTraceChain",
    "DecisionTraceError",
    "FactorContribution",
    "SegmentRecord",
    "TraceSegment",
]


class DecisionTraceError(Exception):
    """决策溯源链输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-RPT-UNREGISTERED-DECISION-TRACE。
    """


class TraceSegment(str, Enum):
    """决策链段（词表闭合，声明序即生命周期序）。"""

    SIGNAL = "signal"
    PLAN = "plan"
    ORDER = "order"
    FILL = "fill"


#: 段生命周期序（全链反查排序键）
_SEGMENT_ORDER: Final[dict[TraceSegment, int]] = {
    TraceSegment.SIGNAL: 0,
    TraceSegment.PLAN: 1,
    TraceSegment.ORDER: 2,
    TraceSegment.FILL: 3,
}


@dataclass(frozen=True)
class SegmentRecord:
    """单段落痕记录（frozen）。"""

    decision_id: str
    segment: TraceSegment
    payload: dict
    recorded_at: datetime.datetime


@dataclass(frozen=True)
class FactorContribution:
    """单因子贡献度（frozen）。"""

    factor: str
    contribution: float


@dataclass(frozen=True)
class DecisionTrace:
    """全链反查结果（frozen；segments 按生命周期序确定性排序）。"""

    decision_id: str
    segments: tuple[SegmentRecord, ...]
    factor_summary: tuple[FactorContribution, ...]
    confidence: float | None


class DecisionTraceChain:
    """决策溯源链协议件（四段落痕 + 全链反查 + 因子摘要 + 置信度调整）。"""

    def __init__(
        self,
        *,
        segment_store: Callable[[SegmentRecord], None] | None = None,
        factor_contributions: Callable[[str], Mapping[str, float]] | None = None,
        quantile_confidence: Sequence[tuple[float, float]] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        if quantile_confidence is not None:
            bins = [(float(q), float(c)) for q, c in quantile_confidence]
            if not bins:
                raise DecisionTraceError("quantile_confidence 分桶为空")
            prev = -1.0
            for upper, conf in bins:
                if not (0.0 <= upper <= 1.0):
                    raise DecisionTraceError(f"分位上界越界: {upper!r}（须∈[0,1]）")
                if not (0.0 <= conf <= 1.0):
                    raise DecisionTraceError(f"置信度越界: {conf!r}（须∈[0,1]）")
                if upper <= prev:
                    raise DecisionTraceError("分位上界须严格升序")
                prev = upper
            self._qconf: tuple[tuple[float, float], ...] | None = tuple(bins)
        else:
            self._qconf = None
        self._store = segment_store
        self._factor_fn = factor_contributions
        self._clock = clock or datetime.datetime.now
        self._records: dict[str, list[SegmentRecord]] = {}

    # ── 落痕 ─────────────────────────────────────────────────────────────

    def record_segment(self, record: SegmentRecord) -> None:
        """段记录落痕：内存 append-only 视图 + 注入存储（异常包装 Fail-Closed）。"""
        if not record.decision_id:
            raise DecisionTraceError("decision_id 为空")
        if not isinstance(record.segment, TraceSegment):
            raise DecisionTraceError(f"非法段: {record.segment!r}（词表闭合 signal|plan|order|fill）")
        self._records.setdefault(record.decision_id, []).append(record)
        if self._store is not None:
            try:
                self._store(record)
            except Exception as exc:  # noqa: BLE001 — 存储副作用异常不旁路
                _log.exception("segment_store 落盘异常: %s", record.decision_id)
                raise DecisionTraceError(
                    f"segment_store 落盘失败: {record.decision_id!r}/{record.segment.value}"
                ) from exc

    # ── 全链反查 ──────────────────────────────────────────────────────────

    def segments_of(self, decision_id: str) -> tuple[SegmentRecord, ...]:
        """按 decision_id 聚合全链段（生命周期序+recorded_at 确定性排序）。"""
        recs = self._records.get(decision_id)
        if recs is None:
            raise DecisionTraceError(f"未知 decision_id: {decision_id!r}")
        return tuple(sorted(recs, key=lambda r: (_SEGMENT_ORDER[r.segment], r.recorded_at)))

    def factor_summary(self, decision_id: str) -> tuple[FactorContribution, ...]:
        """因子贡献摘要（注入贡献度；|贡献度|降序+名称升序确定性排序）。"""
        if decision_id not in self._records:
            raise DecisionTraceError(f"未知 decision_id: {decision_id!r}")
        if self._factor_fn is None:
            raise DecisionTraceError("factor_contributions 未注入（因子贡献摘要无来源）")
        contrib = self._factor_fn(decision_id)
        items = [FactorContribution(factor=f, contribution=float(v)) for f, v in contrib.items()]
        items.sort(key=lambda fc: (-abs(fc.contribution), fc.factor))
        return tuple(items)

    # ── 密度感知置信度调整 ────────────────────────────────────────────────

    def adjusted_confidence(self, quantile: float) -> float:
        """分位数→置信度映射（分桶注入；未注入/越界 Fail-Closed）。"""
        if self._qconf is None:
            raise DecisionTraceError("quantile_confidence 未注入（密度感知置信度映射缺失）")
        q = float(quantile)
        if not (0.0 <= q <= 1.0):
            raise DecisionTraceError(f"分位数越界: {quantile!r}（须∈[0,1]）")
        for upper, conf in self._qconf:
            if q <= upper:
                return conf
        raise DecisionTraceError(f"分位数 {q!r} 超出映射末桶上界 {self._qconf[-1][0]!r}")

    def trace(
        self,
        decision_id: str,
        *,
        quantile: float | None = None,
    ) -> DecisionTrace:
        """全链反查：段聚合 + 因子摘要（未注入则空）+ 置信度（给分位数则调整）。"""
        segments = self.segments_of(decision_id)
        factors = self.factor_summary(decision_id) if self._factor_fn is not None else ()
        confidence = self.adjusted_confidence(quantile) if quantile is not None else None
        return DecisionTrace(
            decision_id=decision_id,
            segments=segments,
            factor_summary=factors,
            confidence=confidence,
        )
