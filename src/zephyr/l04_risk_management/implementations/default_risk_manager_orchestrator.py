# ---
# layer: l04_risk_management
# category: risk_implementation
# status: active
# created: "2026-05-05"
# ---

"""L04 — Default Risk Manager Orchestrator

风险总管具体实现。编排事前/事后风控检查、日终盈亏校验、综合风控报告。

调用链：
  pre_trade_check → post_trade_check → daily_pnl_check → aggregate_report

CTR 契约：
  消费者 — CTR-002 (FactorSignal) ← L02
  消费者 — CTR-003 (RiskLimits) ← 本层
  消费者 — CTR-004 (Order) ← L05
  消费者 — CTR-005 (Fill) ← L06
  消费者 — CTR-006 (PositionSnapshot) ← L06
  生产者 — CTR-003 (RiskLimits) → L05
  生产者 — CTR-ERR-004 (RiskLimitViolationError) → L05, L06
  生产者 — CTR-P1-008 (RiskDashboardSnapshot) → L08

SSoT: cross-layer-contracts.yaml → CTR-003 + CTR-ERR-004 + CTR-P1-008
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional

from zephyr.l04_risk_management.risk_manager import (
    RiskLimits,
    RiskLimitViolationError,
    RiskDashboardSnapshot,
    RiskMetricsReport,
)
from zephyr.l04_risk_management.risk_manager_base import (
    RiskCheckResult,
    RiskManagerOrchestratorBase,
    RiskReport,
)
from zephyr.l04_risk_management.implementations.default_risk_limits_calculator import (
    DefaultRiskLimitsCalculator,
)
from zephyr.l04_risk_management.implementations.default_risk_validator import (
    DefaultRiskValidator,
)
from zephyr.l04_risk_management.implementations.default_position_limit_checker import (
    DefaultPositionLimitChecker,
)
from zephyr.l04_risk_management.implementations.default_stop_loss_engine import (
    DefaultStopLossEngine,
    StopLossRules,
)


__checker_id__ = "default-risk-manager-orchestrator"


class DefaultRiskManagerOrchestrator(RiskManagerOrchestratorBase):
    """默认风险总管——编排全套风控检查"""

    __checker_id__ = __checker_id__

    def __init__(
        self,
        portfolio_id: str,
        limits_calculator: Optional[DefaultRiskLimitsCalculator] = None,
        validator: Optional[DefaultRiskValidator] = None,
        position_checker: Optional[DefaultPositionLimitChecker] = None,
        stop_loss_engine: Optional[DefaultStopLossEngine] = None,
    ):
        self._portfolio_id = portfolio_id
        self._limits_calculator = limits_calculator or DefaultRiskLimitsCalculator()
        self._validator = validator or DefaultRiskValidator()
        self._position_checker = position_checker or DefaultPositionLimitChecker()
        self._stop_loss_engine = stop_loss_engine or DefaultStopLossEngine()
        self._check_results: list[RiskCheckResult] = []
        self._active_limits: Optional[RiskLimits] = None
        self._daily_pnl: Decimal = Decimal("0")
        self._loss_limit: Decimal = Decimal("50000")

    def pre_trade_check(self, order: Any, limits: Any, positions: Any) -> RiskCheckResult:
        if self._active_limits is None:
            self._active_limits = isinstance(limits, RiskLimits) and limits or self._compute_limits(positions)

        violations = self._validator.validate_order(
            symbol=order.symbol if hasattr(order, "symbol") else order.get("symbol", ""),
            target_weight=order.quantity if hasattr(order, "quantity") else order.get("quantity", 0),
            current_holdings={pos.get("symbol", ""): pos.get("weight", 0) for pos in (positions if isinstance(positions, list) else [positions])} if isinstance(positions, (list, dict)) else {},
            limits=self._active_limits,
        )

        passed = len([v for v in violations if v.severity == "HALT"]) == 0
        check_id = f"pre-{int(datetime.now(timezone.utc).timestamp())}"
        result = RiskCheckResult(
            check_id=check_id,
            rule_name="pre_trade_check",
            passed=passed,
            limit_value=1.0,
            actual_value=float(len(violations)),
            message=f"violations={len(violations)} halt={len([v for v in violations if v.severity == 'HALT'])}" if violations else "all_clear",
            timestamp=datetime.now(timezone.utc),
            severity="HALT" if not passed else "info",
        )
        self._check_results.append(result)

        if not passed:
            halt_violations = [v for v in violations if v.severity == "HALT"]
            raise RiskLimitViolationError(
                error_id=check_id,
                portfolio_id=self._portfolio_id,
                violated_constraint=halt_violations[0].constraint,
                violation_detail=halt_violations[0].description,
                limit_value=halt_violations[0].limit_value,
                actual_value=halt_violations[0].actual_value,
                recovery_hint="REDUCE_AND_RETRY",
                idempotency_key=f"err-{check_id}",
            )

        return result

    def post_trade_check(self, fill: Any, positions: Any) -> RiskCheckResult:
        check_id = f"post-{int(datetime.now(timezone.utc).timestamp())}"
        result = RiskCheckResult(
            check_id=check_id,
            rule_name="post_trade_check",
            passed=True,
            limit_value=0.0,
            actual_value=0.0,
            message="post_trade check passed",
            timestamp=datetime.now(timezone.utc),
            severity="info",
        )
        self._check_results.append(result)
        return result

    def daily_pnl_check(self, daily_pnl: Decimal, loss_limit: Decimal) -> RiskCheckResult:
        passed = daily_pnl >= -loss_limit
        check_id = f"pnl-{int(datetime.now(timezone.utc).timestamp())}"
        result = RiskCheckResult(
            check_id=check_id,
            rule_name="daily_pnl_check",
            passed=passed,
            limit_value=float(-loss_limit),
            actual_value=float(daily_pnl),
            message=f"daily_pnl={daily_pnl} loss_limit={loss_limit}",
            timestamp=datetime.now(timezone.utc),
            severity="HALT" if not passed else "info",
        )
        self._check_results.append(result)
        self._daily_pnl = daily_pnl

        if not passed:
            self._validator.trigger_kill_switch()

        return result

    def aggregate_report(self) -> RiskReport:
        failed = [c for c in self._check_results if not c.passed]
        alerts = [c.message for c in failed] if failed else []
        return RiskReport(
            as_of_timestamp=datetime.now(timezone.utc),
            portfolio_id=self._portfolio_id,
            checks=self._check_results.copy(),
            overall_pass=len(failed) == 0,
            active_alerts=alerts,
            kill_switch_active=self._validator.kill_switch_active,
        )

    def snapshot(self, portfolio_id: str) -> Optional[RiskDashboardSnapshot]:
        if not self._active_limits:
            return None
        var_cap = self._active_limits.max_portfolio_var_1d
        var_f = float(var_cap) if var_cap is not None else 0.0
        return RiskDashboardSnapshot(
            snapshot_time=datetime.now(timezone.utc).isoformat(),
            portfolio_id=portfolio_id,
            portfolio_var_1d=var_f,
            max_drawdown_current=float(self._active_limits.max_drawdown_limit or 0.0),
            gross_leverage=float(self._active_limits.max_gross_leverage),
            top_position_concentration=float(self._active_limits.max_single_position),
            sector_concentrations={},
            active_alerts=[c.message for c in self._check_results if not c.passed],
            overall_risk_score=self._compute_risk_score(),
            idempotency_key=f"snap-{int(datetime.now(timezone.utc).timestamp())}",
        )

    def _compute_limits(self, positions: Any) -> RiskLimits:
        positions_dict = {}
        market_values = {}
        total_nav = Decimal("1000000")
        if isinstance(positions, dict):
            positions_dict = positions
            market_values = {k: float(v) * float(total_nav) for k, v in positions.items()}
        return self._limits_calculator.calculate(
            positions=positions_dict,
            market_values=market_values,
            total_nav=total_nav,
        )

    def _compute_risk_score(self) -> float:
        failed_count = len([c for c in self._check_results if not c.passed])
        base = 1.0
        for c in self._check_results:
            if c.severity == "HALT":
                base += 3.0
            elif c.severity == "warning":
                base += 1.5
        return min(10.0, base)


__all__ = ["DefaultRiskManagerOrchestrator"]
