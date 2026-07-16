# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.integration.pipeline_bridge
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
# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
PipelineSkillBridge — Agent Spec -> Pipeline 双向桥接

职责:
  1. 接收 TaskCard -> 通过 TriggerRouter 匹配 Domain Skill + Role Skill
  2. 通过 SkillLoader.progressive_load 加载对应 Skill
  3. 返回 SkillInjectionResult 供 Pipeline Module 执行时注入

用法:
    bridge = PipelineSkillBridge()
    result = bridge.inject_for_task(task_description="修改数据库模型", stage="construction")
    # -> 加载 database-specialist + implementer
"""

from __future__ import annotations

from dataclasses import dataclass, field

from zephyr.autonomy_core.skills.skill_loader import SkillLoader
from zephyr.autonomy_core.trigger_router import ConstructionStage, TriggerRouter


@dataclass
class SkillInjectionResult:
    skill_id: str
    domain_skill_id: str | None
    role_skill_id: str | None
    l0_constitution: dict
    l1_domain_meta: dict | None = None
    l1_role_meta: dict | None = None
    l2_domain_body: str = ""
    l2_role_body: str = ""
    token_budget: dict = field(default_factory=dict)
    injection_context: str = ""
    loaded: bool = False

    def to_context_string(self) -> str:
        if not self.loaded:
            return ""
        parts = []
        if self.l2_domain_body:
            parts.append(f"[Domain Skill: {self.domain_skill_id}]\n{self.l2_domain_body}")
        if self.l2_role_body:
            parts.append(f"[Role Skill: {self.role_skill_id}]\n{self.l2_role_body}")
        return "\n\n".join(parts)


class SkillContextInjector:
    def __init__(self, loader: SkillLoader | None = None):
        self._loader = loader or SkillLoader()

    def inject(self, domain_skill_id: str, role_skill_id: str, load_l3: bool = False) -> SkillInjectionResult:
        try:
            domain = self._loader.progressive_load(domain_skill_id)
            role = self._loader.progressive_load(role_skill_id)
            l0 = self._loader.load_l0()
            budget = self._loader.check_token_budget(domain_skill_id, role_skill_id)

            result = SkillInjectionResult(
                skill_id=f"{domain_skill_id}+{role_skill_id}",
                domain_skill_id=domain_skill_id,
                role_skill_id=role_skill_id,
                l0_constitution=l0,
                l1_domain_meta=domain.get("l1"),
                l1_role_meta=role.get("l1"),
                l2_domain_body=domain.get("l2", ""),
                l2_role_body=role.get("l2", ""),
                token_budget=budget,
                loaded=True,
            )
            if load_l3:
                l3_domain = "\n\n".join(domain.get("l3_available", []))
                l3_role = "\n\n".join(role.get("l3_available", []))
                if l3_domain or l3_role:
                    parts = []
                    if result.l2_domain_body:
                        parts.append(f"[Domain Skill: {domain_skill_id}]\n{result.l2_domain_body}")
                    if l3_domain:
                        parts.append(f"[Domain L3 References: {domain_skill_id}]\n{l3_domain}")
                    if result.l2_role_body:
                        parts.append(f"[Role Skill: {role_skill_id}]\n{result.l2_role_body}")
                    if l3_role:
                        parts.append(f"[Role L3 References: {role_skill_id}]\n{l3_role}")
                    result.injection_context = "\n\n".join(parts)
                else:
                    result.injection_context = result.to_context_string()
            else:
                result.injection_context = result.to_context_string()
            return result
        except Exception:
            return SkillInjectionResult(
                skill_id=f"{domain_skill_id}+{role_skill_id}",
                domain_skill_id=domain_skill_id,
                role_skill_id=role_skill_id,
                l0_constitution={},
                loaded=False,
            )

    def inject_single(self, skill_id: str) -> SkillInjectionResult:
        try:
            data = self._loader.progressive_load(skill_id)
            l0 = self._loader.load_l0()

            return SkillInjectionResult(
                skill_id=skill_id,
                domain_skill_id=skill_id,
                role_skill_id=None,
                l0_constitution=l0,
                l1_domain_meta=data.get("l1"),
                l2_domain_body=data.get("l2", ""),
                loaded=True,
            )
        except Exception:
            return SkillInjectionResult(
                skill_id=skill_id,
                domain_skill_id=skill_id,
                role_skill_id=None,
                l0_constitution={},
                loaded=False,
            )


def _resolve_construction_stage(stage_map, stage):
    construction_stage = None
    if stage:
        stage_lower = stage.lower()
        construction_stage = stage_map.get(stage_lower)
        if construction_stage is None:
            for key, val in stage_map.items():
                if key in stage_lower:
                    construction_stage = val
                    break
    return construction_stage


def _find_skill_id(category_skills, name):
    for sid, data in category_skills.items():
        if data.get("name") == name or sid.endswith(name):
            return sid
    return None


class PipelineSkillBridge:
    def __init__(self):
        self._router = TriggerRouter()
        self._injector = SkillContextInjector()
        self._stage_map = {
            "idea": ConstructionStage.IDEA,
            "draft": ConstructionStage.IDEA,
            "pre_audit": ConstructionStage.PRE_AUDIT,
            "blueprint": ConstructionStage.BLUEPRINT,
            "design": ConstructionStage.BLUEPRINT,
            "construction": ConstructionStage.CONSTRUCTION,
            "implement": ConstructionStage.CONSTRUCTION,
            "verification": ConstructionStage.VERIFICATION,
            "verify": ConstructionStage.VERIFICATION,
            "post_audit": ConstructionStage.POST_AUDIT,
            "audit": ConstructionStage.POST_AUDIT,
        }

    def inject_for_task(
        self,
        task_description: str,
        stage: str | None = None,
        load_l3: bool = False,
    ) -> SkillInjectionResult:
        construction_stage = _resolve_construction_stage(self._stage_map, stage)

        role, domain = self._router.route(construction_stage, task_description)

        if domain and role:
            registry = self._injector._loader._load_registry()
            skills = registry.get("skills", {})
            domain_skill_id = _find_skill_id(skills.get("domain", {}), domain)
            role_skill_id = _find_skill_id(skills.get("role", {}), role)

            if domain_skill_id and role_skill_id:
                return self._injector.inject(domain_skill_id, role_skill_id, load_l3=load_l3)
            if domain_skill_id:
                return self._injector.inject_single(domain_skill_id)

        return SkillInjectionResult(
            skill_id="fallback",
            domain_skill_id=None,
            role_skill_id=None,
            l0_constitution=self._injector._loader.load_l0(),
            loaded=False,
        )
