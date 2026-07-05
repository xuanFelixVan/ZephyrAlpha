# [BLUEPRINT] SRC-142 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.sla.sla_monitor
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_sla_monitor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
SLA Monitor — 服务等级协议 (SLA) 监控 RTO/RPO。

依据：
    蓝图 MOD-TASK_SYSTEM §6.10 + v0.6.0
    任务卡 TASK-INF-0115

RTO: Recovery Time Objective ≤ 300s
RPO: Recovery Point Objective ≤ 1 task
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

RTO_TARGET_S = 300
RPO_TARGET_TASKS = 1


@dataclass
class SLABreach:
    metric: str
    target: float
    actual: float
    timestamp_utc: str
    details: str = ""


@dataclass
class SLAReport:
    report_id: str
    rto_ms: float
    rto_ok: bool
    rpo_tasks: int
    rpo_ok: bool
    breaches: list[SLABreach]
    overall_ok: bool
    timestamp_utc: str


class SLAMonitor:
    def __init__(self, data_dir: Path | None = None) -> None:
        self._data_dir = data_dir or Path("data/sla")
        self._breach_log_path = self._data_dir / "sla_breaches.jsonl"
        self._rto_samples: list[float] = []
        self._rpo_counts: list[int] = []

    def record_rto(self, recovery_time_s: float) -> SLABreach | None:
        self._rto_samples.append(recovery_time_s)

        if recovery_time_s > RTO_TARGET_S:
            breach = SLABreach(
                metric="RTO",
                target=RTO_TARGET_S,
                actual=recovery_time_s,
                timestamp_utc=datetime.now(UTC).isoformat(),
                details=f"Recovery time {recovery_time_s:.1f}s exceeds target {RTO_TARGET_S}s",
            )
            self._log_breach(breach)
            return breach

        return None

    def record_rpo(self, lost_tasks: int) -> SLABreach | None:
        self._rpo_counts.append(lost_tasks)

        if lost_tasks > RPO_TARGET_TASKS:
            breach = SLABreach(
                metric="RPO",
                target=RPO_TARGET_TASKS,
                actual=lost_tasks,
                timestamp_utc=datetime.now(UTC).isoformat(),
                details=f"Lost {lost_tasks} tasks exceeds RPO target {RPO_TARGET_TASKS}",
            )
            self._log_breach(breach)
            return breach

        return None

    def record_recovery(self, start_time: float, lost_tasks: int = 0) -> SLAReport:
        recovery_time_s = time.time() - start_time

        rto_breach = self.record_rto(recovery_time_s)
        rpo_breach = self.record_rpo(lost_tasks)

        breaches: list[SLABreach] = []
        if rto_breach:
            breaches.append(rto_breach)
        if rpo_breach:
            breaches.append(rpo_breach)

        overall = len(breaches) == 0

        report = SLAReport(
            report_id=f"SLA-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}",
            rto_ms=round(recovery_time_s * 1000, 1),
            rto_ok=rto_breach is None,
            rpo_tasks=lost_tasks,
            rpo_ok=rpo_breach is None,
            breaches=breaches,
            overall_ok=overall,
            timestamp_utc=datetime.now(UTC).isoformat(),
        )

        self._save_report(report)

        return report

    def get_statistics(self) -> dict[str, Any]:
        avg_rto = sum(self._rto_samples) / max(len(self._rto_samples), 1)
        avg_rpo = sum(self._rpo_counts) / max(len(self._rpo_counts), 1)

        rto_compliance = sum(1 for s in self._rto_samples if s <= RTO_TARGET_S) / max(len(self._rto_samples), 1)
        rpo_compliance = sum(1 for c in self._rpo_counts if c <= RPO_TARGET_TASKS) / max(len(self._rpo_counts), 1)

        return {
            "avg_rto_s": round(avg_rto, 1),
            "rto_compliance": round(rto_compliance, 2),
            "avg_rpo_tasks": round(avg_rpo, 1),
            "rpo_compliance": round(rpo_compliance, 2),
            "total_samples": len(self._rto_samples),
        }

    def _log_breach(self, breach: SLABreach) -> None:
        self._data_dir.mkdir(parents=True, exist_ok=True)
        with open(self._breach_log_path, "a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "metric": breach.metric,
                        "target": breach.target,
                        "actual": breach.actual,
                        "timestamp_utc": breach.timestamp_utc,
                        "details": breach.details,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

    def _save_report(self, report: SLAReport) -> None:
        self._data_dir.mkdir(parents=True, exist_ok=True)
        report_path = self._data_dir / f"{report.report_id}.json"
        report_path.write_text(
            json.dumps(
                {
                    "report_id": report.report_id,
                    "rto_ms": report.rto_ms,
                    "rto_ok": report.rto_ok,
                    "rpo_tasks": report.rpo_tasks,
                    "rpo_ok": report.rpo_ok,
                    "breaches": [
                        {"metric": b.metric, "actual": b.actual, "details": b.details} for b in report.breaches
                    ],
                    "overall_ok": report.overall_ok,
                    "timestamp_utc": report.timestamp_utc,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
