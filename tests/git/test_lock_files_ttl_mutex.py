# [A_test] test_id=ARCH-AICOLLAB-001-57 | module=scripts/lock_files.py | gate=pytest
# [BLUEPRINT] MOD-INF-005 | scripts/lock_files.py | §7.28+§11.2.2
# [TESTS] tests/git/test_lock_files_ttl_mutex.py
# [TTL] task_bound
"""65 memo #57 验收测试: lock_files.py TTL 扩展（§11.2.2 五命令）+ §7.28 Mutex 原子写.

验证场景（对应 65 memo §8.4 验收矩阵）:
1. acquire 默认 TTL=1800s（trae_001 ttl_design 真源），owner.json/registry 写 expires_at
2. acquire --ttl 60 自定义 TTL → expires_at = timestamp + 3600
3. TTL 到期后 check 自动清理（§8.4: acquire --ttl 后超时 check → FREE）
4. 过期锁可被他人 acquire（stale 清理后获得）
5. 未过期锁拒绝他人 / 同人重入 OK
6. 旧格式锁（无 expires_at）回退 timestamp+DEFAULT_TTL_S 判定
7. list --session 过滤（§11.2.2 五命令）
8. 26 线程并发 acquire/release registry.json 无损坏无丢锁（§7.28 + §8.4）
9. Mutex 超时（5s 未获得）→ acquire DENIED 且回滚锁目录（无半锁状态）
"""

from __future__ import annotations

import contextlib
import io
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

# 确保 scripts/ 在 sys.path（tests/git/ 需 3 级 parent）
SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import lock_files  # noqa: E402


@pytest.fixture
def isolated_lock_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """隔离 LOCK_ROOT/REGISTRY_PATH 到 tmp，避免污染真仓 .ailocks。"""
    lock_root = tmp_path / ".ailocks"
    monkeypatch.setattr(lock_files, "LOCK_ROOT", lock_root)
    monkeypatch.setattr(lock_files, "REGISTRY_PATH", lock_root / "registry.json")
    return lock_root


def _run(func, *args, **kwargs) -> tuple[int, str]:
    """执行 cmd_* 并捕获 stdout，返回 (exit_code, output)。"""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = func(*args, **kwargs)
    return rc, buf.getvalue()


def _registry(lock_root: Path) -> dict:
    return json.loads((lock_root / "registry.json").read_text(encoding="utf-8"))


def _owner(lock_root: Path, file_path: str) -> dict:
    owner_file = lock_files._owner_file(lock_files._lock_dir(file_path))
    return json.loads(owner_file.read_text(encoding="utf-8"))


# ── 1. 默认 TTL（真源 1800s）──
def test_acquire_default_ttl_writes_expires_at(isolated_lock_root: Path) -> None:
    before = time.time()
    rc, out = _run(lock_files.cmd_acquire, "docs/a.md", "sess-1", options=lock_files.AcquireOptions(skip_naming_check=True))
    after = time.time()
    assert rc == 0, out
    assert "ACQUIRED" in out

    owner = _owner(isolated_lock_root, "docs/a.md")
    assert owner["ttl_s"] == lock_files.DEFAULT_TTL_S == 1800.0
    assert before + 1800.0 <= owner["expires_at"] <= after + 1800.0

    reg_entry = _registry(isolated_lock_root)["locks"]["docs/a.md"]
    # owner.json 与 registry 各自取 time.time()，允许亚秒级差异
    assert abs(reg_entry["expires_at"] - owner["expires_at"]) < 1.0


# ── 2. 自定义 --ttl（分钟）──
def test_acquire_custom_ttl(isolated_lock_root: Path) -> None:
    before = time.time()
    rc, out = _run(lock_files.cmd_acquire, "docs/b.md", "sess-1", options=lock_files.AcquireOptions(skip_naming_check=True, ttl_minutes=60.0))
    after = time.time()
    assert rc == 0, out
    assert "TTL: 60 分钟" in out

    owner = _owner(isolated_lock_root, "docs/b.md")
    assert owner["ttl_s"] == 3600.0
    assert before + 3600.0 <= owner["expires_at"] <= after + 3600.0


# ── 3. TTL 到期 check 自动清理（§8.4 验收行）──
def test_expired_lock_auto_cleaned_on_check(isolated_lock_root: Path) -> None:
    rc, _ = _run(lock_files.cmd_acquire, "docs/c.md", "sess-1", options=lock_files.AcquireOptions(skip_naming_check=True, ttl_minutes=0.01))  # 0.6s
    assert rc == 0
    time.sleep(0.8)

    rc, out = _run(lock_files.cmd_check, "docs/c.md")
    assert rc == 0, out
    assert "FREE" in out and "死锁已被自动清理" in out
    assert not lock_files._lock_dir("docs/c.md").is_dir()
    assert "docs/c.md" not in _registry(isolated_lock_root).get("locks", {})


# ── 4. 过期锁可被他人 acquire ──
def test_expired_lock_reacquired_by_other(isolated_lock_root: Path) -> None:
    rc, _ = _run(lock_files.cmd_acquire, "docs/d.md", "sess-1", options=lock_files.AcquireOptions(skip_naming_check=True, ttl_minutes=0.01))
    assert rc == 0
    time.sleep(0.8)

    rc, out = _run(lock_files.cmd_acquire, "docs/d.md", "sess-2", options=lock_files.AcquireOptions(skip_naming_check=True))
    assert rc == 0, out
    assert _owner(isolated_lock_root, "docs/d.md")["owner_id"] == "sess-2"


# ── 5. 未过期锁拒绝他人 / 同人重入 ──
def test_fresh_lock_denies_other_and_allows_reentry(isolated_lock_root: Path) -> None:
    rc, _ = _run(lock_files.cmd_acquire, "docs/e.md", "sess-1", options=lock_files.AcquireOptions(skip_naming_check=True, ttl_minutes=30))
    assert rc == 0

    rc, out = _run(lock_files.cmd_acquire, "docs/e.md", "sess-2", options=lock_files.AcquireOptions(skip_naming_check=True))
    assert rc == 1 and "DENIED" in out and "sess-1" in out

    rc, out = _run(lock_files.cmd_acquire, "docs/e.md", "sess-1", options=lock_files.AcquireOptions(skip_naming_check=True))
    assert rc == 0 and "重入" in out


# ── 6. 旧格式锁（无 expires_at）回退 DEFAULT_TTL_S 判定 ──
def test_legacy_lock_without_expires_at_fallback(isolated_lock_root: Path) -> None:
    lock_dir = lock_files._lock_dir("docs/legacy.md")
    lock_dir.mkdir(parents=True)
    stale_owner = {
        "owner_id": "sess-old",
        "pid": None,  # 无 PID → 跳过存活检查，纯 TTL 判定
        "timestamp": time.time() - lock_files.DEFAULT_TTL_S - 10,
        "task": "",
    }
    lock_files._owner_file(lock_dir).write_text(json.dumps(stale_owner), encoding="utf-8")
    assert lock_files._is_stale(lock_dir) is True

    fresh_owner = dict(stale_owner, timestamp=time.time())
    lock_files._owner_file(lock_dir).write_text(json.dumps(fresh_owner), encoding="utf-8")
    assert lock_files._is_stale(lock_dir) is False


# ── 7. list --session 过滤（§11.2.2 五命令）──
def test_list_session_filter(isolated_lock_root: Path) -> None:
    _run(lock_files.cmd_acquire, "docs/f1.md", "sess-1", options=lock_files.AcquireOptions(skip_naming_check=True))
    _run(lock_files.cmd_acquire, "docs/f2.md", "sess-1", options=lock_files.AcquireOptions(skip_naming_check=True))
    _run(lock_files.cmd_acquire, "docs/f3.md", "sess-2", options=lock_files.AcquireOptions(skip_naming_check=True))

    rc, out = _run(lock_files.cmd_list)
    assert rc == 0 and "3 个文件锁" in out and "剩余" in out

    rc, out = _run(lock_files.cmd_list, "sess-1")
    assert "2 个文件锁" in out and "docs/f1.md" in out and "docs/f3.md" not in out

    rc, out = _run(lock_files.cmd_list, "sess-nobody")
    assert rc == 0 and "CLEAN" in out


# ── 8. 26 线程并发 acquire/release：registry 无损坏无丢锁（§7.28 + §8.4）──
def test_registry_concurrent_no_lost_locks(isolated_lock_root: Path) -> None:
    sessions = [f"sess-{i:02d}" for i in range(26)]
    files = [f"docs/concurrent/{s}.md" for s in sessions]

    with ThreadPoolExecutor(max_workers=26) as pool:
        results = list(
            pool.map(
                lambda i: _run(
                    lock_files.cmd_acquire, files[i], sessions[i], options=lock_files.AcquireOptions(skip_naming_check=True)
                )[0],
                range(26),
            )
        )
    assert all(rc == 0 for rc in results), f"有 acquire 失败: {results}"

    # registry.json 必须是完好 JSON 且 26 锁全在（无丢锁）
    locks = _registry(isolated_lock_root)["locks"]
    assert len(locks) == 26, f"丢锁: 期望 26 实际 {len(locks)}"
    for f in files:
        assert f in locks

    with ThreadPoolExecutor(max_workers=26) as pool:
        results = list(
            pool.map(
                lambda i: _run(lock_files.cmd_release, files[i], sessions[i])[0],
                range(26),
            )
        )
    assert all(rc == 0 for rc in results)
    assert _registry(isolated_lock_root)["locks"] == {}


# ── 9. Mutex 超时 → DENIED + 回滚锁目录（无半锁状态）──
def test_mutex_timeout_denies_and_rolls_back(isolated_lock_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    @contextlib.contextmanager
    def _fake_mutex():
        yield False  # 模拟 5s 超时未获得

    monkeypatch.setattr(lock_files, "_registry_mutex", _fake_mutex)
    rc, out = _run(lock_files.cmd_acquire, "docs/g.md", "sess-1", options=lock_files.AcquireOptions(skip_naming_check=True))
    assert rc == 1 and "互斥锁超时" in out
    # 锁目录已回滚，不留 owner.json 存在但 registry 漏登记的半锁
    assert not lock_files._lock_dir("docs/g.md").exists()


# ---------------------------------------------------------------------------
# TestCliFileArgGuard — #120 防呆回归
# ---------------------------------------------------------------------------


class TestCliFileArgGuard:
    """#120 防呆：文件参数以 -- 开头拒绝落锁。

    实证：AI-POT-001 误把 list --session 写法带到 acquire，字面量 --session
    被当文件落锁（全仓唯一垃圾锁）。仓库内合法路径不会以 -- 开头。
    """

    def test_acquire_rejects_dash_dash_file(self, isolated_lock_root, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["lock_files.py", "acquire", "--session", "AI-PROBE-001"])
        rc = lock_files.main()
        assert rc == 1
        out = capsys.readouterr().out
        assert "文件参数非法" in out
        assert not (isolated_lock_root / "--session.lock").exists()

    def test_guard_write_rejects_dash_dash_file(self, isolated_lock_root, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["lock_files.py", "guard-write", "--task", "AI-PROBE-001"])
        assert lock_files.main() == 1

    def test_release_rejects_dash_dash_file(self, isolated_lock_root, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["lock_files.py", "release", "--session", "AI-PROBE-001"])
        assert lock_files.main() == 1

    def test_check_rejects_dash_dash_file(self, isolated_lock_root, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["lock_files.py", "check", "--session"])
        assert lock_files.main() == 1

    def test_acquire_legit_file_still_works(self, isolated_lock_root, monkeypatch):
        monkeypatch.setattr(
            sys,
            "argv",
            ["lock_files.py", "acquire", "src/probe_govb120.py", "AI-PROBE-001", "--skip-naming-check"],
        )
        rc = lock_files.main()
        assert rc == 0
        monkeypatch.setattr(sys, "argv", ["lock_files.py", "release", "src/probe_govb120.py", "AI-PROBE-001"])
        assert lock_files.main() == 0


# ---------------------------------------------------------------------------
# TestTrackedFileNamingSkip — B5③(2026-09-14) 回归：存量已跟踪文件跳过命名门禁
# ---------------------------------------------------------------------------


class TestTrackedFileNamingSkip:
    """B5③：lock_files acquire 对存量已跟踪文件误拒（N-11/N-13 假阳性）。

    病灶：acquire 对任何文件重跑全量命名门禁，存量已跟踪文件的文件名在
    创建/提交时已被提交侧裁决（提交侧对修改文件有历史豁免），锁侧更严只会误拒
    ——实证：gate_tracked_write_allowlist.yaml（N-11）与
    data_download_config.yaml（N-13）被 acquire 拒绝。
    修法：_is_git_tracked(git ls-files --error-unmatch) 判定存量，跟踪文件
    跳过命名检查；未跟踪新文件仍全量检查（早期反馈，无冤案）；
    git 不可用 fail-closed（返回 False → 仍检查）。
    """

    def test_tracked_file_skips_naming_gate(self, isolated_lock_root, monkeypatch):
        """存量已跟踪文件：命名违规也不拒（提交侧已裁决，锁侧不重复执法）。"""
        monkeypatch.setattr(lock_files, "_is_git_tracked", lambda p: True)
        rc, out = _run(lock_files.cmd_acquire, "docs/bad-name-BadName.yaml", "sess-b53")
        assert rc == 0, out
        assert "ACQUIRED" in out

    def test_untracked_file_still_checked(self, isolated_lock_root, monkeypatch):
        """未跟踪新文件：命名门禁仍生效（早期反馈）。"""
        monkeypatch.setattr(lock_files, "_is_git_tracked", lambda p: False)
        rc, out = _run(lock_files.cmd_acquire, "docs/bad-name-BadName.yaml", "sess-b53")
        assert rc == 1
        assert "NAMING VIOLATION" in out

    def test_untracked_clean_file_passes(self, isolated_lock_root, monkeypatch):
        """未跟踪新文件：命名合规正常放行。"""
        monkeypatch.setattr(lock_files, "_is_git_tracked", lambda p: False)
        rc, out = _run(lock_files.cmd_acquire, "docs/good_name.yaml", "sess-b53")
        assert rc == 0, out
        assert "ACQUIRED" in out

    def test_git_unavailable_fail_closed(self, isolated_lock_root, monkeypatch):
        """git 不可用：fail-closed 仍走命名检查（不因环境故障放行新文件）。"""
        import subprocess as _sp

        def _boom(*a, **k):
            raise _sp.SubprocessError("git gone")

        monkeypatch.setattr(_sp, "run", _boom)
        assert lock_files._is_git_tracked("docs/anything.yaml") is False

    def test_reject_before_fix_now_passes(self, isolated_lock_root, monkeypatch):
        """事故原件复验：真实 repo 环境下 gate_tracked_write_allowlist.yaml 可 acquire。

        该文件是 git 跟踪的存量文件且文件名含 kebab 片段，修复前被 N-11 误拒
        （doc_type=register 期望 _registry 后缀）。不 mock _is_git_tracked，
        走真实 git ls-files 判定。
        """
        rc, out = _run(
            lock_files.cmd_acquire,
            "docs/01_policies_and_standards/_registry/catalogs/gate_tracked_write_allowlist.yaml",
            "sess-b53",
        )
        assert rc == 0, out
        assert "ACQUIRED" in out


# ---------------------------------------------------------------------------
# 批量锁接口（P2-1 出仓战役 2026-09-16：千件级 claim 吞吐前置）
# ---------------------------------------------------------------------------
class TestBatchLockInterface:
    """acquire-batch / release-batch：语义等价逐件 + registry 整表只写一次。"""

    def test_acquire_batch_registers_all(self, isolated_lock_root: Path) -> None:
        opts = lock_files.AcquireOptions(skip_naming_check=True, session_id="sess-1")
        rc, out = _run(lock_files.cmd_acquire_batch, "sess-1", ["docs/a.md", "docs/b.md", "docs/c.md"], opts)
        assert rc == 0, out
        assert "acquired=3 denied=0 total=3" in out
        locks = _registry(isolated_lock_root)["locks"]
        assert set(locks) == {"docs/a.md", "docs/b.md", "docs/c.md"}
        assert all(v["owner_id"] == "sess-1" for v in locks.values())
        # owner.json 逐件落地（会话绑定与单件 acquire 同构）
        assert _owner(isolated_lock_root, "docs/a.md")["session_id"] == "sess-1"

    def test_acquire_batch_partial_denial_keeps_rest(self, isolated_lock_root: Path) -> None:
        foreign = lock_files.AcquireOptions(skip_naming_check=True)
        _run(lock_files.cmd_acquire, "docs/taken.md", "sess-2", foreign)
        rc, out = _run(
            lock_files.cmd_acquire_batch,
            "sess-1",
            ["docs/taken.md", "docs/free.md"],
            foreign,
        )
        assert rc == 1  # 有 DENIED → 整体非零，但其余件已获得
        assert "DENIED — docs/taken.md" in out
        locks = _registry(isolated_lock_root)["locks"]
        assert locks["docs/free.md"]["owner_id"] == "sess-1"
        assert locks["docs/taken.md"]["owner_id"] == "sess-2"

    def test_acquire_batch_idempotent_reentry(self, isolated_lock_root: Path) -> None:
        opts = lock_files.AcquireOptions(skip_naming_check=True)
        _run(lock_files.cmd_acquire_batch, "sess-1", ["docs/a.md", "docs/b.md"], opts)
        rc, out = _run(lock_files.cmd_acquire_batch, "sess-1", ["docs/a.md", "docs/b.md"], opts)
        assert rc == 0, out
        assert "acquired=2" in out
        assert len(_registry(isolated_lock_root)["locks"]) == 2

    def test_acquire_batch_writes_registry_once(self, isolated_lock_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """O(N²) 治本断言：整表写回次数与件数无关（逐件版=每件一次）。"""
        calls = {"n": 0}
        orig_save = lock_files._save_registry

        def _counting(reg):
            calls["n"] += 1
            return orig_save(reg)

        monkeypatch.setattr(lock_files, "_save_registry", _counting)
        opts = lock_files.AcquireOptions(skip_naming_check=True)
        rc, _ = _run(lock_files.cmd_acquire_batch, "sess-1", [f"docs/f{i}.md" for i in range(60)], opts)
        assert rc == 0
        assert calls["n"] == 1, f"批量 claim 整表写了 {calls['n']} 次"

    def test_acquire_batch_mutex_timeout_rolls_back_all(self, isolated_lock_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        @contextlib.contextmanager
        def _fake_mutex():
            yield False

        monkeypatch.setattr(lock_files, "_registry_mutex", _fake_mutex)
        opts = lock_files.AcquireOptions(skip_naming_check=True)
        rc, out = _run(lock_files.cmd_acquire_batch, "sess-1", ["docs/x.md", "docs/y.md"], opts)
        assert rc == 1 and "已回滚" in out
        assert not lock_files._lock_dir("docs/x.md").exists()
        assert not lock_files._lock_dir("docs/y.md").exists()

    def test_release_batch_only_own(self, isolated_lock_root: Path) -> None:
        opts = lock_files.AcquireOptions(skip_naming_check=True)
        _run(lock_files.cmd_acquire_batch, "sess-1", ["docs/a.md", "docs/b.md"], opts)
        _run(lock_files.cmd_acquire, "docs/c.md", "sess-2", opts)

        rc, out = _run(lock_files.cmd_release_batch, "sess-1", ["docs/a.md", "docs/b.md", "docs/c.md"], warn=False)
        assert rc == 1  # docs/c.md 是他人锁 → DENIED
        assert "released=2 denied=1" in out
        locks = _registry(isolated_lock_root)["locks"]
        assert "docs/a.md" not in locks and "docs/b.md" not in locks
        assert "docs/c.md" in locks

    def test_tracked_paths_batch_matches_per_file(self) -> None:
        """批量 git 判定与逐件 _is_git_tracked 真值一致（真实仓环境）。"""
        tracked_file = "scripts/lock_files.py"
        untracked_file = "docs/_working/zz_definitely_untracked_batch_probe.md"
        got = lock_files._tracked_paths_batch([tracked_file, untracked_file])
        assert (tracked_file in got) is lock_files._is_git_tracked(tracked_file) is True
        assert (untracked_file in got) is lock_files._is_git_tracked(untracked_file) is False

    def test_collect_path_args_mixes_sources(self, tmp_path: Path) -> None:
        listing = tmp_path / "files.txt"
        listing.write_text("docs/one.md\n# 注释行\n\ndocs/two.md\n", encoding="utf-8")
        args = [
            "--files-from",
            str(listing),
            "--files",
            "docs/three.md,docs/four.md",
            "--task",
            "批量加锁",
            "--session",
            "sess-1",
            "--skip-naming-check",
            "docs/five.md",
        ]
        got = lock_files._collect_path_args(args)
        assert got == [
            "docs/one.md",
            "docs/two.md",
            "docs/three.md",
            "docs/four.md",
            "docs/five.md",
        ]

    def test_collect_path_args_rejects_bad_list(self) -> None:
        assert lock_files._collect_path_args(["--files-from", "Z:/no/such/list.txt"]) is None
        assert lock_files._collect_path_args(["--files"]) is None
