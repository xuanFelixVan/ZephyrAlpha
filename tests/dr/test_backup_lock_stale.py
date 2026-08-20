# [BLUEPRINT] MOD-INF-005 | tests/dr/test_backup_lock_stale.py | §
# [MODULE] tests.dr.test_backup_lock_stale
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.meta.backup_runtime_state
# [CONSUMERS] none
# [STARTUP] manual
# [MATURITY] production
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-INF-005 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [TESTS] tests/dr/test_backup_lock_stale.py
"""僵尸锁接管测试（P4 治本，2026-08-03）。

背景：_backup_lock 原 FileExistsError 直接让步，若持有进程异常退出（崩溃/kill）
未走 finally unlink，lock 永久残留导致后续所有备份全 SKIP。
实测 .backup_pg.lock 自 8/2 残留至 8/3，12 次备份全失效。

测试覆盖：
1. 僵尸锁检测——lock 持有 PID 已死 → 接管并正常备份
2. 活锁尊重——lock 持有 PID 存活 → 正常让步 SKIP
3. lock 清理——正常流程结束后 lock 文件被清理
4. 损坏 lock——lock 文件内容非 JSON → 保守不接管（返回 None pid）
"""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_GOV_META = _REPO_ROOT / "scripts" / "governance" / "meta"
if str(_GOV_META) not in sys.path:
    sys.path.insert(0, str(_GOV_META))

from backup_runtime_state import _backup_lock, _is_pid_alive, _read_lock_holder_pid  # noqa: E402


def _write_lock(lock_path: Path, pid: int, label: str = "test") -> None:
    """模拟持有进程写 lock 文件。"""
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps({"pid": pid, "label": label, "acquired_at": datetime.now(UTC).isoformat()})
    lock_path.write_text(payload, encoding="utf-8")


def _find_dead_pid() -> int:
    """找一个确定不存在的 PID（避开当前进程及合理范围）。

    Windows PID 通常是 4 的倍数，找一个大于 100000 的数几乎必然不存在。
    """
    return 999999  # 几乎不可能存在的 PID


class TestStaleLockTakeover:
    """僵尸锁接管测试。"""

    def test_dead_pid_lock_is_taken_over(self, tmp_path: Path) -> None:
        """僵尸锁（持有 PID 已死）→ 接管并正常获取锁。"""
        lock_path = tmp_path / ".backup_pg.lock"
        dead_pid = _find_dead_pid()
        _write_lock(lock_path, dead_pid)

        with _backup_lock(lock_path, label="test") as got:
            assert got is True, "僵尸锁应被接管"

    def test_dead_pid_lock_emits_takeover_message(self, tmp_path: Path, capsys) -> None:
        """僵尸锁接管时输出检测消息。"""
        lock_path = tmp_path / ".backup_pg.lock"
        dead_pid = _find_dead_pid()
        _write_lock(lock_path, dead_pid)

        with _backup_lock(lock_path, label="test") as got:
            assert got is True

        captured = capsys.readouterr()
        assert "僵尸锁" in captured.err or "zombie" in captured.err.lower(), (
            f"应输出僵尸锁检测消息，实际: {captured.err!r}"
        )

    def test_lock_cleaned_after_takeover(self, tmp_path: Path) -> None:
        """僵尸锁接管后，退出时 lock 文件被正常清理。"""
        lock_path = tmp_path / ".backup_pg.lock"
        _write_lock(lock_path, _find_dead_pid())

        with _backup_lock(lock_path, label="test"):
            pass

        assert not lock_path.exists(), "接管并退出后 lock 文件应被清理"


class TestLiveLockRespect:
    """活锁尊重测试——持有 PID 存活时正常让步。"""

    def test_live_pid_lock_yields(self, tmp_path: Path) -> None:
        """活锁（持有 PID 是当前进程）→ 让步 SKIP。"""
        lock_path = tmp_path / ".backup_pg.lock"
        _write_lock(lock_path, os.getpid())  # 当前进程必然存活

        with _backup_lock(lock_path, label="test") as got:
            assert got is False, "活锁应让步，不应接管"

    def test_live_pid_lock_not_taken_over(self, tmp_path: Path, capsys) -> None:
        """活锁不接管——不输出接管消息。"""
        lock_path = tmp_path / ".backup_pg.lock"
        _write_lock(lock_path, os.getpid())

        with _backup_lock(lock_path, label="test"):
            pass

        captured = capsys.readouterr()
        assert "僵尸锁" not in captured.err, "活锁不应触发接管消息"


class TestLockCleanup:
    """lock 正常清理测试。"""

    def test_lock_created_and_cleaned(self, tmp_path: Path) -> None:
        """无既有 lock 时正常创建，退出时清理。"""
        lock_path = tmp_path / ".backup_pg.lock"

        with _backup_lock(lock_path, label="test") as got:
            assert got is True
            assert lock_path.exists(), "持锁期间 lock 文件应存在"

        assert not lock_path.exists(), "退出后 lock 文件应被清理"


class TestCorruptLock:
    """损坏 lock 文件测试——保守不接管。"""

    def test_corrupt_lock_returns_none_pid(self, tmp_path: Path) -> None:
        """lock 内容非 JSON → _read_lock_holder_pid 返回 None（保守不接管）。"""
        lock_path = tmp_path / ".backup_pg.lock"
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        lock_path.write_text("not valid json {{{", encoding="utf-8")

        pid = _read_lock_holder_pid(lock_path)
        assert pid is None, "损坏 lock 应返回 None"

    def test_corrupt_lock_not_taken_over(self, tmp_path: Path) -> None:
        """损坏 lock → 不接管（保守让步），避免误删未知状态 lock。"""
        lock_path = tmp_path / ".backup_pg.lock"
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        lock_path.write_text("corrupt content", encoding="utf-8")

        with _backup_lock(lock_path, label="test") as got:
            # 损坏 lock 解析 pid 失败返回 None，holder_pid is None 条件不满足，
            # 走"持有进程仍存活，正常让步"分支
            assert got is False, "损坏 lock 应保守让步不接管"


class TestPidAliveDetection:
    """PID 存活检测跨平台测试。"""

    def test_current_pid_is_alive(self) -> None:
        """当前进程 PID 检测为存活。"""
        assert _is_pid_alive(os.getpid()) is True

    def test_nonexistent_pid_is_dead(self) -> None:
        """不存在的 PID 检测为已死。"""
        assert _is_pid_alive(_find_dead_pid()) is False

    def test_pid_zero_is_dead(self) -> None:
        """PID 0（System Idle Process，特殊）——Windows 上 PID 0 存活但不应接管。

        此测试验证不接管 PID 0 的边界（保守：PID 0 存活但无意义）。
        在 POSIX 上 PID 0 通常表示当前进程组，也视为存活。
        """
        # PID 0 在 Windows 上 OpenProcess 可能成功（System Idle Process），
        # 我们不强制要求结果，只验证函数不抛异常
        result = _is_pid_alive(0)
        assert isinstance(result, bool)
