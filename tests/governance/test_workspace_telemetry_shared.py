# [A_test] module_id: MOD-GOV_workspace_telemetry_shared | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-WORKSPACE_TELEMETRY | docs/03_modules/_cross_layer/shared_core/blueprint.md | §workspace-telemetry
# [MODULE] tests.governance.test_workspace_telemetry_shared
# [DOMAIN] D_GOV_AUDIT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/governance/test_workspace_telemetry_shared.py
# [A_module] module_id=MOD-WORKSPACE_TELEMETRY | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_workspace_telemetry_shared.py — shared workspace_telemetry 公共 API 单测

权威依据：src/zephyr/shared/io/workspace_telemetry.py（#ARCH-P3-FOLLOWUP-TODOS-001 裁定 A）

测试组：
- TestLogWorkspaceOp: log_workspace_op 写入 worktree_ops_log.jsonl 的字段完整性
- TestLogWorkspaceOpDegradation: 遥测失败仅 debug 日志，不抛异常
- TestComputeContentHash: compute_content_hash sha256 hex 前 16 字符
- TestStripSessionWorktreeIntegration: root 是 worktree 路径时自动 strip 到主仓库 .runtime/

测试隔离：tmp_path 创建临时仓库结构；monkeypatch 替换 strip_session_worktree 行为。
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.shared.io.workspace_telemetry import (  # noqa: E402
    compute_content_hash,
    log_workspace_op,
)

# ===========================================================================
# TestLogWorkspaceOp: 字段完整性
# ===========================================================================

class TestLogWorkspaceOp:
    """log_workspace_op 写入 worktree_ops_log.jsonl 的字段完整性。"""

    def test_writes_all_required_fields(self, tmp_path):
        """所有必填字段正确写入 jsonl。"""
        log_workspace_op(
            op="git_restore_rollback",
            session_id="sess-test-001",
            source="self_healer.rollback",
            root=tmp_path,
            file="src/foo.py",
            content_hash="abc123def456abcd",
            backup_path="",
        )

        log_file = tmp_path / ".runtime" / "worktree_ops_log.jsonl"
        assert log_file.exists(), "log file should be created"
        lines = log_file.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1, "exactly one entry expected"

        entry = json.loads(lines[0])
        # 必填字段（项目记忆硬约束）
        assert entry["op"] == "git_restore_rollback"
        assert entry["session_id"] == "sess-test-001"
        assert entry["source"] == "self_healer.rollback"
        assert entry["file"] == "src/foo.py"
        assert entry["content_hash"] == "abc123def456abcd"
        assert entry["backup_path"] == ""
        # ts 字段应为 ISO 格式（含时区）
        assert "ts" in entry
        assert "T" in entry["ts"], "ts should be ISO format"

    def test_optional_fields_default_empty(self, tmp_path):
        """可选字段（file/backup_path/content_hash）默认空字符串。"""
        log_workspace_op(
            op="file_stash",
            session_id="sess-test-002",
            source="test_caller",
            root=tmp_path,
        )

        log_file = tmp_path / ".runtime" / "worktree_ops_log.jsonl"
        entry = json.loads(log_file.read_text(encoding="utf-8").strip())
        assert entry["file"] == ""
        assert entry["backup_path"] == ""
        assert entry["content_hash"] == ""

    def test_appends_multiple_entries(self, tmp_path):
        """多次调用追加到同一文件（不覆盖）。"""
        for i in range(3):
            log_workspace_op(
                op=f"op_{i}",
                session_id="sess-test-003",
                source="test_caller",
                root=tmp_path,
            )

        log_file = tmp_path / ".runtime" / "worktree_ops_log.jsonl"
        lines = log_file.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 3, "3 entries expected after 3 calls"
        ops = [json.loads(line)["op"] for line in lines]
        assert ops == ["op_0", "op_1", "op_2"]

    def test_creates_runtime_dir_if_missing(self, tmp_path):
        """root/.runtime 目录不存在时自动创建。"""
        # 确保目录不存在
        runtime_dir = tmp_path / ".runtime"
        assert not runtime_dir.exists()

        log_workspace_op(
            op="test_op",
            session_id="sess-test-004",
            source="test_caller",
            root=tmp_path,
        )

        assert runtime_dir.exists(), ".runtime dir should be auto-created"
        assert (runtime_dir / "worktree_ops_log.jsonl").exists()


# ===========================================================================
# TestLogWorkspaceOpDegradation: 遥测降级
# ===========================================================================

class TestLogWorkspaceOpDegradation:
    """遥测失败仅 debug 日志，不抛异常（ERROR_CONTRACT）。"""

    def test_invalid_root_path_no_raise(self):
        """root 为不存在路径且无法创建时不抛异常（降级为 debug 日志）。"""
        # Windows 下只读父目录可能导致 mkdir 失败，但 pathlib mkdir parents=True 通常能创建
        # 用一个明确不可写的路径模拟（如已存在的文件作为父目录）
        # 这里用 tmp_path 下的一个文件作为 root，mkdir 会失败
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as f:
            invalid_root = Path(f.name)

        try:
            # root 是文件而非目录，mkdir 应失败
            # 但 log_workspace_op 内部用 try/except 包裹，应降级不抛
            log_workspace_op(
                op="test_degradation",
                session_id="sess-degrade-001",
                source="test_caller",
                root=invalid_root,
            )
            # 无 assert — 不抛即通过
        finally:
            invalid_root.unlink(missing_ok=True)

    def test_exception_in_strip_no_raise(self, tmp_path, monkeypatch):
        """anchor_main_root 抛异常时不影响 log_workspace_op（降级）。"""
        from zephyr.shared.io import workspace_telemetry as wt

        def boom(_path):
            raise RuntimeError("anchor failed")

        monkeypatch.setattr(wt, "anchor_main_root", boom)

        # 不应抛异常
        log_workspace_op(
            op="test_strip_fail",
            session_id="sess-degrade-002",
            source="test_caller",
            root=tmp_path,
        )

    def test_no_logging_error_propagation(self, tmp_path, caplog):
        """遥测失败时记录 debug 日志，不传播 error。"""
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as f:
            invalid_root = Path(f.name)

        try:
            with caplog.at_level(logging.DEBUG, logger="zephyr.shared.io.workspace_telemetry"):
                log_workspace_op(
                    op="test_caplog",
                    session_id="sess-degrade-003",
                    source="test_caller",
                    root=invalid_root,
                )
            # 不抛即通过；debug 日志可选
        finally:
            invalid_root.unlink(missing_ok=True)


# ===========================================================================
# TestComputeContentHash: sha256 hex 前 16 字符
# ===========================================================================

class TestComputeContentHash:
    """compute_content_hash 返回 sha256 hex 前 16 字符。"""

    def test_returns_hex_first_16_chars(self, tmp_path):
        """已知内容的 sha256 hex 前 16 字符。"""
        import hashlib
        content = b"hello world\n"
        expected = hashlib.sha256(content).hexdigest()[:16]

        test_file = tmp_path / "test.txt"
        test_file.write_bytes(content)

        result = compute_content_hash(test_file)
        assert result == expected
        assert len(result) == 16, "should return exactly 16 chars"

    def test_empty_file_returns_hash(self, tmp_path):
        """空文件返回 sha256("")[:16]（非空字符串）。"""
        import hashlib
        empty_file = tmp_path / "empty.txt"
        empty_file.write_bytes(b"")

        result = compute_content_hash(empty_file)
        assert result == hashlib.sha256(b"").hexdigest()[:16]
        assert len(result) == 16

    def test_nonexistent_file_returns_empty(self, tmp_path):
        """文件不存在返回空字符串（不抛异常）。"""
        nonexistent = tmp_path / "does_not_exist.txt"
        result = compute_content_hash(nonexistent)
        assert result == "", "nonexistent file should return empty string"

    def test_large_file_hashed_correctly(self, tmp_path):
        """大文件（>8192 bytes，超过 chunk size）正确分块哈希。"""
        import hashlib
        # 20KB 内容（超过 8192 chunk size，验证分块逻辑）
        content = b"x" * 20480
        expected = hashlib.sha256(content).hexdigest()[:16]

        large_file = tmp_path / "large.bin"
        large_file.write_bytes(content)

        result = compute_content_hash(large_file)
        assert result == expected

    def test_different_content_different_hash(self, tmp_path):
        """不同内容返回不同 hash。"""
        f1 = tmp_path / "f1.txt"
        f2 = tmp_path / "f2.txt"
        f1.write_bytes(b"content A")
        f2.write_bytes(b"content B")

        h1 = compute_content_hash(f1)
        h2 = compute_content_hash(f2)
        assert h1 != h2, "different content should produce different hash"


# ===========================================================================
# TestStripSessionWorktreeIntegration: worktree 路径自动 strip
# ===========================================================================

class TestStripSessionWorktreeIntegration:
    """root 是 worktree 路径时自动 strip 到主仓库 .runtime/。"""

    def test_worktree_path_stripped_to_main_repo(self, tmp_path, monkeypatch):
        """root 含 .aidrafts/sess-xxx worktree 前缀时，日志写到主仓库 .runtime/。"""
        main_repo = tmp_path / "main_repo"
        main_repo.mkdir()
        worktree_path = main_repo / ".aidrafts" / "sess-test-strip-001"
        worktree_path.mkdir(parents=True)

        # monkeypatch anchor_main_root 返回主仓库路径（单级父目录判定语义）
        from zephyr.shared.io import workspace_telemetry as wt

        def fake_anchor(p):
            s = str(p)
            if ".aidrafts" in s:
                # 返回 .aidrafts 之前的部分（主仓库根）
                idx = s.find(".aidrafts")
                return Path(s[:idx].rstrip("\\/"))
            return p

        monkeypatch.setattr(wt, "anchor_main_root", fake_anchor)

        log_workspace_op(
            op="worktree_op",
            session_id="sess-test-strip-001",
            source="session_worktree_commit",
            root=worktree_path,
            file="src/foo.py",
        )

        # 日志应写入主仓库 .runtime/，而非 worktree 内
        main_log = main_repo / ".runtime" / "worktree_ops_log.jsonl"
        worktree_log = worktree_path / ".runtime" / "worktree_ops_log.jsonl"

        assert main_log.exists(), "log should be in main repo .runtime/"
        assert not worktree_log.exists(), "log should NOT be in worktree .runtime/"

    def test_normal_path_not_stripped(self, tmp_path, monkeypatch):
        """root 是普通路径（无 .aidrafts 前缀）时，日志写到该路径 .runtime/。"""
        from zephyr.shared.io import workspace_telemetry as wt
        from zephyr.shared.io.paths import anchor_main_root as real_anchor

        # 用真实的 anchor_main_root（不 mock）
        monkeypatch.setattr(wt, "anchor_main_root", real_anchor)

        normal_root = tmp_path / "project"
        normal_root.mkdir()

        log_workspace_op(
            op="normal_op",
            session_id="sess-test-normal-001",
            source="test_caller",
            root=normal_root,
        )

        log_file = normal_root / ".runtime" / "worktree_ops_log.jsonl"
        assert log_file.exists(), "log should be in normal_root .runtime/"
