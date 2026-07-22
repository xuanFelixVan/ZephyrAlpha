# [A_test] module_id: MOD-GOV_finding_schema | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-641 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_finding_schema
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""script_system.finding Finding Schema — MOD-INF-005 §6.5 recommendation 对齐。"""


from zephyr.infrastructure.script_system.finding import (
    Dimension,
    Finding,
    RecommendationType,
    RecommendedAction,
    RemediationAction,
    Severity,
)


def test_to_dict_backward_compatible_without_recommendation() -> None:
    f = Finding(
        dimension=Dimension.D3,
        severity=Severity.MEDIUM,
        category="test",
        target_file="docs/x.md",
        description="missing field",
        remediation_action=RemediationAction.FIX,
    )
    d = f.to_dict()
    assert "recommendation_block" not in d
    assert d["severity"] == "MEDIUM"


def test_to_dict_with_recommendation_block() -> None:
    f = Finding(
        dimension=Dimension.D3,
        severity=Severity.MEDIUM,
        category="test",
        target_file="docs/x.md",
        description="needs fix suggestion",
        recommendation="在 frontmatter 增加 version",
        recommendation_type=RecommendationType.MANUAL_ONLY,
        recommended_action=RecommendedAction.MODIFY_FILE,
    )
    d = f.to_dict()
    assert "recommendation_block" in d
    rb = d["recommendation_block"]
    assert rb["recommendation"] == "在 frontmatter 增加 version"
    assert rb["recommendation_type"] == "manual_only"
    assert rb["recommended_action"] == "modify_file"
