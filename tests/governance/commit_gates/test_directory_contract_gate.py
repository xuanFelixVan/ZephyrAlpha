# [TTL] task_bound
"""test_directory_contract_gate.py — DCR-001~007 等效校验门禁单元测试。

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

from zephyr.gov_enforcement.commit_gates.directory_contract_gate import (  # noqa: E402
    make_directory_contract_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402

# ── check_directory_contract.py 纯函数加载（TestCheckDeprecatedDirectory 用） ──
# check_directory_contract.py 在 scripts/ 下（非包模块），用 importlib 从文件路径加载。
# 模块自身有 bootstrap（L54-57）把 _shared 所在目录加到 sys.path，exec_module 时自动执行。
import importlib.util  # noqa: E402

_SCRIPT_DIR = Path(__file__).resolve().parent.parent.parent.parent / "scripts" / "governance" / "d1_structure"
_spec = importlib.util.spec_from_file_location(
    "_check_directory_contract_under_test",
    _SCRIPT_DIR / "check_directory_contract.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
check_deprecated_directory = _mod.check_deprecated_directory
scan_files = _mod.scan_files


class _MockGateway:
    """Mock gateway——DCR gate 只用 project_root 属性。"""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root


def _make_checker_stub(
    repo_dir: Path, exit_code: int = 0, stderr_msg: str = ""
) -> Path:
    """在 repo_dir/scripts/governance/d1_structure/ 创建 check_directory_contract.py stub。

    stub 行为由 exit_code + stderr_msg 参数控制，模拟真 checker 的 exit 0/1/2。
    """
    checker = (
        repo_dir
        / "scripts"
        / "governance"
        / "d1_structure"
        / "check_directory_contract.py"
    )
    checker.parent.mkdir(parents=True, exist_ok=True)
    lines = ["#!/usr/bin/env python", "import sys"]
    if stderr_msg:
        lines.append(f"sys.stderr.write({stderr_msg!r})")
    lines.append(f"sys.exit({exit_code})")
    checker.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return checker


def _make_target_file(repo_dir: Path, rel: str = "foo.py") -> Path:
    """在 repo_dir 下创建一个目标文件（DCR gate 跳过不存在的文件）。"""
    f = repo_dir / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text("", encoding="utf-8")
    return f


class TestGateSpecAttributes:
    """GateSpec 属性——_commit_auto 通过 gate_registry.get("DIRECTORY-CONTRACT") 复用本 spec。"""

    def test_gate_id(self):
        spec = make_directory_contract_gate()
        assert spec.gate_id == "DIRECTORY-CONTRACT"

    def test_priority_is_30(self):
        spec = make_directory_contract_gate()
        assert spec.priority == 30

    def test_returns_gate_spec_instance(self):
        spec = make_directory_contract_gate()
        assert isinstance(spec, GateSpec)


class TestCheckEmptyFiles:
    """空文件列表——无文件可校验，直接通过。"""

    def test_empty_files_returns_true(self, tmp_path):
        gw = _MockGateway(tmp_path)
        spec = make_directory_contract_gate()
        passed, detail = spec.check(gw, [])
        assert passed is True
        assert "no files" in detail


class TestCheckDeletionCommit:
    """deletion commit——文件已删除（不存在），跳过校验（无法判定目录归属）。"""

    def test_all_nonexistent_files_returns_true(self, tmp_path):
        gw = _MockGateway(tmp_path)
        spec = make_directory_contract_gate()
        passed, detail = spec.check(gw, [str(tmp_path / "deleted.py")])
        assert passed is True
        assert "no files" in detail

    def test_mixed_existing_and_nonexistent(self, tmp_path):
        """部分存在部分不存在——只校验存在的。"""
        gw = _MockGateway(tmp_path)
        _make_checker_stub(tmp_path, exit_code=0)
        existing = _make_target_file(tmp_path, "foo.py")
        nonexistent = str(tmp_path / "deleted.py")
        spec = make_directory_contract_gate()
        passed, detail = spec.check(gw, [str(existing), nonexistent])
        assert passed is True  # 存在的文件 checker exit 0


class TestCheckCheckerNotFound:
    """checker 缺失——fail-closed 阻断（环境异常必须阻断，对标 _check_frontmatter_ttl）。"""

    def test_checker_missing_returns_false(self, tmp_path):
        gw = _MockGateway(tmp_path)
        _make_target_file(tmp_path, "foo.py")  # 文件存在但不重要
        spec = make_directory_contract_gate()
        passed, detail = spec.check(gw, [str(tmp_path / "foo.py")])
        assert passed is False
        assert "not found" in detail
        assert "check_directory_contract.py" in detail


class TestCheckPass:
    """checker exit 0——通过。"""

    def test_checker_exit_0_returns_true(self, tmp_path):
        gw = _MockGateway(tmp_path)
        _make_checker_stub(tmp_path, exit_code=0)
        _make_target_file(tmp_path, "foo.py")
        spec = make_directory_contract_gate()
        passed, detail = spec.check(gw, [str(tmp_path / "foo.py")])
        assert passed is True
        assert "passed" in detail


class TestCheckViolation:
    """checker exit 1——有违规，阻断 + detail 透传。"""

    def test_checker_exit_1_returns_false_with_detail(self, tmp_path):
        gw = _MockGateway(tmp_path)
        _make_checker_stub(
            tmp_path, exit_code=1, stderr_msg="DCR-001 violation: foo.py in wrong dir"
        )
        _make_target_file(tmp_path, "foo.py")
        spec = make_directory_contract_gate()
        passed, detail = spec.check(gw, [str(tmp_path / "foo.py")])
        assert passed is False
        assert "DCR-001" in detail

    def test_checker_exit_1_empty_stderr_falls_back_to_stdout(self, tmp_path):
        """stderr 空时 fallback 到 stdout（gate L131-132 逻辑）。"""
        gw = _MockGateway(tmp_path)
        # stderr_msg="" + exit 1——stderr 空，但 stub 也不写 stdout，
        # gate 会 fallback 到 stdout（也空），最终返回 "unknown detail"
        _make_checker_stub(tmp_path, exit_code=1, stderr_msg="")
        _make_target_file(tmp_path, "foo.py")
        spec = make_directory_contract_gate()
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
        spec = make_directory_contract_gate()
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
        spec = make_directory_contract_gate()
        passed, detail = spec.check(gw, [str(tmp_path / "foo.py")])
        assert passed is False
        assert "execution failed" in detail
        assert "permission denied" in detail


class TestRelativePathHandling:
    """相对路径转换——Windows 反斜杠转正斜杠（check_directory_contract.py 接受正斜杠）。"""

    def test_windows_backslash_converted(self, tmp_path, monkeypatch):
        """验证 _check 内部把 Windows 反斜杠转正斜杠传给 checker。"""
        gw = _MockGateway(tmp_path)
        _make_checker_stub(tmp_path, exit_code=0)
        # 创建嵌套文件触发反斜杠路径
        _make_target_file(tmp_path, "docs/sub/foo.py")

        captured_cmd: list[str] = []

        def _capture_cmd(*args, **kwargs):
            captured_cmd.extend(args[0])
            class _R:
                returncode = 0
                stderr = b""
                stdout = b""
            return _R()

        monkeypatch.setattr(subprocess, "run", _capture_cmd)
        spec = make_directory_contract_gate()
        spec.check(gw, [str(tmp_path / "docs/sub/foo.py")])
        # cmd = [python, checker_script, rel_path]
        # rel_path 应该是 "docs/sub/foo.py"（正斜杠），不是 "docs\\sub\\foo.py"
        assert len(captured_cmd) >= 3
        rel_arg = captured_cmd[2]
        assert "\\" not in rel_arg, f"expected forward slash, got {rel_arg!r}"
        assert rel_arg == "docs/sub/foo.py"


class TestCheckDeprecatedDirectory:
    """check_deprecated_directory 纯函数测试——检测文件是否位于废弃目录。

    验证 directory_contract.yaml §7 deprecated_directories 的检测逻辑：
    前缀匹配 + "/" 边界匹配（防 docs/09_audit 误报 docs/09_audit_other）。
    2026-06-30 补全：原 scan_files 漏检 deprecated_directories，新增本函数修复。
    """

    def test_file_in_deprecated_dir_detected(self, monkeypatch, tmp_path):
        """文件在废弃目录内 → 命中 DCR-DEPRECATED。

        用 monkeypatch + tmp_path 创建真实文件（ARCH-DEBT-BACKUP-CLEANUP 2026-07-08：
        check_deprecated_directory 现在检查文件存在性，虚构路径会被当作删除操作跳过）。
        """
        # 在 tmp_path 下创建废弃目录+文件
        deprecated_dir = tmp_path / "docs" / "_archive"
        deprecated_dir.mkdir(parents=True)
        (deprecated_dir / "old.md").touch()
        # monkeypatch REPO_ROOT 指向 tmp_path（check_deprecated_directory 用 REPOROOT / rel_path 检查存在性）
        monkeypatch.setattr(_mod, "REPO_ROOT", tmp_path)
        contract = {
            "deprecated_directories": [
                {"path": "docs/_archive", "reason": "已迁移", "migrated_to": "docs/01_policies"}
            ]
        }
        findings = check_deprecated_directory("docs/_archive/old.md", contract)
        assert len(findings) == 1
        assert findings[0]["rule"] == "DCR-DEPRECATED"
        assert "docs/_archive" in findings[0]["detail"]

    def test_file_in_safe_dir_not_flagged(self):
        """文件在安全目录 → 放行（无 finding）。"""
        contract = {
            "deprecated_directories": [
                {"path": "docs/_archive", "reason": "已迁移", "migrated_to": "docs/01_policies"}
            ]
        }
        findings = check_deprecated_directory("docs/01_policies/new.md", contract)
        assert findings == []

    def test_exact_deprecated_path_detected(self):
        """精确路径命中（rel_path 本身就是废弃目录路径）。"""
        contract = {
            "deprecated_directories": [{"path": "docs/_archive"}]
        }
        findings = check_deprecated_directory("docs/_archive", contract)
        assert len(findings) == 1

    def test_prefix_similar_not_false_positive(self):
        """前缀相似非子目录不误报（docs/09_audit vs docs/09_audit_other）。

        边界匹配：rel_norm == dep_path or rel_norm.startswith(dep_path + "/")。
        docs/09_audit_other 不以 "docs/09_audit/" 开头，故不误报。
        """
        contract = {
            "deprecated_directories": [{"path": "docs/09_audit"}]
        }
        findings = check_deprecated_directory("docs/09_audit_other/foo.md", contract)
        assert findings == []

    def test_empty_deprecated_directories(self):
        """contract 无 deprecated_directories → 放行。"""
        findings = check_deprecated_directory("any/file.py", {})
        assert findings == []

    def test_nonexistent_file_skipped(self):
        """文件不存在=删除操作 → 跳过 deprecated 检查（ARCH-DEBT-BACKUP-CLEANUP 2026-07-08）。

        deprecated_directories 设计意图是阻断**新建**文件进入废弃目录，而非阻断
        **删除**废弃目录中的已有文件。删除废弃目录中的文件正是期望的迁移行为。
        通过检测文件是否存在于磁盘上区分 add/modify vs delete：文件不存在=删除→放行。
        """
        contract = {
            "deprecated_directories": [
                {"path": "data/databases/backups", "reason": "已迁移", "migrated_to": "tmp/pg_backups"}
            ]
        }
        # 传入一个磁盘上不存在的路径（模拟删除操作）
        findings = check_deprecated_directory(
            "data/databases/backups/ghost_autoclean_nonexistent_test/deleted.csv", contract
        )
        assert findings == [], "删除废弃目录中的文件应放行，不应报 DCR-DEPRECATED"

    def test_scan_files_calls_check_deprecated_directory(self, monkeypatch):
        """scan_files 集成——验证 scan_files 调用 check_deprecated_directory（防漏调）。

        用 monkeypatch 替换为 spy，验证每个文件都被检测。防未来误删 scan_files L415 的调用。
        其他 check 函数 stub 为空（避免 contract 不完整报错，聚焦 deprecated 调用验证）。
        """
        called = []

        def _spy(rel_path, contract):
            called.append(rel_path)
            return []

        monkeypatch.setattr(_mod, "check_deprecated_directory", _spy)
        monkeypatch.setattr(_mod, "check_doc_type_directory", lambda *a, **k: [])
        monkeypatch.setattr(_mod, "check_extension", lambda *a, **k: [])
        monkeypatch.setattr(_mod, "check_root_whitelist", lambda *a, **k: [])
        monkeypatch.setattr(_mod, "check_ttl_zone", lambda *a, **k: [])
        scan_files(["foo.py", "bar.py"], {})
        assert called == ["foo.py", "bar.py"]
