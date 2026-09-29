# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.saga_session_orchestrator
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.order_manager; zephyr.shared.contracts.enums.order_enums; zephyr.shared.contracts.order; zephyr.shared.contracts.fill
# [CONSUMERS] zephyr.ex_core.trading_session(可选注入 attach)；装配层(start_paper_session 等)
# [STARTUP] imported
# [MATURITY] draft
# [INVARIANTS] Saga=TradingSession 提交面的编排层封装，非第二提交通道——唯一写通道仍是 OrderManager(cancel 经 OM 同一入口)；单写者不变——本模块禁写 order.status/禁 apply_fill/禁碰持仓账本(账本写者=session 成交链)；补偿三态(CANCELLED/NOT_NEEDED/FAILED)；超时补偿只事件触发(rebalance 开始/fill/订单事件到达时懒扫)，禁 Timer/sleep-loop；九态映射唯一真源=shared BROKER_STATE_TO_ORDER_STATUS(禁重造映射表)；未知九态 fail-closed；非法流转 fail-closed 不落内部状态机
# [MODIFY-GUARD] docs/_working/fullconnect_campaign/f_exec_risk/08_f53_order_lifecycle_precheck.md（缺口1/2 处方：双编排解冻=Saga 作 session 编排层封装）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 未知九态 ValueError(fail-closed)；sweep/reconcile 单订单异常吞没隔离不阻断主链
# [TESTS] tests/ex_core/test_saga_session_orchestrator.py; tests/ex_core/test_saga_nine_state_bridge.py; tests/ex_core/test_trading_session_saga_wiring.py
# [A_module] module_id=MOD-L06-001-SAGAO | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Saga Session Orchestrator — TradingSession 提交面的 Saga 编排层封装（F53）。

双编排解冻处方落地（F53 预检 §四缺口 1/2，Owner 解冻 2026-09-28）：
OrderExecutionSaga(MOD-EX-057) 与 TradingSession 直连路径长期两套并存（双编排）。
本模块按处方把 Saga 的订单生命周期补偿语义接到 TradingSession 提交面——
**Saga 是 TradingSession 的编排层封装，非第二提交通道**：

    下单(PLACED) → 部分成交(PARTIAL) → 终态(TERMINAL) → 对账(RECONCILED)
         └──────── 超时未终态 → 补偿撤单（三态：CANCELLED/NOT_NEEDED/FAILED）

与同步六步 OrderExecutionSaga 的分工：
  - MOD-EX-057：单笔订单同步阻塞执行（≤5s 契约），持有 position_tracker 写权；
  - 本模块：session 异步提交流的在途生命周期跟踪+补偿+九态对账断言，
    **不写持仓不写订单状态**——账本唯一写者仍是 session 成交链（单写者不变），
    撤单走 OrderManager.cancel_order 同一通道（与会话直连路径单写者汇合）。

九态桥 Saga 面（T 线 G41-2 桥已覆盖九态→7 态映射真源；本侧增量）：
  - 九态断言：内部 7 态 → 九态词表反向表（由 BROKER_STATE_TO_ORDER_STATUS
    导入时自动求逆派生，禁手工维护）——对账报告用券商词表输出；
  - 流转守卫：券商九态事件映射后的内部态流转合法性校验
    （幂等重申/合法流转/非法流转 fail-closed/未知态 fail-closed）；
  - 对账断言：本地台账态 vs 券商九态映射一致性（漂移=critical 需人工对账）。

线程模型：rebalance 持 session 锁；本模块回调来自 broker/OM 线程——
内部 _tracked 全程持 threading.Lock；超时补偿懒扫（事件触发）无任何定时器。

SSoT: depgraph MOD-L06-001-SAGAO
设计真源: docs/_working/fullconnect_campaign/f_exec_risk/08_f53_order_lifecycle_precheck.md
Version: 0.1.0

# [ALGO_FLOW] external: docs/03_modules/_domain_execution_core/algo_flow/order_manager.yaml
"""

from __future__ import annotations

import logging
import threading
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import TYPE_CHECKING, Final

from zephyr.ex_core.order_manager import OrderManager
from zephyr.shared.contracts.enums.order_enums import (
    BROKER_STATE_TO_ORDER_STATUS,
    BrokerOrderState,
    OrderSide,
    OrderStatus,
    map_broker_state_to_order_status,
)
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.order import Order

if TYPE_CHECKING:
    from zephyr.ex_core.audit_journal.auditor import (
        AuditSource,
        ExecutionAuditEventType,
        ExecutionAuditLogger,
    )

_logger = logging.getLogger(__name__)

__all__: Final = [
    "SagaPhase",
    "CompensationOutcome",
    "CompensationRecord",
    "GuardVerdict",
    "NineStateVerdict",
    "ReconciliationVerdict",
    "SagaNineStateBridge",
    "SagaOrderLifecycle",
    "SagaSessionOrchestrator",
]

#: 默认在途订单生命周期超时（秒）。异步流语义：与 MOD-EX-057 的 ≤5s 同步契约
#: 无关——本超时覆盖"委托在途未终态"窗口，缺省 30s（QMT 常规回执上限量级）。
DEFAULT_ORDER_TIMEOUT_SECONDS: Final = 30.0

#: 内部 7 态全集（终态判定用）。
_TERMINAL_STATUSES: Final[frozenset[OrderStatus]] = frozenset(
    {OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED, OrderStatus.EXPIRED}
)

#: 在途状态（与 OrderManager.cancel_order 可撤面一致）。
_ACTIVE_STATUSES: Final[frozenset[OrderStatus]] = frozenset(
    {OrderStatus.PENDING, OrderStatus.SUBMITTED, OrderStatus.PARTIAL}
)


# ──────────────────────────────────────────────────────────────────────────────
# 状态与判定模型
# ──────────────────────────────────────────────────────────────────────────────


class SagaPhase(str, Enum):
    """在途订单 Saga 生命周期相位：下单→部分成交→终态→对账。"""

    def __str__(self) -> str:
        return self.value

    PLACED = "PLACED"  # 下单已接（session 提交面 submit 成功，跟踪开始）
    PARTIAL = "PARTIAL"  # 部分成交在途
    TERMINAL = "TERMINAL"  # 终态已到（FILLED/CANCELLED/REJECTED/EXPIRED）
    RECONCILED = "RECONCILED"  # 九态对账断言完成（matched）


class CompensationOutcome(str, Enum):
    """补偿三态（与 MOD-EX-057 _CancelOutcome 同型语义，异步流公开化）。"""

    def __str__(self) -> str:
        return self.value

    CANCELLED = "CANCELLED"  # 超时撤单成功
    NOT_NEEDED = "NOT_NEEDED"  # 已终态，无需补偿
    FAILED = "FAILED"  # 撤单失败且终态不可确认——升级人工对账


class GuardVerdict(str, Enum):
    """九态流转守卫判定。"""

    def __str__(self) -> str:
        return self.value

    IDEMPOTENT = "IDEMPOTENT"  # 同态重申（映射结果=当前内部态）
    ALLOWED = "ALLOWED"  # 合法流转（VALID_TRANSITIONS 白名单内）
    BLOCKED = "BLOCKED"  # 非法流转——fail-closed，不落内部状态机
    UNKNOWN_STATE = "UNKNOWN_STATE"  # 九态词表外——fail-closed


@dataclass(frozen=True)
class NineStateVerdict:
    """单次流转守卫判定结果（不可变）。"""

    order_id: str
    broker_state: str | None  # 原始九态（词表外时仍回带原文）
    mapped_status: OrderStatus | None  # 映射后内部态（未知态=None）
    current_status: OrderStatus
    verdict: GuardVerdict
    reason: str


@dataclass(frozen=True)
class ReconciliationVerdict:
    """单次九态对账断言结果（不可变）。"""

    order_id: str
    local_status: OrderStatus
    broker_state: str
    mapped_status: OrderStatus
    matched: bool
    detail: str


@dataclass(frozen=True)
class CompensationRecord:
    """单次补偿动作记录（不可变）。"""

    order_id: str
    outcome: CompensationOutcome
    detail: str
    at: datetime


# ──────────────────────────────────────────────────────────────────────────────
# Saga 面九态桥
# ──────────────────────────────────────────────────────────────────────────────

#: 内部 7 态 → 九态词表反向表——由 BROKER_STATE_TO_ORDER_STATUS 导入时自动求逆
#: 派生（静态清单禁手工维护铁律：单一真源=shared 封闭表，本表零手工条目）。
#: SUBMITTED 对应九态三词（ACCEPTED/SUSPENDED/PENDING_CANCEL——G41-2 收口策略：
#: 柜台侧仍存活的委托均归 SUBMITTED 工作态），对账输出按词表全集断言。
ORDER_STATUS_TO_BROKER_STATES: Final[dict[OrderStatus, frozenset[BrokerOrderState]]] = {}
for _bs in BrokerOrderState:
    _target = BROKER_STATE_TO_ORDER_STATUS[_bs]
    ORDER_STATUS_TO_BROKER_STATES[_target] = ORDER_STATUS_TO_BROKER_STATES.get(_target, frozenset()) | {_bs}
del _bs, _target

# 求逆完备性自证：内部 7 态每态在九态词表必须至少有一个出口（封闭表漂移即炸）
for _st in OrderStatus:
    if not ORDER_STATUS_TO_BROKER_STATES.get(_st):
        raise RuntimeError(f"九态反向表缺出口: {_st}（BROKER_STATE_TO_ORDER_STATUS 封闭表漂移）")
del _st


class SagaNineStateBridge:
    """九态桥 Saga 面：断言+流转守卫+对账（映射真源=T 线 shared 封闭表）。"""

    def map_broker_state(self, broker_state: BrokerOrderState | str) -> OrderStatus:
        """券商九态 → 内部 7 态（真源委派 shared.map_broker_state_to_order_status）。

        Raises:
            ValueError: 九态词表外（fail-closed，禁隐式吞掉）。
        """
        return map_broker_state_to_order_status(broker_state)

    def nine_states_for(self, status: OrderStatus) -> frozenset[BrokerOrderState]:
        """内部态 → 九态词表出口（对账报告词表）。"""
        return ORDER_STATUS_TO_BROKER_STATES[status]

    def assert_transition(
        self,
        order_id: str,
        current_status: OrderStatus,
        broker_state: BrokerOrderState | str,
    ) -> NineStateVerdict:
        """流转守卫：券商九态事件映射后的内部态流转合法性判定（不落状态机）。

        判定序：未知态 fail-closed → 同态重申幂等 → 白名单合法 → 其余 fail-closed。
        """
        raw = broker_state.value if isinstance(broker_state, BrokerOrderState) else str(broker_state)
        try:
            mapped = map_broker_state_to_order_status(broker_state)
        except ValueError as exc:
            _logger.error("九态流转守卫 fail-closed（词表外）: order=%s state=%r", order_id, broker_state)
            return NineStateVerdict(
                order_id=order_id,
                broker_state=raw,
                mapped_status=None,
                current_status=current_status,
                verdict=GuardVerdict.UNKNOWN_STATE,
                reason=str(exc),
            )
        if mapped is current_status:
            return NineStateVerdict(
                order_id=order_id,
                broker_state=raw,
                mapped_status=mapped,
                current_status=current_status,
                verdict=GuardVerdict.IDEMPOTENT,
                reason=f"同态重申: {current_status.value} ← {raw}",
            )
        if mapped in OrderManager.VALID_TRANSITIONS.get(current_status, set()):
            return NineStateVerdict(
                order_id=order_id,
                broker_state=raw,
                mapped_status=mapped,
                current_status=current_status,
                verdict=GuardVerdict.ALLOWED,
                reason=f"合法流转: {current_status.value} -> {mapped.value} ({raw})",
            )
        _logger.error(
            "九态流转守卫 fail-closed（非法流转）: order=%s %s -> %s (九态=%s)",
            order_id,
            current_status.value,
            mapped.value,
            raw,
        )
        return NineStateVerdict(
            order_id=order_id,
            broker_state=raw,
            mapped_status=mapped,
            current_status=current_status,
            verdict=GuardVerdict.BLOCKED,
            reason=f"非法流转: {current_status.value} -> {mapped.value} (九态={raw})",
        )

    def reconcile(
        self,
        order_id: str,
        local_status: OrderStatus,
        broker_state: BrokerOrderState | str,
    ) -> ReconciliationVerdict:
        """九态对账断言：本地台账态 vs 券商九态映射一致性。

        一致判据：map(券商九态) == 本地态。SUBMITTED 与 ACCEPTED/SUSPENDED/
        PENDING_CANCEL 三词互认由封闭表天然保证（无特判）。漂移≠改账——
        返回 matched=False 由调用方升级（本地账本写者唯一，对账面只断言）。
        """
        mapped = map_broker_state_to_order_status(broker_state)  # 词表外原样抛 ValueError
        raw = broker_state.value if isinstance(broker_state, BrokerOrderState) else str(broker_state)
        matched = mapped is local_status
        detail = (
            f"对账一致: local={local_status.value} broker={raw}→{mapped.value}"
            if matched
            else f"对账漂移: local={local_status.value} broker={raw}→{mapped.value}（需人工对账）"
        )
        if not matched:
            _logger.critical("九态对账漂移: order=%s %s", order_id, detail)
        return ReconciliationVerdict(
            order_id=order_id,
            local_status=local_status,
            broker_state=raw,
            mapped_status=mapped,
            matched=matched,
            detail=detail,
        )


# ──────────────────────────────────────────────────────────────────────────────
# 在途订单生命周期记录
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class SagaOrderLifecycle:
    """单笔在途订单的 Saga 跟踪记录（可变，仅编排器内部维护）。"""

    saga_id: str
    order_id: str
    symbol: str
    side: OrderSide
    phase: SagaPhase = SagaPhase.PLACED
    placed_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    deadline: datetime | None = None  # 超时补偿判定线（事件触发懒扫用）
    nine_assertions: list[ReconciliationVerdict] = field(default_factory=list)
    guard_verdicts: list[NineStateVerdict] = field(default_factory=list)
    compensations: list[CompensationRecord] = field(default_factory=list)
    terminal_status: OrderStatus | None = None

    def to_report(self) -> dict[str, object]:
        """生命周期报告（对账面输出，九态词表）。"""
        bridge = SagaNineStateBridge()
        return {
            "saga_id": self.saga_id,
            "order_id": self.order_id,
            "symbol": self.symbol,
            "side": self.side.value,
            "phase": self.phase.value,
            "terminal_status": self.terminal_status.value if self.terminal_status else None,
            "nine_vocabulary": sorted(
                s.value for s in bridge.nine_states_for(self.terminal_status or OrderStatus.PENDING)
            ),
            "compensations": [c.outcome.value for c in self.compensations],
            "assertion_count": len(self.nine_assertions),
        }


# ──────────────────────────────────────────────────────────────────────────────
# Saga 编排层封装（TradingSession 提交面）
# ──────────────────────────────────────────────────────────────────────────────


class SagaSessionOrchestrator:
    """TradingSession 提交面的 Saga 编排层封装（非第二提交通道）。

    用法（装配层）::

        orch = SagaSessionOrchestrator(order_manager)
        session = TradingSession(..., saga_orchestrator=orch)

    接线点（TradingSession 侧，注入即生效、None=既有行为零变化）：
      - submit 成功后 ``track_order``（下单相位登记）；
      - 每次 rebalance 开始 ``sweep()``（事件触发的超时补偿懒扫）；
      - fill/订单事件经 OrderManager 回调自动到达（构造时挂接）。

    单写者契约：本类对订单账本只读（状态观察经 Order 引用与 OM 回调），
    唯一写动作=补偿撤单（OrderManager.cancel_order 同一通道）；持仓/成交
    入账完全归 session 成交链，本类禁 apply_fill/禁改 order.status。
    """

    def __init__(
        self,
        order_manager: OrderManager,
        *,
        order_timeout_seconds: float = DEFAULT_ORDER_TIMEOUT_SECONDS,
        bridge: SagaNineStateBridge | None = None,
        audit_logger: ExecutionAuditLogger | None = None,
        on_drift: Callable[[ReconciliationVerdict], None] | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        """初始化编排层封装。

        Args:
            order_manager: 订单管理器（唯一写通道，与 session 提交面同实例）。
            order_timeout_seconds: 在途订单超时补偿线（秒，>0）。
            bridge: 九态桥（None=默认 SagaNineStateBridge）。
            audit_logger: 执行审计记录器（None=仅日志）。
            on_drift: 对账漂移升级回调（None=仅 critical 日志；装配层可接
                对账冻结/告警面）。
            clock: 时间源（None=UTC now；测试注入确定性时钟）。
        """
        if order_timeout_seconds <= 0:
            raise ValueError(f"order_timeout_seconds 必须为正数，got {order_timeout_seconds}")
        self._order_manager = order_manager
        self._timeout_seconds = order_timeout_seconds
        self._bridge = bridge or SagaNineStateBridge()
        self._audit = audit_logger
        self._on_drift = on_drift
        self._clock = clock or (lambda: datetime.now(UTC))
        self._lock = threading.Lock()
        self._tracked: dict[str, SagaOrderLifecycle] = {}
        # 事件挂接：fill（部分成交相位推进）+ 订单事件（终态相位推进）。
        # 单挂接点=本构造器；TradingSession 不再转发（防双观察）。
        self._order_manager.register_fill_callback(self.on_fill)
        self._order_manager.register_order_event_callback(self.on_order_event)
        _logger.info(
            "SagaSessionOrchestrator attached: timeout=%ss（Saga=编排层封装，非第二提交通道）",
            self._timeout_seconds,
        )

    # ── 只读面 ──

    @property
    def tracked_count(self) -> int:
        """在册跟踪订单数。"""
        with self._lock:
            return len(self._tracked)

    def get_lifecycle(self, order_id: str) -> SagaOrderLifecycle | None:
        """读取订单生命周期记录（只读）。"""
        with self._lock:
            return self._tracked.get(order_id)

    def lifecycle_report(self) -> list[dict[str, object]]:
        """全部生命周期报告（对账面输出）。"""
        with self._lock:
            lives = list(self._tracked.values())
        return [life.to_report() for life in lives]

    # ── 接线点 1：下单登记（TradingSession 提交面 submit 成功后调用）──

    def track_order(self, order: Order, side: OrderSide | None = None) -> SagaOrderLifecycle:
        """登记在途订单跟踪（下单相位；重复登记幂等返回既有记录）。"""
        if side is None:
            side = order.side if isinstance(order.side, OrderSide) else OrderSide.BUY
        with self._lock:
            existing = self._tracked.get(order.order_id)
            if existing is not None:
                return existing  # 幂等：同单不重复起 Saga
            life = SagaOrderLifecycle(
                saga_id=uuid.uuid4().hex,
                order_id=order.order_id,
                symbol=order.symbol,
                side=side,
                placed_at=self._clock(),
                deadline=self._clock() + timedelta(seconds=self._timeout_seconds),
            )
            self._tracked[order.order_id] = life
        # 已终态订单直接落终态相位（迟到登记防挂账）
        if order.status in _TERMINAL_STATUSES:
            self._mark_terminal(order)
        _logger.info(
            "[Saga %s] TRACK order=%s symbol=%s side=%s phase=PLACED",
            life.saga_id[:8],
            order.order_id,
            order.symbol,
            side.value,
        )
        return life

    # ── 事件面：OrderManager 回调（构造时挂接）──

    def on_fill(self, fill: Fill) -> None:
        """fill 回调——部分成交/终态相位推进 + 事件触发超时懒扫。

        只观察不写账（入账写者=session 成交链）。全成 fill 不发订单事件
        （OM 订单事件面仅 submit/cancel/expire 发射），故终态探测在 fill
        事件内完成——fill 本身就是事件。
        """
        try:
            with self._lock:
                life = self._tracked.get(fill.order_id)
                if life is not None and life.phase is SagaPhase.PLACED:
                    life.phase = SagaPhase.PARTIAL
                    _logger.info(
                        "[Saga %s] PARTIAL order=%s qty=%s",
                        life.saga_id[:8],
                        fill.order_id,
                        fill.filled_quantity,
                    )
        except Exception:  # noqa: BLE001 — 相位推进异常不阻断 fill 主链
            _logger.exception("saga on_fill 相位推进异常: order=%s", fill.order_id)
        # 全成探测：fill 使订单达终态（FILLED）时推进终态相位
        try:
            order = self._order_manager.get_order(fill.order_id)
            if order is not None and order.status in _TERMINAL_STATUSES:
                self._mark_terminal(order)
        except Exception:  # noqa: BLE001 — 终态探测异常不阻断 fill 主链
            _logger.exception("saga on_fill 终态探测异常: order=%s", fill.order_id)
        self.sweep()

    def on_order_event(self, order: Order) -> None:
        """订单事件回调——终态相位推进（含九态断言）+ 懒扫。"""
        try:
            if order.status in _TERMINAL_STATUSES:
                with self._lock:
                    life = self._tracked.get(order.order_id)
                if life is not None:
                    self._mark_terminal(order)
        except Exception:  # noqa: BLE001 — 相位推进异常不阻断订单主链
            _logger.exception("saga on_order_event 相位推进异常: order=%s", order.order_id)
        self.sweep()

    def _mark_terminal(self, order: Order) -> None:
        """终态相位推进 + 九态词表断言（本地台账 → 九态词表出口）。"""
        with self._lock:
            life = self._tracked.get(order.order_id)
            if life is None or life.phase is SagaPhase.TERMINAL:
                return
            life.phase = SagaPhase.TERMINAL
            life.terminal_status = order.status
        # 九态断言：终态的九态词表出口应为单词（FILLED/CANCELLED/REJECTED/
        # EXPIRED 在反向表均为单词出口），多词出口仅 SUBMITTED 工作态所有。
        exits = self._bridge.nine_states_for(order.status)
        _logger.info(
            "[Saga %s] TERMINAL order=%s status=%s nine=%s",
            life.saga_id[:8],
            order.order_id,
            order.status.value,
            sorted(s.value for s in exits),
        )

    # ── 接线点 2：事件触发超时补偿懒扫（禁 Timer/sleep-loop）──

    def sweep(self, now: datetime | None = None) -> list[CompensationRecord]:
        """扫描在途超时订单并执行补偿撤单（rebalance 开始/fill/订单事件到达时懒扫）。

        Returns:
            本次触发的补偿记录列表（无到期=空）。
        """
        current = now or self._clock()
        with self._lock:
            due = [
                life
                for life in self._tracked.values()
                if life.phase in (SagaPhase.PLACED, SagaPhase.PARTIAL)
                and life.deadline is not None
                and current >= life.deadline
            ]
        records: list[CompensationRecord] = []
        for life in due:
            record = self._compensate_timeout(life)
            if record is not None:
                records.append(record)
        return records

    def _compensate_timeout(self, life: SagaOrderLifecycle) -> CompensationRecord | None:
        """超时补偿：撤单（唯一写动作，OM 同一通道）→ 三态分流。"""
        order = self._order_manager.get_order(life.order_id)
        if order is None:
            record = CompensationRecord(
                order_id=life.order_id,
                outcome=CompensationOutcome.NOT_NEEDED,
                detail="订单不在册（无状态可补偿）",
                at=self._clock(),
            )
            self._record_compensation(life, record)
            return record
        if order.status not in _ACTIVE_STATUSES:
            record = CompensationRecord(
                order_id=life.order_id,
                outcome=CompensationOutcome.NOT_NEEDED,
                detail=f"已终态 {order.status.value}，无需补偿",
                at=self._clock(),
            )
            self._record_compensation(life, record)
            self._mark_terminal(order)
            return record
        cancelled = False
        try:
            cancelled = bool(self._order_manager.cancel_order(life.order_id))
        except Exception as exc:  # noqa: BLE001 — 撤单异常按 FAILED 分流（终态分流兜底）
            _logger.error("[Saga %s] 补偿撤单异常: order=%s error=%s", life.saga_id[:8], life.order_id, exc)
        if cancelled:
            record = CompensationRecord(
                order_id=life.order_id,
                outcome=CompensationOutcome.CANCELLED,
                detail="超时撤单成功（OM 同一通道）",
                at=self._clock(),
            )
            self._record_compensation(life, record)
            self._audit_log_order_cancelled(order, record)
            return record
        # 撤单失败——可能已成交：强制查终态分流（#ARCH-100 同型治本：
        # 超时+撤单失败吞成交=持仓账与券商漂移）。入账写者=session 成交链，
        # 本侧只按 OM 台账现况分流并升级，不补写账。
        refreshed = self._order_manager.get_order(life.order_id)
        if refreshed is not None and refreshed.status in _TERMINAL_STATUSES:
            record = CompensationRecord(
                order_id=life.order_id,
                outcome=CompensationOutcome.NOT_NEEDED,
                detail=f"撤单失败但已终态 {refreshed.status.value}（成交部分由 session 成交链入账），转对账",
                at=self._clock(),
            )
            self._record_compensation(life, record)
            self._mark_terminal(refreshed)
            return record
        record = CompensationRecord(
            order_id=life.order_id,
            outcome=CompensationOutcome.FAILED,
            detail="撤单失败且终态不可确认——本地台账可能与券商不一致，需人工对账",
            at=self._clock(),
        )
        self._record_compensation(life, record)
        _logger.critical(
            "[Saga %s] 补偿三态=FAILED：撤单失败且终态不可确认，需人工对账: order=%s",
            life.saga_id[:8],
            life.order_id,
        )
        return record

    def _record_compensation(self, life: SagaOrderLifecycle, record: CompensationRecord) -> None:
        with self._lock:
            life.compensations.append(record)

    def _audit_log_order_cancelled(self, order: Order, record: CompensationRecord) -> None:
        """补偿撤单审计（注入审计器时）。"""
        if self._audit is None:
            return
        try:
            from zephyr.ex_core.audit_journal.auditor import AuditSource, ExecutionAuditEventType

            self._audit.log(
                ExecutionAuditEventType.ORDER_CANCELLED,
                order.order_id,
                order.symbol,
                AuditSource.AUTO,
                {"reason": "saga_session_compensate", "outcome": record.outcome.value},
            )
        except Exception:  # noqa: BLE001 — 审计失效不阻断补偿主链
            _logger.exception("补偿撤单审计异常: order=%s", order.order_id)

    # ── 接线点 3：对账面（九态断言）──

    def reconcile(
        self,
        order_id: str,
        broker_state: BrokerOrderState | str,
    ) -> ReconciliationVerdict | None:
        """单订单九态对账断言（本地台账 vs 券商九态）。

        Returns:
            断言结果；订单不在册=None（对账面只对在册跟踪订单负责）。
        """
        with self._lock:
            life = self._tracked.get(order_id)
        order = self._order_manager.get_order(order_id)
        if life is None or order is None:
            return None
        verdict = self._bridge.reconcile(order_id, order.status, broker_state)
        with self._lock:
            life.nine_assertions.append(verdict)
            if verdict.matched and order.status in _TERMINAL_STATUSES:
                life.phase = SagaPhase.RECONCILED
        if not verdict.matched and self._on_drift is not None:
            try:
                self._on_drift(verdict)
            except Exception:  # noqa: BLE001 — 升级回调异常不阻断对账面
                _logger.exception("对账漂移升级回调异常: order=%s", order_id)
        return verdict

    def reconcile_all(
        self,
        broker_states: Mapping[str, BrokerOrderState | str],
    ) -> list[ReconciliationVerdict]:
        """批量九态对账（eod 归档/盘后对账事件触发；输入=适配器面九态快照）。

        未知九态 fail-closed：ValueError 逐单吞没为漂移记录（不断言不断链）。
        """
        verdicts: list[ReconciliationVerdict] = []
        with self._lock:
            order_ids = list(self._tracked.keys())
        for order_id in order_ids:
            if order_id not in broker_states:
                continue
            try:
                verdict = self.reconcile(order_id, broker_states[order_id])
            except ValueError as exc:
                _logger.error(
                    "批量对账 fail-closed（词表外九态）: order=%s state=%r", order_id, broker_states[order_id]
                )
                verdict = ReconciliationVerdict(
                    order_id=order_id,
                    local_status=self._order_manager.get_order(order_id).status  # type: ignore[union-attr]
                    if self._order_manager.get_order(order_id) is not None
                    else OrderStatus.PENDING,
                    broker_state=str(broker_states[order_id]),
                    mapped_status=None,
                    matched=False,
                    detail=f"fail-closed: {exc}",
                )
            if verdict is not None:
                verdicts.append(verdict)
        return verdicts
