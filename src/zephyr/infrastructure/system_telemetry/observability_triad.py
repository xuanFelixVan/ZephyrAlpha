# [BLUEPRINT] MOD-INF-082 | docs/03_modules/_domain_infrastructure_operations/observability_triad/blueprint.md
# [MODULE] zephyr.infrastructure.system_telemetry.observability_triad
# [DOMAIN] D_INFRA_TELEMETRY
# [DEPENDENCIES] 无（纯内存；时钟/审计回调/归档执行回调全注入，不重启 OTel 不触网）
# [CONSUMERS] 运行时装配批（三支柱统一入口装配 / 审计链对接 / 冷归档调度）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 指标名唯一注册; counter 单调不减; render_prometheus 按名排序确定性输出; 日志 append-only 且 prev_hash 哈希链; 归档窗口=注入时钟-hot_days; 归档执行回调未注入 Fail-Closed; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_infrastructure_operations/observability_triad/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ObservabilityTriadError(占位 ZA-INF-UNREGISTERED-OBSERVABILITY-TRIAD)——空名/重复注册/未知指标/负增量/非法hot_days/归档回调缺失时抛
# [TESTS] tests/infrastructure/test_observability_triad.py
# [A_module] module_id=MOD-INF-082 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
ObservabilityTriad — 可观测性三支柱整合门面（MOD-INF-082）。

B11-02678（AUD-DRAFT-001-DIGEST P2 波 P2-W01，CAND-INFRATEL-002，A7-Agent架构）：
Traces/Metrics/Logs 三支柱统一 TriadSink 入口——Metrics Prometheus 文本格式导出
（counter/gauge 注册 + render_prometheus()）、Logs JSON 结构化不可变追加
（append-only + prev_hash 哈希链）、热数据 7 天/冷数据 Parquet 归档指针策略裁决
（注入时钟判定应归档记录，归档执行回调注入）、审计链对接回调注入。不重启 OTel，
纯内存确定性实现。

查重分工（蓝图 §0）：shared/observability/tracing.py=OTel 接线（本件为门面语义
层，不做 SDK 初始化）；archive 族=归档存储实现（本件只裁决窗口并经回调执行）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: observability_triad.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: audit_sink 参数
#   fields: 参数 audit_sink（无注解）
#   code: observability_triad.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: archive_executor 参数
#   fields: 参数 archive_executor（无注解）
#   code: observability_triad.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: hot_days 参数
#   fields: 参数 hot_days（无注解）
#   code: observability_triad.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ObservabilityTriad
#   name_en: ObservabilityTriad
#   intro: 可观测性三支柱门面（统一入口 + 归档裁决 + 审计对接）。
#   desc: 可观测性三支柱门面（统一入口 + 归档裁决 + 审计对接）。；公共方法（定义序）: emit_trace, traces, register_counter, register_gauge, inc_counter,…
#   inputs: clock audit_sink archive_executor hot_days
#   outputs: 返回值
#   （注：A1 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: ObservabilityTriad
#   downstream: 运行时装配批（三支柱统一入口装配 / 审计链对接 / 冷归档调度）
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
import hashlib
import json
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "LogEntry",
    "MetricKind",
    "ObservabilityTriad",
    "ObservabilityTriadError",
    "TraceRecord",
]

#: 日志哈希链创世值（首条 prev_hash）
_GENESIS_HASH: Final[str] = "0" * 64
#: 默认热数据窗口（天）
_DEFAULT_HOT_DAYS: Final[int] = 7


class ObservabilityTriadError(Exception):
    """三支柱门面输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-INF-UNREGISTERED-OBSERVABILITY-TRIAD。
    """


class MetricKind(str, Enum):
    """指标类型（Prometheus 词表闭合）。"""

    COUNTER = "counter"
    GAUGE = "gauge"


@dataclass(frozen=True)
class TraceRecord:
    """Trace 记录（W3C TraceContext 语义载体，frozen）。"""

    trace_id: str
    name: str
    attributes: dict
    ts: datetime.datetime


@dataclass(frozen=True)
class LogEntry:
    """JSON 结构化日志条目（不可变追加 + 哈希链，frozen）。"""

    seq: int
    ts: datetime.datetime
    level: str
    message: str
    fields: dict
    prev_hash: str
    entry_hash: str


def _entry_hash(seq: int, ts: datetime.datetime, level: str, message: str, fields: Mapping, prev_hash: str) -> str:
    """日志条目 sha256（canonical JSON 覆盖全字段 + prev_hash 链）。"""
    payload = {
        "seq": seq,
        "ts": ts.isoformat(),
        "level": level,
        "message": message,
        "fields": dict(fields),
        "prev_hash": prev_hash,
    }
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _fmt_value(value: float) -> str:
    """Prometheus 样本值确定性格式化（整数值去小数点）。"""
    return str(int(value)) if float(value).is_integer() else repr(value)


class ObservabilityTriad:
    """可观测性三支柱门面（统一入口 + 归档裁决 + 审计对接）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        audit_sink: Callable[[str, Mapping], None] | None = None,
        archive_executor: Callable[[tuple[LogEntry, ...]], None] | None = None,
        hot_days: int = _DEFAULT_HOT_DAYS,
    ) -> None:
        if not isinstance(hot_days, int) or hot_days <= 0:
            raise ObservabilityTriadError(f"hot_days 非法: {hot_days!r}")
        self._clock = clock or datetime.datetime.now
        self._audit_sink = audit_sink
        self._archive_executor = archive_executor
        self._hot_days = hot_days
        self._traces: list[TraceRecord] = []
        self._metrics: dict[str, tuple[MetricKind, str, float]] = {}
        self._logs: list[LogEntry] = []

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _audit(self, event: str, payload: Mapping) -> None:
        if self._audit_sink is not None:
            try:
                self._audit_sink(event, payload)
            except Exception:  # noqa: BLE001 — 审计失败不阻断主链路
                _log.exception("audit_sink 回调失败: %s", event)

    # ── Traces ───────────────────────────────────────────────────────────

    def emit_trace(
        self,
        trace_id: str,
        name: str,
        attributes: Mapping | None = None,
    ) -> TraceRecord:
        """记录一条 Trace（跨 Agent 贯通语义载体）。"""
        if not trace_id:
            raise ObservabilityTriadError("trace_id 为空")
        if not name:
            raise ObservabilityTriadError("trace name 为空")
        record = TraceRecord(trace_id=trace_id, name=name, attributes=dict(attributes or {}), ts=self._clock())
        self._traces.append(record)
        self._audit("trace", {"trace_id": trace_id, "name": name})
        return record

    @property
    def traces(self) -> tuple[TraceRecord, ...]:
        """Trace 记录只读视图（发射序）。"""
        return tuple(self._traces)

    # ── Metrics ──────────────────────────────────────────────────────────

    def _register(self, name: str, kind: MetricKind, help_text: str) -> None:
        if not name:
            raise ObservabilityTriadError("指标名为空")
        if name in self._metrics:
            raise ObservabilityTriadError(f"指标重复注册: {name!r}")
        self._metrics[name] = (kind, help_text, 0.0)

    def register_counter(self, name: str, help_text: str = "") -> None:
        """注册 counter（单调递增）。"""
        self._register(name, MetricKind.COUNTER, help_text)

    def register_gauge(self, name: str, help_text: str = "") -> None:
        """注册 gauge（可升可降瞬时值）。"""
        self._register(name, MetricKind.GAUGE, help_text)

    def inc_counter(self, name: str, value: float = 1.0) -> None:
        """counter 增量（负增量破坏单调性 → 拒绝）。"""
        entry = self._metrics.get(name)
        if entry is None:
            raise ObservabilityTriadError(f"未知指标: {name!r}")
        if entry[0] is not MetricKind.COUNTER:
            raise ObservabilityTriadError(f"非 counter 不可增量: {name!r}")
        if value < 0:
            raise ObservabilityTriadError(f"counter 负增量非法: {value!r}")
        kind, help_text, old = entry
        self._metrics[name] = (kind, help_text, old + value)
        self._audit("metric", {"name": name, "kind": kind.value, "value": old + value})

    def set_gauge(self, name: str, value: float) -> None:
        """gauge 设定瞬时值。"""
        entry = self._metrics.get(name)
        if entry is None:
            raise ObservabilityTriadError(f"未知指标: {name!r}")
        if entry[0] is not MetricKind.GAUGE:
            raise ObservabilityTriadError(f"非 gauge 不可设值: {name!r}")
        kind, help_text, _ = entry
        self._metrics[name] = (kind, help_text, float(value))
        self._audit("metric", {"name": name, "kind": kind.value, "value": float(value)})

    def render_prometheus(self) -> str:
        """Prometheus 文本格式导出（按指标名排序，确定性）。"""
        lines: list[str] = []
        for name in sorted(self._metrics):
            kind, help_text, value = self._metrics[name]
            if help_text:
                lines.append(f"# HELP {name} {help_text}")
            lines.append(f"# TYPE {name} {kind.value}")
            lines.append(f"{name} {_fmt_value(value)}")
        return "\n".join(lines) + ("\n" if lines else "")

    # ── Logs ─────────────────────────────────────────────────────────────

    def emit_log(
        self,
        level: str,
        message: str,
        fields: Mapping | None = None,
    ) -> LogEntry:
        """追加一条结构化日志（不可变 append-only + prev_hash 哈希链）。"""
        if not level:
            raise ObservabilityTriadError("日志 level 为空")
        seq = len(self._logs)
        ts = self._clock()
        prev_hash = self._logs[-1].entry_hash if self._logs else _GENESIS_HASH
        digest = _entry_hash(seq, ts, level, message, fields or {}, prev_hash)
        entry = LogEntry(
            seq=seq,
            ts=ts,
            level=level,
            message=message,
            fields=dict(fields or {}),
            prev_hash=prev_hash,
            entry_hash=digest,
        )
        self._logs.append(entry)
        self._audit("log", {"seq": seq, "level": level, "entry_hash": digest})
        return entry

    @property
    def logs(self) -> tuple[LogEntry, ...]:
        """日志只读视图（append-only 序）。"""
        return tuple(self._logs)

    def verify_log_chain(self) -> bool:
        """哈希链完整性校验（逐条重算 + prev_hash 衔接）。"""
        prev = _GENESIS_HASH
        for entry in self._logs:
            if entry.prev_hash != prev:
                return False
            if (
                _entry_hash(entry.seq, entry.ts, entry.level, entry.message, entry.fields, entry.prev_hash)
                != entry.entry_hash
            ):
                return False
            prev = entry.entry_hash
        return True

    # ── 归档裁决（热 7 天 / 冷 Parquet） ──────────────────────────────────

    def archivable_logs(self) -> tuple[LogEntry, ...]:
        """应归档日志裁决：ts 早于 注入时钟 - hot_days 的记录（确定性序）。"""
        cutoff = self._clock() - datetime.timedelta(days=self._hot_days)
        return tuple(e for e in self._logs if e.ts < cutoff)

    def run_archive(self) -> int:
        """执行归档：应归档记录经注入 archive_executor 移交冷存（Parquet 指针语义）。

        归档执行回调未注入 → Fail-Closed（不允许静默丢弃归档义务）。
        """
        if self._archive_executor is None:
            raise ObservabilityTriadError("archive_executor 未注入（归档执行强制回调，禁止旁路）")
        entries = self.archivable_logs()
        if not entries:
            return 0
        try:
            self._archive_executor(entries)
        except Exception as exc:  # noqa: BLE001 — 归档失败 Fail-Closed
            _log.exception("archive_executor 执行失败")
            raise ObservabilityTriadError(f"归档执行失败: {exc}") from exc
        archived = set(e.seq for e in entries)
        self._logs = [e for e in self._logs if e.seq not in archived]
        self._audit("archive", {"count": len(entries), "seqs": sorted(archived)})
        _log.info("日志归档完成: %d 条移交冷存", len(entries))
        return len(entries)
