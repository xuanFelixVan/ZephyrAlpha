# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.trading.trading_contracts.execution.execution_report
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.shared.contracts.execution_report
# [CONSUMERS] pf_core
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Re-export wrapper: ExecutionReport 真源在 zephyr.shared.contracts.execution_report（CTR-P1-007 codegen）

治本修复: 原文件重复定义 ExecutionReport 类（多真源），导致 isinstance 跨模块判断失败。
改为 re-export shared 层真源，消除多真源。
SSoT: cross_layer_contracts.yaml -> CTR-P1-007 (codegen 生成 shared/contracts/execution_report.py)
"""

from __future__ import annotations

from zephyr.shared.contracts.execution_report import ExecutionReport

__all__ = ["ExecutionReport"]
