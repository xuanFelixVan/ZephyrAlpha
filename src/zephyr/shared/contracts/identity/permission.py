# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.contracts.identity.permission
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.security.access_control.guards.permission_guard;zephyr.infrastructure.escalation;zephyr.governance;zephyr.integration.mcp
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 权限判定枚举不可扩展
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT]
# [TESTS] tests/agent_rbac/test_rbac_core.py; tests/escalation/test_escalation_gov_rbac_bridge.py  # 2026-09-05 STEWARD B20 重锚：AI-00 修复脚本 src. 前缀 bug 漏网（AST/patch 直查 2 个测试）
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
# [ALGO_FLOW] external: docs/03_modules/_domain_shared/algo_flow/contracts/identity/permission.yaml
"""

from dataclasses import dataclass, field
from enum import Enum


class GuardDecision(str, Enum):
    ALLOW = "ALLOW"
    AUTO_GUARD = "AUTO_GUARD"
    BLOCKED = "BLOCKED"


@dataclass
class GuardResult:
    # P1-3: 合并 security 版 permission_guard.py 的 target 字段（原 security 版独有）
    decision: GuardDecision = GuardDecision.ALLOW
    layer: str = ""
    reason: str = ""
    rule_id: str = ""
    target: str = ""
    audit_context: dict = field(default_factory=dict)
    timing_ns: int = 0
