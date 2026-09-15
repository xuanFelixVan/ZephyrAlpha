# [A_test] module_id: MOD-GOV_file_copy_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_FILE_COPY_GATE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_file_copy_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GOV_FILE_COPY_GATE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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

测试隔离：MagicMock 模拟 gateway.run_git + monkeypatch subprocess.run，不读/不写真实仓库。
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

import zephyr.gov_enforcement.commit_gates.file_copy_gate as _fc_mod  # noqa: E402
import zephyr.gov_enforcement.commit_gates.file_copy_gate as _gate_mod_file_copy_gate  # noqa: E402
from zephyr.gov_enforcement.commit_gates.file_copy_gate import (  # noqa: E402
    _THRESHOLD,
    make_file_copy_gate,
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


def _make_gateway(staged_new=None, project_root=None, diff_fails=False, diff_raises=False):
    """构造 mock gateway：--diff-filter=A --name-only 返回新增文件列表。
    file_copy 不调用 git rev-parse，路径解析用 gateway.project_root。"""
    gw = MagicMock()
    gw.project_root = project_root or str(_PROJECT_ROOT)

    if diff_raises:

        def _raise(*a, **k):
            raise RuntimeError("git not found")

        gw.run_git = _raise
        return gw

    def _run_git(cmd):
        cmd_str = " ".join(cmd)
        if diff_fails and "--diff-filter=A" in cmd_str:
            return _MockResult(1, "")
        if "--diff-filter=A" in cmd_str and "--name-only" in cmd_str:
            return _MockResult(0, "\n".join(staged_new or []))
        return _MockResult(0, "")

    gw.run_git = _run_git
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

        monkeypatch.setattr(_gate_mod_file_copy_gate, "run_checker_script", _raise)
    else:
        res = result or _SubResult(0, "", "")
        monkeypatch.setattr(_gate_mod_file_copy_gate, "run_checker_script", lambda *a, **k: res)


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
        gw = _make_gateway(staged_new=["src/x.py"], project_root=str(tmp_path), diff_fails=True)
        passed, msg = make_file_copy_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_git_diff_exception_fail_open(self, tmp_path, monkeypatch):
        _patch_script(monkeypatch, tmp_path)
        gw = _make_gateway(staged_new=["src/x.py"], project_root=str(tmp_path), diff_raises=True)
        passed, msg = make_file_copy_gate().check(gw, [])
        assert passed
        assert msg == ""


class TestCrossTreeTwinExclusion:
    """FILE-COPY 跨树自比较治本回归钉（st-commitspeed-20260916，-0016 死信实证）：
    队列落地的新 .py 位于 serializer worktree，主区同名孪生（AI 施工原文）绝对
    路径不同——排除集必须按仓锚后缀（src/zephyr|scripts 后相对段）等价，否则
    新文件与自己 100% 相似误报。"""

    def test_worktree_twin_not_flagged(self, tmp_path):
        import subprocess
        import sys as _sys

        repo_root = Path(__file__).resolve().parents[3]
        src_twin_target = repo_root / "src" / "zephyr" / "gov_enforcement" / "rule_bridge" / "commit_preflight.py"
        if not src_twin_target.exists():
            pytest.skip("主区原文不在（HEAD 漂移），跳过孪生复刻")
        # 构造 worktree 孪生：同锚后缀不同绝对路径（复刻 serializer worktree 形态）
        wt_file = tmp_path / "commit_queue" / "worktree" / "src" / "zephyr" / "gov_enforcement" / "rule_bridge" / "commit_preflight.py"
        wt_file.parent.mkdir(parents=True)
        wt_file.write_bytes(src_twin_target.read_bytes())
        r = subprocess.run(
            [
                _sys.executable,
                str(repo_root / "scripts" / "governance" / "d5_architecture" / "checkers" / "check_code_duplication.py"),
                "--files",
                str(wt_file),
                "--ast",
                "--threshold",
                "0.7",
            ],
            capture_output=True,
            text=True,
            timeout=180,
        )
        assert r.returncode == 0, f"跨树孪生不得误报（rc={r.returncode}）: {r.stdout[-200:]}"

    def test_real_copy_still_flagged(self, tmp_path):
        """真克隆（不同路径名不同内容同构）仍须拦截——修复不放松检测语义。"""
        import subprocess
        import sys as _sys

        repo_root = Path(__file__).resolve().parents[3]
        # 用一个确有同形孪生的场景：直接把 belt daemon 测试外克隆为不同锚后缀同 basename 不同内容变体——
        # 简化验证：拿两个内容 100% 相同但锚后缀不同的文件（tmp 伪造 repo 结构）
        src_file = repo_root / "src" / "zephyr" / "gov_enforcement" / "rule_bridge" / "commit_preflight.py"
        if not src_file.exists():
            pytest.skip("主区原文不在，跳过")
        fake_repo = tmp_path / "scripts"
        fake_repo.mkdir()
        # 同名不同目录（锚后缀不同）+内容全同 = 真克隆形态
        fake_file = fake_repo / "commit_preflight.py"
        fake_file.write_bytes(src_file.read_bytes())
        # new 文件指向 fake（锚后缀=scripts/commit_preflight.py），existing=主区原文
        # 两者锚后缀不同 → 不在排除集 → 相似度 100% → 须 rc=1
        r = subprocess.run(
            [
                _sys.executable,
                str(repo_root / "scripts" / "governance" / "d5_architecture" / "checkers" / "check_code_duplication.py"),
                "--files",
                str(fake_file),
                "--ast",
                "--threshold",
                "0.7",
            ],
            capture_output=True,
            text=True,
            timeout=180,
        )
        assert r.returncode == 1, "真克隆（锚后缀不同的全同内容）仍须拦截"
