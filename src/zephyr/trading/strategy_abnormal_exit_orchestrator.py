# [BLUEPRINT] MOD-TRADING-008 | docs/03_modules/_domain_trading/strategy_abnormal_exit/blueprint.md
# [MODULE] zephyr.trading.strategy_abnormal_exit_orchestrator
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.shared.contracts.strategy_lifecycle_event(MOD-INF-016); zephyr.shared.foundation.errors(MOD-INF-016)
# [CONSUMERS] finalizer(MOD-INF-035, 运行时装配批 register 清理函数); stop_gate(MOD-INF-035, has_unresolved_exits 探针)
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 五步编排顺序固定(冻结→撤单→平仓→核对→置态); 冻结失败不宣称EXITED(Fail-Closed)但撤单/平仓继续(安全方向); 撤单/平仓按优先级降序; 核对残留或任一腿失败→EXIT_FAILED+升级告警; 幂等键重放返回缓存报告; 纯编排无IO(执行委托注入端口); 报告frozen不可变
# [MODIFY-GUARD] docs/03_modules/_domain_trading/strategy_abnormal_exit/blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidExitRequestError
# [TESTS] tests/trading/test_strategy_abnormal_exit_orchestrator.py
# [A_module] module_id=MOD-TRADING-008 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent

# [ALGO_FLOW]
# I1: AbnormalExitRequest(strategy_id/trigger/reason/open_orders/positions/idempotency_key)
# I2: 注入端口(freezer/canceller/closer/verifier/recorder/alert/audit) + clock
# A1: 校验+幂等命中检查
# A2: 冻结新信号(失败→Fail-Closed: 继续清理但终态EXIT_FAILED+升级告警)
# A3: 按优先级降序撤单→按优先级降序平仓(单腿异常隔离记录)
# A4: 仓位清理核对(异常按不可宣称退出处理)
# A5: 全净→StrategyLifecycleEvent(EXITED)置态; 否则EXIT_FAILED+升级告警
# O1: AbnormalExitReport(frozen) + 幂等缓存
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A2
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> O1
"""
Strategy Abnormal Exit Orchestrator — 策略异常退出编排器 (MOD-TRADING-008, D-SIGNAL-150 MVP)

策略异常安全退出的编排面（业界对标：Lean 算法异常 liquidate；vnpy 策略停止回收）。
五步编排（顺序固定）：冻结新信号 → 按优先级撤单/平仓 → 仓位清理核对 →
状态置 EXITED（CTR-P1-006 契约留痕）→ 告警与审计留痕。
覆盖三触发路径：崩溃（CRASH）/ 超时（TIMEOUT）/ 风控触发（RISK_TRIGGERED）。

Fail-Closed 铁律：冻结失败 / 任一腿失败 / 核对残留 → 不宣称 EXITED
（final_status=EXIT_FAILED + CRITICAL 升级告警）；冻结失败时撤单/平仓仍继续
（安全方向）。执行细节（券商撤单/平仓）全部经注入端口，本模块纯编排无 IO。

集成（运行时装配批接线，本模块不 import 不复制）：
  - finalizer.py：register("strategy-abnormal-exit", orch.make_finalizer_cleanup())
  - stop_gate 类消费方：orch.has_unresolved_exits() 判定未决退出

SSoT: docs/03_modules/_domain_trading/strategy_abnormal_exit/blueprint.md
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: signal_freezer 参数
#   fields: 参数 signal_freezer（无注解）
#   code: strategy_abnormal_exit_orchestrator.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: order_canceller 参数
#   fields: 参数 order_canceller（无注解）
#   code: strategy_abnormal_exit_orchestrator.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: position_closer 参数
#   fields: 参数 position_closer（无注解）
#   code: strategy_abnormal_exit_orchestrator.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: position_verifier 参数
#   fields: 参数 position_verifier（无注解）
#   code: strategy_abnormal_exit_orchestrator.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① StrategyAbnormalExitOrchestrator
#   name_en: StrategyAbnormalExitOrchestrator
#   intro: 策略异常退出编排器（五步编排，全部 Fail-Closed）。
#   desc: 策略异常退出编排器（五步编排，全部 Fail-Closed）。 Args: signal_freezer: 冻结新信号端口；返回 True=冻结确认。 order_cancell…；公共方法（定义序）: execute…
#   inputs: signal_freezer order_canceller position_closer position_verifier life…
#   outputs: 返回值
#   （注：A1 之后另有 7 个公共定义未列入（含 7 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（8 定义）
#   name_en: public defs
#   intro: StrategyAbnormalExitOrchestrator
#   downstream: finalizer(MOD-INF-035, 运行时装配批 register 清理函数); stop_gate(MOD-INF-035, has_unreso…
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

import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Final

from zephyr.shared.contracts.strategy_lifecycle_event import StrategyLifecycleEvent
from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)

__all__: Final = [
    "AbnormalExitReport",
    "AbnormalExitRequest",
    "ExitFinalStatus",
    "ExitLeg",
    "ExitTrigger",
    "FailedLeg",
    "InvalidExitRequestError",
    "StrategyAbnormalExitOrchestrator",
]


class InvalidExitRequestError(ZephyrBaseError):
    """异常退出请求非法（空 strategy_id / 空 idempotency_key）。"""


class ExitTrigger(str, Enum):
    """异常退出触发路径（崩溃/超时/风控触发）。"""

    CRASH = "crash"
    TIMEOUT = "timeout"
    RISK_TRIGGERED = "risk_triggered"


class ExitFinalStatus(str, Enum):
    """退出终态（仅全净才 EXITED）。"""

    EXITED = "EXITED"
    EXIT_FAILED = "EXIT_FAILED"


@dataclass(frozen=True)
class ExitLeg:
    """待清理腿（挂单或持仓），priority 越大越先处理。"""

    ref_id: str
    priority: int = 0


@dataclass(frozen=True)
class AbnormalExitRequest:
    """异常退出请求（frozen）。"""

    strategy_id: str
    trigger: ExitTrigger
    reason: str
    idempotency_key: str
    open_orders: tuple[ExitLeg, ...] = ()
    positions: tuple[ExitLeg, ...] = ()
    previous_status: str = "ACTIVE"


@dataclass(frozen=True)
class FailedLeg:
    """失败腿留痕（phase: freeze/cancel_order/close_position/verify/record_status）。"""

    phase: str
    ref_id: str
    error: str


@dataclass(frozen=True)
class AbnormalExitReport:
    """异常退出报告（frozen；final_status=EXITED 仅当全净）。"""

    strategy_id: str
    trigger: ExitTrigger
    final_status: ExitFinalStatus
    freeze_ok: bool
    cancelled_order_ids: tuple[str, ...]
    closed_position_ids: tuple[str, ...]
    failed_legs: tuple[FailedLeg, ...]
    remaining_positions: tuple[str, ...]
    alerts_emitted: int
    audit_records: int
    started_at: datetime
    finished_at: datetime


#: 端口签名（生产接线：券商网关/信号网关/审计链）
SignalFreezer = Callable[[str], bool]
OrderCanceller = Callable[[str], None]
PositionCloser = Callable[[str], None]
PositionVerifier = Callable[[str], tuple[str, ...]]
LifecycleRecorder = Callable[[StrategyLifecycleEvent], None]
AlertSink = Callable[[str, dict], None]
AuditSink = Callable[[str, dict], None]


class StrategyAbnormalExitOrchestrator:
    """策略异常退出编排器（五步编排，全部 Fail-Closed）。

    Args:
        signal_freezer: 冻结新信号端口；返回 True=冻结确认。
        order_canceller: 撤单端口（按 ref_id）；异常=该腿失败。
        position_closer: 平仓端口（按 ref_id）；异常=该腿失败。
        position_verifier: 仓位核对端口；返回残留仓位 ref_id 元组（空=清理干净）。
        lifecycle_recorder: 生命周期事件记录端口（EXITED 置态留痕）。
        alert_sink: 告警端口（level, payload）。
        audit_sink: 审计端口（event, payload）。
        clock: 时钟协议（默认 datetime.now(UTC)）；测试注入固定时钟保判定确定性。
    """

    def __init__(
        self,
        signal_freezer: SignalFreezer,
        order_canceller: OrderCanceller,
        position_closer: PositionCloser,
        position_verifier: PositionVerifier,
        lifecycle_recorder: LifecycleRecorder,
        alert_sink: AlertSink,
        audit_sink: AuditSink,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._freezer = signal_freezer
        self._canceller = order_canceller
        self._closer = position_closer
        self._verifier = position_verifier
        self._recorder = lifecycle_recorder
        self._alert = alert_sink
        self._audit = audit_sink
        self._clock = clock or (lambda: datetime.now(UTC))
        self._lock = threading.Lock()
        self._cache: dict[str, AbnormalExitReport] = {}
        self._reports: list[AbnormalExitReport] = []

    def execute(self, request: AbnormalExitRequest) -> AbnormalExitReport:
        """执行五步异常退出编排。同 idempotency_key 重放返回缓存报告。

        Raises:
            InvalidExitRequestError: strategy_id / idempotency_key 为空。
        """
        if not request.strategy_id.strip():
            raise InvalidExitRequestError(
                "strategy_id 不允许为空",
                details={"idempotency_key": request.idempotency_key},
            )
        if not request.idempotency_key.strip():
            raise InvalidExitRequestError(
                "idempotency_key 不允许为空",
                details={"strategy_id": request.strategy_id},
            )
        with self._lock:
            cached = self._cache.get(request.idempotency_key)
        if cached is not None:
            _logger.info(
                "ABNORMAL_EXIT_REPLAY strategy=%s key=%s 幂等命中",
                request.strategy_id,
                request.idempotency_key,
            )
            return cached

        started_at = self._clock()
        alerts = 0
        audits = 0

        audits += self._emit_audit(
            "EXIT_TRIGGERED",
            {
                "strategy_id": request.strategy_id,
                "trigger": request.trigger.value,
                "reason": request.reason,
                "idempotency_key": request.idempotency_key,
            },
        )
        alerts += self._emit_alert(
            "WARNING",
            {
                "event": "abnormal_exit_triggered",
                "strategy_id": request.strategy_id,
                "trigger": request.trigger.value,
                "reason": request.reason,
            },
        )

        failed_legs: list[FailedLeg] = []

        # ── 步骤 1: 冻结新信号（失败→Fail-Closed，但清理继续）────────
        freeze_ok = False
        try:
            freeze_ok = bool(self._freezer(request.strategy_id))
        except Exception as exc:  # noqa: BLE001 — Fail-Closed
            _logger.critical("EXIT_FREEZE_ERROR strategy=%s error=%s", request.strategy_id, exc)
            failed_legs.append(FailedLeg(phase="freeze", ref_id=request.strategy_id, error=str(exc)))
        if not freeze_ok:
            alerts += self._emit_alert(
                "CRITICAL",
                {
                    "event": "signal_freeze_failed",
                    "strategy_id": request.strategy_id,
                    "detail": "新信号冻结未确认，终态不得宣称EXITED",
                },
            )

        # ── 步骤 2: 按优先级降序撤单/平仓（单腿异常隔离）─────────────
        cancelled: list[str] = []
        for leg in sorted(request.open_orders, key=lambda x: x.priority, reverse=True):
            try:
                self._canceller(leg.ref_id)
                cancelled.append(leg.ref_id)
            except Exception as exc:  # noqa: BLE001 — 单腿隔离，其余腿继续
                _logger.error("EXIT_CANCEL_ERROR order=%s error=%s", leg.ref_id, exc)
                failed_legs.append(FailedLeg(phase="cancel_order", ref_id=leg.ref_id, error=str(exc)))

        closed: list[str] = []
        for leg in sorted(request.positions, key=lambda x: x.priority, reverse=True):
            try:
                self._closer(leg.ref_id)
                closed.append(leg.ref_id)
            except Exception as exc:  # noqa: BLE001 — 单腿隔离，其余腿继续
                _logger.error("EXIT_CLOSE_ERROR position=%s error=%s", leg.ref_id, exc)
                failed_legs.append(FailedLeg(phase="close_position", ref_id=leg.ref_id, error=str(exc)))

        # ── 步骤 3: 仓位清理核对（异常=不可宣称退出）─────────────────
        remaining: tuple[str, ...] = ()
        try:
            remaining = tuple(self._verifier(request.strategy_id))
        except Exception as exc:  # noqa: BLE001 — Fail-Closed
            _logger.error("EXIT_VERIFY_ERROR strategy=%s error=%s", request.strategy_id, exc)
            failed_legs.append(FailedLeg(phase="verify", ref_id=request.strategy_id, error=str(exc)))
            remaining = ("__VERIFY_UNAVAILABLE__",)

        # ── 步骤 4: 状态置 EXITED（仅全净；置态失败=Fail-Closed）─────
        clean = freeze_ok and not failed_legs and not remaining
        if clean:
            try:
                self._recorder(
                    StrategyLifecycleEvent(
                        event_timestamp=self._clock().isoformat(),
                        event_type="STRATEGY_EXITED",
                        idempotency_key=request.idempotency_key,
                        new_status="EXITED",
                        previous_status=request.previous_status,
                        reason=request.reason,
                        strategy_id=request.strategy_id,
                        triggered_by=request.trigger.value,
                    )
                )
            except Exception as exc:  # noqa: BLE001 — 置态留痕失败不得宣称退出
                _logger.error("EXIT_RECORD_ERROR strategy=%s error=%s", request.strategy_id, exc)
                failed_legs.append(FailedLeg(phase="record_status", ref_id=request.strategy_id, error=str(exc)))
                clean = False

        final_status = ExitFinalStatus.EXITED if clean else ExitFinalStatus.EXIT_FAILED

        # ── 步骤 5: 告警与审计留痕（失败升级）────────────────────────
        audits += self._emit_audit(
            "EXIT_COMPLETED" if clean else "EXIT_FAILED",
            {
                "strategy_id": request.strategy_id,
                "final_status": final_status.value,
                "cancelled": list(cancelled),
                "closed": list(closed),
                "failed_legs": [f"{f.phase}:{f.ref_id}" for f in failed_legs],
                "remaining": list(remaining),
            },
        )
        if not clean:
            alerts += self._emit_alert(
                "CRITICAL",
                {
                    "event": "abnormal_exit_failed",
                    "strategy_id": request.strategy_id,
                    "failed_legs": [f"{f.phase}:{f.ref_id}" for f in failed_legs],
                    "remaining": list(remaining),
                },
            )

        report = AbnormalExitReport(
            strategy_id=request.strategy_id,
            trigger=request.trigger,
            final_status=final_status,
            freeze_ok=freeze_ok,
            cancelled_order_ids=tuple(cancelled),
            closed_position_ids=tuple(closed),
            failed_legs=tuple(failed_legs),
            remaining_positions=remaining,
            alerts_emitted=alerts,
            audit_records=audits,
            started_at=started_at,
            finished_at=self._clock(),
        )
        with self._lock:
            self._cache[request.idempotency_key] = report
            self._reports.append(report)
        _logger.info(
            "ABNORMAL_EXIT_DONE strategy=%s status=%s failed_legs=%d remaining=%d",
            request.strategy_id,
            final_status.value,
            len(failed_legs),
            len(remaining),
        )
        return report

    def has_unresolved_exits(self) -> bool:
        """是否存在未决退出（任一报告 EXIT_FAILED）——stop_gate 类消费方探针。"""
        with self._lock:
            return any(r.final_status is ExitFinalStatus.EXIT_FAILED for r in self._reports)

    def processed_reports(self) -> tuple[AbnormalExitReport, ...]:
        """已处理报告（tuple 拷贝，外部不可变内部状态）。"""
        with self._lock:
            return tuple(self._reports)

    def make_finalizer_cleanup(self) -> Callable[[], None]:
        """产 finalizer 清理函数（永不抛异常；运行时装配批 register 接线）。"""

        def _cleanup() -> None:
            try:
                unresolved = self.has_unresolved_exits()
                _logger.info(
                    "strategy-abnormal-exit finalizer cleanup: unresolved_exits=%s reports=%d",
                    unresolved,
                    len(self.processed_reports()),
                )
            except Exception as exc:  # noqa: BLE001 — finalizer 语义：清理函数永不抛
                _logger.debug("strategy-abnormal-exit cleanup failed: %s", exc, exc_info=True)

        return _cleanup

    def _emit_alert(self, level: str, payload: dict) -> int:
        try:
            self._alert(level, payload)
        except Exception as exc:  # noqa: BLE001 — 告警端口故障不阻断编排
            _logger.error("ALERT_SINK_ERROR level=%s error=%s", level, exc)
        return 1

    def _emit_audit(self, event: str, payload: dict) -> int:
        try:
            self._audit(event, payload)
        except Exception as exc:  # noqa: BLE001 — 审计端口故障不阻断编排
            _logger.error("AUDIT_SINK_ERROR event=%s error=%s", event, exc)
        return 1
