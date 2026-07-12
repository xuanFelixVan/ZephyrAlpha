# [A_test] module_id: SRC-TST-2223 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-orphan_module_gate | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_orphan_module_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_orphan_module_gate.py — ORPHAN-MODULE 门禁单测

权威依据：orphan_module_gate.py（make_orphan_module_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestEntryPoint: _is_entry_point 纯函数（__main__.py / __init__.py / scripts/ / __main__ 块）
- TestModulePath: _compute_module_path 纯函数（dotted path / __init__ / short name）
- TestGatewayIntegration: mock gateway 流程
  - 新增模块无 import 引用 → 阻断 (passed=False)
  - 新增模块有 import 引用 → 放行 (passed=True)
  - 入口文件豁免
  - tests/ 豁免
  - fail-open on git diff 失败
  - fail-open on git diff 异常
  - fail-open on git grep 超时
  - fail-open on git grep 异常

测试隔离：MagicMock 模拟 gateway._run_git；monkeypatch 模拟 subprocess.run（git grep）；
tmp_path 创建真实 .py 文件（gate 通过 os.path.join(wt_root, rel) 读盘）。
"""
from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.governance.commit_gates.orphan_module_gate import (  # noqa: E402
    _compute_module_path,
    _is_entry_point,
    make_orphan_module_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


def _make_gateway(tmp_path, staged_files=None, diff_fails=False, diff_raises=False):
    """构造 mock gateway：--name-only 返回相对文件列表；--show-toplevel 返回 tmp_path。"""
    gw = MagicMock()
    gw.project_root = str(tmp_path)

    if diff_raises:
        def _raise(*a, **k):
            raise RuntimeError("git not found")
        gw._run_git = MagicMock(side_effect=_raise)
        return gw

    def _run_git(cmd, cwd=None):
        if diff_fails and "--name-only" in cmd:
            return _MockResult(1, "")
        if "--name-only" in cmd:
            return _MockResult(0, "\n".join(staged_files or []))
        if "rev-parse" in cmd and "--show-toplevel" in cmd:
            return _MockResult(0, str(tmp_path))
        return _MockResult(0, "")

    gw._run_git = MagicMock(side_effect=_run_git)
    return gw


def _write_file(tmp_path, rel_path, content):
    """在 tmp_path 下创建 rel_path 文件，返回相对路径（正斜杠）。"""
    rel = rel_path.replace("\\", "/")
    full = tmp_path / rel.replace("/", os.sep)
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content, encoding="utf-8")
    return rel


class _GrepResult:
    """模拟 subprocess.run 返回值。"""

    def __init__(self, returncode=1, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _patch_grep(gateway, returncode=1, stdout="", raises=None):
    """patch gateway._run_git 的 git grep 调用。
    returncode=1 → 无匹配（孤儿）；0 → 有匹配（非孤儿）。"""
    original_side_effect = gateway._run_git.side_effect

    if raises is not None:
        def _grep_run(cmd, cwd=None):
            if len(cmd) >= 2 and cmd[0:2] == ["git", "grep"]:
                raise raises
            return original_side_effect(cmd)
        gateway._run_git.side_effect = _grep_run
        return

    def _grep_run(cmd, cwd=None):
        if len(cmd) >= 2 and cmd[0:2] == ["git", "grep"]:
            return _GrepResult(returncode=returncode, stdout=stdout)
        return original_side_effect(cmd)

    gateway._run_git.side_effect = _grep_run


@pytest.fixture(autouse=True)
def _shadow_open(monkeypatch):
    """源文件用 open(path).read() 未关闭文件句柄（ResourceWarning）。
    注入 shadow open：read() 后立即关闭真实 fd。"""
    import builtins
    _real_open = builtins.open

    class _AutoClose:
        def __init__(self, fp):
            self._fp = fp

        def read(self, *a, **k):
            try:
                return self._fp.read(*a, **k)
            finally:
                self._fp.close()

        def __enter__(self):
            return self

        def __exit__(self, *a):
            self._fp.close()

        def __getattr__(self, name):
            return getattr(self._fp, name)

    def _shadow(file, mode="r", *args, **kwargs):
        return _AutoClose(_real_open(file, mode, *args, **kwargs))

    import zephyr.governance.commit_gates.orphan_module_gate as mod
    monkeypatch.setattr(mod, "open", _shadow, raising=False)


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------
class TestGateSpecFields:
    def test_is_gate_spec(self):
        assert isinstance(make_orphan_module_gate(), GateSpec)

    def test_gate_id(self):
        assert make_orphan_module_gate().gate_id == "ORPHAN-MODULE"

    def test_priority(self):
        assert make_orphan_module_gate().priority == 86


# ---------------------------------------------------------------------------
# TestEntryPoint — _is_entry_point
# ---------------------------------------------------------------------------
class TestEntryPoint:
    def test_main_file_exempt(self):
        assert _is_entry_point("src/zephyr/cli/__main__.py", "x = 1\n")

    def test_init_file_exempt(self):
        assert _is_entry_point("src/zephyr/pkg/__init__.py", "x = 1\n")

    def test_conftest_exempt(self):
        assert _is_entry_point("tests/conftest.py", "x = 1\n")

    def test_scripts_path_exempt(self):
        assert _is_entry_point("scripts/run.py", "x = 1\n")

    def test_main_block_exempt(self):
        content = (
            'if __name__ == "__main__":\n'
            '    main()\n'
        )
        assert _is_entry_point("src/zephyr/cli/app.py", content)

    def test_regular_file_not_entry(self):
        assert not _is_entry_point("src/zephyr/trading/mod.py", "x = 1\n")


# ---------------------------------------------------------------------------
# TestModulePath — _compute_module_path
# ---------------------------------------------------------------------------
class TestModulePath:
    def test_regular_module(self):
        mp, short = _compute_module_path("src/zephyr/governance/foo.py")
        assert mp == "zephyr.governance.foo"
        assert short == "foo"

    def test_init_module(self):
        mp, short = _compute_module_path("src/zephyr/governance/pkg/__init__.py")
        assert mp == "zephyr.governance.pkg"
        assert short == "pkg"


# ---------------------------------------------------------------------------
# TestGatewayIntegration — mock gateway 流程
# ---------------------------------------------------------------------------
class TestGatewayIntegration:
    def test_orphan_module_blocked(self, tmp_path, monkeypatch):
        red = "src/zephyr/trading/orphan.py"
        _write_file(tmp_path, red, "X = 1\n")
        gw = _make_gateway(tmp_path, staged_files=[red])
        # git grep 无匹配（returncode=1）→ 孤儿
        _patch_grep(gw, returncode=1)
        passed, msg = make_orphan_module_gate().check(gw, [])
        assert not passed
        assert "ORPHAN-MODULE" in msg or "孤儿模块" in msg

    def test_imported_module_passes(self, tmp_path, monkeypatch):
        red = "src/zephyr/trading/used.py"
        _write_file(tmp_path, red, "X = 1\n")
        gw = _make_gateway(tmp_path, staged_files=[red])
        # git grep 有匹配，且匹配的是其他文件 → 非孤儿
        _patch_grep(
            gw,
            returncode=0,
            stdout="src/zephyr/trading/caller.py",
        )
        passed, msg = make_orphan_module_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_only_self_match_is_orphan(self, tmp_path, monkeypatch):
        red = "src/zephyr/trading/self_ref.py"
        _write_file(tmp_path, red, "X = 1\n")
        gw = _make_gateway(tmp_path, staged_files=[red])
        # git grep 仅匹配文件自身 → 仍为孤儿
        _patch_grep(gw, returncode=0, stdout=red)
        passed, msg = make_orphan_module_gate().check(gw, [])
        assert not passed

    def test_entry_file_exempt(self, tmp_path, monkeypatch):
        red = "src/zephyr/cli/__main__.py"
        _write_file(tmp_path, red, "X = 1\n")
        gw = _make_gateway(tmp_path, staged_files=[red])
        _patch_grep(gw, returncode=1)  # 无引用
        passed, msg = make_orphan_module_gate().check(gw, [])
        assert passed  # 入口文件豁免
        assert msg == ""

    def test_tests_dir_exempt(self, tmp_path, monkeypatch):
        red = "tests/governance/test_something.py"
        _write_file(tmp_path, red, "X = 1\n")
        gw = _make_gateway(tmp_path, staged_files=[red])
        _patch_grep(gw, returncode=1)
        passed, msg = make_orphan_module_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_git_diff_failure(self, tmp_path):
        gw = _make_gateway(tmp_path, diff_fails=True)
        passed, msg = make_orphan_module_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_git_diff_exception(self, tmp_path):
        gw = _make_gateway(tmp_path, diff_raises=True)
        passed, msg = make_orphan_module_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_grep_timeout(self, tmp_path, monkeypatch):
        red = "src/zephyr/trading/orphan.py"
        _write_file(tmp_path, red, "X = 1\n")
        gw = _make_gateway(tmp_path, staged_files=[red])
        _patch_grep(gw, raises=subprocess.TimeoutExpired(cmd=["git"], timeout=30))
        passed, msg = make_orphan_module_gate().check(gw, [])
        assert passed  # fail-open
        assert msg == ""

    def test_fail_open_on_grep_exception(self, tmp_path, monkeypatch):
        red = "src/zephyr/trading/orphan.py"
        _write_file(tmp_path, red, "X = 1\n")
        gw = _make_gateway(tmp_path, staged_files=[red])
        _patch_grep(gw, raises=RuntimeError("git not found"))
        passed, msg = make_orphan_module_gate().check(gw, [])
        assert passed  # fail-open
        assert msg == ""

    def test_fail_open_on_grep_error_returncode(self, tmp_path, monkeypatch):
        red = "src/zephyr/trading/orphan.py"
        _write_file(tmp_path, red, "X = 1\n")
        gw = _make_gateway(tmp_path, staged_files=[red])
        # git grep 返回 rc=2（错误，非 0/1）→ fail-open
        _patch_grep(gw, returncode=2)
        passed, msg = make_orphan_module_gate().check(gw, [])
        assert passed
        assert msg == ""
