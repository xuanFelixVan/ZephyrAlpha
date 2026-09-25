# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §model_intel
# [MODULE] zephyr.intelligence.model_intel
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
"""model_intel — OBJ_M M1 模型情报扫描包：情报卡 schema+四闸校验+simhash 查重（intel_card）；源注册表读取+抓取+diff 建卡（scanner）。

设计真源：``docs/_working/ai_layer_vision/OBJ_M_models/DESIGN.md`` §2。
事件触发+周历窗口驱动，码内零定时器（宪法 §9.3）。
"""

from typing import Final

__all__: Final[list[str]] = ["scanner", "intel_card"]
