# AI-generated: T-4-07 Streamlit Dashboard
"""
ZephyrAlpha Dashboard · Streamlit 仪表盘
=========================================

Task ID     : T-4-07
Depends     : T-4-04（fitness_functions）、T-4-05（olap_engine）、
              T-2-11-A（kb_repo）、T-1-13（task_repo）
safety_level: L

5 个页面：
1. 任务进度看板（Phase 0-4 进度）
2. 知识库概览（条目数/状态分布/激活率）
3. 门禁统计（通过率/阻断率/趋势）
4. Fitness Functions（5 类度量仪表盘）
5. OLAP 趋势（DuckDB 趋势图）

数据源：SQLite + DuckDB + ChromaDB

启动方式：
    streamlit run src/zephyr/dashboard/app.py
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Optional

try:
    import streamlit as st
except ImportError:
    st = None

from zephyr.l08_human_ai_interface.dashboard.components.task_progress import (
    TaskProgressData,
    fetch_task_progress,
    render_task_progress,
)
from zephyr.l08_human_ai_interface.dashboard.components.knowledge_overview import (
    KnowledgeOverviewData,
    fetch_knowledge_overview,
    render_knowledge_overview,
)
from zephyr.l08_human_ai_interface.dashboard.components.gate_statistics import (
    GateStatisticsData,
    fetch_gate_statistics,
    render_gate_statistics,
)
from zephyr.l08_human_ai_interface.dashboard.components.fitness_functions import (
    FitnessDashboardData,
    fetch_fitness_data,
    render_fitness_dashboard,
)
from zephyr.l08_human_ai_interface.dashboard.components.olap_trend import (
    OLAPTrendData,
    fetch_olap_trends,
    render_olap_trends,
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
    kb_repo : Any | None
        KbRepo 实例。
    olap_engine : Any | None
        OLAPEngine 实例。
    """

    def __init__(
        self,
        task_repo: Optional[Any] = None,
        kb_repo: Optional[Any] = None,
        olap_engine: Optional[Any] = None,
    ) -> None:
        self._task_repo = task_repo
        self._kb_repo = kb_repo
        self._olap_engine = olap_engine

    def get_task_progress(self) -> TaskProgressData:
        return fetch_task_progress(self._task_repo)

    def get_knowledge_overview(self) -> KnowledgeOverviewData:
        return fetch_knowledge_overview(self._kb_repo)

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
    task_repo: Optional[Any] = None,
    kb_repo: Optional[Any] = None,
    olap_engine: Optional[Any] = None,
) -> DashboardApp:
    return DashboardApp(task_repo=task_repo, kb_repo=kb_repo, olap_engine=olap_engine)


def main() -> None:
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

    app = create_app()

    if page == "Task Progress":
        st.header("Task Progress (Phase 0-4)")
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
