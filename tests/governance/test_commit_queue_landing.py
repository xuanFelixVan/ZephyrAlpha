# [A_test] module_id: MOD-GOV-047 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-047 | scripts/governance/commit_queue_landing.py | §
# [MODULE] tests.governance.test_commit_queue_landing
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; pyyaml; scripts.commit_queue; scripts.governance.commit_queue_landing; scripts.session_worktree; zephyr.gov_enforcement.rule_bridge.git_commit_gateway; zephyr.security.access_control.session_concurrency
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/test_commit_queue_landing.py
# [MATURITY] testing
# [INVARIANTS] 全 tmp 隔离（tmp git 仓 + tmp 队列根，绝不碰主仓 .runtime/commit_queue 与真实 dev/main）；GitCommitGateway 桩化注入——断言接线参数（session/files/message 标记/allow_non_worktree），git 语义（worktree/CAS/update-ref）走真 git
# [MODIFY-GUARD] 66 号 §6.3 MVP 形态 + §6.4 冲突判定 + §8 幂等；08 号文 §4.2 步骤 3/5 验收行（P0-6④ B 段任务口径）
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] permanent
"""test_commit_queue_landing.py — 提交队列 MVP B 段单元层验收（08 号文 §4.2 步骤 3/5）。

与 test_commit_queue_integration.py 分工：集成文件走**真 gateway 全门禁链**（50 提交
零丢失/门禁等价/真 hook 实证）；本文件走**桩化 gateway**——聚焦 landing 与网关的接线
契约（参数断言）+ 幂等短路 + 冲突死信 + flag 门控改道（含 fail-safe 降级）。

断言清单真源（P0-6④ B 段施工单）：
1. landing 成功路径：tmp git 仓造专用 worktree，入队 → drain(landing=WorktreeLanding)
   → blob 落成真实文件 + dev 推进 + commit message 含 [GW:{sid}:{qid}] 标记；
   GitCommitGateway 桩化——断言被调且参数正确（session_id/files/message/allow_non_worktree）。
2. 幂等（66 号 §8）：同项重放 drain → 不双 commit——①done 记录 landed_id is-ancestor
   短路；②landed_id 缺失时 [GW:{sid}:{qid}] 标记 grep dev 历史短路。两条路径分别钉住。
3. 冲突（66 号 §6.4）：base_head 之后目标文件被队列外推进 → ok=False 进 dead 带原因，
   他人推进内容不被覆盖，gateway 桩零调用（冲突在落盘前判定）。
4. flag 门控（08 号文 §4.2 步骤 5）：ALWAYS_OFF（默认）_commit_auto 直提不变且
   enqueue 零调用；flag ON 改道 enqueue（enqueue_item 被调 + 直提路径未执行）；
   改道异常（入队抛错/QueueReject）→ fail-safe 降级直提 + logging.warning 留痕。
5. 主工作区受限收敛（66 号 §9.7 受控放松 2026-08-23）：landing 后干净文件（与旧
   HEAD 逐字节一致）快进写入新内容；脏/缺失/untracked-WIP 一律跳过且审计留痕
   main_workspace_sync.jsonl（零 WIP 丢失）；delete action 收敛删除；崩溃窗口
   （update-ref 后收敛前）重放补收敛且 already_synced 幂等；收敛异常 fail-open
   不改变 LandingResult。
6. worktree 环境备置（2026-09-16 fail-open 治本）：ensure_worktree 两出口（新建/复用）
   都把主仓 config/.env.postgres + .env.clickhouse 备到 worktree（scripts.session_worktree
   _provision_worktree_env 真源，source_root=landing.repo_root）；备置产物不污染
   worktree git 状态；备置抛错仅告警，落盘照常成功。
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import tempfile
import threading
from pathlib import Path

import pytest
import yaml

import scripts.commit_queue as cq
import scripts.governance.commit_queue_landing as cql
import zephyr.gov_enforcement.rule_bridge.git_commit_gateway as gw_mod
from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (
    CommitResult,
    CommitStatus,
    GitCommitGateway,
)
from zephyr.security.access_control.session_concurrency import SessionRegistry

REPO_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# 基础工具（字节安全：内容比对走 bytes；与集成文件同款约定，本文件自含不跨测试文件 import）
# ---------------------------------------------------------------------------


def _git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, timeout=60)
    if check and r.returncode != 0:
        raise AssertionError(
            f"git {' '.join(args)} -> rc={r.returncode}: "
            f"stderr={r.stderr.decode('utf-8', errors='replace')[:400]} "
            f"stdout={r.stdout.decode('utf-8', errors='replace')[:400]}"
        )
    return r


def _git_text(cwd: Path, *args: str) -> str:
    return _git(cwd, *args).stdout.decode("utf-8", errors="replace").strip()


def _git_bytes(cwd: Path, *args: str) -> bytes:
    return _git(cwd, *args).stdout


@pytest.fixture()
def tmp_repo(tmp_path: Path) -> Path:
    """裸 git 仓：main 分支持初始提交，dev 分支同点（落盘目标）。core.autocrlf=false 保字节级比对。"""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "test")
    _git(repo, "config", "core.autocrlf", "false")
    # 与主仓 .gitignore 对齐：运行时目录豁免（worktree 内 .runtime/.ailocks 不污染 clean 断言）
    (repo / ".gitignore").write_text(".runtime/\n.ailocks/\n", encoding="utf-8")
    (repo / "base.txt").write_text("base\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-qm", "init")
    _git(repo, "branch", "dev")
    return repo


@pytest.fixture()
def queue_root(tmp_path: Path) -> Path:
    """队列根固定落 tmp_path（隔离真实 .runtime/commit_queue）。"""
    return tmp_path / "commit_queue"


def _dev_commit_count(repo: Path) -> int:
    base = _git_text(repo, "rev-list", "--max-parents=0", "dev")
    out = _git_text(repo, "rev-list", f"{base}..dev")
    return len([ln for ln in out.splitlines() if ln.strip()])


# ---------------------------------------------------------------------------
# GitCommitGateway 桩（接线契约断言 + 真实 git commit 语义——CAS/update-ref 走真 git）
# ---------------------------------------------------------------------------


class _StubGateway:
    """GitCommitGateway 桩：记录 claim/commit/release 调用参数；commit 在专用 worktree 内
    做**真实** git commit（绕门禁链——桩化意义即豁免门禁，git 对象/ref 语义保真，供
    landing 的 update-ref CAS 与幂等 is-ancestor 判定走真 git）。"""

    def __init__(self, worktree_path: Path) -> None:
        self._wt = worktree_path
        self.events: list[tuple[str, object]] = []  # 调用顺序留痕（claim → commit → release）

    def claim_files(self, session_id: str, files: list[str], adopt_prior_work: bool = False) -> list[str]:
        self.events.append(("claim", (session_id, list(files))))
        return list(files)

    def release_files(self, session_id: str, files: list[str]) -> None:
        self.events.append(("release", (session_id, list(files))))

    def commit(
        self,
        session_id: str,
        files: list[str],
        message: str,
        allow_non_worktree: bool = False,
        allow_tracked_drift: bool = False,  # #ARCH-310 B2：landing 传入（衍生漂移容忍）
        allow_multi_domain: bool = False,  # #ARCH-310 B3：landing 传入（队列项单任务豁免）
        allow_promote: bool = False,  # #ARCH-310 B3b：landing 传入（永久区新文件准入透传）
        lock_wait_timeout: float | None = None,  # 2026-09-16：landing 传入（全局锁等待放宽）
    ) -> CommitResult:
        self.events.append(
            (
                "commit",
                {
                    "session_id": session_id,
                    "files": list(files),
                    "message": message,
                    "allow_non_worktree": allow_non_worktree,
                    "allow_tracked_drift": allow_tracked_drift,
                    "allow_multi_domain": allow_multi_domain,
                    "allow_promote": allow_promote,
                    "lock_wait_timeout": lock_wait_timeout,
                },
            )
        )
        # 对齐生产 GitCommitGateway._add_and_remove_normal_files 契约（桩曾用
        # add -A 简化——对 delete action 破产：_apply_snapshot 已删盘 +
        # _prestage_snapshot 已 rm --cached 后，文件盘上/index 双缺失，
        # add -A 报 fatal: pathspec did not match，2026-09-16 delete 收敛两用例
        # 死信实证）。existing 走 git add；盘上缺失走 git rm --cached
        # --ignore-unmatch（幂等，prestage 后=无操作成功——与生产 gateway 同款）。
        for f in files:
            target = Path(f) if Path(f).is_absolute() else self._wt / f
            if target.is_file():
                _git(self._wt, "add", "--", f)
            else:
                _git(self._wt, "rm", "--cached", "--ignore-unmatch", "--", f)
        _git(self._wt, "commit", "--no-verify", "-qm", message)
        sha = _git_text(self._wt, "rev-parse", "HEAD")
        return CommitResult(status=CommitStatus.OK, message="stub committed", commit_hash=sha)

    def commit_calls(self) -> list[dict]:
        return [payload for kind, payload in self.events if kind == "commit"]


class _PathspecStubGateway:
    """pathspec 保真桩：commit 走生产同款 `git commit --pathspec-from-file`（:(icase)rel 行）
    + step3a 同款 add/rm --cached（git_commit_gateway._write_pathspec_file / _add_and_remove_normal_files）。

    为何不用 _StubGateway：后者用 whole-index `git commit`（无 pathspec），对"新文件在
    commit 前被 worktree 竞态清除"结构性失明——缺失文件被静默跳过不报错，永远 GREEN，
    无法复现 2026-09-17 q-…-0013 等 11 条 `pathspec did not match` 死信签名。本桩忠实
    复现该失败（COMMIT_FAILED + git stderr），供 untracked 新文件落地验收能红能绿。
    git 对象/ref 语义保真（CAS/update-ref/is-ancestor 走真 git），仅豁免门禁链。
    """

    def __init__(self, worktree_path: Path) -> None:
        self._wt = worktree_path
        self.events: list[tuple[str, object]] = []

    def claim_files(self, session_id: str, files: list[str], adopt_prior_work: bool = False) -> list[str]:
        self.events.append(("claim", (session_id, list(files))))
        return list(files)

    def release_files(self, session_id: str, files: list[str]) -> None:
        self.events.append(("release", (session_id, list(files))))

    def commit(
        self,
        session_id: str,
        files: list[str],
        message: str,
        allow_non_worktree: bool = False,
        allow_tracked_drift: bool = False,
        allow_multi_domain: bool = False,
        allow_promote: bool = False,
        lock_wait_timeout: float | None = None,
    ) -> CommitResult:
        self.events.append(("commit", {"session_id": session_id, "files": list(files), "message": message}))
        # step3a 保真：盘上存在→git add；缺失→git rm --cached --ignore-unmatch（幂等）
        for f in files:
            target = Path(f) if Path(f).is_absolute() else self._wt / f
            if target.is_file():
                _git(self._wt, "add", "--", f)
            else:
                _git(self._wt, "rm", "--cached", "--ignore-unmatch", "--", f)
        # pathspec 保真：:(icase)rel 行（rel 相对 worktree=project_root），与生产同款
        rels: list[str] = []
        for f in files:
            target = Path(f) if Path(f).is_absolute() else self._wt / f
            rel = os.path.relpath(str(target), str(self._wt)).replace("\\", "/")
            rels.append(f":(icase){rel}")
        ps_fd, pspec = tempfile.mkstemp(prefix="stub_pathspec_", suffix=".txt")
        with os.fdopen(ps_fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(rels) + "\n")
        msg_fd, msgp = tempfile.mkstemp(prefix="stub_msg_", suffix=".txt")
        with os.fdopen(msg_fd, "w", encoding="utf-8") as fh:
            fh.write(message)
        try:
            r = _git(self._wt, "commit", "--no-verify", "-F", msgp, f"--pathspec-from-file={pspec}", check=False)
            if r.returncode != 0:
                err = (
                    r.stderr.decode("utf-8", errors="replace").strip()
                    or r.stdout.decode("utf-8", errors="replace").strip()
                )
                return CommitResult(status=CommitStatus.COMMIT_FAILED, message=err)
            sha = _git_text(self._wt, "rev-parse", "HEAD")
            return CommitResult(status=CommitStatus.OK, message="stub pathspec committed", commit_hash=sha)
        finally:
            for p in (pspec, msgp):
                try:
                    os.remove(p)
                except OSError:
                    pass

    def commit_calls(self) -> list[dict]:
        return [payload for kind, payload in self.events if kind == "commit"]


def _make_landing_pathspec(repo: Path, qroot: Path) -> tuple[cql.WorktreeLanding, _PathspecStubGateway]:
    """landing + pathspec 保真桩组装（worktree 路径确定性同 _make_landing）。"""
    wt = (qroot / "worktree").resolve()
    stub = _PathspecStubGateway(wt)
    landing = cql.WorktreeLanding(repo_root=repo, queue_root=qroot, gateway=stub)
    return landing, stub


def _make_landing(repo: Path, qroot: Path) -> tuple[cql.WorktreeLanding, _StubGateway]:
    """landing + 桩 gateway 组装（worktree 路径确定性：<queue_root>/worktree，先构造桩仅记录路径）。"""
    wt = (qroot / "worktree").resolve()
    stub = _StubGateway(wt)
    landing = cql.WorktreeLanding(repo_root=repo, queue_root=qroot, gateway=stub)
    return landing, stub


# ---------------------------------------------------------------------------
# 1. landing 成功路径（08 号文 §4.2 步骤 3 验收行）
# ---------------------------------------------------------------------------


class TestWorktreeLandingSuccess:
    def test_enqueue_drain_lands_real_commit_with_queue_marker(self, tmp_repo: Path, queue_root: Path) -> None:
        landing, stub = _make_landing(tmp_repo, queue_root)
        sid = "sess-land-a"
        content = "hello 落盘\n".encode()
        item = cq.enqueue_item(sid, "feat: landing 成功路径", [("docs/landed.txt", content)], queue_root=queue_root)

        stats = cq.drain_queue(queue_root, landing=landing)
        assert stats["done"] == 1 and stats["dead"] == 0, f"drain 统计异常: {stats}"

        # 桩被调且接线参数正确（gateway 契约断言）
        calls = stub.commit_calls()
        assert len(calls) == 1, "gateway.commit 恰被调一次"
        call = calls[0]
        marker = cql.queue_marker(sid, item["qid"])
        assert call["session_id"] == sid
        assert marker in call["message"], f"commit message 缺 [GW:{{sid}}:{{qid}}] 标记: {call['message']!r}"
        assert call["message"].startswith("feat: landing 成功路径"), "原 message 在前、标记追加在后"
        assert call["allow_non_worktree"] is True, (
            "落盘经 allow_non_worktree 逃生参数（.runtime 路径不命中 worktree 判定）"
        )
        assert call["files"] == [str(landing.worktree_path / "docs" / "landed.txt")], (
            "pathspec 限定本项文件（零搭便车）"
        )

        # claim → commit → release 顺序（CLAIM-REQUIRED 协议接线）
        kinds = [kind for kind, _ in stub.events]
        assert kinds == ["claim", "commit", "release"], f"claim/commit/release 顺序异常: {kinds}"

        # 真实落盘：dev HEAD == 桩 commit；内容字节级一致；done 记录 landed_id
        landed_id = _git_text(tmp_repo, "rev-parse", "refs/heads/dev")
        assert _dev_commit_count(tmp_repo) == 1
        assert _git_bytes(tmp_repo, "show", "dev:docs/landed.txt") == content
        # 落盘后 dev 历史中的 commit message 含队列标记（POST-COMMIT-GUARD 兼容面）
        dev_msg = _git_bytes(tmp_repo, "show", "-s", "--format=%B", "refs/heads/dev").decode("utf-8")
        assert marker in dev_msg
        done_item = json.loads((queue_root / "done" / f"{item['qid']}.json").read_text(encoding="utf-8"))
        assert done_item["landed_id"] == landed_id

        # 专用 worktree 懒创建已发生且是独立 git worktree（非主工作区）
        wt = landing.worktree_path
        assert wt.is_dir() and (wt / ".git").is_file(), "worktree .git 指针文件存在（独立 worktree 形态）"
        assert _git_text(wt, "rev-parse", "HEAD") == landed_id, "66 号 §11 #6 终态：worktree HEAD == dev HEAD"
        assert _git_text(wt, "status", "--porcelain") == "", "落盘后 worktree 干净"

    def test_worktree_lazy_creation_failure_goes_dead(
        self, tmp_repo: Path, queue_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """worktree 懒创建失败 → 降级 ok=False 进死信带原因（不抛出不卡队）。"""
        landing, stub = _make_landing(tmp_repo, queue_root)

        def _boom(*args: str, check: bool = True) -> subprocess.CompletedProcess:
            raise RuntimeError("worktree add failed（模拟磁盘/权限故障）")

        monkeypatch.setattr(landing, "_git_repo", _boom)
        item = cq.enqueue_item("sess-land-b", "feat: doomed", [("docs/x.txt", b"x\n")], queue_root=queue_root)
        stats = cq.drain_queue(queue_root, landing=landing)
        assert stats["dead"] == 1 and stats["done"] == 0
        dead_item = json.loads((queue_root / "dead" / f"{item['qid']}.json").read_text(encoding="utf-8"))
        assert "worktree add failed" in dead_item["dead_reason"], f"死信带创建失败原因: {dead_item['dead_reason']}"
        assert stub.commit_calls() == [], "创建失败不得触达 gateway"
        assert _dev_commit_count(tmp_repo) == 0, "失败项不得推进 dev"


# ---------------------------------------------------------------------------
# 2. 幂等（66 号 §8：is-ancestor / 标记 grep 短路——崩溃重入不双落）
# ---------------------------------------------------------------------------


class TestWorktreeLandingIdempotent:
    def test_replay_done_item_short_circuits_via_is_ancestor(self, tmp_repo: Path, queue_root: Path) -> None:
        """短路径①：重放项带 landed_id 且已在 dev 历史（is-ancestor）→ 复用不双落。"""
        landing, stub = _make_landing(tmp_repo, queue_root)
        item = cq.enqueue_item("sess-idem-a", "feat: 幂等", [("docs/idem.txt", b"v1\n")], queue_root=queue_root)
        stats = cq.drain_queue(queue_root, landing=landing)
        assert stats["done"] == 1
        assert len(stub.commit_calls()) == 1
        first_sha = _git_text(tmp_repo, "rev-parse", "refs/heads/dev")

        # 重放：done 项原样（含 landed_id）回到 pending——模拟崩溃重入/重复调度
        done_path = queue_root / "done" / f"{item['qid']}.json"
        (queue_root / "pending" / done_path.name).write_bytes(done_path.read_bytes())
        stats2 = cq.drain_queue(queue_root, landing=landing)
        assert stats2["done"] == 1 and stats2["dead"] == 0
        assert len(stub.commit_calls()) == 1, "幂等短路：gateway.commit 不得二次调用"
        assert _dev_commit_count(tmp_repo) == 1, "不双 commit"
        assert _git_text(tmp_repo, "rev-parse", "refs/heads/dev") == first_sha, "dev 未再推进"
        done_item = json.loads(done_path.read_text(encoding="utf-8"))
        assert done_item["landed_id"] == first_sha, "复用已落 commit sha"

    def test_replay_without_landed_id_short_circuits_via_marker_grep(self, tmp_repo: Path, queue_root: Path) -> None:
        """短路径②：landed_id 缺失（done 记录丢失形态）但标记在史 → grep 命中复用。"""
        landing, stub = _make_landing(tmp_repo, queue_root)
        item = cq.enqueue_item("sess-idem-b", "feat: 幂等2", [("docs/idem2.txt", b"v2\n")], queue_root=queue_root)
        cq.drain_queue(queue_root, landing=landing)
        assert len(stub.commit_calls()) == 1
        first_sha = _git_text(tmp_repo, "rev-parse", "refs/heads/dev")

        # 重放项：剥掉 landed_id/landed_at（仅剩标记在 dev 历史可证已落盘）
        done_path = queue_root / "done" / f"{item['qid']}.json"
        replay = json.loads(done_path.read_text(encoding="utf-8"))
        replay.pop("landed_id", None)
        replay.pop("landed_at", None)
        os.remove(done_path)
        (queue_root / "pending" / done_path.name).write_text(
            json.dumps(replay, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        stats2 = cq.drain_queue(queue_root, landing=landing)
        assert stats2["done"] == 1 and stats2["dead"] == 0
        assert len(stub.commit_calls()) == 1, "标记 grep 短路：gateway.commit 不得二次调用"
        assert _dev_commit_count(tmp_repo) == 1
        done_item = json.loads(done_path.read_text(encoding="utf-8"))
        assert done_item["landed_id"] == first_sha, "grep 短路回填已落 commit sha"


# ---------------------------------------------------------------------------
# 3. 冲突判定（66 号 §6.4：base_head 以来同路径被推进 → 死信回退人工，不静默覆盖）
# ---------------------------------------------------------------------------


class TestWorktreeLandingConflict:
    def test_base_head_conflict_goes_dead_and_preserves_theirs(self, tmp_repo: Path, queue_root: Path) -> None:
        landing, stub = _make_landing(tmp_repo, queue_root)
        base = _git_text(tmp_repo, "rev-parse", "refs/heads/dev")
        item = cq.enqueue_item(
            "sess-conf-a",
            "feat: 冲突项",
            [("docs/a.txt", b"mine\n")],
            queue_root=queue_root,
            options=cq.EnqueueOptions(base_head=base),
        )
        # 入队后 dev 被队列外写入者推进且触及同路径（flag OFF 期第二写入者形态模拟）
        (tmp_repo / "docs").mkdir(exist_ok=True)
        (tmp_repo / "docs" / "a.txt").write_bytes(b"theirs\n")  # write_bytes 防 Windows 文本模式 \r\n 转换
        _git(tmp_repo, "add", "docs/a.txt")
        _git(tmp_repo, "commit", "-qm", "direct writer touches same file")
        _git(tmp_repo, "branch", "-f", "dev", "HEAD")

        stats = cq.drain_queue(queue_root, landing=landing)
        assert stats["dead"] == 1 and stats["done"] == 0
        dead_item = json.loads((queue_root / "dead" / f"{item['qid']}.json").read_text(encoding="utf-8"))
        assert "冲突" in dead_item["dead_reason"] and "docs/a.txt" in dead_item["dead_reason"], (
            f"死信正确归因（66 号 §10）：{dead_item['dead_reason']}"
        )
        assert stub.commit_calls() == [], "冲突在落盘前判定——gateway 零调用"
        assert _git_bytes(tmp_repo, "show", "dev:docs/a.txt") == b"theirs\n", "他人推进内容不被静默覆盖"

    def test_disjoint_advance_does_not_conflict(self, tmp_repo: Path, queue_root: Path) -> None:
        """对照：base_head 后 dev 推进但不触及本项路径 → 正常落盘（逐文件快进判定）。"""
        landing, stub = _make_landing(tmp_repo, queue_root)
        base = _git_text(tmp_repo, "rev-parse", "refs/heads/dev")
        cq.enqueue_item(
            "sess-conf-b",
            "feat: 不相交",
            [("docs/mine.txt", b"mine\n")],
            queue_root=queue_root,
            options=cq.EnqueueOptions(base_head=base),
        )
        (tmp_repo / "docs").mkdir(exist_ok=True)
        (tmp_repo / "docs" / "other.txt").write_bytes(b"other\n")
        _git(tmp_repo, "add", "docs/other.txt")
        _git(tmp_repo, "commit", "-qm", "direct writer touches disjoint file")
        _git(tmp_repo, "branch", "-f", "dev", "HEAD")

        stats = cq.drain_queue(queue_root, landing=landing)
        assert stats["done"] == 1 and stats["dead"] == 0, "不相交推进不构成冲突（逐文件快进）"
        assert _git_bytes(tmp_repo, "show", "dev:docs/mine.txt") == b"mine\n"
        assert _git_bytes(tmp_repo, "show", "dev:docs/other.txt") == b"other\n", "他人推进不丢"


# ---------------------------------------------------------------------------
# 4. flag 门控（08 号文 §4.2 步骤 5：ALWAYS_OFF 默认 / ON 改道 / 异常 fail-safe 降级）
# ---------------------------------------------------------------------------


class TestCommitAutoFlagGating:
    def _gateway(self, repo: Path, sid: str = "sess-flag-l") -> GitCommitGateway:
        reg = SessionRegistry(repo)
        reg.register(sid)
        return GitCommitGateway(project_root=repo, registry=reg)

    def test_flags_yaml_registers_flag_matches_owner_window_state(self) -> None:
        """flag 注册与 Owner 窗口状态一致性证明：真仓 config/flags.yaml 注册
        commit_queue_serializer，且 enabled 值与 _commit_queue_serializer_enabled()
        设施读出端到端一致（单真源，禁止 YAML 与设施漂移）。

        状态沿革：注册默认 ALWAYS_OFF（宪章 B-007 安全默认）→ Owner 2026-08-22 批准
        翻开启用（commit 2814b7f469，Owner 窗口操作非本测试职责）。本测试只钉
        「YAML 值 == 设施读出值」一致性 + 当前 Owner 批准态为 ON。"""
        flags = yaml.safe_load((REPO_ROOT / "config" / "flags.yaml").read_text(encoding="utf-8"))
        entry = flags["flags"]["commit_queue_serializer"]
        assert entry["enabled"] is True, (
            "commit_queue_serializer 当前 Owner 批准态=ON（2814b7f469，2026-08-22）；"
            "若需回退 ALWAYS_OFF 须再走 Owner 窗口并同步改本断言"
        )
        # YAML 与真 flags 设施读出端到端一致（接线点 _commit_queue_serializer_enabled）
        assert gw_mod._commit_queue_serializer_enabled() is True

    def test_flag_off_direct_commit_unchanged(
        self, tmp_repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """ALWAYS_OFF：_commit_auto 现行直提一字不动——enqueue 零调用，HEAD 真实推进。"""
        monkeypatch.setenv(cq.QUEUE_ENV_VAR, str(tmp_path / "cq_off"))  # 隔离真实队列目录
        monkeypatch.setattr(gw_mod, "_commit_queue_serializer_enabled", lambda: False)

        def _forbidden_enqueue(*args, **kwargs):
            raise AssertionError("flag OFF 不得调 enqueue_item（直提路径不入队）")

        monkeypatch.setattr(cq, "enqueue_item", _forbidden_enqueue)
        gw = self._gateway(tmp_repo)
        (tmp_repo / "auto_off.txt").write_text("auto\n", encoding="utf-8")
        result = gw._commit_auto("sess-flag-l", [str(tmp_repo / "auto_off.txt")], "chore: auto off")
        assert result.status is CommitStatus.OK, f"flag OFF 直提失败: {result.message}"
        msg = _git_bytes(tmp_repo, "show", "-s", "--format=%B", "HEAD").decode("utf-8")
        assert "[GW:sess-flag-l:auto]" in msg, "直提保留 :auto 标记（现行行为不变）"
        qroot = tmp_path / "cq_off"
        assert not qroot.exists() or not list((qroot / "pending").glob("q-*.json")), "flag OFF 不得产生队列项"

    def test_flag_on_reroutes_to_enqueue(self, tmp_repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """flag ON：改道 enqueue（enqueue_item 被调 + 直提路径未执行 + 自举排空尝试）。"""
        monkeypatch.setenv(cq.QUEUE_ENV_VAR, str(tmp_path / "cq_on"))
        monkeypatch.setattr(gw_mod, "_commit_queue_serializer_enabled", lambda: True)
        enqueue_calls: list[dict] = []

        def _spy_enqueue(session_id, message, files, **kwargs):
            enqueue_calls.append({"session_id": session_id, "message": message, "files": list(files), "kwargs": kwargs})
            return {"qid": "q-20260821-sess-flag-l-0001", "session_id": session_id, "files": []}

        monkeypatch.setattr(cq, "enqueue_item", _spy_enqueue)
        bootstrap_calls: list[dict] = []
        monkeypatch.setattr(
            cql, "bootstrap_drain_with_landing", lambda **kw: bootstrap_calls.append(kw) or {"skipped": True}
        )
        gw = self._gateway(tmp_repo)
        head_before = _git_text(tmp_repo, "rev-parse", "HEAD")
        (tmp_repo / "auto_on.txt").write_text("auto on\n", encoding="utf-8")
        result = gw._commit_auto("sess-flag-l", [str(tmp_repo / "auto_on.txt")], "chore: auto on")
        assert result.status is CommitStatus.OK and result.commit_hash.startswith("QUEUED:"), (
            f"改道回执异常: {result.status} {result.commit_hash}"
        )
        assert _git_text(tmp_repo, "rev-parse", "HEAD") == head_before, "改道后直提路径未执行（HEAD 不动）"
        assert len(enqueue_calls) == 1, "enqueue_item 恰被调一次"
        call = enqueue_calls[0]
        assert call["session_id"] == "sess-flag-l"
        assert call["message"] == "chore: auto on"
        assert [path for path, _ in call["files"]] == ["auto_on.txt"], "仓内相对路径快照入袋"
        opts = call["kwargs"].get("options")
        assert isinstance(opts, cq.EnqueueOptions), "可选参数束走 EnqueueOptions（A 段签名收口）"
        assert opts.base_head == _git_text(tmp_repo, "rev-parse", "refs/heads/dev"), "base_head 落袋"
        assert opts.meta_extra == {"rerouted_from": "_commit_auto", "lane": "machine"}, (
            "改道来源审计标记+P1-D 车道标记落袋"
        )
        assert bootstrap_calls, "入队后触发自举排空尝试（66 号 §8；mock 不真实落盘）"

    def test_flag_on_enqueue_exception_falls_back_to_direct_commit(
        self, tmp_repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        """fail-safe：enqueue 抛异常 → 降级现行直提 + logging.warning（队列异常不阻塞 reconciler）。"""
        monkeypatch.setenv(cq.QUEUE_ENV_VAR, str(tmp_path / "cq_fb"))
        monkeypatch.setattr(gw_mod, "_commit_queue_serializer_enabled", lambda: True)

        def _boom(*args, **kwargs):
            raise RuntimeError("queue infra down（模拟队列设施异常）")

        monkeypatch.setattr(cq, "enqueue_item", _boom)
        gw = self._gateway(tmp_repo)
        (tmp_repo / "auto_fb.txt").write_text("fb\n", encoding="utf-8")
        with caplog.at_level(logging.WARNING):
            result = gw._commit_auto("sess-flag-l", [str(tmp_repo / "auto_fb.txt")], "chore: auto fallback")
        assert result.status is CommitStatus.OK, f"降级直提失败: {result.message}"
        msg = _git_bytes(tmp_repo, "show", "-s", "--format=%B", "HEAD").decode("utf-8")
        assert "[GW:sess-flag-l:auto]" in msg, "降级=现行直提（:auto 标记，无队列标记——单写者断言可点名）"
        warnings = [r for r in caplog.records if r.levelno >= logging.WARNING and "降级" in r.getMessage()]
        assert warnings, "降级必须 logging.warning 留痕（非静默）"

    def test_flag_on_queue_reject_falls_back_to_direct_commit(
        self, tmp_repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        """fail-safe 含 QueueReject：入队被拒（内容违例）同样降级直提 + warning——
        拒绝项多为 reconciler 生成物，永久 COMMIT_FAILED 会卡死 reconciler 工作流
        （08 号文 §4.2 步骤 5 任务口径；直提路径自有门禁链兜底）。"""
        monkeypatch.setenv(cq.QUEUE_ENV_VAR, str(tmp_path / "cq_rj"))
        monkeypatch.setattr(gw_mod, "_commit_queue_serializer_enabled", lambda: True)

        def _reject(*args, **kwargs):
            raise cq.QueueReject("模拟入队轻检拒绝")

        monkeypatch.setattr(cq, "enqueue_item", _reject)
        gw = self._gateway(tmp_repo)
        (tmp_repo / "auto_rj.txt").write_text("rj\n", encoding="utf-8")
        with caplog.at_level(logging.WARNING):
            result = gw._commit_auto("sess-flag-l", [str(tmp_repo / "auto_rj.txt")], "chore: auto reject fallback")
        assert result.status is CommitStatus.OK, f"QueueReject 降级直提失败: {result.message}"
        warnings = [r for r in caplog.records if r.levelno >= logging.WARNING and "降级" in r.getMessage()]
        assert warnings, "QueueReject 降级同样 warning 留痕"


# ---------------------------------------------------------------------------
# 5. 主工作区受限收敛（66 号 §9.7 受控放松 2026-08-23）
#    干净快进 / 脏·缺失·untracked-WIP 跳过留痕 / 崩溃重放补收敛 / fail-open
# ---------------------------------------------------------------------------


def _audit_records(qroot: Path) -> list[dict]:
    """读取主工作区收敛审计 JSONL（不存在=零跳过，返回空表）。"""
    p = qroot / "main_workspace_sync.jsonl"
    if not p.exists():
        return []
    return [json.loads(ln) for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()]


class TestMainWorkspaceConvergence:
    def test_clean_file_fast_forwarded_to_main_workspace(self, tmp_repo: Path, queue_root: Path) -> None:
        """干净文件（与旧 HEAD 逐字节一致）→ 快进写入新内容；零审计（无跳过项）。"""
        landing, _stub = _make_landing(tmp_repo, queue_root)
        new_base = "base v2 落盘\n".encode()
        item = cq.enqueue_item(
            "sess-conv-a",
            "feat: 收敛快进",
            [("base.txt", new_base), ("docs/added.txt", b"new file\n")],
            queue_root=queue_root,
        )
        stats = cq.drain_queue(queue_root, landing=landing)
        assert stats["done"] == 1 and stats["dead"] == 0

        # 主工作区字节级快进（治陈旧快照：landing 后工作区即见新内容）
        assert (tmp_repo / "base.txt").read_bytes() == new_base
        assert (tmp_repo / "docs" / "added.txt").read_bytes() == b"new file\n"
        assert _audit_records(queue_root) == [], f"干净快进不得产生审计留痕（qid={item['qid']}）"

    def test_dirty_file_skipped_with_audit_and_wip_preserved(self, tmp_repo: Path, queue_root: Path) -> None:
        """脏文件（主工作区有 WIP 修改）→ 跳过 + 审计留痕，WIP 字节零丢失。"""
        landing, _stub = _make_landing(tmp_repo, queue_root)
        wip = "本地 WIP 未提交\n".encode()
        (tmp_repo / "base.txt").write_bytes(wip)  # 队列外会话的未提交修改
        item = cq.enqueue_item("sess-conv-b", "feat: 脏跳过", [("base.txt", b"queue content\n")], queue_root=queue_root)
        stats = cq.drain_queue(queue_root, landing=landing)
        assert stats["done"] == 1, "landing 从专用 worktree 落盘，主工作区脏不阻塞"

        assert (tmp_repo / "base.txt").read_bytes() == wip, "零 WIP 丢失铁律：脏文件绝不被覆写"
        assert _git_bytes(tmp_repo, "show", "dev:base.txt") == b"queue content\n", "dev 树已推进（收敛只影响工作区）"
        recs = _audit_records(queue_root)
        assert len(recs) == 1 and recs[0]["action"] == "skipped_dirty"
        assert recs[0]["path"] == "base.txt" and recs[0]["qid"] == item["qid"]

    def test_missing_file_skipped_with_audit(self, tmp_repo: Path, queue_root: Path) -> None:
        """缺失文件（WIP 删除态）→ skipped_missing + 审计；盘上维持缺失不重建。"""
        landing, _stub = _make_landing(tmp_repo, queue_root)
        os.remove(tmp_repo / "base.txt")  # 队列外会话的未提交删除
        item = cq.enqueue_item(
            "sess-conv-c", "feat: 缺失跳过", [("base.txt", b"queue content\n")], queue_root=queue_root
        )
        stats = cq.drain_queue(queue_root, landing=landing)
        assert stats["done"] == 1

        assert not (tmp_repo / "base.txt").exists(), "缺失态不被收敛重建（WIP 删除同样受保护）"
        recs = _audit_records(queue_root)
        assert len(recs) == 1 and recs[0]["action"] == "skipped_missing"
        assert recs[0]["path"] == "base.txt" and recs[0]["qid"] == item["qid"]

    def test_untracked_wip_at_new_path_skipped_not_overwritten(self, tmp_repo: Path, queue_root: Path) -> None:
        """untracked-WIP 补盲（红队钉）：旧树无此路径 + 盘上有未跟踪同名文件——
        git diff 对 untracked 不可见会误判「双方一致」，快进即覆写他人 WIP。
        必须按脏跳过 + 审计，WIP 字节保留。"""
        landing, _stub = _make_landing(tmp_repo, queue_root)
        (tmp_repo / "docs").mkdir(exist_ok=True)
        wip = "他人 untracked WIP\n".encode()
        (tmp_repo / "docs" / "wip.txt").write_bytes(wip)
        cq.enqueue_item(
            "sess-conv-d", "feat: untracked 补盲", [("docs/wip.txt", b"queue content\n")], queue_root=queue_root
        )
        stats = cq.drain_queue(queue_root, landing=landing)
        assert stats["done"] == 1

        assert (tmp_repo / "docs" / "wip.txt").read_bytes() == wip, "untracked WIP 绝不被快进覆写"
        assert _git_bytes(tmp_repo, "show", "dev:docs/wip.txt") == b"queue content\n"
        recs = _audit_records(queue_root)
        assert len(recs) == 1 and recs[0]["action"] == "skipped_dirty"
        assert recs[0]["path"] == "docs/wip.txt"

    def test_delete_action_removes_clean_file_from_main_workspace(self, tmp_repo: Path, queue_root: Path) -> None:
        """delete action + 工作区干净 → 收敛删除主工作区文件（dev 树与工作区同态）。"""
        landing, _stub = _make_landing(tmp_repo, queue_root)
        cq.enqueue_item(
            "sess-conv-e",
            "chore: 删除收敛",
            [],
            queue_root=queue_root,
            options=cq.EnqueueOptions(deletes=["base.txt"]),
        )
        stats = cq.drain_queue(queue_root, landing=landing)
        assert stats["done"] == 1 and stats["dead"] == 0

        assert not (tmp_repo / "base.txt").exists(), "干净删除项收敛后工作区文件移除"
        assert _git(tmp_repo, "cat-file", "-e", "dev:base.txt", check=False).returncode != 0, "dev 树已删除"
        assert _audit_records(queue_root) == [], "成功删除非跳过项，零审计"

    def test_delete_action_already_missing_is_noop_without_audit(self, tmp_repo: Path, queue_root: Path) -> None:
        """delete action + 工作区已缺失（WIP 删除先行）→ already_deleted 幂等零审计。"""
        landing, _stub = _make_landing(tmp_repo, queue_root)
        os.remove(tmp_repo / "base.txt")
        cq.enqueue_item(
            "sess-conv-f",
            "chore: 删除幂等",
            [],
            queue_root=queue_root,
            options=cq.EnqueueOptions(deletes=["base.txt"]),
        )
        stats = cq.drain_queue(queue_root, landing=landing)
        assert stats["done"] == 1
        assert not (tmp_repo / "base.txt").exists()
        assert _audit_records(queue_root) == [], "语义已达成的删除不审计（already_deleted）"

    def test_replay_converges_after_crash_window(
        self, tmp_repo: Path, queue_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """崩溃窗口补收敛 + fail-open 双钉：①收敛抛异常不改变 LandingResult（landing
        已成功，done=1）；②重放走 _already_landed 短路时补跑收敛（幂等快进）；
        ③二次重放 already_synced 零审计。"""
        landing, _stub = _make_landing(tmp_repo, queue_root)
        orig_bytes = (tmp_repo / "base.txt").read_bytes()  # fixture text 模式写入，Windows 盘上为 CRLF
        new_base = b"base v2 after crash\n"
        item = cq.enqueue_item("sess-conv-g", "feat: 崩溃窗口", [("base.txt", new_base)], queue_root=queue_root)

        # ① 模拟 update-ref 后、收敛写入前的崩溃窗口：收敛整体失效但 landing 成功
        orig = landing._converge_main_workspace
        calls = {"n": 0}

        def _flaky(it: dict, old: str, new: str) -> None:
            calls["n"] += 1
            if calls["n"] == 1:
                raise RuntimeError("模拟崩溃窗口：dev 已推进，主工作区未收敛")
            orig(it, old, new)

        monkeypatch.setattr(landing, "_converge_main_workspace", _flaky)
        stats = cq.drain_queue(queue_root, landing=landing)
        assert stats["done"] == 1 and stats["dead"] == 0, "收敛 fail-open：异常不改变落盘结果"
        assert (tmp_repo / "base.txt").read_bytes() == orig_bytes, "崩溃窗口内主工作区停在旧内容"

        # ② 重放（done 项回 pending，模拟崩溃重入）→ _already_landed 短路 + 补跑收敛
        done_path = queue_root / "done" / f"{item['qid']}.json"
        (queue_root / "pending" / done_path.name).write_bytes(done_path.read_bytes())
        stats2 = cq.drain_queue(queue_root, landing=landing)
        assert stats2["done"] == 1 and stats2["dead"] == 0
        assert calls["n"] == 2, "重放短路路径补跑收敛"
        assert (tmp_repo / "base.txt").read_bytes() == new_base, "补收敛把干净文件快进到新内容"
        assert _dev_commit_count(tmp_repo) == 1, "补收敛不双 commit"
        assert _audit_records(queue_root) == [], "快进成功零审计"

        # ③ 二次重放：文件已 == new_sha → already_synced，幂等零副作用
        (queue_root / "pending" / done_path.name).write_bytes(done_path.read_bytes())
        stats3 = cq.drain_queue(queue_root, landing=landing)
        assert stats3["done"] == 1
        assert _audit_records(queue_root) == [], "already_synced 幂等，零审计零副作用"


# ---------------------------------------------------------------------------
# 2026-08-29 主仓打穿事故回归：专用 worktree .git 链接丢失 → fail-closed
# ---------------------------------------------------------------------------


class TestWorktreeGitlinkGuard:
    """2026-08-29 事故回归：专用 worktree 目录在而 .git 链接丢失 → git walk-up 打穿主仓。

    事故实证：.runtime/commit_queue/worktree 注册残留（git worktree list 标 prunable）且目录内
    .git 链接文件丢失（残留检出树仍在）——landing 的 _sync_worktree 以该目录为 cwd 执行
    reset --hard refs/heads/dev + clean -fd 时，git 向上查找命中主仓 .git，主工作区未提交
    修改被清（当日 reflog 6 次成对 reset）。治本：_git_wt fail-closed + ensure_worktree 检测重建。
    """

    def test_git_wt_refuses_when_gitlink_missing(self, tmp_path: Path):
        """目录在、.git 链接缺失（事故形态）→ RuntimeError，绝不执行 git。"""
        landing = cql.WorktreeLanding.__new__(cql.WorktreeLanding)
        landing.worktree_path = tmp_path / "worktree"
        landing.worktree_path.mkdir()
        with pytest.raises(RuntimeError, match=r"\.git"):
            landing._git_wt("status")

    def test_git_wt_refuses_when_toplevel_drifts(self, tmp_path: Path, monkeypatch):
        """.git 链接在但 toplevel 解析漂移（walk-up 命中外层仓）→ RuntimeError。"""
        landing = cql.WorktreeLanding.__new__(cql.WorktreeLanding)
        wt = tmp_path / "worktree"
        wt.mkdir()
        (wt / ".git").write_text("gitdir: ../fake", encoding="utf-8")
        landing.worktree_path = wt

        class _FakeR:
            stdout = str(tmp_path)  # toplevel 漂移到上级目录（walk-up 命中外层仓形态）

        monkeypatch.setattr(cql, "_run_git", lambda *a, **k: _FakeR())
        with pytest.raises(RuntimeError, match="toplevel"):
            landing._git_wt("status")

    def test_ensure_worktree_rebuilds_when_gitlink_missing(self, tmp_repo: Path, queue_root: Path):
        """registered + 目录在但 .git 链接丢失 → 不复用：prune + 清残骸 + 重建（.git 链接恢复）。"""
        landing = cql.WorktreeLanding(tmp_repo, queue_root=queue_root)
        wt = landing.ensure_worktree()
        assert (wt / ".git").exists(), "首次建立后 .git 链接应在位"
        # 制造事故形态：删掉 .git 链接文件（目录残留树保留）
        (wt / ".git").unlink()
        wt2 = landing.ensure_worktree()
        assert (wt2 / ".git").exists(), "链接丢失后须重建恢复 .git"
        # 重建后 _git_wt 恢复可用
        r = landing._git_wt("rev-parse", "--show-toplevel")
        assert Path(r.stdout.strip()).resolve() == wt2.resolve()


class _NothingToCommitStub(_StubGateway):
    """模拟快照应用静默丢失（2026-09-15 q-0003 假落地事故）：gateway 报
    NOTHING_TO_COMMIT 且不产生任何 commit——guard 必须死信而非伪装 ok。"""

    def commit(self, *args, **kwargs):  # noqa: ANN002, ANN003 — 桩签名放宽
        self.events.append(("commit", {"message": "", "files": []}))
        return CommitResult(status=CommitStatus.NOTHING_TO_COMMIT, message="nothing staged", commit_hash=None)


def test_nothing_to_commit_with_unapplied_blobs_goes_dead(
    tmp_repo: Path, queue_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    landing, _real = _make_landing(tmp_repo, queue_root)
    nothing = _NothingToCommitStub(landing.worktree_path)
    monkeypatch.setattr(landing, "_gateway", nothing)

    item = cq.enqueue_item(
        "sess-false-done",
        "feat: 假落地回归测试",
        [("docs/guard.txt", b"v2-line")],
        queue_root=queue_root,
    )
    stats = cq.drain_queue(queue_root, landing=landing)

    assert stats["dead"] == 1 and stats["done"] == 0, f"必须死信不得假 ok: {stats}"
    dead = json.loads((queue_root / "dead" / f"{item['qid']}.json").read_text(encoding="utf-8"))
    assert "快照未真应用" in dead.get("dead_reason", ""), dead.get("dead_reason", "")
    # dev 未被推进（无假 landed_id）
    assert _git_text(tmp_repo, "rev-parse", "refs/heads/dev") != (item.get("landed_id") or "unset")


def test_nothing_to_commit_matching_blobs_records_noop_landed_id(
    tmp_repo: Path, queue_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """no-op 落地哨兵（2026-09-16 q-20260916-0004 错位事故）：快照与 HEAD 逐字节一致的
    幂等空转项 done 时 landed_id 必须记 "noop@<old_dev>"，禁止裸记 old_dev——裸记会让
    排查者误以为内容已随他会话提交落库（landed_id 错位归因）。"""
    landing, _real = _make_landing(tmp_repo, queue_root)
    nothing = _NothingToCommitStub(landing.worktree_path)
    monkeypatch.setattr(landing, "_gateway", nothing)

    item = cq.enqueue_item(
        "sess-noop-done",
        "feat: 幂等空转回归测试",
        # 与 dev HEAD 逐字节一致 → 真幂等（读盘字节：fixture 文件在 Windows 盘上为 CRLF）
        [("base.txt", (tmp_repo / "base.txt").read_bytes())],
        queue_root=queue_root,
    )
    stats = cq.drain_queue(queue_root, landing=landing)

    assert stats["done"] == 1 and stats["dead"] == 0, f"真幂等应 done: {stats}"
    done = json.loads((queue_root / "done" / f"{item['qid']}.json").read_text(encoding="utf-8"))
    dev_sha = _git_text(tmp_repo, "rev-parse", "refs/heads/dev")
    assert done.get("landed_id", "").startswith(cql._NOOP_LANDED_PREFIX), done.get("landed_id")
    assert done.get("landed_id") == f"{cql._NOOP_LANDED_PREFIX}{dev_sha}"


def test_already_landed_strips_noop_prefix_for_ancestor_check(
    tmp_repo: Path, queue_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """noop 哨兵重放防循环：_already_landed 必须剥 "noop@" 前缀再做 is-ancestor，
    否则重放项永远判未落盘 → 无限重入队。"""
    landing, _real = _make_landing(tmp_repo, queue_root)
    dev_sha = _git_text(tmp_repo, "rev-parse", "refs/heads/dev")
    assert landing._already_landed({"landed_id": f"{cql._NOOP_LANDED_PREFIX}{dev_sha}"}) == dev_sha
    # 真实不存在的前缀 sha 仍判未落盘
    assert landing._already_landed({"landed_id": f"{cql._NOOP_LANDED_PREFIX}{'0' * 40}"}) is None


class TestPathspecSelfHeal:
    """Mode B 自愈红蓝钉（st-commitspeed-20260916 晚，st-resched-fix/st-auditfix 死信）：
    gateway 首次 commit 报 pathspec did not match（新文件 staging 丢失微因）→
    重放 apply+prestage 后重试须成功。"""

    def test_self_heal_retry_succeeds(self, tmp_repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        import hashlib  # 局部导入：blob sha 计算

        real_gateway = cql.WorktreeLanding(repo_root=tmp_repo, queue_root=tmp_path / "cq_real")
        # 构造：正常 landing 走到 gateway.commit 前，把 gateway.commit 替换为
        # 首次返回 pathspec 失败、重放后放行真 commit 的序列
        import scripts.governance.commit_queue_landing as cql_mod

        landing = cql.WorktreeLanding(repo_root=tmp_repo, queue_root=tmp_path / "cq_sh")
        landing.ensure_worktree()
        gw = landing._get_gateway()
        _sha = hashlib.sha256(b"x=1\n").hexdigest()
        item = {
            "qid": "q-20260916-sess-sh-0001",
            "session_id": "sess-sh",
            "message": "self heal probe",
            "files": [{"path": "sh_new.py", "action": "modify", "blob_sha256": _sha, "blob_ref": f"blobs/{_sha}"}],
        }
        # 种 blob
        (tmp_path / "cq_sh" / "blobs").mkdir(parents=True, exist_ok=True)
        (tmp_path / "cq_sh" / "blobs" / hashlib.sha256(b"x=1\n").hexdigest()).write_bytes(b"x=1\n")
        calls = {"n": 0}
        orig_commit = type(gw).commit

        def flaky_commit(self, *a, **k):
            calls["n"] += 1
            if calls["n"] == 1:
                return gw_mod.CommitResult(
                    status=gw_mod.CommitStatus.COMMIT_FAILED,
                    message="git commit failed: error: pathspec ':(icase)sh_new.py' did not match any file(s) known to git",
                )
            return orig_commit(self, *a, **k)

        from unittest.mock import patch

        with patch.object(type(gw), "commit", flaky_commit):
            result = landing(item, tmp_path / "cq_sh")
        assert result.ok, f"自愈重试后须落地成功: {result.reason}"


class TestUntrackedNewFileLanding:
    """untracked 新文件落地验收（2026-09-18 st-flashspeed-20260918 缺陷包 acceptance ①）。

    缺陷签名（2026-09-17 q-…-0013 等 11 条死信）：含 untracked 新文件的队列项落地时
    `pathspec ':(icase)<新文件>' did not match any file(s) known to git`。根因=SerializerLease
    无续租 + TTL 抢活体持有者 → 并发 drain 争用同一 serializer worktree → thief 的
    _sync_worktree(reset --hard + clean -fd) 删掉 victim 已 materialize 未 commit 的新文件
    （tracked 文件 reset 后仍在盘，故只有新文件死=签名）。lease 治本修复见
    test_commit_queue.py::TestSerializerLease（活体不抢 + renew 心跳）；本类用 pathspec
    保真桩钉住落地侧"新文件正常落地字节级一致"与"一旦被清的确切死信形态"。
    """

    def test_untracked_new_file_lands_byte_identical_via_pathspec(self, tmp_repo: Path, queue_root: Path) -> None:
        """acceptance ①：入队含 untracked 新文件快照 → 落地成功 + blob 字节级一致 + 零自愈重试。"""
        landing, stub = _make_landing_pathspec(tmp_repo, queue_root)
        sid = "sess-newfile-ok"
        content = "新文件 byte-identical 验收\n".encode()
        item = cq.enqueue_item(
            sid, "feat: untracked 新文件落地", [("docs/brand_new.txt", content)], queue_root=queue_root
        )

        stats = cq.drain_queue(queue_root, landing=landing)
        assert stats["done"] == 1 and stats["dead"] == 0, f"新文件落地不应死信: {stats}"
        # pathspec 保真 commit 恰一次（staging 未丢=无需 Mode B 自愈重试）
        assert len(stub.commit_calls()) == 1, "pathspec commit 恰被调一次（零自愈重试）"
        # dev 推进且新文件 blob 字节级一致（pathspec 限定本项，零搭便车）
        assert _dev_commit_count(tmp_repo) == 1
        assert _git_bytes(tmp_repo, "show", "dev:docs/brand_new.txt") == content, "落盘 blob 字节级一致"
        # commit message 含队列标记（POST-COMMIT-GUARD 兼容面）
        marker = cql.queue_marker(sid, item["qid"])
        dev_msg = _git_bytes(tmp_repo, "show", "-s", "--format=%B", "refs/heads/dev").decode("utf-8")
        assert marker in dev_msg
        # done 记录 landed_id == dev HEAD
        landed_id = _git_text(tmp_repo, "rev-parse", "refs/heads/dev")
        done_item = json.loads((queue_root / "done" / f"{item['qid']}.json").read_text(encoding="utf-8"))
        assert done_item["landed_id"] == landed_id

    def test_new_file_wiped_before_commit_reproduces_pathspec_deadletter(
        self, tmp_repo: Path, queue_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """能红证明（harness 保真）：新文件在 prestage 后、commit 前被持续清除 → pathspec
        did-not-match → Mode B 自愈重放仍被清 → 死信带 [诊断]（q-…-0013 取证签名）。

        模拟 thief 的 clean -fd：monkeypatch _prestage_snapshot 在预暂存后删盘上文件
        （每次 materialize 都被清，复现持续竞态）。lease 治本修复令该并发清除永不发生
        （活体持有者不被 TTL 抢 + renew 心跳保鲜）；本测试钉住"一旦发生的确切死信形态"，
        同时证明 pathspec 保真桩对缺陷可见（_StubGateway whole-index commit 对此恒 GREEN）。
        """
        landing, stub = _make_landing_pathspec(tmp_repo, queue_root)
        sid = "sess-newfile-wipe"
        content = b"will be wiped before commit\n"

        real_prestage = landing._prestage_snapshot

        def prestage_then_wipe(item: dict, commit_files: list[str]) -> None:
            real_prestage(item, commit_files)
            # 模拟 thief worktree 竞态清除：删掉刚 materialize+staged 的 untracked 新文件
            for f in commit_files:
                try:
                    os.remove(f)
                except OSError:
                    pass

        monkeypatch.setattr(landing, "_prestage_snapshot", prestage_then_wipe)
        item = cq.enqueue_item(sid, "feat: 必死新文件", [("docs/wiped.txt", content)], queue_root=queue_root)

        stats = cq.drain_queue(queue_root, landing=landing)
        assert stats["dead"] == 1 and stats["done"] == 0, f"新文件被清后应死信: {stats}"
        # 自愈重放后仍败=commit 被调两次（首次 + Mode B 重试）
        assert len(stub.commit_calls()) == 2, f"pathspec 失败触发自愈重试一次: {len(stub.commit_calls())}"
        dead = json.loads((queue_root / "dead" / f"{item['qid']}.json").read_text(encoding="utf-8"))
        reason = dead["dead_reason"]
        assert "did not match" in reason and "pathspec" in reason, f"死信签名=pathspec did-not-match: {reason}"
        assert "[诊断]" in reason, "自愈重试仍败附 git status 诊断（下次可归因）"
        # dev 未被推进（失败项不落盘）
        assert _dev_commit_count(tmp_repo) == 0, "死信项不得推进 dev"


# ---------------------------------------------------------------------------
# 6. 瞬态失败与环境失败分流（2026-09-16 q-…-0009/0010/0011 LOCK_TIMEOUT 死信 +
#    q-…-0013 CAS 重试耗尽死信 治本钉）
# ---------------------------------------------------------------------------


class _LockTimeoutStub(_StubGateway):
    """模拟他会话正持全局提交锁：commit 返回 LOCK_TIMEOUT 且不产生任何 commit。"""

    def commit(self, *args, **kwargs):  # noqa: ANN002, ANN003 — 桩签名放宽
        self.events.append(("commit", {"lock_wait_timeout": kwargs.get("lock_wait_timeout"), "files": []}))
        return CommitResult(
            status=CommitStatus.LOCK_TIMEOUT,
            message="internal error: Cannot acquire global commit lock (timeout 300.0s)",
        )


class TestTransientLockAndCasRetries:
    def test_lock_wait_timeout_is_wired_to_gateway(self, tmp_repo: Path, queue_root: Path) -> None:
        """落地必须把放宽后的锁等待透传给 gateway（缺省 60s 在并发期必然假失败）。"""
        landing, stub = _make_landing(tmp_repo, queue_root)
        assert landing._lock_wait_seconds == cql._LANDING_LOCK_WAIT_SECONDS == 300.0
        cq.enqueue_item("sess-lock-a", "feat: 锁等待接线", [("docs/lw.txt", b"v1\n")], queue_root=queue_root)
        stats = cq.drain_queue(queue_root, landing=landing)
        assert stats["done"] == 1, stats
        assert stub.commit_calls()[0]["lock_wait_timeout"] == 300.0

    def test_lock_timeout_returns_item_to_pending_not_dead(
        self, tmp_repo: Path, queue_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """LOCK_TIMEOUT=瞬态环境失败：项退回 pending、零死信、dev 不推进、claim 已释放。"""
        landing, _stub = _make_landing(tmp_repo, queue_root)
        locky = _LockTimeoutStub(landing.worktree_path)
        monkeypatch.setattr(landing, "_gateway", locky)
        before = _git_text(tmp_repo, "rev-parse", "refs/heads/dev")

        item = cq.enqueue_item("sess-lock-b", "feat: 撞锁项", [("docs/lock.txt", b"v1\n")], queue_root=queue_root)
        stats = cq.drain_queue(queue_root, landing=landing)

        assert stats["dead"] == 0, f"锁争用绝不死信（q-…-0009/0010/0011 事故）: {stats}"
        assert stats["done"] == 0
        assert (queue_root / "pending" / f"{item['qid']}.json").is_file(), "项必须退回 pending 等下次自举"
        assert not list((queue_root / "dead").glob("*.json")), "dead/ 必须空"
        assert not list((queue_root / "processing").glob("*.json")), "processing 不残留"
        assert _git_text(tmp_repo, "rev-parse", "refs/heads/dev") == before, "未落盘不得推进 dev"
        kinds = [kind for kind, _ in locky.events]
        assert kinds == ["claim", "commit", "release"], f"claim 必须释放（否则下次自举撞 CLAIM_REQUIRED）: {kinds}"

    def test_cas_exhaustion_still_dead_letters(
        self, tmp_repo: Path, queue_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """模块 INVARIANT 守住：CAS 重试耗尽仍是死信（不卡队），不是环境失败。"""
        landing, stub = _make_landing(tmp_repo, queue_root)
        monkeypatch.setattr(landing, "_max_cas_retries", 2)

        def _always_conflict(old_sha: str, new_sha: str) -> None:
            raise cql.CasConflict(f"simulated CAS race {old_sha[:8]}->{new_sha[:8]}")

        monkeypatch.setattr(landing, "_advance_dev", _always_conflict)
        # 无同路径重叠 → 走重同步重试分支（有重叠会直接死信，测不到重试上限）
        monkeypatch.setattr(landing, "_changed_paths_between", lambda a, b: set())

        item = cq.enqueue_item("sess-cas-x", "feat: CAS 耗尽", [("docs/cas.txt", b"v1\n")], queue_root=queue_root)
        stats = cq.drain_queue(queue_root, landing=landing)

        assert stats["dead"] == 1 and stats["done"] == 0, stats
        dead = json.loads((queue_root / "dead" / f"{item['qid']}.json").read_text(encoding="utf-8"))
        assert "重试耗尽" in dead["dead_reason"], dead["dead_reason"]
        assert len(stub.commit_calls()) == 2, f"重试次数=上限（{landing._max_cas_retries}）: {len(stub.commit_calls())}"
        assert cql._MAX_CAS_RETRIES == 6, "缺省上限 3→6（q-…-0013 死信实证），改动须同步本钉"

    def test_windows_handle_collision_returns_item_to_pending_not_dead(
        self, tmp_repo: Path, queue_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Windows 句柄占用致 reset --hard unlink 失败=瞬态环境失败：退回 pending、零死信。

        生产实录（q-20260916-st-consrep-20260916-0018，2026-09-16 22:18）：一个只含 13 个
        consensus 文件的合法批次，因外部进程开着 worktree 内某 yaml 的句柄，被
        "landing 异常: RuntimeError" 通道误判物品失败而死信。
        """
        landing, _stub = _make_landing(tmp_repo, queue_root)
        before = _git_text(tmp_repo, "rev-parse", "refs/heads/dev")

        def _handle_collision() -> None:
            raise RuntimeError(
                "git reset --hard refs/heads/dev -> rc=128: error: unable to unlink old "
                "'docs/03_modules/_cross_layer/database/business_data_categories.yaml': "
                "Invalid argument\nfatal: Could not reset index file to revision 'refs/heads/dev'."
            )

        monkeypatch.setattr(landing, "_sync_worktree", _handle_collision)
        item = cq.enqueue_item("sess-hdl-a", "feat: 句柄占用项", [("docs/hdl.txt", b"v1\n")], queue_root=queue_root)
        stats = cq.drain_queue(queue_root, landing=landing)

        assert stats["dead"] == 0, f"句柄占用绝不死信（q-…-0018 事故）: {stats}"
        assert stats["done"] == 0
        assert (queue_root / "pending" / f"{item['qid']}.json").is_file(), "项必须退回 pending 等下次自举"
        assert not list((queue_root / "dead").glob("*.json")), "dead/ 必须空"
        assert not list((queue_root / "processing").glob("*.json")), "processing 不残留"
        assert _git_text(tmp_repo, "rev-parse", "refs/heads/dev") == before, "未落盘不得推进 dev"

    def test_transient_marker_table_covers_handle_and_lock_families(self) -> None:
        """特征串表钉住两族覆盖 + 裸 "Invalid argument" 不算瞬态（太宽会掩盖真 bug）。"""
        for text in (
            "Unable to create 'D:/x/.git/index.lock': File exists.",
            "error: unable to unlink old 'a.yaml': Invalid argument",
            "Permission denied",
            "The process cannot access the file because it is being used by another process",
        ):
            assert cql._is_transient_git_error(text), f"落地侧须归瞬态: {text}"
            assert cq.classify_dead_reason(f"landing 异常: {text}") == "env", f"死因三分类须归 env: {text}"
        assert not cql._is_transient_git_error("快照路径校验拒绝: ../evil（Invalid argument）"), (
            "裸 Invalid argument 不得归瞬态——真 bug 也报它"
        )
        assert (
            cq.classify_dead_reason(
                "landing 异常: RuntimeError: git reset --hard -> rc=128: error: unable to unlink old "
                "'x.yaml': Invalid argument"
            )
            == "env"
        ), "q-…-0018 生产实录死因必须归 env（历史死信 requeue 判读口径）"
        assert set(cql._TRANSIENT_GIT_MARKERS) >= {"index.lock", "unable to unlink", "permission denied"}


# ---------------------------------------------------------------------------
# 8. worktree 环境备置（2026-09-16 fail-open 治本：正门上的门禁/对账须与主区等价）
# ---------------------------------------------------------------------------


def _seed_conn_env(repo: Path) -> None:
    """主仓连接配置就位 + .gitignore 豁免其追踪（对标主仓真源：config/.env.* 与根平铺
    activate_env.ps1 均被忽略——否则备置会让 worktree 变脏，违反 §11 #6 clean 不变量）。

    规则须进 dev 可达的提交：worktree 从 refs/heads/dev 检出，其 .gitignore 决定忽略面。
    """
    (repo / "config").mkdir(parents=True, exist_ok=True)
    (repo / "config" / ".env.postgres").write_text("PGHOST=main\n", encoding="utf-8")
    (repo / "config" / ".env.clickhouse").write_text("CLICKHOUSE_HOST=main\n", encoding="utf-8")
    ig = repo / ".gitignore"
    ig.write_text(ig.read_text(encoding="utf-8") + "config/.env.*\n/activate_env.ps1\n", encoding="utf-8")
    _git(repo, "add", ".gitignore")
    _git(repo, "commit", "-qm", "seed conn env + ignore rules")
    _git(repo, "branch", "-f", "dev")


class TestWorktreeEnvProvisioning:
    def test_fresh_worktree_gets_conn_configs_without_pollution(self, tmp_repo: Path, queue_root: Path) -> None:
        """新建出口：PG+CH 配置 + lookup_audit 备到 worktree，且 worktree 仍 git-clean。"""
        _seed_conn_env(tmp_repo)
        landing, _stub = _make_landing(tmp_repo, queue_root)

        wt = landing.ensure_worktree()

        assert (wt / "config" / ".env.postgres").read_text(encoding="utf-8") == "PGHOST=main\n"
        assert (wt / "config" / ".env.clickhouse").read_text(encoding="utf-8") == "CLICKHOUSE_HOST=main\n"
        assert (wt / ".runtime" / "lookup_audit").is_dir()
        assert _git_text(wt, "status", "--porcelain") == "", "备置产物不得让 worktree 变脏（§11 #6 clean 不变量）"

    def test_reuse_path_reprovisions_rotated_configs(self, tmp_repo: Path, queue_root: Path) -> None:
        """复用出口：主区配置轮换后（worktree 副本被删/过期）每项处理仍重新备置。

        生产常态——worktree 跨 drain 长期存活，第二次起走复用快路径直接 return，
        早于本修复的语义是"永不更新"（旧 worktree 缺配置即永久缺）。
        """
        _seed_conn_env(tmp_repo)
        landing, _stub = _make_landing(tmp_repo, queue_root)
        wt = landing.ensure_worktree()
        assert (wt / "config" / ".env.clickhouse").is_file()

        (wt / "config" / ".env.postgres").unlink()
        (wt / "config" / ".env.clickhouse").unlink()
        assert landing.ensure_worktree() == wt, "已注册且 .git 链接在 → 复用同一路径"

        assert (wt / "config" / ".env.postgres").read_text(encoding="utf-8") == "PGHOST=main\n"
        assert (wt / "config" / ".env.clickhouse").read_text(encoding="utf-8") == "CLICKHOUSE_HOST=main\n"

    def test_source_root_is_the_landing_repo_root(
        self, tmp_repo: Path, queue_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """配置真源=landing.repo_root（非 session_worktree 模块自身 REPO_ROOT 的 import 锚点）。"""
        _seed_conn_env(tmp_repo)
        landing, _stub = _make_landing(tmp_repo, queue_root)
        decoy = tmp_path / "anchored_elsewhere"
        (decoy / "config").mkdir(parents=True)
        (decoy / "config" / ".env.postgres").write_text("PGHOST=decoy\n", encoding="utf-8")
        import scripts.session_worktree as ses

        # 把模块锚点漂到别处：若备置读模块 REPO_ROOT，worktree 会拿到 decoy 内容
        monkeypatch.setattr(ses, "REPO_ROOT", decoy)

        wt = landing.ensure_worktree()

        assert (wt / "config" / ".env.postgres").read_text(encoding="utf-8") == "PGHOST=main\n"

    def test_provisioning_failure_never_blocks_landing(
        self, tmp_repo: Path, queue_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """备置抛错=环境治理不挡施工：worktree 照常就位、落盘照常成功。"""
        landing, _stub = _make_landing(tmp_repo, queue_root)
        import scripts.session_worktree as ses

        monkeypatch.setattr(
            ses, "_provision_worktree_env", lambda *a, **k: (_ for _ in ()).throw(OSError("磁盘不可用"))
        )

        assert landing.ensure_worktree().is_dir(), "备置异常不得阻断 worktree 就位"

        item = cq.enqueue_item("sess-env-a", "feat: 备置异常仍落盘", [("docs/env.txt", b"v\n")], queue_root=queue_root)
        stats = cq.drain_queue(queue_root, landing=landing)

        assert stats["done"] == 1 and stats["dead"] == 0, f"备置异常必须不影响落盘: {stats}"
        assert _dev_commit_count(tmp_repo) == 1
        done_qids = [json.loads(p.read_text(encoding="utf-8"))["qid"] for p in (queue_root / "done").glob("*.json")]
        assert item["qid"] in done_qids

    def test_drain_leads_to_provisioned_worktree(self, tmp_repo: Path, queue_root: Path) -> None:
        """端到端：真 drain 一次（经 _land_item → ensure_worktree）后 worktree 已备置。"""
        _seed_conn_env(tmp_repo)
        landing, _stub = _make_landing(tmp_repo, queue_root)
        cq.enqueue_item("sess-env-b", "feat: 落盘即备置", [("docs/env2.txt", b"v\n")], queue_root=queue_root)

        stats = cq.drain_queue(queue_root, landing=landing)

        assert stats["done"] == 1 and stats["dead"] == 0
        wt = landing.worktree_path
        assert (wt / "config" / ".env.postgres").is_file() and (wt / "config" / ".env.clickhouse").is_file()


# ---------------------------------------------------------------------------
# F2 前置件（2026-09-18 st-flashspeed，判据书 F2「前置（机读）」行）：
# ①「同域同文件双通道并发」压测——lease O_EXCL 单写者物化：并发 drain 争用下
#   零丢失/零死信/零丢失更新/dev 历史全队列标记（双写者窗口=0）；
# ②跨域热文件单通道闸——channel_key_for_files 域映射配置：热文件强制单一热
#   通道、同域同文件双项必同键（=同通道串行，k=4 分区后并发安全的路由前提）；
# ③exit-burst——drain 中途突发注入同轮消化 + lease 释放瞬间双自举竞态零双落。
# ---------------------------------------------------------------------------


class TestF2HotFileChannelGate:
    """F2 前置②：跨域热文件单通道闸（域映射配置在案，纯函数不变量）。"""

    def test_registry_family_routes_to_hot_channel(self) -> None:
        f = "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml"
        assert cq.channel_key_for_files([f]) == cq.HOT_CHANNEL_KEY

    def test_roor_agents_standards_route_to_hot_channel(self) -> None:
        for f in (
            "docs/registry_of_registries.yaml",
            "AGENTS.md",
            "docs/01_policies_and_standards/standards.yaml",
        ):
            assert cq.channel_key_for_files([f]) == cq.HOT_CHANNEL_KEY, f"{f} 应路由热通道"

    def test_hot_wins_over_domain_mix(self) -> None:
        files = ["src/zephyr/alt_data/x.py", "AGENTS.md"]
        assert cq.channel_key_for_files(files) == cq.HOT_CHANNEL_KEY

    def test_same_domain_files_share_one_key(self) -> None:
        k = cq.channel_key_for_files(["src/zephyr/alt_data/a.py", "src/zephyr/alt_data/b.py"])
        assert k == "src/zephyr/alt_data"

    def test_same_domain_same_file_dual_items_get_same_key(self) -> None:
        """核心不变量：同域同文件双队列项必得同键（=同通道串行，双通道并发不撕同域）。"""
        k1 = cq.channel_key_for_files(["src/zephyr/alt_data/cohort.py"])
        k2 = cq.channel_key_for_files(["src/zephyr/alt_data/cohort.py", "src/zephyr/alt_data/util.py"])
        assert k1 == k2 == "src/zephyr/alt_data"

    def test_cross_domain_mix_falls_to_shared_channel(self) -> None:
        assert cq.channel_key_for_files(["scripts/a.py", "docs/b.md"]) == cq.MIXED_CHANNEL_KEY

    def test_windows_backslash_path_normalized(self) -> None:
        f = "docs\\01_policies_and_standards\\_registry\\catalogs\\x.yaml"
        assert cq.channel_key_for_files([f]) == cq.HOT_CHANNEL_KEY


class TestF2SameDomainDualChannelConcurrency:
    """F2 前置①：「同域同文件双通道并发」压测（判据「lease 双写者窗口=0」物化）。

    模拟 k=4 分区后双通道（双 drain 自举）并发处理同域同文件项的竞态：
    O_EXCL lease 保证任一时间点活跃 drainer ≤1，败者退避（LeaseUnavailable），
    零死信、零丢失更新、dev 历史单写者（全 commit 带 [GW:sid:qid] 队列标记）。
    """

    def test_dual_drainer_same_file_no_lost_update_single_writer(self, tmp_repo: Path, queue_root: Path) -> None:
        landing, _stub = _make_landing_pathspec(tmp_repo, queue_root)
        base_sha = _git_text(tmp_repo, "rev-parse", "dev")  # 单写者断言基线（fixture init 笔豁免面）
        # 同域同文件双项（v1→v2，qid 定序）
        it1 = cq.enqueue_item("sess-dc-a", "feat: v1", [("src/mod/hot.py", b"v1\n")], queue_root=queue_root)
        it2 = cq.enqueue_item("sess-dc-b", "feat: v2", [("src/mod/hot.py", b"v2\n")], queue_root=queue_root)
        # 路由前提：同域同文件双项必得同通道键（分区后必串行）
        assert cq.channel_key_for_files(["src/mod/hot.py"]) == cq.channel_key_for_files(["src/mod/hot.py"])

        results: dict[str, object] = {}
        barrier = threading.Barrier(2)

        def _run(name: str) -> None:
            barrier.wait()  # 同时起跑=最大竞态窗口
            try:
                results[name] = cq.drain_queue(queue_root, landing=landing, lease_timeout=0.3)
            except cq.LeaseUnavailable:
                results[name] = "backed-off"

        threads = [threading.Thread(target=_run, args=(f"ch{i}",)) for i in (1, 2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=180)
        assert all(not t.is_alive() for t in threads), "drain 线程未收敛"

        # 败者退避后补排空收敛（自举语义：拿不到等下次）
        final = cq.drain_queue(queue_root, landing=landing)

        all_stats = [s for s in list(results.values()) + [final] if isinstance(s, dict)]
        done_total = sum(s["done"] for s in all_stats)
        dead_total = sum(s["dead"] for s in all_stats)
        assert done_total == 2, f"双项全落地零丢失: results={results} final={final}"
        assert dead_total == 0, f"零死信: results={results} final={final}"
        assert list((queue_root / "pending").glob("q-*.json")) == []
        assert list((queue_root / "processing").glob("q-*.json")) == []
        assert list((queue_root / "dead").glob("q-*.json")) == []

        # 零丢失更新：后项（v2）终态胜出；双 commit 定序落地
        assert _git_bytes(tmp_repo, "show", "dev:src/mod/hot.py") == b"v2\n"
        assert _dev_commit_count(tmp_repo) == 2

        # 单写者不变量：落地窗内 dev 历史全部带队列标记（双写者窗口=0 的历史面证据；
        # since=基线 sha——fixture init 笔是队列前直提，属断言函数的 since 豁免口径）
        assert cql.assert_single_writer_dev_history(tmp_repo, since=base_sha) == []

        # FIFO：v1 commit 是 v2 commit 的祖先（qid 定序未被并发撕乱）
        done1 = json.loads((queue_root / "done" / f"{it1['qid']}.json").read_text(encoding="utf-8"))
        done2 = json.loads((queue_root / "done" / f"{it2['qid']}.json").read_text(encoding="utf-8"))
        r = _git(tmp_repo, "merge-base", "--is-ancestor", done1["landed_id"], done2["landed_id"], check=False)
        assert r.returncode == 0, "it1 落地 commit 必须是 it2 的祖先（同域同文件定序）"


class TestF2ExitBurst:
    """F2 前置③：exit-burst——drain 中途突发注入同轮消化 + lease 释放瞬间双自举竞态。

    病灶面（P2 压测取证）：drain 排空退出瞬间是 lease 释放→再获取的窗口，
    突发入队若错过本轮又遇双自举竞态，最坏=饿死（无人再排）或双落（重复 commit）。
    断言：突发项零丢失（belt 逐项 re-glob 同轮消化或补排空收敛）、双自举零双落、
    dev 历史单写者。
    """

    def test_mid_drain_burst_and_exit_race_zero_loss(self, tmp_repo: Path, queue_root: Path) -> None:
        landing, _stub = _make_landing_pathspec(tmp_repo, queue_root)
        base_sha = _git_text(tmp_repo, "rev-parse", "dev")  # 单写者断言基线
        n_pre, n_burst = 6, 6
        for i in range(n_pre):
            cq.enqueue_item(
                f"sess-burst-p{i}",
                f"feat: pre-{i}",
                [(f"docs/burst/p{i}.txt", f"pre-{i}\n".encode())],
                queue_root=queue_root,
            )

        main_stats: dict[str, object] = {}

        def _main_drain() -> None:
            main_stats["stats"] = cq.drain_queue(queue_root, landing=landing)

        def _burst() -> None:
            # 主 drain 在途时突发注入（belt 逐项 re-glob pending，应同轮消化）
            for j in range(n_burst):
                cq.enqueue_item(
                    f"sess-burst-b{j}",
                    f"feat: burst-{j}",
                    [(f"docs/burst/b{j}.txt", f"burst-{j}\n".encode())],
                    queue_root=queue_root,
                )

        t_main = threading.Thread(target=_main_drain)
        t_burst = threading.Thread(target=_burst)
        t_main.start()
        t_burst.start()
        t_burst.join(timeout=60)
        t_main.join(timeout=300)
        assert not t_main.is_alive(), "主 drain 未收敛"

        # lease 释放瞬间双自举竞态：两个补排空同时起跑，收敛残余且零双落
        final_results: dict[str, object] = {}
        barrier = threading.Barrier(2)

        def _final(name: str) -> None:
            barrier.wait()
            try:
                final_results[name] = cq.drain_queue(queue_root, landing=landing, lease_timeout=0.3)
            except cq.LeaseUnavailable:
                final_results[name] = "backed-off"

        t_f1 = threading.Thread(target=_final, args=("f1",))
        t_f2 = threading.Thread(target=_final, args=("f2",))
        t_f1.start()
        t_f2.start()
        t_f1.join(timeout=300)
        t_f2.join(timeout=300)

        n_total = n_pre + n_burst
        done_files = list((queue_root / "done").glob("q-*.json"))
        assert len(done_files) == n_total, f"{n_total} 项全 done 零丢失: {len(done_files)}"
        assert list((queue_root / "dead").glob("q-*.json")) == [], "零死信"
        assert list((queue_root / "pending").glob("q-*.json")) == [], "pending 排空"
        assert list((queue_root / "processing").glob("q-*.json")) == [], "processing 无孤儿"

        # 零双落：dev 恰 n_total 笔、每项 landed_id 唯一且都在 dev 历史
        assert _dev_commit_count(tmp_repo) == n_total, "零双落（commit 数==项数）"
        landed_ids = [json.loads(p.read_text(encoding="utf-8"))["landed_id"] for p in done_files]
        assert len(set(landed_ids)) == n_total, "landed_id 全唯一（无重复落地）"
        for lid in landed_ids:
            r = _git(tmp_repo, "merge-base", "--is-ancestor", lid, "dev", check=False)
            assert r.returncode == 0, f"landed_id {lid[:12]} 必须在 dev 历史"

        # 单写者不变量（burst+双自举竞态全程落地窗内 dev 历史只经队列通道）
        assert cql.assert_single_writer_dev_history(tmp_repo, since=base_sha) == []


# ---------------------------------------------------------------------------
# 14. 注册表族落地三向合并（W2 治本，2026-09-22 注册表事故——DISPATCH_v1 Lane A）
# 病根：_apply_snapshot 整文件覆盖，陈旧快照 blob 一写抹掉已提交身份（fb5a7821d
# 实证 -103 条）。治本后注册表族（docs/01_policies_and_standards/_registry/catalogs/
# 且 .yaml）落地走条目级三向合并；非注册表维持整文件语义零变更。
# ---------------------------------------------------------------------------

_REG_REL = "docs/01_policies_and_standards/_registry/catalogs/test_w2_registry.yaml"


def _reg_text(entries: list[tuple[str, str]], *, header: str = "title: t\nentries:\n") -> str:
    """构造测试注册表 YAML 文本（条目 = (id, path)）。"""
    lines = [header]
    for eid, path in entries:
        lines.append(f"  - id: {eid}\n    path: {path}\n")
    return "".join(lines)


class TestRegistryThreeWayMergePure:
    """合并纯函数层：DISPATCH W2 四规则 + 三方同键细分 + fail-closed 死信。"""

    BASE = _reg_text([("A", "a.md"), ("B", "b.md"), ("C", "c.md")])

    def _ids(self, text: str) -> list[str]:
        return [e["id"] for e in yaml.safe_load(text)["entries"]]

    def test_both_sides_add_disjoint_entries_both_survive(self):
        ours = self.BASE + "  - id: D\n    path: d.md\n"
        theirs = self.BASE + "  - id: E\n    path: e.md\n"
        merged, err = cql.three_way_merge_registry_yaml(self.BASE, ours, theirs, rel_path=_REG_REL)
        assert err == "", err
        assert set(self._ids(merged)) == {"A", "B", "C", "D", "E"}, "双侧新增零丢失"

    def test_theirs_edit_ours_untouched_adopts_theirs(self):
        theirs = self.BASE.replace("path: a.md", "path: a2.md")
        merged, err = cql.three_way_merge_registry_yaml(self.BASE, self.BASE, theirs, rel_path=_REG_REL)
        assert err == "", err
        a = [e for e in yaml.safe_load(merged)["entries"] if e["id"] == "A"][0]
        assert a["path"] == "a2.md", "ours 未动、theirs 改了 → 采纳 theirs"

    def test_ours_edit_theirs_untouched_keeps_ours(self):
        ours = self.BASE.replace("path: a.md", "path: a-ours.md")
        merged, err = cql.three_way_merge_registry_yaml(self.BASE, ours, self.BASE, rel_path=_REG_REL)
        assert err == "", err
        a = [e for e in yaml.safe_load(merged)["entries"] if e["id"] == "A"][0]
        assert a["path"] == "a-ours.md", "陈旧快照零改动 → ours 修改保留"

    def test_three_way_same_key_edit_dead_letters_with_both_entries(self):
        ours = self.BASE.replace("path: a.md", "path: ours3.md")
        theirs = self.BASE.replace("path: a.md", "path: theirs3.md")
        merged, err = cql.three_way_merge_registry_yaml(self.BASE, ours, theirs, rel_path=_REG_REL)
        assert merged is None, "三方各自改同键 → 死信"
        assert "id=A" in err and "ours (dev)" in err and "theirs (快照)" in err
        assert "ours3.md" in err and "theirs3.md" in err, "dead_reason 带双方条目全文"

    def test_snapshot_delete_does_not_suppress_incumbent(self):
        """规则 c：base 有+ours 有+theirs 无 → 保留 ours（快照侧删除不镇压现役）。"""
        ours = self.BASE + "  - id: D\n    path: d.md\n"
        theirs = _reg_text([("A", "a.md"), ("C", "c.md")])  # theirs 快照缺 B
        merged, err = cql.three_way_merge_registry_yaml(self.BASE, ours, theirs, rel_path=_REG_REL)
        assert err == "", err
        assert {"A", "B", "C", "D"} <= set(self._ids(merged)), "theirs 删 B 不生效（B 现役保留）"

    def test_ours_delete_revived_unless_legitimately_retired(self):
        """规则 b：base 有+ours 无+theirs 有 → 采纳恢复；合法退役（retired_check=True）除外。"""
        ours = _reg_text([("A", "a.md"), ("C", "c.md")])  # ours 侧 B 消失
        merged, err = cql.three_way_merge_registry_yaml(self.BASE, ours, self.BASE, rel_path=_REG_REL)
        assert err == "", err
        assert "B" in self._ids(merged), "ours 侧消失但非退役 → 快照救回"

        merged2, err2 = cql.three_way_merge_registry_yaml(
            self.BASE,
            ours,
            self.BASE,
            rel_path=_REG_REL,
            retired_check=lambda e: e.get("id") == "B",  # 条目引用路径盘上+HEAD 双不存在
        )
        assert err2 == "", err2
        assert "B" not in self._ids(merged2), "合法退役被尊重，不复活"

    def test_structure_drift_dead_letters(self):
        theirs = self.BASE + "newfamily:\n  - id: Z\n"
        merged, err = cql.three_way_merge_registry_yaml(self.BASE, self.BASE, theirs, rel_path=_REG_REL)
        assert merged is None and "结构漂移" in err

    def test_identical_snapshot_short_circuits(self):
        merged, err = cql.three_way_merge_registry_yaml(self.BASE, self.BASE, self.BASE, rel_path=_REG_REL)
        assert err == "" and merged == self.BASE

    def test_multi_family_file_merges_each_family(self):
        base = "meta:\n  v: 1\nentries:\n  - id: A\n    path: a.md\nothers:\n  - name: X\n"
        theirs = base + "  - name: Y\n"
        merged, err = cql.three_way_merge_registry_yaml(base, base, theirs, rel_path=_REG_REL)
        assert err == "", err
        assert yaml.safe_load(merged)["others"] == [{"name": "X"}, {"name": "Y"}]

    def test_unidentifiable_entry_dead_letters_not_silently_merged(self):
        base = "entries:\n  - id: A\n  - scalar_entry\n"
        merged, err = cql.three_way_merge_registry_yaml(base, base, base + "  - id: Z\n", rel_path=_REG_REL)
        assert merged is None, "身份判不了的条目 fail-closed 死信（不静默合并）"
        assert "身份判不了" in err

    def test_schema_metadata_scalar_family_passthrough(self):
        """Lane B THD-ALERT-007 复形（q-0001 死信回归）：顶层 schema 元数据 list
        （unique_key: [字段名]——纯标量族）不参与身份合并，passthrough 保留 ours 原样，
        同文件正常条目族（thresholds）三向合并不受牵连。"""
        base = "unique_key:\n  - threshold_id\nthresholds:\n  - threshold_id: old\n    value: 1\n"
        ours = "unique_key:\n  - threshold_id\nthresholds:\n  - threshold_id: old\n    value: 2\n"
        theirs = (
            "unique_key:\n  - threshold_id\nthresholds:\n  - threshold_id: old\n    value: 1\n"
            "  - threshold_id: fresh\n    value: 86400\n"
        )
        merged, err = cql.three_way_merge_registry_yaml(base, ours, theirs, rel_path=_REG_REL)
        assert err == "", err
        got = yaml.safe_load(merged)
        assert got["unique_key"] == ["threshold_id"], "元数据族原样保留（不判身份不死信）"
        ids = {e["threshold_id"]: e["value"] for e in got["thresholds"]}
        assert ids == {"old": 2, "fresh": 86400}, "正常条目族合并不受牵连（ours 改动保留+theirs 新增插入）"


class TestRegistryMergeCompoundIdentity:
    """W2 热修（q-20260923-st-gateaudit-20260922-0078 实战）：复合身份键。

    实战：HEAD 41 个文件合法持多条 creation_token（同 file 多 token——blueprint 双
    capability/night-gw 新旧并存），gate 首标量字段单键（=file）判「同侧身份键重复」
    误死信。修法：合并器键升级为 `首标量|token=值` 复合（首字段=file 时即 (file, token)，
    与 batch_creation_tokens B22 立法身份同构）；无 token 字段的注册表自动退化单键。
    """

    @staticmethod
    def _tok_reg(entries: list[tuple[str, str]], extra: str = "") -> str:
        lines = ["unique_key:\n  - file\ncreation_tokens:\n"]
        for f, t in entries:
            lines.append(f"  - file: {f}\n    token: {t}\n")
        return "".join(lines) + extra

    def test_same_file_multi_token_coexists_no_deadletter(self):
        """q-0078 实战复形：同 file 双 token 三侧并存 → 合并零死信（旧单键必死信）。"""
        base = self._tok_reg([("src/a.py", "cap-a-20260901"), ("src/a.py", "cap-a-night-gw-20260902")])
        ours = base
        theirs = base + "  - file: src/a.py\n    token: cap-a-third-20260903\n"
        merged, err = cql.three_way_merge_registry_yaml(
            base, ours, theirs, rel_path="capability_canonical_file_registry.yaml"
        )
        assert err == "", f"同 file 多 token 合法形态不得死信: {err}"
        toks = sorted(e["token"] for e in yaml.safe_load(merged)["creation_tokens"])
        assert toks == ["cap-a-20260901", "cap-a-night-gw-20260902", "cap-a-third-20260903"]

    def test_same_file_token_removal_revived_unless_retired(self):
        """复合键粒度下的规则 b/c：同 file 删其中一条 token——非退役救回/退役尊重。"""
        base = self._tok_reg([("src/a.py", "tok-1"), ("src/a.py", "tok-2")])
        ours = self._tok_reg([("src/a.py", "tok-1")])  # ours 侧 tok-2 消失
        theirs = base
        merged, err = cql.three_way_merge_registry_yaml(base, ours, theirs, rel_path="x.yaml")
        assert err == "", err
        toks = [e["token"] for e in yaml.safe_load(merged)["creation_tokens"]]
        assert toks == ["tok-1", "tok-2"], "非退役删除被快照救回（复合键粒度判定）"

        merged2, err2 = cql.three_way_merge_registry_yaml(
            base,
            ours,
            theirs,
            rel_path="x.yaml",
            retired_check=lambda e: e.get("token") == "tok-2",
        )
        assert err2 == "", err2
        toks2 = [e["token"] for e in yaml.safe_load(merged2)["creation_tokens"]]
        assert toks2 == ["tok-1"], "合法退役（复合键定位）被尊重"

    def test_true_duplicate_compound_key_still_deadletters(self):
        """同 file 同 token 两条（复合键下真重复）→ 死信保留（fail-closed 不放松）。"""
        dup = self._tok_reg([("src/a.py", "tok-1"), ("src/a.py", "tok-1")])
        merged, err = cql.three_way_merge_registry_yaml(
            dup, dup, dup + "  - file: b.md\n    token: t2\n", rel_path="x.yaml"
        )
        assert merged is None and "身份不唯一" in err

    def test_token_field_edit_is_same_key_content_conflict(self):
        """复合键不含非 token 字段：改 created_by（非键字段）= 同键内容异语义照旧。"""
        base = self._tok_reg([("src/a.py", "tok-1")])
        ours = base.replace(
            "  - file: src/a.py\n    token: tok-1\n", "  - file: src/a.py\n    token: tok-1\n    created_by: ours\n"
        )
        theirs = base.replace(
            "  - file: src/a.py\n    token: tok-1\n", "  - file: src/a.py\n    token: tok-1\n    created_by: theirs\n"
        )
        merged, err = cql.three_way_merge_registry_yaml(base, ours, theirs, rel_path="x.yaml")
        assert merged is None, "三方各改非键字段（键=复合身份不变）→ 同键内容冲突死信"
        assert "同键条目内容冲突" in err

    def test_no_token_field_registry_degrades_to_single_key(self):
        """无 token 字段的注册表（ruling_id 单键形态）退化为 gate 单键零行为漂移。"""
        base = "entries:\n  - ruling_id: '#1'\n    title: t\n"
        ours = base + "  - ruling_id: '#2'\n    title: u\n"
        theirs = base + "  - ruling_id: '#3'\n    title: v\n"
        merged, err = cql.three_way_merge_registry_yaml(base, ours, theirs, rel_path="x.yaml")
        assert err == "", err
        ids = [e["ruling_id"] for e in yaml.safe_load(merged)["entries"]]
        assert ids == ["#1", "#2", "#3"], "单键退化形态双向新增并存"


class TestRegistryMergeLandingIntegration:
    """集成层：三写者红蓝（DISPATCH 验证判据：A 入队陈旧快照→B 先落地→A 落地，零丢失）。

    注意 tmp_repo fixture 的 HEAD 停在 main（dev 同点创建不检出）——「队列外写者
    推进 dev」的直提统一走 _advance_dev_ref（update-ref dev 搬运 HEAD），否则提交
    落 main、dev 纹丝不动，合并器 ours 侧读到 init 提交的「文件不存在」。
    写盘统一 newline="\n" 钉 LF——Windows 默认会把 \n 翻成 \r\n，而入队快照
    encode() 是纯 LF，两侧行尾漂移会污染字节级一致性判定。
    """

    def _init_registry(self, tmp_repo: Path, base_text: str) -> str:
        reg_dir = tmp_repo / "docs/01_policies_and_standards/_registry/catalogs"
        reg_dir.mkdir(parents=True, exist_ok=True)
        (tmp_repo / _REG_REL).write_text(base_text, encoding="utf-8", newline="\n")
        _git(tmp_repo, "add", ".")
        _git(tmp_repo, "commit", "-qm", "init registry")
        # fixture 的 HEAD 停在 main——commit 落 main，dev 仍指无 registry 的 init 提交；
        # 先把 dev 搬到当前 HEAD 再取 base（否则 base_head 树里根本没有 registry 文件）
        self._advance_dev_ref(tmp_repo)
        return _git_text(tmp_repo, "rev-parse", "refs/heads/dev")

    def _advance_dev_ref(self, tmp_repo: Path) -> str:
        """模拟队列外写者：把刚落在 HEAD（main）的直提搬成 dev 的新值。"""
        sha = _git_text(tmp_repo, "rev-parse", "HEAD")
        _git(tmp_repo, "update-ref", "refs/heads/dev", sha)
        return sha

    def test_three_writer_scenario_zero_loss(self, tmp_repo: Path, queue_root: Path) -> None:
        base_text = _reg_text([("A", "a.md"), ("B", "b.md"), ("C", "c.md")])
        base_sha = self._init_registry(tmp_repo, base_text)

        # 写者 A：基于 base 快照入队（A 改名 + E 新增）——此刻 dev 尚未推进
        snapshot_a = base_text.replace("path: a.md", "path: a2.md") + "  - id: E\n    path: e.md\n"
        cq.enqueue_item(
            "sess-reg-a",
            "feat: A 批（快照含 A 改名+E 新增）",
            [(_REG_REL, snapshot_a.encode("utf-8"))],
            queue_root=queue_root,
            options=cq.EnqueueOptions(base_head=base_sha),
        )

        # 写者 B：队列外直接推进 dev（B 改名 + D 新增）——制造 base..dev 同路径漂移
        drift_text = base_text.replace("path: b.md", "path: b2.md") + "  - id: D\n    path: d.md\n"
        (tmp_repo / _REG_REL).write_text(drift_text, encoding="utf-8", newline="\n")
        _git(tmp_repo, "add", _REG_REL)
        _git(tmp_repo, "commit", "-qm", "B 批直提（B 改名+D 新增）")
        self._advance_dev_ref(tmp_repo)

        # A 的陈旧快照落地：W2 合并后 A'/B'/C/D/E 全存活——fb5a7821d 型整文件覆盖被治本
        landing, stub = _make_landing(tmp_repo, queue_root)
        stats = cq.drain_queue(queue_root, landing=landing)
        assert stats["done"] == 1 and stats["dead"] == 0, f"drain 统计异常: {stats}"

        landed = yaml.safe_load(_git_bytes(tmp_repo, "show", f"dev:{_REG_REL}").decode("utf-8"))
        by_id = {e["id"]: e for e in landed["entries"]}
        assert by_id["A"]["path"] == "a2.md", "A 的快照修改（theirs 改、ours 侧没动 A）被采纳"
        assert by_id["B"]["path"] == "b2.md", "B 的 dev 修改不被陈旧快照镇压"
        assert by_id["C"]["path"] == "c.md", "未涉条目原样"
        assert by_id["D"]["path"] == "d.md", "dev 侧新增 D 不被快照抹掉（事故主症状）"
        assert by_id["E"]["path"] == "e.md", "快照侧新增 E 落地"
        assert len(by_id) == 5, "五条目零丢失"
        assert len(stub.commit_calls()) == 1, "gateway 恰一次 commit"

    def test_same_key_three_way_conflict_dead_letters_content_preserved(self, tmp_repo: Path, queue_root: Path) -> None:
        base_text = _reg_text([("A", "a.md")])
        base_sha = self._init_registry(tmp_repo, base_text)

        snapshot = base_text.replace("path: a.md", "path: theirs.md")
        cq.enqueue_item(
            "sess-reg-c",
            "feat: 同键三方冲突项",
            [(_REG_REL, snapshot.encode("utf-8"))],
            queue_root=queue_root,
            options=cq.EnqueueOptions(base_head=base_sha),
        )
        (tmp_repo / _REG_REL).write_text(
            base_text.replace("path: a.md", "path: ours.md"), encoding="utf-8", newline="\n"
        )
        _git(tmp_repo, "add", _REG_REL)
        _git(tmp_repo, "commit", "-qm", "ours 改 A")
        self._advance_dev_ref(tmp_repo)

        landing, stub = _make_landing(tmp_repo, queue_root)
        stats = cq.drain_queue(queue_root, landing=landing)
        assert stats["dead"] == 1 and stats["done"] == 0, f"同键三方冲突必须死信: {stats}"
        dead = json.loads(next((queue_root / "dead").glob("q-*.json")).read_text(encoding="utf-8"))
        assert "id=A" in dead["dead_reason"] and "ours.md" in dead["dead_reason"]
        assert "theirs.md" in dead["dead_reason"], "死信带双方条目全文"
        # dev 侧内容原样保留（死信不产生任何写入）
        assert _git_bytes(tmp_repo, "show", f"dev:{_REG_REL}").decode("utf-8") == base_text.replace(
            "path: a.md", "path: ours.md"
        )
        assert stub.commit_calls() == [], "死信不得触达 gateway commit"

    def test_non_registry_file_still_path_conflict_dead(self, tmp_repo: Path, queue_root: Path) -> None:
        """非注册表文件零变更验证：base..dev 触及同路径照旧逐文件快进死信。"""
        (tmp_repo / "docs").mkdir(exist_ok=True)
        (tmp_repo / "docs/plain.txt").write_text("base\n", encoding="utf-8", newline="\n")
        _git(tmp_repo, "add", ".")
        _git(tmp_repo, "commit", "-qm", "plain base")
        base = _git_text(tmp_repo, "rev-parse", "refs/heads/dev")
        cq.enqueue_item(
            "sess-reg-n",
            "feat: 普通文件冲突项",
            [("docs/plain.txt", b"mine\n")],
            queue_root=queue_root,
            options=cq.EnqueueOptions(base_head=base),
        )
        (tmp_repo / "docs/plain.txt").write_text("theirs-dev\n", encoding="utf-8", newline="\n")
        _git(tmp_repo, "add", "docs/plain.txt")
        _git(tmp_repo, "commit", "-qm", "dev 侧推进 plain.txt")
        self._advance_dev_ref(tmp_repo)
        landing, _ = _make_landing(tmp_repo, queue_root)
        stats = cq.drain_queue(queue_root, landing=landing)
        assert stats["dead"] == 1, "非注册表路径冲突照旧死信（零变更）"
        dead = json.loads(next((queue_root / "dead").glob("q-*.json")).read_text(encoding="utf-8"))
        assert "冲突" in dead["dead_reason"]

    def test_registry_path_drift_no_longer_path_conflicts(self, tmp_repo: Path, queue_root: Path) -> None:
        """W2 配套：注册表族路径 base..dev 漂移不再触发 path 级死信（交合并器消化）。"""
        base_text = _reg_text([("A", "a.md")])
        base_sha = self._init_registry(tmp_repo, base_text)
        cq.enqueue_item(
            "sess-reg-d",
            "feat: 注册表同路径漂移项",
            [(_REG_REL, base_text.encode("utf-8"))],
            queue_root=queue_root,
            options=cq.EnqueueOptions(base_head=base_sha),
        )
        (tmp_repo / _REG_REL).write_text(base_text.replace("path: a.md", "path: b.md"), encoding="utf-8", newline="\n")
        _git(tmp_repo, "add", _REG_REL)
        _git(tmp_repo, "commit", "-qm", "dev 侧推进注册表")
        self._advance_dev_ref(tmp_repo)
        landing, _ = _make_landing(tmp_repo, queue_root)
        stats = cq.drain_queue(queue_root, landing=landing)
        assert stats["done"] == 1 and stats["dead"] == 0, f"注册表路径漂移交合并器: {stats}"
        landed = yaml.safe_load(_git_bytes(tmp_repo, "show", f"dev:{_REG_REL}").decode("utf-8"))
        assert landed["entries"][0]["path"] == "b.md", "dev 侧修改保留（快照=base 零改动不回滚）"

    def test_ours_retirement_honored_via_real_path_check(self, tmp_repo: Path, queue_root: Path) -> None:
        """retired_check 真实路径版：条目引用文件 dev 侧已真退役（盘上+HEAD 双无）→ 不复活。"""
        base_text = _reg_text([("A", "a.md"), ("B", "retired_doc.md")])
        base_sha = self._init_registry(tmp_repo, base_text)
        (tmp_repo / "retired_doc.md").write_text("to be retired\n", encoding="utf-8", newline="\n")
        _git(tmp_repo, "add", ".")
        _git(tmp_repo, "commit", "-qm", "add doc")
        base_sha2 = _git_text(tmp_repo, "rev-parse", "refs/heads/dev")
        self._advance_dev_ref(tmp_repo)

        # dev 侧：删掉 B 条目 + 删掉其引用文件（真退役）
        ours_text = _reg_text([("A", "a.md")])
        (tmp_repo / _REG_REL).write_text(ours_text, encoding="utf-8", newline="\n")
        (tmp_repo / "retired_doc.md").unlink()
        _git(tmp_repo, "add", "-A")
        _git(tmp_repo, "commit", "-qm", "B 真退役（条目+文件双删）")
        self._advance_dev_ref(tmp_repo)

        # 快照（base_sha2 时点，仍含 B）落地 → B 引用文件已双不存在 → 尊重退役不复活
        cq.enqueue_item(
            "sess-reg-e",
            "feat: 陈旧快照含已退役条目",
            [(_REG_REL, base_text.encode("utf-8"))],
            queue_root=queue_root,
            options=cq.EnqueueOptions(base_head=base_sha2),
        )
        landing, _ = _make_landing(tmp_repo, queue_root)
        stats = cq.drain_queue(queue_root, landing=landing)
        assert stats["done"] == 1 and stats["dead"] == 0, f"drain 异常: {stats}"
        landed = yaml.safe_load(_git_bytes(tmp_repo, "show", f"dev:{_REG_REL}").decode("utf-8"))
        assert "B" not in [e["id"] for e in landed["entries"]], "真退役条目不被快照复活"
