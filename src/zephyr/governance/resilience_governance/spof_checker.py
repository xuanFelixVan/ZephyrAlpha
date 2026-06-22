# [A_module] module_id=MOD-GOV_spof_checker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-074 | docs/03_modules/_domain-governance/blueprint.md | §

# [MODULE] zephyr.governance.spof_checker

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class SPOFType(str, Enum):
    BROKER = "BROKER"
    DATA_SOURCE = "DATA_SOURCE"
    LLM_MODEL = "LLM_MODEL"
    OWNER = "OWNER"


class SPOFReport(BaseModel):
    spof_type: SPOFType
    current: str
    risk_level: str
    backup: list[str] = Field(default_factory=list)
    mitigated: bool = False


SPOF_CHECKS: dict[SPOFType, SPOFReport] = {
    SPOFType.BROKER: SPOFReport(
        spof_type=SPOFType.BROKER,
        current="单一经纪商API",
        risk_level="CRITICAL",
        backup=["多经纪商备份", "应急平仓"],
        mitigated=True,
    ),
    SPOFType.DATA_SOURCE: SPOFReport(
        spof_type=SPOFType.DATA_SOURCE,
        current="单一数据源",
        risk_level="CRITICAL",
        backup=["双源交叉验证"],
        mitigated=True,
    ),
    SPOFType.LLM_MODEL: SPOFReport(
        spof_type=SPOFType.LLM_MODEL,
        current="单LLM模型",
        risk_level="HIGH",
        backup=["多模型路由", "Fallback策略"],
        mitigated=True,
    ),
    SPOFType.OWNER: SPOFReport(
        spof_type=SPOFType.OWNER,
        current="Owner离线",
        risk_level="MEDIUM",
        backup=["冻结模式", "分级响应"],
        mitigated=True,
    ),
}


def check_spof(spof_type: SPOFType) -> SPOFReport:
    return SPOF_CHECKS.get(spof_type, SPOFReport(spof_type=spof_type, current="UNKNOWN", risk_level="UNKNOWN"))


def all_mitigated() -> bool:
    return all(r.mitigated for r in SPOF_CHECKS.values())
