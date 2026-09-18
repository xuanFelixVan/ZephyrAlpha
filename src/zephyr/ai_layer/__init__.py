# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer
# [MODULE] zephyr.ai_layer
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
"""ai_layer — AI 层（自我进化引擎）顶层包：七段一常数（L1-L7 + OBJ_M/R/S/T）工程落点。

总骨架真源：``docs/_working/ai_layer_vision/README.md``。本包内子包按段落组织，
首批落地=L2 收集段（``intake``）。产线（业务层）代码禁 import 本包内生食库模块。
"""

__all__: list[str] = ["intake"]
