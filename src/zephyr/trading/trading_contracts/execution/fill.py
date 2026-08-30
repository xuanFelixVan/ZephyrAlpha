# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.trading.trading_contracts.execution.fill
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.shared.contracts.fill
# [CONSUMERS] ex_core; pf_core
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
"""
Re-export wrapper: Fill 真源在 zephyr.shared.contracts.fill（CTR-005 codegen）

治本修复: 原文件重复定义 Fill 类（多真源），导致 isinstance 跨模块判断失败。
改为 re-export shared 层真源，消除多真源。
SSoT: cross_layer_contracts.yaml -> CTR-005 (codegen 生成 shared/contracts/fill.py)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: fill.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 Fill（共 1 符号）
#   desc: __init__ import L0；__all__ 1 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（1 符号）
#   name_en: __all__
#   intro: Fill
#   downstream: ex_core; pf_core
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from zephyr.shared.contracts.fill import Fill

__all__ = ["Fill"]
