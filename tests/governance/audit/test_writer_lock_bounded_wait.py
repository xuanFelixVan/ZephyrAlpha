# [A_test] module_id: SRC-TST-GWA-LOCKWAIT | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §4.4
# [MODULE] tests.test_writer_lock_bounded_wait
# [DOMAIN] D_GOV_AUDIT
# [INVARIANTS] 锁等待必须有界：竞争下超预算快速让路（TimeoutError），不得无界阻塞
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [A_module] module_id=MOD-INF-020 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""跨进程 append 锁有界等待回归（2026-09-29 lane-l 治本）。

四战实证（governance 跑批连续 4 次楔死于 writer.py 锁等待，pytest-timeout
420s 打栈）：多队并发提交窗口中提交链批量审计写反复过锁，等待方在
msvcrt LK_LOCK（每次最长 ~10s 一次性 OS 等待窗口）上累计阻塞 10s×N；
POSIX flock 更是无界阻塞直至持锁方释放。

治本=LK_NBLCK/LOCK_NB 非阻塞尝试 + 50ms 短轮询 + 总预算（默认 30s，
env GOV_AUDIT_LOCK_WAIT_S 覆盖）+ 预算耗尽让路 TimeoutError（消息含
lock_path 与实际等待时长）。fail-closed 语义不变：丢一条事件好过写断链。

红基准（治本前）：持锁方持锁 6s 时——Windows 等待方 ~10s 才 TimeoutError
（超本测试 5s 上限=红）；POSIX 等待方阻塞 ~6s 后成功进入（无 TimeoutError=红）。

子进程用 sys.executable -c 内联 worker（与 test_writer_multiproc_append.py
同配方，规避 multiprocessing spawn 再导入平台差异），全部落 tmp_path 沙箱。
"""

from __future__ import annotations

import subprocess
import sys
import time as _time
from pathlib import Path

import pytest

from zephyr.gov_audit.writer import (
    AuditWriter,
    _cross_process_append_lock,
    _lock_wait_budget_s,
)

_REPO_SRC = str(Path(__file__).resolve().parents[3] / "src")

# 内联子进程 holder：获取锁 → 写 marker（主进程据此开始计时）→ 持锁 sleep
_HOLDER_CHILD = (
    "import pathlib, sys, time\n"
    "sys.path.insert(0, sys.argv[3])\n"
    "from zephyr.gov_audit.writer import _cross_process_append_lock\n"
    "with _cross_process_append_lock(pathlib.Path(sys.argv[1])):\n"
    "    pathlib.Path(sys.argv[2]).write_text('held')\n"
    "    time.sleep(float(sys.argv[4]))\n"
)


def _spawn_lock_holder(events_jsonl: Path, marker: Path, hold_seconds: float) -> subprocess.Popen:
    return subprocess.Popen(
        [sys.executable, "-c", _HOLDER_CHILD, str(events_jsonl), str(marker), _REPO_SRC, str(hold_seconds)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )


def _wait_holder_acquired(marker: Path, proc: subprocess.Popen, timeout: float = 20.0) -> None:
    deadline = _time.monotonic() + timeout
    while not marker.exists():
        assert proc.poll() is None, "holder died before acquiring lock: " + (
            proc.stderr.read().decode("utf-8", errors="replace")[-300:] if proc.stderr else ""
        )
        assert _time.monotonic() < deadline, "holder never acquired lock"
        _time.sleep(0.02)


def _stop_holder(proc: subprocess.Popen) -> None:
    """杀掉并收尸 holder，且显式关闭 stderr 管道——防 GC 晚期 unraisable
    ResourceWarning（repo pytest 配置 warning→error，会误伤后续测试）。"""
    proc.kill()
    proc.wait(timeout=10)
    if proc.stderr:
        try:
            proc.stderr.close()
        except OSError:
            pass


class TestBoundedWaitUnderContention:
    def test_contended_lock_times_out_within_budget(self, tmp_path, monkeypatch):
        """持锁方持锁 6s + 预算 1s → 等待方 ~1s 内 TimeoutError 让路（非 10s 级/无界阻塞）。

        治本前红：Windows LK_LOCK ~10s 才 OSError（elapsed 超 5s 上限）；
        POSIX flock 阻塞到持锁方释放（~6s 成功进入，无 TimeoutError）。
        """
        monkeypatch.setenv("GOV_AUDIT_LOCK_WAIT_S", "1")
        events = tmp_path / "events.jsonl"
        marker = tmp_path / "held.marker"
        holder = _spawn_lock_holder(events, marker, hold_seconds=6.0)
        try:
            _wait_holder_acquired(marker, holder)
            t0 = _time.monotonic()
            with pytest.raises(TimeoutError) as exc_info:
                with _cross_process_append_lock(events):
                    pass
            elapsed = _time.monotonic() - t0
        finally:
            _stop_holder(holder)
        # 有界：远小于旧 LK_LOCK 的 ~10s OS 窗口
        assert elapsed < 5.0, f"lock wait took {elapsed:.1f}s (unbounded/10s-level blocking)"
        # 让路消息可诊断：含 lock_path 与实际等待时长
        msg = str(exc_info.value)
        assert str(events) in msg, f"timeout message lacks lock_path: {msg}"
        assert "waited" in msg, f"timeout message lacks waited duration: {msg}"

    def test_lock_acquired_after_release_within_budget(self, tmp_path):
        """预算内持锁方释放 → 等待方轮询拿到锁并进入（互斥+最终获取语义保持）。"""
        events = tmp_path / "events.jsonl"
        marker = tmp_path / "held.marker"
        holder = _spawn_lock_holder(events, marker, hold_seconds=1.5)
        try:
            _wait_holder_acquired(marker, holder)
            t0 = _time.monotonic()
            with _cross_process_append_lock(events):
                acquired_at = _time.monotonic() - t0
        finally:
            _stop_holder(holder)
        # 持锁 1.5s 期间不得提前进入（互斥），释放后 promptly 进入（预算默认 30s 足够）
        assert acquired_at >= 1.2, f"entered while still held? acquired after {acquired_at:.2f}s"
        assert acquired_at < 15.0, f"acquisition took {acquired_at:.1f}s after release"

    def test_budget_env_override_semantics(self, monkeypatch):
        """预算解析：默认 30s；合法 env 覆盖生效；0=仅试一次；非法值回落默认。"""
        monkeypatch.delenv("GOV_AUDIT_LOCK_WAIT_S", raising=False)
        assert _lock_wait_budget_s() == 30.0
        monkeypatch.setenv("GOV_AUDIT_LOCK_WAIT_S", "5")
        assert _lock_wait_budget_s() == 5.0
        monkeypatch.setenv("GOV_AUDIT_LOCK_WAIT_S", "0")
        assert _lock_wait_budget_s() == 0.0
        monkeypatch.setenv("GOV_AUDIT_LOCK_WAIT_S", "not-a-number")
        assert _lock_wait_budget_s() == 30.0
        monkeypatch.setenv("GOV_AUDIT_LOCK_WAIT_S", "-3")
        assert _lock_wait_budget_s() == 30.0

    def test_zero_budget_fails_immediately_under_contention(self, tmp_path, monkeypatch):
        """GOV_AUDIT_LOCK_WAIT_S=0 → 单次尝试，竞争下立即让路（<1s）。"""
        monkeypatch.setenv("GOV_AUDIT_LOCK_WAIT_S", "0")
        events = tmp_path / "events.jsonl"
        marker = tmp_path / "held.marker"
        holder = _spawn_lock_holder(events, marker, hold_seconds=5.0)
        try:
            _wait_holder_acquired(marker, holder)
            t0 = _time.monotonic()
            with pytest.raises(TimeoutError):
                with _cross_process_append_lock(events):
                    pass
            elapsed = _time.monotonic() - t0
        finally:
            _stop_holder(holder)
        assert elapsed < 1.0, f"zero budget should fail fast, took {elapsed:.1f}s"


class TestWriterLevelBoundedWait:
    def test_audit_writer_write_yields_timeout_under_contention(self, tmp_path, monkeypatch):
        """writer 级接线：竞争超预算 → AuditWriter.write 抛 TimeoutError 且计入失败计数。

        I8 fail-closed 保持：异常必须穿透 write()（驱动 _write_failures→readonly
        保护），消费方（session_audit/AuditChainVerifier）本就吞 OSError/RuntimeError。
        """
        monkeypatch.setenv("GOV_AUDIT_LOCK_WAIT_S", "1")
        data_dir = tmp_path / "audit_trail"
        data_dir.mkdir(parents=True)  # holder 先于 AuditWriter 构造，目录必须预建（writer 不做兜底 mkdir，I8 语义）
        events = data_dir / "events.jsonl"
        marker = tmp_path / "held.marker"
        holder = _spawn_lock_holder(events, marker, hold_seconds=6.0)
        try:
            _wait_holder_acquired(marker, holder)
            w = AuditWriter(data_dir=data_dir, enable_merkle=False, hmac_key="test-key")
            t0 = _time.monotonic()
            with pytest.raises(TimeoutError):
                w.write({"event_type": "generic", "agent_id": "contended"})
            elapsed = _time.monotonic() - t0
        finally:
            _stop_holder(holder)
        assert elapsed < 5.0, f"write() blocked {elapsed:.1f}s under contention"
        assert w.write_failures == 1, "lock timeout must be counted as a write failure (I8)"
        assert not w.readonly, "single failure must not trip readonly"
