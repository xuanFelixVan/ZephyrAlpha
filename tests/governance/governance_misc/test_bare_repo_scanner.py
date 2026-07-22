# [A_test] module_id: MOD-GOV_bare_repo_scanner | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_bare_repo_scanner
# [INVARIANTS] bare_repo_detected_when_HEAD_missing;non_bare_repo_not_detected;nonexistent_path_returns_empty
# [MODIFY-GUARD] source-change-only
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.ExitCode
# [TESTS] test_bare_repo_scanner.py
# [TTL] task_bound

import os
import tempfile

from zephyr.governance.security_governance.bare_repo_scanner import BareRepoScanner


class TestBareRepoScanner:
    def test_nonexistent_path_returns_empty(self):
        scanner = BareRepoScanner()
        result = scanner.scan_directory("/nonexistent/path/xyz")
        assert result == []

    def test_no_git_dirs_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = BareRepoScanner()
            result = scanner.scan_directory(tmpdir)
            assert result == []

    def test_normal_repo_not_detected(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            git_dir = os.path.join(tmpdir, ".git")
            os.makedirs(git_dir)
            with open(os.path.join(git_dir, "HEAD"), "w", encoding="utf-8") as f:
                f.write("ref: refs/heads/main\n")
            with open(os.path.join(git_dir, "config"), "w", encoding="utf-8") as f:
                f.write("[core]\n")
            scanner = BareRepoScanner()
            result = scanner.scan_directory(tmpdir)
            assert result == []

    def test_bare_repo_detected(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            git_dir = os.path.join(tmpdir, ".git")
            os.makedirs(git_dir)
            with open(os.path.join(git_dir, "config"), "w", encoding="utf-8") as f:
                f.write("[core]\n\tbare = true\n")
            scanner = BareRepoScanner()
            result = scanner.scan_directory(tmpdir)
            assert tmpdir in result

    def test_nested_bare_repo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            nested = os.path.join(tmpdir, "subdir")
            os.makedirs(nested)
            git_dir = os.path.join(nested, ".git")
            os.makedirs(git_dir)
            with open(os.path.join(git_dir, "config"), "w", encoding="utf-8") as f:
                f.write("[core]\n")
            scanner = BareRepoScanner()
            result = scanner.scan_directory(tmpdir)
            assert nested in result

    def test_git_dir_without_config_not_detected(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            git_dir = os.path.join(tmpdir, ".git")
            os.makedirs(git_dir)
            scanner = BareRepoScanner()
            result = scanner.scan_directory(tmpdir)
            assert result == []

    def test_empty_directory_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = BareRepoScanner()
            assert scanner.scan_directory(tmpdir) == []
