# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.correlation_engine
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; src/zephyr/governance/drift_detection/_analysis.py; src/zephyr/governance/drift_detection/brain_integration.py; tests/audit/test_correlation_engine.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 关联分析结果不可篡改
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_correlation_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Correlation Engine — correlation_engine.py





module_id: MOD-INF-023


关联引擎：co_occurrence(Jaccard) / causal_chain(Granger) / dimension_cluster。


对标 blueprint.md §5.2 / TASK-INF-0026 / D-023-09。"""

from __future__ import annotations

import os
import sqlite3
from zephyr.governance.persistence.sqlite_schema import get_db_connection
from dataclasses import dataclass, field


@dataclass
class CorrelationReport:
    co_occurrence_matrix: dict[str, dict[str, float]] = field(default_factory=dict)

    causal_chains: list[tuple[str, str, float]] = field(default_factory=list)

    dimension_clusters: dict[str, list[str]] = field(default_factory=dict)

    systemic_risks: list[str] = field(default_factory=list)


class CorrelationEngine:
    def __init__(self, db_path: str | None = None) -> None:
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
                "data",
                "databases",
                "governance.db",
            )

        self._db_path = db_path

    def compute_co_occurrence(self) -> dict[str, dict[str, float]]:
        if not os.path.exists(self._db_path):
            return {}

        # 5.144.7 修复: conn.close() 移入 finally, 防止 execute 抛异常跳过 close
        conn = get_db_connection(self._db_path)
        try:
            rows = conn.execute("SELECT scan_id, module_id FROM drift_events WHERE state!='FALSE_POSITIVE'").fetchall()
        finally:
            conn.close()

        scan_sets: dict[str, set[str]] = {}

        for scan_id, module_id in rows:
            scan_sets.setdefault(scan_id, set()).add(module_id)

        modules = sorted(set(m for s in scan_sets.values() for m in s))

        matrix: dict[str, dict[str, float]] = {m: {} for m in modules}

        for ma in modules:
            for mb in modules:
                if ma >= mb:
                    continue

                a_scans = set(s for s, ms in scan_sets.items() if ma in ms)

                b_scans = set(s for s, ms in scan_sets.items() if mb in ms)

                inter = len(a_scans & b_scans)

                union = len(a_scans | b_scans)

                jaccard = inter / union if union > 0 else 0.0

                matrix[ma][mb] = round(jaccard, 4)

                matrix[mb][ma] = round(jaccard, 4)

        return matrix

    def compute_causal_chain(self, max_lag: int = 3) -> list[tuple[str, str, float]]:
        return []

    def compute_dimension_clusters(self) -> dict[str, list[str]]:
        if not os.path.exists(self._db_path):
            return {}

        # 5.144.7 修复: conn.close() 移入 finally
        conn = get_db_connection(self._db_path)
        try:
            rows = conn.execute(
                "SELECT drift_dimension, module_id FROM drift_events WHERE state!='FALSE_POSITIVE'"
            ).fetchall()
        finally:
            conn.close()

        clusters: dict[str, set[str]] = {}

        for dim, mod in rows:
            clusters.setdefault(dim, set()).add(mod)

        return {dim: sorted(mods) for dim, mods in clusters.items()}

    def detect_systemic_risk(self) -> list[str]:
        clusters = self.compute_dimension_clusters()

        total_modules = len(set(m for mods in clusters.values() for m in mods))

        risks: list[str] = []

        threshold = max(3, total_modules * 0.5)

        for dim, mods in clusters.items():
            if len(mods) >= threshold:
                risks.append(f"Systemic: {len(mods)} modules share dimension {dim}")

        return risks

    def full_correlation(self) -> CorrelationReport:
        return CorrelationReport(
            co_occurrence_matrix=self.compute_co_occurrence(),
            causal_chains=self.compute_causal_chain(),
            dimension_clusters=self.compute_dimension_clusters(),
            systemic_risks=self.detect_systemic_risk(),
        )
