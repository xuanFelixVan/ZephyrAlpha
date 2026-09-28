# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §l6_switch_engine
# [MODULE] zephyr.intelligence.switch_engine
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] （见正文/DESIGN）
# [CONSUMERS] CLI 与段内消费方（见各模块头）
# [STARTUP] manual
# [MATURITY] evolving
# [INVARIANTS] （见正文/DESIGN）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/（段 DESIGN.md）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] （见正文/DESIGN）
# [TESTS] tests/ai_layer/（对应段测试目录）
# [TTL] permanent
"""switch_engine — L6 切换段工程包（A/B 蓝绿·champion/challenger 进化安全带）。

设计真源：``docs/_working/ai_layer_vision/L6_ab_switch/DESIGN.md``。
形态铁律：B 组并行的一切产出只写对比区，永不回流生产决策路径——影子不下真决策
是本包第一不变量；promote=一次性切换动作（事件），promoted=动作后驻留态。

施工项落位（DESIGN §④）：S1=switch_registry / S2 加载器=criteria（YAML 真源在
config/switch_criteria.yaml）/ S3=shadow_runner / S4=switch_engine。

# [ALGO_FLOW] external: docs/03_modules/_domain_ai_layer/algo_flow/iswitch_pkg.yaml
"""

from typing import Final

__all__: Final[list[str]] = ["criteria", "shadow_runner", "switch_engine", "switch_registry"]
# 包公共面显式重导出（2026-09-24 st-ailayer-final-20260924：ORPHAN-MODULE 静态可见边——动态派发消费型模块）
from . import (
    criteria,  # noqa: F401  # noqa: F401
    shadow_runner,  # noqa: F401  # noqa: F401
)
