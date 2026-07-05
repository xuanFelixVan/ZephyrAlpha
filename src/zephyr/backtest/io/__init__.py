# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.io
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.core.engine_base
# [CONSUMERS] zephyr.frontend.dashboard.components.backtest_results; zephyr.frontend.dashboard.components.tick_replay
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] PIT铁律(零前瞻偏差)
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] BacktestResultSinkError; ArtifactNotFoundError
# [TESTS]
# [A_module] module_id=MOD-BT-001-io | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""io · D_BACKTEST 可视化产物 io 子包（v1.3.0 新增，#ARCH-047）

蓝图规格: docs/03_modules/_domain_backtest/blueprint.md §16.7
配合前端可视化技术栈 Streamlit→Panel+HoloViz 重构(#ARCH-047)。

包含:
  - backtest_result_sink.py: BacktestResult → BacktestSinkData 数据落地
  - result_repository.py: BacktestRunArtifact(CTR-P1-017) 持久化/检索

数据流:
  BacktestResult(CTR-P1-016)
    → sink_backtest_result() → BacktestSinkData
    → build_artifact_from_data() → BacktestRunArtifact(CTR-P1-017)
    → save_artifact() → 文件系统持久化
    → get_artifact() → D_FRONTEND 组件消费
"""
from zephyr.backtest.io.backtest_result_sink import (
    BacktestSinkData,
    BacktestResultSinkError,
    BenchmarkPoint,
    DrawdownPoint,
    EquityPoint,
    TradeRecord,
    sink_backtest_result,
)
from zephyr.backtest.io.result_repository import (
    ArtifactNotFoundError,
    BacktestRunArtifact,
    build_artifact_from_data,
    delete_artifact,
    get_artifact,
    list_artifacts,
    save_artifact,
)
from zephyr.backtest.io.decisiongraph_adapter import (
    backtest_result_to_decision_node,
    register_backtest_result_in_decisiongraph,
)

__all__ = [
    # backtest_result_sink
    "BacktestSinkData",
    "BacktestResultSinkError",
    "EquityPoint",
    "TradeRecord",
    "DrawdownPoint",
    "BenchmarkPoint",
    "sink_backtest_result",
    # result_repository
    "ArtifactNotFoundError",
    "BacktestRunArtifact",
    "save_artifact",
    "get_artifact",
    "list_artifacts",
    "delete_artifact",
    "build_artifact_from_data",
    # decisiongraph_adapter (TRAE-061 Phase 5)
    "backtest_result_to_decision_node",
    "register_backtest_result_in_decisiongraph",
]
