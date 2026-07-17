# [BLUEPRINT] MOD-GOV-commit_gates | (auto-injected by S4 reconciler) | §
# [TTL] task_bound
"""test_data_task_completeness_gate.py — 数据任务完整性门禁单元测试。

测试组：
- TestGateSpecAttributes: GateSpec 属性（gate_id / priority）
- TestExtractNewTaskIds: git diff 新增 task_id 提取
- TestCheckTaskHasFallback: 任务 fallback_sources 检测
- TestCheckNoTasksYamlChange: tasks.yaml 未修改时跳过
- TestCheckNewTaskWithFallback: 新增任务有 fallback_sources 通过
- TestCheckNewTaskWithoutFallback: 新增任务无 fallback_sources warn（不阻断）
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

_SRC = Path(__file__).parent.parent.parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from zephyr.gov_enforcement.commit_gates.data_task_completeness_gate import (  # noqa: E402
    make_data_task_completeness_gate,
    _extract_new_task_ids,
    _check_task_has_fallback,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


class _MockGateway:
    """Mock gateway——data_task_completeness_gate 只用 project_root 属性。"""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root


class TestGateSpecAttributes:
    """GateSpec 属性。"""

    def test_gate_id(self):
        spec = make_data_task_completeness_gate()
        assert spec.gate_id == "DATA-TASK-COMPLETENESS"

    def test_priority_is_78(self):
        spec = make_data_task_completeness_gate()
        assert spec.priority == 78

    def test_returns_gate_spec_instance(self):
        spec = make_data_task_completeness_gate()
        assert isinstance(spec, GateSpec)


class TestExtractNewTaskIds:
    """git diff 新增 task_id 提取。"""

    def test_single_new_task(self):
        diff = "+  - task_id: new_task_incremental\n+    table: c1_market.new_table"
        ids = _extract_new_task_ids(diff)
        assert ids == ["new_task_incremental"]

    def test_multiple_new_tasks(self):
        diff = (
            "+  - task_id: task_a_incremental\n"
            "+    table: c1_market.task_a\n"
            "+  - task_id: task_b_incremental\n"
            "+    table: c1_market.task_b\n"
        )
        ids = _extract_new_task_ids(diff)
        assert ids == ["task_a_incremental", "task_b_incremental"]

    def test_no_new_tasks(self):
        diff = "+    description: 'updated description'\n+    extra:"
        ids = _extract_new_task_ids(diff)
        assert ids == []

    def test_ignores_removed_tasks(self):
        """删除的行（- 前缀）不算新增。"""
        diff = "-  - task_id: removed_task_incremental\n+  - task_id: added_task_incremental"
        ids = _extract_new_task_ids(diff)
        assert ids == ["added_task_incremental"]

    def test_empty_diff(self):
        assert _extract_new_task_ids("") == []


class TestCheckTaskHasFallback:
    """任务 fallback_sources 检测。"""

    def test_has_fallback(self):
        tasks = [
            {"task_id": "task_a", "fallback_sources": [{"source": "akshare"}]},
        ]
        assert _check_task_has_fallback(tasks, "task_a") is True

    def test_no_fallback(self):
        tasks = [
            {"task_id": "task_a"},
        ]
        assert _check_task_has_fallback(tasks, "task_a") is False

    def test_empty_fallback(self):
        tasks = [
            {"task_id": "task_a", "fallback_sources": []},
        ]
        assert _check_task_has_fallback(tasks, "task_a") is False

    def test_task_not_found(self):
        """找不到任务（可能已删除）-> 不告警。"""
        tasks = [{"task_id": "task_a"}]
        assert _check_task_has_fallback(tasks, "nonexistent") is True


class TestCheckNoTasksYamlChange:
    """tasks.yaml 未修改时跳过。"""

    def test_no_tasks_yaml_in_files(self, tmp_path):
        gw = _MockGateway(tmp_path)
        spec = make_data_task_completeness_gate()
        passed, detail = spec.check(gw, ["src/zephyr/data/scheduler.py"])
        assert passed is True
        assert "skip" in detail


class TestCheckNewTaskWithFallback:
    """新增任务有 fallback_sources——通过（warn 级始终 passed=True）。"""

    def test_new_task_has_fallback(self, tmp_path):
        gw = _MockGateway(tmp_path)
        spec = make_data_task_completeness_gate()

        mock_diff = "+  - task_id: new_task_incremental\n+    fallback_sources:\n+      - source: akshare"
        mock_subprocess = MagicMock()
        mock_subprocess.returncode = 0
        mock_subprocess.stdout = mock_diff

        tasks = [{"task_id": "new_task_incremental", "fallback_sources": [{"source": "akshare"}]}]

        with patch("zephyr.gov_enforcement.commit_gates.data_task_completeness_gate.subprocess.run", return_value=mock_subprocess), \
             patch("zephyr.gov_enforcement.commit_gates.data_task_completeness_gate._load_tasks_yaml", return_value=tasks):
            passed, detail = spec.check(gw, ["src/zephyr/data/config/tasks.yaml"])

        assert passed is True
        assert "have fallback_sources" in detail


class TestCheckNewTaskWithoutFallback:
    """新增任务无 fallback_sources——warn（passed=True 但 detail 含 WARN）。"""

    def test_new_task_missing_fallback(self, tmp_path):
        gw = _MockGateway(tmp_path)
        spec = make_data_task_completeness_gate()

        mock_diff = "+  - task_id: new_task_incremental\n+    table: c1_market.new_table"
        mock_subprocess = MagicMock()
        mock_subprocess.returncode = 0
        mock_subprocess.stdout = mock_diff

        tasks = [{"task_id": "new_task_incremental"}]  # 无 fallback_sources

        with patch("zephyr.gov_enforcement.commit_gates.data_task_completeness_gate.subprocess.run", return_value=mock_subprocess), \
             patch("zephyr.gov_enforcement.commit_gates.data_task_completeness_gate._load_tasks_yaml", return_value=tasks):
            passed, detail = spec.check(gw, ["src/zephyr/data/config/tasks.yaml"])

        # warn 级——始终 passed=True（不阻断 commit）
        assert passed is True
        assert "WARN" in detail
        assert "new_task_incremental" in detail
        assert "fallback_sources" in detail

    def test_no_new_tasks_in_diff(self, tmp_path):
        """tasks.yaml 修改但无新增 task_id。"""
        gw = _MockGateway(tmp_path)
        spec = make_data_task_completeness_gate()

        mock_diff = "+    description: 'updated description'"
        mock_subprocess = MagicMock()
        mock_subprocess.returncode = 0
        mock_subprocess.stdout = mock_diff

        with patch("zephyr.gov_enforcement.commit_gates.data_task_completeness_gate.subprocess.run", return_value=mock_subprocess):
            passed, detail = spec.check(gw, ["src/zephyr/data/config/tasks.yaml"])

        assert passed is True
        assert "no new task_id" in detail
