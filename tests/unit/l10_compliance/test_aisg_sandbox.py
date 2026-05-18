# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l10_compliance.test_aisg_sandbox
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""AISGSandbox — 危险模式拦截与安全样本放行。"""

from zephyr.l10_compliance.aisg_sandbox import AISGSandbox


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
