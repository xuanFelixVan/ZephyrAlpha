# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.audit.test_undefined_name_baseline_reconciler
# [DOMAIN] D_GOV_AUDIT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_undefined_name_baseline_reconciler.py — GATE-UNDEFINED-NAME-BASELINE reconciler 单测

权威依据：reconciliation_registry.py::make_undefined_name_baseline_reconciler
（GATE-DEPGRAPH-OPS 治本 Phase 1 baseline 全扫）

测试组：
- TestReconcilerSpecFields: gate_id / priority / isinstance(ReconcilerSpec)
- TestTrigger: scripts/governance/*.py 触发 / src/*.py 触发 / undefined_name_gate.py 触发 /
  .md 不触发 / 空列表不触发
- TestReconcile: tmp_path 隔离环境，直接复用真实 scan_all_for_undefined_names
  - 无 src/ 与 scripts/governance/ → skip
  - 合法 .py 文件（无 undefined name） → clean
  - 含 undefined name 的 .py 文件 → warn
  - 多个违规被计数
  - 只扫 scripts/governance/ + src/ 下文件（其他路径忽略）
  - scan 异常 → warn 降级（monkeypatch 注入）
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.governance.audit.reconciliation_registry import (  # noqa: E402
    ReconcilerSpec,
    make_undefined_name_baseline_reconciler,
)


def _make_gateway(project_root: Path) -> MagicMock:
    """构造 mock gateway：仅暴露 project_root 属性。"""
    gw = MagicMock()
    gw.project_root = project_root
    return gw


def _write_py_file(project_root: Path, rel_path: str, content: str) -> Path:
    """在 project_root 下写一个 .py 文件。

    Args:
        rel_path: 相对路径（如 "src/zephyr/foo.py"）
        content: 文件内容

    Returns:
        文件绝对路径。
    """
    file_path = project_root / rel_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return file_path


# 合法 .py 文件：所有名字都有定义/import
_CLEAN_SRC = '''\
"""clean module — no undefined names."""
import os
import sys


def foo(x: int) -> int:
    return x + 1


class Bar:
    def __init__(self) -> None:
        self.value = foo(42)


BUZZ = Bar()
print(os.getcwd(), sys.version, BUZZ.value)
'''

# 含 undefined name 的 .py 文件：使用了未 import/未定义的符号
_DIRTY_SRC = '''\
"""dirty module — uses undefined name 'ghost_function'."""
def helper() -> None:
    result = ghost_function(42)  # noqa: F821 — undefined name (test fixture)
    return result
'''

# 含多个 undefined name 的 .py 文件
_MULTI_DIRTY_SRC = '''\
"""multiple undefined names."""
def func() -> None:
    a = undefined_one  # noqa: F821
    b = undefined_two  # noqa: F821
    c = undefined_three  # noqa: F821
    return a + b + c
'''


class TestReconcilerSpecFields:
    """ReconcilerSpec 字段校验。"""

    def test_gate_id(self, tmp_path: Path) -> None:
        gw = _make_gateway(tmp_path)
        spec = make_undefined_name_baseline_reconciler(gw)
        assert spec.gate_id == "GATE-UNDEFINED-NAME-BASELINE"

    def test_priority(self, tmp_path: Path) -> None:
        gw = _make_gateway(tmp_path)
        spec = make_undefined_name_baseline_reconciler(gw)
        assert spec.priority == 211

    def test_is_reconciler_spec(self, tmp_path: Path) -> None:
        gw = _make_gateway(tmp_path)
        spec = make_undefined_name_baseline_reconciler(gw)
        assert isinstance(spec, ReconcilerSpec)

    def test_trigger_callable(self, tmp_path: Path) -> None:
        gw = _make_gateway(tmp_path)
        spec = make_undefined_name_baseline_reconciler(gw)
        assert callable(spec.trigger)

    def test_reconcile_callable(self, tmp_path: Path) -> None:
        gw = _make_gateway(tmp_path)
        spec = make_undefined_name_baseline_reconciler(gw)
        assert callable(spec.reconcile)


class TestTrigger:
    """trigger 函数行为。"""

    def test_scripts_governance_py_triggers(self, tmp_path: Path) -> None:
        gw = _make_gateway(tmp_path)
        spec = make_undefined_name_baseline_reconciler(gw)
        assert spec.trigger(["scripts/governance/foo.py"]) is True

    def test_src_py_triggers(self, tmp_path: Path) -> None:
        gw = _make_gateway(tmp_path)
        spec = make_undefined_name_baseline_reconciler(gw)
        assert spec.trigger(["src/zephyr/foo.py"]) is True

    def test_undefined_name_gate_py_triggers(self, tmp_path: Path) -> None:
        """undefined_name_gate.py 自身变更触发（检测逻辑变更应重跑 baseline）。"""
        gw = _make_gateway(tmp_path)
        spec = make_undefined_name_baseline_reconciler(gw)
        assert spec.trigger(["src/zephyr/gov_enforcement/commit_gates/undefined_name_gate.py"]) is True

    def test_md_file_does_not_trigger(self, tmp_path: Path) -> None:
        gw = _make_gateway(tmp_path)
        spec = make_undefined_name_baseline_reconciler(gw)
        assert spec.trigger(["docs/03_modules/foo/blueprint.md"]) is False

    def test_empty_list_does_not_trigger(self, tmp_path: Path) -> None:
        gw = _make_gateway(tmp_path)
        spec = make_undefined_name_baseline_reconciler(gw)
        assert spec.trigger([]) is False

    def test_other_dirs_do_not_trigger(self, tmp_path: Path) -> None:
        """tests/ / docs/ / .runtime/ 等路径不触发（避免无谓全扫开销）。"""
        gw = _make_gateway(tmp_path)
        spec = make_undefined_name_baseline_reconciler(gw)
        assert spec.trigger(["tests/governance/test_foo.py"]) is False
        assert spec.trigger([".runtime/cache.py"]) is False

    def test_windows_path_separator_triggers(self, tmp_path: Path) -> None:
        """Windows 路径分隔符 \\ 也能被正确识别（normalize 后触发）。"""
        gw = _make_gateway(tmp_path)
        spec = make_undefined_name_baseline_reconciler(gw)
        assert spec.trigger(["src\\zephyr\\foo.py"]) is True


class TestReconcile:
    """reconcile 函数行为（tmp_path 隔离环境，复用真实 scan_all_for_undefined_names）。"""

    def test_skip_when_no_scan_dirs(self, tmp_path: Path) -> None:
        """无 src/ 与 scripts/governance/ -> scan 返回 error_msg -> skip（fail-open）。"""
        gw = _make_gateway(tmp_path)
        spec = make_undefined_name_baseline_reconciler(gw)
        result = spec.reconcile(["src/zephyr/foo.py"], "test-session")
        assert result.action == "skip"
        assert "baseline scan skip" in result.detail

    def test_clean_when_no_violations(self, tmp_path: Path) -> None:
        """合法 .py 文件（无 undefined name） -> clean。"""
        _write_py_file(tmp_path, "src/zephyr/clean.py", _CLEAN_SRC)
        gw = _make_gateway(tmp_path)
        spec = make_undefined_name_baseline_reconciler(gw)
        result = spec.reconcile(["src/zephyr/clean.py"], "test-session")
        assert result.action == "clean"
        assert "0 violations" in result.detail

    def test_warn_when_undefined_name_in_src(self, tmp_path: Path) -> None:
        """src/ 下含 undefined name -> warn。"""
        _write_py_file(tmp_path, "src/zephyr/dirty.py", _DIRTY_SRC)
        gw = _make_gateway(tmp_path)
        spec = make_undefined_name_baseline_reconciler(gw)
        result = spec.reconcile(["src/zephyr/dirty.py"], "test-session")
        assert result.action == "warn"
        assert "1 violation" in result.detail
        assert "ghost_function" in result.detail

    def test_warn_when_undefined_name_in_scripts_governance(self, tmp_path: Path) -> None:
        """scripts/governance/ 下含 undefined name -> warn。"""
        _write_py_file(tmp_path, "scripts/governance/dirty.py", _DIRTY_SRC)
        gw = _make_gateway(tmp_path)
        spec = make_undefined_name_baseline_reconciler(gw)
        result = spec.reconcile(["scripts/governance/dirty.py"], "test-session")
        assert result.action == "warn"
        assert "1 violation" in result.detail
        assert "ghost_function" in result.detail

    def test_multiple_violations_counted(self, tmp_path: Path) -> None:
        """单个文件多个 undefined name 都被计数。"""
        _write_py_file(tmp_path, "src/zephyr/multi.py", _MULTI_DIRTY_SRC)
        gw = _make_gateway(tmp_path)
        spec = make_undefined_name_baseline_reconciler(gw)
        result = spec.reconcile(["src/zephyr/multi.py"], "test-session")
        assert result.action == "warn"
        assert "3 violation" in result.detail

    def test_multiple_files_all_scanned(self, tmp_path: Path) -> None:
        """多个违规文件都被扫描计数。"""
        _write_py_file(tmp_path, "src/zephyr/a.py", _DIRTY_SRC)
        _write_py_file(tmp_path, "src/zephyr/b.py", _DIRTY_SRC)
        _write_py_file(tmp_path, "scripts/governance/c.py", _DIRTY_SRC)
        gw = _make_gateway(tmp_path)
        spec = make_undefined_name_baseline_reconciler(gw)
        result = spec.reconcile(["src/zephyr/a.py", "src/zephyr/b.py", "scripts/governance/c.py"], "test-session")
        assert result.action == "warn"
        assert "3 violation" in result.detail

    def test_clean_and_dirty_mixed(self, tmp_path: Path) -> None:
        """混合：1 个 clean 文件 + 1 个 dirty 文件 -> warn 1 violation。"""
        _write_py_file(tmp_path, "src/zephyr/clean.py", _CLEAN_SRC)
        _write_py_file(tmp_path, "src/zephyr/dirty.py", _DIRTY_SRC)
        gw = _make_gateway(tmp_path)
        spec = make_undefined_name_baseline_reconciler(gw)
        result = spec.reconcile(["src/zephyr/clean.py", "src/zephyr/dirty.py"], "test-session")
        assert result.action == "warn"
        assert "1 violation" in result.detail

    def test_other_dirs_not_scanned(self, tmp_path: Path) -> None:
        """tests/ 下的 dirty 文件不在扫描范围（gate 扫 scripts/governance/ + src/）。"""
        _write_py_file(tmp_path, "tests/governance/dirty.py", _DIRTY_SRC)
        gw = _make_gateway(tmp_path)
        spec = make_undefined_name_baseline_reconciler(gw)
        # tests/ 下文件不在扫描范围，且 src/scripts/governance 均无文件 -> skip
        result = spec.reconcile(["tests/governance/dirty.py"], "test-session")
        assert result.action == "skip"

    def test_scan_exception_degrades_to_warn(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """scan_all_for_undefined_names 抛异常 -> 降级 warn（reconciler 容错不阻断）。"""
        _write_py_file(tmp_path, "src/zephyr/clean.py", _CLEAN_SRC)  # 让 src/ 存在以便通过 skip 检查

        def _raise(_project_root):
            raise RuntimeError("simulated scan failure")

        # lazy import 路径：reconciler 内部 `from ...undefined_name_gate import scan_all_for_undefined_names`
        # monkeypatch 替换模块属性，使后续 from-import 拿到抛异常的版本
        from zephyr.gov_enforcement.commit_gates import undefined_name_gate

        monkeypatch.setattr(undefined_name_gate, "scan_all_for_undefined_names", _raise)

        gw = _make_gateway(tmp_path)
        spec = make_undefined_name_baseline_reconciler(gw)
        result = spec.reconcile(["src/zephyr/clean.py"], "test-session")
        assert result.action == "warn"
        assert "降级告警" in result.detail
        assert "simulated scan failure" in result.detail

    def test_detail_truncation_for_many_violations(self, tmp_path: Path) -> None:
        """超过 30 条违规时 detail 截断并显示 (...+N more)。"""
        # 构造 35 个 undefined name（一个文件里）
        lines = ['"""35 undefined names."""', "def f() -> None:"]
        for i in range(35):
            lines.append(f"    _ = ghost_var_{i}  # noqa: F821")
        content = "\n".join(lines) + "\n"
        _write_py_file(tmp_path, "src/zephyr/many.py", content)
        gw = _make_gateway(tmp_path)
        spec = make_undefined_name_baseline_reconciler(gw)
        result = spec.reconcile(["src/zephyr/many.py"], "test-session")
        assert result.action == "warn"
        assert "35 violation" in result.detail
        assert "+5 more" in result.detail
