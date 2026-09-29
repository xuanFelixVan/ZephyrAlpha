# [BLUEPRINT] MOD-INF-005 | tests/git/test_lock_wait_ledger.py | st-finaldel-crx2-20260929 Rx-2
# [MODULE] tests.git.test_lock_wait_ledger
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; zephyr.gov_enforcement.rule_bridge.git_commit_gateway
# [STARTUP] python -m pytest tests/git/test_lock_wait_ledger.py
# [MATURITY] testing
# [INVARIANTS] 锁等待记账字段断言（waited_ms/holder/timeout/_timed_out）；账本断言一律 tmp_path（测试隔离红线，禁写生产 .runtime）；不mock锁文件语义本身
# [ERROR_CONTRACT] 全部用例不触碰真实主仓锁（.ailocks 一律落在 tmp_path 下）
# [TTL] task_bound
"""test_lock_wait_ledger.py — Rx-2 锁等待插桩验收（st-finaldel-crx-20260929）。

红蓝例：
- 蓝例：锁被活进程持有，__enter__ 等待释放后成功 → waited_ms≥延迟且 holder 记录「等了谁」；
- 蓝例：无竞争立即获取 → waited_ms≈0 且 holder=""；
- 红例：锁永不释放 → GatewayError 且 waited_ms≈timeout、_timed_out=True、holder 在账；
- 账本：_append_lock_wait_event 落行字段齐（timestamp/event/session_id/waited_ms/holder/
  timeout）、env ZEPHYR_LOCK_WAIT_LEDGER=0 一键回退、写失败容错不上抛。
"""

from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path

import pytest

from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (
    _LOCK_WAIT_LEDGER_ENV,
    GatewayError,
    _append_lock_wait_event,
    _GlobalCommitLock,
    _lock_wait_ledger_enabled,
)


def _hold_lock(project_root: Path, holder_pid: int) -> Path:
    """在 tmp_path 下伪造一把持有中的全局锁（pid 可控）。"""
    lock_file = project_root / ".ailocks" / "git_commit_global.lock"
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    lock_file.write_text(json.dumps({"pid": holder_pid, "acquired_at": time.time()}), encoding="utf-8")
    return lock_file


class TestLockWaitedMs:
    """_GlobalCommitLock 等待耗时/持有者字段语义（Rx-2 施工点1）。"""

    def test_success_after_delay_records_waited_ms_and_holder(self, tmp_path: Path) -> None:
        lock_file = _hold_lock(tmp_path, os.getpid())  # 活进程=pytest 自身（必活，不触发僵尸回收）
        release = threading.Event()

        def _release_later() -> None:
            release.wait(1.5)
            lock_file.unlink(missing_ok=True)

        t = threading.Thread(target=_release_later, daemon=True)
        t.start()
        try:
            with _GlobalCommitLock(tmp_path, timeout=10.0) as lock:
                assert lock.waited_ms is not None
                assert lock.waited_ms >= 300.0  # 延迟 1.5s 释放（下界放宽到 300ms 防调度抖动假红）
                assert lock.holder == f"pid={os.getpid()}"  # 「等了谁」在账
        finally:
            release.set()
            t.join(timeout=3)

    def test_immediate_acquire_waited_ms_near_zero_and_holder_empty(self, tmp_path: Path) -> None:
        with _GlobalCommitLock(tmp_path, timeout=5.0) as lock:
            assert lock.waited_ms is not None
            assert lock.waited_ms < 1000.0  # 无竞争立即获取
            assert lock.holder == ""  # 未经历等待

    def test_timeout_carries_waited_ms_holder_and_flag(self, tmp_path: Path) -> None:
        _hold_lock(tmp_path, os.getpid())  # 活进程持有且永不释放
        lock = _GlobalCommitLock(tmp_path, timeout=0.3)
        with pytest.raises(GatewayError):
            lock.__enter__()
        assert lock._timed_out is True
        assert lock.waited_ms is not None
        assert lock.waited_ms >= 250.0  # ≈timeout 值随异常带出
        assert lock.holder == f"pid={os.getpid()}"

    def test_zombie_lock_reaped_still_records_holder(self, tmp_path: Path) -> None:
        _hold_lock(tmp_path, -1)  # 死 PID（pid<=0 不存活）→ 僵尸回收后立即可拿
        with _GlobalCommitLock(tmp_path, timeout=5.0) as lock:
            assert lock.waited_ms is not None
            assert lock.holder == "pid=-1"  # 被清掉的僵尸持有者仍可观测


class TestLockWaitLedgerWriter:
    """_append_lock_wait_event 账本写入器（Rx-2 施工点2：新 jsonl+容错+env 回退）。"""

    @pytest.fixture(autouse=True)
    def _env_default_on(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(_LOCK_WAIT_LEDGER_ENV, raising=False)  # 缺省 ON 口径隔离

    def test_row_fields_complete(self, tmp_path: Path) -> None:
        _append_lock_wait_event(
            tmp_path,
            {"event": "lock_wait", "session_id": "s1", "waited_ms": 123, "holder": "pid=9", "timeout": 60.0},
        )
        ledger = tmp_path / ".runtime" / "audit" / "lock_wait_events.jsonl"
        rows = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines() if line.strip()]
        assert len(rows) == 1
        row = rows[0]
        # Owner 口径六字段齐全
        assert {"timestamp", "event", "session_id", "waited_ms", "holder", "timeout"} <= set(row)
        assert row["event"] == "lock_wait"
        assert row["session_id"] == "s1"
        assert row["waited_ms"] == 123
        assert row["holder"] == "pid=9"
        assert row["timeout"] == 60.0
        assert row["timestamp"]  # isoformat 非空

    def test_env_off_disables_ledger(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv(_LOCK_WAIT_LEDGER_ENV, "0")
        assert _lock_wait_ledger_enabled() is False
        _append_lock_wait_event(
            tmp_path,
            {"event": "lock_timeout", "session_id": "s", "waited_ms": 1, "holder": "pid=1", "timeout": 1},
        )
        assert not (tmp_path / ".runtime" / "audit" / "lock_wait_events.jsonl").exists()

    def test_writer_fault_tolerant_no_raise(self, tmp_path: Path) -> None:
        blocker = tmp_path / "not_a_dir"
        blocker.write_text("x", encoding="utf-8")
        # project_root 指向文件子路径（mkdir 必败）→ 审计写失败必须静默不上抛
        _append_lock_wait_event(
            blocker / "sub",
            {"event": "lock_wait", "session_id": "s", "waited_ms": 0, "holder": "", "timeout": 1},
        )  # 不抛即过

    def test_default_enabled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(_LOCK_WAIT_LEDGER_ENV, raising=False)
        assert _lock_wait_ledger_enabled() is True
