# [BLUEPRINT] MOD-POS-009 | docs/03_modules/_domain_position/position_audit_logger/blueprint.md
# [MODULE] zephyr.position.services.position_audit_logger
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.position.core.position_sizing_engine; zephyr.position.core.position_state_machine; zephyr.position.core.position_drift_monitor; zephyr.position.core.rebalance_engine; zephyr.shared.foundation.errors
# [CONSUMERS] D-REPORTING(消费PositionAuditReport); D-GOVERNANCE(消费PositionAuditReport)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 全记录不可跳过;哈希链防篡改;frozen record不可变;listener异常不阻断主流程
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AuditChainError
# [TESTS] tests/position/test_position_audit_logger.py
# [A_module] module_id=MOD-POS-009 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Position Audit Logger — 仓位审计记录器 (MOD-POS-009)

D-POSITION 域审计基础设施: 监听仓位变更事件(E-POS-01/02/03/05),
全量记录 + 哈希链防篡改 + 可追溯, 产出仓位审计报告。

职责:
    - 接收 PositionSized / DriftDetected / RebalanceTriggered / StateChanged 事件
    - 每笔变更生成 PositionAuditRecord (frozen, 哈希链节点)
    - 支持按 symbol / event_type / time_range 查询历史
    - 生成 PositionAuditReport (统计摘要 + 链完整性校验)

边界:
    - 不决定仓位(POS-001 承接)
    - 不执行交易(D-EX-CORE 承接)
    - 不触发风控(D-RISK 承接)
    - 本模块是"仓位变更的记录者", 不是"仓位决策的参与者"

SSoT: depgraph MOD-POS-009
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: E-POS-05 状态变更事件
#   fields: StateChangedEvent(from_state/to_state/reason/timestamp)
#   code: on_state_changed() L271，来自MOD-POS-002
# - id: I2
#   name: E-POS-02 漂移检测事件
#   fields: DriftDetectedEvent(组合/标的告警列表)
#   code: on_drift_detected() L292，来自MOD-POS-003
# - id: I3
#   name: E-POS-03 再平衡触发事件
#   fields: RebalanceTriggeredEvent(decision含orders/成本/改善比)
#   code: on_rebalance_triggered() L331，来自MOD-POS-004
# - id: I4
#   name: E-POS-01 仓位计划
#   fields: PositionSizingPlan(positions/total_exposure/degraded等)
#   code: log_position_sized() L363，POS-001 size()返回后直接调用
# - id: I5
#   name: 持久化路径(可选)
#   fields: persist_path JSONL文件路径，None=仅内存
#   code: PositionAuditLogger.__init__ L248
# 层: 算法
# - id: A1
#   name_zh: ① 事件接收与详情提取
#   name_en: on_*/log_position_sized
#   intro: 四个入口把各类仓位事件拍平成审计detail，异常只记日志不阻断主流程
#   desc: StateChanged/Drift/Rebalance走listener接口，PositionSized由POS-001直接调用；degraded计划标记EMERGENCY来源
#   inputs: I1 I2 I3 I4
#   outputs: (event_type, symbol, source, detail, timestamp)
#   invariant: listener异常不阻断主流程
# - id: A2
#   name_zh: ② 哈希链记录生成与追加
#   name_en: _create_record/_append
#   intro: 每笔变更生成frozen不可变记录，哈希串成防篡改链
#   desc: record_hash=SHA256(record_id|timestamp|event_type|symbol|source|detail_json|prev_hash)；prev_hash取链尾last_hash，首条为ZERO_HASH
#   inputs: A1
#   outputs: PositionAuditRecord
#   invariant: 全记录不可跳过；哈希链防篡改；frozen record不可变
# - id: A3
#   name_zh: ③ 条件查询
#   name_en: query
#   intro: 按标的/事件类型/时间范围检索历史记录
#   desc: symbol子串匹配+event_type精确匹配+start/end时间窗过滤，按时间升序返回
#   inputs: A2
#   outputs: 匹配记录列表
# - id: A4
#   name_zh: ④ 报告生成与链校验
#   name_en: generate_report/verify_chain
#   intro: 统计三类维度摘要，并逐条重算哈希验证链没被篡改
#   desc: by_event_type/by_symbol/by_source计数；verify_chain核对prev_hash链接+重算record_hash，断链返回record_id
#   inputs: A2 A3
#   outputs: PositionAuditReport
# - id: A5
#   name_zh: ⑤ JSONL持久化
#   name_en: flush/load
#   intro: 记录写临时文件再原子替换落盘，启动时可加载恢复
#   desc: flush写.jsonl.tmp再replace成.jsonl；load逐行解析重建记录列表；失败仅记日志best-effort
#   inputs: I5 A2
#   outputs: JSONL文件
# 层: 输出
# - id: O1
#   name_zh: 审计记录链
#   name_en: PositionAuditRecord列表
#   intro: 内存中的全量不可变审计记录，可查询
#   downstream: 无下游/内部使用(query查询)
# - id: O2
#   name_zh: 仓位审计报告
#   name_en: PositionAuditReport
#   intro: 统计摘要+链完整性校验结果的定期报告
#   downstream: D-REPORTING D-GOVERNANCE
# - id: O3
#   name_zh: JSONL持久化文件
#   name_en: persist_path.jsonl
#   intro: 每行一条JSON记录的落盘文件，重启可load恢复
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# I5 --> A5
# A1 --> A2
# A2 --> A3
# A2 --> A4
# A3 --> A4
# A2 --> A5
# A2 --> O1
# A3 --> O1
# A4 --> O2
# A5 --> O3
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

from zephyr.shared.foundation.errors import ZephyrBaseError

if TYPE_CHECKING:
    from zephyr.position.core.position_drift_monitor import DriftDetectedEvent
    from zephyr.position.core.position_sizing_engine import PositionSizingPlan
    from zephyr.position.core.position_state_machine import StateChangedEvent
    from zephyr.position.core.rebalance_engine import RebalanceTriggeredEvent

logger = logging.getLogger(__name__)

__all__: Final = [
    "AuditChainError",
    "PositionAuditEventType",
    "AuditSource",
    "PositionAuditLogger",
    "PositionAuditRecord",
    "PositionAuditReport",
]

ZERO_HASH: str = "0" * 64


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class AuditChainError(ZephyrBaseError):
    """审计链错误——哈希链断裂或记录损坏。"""

    error_code = "ZA-POS-0009"


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class PositionAuditEventType(str, Enum):
    """仓位审计事件类型 (对应 E-POS-* 事件)。"""

    POSITION_SIZED = "POSITION_SIZED"  # E-POS-01 仓位决策完成
    DRIFT_DETECTED = "DRIFT_DETECTED"  # E-POS-02 持仓漂移
    REBALANCE_TRIGGERED = "REBALANCE_TRIGGERED"  # E-POS-03 再平衡指令
    STATE_CHANGED = "STATE_CHANGED"  # E-POS-05 持仓状态变更


class AuditSource(str, Enum):
    """仓位变更来源 (审批链)。"""

    AUTO = "AUTO"  # 系统自动决策(POS-001 Kelly/约束裁决)
    MANUAL = "MANUAL"  # 人工调仓指令(轨道3)
    EMERGENCY = "EMERGENCY"  # 应急保命模式(轨道4)
    REBALANCE = "REBALANCE"  # 再平衡触发(POS-004)
    DRIFT = "DRIFT"  # 漂移检测触发(POS-003)


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class PositionAuditRecord:
    """仓位审计记录——单条不可变记录, 哈希链节点。

    Attributes:
        record_id: UUID, 唯一标识
        timestamp: 记录时间(UTC)
        event_type: 事件类型
        symbol: 标的代码(portfolio 级事件用 "*")
        source: 变更来源(审批链)
        detail: 事件详情(事件特定字段)
        prev_hash: 上一条记录的 hash (首条为 ZERO_HASH)
        record_hash: 本条记录的 hash (SHA-256)
    """

    record_id: str
    timestamp: datetime
    event_type: PositionAuditEventType
    symbol: str
    source: AuditSource
    detail: dict[str, Any]
    prev_hash: str
    record_hash: str


@dataclass(frozen=True)
class PositionAuditReport:
    """仓位审计报告——定期或按需生成的摘要。

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
    event_type: PositionAuditEventType,
    symbol: str,
    source: AuditSource,
    detail: dict[str, Any],
    prev_hash: str,
) -> str:
    """计算记录哈希 (SHA-256)。

    hash = SHA-256(record_id | timestamp | event_type | symbol | source | detail_json | prev_hash)
    """
    payload = {
        "record_id": record_id,
        "timestamp": timestamp.isoformat(),
        "event_type": event_type.value,
        "symbol": symbol,
        "source": source.value,
        "detail": detail,
        "prev_hash": prev_hash,
    }
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _create_record(
    event_type: PositionAuditEventType,
    symbol: str,
    source: AuditSource,
    detail: dict[str, Any],
    prev_hash: str,
    timestamp: datetime | None = None,
) -> PositionAuditRecord:
    """创建一条审计记录 (自动计算 record_hash)。"""
    ts = timestamp if timestamp is not None else datetime.now(UTC)
    rid = uuid.uuid4().hex
    rhash = _compute_record_hash(rid, ts, event_type, symbol, source, detail, prev_hash)
    return PositionAuditRecord(
        record_id=rid,
        timestamp=ts,
        event_type=event_type,
        symbol=symbol,
        source=source,
        detail=detail,
        prev_hash=prev_hash,
        record_hash=rhash,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 仓位审计记录器
# ──────────────────────────────────────────────────────────────────────────────


class PositionAuditLogger:
    """仓位审计记录器——监听事件 + 全记录 + 哈希链 + 报告。

    用法:
        # 1. 创建记录器
        audit = PositionAuditLogger()

        # 2. 注册为各模块的 listener
        state_machine.on_state_changed(audit.on_state_changed)
        drift_monitor.on_drift_detected(audit.on_drift_detected)
        rebalance_engine.on_rebalance_triggered(audit.on_rebalance_triggered)

        # 3. POS-001 直接调用 (size() 返回后)
        plan = sizing_engine.size(inp)
        audit.log_position_sized(plan)

        # 4. 查询 / 报告
        records = audit.query(symbol="000001.SZ")
        report = audit.generate_report(start, end)
    """

    def __init__(self, persist_path: Path | str | None = None) -> None:
        """初始化审计记录器。

        Args:
            persist_path: JSONL 持久化文件路径 (None=仅内存)
        """
        self._records: list[PositionAuditRecord] = []
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

    # ── 事件接收: listener 接口 (异常不阻断主流程, C5) ──

    def on_state_changed(self, event: StateChangedEvent) -> None:
        """处理 E-POS-05 StateChanged 事件 (listener 接口)。

        异常不阻断状态机主流程, 仅记录日志 (C5)。
        """
        try:
            detail = {
                "from_state": event.from_state.value,
                "to_state": event.to_state.value,
                "reason": event.reason,
            }
            self._append(
                PositionAuditEventType.STATE_CHANGED,
                event.symbol,
                AuditSource.AUTO,
                detail,
                event.timestamp,
            )
        except Exception as exc:  # noqa: BLE001 — C5: listener 异常不阻断主流程
            logger.error("[POS-009] on_state_changed failed: %s", exc, exc_info=True)

    def on_drift_detected(self, event: DriftDetectedEvent) -> None:
        """处理 E-POS-02 DriftDetected 事件 (listener 接口)。

        异常不阻断漂移监控主流程, 仅记录日志 (C5)。
        """
        try:
            result = event.result
            detail: dict[str, Any] = {"alerts": []}
            if result.portfolio_alert is not None:
                pa = result.portfolio_alert
                detail["portfolio"] = {
                    "actual_weight": pa.actual_weight,
                    "target_weight": pa.target_weight,
                    "drift": pa.drift,
                    "threshold": pa.threshold,
                }
            for sa in result.symbol_alerts:
                detail["alerts"].append(
                    {
                        "symbol": sa.symbol,
                        "actual_weight": sa.actual_weight,
                        "target_weight": sa.target_weight,
                        "drift": sa.drift,
                        "threshold": sa.threshold,
                    }
                )
            symbol = "*"
            if result.symbol_alerts:
                symbol = ",".join(sorted({sa.symbol for sa in result.symbol_alerts if sa.symbol}))
            self._append(
                PositionAuditEventType.DRIFT_DETECTED,
                symbol,
                AuditSource.DRIFT,
                detail,
                event.timestamp,
            )
        except Exception as exc:  # noqa: BLE001 — C5
            logger.error("[POS-009] on_drift_detected failed: %s", exc, exc_info=True)

    def on_rebalance_triggered(self, event: RebalanceTriggeredEvent) -> None:
        """处理 E-POS-03 RebalanceTriggered 事件 (listener 接口)。

        异常不阻断再平衡引擎主流程, 仅记录日志 (C5)。
        """
        try:
            dec = event.decision
            detail = {
                "should_rebalance": dec.should_rebalance,
                "trigger": dec.trigger.value,
                "order_count": len(dec.orders),
                "expected_improvement": dec.expected_improvement,
                "transaction_cost": dec.transaction_cost,
                "improvement_ratio": dec.improvement_ratio,
                "reason": dec.reason,
                "symbols": [o.symbol for o in dec.orders],
            }
            symbol = "*"
            if dec.orders:
                symbol = ",".join(sorted({o.symbol for o in dec.orders}))
            self._append(
                PositionAuditEventType.REBALANCE_TRIGGERED,
                symbol,
                AuditSource.REBALANCE,
                detail,
                event.timestamp,
            )
        except Exception as exc:  # noqa: BLE001 — C5
            logger.error("[POS-009] on_rebalance_triggered failed: %s", exc, exc_info=True)

    # ── 事件接收: 直接调用 (POS-001 不用 listener) ──

    def log_position_sized(self, plan: PositionSizingPlan) -> None:
        """记录 E-POS-01 PositionSized 事件 (直接调用)。

        在 PositionSizingEngine.size() 返回后调用。
        """
        symbols = sorted(plan.positions.keys()) if plan.positions else []
        detail = {
            "plan_id": plan.plan_id,
            "strategy_id": plan.strategy_id,
            "total_exposure": plan.total_exposure,
            "cash_reserve": plan.cash_reserve,
            "capital_curve_discount": plan.capital_curve_discount,
            "calendar_constraint_active": plan.calendar_constraint_active,
            "volatility_adjustment": plan.volatility_adjustment,
            "degraded": plan.degraded,
            "symbols": symbols,
            "idempotency_key": plan.idempotency_key,
        }
        symbol = ",".join(symbols) if symbols else "*"
        source = AuditSource.EMERGENCY if plan.degraded else AuditSource.AUTO
        self._append(
            PositionAuditEventType.POSITION_SIZED,
            symbol,
            source,
            detail,
            plan.created_at,
        )

    # ── 内部: 追加记录 ──

    def _append(
        self,
        event_type: PositionAuditEventType,
        symbol: str,
        source: AuditSource,
        detail: dict[str, Any],
        timestamp: datetime | None = None,
    ) -> PositionAuditRecord:
        """创建并追加一条审计记录到链尾。"""
        record = _create_record(
            event_type=event_type,
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
        symbol: str | None = None,
        event_type: PositionAuditEventType | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[PositionAuditRecord]:
        """按条件查询审计记录。

        Args:
            symbol: 标的代码过滤 (None=不限, 精确匹配或子串匹配)
            event_type: 事件类型过滤 (None=不限)
            start: 起始时间 (None=不限)
            end: 结束时间 (None=不限)

        Returns:
            匹配的审计记录列表 (按时间升序)
        """
        results: list[PositionAuditRecord] = []
        for rec in self._records:
            if symbol is not None and symbol not in rec.symbol:
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
    ) -> PositionAuditReport:
        """生成仓位审计报告。

        Args:
            period_start: 报告周期起始
            period_end: 报告周期结束

        Returns:
            PositionAuditReport 含统计摘要 + 链完整性校验
        """
        records = self.query(start=period_start, end=period_end)

        by_event_type: dict[str, int] = {}
        by_symbol: dict[str, int] = {}
        by_source: dict[str, int] = {}

        for rec in records:
            et = rec.event_type.value
            by_event_type[et] = by_event_type.get(et, 0) + 1
            for sym in rec.symbol.split(","):
                sym = sym.strip()
                if sym:
                    by_symbol[sym] = by_symbol.get(sym, 0) + 1
            src = rec.source.value
            by_source[src] = by_source.get(src, 0) + 1

        chain_valid, chain_break_at = self.verify_chain()

        return PositionAuditReport(
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

        每行一条 JSON 记录, 最后一行为完整链。
        失败时记录日志, 不抛异常 (best-effort)。
        """
        if self._persist_path is None:
            return
        try:
            self._persist_path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self._persist_path.with_suffix(".jsonl.tmp")
            with open(tmp, "w", encoding="utf-8") as fh:
                for rec in self._records:
                    fh.write(
                        json.dumps(
                            {
                                "record_id": rec.record_id,
                                "timestamp": rec.timestamp.isoformat(),
                                "event_type": rec.event_type.value,
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
            tmp.replace(self._persist_path.with_suffix(".jsonl"))
        except Exception as exc:  # noqa: BLE001 — best-effort
            logger.error("[POS-009] flush failed: %s", exc, exc_info=True)

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
            loaded: list[PositionAuditRecord] = []
            with open(jsonl_path, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    data = json.loads(line)
                    loaded.append(
                        PositionAuditRecord(
                            record_id=data["record_id"],
                            timestamp=datetime.fromisoformat(data["timestamp"]),
                            event_type=PositionAuditEventType(data["event_type"]),
                            symbol=data["symbol"],
                            source=AuditSource(data["source"]),
                            detail=data["detail"],
                            prev_hash=data["prev_hash"],
                            record_hash=data["record_hash"],
                        )
                    )
            self._records = loaded
            logger.info("[POS-009] loaded %d records from %s", len(loaded), jsonl_path)
        except Exception as exc:  # noqa: BLE001 — best-effort
            logger.error("[POS-009] load failed: %s", exc, exc_info=True)
