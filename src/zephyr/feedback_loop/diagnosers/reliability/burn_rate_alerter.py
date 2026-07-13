# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.reliability.burn_rate_alerter
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
# [A_module] module_id=MOD-UNK_burn_rate_alerter | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Burn Rate Alerter — v0.14.0 R200

Blindspot: SLO burn rate not tracked; error budget exhausted silently.
Risk: R200 — 36-hour burn at 10x exhausts 30-day budget; no alert until SLO already breached.

Mitigation: Multi-window burn rate alerts per Google SRE workbook methodology.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BurnWindow:
    name: str
    window_seconds: float
    target_burn_rate: float
    current_burn_rate: float = 0.0
    error_count: int = 0
    total_count: int = 0


@dataclass
class BurnRateAlerter:
    slo_pct: float = 99.9
    windows: list[BurnWindow] = field(
        default_factory=lambda: [
            BurnWindow(name="1h", window_seconds=3600, target_burn_rate=14.4),
            BurnWindow(name="6h", window_seconds=21600, target_burn_rate=6.0),
            BurnWindow(name="3d", window_seconds=259200, target_burn_rate=1.0),
        ]
    )

    def record(self, success: bool) -> None:
        for w in self.windows:
            w.total_count += 1
            if not success:
                w.error_count += 1
            if w.total_count > 0:
                error_budget_pct = (100.0 - self.slo_pct) / 100.0
                w.current_burn_rate = (
                    (w.error_count / w.total_count) / error_budget_pct if error_budget_pct > 0 else 0.0
                )

    def alerts(self) -> list[str]:
        return [
            f"{w.name} burn rate {w.current_burn_rate:.1f}x > {w.target_burn_rate}x"
            for w in self.windows
            if w.current_burn_rate > w.target_burn_rate
        ]
