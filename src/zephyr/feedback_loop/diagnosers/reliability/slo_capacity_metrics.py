# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.reliability.slo_capacity_metrics
# [DOMAIN] D_FBL_DIAGNOSERS
# [DEPENDENCIES] zephyr.feedback_loop.diagnosers.__init__
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
# [A_module] module_id=MOD-UNK_slo_capacity_metrics | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""SLO Capacity Metrics — v0.17.0+ R243-R248

SLO budget + burn rate + time_to_exhaustion 追踪：
  - error_budget_remaining_pct: 剩余错误预算 %
  - burn_rate_1h/6h/3d: 多窗口燃尽率
  - time_to_exhaustion_h: 预算完全耗尽预估小时
  - self_api_capacity_headroom: 自身API容量余量
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SLOWindow:
    window_hours: float
    error_count: int = 0
    total_count: int = 0
    target_burn_rate: float = 1.0

    @property
    def burn_rate(self) -> float:
        if self.total_count == 0:
            return 0.0
        return self.error_count / self.total_count

    @property
    def alert(self) -> bool:
        return self.burn_rate > self.target_burn_rate


@dataclass
class SLOCapacityMetrics:
    slo_pct: float = 99.9
    windows: dict[str, SLOWindow] = field(
        default_factory=lambda: {
            "1h": SLOWindow(1.0, target_burn_rate=14.4),
            "6h": SLOWindow(6.0, target_burn_rate=6.0),
            "3d": SLOWindow(72.0, target_burn_rate=1.0),
        }
    )
    total_requests: int = 0
    total_errors: int = 0

    def record(self, success: bool) -> None:
        self.total_requests += 1
        if not success:
            self.total_errors += 1
            for w in self.windows.values():
                w.error_count += 1
                w.total_count += 1

    def error_budget_remaining_pct(self) -> float:
        if self.total_requests == 0:
            return 100.0
        budget_errors = self.total_requests * (1.0 - self.slo_pct / 100.0)
        remaining = max(0.0, budget_errors - self.total_errors)
        return remaining / budget_errors * 100.0 if budget_errors > 0 else 0.0

    def exhaustion_alerts(self) -> list[str]:
        return [
            f"{name}: {w.burn_rate:.1f}x burn (target {w.target_burn_rate}x)"
            for name, w in self.windows.items()
            if w.alert
        ]
