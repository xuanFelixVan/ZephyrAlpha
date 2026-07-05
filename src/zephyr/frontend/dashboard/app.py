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
# [A_module] module_id=MOD-UNK_app | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# AI-generated: T-4-07 Streamlit Dashboard
"""
ZephyrAlpha Dashboard · Streamlit 仪表盘
=========================================

Task ID     : T-4-07
Depends     : T-4-04（fitness_functions）、T-4-05（olap_engine）、
              T-1-13（task_repo）
safety_level: L

5 个页面：
1. 任务进度看板（4 进度）
2. 知识库概览（条目数/状态分布/激活率）
3. 门禁统计（通过率/阻断率/趋势）
4. Fitness Functions（5 类度量仪表盘）
5. OLAP 趋势（DuckDB 趋势图）

数据源：SQLite + DuckDB + ChromaDB

启动方式：
    streamlit run frontend/app.py
"""

from __future__ import annotations

from typing import Any

try:
    import streamlit as st
except ImportError:
    st = None

from zephyr.governance.persistence.sqlite_schema import init_db
from zephyr.governance.persistence.task_repo import TaskRepository
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
    """Streamlit 仪表盘应用。

    Parameters
    ----------
    task_repo : Any | None
        TaskRepo 实例。
    olap_engine : Any | None
        OLAPEngine 实例。
    """

    def __init__(
        self,
        task_repo: Any | None = None,
        olap_engine: Any | None = None,
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
    task_repo: Any | None = None,
    olap_engine: Any | None = None,
) -> DashboardApp:
    return DashboardApp(task_repo=task_repo, olap_engine=olap_engine)


def main() -> None:
    import sys
    print("[DEPRECATED v3.1.0] app.py (Streamlit) 已弃用，请使用 Panel 主入口:", file=sys.stderr)
    print("  panel serve src/zephyr/frontend/dashboard/app_panel.py --show --port 5006", file=sys.stderr)
    print("  或: python src/zephyr/frontend/dashboard/app_panel.py", file=sys.stderr)
    if st is None:
        print("Streamlit is not installed. Install with: pip install streamlit")
        return

    st.set_page_config(
        page_title="ZephyrAlpha Dashboard",
        page_icon="📊",
        layout="wide",
    )

    st.title("ZephyrAlpha Dashboard")

    page = st.sidebar.selectbox(
        "Select Page",
        [
            "Task Progress",
            "Knowledge Overview",
            "Gate Statistics",
            "Fitness Functions",
            "OLAP Trends",
        ],
    )

    init_db()
    app = create_app(task_repo=TaskRepository())

    if page == "Task Progress":
        st.header("Task Progress (4)")
        data = app.get_task_progress()
        st.metric("Overall Completion Rate", f"{data.overall_rate:.1%}")
        st.metric("Total Tasks", data.total_tasks)
        st.metric("Completed", data.total_completed)
        for pp in data.phases:
            with st.expander(f"Phase {pp.phase}", expanded=True):
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total", pp.total_tasks)
                col2.metric("Completed", pp.completed_tasks)
                col3.metric("In Progress", pp.in_progress_tasks)
                col4.metric("Failed", pp.failed_tasks)
                st.progress(pp.completion_rate)

    elif page == "Knowledge Overview":
        st.header("Knowledge Base Overview")
        data = app.get_knowledge_overview()
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Entries", data.total_entries)
        col2.metric("Activated", data.activated_entries)
        col3.metric("Activation Rate", f"{data.activation_rate:.1%}")
        if data.status_distribution:
            st.subheader("Status Distribution")
            for d in data.status_distribution:
                st.write(f"  {d.status}: {d.count}")

    elif page == "Gate Statistics":
        st.header("Gate Statistics")
        data = app.get_gate_statistics()
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Runs", data.total_runs)
        col2.metric("Pass Rate", f"{data.overall_pass_rate:.1%}")
        col3.metric("Block Rate", f"{data.overall_block_rate:.1%}")

    elif page == "Fitness Functions":
        st.header("Fitness Functions")
        data = app.get_fitness_data()
        st.metric("Overall Status", data.overall_status)
        for m in data.metrics:
            st.write(f"**{m['metric_name']}**: {m['value']} ({m['status']})")

    elif page == "OLAP Trends":
        st.header("OLAP Trends")
        data = app.get_olap_trends()
        if data.task_progress:
            st.subheader("Task Progress Trend")
            st.dataframe(data.task_progress)
        if data.compliance_rate:
            st.subheader("Compliance Rate Trend")
            st.dataframe(data.compliance_rate)
        if data.knowledge_activation:
            st.subheader("Knowledge Activation Trend")
            st.dataframe(data.knowledge_activation)


if __name__ == "__main__":
    main()
