# [BLUEPRINT] MOD-L10-001 | docs/03_modules/_domain_compliance/blueprint.md
# [MODULE] zephyr.governance.implementations.default_security_gateway
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.security_governance.default_security_gateway
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L10-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# Re-export shim: canonical source = zephyr.governance.security_governance.default_security_gateway (SSoT 收敛，消除多真源)

"""default_security_gateway — re-export shim（真源 zephyr.governance.security_governance.default_security_gateway）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: shim 导入请求
#   fields: import zephyr.governance.implementations.default_security_gateway
#   code: L21-25 from-import
# 层: 算法
# - id: A1
#   name_zh: 真源透传
#   name_en: ssot_reexport
#   intro: 无逻辑——三个符号从 security_governance 真源原样再导出
# 层: 输出
# - id: O1
#   name_zh: 兼容符号
#   name_en: compat_symbols
#   intro: DefaultSecurityGateway / ScanFinding / SecurityContext
#   downstream: 存量旧路径消费者
# [/ALGO_FLOW]
# 边: I1 --> A1 ; A1 --> O1
"""

from __future__ import annotations

from zephyr.governance.security_governance.default_security_gateway import (
    DefaultSecurityGateway,
    ScanFinding,
    SecurityContext,
)

__all__ = [
    "DefaultSecurityGateway",
    "ScanFinding",
    "SecurityContext",
]
