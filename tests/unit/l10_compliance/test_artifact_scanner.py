"""ArtifactScanner — SSRF / 凭据等规则冒烟测试。"""

from zephyr.l10_compliance.artifact_scanner import ArtifactScanner


def test_artifact_scanner_flags_localhost_ssrf() -> None:
    scanner = ArtifactScanner()
    report = scanner.scan_content('url = "http://localhost:8080/internal"')
    assert report.error_count >= 1
    assert any(f.rule_id.startswith("S-01") for f in report.findings)


def test_artifact_scanner_clean_python_snippet() -> None:
    scanner = ArtifactScanner()
    report = scanner.scan_content("def foo():\n    return 42\n")
    assert report.is_clean
