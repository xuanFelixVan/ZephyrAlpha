# [BLUEPRINT] MOD-GOV_GATE_ENGINE | tests/governance/test_precommit_channel_out_of_lock.py | D2
# [MODULE] tests.governance.test_precommit_channel_out_of_lock
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] pytest; zephyr.gov_enforcement.rule_bridge.git_commit_gateway
# [STARTUP] python -m pytest tests/governance/test_precommit_channel_out_of_lock.py
# [MATURITY] testing
# [INVARIANTS] D2 出锁手术红蓝钉（docs/_working/commit_chain_fullflow/11_channel_out_of_lock_surgery.md，
#   Owner 批 gate_survival_adjudication §8.8）：R-D2-a 通道执行时不得持有 _GlobalCommitLock；
#   R-D2-b 锁外绿+锁内 staged 指纹漂移→锁内重跑且重跑结果定案；矩阵1 指纹一致→采信锁外结果单趟
#   （adopted 落账）；矩阵2 锁外阻断文案逐字节透传且不重跑；矩阵7 HEAD 零变化守卫不白跑通道；
#   回退手柄 env ZEPHYR_PRECOMMIT_OUT_OF_LOCK=0 → 现行锁内全量。矩阵4（超时）/5（SKIP）由通道
#   本体零变更+既有通道套件承载，本文件不复制。全部 tmp_path 真 git 仓（测试隔离红线）。
# [MODIFY-GUARD] gate_id="TEST-PRECOMMIT-OUT-OF-LOCK"；新增用例 MUST 与被测行为同批修改
# [ERROR_CONTRACT] 断言失败正常报错；不触碰生产 .ailocks/.runtime（全部落在 tmp_path 下）
# [TESTS] tests/governance/test_precommit_channel_out_of_lock.py（自锚）
# [A_module] module_id=MOD-GOV_GATE_ENGINE | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""D2 出锁手术验收——pre-commit 通道锁外前移 + 锁内 staged 指纹复核。

红测两针（先红后修纪律）：
- R-D2-a：通道执行时全局锁文件不得存在（旧码 :3875 在 _commit_locked 内=锁内，必红）；
- R-D2-b：锁外通道绿 → 锁内 staged 漂移（add 前内容被改）→ 锁内重跑被触发且重跑结果定案
  （旧码无重跑语义，必红）。
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (
    CommitStatus,
    GitCommitGateway,
)

# ---------------------------------------------------------------------------
# 夹具：tmp 真 git 仓 + 门禁链静音（本单只验执行结构，不验门禁判据）
# ---------------------------------------------------------------------------


def _mk_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "pkg").mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)
    (repo / "pkg" / "base.py").write_text("VALUE = 1\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=repo, check=True)
    return repo


def _silence_gates(monkeypatch: pytest.MonkeyPatch) -> None:
    """门禁链整体静音：本单判据零变化，只验通道执行位置与指纹语义。"""
    monkeypatch.setattr(GitCommitGateway, "_check_gates_with_drift_watch", lambda self, *a, **k: [])


def _quiet_post_commit(monkeypatch: pytest.MonkeyPatch, gw: GitCommitGateway) -> None:
    """post-commit 对外面（reconciler 触发）静音，防测试触碰生产队列。"""
    monkeypatch.setattr(gw, "_run_post_commit_reconcile", lambda *a, **k: None)


def _read_anomaly_events(repo: Path) -> list[dict]:
    f = repo / ".runtime" / "audit" / "commit_block_events.jsonl"
    if not f.exists():
        return []
    return [json.loads(line) for line in f.read_text(encoding="utf-8").splitlines() if line.strip()]


# ---------------------------------------------------------------------------
# 红测两针（R-D2-a / R-D2-b）
# ---------------------------------------------------------------------------


class TestD2RedNeedles:
    def test_channel_runs_without_global_lock_held(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """R-D2-a：通道执行时不得持有 _GlobalCommitLock（旧码锁内执行，必红）。"""
        repo = _mk_repo(tmp_path)
        target = repo / "pkg" / "mod.py"
        target.write_text("X = 1\n", encoding="utf-8")
        gw = GitCommitGateway(project_root=str(repo))
        lock_path = repo / ".ailocks" / "git_commit_global.lock"
        seen: dict = {}

        def _spy(session_id, files):
            seen["lock_held"] = lock_path.exists()
            return None

        monkeypatch.setattr(gw, "_run_precommit_channel", _spy)
        _silence_gates(monkeypatch)
        _quiet_post_commit(monkeypatch, gw)

        res = gw.commit("t-d2", [str(target)], "test: d2 out-of-lock", allow_non_worktree=True)

        assert res.status == CommitStatus.OK
        assert seen.get("lock_held") is False, "通道必须在全局锁外执行（D2 R-D2-a）"

    def test_drift_triggers_in_lock_rerun_and_rerun_verdict_wins(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """R-D2-b：锁外绿 → 锁内 staged 漂移 → 重跑被触发且重跑阻断定案（旧码无重跑，必红）。"""
        repo = _mk_repo(tmp_path)
        target = repo / "pkg" / "mod.py"
        target.write_text("X = 1\n", encoding="utf-8")
        gw = GitCommitGateway(project_root=str(repo))
        calls: list[str] = []

        def _spy(session_id, files):
            calls.append("run")
            return None if len(calls) == 1 else "门禁 GATE-PRECOMMIT-RUN 阻断: fake-drift"

        monkeypatch.setattr(gw, "_run_precommit_channel", _spy)
        _silence_gates(monkeypatch)
        _quiet_post_commit(monkeypatch, gw)

        orig_add = GitCommitGateway._add_and_remove_normal_files

        def _drift_then_add(normal_files):
            target.write_text("X = 2\n", encoding="utf-8")  # 锁外通道后、add 前被并发写入
            return orig_add(gw, normal_files)

        monkeypatch.setattr(gw, "_add_and_remove_normal_files", _drift_then_add)

        res = gw.commit("t-d2", [str(target)], "test: d2 drift", allow_non_worktree=True)

        assert res.status == CommitStatus.COMMIT_FAILED
        assert res.message == "门禁 GATE-PRECOMMIT-RUN 阻断: fake-drift"
        assert calls == ["run", "run"], "指纹漂移必须触发锁内重跑（锁外1次+锁内1次）"


# ---------------------------------------------------------------------------
# 语义等价矩阵（蓝图 §5；例4/5 由通道本体零变更承载，不复制）
# ---------------------------------------------------------------------------


class TestD2Matrix:
    def test_m1_no_drift_adopts_prelock_result_single_run(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """矩阵1：通道绿+锁内无漂移 → 采信锁外结果，通道只跑一趟，adopted 落账。"""
        repo = _mk_repo(tmp_path)
        target = repo / "pkg" / "mod.py"
        target.write_text("X = 1\n", encoding="utf-8")
        gw = GitCommitGateway(project_root=str(repo))
        calls: list[str] = []

        def _spy(session_id, files):
            calls.append("run")
            return None

        monkeypatch.setattr(gw, "_run_precommit_channel", _spy)
        _silence_gates(monkeypatch)
        _quiet_post_commit(monkeypatch, gw)

        res = gw.commit("t-d2", [str(target)], "test: d2 adopt", allow_non_worktree=True)

        assert res.status == CommitStatus.OK
        assert calls == ["run"], "指纹一致必须采信锁外结果（单趟，不重跑）"
        adopted = [e for e in _read_anomaly_events(repo) if e.get("event") == "precommit_channel_adopted"]
        assert adopted, "采信必须落 adopted 审计事件"
        assert adopted[-1].get("verdict") == "pass"

    def test_m2_prelock_block_message_passthrough_no_rerun(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """矩阵2：通道红 → COMMIT_FAILED 且文案逐字节一致，指纹一致不重跑。"""
        repo = _mk_repo(tmp_path)
        target = repo / "pkg" / "mod.py"
        target.write_text("X = 1\n", encoding="utf-8")
        gw = GitCommitGateway(project_root=str(repo))
        block_msg = "门禁 GATE-PRECOMMIT-RUN 阻断: ruff-format 3 files"
        calls: list[str] = []

        def _spy(session_id, files):
            calls.append("run")
            return block_msg

        monkeypatch.setattr(gw, "_run_precommit_channel", _spy)
        _silence_gates(monkeypatch)
        _quiet_post_commit(monkeypatch, gw)

        res = gw.commit("t-d2", [str(target)], "test: d2 block", allow_non_worktree=True)

        assert res.status == CommitStatus.COMMIT_FAILED
        assert res.message == block_msg
        assert calls == ["run"]

    def test_m7_head_unchanged_guard_skips_channel(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """矩阵7：本提交文件相对 HEAD 零变化 → 守卫先短路，不白跑通道。"""
        repo = _mk_repo(tmp_path)
        target = repo / "pkg" / "base.py"  # 与 HEAD 完全一致
        gw = GitCommitGateway(project_root=str(repo))
        calls: list[str] = []

        def _spy(session_id, files):
            calls.append("run")
            return None

        monkeypatch.setattr(gw, "_run_precommit_channel", _spy)
        _silence_gates(monkeypatch)
        _quiet_post_commit(monkeypatch, gw)

        res = gw.commit("t-d2", [str(target)], "test: d2 noop", allow_non_worktree=True)

        assert res.status == CommitStatus.NOTHING_TO_COMMIT
        assert calls == [], "无可提交内容不得白跑通道"

    def test_runner_exception_falls_back_to_in_lock_channel(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """fail-safe：锁外前移编排异常 → 回退现行锁内全量通道（正确性永不依赖前移）。"""
        repo = _mk_repo(tmp_path)
        target = repo / "pkg" / "mod.py"
        target.write_text("X = 1\n", encoding="utf-8")
        gw = GitCommitGateway(project_root=str(repo))
        lock_path = repo / ".ailocks" / "git_commit_global.lock"
        seen: dict = {}

        def _spy(session_id, files):
            seen["lock_held"] = lock_path.exists()
            return None

        def _boom(files):
            raise RuntimeError("snapshot infra broken")

        monkeypatch.setattr(gw, "_precommit_snapshot_blob_shas", _boom)
        monkeypatch.setattr(gw, "_run_precommit_channel", _spy)
        _silence_gates(monkeypatch)
        _quiet_post_commit(monkeypatch, gw)

        res = gw.commit("t-d2", [str(target)], "test: d2 fallback", allow_non_worktree=True)

        assert res.status == CommitStatus.OK
        assert seen.get("lock_held") is True, "回退路径=现行锁内通道"

    def test_rollback_env_returns_in_lock_channel(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """回退手柄：ZEPHYR_PRECOMMIT_OUT_OF_LOCK=0 → 现行锁内全量通道。"""
        repo = _mk_repo(tmp_path)
        target = repo / "pkg" / "mod.py"
        target.write_text("X = 1\n", encoding="utf-8")
        gw = GitCommitGateway(project_root=str(repo))
        lock_path = repo / ".ailocks" / "git_commit_global.lock"
        seen: dict = {}

        def _spy(session_id, files):
            seen["lock_held"] = lock_path.exists()
            return None

        monkeypatch.setattr(gw, "_run_precommit_channel", _spy)
        monkeypatch.setenv("ZEPHYR_PRECOMMIT_OUT_OF_LOCK", "0")
        _silence_gates(monkeypatch)
        _quiet_post_commit(monkeypatch, gw)

        res = gw.commit("t-d2", [str(target)], "test: d2 rollback", allow_non_worktree=True)

        assert res.status == CommitStatus.OK
        assert seen.get("lock_held") is True, "回退手柄必须完整恢复锁内通道"


# ---------------------------------------------------------------------------
# 指纹原语直测（快照/复核/删除标记）
# ---------------------------------------------------------------------------


class TestD2FingerprintPrimitives:
    def test_snapshot_stage_match_and_drift(self, tmp_path: Path) -> None:
        repo = _mk_repo(tmp_path)
        f = repo / "pkg" / "s.py"
        f.write_text("A = 1\n", encoding="utf-8")
        gw = GitCommitGateway(project_root=str(repo))

        snap = gw._precommit_snapshot_blob_shas([str(f)])
        assert "pkg/s.py" in snap
        assert snap["pkg/s.py"] and len(snap["pkg/s.py"]) == 40  # git blob sha1

        subprocess.run(["git", "add", "pkg/s.py"], cwd=repo, check=True)
        assert gw._precommit_fingerprint_matches(snap, [str(f)]) is True

        f.write_text("A = 2\n", encoding="utf-8")
        subprocess.run(["git", "add", "pkg/s.py"], cwd=repo, check=True)
        assert gw._precommit_fingerprint_matches(snap, [str(f)]) is False

    def test_snapshot_deleted_mark_matches_absent_staged(self, tmp_path: Path) -> None:
        repo = _mk_repo(tmp_path)
        gone = repo / "pkg" / "gone.py"  # 盘上不存在、index 也没有
        gw = GitCommitGateway(project_root=str(repo))

        snap = gw._precommit_snapshot_blob_shas([str(gone)])
        assert snap == {"pkg/gone.py": "<deleted>"}
        assert gw._precommit_fingerprint_matches(snap, [str(gone)]) is True


# ---------------------------------------------------------------------------
# E 4→1 统一快照（s4_e_b4_snapshot.md；S4 全流通夜战 G1 车道 2026-09-30）
# ---------------------------------------------------------------------------


class TestE4to1UnifiedSnapshot:
    def test_e1_out_of_lock_single_own_face_capture(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """R-E1：绿路径锁外段 own 面内容捕获必须=1——hash-object 恰 1 次批扫，
        head guard 的 status --porcelain 内容批扫（原 #1）必须绝迹（快照派生替代）。

        现码（status+hash-object 锁外双扫）对「guard status 扫=0」断言必红。
        """
        repo = _mk_repo(tmp_path)
        target = repo / "pkg" / "mod.py"
        target.write_text("X = 1\n", encoding="utf-8")
        gw = GitCommitGateway(project_root=str(repo))
        calls: list[list[str]] = []
        orig_run_git = gw.run_git

        def _rec(cmd, *a, **k):
            calls.append(list(cmd))
            return orig_run_git(cmd, *a, **k)

        monkeypatch.setattr(gw, "run_git", _rec)
        monkeypatch.setattr(gw, "_run_precommit_channel", lambda sid, files: None)
        _silence_gates(monkeypatch)
        _quiet_post_commit(monkeypatch, gw)

        res = gw.commit("t-e1", [str(target)], "test: e1 single capture", allow_non_worktree=True)

        assert res.status == CommitStatus.OK
        hash_object_calls = [c for c in calls if "hash-object" in c]
        guard_status_calls = [c for c in calls if len(c) > 2 and c[1] == "status" and c[2] == "--porcelain"]
        assert len(hash_object_calls) == 1, "own 面内容捕获必须唯一（统一快照，E 4→1）"
        assert not guard_status_calls, "head guard 不得再做 status 内容批扫（原 #1 由快照派生替代）"

    def test_e2_drift_between_snapshot_and_inlock_recheck_reruns(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """R-E2（等价性锚，现码定绿基线）：锁外快照捕获后、锁内指纹复核前注入
        staged 漂移（改写同批文件内容）→ 锁内全量重跑被触发且重跑判定定案——
        任何把锁内复核也合并掉的实现在此必红。注入点=锁内首个 own 面清扫
        （_sweep_intent_to_add_residue），严格晚于快照、早于 step5.5 复核。
        """
        repo = _mk_repo(tmp_path)
        target = repo / "pkg" / "mod.py"
        target.write_text("X = 1\n", encoding="utf-8")
        gw = GitCommitGateway(project_root=str(repo))
        calls: list[str] = []

        def _spy(session_id, files):
            calls.append("run")
            return None if len(calls) == 1 else "门禁 GATE-PRECOMMIT-RUN 阻断: e2-drift"

        monkeypatch.setattr(gw, "_run_precommit_channel", _spy)
        _silence_gates(monkeypatch)
        _quiet_post_commit(monkeypatch, gw)

        orig_sweep = GitCommitGateway._sweep_intent_to_add_residue

        def _drift_on_sweep(self, session_id, exclude_rel):
            target.write_text("X = 2\n", encoding="utf-8")  # 快照已捕获、锁内复核未到
            return orig_sweep(self, session_id, exclude_rel)

        monkeypatch.setattr(GitCommitGateway, "_sweep_intent_to_add_residue", _drift_on_sweep)

        res = gw.commit("t-e2", [str(target)], "test: e2 drift rerun", allow_non_worktree=True)

        assert res.status == CommitStatus.COMMIT_FAILED
        assert res.message == "门禁 GATE-PRECOMMIT-RUN 阻断: e2-drift"
        assert calls == ["run", "run"], "漂移必须触发锁内重跑（锁外 1 次+锁内 1 次，复核语义不可合并）"

    def test_m_e_guard_conservative_status_fallback_on_snapshot_green(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """矩阵7/8 保守分支：工作树内容==HEAD（快照判绿）但 index 面漂移（staged 旧版）
        → status 兜底必须拦住（守卫不跳通道）——ls-tree 快照面看不见 index 漂移，
        该例是 status 兜底存在的本体证明（现码与 E 码同判定，双向锚）。
        """
        repo = _mk_repo(tmp_path)
        target = repo / "pkg" / "base.py"
        target.write_text("BASE = 2\n", encoding="utf-8")
        subprocess.run(["git", "add", "pkg/base.py"], cwd=repo, check=True)  # index≠HEAD
        target.write_text("VALUE = 1\n", encoding="utf-8")  # 工作树回写==HEAD（快照判绿面）
        gw = GitCommitGateway(project_root=str(repo))
        calls: list[str] = []

        def _spy(session_id, files):
            calls.append("run")
            return None

        monkeypatch.setattr(gw, "_run_precommit_channel", _spy)
        _silence_gates(monkeypatch)
        _quiet_post_commit(monkeypatch, gw)

        res = gw.commit("t-e8", [str(target)], "test: e8 index drift", allow_non_worktree=True)

        assert calls == ["run"], "index 漂移面必须被 status 兜底捕获，守卫不得跳通道"
        assert res.status == CommitStatus.NOTHING_TO_COMMIT  # add 工作树面后 index==HEAD，锁内短路兜底

    def test_m_e_guard_true_zero_change_skips_channel(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """矩阵7 真阴向：own 面与 HEAD 逐字节一致（含快照判绿+status 兜底双绿）
        → 守卫跳通道不白跑（E 码经快照派生判定，判定与现码一致）。
        """
        repo = _mk_repo(tmp_path)
        target = repo / "pkg" / "base.py"  # 与 HEAD 完全一致
        gw = GitCommitGateway(project_root=str(repo))
        calls: list[str] = []

        def _spy(session_id, files):
            calls.append("run")
            return None

        monkeypatch.setattr(gw, "_run_precommit_channel", _spy)
        _silence_gates(monkeypatch)
        _quiet_post_commit(monkeypatch, gw)

        res = gw.commit("t-e7", [str(target)], "test: e7 true noop", allow_non_worktree=True)

        assert res.status == CommitStatus.NOTHING_TO_COMMIT
        assert calls == [], "真零变化不得白跑通道（快照派生判定不放松）"

    def test_m_e_snapshot_facility_failure_falls_back_to_in_lock(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """矩阵1：hash-object 设施故障（rc≠0，非异常路径）→ 快照 None → 锁内全量通道。"""
        repo = _mk_repo(tmp_path)
        target = repo / "pkg" / "mod.py"
        target.write_text("X = 1\n", encoding="utf-8")
        gw = GitCommitGateway(project_root=str(repo))
        lock_path = repo / ".ailocks" / "git_commit_global.lock"
        seen: dict = {}
        orig_run_git = gw.run_git

        def _ho_fail(cmd, *a, **k):
            r = orig_run_git(cmd, *a, **k)
            if "hash-object" in cmd:
                r.returncode = 128  # 设施故障非 0（不抛异常的故障形态）
            return r

        monkeypatch.setattr(gw, "run_git", _ho_fail)

        def _spy(session_id, files):
            seen["lock_held"] = lock_path.exists()
            return None

        monkeypatch.setattr(gw, "_run_precommit_channel", _spy)
        _silence_gates(monkeypatch)
        _quiet_post_commit(monkeypatch, gw)

        res = gw.commit("t-e1f", [str(target)], "test: e1 facility fail", allow_non_worktree=True)

        assert res.status == CommitStatus.OK
        assert seen.get("lock_held") is True, "快照设施故障必须回退锁内全量通道"

    def test_m_e_batching_over_200_files_snapshot_vs_head(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """矩阵4 分批边界：201 文件（>200 触发分批）全等于 HEAD → 守卫跳通道；
        改写其一 → 守卫放行通道（两向判定跨批有效）。"""
        repo = _mk_repo(tmp_path)
        pkg = repo / "pkg"
        for i in range(201):
            (pkg / f"f{i:03d}.py").write_text(f"V{i} = {i}\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "bulk"], cwd=repo, check=True)
        files = [str(pkg / f"f{i:03d}.py") for i in range(201)]
        gw = GitCommitGateway(project_root=str(repo))

        # 真阴向：全等于 HEAD → 跳
        snap = gw._precommit_snapshot_blob_shas(files)
        assert snap is not None and len(snap) == 201
        assert gw._precommit_head_guard_skip(files, snapshot=snap) is True

        # 真阳向：改写第 201 个（第二批）→ 放行
        (pkg / "f200.py").write_text("V200 = changed\n", encoding="utf-8")
        snap2 = gw._precommit_snapshot_blob_shas(files)
        assert snap2 is not None
        assert gw._precommit_head_guard_skip(files, snapshot=snap2) is False

    def test_m_e_guard_deleted_face_conservative(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """矩阵3：删除面保守不跳（现行语义原样，快照 MARK 不参与守卫判绿）。"""
        repo = _mk_repo(tmp_path)
        gone = repo / "pkg" / "gone.py"
        gone.write_text("G = 1\n", encoding="utf-8")
        subprocess.run(["git", "add", "pkg/gone.py"], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "add gone"], cwd=repo, check=True)
        gone.unlink()  # 盘上删除
        gw = GitCommitGateway(project_root=str(repo))
        calls: list[str] = []

        def _spy(session_id, files):
            calls.append("run")
            return None

        monkeypatch.setattr(gw, "_run_precommit_channel", _spy)
        _silence_gates(monkeypatch)
        _quiet_post_commit(monkeypatch, gw)

        gw.commit("t-e3", [str(gone)], "test: e3 delete conservative", allow_non_worktree=True)
        assert calls == ["run"], "删除面保守不跳，交通道判定"
