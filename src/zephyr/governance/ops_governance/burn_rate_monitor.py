# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.ops_governance.burn_rate_monitor
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.ops_governance.budget_models
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RES_burn_rate_monitor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
Burn Rate Monitor — MOD-INF-024

Four-window burn rate (5min/30min/2h/24h) with distribution shift detection
and alert routing into the escalation protocol.
Blueprint: docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md §5
"""

from __future__ import annotations

import threading
from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum

from .budget_models import (
    BudgetAlert,
    BudgetDimension,
    BudgetLevel,
    BudgetPolicy,
)


class BurnSeverity(Enum):
    NORMAL = "NORMAL"
    ELEVATED = "ELEVATED"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class BurnWindow:
    name: str
    duration_seconds: int
    sample_buffer: deque[tuple[datetime, float]] = field(default_factory=lambda: deque(maxlen=500))
    last_burn_rate: float = 0.0
    severity: BurnSeverity = BurnSeverity.NORMAL


class BurnRateMonitor:
    WINDOWS: list[tuple[str, int, int]] = [
        ("5min", 300, 100),
        ("30min", 1800, 200),
        ("2h", 7200, 300),
        ("24h", 86400, 500),
    ]

    SEVERITY_THRESHOLDS: dict[BudgetDimension, dict[BurnSeverity, float]] = {
        BudgetDimension.TOKEN: {
            BurnSeverity.ELEVATED: 0.5,
            BurnSeverity.HIGH: 0.7,
            BurnSeverity.CRITICAL: 0.9,
        },
        BudgetDimension.COST: {
            BurnSeverity.ELEVATED: 0.4,
            BurnSeverity.HIGH: 0.6,
            BurnSeverity.CRITICAL: 0.85,
        },
    }

    def __init__(self, dimension: BudgetDimension = BudgetDimension.TOKEN):
        self.dimension = dimension
        self._windows: dict[str, BurnWindow] = {}
        self._alerts: list[BudgetAlert] = []
        self._distribution_baseline: list[float] | None = None
        self._lock = threading.Lock()
        self._init_windows()

    def _init_windows(self) -> None:
        for name, duration, _max_samples in self.WINDOWS:
            self._windows[name] = BurnWindow(name=name, duration_seconds=duration)

    def record_consumption(self, amount: float, timestamp: datetime | None = None) -> None:
        ts = timestamp or datetime.now(UTC)
        with self._lock:
            for win in self._windows.values():
                win.sample_buffer.append((ts, amount))
                self._prune_window(win)

    def compute_burn_rates(self, daily_limit: float) -> None:
        with self._lock:
            for win in self._windows.values():
                total = sum(amt for _ts, amt in win.sample_buffer)
                win.last_burn_rate = total / daily_limit if daily_limit > 0 else 0.0
                win.severity = self._classify_burn(win.last_burn_rate)

    def get_severity(self) -> BurnSeverity:
        with self._lock:
            worst = BurnSeverity.NORMAL
            severity_order = list(BurnSeverity)
            for win in self._windows.values():
                if severity_order.index(win.severity) > severity_order.index(worst):
                    worst = win.severity
            return worst

    def detect_distribution_shift(self, recent_samples: list[float] | None = None) -> float:
        with self._lock:
            if self._distribution_baseline is None:
                self._distribution_baseline = [win.last_burn_rate for win in self._windows.values()]
                return 0.0

            current = recent_samples or [win.last_burn_rate for win in self._windows.values()]
            shift = self._wasserstein_1d(self._distribution_baseline, current)
            return shift

    def update_baseline(self) -> None:
        with self._lock:
            self._distribution_baseline = [win.last_burn_rate for win in self._windows.values()]

    def generate_alert(self, policy: BudgetPolicy) -> BudgetAlert | None:
        sev = self.get_severity()
        if sev is BurnSeverity.NORMAL:
            return None

        level_map: dict[BurnSeverity, BudgetLevel] = {
            BurnSeverity.ELEVATED: BudgetLevel.L1_WARNING,
            BurnSeverity.HIGH: BudgetLevel.L2_THROTTLED,
            BurnSeverity.CRITICAL: BudgetLevel.L4_EMERGENCY,
        }

        worst_window = max(self._windows.values(), key=lambda w: w.last_burn_rate)

        message = (
            f"Burn rate {worst_window.last_burn_rate:.2%} "
            f"in {worst_window.name} window "
            f"[{self.dimension.name}] severity={sev.name}"
        )

        alert = BudgetAlert(
            policy_id=policy.policy_id,
            dimension=self.dimension,
            level=level_map[sev],
            message=message,
        )

        with self._lock:
            self._alerts.append(alert)

        return alert

    def get_burn_summary(self) -> dict[str, dict[str, object]]:
        with self._lock:
            return {
                name: {
                    "rate": win.last_burn_rate,
                    "severity": win.severity.name,
                    "samples": len(win.sample_buffer),
                }
                for name, win in self._windows.items()
            }

    def get_alerts(self, limit: int = 20) -> list[BudgetAlert]:
        with self._lock:
            return list(self._alerts[-limit:])

    def reset(self) -> None:
        with self._lock:
            self._init_windows()
            self._alerts.clear()
            self._distribution_baseline = None

    def _prune_window(self, win: BurnWindow) -> None:
        cutoff = datetime.now(UTC) - timedelta(seconds=win.duration_seconds)
        pruned = deque(
            ((ts, amt) for ts, amt in win.sample_buffer if ts > cutoff),
            maxlen=win.sample_buffer.maxlen,
        )
        win.sample_buffer = pruned

    def _classify_burn(self, rate: float) -> BurnSeverity:
        thresholds = self.SEVERITY_THRESHOLDS.get(
            self.dimension,
            {BurnSeverity.ELEVATED: 0.3, BurnSeverity.HIGH: 0.5, BurnSeverity.CRITICAL: 0.8},
        )
        if rate >= thresholds.get(BurnSeverity.CRITICAL, 0.9):
            return BurnSeverity.CRITICAL
        if rate >= thresholds.get(BurnSeverity.HIGH, 0.7):
            return BurnSeverity.HIGH
        if rate >= thresholds.get(BurnSeverity.ELEVATED, 0.5):
            return BurnSeverity.ELEVATED
        return BurnSeverity.NORMAL

    def _wasserstein_1d(self, p: list[float], q: list[float]) -> float:
        if len(p) != len(q) or len(p) == 0:
            return 0.0
        p_sorted = sorted(p)
        q_sorted = sorted(q)
        total = sum(abs(a - b) for a, b in zip(p_sorted, q_sorted, strict=False))
        return total / len(p_sorted)
