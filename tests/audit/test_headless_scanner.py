# [A_test] module_id: SRC-TST-1092 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_headless_scanner
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_headless_scanner.py -q
# [TTL] task_bound

from __future__ import annotations

import json
import uuid

from zephyr.gov_drift.drift_models import ScanResult
from zephyr.gov_drift.headless_scanner import (
    HeadlessDiffEntry,
    InterruptLog,
    _scan_script,
    headless_scan_light,
    parse_interrupt_log,
)


class TestHeadlessDiffEntryInstantiation:
    def test_default_values(self):
        entry = HeadlessDiffEntry(file="test.py")
        assert entry.file == "test.py"
        assert entry.hunk == ""
        assert entry.dimension == ""
        assert entry.file_version == ""
        assert entry.sha256 == ""

    def test_all_fields(self):
        entry = HeadlessDiffEntry(
            file="src/main.py",
            hunk="@@ -1,3 +1,4 @@",
            dimension="D5_blueprint_code_sync",
            file_version="v2",
            sha256="abc123",
        )
        assert entry.file == "src/main.py"
        assert entry.hunk == "@@ -1,3 +1,4 @@"
        assert entry.dimension == "D5_blueprint_code_sync"
        assert entry.file_version == "v2"
        assert entry.sha256 == "abc123"


class TestInterruptLogInstantiation:
    def test_creation(self):
        log = InterruptLog(
            session_id="session-001",
            triggered_by="drift",
            context_at="scan",
            scan_outcome="fail",
            errors_found=3,
        )
        assert log.session_id == "session-001"
        assert log.triggered_by == "drift"
        assert log.context_at == "scan"
        assert log.scan_outcome == "fail"
        assert log.errors_found == 3

    def test_zero_errors(self):
        log = InterruptLog(
            session_id="s2",
            triggered_by="timeout",
            context_at="idle",
            scan_outcome="ok",
            errors_found=0,
        )
        assert log.errors_found == 0


class TestScanScript:
    def test_nonexistent_path(self):
        result = _scan_script("/nonexistent/path/script.py")
        assert result == []

    def test_script_with_valid_json_output(self, tmp_path):
        script = tmp_path / "validate_test.py"
        output = [{"file": "a.py", "hunk": "h1", "dimension": "D5", "sha256": "abc"}]
        script.write_text(
            f"import json; print(json.dumps({json.dumps(output)}))",
            encoding="utf-8",
        )
        result = _scan_script(str(script))
        assert len(result) == 1
        assert result[0].file == "a.py"
        assert result[0].sha256 == "abc"

    def test_script_with_nonzero_exit(self, tmp_path):
        script = tmp_path / "fail_script.py"
        script.write_text("import sys; sys.exit(1)", encoding="utf-8")
        result = _scan_script(str(script))
        assert result == []

    def test_script_with_invalid_json(self, tmp_path):
        script = tmp_path / "bad_json.py"
        script.write_text("print('not json')", encoding="utf-8")
        result = _scan_script(str(script))
        assert result == []

    def test_script_with_non_list_json(self, tmp_path):
        script = tmp_path / "dict_output.py"
        script.write_text("import json; print(json.dumps({'key': 'val'}))", encoding="utf-8")
        result = _scan_script(str(script))
        assert result == []

    def test_script_with_multiple_entries(self, tmp_path):
        script = tmp_path / "multi.py"
        output = [
            {"file": "a.py", "hunk": "h1", "dimension": "D5", "sha256": "abc"},
            {"file": "b.py", "hunk": "h2", "dimension": "D6", "sha256": "def"},
        ]
        script.write_text(
            f"import json; print(json.dumps({json.dumps(output)}))",
            encoding="utf-8",
        )
        result = _scan_script(str(script))
        assert len(result) == 2


class TestHeadlessScanLight:
    def test_returns_scan_result(self, tmp_path):
        result = headless_scan_light(modules=[], project_root=str(tmp_path))
        assert isinstance(result, ScanResult)
        assert isinstance(result.scan_id, uuid.UUID)
        assert isinstance(result.total_drift_events, int)
        assert isinstance(result.storm_mode_triggered, bool)

    def test_nonexistent_root(self, tmp_path):
        fake_root = str(tmp_path / "nonexistent_dir")
        result = headless_scan_light(modules=[], project_root=fake_root)
        assert isinstance(result, ScanResult)
        assert result.total_drift_events == 0
        assert result.storm_mode_triggered is False

    def test_detectors_run_is_int(self, tmp_path):
        result = headless_scan_light(modules=[], project_root=str(tmp_path))
        assert isinstance(result.detectors_run, int)


class TestParseInterruptLog:
    def test_nonexistent_file(self):
        result = parse_interrupt_log("/nonexistent/path/log.jsonl")
        assert result == []

    def test_valid_jsonl(self, tmp_path):
        log_file = tmp_path / "_interrupt_log.jsonl"
        entries = [
            {
                "session_id": "s1",
                "triggered_by": "drift",
                "context_at": "scan",
                "scan_outcome": "fail",
                "errors_found": 2,
            },
            {
                "session_id": "s2",
                "triggered_by": "timeout",
                "context_at": "idle",
                "scan_outcome": "ok",
                "errors_found": 0,
            },
        ]
        lines = [json.dumps(e) for e in entries]
        log_file.write_text("\n".join(lines), encoding="utf-8")
        result = parse_interrupt_log(str(log_file))
        assert len(result) == 2
        assert result[0].session_id == "s1"
        assert result[1].errors_found == 0

    def test_empty_file(self, tmp_path):
        log_file = tmp_path / "empty.jsonl"
        log_file.write_text("", encoding="utf-8")
        result = parse_interrupt_log(str(log_file))
        assert result == []

    def test_mixed_valid_invalid_lines(self, tmp_path):
        log_file = tmp_path / "mixed.jsonl"
        valid = json.dumps(
            {"session_id": "s1", "triggered_by": "x", "context_at": "y", "scan_outcome": "z", "errors_found": 1}
        )
        log_file.write_text(f"{valid}\nnot json\n\n", encoding="utf-8")
        result = parse_interrupt_log(str(log_file))
        assert len(result) == 1
        assert result[0].session_id == "s1"

    def test_missing_fields_default(self, tmp_path):
        log_file = tmp_path / "partial.jsonl"
        log_file.write_text(json.dumps({"session_id": "s1"}), encoding="utf-8")
        result = parse_interrupt_log(str(log_file))
        assert len(result) == 1
        assert result[0].triggered_by == ""
        assert result[0].errors_found == 0
