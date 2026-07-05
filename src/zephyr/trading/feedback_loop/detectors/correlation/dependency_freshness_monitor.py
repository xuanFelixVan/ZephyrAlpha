# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.detectors.correlation.dependency_freshness_monitor
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.trading.feedback_loop.detectors.__init__
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
# [A_module] module_id=MOD-UNK_dependency_freshness_monitor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Dependency Freshness Monitor — v0.38.0 R474

Blindspot: Package dependencies age silently — security vulnerabilities accumulate,
deprecated APIs approach end-of-life, major version gaps widen. In 1-person+AI
maintenance, no one is actively tracking dependency health.

Risk: R474 — Supply chain attack via stale dependency; breaking change in updated
transient dependency; CVE unpatched for months because no one noticed.

Mitigation: Track dependency age, major version lag, and known CVE exposure.
Alert when any dependency exceeds freshness threshold. Integrate with CVE
scanner for vulnerability cross-referencing.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class FreshnessStatus(str, Enum):
    FRESH = "FRESH"
    AGING = "AGING"
    STALE = "STALE"
    CRITICAL = "CRITICAL"


@dataclass
class DependencyFreshnessMonitor:
    max_age_days: int = 180
    max_major_version_lag: int = 2
    cve_severity_threshold: str = "HIGH"

    dependencies: dict[str, dict] = field(default_factory=dict)
    freshness_alerts: list[dict] = field(default_factory=list)

    def register(
        self,
        package_name: str,
        current_version: str,
        latest_version: str,
        last_updated_ts: float,
        known_cves: list[str] | None = None,
    ) -> None:
        self.dependencies[package_name] = {
            "current": current_version,
            "latest": latest_version,
            "last_updated": last_updated_ts,
            "cves": known_cves or [],
        }

    def check_freshness(self) -> list[dict]:
        now = time.time()
        alerts = []

        for name, dep in self.dependencies.items():
            age_days = (now - dep["last_updated"]) / 86400.0

            current_major = int(dep["current"].split(".")[0]) if dep["current"] else 0
            latest_major = int(dep["latest"].split(".")[0]) if dep["latest"] else 0
            version_lag = latest_major - current_major

            has_critical_cve = len(dep.get("cves", [])) > 0

            if has_critical_cve or age_days > self.max_age_days * 2:
                status = FreshnessStatus.CRITICAL
            elif age_days > self.max_age_days or version_lag >= self.max_major_version_lag:
                status = FreshnessStatus.STALE
            elif age_days > self.max_age_days / 2:
                status = FreshnessStatus.AGING
            else:
                status = FreshnessStatus.FRESH

            if status != FreshnessStatus.FRESH:
                alert = {
                    "package": name,
                    "status": status.value,
                    "age_days": round(age_days, 1),
                    "version_lag": version_lag,
                    "current": dep["current"],
                    "latest": dep["latest"],
                    "cvss_count": len(dep.get("cves", [])),
                }
                alerts.append(alert)

        if alerts:
            self.freshness_alerts.extend(alerts)
        return alerts

    def get_stalest(self, top_n: int = 5) -> list[dict]:
        now = time.time()
        ranked = []
        for name, dep in self.dependencies.items():
            age = (now - dep["last_updated"]) / 86400.0
            ranked.append({"package": name, "age_days": round(age, 1), "cves": len(dep.get("cves", []))})
        ranked.sort(key=lambda x: (-x["cves"], -x["age_days"]))
        return ranked[:top_n]

    def overall_health_score(self) -> float:
        if not self.dependencies:
            return 1.0
        now = time.time()
        scores = []
        for dep in self.dependencies.values():
            age = (now - dep["last_updated"]) / 86400.0
            score = max(0, 1.0 - age / (self.max_age_days * 2))
            if dep.get("cves"):
                score *= 0.5
            scores.append(score)
        return round(sum(scores) / len(scores), 3)
