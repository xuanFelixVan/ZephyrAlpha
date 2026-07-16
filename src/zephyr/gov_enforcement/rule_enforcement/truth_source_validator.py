# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.truth_source_validator
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES] zephyr.gov_audit.bridge; zephyr.shared.schemas
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_truth_source_validator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测

"""
真源优先级裁决器（Truth Source Validator）

依据：MOD-MASTER-002 蓝图 §零之零 真源优先级宪章
实现 5 级优先级链：Tier 0(本蓝图) -> Tier 1(architecture_model YAML)
-> Tier 2(模块蓝图) -> Tier 3(策略标准文档) -> Tier 4(实际代码)

功能：
1. 检测多文档源对同一事实的不同定义
2. 按优先级表确定权威源并裁决
3. 自动生成 DOC_INCONSISTENCY Finding
4. 阻止 AI agent 自行修改权威源
"""

from __future__ import annotations

from typing import Final
import hashlib
import logging
from datetime import UTC, datetime
from enum import IntEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, model_validator

from zephyr.gov_audit.bridge import write_to_core
from zephyr.shared.schema.schemas import AuditFinding, AuditSeverity

logger = logging.getLogger(__name__)


class TruthTier(IntEnum):
    TIER_0 = 0
    TIER_1 = 1
    TIER_2 = 2
    TIER_3 = 3
    TIER_4 = 4


TIER_LABELS: Final[dict[TruthTier, str]] = {
    TruthTier.TIER_0: "本蓝图 MOD-MASTER_BLUEPRINT（跨系统集成契约）",
    TruthTier.TIER_1: "architecture_model/layers/{module}.yaml（单模块结构定义）",
    TruthTier.TIER_2: "docs/03_modules/{layer}/blueprint.md（模块级实现指引）",
    TruthTier.TIER_3: "docs/01_policies_and_standards/（通用规范与策略）",
    TruthTier.TIER_4: "实际代码（运行时现实）",
}

TIER_ORDER: Final[tuple[TruthTier, ...]] = (
    TruthTier.TIER_0,
    TruthTier.TIER_1,
    TruthTier.TIER_2,
    TruthTier.TIER_3,
    TruthTier.TIER_4,
)


def _classify_path(path: str) -> TruthTier:
    normalized = path.replace("\\", "/").lower()

    if "_master-blueprint" in normalized and "blueprint.md" in normalized:
        return TruthTier.TIER_0
    if "architecture_model/layers/" in normalized and normalized.endswith(".yaml"):
        return TruthTier.TIER_1
    if "docs/03_modules/" in normalized and normalized.endswith("blueprint.md"):
        return TruthTier.TIER_2
    if "docs/01_policies_and_standards/" in normalized:
        return TruthTier.TIER_3
    return TruthTier.TIER_4


class TruthClaim(BaseModel):
    fact_id: str = Field(min_length=1, description="事实标识符，如 'TaskCard.field_count'")
    value: object
    source_path: str = Field(min_length=1)
    source_line: int | None = None
    tier: TruthTier

    @model_validator(mode="after")
    def _auto_classify_tier(self) -> TruthClaim:
        if self.tier is None:
            object.__setattr__(self, "tier", _classify_path(self.source_path))
        return self


class TruthConflict(BaseModel):
    fact_id: str
    claims: list[TruthClaim]
    winner: TruthClaim
    loser: TruthClaim
    resolved_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AuditLogEntry(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    action: str
    target_path: str
    agent_id: str
    result: str
    reason: str = ""


class TruthSourceValidator:
    def __init__(self, project_root: str | None = None):
        self._project_root = Path(project_root) if project_root else Path.cwd()
        self._audit_log: list[AuditLogEntry] = []
        self._conflicts: list[TruthConflict] = []

    @property
    def project_root(self) -> Path:
        return self._project_root

    def classify_source(self, source_path: str) -> TruthTier:
        return _classify_path(source_path)

    def resolve(self, claims: list[TruthClaim]) -> TruthConflict | None:
        if len(claims) < 2:
            return None

        fact_id = claims[0].fact_id
        sorted_claims = sorted(claims, key=lambda c: c.tier.value)

        winner = sorted_claims[0]
        loser_candidates = [c for c in sorted_claims if c.tier != winner.tier and c.value != winner.value]

        if not loser_candidates:
            return None

        loser = loser_candidates[0]
        conflict = TruthConflict(
            fact_id=fact_id,
            claims=sorted_claims,
            winner=winner,
            loser=loser,
        )
        self._conflicts.append(conflict)
        return conflict

    def resolve_fact(self, fact_id: str, claims: list[TruthClaim]) -> object | None:
        conflict = self.resolve(claims)
        if conflict is None:
            if claims:
                return claims[0].value
            return None
        return conflict.winner.value

    def generate_finding(
        self,
        conflict: TruthConflict,
        session_id: str | None = None,
    ) -> AuditFinding:
        description = (
            f"文档不一致：{conflict.fact_id} — "
            f"权威源 {TIER_LABELS.get(conflict.winner.tier, f'Tier {conflict.winner.tier.value}')} "
            f"({conflict.winner.source_path}) 定义为 {conflict.winner.value!r}，"
            f"但 {TIER_LABELS.get(conflict.loser.tier, f'Tier {conflict.loser.tier.value}')} "
            f"({conflict.loser.source_path}) 定义为 {conflict.loser.value!r}。"
            f"裁决：以 Tier {conflict.winner.tier.value} 为准。"
        )

        finding_id = self._make_finding_id(conflict)
        return AuditFinding(
            finding_id=finding_id,
            severity=AuditSeverity.P2,
            description=description[:1000],
            file_path=conflict.loser.source_path,
            suggestion=(
                f"将 {conflict.loser.source_path} 中的 {conflict.fact_id} "
                f"从 {conflict.loser.value!r} 更新为 {conflict.winner.value!r}，"
                f"或创建 Finding 记录不一致"
            ),
        )

    @staticmethod
    def _make_finding_id(conflict: TruthConflict) -> str:
        digest = hashlib.sha256(
            f"{conflict.fact_id}:{conflict.winner.source_path}:{conflict.winner.value}".encode()
        ).hexdigest()[:8]
        return f"DOC-{digest.upper()}"

    def guard_modification(
        self,
        target_path: str,
        agent_id: str,
        proposed_change: str = "",
    ) -> bool:
        tier = self.classify_source(target_path)

        if tier in (TruthTier.TIER_0, TruthTier.TIER_1):
            self._audit_log.append(
                AuditLogEntry(
                    action="BLOCK_MODIFICATION",
                    target_path=target_path,
                    agent_id=agent_id,
                    result="BLOCKED",
                    reason=f"禁止修改 Tier {tier.value} 权威源 ({TIER_LABELS[tier]})",
                )
            )
            write_to_core(
                "truth_source_blocked",
                {
                    "target_path": target_path,
                    "agent_id": agent_id,
                    "tier": tier.value,
                },
            )
            logger.warning(
                "BLOCKED: agent=%s 尝试修改 Tier %d 权威源 %s",
                agent_id,
                tier.value,
                target_path,
            )
            return False

        self._audit_log.append(
            AuditLogEntry(
                action="ALLOW_MODIFICATION",
                target_path=target_path,
                agent_id=agent_id,
                result="ALLOWED",
                reason=f"Tier {tier.value} 允许修改",
            )
        )
        return True

    def audit_log(self) -> list[AuditLogEntry]:
        return list(self._audit_log)

    def get_findings(self) -> list[AuditFinding]:
        return [self.generate_finding(c) for c in self._conflicts]

    def resolve_all(self, claims_by_fact: dict[str, list[TruthClaim]]) -> list[TruthConflict]:
        results: list[TruthConflict] = []
        for fact_id, claims in claims_by_fact.items():
            conflict = self.resolve(claims)
            if conflict:
                results.append(conflict)
        return results
