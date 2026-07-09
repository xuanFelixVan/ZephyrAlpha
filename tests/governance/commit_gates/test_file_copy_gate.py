# [A_test] module_id: SRC-TST-2209 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-file_copy_gate | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_file_copy_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_file_copy_gate.py — FILE-COPY 门禁单测

权威依据：file_copy_gate.py（make_file_copy_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec) / _THRESHOLD
- TestSubprocessContract: subprocess exit-code 契约
  （exit0 放行 / exit1 阻断 / exit1 默认 detail / exit2 fail-open / 超时 fail-open / 异常 fail-open）
- TestGatewayIntegration: mock gateway 流程
  - tests/ 豁免
  - 无新增 .py 文件 → 放行
  - 非 .py 文件忽略
  - 检测脚本缺失 → fail-open
  - abs 文件不存在 → 过滤后放行
  - git diff 失败 → fail-open
  - git diff 异常 → fail-open

注意：file_copy_gate 是 thin wrapper，检测逻辑真源在
check_code_duplication.py（subprocess 调用 --files --ast --threshold 0.7）。
本测试 mock subprocess.run，不调用真实脚本；用 tmp_path 创建真实文件使
os.path.isfile 通过。只检测新增文件（diff-filter=A）。路径解析对标
gateway.project_root（主仓库根，非 worktree root）。

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

import zephyr.governance.commit_gates.file_copy_gate as _fc_mod  # noqa: E402
from zephyr.governance.commit_gates.file_copy_gate import (  # noqa: E402
    _THRESHOLD,
    make_file_copy_gate,
)
from zephyr.governance.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


@dataclass
class _SubResult:
    returncode: int = 0
    stdout: str = ""
    stderr: str = ""


def _make_gateway(staged_new=None, project_root=None, diff_fails=False, diff_raises=False):
    """构造 mock gateway：--diff-filter=A --name-only 返回新增文件列表。
    file_copy 不调用 git rev-parse，路径解析用 gateway.project_root。"""
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
    """patch _DUP_SCRIPT 到 tmp_path 下的（可能不存在的）脚本。"""
    script = tmp_path / "check_code_duplication.py"
    if exists:
        script.write_text("# dummy checker\n", encoding="utf-8")
    monkeypatch.setattr(_fc_mod, "_DUP_SCRIPT", str(script))


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
        assert isinstance(make_file_copy_gate(), GateSpec)

    def test_gate_id(self):
        assert make_file_copy_gate().gate_id == "FILE-COPY"

    def test_priority(self):
        assert make_file_copy_gate().priority == 85

    def test_threshold_value(self):
        assert _THRESHOLD == 0.7


# ---------------------------------------------------------------------------
# TestSubprocessContract — exit-code 契约
# ---------------------------------------------------------------------------
class TestSubprocessContract:
    def test_exit_zero_passes(self, tmp_path, monkeypatch):
        rel = "src/zephyr/trading/new_mod.py"
        _create_files(tmp_path, [rel])
        _patch_script(monkeypatch, tmp_path)
        _patch_subprocess(monkeypatch, _SubResult(0, "", ""))
        gw = _make_gateway(staged_new=[rel], project_root=str(tmp_path))
        passed, msg = make_file_copy_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_exit_one_blocks_with_detail(self, tmp_path, monkeypatch):
        rel = "src/zephyr/trading/new_mod.py"
        _create_files(tmp_path, [rel])
        _patch_script(monkeypatch, tmp_path)
        _patch_subprocess(monkeypatch, _SubResult(1, "dup new_mod.py ~ old_mod.py 85%\n", ""))
        gw = _make_gateway(staged_new=[rel], project_root=str(tmp_path))
        passed, msg = make_file_copy_gate().check(gw, [])
        assert not passed
        assert "AST 相似度>70%" in msg
        assert "dup new_mod.py ~ old_mod.py 85%" in msg

    def test_exit_one_default_detail_when_filtered(self, tmp_path, monkeypatch):
        rel = "src/zephyr/trading/new_mod.py"
        _create_files(tmp_path, [rel])
        _patch_script(monkeypatch, tmp_path)
        # 全部行被 "FILE COPY"/"新文件"/"---" 前缀过滤 → detail_str 走默认
        _patch_subprocess(monkeypatch, _SubResult(1, "FILE COPY detected\n新文件: x\n---\n", ""))
        gw = _make_gateway(staged_new=[rel], project_root=str(tmp_path))
        passed, msg = make_file_copy_gate().check(gw, [])
        assert not passed
        assert "文件复制检测违规（见 check_code_duplication.py 输出）" in msg

    def test_exit_two_fail_open(self, tmp_path, monkeypatch):
        rel = "src/zephyr/trading/new_mod.py"
        _create_files(tmp_path, [rel])
        _patch_script(monkeypatch, tmp_path)
        _patch_subprocess(monkeypatch, _SubResult(2, "", "script error"))
        gw = _make_gateway(staged_new=[rel], project_root=str(tmp_path))
        passed, msg = make_file_copy_gate().check(gw, [])
        assert passed  # 脚本异常 fail-open
        assert msg == ""

    def test_timeout_fail_open(self, tmp_path, monkeypatch):
        rel = "src/zephyr/trading/new_mod.py"
        _create_files(tmp_path, [rel])
        _patch_script(monkeypatch, tmp_path)
        _patch_subprocess(
            monkeypatch,
            raises=subprocess.TimeoutExpired(cmd=["x"], timeout=120),
        )
        gw = _make_gateway(staged_new=[rel], project_root=str(tmp_path))
        passed, msg = make_file_copy_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_subprocess_exception_fail_open(self, tmp_path, monkeypatch):
        rel = "src/zephyr/trading/new_mod.py"
        _create_files(tmp_path, [rel])
        _patch_script(monkeypatch, tmp_path)
        _patch_subprocess(monkeypatch, raises=OSError("boom"))
        gw = _make_gateway(staged_new=[rel], project_root=str(tmp_path))
        passed, msg = make_file_copy_gate().check(gw, [])
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
        _patch_subprocess(monkeypatch, _SubResult(1, "dup x\n", ""))
        gw = _make_gateway(staged_new=[rel], project_root=str(tmp_path))
        passed, msg = make_file_copy_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_no_new_py_files_passes(self, tmp_path, monkeypatch):
        _patch_script(monkeypatch, tmp_path)
        gw = _make_gateway(staged_new=[], project_root=str(tmp_path))
        passed, msg = make_file_copy_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_non_py_file_ignored(self, tmp_path, monkeypatch):
        rel = "docs/readme.md"
        _create_files(tmp_path, [rel])
        _patch_script(monkeypatch, tmp_path)
        gw = _make_gateway(staged_new=[rel], project_root=str(tmp_path))
        passed, msg = make_file_copy_gate().check(gw, [])
        assert passed  # 非 .py 文件忽略
        assert msg == ""

    def test_script_missing_fail_open(self, tmp_path, monkeypatch):
        rel = "src/zephyr/trading/new_mod.py"
        _create_files(tmp_path, [rel])
        _patch_script(monkeypatch, tmp_path, exists=False)  # 脚本不存在
        _patch_subprocess(monkeypatch, _SubResult(1, "dup x\n", ""))
        gw = _make_gateway(staged_new=[rel], project_root=str(tmp_path))
        passed, msg = make_file_copy_gate().check(gw, [])
        assert passed  # 脚本缺失 fail-open
        assert msg == ""

    def test_abs_files_nonexistent_filtered(self, tmp_path, monkeypatch):
        rel = "src/zephyr/trading/ghost.py"
        # 不创建文件 → os.path.isfile False → abs_files 空 → 放行
        _patch_script(monkeypatch, tmp_path)
        _patch_subprocess(monkeypatch, _SubResult(1, "dup x\n", ""))
        gw = _make_gateway(staged_new=[rel], project_root=str(tmp_path))
        passed, msg = make_file_copy_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_git_diff_failure_fail_open(self, tmp_path, monkeypatch):
        _patch_script(monkeypatch, tmp_path)
        gw = _make_gateway(staged_new=["src/x.py"], project_root=str(tmp_path),
                           diff_fails=True)
        passed, msg = make_file_copy_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_git_diff_exception_fail_open(self, tmp_path, monkeypatch):
        _patch_script(monkeypatch, tmp_path)
        gw = _make_gateway(staged_new=["src/x.py"], project_root=str(tmp_path),
                           diff_raises=True)
        passed, msg = make_file_copy_gate().check(gw, [])
        assert passed
        assert msg == ""
