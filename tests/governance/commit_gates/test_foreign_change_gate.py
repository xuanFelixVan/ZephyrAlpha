# [A_test] module_id: MOD-GOV_foreign_change_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.test_foreign_change_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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
- TestAdoptPriorWork: 治本(2026-07-23)——claim_files(adopt_prior_work=True) 认领跨 session 前序工作（空基线+审计）
- TestIdempotentClaimPreservesBaseline: tracker #92 治本（2026-08-16）——幂等重跑保留首次基线（干净/脏/adopt 三态+release 生命周期）
- TestPostClaimAuditNormalSelfEditSkipped: P1——正常自编辑不记审计（噪音过滤）
- TestPostClaimAuditDirtyBaselineChanged: P1——基线非空+变化→记审计（gate同时阻断）
- TestPostClaimAuditAdoptedChanged: P1——adopted文件+变化→记审计
- TestPostClaimAuditNoChange: P1——无变化不记审计
- TestPostClaimAuditFailOpen: P1——审计失败不阻断commit
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import MagicMock

from zephyr.gov_enforcement.commit_gates.foreign_change_gate import (
    make_foreign_change_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec
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
        gw.claim_snapshots.get.side_effect = raise_exc
    else:
        gw.claim_snapshots.get.return_value = session_snapshots or {}
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
    gw.claim_snapshots = {}
    gw.claim_snapshots_dir = project_root / ".runtime" / "claim_snapshots"
    return gw


class TestSnapshotDiskPersistence:
    """S3-C: claim 快照磁盘持久化——_save/_load/_delete helper 测试。"""

    def test_save_session_snapshot_writes_json(self, tmp_path):
        """_save_session_snapshot 将快照写入 .runtime/claim_snapshots/{session_id}.json。"""
        gw = _make_minimal_gateway(tmp_path)
        gw.claim_snapshots["sess-test"] = {"/abs/file.py": "diff content"}
        gw.save_session_snapshot("sess-test")
        snap_file = gw.claim_snapshots_dir / "sess-test.json"
        assert snap_file.exists(), "快照文件未创建"
        data = json.loads(snap_file.read_text(encoding="utf-8"))
        assert data["session_id"] == "sess-test"
        assert data["snapshots"]["/abs/file.py"] == "diff content"

    def test_load_claim_snapshots_from_disk_recovers(self, tmp_path):
        """新 gateway __init__ 从磁盘恢复快照（崩溃恢复核心场景）。"""
        # 第一个 gateway 写入快照
        gw1 = _make_minimal_gateway(tmp_path)
        gw1.claim_snapshots["sess-crash"] = {"/abs/a.py": "baseline diff"}
        gw1.save_session_snapshot("sess-crash")
        # 模拟进程崩溃：新 gateway 实例从磁盘加载
        gw2 = _make_minimal_gateway(tmp_path)
        gw2.load_claim_snapshots_from_disk()
        assert "sess-crash" in gw2.claim_snapshots
        assert gw2.claim_snapshots["sess-crash"]["/abs/a.py"] == "baseline diff"

    def test_delete_session_snapshot_removes_file(self, tmp_path):
        """_delete_session_snapshot 删除磁盘快照文件。"""
        gw = _make_minimal_gateway(tmp_path)
        gw.claim_snapshots["sess-del"] = {"/abs/x.py": "diff"}
        gw.save_session_snapshot("sess-del")
        snap_file = gw.claim_snapshots_dir / "sess-del.json"
        assert snap_file.exists()
        gw.delete_session_snapshot("sess-del")
        assert not snap_file.exists(), "快照文件未删除"

    def test_delete_nonexistent_snapshot_is_silent(self, tmp_path):
        """_delete_session_snapshot 对不存在的文件静默（不抛异常）。"""
        gw = _make_minimal_gateway(tmp_path)
        # 不应抛异常
        gw.delete_session_snapshot("sess-ghost")

    def test_load_skips_corrupt_snapshot_file(self, tmp_path):
        """损坏的 JSON 文件被跳过（不崩溃，log warning）。"""
        gw = _make_minimal_gateway(tmp_path)
        gw.claim_snapshots_dir.mkdir(parents=True, exist_ok=True)
        # 写入正常快照
        (gw.claim_snapshots_dir / "sess-good.json").write_text(
            json.dumps({"session_id": "sess-good", "snapshots": {"/a": "diff"}}),
            encoding="utf-8",
        )
        # 写入损坏快照
        (gw.claim_snapshots_dir / "sess-corrupt.json").write_text(
            "{invalid json!!!", encoding="utf-8",
        )
        gw.load_claim_snapshots_from_disk()
        assert "sess-good" in gw.claim_snapshots
        assert "sess-corrupt" not in gw.claim_snapshots

    def test_load_from_empty_dir_is_safe(self, tmp_path):
        """空快照目录加载安全（不抛异常）。"""
        gw = _make_minimal_gateway(tmp_path)
        gw.load_claim_snapshots_from_disk()  # 目录不存在
        assert gw.claim_snapshots == {}

    def test_snapshot_round_trip_preserves_dirty_baseline(self, tmp_path):
        """完整往返：save → load → 验证脏基线被保留（FOREIGN_CHANGE gate 可用）。"""
        gw1 = _make_minimal_gateway(tmp_path)
        dirty_baseline = "-old line\n+foreign modification"
        gw1.claim_snapshots["sess-rt"] = {"/abs/dirty.py": dirty_baseline}
        gw1.save_session_snapshot("sess-rt")

        gw2 = _make_minimal_gateway(tmp_path)
        gw2.load_claim_snapshots_from_disk()

        # 模拟 FOREIGN_CHANGE gate 读取快照
        snapshots = gw2.claim_snapshots.get("sess-rt", {})
        assert "/abs/dirty.py" in snapshots
        assert snapshots["/abs/dirty.py"] == dirty_baseline
        # 非空基线 → gate 会 BLOCK（搭便车检测生效）
        assert snapshots["/abs/dirty.py"] != ""


class TestAdoptPriorWork:
    """治本(2026-07-23): claim_files(adopt_prior_work=True) 认领跨 session 前序工作。

    adopt 对有实际 diff 的文件记录审计日志但存储空基线，使 FOREIGN-CHANGE gate 放行。
    与 allow_overlap 逃生通道互补——adopt 在 claim 时认领附审计，allow_overlap 在
    commit 时绕 gate。
    """

    def _make_claimable_gateway(
        self, project_root: Path, baseline_map: dict[str, str]
    ) -> GitCommitGateway:
        """构造可 claim 的 gateway：_registry.claim_file 返回 True，
        _capture_baseline_diff 按 baseline_map 返回基线（绕过真实 git diff）。"""
        gw = GitCommitGateway.__new__(GitCommitGateway)
        gw.project_root = project_root
        gw.claim_snapshots = {}
        gw.claim_snapshots_dir = project_root / ".runtime" / "claim_snapshots"
        gw.registry = MagicMock()
        gw.registry.claim_file.return_value = True
        gw.capture_baseline_diff = lambda abs_f: baseline_map.get(abs_f, "")
        return gw

    def test_adopt_resets_dirty_baseline_to_empty(self, tmp_path):
        """adopt_prior_work=True 对 dirty 文件 → 快照存空基线 → gate PASS。"""
        target = tmp_path / "a.py"
        target.touch()
        abs_target = os.path.abspath(str(target))
        gw = self._make_claimable_gateway(tmp_path, {abs_target: "-old\n+new dirty"})
        gw.claim_files("s1", [str(target)], adopt_prior_work=True)
        # 快照应为空基线（adopt 认领后）
        assert gw.claim_snapshots["s1"][abs_target] == ""
        # gate 检查：空基线 → PASS
        gate = make_foreign_change_gate()
        gw_mock = _make_gateway(tmp_path, session_snapshots={abs_target: ""})
        passed, detail = gate.check(
            gw_mock, [str(target)], session_id="s1", allow_overlap=False,
        )
        assert passed is True
        assert detail == ""

    def test_adopt_writes_audit_log(self, tmp_path):
        """adopt 后审计日志 {sid}_adopted.jsonl 含 diff_size/diff_sha256。"""
        target = tmp_path / "a.py"
        target.touch()
        abs_target = os.path.abspath(str(target))
        gw = self._make_claimable_gateway(tmp_path, {abs_target: "-old\n+new dirty work"})
        gw.claim_files("s1", [str(target)], adopt_prior_work=True)
        audit_file = gw.claim_snapshots_dir / "s1_adopted.jsonl"
        assert audit_file.exists(), "adopt 审计日志未创建"
        records = [
            json.loads(line)
            for line in audit_file.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        assert len(records) == 1
        assert records[0]["file"] == abs_target
        assert records[0]["diff_size"] > 0
        assert "diff_sha256" in records[0]
        assert len(records[0]["diff_sha256"]) == 16
        # P2：domain 字段存在（空文件无 [DOMAIN] 头 → UNKNOWN）
        assert records[0]["domain"] == "UNKNOWN"

    def test_adopt_audit_includes_domain(self, tmp_path):
        """P2：adopt 审计记录含 domain 字段（从文件 [DOMAIN] 头部读取）。"""
        target = tmp_path / "a.py"
        # 写入 [DOMAIN] 头部
        target.write_text("# [DOMAIN] D_REGIME\n# [MODULE] test\nx = 1\n", encoding="utf-8")
        abs_target = os.path.abspath(str(target))
        gw = self._make_claimable_gateway(tmp_path, {abs_target: "-old\n+new dirty work"})
        gw.claim_files("s1", [str(target)], adopt_prior_work=True)
        audit_file = gw.claim_snapshots_dir / "s1_adopted.jsonl"
        records = [
            json.loads(line)
            for line in audit_file.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        assert len(records) == 1
        assert records[0]["domain"] == "D_REGIME"

    def test_adopt_clean_file_no_audit(self, tmp_path):
        """clean 文件（actual_baseline 空）adopt → 不写审计（无前序工作可认领）。"""
        target = tmp_path / "a.py"
        target.touch()
        abs_target = os.path.abspath(str(target))
        gw = self._make_claimable_gateway(tmp_path, {abs_target: ""})  # clean
        gw.claim_files("s1", [str(target)], adopt_prior_work=True)
        audit_file = gw.claim_snapshots_dir / "s1_adopted.jsonl"
        assert not audit_file.exists(), "clean 文件不应写 adopt 审计"
        # 快照仍为空基线（clean 文件本就是空）
        assert gw.claim_snapshots["s1"][abs_target] == ""

    def test_adopt_default_false_unchanged(self, tmp_path):
        """adopt_prior_work=False（默认）→ dirty 基线保留 → gate BLOCK（行为不变）。"""
        target = tmp_path / "a.py"
        target.touch()
        abs_target = os.path.abspath(str(target))
        dirty = "-old\n+new dirty"
        gw = self._make_claimable_gateway(tmp_path, {abs_target: dirty})
        gw.claim_files("s1", [str(target)])  # 默认 adopt_prior_work=False
        # 快照保留 dirty 基线（未认领）
        assert gw.claim_snapshots["s1"][abs_target] == dirty
        # gate 检查：dirty 基线 → BLOCK
        gate = make_foreign_change_gate()
        gw_mock = _make_gateway(tmp_path, session_snapshots={abs_target: dirty})
        passed, detail = gate.check(
            gw_mock, [str(target)], session_id="s1", allow_overlap=False,
        )
        assert passed is False
        assert "FOREIGN_CHANGE_VIOLATION" in detail
        # 无 adopt 审计日志
        audit_file = gw.claim_snapshots_dir / "s1_adopted.jsonl"
        assert not audit_file.exists()


class TestIdempotentClaimPreservesBaseline:
    """tracker #92 治本（2026-08-16）：幂等重跑 claim_files 保留首次基线不重捕获。

    根因复现实证：CLI commit 主流程自带 adopt_prior_work=False 的 claim_files 重跑，
    重捕获把 adopt 的空基线/首次干净基线覆盖为 commit 时刻真基线，破坏
    「基线=首次 claim 时刻」语义（ARCH-054）→ FOREIGN-CHANGE 重复拦截。
    修复后语义：基线=首次 claim 时刻快照；release 后快照删除，重新 claim 重新捕获。
    """

    @staticmethod
    def _make_gw(project_root: Path, baseline_map: dict[str, str]) -> GitCommitGateway:
        """构造可 claim 的 gateway（baseline_map 引用捕获——测试中途改值即改变 capture 返回）。"""
        gw = GitCommitGateway.__new__(GitCommitGateway)
        gw.project_root = project_root
        gw.claim_snapshots = {}
        gw.claim_snapshots_dir = project_root / ".runtime" / "claim_snapshots"
        gw.registry = MagicMock()
        gw.registry.claim_file.return_value = True
        gw.capture_baseline_diff = lambda abs_f: baseline_map.get(abs_f, "")
        return gw

    def test_reclaim_preserves_clean_baseline(self, tmp_path):
        """首次干净 claim（基线空）→ 后续编辑 → 重 claim 不重捕获 → 基线仍空 → gate PASS。"""
        target = tmp_path / "a.py"
        target.touch()
        abs_target = os.path.abspath(str(target))
        baseline_map = {abs_target: ""}  # 首次 claim 时干净
        gw = self._make_gw(tmp_path, baseline_map)
        gw.claim_files("s1", [str(target)])
        assert gw.claim_snapshots["s1"][abs_target] == ""
        # 模拟 claim 后本 session 自己编辑（文件变脏）
        baseline_map[abs_target] = "-old\n+my own edit"
        # CLI commit 主流程重跑 claim_files（无 adopt）
        gw.claim_files("s1", [str(target)])
        # 基线保留首次干净态——不被覆盖为脏
        assert gw.claim_snapshots["s1"][abs_target] == ""
        gate = make_foreign_change_gate()
        gw_mock = _make_gateway(tmp_path, session_snapshots={abs_target: ""})
        passed, _ = gate.check(gw_mock, [str(target)], session_id="s1", allow_overlap=False)
        assert passed is True

    def test_reclaim_preserves_dirty_baseline(self, tmp_path):
        """首次脏 claim（基线真）→ 重 claim 不重捕获 → 基线仍真 → gate 仍 BLOCK（不削弱防护）。"""
        target = tmp_path / "a.py"
        target.touch()
        abs_target = os.path.abspath(str(target))
        dirty = "-old\n+foreign wip"
        baseline_map = {abs_target: dirty}
        gw = self._make_gw(tmp_path, baseline_map)
        gw.claim_files("s1", [str(target)])
        assert gw.claim_snapshots["s1"][abs_target] == dirty
        # 重跑 claim（即使此刻 capture 返回空也不覆盖既有真基线）
        baseline_map[abs_target] = ""
        gw.claim_files("s1", [str(target)])
        assert gw.claim_snapshots["s1"][abs_target] == dirty
        gate = make_foreign_change_gate()
        gw_mock = _make_gateway(tmp_path, session_snapshots={abs_target: dirty})
        passed, detail = gate.check(gw_mock, [str(target)], session_id="s1", allow_overlap=False)
        assert passed is False
        assert "FOREIGN_CHANGE_VIOLATION" in detail

    def test_adopt_then_bare_reclaim_keeps_empty_baseline(self, tmp_path):
        """#92 核心回归：adopt 认领（空基线+审计）→ 裸重 claim（无 adopt）→ 空基线不被冲掉。"""
        target = tmp_path / "a.py"
        target.touch()
        abs_target = os.path.abspath(str(target))
        baseline_map = {abs_target: "-old\n+prior session wip"}
        gw = self._make_gw(tmp_path, baseline_map)
        # adopt 认领前序 WIP：空基线 + 审计
        gw.claim_files("s1", [str(target)], adopt_prior_work=True)
        assert gw.claim_snapshots["s1"][abs_target] == ""
        assert (gw.claim_snapshots_dir / "s1_adopted.jsonl").exists()
        # CLI commit 主流程重跑 claim_files（adopt=False）——修复前此处覆盖回真基线
        gw.claim_files("s1", [str(target)])
        assert gw.claim_snapshots["s1"][abs_target] == ""
        gate = make_foreign_change_gate()
        gw_mock = _make_gateway(tmp_path, session_snapshots={abs_target: ""})
        passed, _ = gate.check(gw_mock, [str(target)], session_id="s1", allow_overlap=False)
        assert passed is True
        # adopt 审计不因重跑重复记录
        records = [
            line for line in (gw.claim_snapshots_dir / "s1_adopted.jsonl")
            .read_text(encoding="utf-8").splitlines() if line.strip()
        ]
        assert len(records) == 1

    def test_release_then_reclaim_recaptures(self, tmp_path):
        """release 删快照 → 重新 claim 重新捕获（生命周期正确：基线锚定新一轮首次 claim）。"""
        target = tmp_path / "a.py"
        target.touch()
        abs_target = os.path.abspath(str(target))
        baseline_map = {abs_target: ""}
        gw = self._make_gw(tmp_path, baseline_map)
        gw.claim_files("s1", [str(target)])
        assert gw.claim_snapshots["s1"][abs_target] == ""
        # release 后快照删除
        gw.release_files("s1", [str(target)])
        assert "s1" not in gw.claim_snapshots
        # 重新 claim：文件已脏 → 重新捕获真基线
        baseline_map[abs_target] = "-old\n+new foreign wip"
        gw.claim_files("s1", [str(target)])
        assert gw.claim_snapshots["s1"][abs_target] == "-old\n+new foreign wip"


# ---------------------------------------------------------------------------
# P1（13a5e1d512 治本补强）：post-claim 修改审计测试
# ---------------------------------------------------------------------------

def _make_audit_gateway(
    project_root: Path,
    session_snapshots: dict[str, str] | None = None,
    capture_map: dict[str, str] | None = None,
    adopted_records: list[dict] | None = None,
) -> MagicMock:
    """构造 mock gateway，支持 post-claim 审计测试。

    Args:
        project_root: 项目根目录（真实 Path，审计日志写入此目录下）。
        session_snapshots: per-session 快照 {abs_path: baseline}。
        capture_map: capture_baseline_diff 返回值映射 {abs_path: current_diff}。
            未命中的文件返回空串（模拟干净文件）。
        adopted_records: 写入 {sid}_adopted.jsonl 的记录列表（模拟 adopt_prior_work）。
    """
    gw = MagicMock()
    gw.project_root = project_root
    gw.claim_snapshots.get.return_value = session_snapshots or {}
    gw.claim_snapshots_dir = project_root / ".runtime" / "claim_snapshots"
    capture_map = capture_map or {}

    def _capture(abs_f):
        return capture_map.get(abs_f, "")

    gw.capture_baseline_diff = _capture

    # 写入 adopted 日志（模拟 adopt_prior_work 的审计记录）
    if adopted_records:
        gw.claim_snapshots_dir.mkdir(parents=True, exist_ok=True)
        adopted_file = gw.claim_snapshots_dir / "s1_adopted.jsonl"
        with adopted_file.open("w", encoding="utf-8") as fh:
            for rec in adopted_records:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    return gw


def _read_audit_log(project_root: Path) -> list[dict]:
    """读取 post_claim_modifications.jsonl 审计日志。"""
    audit_path = project_root / ".runtime" / "gate_audit" / "post_claim_modifications.jsonl"
    if not audit_path.is_file():
        return []
    return [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class TestPostClaimAuditNormalSelfEditSkipped:
    """正常自编辑（空基线+非adopted+当前有diff）→ 不记审计（噪音过滤）。"""

    def test_self_edit_not_audited(self, tmp_path):
        """session claim 干净文件后自己编辑 → 审计跳过（baseline空+current非空=自编辑）。"""
        target = tmp_path / "a.py"
        target.touch()
        abs_target = os.path.abspath(str(target))
        gw = _make_audit_gateway(
            tmp_path,
            session_snapshots={abs_target: ""},  # 干净 claim
            capture_map={abs_target: "+my own edit\n-new line"},  # session 自己编辑
        )
        gate = make_foreign_change_gate()
        gate.check(gw, [str(target)], session_id="s1", allow_overlap=False)
        records = _read_audit_log(tmp_path)
        assert records == [], "正常自编辑不应记审计"


class TestPostClaimAuditDirtyBaselineChanged:
    """基线非空 + 当前≠基线 → 记审计（可疑：claim 时已脏且继续变）。"""

    def test_dirty_baseline_change_audited(self, tmp_path):
        """基线非空（claim 时脏）+ 当前 diff 变化 → 审计记录（gate 同时阻断）。"""
        target = tmp_path / "a.py"
        target.touch()
        abs_target = os.path.abspath(str(target))
        gw = _make_audit_gateway(
            tmp_path,
            session_snapshots={abs_target: "-old\n+foreign"},  # claim 时脏
            capture_map={abs_target: "-old\n+foreign\n+more changes"},  # commit 时变了
        )
        gate = make_foreign_change_gate()
        passed, detail = gate.check(
            gw, [str(target)], session_id="s1", allow_overlap=False,
        )
        assert passed is False  # gate 阻断（基线非空）
        records = _read_audit_log(tmp_path)
        assert len(records) == 1, "基线非空+变化应记审计"
        assert records[0]["file"] == "a.py"
        assert records[0]["baseline_size"] > 0
        assert records[0]["current_size"] > records[0]["baseline_size"]
        assert records[0]["adopted"] is False
        assert records[0]["post_claim_change"] is True


class TestPostClaimAuditAdoptedChanged:
    """adopted 文件（空存储基线+adopted日志）+ 当前有diff → 记审计。"""

    def test_adopted_file_change_audited(self, tmp_path):
        """adopt_prior_work 认领的文件（空基线）+ commit 时有 diff → 审计记录。"""
        target = tmp_path / "a.py"
        target.touch()
        abs_target = os.path.abspath(str(target))
        gw = _make_audit_gateway(
            tmp_path,
            session_snapshots={abs_target: ""},  # adopt 清空了基线
            capture_map={abs_target: "+adopted work visible at commit"},  # commit 时有 diff
            adopted_records=[{  # adopt 审计日志
                "timestamp": 1700000000.0,
                "session_id": "s1",
                "file": abs_target,
                "diff_size": 50,
                "diff_sha256": "abc123def456abc7",
            }],
        )
        gate = make_foreign_change_gate()
        passed, detail = gate.check(
            gw, [str(target)], session_id="s1", allow_overlap=False,
        )
        assert passed is True  # 空基线 → gate 放行
        records = _read_audit_log(tmp_path)
        assert len(records) == 1, "adopted+变化应记审计"
        assert records[0]["adopted"] is True
        assert records[0]["baseline_size"] == 0  # 存储基线为空
        assert records[0]["current_size"] > 0


class TestPostClaimAuditNoChange:
    """当前==基线 → 不记审计（无 post-claim 变化）。"""

    def test_no_change_not_audited(self, tmp_path):
        """文件自 claim 后未变 → 审计跳过。"""
        target = tmp_path / "a.py"
        target.touch()
        abs_target = os.path.abspath(str(target))
        same_diff = "-old\n+unchanged"
        gw = _make_audit_gateway(
            tmp_path,
            session_snapshots={abs_target: same_diff},
            capture_map={abs_target: same_diff},  # 当前==基线
        )
        gate = make_foreign_change_gate()
        gate.check(gw, [str(target)], session_id="s1", allow_overlap=False)
        records = _read_audit_log(tmp_path)
        assert records == [], "无变化不应记审计"


class TestPostClaimAuditFailOpen:
    """审计写入失败不阻断 commit（fail-open）。"""

    def test_audit_failure_doesnt_block(self, tmp_path):
        """project_root 不可写 → 审计失败 → gate 仍正常阻断/放行。"""
        target = tmp_path / "a.py"
        target.touch()
        abs_target = os.path.abspath(str(target))
        # 构造 gateway：project_root 指向不可写路径触发审计失败
        gw = MagicMock()
        gw.project_root = tmp_path  # 正常路径（claim_snapshots 可读）
        gw.claim_snapshots.get.return_value = {abs_target: ""}
        gw.claim_snapshots_dir = tmp_path / ".runtime" / "claim_snapshots"
        # capture_baseline_diff 返回非 str → 审计跳过该文件（不崩溃）
        gw.capture_baseline_diff = lambda abs_f: 42  # int，非 str
        gate = make_foreign_change_gate()
        passed, detail = gate.check(
            gw, [str(target)], session_id="s1", allow_overlap=False,
        )
        assert passed is True  # 空基线 → 放行，审计异常不影响决策
