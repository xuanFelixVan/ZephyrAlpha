# [A_test] module_id: SRC-TST-1802 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infra_ops/capacity_assurance/blueprint.md | §test
# [MODULE] tests.test_winfs_defense
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_winfs_defense.py
# [TTL] task_bound

import sys

import pytest

mod = pytest.importorskip("zephyr.ops.capacity_assurance.winfs_defense", reason="winfs_defense not available")
WinFSDefense = mod.WinFSDefense


class TestWinFSDefense:
    def test_instantiation(self):
        wfs = WinFSDefense()
        assert wfs._long_path_enabled is False

    def test_normalize_path_basic(self):
        wfs = WinFSDefense()
        result = wfs.normalize_path("some/path/to/file.txt")
        assert isinstance(result, str)
        assert "file.txt" in result

    def test_normalize_path_with_backslashes(self):
        wfs = WinFSDefense()
        result = wfs.normalize_path("some\\path\\to\\file.txt")
        assert isinstance(result, str)

    def test_enable_long_paths(self):
        wfs = WinFSDefense()
        wfs.enable_long_paths()
        if sys.platform == "win32":
            assert wfs._long_path_enabled is True
        else:
            assert wfs._long_path_enabled is False

    def test_check_filesystem(self):
        wfs = WinFSDefense()
        result = wfs.check_filesystem()
        assert "cwd" in result
        assert "cwd_exists" in result
        assert "long_path_enabled" in result
        assert "platform" in result
        assert result["cwd_exists"] is True

    def test_safe_open_write_and_read(self, tmp_path):
        wfs = WinFSDefense()
        f = tmp_path / "test_file.txt"
        with wfs.safe_open(str(f), "w") as fh:
            fh.write("hello")
        with wfs.safe_open(str(f), "r") as fh:
            content = fh.read()
        assert content == "hello"
