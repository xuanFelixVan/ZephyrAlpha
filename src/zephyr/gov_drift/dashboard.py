# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.dashboard
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; src/zephyr/gov_drift/_infrastructure.py; tests/ba/test_ba_dashboard.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 仪表板数据只读
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_dashboard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Coverage Dashboard — dashboard.py


覆盖率仪表板：detector_coverage_matrix / module_health_index / drift_heatmap + MCP JSON导出。


对标 blueprint.md §5.3 / TASK-INF-0027。"""

from __future__ import annotations

import json
import os
import sqlite3
from zephyr.governance.persistence.sqlite_schema import get_db_connection
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class DashboardData:
    coverage_matrix: dict[str, dict[str, object]] = field(default_factory=dict)

    module_health_index: dict[str, float] = field(default_factory=dict)

    drift_heatmap: list[dict[str, object]] = field(default_factory=list)

    generated_at: str = ""


class Dashboard:
    def __init__(self, project_root: str | None = None) -> None:
        if project_root is None:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

        self._project_root = project_root

        self._db_path = os.path.join(project_root, "data", "databases", "governance.db")

        self._registry_path = os.path.join(os.path.dirname(__file__), "_detector-registry.yaml")

    def _load_coverage_matrix(self) -> dict[str, dict[str, object]]:
        import yaml

        if not os.path.exists(self._registry_path):
            return {}

        with open(self._registry_path, encoding="utf-8") as fh:
            raw = yaml.safe_load(fh) or {}

        return raw.get("coverage_matrix", {}) or {}

    def compute_module_health(self) -> dict[str, float]:
        if not os.path.exists(self._db_path):
            return {}

        # 5.144.8 修复: conn.close() 移入 finally
        conn = get_db_connection(self._db_path)
        try:
            rows = conn.execute(
                "SELECT module_id, COUNT(*) as total, SUM(CASE WHEN state='VERIFIED' THEN 1 ELSE 0 END) as resolved FROM drift_events GROUP BY module_id"
            ).fetchall()
        finally:
            conn.close()

        health: dict[str, float] = {}

        for mod, total, resolved in rows:
            res_rate = resolved / total if total > 0 else 1.0

            raw = min(1.0, max(0.0, res_rate - (total * 0.02)))

            health[mod] = round(raw, 4)

        return health

    def compute_drift_heatmap(self) -> list[dict[str, object]]:
        if not os.path.exists(self._db_path):
            return []

        # 5.144.8 修复: conn.close() 移入 finally
        conn = get_db_connection(self._db_path)
        try:
            rows = conn.execute(
                "SELECT date(created_at) as day, module_id, COUNT(*) as cnt FROM drift_events GROUP BY day, module_id ORDER BY day"
            ).fetchall()
        finally:
            conn.close()

        return [{"date": day, "module_id": mod, "count": cnt} for day, mod, cnt in rows]

    def generate(self) -> DashboardData:
        return DashboardData(
            coverage_matrix=self._load_coverage_matrix(),
            module_health_index=self.compute_module_health(),
            drift_heatmap=self.compute_drift_heatmap(),
            generated_at=datetime.now(UTC).isoformat(),
        )

    def to_json_summary(self) -> str:
        data = self.generate()

        summary = {
            "coverage_dimensions": len(data.coverage_matrix),
            "modules": len(data.module_health_index),
            "health_index": data.module_health_index,
            "generated_at": data.generated_at,
        }

        return json.dumps(summary, ensure_ascii=False)

    def to_cli_table(self) -> str:
        data = self.generate()

        lines = ["Module Health Index", "-" * 60]

        for mod, score in sorted(data.module_health_index.items()):
            bar = "█" * int(score * 20)

            lines.append(f"  {mod:.<30} {score:.2f} {bar}")

        return "\n".join(lines)
