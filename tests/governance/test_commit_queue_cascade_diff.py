# [A_test] module_id: MOD-GOV-047 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-047 | scripts/governance/commit_queue_landing.py + scripts/commit_queue.py | §D1 stats_lock 停世界临界区（docs/_working/commit_speedup_campaign/10_D1_D2/D1_stats_lock.md）
# [MODULE] tests.governance.test_commit_queue_cascade_diff
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; scripts.commit_queue; scripts.governance.commit_queue_landing; git CLI（HEAD 基线取证）
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/test_commit_queue_cascade_diff.py
# [MATURITY] testing
# [INVARIANTS] 全 tmp 隔离（tmp git 仓 + tmp 队列根，绝不碰生产 .runtime/commit_queue）；红测 R-D1-a/R-D1-b 先于修复证明能红（D1_stats_lock.md §6，结构断言非计时赌概率）；§5 差分自证=旧实现（git show HEAD 经 importlib 一次性命名空间）与盘面新实现双跑 12 场景×串/池四元对照，断言=四目录+影子文件名集合相等+键集双向差分+逐键值比对（白名单=*_at 墙钟戳族）+stats 计数与 processed_qids 集合全等+stale_by 首因全等；禁伪红测（只比成功/只比文件数/只比计数/sleep 造争用）；池腿确定性=FIFO 接力认领（claim n+1 等 claim n 项离开 processing），把交错窗关死使新旧两跑同序可比
# [MODIFY-GUARD] D1_stats_lock.md §6 红测方案 + §5 语义等价性自证方案；stale_by 首因审计（按落地序第一个命中者）在本文件被机械检验
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败；legacy 模块装载失败（git show/importlib）应显式报错而非静默跳过
# [TESTS] 本文件
# [TTL] permanent
"""test_commit_queue_cascade_diff.py — D1（stats_lock 停世界临界区）红测 + 差分自证。

真源：docs/_working/commit_speedup_campaign/10_D1_D2/D1_stats_lock.md §5/§6/§7。

- §6 红测（先证能红，再谈修复）：
  R-D1-a 结构断言——`_mark_cascade_stale`（或其 batch 继任者）与
  `_notify_task_board_dead_letter` 被调用时**不得持池级 stats_lock**
  （monkeypatch 函数体内检查追踪锁的 owner 线程，现码必红）；
  R-D1-b 扇出次数断言——「4 件落地 + 83 件 pending 同 base」的波内
  级联入口调用 ≤1 次/波（现码=4=落地次数，必红）且 pending 影子写入 ≤83 次。
  矿③ 影子化后「pending 重写」的介质=pending/.stale/<qid>.json 影子指令
  （袋体 append-only 零改写），故扇出计数锚在 `_write_stale_shadow`。
- §5 差分 harness：旧实现（HEAD 基线字节）× 新实现（盘面）× 串传送带 × k=4 池，
  12 场景矩阵；池腿用 FIFO 接力认领把线程交错窗关死（确定性串行流水线），
  否则同 base 件的处置取决于「认领 vs 落地」的线程时序，两跑不可比。
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import threading
import time
from pathlib import Path
from types import ModuleType

import pytest

import scripts.commit_queue as cq
import scripts.governance.commit_queue_landing as cql
from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import CommitResult, CommitStatus

#: 仓库根（git show 基线取证锚；测试文件位于 <repo>/tests/governance/ 下）
REPO_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# 基础工具（与 test_commit_queue_pool 同款约定：真 git tmp 仓 + tmp 队列根全隔离）
# ---------------------------------------------------------------------------


def _git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, timeout=60)
    if check and r.returncode != 0:
        raise AssertionError(
            f"git {' '.join(args)} -> rc={r.returncode}: stderr={r.stderr.decode('utf-8', errors='replace')[:400]}"
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
    (repo / ".gitignore").write_text(".runtime/\n", encoding="utf-8")
    (repo / "base.txt").write_text("base\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-qm", "init")
    _git(repo, "branch", "dev")
    return repo


@pytest.fixture()
def queue_root(tmp_path: Path) -> Path:
    return tmp_path / "commit_queue"


def _enqueue(repo: Path, qroot: Path, sid: str, rel: str, content: str, msg: str) -> dict:
    return cq.enqueue_item(
        sid,
        msg,
        [(rel, content.encode("utf-8"))],
        queue_root=qroot,
        options=cq.EnqueueOptions(base_head=_git_text(repo, "rev-parse", "refs/heads/dev")),
    )


class _StubGateway:
    """真 git commit 桩（门禁豁免）；fail_qids 命中提交信息内 qid 标记时抛普通异常=物品死信。"""

    def __init__(self, worktree_path: Path, fail_qids: set[str] | None = None) -> None:
        self._wt = worktree_path
        self._fail = fail_qids or set()

    def claim_files(self, session_id: str, files: list[str], adopt_prior_work: bool = False) -> list[str]:
        return list(files)

    def release_files(self, session_id: str, files: list[str]) -> None:
        pass

    def commit(self, session_id, files, message, **_kw):
        for q in self._fail:
            if q in message:
                raise RuntimeError(f"stub-fail:{q}")
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


def _inject_stub_workers(monkeypatch: pytest.MonkeyPatch, fail_qids: set[str] | None = None) -> None:
    real_make = cql.make_worker_landing

    def _make(repo, root, worker_id):
        landing = real_make(repo, root, worker_id)
        landing._gateway = _StubGateway(landing.worktree_path, fail_qids=fail_qids)
        return landing

    monkeypatch.setattr(cql, "make_worker_landing", _make)


def _cascade_entry_name() -> str:
    """级联入口分派：修复后=batch（单一实现入口），现码=_mark_cascade_stale。"""
    return "mark_cascade_stale_batch" if hasattr(cq, "mark_cascade_stale_batch") else "_mark_cascade_stale"


# ---------------------------------------------------------------------------
# 锁追踪 shim（R-D1-a 用）：替换 landing 模块命名空间内的 threading，
# 使波内创建的每把锁（stats_lock/路径锁）都可查「当前线程是否持有人」。
# 用 owner-tid 判定而非非阻塞 acquire——后者会把「他工恰持锁」误判成「本工持锁」。
# ---------------------------------------------------------------------------


class _TrackedLock:
    def __init__(self, lock) -> None:
        self._lock = lock
        self._owner: int | None = None

    def acquire(self, *a, **kw):
        got = self._lock.acquire(*a, **kw)
        if got:
            self._owner = threading.get_ident()
        return got

    def release(self):
        self._owner = None
        self._lock.release()

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, *exc):
        self.release()

    def owned_by_current(self) -> bool:
        return self._owner == threading.get_ident()


class _ThreadingShim:
    """代理 threading 模块：Lock() 换追踪锁，其余成员全透传（只影响 landing.py 命名空间）。"""

    def __init__(self, real: ModuleType) -> None:
        self._real = real
        self.locks: list[_TrackedLock] = []

    def Lock(self):
        lk = _TrackedLock(self._real.Lock())
        self.locks.append(lk)
        return lk

    def __getattr__(self, name):
        return getattr(self._real, name)


# ---------------------------------------------------------------------------
# §6 R-D1-a 结构断言：级联标记 / 死信通知被调用时不得持池级锁（现码必红）
# ---------------------------------------------------------------------------


class TestRD1AStructuralNoLock:
    def test_cascade_and_deadletter_called_outside_stats_lock(self, tmp_repo: Path, queue_root: Path, monkeypatch):
        """monkeypatch 级联入口与死信通知，在函数体内检查池波创建的锁：
        调用时刻**本线程不得持有任何一把**。现码 `_pool_process_item` 落账段
        `with stats_lock:` 内调 `_mark_cascade_stale` 与 `_notify_task_board_dead_letter`
        → owner=本工线程 → 必红；修复后（出锁+波末批标记）→ 绿。"""
        ok_item = _enqueue(tmp_repo, queue_root, "sess-ok", "ok.txt", "OK\n", "land me")
        dead_item = _enqueue(tmp_repo, queue_root, "sess-dead", "dead.txt", "DEAD\n", "fail me")
        _inject_stub_workers(monkeypatch, fail_qids={dead_item["qid"]})

        shim = _ThreadingShim(threading)
        monkeypatch.setattr(cql, "threading", shim)

        entry_name = _cascade_entry_name()
        real_entry = getattr(cq, entry_name)
        real_notify = cq._notify_task_board_dead_letter
        entry_snaps: list[list[bool]] = []
        notify_snaps: list[list[bool]] = []

        def spy_entry(root, *a, **kw):
            entry_snaps.append([lk.owned_by_current() for lk in shim.locks])
            return real_entry(root, *a, **kw)

        def spy_notify(item):
            notify_snaps.append([lk.owned_by_current() for lk in shim.locks])
            return real_notify(item)

        monkeypatch.setattr(cq, entry_name, spy_entry)
        monkeypatch.setattr(cq, "_notify_task_board_dead_letter", spy_notify)

        stats = cql.drain_queue_pool(queue_root=queue_root, repo_root=tmp_repo, workers=2)

        assert stats["done"] == 1 and stats["dead"] == 1, stats  # 两支都必须真实走到
        assert entry_snaps, "级联入口未被调用——注入未生效（测试无判别力）"
        assert notify_snaps, "死信通知未被调用——注入未生效（测试无判别力）"
        held_at_entry = [i for snap in entry_snaps for i, held in enumerate(snap) if held]
        held_at_notify = [i for snap in notify_snaps for i, held in enumerate(snap) if held]
        assert not held_at_entry, (
            f"D1 缺陷在场：级联标记（{entry_name}）被调用时本工线程仍持池级锁 "
            f"（持锁锁序号={held_at_entry}/{len(shim.locks)} 把追踪锁）——停世界临界区未拆"
        )
        assert not held_at_notify, (
            f"D1 缺陷在场：死信通知 _notify_task_board_dead_letter 被调用时本工线程仍持池级锁 "
            f"（持锁锁序号={held_at_notify}）——sqlite 通知在临界区内"
        )


# ---------------------------------------------------------------------------
# §6 R-D1-b 扇出次数断言：级联入口 1 次/波 + pending 影子写入 ≤83（现码必红）
# ---------------------------------------------------------------------------


class TestRD1BFanoutOncePerWave:
    def test_wave_marks_batch_once_with_bounded_pending_writes(self, tmp_repo: Path, queue_root: Path, monkeypatch):
        """「4 件落地 + 83 件 pending 同 base」：修复后波内级联入口恰 1 次、
        影子写入 ≤83（每波一遍）；现码=每落地一次入口（4 次）必红。
        影子写入（`_write_stale_shadow` 成功返回）即矿③ 后「pending 重写」的计数介质。"""
        base = _git_text(tmp_repo, "rev-parse", "refs/heads/dev")
        land_qids: list[str] = []
        for i in range(4):
            it = cq.enqueue_item(
                f"sess-land{i}",
                f"land {i}",
                [(f"land{i}.txt", f"content {i}\n".encode())],
                queue_root=queue_root,
                options=cq.EnqueueOptions(base_head=base),
            )
            land_qids.append(it["qid"])
        for i in range(83):
            cq.enqueue_item(
                f"sess-p{i:02d}",
                f"pend {i}",
                [(f"p{i:02d}.txt", f"p {i}\n".encode())],
                queue_root=queue_root,
                options=cq.EnqueueOptions(base_head=base),  # 与落地 4 件同 base → 全命中
            )
        _inject_stub_workers(monkeypatch)

        entry_name = _cascade_entry_name()
        real_entry = getattr(cq, entry_name)
        real_shadow = cq._write_stale_shadow
        counts = {"entry": 0, "shadow": 0}

        def spy_entry(root, *a, **kw):
            counts["entry"] += 1
            return real_entry(root, *a, **kw)

        def spy_shadow(root, qid, stale_by, trigger):
            ok = real_shadow(root, qid, stale_by, trigger)
            if ok:
                counts["shadow"] += 1
            return ok

        monkeypatch.setattr(cq, entry_name, spy_entry)
        monkeypatch.setattr(cq, "_write_stale_shadow", spy_shadow)

        stats = cql.drain_queue_pool(queue_root=queue_root, repo_root=tmp_repo, workers=4, max_items=4)

        assert stats["done"] == 4, stats  # 恰一波落地 4 件
        assert counts["entry"] <= 1, (
            f"D1 缺陷在场：波内级联入口（{entry_name}）被调 {counts['entry']} 次"
            f"（=落地次数）——O(N) 扫描扇出未批量化（每落地一遍全量扫描）"
        )
        assert counts["shadow"] <= 83, f"pending 重写扇出超界：影子写入 {counts['shadow']} 次 > 83（每波一遍上限）"
        assert counts["shadow"] == 83, f"影子写入应恰 83（83 件同 base 全命中）: {counts}"


# ---------------------------------------------------------------------------
# §5 差分自证 harness：旧实现（git HEAD 基线）× 新实现（盘面）× 串 × 池
# ---------------------------------------------------------------------------

_LEGACY: tuple[ModuleType, ModuleType] | None = None


def _exec_git_module(src: str, origin: str, name: str) -> ModuleType:
    """一次性命名空间装载（不进 sys.path、不污染真实模块名；dataclass 需 sys.modules 登记）。

    `__file__` 指向真源盘面路径——HEAD 源模块级 `Path(__file__)`（sys.path 补根）依赖它。"""
    mod = importlib.util.module_from_spec(importlib.util.spec_from_loader(name, loader=None))
    sys.modules[name] = mod
    mod.__dict__["__file__"] = str(REPO_ROOT / origin)
    exec(compile(src, f"<git-head:{origin}>", "exec"), mod.__dict__)  # noqa: S102 - 蓝本 §5 指定装法
    return mod


def _legacy_impls() -> tuple[ModuleType, ModuleType]:
    """旧实现=HEAD 基线字节（git show 经 importlib）；旧 landing 必须绑旧 cq（配对完整）。"""
    global _LEGACY
    if _LEGACY is None:
        cq_src = subprocess.run(
            ["git", "show", "HEAD:scripts/commit_queue.py"],
            capture_output=True,
            check=True,
            timeout=60,
            cwd=str(REPO_ROOT),
        ).stdout.decode("utf-8")
        cql_src = subprocess.run(
            ["git", "show", "HEAD:scripts/governance/commit_queue_landing.py"],
            capture_output=True,
            check=True,
            timeout=60,
            cwd=str(REPO_ROOT),
        ).stdout.decode("utf-8")
        old_cq = _exec_git_module(cq_src, "scripts/commit_queue.py", "_d1_legacy_commit_queue")
        old_cql = _exec_git_module(
            cql_src, "scripts/governance/commit_queue_landing.py", "_d1_legacy_commit_queue_landing"
        )
        old_cql.cq = old_cq
        _LEGACY = (old_cq, old_cql)
    return _LEGACY


class _TimeShim:
    """代理 time 模块：级联 F1 飞行窗睡眠（≤60ms）确定性跳过，其余透传。

    动机：`_mark_cascade_stale` 每命中睡 50ms 后二扫清理「认领飞行中」件的影子——
    该清理与接力认领的相对推进是纯墙钟赛跑，两跑结果天然不可比（实测同码两跑
    stale_cleared 17 vs 18）。两实现**同装同跳**（介质逻辑零改动，只拆墙钟耦合）
    ⇒ 影子写定即存活，标记结果由认领序唯一决定。F1 真实时序行为由必绿套件
    （无 shim 环境）覆盖，不在本差分断言面内。"""

    def __init__(self, real: ModuleType, skip_max: float = 0.06) -> None:
        self._real = real
        self._skip_max = skip_max

    def sleep(self, seconds: float) -> None:
        if seconds <= self._skip_max:
            return
        return self._real.sleep(seconds)

    def __getattr__(self, name):
        return getattr(self._real, name)


def _install_time_shim(cqmod: ModuleType) -> ModuleType:
    saved = cqmod.time
    cqmod.time = _TimeShim(saved)
    return saved


class _FakeCompleted:
    def __init__(self, returncode: int, stdout: bytes) -> None:
        self.returncode = returncode
        self.stdout = stdout


class _DiffLanding:
    """纯桩落地执行体（零 git worktree）：_pool_process_item/drain_queue 所需最小面。"""

    def __init__(self, anchor: Path, cqmod: ModuleType, head_sha: str | None = None, **_kw) -> None:
        self.worktree_path = anchor  # _emit_landing_phase_stat 落账锚（tmp 内）
        self.target_branch = "dev"
        self._cq = cqmod
        self._head_sha = head_sha

    def _item_paths(self, item: dict) -> set[str]:
        return {f.get("path", "") for f in (item.get("files") or []) if f.get("path")}

    def _git_repo(self, *args: str, **_kw) -> _FakeCompleted:
        if self._head_sha and args and args[0] == "rev-parse" and len(args) > 1 and ":" in args[1]:
            return _FakeCompleted(0, (self._head_sha + "\n").encode("utf-8"))
        return _FakeCompleted(1, b"")

    def __call__(self, item: dict, root: Path):
        return self._cq.LandingResult(ok=True, landed_id=f"stub:{item.get('qid', '')}")


def _install_pool_stubs(cqlmod: ModuleType, anchor: Path, cqmod: ModuleType, head_sha: str | None, hooks=None):
    """池工落地执行体桩化 + FIFO 接力认领（确定性串行流水线，关死交错窗）。

    接力语义：claim#(n+1) 等 claim#(n) 的项**离开 processing**（done/dead/退回 pending
    皆算离场）才认领下一项——任一时刻至多一项在途，且第 n 项的认领-判定时刻之前
    恰有 n-1 次落地完成。新旧两跑同序 ⇒ 同 base 件的 stale 处置逐场对应可比。
    hooks: {前一项文件名 -> callable(root)}——该前项离场静默窗结束后执行一次
    （场景 8/9 的「候选被 compaction 移走」外部事件注入位）。"""
    saved = {"make": cqlmod.make_worker_landing, "claim": cqlmod._pool_claim_item}
    orig_claim = saved["claim"]
    cv = threading.Condition()
    state: dict = {"next_ticket": 0, "items": {}}

    def make(repo, root, worker_id, **kw):
        return _DiffLanding(anchor, cqmod, head_sha=head_sha, **kw)

    def relay_claim(root: Path):
        with cv:
            t = state["next_ticket"]
            state["next_ticket"] += 1
            if t > 0:
                # 等上一认领**记录在案**（返回并登记其项/空）——缺记录=尚未返回，必须等；
                # （不能用「claims_done>=t-1」做闸：t=1 时 0>=0 恒真，会抢在 t0 返回前
                # 读到缺记录并误判「上一认领无项」而直接放行——实测 16ms 内全队列认领完）
                deadline_cv = time.monotonic() + 60
                while (t - 1) not in state["items"]:
                    if time.monotonic() > deadline_cv:
                        raise AssertionError(f"relay 断链：认领#{t - 1} 60s 未返回")
                    cv.wait(timeout=1.0)
            prev = state["items"].get(t - 1)
        if prev is not None:
            deadline = time.monotonic() + 60
            while time.monotonic() < deadline:
                if not (root / "processing" / prev).exists():
                    break  # done/dead/退回 pending——任一离场形态
                time.sleep(0.005)
            else:
                raise AssertionError(f"relay 断链：前一项 {prev} 60s 未离场")
            # 离场≠落定：终态 rename 之后同函数内还有级联标记/索引记账（旧=锁内
            # _mark_cascade_stale，新=landed_index append）——微秒级尾段。给 50ms
            # 静默窗，令下一认领的 stale 判定恰见前一落地的完整效果（新旧同序可比）。
            time.sleep(0.05)
            if prev is not None and hooks and prev in hooks:
                hooks[prev](root)
        p = orig_claim(root)
        with cv:
            state["items"][t] = p.name if p is not None else None
            cv.notify_all()
        return p

    cqlmod.make_worker_landing = make
    cqlmod._pool_claim_item = relay_claim
    return saved


def _write_items(root: Path, specs: list[dict]) -> None:
    """直写 pending 项（绕开 enqueue 的墙钟/seq 面——输入逐字节确定）。"""
    pending = root / "pending"
    pending.mkdir(parents=True, exist_ok=True)
    for i, s in enumerate(specs):
        item: dict = {
            "qid": s["qid"],
            "session_id": s.get("sid", "sess-d1"),
            "message": s.get("msg", "d1-diff"),
            "created_at": f"2026-01-01T00:00:{i:02d}+00:00",
            "files": s["files"],
            "meta": s.get("meta", {}),
        }
        if s.get("base_head") is not None:
            item["base_head"] = s["base_head"]
        (pending / f"{s['qid']}.json").write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")


def _q(i: int) -> str:
    return f"q-20260101-d1-{i:04d}"


def _f(path: str, base_blob: str | None = None) -> dict:
    d = {"path": path}
    if base_blob:
        d["base_blob"] = base_blob
    return d


# 易变字段白名单（逐条理由）：凡叶子键以 _at 结尾皆为墙钟戳——created_at/landed_at/
# dead_at（蓝本 §5 明列）+ stale_at/stale_cleared_at/first_dead_at（影子注入/清标放行/
# 死信封印的当场时刻，两跑墙钟必然不同，语义位由 stale_by/dead_reason 等确定性字段承载）。
def _is_volatile(key: str) -> bool:
    return key.endswith("_at")


def _diff_value(prefix: str, a, b: object, diffs: list[str]) -> None:
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                diffs.append(f"{prefix}.{k} old=<缺失> new={b[k]!r}")  # 键集双向差分：new-only
            elif k not in b:
                diffs.append(f"{prefix}.{k} old={a[k]!r} new=<缺失>")  # 键集双向差分：old-only
            elif _is_volatile(k):
                continue  # 白名单内：墙钟戳不比
            else:
                _diff_value(f"{prefix}.{k}", a[k], b[k], diffs)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            diffs.append(f"{prefix} 列长 old={len(a)} new={len(b)}")
        else:
            for i, (x, y) in enumerate(zip(a, b, strict=True)):
                _diff_value(f"{prefix}[{i}]", x, y, diffs)
    elif a != b:
        diffs.append(f"{prefix} old={a!r} new={b!r}")


def _read_json_loose(p: Path) -> dict:
    """容错读：损坏 JSON/目录候选（场景 8/9 的盘面残留）按原样字节/形态进对照——
    两跑残留逐字节相同 ⇒ 以哨兵形态参与差分，不因解析失败崩采集。"""
    if p.is_dir():
        return {"__dir__": True}
    raw = p.read_text(encoding="utf-8", errors="replace")
    try:
        return json.loads(raw)
    except ValueError:
        return {"__raw__": raw}


def _collect_state(root: Path) -> dict:
    state: dict = {"dirs": {}, "shadows": {}}
    for d in ("pending", "processing", "done", "dead"):
        state["dirs"][d] = {p.name: _read_json_loose(p) for p in sorted((root / d).glob("q-*.json"))}
    sd = root / "pending" / ".stale"
    if sd.is_dir():
        state["shadows"] = {p.name: _read_json_loose(p) for p in sorted(sd.glob("*.json"))}
    return state


def _run_one(cqmod: ModuleType, cqlmod: ModuleType, scenario: dict, base: Path) -> dict:
    root = base / "queue"
    _write_items(root, scenario["items"])
    setup = scenario.get("setup")
    if setup is not None:
        setup(root)
    head_sha = scenario.get("head_sha")
    saved_time = _install_time_shim(cqmod)  # F1 墙钟窗确定性化（新旧同装，见 _TimeShim）
    try:
        if scenario["path"] == "serial":
            landing = _DiffLanding(base, cqmod, head_sha=head_sha)
            head_reader = (lambda rel: head_sha) if head_sha else None
            stats = cqmod.drain_queue(root, landing=landing, head_reader=head_reader)
        else:
            saved = _install_pool_stubs(cqlmod, base, cqmod, head_sha, hooks=scenario.get("hooks"))
            try:
                stats = cqlmod.drain_queue_pool(
                    queue_root=root,
                    repo_root=base,
                    workers=4,
                    max_items=scenario.get("max_items"),
                )
            finally:
                cqlmod.make_worker_landing = saved["make"]
                cqlmod._pool_claim_item = saved["claim"]
    finally:
        cqmod.time = saved_time
    return {"stats": stats, "state": _collect_state(root)}


def _assert_equivalent(scenario_name: str, old: dict, new: dict) -> None:
    diffs: list[str] = []
    for d, files in old["state"]["dirs"].items():
        new_files = new["state"]["dirs"][d]
        old_only = sorted(set(files) - set(new_files))
        new_only = sorted(set(new_files) - set(files))
        if old_only or new_only:
            diffs.append(f"{d}/ 文件名集合差分 old-only={old_only} new-only={new_only}")
            continue
        for name in sorted(files):
            _diff_value(f"{d}/{name}", files[name], new_files[name], diffs)
    old_sh, new_sh = old["state"]["shadows"], new["state"]["shadows"]
    # 影子比对（方向性容忍，逐条理由）：已消费件（done/dead）名下的影子是标记介质的
    # 遗留物——旧介质（落地临界区即时写影）在池死信出口遗留孤儿影（pool dead 支不清理、
    # `_sweep_orphan_stale_shadows` 终态核对又护其不被清扫）；新介质（内存索引+波末批）
    # 对已消费件天然无影。其语义负载（stale/stale_by 视图）已随袋持久化进终态袋体 meta
    # （上面四目录逐键比对已覆盖），影文件对已消费件无行为意义（_read_item 只读
    # pending/processing）。故：已消费件名下 old-only 容忍（介质演进自然差）、new-only
    # 照红（幽灵标记）；pending 件名下的影子全严比对（活语义：stale_by 首因审计）。
    consumed = set(old["state"]["dirs"]["done"]) | set(old["state"]["dirs"]["dead"])
    for name in sorted(set(old_sh) | set(new_sh)):
        in_old, in_new = name in old_sh, name in new_sh
        prefix = f"pending/.stale/{name}"
        if name in consumed:
            if in_new and not in_old:
                diffs.append(f"{prefix} 已消费件幽灵影 new-only（旧介质无此影）")
            elif in_old and in_new:
                _diff_value(prefix, old_sh[name], new_sh[name], diffs)
            # old-only：旧介质遗留孤儿影——容忍（理由见上）
        else:
            if in_old != in_new:
                diffs.append(f"{prefix} pending 件影子集合差分 old-only={not in_new} new-only={not in_old}")
            elif in_old:
                _diff_value(prefix, old_sh[name], new_sh[name], diffs)
    for key in ("cascade_marked", "done", "dead", "stale_cleared"):
        if old["stats"][key] != new["stats"][key]:
            diffs.append(f"stats[{key}] old={old['stats'][key]} new={new['stats'][key]}")
    if sorted(old["stats"]["processed_qids"]) != sorted(new["stats"]["processed_qids"]):
        diffs.append(
            f"stats[processed_qids] 集合差分 old={sorted(old['stats']['processed_qids'])} "
            f"new={sorted(new['stats']['processed_qids'])}"
        )
    assert not diffs, f"[{scenario_name}] 新旧实现语义差分（{len(diffs)} 处）:\n" + "\n".join(diffs)


def _scenario_base(n: int, base: str, **kw) -> dict:
    kw.setdefault("files", [_f(f"f{n}.txt")])
    kw.setdefault("qid", _q(n))
    kw.setdefault("base_head", base)
    return kw


def _build_scenarios() -> dict[str, dict]:
    """§5 场景矩阵 12 例（蓝本逐条）。head_sha 给出时=重校验必不适（mismatch→死信）。"""
    sc: dict[str, dict] = {}

    def item(qn: int, base: str | None, **kw) -> dict:
        return _scenario_base(qn, base, **kw)

    # (1) 全部同 base（最坏扇出，N=20）
    sc["01_all_same_base_n20"] = {
        "items": [item(i, "B-SAME") for i in range(20)],
        "path": "both",
    }
    # (2) 全部不相交 base（零命中）
    sc["02_disjoint_bases"] = {
        "items": [item(i, f"B-UNIQ-{i}") for i in range(6)],
        "path": "both",
    }
    # (3) 分组 base（3 组，含单件组）
    sc["03_grouped_bases"] = {
        "items": [
            item(0, "G-A"),
            item(1, "G-A"),
            item(2, "G-B"),
            item(3, "G-B"),
            item(4, "G-B"),
            item(5, "G-C"),  # 单件组
        ],
        "path": "both",
    }
    # (4) depends_on 命中 + base 不命中（depends_on 无 base_head）
    sc["04_depends_hit_base_miss"] = {
        "items": [
            item(0, None),
            item(1, None, meta={"depends_on": [_q(0)]}),
        ],
        "path": "both",
    }
    # (5) depends 与 base 同时命中（验 stale_by 首因=按落地序第一个命中者）
    sc["05_dual_hit_first_cause"] = {
        "items": [
            item(0, "B-5A"),
            item(1, "B-5B"),
            item(2, "B-5A", meta={"depends_on": [_q(1)]}),  # base 命中 X0（先落），depends 命中 X1
            item(3, "B-5B", meta={"depends_on": [_q(1)]}),  # base+depends 同源 X1
        ],
        "path": "both",
    }
    # (6) 交错认领：A 已落地、波末 flush 之前 B 被认领（专证 §4.4 盘旗∪内存 index）
    #     B 带 base_blob 且 head_reader 恒异 → 重校验不适 → cascade_stale 死信；
    #     若 §4.4 缺失（未重校验即落 dev）B 会进 done/ → 目录级差分必红。
    sc["06_interleaved_claim_revalidate"] = {
        "items": [
            item(0, "B-6", files=[_f("x6.txt")]),
            item(1, "B-6", files=[_f("y6.txt", "blob-b6")]),
        ],
        "head_sha": "head-moved-on",
        "path": "both",
    }

    # (7) 候选项已 stale（袋旧位 + 影子旁路）：不重标、stale_by 不被覆写
    def _setup_07(root: Path) -> None:
        sd = root / "pending" / ".stale"
        sd.mkdir(parents=True, exist_ok=True)
        (sd / f"{_q(2)}.json").write_text(
            json.dumps(
                {
                    "qid": _q(2),
                    "stale": True,
                    "stale_by": "pre-shadow",
                    "stale_at": "2026-01-01T00:00:00+00:00",
                    "trigger": "base_head",
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    sc["07_pre_stale_candidates"] = {
        "items": [
            item(0, "B-7"),
            item(1, "B-7", meta={"stale": True, "stale_by": "pre-bag"}),  # 袋旧位已标
            item(2, "B-7"),  # 影子已标（setup 写入）
            item(3, "B-7"),  # 新鲜——唯一会被级联标记的
        ],
        "setup": _setup_07,
        "path": "both",
    }

    # (8) 候选项 JSON 损坏（ValueError 跳过口径）。池腿经 relay hook 在 X0 离场后把
    #     损坏件「compaction 移走」——池车道对不可读件会无限认领-退回循环（预算退还
    #     再生），无自然收工点，故外部移走（串腿保留自然 break 口径：读失败退回即断）。
    def _hook_rm(base_name: str, victim: str):
        def _rm(root: Path):
            p = root / "pending" / victim
            try:
                p.unlink()
            except OSError:
                pass

        return _rm

    sc["08_corrupt_candidate"] = {
        "items": [item(0, "B-8"), item(1, "B-8")],
        "setup": lambda root: (root / "pending" / f"{_q(9)}.json").write_text("{corrupt", encoding="utf-8"),
        "hooks": {f"{_q(0)}.json": _hook_rm(f"{_q(0)}.json", f"{_q(9)}.json")},
        "path": "both",
    }

    # (9) 候选项在扫描中消失（FileNotFoundError/OSError 跳过口径的确定性替身：目录候选
    #     匹配 glob 但 read_text 恒 OSError——与 FileNotFoundError 同落 except (OSError, ValueError)）
    def _hook_rmdir(_base_name: str, victim: str):
        def _rm(root: Path):
            import shutil as _sh

            p = root / "pending" / victim
            try:
                _sh.rmtree(p, ignore_errors=True)
            except OSError:
                pass

        return _rm

    sc["09_vanished_candidate"] = {
        "items": [item(0, "B-9"), item(1, "B-9")],
        "setup": lambda root: (root / "pending" / f"{_q(9)}.json").mkdir(),
        "hooks": {f"{_q(0)}.json": _hook_rmdir(f"{_q(0)}.json", f"{_q(9)}.json")},
        "path": "both",
    }
    # (10) 超大件（生产实测 max=15KB）
    sc["10_oversize_item"] = {
        "items": [
            item(0, "B-10"),
            item(1, "B-10", msg="m" * 15360),
        ],
        "path": "both",
    }
    # (11) 含 deletes 通道件
    sc["11_deletes_channel"] = {
        "items": [
            item(0, "B-11", files=[{"path": "gone11.txt", "action": "delete"}]),
            item(1, "B-11"),
        ],
        "path": "both",
    }
    # (12) N=1（回归锚）
    sc["12_single_item"] = {"items": [item(0, "B-12")], "path": "both"}
    return sc


def _iter_impl_pairs():
    old_cq, old_cql = _legacy_impls()
    yield ("legacy(HEAD)", old_cq, old_cql)
    yield ("current(盘面)", cq, cql)


class TestCascadeSemanticDifferential:
    """§5：12 场景 ×（串传送带 / k=4 池）×（HEAD 基线 / 盘面），四元对照逐场差分。"""

    @pytest.mark.parametrize("scenario_name", sorted(_build_scenarios().keys()))
    def test_scenario_serial_and_pool(self, tmp_path: Path, scenario_name: str) -> None:
        scenario = _build_scenarios()[scenario_name]
        runs: dict[str, dict[str, dict]] = {"serial": {}, "pool": {}}
        for label, cqmod, cqlmod in _iter_impl_pairs():
            for kind in ("serial", "pool"):
                runs[kind][label] = _run_one(
                    cqmod, cqlmod, {**scenario, "path": kind}, tmp_path / f"{kind}-{label.split('(')[0]}"
                )
        for kind in ("serial", "pool"):
            old = runs[kind]["legacy(HEAD)"]
            new = runs[kind]["current(盘面)"]
            _assert_equivalent(f"{scenario_name}/{kind}", old, new)

    @pytest.mark.parametrize("kind", ["serial", "pool"])
    def test_scenario06_interleaved_claim_must_revalidate(self, tmp_path: Path, kind: str) -> None:
        """§4.4 专项：交错认领件 B 的最终处置必须=重校验分岔（本构造→cascade_stale 死信），
        绝不允许「B 未重校验即落 dev」。对盘面新实现直接断言（不依赖与旧实现的对照）。"""
        scenario = _build_scenarios()["06_interleaved_claim_revalidate"]
        cqmod, cqlmod = cq, cql
        result = _run_one(cqmod, cqlmod, {**scenario, "path": kind}, tmp_path / f"s06-{kind}")
        state = result["state"]
        done_names = set(state["dirs"]["done"])
        dead_names = set(state["dirs"]["dead"])
        assert f"{_q(1)}.json" in dead_names, (
            f"[{kind}] B 未走 stale 重校验分岔（dead/ 无 B）：done={sorted(done_names)}"
        )
        assert f"{_q(1)}.json" not in done_names, f"[{kind}] B 未经重校验即落 dev（§4.4 不变式破口）"
        assert "cascade_stale" in state["dirs"]["dead"][f"{_q(1)}.json"]["dead_reason"]
        assert f"{_q(0)}.json" in done_names and len(done_names) == 1
