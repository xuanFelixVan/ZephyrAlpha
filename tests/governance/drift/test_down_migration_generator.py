# [A_test] module_id: SRC-TST-0764 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §

# [MODULE] tests.test_down_migration_generator

# [INVARIANTS] DownMigrationGenerator.generate produces both .sh and .ps1 files

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
from unittest.mock import patch

from zephyr.infrastructure.rollback.down_migration_generator import DownMigration, DownMigrationGenerator


class TestDownMigrationGeneratorInit:
    def test_default_project_root(self, tmp_path: Path):
        gen = DownMigrationGenerator(project_root=tmp_path)
        assert gen._project_root == tmp_path
        assert gen._output_dir == tmp_path / DownMigrationGenerator.OUTPUT_DIR

    def test_output_dir_created(self, tmp_path: Path):
        gen = DownMigrationGenerator(project_root=tmp_path)
        assert gen._output_dir.exists()

    def test_none_project_root_uses_cwd(self):
        gen = DownMigrationGenerator(project_root=None)
        assert gen._project_root == Path.cwd()


class TestDownMigrationGeneratorGenerate:
    def test_generate_with_explicit_sha(self, tmp_path: Path):
        gen = DownMigrationGenerator(project_root=tmp_path)
        result = gen.generate("abc1234")
        assert isinstance(result, DownMigration)
        assert result.commit_sha == "abc1234"
        assert Path(result.bash_script).exists()
        assert Path(result.pwsh_script).exists()

    def test_generate_bash_content(self, tmp_path: Path):
        gen = DownMigrationGenerator(project_root=tmp_path)
        result = gen.generate("deadbeef")
        bash_text = Path(result.bash_script).read_text(encoding="utf-8")
        assert "#!/bin/bash" in bash_text
        assert "deadbeef" in bash_text
        assert "git revert --no-edit deadbeef" in bash_text

    def test_generate_pwsh_content(self, tmp_path: Path):
        gen = DownMigrationGenerator(project_root=tmp_path)
        result = gen.generate("deadbeef")
        pwsh_text = Path(result.pwsh_script).read_text(encoding="utf-8")
        assert "$ErrorActionPreference = 'Stop'" in pwsh_text
        assert "deadbeef" in pwsh_text
        assert "git revert --no-edit deadbeef" in pwsh_text

    def test_generate_returns_files_changed(self, tmp_path: Path):
        gen = DownMigrationGenerator(project_root=tmp_path)
        with patch.object(gen, "_get_changed_files", return_value=["file1.py", "file2.py"]):
            result = gen.generate("sha789")
        assert result.files_changed == ["file1.py", "file2.py"]

    def test_generate_head_resolves_to_sha(self, tmp_path: Path):
        gen = DownMigrationGenerator(project_root=tmp_path)
        with patch.object(gen, "_get_head_short", return_value="a1b2c3d"):
            with patch.object(gen, "_get_changed_files", return_value=[]):
                result = gen.generate("HEAD")
        assert result.commit_sha == "a1b2c3d"

    def test_generate_empty_string_resolves_head(self, tmp_path: Path):
        gen = DownMigrationGenerator(project_root=tmp_path)
        with patch.object(gen, "_get_head_short", return_value="xyz9999"):
            with patch.object(gen, "_get_changed_files", return_value=[]):
                result = gen.generate("")
        assert result.commit_sha == "xyz9999"


class TestDownMigrationGeneratorBoundary:
    def test_get_head_short_git_failure(self, tmp_path: Path):
        gen = DownMigrationGenerator(project_root=tmp_path)
        with patch(
            "zephyr.infrastructure.rollback.down_migration_generator.subprocess.run", side_effect=OSError("no git")
        ):
            sha = gen._get_head_short()
        assert sha == "unknown"

    def test_get_changed_files_git_failure(self, tmp_path: Path):
        gen = DownMigrationGenerator(project_root=tmp_path)
        with patch(
            "zephyr.infrastructure.rollback.down_migration_generator.subprocess.run", side_effect=OSError("no git")
        ):
            files = gen._get_changed_files("abc123")
        assert files == []

    def test_generate_generated_at_populated(self, tmp_path: Path):
        gen = DownMigrationGenerator(project_root=tmp_path)
        result = gen.generate("timecheck")
        assert result.generated_at
        assert "T" in result.generated_at
