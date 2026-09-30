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
