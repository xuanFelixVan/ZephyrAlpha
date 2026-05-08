"""
Error Budget Tracker — Error Budget 五级响应追踪 + Burn Rate 多窗口监控 (M-21)
对标：Google SRE Workbook §4 Error Budgets + §5.4 Multi-Window Multi-Burn-Rate Alerts

特性：
  - 五级响应：L0(Healthy) / L1(Warning) / L2(Cautious) / L3(Critical) / L4(Emergency)
  - 四窗口 Burn Rate 监控：1h / 6h / 3d / 30d
  - 自动恢复冷却：Emergency→Critical 6h, Critical→Cautious 24h
"""
import os
import sqlite3
import time
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Optional


class ResponseTier(IntEnum):
    L0_HEALTHY = 0
    L1_WARNING = 1
    L2_CAUTIOUS = 2
    L3_CRITICAL = 3
    L4_EMERGENCY = 4


BURN_RATE_THRESHOLDS = {
    "1h": {ResponseTier.L1_WARNING: 1.0, ResponseTier.L4_EMERGENCY: 14.4},
    "6h": {ResponseTier.L1_WARNING: 1.0, ResponseTier.L3_CRITICAL: 5.0},
    "3d": {ResponseTier.L1_WARNING: 1.0, ResponseTier.L2_CAUTIOUS: 3.0},
    "30d": {ResponseTier.L1_WARNING: 1.0, ResponseTier.L2_CAUTIOUS: 2.0},
}

RECOVERY_COOLDOWNS = {
    (ResponseTier.L4_EMERGENCY, ResponseTier.L3_CRITICAL): 6 * 3600,
    (ResponseTier.L3_CRITICAL, ResponseTier.L2_CAUTIOUS): 24 * 3600,
}


@dataclass
class BurnRateWindow:
    window_name: str
    window_seconds: int
    error_budget_total: float
    errors_observed: float
    burn_rate: float
    tier: ResponseTier


class ErrorBudgetTracker:
    """
    Error Budget 五级响应追踪器 (M-21)
    """

    WINDOWS = {"1h": 3600, "6h": 21600, "3d": 259200, "30d": 2592000}

    def __init__(self, db_path: Optional[str] = None, slo_target: float = 0.999):
        self.db_path = db_path or self._default_db_path()
        self.slo_target = slo_target
        self.error_budget_total = 1.0 - slo_target
        self._current_tier = ResponseTier.L0_HEALTHY
        self._tier_changed_at: float = 0.0

    def _default_db_path(self) -> str:
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "data", "capacity.db"
        )

    def evaluate(self) -> dict:
        now = time.time()
        burn_rates = {}

        for window_name, window_seconds in self.WINDOWS.items():
            errors = self._count_errors_since(now - window_seconds)
            burn_rate = errors / max(self.error_budget_total, 0.0001)
            burn_rates[window_name] = burn_rate

        tier = self._compute_tier(burn_rates)
        tier = self._apply_cooldown(tier)

        self._current_tier = tier

        return {
            "tier": tier.name,
            "tier_value": int(tier),
            "burn_rates": burn_rates,
            "error_budget_total": self.error_budget_total,
            "slo_target": self.slo_target,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
        }

    def _count_errors_since(self, since_timestamp: float) -> float:
        try:
            conn = sqlite3.connect(self.db_path)
            since_str = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(since_timestamp))
            row = conn.execute(
                "SELECT COUNT(*) FROM capacity_metrics WHERE sli_id = 'CAP-003-error-rate' "
                "AND ts > ? AND value > 0",
                (since_str,)
            ).fetchone()
            conn.close()
            return float(row[0]) if row else 0.0
        except Exception:
            return 0.0

    def _compute_tier(self, burn_rates: dict[str, float]) -> ResponseTier:
        tier = ResponseTier.L0_HEALTHY
        for window_name, burn_rate in burn_rates.items():
            thresholds = BURN_RATE_THRESHOLDS.get(window_name, {})
            for check_tier, threshold in sorted(thresholds.items(), reverse=True):
                if burn_rate >= threshold and check_tier > tier:
                    tier = check_tier
        return tier

    def _apply_cooldown(self, new_tier: ResponseTier) -> ResponseTier:
        if new_tier < self._current_tier:
            cooldown_key = (self._current_tier, new_tier)
            cooldown = RECOVERY_COOLDOWNS.get(cooldown_key, 0)
            if cooldown > 0:
                elapsed = time.time() - self._tier_changed_at
                if elapsed < cooldown:
                    return self._current_tier

        if new_tier != self._current_tier:
            self._tier_changed_at = time.time()
        return new_tier

    def persist(self, slo_id: str, tier: ResponseTier,
                budget_remaining: float, budget_consumed: float):
        try:
            conn = sqlite3.connect(self.db_path)
            now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            conn.execute(
                "INSERT INTO error_budget (slo_id, window_start, window_end, "
                "budget_total, budget_consumed, budget_remaining, response_tier, last_updated) "
                "VALUES (?, datetime('now', '-1 hour'), datetime('now'), ?, ?, ?, ?, ?)",
                (slo_id, self.error_budget_total, budget_consumed, budget_remaining, tier.name, now)
            )
            conn.commit()
            conn.close()
        except Exception:
            pass


_tracker: Optional[ErrorBudgetTracker] = None


def get_budget_tracker() -> ErrorBudgetTracker:
    global _tracker
    if _tracker is None:
        _tracker = ErrorBudgetTracker()
    return _tracker
