# [A_test] module_id: MOD-GOV_audit_worktree_ops_telemetry | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-280 | docs/03_modules/_domain_governance/blueprint.md | §Ruling-100PCT-AI-GOVERNANCE-P2-6
# [MODULE] tests.governance.test_audit_worktree_ops_telemetry
# [DOMAIN] D_GOV_CODE_QUALITY
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] subprocess error->skip_test
# [TESTS] tests/governance/test_audit_worktree_ops_telemetry.py
# [A_module] module_id=MOD-TEST-280 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_audit_worktree_ops_telemetry.py — worktree_ops_log 遥测完整性审计测试

#Ruling-100PCT-AI-GOVERNANCE P2-6 治本：验证 audit_worktree_ops_telemetry.py 的检测逻辑
+ _log_workspace_op content_hash 字段 + _compute_content_hash + _quarantine_file hash 集成。

病根
----
项目记忆硬约束：主工作区文件级擦除（restore/unlink/quarantine）操作必须全量纳入
worktree_ops_log.jsonl 遥测，记录 session_id / source / file / content_hash / backup_path。
P2-6 前缺失 content_hash 字段，且有 _safe_unlink_main_file 死代码无遥测。

治本
----
1. _log_workspace_op 添加 content_hash 字段
2. _compute_content_hash 辅助函数（sha256 hex 前 16 字符）
3. _quarantine_file 移送前计算 hash
4. stash 遥测调用方计算 pre-stash hash
5. file_restore 遥测（git restore --source 恢复路径）
6. 删除 _safe_unlink_main_file 死代码
7. audit_worktree_ops_telemetry.py 审计脚本

测试覆盖
--------
- Part A: audit_worktree_ops_telemetry.py 审计脚本检测逻辑（14 项）
- Part B: _log_workspace_op content_hash 字段（4 项）
- Part C: _compute_content_hash 辅助函数（3 项）
- Part D: _quarantine_file hash 集成（2 项）
- Part E: e2e 真实仓库验证（2 项）
"""

from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "governance" / "audit_worktree_ops_telemetry.py"


# ---------------------------------------------------------------------------
# 加载被测模块（审计脚本）
# ---------------------------------------------------------------------------


def _load_audit_module():
    """用 importlib 加载 audit_worktree_ops_telemetry.py 为模块。

    注意：@dataclass 装饰器在 Python 3.11+ 需要 sys.modules 注册。
    """
    import importlib.util

    mod_name = "_test_target_audit_worktree_ops_telemetry"
    spec = importlib.util.spec_from_file_location(mod_name, SCRIPT_PATH)
    assert spec is not None and spec.loader is not None, f"无法加载 {SCRIPT_PATH}"
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def au():
    """加载审计脚本模块。"""
    return _load_audit_module()


# ---------------------------------------------------------------------------
# Part A: 审计脚本检测逻辑
# ---------------------------------------------------------------------------
pytestmark = pytest.mark.silent_failure  # Ruling:100PCT-AI-GOVERNANCE P3-2


class TestAuditScriptDetection:
    """audit_worktree_ops_telemetry.py 检测逻辑。"""

    def test_detects_git_stash_push_without_telemetry(self, au, tmp_path):
        """git stash push 无遥测 → error violation。"""
        f = tmp_path / "bad.py"
        f.write_text(
            textwrap.dedent("""
            def clean(root):
                subprocess.run(["git", "stash", "push", "-m", "x", "--", "a.py"],
                               cwd=str(root))
        """),
            encoding="utf-8",
        )
        violations = au.audit_worktree_ops_telemetry([f])
        assert len(violations) == 1
        v = violations[0]
        assert v.op == "git_stash_push"
        assert v.severity == "error"

    def test_detects_git_restore_without_telemetry(self, au, tmp_path):
        """git restore 无遥测 → error violation。"""
        f = tmp_path / "bad.py"
        f.write_text(
            textwrap.dedent("""
            def restore_file(root):
                subprocess.run(["git", "restore", "--source", "stash@{0}", "--", "a.py"],
                               cwd=str(root))
        """),
            encoding="utf-8",
        )
        violations = au.audit_worktree_ops_telemetry([f])
        assert len(violations) == 1
        assert violations[0].op == "git_restore"
        assert violations[0].severity == "error"

    def test_detects_path_unlink_without_telemetry(self, au, tmp_path):
        """Path.unlink() 无遥测 → warning violation。"""
        f = tmp_path / "bad.py"
        f.write_text(
            textwrap.dedent("""
            def delete(root, file):
                p = root / file
                p.unlink()
        """),
            encoding="utf-8",
        )
        violations = au.audit_worktree_ops_telemetry([f])
        assert len(violations) >= 1
        assert any(v.op == "path_unlink" and v.severity == "warning" for v in violations)

    def test_passes_when_telemetry_present(self, au, tmp_path):
        """函数内有 _log_workspace_op 调用 → 无违规。"""
        f = tmp_path / "good.py"
        f.write_text(
            textwrap.dedent("""
            def clean(root, session_id):
                subprocess.run(["git", "stash", "push", "-m", "x", "--", "a.py"],
                               cwd=str(root))
                _log_workspace_op("file_stash", session_id, "clean", root,
                                  file="a.py", backup_path="stash:x",
                                  content_hash="abc123")
        """),
            encoding="utf-8",
        )
        violations = au.audit_worktree_ops_telemetry([f])
        # git_stash_push 有遥测 → 0 violation
        stash_violations = [v for v in violations if v.op == "git_stash_push"]
        assert stash_violations == []

    def test_exempt_by_function_name(self, au, tmp_path):
        """函数名含豁免关键词（如 worktree_file）→ 无违规。"""
        f = tmp_path / "exempt.py"
        f.write_text(
            textwrap.dedent("""
            def _delete_worktree_file(dst, rel_file, wt_path):
                dst.unlink()
        """),
            encoding="utf-8",
        )
        violations = au.audit_worktree_ops_telemetry([f])
        assert violations == []

    def test_exempt_by_path_keyword(self, au, tmp_path):
        """行涉及 lock_file 路径关键词 → 豁免。"""
        f = tmp_path / "exempt.py"
        f.write_text(
            textwrap.dedent("""
            def release(root):
                import os
                os.remove(str(self._lock_file))
        """),
            encoding="utf-8",
        )
        violations = au.audit_worktree_ops_telemetry([f])
        # _lock_file 在 EXEMPT_PATH_KEYWORDS 中
        assert violations == []

    def test_docstring_lines_skipped(self, au, tmp_path):
        """docstring 中的 unlink/rmtree 字样不触发违规。"""
        f = tmp_path / "doc.py"
        f.write_text(
            textwrap.dedent('''
            """模块 docstring。

            检测 Path.unlink() / os.unlink() / os.remove() / shutil.rmtree() 操作。
            """

            def real_func(x):
                return x + 1
        '''),
            encoding="utf-8",
        )
        violations = au.audit_worktree_ops_telemetry([f])
        assert violations == []

    def test_comment_lines_skipped(self, au, tmp_path):
        """注释行不触发违规。"""
        f = tmp_path / "comment.py"
        f.write_text(
            textwrap.dedent("""
            def func(root):
                # p.unlink()  # 这只是注释
                return root
        """),
            encoding="utf-8",
        )
        violations = au.audit_worktree_ops_telemetry([f])
        assert violations == []

    def test_module_level_erasure_reported(self, au, tmp_path):
        """模块级（无函数包裹）擦除操作 → 报告。"""
        f = tmp_path / "module_level.py"
        f.write_text(
            textwrap.dedent("""
            import subprocess
            subprocess.run(["git", "stash", "push", "-m", "x", "--", "a.py"])
        """),
            encoding="utf-8",
        )
        violations = au.audit_worktree_ops_telemetry([f])
        assert len(violations) >= 1
        assert violations[0].function == "<module>"

    def test_directory_traversal_excludes_archive(self, au, tmp_path):
        """目录遍历排除 _archive 目录。"""
        archive = tmp_path / "_archive"
        archive.mkdir()
        (archive / "old.py").write_text(
            textwrap.dedent("""
            def clean(root):
                subprocess.run(["git", "stash", "push", "-m", "x", "--", "a.py"],
                               cwd=str(root))
        """),
            encoding="utf-8",
        )
        violations = au.audit_directory(tmp_path)
        assert all("_archive" not in v.file for v in violations)

    def test_directory_traversal_excludes_pycache(self, au, tmp_path):
        """目录遍历排除 __pycache__。"""
        pc = tmp_path / "__pycache__"
        pc.mkdir()
        (pc / "bad.py").write_text(
            textwrap.dedent("""
            def clean(root):
                subprocess.run(["git", "stash", "push", "-m", "x", "--", "a.py"],
                               cwd=str(root))
        """),
            encoding="utf-8",
        )
        violations = au.audit_directory(tmp_path)
        assert all("__pycache__" not in v.file for v in violations)

    def test_non_python_file_ignored(self, au, tmp_path):
        """非 .py 文件被忽略。"""
        f = tmp_path / "bad.txt"
        f.write_text('subprocess.run(["git", "stash", "push"])', encoding="utf-8")
        violations = au.audit_worktree_ops_telemetry([f])
        assert violations == []

    def test_syntax_error_file_skipped(self, au, tmp_path):
        """SyntaxError 文件 skip（返回空列表）。"""
        f = tmp_path / "broken.py"
        f.write_text("def broken(:\n    pass\n", encoding="utf-8")
        violations = au.audit_worktree_ops_telemetry([f])
        assert violations == []

    def test_sorting_by_file_line_col(self, au, tmp_path):
        """多违规按 (file, line, col) 排序。"""
        f1 = tmp_path / "a.py"
        f1.write_text(
            textwrap.dedent("""
            def clean(root):
                subprocess.run(["git", "stash", "push", "-m", "x", "--", "a.py"],
                               cwd=str(root))
                subprocess.run(["git", "restore", "--", "b.py"], cwd=str(root))
        """),
            encoding="utf-8",
        )
        violations = au.audit_worktree_ops_telemetry([f1])
        for i in range(len(violations) - 1):
            cur = (violations[i].file, violations[i].line, violations[i].col)
            nxt = (violations[i + 1].file, violations[i + 1].line, violations[i + 1].col)
            assert cur <= nxt


# ---------------------------------------------------------------------------
# Part B: 审计脚本 CLI
# ---------------------------------------------------------------------------


class TestAuditCli:
    """审计脚本 CLI exit code 与输出。"""

    def test_cli_exit_zero_no_violations(self, au, tmp_path):
        """无违规 → exit 0。"""
        f = tmp_path / "clean.py"
        f.write_text("x = 1\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(f)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert result.returncode == 0
        assert "0 violations" in result.stdout

    def test_cli_exit_one_with_error_violation(self, au, tmp_path):
        """有 error severity 违规 → exit 1。"""
        f = tmp_path / "bad.py"
        f.write_text(
            textwrap.dedent("""
            def clean(root):
                subprocess.run(["git", "stash", "push", "-m", "x", "--", "a.py"],
                               cwd=str(root))
        """),
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(f)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert result.returncode == 1

    def test_cli_json_output(self, au, tmp_path):
        """--json 输出 JSON 数组。"""
        f = tmp_path / "bad.py"
        f.write_text(
            textwrap.dedent("""
            def clean(root):
                subprocess.run(["git", "stash", "push", "-m", "x", "--", "a.py"],
                               cwd=str(root))
        """),
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--json", str(f)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert len(data) >= 1
        assert "op" in data[0]
        assert "file" in data[0]
        assert "line" in data[0]

    def test_cli_only_warning_exit_zero(self, au, tmp_path):
        """只有 warning（无 error）→ exit 0（默认 warning 不阻断）。"""
        f = tmp_path / "warn.py"
        f.write_text(
            textwrap.dedent("""
            def delete(root, file):
                p = root / file
                p.unlink()
        """),
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(f)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert result.returncode == 0

    def test_cli_include_warnings_exit_one(self, au, tmp_path):
        """--include-warnings 时 warning 也阻断 → exit 1。"""
        f = tmp_path / "warn.py"
        f.write_text(
            textwrap.dedent("""
            def delete(root, file):
                p = root / file
                p.unlink()
        """),
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--include-warnings", str(f)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert result.returncode == 1


# ---------------------------------------------------------------------------
# Part C: _log_workspace_op content_hash 字段
# ---------------------------------------------------------------------------


class TestLogWorkspaceOpContentHash:
    """_log_workspace_op content_hash 字段验证。"""

    def test_content_hash_param_exists(self):
        """_log_workspace_op 必须有 content_hash 参数。"""
        import inspect

        from zephyr.gov_enforcement.rule_bridge.session_worktree import _log_workspace_op

        sig = inspect.signature(_log_workspace_op)
        assert "content_hash" in sig.parameters, "_log_workspace_op 必须有 content_hash 参数（P2-6 硬约束）"

    def test_content_hash_recorded_in_log(self, tmp_path):
        """_log_workspace_op 调用后，worktree_ops_log.jsonl 含 content_hash 字段。"""
        from zephyr.gov_enforcement.rule_bridge.session_worktree import _log_workspace_op

        # tmp_path 不是 git 仓库，但 _log_workspace_op 用 strip_session_worktree 锚定主仓库
        # 直接调用，遥测降级不阻断
        _log_workspace_op(
            "file_stash",
            "sess-test",
            "test_source",
            tmp_path,
            file="test.py",
            backup_path="stash:test",
            content_hash="abc123def456",
        )
        log_file = tmp_path / ".runtime" / "worktree_ops_log.jsonl"
        assert log_file.exists(), f"遥测日志未写入: {log_file}"
        lines = log_file.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) >= 1
        entry = json.loads(lines[-1])
        assert entry["content_hash"] == "abc123def456"
        assert entry["session_id"] == "sess-test"
        assert entry["source"] == "test_source"
        assert entry["file"] == "test.py"
        assert entry["backup_path"] == "stash:test"

    def test_content_hash_defaults_empty(self, tmp_path):
        """不传 content_hash 时默认空字符串（向后兼容）。"""
        from zephyr.gov_enforcement.rule_bridge.session_worktree import _log_workspace_op

        _log_workspace_op(
            "file_stash",
            "sess-test",
            "test_source",
            tmp_path,
            file="test.py",
            backup_path="stash:test",
        )
        log_file = tmp_path / ".runtime" / "worktree_ops_log.jsonl"
        entry = json.loads(log_file.read_text(encoding="utf-8").strip().splitlines()[-1])
        assert entry["content_hash"] == ""

    def test_log_entry_has_all_required_fields(self, tmp_path):
        """日志条目含项目记忆硬约束的所有必填字段。"""
        from zephyr.gov_enforcement.rule_bridge.session_worktree import _log_workspace_op

        _log_workspace_op(
            "file_quarantine",
            "sess-test",
            "test_source",
            tmp_path,
            file="test.py",
            backup_path="/path/to/quarantine",
            content_hash="deadbeef",
        )
        log_file = tmp_path / ".runtime" / "worktree_ops_log.jsonl"
        entry = json.loads(log_file.read_text(encoding="utf-8").strip().splitlines()[-1])
        # 项目记忆硬约束：session_id / source / file / content_hash / backup_path
        required = {"session_id", "source", "file", "content_hash", "backup_path"}
        assert required.issubset(entry.keys()), f"缺少必填字段: {required - set(entry.keys())}"


# ---------------------------------------------------------------------------
# Part D: _compute_content_hash 辅助函数
# ---------------------------------------------------------------------------


class TestComputeContentHash:
    """_compute_content_hash 辅助函数。"""

    def test_computes_sha256_hex_16_chars(self, tmp_path):
        """返回 sha256 hex 前 16 字符。"""
        from zephyr.gov_enforcement.rule_bridge.session_worktree import _compute_content_hash

        f = tmp_path / "test.txt"
        f.write_text("hello world", encoding="utf-8")
        h = _compute_content_hash(f)
        assert len(h) == 16, f"hash 长度应为 16，实际 {len(h)}"
        # sha256("hello world") 前 16 字符
        import hashlib

        expected = hashlib.sha256(b"hello world").hexdigest()[:16]
        assert h == expected

    def test_nonexistent_file_returns_empty(self, tmp_path):
        """文件不存在 → 返回空字符串（不抛异常）。"""
        from zephyr.gov_enforcement.rule_bridge.session_worktree import _compute_content_hash

        h = _compute_content_hash(tmp_path / "does_not_exist.txt")
        assert h == ""

    def test_same_content_same_hash(self, tmp_path):
        """相同内容 → 相同 hash。"""
        from zephyr.gov_enforcement.rule_bridge.session_worktree import _compute_content_hash

        f1 = tmp_path / "a.txt"
        f1.write_text("same content", encoding="utf-8")
        f2 = tmp_path / "b.txt"
        f2.write_text("same content", encoding="utf-8")
        assert _compute_content_hash(f1) == _compute_content_hash(f2)

    def test_different_content_different_hash(self, tmp_path):
        """不同内容 → 不同 hash。"""
        from zephyr.gov_enforcement.rule_bridge.session_worktree import _compute_content_hash

        f1 = tmp_path / "a.txt"
        f1.write_text("content A", encoding="utf-8")
        f2 = tmp_path / "b.txt"
        f2.write_text("content B", encoding="utf-8")
        assert _compute_content_hash(f1) != _compute_content_hash(f2)


# ---------------------------------------------------------------------------
# Part E: _quarantine_file hash 集成
# ---------------------------------------------------------------------------


class TestQuarantineFileHashIntegration:
    """_quarantine_file 集成 content_hash 验证。"""

    def test_quarantine_logs_content_hash(self, tmp_path):
        """_quarantine_file 移送文件后，遥测日志含 content_hash。"""
        from zephyr.gov_enforcement.rule_bridge.session_worktree import (
            _quarantine_file,
            _quarantine_root,
        )

        # 创建测试文件
        src_file = tmp_path / "test_untracked.py"
        src_file.write_text("# AI generated temp file\n", encoding="utf-8")
        rel_file = "test_untracked.py"

        # 执行 quarantine
        result = _quarantine_file(tmp_path, rel_file, "sess-test", "test_source")
        assert result is not None, "quarantine 应成功"

        # 检查遥测日志
        log_file = tmp_path / ".runtime" / "worktree_ops_log.jsonl"
        assert log_file.exists()
        entry = json.loads(log_file.read_text(encoding="utf-8").strip().splitlines()[-1])
        assert entry["op"] == "file_quarantine"
        assert entry["content_hash"] != "", "quarantine 遥测必须含 content_hash"
        assert len(entry["content_hash"]) == 16
        assert entry["file"] == rel_file
        assert entry["backup_path"] == result

    def test_quarantine_hash_matches_file_content(self, tmp_path):
        """quarantine 记录的 content_hash 与原文件内容一致。"""
        import hashlib

        from zephyr.gov_enforcement.rule_bridge.session_worktree import _quarantine_file

        content = b"# test content for hash verification\n"
        src_file = tmp_path / "verify.py"
        src_file.write_bytes(content)
        expected_hash = hashlib.sha256(content).hexdigest()[:16]

        _quarantine_file(tmp_path, "verify.py", "sess-test", "test_source")

        log_file = tmp_path / ".runtime" / "worktree_ops_log.jsonl"
        entry = json.loads(log_file.read_text(encoding="utf-8").strip().splitlines()[-1])
        assert entry["content_hash"] == expected_hash, f"hash 不匹配: {entry['content_hash']} != {expected_hash}"


# ---------------------------------------------------------------------------
# Part F: _safe_unlink_main_file 死代码已删除
# ---------------------------------------------------------------------------


class TestSafeUnlinkMainFileDeleted:
    """验证 _safe_unlink_main_file 死代码已删除（P2-6b）。"""

    def test_safe_unlink_main_file_not_importable(self):
        """_safe_unlink_main_file 不应再可导入（已删除）。"""
        try:
            from zephyr.gov_enforcement.rule_bridge.session_worktree import _safe_unlink_main_file  # noqa: F401

            pytest.fail("_safe_unlink_main_file 应已删除，但仍可导入")
        except ImportError:
            pass  # 预期：已删除


# ---------------------------------------------------------------------------
# Part G: file_restore 遥测（P2-6c）
# ---------------------------------------------------------------------------


class TestFileRestoreTelemetry:
    """验证 _recover_changes_from_stash 添加了 file_restore 遥测。"""

    def test_recover_function_has_telemetry_call(self):
        """_recover_changes_from_stash 函数体内有 _log_workspace_op 调用。"""
        import inspect

        from zephyr.gov_enforcement.rule_bridge.session_worktree import _recover_changes_from_stash

        source = inspect.getsource(_recover_changes_from_stash)
        assert "_log_workspace_op" in source, "_recover_changes_from_stash 必须含 _log_workspace_op 调用（P2-6c）"
        assert "file_restore" in source, "_recover_changes_from_stash 必须含 file_restore op（P2-6c）"
        assert "_compute_content_hash" in source, "_recover_changes_from_stash 必须计算 content_hash（P2-6c）"


# ---------------------------------------------------------------------------
# Part H: e2e 真实仓库验证
# ---------------------------------------------------------------------------


class TestE2ERealRepo:
    """在真实 ZephyrAlpha 仓库上验证。"""

    def test_real_repo_rule_bridge_no_error_violations(self, au):
        """rule_bridge/ 目录 0 error severity 违规。"""
        violations = au.audit_directory(REPO_ROOT / "src" / "zephyr" / "gov_enforcement" / "rule_bridge")
        errors = [v for v in violations if v.severity == "error"]
        assert errors == [], (
            f"rule_bridge/ 发现 {len(errors)} 个 error 违规（应为 0）: {[(v.file, v.line, v.op) for v in errors[:5]]}"
        )

    def test_real_repo_gov_enforcement_no_error_violations(self, au):
        """整个 gov_enforcement/ 0 error severity 违规。"""
        violations = au.audit_directory(REPO_ROOT / "src" / "zephyr" / "gov_enforcement")
        errors = [v for v in violations if v.severity == "error"]
        assert errors == [], (
            f"gov_enforcement/ 发现 {len(errors)} 个 error 违规（应为 0）: "
            f"{[(v.file, v.line, v.op) for v in errors[:5]]}"
        )

    def test_real_repo_worktree_ops_log_has_content_hash_field(self):
        """真实仓库的 _log_workspace_op 源码含 content_hash 字段定义。"""
        sw_path = REPO_ROOT / "src" / "zephyr" / "gov_enforcement" / "rule_bridge" / "session_worktree.py"
        source = sw_path.read_text(encoding="utf-8")
        assert '"content_hash": content_hash' in source, "_log_workspace_op entry dict 必须含 content_hash 字段"
        assert "def _compute_content_hash" in source, "必须有 _compute_content_hash 辅助函数"
