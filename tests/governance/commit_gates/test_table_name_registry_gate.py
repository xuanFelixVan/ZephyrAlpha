# [BLUEPRINT] MOD-GOV_COMMIT_GATES | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# -*- coding: utf-8 -*-
"""test_table_name_registry_gate.py — TABLE-NAME-REGISTRY gate 测试

裁定 #ARCH-CH-024 Phase 4：SSoT 真源强制闭环。
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from zephyr.data.table_registry import TableRegistry
from zephyr.gov_enforcement.commit_gates.table_name_registry_gate import (
    _build_table_name_pattern,
    check_hardcoded_tables_in_file,
    check_tasks_yaml_tables,
    make_table_name_registry_gate,
)

# ============================================================================
# 测试辅助
# ============================================================================


def _make_test_registry() -> TableRegistry:
    """构造测试用 TableRegistry（2 条品类）。"""
    return TableRegistry(categories=[
        {
            "category_id": "market_kline_daily",
            "database": "c1_market",
            "table": "kline_daily",
        },
        {
            "category_id": "market_adj_factor",
            "database": "c1_market",
            "table": "adj_factor",
        },
    ])


def _make_mock_gateway(staged_files: dict[str, str] | None = None) -> MagicMock:
    """构造 mock gateway，用于 diff-based gate 测试。

    所有 staged 文件视为新文件（全行 added），适合防蔓延检测测试。
    """
    staged = staged_files or {}

    def _run_git(cmd):
        result = MagicMock()

        if "show" in cmd:
            show_idx = cmd.index("show")
            path = cmd[show_idx + 1].lstrip(":")
            content = staged.get(path, "")
            result.returncode = 0 if path in staged else 1
            result.stdout = content

        elif "--name-only" in cmd:
            py_files = [f for f in staged if f.endswith(".py")]
            result.returncode = 0
            result.stdout = "\n".join(py_files)

        elif "--unified=0" in cmd:
            path = cmd[-1]
            content = staged.get(path, "")
            lines = content.splitlines()
            if lines:
                result.stdout = (
                    f"@@ -0,0 +1,{len(lines)} @@\n"
                    + "".join(f"+{l}\n" for l in lines)
                )
            else:
                result.stdout = ""
            result.returncode = 0

        else:
            result.returncode = 1
            result.stdout = ""

        return result

    gw = MagicMock()
    gw.run_git = _run_git
    gw.project_root = "/test"
    return gw


# ============================================================================
# _build_table_name_pattern 测试
# ============================================================================


class TestBuildTableNamePattern:
    """测试表名子串匹配正则构建。"""

    def test_build_with_tables(self):
        """有表名时返回编译后的正则。"""
        tables = {"c1_market.kline_daily", "c1_market.adj_factor"}
        pattern = _build_table_name_pattern(tables)
        assert pattern is not None
        assert pattern.search("SELECT * FROM c1_market.kline_daily")

    def test_build_empty(self):
        """空集合返回 None。"""
        assert _build_table_name_pattern(set()) is None

    def test_build_matches_exact(self):
        """精确匹配表名。"""
        tables = {"c1_market.kline_daily"}
        pattern = _build_table_name_pattern(tables)
        assert pattern.findall("c1_market.kline_daily") == ["c1_market.kline_daily"]

    def test_build_longer_table_preferred(self):
        """长表名优先匹配（避免短名误匹配）。"""
        tables = {"c1_market.k", "c1_market.kline_daily"}
        pattern = _build_table_name_pattern(tables)
        matches = pattern.findall("SELECT FROM c1_market.kline_daily")
        assert "c1_market.kline_daily" in matches


# ============================================================================
# check_hardcoded_tables_in_file 测试
# ============================================================================


class TestCheckHardcodedTablesInFile:
    """检测单个文件中的硬编码表名。"""

    def test_exact_match_hardcoded(self):
        """精确匹配：直接硬编码表名 → 违规。"""
        content = 'TABLE_NAME = "c1_market.kline_daily"\n'
        gw = _make_mock_gateway({"src/zephyr/data/foo.py": content})
        tables = {"c1_market.kline_daily", "c1_market.adj_factor"}
        pattern = _build_table_name_pattern(tables)
        violations = check_hardcoded_tables_in_file(
            gw, "src/zephyr/data/foo.py", tables, pattern
        )
        assert len(violations) == 1
        assert "c1_market.kline_daily" in violations[0]
        assert "TableRegistry" in violations[0]

    def test_substring_match_in_sql(self):
        """子串匹配：SQL 字符串含表名 → 违规。"""
        content = (
            'sql = "SELECT * FROM c1_market.kline_daily WHERE trade_date > ?"\n'
        )
        gw = _make_mock_gateway({"src/zephyr/data/foo.py": content})
        tables = {"c1_market.kline_daily"}
        pattern = _build_table_name_pattern(tables)
        violations = check_hardcoded_tables_in_file(
            gw, "src/zephyr/data/foo.py", tables, pattern
        )
        assert len(violations) == 1
        assert "c1_market.kline_daily" in violations[0]

    def test_no_table_name(self):
        """字符串不含表名 → 通过。"""
        content = 'msg = "hello world"\n'
        gw = _make_mock_gateway({"src/zephyr/data/foo.py": content})
        tables = {"c1_market.kline_daily"}
        pattern = _build_table_name_pattern(tables)
        violations = check_hardcoded_tables_in_file(
            gw, "src/zephyr/data/foo.py", tables, pattern
        )
        assert violations == []

    def test_docstring_exempt(self):
        """docstring 中的表名 → 豁免。"""
        content = (
            '"""Module docstring.\n\n'
            '    Uses c1_market.kline_daily table.\n'
            '    """\n'
            'x = 1\n'
        )
        gw = _make_mock_gateway({"src/zephyr/data/foo.py": content})
        tables = {"c1_market.kline_daily"}
        pattern = _build_table_name_pattern(tables)
        violations = check_hardcoded_tables_in_file(
            gw, "src/zephyr/data/foo.py", tables, pattern
        )
        assert violations == []

    def test_empty_file_content(self):
        """空文件内容 → 通过。"""
        gw = _make_mock_gateway({"src/zephyr/data/foo.py": ""})
        tables = {"c1_market.kline_daily"}
        pattern = _build_table_name_pattern(tables)
        violations = check_hardcoded_tables_in_file(
            gw, "src/zephyr/data/foo.py", tables, pattern
        )
        assert violations == []

    def test_no_added_lines(self):
        """无 added 行（modified 文件未改含表名的行）→ 通过。"""
        content = 'TABLE = "c1_market.kline_daily"\n'
        gw = _make_mock_gateway({"src/zephyr/data/foo.py": content})
        # Override _get_added_lines to return empty
        with patch(
            "zephyr.gov_enforcement.commit_gates.table_name_registry_gate"
            "._get_added_lines",
            return_value=[],
        ):
            tables = {"c1_market.kline_daily"}
            pattern = _build_table_name_pattern(tables)
            violations = check_hardcoded_tables_in_file(
                gw, "src/zephyr/data/foo.py", tables, pattern
            )
            assert violations == []

    def test_multiple_violations(self):
        """多行硬编码表名 → 多条违规。"""
        content = (
            'T1 = "c1_market.kline_daily"\n'
            'T2 = "c1_market.adj_factor"\n'
            'T3 = "not_a_table"\n'
        )
        gw = _make_mock_gateway({"src/zephyr/data/foo.py": content})
        tables = {"c1_market.kline_daily", "c1_market.adj_factor"}
        pattern = _build_table_name_pattern(tables)
        violations = check_hardcoded_tables_in_file(
            gw, "src/zephyr/data/foo.py", tables, pattern
        )
        assert len(violations) == 2

    def test_syntax_error_fail_open(self):
        """语法错误 → fail-open 返回空。"""
        content = 'def broken(:\n'
        gw = _make_mock_gateway({"src/zephyr/data/foo.py": content})
        tables = {"c1_market.kline_daily"}
        pattern = _build_table_name_pattern(tables)
        violations = check_hardcoded_tables_in_file(
            gw, "src/zephyr/data/foo.py", tables, pattern
        )
        assert violations == []


# ============================================================================
# check_tasks_yaml_tables 测试
# ============================================================================


class TestCheckTasksYamlTables:
    """检测 tasks.yaml 表名校验。"""

    def test_registered_table_pass(self):
        """tasks.yaml 表名已注册 → 通过。"""
        content = (
            "tasks:\n"
            "  - task_id: test_task\n"
            "    table: c1_market.kline_daily\n"
        )
        gw = _make_mock_gateway({"src/zephyr/data/config/tasks.yaml": content})
        registry = _make_test_registry()
        warnings = check_tasks_yaml_tables(gw, registry)
        assert warnings == []

    def test_unregistered_table_warn(self):
        """tasks.yaml 表名未注册 → 警告。"""
        content = (
            "tasks:\n"
            "  - task_id: test_task\n"
            "    table: c1_market.nonexistent\n"
        )
        gw = _make_mock_gateway({"src/zephyr/data/config/tasks.yaml": content})
        registry = _make_test_registry()
        warnings = check_tasks_yaml_tables(gw, registry)
        assert len(warnings) == 1
        assert "nonexistent" in warnings[0]

    def test_empty_tasks(self):
        """空 tasks 列表 → 通过。"""
        content = "tasks: []\n"
        gw = _make_mock_gateway({"src/zephyr/data/config/tasks.yaml": content})
        registry = _make_test_registry()
        warnings = check_tasks_yaml_tables(gw, registry)
        assert warnings == []

    def test_no_table_field(self):
        """任务无 table 字段 → 跳过。"""
        content = (
            "tasks:\n"
            "  - task_id: no_table_task\n"
            "    source: test\n"
        )
        gw = _make_mock_gateway({"src/zephyr/data/config/tasks.yaml": content})
        registry = _make_test_registry()
        warnings = check_tasks_yaml_tables(gw, registry)
        assert warnings == []

    def test_yaml_parse_error_fail_open(self):
        """YAML 解析失败 → fail-open。"""
        content = "invalid: yaml: ["
        gw = _make_mock_gateway({"src/zephyr/data/config/tasks.yaml": content})
        registry = _make_test_registry()
        warnings = check_tasks_yaml_tables(gw, registry)
        assert warnings == []

    def test_empty_content_fail_open(self):
        """空内容 → fail-open。"""
        gw = _make_mock_gateway({})
        registry = _make_test_registry()
        warnings = check_tasks_yaml_tables(gw, registry)
        assert warnings == []


# ============================================================================
# GateSpec 字段测试
# ============================================================================


class TestGateSpecFields:
    """测试 GateSpec 字段。"""

    def test_gate_id(self):
        assert make_table_name_registry_gate().gate_id == "TABLE-NAME-REGISTRY"

    def test_priority_is_120(self):
        # 119=NOQA-DENSITY 已占用，用 120
        assert make_table_name_registry_gate().priority == 120

    def test_check_callable(self):
        assert callable(make_table_name_registry_gate().check)


# ============================================================================
# _check 闭包测试
# ============================================================================


class TestCheckClosure:
    """测试 _check 闭包行为。"""

    @patch(
        "zephyr.gov_enforcement.commit_gates.table_name_registry_gate.get_registry"
    )
    def test_no_staged_py_files(self, mock_get_registry, tmp_path):
        """无 staged .py 文件且无 tasks.yaml → 放行。"""
        mock_get_registry.return_value = _make_test_registry()
        gw = _make_mock_gateway({})
        gate = make_table_name_registry_gate()
        passed, detail = gate.check(gw, ["docs/readme.md"])
        assert passed is True
        assert detail == ""

    @patch(
        "zephyr.gov_enforcement.commit_gates.table_name_registry_gate.get_registry"
    )
    def test_hardcoded_table_block(self, mock_get_registry, tmp_path):
        """staged .py 含硬编码表名 → block（passed=False 阻断 commit）。"""
        mock_get_registry.return_value = _make_test_registry()
        content = 'TABLE = "c1_market.kline_daily"\n'
        gw = _make_mock_gateway({"src/zephyr/data/foo.py": content})
        gate = make_table_name_registry_gate()
        passed, detail = gate.check(gw, ["src/zephyr/data/foo.py"])
        assert passed is False  # block
        assert "c1_market.kline_daily" in detail
        assert "TableRegistry" in detail

    @patch(
        "zephyr.gov_enforcement.commit_gates.table_name_registry_gate.get_registry"
    )
    def test_no_hardcoded_table_pass(self, mock_get_registry, tmp_path):
        """staged .py 不含表名 → 放行。"""
        mock_get_registry.return_value = _make_test_registry()
        content = 'msg = "hello"\n'
        gw = _make_mock_gateway({"src/zephyr/data/foo.py": content})
        gate = make_table_name_registry_gate()
        passed, detail = gate.check(gw, ["src/zephyr/data/foo.py"])
        assert passed is True
        assert detail == ""

    @patch(
        "zephyr.gov_enforcement.commit_gates.table_name_registry_gate.get_registry"
    )
    def test_tests_exempt(self, mock_get_registry, tmp_path):
        """tests/ 文件豁免 → 放行（即使含硬编码表名）。"""
        mock_get_registry.return_value = _make_test_registry()
        content = 'TABLE = "c1_market.kline_daily"\n'
        gw = _make_mock_gateway({"tests/test_foo.py": content})
        gate = make_table_name_registry_gate()
        passed, detail = gate.check(gw, ["tests/test_foo.py"])
        assert passed is True
        assert detail == ""

    @patch(
        "zephyr.gov_enforcement.commit_gates.table_name_registry_gate.get_registry"
    )
    def test_table_registry_exempt(self, mock_get_registry, tmp_path):
        """table_registry.py 自身豁免 → 放行。"""
        mock_get_registry.return_value = _make_test_registry()
        content = 'TABLE = "c1_market.kline_daily"\n'
        gw = _make_mock_gateway(
            {"src/zephyr/data/table_registry.py": content}
        )
        gate = make_table_name_registry_gate()
        passed, detail = gate.check(
            gw, ["src/zephyr/data/table_registry.py"]
        )
        assert passed is True
        assert detail == ""

    @patch(
        "zephyr.gov_enforcement.commit_gates.table_name_registry_gate.get_registry"
    )
    def test_tasks_yaml_unregistered_block(self, mock_get_registry, tmp_path):
        """tasks.yaml 含未注册表名 → block（passed=False 阻断 commit）。"""
        mock_get_registry.return_value = _make_test_registry()
        tasks_content = (
            "tasks:\n"
            "  - task_id: bad_task\n"
            "    table: c1_market.nonexistent\n"
        )
        gw = _make_mock_gateway(
            {"src/zephyr/data/config/tasks.yaml": tasks_content}
        )
        gate = make_table_name_registry_gate()
        passed, detail = gate.check(
            gw, ["src/zephyr/data/config/tasks.yaml"]
        )
        assert passed is False  # block
        assert "nonexistent" in detail

    @patch(
        "zephyr.gov_enforcement.commit_gates.table_name_registry_gate.get_registry"
    )
    def test_tasks_yaml_registered_pass(self, mock_get_registry, tmp_path):
        """tasks.yaml 表名全部已注册 → 放行。"""
        mock_get_registry.return_value = _make_test_registry()
        tasks_content = (
            "tasks:\n"
            "  - task_id: good_task\n"
            "    table: c1_market.kline_daily\n"
        )
        gw = _make_mock_gateway(
            {"src/zephyr/data/config/tasks.yaml": tasks_content}
        )
        gate = make_table_name_registry_gate()
        passed, detail = gate.check(
            gw, ["src/zephyr/data/config/tasks.yaml"]
        )
        assert passed is True
        assert detail == ""

    @patch(
        "zephyr.gov_enforcement.commit_gates.table_name_registry_gate.get_registry"
    )
    def test_empty_registry_fail_open(self, mock_get_registry, tmp_path):
        """TableRegistry 为空 → fail-open。"""
        mock_get_registry.return_value = TableRegistry(categories=[])
        content = 'TABLE = "c1_market.kline_daily"\n'
        gw = _make_mock_gateway({"src/zephyr/data/foo.py": content})
        gate = make_table_name_registry_gate()
        passed, detail = gate.check(gw, ["src/zephyr/data/foo.py"])
        assert passed is True
        assert detail == ""

    @patch(
        "zephyr.gov_enforcement.commit_gates.table_name_registry_gate.get_registry"
    )
    def test_registry_load_error_fail_open(self, mock_get_registry, tmp_path):
        """TableRegistry 加载异常 → fail-open。"""
        mock_get_registry.side_effect = RuntimeError("DB down")
        content = 'TABLE = "c1_market.kline_daily"\n'
        gw = _make_mock_gateway({"src/zephyr/data/foo.py": content})
        gate = make_table_name_registry_gate()
        passed, detail = gate.check(gw, ["src/zephyr/data/foo.py"])
        assert passed is True
        assert detail == ""

    @patch(
        "zephyr.gov_enforcement.commit_gates.table_name_registry_gate.get_registry"
    )
    def test_both_detection_modes(self, mock_get_registry, tmp_path):
        """同时触发两种检测模式（.py 硬编码 + tasks.yaml 未注册）。"""
        mock_get_registry.return_value = _make_test_registry()
        py_content = 'TABLE = "c1_market.kline_daily"\n'
        tasks_content = (
            "tasks:\n"
            "  - task_id: bad_task\n"
            "    table: c1_market.nonexistent\n"
        )
        gw = _make_mock_gateway({
            "src/zephyr/data/foo.py": py_content,
            "src/zephyr/data/config/tasks.yaml": tasks_content,
        })
        gate = make_table_name_registry_gate()
        passed, detail = gate.check(
            gw,
            ["src/zephyr/data/foo.py", "src/zephyr/data/config/tasks.yaml"],
        )
        assert passed is False  # block
        assert "c1_market.kline_daily" in detail  # Detection 1
        assert "nonexistent" in detail  # Detection 2

    @patch(
        "zephyr.gov_enforcement.commit_gates.table_name_registry_gate.get_registry"
    )
    def test_windows_path_normalization(self, mock_get_registry, tmp_path):
        """Windows 反斜杠路径归一化（tasks.yaml 触发）。"""
        mock_get_registry.return_value = _make_test_registry()
        tasks_content = (
            "tasks:\n"
            "  - task_id: bad_task\n"
            "    table: c1_market.nonexistent\n"
        )
        gw = _make_mock_gateway(
            {"src/zephyr/data/config/tasks.yaml": tasks_content}
        )
        gate = make_table_name_registry_gate()
        passed, detail = gate.check(
            gw,
            ["src\\zephyr\\data\\config\\tasks.yaml"],
        )
        assert passed is False  # block
        assert "nonexistent" in detail
