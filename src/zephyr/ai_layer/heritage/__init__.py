# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_heritage
# [MODULE] zephyr.ai_layer.heritage
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
"""heritage — AI 层 L7 传承段（经验结构化回流，闭环的关键边）工程包：登记闸库 / 先验 / 事件 / 关单机检 / 遗忘五件。

设计真源：``docs/_working/ai_layer_vision/L7_heredity/DESIGN.md``。
边界总裁定（D-L7-01）：传承库只进一个真源（L6/L4/工单/红蓝/casebook/checklist/memory → L7），
下游全只读（L1 先验/L2 快照/L4 判据先验/L5 祖先分支）；记忆目录永不写入（硬边界自守）。
存储裁定（D-L7-02）：PostgreSQL ``ai_heritage`` schema，全部读写经 DatabaseService/depgraph 通道，禁裸连接。
"""

from typing import Final

__all__: Final[list[str]] = [
    "closure_check",
    "forget",
    "heritage_events",
    "priors",
    "policy",
    "store",
]
from . import forget  # noqa: F401
from . import priors  # noqa: F401

# 包公共面显式重导出（2026-09-24 st-ailayer-final-20260924：ORPHAN-MODULE 静态可见边——动态派发消费型模块）
from . import forget  # noqa: F401
from . import priors  # noqa: F401
