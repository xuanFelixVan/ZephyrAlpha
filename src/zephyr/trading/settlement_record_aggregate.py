# [BLUEPRINT] MOD-TRADING-010 | docs/03_modules/_domain_trading/settlement_record_aggregate/blueprint.md
# [MODULE] zephyr.trading.settlement_record_aggregate
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] 交易运营编排层（运行时装配批）; MOD-TRADING-009 TradingOrder 聚合（SETTLED 联动）; 差异工单消费方（装配批接事件总线）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] settlement_id唯一; idempotency_key幂等(同键重复注册返回既有聚合不回退状态); 结算状态机非法转换Fail-Closed; DiscrepancyTicket frozen不可变; 费用类差异仅参考不升级工单; event_sink异常不阻断聚合; occurred_at由调用方注入(不读墙钟)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SettlementRecordAggregateError(ZA-TR-0029); InvalidSettlementInputError; DuplicateSettlementIdError; InvalidSettlementTransitionError
# [TESTS] tests/trading/test_settlement_record_aggregate.py
# [A_module] module_id=MOD-TRADING-010 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: register(settlement_id/idempotency_key/trade_date/account_id)——结算记录注册; idempotency_key 幂等键
# I2: mark_matched/mark_discrepant(drifts)/resolve/confirm——对账结果驱动的状态迁移请求(occurred_at 注入)
# F1: SettlementRecordBook.register()——幂等注册: 同 idempotency_key 返回既有聚合; id 冲突异键 Fail-Closed
# F2: classify_drift()——差异三档分类: PRICE_QTY_MISMATCH / MISSING_RECORD / FEE_REFERENCE(费用仅参考不出票)
# F3: mark_discrepant()——非费用类差异按类别聚合出 DiscrepancyTicket(OPEN) 经 event_sink 发布
# A1: 非法转换/空差异清单→Fail-Closed; sink 异常仅日志不阻断
# O1: SettlementRecord 聚合根(只读快照) + DiscrepancyTicket 工单事件流(OPEN/CLOSED)
# [/ALGO_FLOW]
"""D_TRADING — SettlementRecord 结算记录核心聚合（AGG-TRD-02，D-TRADING §0）。

交易运营域结算记录聚合根（DDD）。与既有件边界：
  - settlement_reconciliation（MOD-TRADING-003）：纯对账引擎（逐笔比对+
    SettlementDrift+ReconciliationResult+告警回调）——无生命周期、无工单；
    本件消费其差异结果建聚合，**不重复**比对逻辑。
  - broker_settlement_adapter（MOD-TRADING-005）：券商结算单适配（数据流上游）。
  - recon_runner（MOD-TRADING-007）：回测 vs 模拟盘三层对账编排（场景互补）。

结算状态机：PENDING→MATCHED / DISCREPANT→RESOLVED→CONFIRMED。差异三档分类
（PRICE_QTY_MISMATCH / MISSING_RECORD / FEE_REFERENCE——费用类对齐 56 号文
C9 仅参考不升级工单）；非费用类差异按类别聚合成 DiscrepancyTicket(OPEN)
经注入式 event_sink 发布，resolve 时同步 CLOSED 事件；sink 缺失/异常不阻断。

设计真源：docs/03_modules/_domain_trading/settlement_record_aggregate/blueprint.md
（B6-08088 / CAND-TRD-010，AUD-DRAFT-001-DIGEST P1 波 W-P1-23）。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field, replace
from enum import Enum, auto
from typing import Callable, Final

from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)


class SettlementRecordAggregateError(ZephyrBaseError):
    """SettlementRecord 聚合基类异常。"""

    error_code = "ZA-TR-0029"


class InvalidSettlementInputError(SettlementRecordAggregateError):
    """聚合输入非法——空 id/幂等键、未知结算记录、空差异清单。"""

    error_code = "ZA-TR-0030"


class DuplicateSettlementIdError(SettlementRecordAggregateError):
    """settlement_id 冲突（幂等键不同）——Fail-Closed 拒绝双建。"""

    error_code = "ZA-TR-0031"


class InvalidSettlementTransitionError(SettlementRecordAggregateError):
    """非法状态迁移——Fail-Closed。"""

    error_code = "ZA-TR-0032"


class SettlementStatus(Enum):
    """结算记录生命周期状态。"""

    PENDING = auto()
    MATCHED = auto()
    DISCREPANT = auto()
    RESOLVED = auto()
    CONFIRMED = auto()


class DiscrepancyCategory(Enum):
    """差异处理分类（对齐 56 号文 C9：费用类仅参考不升级工单）。"""

    PRICE_QTY_MISMATCH = auto()
    MISSING_RECORD = auto()
    FEE_REFERENCE = auto()


#: 差异类型 → 处理分类映射（drift_type 字符串与 MOD-TRADING-003 DriftType 对齐）
_DRIFT_CATEGORY: Final[dict[str, DiscrepancyCategory]] = {
    "PRICE_MISMATCH": DiscrepancyCategory.PRICE_QTY_MISMATCH,
    "QUANTITY_MISMATCH": DiscrepancyCategory.PRICE_QTY_MISMATCH,
    "MISSING_IN_BROKER": DiscrepancyCategory.MISSING_RECORD,
    "MISSING_IN_SYSTEM": DiscrepancyCategory.MISSING_RECORD,
    "COMMISSION_MISMATCH": DiscrepancyCategory.FEE_REFERENCE,
}

#: 结算状态机合法迁移表（CONFIRMED 终态）
_VALID_TRANSITIONS: Final[dict[SettlementStatus, frozenset[SettlementStatus]]] = {
    SettlementStatus.PENDING: frozenset({SettlementStatus.MATCHED, SettlementStatus.DISCREPANT}),
    SettlementStatus.MATCHED: frozenset({SettlementStatus.CONFIRMED}),
    SettlementStatus.DISCREPANT: frozenset({SettlementStatus.RESOLVED}),
    SettlementStatus.RESOLVED: frozenset({SettlementStatus.CONFIRMED}),
    SettlementStatus.CONFIRMED: frozenset(),
}


@dataclass(frozen=True)
class DiscrepancyTicket:
    """差异处理工单（不可变；event_sink 发布 OPEN/CLOSED 事件）。"""

    ticket_id: str
    settlement_id: str
    category: DiscrepancyCategory
    drift_ids: tuple[str, ...]
    status: str  # OPEN / CLOSED
    occurred_at: str
    note: str = ""
    schema_version: str = "1.0"


@dataclass(frozen=True)
class SettlementRecord:
    """SettlementRecord 聚合根只读快照。"""

    settlement_id: str
    idempotency_key: str
    trade_date: str
    account_id: str
    status: SettlementStatus = SettlementStatus.PENDING
    tickets: tuple[DiscrepancyTicket, ...] = field(default_factory=tuple)
    schema_version: str = "1.0"


class SettlementRecordBook:
    """SettlementRecord 聚合注册表（簿）——幂等注册 + 状态机 + 差异工单事件。

    event_sink：注入式工单事件出口（装配批接事件总线）；缺失仅落聚合内
    工单日志，sink 异常不阻断聚合（不静默——记 WARNING 日志）。
    """

    def __init__(self, event_sink: Callable[[DiscrepancyTicket], None] | None = None) -> None:
        self._event_sink = event_sink
        self._records: dict[str, SettlementRecord] = {}
        self._by_idempotency_key: dict[str, str] = {}
        self._ticket_seq = 0

    @staticmethod
    def classify_drift(drift_type: str) -> DiscrepancyCategory:
        """差异三档分类（未知类型保守归 PRICE_QTY_MISMATCH 升级工单）。"""
        return _DRIFT_CATEGORY.get(drift_type, DiscrepancyCategory.PRICE_QTY_MISMATCH)

    def register(
        self,
        *,
        settlement_id: str,
        idempotency_key: str,
        trade_date: str,
        account_id: str,
    ) -> SettlementRecord:
        """幂等注册：同 idempotency_key 返回既有聚合（不回退状态）。"""
        if not settlement_id or not idempotency_key:
            raise InvalidSettlementInputError("settlement_id/idempotency_key 不能为空")
        existing_id = self._by_idempotency_key.get(idempotency_key)
        if existing_id is not None:
            return self._records[existing_id]
        if settlement_id in self._records:
            raise DuplicateSettlementIdError(f"settlement_id 冲突（幂等键不同）: {settlement_id}")
        record = SettlementRecord(
            settlement_id=settlement_id,
            idempotency_key=idempotency_key,
            trade_date=trade_date,
            account_id=account_id,
        )
        self._records[settlement_id] = record
        self._by_idempotency_key[idempotency_key] = settlement_id
        return record

    def mark_matched(self, settlement_id: str, occurred_at: str) -> SettlementRecord:
        """对账一致：PENDING→MATCHED。"""
        return self._transition(settlement_id, SettlementStatus.MATCHED, occurred_at)

    def mark_discrepant(
        self,
        settlement_id: str,
        occurred_at: str,
        *,
        drifts: tuple[tuple[str, str], ...],
    ) -> SettlementRecord:
        """对账差异：PENDING→DISCREPANT + 非费用类差异按类别聚合成工单(OPEN)。"""
        if not drifts:
            raise InvalidSettlementInputError("drifts 不能为空（DISCREPANT 必须附差异清单）")
        record = self._transition(settlement_id, SettlementStatus.DISCREPANT, occurred_at)
        by_category: dict[DiscrepancyCategory, list[str]] = {}
        for drift_id, drift_type in drifts:
            if not drift_id:
                raise InvalidSettlementInputError("drift_id 不能为空")
            category = self.classify_drift(drift_type)
            if category is DiscrepancyCategory.FEE_REFERENCE:
                continue  # 费用类仅参考不升级工单（56 号文 C9）
            by_category.setdefault(category, []).append(drift_id)
        for category, drift_ids in by_category.items():
            self._ticket_seq += 1
            ticket = DiscrepancyTicket(
                ticket_id=f"TKT-{settlement_id}-{self._ticket_seq}",
                settlement_id=settlement_id,
                category=category,
                drift_ids=tuple(drift_ids),
                status="OPEN",
                occurred_at=occurred_at,
            )
            record = replace(record, tickets=record.tickets + (ticket,))
            self._records[settlement_id] = record
            self._publish(ticket)
        return record

    def resolve(self, settlement_id: str, occurred_at: str, note: str = "") -> SettlementRecord:
        """差异处理完成：DISCREPANT→RESOLVED + 全部 OPEN 工单同步 CLOSED。"""
        record = self._transition(settlement_id, SettlementStatus.RESOLVED, occurred_at)
        closed: list[DiscrepancyTicket] = []
        for ticket in record.tickets:
            if ticket.status != "OPEN":
                closed.append(ticket)
                continue
            migrated = replace(ticket, status="CLOSED", occurred_at=occurred_at, note=note)
            closed.append(migrated)
            self._publish(migrated)
        record = replace(record, tickets=tuple(closed))
        self._records[settlement_id] = record
        return record

    def confirm(self, settlement_id: str, occurred_at: str) -> SettlementRecord:
        """结算确认归档：MATCHED/RESOLVED→CONFIRMED（终态）。"""
        return self._transition(settlement_id, SettlementStatus.CONFIRMED, occurred_at)

    def get(self, settlement_id: str) -> SettlementRecord | None:
        """按 settlement_id 取聚合快照（不存在返回 None）。"""
        return self._records.get(settlement_id)

    def _transition(
        self, settlement_id: str, to_status: SettlementStatus, occurred_at: str
    ) -> SettlementRecord:
        record = self._records.get(settlement_id)
        if record is None:
            raise InvalidSettlementInputError(f"未知结算记录: {settlement_id}")
        if not occurred_at:
            raise InvalidSettlementInputError("occurred_at 不能为空（调用方注入）")
        if to_status not in _VALID_TRANSITIONS[record.status]:
            raise InvalidSettlementTransitionError(
                f"非法状态迁移: {record.status.name} -> {to_status.name} (settlement_id={settlement_id})"
            )
        migrated = replace(record, status=to_status)
        self._records[settlement_id] = migrated
        return migrated

    def _publish(self, ticket: DiscrepancyTicket) -> None:
        if self._event_sink is None:
            return
        try:
            self._event_sink(ticket)
        except Exception:  # noqa: BLE001 — sink 异常不阻断聚合（记日志不静默）
            _logger.warning(
                "settlement event_sink 异常（不阻断聚合）: ticket_id=%s", ticket.ticket_id, exc_info=True
            )


__all__ = [
    "DiscrepancyCategory",
    "DiscrepancyTicket",
    "DuplicateSettlementIdError",
    "InvalidSettlementInputError",
    "InvalidSettlementTransitionError",
    "SettlementRecord",
    "SettlementRecordAggregateError",
    "SettlementRecordBook",
    "SettlementStatus",
]

#: 包门面再导出别名（scaffold 注册约定）
SettlementRecordAggregate = SettlementRecordBook
