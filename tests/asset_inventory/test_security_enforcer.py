# [A_test] module_id: MOD-GOV_security_enforcer | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-241 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.asset_inventory.test_security_enforcer
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Tests for MOD-INF-026 §20 Security Enforcer module."""

from pathlib import Path

from zephyr.infrastructure.asset_inventory.scanner import (
    SecurityAccessLogger,
    SecurityAccessRecord,
    SecurityFilter,
    _match_pattern,
)


class TestPatternMatching:
    def test_exact_match(self) -> None:
        assert _match_pattern(".env", "*.env*")

    def test_wildcard_match(self) -> None:
        assert _match_pattern("secrets.json", "*secrets*")

    def test_no_match(self) -> None:
        assert not _match_pattern("main.py", "*.env*")


class TestSecurityFilter:
    def test_secret_file_rejected(self) -> None:
        sf = SecurityFilter()
        ok, reason = sf.should_scan(Path(".env.production"))
        assert not ok
        assert "secret" in str(reason or "")

    def test_normal_file_accepted(self, tmp_path) -> None:
        normal_file = tmp_path / "main.py"
        normal_file.write_text("print('hello')")
        sf = SecurityFilter()
        ok, reason = sf.should_scan(normal_file)
        assert ok

    def test_excluded_dir_rejected(self) -> None:
        sf = SecurityFilter()
        ok, reason = sf.should_scan(Path(".git/config"))
        assert not ok

    def test_py_cache_rejected(self) -> None:
        sf = SecurityFilter()
        ok, reason = sf.should_scan(Path("src/__pycache__/mod.cpython-312.pyc"))
        assert not ok

    def test_nonexistent_file(self) -> None:
        sf = SecurityFilter()
        ok, reason = sf.should_scan(Path("_nonexistent_/file.txt"))
        assert not ok


class TestSecurityAccessRecord:
    def test_model_creation(self) -> None:
        r = SecurityAccessRecord(
            ts="2024-01-01T00:00:00",
            action="SCAN_OK",
            path="src/test.py",
        )
        assert r.action == "SCAN_OK"

    def test_optional_fields_none(self) -> None:
        r = SecurityAccessRecord(ts="t", action="a", path="p")
        assert r.reason is None
        assert r.sha256 is None


class TestSecurityAccessLogger:
    def test_log_skip(self, tmp_path) -> None:
        logger = SecurityAccessLogger(tmp_path)
        logger.log_skip("src/secret.py", "matches_secret")
        assert (tmp_path / "security_access_log.jsonl").exists()

    def test_log_ok(self, tmp_path) -> None:
        logger = SecurityAccessLogger(tmp_path)
        logger.log_ok("src/main.py", "abc123", 1024)
        content = (tmp_path / "security_access_log.jsonl").read_text()
        assert "SCAN_OK" in content

    def test_recent_skips_empty(self, tmp_path) -> None:
        logger = SecurityAccessLogger(tmp_path)
        assert logger.recent_skips() == []
