# [A_test] module_id: MOD-GOV_cross_platform_shell | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §

# [MODULE] tests.test_cross_platform_shell

# [INVARIANTS] CrossPlatformShell.generate produces both .sh and .ps1 files

# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__

# [CONSUMERS] pytest

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] pytest raises on failure

# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path

from zephyr.infrastructure.rollback.cross_platform_shell import CrossPlatformScripts, CrossPlatformShell


class TestCrossPlatformShellInit:
    def test_default_project_root(self, tmp_path: Path):
        shell = CrossPlatformShell(project_root=tmp_path)
        assert shell.project_root == tmp_path
        assert shell.output_dir == tmp_path / CrossPlatformShell.OUTPUT_DIR

    def test_output_dir_created(self, tmp_path: Path):
        shell = CrossPlatformShell(project_root=tmp_path)
        assert shell.output_dir.exists()

    def test_none_project_root_uses_cwd(self):
        shell = CrossPlatformShell(project_root=None)
        assert shell.project_root == Path.cwd()


class TestCrossPlatformShellGenerate:
    def test_generate_creates_both_files(self, tmp_path: Path):
        shell = CrossPlatformShell(project_root=tmp_path)
        result = shell.generate("abc1234")
        assert isinstance(result, CrossPlatformScripts)
        assert Path(result.bash_path).exists()
        assert Path(result.pwsh_path).exists()
        assert result.commit_sha == "abc1234"

    def test_generate_bash_content(self, tmp_path: Path):
        shell = CrossPlatformShell(project_root=tmp_path)
        result = shell.generate("deadbeef")
        bash_text = Path(result.bash_path).read_text(encoding="utf-8")
        assert "#!/usr/bin/env bash" in bash_text
        assert "deadbeef" in bash_text
        assert "git revert --no-edit deadbeef" in bash_text

    def test_generate_pwsh_content(self, tmp_path: Path):
        shell = CrossPlatformShell(project_root=tmp_path)
        result = shell.generate("deadbeef")
        pwsh_text = Path(result.pwsh_path).read_text(encoding="utf-8")
        assert "#Requires -Version 5.1" in pwsh_text
        assert "deadbeef" in pwsh_text
        assert "git revert --no-edit deadbeef" in pwsh_text

    def test_generate_with_gpg_sign(self, tmp_path: Path):
        shell = CrossPlatformShell(project_root=tmp_path)
        result = shell.generate("signed123", gpg_sign=True)
        bash_text = Path(result.bash_path).read_text(encoding="utf-8")
        pwsh_text = Path(result.pwsh_path).read_text(encoding="utf-8")
        assert "--gpg-sign" in bash_text
        assert "--gpg-sign" in pwsh_text

    def test_generate_without_gpg_sign(self, tmp_path: Path):
        shell = CrossPlatformShell(project_root=tmp_path)
        result = shell.generate("nosign456", gpg_sign=False)
        bash_text = Path(result.bash_path).read_text(encoding="utf-8")
        assert "--gpg-sign" not in bash_text

    def test_generate_generated_at_populated(self, tmp_path: Path):
        shell = CrossPlatformShell(project_root=tmp_path)
        result = shell.generate("timecheck")
        assert result.generated_at
        assert "T" in result.generated_at


class TestCrossPlatformShellBoundary:
    def test_generate_empty_commit_sha(self, tmp_path: Path):
        shell = CrossPlatformShell(project_root=tmp_path)
        result = shell.generate("")
        assert result.commit_sha == ""
        assert Path(result.bash_path).exists()

    def test_generate_long_commit_sha(self, tmp_path: Path):
        sha = "a" * 40
        shell = CrossPlatformShell(project_root=tmp_path)
        result = shell.generate(sha)
        assert result.commit_sha == sha
        bash_text = Path(result.bash_path).read_text(encoding="utf-8")
        assert sha in bash_text

    def test_generate_special_chars_in_sha(self, tmp_path: Path):
        sha = "abc_def-123"
        shell = CrossPlatformShell(project_root=tmp_path)
        result = shell.generate(sha)
        assert result.commit_sha == sha

    def test_generate_overwrites_existing(self, tmp_path: Path):
        shell = CrossPlatformShell(project_root=tmp_path)
        shell.generate("first_sha")
        result = shell.generate("second_sha")
        bash_text = Path(result.bash_path).read_text(encoding="utf-8")
        assert "second_sha" in bash_text
