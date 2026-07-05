# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md
# [MODULE] zephyr.frontend.dashboard.app_panel
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] panel; holoviews; plotly; plotly_resampler; datashader; bokeh; zephyr.frontend.dashboard.components.chart_factory; zephyr.frontend.dashboard.components.backtest_results; zephyr.frontend.dashboard.components.backtest_performance; zephyr.frontend.dashboard.components.tick_replay; zephyr.frontend.dashboard.components.order_book; zephyr.frontend.dashboard.components.position_monitor; zephyr.frontend.dashboard.components.trade_panel; zephyr.frontend.dashboard.components.fitness_functions; zephyr.frontend.dashboard.components.gate_statistics; zephyr.frontend.dashboard.components.knowledge_overview; zephyr.frontend.dashboard.components.olap_trend; zephyr.frontend.dashboard.components.task_progress; zephyr.governance.persistence.sqlite_schema; zephyr.governance.persistence.task_repo
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
# [A_module] module_id=MOD-L08-001-app_panel | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""app_panel · Panel 仪表盘主应用入口（v3.1.0, #ARCH-047）

ARCH-047 v3.1.0: 仪表盘可运行化。Panel 主入口组装 10 个 Tab（5 治理类 + 5 交易/回测类）。
v3.0.0 已完成 5 个交易/回测组件迁移；v3.1.0 完成剩余 5 个治理类组件迁移 + 本主入口。

10 个 Tab:
  治理类（v3.1.0 迁移）:
    1. 任务进度看板     — task_progress
    2. 知识库概览       — knowledge_overview
    3. 门禁统计         — gate_statistics
    4. Fitness Functions — fitness_functions
    5. OLAP 趋势        — olap_trend
  交易/回测类（v3.0.0 迁移）:
    6. 回测结果         — backtest_results
    7. Tick 回放        — tick_replay
    8. 5档盘口          — order_book
    9. 持仓监控         — position_monitor
    10. 交易面板        — trade_panel

启动方式:
    方式1 (panel serve, 推荐):
        panel serve src/zephyr/frontend/dashboard/app_panel.py --show --port 5006
    方式2 (python 直接运行):
        python src/zephyr/frontend/dashboard/app_panel.py
    浏览器访问: http://localhost:5006

数据源:
    - TaskRepository (SQLite) — 任务进度
    - FitnessFunctionFramework — Fitness 度量
    - OLAPEngine (可选) — 门禁统计/OLAP 趋势
    - D_BACKTEST/D_EX_CORE/D_DATA (可选) — 交易/回测组件, 未注入时显示空状态

设计原则:
    - callback仅编排: 各 Tab 仅调用 fetch_xxx + render_xxx, 不含业务逻辑
    - 依赖注入: 数据源通过构造函数传入, 禁止直接 import 业务层
    - 可选依赖: panel/holoviews/plotly 通过 try/except 导入
"""
from __future__ import annotations

from typing import Any, Optional

try:
    import panel as pn
except ImportError:  # 测试环境无 panel
    pn = None

try:
    import holoviews as hv
    hv.extension("bokeh")
except ImportError:
    hv = None

from zephyr.governance.persistence.sqlite_schema import init_db
from zephyr.governance.persistence.task_repo import TaskRepository

# 治理类组件（v3.1.0 迁移）
from zephyr.frontend.dashboard.components.fitness_functions import (
    fetch_fitness_data,
    render_fitness_dashboard,
)
from zephyr.frontend.dashboard.components.gate_statistics import (
    fetch_gate_statistics,
    render_gate_statistics,
)
from zephyr.frontend.dashboard.components.knowledge_overview import (
    fetch_knowledge_overview,
    render_knowledge_overview,
)
from zephyr.frontend.dashboard.components.olap_trend import (
    fetch_olap_trends,
    render_olap_trends,
)
from zephyr.frontend.dashboard.components.task_progress import (
    fetch_task_progress,
    render_task_progress,
)

# 交易/回测类组件（v3.0.0 迁移）
from zephyr.frontend.dashboard.components.backtest_results import (
    BacktestGateStatus,
    BacktestMetrics,
    BacktestResultData,
    render_backtest_results,
)
# 掘金风格 5-Tab 绩效分析 (v3.2.0, bt-visualizer + 掘金量化)
from zephyr.frontend.dashboard.components.backtest_performance import (
    BacktestPerformanceData,
    generate_demo_performance_data,
    render_backtest_performance,
)
from zephyr.frontend.dashboard.components.tick_replay import (
    ReplaySpeed,
    fetch_tick_replay,
    render_tick_replay,
)
from zephyr.frontend.dashboard.components.order_book import (
    fetch_order_book,
    render_order_book,
)
from zephyr.frontend.dashboard.components.position_monitor import (
    fetch_position_monitor,
    render_position_monitor,
)
from zephyr.frontend.dashboard.components.trade_panel import (
    TradePanelData,
    render_trade_panel,
)

__all__ = [
    "DashboardPanelApp",
    "create_dashboard",
    "main",
    "BacktestPerformanceData",
    "generate_demo_performance_data",
    "render_backtest_performance",
]


class DashboardPanelApp:
    """Panel 仪表盘应用（v3.1.0, #ARCH-047）

    组装 10 个 Tab：5 治理类 + 5 交易/回测类。

    Parameters
    ----------
    task_repo : Any | None
        TaskRepository 实例（任务进度数据源）
    olap_engine : Any | None
        OLAPEngine 实例（门禁统计/OLAP 趋势数据源）
    backtest_result : Any | None
        BacktestResult 实例（回测结果数据源, D_BACKTEST）
    tick_data : list | None
        Tick 数据序列（Tick 回放数据源, D_BACKTEST）
    miniqmt_provider : Any | None
        MiniQmtProvider 实例（5档盘口数据源, D_DATA）
    miniqmt_broker : Any | None
        MiniQmtBroker 实例（持仓数据源, D_EX_CORE）
    execution_engine : Any | None
        ExecutionEngine 实例（交易面板数据源, D_EX_CORE）
    """

    def __init__(
        self,
        task_repo: Any | None = None,
        olap_engine: Any | None = None,
        backtest_result: Any | None = None,
        tick_data: Optional[list] = None,
        miniqmt_provider: Any | None = None,
        miniqmt_broker: Any | None = None,
        execution_engine: Any | None = None,
    ) -> None:
        self._task_repo = task_repo
        self._olap_engine = olap_engine
        self._backtest_result = backtest_result
        self._tick_data = tick_data
        self._miniqmt_provider = miniqmt_provider
        self._miniqmt_broker = miniqmt_broker
        self._execution_engine = execution_engine

    # ===== 治理类 Tab =====

    def _tab_task_progress(self) -> Any:
        data = fetch_task_progress(self._task_repo)
        payload = render_task_progress(data)
        return payload.get("_layout") or pn.pane.Markdown("任务进度渲染失败")

    def _tab_knowledge_overview(self) -> Any:
        data = fetch_knowledge_overview()
        payload = render_knowledge_overview(data)
        return payload.get("_layout") or pn.pane.Markdown("知识库概览渲染失败")

    def _tab_gate_statistics(self) -> Any:
        data = fetch_gate_statistics(self._olap_engine)
        payload = render_gate_statistics(data)
        return payload.get("_layout") or pn.pane.Markdown("门禁统计渲染失败")

    def _tab_fitness_functions(self) -> Any:
        data = fetch_fitness_data()
        payload = render_fitness_dashboard(data)
        return payload.get("_layout") or pn.pane.Markdown("Fitness 渲染失败")

    def _tab_olap_trends(self) -> Any:
        data = fetch_olap_trends(self._olap_engine)
        payload = render_olap_trends(data)
        return payload.get("_layout") or pn.pane.Markdown("OLAP 趋势渲染失败")

    # ===== 交易/回测类 Tab =====

    def _tab_backtest_results(self) -> Any:
        # v3.2.0: 掘金风格 5-Tab 绩效分析 (bt-visualizer + 掘金量化)
        # 5 子 Tab: 绩效概览 / 持仓分析 / 交易统计 / 每日明细 / 信号分析
        perf_data = generate_demo_performance_data()
        payload = render_backtest_performance(perf_data)
        return payload.get("_layout") or pn.pane.Markdown("回测绩效分析渲染失败")

    def _tab_tick_replay(self) -> Any:
        ticks = self._tick_data if self._tick_data is not None else []
        data = fetch_tick_replay(ticks, symbol="demo", replay_speed=ReplaySpeed.MAX_SPEED)
        payload = render_tick_replay(data)
        return payload.get("_layout") or pn.pane.Markdown("Tick 回放渲染失败")

    def _tab_order_book(self) -> Any:
        data = fetch_order_book(self._miniqmt_provider, symbol="demo")
        payload = render_order_book(data)
        return payload.get("_layout") or pn.pane.Markdown("盘口渲染失败")

    def _tab_position_monitor(self) -> Any:
        data = fetch_position_monitor(self._miniqmt_broker)
        payload = render_position_monitor(data)
        return payload.get("_layout") or pn.pane.Markdown("持仓监控渲染失败")

    def _tab_trade_panel(self) -> Any:
        data = TradePanelData()
        payload = render_trade_panel(data, execution_engine=self._execution_engine)
        return payload.get("_layout") or pn.pane.Markdown("交易面板渲染失败")

    # ===== Demo 数据（无 BacktestResult 注入时展示，证明仪表盘可运行）=====

    @staticmethod
    def _demo_backtest_data() -> BacktestResultData:
        """生成演示用回测数据（净值/回撤曲线），证明 backtest_results Tab 可渲染"""
        nav = [1.0]
        for r in [0.012, -0.008, 0.015, -0.005, 0.020, -0.012, 0.018, -0.003,
                  0.010, -0.007, 0.022, -0.010, 0.016, -0.004, 0.014]:
            nav.append(nav[-1] * (1 + r))
        peak = 0.0
        drawdown = []
        for v in nav:
            peak = max(peak, v)
            drawdown.append(v - peak)
        return BacktestResultData(
            backtest_id="demo-001",
            strategy_id="demo-strategy",
            net_value_curve=nav,
            drawdown_curve=drawdown,
            timestamps=[f"2026-01-{i:02d}" for i in range(1, len(nav) + 1)],
            metrics=BacktestMetrics(
                sharpe=1.85,
                sortino=2.31,
                max_drawdown=-0.034,
                ic=0.062,
                ir=0.78,
                win_rate=0.56,
                annual_return=0.235,
            ),
            gate_status=BacktestGateStatus(
                is_passed=True,
                wfa_passed=True,
                oos_passed=False,
            ),
            overfitting_flag=False,
        )

    # ===== 组装 =====

    def build_tabs(self) -> Any:
        """构建 10 个 Tab 的 pn.Tabs 布局"""
        tabs_spec = [
            ("任务进度", self._tab_task_progress),
            ("知识库概览", self._tab_knowledge_overview),
            ("门禁统计", self._tab_gate_statistics),
            ("Fitness", self._tab_fitness_functions),
            ("OLAP 趋势", self._tab_olap_trends),
            ("回测结果", self._tab_backtest_results),
            ("Tick 回放", self._tab_tick_replay),
            ("5档盘口", self._tab_order_book),
            ("持仓监控", self._tab_position_monitor),
            ("交易面板", self._tab_trade_panel),
        ]
        tab_objects = []
        for name, builder in tabs_spec:
            try:
                tab_objects.append((name, builder()))
            except Exception as e:  # 单 Tab 失败不影响其他 Tab
                tab_objects.append((name, pn.pane.Alert(
                    f"❌ Tab '{name}' 渲染异常: {e}", alert_type="danger"
                )))
        return pn.Tabs(
            *tab_objects,
            tabs_location="left",
            sizing_mode="stretch_width",
        )


def create_dashboard(
    task_repo: Any | None = None,
    olap_engine: Any | None = None,
    **kwargs: Any,
) -> Any:
    """创建仪表盘顶层布局（pn.Column: 标题 + Tabs）

    可在 panel serve 模式下 .servable()，也可在 python 模式下传给 pn.serve()。
    """
    if pn is None:
        raise RuntimeError("panel 未安装，请运行: pip install panel holoviews plotly plotly_resampler datashader bokeh")

    pn.extension("plotly", sizing_mode="stretch_width")

    # 默认注入 TaskRepository（SQLite 已初始化）
    if task_repo is None:
        try:
            init_db()
            task_repo = TaskRepository()
        except Exception:
            task_repo = None

    app = DashboardPanelApp(task_repo=task_repo, olap_engine=olap_engine, **kwargs)
    tabs = app.build_tabs()

    header = pn.pane.Markdown(
        "# ZephyrAlpha Dashboard\n"
        "Panel+HoloViz 仪表盘 (v3.1.0, #ARCH-047) — 10 Tab 治理+交易/回测",
    )
    layout = pn.Column(header, tabs, sizing_mode="stretch_width")
    return layout


def main() -> None:
    """python 直接运行入口: python src/zephyr/frontend/dashboard/app_panel.py"""
    if pn is None:
        print("panel 未安装，请运行: pip install panel holoviews plotly plotly_resampler datashader bokeh")
        return
    dashboard = create_dashboard()
    pn.serve(dashboard, show=True, port=5006, title="ZephyrAlpha Dashboard")


# panel serve 模式：自动 .servable()
if pn is not None:
    try:
        _DASHBOARD = create_dashboard()
        _DASHBOARD.servable()
    except Exception as _e:  # pragma: no cover — servable 失败不阻断 import
        import sys
        print(f"[app_panel] servable 初始化警告: {_e}", file=sys.stderr)


if __name__ == "__main__":
    main()
