# [BLUEPRINT] MOD-TDMVAL-001 | docs/03_modules/_domain_trading/validation/blueprint.md
# [MODULE] zephyr.trading.validation
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.decision_map; zephyr.data.ch_writer; zephyr.shared.io.paths
# [CONSUMERS] zephyr.frontend.dashboard.api_server; P2-1 衰减巡检（decay watch）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] holdout 窗口排除最近 12 个月；触发<30 不下结论；验证态只进台账不进地图 YAML
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValidationError
# [TESTS] tests/trading/test_validation_runner.py
# [TTL] permanent
"""TDM 节点验证包（节点级可回测治理 P1-2，PB-01/PB-12/PB-13/PB-16 落地）。

真源: docs/_working/2026-09-09-node-backtest-governance.md §8.2
蓝图: docs/03_modules/_domain_trading/validation/blueprint.md

公共面:
    run_validation  验证批入口（默认 L4 执行类首批 14 节点 → node_verdict 台账）
    ValidationError 验证数据/配置异常
"""

from zephyr.trading.validation.runner import ValidationError, run_validation

__all__ = ["ValidationError", "run_validation"]
