# [BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic-auditor/blueprint.md
# [MODULE] zephyr.governance.semantic_audit.spec_auditor
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.semantic_audit.__init__
# [CONSUMERS] 见蓝图 §4 接口契约
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 蓝图 §4 文件清单与代码双向对齐
# [MODIFY-GUARD] semantic-auditor/blueprint.md; semantic-auditor/__init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SemanticAuditError
# [TESTS] tests/semantic-auditor/
# [A_module] module_id=MOD-GOV_spec_auditor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic-auditor/blueprint.md

G-CT-007 — Audit.record_agent_spec() 记录 Agent Spec 注册与变更.

"""

from __future__ import annotations

import importlib
from datetime import UTC, datetime
from typing import Any

_mod = importlib.import_module("zephyr.autonomy_core.skill_rbac_registry")
AgentCapability = _mod.AgentCapability


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
