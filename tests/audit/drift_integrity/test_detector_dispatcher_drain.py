# [A_test] module_id: MOD-GOV_detector_dispatcher | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_detector_dispatcher_drain
# [INVARIANTS] detector 子进程 TIMEOUT 路径必须 kill+有界排空（批5 drift_engine 同口径），不残留孤儿进程
# [CONSUMERS] pytest
# [TESTS] tests/test_detector_dispatcher_drain.py
# [TTL] task_bound

from __future__ import annotations

import asyncio
import time

import psutil
import pytest

import zephyr.gov_drift.detector_dispatcher as dd_module
from zephyr.gov_drift.detector_dispatcher import DetectorDispatcher
from zephyr.gov_drift.drift_models import Detector, Severity


def _make_dispatcher_with_sleep_script(tmp_path):
    """构造 dispatcher + 一个写自身 PID 后长睡的 detector 脚本。"""
    dd = DetectorDispatcher(registry_path=str(tmp_path / "registry.yaml"))
    dd._scripts_root = str(tmp_path)

    pid_file = tmp_path / "child.pid"
    script_path = tmp_path / "sleepy_detector.py"
    script_path.write_text(
        "import os, time\n"
        f"open(r'{pid_file}', 'w').write(str(os.getpid()))\n"
        "time.sleep(120)\n",
        encoding="utf-8",
    )

    det = Detector(
        id="det-drain",
        drift_dimension="test",
        severity=Severity.MEDIUM,
        category="test",
        script="sleepy_detector.py",
    )
    return dd, det, pid_file


def _wait_pid_gone(pid: int, timeout_s: float = 5.0) -> bool:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if not psutil.pid_exists(pid):
            return True
        time.sleep(0.05)
    return not psutil.pid_exists(pid)


def _wait_pid_file(pid_file, timeout_s: float = 5.0) -> int:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if pid_file.exists():
            return int(pid_file.read_text(encoding="utf-8"))
        time.sleep(0.05)
    raise AssertionError(f"子进程未在 {timeout_s}s 内写入 PID 文件 {pid_file}")


@pytest.mark.asyncio
async def test_timeout_kills_child_and_drains(tmp_path, monkeypatch):
    """TIMEOUT 路径：kill 后 5s 排空生效，子进程被回收，不残留孤儿。"""
    dd, det, pid_file = _make_dispatcher_with_sleep_script(tmp_path)

    real_wait_for = asyncio.wait_for

    def fake_wait_for(fut, timeout=None):
        if timeout == 30:
            # 等子进程真实启动并写下 PID，再触发超时（防 kill 抢在首行前）
            _wait_pid_file(pid_file)
            if hasattr(fut, "close"):
                fut.close()
            raise TimeoutError
        return real_wait_for(fut, timeout=timeout)

    monkeypatch.setattr(dd_module.asyncio, "wait_for", fake_wait_for)

    result = await dd._run_detector(det, [], asyncio.Semaphore(1))

    assert result.success is False
    assert "TIMEOUT" in result.error

    child_pid = _wait_pid_file(pid_file)
    assert _wait_pid_gone(child_pid), f"detector 子进程 {child_pid} 在 kill+排空后仍存活"


@pytest.mark.asyncio
async def test_drain_timeout_closes_transport_fallback(tmp_path, monkeypatch):
    """排空 5s 也超时（孙进程持管道句柄场景）：transport.close() 兜底被触发。"""
    dd, det, pid_file = _make_dispatcher_with_sleep_script(tmp_path)

    real_wait_for = asyncio.wait_for
    captured = []

    real_exec = dd_module.asyncio.create_subprocess_exec

    async def spy_exec(*args, **kwargs):
        proc = await real_exec(*args, **kwargs)
        captured.append(proc)
        return proc

    def fake_wait_for(fut, timeout=None):
        if timeout in (30, 5):
            if timeout == 30:
                # 等子进程真实启动再触发超时
                _wait_pid_file(pid_file)
            if hasattr(fut, "close"):
                fut.close()
            raise TimeoutError
        return real_wait_for(fut, timeout=timeout)

    monkeypatch.setattr(dd_module.asyncio, "create_subprocess_exec", spy_exec)
    monkeypatch.setattr(dd_module.asyncio, "wait_for", fake_wait_for)

    result = await dd._run_detector(det, [], asyncio.Semaphore(1))

    assert result.success is False
    assert "TIMEOUT" in result.error
    assert captured, "子进程未被创建"

    proc = captured[0]
    transport = getattr(proc, "_transport", None)
    assert transport is not None, "asyncio subprocess transport 缺失"
    assert transport.is_closing() or getattr(transport, "_closed", False), (
        "排空超时后 transport.close() 兜底未生效"
    )

    child_pid = _wait_pid_file(pid_file)
    assert _wait_pid_gone(child_pid), f"detector 子进程 {child_pid} 在兜底路径后仍存活"
