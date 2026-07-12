# [A_test] module_id: SRC-TST-2229 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-vocab_hardcode_gate | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_vocab_hardcode_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_vocab_hardcode_gate.py — VOCAB-HARDCODE 门禁单测

权威依据：vocab_hardcode_gate.py（make_vocab_hardcode_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestSubprocessContract: subprocess exit-code 契约
  （exit0 放行 / exit1 阻断 / exit2 fail-open / 超时 fail-open / 异常 fail-open）
- TestGatewayIntegration: mock gateway 流程
  - tests/ 豁免
  - 无新增 .py 文件 → 放行
  - 非 .py 文件忽略
  - 检测脚本缺失 → fail-open
  - abs 文件不存在 → 过滤后放行
  - git diff 失败 → fail-open
  - git diff 异常 → fail-open
  - worktree toplevel 失败 → 回退 project_root

注意：vocab_hardcode_gate 是 thin wrapper，检测逻辑真源在
check_vocab_hardcode.py（subprocess 调用 --files --ci）。本测试 mock
subprocess.run，不调用真实脚本；用 tmp_path 创建真实文件使 os.path.isfile
通过。只检测新增文件（diff-filter=A），不触碰存量违规。

测试隔离：MagicMock 模拟 gateway._run_git + monkeypatch subprocess.run，不读/不写真实仓库。
"""
from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import zephyr.gov_enforcement.commit_gates.vocab_hardcode_gate as _vocab_mod  # noqa: E402
from zephyr.gov_enforcement.commit_gates.vocab_hardcode_gate import (  # noqa: E402
    make_vocab_hardcode_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


@dataclass
class _SubResult:
    returncode: int = 0
    stdout: str = ""
    stderr: str = ""


def _make_gateway(staged_new=None, project_root=None, toplevel=None,
                  toplevel_fails=False, diff_fails=False, diff_raises=False):
    """构造 mock gateway：--diff-filter=A --name-only 返回新增文件列表；
    git rev-parse --show-toplevel 返回 worktree root。"""
    gw = MagicMock()
    gw.project_root = project_root or str(_PROJECT_ROOT)

    if diff_raises:
        def _raise(*a, **k):
            raise RuntimeError("git not found")
        gw._run_git = _raise
        return gw

    def _run_git(cmd):
        cmd_str = " ".join(cmd)
        if diff_fails and "--diff-filter=A" in cmd_str:
            return _MockResult(1, "")
        if "--diff-filter=A" in cmd_str and "--name-only" in cmd_str:
            return _MockResult(0, "\n".join(staged_new or []))
        if "rev-parse" in cmd_str and "--show-toplevel" in cmd_str:
            if toplevel_fails:
                return _MockResult(1, "")
            return _MockResult(0, toplevel or str(gw.project_root))
        return _MockResult(0, "")

    gw._run_git = _run_git
    return gw


def _create_files(tmp_path, rels):
    """在 tmp_path 下创建真实 .py 文件（使 os.path.isfile 通过）。"""
    for rel in rels:
        fpath = tmp_path.joinpath(*rel.split("/"))
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_text("# dummy module\n", encoding="utf-8")


def _patch_script(monkeypatch, tmp_path, exists=True):
    """patch _VOCAB_SCRIPT 到 tmp_path 下的（可能不存在的）脚本。"""
    script = tmp_path / "check_vocab_hardcode.py"
    if exists:
        script.write_text("# dummy checker\n", encoding="utf-8")
    monkeypatch.setattr(_vocab_mod, "_VOCAB_SCRIPT", str(script))


def _patch_subprocess(monkeypatch, result=None, raises=None):
    """patch subprocess.run：返回固定 result 或抛指定异常。"""
    if raises is not None:
        def _raise(*a, **k):
            raise raises
        monkeypatch.setattr(subprocess, "run", _raise)
    else:
        res = result or _SubResult(0, "", "")
        monkeypatch.setattr(subprocess, "run", lambda *a, **k: res)


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------
class TestGateSpecFields:
    def test_is_gate_spec(self):
        assert isinstance(make_vocab_hardcode_gate(), GateSpec)

    def test_gate_id(self):
        assert make_vocab_hardcode_gate().gate_id == "VOCAB-HARDCODE"

    def test_priority(self):
        assert make_vocab_hardcode_gate().priority == 80


# ---------------------------------------------------------------------------
# TestSubprocessContract — exit-code 契约
# ---------------------------------------------------------------------------
class TestSubprocessContract:
    def test_exit_zero_passes(self, tmp_path, monkeypatch):
        rel = "src/zephyr/trading/new_mod.py"
        _create_files(tmp_path, [rel])
        _patch_script(monkeypatch, tmp_path)
        _patch_subprocess(monkeypatch, _SubResult(0, "", ""))
        gw = _make_gateway(staged_new=[rel], project_root=str(tmp_path),
                           toplevel=str(tmp_path))
        passed, msg = make_vocab_hardcode_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_exit_one_blocks(self, tmp_path, monkeypatch):
        rel = "src/zephyr/trading/new_mod.py"
        _create_files(tmp_path, [rel])
        _patch_script(monkeypatch, tmp_path)
        _patch_subprocess(monkeypatch, _SubResult(1, "WARN: new_mod.py hardcodes vocab\n", ""))
        gw = _make_gateway(staged_new=[rel], project_root=str(tmp_path),
                           toplevel=str(tmp_path))
        passed, msg = make_vocab_hardcode_gate().check(gw, [])
        assert not passed
        assert "词表硬编码" in msg

    def test_exit_one_default_detail_when_no_warn(self, tmp_path, monkeypatch):
        rel = "src/zephyr/trading/new_mod.py"
        _create_files(tmp_path, [rel])
        _patch_script(monkeypatch, tmp_path)
        # 无 WARN: 前缀行 → detail_str 走默认
        _patch_subprocess(monkeypatch, _SubResult(1, "some raw output\n", ""))
        gw = _make_gateway(staged_new=[rel], project_root=str(tmp_path),
                           toplevel=str(tmp_path))
        passed, msg = make_vocab_hardcode_gate().check(gw, [])
        assert not passed
        assert "词表硬编码违规（见 check_vocab_hardcode.py 输出）" in msg

    def test_exit_two_fail_open(self, tmp_path, monkeypatch):
        rel = "src/zephyr/trading/new_mod.py"
        _create_files(tmp_path, [rel])
        _patch_script(monkeypatch, tmp_path)
        _patch_subprocess(monkeypatch, _SubResult(2, "", "script error"))
        gw = _make_gateway(staged_new=[rel], project_root=str(tmp_path),
                           toplevel=str(tmp_path))
        passed, msg = make_vocab_hardcode_gate().check(gw, [])
        assert passed  # 脚本异常 fail-open
        assert msg == ""

    def test_timeout_fail_open(self, tmp_path, monkeypatch):
        rel = "src/zephyr/trading/new_mod.py"
        _create_files(tmp_path, [rel])
        _patch_script(monkeypatch, tmp_path)
        _patch_subprocess(
            monkeypatch,
            raises=subprocess.TimeoutExpired(cmd=["x"], timeout=60),
        )
        gw = _make_gateway(staged_new=[rel], project_root=str(tmp_path),
                           toplevel=str(tmp_path))
        passed, msg = make_vocab_hardcode_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_subprocess_exception_fail_open(self, tmp_path, monkeypatch):
        rel = "src/zephyr/trading/new_mod.py"
        _create_files(tmp_path, [rel])
        _patch_script(monkeypatch, tmp_path)
        _patch_subprocess(monkeypatch, raises=OSError("boom"))
        gw = _make_gateway(staged_new=[rel], project_root=str(tmp_path),
                           toplevel=str(tmp_path))
        passed, msg = make_vocab_hardcode_gate().check(gw, [])
        assert passed
        assert msg == ""


# ---------------------------------------------------------------------------
# TestGatewayIntegration — mock gateway 流程
# ---------------------------------------------------------------------------
class TestGatewayIntegration:
    def test_tests_dir_exempt(self, tmp_path, monkeypatch):
        rel = "tests/governance/test_something.py"
        _create_files(tmp_path, [rel])
        _patch_script(monkeypatch, tmp_path)
        # 即使脚本会检出违规，tests/ 豁免不应触发检测
        _patch_subprocess(monkeypatch, _SubResult(1, "WARN: x\n", ""))
        gw = _make_gateway(staged_new=[rel], project_root=str(tmp_path),
                           toplevel=str(tmp_path))
        passed, msg = make_vocab_hardcode_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_no_new_py_files_passes(self, tmp_path, monkeypatch):
        _patch_script(monkeypatch, tmp_path)
        gw = _make_gateway(staged_new=[], project_root=str(tmp_path))
        passed, msg = make_vocab_hardcode_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_non_py_file_ignored(self, tmp_path, monkeypatch):
        rel = "docs/readme.md"
        _create_files(tmp_path, [rel])
        _patch_script(monkeypatch, tmp_path)
        gw = _make_gateway(staged_new=[rel], project_root=str(tmp_path))
        passed, msg = make_vocab_hardcode_gate().check(gw, [])
        assert passed  # 非 .py 文件忽略
        assert msg == ""

    def test_script_missing_fail_open(self, tmp_path, monkeypatch):
        rel = "src/zephyr/trading/new_mod.py"
        _create_files(tmp_path, [rel])
        _patch_script(monkeypatch, tmp_path, exists=False)  # 脚本不存在
        _patch_subprocess(monkeypatch, _SubResult(1, "WARN: x\n", ""))
        gw = _make_gateway(staged_new=[rel], project_root=str(tmp_path),
                           toplevel=str(tmp_path))
        passed, msg = make_vocab_hardcode_gate().check(gw, [])
        assert passed  # 脚本缺失 fail-open
        assert msg == ""

    def test_abs_files_nonexistent_filtered(self, tmp_path, monkeypatch):
        rel = "src/zephyr/trading/ghost.py"
        # 不创建文件 → os.path.isfile False → abs_files 空 → 放行
        _patch_script(monkeypatch, tmp_path)
        _patch_subprocess(monkeypatch, _SubResult(1, "WARN: x\n", ""))
        gw = _make_gateway(staged_new=[rel], project_root=str(tmp_path),
                           toplevel=str(tmp_path))
        passed, msg = make_vocab_hardcode_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_git_diff_failure_fail_open(self, tmp_path, monkeypatch):
        _patch_script(monkeypatch, tmp_path)
        gw = _make_gateway(staged_new=["src/x.py"], project_root=str(tmp_path),
                           diff_fails=True)
        passed, msg = make_vocab_hardcode_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_git_diff_exception_fail_open(self, tmp_path, monkeypatch):
        _patch_script(monkeypatch, tmp_path)
        gw = _make_gateway(staged_new=["src/x.py"], project_root=str(tmp_path),
                           diff_raises=True)
        passed, msg = make_vocab_hardcode_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_toplevel_failure_fallback_to_project_root(self, tmp_path, monkeypatch):
        rel = "src/zephyr/trading/new_mod.py"
        _create_files(tmp_path, [rel])
        _patch_script(monkeypatch, tmp_path)
        _patch_subprocess(monkeypatch, _SubResult(0, "", ""))
        # toplevel 解析失败 → 回退 project_root，文件仍可达
        gw = _make_gateway(staged_new=[rel], project_root=str(tmp_path),
                           toplevel_fails=True)
        passed, msg = make_vocab_hardcode_gate().check(gw, [])
        assert passed
        assert msg == ""
