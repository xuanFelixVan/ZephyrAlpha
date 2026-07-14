# [A_test] module_id: SRC-TST-2240 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_ch_version_col_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_ch_version_col_gate.py — CH-VERSION-COL 门禁单测

权威依据：ch_version_col_gate.py（make_ch_version_col_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestBlockedVersionCols: _BLOCKED_VERSION_COLS 集合内容
- TestRegexPattern: _REPLACING_MT_PATTERN 正则匹配
- TestGatewayIntegration: mock gateway 流程
  - ReplacingMergeTree(quality_flag) in .py → 阻断
  - ReplacingMergeTree(ingest_ts) in .py → 放行
  - ReplacingMergeTree(quality_flag) in .md → 阻断
  - tests/ 豁免
  - 多文件多违规 → 汇总
  - git diff 失败 → fail-open
  - 空 staged → 放行

测试隔离：MagicMock 模拟 gateway._run_git，不读/不写真实仓库。
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.commit_gates.ch_version_col_gate import (  # noqa: E402
    _BLOCKED_VERSION_COLS,
    _REPLACING_MT_PATTERN,
    make_ch_version_col_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


def _make_gateway(staged_files: list[str], added_lines: dict[str, list[str]]):
    """构造 mock gateway，模拟 git diff --cached 输出。

    Args:
        staged_files: staged 文件路径列表（--name-only 输出）。
        added_lines: {rel_path: [added_line_text, ...]}（--unified=0 输出）。
    """
    gw = MagicMock()
    files_list = "\n".join(staged_files)

    def _run_git(cmd):
        if "--name-only" in cmd:
            return _MockResult(returncode=0, stdout=files_list)
        if "--unified=0" in cmd:
            # cmd 最后一个非 '--' 的参数是文件路径
            for arg in cmd:
                if arg and arg != "--" and ("." in arg or "/" in arg):
                    lines = added_lines.get(arg, [])
                    diff_lines = ["+++ b/" + arg]
                    for ln in lines:
                        diff_lines.append("+" + ln)
                    return _MockResult(returncode=0, stdout="\n".join(diff_lines))
            return _MockResult(returncode=0, stdout="")
        return _MockResult(returncode=0, stdout="")

    gw._run_git = _run_git
    return gw


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------
class TestGateSpecFields:
    def test_is_gate_spec(self):
        assert isinstance(make_ch_version_col_gate(), GateSpec)

    def test_gate_id(self):
        assert make_ch_version_col_gate().gate_id == "CH-VERSION-COL"

    def test_priority(self):
        assert make_ch_version_col_gate().priority == 38


# ---------------------------------------------------------------------------
# TestBlockedVersionCols — _BLOCKED_VERSION_COLS 集合内容
# ---------------------------------------------------------------------------
class TestBlockedVersionCols:
    def test_quality_flag_in_blocked(self):
        assert "quality_flag" in _BLOCKED_VERSION_COLS

    def test_is_deleted_in_blocked(self):
        assert "is_deleted" in _BLOCKED_VERSION_COLS

    def test_ingest_ts_not_in_blocked(self):
        assert "ingest_ts" not in _BLOCKED_VERSION_COLS


# ---------------------------------------------------------------------------
# TestRegexPattern — _REPLACING_MT_PATTERN 正则匹配
# ---------------------------------------------------------------------------
class TestRegexPattern:
    def test_matches_simple(self):
        m = _REPLACING_MT_PATTERN.search("ENGINE = ReplacingMergeTree(quality_flag)")
        assert m is not None
        assert m.group(1) == "quality_flag"

    def test_matches_with_spaces(self):
        m = _REPLACING_MT_PATTERN.search("ReplacingMergeTree( quality_flag )")
        assert m is not None
        assert m.group(1) == "quality_flag"

    def test_case_insensitive(self):
        m = _REPLACING_MT_PATTERN.search("replacingmergetree(quality_flag)")
        assert m is not None
        assert m.group(1) == "quality_flag"

    def test_no_match_plain_mergetree(self):
        m = _REPLACING_MT_PATTERN.search("ENGINE = MergeTree()")
        assert m is None


# ---------------------------------------------------------------------------
# TestGatewayIntegration — mock gateway 流程
# ---------------------------------------------------------------------------
class TestGatewayIntegration:
    def test_quality_flag_in_py_blocked(self):
        """staged .py 文件含 ReplacingMergeTree(quality_flag) → 阻断。"""
        rel = "src/zephyr/data/scheduler.py"
        gw = _make_gateway(
            staged_files=[rel],
            added_lines={rel: ["ENGINE = ReplacingMergeTree(quality_flag)"]},
        )
        passed, msg = make_ch_version_col_gate().check(gw, [])
        assert not passed
        assert "CH-VERSION-COL" in msg
        assert "quality_flag" in msg
        assert "#ARCH-CH-009" in msg

    def test_ingest_ts_in_py_passes(self):
        """staged .py 文件含 ReplacingMergeTree(ingest_ts) → 放行。"""
        rel = "src/zephyr/data/scheduler.py"
        gw = _make_gateway(
            staged_files=[rel],
            added_lines={rel: ["ENGINE = ReplacingMergeTree(ingest_ts)"]},
        )
        passed, msg = make_ch_version_col_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_quality_flag_in_md_blocked(self):
        """staged .md 文件含 ReplacingMergeTree(quality_flag) → 阻断。"""
        rel = "docs/03_modules/_cross_layer/database/sub_blueprint.md"
        gw = _make_gateway(
            staged_files=[rel],
            added_lines={rel: ["ENGINE = ReplacingMergeTree(quality_flag)"]},
        )
        passed, msg = make_ch_version_col_gate().check(gw, [])
        assert not passed
        assert "CH-VERSION-COL" in msg

    def test_tests_dir_exempt(self):
        """tests/ 目录豁免。"""
        rel = "tests/governance/test_something.py"
        gw = _make_gateway(
            staged_files=[rel],
            added_lines={rel: ["ENGINE = ReplacingMergeTree(quality_flag)"]},
        )
        passed, msg = make_ch_version_col_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_multiple_violations_aggregated(self):
        """多文件多违规 → 汇总报告。"""
        rel1 = "src/zephyr/data/a.py"
        rel2 = "src/zephyr/data/b.py"
        gw = _make_gateway(
            staged_files=[rel1, rel2],
            added_lines={
                rel1: ["ENGINE = ReplacingMergeTree(quality_flag)"],
                rel2: ["ENGINE = ReplacingMergeTree(is_deleted)"],
            },
        )
        passed, msg = make_ch_version_col_gate().check(gw, [])
        assert not passed
        assert rel1 in msg
        assert rel2 in msg
        assert "quality_flag" in msg
        assert "is_deleted" in msg

    def test_fail_open_on_git_diff_failure(self):
        """git diff --name-only 失败 → fail-open。"""
        gw = MagicMock()

        def _run_git(cmd):
            if "--name-only" in cmd:
                return _MockResult(returncode=1, stdout="")
            return _MockResult(returncode=0, stdout="")

        gw._run_git = _run_git
        passed, msg = make_ch_version_col_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_empty_staged_passes(self):
        """空 staged → 放行。"""
        gw = _make_gateway(staged_files=[], added_lines={})
        passed, msg = make_ch_version_col_gate().check(gw, [])
        assert passed
        assert msg == ""
