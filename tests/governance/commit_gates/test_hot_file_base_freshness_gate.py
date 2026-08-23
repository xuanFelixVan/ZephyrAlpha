# [A_test] module_id: MOD-GATE_ENGINE | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.test_hot_file_base_freshness_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""test_hot_file_base_freshness_gate.py — 热文件 base 新鲜度门禁单测（HOT-FILE-BASE-FRESHNESS）

权威依据：hot_file_base_freshness_gate.py（make_hot_file_base_freshness_gate）
+ git_commit_gateway.py（claim_head 锚点生命周期：claim_files 捕获 / save/load 持久化 / release_files 清理）

测试组：
- TestGateSpecFields: gate_id / priority=47 字段正确
- TestAllowOverlapEscape: allow_overlap=True 逃生通道放行
- TestNoSessionIdPasses: 无 session_id → 放行
- TestNoClaimHeadPasses: session 无锚点（未走 claim_files）→ 放行且不调 git
- TestHeadUnchangedPasses: HEAD==claim_head（无上游推进）→ 放行
- TestUpstreamUntouchedPasses: HEAD 已推进但热文件未被上游改动 → 放行
- TestStaleBaseBlocked: 热文件在 claim_head..HEAD 被上游改动 → 阻断（含处置指引）
- TestNonHotFileSkipped: 非热文件即使上游改动也不检查 → 放行
- TestMixedTargets: 混合目标只查热文件
- TestGitErrorFailOpen: rev-parse/diff 失败或异常 → 放行（fail-open）
- TestClaimHeadsReadExceptionSafe: claim_heads 读取异常 → 安全降级放行
- TestClaimHeadLifecycle: gateway 侧锚点生命周期（claim 捕获幂等/持久化/崩溃恢复/release 清理/旧格式兼容）
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import MagicMock

from zephyr.gov_enforcement.commit_gates.hot_file_base_freshness_gate import (
    make_hot_file_base_freshness_gate,
)
from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import GitCommitGateway

_CLAIM_HEAD = "a" * 40  # claim 时锚定的 HEAD sha
_CURRENT_HEAD = "b" * 40  # commit 时当前 HEAD sha（上游已推进）


def _make_run_git(
    head_sha: str = _CURRENT_HEAD,
    head_rc: int = 0,
    diff_touched: frozenset[str] = frozenset(),
    diff_rc: int = 0,
    raise_exc: Exception | None = None,
):
    """构造 run_git 分发器：rev-parse 返回 head_sha，diff 按 diff_touched 报告改动文件。"""

    def _run_git(cmd: list[str], cwd: str | None = None) -> MagicMock:
        if raise_exc is not None:
            raise raise_exc
        result = MagicMock()
        if cmd[1] == "rev-parse":
            result.returncode = head_rc
            result.stdout = head_sha
        elif cmd[1] == "diff":
            result.returncode = diff_rc
            rel = cmd[-1]
            result.stdout = f"{rel}\n" if rel in diff_touched else ""
        else:
            result.returncode = 0
            result.stdout = ""
        return result

    return _run_git


def _make_gateway(
    project_root: Path,
    claim_head: str = _CLAIM_HEAD,
    session_snapshots_raise: Exception | None = None,
    **run_git_kwargs,
) -> MagicMock:
    """构造 mock gateway：claim_heads.get 返回 claim_head，run_git 由 _make_run_git 分发。

    Args:
        project_root: 项目根目录。
        claim_head: session 的 claim_head 锚点（空串=无锚点）。
        session_snapshots_raise: 若非 None，claim_heads.get 抛此异常（测试安全降级）。
        run_git_kwargs: 透传 _make_run_git（head_sha/head_rc/diff_touched/diff_rc/raise_exc）。
    """
    gw = MagicMock()
    gw.project_root = project_root
    if session_snapshots_raise is not None:
        gw.claim_heads.get.side_effect = session_snapshots_raise
    else:
        gw.claim_heads.get.return_value = claim_head
    gw.run_git.side_effect = _make_run_git(**run_git_kwargs)
    return gw


class TestGateSpecFields:
    """gate_id / priority 字段正确。"""

    def test_gate_id_and_priority(self):
        spec = make_hot_file_base_freshness_gate()
        assert spec.gate_id == "HOT-FILE-BASE-FRESHNESS"
        assert spec.priority == 47


class TestAllowOverlapEscape:
    """allow_overlap=True 逃生通道放行（即使 base 确已陈旧）。"""

    def test_allow_overlap_passes(self, tmp_path):
        gw = _make_gateway(tmp_path, diff_touched=frozenset({"AGENTS.md"}))
        gate = make_hot_file_base_freshness_gate()
        target = tmp_path / "AGENTS.md"
        passed, detail = gate.check(
            gw,
            [str(target)],
            session_id="s1",
            allow_overlap=True,
        )
        assert passed is True
        assert detail == ""


class TestNoSessionIdPasses:
    """无 session_id → 放行（CLAIM-REQUIRED 职责，本 gate 不阻断）。"""

    def test_no_session_id_passes(self, tmp_path):
        gw = _make_gateway(tmp_path, diff_touched=frozenset({"AGENTS.md"}))
        gate = make_hot_file_base_freshness_gate()
        target = tmp_path / "AGENTS.md"
        passed, _ = gate.check(gw, [str(target)], session_id="", allow_overlap=False)
        assert passed is True


class TestNoClaimHeadPasses:
    """session 无 claim_head 锚点（reconciler auto-commit 等未走 claim_files 路径）→ 放行。"""

    def test_no_claim_head_passes_and_skips_git(self, tmp_path):
        gw = _make_gateway(tmp_path, claim_head="", diff_touched=frozenset({"AGENTS.md"}))
        gate = make_hot_file_base_freshness_gate()
        target = tmp_path / "AGENTS.md"
        passed, detail = gate.check(
            gw,
            [str(target)],
            session_id="s1",
            allow_overlap=False,
        )
        assert passed is True
        assert detail == ""
        gw.run_git.assert_not_called()  # 无锚点短路，不应产生 git 调用开销


class TestHeadUnchangedPasses:
    """当前 HEAD == claim_head（无上游推进）→ 放行。"""

    def test_head_unchanged_passes(self, tmp_path):
        gw = _make_gateway(tmp_path, head_sha=_CLAIM_HEAD, diff_touched=frozenset({"AGENTS.md"}))
        gate = make_hot_file_base_freshness_gate()
        target = tmp_path / "AGENTS.md"
        passed, _ = gate.check(gw, [str(target)], session_id="s1", allow_overlap=False)
        assert passed is True


class TestUpstreamUntouchedPasses:
    """HEAD 已推进但目标热文件在 claim_head..HEAD 区间未被上游改动 → 放行。"""

    def test_upstream_moved_but_file_untouched_passes(self, tmp_path):
        gw = _make_gateway(tmp_path, diff_touched=frozenset())  # diff 空
        gate = make_hot_file_base_freshness_gate()
        target = tmp_path / "AGENTS.md"
        passed, detail = gate.check(gw, [str(target)], session_id="s1", allow_overlap=False)
        assert passed is True
        assert detail == ""


class TestStaleBaseBlocked:
    """热文件在 claim_head..HEAD 区间被上游改动 → 阻断（STALE_BASE_VIOLATION）。"""

    def test_stale_base_blocked(self, tmp_path):
        gw = _make_gateway(tmp_path, diff_touched=frozenset({"AGENTS.md"}))
        gate = make_hot_file_base_freshness_gate()
        target = tmp_path / "AGENTS.md"
        passed, detail = gate.check(gw, [str(target)], session_id="s1", allow_overlap=False)
        assert passed is False
        assert "STALE_BASE_VIOLATION" in detail
        assert "AGENTS.md" in detail
        # detail 含处置指引 + 双 sha 短号（MSG-EXPOSURE 合规：不含 session_id）
        assert "release_files" in detail
        assert "aaaa" in detail and "bbbb" in detail
        assert "s1" not in detail

    def test_multiple_stale_files_all_listed(self, tmp_path):
        """多个热文件同时陈旧 → 全部列出。"""
        touched = frozenset(
            {
                "AGENTS.md",
                "docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml",
            }
        )
        gw = _make_gateway(tmp_path, diff_touched=touched)
        gate = make_hot_file_base_freshness_gate()
        targets = [str(tmp_path / rel) for rel in touched]
        passed, detail = gate.check(gw, targets, session_id="s1", allow_overlap=False)
        assert passed is False
        assert "AGENTS.md" in detail
        assert "candidate_module_registry.yaml" in detail


class TestNonHotFileSkipped:
    """非热文件不做 base 新鲜度检查（上游改动也放行——CAS/其他 gate 职责）。"""

    def test_non_hot_file_passes(self, tmp_path):
        gw = _make_gateway(tmp_path, diff_touched=frozenset({"src/zephyr/foo.py"}))
        gate = make_hot_file_base_freshness_gate()
        target = tmp_path / "src" / "zephyr" / "foo.py"
        passed, detail = gate.check(gw, [str(target)], session_id="s1", allow_overlap=False)
        assert passed is True
        assert detail == ""
        # 非热文件在 is_hot_file 判定后即跳过，不应产生 diff 调用
        diff_calls = [c for c in gw.run_git.call_args_list if c.args[0][1] == "diff"]
        assert diff_calls == []


class TestMixedTargets:
    """混合 commit 目标：只查热文件，阻断清单仅含陈旧热文件。"""

    def test_mixed_only_hot_checked(self, tmp_path):
        hot_rel = "AGENTS.md"
        cold_rel = "src/zephyr/foo.py"
        # 上游只改了非热文件 → 放行
        gw = _make_gateway(tmp_path, diff_touched=frozenset({cold_rel}))
        gate = make_hot_file_base_freshness_gate()
        targets = [str(tmp_path / hot_rel), str(tmp_path / "src" / "zephyr" / "foo.py")]
        passed, _ = gate.check(gw, targets, session_id="s1", allow_overlap=False)
        assert passed is True

        # 上游同时改了热文件与非热文件 → 阻断且仅列热文件
        gw2 = _make_gateway(tmp_path, diff_touched=frozenset({hot_rel, cold_rel}))
        passed2, detail2 = gate.check(gw2, targets, session_id="s1", allow_overlap=False)
        assert passed2 is False
        assert "AGENTS.md" in detail2
        assert "foo.py" not in detail2


class TestGitErrorFailOpen:
    """git 异常/失败 → fail-open 放行（环境异常非违规）。"""

    def test_rev_parse_failure_passes(self, tmp_path):
        gw = _make_gateway(tmp_path, head_rc=128, head_sha="")
        gate = make_hot_file_base_freshness_gate()
        target = tmp_path / "AGENTS.md"
        passed, _ = gate.check(gw, [str(target)], session_id="s1", allow_overlap=False)
        assert passed is True

    def test_diff_failure_passes(self, tmp_path):
        gw = _make_gateway(tmp_path, diff_rc=1, diff_touched=frozenset({"AGENTS.md"}))
        gate = make_hot_file_base_freshness_gate()
        target = tmp_path / "AGENTS.md"
        passed, _ = gate.check(gw, [str(target)], session_id="s1", allow_overlap=False)
        assert passed is True

    def test_run_git_exception_passes(self, tmp_path):
        gw = _make_gateway(tmp_path, raise_exc=RuntimeError("git exploded"))
        gate = make_hot_file_base_freshness_gate()
        target = tmp_path / "AGENTS.md"
        passed, _ = gate.check(gw, [str(target)], session_id="s1", allow_overlap=False)
        assert passed is True


class TestClaimHeadsReadExceptionSafe:
    """claim_heads 读取异常 → 安全降级为无锚点（放行，不阻断 commit）。"""

    def test_claim_heads_exception_passes(self, tmp_path):
        gw = _make_gateway(tmp_path, session_snapshots_raise=RuntimeError("dict corrupt"))
        gate = make_hot_file_base_freshness_gate()
        target = tmp_path / "AGENTS.md"
        passed, _ = gate.check(gw, [str(target)], session_id="s1", allow_overlap=False)
        assert passed is True


# ---------------------------------------------------------------------------
# gateway 侧 claim_head 锚点生命周期（__new__ 轻量构造，对标 TestSnapshotDiskPersistence）
# ---------------------------------------------------------------------------


def _make_minimal_gateway(project_root: Path, head_sha: str = _CLAIM_HEAD) -> GitCommitGateway:
    """构造最小化 GitCommitGateway（__new__ 绕过重量级 __init__），run_git 返回固定 HEAD。"""
    gw = GitCommitGateway.__new__(GitCommitGateway)
    gw.project_root = project_root
    gw.claim_snapshots = {}
    gw.claim_snapshots_dir = project_root / ".runtime" / "claim_snapshots"
    gw.registry = MagicMock()
    gw.registry.claim_file.return_value = True
    gw.capture_baseline_diff = lambda abs_f: ""
    gw.run_git = _make_run_git(head_sha=head_sha)
    return gw


class TestClaimHeadLifecycle:
    """claim_head 锚点生命周期：claim 捕获（幂等）→ 磁盘持久化 → 崩溃恢复 → release 清理。"""

    def test_claim_files_captures_head_once(self, tmp_path):
        """首次 claim 锚定 HEAD；幂等重跑不覆盖首次锚点（与基线快照语义一致）。"""
        target = tmp_path / "a.py"
        target.touch()
        gw = _make_minimal_gateway(tmp_path, head_sha=_CLAIM_HEAD)
        gw.claim_files("s1", [str(target)])
        assert gw.claim_heads["s1"] == _CLAIM_HEAD

        # 模拟上游推进后重跑 claim（幂等）——锚点保留首次值
        gw.run_git = _make_run_git(head_sha=_CURRENT_HEAD)
        gw.claim_files("s1", [str(target)])
        assert gw.claim_heads["s1"] == _CLAIM_HEAD, "幂等重跑不得覆盖首次 HEAD 锚点"

    def test_claim_head_persisted_with_snapshot(self, tmp_path):
        """save_session_snapshot 负载含 claim_head 字段。"""
        gw = _make_minimal_gateway(tmp_path)
        gw.claim_snapshots["s1"] = {}
        gw.claim_heads["s1"] = _CLAIM_HEAD
        gw.save_session_snapshot("s1")
        data = json.loads((gw.claim_snapshots_dir / "s1.json").read_text(encoding="utf-8"))
        assert data["claim_head"] == _CLAIM_HEAD

    def test_load_recovers_claim_head(self, tmp_path):
        """崩溃恢复：新 gateway 实例从磁盘恢复 claim_head。"""
        gw1 = _make_minimal_gateway(tmp_path)
        gw1.claim_snapshots["s-crash"] = {}
        gw1.claim_heads["s-crash"] = _CLAIM_HEAD
        gw1.save_session_snapshot("s-crash")

        gw2 = _make_minimal_gateway(tmp_path)
        gw2.load_claim_snapshots_from_disk()
        assert gw2.claim_heads["s-crash"] == _CLAIM_HEAD

    def test_load_legacy_snapshot_without_claim_head(self, tmp_path):
        """旧格式快照（无 claim_head 字段）→ 正常加载快照，锚点缺省不报错。"""
        gw1 = _make_minimal_gateway(tmp_path)
        gw1.claim_snapshots_dir.mkdir(parents=True, exist_ok=True)
        legacy = {"session_id": "s-legacy", "snapshots": {"/abs/x.py": "diff"}}
        (gw1.claim_snapshots_dir / "s-legacy.json").write_text(
            json.dumps(legacy), encoding="utf-8"
        )
        gw2 = _make_minimal_gateway(tmp_path)
        gw2.load_claim_snapshots_from_disk()
        assert gw2.claim_snapshots["s-legacy"]["/abs/x.py"] == "diff"
        assert "s-legacy" not in gw2.claim_heads

    def test_release_files_clears_claim_head(self, tmp_path):
        """release_files 清理锚点（与快照同生命周期）——重 claim 刷新到新 HEAD。"""
        target = tmp_path / "b.py"
        target.touch()
        gw = _make_minimal_gateway(tmp_path, head_sha=_CLAIM_HEAD)
        gw.claim_files("s1", [str(target)])
        assert "s1" in gw.claim_heads

        gw.release_files("s1", [str(target)])
        assert "s1" not in gw.claim_heads

        # 上游推进后重新 claim → 锚点刷新为新 HEAD
        gw.run_git = _make_run_git(head_sha=_CURRENT_HEAD)
        gw.claim_files("s1", [str(target)])
        assert gw.claim_heads["s1"] == _CURRENT_HEAD

    def test_claim_head_git_failure_not_recorded(self, tmp_path):
        """rev-parse 失败（非 git 目录等）→ 不记锚点（gate fail-open 等效），claim 本身不受影响。"""
        target = tmp_path / "c.py"
        target.touch()
        gw = _make_minimal_gateway(tmp_path)
        gw.run_git = _make_run_git(head_rc=128, head_sha="")
        claimed = gw.claim_files("s1", [str(target)])
        assert claimed == [str(target)], "git 异常不得影响 claim 主流程"
        assert gw.claim_heads.get("s1", "") == ""
