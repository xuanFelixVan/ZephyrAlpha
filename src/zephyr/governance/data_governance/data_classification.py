# [BLUEPRINT] SRC-030 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.data_governance.data_classification
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.data_governance.__init__
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
# [A_module] module_id=MOD-GOV_data_classification | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Final
from enum import Enum

from pydantic import BaseModel, Field


class DataLevel(str, Enum):
    L1_PUBLIC = "L1_PUBLIC"
    L2_INTERNAL = "L2_INTERNAL"
    L3_CONFIDENTIAL = "L3_CONFIDENTIAL"
    L4_RESTRICTED = "L4_RESTRICTED"


class LevelAttributes(BaseModel):
    level: DataLevel
    label: str
    encryption_required: bool
    access_control: list[str] = Field(default_factory=list)
    audit_log: bool
    retention_days: int
    examples: list[str] = Field(default_factory=list)


DATA_CLASSIFICATION: Final[dict[DataLevel, LevelAttributes]] = {
    DataLevel.L1_PUBLIC: LevelAttributes(
        level=DataLevel.L1_PUBLIC,
        label="Public — 公开数据",
        encryption_required=False,
        access_control=[],
        audit_log=False,
        retention_days=0,
        examples=["README", "公共文档", "开源代码"],
    ),
    DataLevel.L2_INTERNAL: LevelAttributes(
        level=DataLevel.L2_INTERNAL,
        label="Internal — 内部数据",
        encryption_required=False,
        access_control=["role:developer"],
        audit_log=False,
        retention_days=365,
        examples=["蓝图文档", "施工日志", "测试用例"],
    ),
    DataLevel.L3_CONFIDENTIAL: LevelAttributes(
        level=DataLevel.L3_CONFIDENTIAL,
        label="Confidential — 机密数据",
        encryption_required=True,
        access_control=["role:developer", "role:owner"],
        audit_log=True,
        retention_days=1825,
        examples=["策略参数", "因子定义", "回测结果"],
    ),
    DataLevel.L4_RESTRICTED: LevelAttributes(
        level=DataLevel.L4_RESTRICTED,
        label="Restricted — 受限数据",
        encryption_required=True,
        access_control=["role:owner"],
        audit_log=True,
        retention_days=3650,
        examples=["API密钥", "交易凭证", "合规审计轨迹"],
    ),
}

LEVEL_ORDER: Final[dict[DataLevel, int]] = {
    DataLevel.L1_PUBLIC: 1,
    DataLevel.L2_INTERNAL: 2,
    DataLevel.L3_CONFIDENTIAL: 3,
    DataLevel.L4_RESTRICTED: 4,
}


def get_level(level: DataLevel) -> LevelAttributes | None:
    return DATA_CLASSIFICATION.get(level)


def classify(self_level: DataLevel, target_level: DataLevel) -> bool:
    """检查 self_level 是否有权限访问 target_level 的数据。"""
    self_order = LEVEL_ORDER.get(self_level, 0)
    target_order = LEVEL_ORDER.get(target_level, 0)
    return self_order >= target_order


def max_level_from_list(levels: list[DataLevel]) -> DataLevel:
    """从列表中返回最高安全级别。"""
    # 5.106.7 修复: 空列表时 max() 抛 ValueError。公开函数需空集保护,
    # 默认返回 PUBLIC(最低安全级别,失败开放语义)。
    if not levels:
        return DataLevel.PUBLIC
    return max(levels, key=lambda l: LEVEL_ORDER.get(l, 0))
