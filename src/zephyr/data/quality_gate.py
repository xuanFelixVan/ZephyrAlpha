# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.quality_gate
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.gov_enforcement.rule_enforcement.quality_gate
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV-quality_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
Re-export wrapper: QualityReport 真源在 zephyr.gov_enforcement.rule_enforcement.quality_gate

治本修复: 测试通过 zephyr.data.quality_gate 导入 QualityReport，但真源在
gov_enforcement.rule_enforcement.quality_gate。创建 re-export 消除 ModuleNotFoundError。
SSoT: cross_layer_contracts.yaml -> CTR-ERR-001

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: quality_gate.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 QualityReport, MarketDataValidator, apply_quality_gate（共 3 符号）
#   desc: __init__ import L0；__all__ 3 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（3 符号）
#   name_en: __all__
#   intro: QualityReport, MarketDataValidator, apply_quality_gate
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from zephyr.gov_enforcement.rule_enforcement.quality_gate import (
    MarketDataValidator,
    QualityReport,
    apply_quality_gate,
)

__all__ = ["QualityReport", "MarketDataValidator", "apply_quality_gate"]
