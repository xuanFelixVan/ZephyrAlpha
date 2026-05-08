from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, List
from datetime import datetime


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
    allowed_tools: List[str]
    model_hint: Optional[str] = None
    freshness_score: float = Field(default=100.0, ge=0.0, le=100.0)
    last_validated: Optional[datetime] = None
    version: str = "0.1.0"
    token_budget_l1: int = 50
    token_budget_l2: int = 500
    author: str = "factory-agent"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    path: str
    references: List[str] = []
    upstream_modules: List[str] = []
