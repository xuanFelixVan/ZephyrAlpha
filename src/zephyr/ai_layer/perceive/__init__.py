# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_perceive
# [MODULE] zephyr.ai_layer.perceive
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
"""perceive — AI 层 L1 感知段（外扫+内监）工程包：源注册表 / 搜索任务单 / 内监翻译器 三件。

设计真源：``docs/_working/ai_layer_vision/L1_perceive/DESIGN.md``（design_v1，Owner 夜批）。
一句话：L1=进化循环的点火器——内监（五个既有探测器的事件信号）与外扫（源注册表驱动的
节拍浅扫）双通道，产出定向搜索任务单喂 L2 收集段。
事件纪律：内监零定时器（全部挂既有事件源）；外扫节拍宿主=施工项 7，受 T3 双前置约束
（Owner 追认+裁定登记）未解锁，本包只提供任务单层，不含任何排班逻辑（禁 cron/Timer/sleep-loop）。
"""

from typing import Final

__all__: Final[list[str]] = ["search_orders", "source_registry", "translator"]
from . import translator  # noqa: F401

# 包公共面显式重导出（2026-09-24 st-ailayer-final-20260924：ORPHAN-MODULE 静态可见边——动态派发消费型模块）
from . import translator  # noqa: F401
