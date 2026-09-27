# [A_test] module_id: MOD-GOV-047 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-047 | scripts/governance/commit_queue_landing.py | §提交链鲁棒性红蓝（杀工复活/双写者/故障注入）
# [MODULE] tests.governance.test_redblue_robust
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; scripts.commit_queue; scripts.governance.commit_queue_landing; zephyr.gov_enforcement.rule_bridge.git_commit_gateway
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/test_redblue_robust.py -p no:cacheprovider
# [MATURITY] testing
# [INVARIANTS] 全沙盘隔离（repo=tmp_path；queue root 一律 .runtime/tmp/csx_rb_qroot/<uniq> 自建自清，绝不碰生产 .runtime/commit_queue 与主区 index/staged）；GitCommitGateway 桩化（与 test_commit_queue_landing 同款约定）；每把尺自带红证（monkeypatch 临时开倒车/对照形态断言坏结果，证明尺对缺失防护敏感）；不做任何生产进程/生产盘面写操作
# [MODIFY-GUARD] 红蓝对抗 csx-s1：场景①杀工复活（D3）②双写者同路径（D4）③故障注入三小态
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] task_bound
"""test_redblue_robust.py — 提交链战役红蓝对抗（鲁棒性组，三场景）。

真源：scripts/governance/commit_queue_landing.py（_run_pool_wave/_pool_claim_item/
_pool_process_item/_TRANSIENT_GIT_MARKERS/M5.2 gate 装载分流/_WORKER_ERR_STREAK）+
scripts/commit_queue.py（_recover_orphans/enqueue_item/_atomic_write）。

每场景两把尺：绿尺钉住修复后不变量；红证尺以 monkeypatch 开倒车（或对照形态）断言
「坏结果确实会发生」——证明绿尺对防护缺失敏感（恒绿尺=无效尺）。

场景① 杀工复活（D3）：某工桩 commit 抛异常模拟异常死亡——其余工继续消化完剩余件、
  死工项下一波 _recover_orphans 回收、done 恒等于投入数。码内契约把「异常死亡」分
  两态分别钉住：BaseException=进程崩溃语义（项留 processing 等回收、实例已死）；
  RuntimeError=在途异常语义（工不死、崩溃实例复活续做、在手项按单项泛化分支死信）。
  记账按 (worker_id, gen) landing 实例，避开「死一工被余工/新波掩盖」的伪绿盲区
  （done==N 在旧码同样成立，不构成判别；红证尺=_WORKER_ERR_STREAK→0 首错即 GIVEUP）。
场景② 双写者同路径（D4）：两线程同根并发 claim 同一文件——原子 rename 恰一成功、
  败者 FileNotFoundError 重扫收 None；done 出现同名后任何活副本都是幽灵——弃置不
  落地，done 无重复。
场景③ 故障注入：(a) index.lock 占用 → 瞬态环境类退回 pending 自愈不死信；全局提交
  锁 LOCK_TIMEOUT 同口径改道。(b) os.replace 抛 OSError 28（盘满）打在 done 记账点 →
  件不死信不丢失、幂等短路保证每 qid 在 dev 恰落地一次。(c) gate 装载 import 崩 →
  M5.2 分流（fresh fail=死信带处方 / fresh pass=退 pending 自愈），drain 正常返回
  （进程不崩）；导入设施自身被断时按类型名 fail-open 兜底。
"""

from __future__ import annotations

import builtins
import json
import os
import re
import shutil
import subprocess
import threading
import time
from pathlib import Path
from uuid import uuid4

import pytest

import scripts.commit_queue as cq
import scripts.governance.commit_queue_landing as cql
from zephyr.gov_enforcement.rule_bridge.gate_auto_registrar import GateAutoRegistrationError
from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import CommitResult, CommitStatus

# ---------------------------------------------------------------------------
# 沙盘基座（与 test_commit_queue_pool 同款约定：字节安全 + 全隔离）
# ---------------------------------------------------------------------------

_QROOT_SANDBOX = Path(__file__).resolve().parents[2] / ".runtime" / "tmp" / "csx_rb_qroot"
_MARKER_RE = re.compile(r"\[GW:(?P<sid>.+?):(?P<qid>q-.+?)\]\s*$")


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
def rb_queue_root(tmp_path: Path) -> Path:
    """队列根沙盘（任务口径）：一律落 .runtime/tmp/csx_rb_qroot/<uniq>，自建自清。"""
    _QROOT_SANDBOX.mkdir(parents=True, exist_ok=True)
    qroot = _QROOT_SANDBOX / uuid4().hex
    qroot.mkdir()
    try:
        yield qroot
    finally:
        shutil.rmtree(qroot, ignore_errors=True)


class _StubGateway:
    """真 git commit 桩（门禁豁免、ref/对象语义保真）。allow_empty=双落地判别用。"""

    def __init__(self, worktree_path: Path, *, slow_s: float = 0.0, allow_empty: bool = False) -> None:
        self._wt = worktree_path
        self._slow_s = slow_s
        self._allow_empty = allow_empty

    def claim_files(self, session_id: str, files: list[str], adopt_prior_work: bool = False) -> list[str]:
        return list(files)

    def release_files(self, session_id: str, files: list[str]) -> None:
        pass

    def commit(self, session_id, files, message, **_kw) -> CommitResult:
        if self._slow_s:
            time.sleep(self._slow_s)
        for f in files:
            target = Path(f) if Path(f).is_absolute() else self._wt / f
            if target.is_file():
                _git(self._wt, "add", "--", f)
            else:
                _git(self._wt, "rm", "--cached", "--ignore-unmatch", "--", f)
        args = ["commit", "--no-verify", "-qm", message]
        if self._allow_empty:
            args.insert(1, "--allow-empty")
        _git(self._wt, *args)
        return CommitResult(
            status=CommitStatus.OK, message="stub", commit_hash=_git_text(self._wt, "rev-parse", "HEAD")
        )


def _enqueue(repo: Path, qroot: Path, sid: str, rel: str, content: str, msg: str) -> dict:
    return cq.enqueue_item(
        sid,
        msg,
        [(rel, content.encode("utf-8"))],
        queue_root=qroot,
        options=cq.EnqueueOptions(base_head=_git_text(repo, "rev-parse", "refs/heads/dev")),
    )


def _marker_count(repo: Path, marker: str) -> int:
    """dev 全量提交 message 中队列标记出现次数（=该 qid 实际落地次数）。"""
    return _git_text(repo, "log", "--format=%B", "dev").count(marker)


_ORIG_MAKE_WORKER_LANDING = cql.make_worker_landing  # import 时刻真身（防运行期 monkeypatch 串味）


def _prewarm_worktrees(repo: Path, qroot: Path, k: int) -> None:
    """波前串行预热 k 个工棚。

    为什么必须：drain 对空仓直接起 k 工时，k 个线程并发 `git worktree add` 会在
    .git/worktrees 元数据上互踩（实测 fatal: failed to read .git/worktrees/w2/commondir
    → env pending 自愈，语义安全但构成并发度塌缩+测试噪声）——生产池由常驻工棚规避，
    测试以同款「先备棚后开工」形态钉住排空语义本身。
    """
    for i in range(k):
        landing = _ORIG_MAKE_WORKER_LANDING(repo, qroot, i)
        landing._gateway = _StubGateway(landing.worktree_path)
        landing.ensure_worktree()


def _drain_until_quiescent(repo: Path, qroot: Path, *, workers: int = 3, attempts: int = 4) -> tuple[dict, dict]:
    """直驱 drain_queue_pool 的排空到盘面静止（pending/processing 双空），返回
    (末轮 stats, 累计 totals)。尊重测试内已 monkeypatch 的 make_worker_landing。

    为什么必须重试：Windows 下刚 rename 的项文件可被杀软/索引器短暂拒开
    （ERROR_ACCESS_DENIED 持续超 _read_item 的 1s 重试窗）→ 项退回 pending、本轮
    wave_done==0 提前收工——生产由反复自举排空覆盖（语义安全，绝不死信），测试
    以同口径重试到盘面静止。"""
    totals: dict = {"done": 0, "dead": 0}
    last: dict = {}
    for _ in range(attempts):
        last = cql.drain_queue_pool(queue_root=qroot, repo_root=repo, workers=workers)
        totals["done"] += last.get("done", 0)
        totals["dead"] += last.get("dead", 0)
        if not list((qroot / "pending").glob("q-*.json")) and not list((qroot / "processing").glob("q-*.json")):
            break
    return last, totals


def _drain_with_stub(repo: Path, qroot: Path, *, workers: int = 2) -> dict:
    """带健康桩工的排空（内置盘面静止重试，见 _drain_until_quiescent）。

    注意 workers MUST >= 2：k<=1 走 drain_queue_pool 降级开关，直接构造**真**
    WorktreeLanding（真实网关），桩注入不生效。
    """
    assert workers >= 2, "k<=1 降级路径绕过 make_worker_landing，桩注入无效"
    _prewarm_worktrees(repo, qroot, workers)

    def _make(r, root, worker_id):
        landing = _ORIG_MAKE_WORKER_LANDING(r, root, worker_id)
        landing._gateway = _StubGateway(landing.worktree_path)
        return landing

    totals: dict = {"done": 0, "dead": 0}
    cql.make_worker_landing = _make
    try:
        for _ in range(4):
            stats = cql.drain_queue_pool(queue_root=qroot, repo_root=repo, workers=workers)
            totals["done"] += stats.get("done", 0)
            totals["dead"] += stats.get("dead", 0)
            if not list((qroot / "pending").glob("q-*.json")) and not list((qroot / "processing").glob("q-*.json")):
                break
    finally:
        cql.make_worker_landing = _ORIG_MAKE_WORKER_LANDING
    return totals


def _drain_until_done(repo: Path, qroot: Path, *, expect_done: int = 1, attempts: int = 4) -> dict:
    """排空重试壳：Windows 下刚入队的项偶发被句柄/杀软短暂占用（_read_item 重试窗口
    整轮放弃→项回 pending），再排一轮即落地——终态判定必须容忍该瞬态。"""
    stats: dict = {}
    for _ in range(attempts):
        stats = _drain_with_stub(repo, qroot, workers=2)
        if stats.get("done", 0) >= expect_done:
            return stats
        time.sleep(0.3)
    return stats


# ---------------------------------------------------------------------------
# 场景①：杀工复活（D3）
# ---------------------------------------------------------------------------


class _CrashLedger:
    """按 landing 实例记账的崩溃账本（判别死工是否在同波复活的关键）。

    为什么按实例：每波 make_worker_landing 都新建工体，w2 这个**编号**在下一波会被
    全新实例复用——按编号记账会把新波的正常作业误记成「死工复活」（红证形态下两边
    都绿的伪判别根源）。按 (worker_id, gen) 记账后，绿尺断言的是「崩溃的那个实例
    自己续上了作业」。"""

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.gen: dict[int, int] = {}
        self.commits: dict[tuple[int, int], int] = {}
        self.crashed: dict = {}

    def register(self, worker_id: int) -> tuple[int, int]:
        with self.lock:
            key = (worker_id, self.gen.get(worker_id, 0))
            self.gen[worker_id] = key[1] + 1
            return key

    def note_commit(self, key: tuple[int, int]) -> None:
        with self.lock:
            self.commits[key] = self.commits.get(key, 0) + 1

    def note_crash(self, key: tuple[int, int], sid: str, qid: str, rel: str, worker_id: int) -> None:
        with self.lock:
            self.crashed = {"key": key, "sid": sid, "qid": qid, "rel": rel, "worker": worker_id}


def _inject_crash_worker(
    monkeypatch: pytest.MonkeyPatch,
    ledger: _CrashLedger,
    *,
    slow_s: float = 0.15,
    kill_process: bool = False,
) -> None:
    """**首个到达 commit 的工**首次 commit 抛异常（一次性，全局单发）。

    为什么不定向「工 2」：满载下最快工总在认领「刚被 rename 的项」→ 反复吃 Windows
    读竞态（_read_item 整轮放弃→项回 pending），定向工可能整轮到不了 commit＝注入
    不生效（伪判别）。D3 的不变量本是**按工实例**（谁崩了谁不得早退/死了不影响余工
    与队列），工号只是叙事外衣；崩溃者实际工号由账本记录供断言与报告。

    kill_process=True → BaseException（进程崩溃语义：项留 processing 等波首回收）；
    False → RuntimeError（在途异常语义：D3 工不死，项走泛化分支死信）。码内契约
    真源=commit_queue_landing 模块头 ERROR_CONTRACT——两者不可混测。"""
    real_make = cql.make_worker_landing
    fired = {"done": False}

    def _make(repo, root, worker_id):
        landing = real_make(repo, root, worker_id)
        key = ledger.register(worker_id)
        stub = _StubGateway(landing.worktree_path, slow_s=slow_s)

        class _LedgeredGateway:
            def claim_files(self, sid, files, adopt_prior_work=False):
                return stub.claim_files(sid, files, adopt_prior_work)

            def release_files(self, sid, files):
                stub.release_files(sid, files)

            def commit(self, sid, files, message, **kw):
                if not fired["done"]:
                    fired["done"] = True
                    m = _MARKER_RE.search(message or "")
                    rel = str(Path(files[0]).name) if files else ""
                    ledger.note_crash(key, sid, m.group("qid") if m else "", rel, worker_id)
                    if kill_process:
                        raise BaseException(f"simulated worker crash（工 w{worker_id} 进程崩溃语义）")
                    raise RuntimeError(f"simulated worker death（工 w{worker_id} 在途异常，桩注入）")
                res = stub.commit(sid, files, message, **kw)
                ledger.note_commit(key)
                return res

        landing._gateway = _LedgeredGateway()
        return landing

    monkeypatch.setattr(cql, "make_worker_landing", _make)


class TestScenario1WorkerKillRevival:
    @pytest.mark.filterwarnings("ignore::pytest.PytestUnhandledThreadExceptionWarning")
    @pytest.mark.timeout(300)  # 满载下单条 git 可停顿 45s+（120s git 超时兜底），放宽测试预算
    def test_worker2_process_crash_orphan_recovered_done_equals_input(
        self, tmp_repo: Path, rb_queue_root: Path, monkeypatch
    ):
        """绿尺（D3/工棚级复活）：工②进程崩溃（BaseException）不拖垮池——工①工③继续
        消化完剩余件、死工项（崩溃时在手件）下一波 _recover_orphans 回收重落、
        done 恒等于投入数、零死信。"""
        n = 8
        for i in range(n):
            _enqueue(tmp_repo, rb_queue_root, f"sess-k{i}", f"k{i}.txt", f"k{i}\n", f"add k{i}")
        # 隔离级联写回竞态窗（发现 F1，另报）：同基底批量入队会触发级联标记，其写后
        # 清扫与认领的竞态可致同件双完成、污染 done==N 判据。本场景靶心是工生命周期，
        # 级联语义不在靶面。
        monkeypatch.setattr(cq, "_mark_cascade_stale", lambda root, item: [])
        ledger = _CrashLedger()
        _inject_crash_worker(monkeypatch, ledger, slow_s=0.15, kill_process=True)

        _prewarm_worktrees(tmp_repo, rb_queue_root, 3)
        stats, totals = _drain_until_quiescent(tmp_repo, rb_queue_root, workers=3)

        assert totals["done"] == n, f"done 恒等于投入数被破坏: {stats} totals={totals}"
        assert totals["dead"] == 0, f"进程崩溃不得产生死信（项留 processing 等回收）: {totals}"
        assert not list((rb_queue_root / "processing").glob("q-*.json")), "排空后不得残留 processing 孤儿"
        assert ledger.crashed, "崩溃注入未生效（尺无判别力）"
        # 死工项经下一波回收、恰一次落地（内容在 dev、标记恰一次）
        assert _marker_count(tmp_repo, cql.queue_marker(ledger.crashed["sid"], ledger.crashed["qid"])) == 1
        _rel = ledger.crashed["rel"]
        assert (tmp_repo / _rel).read_text(encoding="utf-8") == f"{Path(_rel).stem}\n"
        # 崩溃实例本体已死：同实例不再完成任何作业（新波是全新实例，按实例记账不混淆）
        assert ledger.commits.get(ledger.crashed["key"], 0) == 0
        # 全部件内容落地 dev（零丢失）
        for i in range(n):
            assert (tmp_repo / f"k{i}.txt").read_text(encoding="utf-8") == f"k{i}\n"

    @pytest.mark.timeout(300)
    def test_worker2_runtimeerror_survives_but_item_dead_letters(
        self, tmp_repo: Path, rb_queue_root: Path, monkeypatch
    ):
        """绿尺（D3 在途异常面，任务书字面注入 RuntimeError）：工②不死——崩溃实例
        复活后仍完成作业；在手项按码内契约进死信（泛化分支「单项失败→死信不卡队」，
        非 orphan 回收通道），池整体不停摆。任务书「RuntimeError→_recover_orphans
        回收」与码内契约不符，此处按真源钉住真实语义。"""
        n = 8
        for i in range(n):
            _enqueue(tmp_repo, rb_queue_root, f"sess-e{i}", f"e{i}.txt", f"e{i}\n", f"add e{i}")
        monkeypatch.setattr(cq, "_mark_cascade_stale", lambda root, item: [])  # 隔离 F1 竞态（同上）
        ledger = _CrashLedger()
        _inject_crash_worker(monkeypatch, ledger, slow_s=0.15, kill_process=False)

        _prewarm_worktrees(tmp_repo, rb_queue_root, 3)
        stats, totals = _drain_until_quiescent(tmp_repo, rb_queue_root, workers=3)

        assert ledger.crashed, "崩溃注入未生效（尺无判别力）"
        # 崩溃工（实际工号见账本）存活：崩溃实例后续仍完成作业（D3「不得早退」的直接不变量）
        assert ledger.commits.get(ledger.crashed["key"], 0) >= 1, (
            f"崩溃实例未复活续做（D3 失效＝早退）: commits={ledger.commits}"
        )
        # 在手项按码内契约死信（可见病灶带原因+处方），其余 7 件全落。
        # 注：landing 内抛的 RuntimeError 被 _pool_process_item 泛化分支就地转死信，
        # 到不了工层 err_streak/process_raised 记账——工层异常账只覆盖逃逸异常
        # （认领段/记账段），观察面分流本身即码内契约的一部分。
        assert totals["done"] == n - 1 and totals["dead"] == 1, f"{stats} totals={totals}"
        dead = json.loads((rb_queue_root / "dead" / f"{ledger.crashed['qid']}.json").read_text(encoding="utf-8"))
        assert "simulated worker death" in (dead.get("dead_reason") or ""), dead
        assert dead.get("prescription"), "死信必须带处方"
        assert not (tmp_repo / ledger.crashed["rel"]).exists(), "死信件内容不得混入 dev"

    @pytest.mark.timeout(300)
    def test_red_probe_err_streak_zero_reverts_early_exit(self, tmp_repo: Path, rb_queue_root: Path, monkeypatch):
        """红证：_WORKER_ERR_STREAK→0（旧码形态：首错即收工）下，认领段连续抛错的工
        **首错即死、永不认领**——「工不早退」这把尺在旧形态必红。注入点取认领段
        （_pool_claim_item 抛 FileExistsError）：该段异常才到得了工层 err_streak 处理器
        （landing 内异常被单项泛化分支就地消化，见上一条注）。队列仍排空（余工+新波
        兜底），恰是历史上「死一工被余工掩盖」的盲区。"""

        real_claim = cql._pool_claim_item
        calls = {"w2": 0}

        def flaky_claim(root: Path):
            m = re.search(r"pool-w(\d+)$", threading.current_thread().name)
            if m and m.group(1) == "2":
                calls["w2"] += 1
                if calls["w2"] <= 2:  # w2 前两次认领必撞瞬时异常（Windows rename 撞同名残留形态）
                    raise FileExistsError(17, "File exists")
            return real_claim(root)

        monkeypatch.setattr(cql, "_WORKER_ERR_STREAK", 0)  # 开倒车：连错上限 0＝首错即 GIVEUP
        monkeypatch.setattr(cql, "_pool_claim_item", flaky_claim)
        n = 8
        for i in range(n):
            _enqueue(tmp_repo, rb_queue_root, f"sess-r{i}", f"r{i}.txt", f"r{i}\n", f"add r{i}")
        monkeypatch.setattr(cq, "_mark_cascade_stale", lambda root, item: [])  # 隔离 F1 竞态（同上）

        _prewarm_worktrees(tmp_repo, rb_queue_root, 3)
        totals = _drain_with_stub(tmp_repo, rb_queue_root, workers=3)  # 健康桩工（认领注入独立在位）

        assert calls["w2"] >= 2, "认领异常注入未生效（尺无判别力）"
        log = (rb_queue_root / "pool_wave.log").read_text(encoding="utf-8")
        giveups = [x for x in log.splitlines() if "claim_raised" in x and "GIVEUP" in x]
        assert giveups, f"旧形态（threshold=0）应首错即 GIVEUP 收工: {log}"
        # 队列仍排空（余工消化 + 新波兜底）——旧形态的隐藏代价在账面上不可见
        assert totals["done"] == n and totals["dead"] == 0, f"队列未排空: totals={totals}"


# ---------------------------------------------------------------------------
# 场景②：双写者同路径（D4）
# ---------------------------------------------------------------------------


class TestScenario2DualWriterSamePath:
    def test_atomic_rename_claim_race_exactly_one_winner(self, tmp_repo: Path, rb_queue_root: Path):
        """两线程对同一 queue root 同一文件并发 claim：原子 rename=互斥点，恰一成功；
        败者 FileNotFoundError 重扫（队空收 None）。盘面上该件恰存在一份。"""
        _enqueue(tmp_repo, rb_queue_root, "sess-dw", "dw.txt", "dw\n", "add dw")
        barrier = threading.Barrier(2)
        results: list = []
        lock = threading.Lock()

        def racer() -> None:
            barrier.wait(timeout=30)
            got = cql._pool_claim_item(rb_queue_root)
            with lock:
                results.append(got)

        threads = [threading.Thread(target=racer, name=f"rb2-racer-{i}") for i in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=60)

        assert len(results) == 2
        winners = [r for r in results if r is not None]
        assert len(winners) == 1, f"原子 rename 互斥被破坏（{len(winners)} 个赢家）: {results}"
        assert winners[0].exists() and winners[0].parent.name == "processing"
        assert not list((rb_queue_root / "pending").glob("q-*.json"))
        assert len(list((rb_queue_root / "processing").glob("q-*.json"))) == 1  # 恰一份，无副本

    def test_done_terminal_recheck_discards_ghost_no_duplicate(self, tmp_repo: Path, rb_queue_root: Path):
        """D4 终止性复查：done/ 已有同名后，任何 pending 活副本都是幽灵——认领必须
        弃置（不进 processing、不二次落地），done 恒无重复。"""
        cq._ensure_dirs(rb_queue_root)
        name = "q-rb2-ghost.json"
        (rb_queue_root / "pending" / name).write_text(
            json.dumps({"qid": name[:-5], "session_id": "s-rb2", "files": []}), encoding="utf-8"
        )
        (rb_queue_root / "done" / name).write_text(
            json.dumps({"qid": name[:-5], "landed_id": "abc123"}), encoding="utf-8"
        )

        claimed = cql._pool_claim_item(rb_queue_root)

        assert claimed is None, "幽灵被认领成 processing：双落地窗口未闭合"
        assert not (rb_queue_root / "processing" / name).exists()
        assert not (rb_queue_root / "pending" / name).exists(), "pending 侧幽灵应被清扫"
        assert len(list((rb_queue_root / "done").glob(name))) == 1  # done 无重复、终态件不被动

    def test_red_probe_claim_without_done_recheck_claims_ghost(self, tmp_repo: Path, rb_queue_root: Path, monkeypatch):
        """红证：拆掉 done 终止性复查的旧形态 claim（D4 之前的码形）→ 幽灵被认领成
        processing 与 done 同名并存＝二次落地入口重开。钉住绿尺对复查缺失敏感。"""

        def legacy_claim_no_recheck(root: Path):
            """D4 之前形态：认领不做任何 done/ 终止性复查。"""
            heads = sorted((root / "pending").glob("q-*.json"))
            if not heads:
                return None
            head, _lane = cq._pick_head(heads)
            if head is None:
                return None
            processing_path = root / "processing" / head.name
            try:
                os.rename(head, processing_path)
            except (FileNotFoundError, PermissionError):
                return None
            return processing_path

        name = "q-rb2-ghost2.json"
        cq._ensure_dirs(rb_queue_root)
        (rb_queue_root / "pending" / name).write_text(
            json.dumps({"qid": name[:-5], "session_id": "s-rb2", "files": []}), encoding="utf-8"
        )
        (rb_queue_root / "done" / name).write_text(
            json.dumps({"qid": name[:-5], "landed_id": "abc123"}), encoding="utf-8"
        )
        monkeypatch.setattr(cql, "_pool_claim_item", legacy_claim_no_recheck)

        claimed = cql._pool_claim_item(rb_queue_root)  # 旧形态

        assert claimed is not None, "旧形态未认领幽灵（红证失效）"
        assert (rb_queue_root / "processing" / name).exists(), "旧形态：幽灵与 done 同名并存（双落地入口）"

    def test_concurrent_enqueue_same_session_same_path_single_done(self, tmp_repo: Path, rb_queue_root: Path):
        """两线程同会话同路径并发 enqueue：会话锁内 compaction 收敛为恰一件，排空后
        done 无重复（done 文件数==distinct qid 数==1）。"""
        results: list = []
        lock = threading.Lock()

        def writer(tag: str) -> None:
            item = _enqueue(tmp_repo, rb_queue_root, "sess-dw2", "dw2.txt", f"content-{tag}\n", f"write dw2 {tag}")
            with lock:
                results.append(item["qid"])

        threads = [threading.Thread(target=writer, args=(t,)) for t in ("a", "b")]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=60)

        assert len(results) == 2
        pending = list((rb_queue_root / "pending").glob("q-*.json"))
        assert len(pending) == 1, f"同会话同路径双写必须收敛为一件: {[p.name for p in pending]}"
        stats = _drain_with_stub(tmp_repo, rb_queue_root, workers=2)
        assert stats["done"] == 1 and stats["dead"] == 0, stats
        assert len(list((rb_queue_root / "done").glob("q-*.json"))) == 1  # done 无重复


# ---------------------------------------------------------------------------
# 场景③：故障注入
# ---------------------------------------------------------------------------


def _worktree_gitdir(landing: cql.WorktreeLanding) -> Path:
    """从专用 worktree 的 .git 链接文件解析其私有 gitdir（per-worktree index 所在）。"""
    link = (landing.worktree_path / ".git").read_text(encoding="utf-8").strip()
    assert link.startswith("gitdir:"), f"非 worktree .git 链接: {link!r}"
    gitdir = Path(link.split(":", 1)[1].strip())
    assert gitdir.is_dir(), f"gitdir 不存在: {gitdir}"
    return gitdir


class TestScenario3aIndexLock:
    def test_index_lock_transient_env_pending_then_selfheal(self, tmp_repo: Path, rb_queue_root: Path, monkeypatch):
        """(a) index.lock 占用：reset --hard 撞锁 → RuntimeError 命中
        _TRANSIENT_GIT_MARKERS → LandingEnvironmentError（项退回 pending 绝不死信）；
        锁释放后下一轮排空自愈落地。"""
        landing = cql.make_worker_landing(tmp_repo, rb_queue_root, 0)
        landing._gateway = _StubGateway(landing.worktree_path)
        landing.ensure_worktree()
        gitdir = _worktree_gitdir(landing)
        item = _enqueue(tmp_repo, rb_queue_root, "sess-lock", "lk.txt", "lk\n", "add lk")

        lock_file = gitdir / "index.lock"
        lock_file.write_bytes(b"")
        try:
            with pytest.raises(cq.LandingEnvironmentError) as ei:
                landing(item, rb_queue_root)
            assert "index.lock" in str(ei.value), f"环境失败未携带病灶特征: {ei.value}"
            assert getattr(ei.value, "retried_key", "") == "env_retry"  # 计数闸在位
        finally:
            lock_file.unlink(missing_ok=True)

        # 锁释放 → 排空自愈：件不死信、恰一次落地
        stats = _drain_with_stub(tmp_repo, rb_queue_root, workers=2)
        assert stats["done"] == 1 and stats["dead"] == 0, stats
        assert (tmp_repo / "lk.txt").read_text(encoding="utf-8") == "lk\n"

    def test_red_probe_unclassified_index_lock_escapes_as_runtime_error(
        self, tmp_repo: Path, rb_queue_root: Path, monkeypatch
    ):
        """红证：关掉瞬态分类（_is_transient_git_error→False，2026-09-10 治本前的码形）
        → 同一撞锁错误以裸 RuntimeError 逃逸 __call__——池化泛化分支会把它判成物品
        失败死信。钉住「环境类绝不死信」这把尺对分类缺失敏感。"""
        monkeypatch.setattr(cql, "_is_transient_git_error", lambda exc: False)
        landing = cql.make_worker_landing(tmp_repo, rb_queue_root, 0)
        landing._gateway = _StubGateway(landing.worktree_path)
        landing.ensure_worktree()
        gitdir = _worktree_gitdir(landing)
        item = _enqueue(tmp_repo, rb_queue_root, "sess-lock2", "lk2.txt", "lk2\n", "add lk2")

        lock_file = gitdir / "index.lock"
        lock_file.write_bytes(b"")
        try:
            with pytest.raises(RuntimeError) as ei:
                landing(item, rb_queue_root)
            assert not isinstance(ei.value, cq.LandingEnvironmentError), "分类关闭后仍转环境专类（红证失效）"
            assert "index.lock" in str(ei.value)
        finally:
            lock_file.unlink(missing_ok=True)

    def test_global_lock_timeout_reroutes_to_pending_not_dead(self, tmp_repo: Path, rb_queue_root: Path, monkeypatch):
        """(a) 第二分支：全局提交锁 LOCK_TIMEOUT（网关超时的非异常出口）→ landing 转
        环境专类、项退回 pending（改道不死信）；锁释放后重排落地。"""
        real_make = cql.make_worker_landing

        def _make(repo, root, worker_id):
            landing = real_make(repo, root, worker_id)

            class _LockedOutGateway:
                def claim_files(self, sid, files, adopt_prior_work=False):
                    return list(files)

                def release_files(self, sid, files):
                    pass

                def commit(self, sid, files, message, **kw):
                    return CommitResult(
                        status=CommitStatus.LOCK_TIMEOUT,
                        message="Cannot acquire global commit lock (timeout 300s)— another session is committing.",
                    )

            landing._gateway = _LockedOutGateway()
            return landing

        monkeypatch.setattr(cql, "make_worker_landing", _make)
        item = _enqueue(tmp_repo, rb_queue_root, "sess-glock", "gl.txt", "gl\n", "add gl")

        _prewarm_worktrees(tmp_repo, rb_queue_root, 2)
        stats = cql.drain_queue_pool(queue_root=rb_queue_root, repo_root=tmp_repo, workers=2)

        assert stats["done"] == 0 and stats["dead"] == 0, f"LOCK_TIMEOUT 改道语义被破坏: {stats}"
        assert (rb_queue_root / "pending" / f"{item['qid']}.json").exists(), "项应退回 pending 等下次自举"
        rerouted = json.loads((rb_queue_root / "pending" / f"{item['qid']}.json").read_text(encoding="utf-8"))
        rerouted_retry = (rerouted.get("meta") or {}).get("env_retry")
        assert rerouted_retry and rerouted_retry >= 1, "env_retry 计数闸未记账"

        # 锁释放（换健康桩）→ 重排落地
        stats2 = _drain_with_stub(tmp_repo, rb_queue_root, workers=2)
        assert stats2["done"] == 1 and stats2["dead"] == 0, stats2

    def test_global_commit_lock_contention_raises_gateway_error_fast(self, tmp_path: Path):
        """网关锁真源行为：持有者健在（PID 活、未过 TTL）时，后来者 timeout 到点抛
        GatewayError——正是 commit 流程转 LOCK_TIMEOUT 的原料。"""
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (
            _GLOBAL_LOCK_FILE,
            GatewayError,
            _GlobalCommitLock,
        )

        lock_dir = tmp_path / ".ailocks"
        lock_dir.mkdir()
        lock_file = lock_dir / _GLOBAL_LOCK_FILE
        lock_file.write_text(json.dumps({"pid": os.getpid(), "acquired_at": time.time()}), encoding="utf-8")
        t0 = time.monotonic()
        with pytest.raises(GatewayError) as ei:
            with _GlobalCommitLock(tmp_path, timeout=0.5):
                pass  # pragma: no cover - 不可达
        elapsed = time.monotonic() - t0
        assert elapsed < 5, f"锁竞争未按 timeout 快速失败: {elapsed:.1f}s"
        assert "Cannot acquire global commit lock" in str(ei.value)
        lock_file.unlink(missing_ok=True)


class TestScenario3bDiskFull:
    @pytest.mark.timeout(300)
    def test_done_bookkeeping_enospc_no_dead_and_lands_exactly_once(
        self, tmp_repo: Path, rb_queue_root: Path, monkeypatch
    ):
        """(b) 盘满（os.replace 抛 OSError 28）打在 done 记账点：件不得死信、不得丢失
        ——留待波首回收，经幂等短路重入 done；每 qid 在 dev 上恰落地一次（done 无重复）。

        判据用盘面真相（done/ 文件数、processing/pending 清空、标记恰一次）而非
        stats["done"] 计数器：红蓝实测发现级联写回清扫与认领的竞态窗下同件可被完成
        两次（见 docs/_working/commit_speedup_campaign/70_redblue/redblu_robust.md 发现
        F1），stats 计数与盘面可能脱钩——稳态判据必须锚盘面。本测隔离级联写回
        （cq._mark_cascade_stale→空转）把故障面收敛在记账 I/O 本身；级联竞态另立发现。
        工体用桩网关（与全文件同款约定，不跑真门禁链）。"""
        n = 3
        items = [
            _enqueue(tmp_repo, rb_queue_root, f"sess-df{i}", f"df{i}.txt", f"df{i}\n", f"add df{i}") for i in range(n)
        ]
        real_replace = os.replace
        state = {"fired": 0}
        fired_events: list[tuple[str, str]] = []

        def enospc_replace(src, dst, *a, **k):
            dst_path = Path(str(dst))
            if state["fired"] == 0 and dst_path.parent.name == "done" and dst_path.name.startswith("q-"):
                state["fired"] += 1
                fired_events.append((str(src), str(dst)))
                raise OSError(28, "No space left on device")
            return real_replace(src, dst, *a, **k)

        monkeypatch.setattr(os, "replace", enospc_replace)
        monkeypatch.setattr(cq, "_mark_cascade_stale", lambda root, item: [])  # 隔离 D4 级联竞态（另报 F1）
        _prewarm_worktrees(tmp_repo, rb_queue_root, 3)

        def _make(r, root, worker_id):
            landing = _ORIG_MAKE_WORKER_LANDING(r, root, worker_id)
            landing._gateway = _StubGateway(landing.worktree_path)
            return landing

        monkeypatch.setattr(cql, "make_worker_landing", _make)
        stats, totals = _drain_until_quiescent(tmp_repo, rb_queue_root, workers=3)

        assert state["fired"] == 1, f"盘满注入未生效（尺无判别力）: {fired_events}"
        assert fired_events and Path(fired_events[0][1]).parent.name == "done", "故障必须打在 done 记账点"
        assert totals["dead"] == 0, f"记账 I/O 失败不得死信: {stats} totals={totals}"
        done_files = list((rb_queue_root / "done").glob("q-*.json"))
        assert len(done_files) == n, f"done 盘面文件恒等于投入数: {[p.name for p in done_files]}"
        assert not list((rb_queue_root / "processing").glob("q-*.json")), "故障件应已被回收，不得滞留"
        assert not list((rb_queue_root / "pending").glob("q-*.json")), "排空后不得残留 pending"
        # 每件恰一次落地（done 无重复的另一面：dev 上无二次提交）+ 内容在 dev
        for it in items:
            assert _marker_count(tmp_repo, cql.queue_marker(it["session_id"], it["qid"])) == 1
        for i in range(n):
            assert (tmp_repo / f"df{i}.txt").read_text(encoding="utf-8") == f"df{i}\n"

    def test_replay_after_bookkeeping_loss_is_idempotent(self, tmp_repo: Path, rb_queue_root: Path):
        """绿尺（幂等面）：done 记账丢失形态下重放同一件（标记已在 dev 史）→ 幂等
        短路返回已落 sha，不产生第二次提交。"""
        item = _enqueue(tmp_repo, rb_queue_root, "sess-idem", "idem.txt", "idem\n", "add idem")
        stats = _drain_with_stub(tmp_repo, rb_queue_root, workers=2)
        assert stats["done"] == 1, stats
        marker = cql.queue_marker(item["session_id"], item["qid"])
        assert _marker_count(tmp_repo, marker) == 1

        # 模拟 done 记账丢失后的裸重放（done 不在，直接再调 landing）
        landing = cql.make_worker_landing(tmp_repo, rb_queue_root, 0)
        landing._gateway = _StubGateway(landing.worktree_path, allow_empty=True)
        landing.ensure_worktree()
        res = landing(item, rb_queue_root)

        assert res.ok, f"幂等重放应成功短路: {res.reason}"
        assert _marker_count(tmp_repo, marker) == 1, "重放产生了第二次提交＝双落地"
        # 与生产 _already_landed 同口径（-F 固定串：[GW:...] 会被 POSIX 正则当字符组解析）
        expected = _git_text(tmp_repo, "log", "-1", "--format=%H", "-F", f"--grep={marker}", "refs/heads/dev")
        assert res.landed_id == expected, f"幂等短路应返回已落 sha: {res.landed_id} != {expected}"

    def test_red_probe_blind_idempotency_double_lands(self, tmp_repo: Path, rb_queue_root: Path, monkeypatch):
        """红证：幂等判定失明（_already_landed→None，landed_id+标记 grep 双证皆废的
        旧态）→ 同一件重放在 dev 上二次落地（标记出现 2 次）。钉住「done 恒等于投入
        数」这把尺对幂等缺失敏感。"""
        item = _enqueue(tmp_repo, rb_queue_root, "sess-blind", "blind.txt", "blind\n", "add blind")
        stats = _drain_with_stub(tmp_repo, rb_queue_root, workers=2)
        assert stats["done"] == 1, stats
        marker = cql.queue_marker(item["session_id"], item["qid"])
        assert _marker_count(tmp_repo, marker) == 1

        monkeypatch.setattr(cql.WorktreeLanding, "_already_landed", lambda self, it: None)
        landing = cql.make_worker_landing(tmp_repo, rb_queue_root, 0)
        landing._gateway = _StubGateway(landing.worktree_path, allow_empty=True)
        landing.ensure_worktree()
        item = dict(item)
        item["base_head"] = _git_text(tmp_repo, "rev-parse", "refs/heads/dev")  # 规避基底冲突支路
        res = landing(item, rb_queue_root)

        assert res.ok, f"失明形态下重放被放行才构成红证: {res.reason}"
        assert _marker_count(tmp_repo, marker) == 2, "失明形态未双落地（红证失效）"


class TestScenario3cImportCrash:
    _SENTINEL = "zephyr.rb_redblue.sentinel_gate_module"
    _REGISTRAR = "zephyr.gov_enforcement.rule_bridge.gate_auto_registrar"

    @staticmethod
    def _guard_import(monkeypatch: pytest.MonkeyPatch, blocked: str) -> None:
        real_import = builtins.__import__

        def guarded(name, *args, **kwargs):
            if name == blocked:
                raise ImportError(f"simulated import crash: {name}")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", guarded)

    def _inject_gate_crash(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """gate 装载 import 崩形态：_get_gateway 把 ImportError（经 __import__ 注入）
        包成真 GateAutoRegistrationError——复刻 auto_register_gates 的 fail-closed 出口。"""
        sentinel = self._SENTINEL
        self._guard_import(monkeypatch, sentinel)

        def crash_get_gateway(self):
            try:
                __import__(sentinel)
            except ImportError as exc:
                raise GateAutoRegistrationError(f"gate 装载失败: {exc}") from exc
            raise AssertionError("哨兵注入失效")

        monkeypatch.setattr(cql.WorktreeLanding, "_get_gateway", crash_get_gateway)

    @pytest.mark.parametrize("probe", ["fail", "pass"])
    @pytest.mark.timeout(300)
    def test_import_crash_routed_by_m52_never_crashes_drain(
        self, tmp_repo: Path, rb_queue_root: Path, monkeypatch, probe: str
    ):
        """(c) import 崩主链：M5.2 分流两支——fresh fail=确定性册坏→死信带处方（阻断
        路径）；fresh pass=本进程纪元陈旧→退 pending（fail-open 路径）。两支都必然
        「drain 正常返回」（进程不崩），且各自的定态互斥。"""
        self._inject_gate_crash(monkeypatch)
        monkeypatch.setattr(
            cql.WorktreeLanding,
            "_probe_fresh_gate_registration",
            lambda self, timeout=120.0: (
                ("fail", "rc=1: simulated deterministic roster defect") if probe == "fail" else ("pass", "")
            ),
        )
        item = _enqueue(tmp_repo, rb_queue_root, "sess-imp", "imp.txt", "imp\n", "add imp")

        _prewarm_worktrees(tmp_repo, rb_queue_root, 2)
        stats = cql.drain_queue_pool(queue_root=rb_queue_root, repo_root=tmp_repo, workers=2)  # 不崩即过
        if probe == "fail":
            # 阻断支允许重试：读竞态（_read_item 整轮放弃→项回 pending）下补排一轮，
            # 终态必达死信；pass 支不可重试（每轮 env_retry+1，3 轮即误升死信）。
            for _ in range(3):
                if stats.get("dead", 0) >= 1 or not list((rb_queue_root / "pending").glob("q-*.json")):
                    break
                stats = cql.drain_queue_pool(queue_root=rb_queue_root, repo_root=tmp_repo, workers=2)

        if probe == "fail":
            # 阻断路径：死信 + 可行动处方（修册），绝不退 pending 无限自旋
            assert stats["dead"] == 1 and stats["done"] == 0, stats
            dead = json.loads((rb_queue_root / "dead" / f"{item['qid']}.json").read_text(encoding="utf-8"))
            assert dead.get("prescription"), "确定性册坏死信必须带处方"
            assert "gate" in (dead.get("dead_reason") or "") + (dead.get("prescription") or "")
        else:
            # fail-open 路径：退 pending 记账等自愈，绝不死信
            assert stats["done"] == 0 and stats["dead"] == 0, stats
            pend = json.loads((rb_queue_root / "pending" / f"{item['qid']}.json").read_text(encoding="utf-8"))
            env_retry = (pend.get("meta") or {}).get("env_retry")
            assert env_retry and env_retry >= 1, "env_retry 计数闸未记账"
            # 注：env_aborted 置旗前他工可再拾取同件一次，env_retry 允许 ≥1 的良性竞态
            assert env_retry <= 2, f"env_retry 异常膨胀: {env_retry}"

        # 链路存活面：撤掉全部注入后 drain 仍正常消化（不崩进程的实质验证）
        monkeypatch.undo()
        if probe == "pass":
            stats2 = _drain_until_done(tmp_repo, rb_queue_root)  # 原 pending 件自愈落地
            assert stats2["done"] == 1 and stats2["dead"] == 0, stats2
        else:
            _enqueue(tmp_repo, rb_queue_root, "sess-imp-after", "after.txt", "after\n", "add after")
            stats2 = _drain_until_done(tmp_repo, rb_queue_root)
            assert stats2["done"] == 1 and stats2["dead"] == 0, stats2

    @pytest.mark.timeout(300)
    def test_red_probe_routing_lost_gate_crash_stalls_in_pending(
        self, tmp_repo: Path, rb_queue_root: Path, monkeypatch
    ):
        """红证：M5.2 分流失存（_is_gate_auto_registration_error→False，旧码形态）→
        确定性册坏也走泛化 env 分支退 pending——「死信+处方」这把尺在旧形态必红
        （活锁形态：全队无限 pending 无可见病灶）。"""
        self._inject_gate_crash(monkeypatch)
        monkeypatch.setattr(
            cql.WorktreeLanding,
            "_probe_fresh_gate_registration",
            lambda self, timeout=120.0: ("fail", "rc=1: deterministic"),
        )
        monkeypatch.setattr(cql, "_is_gate_auto_registration_error", lambda exc: False)  # 拆分流
        item = _enqueue(tmp_repo, rb_queue_root, "sess-imp2", "imp2.txt", "imp2\n", "add imp2")

        _prewarm_worktrees(tmp_repo, rb_queue_root, 2)
        stats = cql.drain_queue_pool(queue_root=rb_queue_root, repo_root=tmp_repo, workers=2)

        assert stats["dead"] == 0, "分流失存后不应产生死信（旧形态＝pending 滞留）"
        assert stats["done"] == 0, stats
        assert (rb_queue_root / "pending" / f"{item['qid']}.json").exists(), "旧形态：确定性册坏滞留 pending"

    def test_import_facility_crash_falls_open_to_name_match(self, monkeypatch):
        """导入设施自身被断（__import__ 对 registrar 模块抛 ImportError）→
        _is_gate_auto_registration_error 按类型名 fail-open 兜底：判定不崩、分流不错。"""
        exc = GateAutoRegistrationError("boom")  # 先构造真实例（未断 import 时）
        self._guard_import(monkeypatch, self._REGISTRAR)
        assert cql._is_gate_auto_registration_error(exc) is True, "设施崩后同名兜底失效＝误分流"
        assert cql._is_gate_auto_registration_error(RuntimeError("plain")) is False, "兜底不得扩大命中面"
