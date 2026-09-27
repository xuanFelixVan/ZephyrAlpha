# [MODULE] tests.frontend.test_api_server_heartbeat
# [DOMAIN] D_FRONTEND
# [TTL] permanent
"""QMine 06 业务扶正②验收：api_server 仪表盘心跳（tmp/dashboard.heartbeat）。

三查：管道格式契约（`ISO8601|pid|pid`，services_registry._read_heartbeat 即认，零新增
解析器）/ 原子写（tmp+os.replace，无半行无残留）/ 停机 best-effort 清除（仅删本进程 pid）。
"""

from __future__ import annotations

import os
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

import zephyr.frontend.dashboard.api_server as api_server  # noqa: E402
from zephyr.frontend.dashboard import services_registry  # noqa: E402


@pytest.fixture()
def hb_path(tmp_path: Path, monkeypatch):
    """心跳落点重定向到 tmp_path（测试隔离红线：禁写生产 tmp/）。"""
    p = tmp_path / "dashboard.heartbeat"
    monkeypatch.setattr(api_server, "HEARTBEAT_PATH", p)
    return p


def test_write_format_pipe_contract(hb_path: Path, tmp_path: Path, monkeypatch):
    """心跳格式 = ISO8601(显式时区)|pid|pid，且读端 services_registry 即认。"""
    api_server._write_heartbeat()
    parts = hb_path.read_text(encoding="utf-8").strip().split("|")
    assert len(parts) == 3, f"管道格式须三段: {parts!r}"
    ts = datetime.fromisoformat(parts[0])
    assert ts.tzinfo is not None  # RULE-SCHEMA-TZ：显式时区
    assert abs(time.time() - ts.timestamp()) < 10
    assert parts[1] == parts[2] == str(os.getpid())  # guard/child 双槽位同填本进程
    monkeypatch.setattr(services_registry, "_TMP", tmp_path)
    hb = services_registry._read_heartbeat("dashboard.heartbeat")
    assert hb is not None
    assert hb["guard_pid"] == os.getpid() and hb["child_pid"] == os.getpid()
    assert abs(hb["ts"] - time.time()) < 10


def test_write_atomic_no_tmp_leftover(hb_path: Path):
    """连写两跳：每跳 tmp 均被 os.replace 消费，落点目录只剩成品（无半行无残留）。"""
    for _ in range(2):
        api_server._write_heartbeat()
    assert list(hb_path.parent.iterdir()) == [hb_path]
    parts = hb_path.read_text(encoding="utf-8").strip().split("|")
    assert len(parts) == 3 and parts[1] == str(os.getpid())


def test_cleanup_removes_own_pid_only(hb_path: Path):
    """停机清除只删本进程 pid 的心跳，不误删后继实例。"""
    api_server._write_heartbeat()
    api_server._cleanup_heartbeat()
    assert not hb_path.exists()
    hb_path.write_text("2026-01-01T00:00:00+00:00|999999|999999\n", encoding="utf-8")
    api_server._cleanup_heartbeat()
    assert hb_path.exists()  # 他者心跳保留


def test_cleanup_tolerates_missing_and_garbage(hb_path: Path):
    """best-effort：文件缺失/损坏（无 pid 段）均不抛、不误删。"""
    api_server._cleanup_heartbeat()  # 缺失
    assert not hb_path.exists()
    hb_path.write_text("garbage-no-pipe", encoding="utf-8")
    api_server._cleanup_heartbeat()  # 半行/损坏
    assert hb_path.exists()


def test_no_heartbeat_thread_under_pytest():
    """pytest 守卫：测试进程禁启心跳线程（同 ops-alert-feed 惯例，防写生产 tmp/）。"""
    assert not [t for t in threading.enumerate() if t.name == "dashboard-heartbeat"]
