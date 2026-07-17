# [A_test] module_id: SRC-TST-2159 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.test_foreign_change_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
# [ARCH-054]
"""test_foreign_change_gate.py — 外来变更检测门禁单测（FOREIGN-CHANGE-DETECTION，ARCH-054 治本）

权威依据：foreign_change_gate.py（make_foreign_change_gate）

测试组：
- TestNoSnapshotPasses: 无基线快照（reconciler auto-commit 路径）→ passed=True
- TestCleanBaselinePasses: 基线为空（claim 时文件干净）→ passed=True
- TestDirtyBaselineBlocked: 基线非空（claim 时已有外来变更）→ passed=False
- TestAllowOverlapEscape: allow_overlap=True 逃生通道放行
- TestNoSessionIdPasses: 无 session_id → 放行
- TestSnapshotExceptionSafe: _claim_snapshots 读取异常安全降级（不阻断）
- TestGateSpecFields: gate_id / priority 字段正确
- TestSnapshotDiskPersistence: S3-C 治本——claim 快照磁盘持久化 + 崩溃恢复
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import MagicMock

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec
from zephyr.gov_enforcement.commit_gates.foreign_change_gate import (
    make_foreign_change_gate,
)
from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import GitCommitGateway


def _make_gateway(
    project_root: Path,
    session_snapshots: dict[str, str] | None = None,
    raise_exc: Exception | None = None,
) -> MagicMock:
    """构造 mock gateway，模拟 _claim_snapshots。

    Args:
        project_root: 项目根目录。
        session_snapshots: per-session 快照内层 dict（abs_path -> baseline）。
            模拟 _claim_snapshots.get(session_id, {}) 的返回值。
        raise_exc: 若非 None，_claim_snapshots.get 抛此异常（测试安全降级）。
    """
    gw = MagicMock()
    gw.project_root = project_root
    if raise_exc is not None:
        gw._claim_snapshots.get.side_effect = raise_exc
    else:
        gw._claim_snapshots.get.return_value = session_snapshots or {}
    return gw


class TestNoSnapshotPasses:
    """无基线快照（未走 claim_files 的路径）→ 放行。"""

    def test_no_snapshot_passes(self, tmp_path):
        """文件不在 snapshots 中 → passed=True（reconciler auto-commit 路径）。"""
        gw = _make_gateway(tmp_path)
        gate = make_foreign_change_gate()
        target = tmp_path / "a.py"
        target.touch()
        passed, detail = gate.check(
            gw, [str(target)], session_id="s1", allow_overlap=False,
        )
        assert passed is True
        assert detail == ""


class TestCleanBaselinePasses:
    """基线为空（claim 时文件干净）→ 放行。"""

    def test_empty_baseline_passes(self, tmp_path):
        """文件在 snapshots 中但基线为空串 → passed=True。"""
        target = tmp_path / "a.py"
        target.touch()
        abs_target = os.path.abspath(str(target))
        gw = _make_gateway(tmp_path, session_snapshots={abs_target: ""})
        gate = make_foreign_change_gate()
        passed, detail = gate.check(
            gw, [str(target)], session_id="s1", allow_overlap=False,
        )
        assert passed is True
        assert detail == ""


class TestDirtyBaselineBlocked:
    """基线非空（claim 时文件已有外来变更）→ 阻断。"""

    def test_dirty_baseline_blocked(self, tmp_path):
        """文件基线非空 → passed=False，detail 含 FOREIGN_CHANGE_VIOLATION。"""
        target = tmp_path / "a.py"
        target.touch()
        abs_target = os.path.abspath(str(target))
        gw = _make_gateway(
            tmp_path, session_snapshots={abs_target: "-old foreign line\n+new foreign line"},
        )
        gate = make_foreign_change_gate()
        passed, detail = gate.check(
            gw, [str(target)], session_id="s1", allow_overlap=False,
        )
        assert passed is False
        assert "FOREIGN_CHANGE_VIOLATION" in detail
        assert "a.py" in detail  # 相对路径显示

    def test_partial_dirty_blocked(self, tmp_path):
        """多文件中部分基线非空 → 阻断。"""
        a = tmp_path / "a.py"
        b = tmp_path / "b.py"
        a.touch()
        b.touch()
        abs_a = os.path.abspath(str(a))
        abs_b = os.path.abspath(str(b))
        # a 干净，b 脏
        gw = _make_gateway(
            tmp_path, session_snapshots={abs_a: "", abs_b: "dirty diff content"},
        )
        gate = make_foreign_change_gate()
        passed, detail = gate.check(
            gw, [str(a), str(b)], session_id="s1", allow_overlap=False,
        )
        assert passed is False
        assert "b.py" in detail
        assert "a.py" not in detail  # a 干净不在违规列表


class TestAllowOverlapEscape:
    """allow_overlap=True 逃生通道放行。"""

    def test_escape_hatch_passes_even_on_dirty(self, tmp_path):
        """基线非空但 allow_overlap=True → 放行（逃生通道）。"""
        target = tmp_path / "a.py"
        target.touch()
        abs_target = os.path.abspath(str(target))
        gw = _make_gateway(
            tmp_path, session_snapshots={abs_target: "dirty foreign content"},
        )
        gate = make_foreign_change_gate()
        passed, detail = gate.check(
            gw, [str(target)], session_id="s1", allow_overlap=True,
        )
        assert passed is True
        assert detail == ""


class TestNoSessionIdPasses:
    """无 session_id → 放行。"""

    def test_empty_session_id_passes(self, tmp_path):
        """session_id 为空 → passed=True（CLAIM-REQUIRED 会处理）。"""
        target = tmp_path / "a.py"
        target.touch()
        gw = _make_gateway(tmp_path)
        gate = make_foreign_change_gate()
        passed, detail = gate.check(
            gw, [str(target)], session_id="", allow_overlap=False,
        )
        assert passed is True
        assert detail == ""


class TestSnapshotExceptionSafe:
    """_claim_snapshots 读取异常安全降级（不阻断 commit）。"""

    def test_exception_degrades_to_pass(self, tmp_path):
        """_claim_snapshots.get 异常 → 降级为无快照 → 放行。"""
        target = tmp_path / "a.py"
        target.touch()
        gw = _make_gateway(
            tmp_path, raise_exc=RuntimeError("snapshots dict corrupted"),
        )
        gate = make_foreign_change_gate()
        passed, detail = gate.check(
            gw, [str(target)], session_id="s1", allow_overlap=False,
        )
        assert passed is True
        assert detail == ""


class TestGateSpecFields:
    """gate_id / priority 字段正确。"""

    def test_gate_id_and_priority(self):
        """返回的 GateSpec 字段符合约定。"""
        spec = make_foreign_change_gate()
        assert isinstance(spec, GateSpec)
        assert spec.gate_id == "FOREIGN-CHANGE-DETECTION"
        assert spec.priority == 45  # 在 CLAIM-REQUIRED(40) 后、HELD-OVERLAP(50) 前


# ---------------------------------------------------------------------------
# S3-C 治本（2026-07-17）：claim 快照磁盘持久化测试
# ---------------------------------------------------------------------------

def _make_minimal_gateway(project_root: Path) -> GitCommitGateway:
    """构造最小化 GitCommitGateway（跳过 __init__ 的重量级注册），仅设置快照相关属性。

    用于测试 _save/_load/_delete_session_snapshot 磁盘持久化 helper。
    """
    gw = GitCommitGateway.__new__(GitCommitGateway)
    gw.project_root = project_root
    gw._claim_snapshots = {}
    gw._claim_snapshots_dir = project_root / ".runtime" / "claim_snapshots"
    return gw


class TestSnapshotDiskPersistence:
    """S3-C: claim 快照磁盘持久化——_save/_load/_delete helper 测试。"""

    def test_save_session_snapshot_writes_json(self, tmp_path):
        """_save_session_snapshot 将快照写入 .runtime/claim_snapshots/{session_id}.json。"""
        gw = _make_minimal_gateway(tmp_path)
        gw._claim_snapshots["sess-test"] = {"/abs/file.py": "diff content"}
        gw._save_session_snapshot("sess-test")
        snap_file = gw._claim_snapshots_dir / "sess-test.json"
        assert snap_file.exists(), "快照文件未创建"
        data = json.loads(snap_file.read_text(encoding="utf-8"))
        assert data["session_id"] == "sess-test"
        assert data["snapshots"]["/abs/file.py"] == "diff content"

    def test_load_claim_snapshots_from_disk_recovers(self, tmp_path):
        """新 gateway __init__ 从磁盘恢复快照（崩溃恢复核心场景）。"""
        # 第一个 gateway 写入快照
        gw1 = _make_minimal_gateway(tmp_path)
        gw1._claim_snapshots["sess-crash"] = {"/abs/a.py": "baseline diff"}
        gw1._save_session_snapshot("sess-crash")
        # 模拟进程崩溃：新 gateway 实例从磁盘加载
        gw2 = _make_minimal_gateway(tmp_path)
        gw2._load_claim_snapshots_from_disk()
        assert "sess-crash" in gw2._claim_snapshots
        assert gw2._claim_snapshots["sess-crash"]["/abs/a.py"] == "baseline diff"

    def test_delete_session_snapshot_removes_file(self, tmp_path):
        """_delete_session_snapshot 删除磁盘快照文件。"""
        gw = _make_minimal_gateway(tmp_path)
        gw._claim_snapshots["sess-del"] = {"/abs/x.py": "diff"}
        gw._save_session_snapshot("sess-del")
        snap_file = gw._claim_snapshots_dir / "sess-del.json"
        assert snap_file.exists()
        gw._delete_session_snapshot("sess-del")
        assert not snap_file.exists(), "快照文件未删除"

    def test_delete_nonexistent_snapshot_is_silent(self, tmp_path):
        """_delete_session_snapshot 对不存在的文件静默（不抛异常）。"""
        gw = _make_minimal_gateway(tmp_path)
        # 不应抛异常
        gw._delete_session_snapshot("sess-ghost")

    def test_load_skips_corrupt_snapshot_file(self, tmp_path):
        """损坏的 JSON 文件被跳过（不崩溃，log warning）。"""
        gw = _make_minimal_gateway(tmp_path)
        gw._claim_snapshots_dir.mkdir(parents=True, exist_ok=True)
        # 写入正常快照
        (gw._claim_snapshots_dir / "sess-good.json").write_text(
            json.dumps({"session_id": "sess-good", "snapshots": {"/a": "diff"}}),
            encoding="utf-8",
        )
        # 写入损坏快照
        (gw._claim_snapshots_dir / "sess-corrupt.json").write_text(
            "{invalid json!!!", encoding="utf-8",
        )
        gw._load_claim_snapshots_from_disk()
        assert "sess-good" in gw._claim_snapshots
        assert "sess-corrupt" not in gw._claim_snapshots

    def test_load_from_empty_dir_is_safe(self, tmp_path):
        """空快照目录加载安全（不抛异常）。"""
        gw = _make_minimal_gateway(tmp_path)
        gw._load_claim_snapshots_from_disk()  # 目录不存在
        assert gw._claim_snapshots == {}

    def test_snapshot_round_trip_preserves_dirty_baseline(self, tmp_path):
        """完整往返：save → load → 验证脏基线被保留（FOREIGN_CHANGE gate 可用）。"""
        gw1 = _make_minimal_gateway(tmp_path)
        dirty_baseline = "-old line\n+foreign modification"
        gw1._claim_snapshots["sess-rt"] = {"/abs/dirty.py": dirty_baseline}
        gw1._save_session_snapshot("sess-rt")

        gw2 = _make_minimal_gateway(tmp_path)
        gw2._load_claim_snapshots_from_disk()

        # 模拟 FOREIGN_CHANGE gate 读取快照
        snapshots = gw2._claim_snapshots.get("sess-rt", {})
        assert "/abs/dirty.py" in snapshots
        assert snapshots["/abs/dirty.py"] == dirty_baseline
        # 非空基线 → gate 会 BLOCK（搭便车检测生效）
        assert snapshots["/abs/dirty.py"] != ""
