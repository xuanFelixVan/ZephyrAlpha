# [A_test] module_id: SRC-TST-1975 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-592 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_artifact_scanner
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""ArtifactScanner — SSRF / 凭据等规则冒烟测试。"""


from zephyr.gov_drift.artifact_scanner import ArtifactScanner


def test_artifact_scanner_flags_localhost_ssrf() -> None:
    scanner = ArtifactScanner()
    report = scanner.scan_content('url = "http://localhost:8080/internal"')
    assert report.error_count >= 1
    assert any(f.rule_id.startswith("S-01") for f in report.findings)


def test_artifact_scanner_clean_python_snippet() -> None:
    scanner = ArtifactScanner()
    report = scanner.scan_content("def foo():\n    return 42\n")
    assert report.is_clean
