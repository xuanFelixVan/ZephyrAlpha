# [BLUEPRINT] MOD-014 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.sla.sla_monitor
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.shared.io.paths; zephyr.shared.event_bus
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
import logging
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)

# P3-24: SLA 目标从 YAML 加载（SSoT），fallback 到硬编码默认值
_SLA_CONFIG_PATH: Path = REPO_ROOT / "config" / "sla_targets.yaml"

_RTO_TARGET_S_DEFAULT = 300
_RPO_TARGET_TASKS_DEFAULT = 1


def _load_sla_targets() -> tuple[int, int]:
    """从 config/sla_targets.yaml 加载 RTO/RPO 目标，失败时 fallback 到默认值。"""
    try:
        import yaml

        if not _SLA_CONFIG_PATH.exists():
            return _RTO_TARGET_S_DEFAULT, _RPO_TARGET_TASKS_DEFAULT
        data = yaml.safe_load(_SLA_CONFIG_PATH.read_text(encoding="utf-8"))
        targets = data.get("targets", {}) if isinstance(data, dict) else {}
        rto = int(targets.get("rto_target_s", _RTO_TARGET_S_DEFAULT))
        rpo = int(targets.get("rpo_target_tasks", _RPO_TARGET_TASKS_DEFAULT))
        return rto, rpo
    except Exception:
        logger.debug("SLA targets YAML load failed, using defaults", exc_info=True)
        return _RTO_TARGET_S_DEFAULT, _RPO_TARGET_TASKS_DEFAULT


RTO_TARGET_S, RPO_TARGET_TASKS = _load_sla_targets()


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
        # P1-9 修复：相对路径改为 REPO_ROOT 锚定（禁止相对路径硬约束）
        self._data_dir = data_dir or (REPO_ROOT / "data" / "sla")
        self._breach_log_path = self._data_dir / "sla_breaches.jsonl"
        self._rto_samples: list[float] = []
        self._rpo_counts: list[int] = []
        self._subscribed = False
        self._recovery_start_time: float | None = None

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

    # ── P1-9 修复：事件驱动订阅（替代被动手动调用）──────────────────

    def subscribe_eventbus(self) -> None:
        """订阅 EventBusBackpressure 事件，实现自动 SLA 记录。

        幂等：重复调用安全。订阅事件：
        - pipeline_failed / kill_switch_triggered: 记录恢复开始时间（RTO 计时起点）
        - rollback_completed: 记录 RTO/RPO（恢复完成）
        """
        if self._subscribed:
            return
        try:
            from zephyr.shared.event_bus import bus

            bus.subscribe("pipeline_failed", self._on_recovery_start)
            bus.subscribe("kill_switch_triggered", self._on_recovery_start)
            bus.subscribe("rollback_completed", self._on_recovery_completed)
            self._subscribed = True
            logger.info(
                "SLAMonitor: subscribed to 3 events "
                "(pipeline_failed/kill_switch_triggered/rollback_completed)"
            )
        except Exception as e:
            logger.warning("SLAMonitor: subscribe_eventbus failed: %s", e, exc_info=True)

    def _on_recovery_start(self, payload: object) -> None:
        """失败事件触发：记录恢复开始时间（RTO 计时起点）。轻量handler。"""
        self._recovery_start_time = time.time()
        logger.debug("SLAMonitor: recovery timer started")

    def _on_recovery_completed(self, payload: object) -> None:
        """rollback_completed 事件：记录 RTO/RPO（恢复完成）。轻量handler。"""
        if self._recovery_start_time is None:
            logger.debug("SLAMonitor: rollback_completed without prior failure event, skipping")
            return
        try:
            data = payload if isinstance(payload, dict) else {}
            lost_tasks = int(data.get("lost_tasks", 0))
            self.record_recovery(self._recovery_start_time, lost_tasks=lost_tasks)
            logger.info(
                "SLAMonitor: recovery recorded via rollback_completed event (RTO/RPO measured)"
            )
        except Exception as e:
            logger.warning("SLAMonitor: _on_recovery_completed failed: %s", e, exc_info=True)
        finally:
            self._recovery_start_time = None
