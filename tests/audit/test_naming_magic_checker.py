# [A_test] module_id: SRC-TST-1306 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_naming_magic_checker
# [INVARIANTS] 命名约定检查不可跳过
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] tests/test_naming_magic_checker.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_drift.naming_magic_checker import (
    NamingMagicAlert,
    scan_naming_magic,
)


class TestNamingMagicAlert:
    def test_defaults(self):
        alert = NamingMagicAlert(
            alert_id="nm-1",
            file_path="test.py",
            line_no=10,
            magic_type="version_hardcode",
            current_code="import hashlib==2.0.1",
            description="version hardcoded",
        )
        assert alert.severity == "MAJOR"
        assert alert.detected_at is not None

    def test_custom_severity(self):
        alert = NamingMagicAlert(
            alert_id="nm-2",
            file_path="a.py",
            line_no=5,
            magic_type="hidden_cycle",
            current_code="from tests.x import y",
            description="cycle",
            severity="CRITICAL",
        )
        assert alert.severity == "CRITICAL"


class TestScanNamingMagic:
    def test_empty_directory(self, tmp_path):
        result = scan_naming_magic(str(tmp_path))
        assert result == []

    def test_detects_version_hardcode(self, tmp_path):
        py_file = tmp_path / "bad_import.py"
        py_file.write_text("import hashlib==2.0.1\n", encoding="utf-8")
        result = scan_naming_magic(str(tmp_path))
        version_alerts = [a for a in result if a.magic_type == "version_hardcode"]
        assert len(version_alerts) >= 1

    def test_detects_hidden_cycle(self, tmp_path):
        py_file = tmp_path / "cycle.py"
        py_file.write_text("from tests.fixtures import data\n", encoding="utf-8")
        result = scan_naming_magic(str(tmp_path))
        cycle_alerts = [a for a in result if a.magic_type == "hidden_cycle"]
        assert len(cycle_alerts) >= 1

    def test_detects_implicit_file_patterns(self, tmp_path):
        py_file = tmp_path / "implicit.py"
        py_file.write_text("import models\n", encoding="utf-8")
        result = scan_naming_magic(str(tmp_path))
        pattern_alerts = [a for a in result if a.magic_type == "import_models_convention"]
        assert len(pattern_alerts) >= 1

    def test_clean_file_no_alerts(self, tmp_path):
        py_file = tmp_path / "clean.py"
        py_file.write_text("import os\nimport sys\nprint('hello')\n", encoding="utf-8")
        result = scan_naming_magic(str(tmp_path))
        assert result == []

    def test_nonexistent_root(self, tmp_path):
        fake_root = str(tmp_path / "nonexistent")
        result = scan_naming_magic(fake_root)
        assert result == []

    def test_ignores_pycache(self, tmp_path):
        cache_dir = tmp_path / "__pycache__"
        cache_dir.mkdir()
        cached = cache_dir / "bad.cpython-39.pyc"
        cached.write_bytes(b"fake bytecode")
        result = scan_naming_magic(str(tmp_path))
        for alert in result:
            assert "__pycache__" not in alert.file_path

    def test_alert_has_required_fields(self, tmp_path):
        py_file = tmp_path / "versioned.py"
        py_file.write_text("import hashlib==2.0.1\n", encoding="utf-8")
        result = scan_naming_magic(str(tmp_path))
        if result:
            alert = result[0]
            assert alert.alert_id != ""
            assert alert.file_path != ""
            assert alert.line_no > 0
            assert alert.magic_type != ""
            assert alert.current_code != ""
            assert alert.description != ""
