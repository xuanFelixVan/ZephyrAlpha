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

# S5: drift 持续监控 SQL（§5.160.2 NO-BARE-SQL gate 合规）
# 数据源：drift_scan_results（S1 写入）、drift_audit_findings（S2 写入）
SQL_DRIFT_TREND = (
    "SELECT scan_time, total_drifts, high_count, low_count, auto_fixable "
    "FROM drift_scan_results ORDER BY scan_time DESC LIMIT 50"
)
SQL_LATEST_SCAN = (
    "SELECT total_drifts, high_count, low_count, auto_fixable "
    "FROM drift_scan_results ORDER BY scan_time DESC LIMIT 1"
)
SQL_TOTAL_SCANS = "SELECT COUNT(*) FROM drift_scan_results"
SQL_SUM_AUTO_FIXABLE = "SELECT COALESCE(SUM(auto_fixable), 0) FROM drift_scan_results"
SQL_SUM_TOTAL_DRIFTS = "SELECT COALESCE(SUM(total_drifts), 0) FROM drift_scan_results"
SQL_OPEN_FINDINGS = "SELECT COUNT(*) FROM drift_audit_findings WHERE status = 'open'"
SQL_FINDINGS_BY_TYPE = (
    "SELECT drift_type, severity, COUNT(*) as cnt "
    "FROM drift_audit_findings WHERE status = 'open' "
    "GROUP BY drift_type, severity ORDER BY cnt DESC"
)


@dataclass
class DashboardData:
    coverage_matrix: dict[str, dict[str, object]] = field(default_factory=dict)

    module_health_index: dict[str, float] = field(default_factory=dict)

    drift_heatmap: list[dict[str, object]] = field(default_factory=list)

    # S5: drift 持续监控字段（MOD-GOV-ALIGNMENT-LOOP §4.S5）
    drift_trend: list[dict[str, object]] = field(default_factory=list)

    auto_fix_stats: dict[str, object] = field(default_factory=dict)

    drift_distribution: dict[str, object] = field(default_factory=dict)

    manual_interventions: int = 0

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

    # ------------------------------------------------------------------
    # S5: drift 持续监控（MOD-GOV-ALIGNMENT-LOOP §4.S5）
    # 数据源：drift_scan_results（S1）、drift_audit_findings（S2）
    # ------------------------------------------------------------------

    def _query_governance_db(self, sql: str, params: tuple = ()) -> list[tuple]:
        """安全查询 governance.db，表不存在时返回空列表。"""
        if not os.path.exists(self._db_path):
            return []
        conn = get_db_connection(self._db_path)
        try:
            cur = conn.execute(sql, params)
            return cur.fetchall()
        except sqlite3.OperationalError:
            # 表不存在（S1/S2 未运行过）
            return []
        finally:
            conn.close()

    def compute_drift_trend(self) -> list[dict[str, object]]:
        """drift 数量趋势（最近 50 次扫描的时间序列）。"""
        rows = self._query_governance_db(SQL_DRIFT_TREND)
        return [
            {
                "scan_time": row[0],
                "total_drifts": row[1],
                "high_count": row[2],
                "low_count": row[3],
                "auto_fixable": row[4],
            }
            for row in reversed(rows)  # 反转为时间正序
        ]

    def compute_auto_fix_stats(self) -> dict[str, object]:
        """自动修复成功率（auto_fixable 总数 / total_drifts 总数）。"""
        rows = self._query_governance_db(SQL_LATEST_SCAN)
        if not rows:
            return {"total_scans": 0, "auto_fixable_total": 0, "success_rate": 0.0}
        total_scans_row = self._query_governance_db(SQL_TOTAL_SCANS)
        auto_sum_row = self._query_governance_db(SQL_SUM_AUTO_FIXABLE)
        total_scans = total_scans_row[0][0] if total_scans_row else 0
        auto_fixable_sum = auto_sum_row[0][0] if auto_sum_row else 0
        # 从 latest scan 取当前状态
        latest_total, latest_high, latest_low, latest_auto = rows[0]
        # 成功率 = auto_fixable / total_drifts（基于历史累计）
        drift_total_row = self._query_governance_db(SQL_SUM_TOTAL_DRIFTS)
        drift_total = drift_total_row[0][0] if drift_total_row else 0
        success_rate = round(auto_fixable_sum / drift_total, 4) if drift_total > 0 else 0.0
        return {
            "total_scans": total_scans,
            "drift_total": drift_total,
            "auto_fixable_total": auto_fixable_sum,
            "success_rate": success_rate,
            "latest": {
                "total_drifts": latest_total,
                "high_count": latest_high,
                "low_count": latest_low,
                "auto_fixable": latest_auto,
            },
        }

    def compute_drift_distribution(self) -> dict[str, object]:
        """各类 drift 分布（最新扫描的 HIGH/LOW 分布）。"""
        rows = self._query_governance_db(SQL_LATEST_SCAN)
        if not rows:
            return {"high": 0, "low": 0}
        total, high, low, auto_fixable = rows[0]
        return {
            "high": high,
            "low": low,
            "total": total,
            "auto_fixable": auto_fixable,
            "manual_required": total - auto_fixable if total else 0,
        }

    def compute_manual_interventions(self) -> int:
        """人工干预次数（未关闭的 audit findings 数）。"""
        rows = self._query_governance_db(SQL_OPEN_FINDINGS)
        return rows[0][0] if rows else 0

    def generate(self) -> DashboardData:
        return DashboardData(
            coverage_matrix=self._load_coverage_matrix(),
            module_health_index=self.compute_module_health(),
            drift_heatmap=self.compute_drift_heatmap(),
            drift_trend=self.compute_drift_trend(),
            auto_fix_stats=self.compute_auto_fix_stats(),
            drift_distribution=self.compute_drift_distribution(),
            manual_interventions=self.compute_manual_interventions(),
            generated_at=datetime.now(UTC).isoformat(),
        )

    def to_json_summary(self) -> str:
        data = self.generate()

        summary = {
            "coverage_dimensions": len(data.coverage_matrix),
            "modules": len(data.module_health_index),
            "health_index": data.module_health_index,
            "drift_trend": data.drift_trend,
            "auto_fix_stats": data.auto_fix_stats,
            "drift_distribution": data.drift_distribution,
            "manual_interventions": data.manual_interventions,
            "generated_at": data.generated_at,
        }

        return json.dumps(summary, ensure_ascii=False)

    def to_cli_table(self) -> str:
        data = self.generate()

        lines = ["Module Health Index", "-" * 60]

        for mod, score in sorted(data.module_health_index.items()):
            bar = "█" * int(score * 20)

            lines.append(f"  {mod:.<30} {score:.2f} {bar}")

        # S5: drift 持续监控摘要
        stats = data.auto_fix_stats
        dist = data.drift_distribution
        if stats.get("total_scans", 0) > 0:
            lines.append("")
            lines.append("Drift Monitoring (S5)")
            lines.append("-" * 60)
            lines.append(f"  Total scans:          {stats['total_scans']}")
            lines.append(f"  Total drifts:         {stats['drift_total']}")
            lines.append(f"  Auto-fixable:         {stats['auto_fixable_total']}")
            lines.append(f"  Auto-fix success rate: {stats['success_rate']:.1%}")
            lines.append(f"  Latest HIGH/LOW:      {dist['high']}/{dist['low']}")
            lines.append(f"  Manual interventions: {data.manual_interventions}")

        return "\n".join(lines)
