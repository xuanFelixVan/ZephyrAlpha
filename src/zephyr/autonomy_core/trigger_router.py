# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.trigger_router
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-AUTONOMY_stage_router | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

import re
from enum import Enum
from typing import Optional


class ConstructionStage(str, Enum):
    IDEA = "idea"
    PRE_AUDIT = "pre_audit"
    BLUEPRINT = "blueprint"
    CONSTRUCTION = "construction"
    VERIFICATION = "verification"
    POST_AUDIT = "post_audit"

    @classmethod
    def from_label(cls, label: str) -> Optional["ConstructionStage"]:
        mapping = {
            "想法": cls.IDEA,
            "草稿": cls.IDEA,
            "审计（施工前）": cls.PRE_AUDIT,
            "审计(施工前)": cls.PRE_AUDIT,
            "蓝图": cls.BLUEPRINT,
            "设计": cls.BLUEPRINT,
            "施工": cls.CONSTRUCTION,
            "实现": cls.CONSTRUCTION,
            "验收": cls.VERIFICATION,
            "验证": cls.VERIFICATION,
            "审计（施工后）": cls.POST_AUDIT,
            "审计(施工后)": cls.POST_AUDIT,
        }
        return mapping.get(label)


class TriggerRouter:
    STAGE_ROUTING = {
        ConstructionStage.IDEA: {
            "role": "architect",
            "domain_default": "master-blueprint",
        },
        ConstructionStage.PRE_AUDIT: {
            "role": "governor",
            "domain_default": "gate-engine",
        },
        ConstructionStage.BLUEPRINT: {
            "role": "architect",
            "domain_match_mode": "topic",
        },
        ConstructionStage.CONSTRUCTION: {
            "role": "implementer",
            "domain_match_mode": "module",
        },
        ConstructionStage.VERIFICATION: {
            "role": "governor",
            "domain_match_mode": "module",
        },
        ConstructionStage.POST_AUDIT: {
            "role": "governor",
            "domain_default": "drift-detector",
        },
    }

    TASK_ROUTING: list[tuple[str, str, str]] = [
        (r"database|migration|sql|atm", "database-specialist", "implementer"),
        (r"mcp\s*(?:server|tool|protocol)?", "mcp-specialist", "implementer"),
        (r"context|pipeline", "context-specialist", "implementer"),
        (r"feedback|loop", "feedback-specialist", "implementer"),
        (r"gate|rule|policy", "gate-specialist", "governor"),
        (r"permission|rbac|acl", "agent-specialist", "governor"),
        (r"blueprint", "master-blueprint", "architect"),
        (r"audit|compliance|governance|drift", "drift-detector", "governor"),
        (r"knowledge|k[ea]\b|kb", "knowledge-specialist", "implementer"),
    ]

    DEFAULT = {"role": "implementer", "domain_default": None}

    def route(
        self,
        stage: ConstructionStage | None,
        task_description: str,
    ) -> tuple[str, str | None]:
        role: str | None = None
        domain: str | None = None

        domain_override = self._match_task_routing(task_description)
        if domain_override:
            domain, role = domain_override

        if stage is not None and stage in self.STAGE_ROUTING:
            stage_config = self.STAGE_ROUTING[stage]
            if role is None:
                role = stage_config.get("role")
            if domain is None:
                domain = stage_config.get("domain_default")
                if domain is None and "domain_match_mode" in stage_config:
                    domain = self._match_domain(task_description)

        if role is None:
            role = self.DEFAULT["role"]
        if domain is None:
            domain = self.DEFAULT["domain_default"]

        return (role, domain)

    def _match_task_routing(self, task_description: str) -> tuple[str, str] | None:
        description_lower = task_description.lower()
        for pattern, domain, role in self.TASK_ROUTING:
            if re.search(pattern, description_lower):
                return (domain, role)
        return None

    def _match_domain(self, task_description: str) -> str | None:
        match = self._match_task_routing(task_description)
        return match[0] if match else None
