# [BLUEPRINT] MOD-GOV_COMMIT_GATES | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [TTL] task_bound
"""test_encoding_gate.py — 编码安全校验门禁单元测试。

测试组：
- TestGateSpecAttributes: GateSpec 属性（gate_id / priority）
- TestCheckEmptyFiles: 空文件列表直接通过
- TestCheckDeletionCommit: 全 deletion（文件不存在）直接通过
- TestCheckSuffixFilter: 后缀过滤——非相关后缀直接通过
- TestCheckCheckerNotFound: checker 缺失 fail-open 放行
- TestCheckPass: checker exit 0 通过
- TestCheckViolation: checker exit 1 阻断 + detail 透传
- TestCheckScriptError: checker exit 2 fail-open 放行
- TestCheckSubprocessException: subprocess 异常（timeout/OSError）fail-open 放行
- TestCheckMultipleFiles: 多文件中部分违规——聚合 detail
- TestCheckBatchInvocation: 批量调用结构——单次调用/64 分块/块违规阻断（2026-09-11 治本）
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# 确保能 import zephyr.*（pytest 自动加 src/ 到 path，但独立运行也兼容）
_SRC = Path(__file__).parent.parent.parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from zephyr.gov_enforcement.commit_gates.encoding_gate import make_encoding_gate  # noqa: E402
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


class _MockGateway:
    """Mock gateway——encoding gate 只用 project_root 属性。"""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root


def _make_checker_stub(repo_dir: Path, exit_code: int = 0, stdout_msg: str = "", stderr_msg: str = "") -> Path:
    """在 repo_dir/scripts/governance/d7_code/ 创建 check_encoding.py stub。

    stub 行为由 exit_code + stdout_msg + stderr_msg 参数控制，模拟真 checker
    的 exit 0/1/2（与 check_encoding.py 一致：0=通过，1=有违规，2=脚本异常）。
    """
    checker = repo_dir / "scripts" / "governance" / "d7_code" / "check_encoding.py"
    checker.parent.mkdir(parents=True, exist_ok=True)
    lines = ["#!/usr/bin/env python", "import sys"]
    if stdout_msg:
        lines.append(f"sys.stdout.write({stdout_msg!r})")
    if stderr_msg:
        lines.append(f"sys.stderr.write({stderr_msg!r})")
    lines.append(f"sys.exit({exit_code})")
    checker.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return checker


def _make_target_file(repo_dir: Path, rel: str = "foo.py") -> Path:
    """在 repo_dir 下创建一个目标文件（encoding gate 跳过不存在的文件）。"""
    f = repo_dir / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text("", encoding="utf-8")
    return f


class TestGateSpecAttributes:
    """GateSpec 属性——_commit_auto 通过 gate_registry.get("ENCODING-SAFETY") 复用本 spec。"""

    def test_gate_id(self):
        spec = make_encoding_gate()
        assert spec.gate_id == "ENCODING-SAFETY"

    def test_priority_is_42(self):
        spec = make_encoding_gate()
        assert spec.priority == 42

    def test_returns_gate_spec_instance(self):
        spec = make_encoding_gate()
        assert isinstance(spec, GateSpec)


class TestCheckEmptyFiles:
    """空文件列表——无文件可校验，直接通过。"""

    def test_empty_files_returns_true(self, tmp_path):
        gw = _MockGateway(tmp_path)
        spec = make_encoding_gate()
        passed, detail = spec.check(gw, [])
        assert passed is True
        assert "no files" in detail


class TestCheckDeletionCommit:
    """deletion commit——文件已删除（不存在），跳过校验。"""

    def test_all_nonexistent_files_returns_true(self, tmp_path):
        gw = _MockGateway(tmp_path)
        spec = make_encoding_gate()
        passed, detail = spec.check(gw, [str(tmp_path / "deleted.py")])
        assert passed is True
        assert "no files" in detail


class TestCheckSuffixFilter:
    """后缀过滤——非 .py/.md/.yaml/.yml/.json/.toml/.ps1 后缀直接通过。"""

    def test_non_checked_suffix_returns_true(self, tmp_path):
        """二进制文件（.png）应被跳过——直接通过。"""
        gw = _MockGateway(tmp_path)
        _make_target_file(tmp_path, "image.png")
        spec = make_encoding_gate()
        passed, detail = spec.check(gw, [str(tmp_path / "image.png")])
        assert passed is True
        assert "no files" in detail  # 过滤后无相关后缀文件

    def test_mixed_suffixes_only_checks_relevant(self, tmp_path):
        """混合后缀——只校验相关后缀文件（.py 通过，.png 跳过）。"""
        gw = _MockGateway(tmp_path)
        _make_checker_stub(tmp_path, exit_code=0)
        _make_target_file(tmp_path, "foo.py")
        _make_target_file(tmp_path, "image.png")
        spec = make_encoding_gate()
        passed, detail = spec.check(gw, [str(tmp_path / "foo.py"), str(tmp_path / "image.png")])
        assert passed is True
        assert "1 file" in detail  # 只校验了 1 个文件

    def test_ps1_suffix_is_checked(self, tmp_path):
        """.ps1 后缀必须校验（这是 F-05 治本的核心场景）。"""
        gw = _MockGateway(tmp_path)
        _make_checker_stub(tmp_path, exit_code=0)
        _make_target_file(tmp_path, "backup.ps1")
        spec = make_encoding_gate()
        passed, detail = spec.check(gw, [str(tmp_path / "backup.ps1")])
        assert passed is True
        assert "1 file" in detail


class TestCheckCheckerNotFound:
    """checker 缺失——fail-open 放行（环境异常非违规，与 pure_shim_gate 等一致）。"""

    def test_checker_missing_returns_true(self, tmp_path):
        gw = _MockGateway(tmp_path)
        _make_target_file(tmp_path, "foo.py")  # 文件存在
        spec = make_encoding_gate()
        passed, detail = spec.check(gw, [str(tmp_path / "foo.py")])
        assert passed is True
        assert "not found" in detail
        assert "check_encoding.py" in detail


class TestCheckPass:
    """checker exit 0——通过。"""

    def test_checker_exit_0_returns_true(self, tmp_path):
        gw = _MockGateway(tmp_path)
        _make_checker_stub(tmp_path, exit_code=0)
        _make_target_file(tmp_path, "foo.py")
        spec = make_encoding_gate()
        passed, detail = spec.check(gw, [str(tmp_path / "foo.py")])
        assert passed is True
        assert "passed" in detail


class TestCheckViolation:
    """checker exit 1——有违规，阻断 + detail 透传。"""

    def test_checker_exit_1_returns_false_with_detail(self, tmp_path):
        """违规 detail 在 stdout（check_encoding.py 输出 findings 到 stdout）。"""
        gw = _MockGateway(tmp_path)
        _make_checker_stub(tmp_path, exit_code=1, stdout_msg="non-ASCII bytes in foo.ps1")
        _make_target_file(tmp_path, "foo.ps1")
        spec = make_encoding_gate()
        passed, detail = spec.check(gw, [str(tmp_path / "foo.ps1")])
        assert passed is False
        assert "non-ASCII bytes" in detail

    def test_checker_exit_1_empty_stdout_falls_back_to_stderr(self, tmp_path):
        """stdout 空时 fallback 到 stderr。"""
        gw = _MockGateway(tmp_path)
        _make_checker_stub(tmp_path, exit_code=1, stdout_msg="", stderr_msg="mojibake detected")
        _make_target_file(tmp_path, "foo.py")
        spec = make_encoding_gate()
        passed, detail = spec.check(gw, [str(tmp_path / "foo.py")])
        assert passed is False
        assert "mojibake detected" in detail


class TestCheckScriptError:
    """checker exit 2——脚本异常，fail-open 放行（与 pure_shim_gate 等一致）。"""

    def test_checker_exit_2_returns_true_with_stderr(self, tmp_path):
        gw = _MockGateway(tmp_path)
        _make_checker_stub(tmp_path, exit_code=2, stderr_msg="Traceback: FileNotFoundError")
        _make_target_file(tmp_path, "foo.py")
        spec = make_encoding_gate()
        passed, detail = spec.check(gw, [str(tmp_path / "foo.py")])
        assert passed is True
        assert "error" in detail.lower() or "skip" in detail.lower()
        assert "Traceback" in detail


class TestCheckSubprocessException:
    """subprocess 异常（timeout / OSError）——fail-open 放行（与 pure_shim_gate 等一致）。

    注意（2026-09-11 批量化治本）：gate 经 run_checker_script 优先走 checker_supervisor
    持久 worker（不经过 subprocess.run，patch 落空）——测试 MUST 先
    setenv ZEPHYR_CHECKER_SUPERVISOR=0 关闭 supervisor 走直 spawn 回退路径，
    才能模拟底层 spawn 失败（env 逐调用判定，checker_supervisor.py）。
    """

    def test_timeout_returns_true(self, tmp_path, monkeypatch):
        gw = _MockGateway(tmp_path)
        _make_checker_stub(tmp_path, exit_code=0)
        _make_target_file(tmp_path, "foo.py")
        monkeypatch.setenv("ZEPHYR_CHECKER_SUPERVISOR", "0")

        def _raise_timeout(*args, **kwargs):
            raise subprocess.TimeoutExpired(cmd="mock", timeout=30)

        monkeypatch.setattr(subprocess, "run", _raise_timeout)
        spec = make_encoding_gate()
        passed, detail = spec.check(gw, [str(tmp_path / "foo.py")])
        assert passed is True
        assert "execution" in detail.lower() or "skip" in detail.lower()
        assert "timed out" in detail.lower() or "timeout" in detail.lower()

    def test_oserror_returns_true(self, tmp_path, monkeypatch):
        gw = _MockGateway(tmp_path)
        _make_checker_stub(tmp_path, exit_code=0)
        _make_target_file(tmp_path, "foo.py")
        monkeypatch.setenv("ZEPHYR_CHECKER_SUPERVISOR", "0")

        def _raise_oserror(*args, **kwargs):
            raise OSError("mock permission denied")

        monkeypatch.setattr(subprocess, "run", _raise_oserror)
        spec = make_encoding_gate()
        passed, detail = spec.check(gw, [str(tmp_path / "foo.py")])
        assert passed is True
        assert "execution" in detail.lower() or "skip" in detail.lower()
        assert "permission denied" in detail


class TestCheckMultipleFiles:
    """多文件——批量单次 subprocess 调用（2026-09-11 治本：原逐文件 spawn），违规聚合 detail。"""

    def test_multiple_files_all_pass(self, tmp_path):
        """多文件全部通过——detail 含文件数。"""
        gw = _MockGateway(tmp_path)
        _make_checker_stub(tmp_path, exit_code=0)
        _make_target_file(tmp_path, "foo.py")
        _make_target_file(tmp_path, "bar.md")
        spec = make_encoding_gate()
        passed, detail = spec.check(gw, [str(tmp_path / "foo.py"), str(tmp_path / "bar.md")])
        assert passed is True
        assert "2 file" in detail

    def test_multiple_files_partial_violation(self, tmp_path):
        """多文件部分违规——整块 exit 1，detail 透传（批量后 stub 对整块返回同码）。"""
        gw = _MockGateway(tmp_path)
        # 同一 stub 对整块返回相同 exit code——模拟 foo.py 违规
        _make_checker_stub(tmp_path, exit_code=1, stdout_msg="non-ASCII in foo.py")
        _make_target_file(tmp_path, "foo.py")
        _make_target_file(tmp_path, "bar.py")
        spec = make_encoding_gate()
        passed, detail = spec.check(gw, [str(tmp_path / "foo.py"), str(tmp_path / "bar.py")])
        assert passed is False
        assert "non-ASCII in foo.py" in detail


class TestCheckBatchInvocation:
    """批量调用结构（2026-09-11 治本验证）——多文件单次调用 + 64 文件分块。

    通过 monkeypatch encoding_gate.run_checker_script 记录调用（不真跑 checker），
    验证批量化结构本身：N 文件 ≤64 → 恰 1 次调用且参数含全部文件；
    N 文件 >64 → 恰 ceil(N/64) 次调用（Windows 命令行长度安全）。
    """

    def _install_recorder(self, monkeypatch, returncode=0, stdout=b""):
        import zephyr.gov_enforcement.commit_gates.encoding_gate as enc_mod

        calls: list[list[str]] = []

        def _fake_run(script_path, args, *, cwd, timeout, text, env=None):
            calls.append(list(args))
            return subprocess.CompletedProcess(
                args=[str(script_path), *args], returncode=returncode, stdout=stdout, stderr=b""
            )

        monkeypatch.setattr(enc_mod, "run_checker_script", _fake_run)
        return calls

    def test_le_64_files_single_invocation(self, tmp_path, monkeypatch):
        """3 文件 → 恰 1 次调用，--file 后跟全部 3 个文件。"""
        _make_checker_stub(tmp_path, exit_code=0)  # stub 只需存在（run_checker_script 被 fake）
        calls = self._install_recorder(monkeypatch)
        files = []
        for i in range(3):
            rel = f"src/f{i}.py"
            _make_target_file(tmp_path, rel)
            files.append(str(tmp_path / rel))
        spec = make_encoding_gate()
        passed, detail = spec.check(_MockGateway(tmp_path), files)
        assert passed is True
        assert len(calls) == 1
        assert calls[0][0] == "--file"
        assert len(calls[0]) == 4  # --file + 3 文件

    def test_gt_64_files_chunked_invocation(self, tmp_path, monkeypatch):
        """70 文件 → 恰 2 次调用（64+6 分块，Windows CreateProcess 命令行 32767 硬限防护）。"""
        _make_checker_stub(tmp_path, exit_code=0)  # stub 只需存在（run_checker_script 被 fake）
        calls = self._install_recorder(monkeypatch)
        files = []
        for i in range(70):
            rel = f"src/f{i:03d}.py"
            _make_target_file(tmp_path, rel)
            files.append(str(tmp_path / rel))
        spec = make_encoding_gate()
        passed, detail = spec.check(_MockGateway(tmp_path), files)
        assert passed is True
        assert len(calls) == 2
        assert len(calls[0]) == 65  # --file + 64 文件
        assert len(calls[1]) == 7  # --file + 6 文件
        assert "70 file" in detail

    def test_chunk_violation_blocks(self, tmp_path, monkeypatch):
        """某块 exit 1 → 阻断且 detail 透传 stdout（fail-closed 语义保持）。"""
        _make_checker_stub(tmp_path, exit_code=0)  # stub 只需存在（run_checker_script 被 fake）
        calls = self._install_recorder(monkeypatch, returncode=1, stdout=b"INJ-007 FAIL: BOM")
        _make_target_file(tmp_path, "foo.py")
        spec = make_encoding_gate()
        passed, detail = spec.check(_MockGateway(tmp_path), [str(tmp_path / "foo.py")])
        assert passed is False
        assert "INJ-007 FAIL: BOM" in detail
