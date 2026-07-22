# [A_test] module_id: MOD-GOV_aisg_sandbox | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-587 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_aisg_sandbox
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""AISGSandbox — 危险模式拦截与安全样本放行。"""


from zephyr.governance.intelligence_governance.aisg_sandbox import AISGSandbox


def test_aisg_dangerous_patterns_blocked() -> None:
    AISGSandbox.total_tests = 0
    AISGSandbox.tests_passed = 0
    results = AISGSandbox.run_dangerous_pattern_tests()
    assert results
    assert all(r.passed for r in results), [r.test_name for r in results if not r.passed]


def test_aisg_safe_samples_allowed() -> None:
    AISGSandbox.total_tests = 0
    AISGSandbox.tests_passed = 0
    results = AISGSandbox.run_safe_pattern_tests()
    assert results
    assert all(r.passed for r in results), [r.test_name for r in results if not r.passed]
