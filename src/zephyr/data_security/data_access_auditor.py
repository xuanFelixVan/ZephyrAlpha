# [BLUEPRINT] MOD-DATSEC-002 | docs/03_modules/_domain_data_security/data_access_auditor/blueprint.md
# [MODULE] zephyr.data_security.data_access_auditor
# [DOMAIN] D_DATA_SEC
# [DEPENDENCIES] 无（审计核心纯内存；clock/audit_sink/alert_sink 全注入）
# [CONSUMERS] 运行时装配批（CH/SQLite/Parquet 访问切面统一采集 / 事件写 gov_audit 路由）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 源类型词表闭合(clickhouse|sqlite|parquet); 动作词表闭合(query|export); event_id 唯一; 基线按主体(常用表/常用时段/量级)确定性画像; 异常三维规则(非常用表/大批量导出/非常时段)顺序固定; 敏感表注册追踪; 每事件写审计回调; 查询按 (occurred_at,event_id) 确定性排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_data_security/data_access_auditor/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] DataAccessAuditError(占位 ZA-DSEC-UNREGISTERED-ACCESS-AUDIT)——空事件字段/重复event_id/负row_count/未知主体基线/非法阈值/空敏感表名时抛
# [TESTS] tests/data_security/test_data_access_auditor.py
# [A_module] module_id=MOD-DATSEC-002 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
DataAccessAuditor — 数据访问审计器（MOD-DATSEC-002）。

B13-04294（AUD-DRAFT-001-DIGEST P2 波 P2-W02，CAND-DATSEC-002，A3数据架构）：
CH/SQLite/Parquet 访问日志**统一采集**（AccessEvent Schema）+ 查询模式**基线
画像**（按主体常用表/常用时段/量级）+ **异常访问检测**（非常用表/大批量导
出/非常时段三维规则）+ 敏感数据访问追踪（敏感表注册表），事件写 gov_audit
回调。UEBA 轻量单机版。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: data_access_auditor.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: audit_sink 参数
#   fields: 参数 audit_sink（无注解）
#   code: data_access_auditor.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: alert_sink 参数
#   fields: 参数 alert_sink（无注解）
#   code: data_access_auditor.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: bulk_multiplier 参数
#   fields: 参数 bulk_multiplier（无注解）
#   code: data_access_auditor.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① DataAccessAuditor
#   name_en: DataAccessAuditor
#   intro: 数据访问审计器（采集 + 基线画像 + 三维异常检测 + 敏感表追踪）。
#   desc: 数据访问审计器（采集 + 基线画像 + 三维异常检测 + 敏感表追踪）。；公共方法（定义序）: register_sensitive_table, is_sensitive, sensitive_tables, rec…
#   inputs: clock audit_sink alert_sink bulk_multiplier min_repeat baseline_min_s…
#   outputs: 返回值
#   （注：A1 之后另有 7 个公共定义未列入（含 7 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（8 定义）
#   name_en: public defs
#   intro: DataAccessAuditor
#   downstream: 运行时装配批（CH/SQLite/Parquet 访问切面统一采集 / 事件写 gov_audit 路由）
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
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "AccessAction",
    "AccessAnomaly",
    "AccessEvent",
    "AnomalyKind",
    "BaselineProfile",
    "DataAccessAuditError",
    "DataAccessAuditor",
    "SourceType",
]


class DataAccessAuditError(Exception):
    """访问审计输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-DSEC-UNREGISTERED-ACCESS-AUDIT。
    """


class SourceType(str, Enum):
    """数据源类型（词表闭合）。"""

    CLICKHOUSE = "clickhouse"
    SQLITE = "sqlite"
    PARQUET = "parquet"


class AccessAction(str, Enum):
    """访问动作（词表闭合）。"""

    QUERY = "query"
    EXPORT = "export"


class AnomalyKind(str, Enum):
    """异常维度（三维规则，输出顺序固定）。"""

    UNUSUAL_TABLE = "unusual_table"
    BULK_EXPORT = "bulk_export"
    OFF_HOURS = "off_hours"


@dataclass(frozen=True)
class AccessEvent:
    """统一访问事件 Schema（CH/SQLite/Parquet 共用，frozen）。"""

    event_id: str
    subject: str
    action: AccessAction
    source: SourceType
    table_name: str
    row_count: int
    occurred_at: datetime.datetime


@dataclass(frozen=True)
class BaselineProfile:
    """主体查询模式基线画像（确定性排序，frozen）。"""

    subject: str
    sample_size: int
    common_tables: tuple[str, ...]
    common_hours: tuple[int, ...]
    avg_rows: float
    max_rows: int


@dataclass(frozen=True)
class AccessAnomaly:
    """异常访问告警载荷（frozen）。"""

    subject: str
    event_id: str
    kinds: tuple[AnomalyKind, ...]
    reason: str
    raised_at: datetime.datetime


#: 异常维度固定输出顺序
_KIND_ORDER: Final = (
    AnomalyKind.UNUSUAL_TABLE,
    AnomalyKind.BULK_EXPORT,
    AnomalyKind.OFF_HOURS,
)


class DataAccessAuditor:
    """数据访问审计器（采集 + 基线画像 + 三维异常检测 + 敏感表追踪）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        audit_sink: Callable[[AccessEvent], None] | None = None,
        alert_sink: Callable[[AccessAnomaly], None] | None = None,
        bulk_multiplier: float = 10.0,
        min_repeat: int = 2,
        baseline_min_samples: int = 3,
        sensitive_tables: Mapping[str, str] | None = None,
    ) -> None:
        if bulk_multiplier <= 0:
            raise DataAccessAuditError(f"非法 bulk_multiplier: {bulk_multiplier}")
        if min_repeat < 1:
            raise DataAccessAuditError(f"非法 min_repeat: {min_repeat}")
        if baseline_min_samples < 1:
            raise DataAccessAuditError(f"非法 baseline_min_samples: {baseline_min_samples}")
        self._clock = clock or datetime.datetime.now
        self._audit_sink = audit_sink
        self._alert_sink = alert_sink
        self._bulk_multiplier = float(bulk_multiplier)
        self._min_repeat = min_repeat
        self._baseline_min_samples = baseline_min_samples
        self._events: dict[str, AccessEvent] = {}
        self._sensitive: dict[str, str] = {}
        for table, level in (sensitive_tables or {}).items():
            self.register_sensitive_table(table, level)

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _validate_event(self, event: AccessEvent) -> None:
        if not isinstance(event, AccessEvent):
            raise DataAccessAuditError(f"非法事件: {event!r}")
        if not event.event_id:
            raise DataAccessAuditError("event_id 为空")
        if event.event_id in self._events:
            raise DataAccessAuditError(f"event_id 重复: {event.event_id!r}")
        if not event.subject:
            raise DataAccessAuditError("subject 为空")
        if not isinstance(event.action, AccessAction):
            raise DataAccessAuditError(f"非法动作: {event.action!r}")
        if not isinstance(event.source, SourceType):
            raise DataAccessAuditError(f"非法源类型: {event.source!r}")
        if not event.table_name:
            raise DataAccessAuditError("table_name 为空")
        if event.row_count < 0:
            raise DataAccessAuditError(f"row_count 为负: {event.row_count}")

    def _subject_events(self, subject: str, exclude_id: str | None = None) -> list[AccessEvent]:
        out = [e for e in self._events.values() if e.subject == subject and e.event_id != exclude_id]
        out.sort(key=lambda e: (e.occurred_at, e.event_id))
        return out

    def _profile_of(self, subject: str, events: list[AccessEvent]) -> BaselineProfile:
        table_count: dict[str, int] = {}
        hour_count: dict[int, int] = {}
        for e in events:
            table_count[e.table_name] = table_count.get(e.table_name, 0) + 1
            hour_count[e.occurred_at.hour] = hour_count.get(e.occurred_at.hour, 0) + 1
        common_tables = tuple(
            t
            for t, _ in sorted(
                ((t, c) for t, c in table_count.items() if c >= self._min_repeat),
                key=lambda kv: (-kv[1], kv[0]),
            )
        )
        common_hours = tuple(
            h
            for h, _ in sorted(
                ((h, c) for h, c in hour_count.items() if c >= self._min_repeat),
                key=lambda kv: (-kv[1], kv[0]),
            )
        )
        total_rows = sum(e.row_count for e in events)
        avg_rows = total_rows / len(events) if events else 0.0
        max_rows = max((e.row_count for e in events), default=0)
        return BaselineProfile(
            subject=subject,
            sample_size=len(events),
            common_tables=common_tables,
            common_hours=common_hours,
            avg_rows=avg_rows,
            max_rows=max_rows,
        )

    def _alert(self, event: AccessEvent, kinds: tuple[AnomalyKind, ...]) -> None:
        reason = (
            f"异常访问: {event.subject} {event.action.value} {event.table_name} "
            f"rows={event.row_count} 命中={[k.value for k in kinds]}"
        )
        anomaly = AccessAnomaly(
            subject=event.subject,
            event_id=event.event_id,
            kinds=kinds,
            reason=reason,
            raised_at=self._clock(),
        )
        _log.warning("访问异常: %s", reason)
        if self._alert_sink is not None:
            try:
                self._alert_sink(anomaly)
            except Exception:  # noqa: BLE001 — 告警不阻断采集
                _log.exception("alert_sink 告警失败: %s", event.event_id)

    # ── 敏感表注册 ────────────────────────────────────────────────────────

    def register_sensitive_table(self, table_name: str, level: str = "high") -> None:
        """登记敏感表（幂等；空名 Fail-Closed）。"""
        if not table_name:
            raise DataAccessAuditError("敏感表名为空")
        if not level:
            raise DataAccessAuditError("敏感级别为空")
        self._sensitive[table_name] = level

    def is_sensitive(self, table_name: str) -> bool:
        """是否敏感表。"""
        return table_name in self._sensitive

    def sensitive_tables(self) -> dict[str, str]:
        """敏感表注册表快照（确定性排序）。"""
        return {t: self._sensitive[t] for t in sorted(self._sensitive)}

    # ── 采集 + 检测 ───────────────────────────────────────────────────────

    def record(self, event: AccessEvent) -> tuple[AnomalyKind, ...]:
        """采集事件：校验 → 写审计回调 → 三维异常检测（命中告警）。"""
        self._validate_event(event)
        kinds = self._detect_against(event, self._subject_events(event.subject, exclude_id=event.event_id))
        self._events[event.event_id] = event
        if self._audit_sink is not None:
            try:
                self._audit_sink(event)
            except Exception:  # noqa: BLE001 — 审计写失败不阻断采集
                _log.exception("audit_sink 审计失败: %s", event.event_id)
        if kinds:
            self._alert(event, kinds)
        return kinds

    def _detect_against(self, event: AccessEvent, history: list[AccessEvent]) -> tuple[AnomalyKind, ...]:
        """三维规则检测（基线样本不足 → 不判异常，防误报）。"""
        if len(history) < self._baseline_min_samples:
            return ()
        profile = self._profile_of(event.subject, history)
        hits: set[AnomalyKind] = set()
        if event.table_name not in profile.common_tables:
            hits.add(AnomalyKind.UNUSUAL_TABLE)
        threshold = self._bulk_multiplier * profile.avg_rows
        if event.action is AccessAction.EXPORT and event.row_count > threshold:
            hits.add(AnomalyKind.BULK_EXPORT)
        if event.occurred_at.hour not in profile.common_hours:
            hits.add(AnomalyKind.OFF_HOURS)
        return tuple(k for k in _KIND_ORDER if k in hits)

    def detect(self, event: AccessEvent) -> tuple[AnomalyKind, ...]:
        """对已采集历史重放检测（不改动存储，event_id 排除自身）。"""
        if not isinstance(event, AccessEvent):
            raise DataAccessAuditError(f"非法事件: {event!r}")
        if not event.subject or not event.table_name:
            raise DataAccessAuditError("事件字段为空")
        return self._detect_against(event, self._subject_events(event.subject, exclude_id=event.event_id))

    # ── 基线画像 / 查询 ───────────────────────────────────────────────────

    def build_baseline(self, subject: str) -> BaselineProfile:
        """主体基线画像（无事件 → Fail-Closed）。"""
        if not subject:
            raise DataAccessAuditError("subject 为空")
        events = self._subject_events(subject)
        if not events:
            raise DataAccessAuditError(f"未知主体: {subject!r}（无访问事件可画像）")
        return self._profile_of(subject, events)

    def events_of(self, subject: str) -> list[AccessEvent]:
        """主体事件查询（按 (occurred_at, event_id) 确定性排序）。"""
        if not subject:
            raise DataAccessAuditError("subject 为空")
        return self._subject_events(subject)

    def sensitive_events(self, table_name: str | None = None, subject: str | None = None) -> list[AccessEvent]:
        """敏感表访问追踪（可选按表/主体过滤，确定性排序）。"""
        out = [
            e
            for e in self._events.values()
            if e.table_name in self._sensitive
            and (table_name is None or e.table_name == table_name)
            and (subject is None or e.subject == subject)
        ]
        out.sort(key=lambda e: (e.occurred_at, e.event_id))
        return out
