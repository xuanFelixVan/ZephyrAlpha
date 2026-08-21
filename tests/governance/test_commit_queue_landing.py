# [A_test] module_id: MOD-GOV-047 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-047 | scripts/governance/commit_queue_landing.py | §
# [MODULE] tests.governance.test_commit_queue_landing
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; pyyaml; scripts.commit_queue; scripts.governance.commit_queue_landing; zephyr.gov_enforcement.rule_bridge.git_commit_gateway; zephyr.security.access_control.session_concurrency
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
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
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
            f"git {' '.join(args)} -> rc={r.returncode}: {r.stderr.decode('utf-8', errors='replace')[:400]}"
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

    def commit(self, session_id: str, files: list[str], message: str, allow_non_worktree: bool = False) -> CommitResult:
        self.events.append(("commit", {
            "session_id": session_id,
            "files": list(files),
            "message": message,
            "allow_non_worktree": allow_non_worktree,
        }))
        for f in files:
            _git(self._wt, "add", "-A", "--", f)  # -A 兼容 delete action（staging 删除）
        _git(self._wt, "commit", "--no-verify", "-qm", message)
        sha = _git_text(self._wt, "rev-parse", "HEAD")
        return CommitResult(status=CommitStatus.OK, message="stub committed", commit_hash=sha)

    def commit_calls(self) -> list[dict]:
        return [payload for kind, payload in self.events if kind == "commit"]


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
    def test_enqueue_drain_lands_real_commit_with_queue_marker(
        self, tmp_repo: Path, queue_root: Path
    ) -> None:
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
        assert call["allow_non_worktree"] is True, "落盘经 allow_non_worktree 逃生参数（.runtime 路径不命中 worktree 判定）"
        assert call["files"] == [str(landing.worktree_path / "docs" / "landed.txt")], "pathspec 限定本项文件（零搭便车）"

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
    def test_replay_done_item_short_circuits_via_is_ancestor(
        self, tmp_repo: Path, queue_root: Path
    ) -> None:
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

    def test_replay_without_landed_id_short_circuits_via_marker_grep(
        self, tmp_repo: Path, queue_root: Path
    ) -> None:
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
    def test_base_head_conflict_goes_dead_and_preserves_theirs(
        self, tmp_repo: Path, queue_root: Path
    ) -> None:
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

    def test_disjoint_advance_does_not_conflict(
        self, tmp_repo: Path, queue_root: Path
    ) -> None:
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

    def test_flags_yaml_registers_flag_always_off_by_default(self) -> None:
        """默认态证明：真仓 config/flags.yaml 注册 commit_queue_serializer 且 enabled: false。

        宪章 B-007：默认 ALWAYS_OFF；翻开（enabled: true）属 Owner 窗口审批，不属本批。
        """
        flags = yaml.safe_load((REPO_ROOT / "config" / "flags.yaml").read_text(encoding="utf-8"))
        entry = flags["flags"]["commit_queue_serializer"]
        assert entry["enabled"] is False, "commit_queue_serializer 默认 MUST 为 ALWAYS_OFF"
        # 真 flags 设施读出亦为 OFF（接线点 _commit_queue_serializer_enabled 端到端）
        assert gw_mod._commit_queue_serializer_enabled() is False

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

    def test_flag_on_reroutes_to_enqueue(
        self, tmp_repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
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
        assert opts.meta_extra == {"rerouted_from": "_commit_auto"}, "改道来源审计标记落袋"
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
