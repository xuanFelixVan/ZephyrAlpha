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
"""Re-export wrapper: QualityReport 真源在 zephyr.gov_enforcement.rule_enforcement.quality_gate

治本修复: 测试通过 zephyr.data.quality_gate 导入 QualityReport，但真源在
gov_enforcement.rule_enforcement.quality_gate。创建 re-export 消除 ModuleNotFoundError。
SSoT: cross_layer_contracts.yaml -> CTR-ERR-001
"""

from __future__ import annotations

from zephyr.gov_enforcement.rule_enforcement.quality_gate import (
    MarketDataValidator,
    QualityReport,
    apply_quality_gate,
)

__all__ = ["QualityReport", "MarketDataValidator", "apply_quality_gate"]
