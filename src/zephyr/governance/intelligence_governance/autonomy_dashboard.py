# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.intelligence_governance.autonomy_dashboard
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.intelligence_governance.__init__
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
# [A_module] module_id=MOD-INF_autonomy_dashboard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Autonomy Dashboard — AI 自主感知健康仪表。

依据：
    蓝图 MOD-INF-021 §6.15 B94 + 决策 D-021-25
    任务卡 TASK-INF-0262

功能：
    - autonomy_dashboard 实时指标：success/intervention/fp/token/RTO
    - health < 0.3 连续 5 分钟 -> autonomy_downgrade
    - exit 35 (AUTONOMY_DOWNGRADED) + Owner 通知
    - 对标特斯拉 Autopilot disengagement 人工接管模式
"""

from __future__ import annotations

from typing import Final
import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

EXIT_AUTONOMY_DOWNGRADED: Final[int] = 35


@dataclass
class AutonomyMetrics:
    total_rollbacks: int = 0
    successful_rollbacks: int = 0
    failed_rollbacks: int = 0
    human_interventions: int = 0
    false_positives: int = 0
    total_token_cost: int = 0
    total_time_to_restore_ms: int = 0
    samples_since_reset: int = 0

    @property
    def success_rate(self) -> float:
        if self.total_rollbacks == 0:
            return 1.0
        return self.successful_rollbacks / self.total_rollbacks

    @property
    def intervention_rate(self) -> float:
        if self.total_rollbacks == 0:
            return 0.0
        return self.human_interventions / self.total_rollbacks

    @property
    def false_positive_rate(self) -> float:
        if self.total_rollbacks == 0:
            return 0.0
        return self.false_positives / self.total_rollbacks

    @property
    def avg_rto_ms(self) -> float:
        if self.samples_since_reset == 0:
            return 0.0
        return self.total_time_to_restore_ms / self.samples_since_reset


@dataclass
class HealthGauge:
    score: float
    success_weight: float = 0.35
    intervention_penalty: float = 0.30
    false_positive_penalty: float = 0.20
    rto_weight: float = 0.15
    tier: int = 2

    @classmethod
    def from_metrics(cls, metrics: AutonomyMetrics) -> HealthGauge:
        success_score = metrics.success_rate * cls.success_weight

        intervention_score = (1.0 - metrics.intervention_rate) * cls.intervention_penalty

        fp_score = (1.0 - metrics.false_positive_rate) * cls.false_positive_penalty

        rto_score = cls.rto_weight
        if metrics.avg_rto_ms > 0:
            rto_normalized = min(1.0, 30000.0 / max(metrics.avg_rto_ms, 1.0))
            rto_score = rto_normalized * cls.rto_weight

        score = success_score + intervention_score + fp_score + rto_score
        score = max(0.0, min(1.0, score))

        if score > 0.8:
            tier = 2
        elif score > 0.5:
            tier = 1
        else:
            tier = 0

        return cls(score=score, tier=tier)


@dataclass
class DowngradeEvent:
    timestamp_utc: str
    from_tier: int
    to_tier: int
    health_score: float
    reason: str


class AutonomyDashboard:
    def __init__(self, data_dir: Path | None = None) -> None:
        self._data_dir = data_dir or Path("data/rollback/autonomy")
        self._metrics_path = self._data_dir / "autonomy_metrics.json"
        self._history_path = self._data_dir / "autonomy_history.jsonl"
        self._degradation_window_s = 300
        self._degradation_threshold = 0.3
        self._downgrade_events: list[DowngradeEvent] = []

    def record_rollback(self, success: bool, token_cost: int = 0, rto_ms: int = 0) -> AutonomyMetrics:
        metrics = self._load_metrics()

        metrics.total_rollbacks += 1
        metrics.samples_since_reset += 1

        if success:
            metrics.successful_rollbacks += 1
        else:
            metrics.failed_rollbacks += 1

        metrics.total_token_cost += token_cost
        metrics.total_time_to_restore_ms += rto_ms

        self._save_metrics(metrics)
        self._append_history(metrics)

        return metrics

    def record_intervention(self, reason: str = "") -> AutonomyMetrics:
        metrics = self._load_metrics()
        metrics.human_interventions += 1
        self._save_metrics(metrics)
        return metrics

    def record_false_positive(self) -> AutonomyMetrics:
        metrics = self._load_metrics()
        metrics.false_positives += 1
        self._save_metrics(metrics)
        return metrics

    def evaluate_health(self) -> HealthGauge:
        metrics = self._load_metrics()
        gauge = HealthGauge.from_metrics(metrics)
        self._check_degradation(gauge)
        return gauge

    def get_dashboard_report(self) -> dict[str, Any]:
        metrics = self._load_metrics()
        gauge = self.evaluate_health()

        return {
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "health_score": round(gauge.score, 4),
            "autonomy_tier": gauge.tier,
            "tier_description": self._tier_description(gauge.tier),
            "metrics": {
                "total_rollbacks": metrics.total_rollbacks,
                "success_rate": round(metrics.success_rate, 4),
                "intervention_rate": round(metrics.intervention_rate, 4),
                "false_positive_rate": round(metrics.false_positive_rate, 4),
                "total_token_cost": metrics.total_token_cost,
                "avg_rto_ms": round(metrics.avg_rto_ms, 1),
            },
            "downgrade_events_recent": [
                {
                    "timestamp": e.timestamp_utc,
                    "from_tier": e.from_tier,
                    "to_tier": e.to_tier,
                    "reason": e.reason,
                }
                for e in self._downgrade_events[-5:]
            ],
            "exit_code": EXIT_AUTONOMY_DOWNGRADED if gauge.tier == 0 else 0,
        }

    def render_dashboard_markdown(self) -> str:
        report = self.get_dashboard_report()
        m = report["metrics"]

        lines = [
            "# Autonomy Dashboard",
            "",
            f"**Health Score**: {report['health_score']:.2f} | **Tier**: {report['autonomy_tier']}",
            f"**Status**: {report['tier_description']}",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Total Rollbacks | {m['total_rollbacks']} |",
            f"| Success Rate | {m['success_rate']:.2%} |",
            f"| Intervention Rate | {m['intervention_rate']:.2%} |",
            f"| False Positive Rate | {m['false_positive_rate']:.2%} |",
            f"| Total Token Cost | {m['total_token_cost']:,} |",
            f"| Avg RTO (ms) | {m['avg_rto_ms']:.0f} |",
            "",
            "---",
            "",
            "### Tier Map",
            "",
            "| Tier | Health Range | Capability |",
            "|------|-------------|------------|",
            "| 2 | > 0.8 | Auto-revert (full autonomy) |",
            "| 1 | 0.5 - 0.8 | Propose-only (supervised) |",
            "| 0 | < 0.5 | Read-only + human escalation |",
        ]

        return "\n".join(lines)

    def reset_metrics(self) -> None:
        self._save_metrics(AutonomyMetrics())

    def _check_degradation(self, gauge: HealthGauge) -> None:
        recent_history = self._load_recent_history(timedelta(seconds=self._degradation_window_s))

        if len(recent_history) < 2:
            return

        low_health_count = sum(
            1 for h in recent_history if HealthGauge.from_metrics(h).score < self._degradation_threshold
        )

        if low_health_count >= len(recent_history):
            previous_tier = self._get_current_tier_from_history(recent_history[:-1])
            if gauge.tier < previous_tier:
                event = DowngradeEvent(
                    timestamp_utc=datetime.now(UTC).isoformat(),
                    from_tier=previous_tier,
                    to_tier=gauge.tier,
                    health_score=gauge.score,
                    reason=f"Health < {self._degradation_threshold} for {self._degradation_window_s}s",
                )
                self._downgrade_events.append(event)

    def _load_metrics(self) -> AutonomyMetrics:
        if not self._metrics_path.exists():
            return AutonomyMetrics()
        try:
            data = json.loads(self._metrics_path.read_text(encoding="utf-8"))
            return AutonomyMetrics(
                total_rollbacks=data.get("total_rollbacks", 0),
                successful_rollbacks=data.get("successful_rollbacks", 0),
                failed_rollbacks=data.get("failed_rollbacks", 0),
                human_interventions=data.get("human_interventions", 0),
                false_positives=data.get("false_positives", 0),
                total_token_cost=data.get("total_token_cost", 0),
                total_time_to_restore_ms=data.get("total_time_to_restore_ms", 0),
                samples_since_reset=data.get("samples_since_reset", 0),
            )
        except (json.JSONDecodeError, KeyError):
            return AutonomyMetrics()

    def _save_metrics(self, metrics: AutonomyMetrics) -> None:
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._metrics_path.write_text(
            json.dumps(
                {
                    "total_rollbacks": metrics.total_rollbacks,
                    "successful_rollbacks": metrics.successful_rollbacks,
                    "failed_rollbacks": metrics.failed_rollbacks,
                    "human_interventions": metrics.human_interventions,
                    "false_positives": metrics.false_positives,
                    "total_token_cost": metrics.total_token_cost,
                    "total_time_to_restore_ms": metrics.total_time_to_restore_ms,
                    "samples_since_reset": metrics.samples_since_reset,
                    "last_updated": datetime.now(UTC).isoformat(),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def _append_history(self, metrics: AutonomyMetrics) -> None:
        self._data_dir.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "total_rollbacks": metrics.total_rollbacks,
            "success_rate": metrics.success_rate,
            "intervention_rate": metrics.intervention_rate,
            "false_positive_rate": metrics.false_positive_rate,
            "token_cost": metrics.total_token_cost,
            "avg_rto_ms": metrics.avg_rto_ms,
        }
        with open(self._history_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def _load_recent_history(self, window: timedelta) -> list[AutonomyMetrics]:
        cutoff = datetime.now(UTC) - window
        recent: list[AutonomyMetrics] = []

        if not self._history_path.exists():
            return recent

        try:
            for line in self._history_path.read_text(encoding="utf-8").strip().split("\n"):
                if not line:
                    continue
                entry = json.loads(line)
                ts = datetime.fromisoformat(entry["timestamp_utc"])
                if ts >= cutoff:
                    recent.append(
                        AutonomyMetrics(
                            total_rollbacks=entry.get("total_rollbacks", 0),
                            successful_rollbacks=int(entry.get("total_rollbacks", 0) * entry.get("success_rate", 1.0)),
                        )
                    )
        except (json.JSONDecodeError, ValueError):
            pass

        return recent

    def _get_current_tier_from_history(self, history: list[AutonomyMetrics]) -> int:
        if not history:
            return 2
        last = history[-1]
        gauge = HealthGauge.from_metrics(last)
        return gauge.tier

    @staticmethod
    def _tier_description(tier: int) -> str:
        if tier == 2:
            return "FULL_AUTONOMY — auto-revert enabled"
        if tier == 1:
            return "SUPERVISED — propose-only, human confirmation required"
        return "READ_ONLY — autonomy suspended, human escalation mandatory"
