# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.integration.shared.events.event_bus_upgrade
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.shared.events.event_bus_upgrade
# [CONSUMERS] zephyr.integration.shared.events.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""EventBus Upgrade（事件版本化迁移）— backward-compat re-export shim。

AI-15 审计治本（2026-08-17）：本文件原为 zephyr.shared.events.event_bus_upgrade
的逐字复制副本（仅 error_code 漂移为 ZA-IG-0016）。唯一真源已收敛至
zephyr.shared.events.event_bus_upgrade，本文件 re-export 保持向后兼容。
禁止在本文件重新落地实现（D-D-05）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: shim 导入请求
#   fields: 旧路径 import zephyr.integration.shared.events.event_bus_upgrade
#   code: L28-32 from-import
# 层: 算法
# - id: A1
#   name_zh: 真源透传
#   name_en: ssot_reexport
#   intro: 无逻辑——三个符号从 zephyr.shared.events 真源原样再导出
# 层: 输出
# - id: O1
#   name_zh: 兼容符号
#   name_en: compat_symbols
#   intro: EventBusUpgrader / EventSchema / EventVersionError
#   downstream: 存量旧路径消费者
# [/ALGO_FLOW]
# 边: I1 --> A1 ; A1 --> O1
"""

from typing import Final

from zephyr.shared.events.event_bus_upgrade import (
    EventBusUpgrader,
    EventSchema,
    EventVersionError,
)

__all__: Final = [
    "EventBusUpgrader",
    "EventSchema",
    "EventVersionError",
]
