# [A_test] module_id: SRC-TST-2082 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-699 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_truth_source_validator
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""单元测试——真源优先级裁决器（Truth Source Validator）

验证 5 级优先级链裁决正确性：Tier 0 > Tier 1 > Tier 2 > Tier 3 > Tier 4。
至少 10 个测试用例覆盖全部排列组合。
"""


import pytest

from zephyr.gov_enforcement.rule_enforcement.truth_source_validator import (
    TruthClaim,
    TruthSourceValidator,
    TruthTier,
)


@pytest.fixture
def validator():
    return TruthSourceValidator()


class TestClassifySource:
    def test_tier0_master_blueprint(self, validator):
        tier = validator.classify_source("docs/03_modules/_master-blueprint/blueprint.md")
        assert tier == TruthTier.TIER_0

    def test_tier1_architecture_model(self, validator):
        tier = validator.classify_source("architecture_model/layers/b_core.yaml")
        assert tier == TruthTier.TIER_1

    def test_tier2_module_blueprint(self, validator):
        tier = validator.classify_source("docs/03_modules/_domain-infra_ops/escalation-protocol/blueprint.md")
        assert tier == TruthTier.TIER_2

    def test_tier3_policies(self, validator):
        tier = validator.classify_source("docs/01_policies_and_standards/coding-style.md")
        assert tier == TruthTier.TIER_3

    def test_tier4_code(self, validator):
        tier = validator.classify_source("src/zephyr/gov_enforcement/rule_enforcement/gate_engine/gate_engine.py")
        assert tier == TruthTier.TIER_4


class TestConflictResolution:
    def test_tier0_overrides_tier4(self, validator):
        claims = [
            TruthClaim(
                fact_id="TaskCard.field_count",
                value=62,
                source_path="docs/03_modules/_master-blueprint/blueprint.md",
                tier=TruthTier.TIER_0,
            ),
            TruthClaim(
                fact_id="TaskCard.field_count",
                value=74,
                source_path="src/zephyr/shared/schemas.py",
                tier=TruthTier.TIER_4,
            ),
        ]
        conflict = validator.resolve(claims)
        assert conflict is not None
        assert conflict.winner.tier == TruthTier.TIER_0
        assert conflict.winner.value == 62
        assert conflict.loser.tier == TruthTier.TIER_4
        assert conflict.loser.value == 74

    def test_tier0_overrides_tier1(self, validator):
        claims = [
            TruthClaim(
                fact_id="system.boundary",
                value="cross-system",
                source_path="docs/03_modules/_master-blueprint/blueprint.md",
                tier=TruthTier.TIER_0,
            ),
            TruthClaim(
                fact_id="system.boundary",
                value="intra-module",
                source_path="architecture_model/layers/b_core.yaml",
                tier=TruthTier.TIER_1,
            ),
        ]
        conflict = validator.resolve(claims)
        assert conflict is not None
        assert conflict.winner.tier == TruthTier.TIER_0

    def test_tier1_overrides_tier2(self, validator):
        claims = [
            TruthClaim(
                fact_id="module.files",
                value=["a.py", "b.py"],
                source_path="architecture_model/layers/b_core.yaml",
                tier=TruthTier.TIER_1,
            ),
            TruthClaim(
                fact_id="module.files",
                value=["a.py", "b.py", "c.py"],
                source_path="docs/03_modules/_domain-infra_ops/blueprint.md",
                tier=TruthTier.TIER_2,
            ),
        ]
        conflict = validator.resolve(claims)
        assert conflict is not None
        assert conflict.winner.tier == TruthTier.TIER_1

    def test_tier2_overrides_tier3(self, validator):
        claims = [
            TruthClaim(
                fact_id="naming.convention",
                value="snake_case",
                source_path="docs/03_modules/_domain-infra_ops/blueprint.md",
                tier=TruthTier.TIER_2,
            ),
            TruthClaim(
                fact_id="naming.convention",
                value="camelCase",
                source_path="docs/01_policies_and_standards/coding-style.md",
                tier=TruthTier.TIER_3,
            ),
        ]
        conflict = validator.resolve(claims)
        assert conflict is not None
        assert conflict.winner.tier == TruthTier.TIER_2

    def test_tier3_overrides_tier4(self, validator):
        claims = [
            TruthClaim(
                fact_id="max_line_length",
                value=100,
                source_path="docs/01_policies_and_standards/coding-style.md",
                tier=TruthTier.TIER_3,
            ),
            TruthClaim(
                fact_id="max_line_length",
                value=120,
                source_path="src/zephyr/some_module.py",
                tier=TruthTier.TIER_4,
            ),
        ]
        conflict = validator.resolve(claims)
        assert conflict is not None
        assert conflict.winner.tier == TruthTier.TIER_3

    def test_no_conflict_when_same_tier_agree(self, validator):
        claims = [
            TruthClaim(
                fact_id="version",
                value="1.0.0",
                source_path="src/zephyr/module_a.py",
                tier=TruthTier.TIER_4,
            ),
            TruthClaim(
                fact_id="version",
                value="1.0.0",
                source_path="src/zephyr/module_b.py",
                tier=TruthTier.TIER_4,
            ),
        ]
        conflict = validator.resolve(claims)
        assert conflict is None

    def test_single_claim_no_conflict(self, validator):
        claims = [
            TruthClaim(
                fact_id="single.fact",
                value=42,
                source_path="src/zephyr/module.py",
                tier=TruthTier.TIER_4,
            ),
        ]
        conflict = validator.resolve(claims)
        assert conflict is None


class TestFindingGeneration:
    def test_generates_doc_inconsistency_finding(self, validator):
        claims = [
            TruthClaim(
                fact_id="TaskCard.field_count",
                value=62,
                source_path="docs/03_modules/_master-blueprint/blueprint.md",
                tier=TruthTier.TIER_0,
            ),
            TruthClaim(
                fact_id="TaskCard.field_count",
                value=74,
                source_path="src/zephyr/shared/schemas.py",
                tier=TruthTier.TIER_4,
            ),
        ]
        conflict = validator.resolve(claims)
        finding = validator.generate_finding(conflict)
        assert finding is not None
        assert finding.severity.value == "P2"
        assert "TaskCard.field_count" in finding.description
        assert finding.file_path == "src/zephyr/shared/schemas.py"


class TestGuardModification:
    def test_blocks_tier0_modification(self, validator):
        allowed = validator.guard_modification(
            "docs/03_modules/_master-blueprint/blueprint.md",
            agent_id="agent-001",
        )
        assert allowed is False
        assert len(validator.audit_log()) == 1
        assert validator.audit_log()[0].result == "BLOCKED"

    def test_blocks_tier1_modification(self, validator):
        allowed = validator.guard_modification(
            "architecture_model/layers/b_core.yaml",
            agent_id="agent-002",
        )
        assert allowed is False
        assert validator.audit_log()[-1].result == "BLOCKED"

    def test_allows_tier4_modification(self, validator):
        allowed = validator.guard_modification(
            "src/zephyr/some_module.py",
            agent_id="agent-003",
        )
        assert allowed is True
        assert validator.audit_log()[-1].result == "ALLOWED"


class TestResolveAll:
    def test_resolve_all_multiple_facts(self, validator):
        claims_by_fact = {
            "fact.A": [
                TruthClaim(
                    fact_id="fact.A",
                    value=1,
                    source_path="docs/03_modules/_master-blueprint/blueprint.md",
                    tier=TruthTier.TIER_0,
                ),
                TruthClaim(fact_id="fact.A", value=2, source_path="src/zephyr/code.py", tier=TruthTier.TIER_4),
            ],
            "fact.B": [
                TruthClaim(
                    fact_id="fact.B",
                    value="alpha",
                    source_path="architecture_model/layers/test.yaml",
                    tier=TruthTier.TIER_1,
                ),
                TruthClaim(
                    fact_id="fact.B",
                    value="beta",
                    source_path="docs/01_policies_and_standards/policy.md",
                    tier=TruthTier.TIER_3,
                ),
            ],
        }
        conflicts = validator.resolve_all(claims_by_fact)
        assert len(conflicts) == 2
        assert conflicts[0].fact_id == "fact.A"
        assert conflicts[0].winner.tier == TruthTier.TIER_0
        assert conflicts[1].fact_id == "fact.B"
        assert conflicts[1].winner.tier == TruthTier.TIER_1
