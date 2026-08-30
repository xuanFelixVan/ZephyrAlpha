# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.financial_governance.risk_matrix
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] MOD-INF-027;MOD-INF-020;MOD-INF-018
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 升级裁决;四级约束;Kill Switch
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md;src/zephyr/governance/escalation/__init__.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] EscalationError;TimeoutError
# [TESTS] tests/test_escalation_engine/
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: category 参数
#   fields: 参数 category，类型注解 RiskCategory
#   code: risk_matrix.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: risk_a 参数
#   fields: 参数 risk_a，类型注解 RiskItem
#   code: risk_matrix.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: risk_b 参数
#   fields: 参数 risk_b，类型注解 RiskItem
#   code: risk_matrix.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: flag 参数
#   fields: 参数 flag，类型注解 str
#   code: risk_matrix.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① get_risk
#   name_en: get_risk
#   intro: get_risk(category) 源码 L202-L203
#   desc: 源码 L202-L203
#   inputs: category
#   outputs: RiskItem | None
# - id: A2
#   name_zh: ② risks_sorted_by_level
#   name_en: risks_sorted_by_level
#   intro: risks_sorted_by_level() 源码 L206-L207
#   desc: 源码 L206-L207
#   inputs: 无参数
#   outputs: list[RiskItem]
# - id: A3
#   name_zh: ③ get_interactions
#   name_en: get_interactions
#   intro: get_interactions(risk_a, risk_b) 源码 L210-L211
#   desc: 源码 L210-L211
#   inputs: risk_a risk_b
#   outputs: bool
# - id: A4
#   name_zh: ④ flagged_risks
#   name_en: flagged_risks
#   intro: flagged_risks(flag) 源码 L214-L215
#   desc: 源码 L214-L215
#   inputs: flag
#   outputs: list[RiskItem]
#   （注：A4 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: RiskItem | None
#   name_en: RiskItem | None
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-INF-027;MOD-INF-020;MOD-INF-018
# - id: O2
#   name_zh: list[RiskItem]
#   name_en: list[RiskItem]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-INF-027;MOD-INF-020;MOD-INF-018
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> O1
"""

from __future__ import annotations

from enum import Enum
from typing import Final

from pydantic import BaseModel, Field


class RiskCategory(str, Enum):
    OPERATIONAL = "OPERATIONAL"
    DATA = "DATA"
    LEGAL_COMPLIANCE = "LEGAL_COMPLIANCE"
    ISOLATION = "ISOLATION"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskItem(BaseModel):
    name: str
    category: RiskCategory
    likelihood: int = Field(ge=1, le=5)
    impact: int = Field(ge=1, le=5)
    risk_level: RiskLevel
    description: str
    mitigation: str
    mitigator: str
    trigger_flags: list[str] = Field(default_factory=list)
    related_risks: list[str] = Field(default_factory=list)

    @property
    def risk_score(self) -> int:
        return self.likelihood * self.impact


def _compute_risk_level(likelihood: int, impact: int) -> RiskLevel:
    score = likelihood * impact
    if score >= 20:
        return RiskLevel.CRITICAL
    if score >= 12:
        return RiskLevel.HIGH
    if score >= 6:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


RISK_MATRIX: Final[dict[RiskCategory, RiskItem]] = {
    RiskCategory.OPERATIONAL: RiskItem(
        name="操作风险",
        category=RiskCategory.OPERATIONAL,
        likelihood=4,
        impact=5,
        risk_level=_compute_risk_level(4, 5),
        description="AI/AI为主的人为错误/系统错误/流程失败/外部事件",
        mitigation="双AI审查+门禁系统+Session永续+回滚协议",
        mitigator="GateController + DualAI Pipeline",
        trigger_flags=["build_failure", "session_crash", "lock_conflict", "pipeline_stall"],
        related_risks=["DATA", "ISOLATION"],
    ),
    RiskCategory.DATA: RiskItem(
        name="数据风险",
        category=RiskCategory.DATA,
        likelihood=3,
        impact=4,
        risk_level=_compute_risk_level(3, 4),
        description="供应商停机/数据质量/备份失效",
        mitigation="多源冗余+数据质量SPC+定期恢复演练",
        mitigator="DataPipeline Orchestrator + ObservableStack",
        trigger_flags=["vendor_outage", "quality_drift", "backup_failure", "partition_loss"],
        related_risks=["OPERATIONAL", "LEGAL_COMPLIANCE"],
    ),
    RiskCategory.LEGAL_COMPLIANCE: RiskItem(
        name="法律与合规风险",
        category=RiskCategory.LEGAL_COMPLIANCE,
        likelihood=2,
        impact=5,
        risk_level=_compute_risk_level(2, 5),
        description="法规违规/合同违约/KYC/AML",
        mitigation="合规门禁+自动审计轨迹+法律审查清单",
        mitigator="GateController + Compliance Audit",
        trigger_flags=["reg_change", "audit_flag", "jurisdiction_mismatch", "kyc_expiry"],
        related_risks=["DATA"],
    ),
    RiskCategory.ISOLATION: RiskItem(
        name="孤立风险",
        category=RiskCategory.ISOLATION,
        likelihood=3,
        impact=3,
        risk_level=_compute_risk_level(3, 3),
        description="系统孤岛/依赖孤岛/知识孤岛——类比微服务架构反模式",
        mitigation="统一蓝图+全局拓扑图+跨域dispatch",
        mitigator="depgraph（拓扑真源）+ agent_dispatch.py",
        trigger_flags=["module_orphan", "dep_silo", "ctx_gap", "knowledge_silo"],
        related_risks=["OPERATIONAL"],
    ),
}

RISK_LEVEL_ORDER: Final[dict[RiskLevel, int]] = {
    RiskLevel.LOW: 0,
    RiskLevel.MEDIUM: 1,
    RiskLevel.HIGH: 2,
    RiskLevel.CRITICAL: 3,
}


def get_risk(category: RiskCategory) -> RiskItem | None:
    return RISK_MATRIX.get(category)


def risks_sorted_by_level() -> list[RiskItem]:
    return sorted(RISK_MATRIX.values(), key=lambda r: (-RISK_LEVEL_ORDER.get(r.risk_level, 0), -r.risk_score))


def get_interactions(risk_a: RiskItem, risk_b: RiskItem) -> bool:
    return risk_a.name in risk_b.related_risks or risk_b.name in risk_a.related_risks


def flagged_risks(flag: str) -> list[RiskItem]:
    return [r for r in RISK_MATRIX.values() if flag in r.trigger_flags]
