# [A_test] module_id: MOD-GOV_zero_config | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-444 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_zero_config
# [INVARIANTS] ZeroConfig.scan返回ZeroConfigResult; all_passed反映所有checks的passed状态
# [MODIFY-GUARD] 仅当zero_config公开API变更时修改
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip; 实例化失败→fail
# [TESTS] pytest tests/test_zero_config.py -q
# [TTL] task_bound


from zephyr.shared.maintenance.zero_config import (
    ConfigCheck,
    ZeroConfig,
    ZeroConfigResult,
)


class TestZeroConfigInstantiation:
    def test_default_instantiation(self):
        zc = ZeroConfig()
        assert zc is not None

    def test_instantiation_with_project_root(self, tmp_path):
        zc = ZeroConfig(project_root=tmp_path)
        assert zc is not None

    def test_instantiation_with_none_root(self):
        zc = ZeroConfig(project_root=None)
        assert zc is not None


class TestZeroConfigScan:
    def test_scan_returns_result(self, tmp_path):
        zc = ZeroConfig(project_root=tmp_path)
        result = zc.scan()
        assert isinstance(result, ZeroConfigResult)

    def test_scan_checks_non_empty(self, tmp_path):
        zc = ZeroConfig(project_root=tmp_path)
        result = zc.scan()
        assert len(result.checks) > 0

    def test_scan_no_git_repo_detected(self, tmp_path):
        zc = ZeroConfig(project_root=tmp_path)
        result = zc.scan()
        git_checks = [c for c in result.checks if c.name == "GIT_REPO"]
        assert len(git_checks) == 1
        assert git_checks[0].passed is False

    def test_scan_with_git_repo(self, tmp_path):
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        zc = ZeroConfig(project_root=tmp_path)
        result = zc.scan()
        git_checks = [c for c in result.checks if c.name == "GIT_REPO"]
        assert len(git_checks) == 0

    def test_scan_python_check_exists(self, tmp_path):
        zc = ZeroConfig(project_root=tmp_path)
        result = zc.scan()
        python_checks = [c for c in result.checks if c.name == "PYTHON"]
        assert len(python_checks) == 1

    def test_scan_git_config_check_exists(self, tmp_path):
        zc = ZeroConfig(project_root=tmp_path)
        result = zc.scan()
        git_config_checks = [c for c in result.checks if c.name == "GIT_CONFIG"]
        assert len(git_config_checks) == 1

    def test_scan_encoding_check_exists(self, tmp_path):
        zc = ZeroConfig(project_root=tmp_path)
        result = zc.scan()
        encoding_checks = [c for c in result.checks if c.name == "ENCODING"]
        assert len(encoding_checks) == 1

    def test_scan_missing_git_repo_in_missing_list(self, tmp_path):
        zc = ZeroConfig(project_root=tmp_path)
        result = zc.scan()
        assert "git_repo" in result.missing

    def test_scan_missing_git_repo_not_in_missing_list(self, tmp_path):
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        zc = ZeroConfig(project_root=tmp_path)
        result = zc.scan()
        assert "git_repo" not in result.missing

    def test_scan_all_passed_reflects_checks(self, tmp_path):
        zc = ZeroConfig(project_root=tmp_path)
        result = zc.scan()
        expected = all(c.passed for c in result.checks)
        assert result.all_passed == expected


class TestZeroConfigCheckPython:
    def test_python_check_returns_config_check(self, tmp_path):
        zc = ZeroConfig(project_root=tmp_path)
        check = zc.check_python()
        assert isinstance(check, ConfigCheck)
        assert check.name == "PYTHON"

    def test_python_check_has_value(self, tmp_path):
        zc = ZeroConfig(project_root=tmp_path)
        check = zc.check_python()
        assert len(check.value) > 0


class TestZeroConfigCheckGitConfig:
    def test_git_config_check_returns_config_check(self, tmp_path):
        zc = ZeroConfig(project_root=tmp_path)
        check = zc.check_git_config()
        assert isinstance(check, ConfigCheck)
        assert check.name == "GIT_CONFIG"


class TestConfigCheck:
    def test_construction(self):
        cc = ConfigCheck(name="TEST", passed=True, value="ok")
        assert cc.name == "TEST"
        assert cc.passed is True
        assert cc.value == "ok"
        assert cc.message == ""

    def test_construction_with_message(self):
        cc = ConfigCheck(name="TEST", passed=False, value="bad", message="Error detail")
        assert cc.message == "Error detail"

    def test_failed_check(self):
        cc = ConfigCheck(name="TEST", passed=False, value="N/A")
        assert cc.passed is False


class TestZeroConfigResult:
    def test_construction(self):
        result = ZeroConfigResult(
            all_passed=True,
            checks=[],
            missing=[],
            recommendations=[],
        )
        assert result.all_passed is True
        assert result.checks == []
        assert result.missing == []
        assert result.recommendations == []

    def test_with_failed_checks(self):
        checks = [ConfigCheck(name="A", passed=False, value="x")]
        result = ZeroConfigResult(all_passed=False, checks=checks, missing=["a"], recommendations=["fix a"])
        assert result.all_passed is False
        assert len(result.checks) == 1
        assert "a" in result.missing
