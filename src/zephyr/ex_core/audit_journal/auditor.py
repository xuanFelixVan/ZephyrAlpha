# [BLUEPRINT] MOD-EX-003 | docs/03_modules/_domain_execution_core/audit_journal/blueprint.md
# [MODULE] zephyr.ex_core.audit_journal.auditor
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] D-REPORTING(消费ExecutionAuditReport); D-GOVERNANCE(消费ExecutionAuditReport)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 全记录不可跳过;哈希链防篡改;frozen record不可变;log内部异常不阻断主流程
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AuditChainError
# [TESTS] tests/ex_core/test_execution_auditor.py
# [A_module] module_id=MOD-EX-003 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Execution Audit Logger — 执行审计记录器 (MOD-EX-003 / D-EX-CORE-15)

D_EXECUTION_CORE 域审计基础设施: 记录执行事件(E-EX-01~08)的哈希链审计日志,
全量记录 + 哈希链防篡改 + 可追溯, 产出执行审计报告。

职责:
    - 接收订单生命周期事件 (ORDER_CREATED / SUBMITTED / FILLED / CANCELLED / REJECTED / EXPIRED)
    - 接收成交回报事件 (FILL_RECEIVED)
    - 接收幂等性拦截事件 (IDEMPOTENCY_BLOCKED)
    - 每笔事件生成 ExecutionAuditRecord (frozen, 哈希链节点)
    - 支持按 order_id / symbol / event_type / 时间范围查询历史
    - 生成 ExecutionAuditReport (统计摘要 + 链完整性校验)

边界:
    - 不执行订单(D-EX-CORE 执行层承接)
    - 不做合规判断(阶段2合规规则引擎)
    - 不评分执行质量(阶段2 TCA 依赖)
    - 本模块是"执行事件的记录者", 不是"执行决策的参与者"

模式复用: 对齐 MOD-POS-009 PositionAuditLogger (哈希链审计日志同构模式)
    差异: 事件类型(E-EX vs E-POS) / 关联键(order_id vs symbol) / 来源枚举不同

SSoT: depgraph MOD-EX-003
Version: 0.1.0
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Final

from zephyr.shared.foundation.errors import ZephyrBaseError

logger = logging.getLogger(__name__)

__all__: Final = [
    "AuditChainError",
    "ExecutionAuditEventType",
    "AuditSource",
    "ExecutionAuditLogger",
    "ExecutionAuditRecord",
    "ExecutionAuditReport",
]

ZERO_HASH: str = "0" * 64


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class AuditChainError(ZephyrBaseError):
    """审计链错误——哈希链断裂或记录损坏。"""

    error_code = "ZA-EX-0015"


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class ExecutionAuditEventType(str, Enum):
    """执行审计事件类型 (对应 E-EX-01~08 事件)。"""

    ORDER_CREATED = "ORDER_CREATED"  # E-EX-01 订单创建
    ORDER_SUBMITTED = "ORDER_SUBMITTED"  # E-EX-02 订单提交
    ORDER_FILLED = "ORDER_FILLED"  # E-EX-03 订单完全成交
    FILL_RECEIVED = "FILL_RECEIVED"  # E-EX-04 成交回报接收
    ORDER_CANCELLED = "ORDER_CANCELLED"  # E-EX-05 订单撤销
    ORDER_REJECTED = "ORDER_REJECTED"  # E-EX-06 订单被拒
    ORDER_EXPIRED = "ORDER_EXPIRED"  # E-EX-07 订单过期
    IDEMPOTENCY_BLOCKED = "IDEMPOTENCY_BLOCKED"  # E-EX-08 幂等性拦截


class AuditSource(str, Enum):
    """执行事件来源 (审批链)。"""

    AUTO = "AUTO"  # 系统自动执行
    SIMULATION = "SIMULATION"  # 模拟盘
    LIVE = "LIVE"  # 实盘
    MANUAL = "MANUAL"  # 人工干预


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ExecutionAuditRecord:
    """执行审计记录——单条不可变记录, 哈希链节点。

    Attributes:
        record_id: UUID, 唯一标识
        timestamp: 记录时间(UTC)
        event_type: 事件类型 (E-EX-01~08)
        order_id: 订单ID (执行域主键)
        symbol: 标的代码 (portfolio 级事件用 "*")
        source: 事件来源(审批链)
        detail: 事件详情(事件特定字段, JSON 可序列化)
        prev_hash: 上一条记录的 hash (首条为 ZERO_HASH)
        record_hash: 本条记录的 hash (SHA-256)
    """

    record_id: str
    timestamp: datetime
    event_type: ExecutionAuditEventType
    order_id: str
    symbol: str
    source: AuditSource
    detail: dict[str, Any]
    prev_hash: str
    record_hash: str


@dataclass(frozen=True)
class ExecutionAuditReport:
    """执行审计报告——定期或按需生成的摘要。

    Attributes:
        report_id: UUID
        period_start: 报告周期起始
        period_end: 报告周期结束
        total_records: 总记录数
        by_event_type: 按事件类型统计
        by_symbol: 按标的统计
        by_source: 按来源统计
        chain_valid: 哈希链完整性校验结果
        chain_break_at: 断链位置(None=无断链)
        generated_at: 报告生成时间
    """

    report_id: str
    period_start: datetime
    period_end: datetime
    total_records: int
    by_event_type: dict[str, int]
    by_symbol: dict[str, int]
    by_source: dict[str, int]
    chain_valid: bool
    chain_break_at: str | None
    generated_at: datetime


# ──────────────────────────────────────────────────────────────────────────────
# 哈希链工具
# ──────────────────────────────────────────────────────────────────────────────


def _compute_record_hash(
    record_id: str,
    timestamp: datetime,
    event_type: ExecutionAuditEventType,
    order_id: str,
    symbol: str,
    source: AuditSource,
    detail: dict[str, Any],
    prev_hash: str,
) -> str:
    """计算记录哈希 (SHA-256)。

    hash = SHA-256(record_id | timestamp | event_type | order_id | symbol | source | detail_json | prev_hash)
    """
    payload = {
        "record_id": record_id,
        "timestamp": timestamp.isoformat(),
        "event_type": event_type.value,
        "order_id": order_id,
        "symbol": symbol,
        "source": source.value,
        "detail": detail,
        "prev_hash": prev_hash,
    }
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _create_record(
    event_type: ExecutionAuditEventType,
    order_id: str,
    symbol: str,
    source: AuditSource,
    detail: dict[str, Any],
    prev_hash: str,
    timestamp: datetime | None = None,
) -> ExecutionAuditRecord:
    """创建一条审计记录 (自动计算 record_hash)。"""
    ts = timestamp if timestamp is not None else datetime.now(UTC)
    rid = uuid.uuid4().hex
    rhash = _compute_record_hash(rid, ts, event_type, order_id, symbol, source, detail, prev_hash)
    return ExecutionAuditRecord(
        record_id=rid,
        timestamp=ts,
        event_type=event_type,
        order_id=order_id,
        symbol=symbol,
        source=source,
        detail=detail,
        prev_hash=prev_hash,
        record_hash=rhash,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 执行审计记录器
# ──────────────────────────────────────────────────────────────────────────────


class ExecutionAuditLogger:
    """执行审计记录器 — 全记录 + 哈希链防篡改 + 查询/报告。

    用法:
        # 1. 创建记录器
        audit = ExecutionAuditLogger()

        # 2. 记录执行事件 (便捷方法或通用 log)
        audit.log_order_created("ord-001", "600000.SH", {"qty": 100, "price": 10.5})
        audit.log(ExecutionAuditEventType.ORDER_FILLED, "ord-001", "600000.SH",
                  AuditSource.SIMULATION, {"fill_price": 10.52, "filled_qty": 100})

        # 3. 查询 / 报告 / 校验
        records = audit.query(order_id="ord-001")
        report = audit.generate_report(start, end)
        ok, break_at = audit.verify_chain()
    """

    def __init__(self, persist_path: Path | str | None = None) -> None:
        """初始化执行审计记录器。

        Args:
            persist_path: JSONL 持久化文件路径 (None=仅内存)
        """
        self._records: list[ExecutionAuditRecord] = []
        self._persist_path = Path(persist_path) if persist_path is not None else None

    @property
    def record_count(self) -> int:
        """已记录的审计记录数。"""
        return len(self._records)

    @property
    def last_hash(self) -> str:
        """最后一条记录的 hash (空链返回 ZERO_HASH)。"""
        if not self._records:
            return ZERO_HASH
        return self._records[-1].record_hash

    # ── 通用记录入口 ──

    def log(
        self,
        event_type: ExecutionAuditEventType,
        order_id: str,
        symbol: str,
        source: AuditSource,
        detail: dict[str, Any],
        timestamp: datetime | None = None,
    ) -> ExecutionAuditRecord | None:
        """记录一条执行审计事件 (通用入口)。

        内部异常不阻断执行主流程 (catch + log), 失败时返回 None。
        正常情况返回创建的 ExecutionAuditRecord。

        Args:
            event_type: 事件类型 (E-EX-01~08)
            order_id: 订单ID
            symbol: 标的代码
            source: 事件来源
            detail: 事件详情 (JSON 可序列化)
            timestamp: 事件时间 (None=now)

        Returns:
            创建的审计记录, 或 None (内部异常时)
        """
        try:
            return self._append(event_type, order_id, symbol, source, detail, timestamp)
        except Exception as exc:  # noqa: BLE001 — listener 异常不阻断主流程
            logger.error(
                "[EX-015] log failed: event=%s order=%s symbol=%s: %s",
                event_type.value,
                order_id,
                symbol,
                exc,
                exc_info=True,
            )
            return None

    # ── 便捷方法 (每类事件一个, 默认 source=AUTO) ──

    def log_order_created(
        self,
        order_id: str,
        symbol: str,
        detail: dict[str, Any],
        source: AuditSource = AuditSource.AUTO,
    ) -> ExecutionAuditRecord | None:
        """记录 E-EX-01 ORDER_CREATED 事件。"""
        return self.log(ExecutionAuditEventType.ORDER_CREATED, order_id, symbol, source, detail)

    def log_order_submitted(
        self,
        order_id: str,
        symbol: str,
        detail: dict[str, Any],
        source: AuditSource = AuditSource.AUTO,
    ) -> ExecutionAuditRecord | None:
        """记录 E-EX-02 ORDER_SUBMITTED 事件。"""
        return self.log(ExecutionAuditEventType.ORDER_SUBMITTED, order_id, symbol, source, detail)

    def log_order_filled(
        self,
        order_id: str,
        symbol: str,
        detail: dict[str, Any],
        source: AuditSource = AuditSource.AUTO,
    ) -> ExecutionAuditRecord | None:
        """记录 E-EX-03 ORDER_FILLED 事件。"""
        return self.log(ExecutionAuditEventType.ORDER_FILLED, order_id, symbol, source, detail)

    def log_fill_received(
        self,
        order_id: str,
        symbol: str,
        detail: dict[str, Any],
        source: AuditSource = AuditSource.AUTO,
    ) -> ExecutionAuditRecord | None:
        """记录 E-EX-04 FILL_RECEIVED 事件。"""
        return self.log(ExecutionAuditEventType.FILL_RECEIVED, order_id, symbol, source, detail)

    def log_order_cancelled(
        self,
        order_id: str,
        symbol: str,
        detail: dict[str, Any],
        source: AuditSource = AuditSource.AUTO,
    ) -> ExecutionAuditRecord | None:
        """记录 E-EX-05 ORDER_CANCELLED 事件。"""
        return self.log(ExecutionAuditEventType.ORDER_CANCELLED, order_id, symbol, source, detail)

    def log_order_rejected(
        self,
        order_id: str,
        symbol: str,
        detail: dict[str, Any],
        source: AuditSource = AuditSource.AUTO,
    ) -> ExecutionAuditRecord | None:
        """记录 E-EX-06 ORDER_REJECTED 事件。"""
        return self.log(ExecutionAuditEventType.ORDER_REJECTED, order_id, symbol, source, detail)

    def log_order_expired(
        self,
        order_id: str,
        symbol: str,
        detail: dict[str, Any],
        source: AuditSource = AuditSource.AUTO,
    ) -> ExecutionAuditRecord | None:
        """记录 E-EX-07 ORDER_EXPIRED 事件。"""
        return self.log(ExecutionAuditEventType.ORDER_EXPIRED, order_id, symbol, source, detail)

    def log_idempotency_blocked(
        self,
        order_id: str,
        symbol: str,
        detail: dict[str, Any],
        source: AuditSource = AuditSource.AUTO,
    ) -> ExecutionAuditRecord | None:
        """记录 E-EX-08 IDEMPOTENCY_BLOCKED 事件。"""
        return self.log(
            ExecutionAuditEventType.IDEMPOTENCY_BLOCKED, order_id, symbol, source, detail
        )

    # ── 内部: 追加记录 ──

    def _append(
        self,
        event_type: ExecutionAuditEventType,
        order_id: str,
        symbol: str,
        source: AuditSource,
        detail: dict[str, Any],
        timestamp: datetime | None = None,
    ) -> ExecutionAuditRecord:
        """创建并追加一条审计记录到链尾 (无 catch, 供 log() 调用)。"""
        record = _create_record(
            event_type=event_type,
            order_id=order_id,
            symbol=symbol,
            source=source,
            detail=detail,
            prev_hash=self.last_hash,
            timestamp=timestamp,
        )
        self._records.append(record)
        return record

    # ── 查询 ──

    def query(
        self,
        order_id: str | None = None,
        symbol: str | None = None,
        event_type: ExecutionAuditEventType | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[ExecutionAuditRecord]:
        """按条件查询审计记录。

        Args:
            order_id: 订单ID过滤 (None=不限, 精确匹配)
            symbol: 标的代码过滤 (None=不限, 精确匹配)
            event_type: 事件类型过滤 (None=不限)
            start: 起始时间 (None=不限)
            end: 结束时间 (None=不限)

        Returns:
            匹配的审计记录列表 (按时间升序)
        """
        results: list[ExecutionAuditRecord] = []
        for rec in self._records:
            if order_id is not None and rec.order_id != order_id:
                continue
            if symbol is not None and rec.symbol != symbol:
                continue
            if event_type is not None and rec.event_type != event_type:
                continue
            if start is not None and rec.timestamp < start:
                continue
            if end is not None and rec.timestamp > end:
                continue
            results.append(rec)
        return results

    # ── 报告 ──

    def generate_report(
        self,
        period_start: datetime,
        period_end: datetime,
    ) -> ExecutionAuditReport:
        """生成执行审计报告。

        Args:
            period_start: 报告周期起始
            period_end: 报告周期结束

        Returns:
            ExecutionAuditReport 含统计摘要 + 链完整性校验
        """
        records = self.query(start=period_start, end=period_end)

        by_event_type: dict[str, int] = {}
        by_symbol: dict[str, int] = {}
        by_source: dict[str, int] = {}

        for rec in records:
            et = rec.event_type.value
            by_event_type[et] = by_event_type.get(et, 0) + 1

            sym = rec.symbol.strip()
            if sym:
                by_symbol[sym] = by_symbol.get(sym, 0) + 1

            src = rec.source.value
            by_source[src] = by_source.get(src, 0) + 1

        chain_valid, chain_break_at = self.verify_chain()

        return ExecutionAuditReport(
            report_id=uuid.uuid4().hex,
            period_start=period_start,
            period_end=period_end,
            total_records=len(records),
            by_event_type=by_event_type,
            by_symbol=by_symbol,
            by_source=by_source,
            chain_valid=chain_valid,
            chain_break_at=chain_break_at,
            generated_at=datetime.now(UTC),
        )

    # ── 哈希链校验 ──

    def verify_chain(self) -> tuple[bool, str | None]:
        """校验哈希链完整性。

        Returns:
            (chain_valid, chain_break_at):
            - chain_valid: True 如果所有记录哈希链连续且未被篡改
            - chain_break_at: 断链位置的 record_id (None=无断链)
        """
        prev_hash = ZERO_HASH
        for rec in self._records:
            # 检查 prev_hash 链接
            if rec.prev_hash != prev_hash:
                return False, rec.record_id
            # 重算 record_hash 验证未被篡改
            recomputed = _compute_record_hash(
                rec.record_id,
                rec.timestamp,
                rec.event_type,
                rec.order_id,
                rec.symbol,
                rec.source,
                rec.detail,
                rec.prev_hash,
            )
            if recomputed != rec.record_hash:
                return False, rec.record_id
            prev_hash = rec.record_hash
        return True, None

    # ── 持久化 ──

    def flush(self) -> None:
        """将所有记录写入 JSONL 文件 (可选持久化)。

        每行一条 JSON 记录。失败时记录日志, 不抛异常 (best-effort)。
        """
        if self._persist_path is None:
            return
        try:
            self._persist_path.parent.mkdir(parents=True, exist_ok=True)
            jsonl_path = self._persist_path.with_suffix(".jsonl")
            tmp = jsonl_path.with_suffix(".jsonl.tmp")
            with open(tmp, "w", encoding="utf-8") as fh:
                for rec in self._records:
                    fh.write(
                        json.dumps(
                            {
                                "record_id": rec.record_id,
                                "timestamp": rec.timestamp.isoformat(),
                                "event_type": rec.event_type.value,
                                "order_id": rec.order_id,
                                "symbol": rec.symbol,
                                "source": rec.source.value,
                                "detail": rec.detail,
                                "prev_hash": rec.prev_hash,
                                "record_hash": rec.record_hash,
                            },
                            ensure_ascii=False,
                            default=str,
                        )
                        + "\n"
                    )
            tmp.replace(jsonl_path)
        except Exception as exc:  # noqa: BLE001 — best-effort
            logger.error("[EX-015] flush failed: %s", exc, exc_info=True)

    def load(self) -> None:
        """从 JSONL 文件加载历史记录 (可选持久化)。

        失败时记录日志, 不抛异常 (best-effort)。
        """
        if self._persist_path is None:
            return
        jsonl_path = self._persist_path.with_suffix(".jsonl")
        if not jsonl_path.exists():
            return
        try:
            loaded: list[ExecutionAuditRecord] = []
            with open(jsonl_path, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    data = json.loads(line)
                    loaded.append(
                        ExecutionAuditRecord(
                            record_id=data["record_id"],
                            timestamp=datetime.fromisoformat(data["timestamp"]),
                            event_type=ExecutionAuditEventType(data["event_type"]),
                            order_id=data["order_id"],
                            symbol=data["symbol"],
                            source=AuditSource(data["source"]),
                            detail=data["detail"],
                            prev_hash=data["prev_hash"],
                            record_hash=data["record_hash"],
                        )
                    )
            self._records = loaded
            logger.info("[EX-015] loaded %d records from %s", len(loaded), jsonl_path)
        except Exception as exc:  # noqa: BLE001 — best-effort
            logger.error("[EX-015] load failed: %s", exc, exc_info=True)
