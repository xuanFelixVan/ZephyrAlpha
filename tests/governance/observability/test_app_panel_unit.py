# [A_test] module_id: MOD-GOV_app_panel_unit | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md | §16.7
# [MODULE] tests.governance.observability.test_app_panel_unit
# [DOMAIN] D_FRONTEND
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-L08-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""test_app_panel_unit · app_panel.py 单元测试（v3.1.0, #ARCH-047）

测试 DashboardPanelApp / create_dashboard / _demo_backtest_data / build_tabs。
panel 未安装时自动 skip（pytest.importorskip）。
"""

from __future__ import annotations

import pytest

panel = pytest.importorskip("panel", reason="panel not installed")
pytest.importorskip("holoviews", reason="holoviews not installed")

from zephyr.frontend.dashboard.app_panel import (
    DashboardPanelApp,
    create_dashboard,
    main,
)
from zephyr.frontend.dashboard.components.backtest_results import (
    BacktestGateStatus,
    BacktestMetrics,
    BacktestResultData,
)


class TestDashboardPanelApp:
    """DashboardPanelApp 实例化与 Tab 组装测试。"""

    def test_instantiate_no_deps(self) -> None:
        """无依赖实例化——所有数据源为 None。"""
        app = DashboardPanelApp()
        assert app.task_repo is None
        assert app.olap_engine is None
        assert app.backtest_result is None

    def test_instantiate_with_deps(self) -> None:
        """有依赖实例化——注入 mock 数据源。"""
        app = DashboardPanelApp(
            task_repo="mock_repo",
            olap_engine="mock_engine",
            backtest_result="mock_result",
        )
        assert app.task_repo == "mock_repo"
        assert app.olap_engine == "mock_engine"
        assert app.backtest_result == "mock_result"

    def test_demo_backtest_data(self) -> None:
        """_demo_backtest_data 返回合法 BacktestResultData。"""
        data = DashboardPanelApp.demo_backtest_data()
        assert isinstance(data, BacktestResultData)
        assert data.backtest_id == "demo-001"
        assert data.strategy_id == "demo-strategy"
        assert len(data.net_value_curve) > 1
        assert len(data.drawdown_curve) == len(data.net_value_curve)
        assert data.gate_status.is_passed is True
        assert isinstance(data.metrics, BacktestMetrics)
        assert isinstance(data.gate_status, BacktestGateStatus)

    def test_build_tabs_returns_tabs(self) -> None:
        """build_tabs 返回 pn.Tabs，含 14 个 Tab（v3.5.0 作战室首位）。"""
        app = DashboardPanelApp()
        tabs = app.build_tabs()
        # pn.Tabs 对象可通过 len() 获取 Tab 数量
        assert len(tabs) == 14

    def test_warroom_tab_first(self) -> None:
        """作战室 Tab 居首位（v3.5.0, 45号作战手册 P1 实盘组首位）。"""
        app = DashboardPanelApp()
        tabs = app.build_tabs()
        assert tabs._names[0] == "作战室"


class TestCreateDashboard:
    """create_dashboard 工厂函数测试。"""

    def test_create_dashboard_returns_layout(self) -> None:
        """create_dashboard 返回 pn.Column 布局。"""
        layout = create_dashboard()
        assert layout is not None
        # pn.Column 应含 header + tabs
        assert len(layout) >= 2

    def test_create_dashboard_with_task_repo(self) -> None:
        """create_dashboard 接受 task_repo 参数。"""
        layout = create_dashboard(task_repo="mock_repo")
        assert layout is not None


class TestMain:
    """main() 入口函数测试（不实际启动 server）。"""

    def test_main_exists(self) -> None:
        """main 函数可调用（不实际执行 pn.serve）。"""
        assert callable(main)
        assert main.__name__ == "main"
