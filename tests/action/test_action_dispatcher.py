# [A_test] module_id: SRC-TST-0262 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] tests.test_action_dispatcher
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_action_dispatcher.py
# [TTL] task_bound

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from unittest.mock import MagicMock, patch

from zephyr.trading.action_dispatcher import ActionDispatcher, ActionReport


@dataclass
class _FakeTask:
    task_id: str
    capability: str
    result: dict[str, Any] | None
    payload: dict[str, Any] | None = None
    status: str = "completed"
    _acted: bool = False


class TestActionDispatcherInit:
    def test_default_init(self):
        d = ActionDispatcher()
        assert d.dry_run is False
        assert d.stats == {
            "dispatched": 0,
            "modified": 0,
            "skipped": 0,
            "created": 0,
            "deleted": 0,
            "search_replaced": 0,
            "backups": 0,
        }

    def test_dry_run_init(self):
        d = ActionDispatcher(dry_run=True)
        assert d.dry_run is True


class TestActionDispatcherDispatch:
    def test_dispatch_empty_result_returns_skipped(self):
        d = ActionDispatcher()
        task = _FakeTask(task_id="t1", capability="task_classification", result=None)
        report = d.dispatch(task)
        assert report.status == "skipped"
        assert "empty result" in report.detail

    def test_dispatch_unknown_capability_returns_skipped(self):
        d = ActionDispatcher()
        task = _FakeTask(task_id="t2", capability="unknown_cap", result={"x": 1})
        report = d.dispatch(task)
        assert report.status == "skipped"
        assert "no actuator" in report.detail

    def test_dispatch_exception_returns_error(self):
        d = ActionDispatcher()
        task = _FakeTask(task_id="t3", capability="task_classification", result={"category": "test"})
        with patch.object(d, "_annotate_py_file", side_effect=RuntimeError("boom")):
            report = d.dispatch(task)
        assert report.status == "error"
        assert "boom" in report.detail


class TestActionDispatcherSearchReplace:
    def test_search_replace_file_not_found(self, tmp_path):
        d = ActionDispatcher()
        report = d._search_replace_file("nonexistent_module", {"fixes": [{"old_str": "a", "new_str": "b"}]})
        assert report.status == "skipped"

    def test_search_replace_empty_field(self, tmp_path):
        d = ActionDispatcher()
        py_file = tmp_path / "sample.py"
        py_file.write_text("x = 1\n", encoding="utf-8")
        with patch.object(d, "_find_module_file", return_value=py_file):
            with patch.object(d, "_extract_module_name", return_value="sample"):
                report = d._search_replace_file("sample", {"fixes": []})
        assert report.status == "skipped"
        assert "empty fixes" in report.detail

    def test_search_replace_applies_fix(self, tmp_path):
        d = ActionDispatcher(dry_run=True)
        py_file = tmp_path / "target.py"
        py_file.write_text("old_value = 1\n", encoding="utf-8")
        with patch.object(d, "_find_module_file", return_value=py_file):
            with patch.object(d, "_extract_module_name", return_value="target"):
                with patch.object(d, "_version_backup", return_value="bak"):
                    report = d._search_replace_file(
                        "target",
                        {"fixes": [{"old_str": "old_value", "new_str": "new_value", "reason": "fix"}]},
                    )
        assert report.status == "search_replaced"
        assert "1 replaced" in report.detail

    def test_search_replace_no_match(self, tmp_path):
        d = ActionDispatcher()
        py_file = tmp_path / "nomatch.py"
        py_file.write_text("x = 1\n", encoding="utf-8")
        with patch.object(d, "_find_module_file", return_value=py_file):
            with patch.object(d, "_extract_module_name", return_value="nomatch"):
                report = d._search_replace_file(
                    "nomatch",
                    {"fixes": [{"old_str": "not_present", "new_str": "y"}]},
                )
        assert report.status == "skipped"


class TestActionDispatcherSearchReplacePaths:
    """Phase 7e 补充测试：覆盖 _search_replace_file 的宽松匹配/remove/unchanged/空old_str/部分失败/实际写入/backup 路径"""

    def test_search_replace_fuzzy_match_stripped(self, tmp_path):
        """宽松匹配: old_str 带首尾空白, strip 后命中"""
        d = ActionDispatcher(dry_run=True)
        py_file = tmp_path / "fuzzy.py"
        py_file.write_text("target_value = 1\n", encoding="utf-8")
        with patch.object(d, "_find_module_file", return_value=py_file):
            with patch.object(d, "_extract_module_name", return_value="fuzzy"):
                with patch.object(d, "_version_backup", return_value="bak"):
                    report = d._search_replace_file(
                        "fuzzy",
                        {"fixes": [{"old_str": "  target_value  ", "new_str": "replaced"}]},
                    )
        assert report.status == "search_replaced"
        assert "1 replaced" in report.detail

    def test_search_replace_remove_mode(self, tmp_path):
        """remove=True: dead_code_removal, new_str='', 多余空行清理"""
        d = ActionDispatcher(dry_run=True)
        py_file = tmp_path / "remove.py"
        py_file.write_text("keep\n\n\n\ndelete_me\n\n\n\nkeep2\n", encoding="utf-8")
        with patch.object(d, "_find_module_file", return_value=py_file):
            with patch.object(d, "_extract_module_name", return_value="remove"):
                with patch.object(d, "_version_backup", return_value="bak"):
                    report = d._search_replace_file(
                        "remove",
                        {"dead_sections": [{"old_str": "delete_me"}]},
                        field="dead_sections",
                        remove=True,
                    )
        assert report.status == "search_replaced"

    def test_search_replace_unchanged_returns_skipped(self, tmp_path):
        """modified == original (替换为相同内容) → skipped"""
        d = ActionDispatcher(dry_run=True)
        py_file = tmp_path / "same.py"
        py_file.write_text("value = 1\n", encoding="utf-8")
        with patch.object(d, "_find_module_file", return_value=py_file):
            with patch.object(d, "_extract_module_name", return_value="same"):
                report = d._search_replace_file(
                    "same",
                    {"fixes": [{"old_str": "value", "new_str": "value"}]},
                )
        assert report.status == "skipped"
        assert "unchanged" in report.detail

    def test_search_replace_empty_old_str_counts_failed(self, tmp_path):
        """entry 无 old_str → failed++, applied=0 → skipped"""
        d = ActionDispatcher(dry_run=True)
        py_file = tmp_path / "emptyold.py"
        py_file.write_text("x = 1\n", encoding="utf-8")
        with patch.object(d, "_find_module_file", return_value=py_file):
            with patch.object(d, "_extract_module_name", return_value="emptyold"):
                report = d._search_replace_file(
                    "emptyold",
                    {"fixes": [{"old_str": "", "new_str": "y"}]},
                )
        assert report.status == "skipped"
        assert "match" in report.detail

    def test_search_replace_partial_failure_includes_failed(self, tmp_path):
        """部分成功部分失败: applied>0 && failed>0 → detail 含 failed"""
        d = ActionDispatcher(dry_run=True)
        py_file = tmp_path / "partial.py"
        py_file.write_text("alpha = 1\n", encoding="utf-8")
        with patch.object(d, "_find_module_file", return_value=py_file):
            with patch.object(d, "_extract_module_name", return_value="partial"):
                with patch.object(d, "_version_backup", return_value="bak"):
                    report = d._search_replace_file(
                        "partial",
                        {"fixes": [
                            {"old_str": "alpha", "new_str": "beta"},
                            {"old_str": "not_found", "new_str": "gamma"},
                        ]},
                    )
        assert report.status == "search_replaced"
        assert "1 replaced" in report.detail
        assert "failed" in report.detail

    def test_search_replace_writes_file_when_not_dry_run(self, tmp_path):
        """非 dry_run 模式: 文件实际被写入"""
        d = ActionDispatcher(dry_run=False)
        py_file = tmp_path / "writetest.py"
        py_file.write_text("old_content = 1\n", encoding="utf-8")
        with patch.object(d, "_find_module_file", return_value=py_file):
            with patch.object(d, "_extract_module_name", return_value="writetest"):
                with patch.object(d, "_version_backup", return_value="bak"):
                    report = d._search_replace_file(
                        "writetest",
                        {"fixes": [{"old_str": "old_content", "new_str": "new_content"}]},
                    )
        assert report.status == "search_replaced"
        assert "new_content" in py_file.read_text(encoding="utf-8")

    def test_search_replace_backup_increments_stats(self, tmp_path):
        """_version_backup 返回非空 → stats['backups'] 递增"""
        d = ActionDispatcher(dry_run=True)
        py_file = tmp_path / "backup.py"
        py_file.write_text("val = 1\n", encoding="utf-8")
        original_backups = d.stats["backups"]
        with patch.object(d, "_find_module_file", return_value=py_file):
            with patch.object(d, "_extract_module_name", return_value="backup"):
                with patch.object(d, "_version_backup", return_value="backup_001.bak"):
                    report = d._search_replace_file(
                        "backup",
                        {"fixes": [{"old_str": "val", "new_str": "newval"}]},
                    )
        assert report.status == "search_replaced"
        assert d.stats["backups"] == original_backups + 1

    def test_search_replace_reason_accumulated_in_detail(self, tmp_path):
        """reason 字段被累积到 detail 字符串中"""
        d = ActionDispatcher(dry_run=True)
        py_file = tmp_path / "reason.py"
        py_file.write_text("target = 1\n", encoding="utf-8")
        with patch.object(d, "_find_module_file", return_value=py_file):
            with patch.object(d, "_extract_module_name", return_value="reason"):
                with patch.object(d, "_version_backup", return_value="bak"):
                    report = d._search_replace_file(
                        "reason",
                        {"fixes": [{"old_str": "target", "new_str": "replaced", "reason": "security fix"}]},
                    )
        assert report.status == "search_replaced"
        assert "security fix" in report.detail


class TestActionDispatcherCreateFile:
    def test_create_file_no_path(self):
        d = ActionDispatcher()
        report = d._create_file({"file_path": "", "content": "x"})
        assert report.status == "skipped"
        assert "no file_path" in report.detail

    def test_create_file_empty_content(self):
        d = ActionDispatcher()
        report = d._create_file({"file_path": "a.py", "content": ""})
        assert report.status == "skipped"
        assert "empty content" in report.detail

    def test_create_file_path_escape(self, tmp_path):
        d = ActionDispatcher()
        with patch("zephyr.trading.action_dispatcher.PROJECT_ROOT", tmp_path):
            report = d._create_file({"file_path": "../../etc/passwd", "content": "x"})
        assert report.status == "error"
        assert "escapes" in report.detail

    def test_create_file_already_exists(self, tmp_path):
        d = ActionDispatcher()
        existing = tmp_path / "exists.py"
        existing.write_text("old", encoding="utf-8")
        with patch("zephyr.trading.action_dispatcher.PROJECT_ROOT", tmp_path):
            report = d._create_file({"file_path": "exists.py", "content": "new"})
        assert report.status == "skipped"
        assert "already exists" in report.detail

    def test_create_file_success_dry_run(self, tmp_path):
        d = ActionDispatcher(dry_run=True)
        with patch("zephyr.trading.action_dispatcher.PROJECT_ROOT", tmp_path):
            report = d._create_file({"file_path": "new_file.py", "content": "print('hi')"})
        assert report.status == "created"
        assert not (tmp_path / "new_file.py").exists()


class TestActionDispatcherDeleteFile:
    def test_delete_file_not_found(self):
        d = ActionDispatcher()
        report = d._delete_file("nonexistent", {"file_path": ""})
        assert report.status == "skipped"

    def test_delete_file_success_dry_run(self, tmp_path):
        d = ActionDispatcher(dry_run=True)
        target = tmp_path / "to_delete.py"
        target.write_text("content", encoding="utf-8")
        with patch("zephyr.trading.action_dispatcher.PROJECT_ROOT", tmp_path):
            with patch("zephyr.trading.action_dispatcher.BRAIN_TRASH_DIR", tmp_path / ".brain_trash"):
                with patch.object(d, "_find_module_file", return_value=target):
                    with patch.object(d, "_extract_module_name", return_value="to_delete"):
                        with patch.object(d, "_version_backup", return_value="bak"):
                            report = d._delete_file("to_delete", {})
        assert report.status == "deleted"


class TestActionDispatcherAnnotatePyFile:
    def test_annotate_py_file_not_found(self):
        d = ActionDispatcher()
        report = d._annotate_py_file("unknown_mod", {"category": "test"})
        assert report.status == "skipped"

    def test_annotate_py_file_success_dry_run(self, tmp_path):
        d = ActionDispatcher(dry_run=True)
        py_file = tmp_path / "mod.py"
        py_file.write_text("x = 1\n", encoding="utf-8")
        with patch.object(d, "_find_module_file", return_value=py_file):
            with patch.object(d, "_extract_module_name", return_value="mod"):
                with patch.object(d, "_version_backup", return_value="bak"):
                    report = d._annotate_py_file("mod", {"category": "governance"})
        assert report.status == "modified"


class TestActionDispatcherTagModule:
    def test_tag_module_empty_tags(self):
        d = ActionDispatcher()
        report = d._tag_module("mod", {"tags": []})
        assert report.status == "skipped"
        assert "empty tags" in report.detail

    def test_tag_module_no_card(self):
        d = ActionDispatcher()
        with patch.object(d, "_find_capability_card", return_value=None):
            report = d._tag_module("mod", {"tags": ["a"]})
        assert report.status == "skipped"
        assert "no card" in report.detail


class TestActionDispatcherWriteTriageLog:
    def test_write_triage_log(self, tmp_path):
        d = ActionDispatcher()
        with patch("zephyr.trading.action_dispatcher.AUDIT_LOGS_DIR", tmp_path):
            report = d._write_triage_log({"result": {"needs_human": True, "reason": "anomaly"}})
        assert report.status == "modified"
        assert "ALERT" in report.detail

    def test_write_triage_log_clear(self, tmp_path):
        d = ActionDispatcher()
        with patch("zephyr.trading.action_dispatcher.AUDIT_LOGS_DIR", tmp_path):
            report = d._write_triage_log({"result": {"needs_human": False, "reason": "ok"}})
        assert report.status == "modified"
        assert "CLEAR" in report.detail


class TestActionDispatcherDrainResults:
    def test_drain_results_completed_tasks(self):
        d = ActionDispatcher()
        task = _FakeTask(task_id="t1", capability="unknown_cap", result={"x": 1})
        scheduler = MagicMock()
        scheduler._lock = MagicMock()
        scheduler._results = {"t1": task}
        scheduler._lock.__enter__ = MagicMock(return_value=None)
        scheduler._lock.__exit__ = MagicMock(return_value=None)
        reports = d.drain_results(scheduler)
        assert len(reports) == 1
        assert d.stats["dispatched"] == 1

    def test_drain_results_skips_acted(self):
        d = ActionDispatcher()
        task = _FakeTask(task_id="t1", capability="unknown_cap", result={"x": 1})
        task._acted = True
        scheduler = MagicMock()
        scheduler._lock = MagicMock()
        scheduler._results = {"t1": task}
        scheduler._lock.__enter__ = MagicMock(return_value=None)
        scheduler._lock.__exit__ = MagicMock(return_value=None)
        reports = d.drain_results(scheduler)
        assert len(reports) == 0


class TestActionDispatcherHelpers:
    def test_extract_module_name_empty(self):
        d = ActionDispatcher()
        assert d._extract_module_name("") == "unknown"

    def test_extract_module_name_with_prefix(self):
        d = ActionDispatcher()
        assert d._extract_module_name("classify this module: my_mod") == "my_mod"

    def test_build_py_brain_block(self):
        block = ActionDispatcher._build_py_brain_block({"key": "val"})
        assert "# BRAIN key:" in block
        assert "# BRAIN at:" in block

    def test_insert_brain_block(self):
        original = "x = 1\n"
        block = "# BRAIN test: true"
        result = ActionDispatcher._insert_brain_block(original, block)
        assert "# BRAIN test: true" in result
        assert "x = 1" in result

    def test_update_brain_block(self):
        original = "# BRAIN old: true\nx = 1\n"
        block = "# BRAIN new: true"
        result = ActionDispatcher._update_brain_block(original, block)
        assert "# BRAIN new: true" in result
        assert "# BRAIN old: true" not in result


class TestActionReport:
    def test_repr(self):
        r = ActionReport("target", "cap", "ok", "detail")
        assert "target" in repr(r)
        assert "cap" in repr(r)
        assert "ok" in repr(r)

    def test_fields(self):
        r = ActionReport("t", "c", "s", "d")
        assert r.target == "t"
        assert r.capability == "c"
        assert r.status == "s"
        assert r.detail == "d"
