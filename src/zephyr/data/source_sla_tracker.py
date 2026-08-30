# [BLUEPRINT] MOD-DATA-066 | docs/03_modules/_domain_data/source_sla_tracker/blueprint.md
# [MODULE] zephyr.data.source_sla_tracker
# [DOMAIN] D_DATA
# [DEPENDENCIES] 无（聚合核心纯内存；性能记录序列/目标注入；source_health_check 语义参照不 import）
# [CONSUMERS] 运行时装配批（探测记录接入 / SLA 目标注册 / 日周报计划任务 / 看板读侧）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 源须先注册 SLA 目标方可摄入记录; 失败记录必带失败原因且成功记录禁带原因; 百分位=最近秩法(确定性); 日周报按自然日/ISO周确定性窗口; 达标判定=可用率≥目标且P99≤目标; 看板/报表按键确定性排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_data/source_sla_tracker/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] SourceSlaError(占位 ZA-DATA-UNREGISTERED-SOURCE-SLA)——空source/非法目标/未注册源摄入/非法记录/空窗口聚合/非法周期时抛
# [TESTS] tests/data/test_source_sla_tracker.py
# [A_module] module_id=MOD-DATA-066 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""



SourceSlaTracker — 数据源可用性 SLA 追踪器（MOD-DATA-066）。

B13-04332（AUD-DRAFT-001-DIGEST P2 波 P2-W02，CAND-DAT-020，A3数据架构）：
按源聚合可用率 / 延迟 P50·P99 / 失败原因分布（注入性能记录序列）+ 日周
报生成（周期报表字典）+ SLA 达标率判定（目标注入）+ 看板数据输出。
Prometheus SLI/SLO 思想。

查重分工（蓝图 §0）：source_health_check=在线探活执行（本件=探活记录的
离线聚合与 SLO 裁定，不做探活）；data_source_reliability=源可靠性评分
（本件=SLI 聚合与达标判定，不做综合评分模型）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: source_sla_tracker.py
# 层: 算法
# - id: A1
#   name_zh: ① SourceSlaTracker
#   name_en: SourceSlaTracker
#   intro: 数据源 SLA 追踪器（SLI 聚合 + 日周报 + 达标判定 + 看板）。
#   desc: 数据源 SLA 追踪器（SLI 聚合 + 日周报 + 达标判定 + 看板）。；公共方法（定义序）: register_target, target_of, ingest, aggregate, report_daily…
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: SourceSlaTracker
#   downstream: 运行时装配批（探测记录接入 / SLA 目标注册 / 日周报计划任务 / 看板读侧）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
import math
from dataclasses import dataclass
from typing import Final, Iterable

_log = logging.getLogger(__name__)

__all__: Final = [
    "ProbeRecord",
    "SourceAggregate",
    "SourceSlaError",
    "SourceSlaTracker",
    "SlaTarget",
]


class SourceSlaError(Exception):
    """SLA 追踪输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-DATA-UNREGISTERED-SOURCE-SLA。
    """


@dataclass(frozen=True)
class ProbeRecord:
    """单条源性能记录（注入序列的元素，frozen）。"""

    source: str
    ts: datetime.datetime
    ok: bool
    latency_ms: float
    error_reason: str | None = None


@dataclass(frozen=True)
class SlaTarget:
    """SLA 目标（frozen）。"""

    source: str
    availability: float  # (0, 1]
    p99_latency_ms: float  # > 0


@dataclass(frozen=True)
class SourceAggregate:
    """单源窗口聚合（确定性视图，frozen）。"""

    source: str
    total: int
    ok_count: int
    availability: float
    p50_ms: float
    p99_ms: float
    failure_reasons: tuple[tuple[str, int], ...]  # 按原因名排序


class SourceSlaTracker:
    """数据源 SLA 追踪器（SLI 聚合 + 日周报 + 达标判定 + 看板）。"""

    def __init__(self) -> None:
        self._targets: dict[str, SlaTarget] = {}
        self._records: list[ProbeRecord] = []

    # ── 目标注册 ──────────────────────────────────────────────────────────

    def register_target(
        self,
        source: str,
        *,
        availability: float,
        p99_latency_ms: float,
    ) -> None:
        """注册源 SLA 目标（重复注册拒绝防目标漂移）。"""
        if not source:
            raise SourceSlaError("source 为空")
        if not (0.0 < availability <= 1.0):
            raise SourceSlaError(f"availability 非法: {availability!r}（须 (0, 1]）")
        if p99_latency_ms <= 0:
            raise SourceSlaError(f"p99_latency_ms 非法: {p99_latency_ms!r}（须 > 0）")
        if source in self._targets:
            raise SourceSlaError(f"源 {source!r} SLA 目标已注册")
        self._targets[source] = SlaTarget(
            source=source,
            availability=availability,
            p99_latency_ms=p99_latency_ms,
        )

    def target_of(self, source: str) -> SlaTarget:
        """目标查询（未注册 Fail-Closed）。"""
        target = self._targets.get(source)
        if target is None:
            raise SourceSlaError(f"未注册源: {source!r}（须先 register_target）")
        return target

    # ── 记录摄入 ──────────────────────────────────────────────────────────

    def ingest(self, records: Iterable[ProbeRecord]) -> int:
        """摄入性能记录序列（逐条校验 Fail-Closed），返回接受条数。"""
        accepted = 0
        for record in records:
            if not isinstance(record, ProbeRecord):
                raise SourceSlaError(f"非法记录类型: {type(record).__name__}")
            if record.source not in self._targets:
                raise SourceSlaError(f"未注册源记录: {record.source!r}")
            if not isinstance(record.ts, datetime.datetime):
                raise SourceSlaError(f"记录时间戳非法: {record.ts!r}")
            if record.latency_ms < 0:
                raise SourceSlaError(f"latency_ms 非法: {record.latency_ms!r}（须 ≥ 0）")
            if not record.ok and not record.error_reason:
                raise SourceSlaError("失败记录缺 error_reason")
            if record.ok and record.error_reason:
                raise SourceSlaError("成功记录禁带 error_reason")
            self._records.append(record)
            accepted += 1
        return accepted

    # ── 聚合 ─────────────────────────────────────────────────────────────

    @staticmethod
    def _percentile(sorted_values: list[float], pct: float) -> float:
        """最近秩百分位（确定性）：rank=ceil(pct/100·n)。"""
        rank = max(1, math.ceil(pct / 100.0 * len(sorted_values)))
        return sorted_values[rank - 1]

    def aggregate(
        self,
        source: str,
        start: datetime.datetime,
        end: datetime.datetime,
    ) -> SourceAggregate:
        """按源窗口聚合：可用率 / P50 / P99 / 失败原因分布（空窗口 Fail-Closed）。"""
        self.target_of(source)
        if not (start < end):
            raise SourceSlaError(f"非法窗口: start={start.isoformat()} 须早于 end={end.isoformat()}")
        window = [r for r in self._records if r.source == source and start <= r.ts < end]
        if not window:
            raise SourceSlaError(f"源 {source!r} 窗口内无记录")
        latencies = sorted(r.latency_ms for r in window)
        ok_count = sum(1 for r in window if r.ok)
        reasons: dict[str, int] = {}
        for r in window:
            if not r.ok:
                assert r.error_reason is not None  # 摄入时已强制
                reasons[r.error_reason] = reasons.get(r.error_reason, 0) + 1
        return SourceAggregate(
            source=source,
            total=len(window),
            ok_count=ok_count,
            availability=ok_count / len(window),
            p50_ms=self._percentile(latencies, 50.0),
            p99_ms=self._percentile(latencies, 99.0),
            failure_reasons=tuple(sorted(reasons.items())),
        )

    # ── 达标判定 ──────────────────────────────────────────────────────────

    def _judge(self, agg: SourceAggregate) -> dict[str, bool]:
        target = self._targets[agg.source]
        availability_met = agg.availability >= target.availability
        p99_met = agg.p99_ms <= target.p99_latency_ms
        return {
            "availability": availability_met,
            "p99_latency": p99_met,
            "overall": availability_met and p99_met,
        }

    @staticmethod
    def _report_entry(agg: SourceAggregate, judge: dict[str, bool]) -> dict:
        return {
            "total": agg.total,
            "ok_count": agg.ok_count,
            "availability": agg.availability,
            "p50_ms": agg.p50_ms,
            "p99_ms": agg.p99_ms,
            "failure_reasons": dict(agg.failure_reasons),
            "target_met": judge,
        }

    def _period_report(self, kind: str, key: str, start: datetime.datetime, end: datetime.datetime) -> dict:
        sources: dict[str, dict] = {}
        for source in sorted(self._targets):
            window = [r for r in self._records if r.source == source and start <= r.ts < end]
            if not window:
                continue  # 周期内无记录的源不出报
            agg = self.aggregate(source, start, end)
            sources[source] = self._report_entry(agg, self._judge(agg))
        return {"period": {"kind": kind, "key": key}, "sources": sources}

    # ── 日周报 ────────────────────────────────────────────────────────────

    def report_daily(self, day: datetime.date) -> dict:
        """日报：自然日 [00:00, 24:00) 窗口周期报表字典。"""
        if not isinstance(day, datetime.date):
            raise SourceSlaError(f"day 非法: {day!r}（须 datetime.date）")
        start = datetime.datetime(day.year, day.month, day.day)
        end = start + datetime.timedelta(days=1)
        return self._period_report("daily", day.isoformat(), start, end)

    def report_weekly(self, iso_year: int, iso_week: int) -> dict:
        """周报：ISO 周（周一 00:00 起 7 天）周期报表字典。"""
        try:
            monday = datetime.date.fromisocalendar(iso_year, iso_week, 1)
        except ValueError as exc:
            raise SourceSlaError(f"非法 ISO 周: {iso_year}-W{iso_week}") from exc
        start = datetime.datetime(monday.year, monday.month, monday.day)
        end = start + datetime.timedelta(days=7)
        return self._period_report("weekly", f"{iso_year}-W{iso_week:02d}", start, end)

    # ── 看板 ─────────────────────────────────────────────────────────────

    def dashboard(self) -> dict[str, dict]:
        """看板输出：全量记录快照，按键确定性排序；无记录源=no_data。"""
        board: dict[str, dict] = {}
        for source in sorted(self._targets):
            source_records = [r for r in self._records if r.source == source]
            if not source_records:
                board[source] = {"total": 0, "status": "no_data"}
                continue
            start = min(r.ts for r in source_records)
            end = max(r.ts for r in source_records) + datetime.timedelta(microseconds=1)
            agg = self.aggregate(source, start, end)
            judge = self._judge(agg)
            entry = self._report_entry(agg, judge)
            entry["status"] = "ok" if judge["overall"] else "breach"
            board[source] = entry
        return board

    def sources(self) -> tuple[str, ...]:
        """已注册源清单（确定性排序）。"""
        return tuple(sorted(self._targets))
