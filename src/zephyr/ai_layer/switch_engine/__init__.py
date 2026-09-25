# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §l6_switch_engine
# [MODULE] zephyr.ai_layer.switch_engine
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
"""switch_engine（AI 层侧）— L6 切换段治理四件：墓碑管理 / 审批分流 / 回切演练 / 灰度三档。

设计真源：``docs/_working/ai_layer_vision/L6_ab_switch/DESIGN.md`` §②-D/§②-E/§②-F/§②-G
（施工项 S5-S8）。底层状态机与注册表在 ``zephyr.intelligence.switch_engine``
（S1/S3/S4，DESIGN 指定路径），本包只做治理上层，禁绕过状态机直改库。
"""

from typing import Final

__all__: Final[list[str]] = ["approval_router", "revert_drill", "rollout_tiers", "tombstone_manager"]
from . import revert_drill  # noqa: F401
from . import rollout_tiers  # noqa: F401
from . import tombstone_manager  # noqa: F401

# 包公共面显式重导出（2026-09-24 st-ailayer-final-20260924：ORPHAN-MODULE 静态可见边——动态派发消费型模块）
from . import revert_drill  # noqa: F401
from . import rollout_tiers  # noqa: F401
from . import tombstone_manager  # noqa: F401
