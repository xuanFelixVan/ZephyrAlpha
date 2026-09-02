# [A_test] module_id: MOD-GOV_drift_fixer | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] tests.test_drift_fixer
# [INVARIANTS] 测试覆盖scan/fix/validate/rollback;边界:空输入/None/异常
# [MODIFY-GUARD] blueprint.md §3
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.infrastructure.auto_fix_engine.drift_fixer import DriftFixer
from zephyr.infrastructure.auto_fix_engine.models import FixStatus, ValidationResult


class TestDriftFixerInstantiation:
    def test_fixer_id(self):
        f = DriftFixer()
        assert f.fixer_id == "drift_fixer"

    def test_action_type(self):
        f = DriftFixer()
        assert f.action_type == "drift_fix"

    def test_dimension(self):
        f = DriftFixer()
        assert f.dimension == "DIM-DRIFT-001"


class TestScan:
    def test_scan_returns_list(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        f = DriftFixer()
        result = f.scan()
        assert isinstance(result, list)

    def test_scan_finds_pre_release_version(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        y = tmp_path / "test.yaml"
        y.write_text("version: '0.2.0'\n", encoding="utf-8")
        f = DriftFixer()
        result = f.scan()
        assert any(finding["type"] == "pre_release_version" for finding in result)

    def test_scan_no_pre_release(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        y = tmp_path / "test.yaml"
        y.write_text("version: '1.0.0'\n", encoding="utf-8")
        f = DriftFixer()
        result = f.scan()
        # 5.12.5 后 scan() 固定扫描 REPO_ROOT（不受 chdir 隔离），
        # 断言本文件（version 1.0.0）不被标记为 pre_release_version
        assert not any(finding["type"] == "pre_release_version" and finding["file"] == str(y) for finding in result)


class TestFix:
    def test_fix_nonexistent_target(self):
        f = DriftFixer()
        action = f.fix("/nonexistent/path/file.yaml")
        assert action.status == FixStatus.FAILED
        assert action.metadata.get("error") == "Target not found"

    def test_fix_no_drift(self, tmp_path):
        p = tmp_path / "clean.yaml"
        p.write_text("version: '1.0.0'\nkey: value\n", encoding="utf-8")
        f = DriftFixer()
        action = f.fix(str(p))
        assert action.status == FixStatus.COMPLETED
        assert action.metadata.get("note") == "No drift detected"

    def test_fix_with_drift_dry_run(self, tmp_path):
        p = tmp_path / "sample.yaml"
        p.write_text(
            "version: '0.1.0'\nlast_updated: '2025-01-01'\nlast_updated: '2025-03-15'\n",
            encoding="utf-8",
        )
        f = DriftFixer()
        action = f.fix(str(p), dry_run=True)
        assert action.status == FixStatus.COMPLETED

    def test_fix_with_drift_applied(self, tmp_path):
        p = tmp_path / "sample.yaml"
        p.write_text(
            "version: '0.1.0'\nlast_updated: '2025-01-01'\nlast_updated: '2025-03-15'\n",
            encoding="utf-8",
        )
        f = DriftFixer()
        action = f.fix(str(p), dry_run=False)
        assert action.status == FixStatus.COMPLETED

    def test_fix_empty_file(self, tmp_path):
        p = tmp_path / "empty.yaml"
        p.write_text("", encoding="utf-8")
        f = DriftFixer()
        action = f.fix(str(p))
        assert action.status == FixStatus.COMPLETED


class TestValidate:
    def test_validate_nonexistent_target(self):
        f = DriftFixer()
        result = f.validate("/nonexistent/path/file.yaml")
        assert isinstance(result, ValidationResult)
        assert not result.valid
        assert result.error == "Target not found"

    def test_validate_valid_yaml(self, tmp_path):
        p = tmp_path / "clean.yaml"
        p.write_text("version: '1.0.0'\nkey: value\n", encoding="utf-8")
        f = DriftFixer()
        result = f.validate(str(p))
        assert result.valid
        assert result.evidence == "YAML parseable"

    def test_validate_invalid_yaml(self, tmp_path):
        bad = tmp_path / "bad.yaml"
        bad.write_text("key: [unclosed\n", encoding="utf-8")
        f = DriftFixer()
        result = f.validate(str(bad))
        assert not result.valid
        assert "YAML error" in result.error


class TestRollback:
    def test_rollback_returns_false(self):
        f = DriftFixer()
        assert f.rollback("any_path") is False
