# [A_test] module_id: MOD-GOV-047 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-047 | scripts/governance/commit_queue_landing.py | §k=4 通道池（投机并行验证+串行落地）
# [MODULE] tests.governance.test_commit_queue_pool
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; pyyaml; scripts.commit_queue; scripts.governance.commit_queue_landing; zephyr.gov_enforcement.rule_bridge.git_commit_gateway
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/test_commit_queue_pool.py
# [MATURITY] testing
# [INVARIANTS] 全 tmp 隔离（tmp git 仓 + tmp 队列根，绝不碰主仓 .runtime/commit_queue 与真实 dev）；GitCommitGateway 桩化（真 git commit 语义 + 门禁豁免，与 test_commit_queue_landing 同款约定）；红蓝验收判据=Owner 施工令（st-k4-20260923）：①4 路并发落地同册不同条目→全部成功零丢失 ②同文件两项并行→正确串行化零覆盖 ③k=1 降级=现行为逐字节一致（dev tree sha 相等） ④池心跳单点（renew 只来自心跳线程） ⑤杀一工其余工+队列不受影响、遗孤波首复活 ⑥工棚卫生（每项前 reset --hard+clean） ⑥b env 名册/import 同源（roster_root=主仓根）
# [MODIFY-GUARD] st-k4-20260923 施工令红蓝必备四条 + 路径锁串行化 + CAS 重放（_pool_cas_replay/_replay_commit_without_gates）
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] permanent
"""test_commit_queue_pool.py — k=4 通道池红蓝验收（st-k4-20260923）。

真源：scripts/governance/commit_queue_landing.py 池化段（drain_queue_pool/_run_pool_wave/
_pool_process_item/_pool_cas_replay/_item_path_locks）+ Owner 施工令红蓝必备。

红证内嵌：test_same_catalog_entries_red_probe_merge_disabled 证明零丢失断言对
「合并重放缺失」敏感——关掉注册表族合并语义后同册并发即 3 死 1 落（正是池化
必须配条目级三向合并重放的机理实证）。
"""

from __future__ import annotations

import json
import subprocess
import threading
import time
from pathlib import Path

import pytest
import yaml

import scripts.commit_queue as cq
import scripts.governance.commit_queue_landing as cql
import zephyr.gov_enforcement.rule_bridge.git_commit_gateway as gw_mod
from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import CommitResult, CommitStatus

# ---------------------------------------------------------------------------
# 基础工具（与 test_commit_queue_landing 同款约定：字节安全 + tmp 全隔离）
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


@pytest.fixture()
def tmp_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "test")
    _git(repo, "config", "core.autocrlf", "false")
    (repo / ".gitignore").write_text(".runtime/\n.ailocks/\n", encoding="utf-8")
    (repo / "base.txt").write_text("base\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-qm", "init")
    _git(repo, "branch", "dev")
    return repo


@pytest.fixture()
def queue_root(tmp_path: Path) -> Path:
    return tmp_path / "commit_queue"


class _StubGateway:
    """真 git commit 桩（门禁豁免、ref/对象语义保真；与 landing 测试同款）。"""

    def __init__(self, worktree_path: Path, *, slow_s: float = 0.0, crash_state: dict | None = None) -> None:
        self._wt = worktree_path
        self._slow_s = slow_s
        self._crash_state = crash_state  # 共享 dict：{"crashed": bool}=跨波一次性崩溃

    def claim_files(self, session_id: str, files: list[str], adopt_prior_work: bool = False) -> list[str]:
        return list(files)

    def release_files(self, session_id: str, files: list[str]) -> None:
        pass

    def commit(self, session_id, files, message, **_kw) -> CommitResult:
        if self._slow_s:
            time.sleep(self._slow_s)
        if self._crash_state is not None and not self._crash_state["crashed"]:
            self._crash_state["crashed"] = True
            raise BaseException("simulated worker crash（杀工测试）")
        for f in files:
            target = Path(f) if Path(f).is_absolute() else self._wt / f
            if target.is_file():
                _git(self._wt, "add", "--", f)
            else:
                _git(self._wt, "rm", "--cached", "--ignore-unmatch", "--", f)
        _git(self._wt, "commit", "--no-verify", "-qm", message)
        return CommitResult(
            status=CommitStatus.OK, message="stub", commit_hash=_git_text(self._wt, "rev-parse", "HEAD")
        )


def _inject_stub_workers(monkeypatch: pytest.MonkeyPatch, *, slow_s: float = 0.0, crash_worker: int | None = None):
    """给池工注入桩 gateway（drain_queue_pool 内部经 make_worker_landing 构造工）。
    crash_worker：该工首次 commit 抛 BaseException（跨波一次性——模拟瞬态崩溃，
    工棚复活后正常干活）。"""
    real_make = cql.make_worker_landing
    crash_state = {"crashed": False}

    def _make(repo, root, worker_id):
        landing = real_make(repo, root, worker_id)
        do_crash = crash_worker is not None and worker_id == crash_worker
        landing._gateway = _StubGateway(
            landing.worktree_path, slow_s=slow_s, crash_state=crash_state if do_crash else None
        )
        return landing

    monkeypatch.setattr(cql, "make_worker_landing", _make)


def _enqueue(repo: Path, qroot: Path, sid: str, rel: str, content: str, msg: str) -> dict:
    return cq.enqueue_item(
        sid,
        msg,
        [(rel, content.encode("utf-8"))],
        queue_root=qroot,
        options=cq.EnqueueOptions(base_head=_git_text(repo, "rev-parse", "refs/heads/dev")),
    )


_CATALOG = "docs/01_policies_and_standards/_registry/catalogs/test_catalog.yaml"
_BASE_CATALOG = "schema_version: 1.0.0\nitems:\n  - id: base\n    path: base.md\n"


def _catalog_with(extra_id: str) -> str:
    return (
        f"schema_version: 1.0.0\nitems:\n  - id: base\n    path: base.md\n  - id: {extra_id}\n    path: {extra_id}.md\n"
    )


# ---------------------------------------------------------------------------
# 红蓝①：4 路并发落地同册不同条目 → 全部成功零丢失（路径锁串行化 + 条目级合并）
# ---------------------------------------------------------------------------


class TestFourLaneSameCatalogZeroLoss:
    def test_four_workers_same_catalog_all_land(self, tmp_repo: Path, queue_root: Path, monkeypatch):
        (tmp_repo / _CATALOG).parent.mkdir(parents=True, exist_ok=True)
        (tmp_repo / _CATALOG).write_text(_BASE_CATALOG, encoding="utf-8")
        _git(tmp_repo, "add", ".")
        _git(tmp_repo, "commit", "-qm", "catalog base")
        _git(tmp_repo, "update-ref", "refs/heads/dev", "HEAD")

        for i in range(4):
            _enqueue(tmp_repo, queue_root, f"sess-w{i}", _CATALOG, _catalog_with(f"w{i}"), f"add w{i}")
        _inject_stub_workers(monkeypatch)
        stats = cql.drain_queue_pool(queue_root=queue_root, repo_root=tmp_repo, workers=4)

        assert stats["done"] == 4, stats
        assert stats["dead"] == 0, stats
        final = yaml.safe_load((tmp_repo / _CATALOG).read_text(encoding="utf-8"))
        landed_ids = {e["id"] for e in final["items"]}
        assert landed_ids == {"base", "w0", "w1", "w2", "w3"}  # 零丢失：4 条目全部在册
        assert not (queue_root / "serializer.lease").exists()  # 池级 lease 释放

    def test_same_catalog_entries_red_probe_merge_disabled(self, tmp_repo: Path, queue_root: Path, monkeypatch):
        """红证：关掉注册表族合并语义（is_registry_mergeable→False）后，同册并发
        退化为逐文件快进判定——后工基底冲突死信（3 死 1 落）。钉住零丢失断言对
        合并重放缺失敏感：本测试红=零丢失机制真实在场。"""
        (tmp_repo / _CATALOG).parent.mkdir(parents=True, exist_ok=True)
        (tmp_repo / _CATALOG).write_text(_BASE_CATALOG, encoding="utf-8")
        _git(tmp_repo, "add", ".")
        _git(tmp_repo, "commit", "-qm", "catalog base")
        _git(tmp_repo, "update-ref", "refs/heads/dev", "HEAD")

        monkeypatch.setattr(cql, "is_registry_mergeable", lambda rel: False)
        for i in range(4):
            _enqueue(tmp_repo, queue_root, f"sess-w{i}", _CATALOG, _catalog_with(f"w{i}"), f"add w{i}")
        _inject_stub_workers(monkeypatch)
        stats = cql.drain_queue_pool(queue_root=queue_root, repo_root=tmp_repo, workers=4)

        assert stats["done"] == 1 and stats["dead"] == 3, stats  # 无合并重放=同册互踩（对照组）


# ---------------------------------------------------------------------------
# 红蓝②：同文件两项并行 → 正确串行化零覆盖（非注册表=后工基底冲突死信回人工）
# ---------------------------------------------------------------------------


class TestSameFileSerialization:
    def test_same_plain_file_two_items_no_overwrite(self, tmp_repo: Path, queue_root: Path, monkeypatch):
        for i, content in (("a", "content-A\n"), ("b", "content-B\n")):
            _enqueue(tmp_repo, queue_root, f"sess-{i}", "notes/x.txt", content, f"write x {i}")
        _inject_stub_workers(monkeypatch)
        stats = cql.drain_queue_pool(queue_root=queue_root, repo_root=tmp_repo, workers=4)

        assert stats["done"] == 1 and stats["dead"] == 1, stats
        dev_content = (tmp_repo / "notes" / "x.txt").read_text(encoding="utf-8")
        done_files = list((queue_root / "done").glob("q-*.json"))
        assert len(done_files) == 1
        done_item = json.loads(done_files[0].read_text(encoding="utf-8"))
        # 零覆盖铁律：dev 上是恰好一项的内容（落者全文），另一项内容绝不在 dev
        assert dev_content in ("content-A\n", "content-B\n")
        blob_ref = done_item["files"][0]["blob_ref"]
        landed = (queue_root / blob_ref).read_text(encoding="utf-8")
        assert dev_content == landed
        assert stats["dead"] == 1  # 输者死信回人工（66 号 §6.4 语义），绝不静默覆盖


# ---------------------------------------------------------------------------
# 红蓝③：CAS 冲突（无同路径）→ 落地段重放不重跑门禁（commit-tree re-parent）
# ---------------------------------------------------------------------------


class TestCasReplayNoOverlap:
    def test_no_overlap_conflict_reparented(self, tmp_repo: Path, queue_root: Path, monkeypatch):
        _enqueue(tmp_repo, queue_root, "sess-a", "a.txt", "A\n", "add a")
        _enqueue(tmp_repo, queue_root, "sess-b", "b.txt", "B\n", "add b")

        barrier = threading.Barrier(2)
        state = {"used": False}
        orig = cql.WorktreeLanding._advance_dev

        def synced_advance(self, old, new):
            if not state["used"]:
                state["used"] = True
                try:
                    barrier.wait(timeout=30)  # 两工同到 CAS 点 → 必有一冲突
                except threading.BrokenBarrierError:
                    pass
            return orig(self, old, new)

        monkeypatch.setattr(cql.WorktreeLanding, "_advance_dev", synced_advance)
        _inject_stub_workers(monkeypatch)
        stats = cql.drain_queue_pool(queue_root=queue_root, repo_root=tmp_repo, workers=2)

        assert stats["done"] == 2 and stats["dead"] == 0, stats
        assert (tmp_repo / "a.txt").read_text(encoding="utf-8") == "A\n"
        assert (tmp_repo / "b.txt").read_text(encoding="utf-8") == "B\n"
        # 重放产物=单亲线性链（commit-tree re-parent，无分叉无 merge）
        for line in _git_text(tmp_repo, "log", "--format=%P", "dev").splitlines():
            assert len(line.split()) == 1

    def test_registry_overlap_replay_merges_entries(self, tmp_repo: Path, queue_root: Path):
        """单元层：注册表同册 CAS 冲突 → 重放=对新 dev 重三向合并（他会话条目吸收，
        零覆盖零丢失），commit-tree 同 message。"""
        (tmp_repo / _CATALOG).parent.mkdir(parents=True, exist_ok=True)
        (tmp_repo / _CATALOG).write_text(_BASE_CATALOG, encoding="utf-8")
        _git(tmp_repo, "add", ".")
        _git(tmp_repo, "commit", "-qm", "catalog base")
        _git(tmp_repo, "update-ref", "refs/heads/dev", "HEAD")

        item = _enqueue(tmp_repo, queue_root, "sess-m", _CATALOG, _catalog_with("w0"), "add w0")
        landing = cql.make_worker_landing(tmp_repo, queue_root, 0)
        landing._gateway = _StubGateway(landing.worktree_path)
        landing.ensure_worktree()
        landing._sync_worktree()
        old_dev = _git_text(tmp_repo, "rev-parse", "refs/heads/dev")

        wt_files = landing._apply_snapshot(item, queue_root, old_dev)
        landing._prestage_snapshot(item, wt_files)
        marker = cql.queue_marker("sess-m", item["qid"])
        res = landing._gateway.commit("sess-m", wt_files, f"add w0\n\n{marker}")

        # 队列外写入者推进 dev 且触及同册（另一工落地 w_ext 的等效态）
        (tmp_repo / _CATALOG).write_text(_catalog_with("w_ext"), encoding="utf-8")
        _git(tmp_repo, "add", ".")
        _git(tmp_repo, "commit", "-qm", "ext lands w_ext")
        _git(tmp_repo, "update-ref", "refs/heads/dev", "HEAD")
        new_dev = _git_text(tmp_repo, "rev-parse", "refs/heads/dev")

        outcome = landing._pool_cas_replay(item, queue_root, old_dev, res.commit_hash, item["qid"])
        assert outcome.ok, outcome.reason
        final = yaml.safe_load((tmp_repo / _CATALOG).read_text(encoding="utf-8"))
        assert {e["id"] for e in final["items"]} == {"base", "w0", "w_ext"}  # 双侧条目全保
        # 重放 commit 带原队列标记（幂等 grep 依赖）
        assert marker in _git_text(tmp_repo, "log", "-1", "--format=%B", outcome.landed_id)


# ---------------------------------------------------------------------------
# 红蓝④：k=1 降级开关 = 现行为逐字节一致（dev tree sha 相等）
# ---------------------------------------------------------------------------


class TestK1Degradation:
    def _build(self, tmp_path: Path, tag: str) -> tuple[Path, Path]:
        repo = tmp_path / f"repo-{tag}"
        repo.mkdir()
        _git(repo, "init", "-q", "-b", "main")
        _git(repo, "config", "user.email", "t@example.com")
        _git(repo, "config", "user.name", "test")
        _git(repo, "config", "core.autocrlf", "false")
        (repo / ".gitignore").write_text(".runtime/\n", encoding="utf-8")
        (repo / "base.txt").write_text("base\n", encoding="utf-8")
        _git(repo, "add", ".")
        _git(repo, "commit", "-qm", "init")
        _git(repo, "branch", "dev")
        qroot = tmp_path / f"queue-{tag}"
        for i in range(3):
            _enqueue(repo, qroot, f"sess-{i}", f"f{i}.txt", f"content {i}\n", f"add f{i}")
        return repo, qroot

    def test_k1_matches_legacy_byte_for_byte(self, tmp_path: Path):
        repo_pool, qroot_pool = self._build(tmp_path, "pool")
        repo_legacy, qroot_legacy = self._build(tmp_path, "legacy")

        cql.drain_queue_pool(queue_root=qroot_pool, repo_root=repo_pool, workers=1)  # 降级开关
        landing = cql.WorktreeLanding(repo_root=repo_legacy, queue_root=qroot_legacy)
        cq.drain_queue(qroot_legacy, landing=landing)

        tree_pool = _git_text(repo_pool, "rev-parse", "refs/heads/dev^{tree}")
        tree_legacy = _git_text(repo_legacy, "rev-parse", "refs/heads/dev^{tree}")
        assert tree_pool == tree_legacy  # 逐字节一致（tree sha 是内容的全域指纹）
        done_pool = {p.name for p in (qroot_pool / "done").glob("q-*.json")}
        done_legacy = {p.name for p in (qroot_legacy / "done").glob("q-*.json")}
        assert done_pool == done_legacy


# ---------------------------------------------------------------------------
# 红蓝④b：池心跳单点（renew 只来自心跳线程，杜绝四倍心跳病）
# ---------------------------------------------------------------------------


class TestPoolHeartbeatSinglePoint:
    def test_renew_only_from_heartbeat_thread(self, tmp_repo: Path, queue_root: Path, monkeypatch):
        monkeypatch.setattr(cql, "_POOL_WORKER_HEARTBEAT_INTERVAL_S", 0.05)
        _enqueue(tmp_repo, queue_root, "sess-hb", "hb.txt", "hb\n", "add hb")

        orig_sync = cql.WorktreeLanding._sync_worktree
        idents: set[int] = set()
        main_ident = threading.get_ident()
        calls = {"n": 0}
        lock = threading.Lock()

        def slow_sync(self):
            with lock:
                calls["n"] += 0  # no-op 占位保 dict 可变
            time.sleep(0.3)  # 拉长单项墙钟，给心跳线程留续租窗口
            return orig_sync(self)

        orig_renew = cq.SerializerLease.renew

        def spy_renew(self):
            idents.add(threading.get_ident())
            with lock:
                calls["n"] += 1
            return orig_renew(self)

        monkeypatch.setattr(cql.WorktreeLanding, "_sync_worktree", slow_sync)
        monkeypatch.setattr(cq.SerializerLease, "renew", spy_renew)
        _inject_stub_workers(monkeypatch)
        stats = cql.drain_queue_pool(queue_root=queue_root, repo_root=tmp_repo, workers=2)

        assert stats["done"] == 1
        assert calls["n"] >= 2  # 心跳线程在长项在途期间持续续租
        assert len(idents) == 1  # 单点：renew 只来自一个线程
        assert main_ident not in idents  # 且不是主线程（工线程零续租=四倍心跳病根绝）


# ---------------------------------------------------------------------------
# 红蓝⑤：杀一工 → 其余工+队列不受影响，遗孤波首复活
# ---------------------------------------------------------------------------


class TestWorkerKillRevival:
    @pytest.mark.filterwarnings("ignore::pytest.PytestUnhandledThreadExceptionWarning")
    def test_killed_worker_orphan_recovered_next_wave(self, tmp_repo: Path, queue_root: Path, monkeypatch):
        for i in range(5):
            _enqueue(tmp_repo, queue_root, f"sess-k{i}", f"k{i}.txt", f"k{i}\n", f"add k{i}")
        # 工 0 首项即崩（BaseException=进程崩溃语义）；工 1-3 放慢保证工 0 拿到项
        _inject_stub_workers(monkeypatch, slow_s=0.2, crash_worker=0)
        stats = cql.drain_queue_pool(queue_root=queue_root, repo_root=tmp_repo, workers=4)

        assert stats["done"] == 5, stats  # 遗孤下一波波首回收重落（工棚级复活）
        assert stats["dead"] == 0, stats  # 崩溃不产生死信（项留 processing 等回收）
        for i in range(5):
            assert (tmp_repo / f"k{i}.txt").read_text(encoding="utf-8") == f"k{i}\n"


# ---------------------------------------------------------------------------
# ⑤工棚卫生：每项处理前 worktree reset --hard + clean（陈旧拷贝不混入落地）
# ---------------------------------------------------------------------------


class TestWorkerShedHygiene:
    def test_stale_copies_cleaned_before_each_item(self, tmp_repo: Path, queue_root: Path, monkeypatch):
        _enqueue(tmp_repo, queue_root, "sess-h1", "h1.txt", "h1\n", "add h1")
        _inject_stub_workers(monkeypatch)
        cql.drain_queue_pool(queue_root=queue_root, repo_root=tmp_repo, workers=2)

        # 单工直驱（确定性）：先确保工棚 w0 激活，再撒陈旧拷贝（untracked 垃圾 + tracked 本地改）
        landing = cql.make_worker_landing(tmp_repo, queue_root, 0)
        landing._gateway = _StubGateway(landing.worktree_path)
        landing.ensure_worktree()
        wt = landing.worktree_path
        (wt / "stale_junk.txt").write_text("stale\n", encoding="utf-8")
        (wt / "base.txt").write_text("locally dirty\n", encoding="utf-8")

        ref = _enqueue(tmp_repo, queue_root, "sess-h2", "h2.txt", "h2\n", "add h2")
        item = json.loads((queue_root / "pending" / f"{ref['qid']}.json").read_text(encoding="utf-8"))
        path_locks = cql._item_path_locks(landing._item_paths(item))  # 调用方取锁（生产同款）
        try:
            outcome = landing(item, queue_root)  # _sync_worktree（reset+clean）在项应用前执行
        finally:
            cql._release_path_locks(path_locks)
        assert outcome.ok, outcome.reason

        status = _git(wt, "status", "--porcelain", check=False).stdout.decode("utf-8", errors="replace")
        assert status.strip() == "", f"工棚 w0 不干净：{status!r}"  # 陈旧拷贝被逐项卫生清零
        assert (tmp_repo / "base.txt").read_text(encoding="utf-8") == "base\n"  # 陈旧内容零混入 dev
        assert (tmp_repo / "h1.txt").read_text(encoding="utf-8") == "h1\n"
        assert (tmp_repo / "base.txt").read_text(encoding="utf-8") == "base\n"  # 陈旧拷贝零混入


# ---------------------------------------------------------------------------
# ⑥b：env 名册/import 同源（gateway roster_root=主仓根）
# ---------------------------------------------------------------------------


class TestRosterRootSameSource:
    def test_landing_gateway_reads_roster_from_repo_root(self, tmp_repo: Path, queue_root: Path):
        captured: dict = {}

        class _FakeGateway:
            def __init__(self, project_root, registry=None, roster_root=None):
                captured["project_root"] = project_root
                captured["roster_root"] = roster_root

        monkey_target = gw_mod
        orig_cls = monkey_target.GitCommitGateway
        monkey_target.GitCommitGateway = _FakeGateway
        try:
            landing = cql.WorktreeLanding(tmp_repo, queue_root=queue_root)
            landing._get_gateway()
        finally:
            monkey_target.GitCommitGateway = orig_cls
        assert captured["roster_root"] == tmp_repo.resolve()  # 名册与 import 同源（主区盘）
        assert captured["project_root"] == landing.worktree_path  # 门禁扫描面仍是本工 worktree


# ---------------------------------------------------------------------------
# ⑦：bootstrap 路由（k>1→池化；k=1→legacy 零变化）
# ---------------------------------------------------------------------------


class TestBootstrapRouting:
    def _fake_repo_layout(self, tmp_path: Path) -> tuple[Path, Path]:
        repo = tmp_path / "repo"
        (repo / "scripts" / "governance").mkdir(parents=True)
        (repo / "scripts" / "governance" / "commit_queue_landing.py").write_text("#\n", encoding="utf-8")
        qroot = repo / ".runtime" / "commit_queue"
        qroot.mkdir(parents=True)
        return repo, qroot

    def test_k_gt_1_routes_to_pool(self, tmp_path: Path, monkeypatch):
        repo, qroot = self._fake_repo_layout(tmp_path)
        monkeypatch.setattr(cql, "resolve_pool_workers", lambda: 4)
        routed = {"pool": 0, "legacy": 0}
        monkeypatch.setattr(
            cql, "drain_queue_pool", lambda *a, **kw: routed.__setitem__("pool", routed["pool"] + 1) or {}
        )
        monkeypatch.setattr(
            cq, "try_bootstrap_drain", lambda *a, **kw: routed.__setitem__("legacy", routed["legacy"] + 1) or {}
        )
        cql.bootstrap_drain_with_landing(queue_root=qroot)
        assert routed == {"pool": 1, "legacy": 0}

    def test_k1_routes_to_legacy(self, tmp_path: Path, monkeypatch):
        repo, qroot = self._fake_repo_layout(tmp_path)
        monkeypatch.setattr(cql, "resolve_pool_workers", lambda: 1)
        routed = {"pool": 0, "legacy": 0}
        monkeypatch.setattr(
            cql, "drain_queue_pool", lambda *a, **kw: routed.__setitem__("pool", routed["pool"] + 1) or {}
        )
        monkeypatch.setattr(
            cq, "try_bootstrap_drain", lambda *a, **kw: routed.__setitem__("legacy", routed["legacy"] + 1) or {}
        )
        cql.bootstrap_drain_with_landing(queue_root=qroot)
        assert routed == {"pool": 0, "legacy": 1}


# ---------------------------------------------------------------------------
# 通用绿路径：6 项 k=4 全落 + 工棚就位 + stats 形状
# ---------------------------------------------------------------------------


class TestGenericGreenPath:
    def test_six_items_four_workers(self, tmp_repo: Path, queue_root: Path, monkeypatch):
        for i in range(6):
            _enqueue(tmp_repo, queue_root, f"sess-g{i}", f"g{i}.txt", f"g{i}\n", f"add g{i}")
        _inject_stub_workers(monkeypatch)
        stats = cql.drain_queue_pool(queue_root=queue_root, repo_root=tmp_repo, workers=4)

        assert stats["done"] == 6 and stats["dead"] == 0
        assert len(stats["processed_qids"]) == 6
        assert stats["recovered"] == 0 and stats["done_cleaned"] == 0
        for i in range(6):
            assert (tmp_repo / f"g{i}.txt").read_text(encoding="utf-8") == f"g{i}\n"
        for i in range(4):
            assert cql.worker_worktree_path(queue_root, i).is_dir()
