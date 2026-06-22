# [A_module] module_id=MOD-UNK_implementations | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L07-001 | docs/03_modules/_domain-reporting/analytics-core/blueprint.md
# [MODULE] zephyr.pf_core
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
"""L07 — Post-Trade Analytics Concrete Implementations

Phase C 具体实现包。

实现清单：
  - DefaultTCAEngine         : TCAEngineBase 的具体实现（滑点/佣金/Implementation Shortfall）
  - DefaultAttributionEngine : AttributionEngineBase 的具体实现（Brinson 模型）
"""

from zephyr.governance.default_attribution_engine import (
    DefaultAttributionEngine,
)
from zephyr.governance.default_tca_engine import (
    DefaultTCAEngine,
)

__all__ = ["DefaultAttributionEngine", "DefaultTCAEngine", "default_attribution_engine", "default_tca_engine"]
