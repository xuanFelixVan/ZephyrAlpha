# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_model
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_skill_model | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class SkillTier(str, Enum):
    L0_CONSTITUTION = "L0"
    L1_DOMAIN = "L1"
    L2_ROLE = "L2"
    L3_COLD_MEMORY = "L3"


class SkillType(str, Enum):
    DOMAIN = "domain"
    ROLE = "role"


class SkillStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    RETIRED = "retired"
    REMOVED = "removed"


class ProgressiveLevel(str, Enum):
    L1_METADATA = "L1"
    L2_BODY = "L2"
    L3_REFERENCES = "L3"


class SkillModel(BaseModel):
    skill_id: str = Field(..., pattern=r"^SKILL-[A-Z]{3}-[A-Z]{2,3}-\d{3}$")
    name: str
    description: str
    skill_type: SkillType
    tier: SkillTier
    status: SkillStatus = SkillStatus.ACTIVE
    allowed_tools: list[str]
    model_hint: str | None = None
    freshness_score: float = Field(default=100.0, ge=0.0, le=100.0)
    last_validated: datetime | None = None
    version: str = "0.1.0"
    token_budget_l1: int = 50
    token_budget_l2: int = 500
    author: str = "factory-agent"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    path: str
    references: list[str] = []
    upstream_modules: list[str] = []
