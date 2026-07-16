# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain-frontend/hmi-core/blueprint.md
# [MODULE] zephyr.frontend.dashboard.app
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] zephyr.infra_ops.__init__; zephyr.shared.contracts.task_repository_protocol; zephyr.governance.persistence.task_repo; zephyr.governance.persistence.sqlite_schema
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L08-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# AI-generated: T-4-07 Streamlit Dashboard
"""
ZephyrAlpha Dashboard · Streamlit 仪表盘（已弃用 v3.1.0）
=========================================================

Task ID     : T-4-07
safety_level: L

**已弃用**：Streamlit 入口已弃用，请使用 Panel 主入口：
    panel serve src/zephyr/frontend/dashboard/app_panel.py --show --port 5006
    或: python src/zephyr/frontend/dashboard/app_panel.py

DashboardApp 类仍可被编程式使用（render_page 返回 dict 数据）。
"""

from __future__ import annotations

import sys
from typing import Any

from zephyr.frontend.dashboard.components.fitness_functions import (
    FitnessDashboardData,
    fetch_fitness_data,
    render_fitness_dashboard,
)
from zephyr.frontend.dashboard.components.gate_statistics import (
    GateStatisticsData,
    fetch_gate_statistics,
    render_gate_statistics,
)
from zephyr.frontend.dashboard.components.knowledge_overview import (
    KnowledgeOverviewData,
    fetch_knowledge_overview,
    render_knowledge_overview,
)
from zephyr.frontend.dashboard.components.olap_trend import (
    OLAPTrendData,
    fetch_olap_trends,
    render_olap_trends,
)
from zephyr.frontend.dashboard.components.task_progress import (
    TaskProgressData,
    fetch_task_progress,
    render_task_progress,
)

__all__ = [
    "DashboardApp",
    "create_app",
]


class DashboardApp:
    """仪表盘应用（编程式 API，渲染由 Panel 接管）。

    Parameters
    ----------
    task_repo : Any | None
        TaskRepo 实例。
    olap_engine : Any | None
        OLAPEngine 实例。
    """

    def __init__(
        self,
        task_repo: object | None = None,
        olap_engine: object | None = None,
    ) -> None:
        self._task_repo = task_repo
        self._olap_engine = olap_engine

    def get_task_progress(self) -> TaskProgressData:
        return fetch_task_progress(self._task_repo)

    def get_knowledge_overview(self) -> KnowledgeOverviewData:
        return fetch_knowledge_overview()

    def get_gate_statistics(self) -> GateStatisticsData:
        return fetch_gate_statistics(self._olap_engine)

    def get_fitness_data(self) -> FitnessDashboardData:
        return fetch_fitness_data()

    def get_olap_trends(self) -> OLAPTrendData:
        return fetch_olap_trends(self._olap_engine)

    def render_page(self, page_name: str) -> dict[str, Any]:
        if page_name == "task_progress":
            data = self.get_task_progress()
            return render_task_progress(data)
        elif page_name == "knowledge_overview":
            data = self.get_knowledge_overview()
            return render_knowledge_overview(data)
        elif page_name == "gate_statistics":
            data = self.get_gate_statistics()
            return render_gate_statistics(data)
        elif page_name == "fitness_functions":
            data = self.get_fitness_data()
            return render_fitness_dashboard(data)
        elif page_name == "olap_trend":
            data = self.get_olap_trends()
            return render_olap_trends(data)
        else:
            return {"error": f"Unknown page: {page_name}"}


def create_app(
    task_repo: object | None = None,
    olap_engine: object | None = None,
) -> DashboardApp:
    return DashboardApp(task_repo=task_repo, olap_engine=olap_engine)


def main() -> None:
    print("[DEPRECATED v3.1.0] app.py (Streamlit) 已弃用，请使用 Panel 主入口:", file=sys.stderr)
    print("  panel serve src/zephyr/frontend/dashboard/app_panel.py --show --port 5006", file=sys.stderr)
    print("  或: python src/zephyr/frontend/dashboard/app_panel.py", file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
