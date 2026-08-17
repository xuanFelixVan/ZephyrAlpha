# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md
# [MODULE] zephyr.frontend.dashboard.app
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] zephyr.frontend.dashboard.components; zephyr.shared.contracts.task_repository_protocol; zephyr.governance.persistence.task_repo; zephyr.governance.persistence.sqlite_schema
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

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: TaskRepo 任务仓库实例
#   fields: 任务进度数据存取（可空，None 时组件走默认取数）
#   code: DashboardApp(task_repo) L81
# - id: I2
#   name: OLAPEngine 实例
#   fields: 门禁统计与 OLAP 趋势查询引擎（可空）
#   code: DashboardApp(olap_engine) L83
# - id: I3
#   name: 页面名 page_name 字符串
#   fields: task_progress / knowledge_overview / gate_statistics / fitness_functions / olap_trend 五键之一
#   code: render_page(page_name) L104
# 层: 算法
# - id: A1
#   name_zh: ① 五路数据取数
#   name_en: fetch_task_progress 等 5 个 fetch_*
#   intro: 从任务仓库/OLAP引擎等来源把5个面板要的数据分别取出来
#   desc: get_task_progress/get_knowledge_overview/get_gate_statistics/get_fitness_data/get_olap_trends 分别委托 components 包的 5 个 fetch_* 函数，返回对应 Data 对象
#   inputs: I1 I2
#   outputs: TaskProgressData / KnowledgeOverviewData / GateStatisticsData / FitnessDashboardData / OLAPTrendData
# - id: A2
#   name_zh: ② 页面路由渲染
#   name_en: render_page
#   intro: 按页面名把对应数据渲染成 dict，未知页面返回 error
#   desc: if/elif 分发到 5 个 render_* 组件函数；未知 page_name → {"error": "Unknown page"}；create_app 为 DashboardApp 简单工厂
#   inputs: I3 A1
#   outputs: dict[str, Any] 渲染数据
# 层: 输出
# - id: O1
#   name_zh: 页面渲染数据 dict
#   name_en: render_page 返回值
#   intro: 5个治理面板的渲染结果，Streamlit入口已弃用仅余编程式API
#   downstream: Panel 主入口 app_panel.py（v3.1.0 起接管渲染）/ 编程式调用方
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# I3 --> A2
# A2 --> O1
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
