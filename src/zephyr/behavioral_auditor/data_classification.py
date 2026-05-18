# [BLUEPRINT] MOD-INF-023 | docs/03_modules/l01_infrastructure/drift-detector/blueprint.md
# [MODULE] zephyr.behavioral_auditor.data_classification
# [INVARIANTS] Git-native漂移检测;自动对账;漂移预算
# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/drift-detector/blueprint.md;src/zephyr/behavioral_auditor/__init__.py
# [CONSUMERS] MOD-INF-007;MOD-INF-021;MOD-INF-020
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/test_behavioral_auditor/
from __future__ import annotations

from enum import Enum
from typing import Optional

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


DATA_CLASSIFICATION: dict[DataLevel, LevelAttributes] = {
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

LEVEL_ORDER: dict[DataLevel, int] = {
    DataLevel.L1_PUBLIC: 1,
    DataLevel.L2_INTERNAL: 2,
    DataLevel.L3_CONFIDENTIAL: 3,
    DataLevel.L4_RESTRICTED: 4,
}


def get_level(level: DataLevel) -> Optional[LevelAttributes]:
    return DATA_CLASSIFICATION.get(level)


def classify(self_level: DataLevel, target_level: DataLevel) -> bool:
    """检查 self_level 是否有权限访问 target_level 的数据。"""
    self_order = LEVEL_ORDER.get(self_level, 0)
    target_order = LEVEL_ORDER.get(target_level, 0)
    return self_order >= target_order


def max_level_from_list(levels: list[DataLevel]) -> DataLevel:
    """从列表中返回最高安全级别。"""
    return max(levels, key=lambda l: LEVEL_ORDER.get(l, 0))
