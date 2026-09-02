# [A_test] module_id: MOD-GOV-047 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-047 | scripts/governance/commit_queue_landing.py | §
# [MODULE] tests.governance.test_commit_queue_integration
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; scripts.commit_queue; scripts.governance.commit_queue_landing; zephyr.gov_enforcement.rule_bridge.git_commit_gateway; zephyr.security.access_control.session_concurrency
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/test_commit_queue_integration.py
# [MATURITY] testing
# [INVARIANTS] 全 tmp git 仓 + tmp 队列隔离（绝不碰主仓 .runtime/commit_queue 与真实 dev/main）；真落盘零丢失/零搭便车/FIFO/死信归因/幂等不双落
# [MODIFY-GUARD] 66 号 §6.3 MVP 形态 + §8 幂等 + §10 验收口径 + §11 #1/#2/#4/#6；08 号文 §4.2 步骤 3/5 验收行
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] permanent
"""test_commit_queue_integration.py — 提交队列 MVP B 段集成验收（08 号文 §4.2 步骤 3/5 + 66 号 §10/§11）。

断言清单真源：
1. 66 号 §10 MVP 行（worktree_landing 真落盘）：3 会话并发 50 提交——零丢失（done 数==有效
   入队数）、零搭便车（逐 commit `git show` 内容 == 入队快照 hash 比对）、FIFO 序
   （拓扑序 == qid 序）、死信正确归因、无 [GW:*:overlap] 标记混入。
2. 66 号 §11 #2 故障注入（worktree 落盘层）：landing 中途 kill（update-ref 前/后两个注入
   点）→ 下次自举幂等续跑——is-ancestor/标记判定不产生重复 commit（A 段已覆盖队列层孤儿
   回收，本段补落盘层）。
3. 66 号 §11 #4 门禁等价性抽查 5 门：DIRECTORY-CONTRACT / FOREIGN-CHANGE-DETECTION /
   ENCODING-SAFETY / R5-DIGIT-SUFFIX（naming）/ TTL-METADATA（frontmatter）——同一快照
   在专用 worktree 内与主工作区同判（PASS/FAIL 两态各验）。
4. 66 号 §11 #6：连续 3 项同文件落盘，每项处理前 worktree HEAD == dev HEAD 且工作区 clean。
5. 08 号文 §4.2 步骤 5 + 66 号 §7：flag OFF（默认）_commit_auto 直提不变（回归钉住）；
   flag ON 改道 enqueue（mock 验证不真实落盘）；flag 设施异常 fail-closed OFF。
6. 单写者不变量断言函数：flag ON 后 dev 历史只经 Serializer 通道（[GW:*:q-*] 标记）——
   供 Owner 启用后验证。
7. REFERENCE-TRANSACTION-GUARD / POST-COMMIT-GUARD 对 [GW:{sid}:{qid}] 标记不拦
   （真 hook 装入 tmp 仓 .git/hooks 实证），且无标记 plumbing 更新仍被阻断（回归既有防护）。
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import threading
from pathlib import Path

import pytest

import scripts.commit_queue as cq
import scripts.governance.commit_queue_landing as cql
import zephyr.gov_enforcement.rule_bridge.git_commit_gateway as gw_mod
from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (
    CommitStatus,
    GitCommitGateway,
)
from zephyr.security.access_control.session_concurrency import SessionRegistry

# ---------------------------------------------------------------------------
# 基础工具
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
_HOOKS_SRC = REPO_ROOT / "scripts" / "governance" / "git_hooks"


def _git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    """tmp 仓 git 执行（字节安全：commit 内容比对走 bytes）。

    无管道模式（2026-08-23 假死治本）：stdout/stderr 落临时文件而非 PIPE——
    Windows 下 git worktree/hook 链衍生的孙进程（sh.exe 等）继承管道写句柄
    且可能活得比 git 久，PIPE 模式 communicate() 等 EOF 永不返回（C 级阻塞，
    pytest-timeout thread 法杀不动；run 超时 kill 直子后的二次 communicate
    同样堵死）。文件读取不依赖句柄继承链，kill 后无需二次 communicate。
    """
    out_fd, out_path = tempfile.mkstemp(prefix="zcqt_git_out_", suffix=".log")
    err_fd, err_path = tempfile.mkstemp(prefix="zcqt_git_err_", suffix=".log")
    proc: subprocess.Popen | None = None
    try:
        with os.fdopen(out_fd, "wb") as out_f, os.fdopen(err_fd, "wb") as err_f:
            proc = subprocess.Popen(
                ["git", *args],
                cwd=str(cwd),
                stdin=subprocess.DEVNULL,
                stdout=out_f,
                stderr=err_f,
            )
            try:
                proc.wait(timeout=60)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=10)
                raise AssertionError(f"git {' '.join(args)} -> timeout after 60s (killed)") from None
        stdout = Path(out_path).read_bytes()
        stderr = Path(err_path).read_bytes()
    finally:
        for p in (out_path, err_path):
            try:
                os.unlink(p)
            except OSError:  # 孙进程仍持有句柄时 Windows 禁删——留 %TEMP% 由系统清理
                pass
    r = subprocess.CompletedProcess(["git", *args], proc.returncode, stdout, stderr)
    if check and r.returncode != 0:
        raise AssertionError(
            f"git {' '.join(args)} -> rc={r.returncode}: {r.stderr.decode('utf-8', errors='replace')[:400]}"
        )
    return r


def _git_text(cwd: Path, *args: str) -> str:
    return _git(cwd, *args).stdout.decode("utf-8", errors="replace").strip()


def _git_bytes(cwd: Path, *args: str) -> bytes:
    return _git(cwd, *args).stdout


@pytest.fixture()
def tmp_repo(tmp_path: Path) -> Path:
    """裸 git 仓：main 分支持初始提交，dev 分支同点（worktree 落盘目标）。

    core.autocrlf=false——内容字节级比对不受行尾转换干扰。
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "test")
    _git(repo, "config", "core.autocrlf", "false")
    # 与主仓 .gitignore 对齐：运行时目录豁免——worktree 内网关写 .runtime/.ailocks
    # 属运行时产物（66 号 §11 #6 的 clean 断言依赖此豁免，生产同理）
    (repo / ".gitignore").write_text(".runtime/\n.ailocks/\n", encoding="utf-8")
    (repo / "base.txt").write_text("base\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-qm", "init")
    _git(repo, "branch", "dev")
    return repo


@pytest.fixture()
def queue_root(tmp_path: Path) -> Path:
    return tmp_path / "commit_queue"


@pytest.fixture()
def sessions(tmp_repo: Path) -> list[str]:
    """3 生产者会话（sess- 前缀——POST-COMMIT-GUARD sed 解析要求）注册到主仓 registry。"""
    reg = SessionRegistry(tmp_repo)
    sids = ["sess-qint-a", "sess-qint-b", "sess-qint-c"]
    for sid in sids:
        reg.register(sid)
    return sids


@pytest.fixture()
def landing(tmp_repo: Path, queue_root: Path) -> cql.WorktreeLanding:
    return cql.WorktreeLanding(repo_root=tmp_repo, queue_root=queue_root)


def _qid_of(message: str) -> str:
    """从 commit message 提取队列标记中的 qid（[GW:{sid}:{qid}]）。"""
    m = re.search(r"\[GW:[^:\]]+:(q-[^\]]+)\]", message)
    assert m, f"commit message 缺队列标记: {message!r}"
    return m.group(1)


def _dev_commits(repo: Path) -> list[tuple[str, str]]:
    """dev 在初始提交之后的全部 commit（拓扑正序）：[(sha, message), ...]"""
    base = _git_text(repo, "rev-list", "--max-parents=0", "dev")
    shas = _git_text(repo, "rev-list", "--reverse", f"{base}..dev")
    if not shas:
        return []
    out = []
    for sha in shas.splitlines():
        msg = _git_bytes(repo, "show", "-s", "--format=%B", sha).decode("utf-8", errors="replace")
        out.append((sha, msg))
    return out


# ---------------------------------------------------------------------------
# 66 号 §10 MVP 行：3 会话并发 50 提交真落盘——零丢失/零搭便车/FIFO/死信归因
# ---------------------------------------------------------------------------


class TestRealLanding50Commits:
    def test_3_sessions_50_commits_zero_loss_fifo_no_piggyback(
        self, tmp_repo: Path, queue_root: Path, sessions: list[str], landing: cql.WorktreeLanding
    ) -> None:
        shards = [range(0, 17), range(17, 34), range(34, 50)]  # 共 50 项
        # {qid: (path, content)}——入队快照真值，落盘后逐 commit 比对
        truth: dict[str, tuple[str, bytes]] = {}
        qids: list[str] = []
        errors: list[BaseException] = []
        lock = threading.Lock()

        def worker(sid: str, indices: range) -> None:
            for i in indices:
                try:
                    # 每会话独立文件（docs/sess-x/ 前缀）——本用例不触发跨会话冲突
                    path = f"docs/{sid}/f{i:03d}.txt"
                    content = f"content-{sid}-{i}\n".encode()
                    item = cq.enqueue_item(sid, f"msg {sid} #{i}", [(path, content)], queue_root=queue_root)
                    with lock:
                        qids.append(item["qid"])
                        truth[item["qid"]] = (path, content)
                except BaseException as exc:  # noqa: BLE001 - 测试收集一切异常
                    with lock:
                        errors.append(exc)

        threads = [threading.Thread(target=worker, args=(sid, idx)) for sid, idx in zip(sessions, shards, strict=True)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert not errors, f"并发 enqueue 异常: {errors}"
        assert len(qids) == 50 and len(set(qids)) == 50, "50 个 enqueue 不丢不重"

        stats = cq.drain_queue(queue_root, landing=landing)
        # 零丢失：done 数 == 有效入队数（66 号 §10 MVP 行）
        assert stats["done"] == 50 and stats["dead"] == 0, f"drain 统计异常: {stats}"

        commits = _dev_commits(tmp_repo)
        assert len(commits) == 50, "dev 新增 commit 数 == 入队数"

        # FIFO 序：dev 拓扑序 == qid 单调序（66 号 §10）
        commit_qids = [_qid_of(msg) for _, msg in commits]
        assert commit_qids == sorted(qids), "FIFO 破裂：dev commit 序 != qid 序"

        for sha, msg in commits:
            qid = _qid_of(msg)
            path, content = truth[qid]
            # 标记合规：[GW:{sid}:{qid}] + 网关 [GW:{sid}] 尾标；无 overlap 混入（66 号 §11 #1）
            assert re.search(r"\[GW:sess-qint-[abc]\]", msg), f"缺网关尾标: {msg!r}"
            assert "[GW:" in msg and ":overlap]" not in msg, "overlap 标记混入队列 commit"
            # 零搭便车：commit 触及文件恰为队列项文件（pathspec 限定，无搭车）
            touched = _git_text(tmp_repo, "show", "--format=", "--name-only", sha).splitlines()
            assert touched == [path], f"搭便车检出: {qid} 触及 {touched}"
            # 逐 commit 内容 == 入队快照（字节级）
            landed = _git_bytes(tmp_repo, "show", f"{sha}:{path}")
            assert landed == content, f"内容漂移: {qid}"
            # 快照 hash 比对（66 号 §10：逐 commit hash == 入队快照 hash）
            blob_sha = hashlib.sha256(content).hexdigest()
            done_item = json.loads((queue_root / "done" / f"{qid}.json").read_text(encoding="utf-8"))
            assert done_item["files"][0]["blob_sha256"] == blob_sha
            assert done_item["landed_id"] == sha, "done 记录 landed_id == 真实 commit sha"

        # 终态：pending/processing 清空；serializer 分支与 dev 同点且工作区干净（66 号 §11 #6 终态）
        assert not list((queue_root / "pending").glob("q-*.json"))
        assert not list((queue_root / "processing").glob("q-*.json"))
        wt = landing.worktree_path
        assert _git_text(wt, "rev-parse", "HEAD") == _git_text(tmp_repo, "rev-parse", "refs/heads/dev")
        assert _git_text(wt, "status", "--porcelain") == ""


# ---------------------------------------------------------------------------
# 66 号 §11 #6：连续同文件落盘的 worktree 同步不变量（每项处理前 HEAD==dev 且 clean）
# ---------------------------------------------------------------------------


class TestWorktreeSyncInvariant:
    def test_sequential_same_file_items_keep_worktree_synced(
        self, tmp_repo: Path, queue_root: Path, sessions: list[str], landing: cql.WorktreeLanding
    ) -> None:
        sid = sessions[0]
        landing.ensure_worktree()
        wt = landing.worktree_path
        for v in ("v1", "v2", "v3"):
            cq.enqueue_item(sid, f"update {v}", [("docs/same.txt", f"{v}\n".encode())], queue_root=queue_root)
            # 每项处理前：worktree HEAD == 当前 dev HEAD 且工作区 clean（66 号 §11 #6 原文断言）
            assert _git_text(wt, "rev-parse", "HEAD") == _git_text(tmp_repo, "rev-parse", "refs/heads/dev")
            assert _git_text(wt, "status", "--porcelain") == ""
            stats = cq.drain_queue(queue_root, landing=landing)
            assert stats["done"] == 1 and stats["dead"] == 0
        # 同键 3 连落盘：dev 上 3 个 commit 按序推进，终态为 v3
        commits = _dev_commits(tmp_repo)
        assert len(commits) == 3
        assert _git_bytes(tmp_repo, "show", "dev:docs/same.txt") == b"v3\n"


# ---------------------------------------------------------------------------
# 66 号 §11 #2（worktree 落盘层）故障注入：kill → 幂等续跑无双落
# ---------------------------------------------------------------------------


class _SimulatedCrash(BaseException):
    """模拟 Serializer 进程被杀（BaseException——drain 不捕获，项留 processing 等回收）。"""


class TestCrashRecoveryWorktreeLayer:
    def test_kill_after_dev_advance_resume_without_double_commit(
        self, tmp_repo: Path, queue_root: Path, sessions: list[str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """注入点①：update-ref 推进 dev 成功之后、done 落盘之前 kill。

        恢复路径：孤儿回收 → landing 幂等判定（标记 grep + is-ancestor）命中 →
        直接 MarkDone 不重跑 commit——dev 上同 qid 仅 1 个 commit。
        """
        landing = cql.WorktreeLanding(repo_root=tmp_repo, queue_root=queue_root)
        item = cq.enqueue_item(sessions[0], "crash after advance", [("docs/c1.txt", b"c1\n")], queue_root=queue_root)
        orig_advance = landing._advance_dev

        def killer_advance(old_sha: str, new_sha: str) -> None:
            orig_advance(old_sha, new_sha)  # dev 已推进
            raise _SimulatedCrash("killed after dev advance")

        monkeypatch.setattr(landing, "_advance_dev", killer_advance)
        with pytest.raises(_SimulatedCrash):
            cq.drain_queue(queue_root, landing=landing)
        # 崩溃现场：dev 已有 commit，项留 processing
        assert len(_dev_commits(tmp_repo)) == 1
        assert list((queue_root / "processing").glob("q-*.json"))

        monkeypatch.undo()
        stats = cq.drain_queue(queue_root, landing=landing)
        assert stats["recovered"] == 1 and stats["done"] == 1 and stats["dead"] == 0
        commits = _dev_commits(tmp_repo)
        assert len(commits) == 1, "幂等续跑不得产生第二个 commit（无双落）"
        done_item = json.loads((queue_root / "done" / f"{item['qid']}.json").read_text(encoding="utf-8"))
        assert done_item["landed_id"] == commits[0][0], "landed_id 复用已落 commit（is-ancestor 判定）"

    def test_kill_before_dev_advance_resume_lands_exactly_once(
        self, tmp_repo: Path, queue_root: Path, sessions: list[str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """注入点②：gateway commit 成功之后、update-ref 之前 kill（serializer 分支留孤儿 commit）。

        恢复路径：标记不在 dev → 重新同步（reset --hard 弃孤儿）→ 重落 → dev 恰 1 个 commit。
        """
        landing = cql.WorktreeLanding(repo_root=tmp_repo, queue_root=queue_root)
        cq.enqueue_item(sessions[1], "crash before advance", [("docs/c2.txt", b"c2\n")], queue_root=queue_root)

        def killer_advance(old_sha: str, new_sha: str) -> None:
            raise _SimulatedCrash("killed before dev advance")

        monkeypatch.setattr(landing, "_advance_dev", killer_advance)
        with pytest.raises(_SimulatedCrash):
            cq.drain_queue(queue_root, landing=landing)
        assert len(_dev_commits(tmp_repo)) == 0, "崩溃点 dev 尚未推进"

        monkeypatch.undo()
        stats = cq.drain_queue(queue_root, landing=landing)
        assert stats["recovered"] == 1 and stats["done"] == 1 and stats["dead"] == 0
        commits = _dev_commits(tmp_repo)
        assert len(commits) == 1, "重落恰一次（孤儿 commit 已被 reset --hard 遗弃，不进 dev）"
        assert _git_bytes(tmp_repo, "show", "dev:docs/c2.txt") == b"c2\n"


# ---------------------------------------------------------------------------
# 66 号 §6.4 冲突判定与死信归因 + 不卡队；blob 缺失死信；delete action 落盘
# ---------------------------------------------------------------------------


class TestDeadLetterAttribution:
    def test_base_head_conflict_goes_dead_and_queue_continues(
        self, tmp_repo: Path, queue_root: Path, sessions: list[str], landing: cql.WorktreeLanding
    ) -> None:
        base = _git_text(tmp_repo, "rev-parse", "refs/heads/dev")
        item1 = cq.enqueue_item(
            sessions[0],
            "conflicting",
            [("docs/a.txt", b"mine\n")],
            queue_root=queue_root,
            options=cq.EnqueueOptions(base_head=base),
        )
        item2 = cq.enqueue_item(sessions[1], "disjoint", [("docs/b.txt", b"other\n")], queue_root=queue_root)
        # 入队后 dev 被直提推进且触及同路径（flag OFF 期第二写入者形态模拟）
        (tmp_repo / "docs").mkdir(exist_ok=True)
        (tmp_repo / "docs" / "a.txt").write_bytes(b"theirs\n")  # write_bytes 防 Windows 文本模式 \r\n 转换
        _git(tmp_repo, "add", "docs/a.txt")
        _git(tmp_repo, "commit", "-qm", "direct writer touches same file")
        _git(tmp_repo, "branch", "-f", "dev", "HEAD")

        stats = cq.drain_queue(queue_root, landing=landing)
        assert stats["dead"] == 1 and stats["done"] == 1, "冲突项死信 + 后续项正常落盘（不卡队）"
        dead_item = json.loads((queue_root / "dead" / f"{item1['qid']}.json").read_text(encoding="utf-8"))
        assert "冲突" in dead_item["dead_reason"] and "docs/a.txt" in dead_item["dead_reason"], (
            f"死信正确归因（66 号 §10）：{dead_item['dead_reason']}"
        )
        # 冲突项内容未落 dev（不得静默覆盖他人推进）
        assert _git_bytes(tmp_repo, "show", "dev:docs/a.txt") == b"theirs\n"
        # 后续无冲突项正常落盘
        assert _git_bytes(tmp_repo, "show", "dev:docs/b.txt") == b"other\n"

    def test_missing_blob_goes_dead(
        self, tmp_repo: Path, queue_root: Path, sessions: list[str], landing: cql.WorktreeLanding
    ) -> None:
        item = cq.enqueue_item(sessions[0], "doomed", [("docs/x.txt", b"x\n")], queue_root=queue_root)
        os.remove(queue_root / "blobs" / item["files"][0]["blob_sha256"])  # 人为损坏
        stats = cq.drain_queue(queue_root, landing=landing)
        assert stats["dead"] == 1 and stats["done"] == 0
        dead_item = json.loads((queue_root / "dead" / f"{item['qid']}.json").read_text(encoding="utf-8"))
        assert "blob" in dead_item["dead_reason"].lower()
        assert not _dev_commits(tmp_repo), "死信项不得落盘"

    def test_delete_action_removes_file_on_dev(
        self, tmp_repo: Path, queue_root: Path, sessions: list[str], landing: cql.WorktreeLanding
    ) -> None:
        # 先落一个文件，再入队删除项
        cq.enqueue_item(sessions[0], "add doomed", [("docs/doomed.txt", b"gone\n")], queue_root=queue_root)
        cq.drain_queue(queue_root, landing=landing)
        assert _git_bytes(tmp_repo, "show", "dev:docs/doomed.txt") == b"gone\n"

        item = cq.enqueue_item(
            sessions[0],
            "remove doomed",
            [],
            queue_root=queue_root,
            options=cq.EnqueueOptions(deletes=["docs/doomed.txt"]),
        )
        assert item["files"][0]["action"] == "delete"
        stats = cq.drain_queue(queue_root, landing=landing)
        assert stats["done"] == 1 and stats["dead"] == 0
        assert _git(tmp_repo, "ls-tree", "dev", "docs/doomed.txt").stdout.strip() == b"", "删除项落盘"


# ---------------------------------------------------------------------------
# 08 号文 §4.2 步骤 3 验收：REFERENCE-TRANSACTION-GUARD / POST-COMMIT-GUARD 不拦队列 commit
# ---------------------------------------------------------------------------


@pytest.fixture()
def repo_with_hooks(tmp_repo: Path) -> Path:
    """装入两个真 guard hook（git for Windows 自带 sh 执行 .sh hook）。"""
    hooks = tmp_repo / ".git" / "hooks"
    shutil.copy(_HOOKS_SRC / "post_commit_guard.sh", hooks / "post-commit")
    shutil.copy(_HOOKS_SRC / "reference_transaction_guard.sh", hooks / "reference-transaction")
    return tmp_repo


class TestGuardCompatibility:
    def test_reference_transaction_guard_passes_queue_marker_and_blocks_unmarked(
        self, repo_with_hooks: Path, queue_root: Path, sessions: list[str]
    ) -> None:
        repo = repo_with_hooks
        landing = cql.WorktreeLanding(repo_root=repo, queue_root=queue_root)
        cq.enqueue_item(sessions[0], "guarded", [("docs/g.txt", b"g\n")], queue_root=queue_root)
        stats = cq.drain_queue(queue_root, landing=landing)
        assert stats["done"] == 1 and stats["dead"] == 0, "guard 不拦 [GW:{sid}:{qid}] 队列 commit"
        assert len(_dev_commits(repo)) == 1

        # 负对照：无 [GW: 标记的 plumbing 直推 dev 仍被阻断（回归既有防护，66 号 §11 #2 末条）
        wt = landing.worktree_path
        (wt / "docs" / "evil.txt").write_text("evil\n", encoding="utf-8")
        _git(wt, "add", "docs/evil.txt")
        tree = _git_text(wt, "write-tree")
        head = _git_text(repo, "rev-parse", "refs/heads/dev")
        bad = (
            subprocess.run(
                ["git", "commit-tree", tree, "-p", head, "-m", "no marker plumbing bypass"],
                cwd=str(wt),
                capture_output=True,
                check=True,
            )
            .stdout.decode()
            .strip()
        )
        r = _git(repo, "update-ref", "refs/heads/dev", bad, head, check=False)
        assert r.returncode != 0, "无标记 plumbing 更新 MUST 被 REFERENCE-TRANSACTION-GUARD 阻断"
        assert b"REFERENCE-TRANSACTION-GUARD" in r.stderr + r.stdout
        assert _git_text(repo, "rev-parse", "refs/heads/dev") == head, "阻断后 dev 未动"

    def test_post_commit_guard_passes_queue_commits_and_resets_unmarked(
        self, repo_with_hooks: Path, queue_root: Path, sessions: list[str]
    ) -> None:
        repo = repo_with_hooks
        landing = cql.WorktreeLanding(repo_root=repo, queue_root=queue_root)
        cq.enqueue_item(sessions[0], "guarded", [("docs/p.txt", b"p\n")], queue_root=queue_root)
        stats = cq.drain_queue(queue_root, landing=landing)
        assert stats["done"] == 1, "POST-COMMIT-GUARD 不拦队列 commit（session 已注册）"
        assert _git_bytes(repo, "show", "dev:docs/p.txt") == b"p\n", "commit 未被 reset"

        # 负对照：裸 commit 无标记 → guard 自动 reset --soft HEAD~1（既有防护回归）
        head_before = _git_text(repo, "rev-parse", "HEAD")
        (repo / "rogue.txt").write_text("rogue\n", encoding="utf-8")
        _git(repo, "add", "rogue.txt")
        _git(repo, "commit", "-qm", "rogue direct commit", check=False)
        assert _git_text(repo, "rev-parse", "HEAD") == head_before, "non-GW commit MUST 被 reset"


# ---------------------------------------------------------------------------
# 66 号 §11 #4：门禁等价性抽查 5 门——专用 worktree 内与主工作区同判
# ---------------------------------------------------------------------------

_FAKE_CHECKER = (
    "import sys\n"
    "bad = [a for a in sys.argv[1:] if 'bad' in a]\n"
    "if bad:\n"
    "    print('FAKE-CHECKER violation: ' + ','.join(bad))\n"
    "    sys.exit(1)\n"
    "sys.exit(0)\n"
)


@pytest.fixture()
def equiv_repo(tmp_path: Path) -> tuple[Path, Path]:
    """等价性仓：main+dev 同点，serializer worktree 就位；3 个 fake checker 已提交（双侧同版）。

    fake checker 语义：参数含 'bad' → exit 1，否则 exit 0——只验 gate 的路径归一化 +
    subprocess 接线 + exit code 映射在两种 rooting 下同判；checker 真源缺失场景由
    fail-open/fail-closed 对称性覆盖（两侧同缺 → 同判）。
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "test")
    _git(repo, "config", "core.autocrlf", "false")
    checkers = {
        ".gitignore": ".runtime/\n.ailocks/\n",  # 与主仓对齐：运行时目录豁免
        "scripts/governance/d1_structure/check_directory_contract.py": _FAKE_CHECKER,
        "scripts/governance/d3_metadata/check_frontmatter_metadata.py": _FAKE_CHECKER,
        "scripts/governance/d7_code/check_encoding.py": _FAKE_CHECKER,
        "docs/keep.txt": "keep\n",
    }
    for rel, content in checkers.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-qm", "init with fake checkers")
    _git(repo, "branch", "dev")
    wt = tmp_path / "wt"
    _git(repo, "worktree", "add", str(wt), "-b", "serializer/commit-queue", "refs/heads/dev")
    return repo, wt


class TestGateEquivalence:
    """同一快照同一门：主工作区 rooting 与专用 worktree rooting 判定一致（PASS/FAIL 两态）。"""

    def _gateways(self, repo: Path, wt: Path) -> tuple[GitCommitGateway, GitCommitGateway]:
        reg = SessionRegistry(repo)
        reg.register("sess-equiv")
        gw_main = GitCommitGateway(project_root=repo, registry=reg)
        gw_wt = GitCommitGateway(project_root=wt, registry=reg)
        return gw_main, gw_wt

    def _write_both(self, repo: Path, wt: Path, rel: str, content: str) -> tuple[str, str]:
        for root in (repo, wt):
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
        return str(repo / rel), str(wt / rel)

    def _assert_equiv(self, spec, gw_main, gw_wt, main_file, wt_file, expect_pass: bool, gate_label: str) -> None:
        ok_main, _ = spec.check(gw_main, [main_file], session_id="sess-equiv")
        ok_wt, _ = spec.check(gw_wt, [wt_file], session_id="sess-equiv")
        assert ok_main == ok_wt == expect_pass, (
            f"{gate_label} 等价性破裂: main={ok_main} worktree={ok_wt} 期望={expect_pass}"
        )

    def test_directory_contract_equiv(self, equiv_repo) -> None:
        from zephyr.gov_enforcement.commit_gates.directory_contract_gate import make_directory_contract_gate

        repo, wt = equiv_repo
        gw_main, gw_wt = self._gateways(repo, wt)
        spec = make_directory_contract_gate()
        f_main, f_wt = self._write_both(repo, wt, "docs/good_dcr.txt", "x\n")
        self._assert_equiv(spec, gw_main, gw_wt, f_main, f_wt, True, "DIRECTORY-CONTRACT(pass)")
        f_main, f_wt = self._write_both(repo, wt, "docs/bad_dcr.txt", "x\n")
        self._assert_equiv(spec, gw_main, gw_wt, f_main, f_wt, False, "DIRECTORY-CONTRACT(fail)")

    def test_ttl_metadata_equiv(self, equiv_repo) -> None:
        from zephyr.gov_enforcement.commit_gates.ttl_gate import make_ttl_gate

        repo, wt = equiv_repo
        gw_main, gw_wt = self._gateways(repo, wt)
        spec = make_ttl_gate()
        f_main, f_wt = self._write_both(repo, wt, "docs/good_ttl.md", "x\n")
        self._assert_equiv(spec, gw_main, gw_wt, f_main, f_wt, True, "TTL-METADATA(pass)")
        f_main, f_wt = self._write_both(repo, wt, "docs/bad_ttl.md", "x\n")
        self._assert_equiv(spec, gw_main, gw_wt, f_main, f_wt, False, "TTL-METADATA(fail)")

    def test_encoding_safety_equiv(self, equiv_repo) -> None:
        from zephyr.gov_enforcement.commit_gates.encoding_gate import make_encoding_gate

        repo, wt = equiv_repo
        gw_main, gw_wt = self._gateways(repo, wt)
        spec = make_encoding_gate()
        f_main, f_wt = self._write_both(repo, wt, "docs/good_enc.py", "x = 1\n")
        self._assert_equiv(spec, gw_main, gw_wt, f_main, f_wt, True, "ENCODING-SAFETY(pass)")
        f_main, f_wt = self._write_both(repo, wt, "docs/bad_enc.py", "x = 1\n")
        self._assert_equiv(spec, gw_main, gw_wt, f_main, f_wt, False, "ENCODING-SAFETY(fail)")

    def test_r5_digit_suffix_equiv(self, equiv_repo) -> None:
        from zephyr.gov_enforcement.commit_gates.r5_digit_suffix_gate import make_r5_digit_suffix_gate

        repo, wt = equiv_repo
        gw_main, gw_wt = self._gateways(repo, wt)
        spec = make_r5_digit_suffix_gate()
        f_main, f_wt = self._write_both(repo, wt, "docs/plain/f.md", "x\n")
        self._assert_equiv(spec, gw_main, gw_wt, f_main, f_wt, True, "R5-DIGIT-SUFFIX(pass)")
        # 新引入 _NN 后缀目录（HEAD 中不存在）→ 双侧同判阻断
        f_main, f_wt = self._write_both(repo, wt, "docs/bad_99/f.md", "x\n")
        self._assert_equiv(spec, gw_main, gw_wt, f_main, f_wt, False, "R5-DIGIT-SUFFIX(fail)")

    def test_foreign_change_equiv(self, equiv_repo) -> None:
        from zephyr.gov_enforcement.commit_gates.foreign_change_gate import make_foreign_change_gate

        repo, wt = equiv_repo
        gw_main, gw_wt = self._gateways(repo, wt)
        spec = make_foreign_change_gate()
        f_main, f_wt = self._write_both(repo, wt, "docs/fc.txt", "x\n")
        # 空基线（claim 时干净）→ 双侧 PASS
        gw_main.claim_snapshots["sess-equiv"] = {os.path.abspath(f_main): ""}
        gw_wt.claim_snapshots["sess-equiv"] = {os.path.abspath(f_wt): ""}
        self._assert_equiv(spec, gw_main, gw_wt, f_main, f_wt, True, "FOREIGN-CHANGE(pass)")
        # 非空基线（claim 时已有外来变更）→ 双侧 BLOCK
        gw_main.claim_snapshots["sess-equiv"] = {os.path.abspath(f_main): "diff --git a/docs/fc.txt ..."}
        gw_wt.claim_snapshots["sess-equiv"] = {os.path.abspath(f_wt): "diff --git a/docs/fc.txt ..."}
        self._assert_equiv(spec, gw_main, gw_wt, f_main, f_wt, False, "FOREIGN-CHANGE(fail)")


# ---------------------------------------------------------------------------
# 08 号文 §4.2 步骤 5 + 66 号 §7：_commit_auto flag 门控改道
# ---------------------------------------------------------------------------


class TestCommitAutoReroute:
    def _gateway_on_main(self, repo: Path, sid: str = "sess-flag-t") -> GitCommitGateway:
        reg = SessionRegistry(repo)
        reg.register(sid)
        return GitCommitGateway(project_root=repo, registry=reg)

    def test_flag_off_direct_commit_unchanged(
        self, tmp_repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """回归钉住：flag OFF（默认）_commit_auto 现状直提，不入队。"""
        monkeypatch.setenv(cq.QUEUE_ENV_VAR, str(tmp_path / "cq_off"))  # 隔离真实队列目录
        monkeypatch.setattr(gw_mod, "_commit_queue_serializer_enabled", lambda: False)
        gw = self._gateway_on_main(tmp_repo)
        (tmp_repo / "auto.txt").write_text("auto\n", encoding="utf-8")
        result = gw._commit_auto("sess-flag-t", [str(tmp_repo / "auto.txt")], "chore: auto sync")
        assert result.status == CommitStatus.OK, f"flag OFF 直提失败: {result.message}"
        msg = _git_bytes(tmp_repo, "show", "-s", "--format=%B", "HEAD").decode("utf-8")
        assert "[GW:sess-flag-t:auto]" in msg, "直提保留 :auto 标记"
        assert not (tmp_path / "cq_off" / "pending").exists() or not list(
            (tmp_path / "cq_off" / "pending").glob("q-*.json")
        ), "flag OFF 不得产生队列项"

    def test_flag_on_reroutes_to_enqueue(self, tmp_repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """flag ON：_commit_auto 改道 enqueue（快照入袋即返回），不真实落盘（drain 被 mock）。"""
        qroot = tmp_path / "cq_on"
        monkeypatch.setenv(cq.QUEUE_ENV_VAR, str(qroot))
        monkeypatch.setattr(gw_mod, "_commit_queue_serializer_enabled", lambda: True)
        drain_calls: list[dict] = []
        monkeypatch.setattr(
            cql, "bootstrap_drain_with_landing", lambda **kw: drain_calls.append(kw) or {"skipped": True}
        )
        gw = self._gateway_on_main(tmp_repo)
        head_before = _git_text(tmp_repo, "rev-parse", "HEAD")
        (tmp_repo / "auto2.txt").write_text("auto2\n", encoding="utf-8")
        result = gw._commit_auto("sess-flag-t", [str(tmp_repo / "auto2.txt")], "chore: auto sync 2")
        assert result.status == CommitStatus.OK and result.commit_hash.startswith("QUEUED:"), (
            f"改道回执异常: {result.status} {result.commit_hash} {result.message}"
        )
        assert _git_text(tmp_repo, "rev-parse", "HEAD") == head_before, "改道后不得直提（单写者预备）"
        pending = list((qroot / "pending").glob("q-*.json"))
        assert len(pending) == 1, "改道产生恰 1 个队列项"
        item = json.loads(pending[0].read_text(encoding="utf-8"))
        assert item["session_id"] == "sess-flag-t"
        assert item["message"] == "chore: auto sync 2"
        assert [f["path"] for f in item["files"]] == ["auto2.txt"], "仓内相对路径入袋"
        assert item["base_head"] == _git_text(tmp_repo, "rev-parse", "refs/heads/dev"), "base_head 落袋"
        assert drain_calls, "入队后触发自举排空尝试（66 号 §8；mock 不真实落盘）"

    def test_flag_on_delete_file_carried_as_delete_action(
        self, tmp_repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """flag ON：已跟踪文件的删除经 deletes 通道入袋（action=delete），行为不丢。"""
        qroot = tmp_path / "cq_del"
        monkeypatch.setenv(cq.QUEUE_ENV_VAR, str(qroot))
        monkeypatch.setattr(gw_mod, "_commit_queue_serializer_enabled", lambda: True)
        monkeypatch.setattr(cql, "bootstrap_drain_with_landing", lambda **kw: {"skipped": True})
        gw = self._gateway_on_main(tmp_repo)
        os.remove(tmp_repo / "base.txt")  # 已跟踪文件被删
        result = gw._commit_auto("sess-flag-t", [str(tmp_repo / "base.txt")], "chore: drop base")
        assert result.status == CommitStatus.OK
        pending = list((qroot / "pending").glob("q-*.json"))
        assert len(pending) == 1
        item = json.loads(pending[0].read_text(encoding="utf-8"))
        assert item["files"][0]["action"] == "delete" and item["files"][0]["path"] == "base.txt"

    def test_flag_read_fail_closed_on_registry_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """flag 设施异常 → fail-closed OFF（现状直提不变，绝不暗中改道）。"""
        from zephyr.shared.foundation import flags as flags_mod

        def boom(*a, **kw):
            raise RuntimeError("registry exploded")

        monkeypatch.setattr(flags_mod.global_flag_registry, "is_enabled", boom)
        assert gw_mod._commit_queue_serializer_enabled() is False

    def test_flag_default_off_when_unregistered(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """flag 未注册 → is_enabled 返回传入 default=False（fail-closed 语义）。

        注：本测试隔离模拟"未注册"场景，不读生产 config/flags.yaml 当前值——
        该 flag 已经 Owner 2026-08-22 批准翻开（commit 2814b7f4，enabled:true），
        直读生产配置断言 OFF 的旧实现与 Owner 裁定相矛盾。
        """
        from zephyr.shared.foundation import flags as flags_mod

        monkeypatch.setattr(flags_mod.global_flag_registry, "is_enabled", lambda name, default=None: default)
        assert gw_mod._commit_queue_serializer_enabled() is False


# ---------------------------------------------------------------------------
# 单写者不变量断言（Owner 启用 flag 后的验证工具，66 号 §5 关键不变量①）
# ---------------------------------------------------------------------------


class TestSingleWriterAssertion:
    def test_queue_only_history_passes(
        self, tmp_repo: Path, queue_root: Path, sessions: list[str], landing: cql.WorktreeLanding
    ) -> None:
        base = _git_text(tmp_repo, "rev-parse", "refs/heads/dev")
        for i in range(3):
            cq.enqueue_item(sessions[0], f"m{i}", [(f"docs/sw{i}.txt", f"{i}\n".encode())], queue_root=queue_root)
        cq.drain_queue(queue_root, landing=landing)
        violations = cql.assert_single_writer_dev_history(tmp_repo, since=base)
        assert violations == [], f"队列落盘历史应零违例: {violations}"

    def test_rogue_direct_commit_detected(
        self, tmp_repo: Path, queue_root: Path, sessions: list[str], landing: cql.WorktreeLanding
    ) -> None:
        base = _git_text(tmp_repo, "rev-parse", "refs/heads/dev")
        cq.enqueue_item(sessions[0], "ok", [("docs/ok.txt", b"ok\n")], queue_root=queue_root)
        cq.drain_queue(queue_root, landing=landing)
        # 第二写入者：无队列标记直提 dev（违例）
        (tmp_repo / "rogue2.txt").write_text("r\n", encoding="utf-8")
        _git(tmp_repo, "add", "rogue2.txt")
        _git(tmp_repo, "commit", "-qm", "rogue without marker")
        _git(tmp_repo, "branch", "-f", "dev", "HEAD")
        violations = cql.assert_single_writer_dev_history(tmp_repo, since=base)
        assert len(violations) == 1 and "rogue" in violations[0]["subject"], "违例 commit 被点名"
