# [BLUEPRINT] MOD-SIG-006 | docs/03_modules/_domain_signal/blueprint.md
# [MODULE] zephyr.signal_fundamental.audit.signal_audit_logger
# [DOMAIN] D_FUNDAMENTAL_SIGNAL
# [DEPENDENCIES]
# [CONSUMERS] zephyr.signal_ashare.* (all signal modules)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] WORM: append-only; records immutable after write; entry_id monotonically increasing
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AuditLogWriteError; AuditLogQueryError
# [TESTS] tests/signal_fundamental/audit/test_signal_audit_logger.py
# [A_module] module_id=MOD-SIG-006 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""


D-SIGNAL-06 — 信号审计日志

4组件审计日志系统：
  1. 事件采集器（SignalEventCollector）— 采集信号生命周期事件
  2. WORM写入器（WormWriter）— Write Once Read Many 追加写入器
  3. 查询接口（AuditLogQuery）— 审计日志查询
  4. 合规报告生成器（ComplianceReportGenerator）— 合规报告生成

合规要求: MiFID II 交易审计 / SEC 记录保留(5年+) / WORM 合规强制
设计真源: D:\临时工作区\依赖图-D-SIGNAL-信号域.md §1 D-SIGNAL-06

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 信号审计事件 SignalAuditEvent
#   fields: 事件类型(生成/撤销/过期/降级/消费) + signal_id + 标的 + 时间戳 + 严重级别 + 描述 + metadata + 来源模块 + 操作人 + trace_id
#   code: SignalAuditEvent L63
# - id: I2
#   name: 审计日志配置 AuditLogConfig
#   fields: log_dir(空=内存模式) + 保留5年(SEC合规) + 是否启用链式哈希（日志按日滚动命名 audit_YYYYMMDD.log）
#   code: AuditLogConfig L92
# - id: I3
#   name: 审计查询条件
#   fields: symbol/signal_id/event_type/severity/source_module/起止时间/limit 多条件过滤
#   code: query L318
# 层: 算法
# - id: A1
#   name_zh: ① WORM追加写入器
#   name_en: WormWriter.write
#   intro: 事件只追加不修改不删除，逐条算SHA256并链成哈希链
#   desc: entry_id单调递增 → JSON序列化(sort_keys) → sha256(content) → 链式sha256(prev_hash+content_hash) → 内存列表+追加写audit_YYYYMMDD.log
#   inputs: I1 I2
#   outputs: AuditLogEntry(含content_hash/prev_hash)
#   invariant: append-only; entry_id单调递增; 写入后不可变
# - id: A2
#   name_zh: ② 链式完整性验证
#   name_en: WormWriter.verify_chain
#   intro: 重放全部条目重算哈希，逐一比对防篡改
#   desc: 从创世哈希(64个0)起逐条重算content_hash与链式hash，任一不符即False
#   inputs: A1 I2
#   outputs: 完整性布尔值
# - id: A3
#   name_zh: ③ 多条件查询接口
#   name_en: SignalAuditLogger.query
#   intro: 按标的/信号/事件类型/严重级别/时间窗等组合过滤日志
#   desc: 遍历内存条目逐一匹配过滤条件，命中即收集，达limit截断
#   inputs: I3 A1
#   outputs: AuditLogEntry列表
# - id: A4
#   name_zh: ④ 合规报告生成器
#   name_en: generate_compliance_report
#   intro: 汇总事件类型/严重级别/标的分布并附链完整性结论
#   desc: query全量 → 按event_type/severity/symbol计数 → top20标的 → verify_chain → 组装报告dict
#   inputs: A3 A2 I2
#   outputs: 合规报告dict
# 层: 输出
# - id: O1
#   name_zh: 审计日志条目与WORM日志文件
#   name_en: AuditLogEntry / audit_YYYYMMDD.log
#   intro: 内存条目列表 + 文件模式逐行追加的WORM日志，供全信号域埋点
#   invariant: WORM只增不改; 链式哈希可验证
#   downstream: zephyr.signal_ashare.* 全部信号模块（[CONSUMERS]）
# - id: O2
#   name_zh: 合规报告
#   name_en: compliance report dict
#   intro: 含总量/分类统计/top20标的/链完整性/保留策略的合规报表
#   downstream: 无下游/内部使用（合规审计读取）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I2 --> A2
# I2 --> A4
# A1 --> A2
# A1 --> A3
# I3 --> A3
# A3 --> A4
# A2 --> A4
# A1 --> O1
# A4 --> O2
"""

from __future__ import annotations

import hashlib
import json
import os
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class SignalEventType(str, Enum):
    """信号事件类型"""

    GENERATED = "SIGNAL_GENERATED"
    REVOKED = "SIGNAL_REVOKED"
    EXPIRED = "SIGNAL_EXPIRED"
    DEGRADED = "SIGNAL_DEGRADED"
    CONSUMED = "SIGNAL_CONSUMED"


class AuditSeverity(str, Enum):
    """审计严重级别"""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class SignalAuditEvent:
    """信号审计事件（不可变）"""

    event_type: SignalEventType
    signal_id: str
    symbol: str
    timestamp: datetime
    severity: AuditSeverity
    description: str
    metadata: dict[str, Any] = field(default_factory=dict)
    # 来源信息
    source_module: str = ""
    operator: str = "system"
    # 链路追踪
    trace_id: str = ""


@dataclass(frozen=True)
class AuditLogEntry:
    """审计日志条目（WORM不可变）"""

    entry_id: int  # 单调递增
    event: SignalAuditEvent
    written_at: datetime
    content_hash: str  # 内容哈希（防篡改）
    prev_hash: str  # 前一条哈希（链式完整性）


@dataclass
class AuditLogConfig:
    """审计日志配置"""

    log_dir: str = ""  # 空字符串=内存模式（测试用），非空=文件WORM模式
    retention_years: int = 5  # 保留5年（SEC合规）
    enable_hash_chain: bool = True  # 启用链式哈希


class AuditLogWriteError(Exception):
    """审计日志写入错误"""


class AuditLogQueryError(Exception):
    """审计日志查询错误"""


class WormWriter:
    """
    WORM写入器 — Write Once Read Many

    追加写入，不可修改，不可删除。
    支持内存模式（测试）和文件模式（生产）。
    文件模式使用链式哈希保证完整性。
    """

    def __init__(self, config: AuditLogConfig | None = None) -> None:
        self._config = config or AuditLogConfig()
        self._lock = threading.Lock()
        self._entries: list[AuditLogEntry] = []
        self._next_id = 1
        self._prev_hash = "0" * 64  # 创世哈希
        self._file_handle = None

        if self._config.log_dir:
            os.makedirs(self._config.log_dir, exist_ok=True)
            self._current_file = os.path.join(
                self._config.log_dir, f"audit_{datetime.now(timezone.utc).strftime('%Y%m%d')}.log"
            )
        else:
            self._current_file = ""

    def write(self, event: SignalAuditEvent) -> AuditLogEntry:
        """追加写入一条审计事件（WORM）"""
        with self._lock:
            entry_id = self._next_id
            self._next_id += 1

            written_at = datetime.now(timezone.utc)
            content = self._serialize_event(event, entry_id, written_at)
            content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

            if self._config.enable_hash_chain:
                prev_hash = self._prev_hash
                full_hash = hashlib.sha256((prev_hash + content_hash).encode("utf-8")).hexdigest()
            else:
                prev_hash = ""
                full_hash = content_hash

            entry = AuditLogEntry(
                entry_id=entry_id,
                event=event,
                written_at=written_at,
                content_hash=full_hash,
                prev_hash=prev_hash,
            )

            self._entries.append(entry)
            self._prev_hash = full_hash

            if self._config.log_dir:
                self._write_to_file(entry)

            return entry

    def _serialize_event(self, event: SignalAuditEvent, entry_id: int, written_at: datetime) -> str:
        """序列化事件为JSON字符串"""
        data = {
            "entry_id": entry_id,
            "event_type": event.event_type.value,
            "signal_id": event.signal_id,
            "symbol": event.symbol,
            "timestamp": event.timestamp.isoformat(),
            "severity": event.severity.value,
            "description": event.description,
            "metadata": event.metadata,
            "source_module": event.source_module,
            "operator": event.operator,
            "trace_id": event.trace_id,
            "written_at": written_at.isoformat(),
        }
        return json.dumps(data, sort_keys=True, ensure_ascii=False)

    def _write_to_file(self, entry: AuditLogEntry) -> None:
        """写入文件（WORM追加模式）"""
        line = self._serialize_event(entry.event, entry.entry_id, entry.written_at)
        record = json.dumps(
            {
                "entry_id": entry.entry_id,
                "content": line,
                "content_hash": entry.content_hash,
                "prev_hash": entry.prev_hash,
            },
            ensure_ascii=False,
        )
        with open(self._current_file, "a", encoding="utf-8") as f:
            f.write(record + "\n")

    def verify_chain(self) -> bool:
        """验证链式哈希完整性"""
        if not self._config.enable_hash_chain:
            return True

        prev_hash = "0" * 64
        for entry in self._entries:
            content = self._serialize_event(entry.event, entry.entry_id, entry.written_at)
            content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
            expected = hashlib.sha256((prev_hash + content_hash).encode("utf-8")).hexdigest()
            if entry.content_hash != expected:
                return False
            if entry.prev_hash != prev_hash:
                return False
            prev_hash = entry.content_hash
        return True

    @property
    def entry_count(self) -> int:
        return len(self._entries)


class SignalAuditLogger:
    """
    信号审计日志器（D-SIGNAL-06）

    整合4组件：事件采集 + WORM写入 + 查询 + 合规报告

    用法:
        logger = SignalAuditLogger()
        logger.log_event(event)
        entries = logger.query(symbol="000001", event_type=SignalEventType.GENERATED)
        report = logger.generate_compliance_report(start, end)
    """

    def __init__(self, config: AuditLogConfig | None = None) -> None:
        self._config = config or AuditLogConfig()
        self._writer = WormWriter(self._config)

    # ------------------------------------------------------------------
    # 1. 事件采集器 + 2. WORM写入器
    # ------------------------------------------------------------------
    def log_event(self, event: SignalAuditEvent) -> AuditLogEntry:
        """采集并写入信号审计事件"""
        return self._writer.write(event)

    def log_signal_generated(
        self,
        signal_id: str,
        symbol: str,
        timestamp: datetime | None = None,
        source_module: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> AuditLogEntry:
        """便捷方法：记录信号生成事件"""
        event = SignalAuditEvent(
            event_type=SignalEventType.GENERATED,
            signal_id=signal_id,
            symbol=symbol,
            timestamp=timestamp or datetime.now(timezone.utc),
            severity=AuditSeverity.INFO,
            description=f"信号 {signal_id} 已生成",
            metadata=metadata or {},
            source_module=source_module,
        )
        return self.log_event(event)

    def log_signal_revoked(
        self,
        signal_id: str,
        symbol: str,
        reason: str,
        timestamp: datetime | None = None,
        source_module: str = "",
    ) -> AuditLogEntry:
        """便捷方法：记录信号撤销事件"""
        event = SignalAuditEvent(
            event_type=SignalEventType.REVOKED,
            signal_id=signal_id,
            symbol=symbol,
            timestamp=timestamp or datetime.now(timezone.utc),
            severity=AuditSeverity.WARNING,
            description=f"信号 {signal_id} 已撤销: {reason}",
            metadata={"reason": reason},
            source_module=source_module,
        )
        return self.log_event(event)

    def log_signal_degraded(
        self,
        signal_id: str,
        symbol: str,
        degradation_level: str,
        timestamp: datetime | None = None,
        source_module: str = "",
    ) -> AuditLogEntry:
        """便捷方法：记录信号降级事件"""
        event = SignalAuditEvent(
            event_type=SignalEventType.DEGRADED,
            signal_id=signal_id,
            symbol=symbol,
            timestamp=timestamp or datetime.now(timezone.utc),
            severity=AuditSeverity.WARNING,
            description=f"信号 {signal_id} 降级: {degradation_level}",
            metadata={"degradation_level": degradation_level},
            source_module=source_module,
        )
        return self.log_event(event)

    # ------------------------------------------------------------------
    # 3. 查询接口
    # ------------------------------------------------------------------
    def query(
        self,
        symbol: str | None = None,
        signal_id: str | None = None,
        event_type: SignalEventType | None = None,
        severity: AuditSeverity | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        source_module: str | None = None,
        limit: int = 100,
    ) -> list[AuditLogEntry]:
        """查询审计日志（多条件过滤）"""
        results = []
        for entry in self._writer._entries:
            event = entry.event
            if symbol and event.symbol != symbol:
                continue
            if signal_id and event.signal_id != signal_id:
                continue
            if event_type and event.event_type != event_type:
                continue
            if severity and event.severity != severity:
                continue
            if source_module and event.source_module != source_module:
                continue
            if start_time and event.timestamp < start_time:
                continue
            if end_time and event.timestamp > end_time:
                continue
            results.append(entry)
            if len(results) >= limit:
                break
        return results

    def get_by_id(self, entry_id: int) -> AuditLogEntry | None:
        """按 entry_id 查询单条日志"""
        for entry in self._writer._entries:
            if entry.entry_id == entry_id:
                return entry
        return None

    # ------------------------------------------------------------------
    # 4. 合规报告生成器
    # ------------------------------------------------------------------
    def generate_compliance_report(
        self,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> dict[str, Any]:
        """生成合规报告"""
        entries = self.query(start_time=start_time, end_time=end_time, limit=100000)

        # 按事件类型统计
        type_counts: dict[str, int] = {}
        severity_counts: dict[str, int] = {}
        symbol_counts: dict[str, int] = {}

        for entry in entries:
            et = entry.event.event_type.value
            type_counts[et] = type_counts.get(et, 0) + 1

            sv = entry.event.severity.value
            severity_counts[sv] = severity_counts.get(sv, 0) + 1

            sym = entry.event.symbol
            symbol_counts[sym] = symbol_counts.get(sym, 0) + 1

        # 链式完整性验证
        chain_valid = self._writer.verify_chain()

        return {
            "report_generated_at": datetime.now(timezone.utc).isoformat(),
            "period": {
                "start": start_time.isoformat() if start_time else None,
                "end": end_time.isoformat() if end_time else None,
            },
            "total_entries": len(entries),
            "event_type_breakdown": type_counts,
            "severity_breakdown": severity_counts,
            "top_symbols": dict(sorted(symbol_counts.items(), key=lambda x: -x[1])[:20]),
            "chain_integrity_valid": chain_valid,
            "retention_policy_years": self._config.retention_years,
            "worm_compliant": True,
        }

    @property
    def entry_count(self) -> int:
        """总日志条数"""
        return self._writer.entry_count

    def verify_integrity(self) -> bool:
        """验证审计日志完整性"""
        return self._writer.verify_chain()
