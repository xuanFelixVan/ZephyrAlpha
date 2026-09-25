# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_scheduling
# [MODULE] zephyr.ai_layer.scheduling
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
"""scheduling — AI 层 L5 排产段工程包：门闸判定 / 工单生成守护 / 派工编排 / 登记接口。

设计真源：``docs/_working/ai_layer_vision/L5_schedule_gate/DESIGN.md``（D-L5-01：L5 不建任何
新排班真源——排班一张真源（资源画像注册表+周历+冲突闸）是 Owner 已批裁定）。核心三件事：
①门闸判定（成熟度/配额/算力三条件 AND）②胜者证据包→任务书自动套模板 ③派工编排
（优先级/分流/登记）。排班登记只写种子文件 evolution_schedule_seeds.yaml（生成器新源 I7
消费），禁直改 resource_profile_registry.yaml。
"""

from __future__ import annotations  # noqa: F401（包级统一注解前导，对齐仓内硬纪律）

from typing import Final

__all__: Final[list[str]] = [
    "scheduling_events",
    "order_daemon",
    "maturity",
    "router",
    "dispatcher",
    "seed_writer",
]
from . import maturity  # noqa: F401
from . import order_daemon  # noqa: F401
from . import router  # noqa: F401

# 包公共面显式重导出（2026-09-24 st-ailayer-final-20260924：ORPHAN-MODULE 静态可见边——动态派发消费型模块）
from . import maturity  # noqa: F401
from . import order_daemon  # noqa: F401
from . import router  # noqa: F401
