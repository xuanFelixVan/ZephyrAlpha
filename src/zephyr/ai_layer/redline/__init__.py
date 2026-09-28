# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §obj_s_perimeter
# [MODULE] zephyr.ai_layer.redline
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
"""zephyr.ai_layer.redline — OBJ_S 红线与自由域机检面（负面清单 NL-1..6 + SEV 探针 + 双指标看板）。

设计真源：docs/_working/ai_layer_vision/OBJ_S_perimeter/DESIGN.md（§④ 施工项清单 8 项）。
本包只产"扫描/聚合/生成器/建议"性质机检件：红线语义归 Owner（变更走 OBJ_R 四步流水线），
机检实现=普通代码域；刹车动作全部复用已有原生闸（immutable_core/KillSwitch/五级交易熔断/
RULE-GIT-SAFE/REGISTRY-MASS-DELETION），本包零新刹车。

# [ALGO_FLOW] external: docs/03_modules/_domain_ai_layer/algo_flow/redline_pkg.yaml
"""

# 包公共面显式重导出（2026-09-24 st-ailayer-final-20260924：ORPHAN-MODULE 静态可见边——动态派发消费型模块）
from . import (
    annual_review,  # noqa: F401  # noqa: F401
    dashboard_pipeline,  # noqa: F401  # noqa: F401
    drop_gate,  # noqa: F401  # noqa: F401
    negative_list_gates,  # noqa: F401  # noqa: F401
    session_env_guard,  # noqa: F401  # noqa: F401
    sev_router,  # noqa: F401  # noqa: F401
)
