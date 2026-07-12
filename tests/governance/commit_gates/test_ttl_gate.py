# [TTL] task_bound
"""test_ttl_gate.py — ttl 字段校验门禁单元测试。

测试组：
- TestGateSpecAttributes: GateSpec 属性（gate_id / priority）
- TestCheckEmptyFiles: 空文件列表直接通过
- TestCheckDeletionCommit: 全 deletion（文件不存在）直接通过
- TestCheckCheckerNotFound: checker 缺失 fail-closed 阻断
- TestCheckPass: checker exit 0 通过
- TestCheckViolation: checker exit 1 阻断 + detail 透传
- TestCheckSubprocessException: subprocess 异常（timeout/OSError）fail-closed 阻断
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# 确保能 import zephyr.*（pytest 自动加 src/ 到 path，但独立运行也兼容）
_SRC = Path(__file__).parent.parent.parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from zephyr.gov_enforcement.commit_gates.ttl_gate import make_ttl_gate  # noqa: E402
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


class _MockGateway:
    """Mock gateway——ttl gate 只用 project_root 属性。"""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root


def _make_checker_stub(
    repo_dir: Path, exit_code: int = 0, stderr_msg: str = ""
) -> Path:
    """在 repo_dir/scripts/governance/d3_metadata/ 创建 check_frontmatter_metadata.py stub。

    stub 行为由 exit_code + stderr_msg 参数控制，模拟真 checker 的 exit 0/1/2。
    """
    checker = (
        repo_dir
        / "scripts"
        / "governance"
        / "d3_metadata"
        / "check_frontmatter_metadata.py"
    )
    checker.parent.mkdir(parents=True, exist_ok=True)
    lines = ["#!/usr/bin/env python", "import sys"]
    if stderr_msg:
        lines.append(f"sys.stderr.write({stderr_msg!r})")
    lines.append(f"sys.exit({exit_code})")
    checker.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return checker


def _make_target_file(repo_dir: Path, rel: str = "foo.py") -> Path:
    """在 repo_dir 下创建一个目标文件（ttl gate 跳过不存在的文件）。"""
    f = repo_dir / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text("", encoding="utf-8")
    return f


class TestGateSpecAttributes:
    """GateSpec 属性——_commit_auto 通过 gate_registry.get("TTL-METADATA") 复用本 spec。"""

    def test_gate_id(self):
        spec = make_ttl_gate()
        assert spec.gate_id == "TTL-METADATA"

    def test_priority_is_32(self):
        spec = make_ttl_gate()
        assert spec.priority == 32

    def test_returns_gate_spec_instance(self):
        spec = make_ttl_gate()
        assert isinstance(spec, GateSpec)


class TestCheckEmptyFiles:
    """空文件列表——无文件可校验，直接通过。"""

    def test_empty_files_returns_true(self, tmp_path):
        gw = _MockGateway(tmp_path)
        spec = make_ttl_gate()
        passed, detail = spec.check(gw, [])
        assert passed is True
        assert "no files" in detail


class TestCheckDeletionCommit:
    """deletion commit——文件已删除（不存在），跳过校验（无法判定 ttl）。"""

    def test_all_nonexistent_files_returns_true(self, tmp_path):
        gw = _MockGateway(tmp_path)
        spec = make_ttl_gate()
        passed, detail = spec.check(gw, [str(tmp_path / "deleted.py")])
        assert passed is True
        assert "no files" in detail

    def test_mixed_existing_and_nonexistent(self, tmp_path):
        """部分存在部分不存在——只校验存在的。"""
        gw = _MockGateway(tmp_path)
        _make_checker_stub(tmp_path, exit_code=0)
        existing = _make_target_file(tmp_path, "foo.py")
        nonexistent = str(tmp_path / "deleted.py")
        spec = make_ttl_gate()
        passed, detail = spec.check(gw, [str(existing), nonexistent])
        assert passed is True  # 存在的文件 checker exit 0


class TestCheckCheckerNotFound:
    """checker 缺失——fail-closed 阻断（环境异常必须阻断）。"""

    def test_checker_missing_returns_false(self, tmp_path):
        gw = _MockGateway(tmp_path)
        _make_target_file(tmp_path, "foo.py")  # 文件存在但不重要
        spec = make_ttl_gate()
        passed, detail = spec.check(gw, [str(tmp_path / "foo.py")])
        assert passed is False
        assert "not found" in detail
        assert "check_frontmatter_metadata.py" in detail


class TestCheckPass:
    """checker exit 0——通过。"""

    def test_checker_exit_0_returns_true(self, tmp_path):
        gw = _MockGateway(tmp_path)
        _make_checker_stub(tmp_path, exit_code=0)
        _make_target_file(tmp_path, "foo.py")
        spec = make_ttl_gate()
        passed, detail = spec.check(gw, [str(tmp_path / "foo.py")])
        assert passed is True
        assert "passed" in detail


class TestCheckViolation:
    """checker exit 1——有违规，阻断 + detail 透传。"""

    def test_checker_exit_1_returns_false_with_detail(self, tmp_path):
        gw = _MockGateway(tmp_path)
        _make_checker_stub(
            tmp_path, exit_code=1, stderr_msg="ttl missing in foo.py"
        )
        _make_target_file(tmp_path, "foo.py")
        spec = make_ttl_gate()
        passed, detail = spec.check(gw, [str(tmp_path / "foo.py")])
        assert passed is False
        assert "ttl missing" in detail

    def test_checker_exit_1_empty_stderr_falls_back_to_stdout(self, tmp_path):
        """stderr 空时 fallback 到 stdout（gate L131-132 逻辑）。"""
        gw = _MockGateway(tmp_path)
        _make_checker_stub(tmp_path, exit_code=1, stderr_msg="")
        _make_target_file(tmp_path, "foo.py")
        spec = make_ttl_gate()
        passed, detail = spec.check(gw, [str(tmp_path / "foo.py")])
        assert passed is False
        assert "unknown detail" in detail


class TestCheckSubprocessException:
    """subprocess 异常（timeout / OSError）——fail-closed 阻断。"""

    def test_timeout_returns_false(self, tmp_path, monkeypatch):
        gw = _MockGateway(tmp_path)
        _make_checker_stub(tmp_path, exit_code=0)
        _make_target_file(tmp_path, "foo.py")

        def _raise_timeout(*args, **kwargs):
            raise subprocess.TimeoutExpired(cmd="mock", timeout=60)

        monkeypatch.setattr(subprocess, "run", _raise_timeout)
        spec = make_ttl_gate()
        passed, detail = spec.check(gw, [str(tmp_path / "foo.py")])
        assert passed is False
        assert "execution failed" in detail
        assert "timed out" in detail

    def test_oserror_returns_false(self, tmp_path, monkeypatch):
        gw = _MockGateway(tmp_path)
        _make_checker_stub(tmp_path, exit_code=0)
        _make_target_file(tmp_path, "foo.py")

        def _raise_oserror(*args, **kwargs):
            raise OSError("mock permission denied")

        monkeypatch.setattr(subprocess, "run", _raise_oserror)
        spec = make_ttl_gate()
        passed, detail = spec.check(gw, [str(tmp_path / "foo.py")])
        assert passed is False
        assert "execution failed" in detail
        assert "permission denied" in detail
