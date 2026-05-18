# [BLUEPRINT] MOD-INF-033 | 03_modules/_cross_layer/behavioral-auditor/blueprint.md | §

# [MODULE] zephyr.behavioral_auditor.dashboard

# [INVARIANTS] 仪表板数据只读

# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__

# [CONSUMERS] drift_engine;detector_dispatcher;alert_router

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] DriftError;BaselineError

# [TESTS] tests/behavioral_auditor/

"""
Coverage Dashboard — dashboard.py





module_id: MOD-INF-023


覆盖率仪表板：detector_coverage_matrix / module_health_index / drift_heatmap + MCP JSON导出。


对标 blueprint.md §5.3 / TASK-INF-0027。"""



from __future__ import annotations





import json


import sqlite3


import os


from dataclasses import dataclass, field


from datetime import datetime, timezone


from pathlib import Path


from typing import Optional








@dataclass


class DashboardData:


    coverage_matrix: dict[str, dict[str, object]] = field(default_factory=dict)


    module_health_index: dict[str, float] = field(default_factory=dict)


    drift_heatmap: list[dict[str, object]] = field(default_factory=list)


    generated_at: str = ""








class Dashboard:





    def __init__(self, project_root: Optional[str] = None) -> None:


        if project_root is None:


            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


        self._project_root = project_root


        self._db_path = os.path.join(project_root, "data", "drift_audit", "drift_events.db")


        self._registry_path = os.path.join(os.path.dirname(__file__), "_detector_registry.yaml")





    def _load_coverage_matrix(self) -> dict[str, dict[str, object]]:


        import yaml


        if not os.path.exists(self._registry_path):


            return {}


        with open(self._registry_path, "r", encoding="utf-8") as fh:


            raw = yaml.safe_load(fh) or {}


        return raw.get("coverage_matrix", {}) or {}





    def compute_module_health(self) -> dict[str, float]:


        if not os.path.exists(self._db_path):


            return {}


        conn = sqlite3.connect(self._db_path)


        rows = conn.execute(


            "SELECT module_id, COUNT(*) as total, SUM(CASE WHEN state='VERIFIED' THEN 1 ELSE 0 END) as resolved FROM drift_events GROUP BY module_id"


        ).fetchall()


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


        conn = sqlite3.connect(self._db_path)


        rows = conn.execute(


            "SELECT date(created_at) as day, module_id, COUNT(*) as cnt FROM drift_events GROUP BY day, module_id ORDER BY day"


        ).fetchall()


        conn.close()


        return [{"date": day, "module_id": mod, "count": cnt} for day, mod, cnt in rows]





    def generate(self) -> DashboardData:


        return DashboardData(


            coverage_matrix=self._load_coverage_matrix(),


            module_health_index=self.compute_module_health(),


            drift_heatmap=self.compute_drift_heatmap(),


            generated_at=datetime.now(timezone.utc).isoformat(),


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


