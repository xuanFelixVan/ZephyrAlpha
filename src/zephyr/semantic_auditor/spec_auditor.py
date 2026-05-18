# [BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic-auditor/blueprint.md

# [MODULE] zephyr.semantic_auditor.spec_auditor

# [INVARIANTS] 蓝图 §4 文件清单与代码双向对齐

# [MODIFY-GUARD] semantic-auditor/blueprint.md; semantic_auditor/__init__.py __all__

# [CONSUMERS] 见蓝图 §4 接口契约

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] SemanticAuditError

# [TESTS] tests/semantic_auditor/

"""[BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic-auditor/blueprint.md

G-CT-007 — Audit.record_agent_spec() 记录 Agent Spec 注册与变更.

"""


from __future__ import annotations





from datetime import datetime, timezone


from typing import Any





from zephyr.agent_spec.registry import AgentCapability








def record_agent_spec(capability: AgentCapability) -> dict[str, Any]:


    caps = getattr(capability, "capabilities", getattr(capability, "claimed_capabilities", []))


    return {


        "event_type": "AGENT_SPEC_REGISTERED",


        "agent_id": capability.agent_id,


        "claimed_capabilities": caps,


        "model_provider": getattr(capability, "model_provider", "unknown"),


        "version": getattr(capability, "version", "0.0.0"),


        "timestamp": datetime.now(timezone.utc).isoformat(),


    }


