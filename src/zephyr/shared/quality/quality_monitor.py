# [A_module] module_id=MOD-SHR_quality_monitor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §

# [MODULE] zephyr.shared.quality.quality_monitor

# [INVARIANTS] proxy module — redirects to zephyr.infrastructure.quality.quality_monitor

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

# 代理模块：将 zephyr.shared.quality.quality_monitor 重定向到 zephyr.infrastructure.quality.quality_monitor
from zephyr.infrastructure.quality.quality_monitor import (
    CodeQualityReport,
    QualityMetric,
    QualityMonitor,
)

__all__ = ["CodeQualityReport", "QualityMetric", "QualityMonitor"]
