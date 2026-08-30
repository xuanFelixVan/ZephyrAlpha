# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] zephyr.gov_audit.spec_auditor
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.agent_spec.registry
# [CONSUMERS] zephyr.gov_audit
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] see blueprint MOD-INF-020
# [MODIFY-GUARD] __init__.py
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] AuditTrailError
# [TESTS]
# [A_module] module_id=MOD-INF-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: capability 参数
#   fields: 参数 capability，类型注解 AgentCapability
#   code: spec_auditor.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① record_agent_spec
#   name_en: record_agent_spec
#   intro: record_agent_spec(capability) 源码 L56-L66
#   desc: 源码 L56-L66
#   inputs: capability
#   outputs: dict[str, Any]
# 层: 输出
# - id: O1
#   name_zh: dict[str, Any]
#   name_en: dict[str, Any]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.gov_audit
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from zephyr.governance.agent_spec.registry import AgentCapability


def record_agent_spec(capability: AgentCapability) -> dict[str, Any]:
    caps = getattr(capability, "capabilities", getattr(capability, "claimed_capabilities", []))

    return {
        "event_type": "AGENT_SPEC_REGISTERED",
        "agent_id": capability.agent_id,
        "claimed_capabilities": caps,
        "model_provider": getattr(capability, "model_provider", "unknown"),
        "version": getattr(capability, "version", "0.0.0"),
        "timestamp": datetime.now(UTC).isoformat(),
    }
