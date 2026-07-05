# [A_module] module_id=MOD-UNK_components | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain-frontend/hmi-core/blueprint.md
# [MODULE] zephyr.frontend.dashboard.components
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent

# v2.2.0 新增5个组件（MiniQMT实盘+Tick回测仪表盘）
# v3.0.0 新增 ChartFactory 图表统一工厂（#ARCH-047 Streamlit→Panel+HoloViz）
# 用多行单 import 语句（ORPHAN-MODULE gate 的 git grep pattern: from .* import {short_name}）
try:
    from zephyr.frontend.dashboard.components import backtest_results
    from zephyr.frontend.dashboard.components import chart_factory
    from zephyr.frontend.dashboard.components import order_book
    from zephyr.frontend.dashboard.components import position_monitor
    from zephyr.frontend.dashboard.components import tick_replay
    from zephyr.frontend.dashboard.components import trade_panel
except ImportError:
    backtest_results = None  # type: ignore[assignment]
    chart_factory = None  # type: ignore[assignment]
    order_book = None  # type: ignore[assignment]
    position_monitor = None  # type: ignore[assignment]
    tick_replay = None  # type: ignore[assignment]
    trade_panel = None  # type: ignore[assignment]

__all__ = [
    "fitness_functions",
    "gate_statistics",
    "knowledge_overview",
    "olap_trend",
    "task_progress",
    # v2.2.0 新增
    "backtest_results",
    "order_book",
    "position_monitor",
    "tick_replay",
    "trade_panel",
    # v3.0.0 新增（#ARCH-047）
    "chart_factory",
]
