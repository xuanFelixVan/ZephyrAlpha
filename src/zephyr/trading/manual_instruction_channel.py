# [BLUEPRINT] MOD-TRADING-011 | docs/03_modules/_domain_trading/manual_instruction_channel/blueprint.md
# [MODULE] zephyr.trading.manual_instruction_channel
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] 录入面(CLI/前端装配批); track_fusion 轨道3人工指令(MOD-PLAN-020 下游消费); 执行委托 ex_core trading_session(MOD-L06-001，装配批接线)
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] Decimal-only数量; ManualInstruction/IntakeVerdict/ExecutionReconReport/InstructionAuditEvent frozen不可变; intake双闸顺序固定(边界→风控)不短路全量落审计; 探针未接线/异常=REJECTED(Fail-Closed绝不臆造放行); 通道只产裁决与对账状态不直连券商; 审计事件含序号/阶段/结果/时间戳全程可追溯; audit_sink/alert_sink异常吞没不阻断主链
# [MODIFY-GUARD] docs/03_modules/_domain_trading/manual_instruction_channel/blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidManualInstructionError(ZA-TR-0024)
# [TESTS] tests/trading/test_manual_instruction_channel.py
# [A_module] module_id=MOD-TRADING-011 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: ManualInstruction(schema校验Fail-Closed)
# I2: premarket_check_fn/risk_check_fn(注入委托 MOD-EX-063/MOD-EX-024)
# A1: 边界闸(premarket_check_fn; False→PREMARKET_NOT_READY; None→PROBE_UNWIRED; 异常→PROBE_ERROR)
# A2: 风控闸(risk_check_fn C-004面; (False,reason)→RISK_REJECTED; None→PROBE_UNWIRED; 异常→PROBE_ERROR)
# A3: 裁决(双闸全过→ACCEPTED; 任一不过→REJECTED首因reason_code; 逐事件落审计链)
# A4: 对账(execution_probe取回报; None→UNFILLED; 异常→PROBE_ERROR; |filled−expected|>tol→DRIFT+alert+audit)
# O1: IntakeVerdict(frozen,含audit_trail) / ExecutionReconReport(frozen)
# 边:
# I1 --> A1
# I1 --> A2
# I2 --> A1
# I2 --> A2
# A1 --> A3
# A2 --> A3
# A3 --> O1
# A4 --> O1
# [/ALGO_FLOW]
"""C-013 外部指令盯盘 — 人工指令通道 (MOD-TRADING-011, CAND-TRD-003, B1-00192)。

OMS 手工单通道判定核心：
  ① 指令 schema 校验（标的/方向/数量/时限/操作人，frozen，Fail-Closed）；
  ② 录入裁决 intake：盘前边界闸（premarket_check_fn 委托 MOD-EX-063）→
     C-004 风控闸（risk_check_fn 委托 MOD-EX-024/trading_session 合规闸），
     双闸顺序固定不短路，ACCEPTED/REJECTED + reason_code；探针未接线/异常
     = REJECTED（Fail-Closed，绝不臆造放行）；
  ③ 执行回报对账 reconcile：execution_probe 取回报，成交量 vs 指令量容差
     比对 → MATCHED/DRIFT/UNFILLED/PROBE_ERROR，DRIFT 告警+审计；
  ④ 全程审计：接收→边界→风控→裁决→对账逐事件落审计链（audit_sink 委托
     D_GOV_AUDIT）。

不做什么：不直连券商/下单（ACCEPTED 后执行委托既有 ex_core 链）；不做 C-004
判定本身（委托）；CLI/前端录入界面属装配面。
铸号备注：初铸 MOD-TRADING-009 与 W-P1-23 并行会话 trading_order_aggregate
撞号，本方退让改铸 MOD-TRADING-011（depgraph 节点 10631553 已改号）。

SSoT: docs/03_modules/_domain_trading/manual_instruction_channel/blueprint.md
Version: 0.1.0
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from typing import Final

from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)

__all__: Final = [
    "ExecutionReconReport",
    "InstructionAuditEvent",
    "InstructionSide",
    "IntakeVerdict",
    "InvalidManualInstructionError",
    "ManualInstruction",
    "ManualInstructionChannel",
    "ReconStatus",
]


class InvalidManualInstructionError(ZephyrBaseError):
    """人工指令输入非法——空标识/非正数量/时限倒置等（Fail-Closed，占位未登码）。"""

    error_code = "ZA-TR-0024"


class InstructionSide(str, Enum):
    """指令方向（人工买入/卖出/调仓）。"""

    BUY = "BUY"
    SELL = "SELL"
    ADJUST = "ADJUST"


class ReconStatus(str, Enum):
    """执行回报对账状态。"""

    MATCHED = "MATCHED"
    DRIFT = "DRIFT"
    UNFILLED = "UNFILLED"
    PROBE_ERROR = "PROBE_ERROR"


@dataclass(frozen=True)
class ManualInstruction:
    """人工指令 schema（frozen；标的/方向/数量/时限/操作人）。"""

    instruction_id: str
    symbol: str
    side: InstructionSide
    quantity: Decimal
    expire_at: datetime
    operator: str
    created_at: datetime
    note: str = ""

    def __post_init__(self) -> None:
        for name in ("instruction_id", "symbol", "operator"):
            value = getattr(self, name)
            if not value or not str(value).strip():
                raise InvalidManualInstructionError(f"{name} 不能为空")
        if not isinstance(self.side, InstructionSide):
            raise InvalidManualInstructionError(f"side 非法: {self.side!r}")
        if not isinstance(self.quantity, Decimal) or not self.quantity.is_finite() or self.quantity <= 0:
            raise InvalidManualInstructionError(f"quantity 必须为正有限 Decimal: {self.quantity!r}")
        if self.expire_at <= self.created_at:
            raise InvalidManualInstructionError(
                f"时限非法: expire_at={self.expire_at} 须严格晚于 created_at={self.created_at}"
            )


@dataclass(frozen=True)
class InstructionAuditEvent:
    """指令审计事件（frozen；序号/阶段/结果/时间戳，全程可追溯）。"""

    seq: int
    stage: str  # RECEIVED / PREMARKET / RISK / VERDICT / RECONCILE
    outcome: str
    detail: str
    at: datetime


@dataclass(frozen=True)
class IntakeVerdict:
    """录入裁决（frozen；含全量审计链）。"""

    instruction_id: str
    accepted: bool
    reason_code: str  # ACCEPTED / PREMARKET_NOT_READY / RISK_REJECTED / PROBE_UNWIRED / PROBE_ERROR
    reason: str
    audit_trail: tuple[InstructionAuditEvent, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ExecutionReconReport:
    """执行回报对账报告（frozen）。"""

    instruction_id: str
    status: ReconStatus
    expected_quantity: Decimal
    filled_quantity: Decimal
    detail: str


class ManualInstructionChannel:
    """人工指令通道（录入裁决 + 执行回报对账 + 全程审计）。

    Args:
        premarket_check_fn: 盘前边界闸探针（() → ready: bool；委托 MOD-EX-063）。
            None=未接线（Fail-Closed 拒）；异常=PROBE_ERROR 拒。
        risk_check_fn: C-004 风控闸探针（instruction → (ok, reason)；委托
            MOD-EX-024/trading_session 合规闸）。None=未接线拒；异常=PROBE_ERROR 拒。
        audit_sink: 审计事件出口（逐事件调用）；None=仅日志；异常吞没不阻断。
        alert_sink: 告警出口（message）；None=仅日志；异常吞没不阻断。
        clock: 时钟（默认 UTC now）；测试注入固定时钟保确定性。
        qty_tolerance: 对账数量容差（默认 0=精确；严格大于才 DRIFT）。
    """

    def __init__(
        self,
        *,
        premarket_check_fn: Callable[[], bool] | None = None,
        risk_check_fn: Callable[[ManualInstruction], tuple[bool, str]] | None = None,
        audit_sink: Callable[[InstructionAuditEvent], None] | None = None,
        alert_sink: Callable[[str], None] | None = None,
        clock: Callable[[], datetime] | None = None,
        qty_tolerance: Decimal = Decimal("0"),
    ) -> None:
        if not isinstance(qty_tolerance, Decimal) or qty_tolerance < 0:
            raise InvalidManualInstructionError(f"qty_tolerance 必须 ≥0 Decimal: {qty_tolerance!r}")
        self._premarket_fn = premarket_check_fn
        self._risk_fn = risk_check_fn
        self._audit_sink = audit_sink
        self._alert_sink = alert_sink
        self._clock = clock or (lambda: datetime.now(UTC))
        self._qty_tolerance = qty_tolerance

    # ── 内部：审计/告警出口（异常吞没不阻断主链） ─────────────────
    def _emit(self, events: list[InstructionAuditEvent], stage: str, outcome: str, detail: str) -> None:
        event = InstructionAuditEvent(seq=len(events) + 1, stage=stage, outcome=outcome, detail=detail, at=self._clock())
        events.append(event)
        if self._audit_sink is not None:
            try:
                self._audit_sink(event)
            except Exception:  # noqa: BLE001 — 审计出口失败不阻断主链路
                _logger.exception("audit_sink 调用失败（已吞没，不阻断）: stage=%s", stage)

    def _alert(self, message: str) -> None:
        _logger.error("人工指令告警: %s", message)
        if self._alert_sink is not None:
            try:
                self._alert_sink(message)
            except Exception:  # noqa: BLE001 — 告警出口失败不阻断主链路
                _logger.exception("alert_sink 调用失败（已吞没，不阻断）")

    # ── 录入裁决（双闸顺序固定不短路） ────────────────────────────
    def intake(self, instruction: ManualInstruction) -> IntakeVerdict:
        """录入裁决：边界闸 → 风控闸（全量评估），ACCEPTED/REJECTED + 审计链。"""
        events: list[InstructionAuditEvent] = []
        iid = instruction.instruction_id
        self._emit(events, "RECEIVED", "OK", f"指令接收 id={iid} symbol={instruction.symbol} side={instruction.side.value}")

        # 边界闸（盘前就绪，委托 MOD-EX-063；Fail-Closed）
        pre_fail: tuple[str, str] | None = None
        if self._premarket_fn is None:
            pre_fail = ("PROBE_UNWIRED", "盘前边界探针未接线（Fail-Closed）")
        else:
            try:
                if self._premarket_fn():
                    self._emit(events, "PREMARKET", "OK", "盘前边界就绪")
                else:
                    pre_fail = ("PREMARKET_NOT_READY", "盘前边界未就绪（NoGo 边界拒入）")
            except Exception as exc:  # noqa: BLE001 — Fail-Closed
                pre_fail = ("PROBE_ERROR", f"盘前边界探针异常（Fail-Closed）: {exc!r}")
        if pre_fail is not None:
            self._emit(events, "PREMARKET", pre_fail[0], pre_fail[1])

        # 风控闸（C-004，委托 MOD-EX-024 面；Fail-Closed）
        risk_fail: tuple[str, str] | None = None
        if self._risk_fn is None:
            risk_fail = ("PROBE_UNWIRED", "C-004 风控探针未接线（Fail-Closed）")
        else:
            try:
                ok, reason = self._risk_fn(instruction)
                if ok:
                    self._emit(events, "RISK", "OK", "C-004 风控通过")
                else:
                    risk_fail = ("RISK_REJECTED", f"C-004 风控拒单: {reason}")
            except Exception as exc:  # noqa: BLE001 — Fail-Closed
                risk_fail = ("PROBE_ERROR", f"C-004 风控探针异常（Fail-Closed）: {exc!r}")
        if risk_fail is not None:
            self._emit(events, "RISK", risk_fail[0], risk_fail[1])

        # 裁决（首因 reason_code；双闸全过才放行）
        fail = pre_fail or risk_fail
        if fail is None:
            self._emit(events, "VERDICT", "ACCEPTED", "双闸通过，指令受理（执行委托 ex_core 链）")
            return IntakeVerdict(iid, True, "ACCEPTED", "双闸通过，指令受理", tuple(events))
        self._emit(events, "VERDICT", "REJECTED", f"{fail[0]}: {fail[1]}")
        self._alert(f"人工指令拒入 id={iid} {fail[0]}: {fail[1]}")
        return IntakeVerdict(iid, False, fail[0], fail[1], tuple(events))

    # ── 执行回报对账 ──────────────────────────────────────────────
    def reconcile(
        self,
        instruction: ManualInstruction,
        execution_probe: Callable[[str], object | None],
    ) -> ExecutionReconReport:
        """执行回报对账：成交量 vs 指令量容差比对（MATCHED/DRIFT/UNFILLED/PROBE_ERROR）。"""
        iid = instruction.instruction_id
        expected = instruction.quantity
        try:
            report = execution_probe(iid)
        except Exception as exc:  # noqa: BLE001 — 探针异常收敛为状态
            self._alert(f"执行回报探针异常 id={iid}: {exc!r}")
            return ExecutionReconReport(iid, ReconStatus.PROBE_ERROR, expected, Decimal("0"), f"probe error: {exc!r}")
        if report is None:
            return ExecutionReconReport(iid, ReconStatus.UNFILLED, expected, Decimal("0"), "无执行回报（未成交）")
        filled = getattr(report, "filled_quantity", None)
        if not isinstance(filled, Decimal):
            try:
                filled = Decimal(str(filled))
            except Exception:  # noqa: BLE001
                self._alert(f"执行回报数量非法 id={iid}: {filled!r}")
                return ExecutionReconReport(iid, ReconStatus.PROBE_ERROR, expected, Decimal("0"), f"bad filled_quantity: {filled!r}")
        if abs(filled - expected) > self._qty_tolerance:
            events: list[InstructionAuditEvent] = []
            detail = f"对账不一致 id={iid} expected={expected} filled={filled} tol={self._qty_tolerance}"
            self._emit(events, "RECONCILE", "DRIFT", detail)
            self._alert(detail)
            return ExecutionReconReport(iid, ReconStatus.DRIFT, expected, filled, detail)
        events = []
        self._emit(events, "RECONCILE", "MATCHED", f"对账一致 id={iid} filled={filled}")
        return ExecutionReconReport(iid, ReconStatus.MATCHED, expected, filled, "对账一致")
