# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.trend_analyzer
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES] zephyr.governance.persistence.sqlite_schema
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; src/zephyr/governance/drift_detection/_analysis.py; tests/audit/test_trend_analyzer.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 趋势数据不可篡改
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_trend_analyzer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Trend Analyzer — trend_analyzer.py





module_id: MOD-INF-023


时序存储与趋势分析：drift_velocity/resolution_rate/MTTR/fp_ratio + 3种trend_alert。


对标 blueprint.md §5.1 / TASK-INF-0025 / D-023-08。"""

from __future__ import annotations
from zephyr.shared.io.serialization import dumps

import os
import sqlite3
from zephyr.governance.persistence.sqlite_schema import get_db_connection
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from zephyr.shared.io.paths import DB_PATH


@dataclass
class TrendMetrics:
    module_id: str

    drift_velocity: float = 0.0

    resolution_rate: float = 0.0

    mean_time_to_resolve_hours: float = 0.0

    detector_fp_ratio: dict[str, float] = field(default_factory=dict)

    computed_at: str = ""


@dataclass
class TrendAlert:
    module_id: str

    alert_type: str

    severity: str

    detail: str


class TrendAnalyzer:
    VELOCITY_THRESHOLD: int = 5

    RESOLUTION_RATE_THRESHOLD: float = 0.5

    MTTR_THRESHOLD_DAYS: int = 7

    FP_RATIO_THRESHOLD: float = 0.3

    HOT_DATA_DAYS: int = 90

    def __init__(self, project_root: str | None = None) -> None:
        if project_root is None:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

        self._project_root = project_root

        self._db_dir = os.path.join(project_root, "data", "drift_audit")

        os.makedirs(self._db_dir, exist_ok=True)

        self._db_path = str(DB_PATH)

        self._archive_dir = os.path.join(self._db_dir, "archive")

        os.makedirs(self._archive_dir, exist_ok=True)

    def compute_metrics(self, module_id: str) -> TrendMetrics:
        conn = get_db_connection(self._db_path)

        try:
            now = datetime.now(UTC)

            week_ago = (now - timedelta(days=7)).isoformat()

            month_ago = (now - timedelta(days=30)).isoformat()

            velocity = conn.execute(
                "SELECT COUNT(*) FROM drift_events WHERE module_id=? AND created_at>? AND state!='FALSE_POSITIVE'",
                (module_id, week_ago),
            ).fetchone()[0]

            total = conn.execute(
                "SELECT COUNT(*) FROM drift_events WHERE module_id=? AND created_at>?",
                (module_id, month_ago),
            ).fetchone()[0]

            resolved = conn.execute(
                "SELECT COUNT(*) FROM drift_events WHERE module_id=? AND state='VERIFIED' AND updated_at>?",
                (module_id, month_ago),
            ).fetchone()[0]

            res_rate = resolved / total if total > 0 else 1.0

            mttr_hours = 0.0

            rows = conn.execute(
                "SELECT created_at, updated_at FROM drift_events WHERE module_id=? AND state='VERIFIED' AND created_at>?",
                (module_id, month_ago),
            ).fetchall()

            if rows:
                total_h = 0.0

                for created, updated in rows:
                    try:
                        c = datetime.fromisoformat(created)

                        u = datetime.fromisoformat(updated)

                        total_h += (u - c).total_seconds() / 3600

                    except (ValueError, TypeError):
                        pass

                mttr_hours = total_h / len(rows)

            fp_ratios: dict[str, float] = {}

            rows = conn.execute(
                "SELECT detector_id, COUNT(*) as total, SUM(CASE WHEN state='FALSE_POSITIVE' THEN 1 ELSE 0 END) as fp "
                "FROM drift_events WHERE module_id=? AND created_at>? GROUP BY detector_id",
                (module_id, month_ago),
            ).fetchall()

            for det_id, t, fp in rows:
                fp_ratios[det_id] = fp / t if t > 0 else 0.0

            return TrendMetrics(
                module_id=module_id,
                drift_velocity=float(velocity),
                resolution_rate=res_rate,
                mean_time_to_resolve_hours=mttr_hours,
                detector_fp_ratio=fp_ratios,
                computed_at=datetime.now(UTC).isoformat(),
            )
        finally:
            # 5.49.2 修复：异常路径确保连接归还
            conn.close()

    def check_trend_alerts(self, module_id: str) -> list[TrendAlert]:
        metrics = self.compute_metrics(module_id)

        alerts: list[TrendAlert] = []

        if metrics.drift_velocity > self.VELOCITY_THRESHOLD:
            alerts.append(
                TrendAlert(
                    module_id=module_id,
                    alert_type="spike",
                    severity="WARNING",
                    detail=f"Velocity {metrics.drift_velocity}/week exceeds {self.VELOCITY_THRESHOLD}",
                )
            )

        if metrics.resolution_rate < self.RESOLUTION_RATE_THRESHOLD:
            alerts.append(
                TrendAlert(
                    module_id=module_id,
                    alert_type="resolution_rate",
                    severity="WARNING",
                    detail=f"Resolution rate {metrics.resolution_rate:.1%} < {self.RESOLUTION_RATE_THRESHOLD:.0%}",
                )
            )

        if metrics.mean_time_to_resolve_hours > self.MTTR_THRESHOLD_DAYS * 24:
            alerts.append(
                TrendAlert(
                    module_id=module_id,
                    alert_type="MTTR",
                    severity="HIGH",
                    detail=f"MTTR {metrics.mean_time_to_resolve_hours:.0f}h > {self.MTTR_THRESHOLD_DAYS}d",
                )
            )

        for det_id, fp_rate in metrics.detector_fp_ratio.items():
            if fp_rate > self.FP_RATIO_THRESHOLD:
                alerts.append(
                    TrendAlert(
                        module_id=module_id,
                        alert_type="fp_ratio",
                        severity="MEDIUM",
                        detail=f"Detector {det_id} FP rate {fp_rate:.1%} > {self.FP_RATIO_THRESHOLD:.0%}",
                    )
                )

        return alerts

    def archive_old_data(self) -> None:
        conn = get_db_connection(self._db_path)

        cutoff = (datetime.now(UTC) - timedelta(days=self.HOT_DATA_DAYS)).isoformat()

        rows = conn.execute(
            "SELECT event_id, module_id, detector_id, drift_dimension, baseline_version, state, created_at, updated_at, resolved_by, resolution_detail, auto_fixed, rollback_verified FROM drift_events WHERE created_at < ?",
            (cutoff,),
        ).fetchall()

        if rows:
            year = datetime.now(UTC).strftime("%Y")

            archive_path = os.path.join(self._archive_dir, f"drift_{year}.jsonl")

            with open(archive_path, "a", encoding="utf-8") as fh:
                for row in rows:
                    record = {
                        "event_id": row[0],
                        "module_id": row[1],
                        "detector_id": row[2],
                        "drift_dimension": row[3],
                        "baseline_version": row[4],
                        "state": row[5],
                        "created_at": row[6],
                        "updated_at": row[7],
                        "resolved_by": row[8],
                        "resolution_detail": row[9],
                        "auto_fixed": row[10],
                        "rollback_verified": row[11],
                    }

                    fh.write(dumps(record, ensure_ascii=False) + "\n")

            conn.execute("DELETE FROM drift_events WHERE created_at < ?", (cutoff,))

        conn.commit()

        conn.close()
