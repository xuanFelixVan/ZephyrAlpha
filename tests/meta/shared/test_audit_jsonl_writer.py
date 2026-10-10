# [A_test] module_id: TEST-MOD-INF-016-TEST_AUDIT_JSONL_WRITER-TEST_AUDIT_JSONL_WRITER | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.shared.test_audit_jsonl_writer
# [DOMAIN] D_SHARED
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [A_module] module_id=TEST-MOD-INF-016-TEST_AUDIT_JSONL_WRITER-TEST_AUDIT_JSONL_WRITER | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_audit_jsonl_writer.py — 审计 jsonl 统一写入助手单测（批5c 验收）

覆盖：
1. 基本追加写 roundtrip（自动建目录/逐行 jsonl）
2. 写前大小轮转：当前段 ≥ max_bytes → 先轮转（.1 生成）再写入新内容
3. 多段移位：两次轮转后 .1/.2 序号与内容正确（.1 新 .2 老）
4. 最老段丢弃：backup_count=2 轮转 3 次 → 段数 ≤2，最早内容被丢弃
5. 写入失败返回 False 不抛（路径冲突/目录不可创建）——审计永不阻断主链路
"""

from __future__ import annotations

import json
from pathlib import Path

from zephyr.shared.io.audit_jsonl_writer import (
    DEFAULT_BACKUP_COUNT,
    DEFAULT_MAX_BYTES,
    append_audit_jsonl,
    rotate_if_oversized,
)


def _read(path: Path) -> list[dict]:
    return [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


class TestAppendBasics:
    def test_append_creates_dir_and_roundtrip(self, tmp_path: Path) -> None:
        audit_dir = tmp_path / ".runtime" / "gate_audit"
        assert append_audit_jsonl(audit_dir, "x.jsonl", {"a": 1}) is True
        assert append_audit_jsonl(audit_dir, "x.jsonl", {"b": 2}) is True
        rows = _read(audit_dir / "x.jsonl")
        assert rows == [{"a": 1}, {"b": 2}]

    def test_chinese_content_not_escaped(self, tmp_path: Path) -> None:
        """ensure_ascii=False——中文原样落盘（审计可读性）。"""
        append_audit_jsonl(tmp_path, "x.jsonl", {"事件": "删除"})
        assert "删除" in (tmp_path / "x.jsonl").read_text(encoding="utf-8")


class TestRotation:
    def test_oversize_triggers_rotation_before_write(self, tmp_path: Path) -> None:
        """当前段 ≥ max_bytes → 先轮转成 .1，新内容写入新当前段。"""
        p = tmp_path / "x.jsonl"
        p.write_text("o" * 100, encoding="utf-8")
        assert append_audit_jsonl(tmp_path, "x.jsonl", {"n": 1}, max_bytes=50) is True
        assert (tmp_path / "x.jsonl.1").exists(), "超阈值未触发轮转"
        assert (tmp_path / "x.jsonl.1").read_text(encoding="utf-8") == "o" * 100
        assert _read(p) == [{"n": 1}], "新内容应写入轮转后的新当前段"

    def test_multi_rotation_shifts_segments(self, tmp_path: Path) -> None:
        """两次轮转：.1=次新段，.2=最老段，序号越大越老。"""
        p = tmp_path / "x.jsonl"
        p.write_text("A" * 60, encoding="utf-8")
        append_audit_jsonl(tmp_path, "x.jsonl", {"r": 1}, max_bytes=50)  # 轮转1：A→.1
        # 写满当前段触发第二次轮转
        with p.open("a", encoding="utf-8") as f:
            f.write("B" * 60)
        append_audit_jsonl(tmp_path, "x.jsonl", {"r": 2}, max_bytes=50)  # 轮转2：含B段→.1，A段→.2
        seg1 = (tmp_path / "x.jsonl.1").read_text(encoding="utf-8")
        seg2 = (tmp_path / "x.jsonl.2").read_text(encoding="utf-8")
        assert "B" * 60 in seg1 and '"r": 1' in seg1, ".1 应为次新段"
        assert seg2 == "A" * 60, ".2 应为最老段"
        assert _read(p) == [{"r": 2}]

    def test_oldest_segment_dropped_beyond_backup_count(self, tmp_path: Path) -> None:
        """backup_count=2 轮转 3 次 → 最多 2 个历史段，最早内容物理丢弃。"""
        p = tmp_path / "x.jsonl"
        for i in range(3):
            with p.open("a", encoding="utf-8") as f:
                f.write(chr(ord("A") + i) * 60)
            append_audit_jsonl(tmp_path, "x.jsonl", {"r": i}, max_bytes=50, backup_count=2)
        assert (tmp_path / "x.jsonl.1").exists()
        assert (tmp_path / "x.jsonl.2").exists()
        assert not (tmp_path / "x.jsonl.3").exists(), "超出 backup_count 的段未丢弃"
        assert "A" * 60 not in (tmp_path / "x.jsonl.1").read_text(encoding="utf-8") + (
            tmp_path / "x.jsonl.2"
        ).read_text(encoding="utf-8"), "最老段内容应已物理丢弃"

    def test_rotation_failure_does_not_block_append(self, tmp_path: Path) -> None:
        """轮转异常（.1 被目录占位）→ 跳过轮转仍完成追加（保追加优先）。"""
        p = tmp_path / "x.jsonl"
        p.write_text("o" * 100, encoding="utf-8")
        (tmp_path / "x.jsonl.1").mkdir()  # 目录占位使 rename 失败
        assert append_audit_jsonl(tmp_path, "x.jsonl", {"n": 1}, max_bytes=50) is True
        rows = _read(p)
        assert rows[-1] == {"n": 1}, "轮转失败不应阻断追加写"


class TestFailureContract:
    def test_uncreatable_dir_returns_false_not_raise(self, tmp_path: Path) -> None:
        """audit_dir 路径被文件占位（mkdir 必败）→ False 不抛。"""
        blocker = tmp_path / "blocked"
        blocker.write_text("x", encoding="utf-8")
        assert append_audit_jsonl(blocker / "sub", "x.jsonl", {"a": 1}) is False


class TestRotateIfOversizedEntryGate:
    """T14（2026-10-11）入口闸：`rotate_if_oversized`＝把体积判据从"走 writer 才有"
    升级为"打开前先问一把"，供自带 append 的裸写侧（worktree_drift_watchdog /
    bottleneck_ledger 族）复用同一把尺（DEFAULT_MAX_BYTES/DEFAULT_BACKUP_COUNT）。

    红证两面缺一不可：超限必轮转（治膨胀）、未超限**不得**轮转（防把闸做成
    "每次打开都搬文件"——那是把审计件的 mtime/路径语义搅乱）。
    """

    def test_oversized_segment_is_rotated(self, tmp_path: Path) -> None:
        """当前段 ≥ max_bytes → 移位为 .1（保留非删除），返回 True。"""
        p = tmp_path / "ledger.jsonl"
        p.write_text("o" * 100, encoding="utf-8")
        assert rotate_if_oversized(p, max_bytes=50, backup_count=3) is True
        seg1 = tmp_path / "ledger.jsonl.1"
        assert seg1.exists() and seg1.read_text(encoding="utf-8") == "o" * 100
        assert not p.exists(), "轮转后当前段应让位（调用方随后新建追加）"

    def test_under_threshold_is_left_untouched(self, tmp_path: Path) -> None:
        """未超限 → False 且零副作用（不搬文件、不建目录、不改内容）。"""
        p = tmp_path / "ledger.jsonl"
        p.write_text("short", encoding="utf-8")
        before = p.read_bytes()
        assert rotate_if_oversized(p, max_bytes=50) is False
        assert p.read_bytes() == before
        assert not (tmp_path / "ledger.jsonl.1").exists()

    def test_absent_file_returns_false_without_creating(self, tmp_path: Path) -> None:
        """文件不存在（首写）→ False，且绝不创建任何东西（写侧自己负责建目录）。"""
        p = tmp_path / "sub" / "new.jsonl"
        assert rotate_if_oversized(p) is False
        assert not (tmp_path / "sub").exists()

    def test_rotation_failure_returns_false_and_keeps_segment(self, tmp_path: Path) -> None:
        """轮转本体失败（最老段被目录占位，unlink 必抛 OSError）→ False 不抛，原段零丢失。

        ⚠ 不能用 backup_count=3 + `.1` 目录占位来构造失败：`_rotate` 先把 `.1` 移位成
        `.2`，随后文件→`.1` 的目标已空，rename 根本不会失败（既有
        `test_rotation_failure_does_not_block_append` 的前提即为此弱案，其断言只落在
        "追加仍完成"上才没翻车）。backup_count=1 时最老段=`.1` 自身，unlink 目录=真抛。
        """
        p = tmp_path / "ledger.jsonl"
        p.write_text("keepme" * 40, encoding="utf-8")
        (tmp_path / "ledger.jsonl.1").mkdir()
        assert rotate_if_oversized(p, max_bytes=50, backup_count=1) is False
        assert p.exists() and p.read_text(encoding="utf-8").startswith("keepme")

    def test_default_threshold_is_the_50mb_ruler(self) -> None:
        """判据单一口径：入口闸与 append_audit_jsonl 共用 DEFAULT_MAX_BYTES（50MB）。

        在册病根＝"audit_jsonl_writer.py:59 的 50MiB 轮转未被这些写侧套用"——本例
        钉住两处同源同值，防后来者给入口闸另配一把尺（新配置册=违 §4 净零）。
        """
        import inspect

        sig = inspect.signature(rotate_if_oversized)
        assert sig.parameters["max_bytes"].default is DEFAULT_MAX_BYTES
        assert sig.parameters["backup_count"].default is DEFAULT_BACKUP_COUNT
        assert DEFAULT_MAX_BYTES == 50 * 1024 * 1024
