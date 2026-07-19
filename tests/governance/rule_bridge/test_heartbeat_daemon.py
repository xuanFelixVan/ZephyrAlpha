# [BLUEPRINT] MOD-GOV_HEARTBEAT_DAEMON_TEST | tests/governance/rule_bridge/test_heartbeat_daemon.py | §Ruling-100PCT-AI-GOVERNANCE-P3-1
# [MODULE] tests.governance.rule_bridge.test_heartbeat_daemon
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.heartbeat_daemon
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 临时目录隔离测试，不污染主仓库；不依赖真实 DB；不启动真实 daemon 进程
# [MODIFY-GUARD] 测试函数名与 heartbeat_daemon API 对齐
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败→pytest assert error
# [TESTS] self
# [TTL] task_bound
"""test_heartbeat_daemon.py — heartbeat daemon smoke test（Ruling:100PCT-AI-GOVERNANCE P3-1）

测试覆盖（P1-1 ~ P1-3）：
  1. heartbeat_file_path 路径格式
  2. cleanup_heartbeat_file 清理（文件存在 / 不存在 / 不影响 emergency_count.json）
  3. _append_heartbeat_log JSONL 追加（多记录）
  4. _session_in_registry 注册表查询（mock SessionRegistry）
  5. run_daemon 生命周期 smoke（启动 → 心跳 → session 注销后退出）

测试策略：
  - 每个测试用独立临时目录（tmp_path），不污染主仓库
  - mock SessionRegistry 避免真实 DB 依赖
  - run_daemon 用短 interval（0.05s）+ session 立即注销 避免测试阻塞

注：emergency_commit 成本递增 + _classify_merge_failure 错误分类不在 heartbeat 治本范围内，
    由独立测试模块覆盖（避免 test-source 符号漂移）。
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from zephyr.gov_enforcement.rule_bridge.heartbeat_daemon import (
    _append_heartbeat_log,
    _session_in_registry,
    cleanup_heartbeat_file,
    heartbeat_file_path,
    run_daemon,
)


# ---------------------------------------------------------------------------
# P1-1: heartbeat_daemon.py 单元测试
# ---------------------------------------------------------------------------


def test_heartbeat_file_path_format(tmp_path: Path) -> None:
    """heartbeat_file_path 返回正确格式 <root>/.runtime/sessions/<sid>/heartbeat.jsonl。"""
    p = heartbeat_file_path(tmp_path, "sess-test-001")
    assert p == tmp_path / ".runtime" / "sessions" / "sess-test-001" / "heartbeat.jsonl"


def test_cleanup_heartbeat_file_when_exists(tmp_path: Path) -> None:
    """cleanup_heartbeat_file 删除已存在的 heartbeat.jsonl，返回 True。"""
    hb = heartbeat_file_path(tmp_path, "sess-001")
    hb.parent.mkdir(parents=True, exist_ok=True)
    hb.write_text('{"ts":"2026-07-20T00:00:00Z","status":"started"}\n', encoding="utf-8")
    assert hb.exists()
    assert cleanup_heartbeat_file(tmp_path, "sess-001") is True
    assert not hb.exists()


def test_cleanup_heartbeat_file_when_not_exists(tmp_path: Path) -> None:
    """cleanup_heartbeat_file 文件不存在时返回 True（幂等）。"""
    assert cleanup_heartbeat_file(tmp_path, "sess-nonexistent") is True


def test_cleanup_heartbeat_file_preserves_emergency_count(tmp_path: Path) -> None:
    """cleanup_heartbeat_file 只删 heartbeat.jsonl，不删 emergency_count.json。"""
    sid = "sess-preserve-001"
    hb = heartbeat_file_path(tmp_path, sid)
    hb.parent.mkdir(parents=True, exist_ok=True)
    hb.write_text('{"status":"started"}\n', encoding="utf-8")
    emergency_file = hb.parent / "emergency_count.json"
    emergency_file.write_text('{"count":3}', encoding="utf-8")

    assert cleanup_heartbeat_file(tmp_path, sid) is True
    assert not hb.exists()
    assert emergency_file.exists(), "emergency_count.json must NOT be deleted by heartbeat cleanup"


def test_append_heartbeat_log_creates_file(tmp_path: Path) -> None:
    """_append_heartbeat_log 创建文件并写入首条记录。"""
    hb = heartbeat_file_path(tmp_path, "sess-log-001")
    _append_heartbeat_log(hb, "started", {"interval": 30})
    assert hb.exists()
    lines = hb.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    rec = json.loads(lines[0])
    assert rec["status"] == "started"
    assert rec["interval"] == 30
    assert "ts" in rec and "pid" in rec


def test_append_heartbeat_log_appends_multiple(tmp_path: Path) -> None:
    """_append_heartbeat_log 多次调用追加记录（不覆盖）。"""
    hb = heartbeat_file_path(tmp_path, "sess-log-002")
    _append_heartbeat_log(hb, "started")
    _append_heartbeat_log(hb, "alive")
    _append_heartbeat_log(hb, "alive")
    _append_heartbeat_log(hb, "exited", {"reason": "session not in registry"})

    lines = hb.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 4
    statuses = [json.loads(line)["status"] for line in lines]
    assert statuses == ["started", "alive", "alive", "exited"]


# ---------------------------------------------------------------------------
# P1-1: _session_in_registry（mock SessionRegistry）
# ---------------------------------------------------------------------------


def test_session_in_registry_returns_true_when_present(tmp_path: Path) -> None:
    """session 在 registry 中时返回 True。"""
    class _FakeRegistry:
        def __init__(self, root):
            pass
        def get(self, sid):
            return {"session_id": sid}  # 非 None

    with patch(
        "zephyr.security.access_control.session_concurrency.SessionRegistry",
        _FakeRegistry,
    ):
        assert _session_in_registry("sess-001", tmp_path) is True


def test_session_in_registry_returns_false_when_absent(tmp_path: Path) -> None:
    """session 不在 registry 中时返回 False（daemon 应退出）。"""
    class _FakeRegistry:
        def __init__(self, root):
            pass
        def get(self, sid):
            return None

    with patch(
        "zephyr.security.access_control.session_concurrency.SessionRegistry",
        _FakeRegistry,
    ):
        assert _session_in_registry("sess-002", tmp_path) is False


def test_session_in_registry_returns_true_on_exception(tmp_path: Path) -> None:
    """registry 查询异常时返回 True（保守不退出，避免误判）。"""
    class _FakeRegistry:
        def __init__(self, root):
            raise RuntimeError("DB down")
        def get(self, sid):
            return None

    with patch(
        "zephyr.security.access_control.session_concurrency.SessionRegistry",
        _FakeRegistry,
    ):
        assert _session_in_registry("sess-003", tmp_path) is True


# ---------------------------------------------------------------------------
# P1-1: run_daemon 生命周期 smoke test
# ---------------------------------------------------------------------------


def test_run_daemon_lifecycle_smoke(tmp_path: Path) -> None:
    """run_daemon 生命周期：started → alive → exited（session 注销后退出）。

    用短 interval（0.05s）+ mock registry 立即返回 None，确保 1s 内退出。
    """
    call_count = {"n": 0}

    class _FakeRegistry:
        def __init__(self, root):
            pass
        def get(self, sid):
            call_count["n"] += 1
            # 第 1 次查询（_session_in_registry）：返回非 None（alive）
            # 第 2 次开始返回 None，让 daemon 退出
            if call_count["n"] == 1:
                return {"session_id": sid}
            return None
        def heartbeat(self, sid):
            pass

    with patch(
        "zephyr.security.access_control.session_concurrency.SessionRegistry",
        _FakeRegistry,
    ):
        # patch INITIAL_DELAY 和 interval 都缩短到 0.05s
        with patch(
            "zephyr.gov_enforcement.rule_bridge.heartbeat_daemon._INITIAL_DELAY", 0.05
        ), patch(
            "zephyr.gov_enforcement.rule_bridge.heartbeat_daemon._HEARTBEAT_INTERVAL", 0.05
        ):
            rc = run_daemon("sess-life-001", tmp_path, interval=0.05)

    assert rc == 0, "daemon 应正常退出（rc=0）"

    hb = heartbeat_file_path(tmp_path, "sess-life-001")
    assert hb.exists(), "heartbeat.jsonl 应被创建"
    lines = hb.read_text(encoding="utf-8").strip().splitlines()
    statuses = [json.loads(line)["status"] for line in lines]
    assert "started" in statuses, "应有 started 记录"
    assert "exited" in statuses, "应有 exited 记录（session 注销后）"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
