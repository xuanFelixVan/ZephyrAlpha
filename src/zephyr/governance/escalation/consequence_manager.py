# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.escalation.consequence_manager
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] MOD-INF-027;MOD-INF-020;MOD-INF-018
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 升级裁决;四级约束;Kill Switch
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md;src/zephyr/escalation-engine/__init__.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] EscalationError;TimeoutError
# [TESTS] tests/test_escalation_engine/
# [A_module] module_id=MOD-RES_consequence_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, Field


class ConsequenceSeverity(str, Enum):
    DEGRADED = "DEGRADED"
    SEVERE = "SEVERE"
    CRITICAL = "CRITICAL"


class ConsequenceDeclaration(BaseModel):
    con_id: str
    scenario: str
    bluf: str
    severity: ConsequenceSeverity
    t_min_to_recover: int
    escalation_chain: list[str] = Field(default_factory=list)
    recovery_procedure: str = ""
    declared_at: str | None = None
    resolved_at: str | None = None

    @property
    def is_active(self) -> bool:
        return self.declared_at is not None and self.resolved_at is None

    def declare(self) -> None:
        self.declared_at = datetime.now(UTC).isoformat()

    def resolve(self) -> None:
        self.resolved_at = datetime.now(UTC).isoformat()


CONSEQUENCE_REGISTRY: dict[str, ConsequenceDeclaration] = {
    "alpha_unavailable": ConsequenceDeclaration(
        con_id="alpha_unavailable",
        scenario="Alpha 因子管线不可用",
        bluf="BLUF: Alpha生成管线中断——模型输出不可信，所有策略取号已暂停。恢复中——预计 <30min。",
        severity=ConsequenceSeverity.CRITICAL,
        t_min_to_recover=30,
        escalation_chain=["AI自修复", "Session重建", "Owner通知", "手动回滚"],
        recovery_procedure="1.验证数据源 2.重启因子工厂 3.回测验证 4.恢复取号",
    ),
    "data_vendor_outage": ConsequenceDeclaration(
        con_id="data_vendor_outage",
        scenario="数据供应商停机",
        bluf="BLUF: 市场数据供应商不可达——已切换到备用源。延迟 <5s，精度降低。监控中。",
        severity=ConsequenceSeverity.SEVERE,
        t_min_to_recover=15,
        escalation_chain=["自动切换备用源", "验证数据一致性", "Owner确认", "供应商联系"],
        recovery_procedure="1.自动fallback 2.数据校验 3.增量补录 4.切换回主源",
    ),
    "session_loss": ConsequenceDeclaration(
        con_id="session_loss",
        scenario="AI Session 丢失",
        bluf="BLUF: 当前AI对话Session异常终止——checkpoint自动恢复中。施工进度可能滞后 ≤2 cards。",
        severity=ConsequenceSeverity.DEGRADED,
        t_min_to_recover=5,
        escalation_chain=["checkpoint恢复", "journal重建", "Session重建"],
        recovery_procedure="1.读checkpoint 2.读journal 3.重建上下文 4.继续施工",
    ),
    "gate_block": ConsequenceDeclaration(
        con_id="gate_block",
        scenario="门禁阻断",
        bluf="BLUF: 安全门禁检测到异常——Pipeline已暂停。需Owner审查后手动放行。",
        severity=ConsequenceSeverity.SEVERE,
        t_min_to_recover=60,
        escalation_chain=["自动诊断", "AI风险评估", "Owner审查", "手动放行"],
        recovery_procedure="1.读取gate log 2.五因分析 3.修复根因 4.Owner放行",
    ),
}


def get_consequence(con_id: str) -> ConsequenceDeclaration | None:
    return CONSEQUENCE_REGISTRY.get(con_id)


def activate_consequence(con_id: str) -> ConsequenceDeclaration | None:
    cd = CONSEQUENCE_REGISTRY.get(con_id)
    if cd is not None:
        cd.declare()
    return cd


def list_active() -> list[ConsequenceDeclaration]:
    return [c for c in CONSEQUENCE_REGISTRY.values() if c.is_active]


def list_by_severity(severity: ConsequenceSeverity) -> list[ConsequenceDeclaration]:
    return [c for c in CONSEQUENCE_REGISTRY.values() if c.severity == severity]
