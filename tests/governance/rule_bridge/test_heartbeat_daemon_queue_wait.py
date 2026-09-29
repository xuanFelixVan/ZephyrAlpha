# [BLUEPRINT] MOD-GOV_HEARTBEAT_DAEMON_TEST | tests/governance/rule_bridge/test_heartbeat_daemon_queue_wait.py | §C355
# [MODULE] tests.governance.rule_bridge.test_heartbeat_daemon_queue_wait
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.heartbeat_daemon
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] tmp_path 隔离（queue_root 显式传参）；不启动真实 daemon 进程；不触生产队列
# [MODIFY-GUARD] 测试函数名与 heartbeat_daemon._session_has_pending_queue_items / run_daemon 退出语义对齐
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败→pytest assert error
# [TESTS] self
# [A_module] module_id=MOD-GOV_HEARTBEAT_DAEMON_TEST | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""C355 落地期判活测试——队列等待 > TTL 不再导致落地期 SESSION-REQUIRED 误处死。

覆盖：
  1. _session_has_pending_queue_items：pending/processing 命中、他session/空队列不命中、
     腐坏项不判活、resolve_queue_root 故障保守 False
  2. run_daemon：idle 超限 + 有队列待落项 → keepalive=commit_queue_wait 不自退
  3. run_daemon：idle 超限 + 队列清空 → 照旧 idle timeout 自退（#ARCH-HEARTBEAT-002 零回退）
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from unittest.mock import patch

from zephyr.gov_enforcement.rule_bridge.heartbeat_daemon import (
    _session_has_pending_queue_items,
    heartbeat_file_path,
    run_daemon,
)


def _make_queue_item(queue_root: Path, state: str, session_id: str, qid: str = "q-1") -> None:
    state_dir = queue_root / state
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / f"{qid}.json").write_text(
        json.dumps({"qid": qid, "session_id": session_id, "created_at": "t"}),
        encoding="utf-8",
    )


def test_pending_item_for_same_session_is_liveness(tmp_path: Path) -> None:
    _make_queue_item(tmp_path, "pending", "sess-q1")
    assert _session_has_pending_queue_items("sess-q1", tmp_path, queue_root=tmp_path) is True


def test_processing_item_for_same_session_is_liveness(tmp_path: Path) -> None:
    _make_queue_item(tmp_path, "processing", "sess-q2", qid="q-2")
    assert _session_has_pending_queue_items("sess-q2", tmp_path, queue_root=tmp_path) is True


def test_other_session_or_empty_queue_is_not_liveness(tmp_path: Path) -> None:
    _make_queue_item(tmp_path, "pending", "sess-other")
    assert _session_has_pending_queue_items("sess-q3", tmp_path, queue_root=tmp_path) is False
    empty = tmp_path / "empty_queue"
    empty.mkdir()
    assert _session_has_pending_queue_items("sess-q3", tmp_path, queue_root=empty) is False


def test_corrupt_item_does_not_grant_liveness(tmp_path: Path) -> None:
    state_dir = tmp_path / "pending"
    state_dir.mkdir(parents=True)
    (state_dir / "q-bad.json").write_text("{not-json", encoding="utf-8")
    assert _session_has_pending_queue_items("sess-q4", tmp_path, queue_root=tmp_path) is False


def test_resolver_failure_is_conservative_false(tmp_path: Path, monkeypatch) -> None:
    import scripts.commit_queue as cq

    def _boom(_root=None):
        raise RuntimeError("queue root unavailable")

    monkeypatch.setattr(cq, "resolve_queue_root", _boom)
    assert _session_has_pending_queue_items("sess-q5", tmp_path) is False


def test_idle_daemon_kept_alive_by_queue_wait(tmp_path: Path) -> None:
    """idle 4000s + 队列有本会话 pending 项 → keepalive 不自退（落地等待面）。"""
    queue_root = tmp_path / "queue"
    _make_queue_item(queue_root, "pending", "sess-c355-a", qid="q-a1")

    class _FakeRegistry:
        def __init__(self, root):
            pass

        def get_session(self, sid):
            # 恒返回 idle 4000s 的陈旧 session；由 max_iterations 兜底退出
            return {
                "session_id": sid,
                "last_activity": time.time() - 4000,
                "start_time": time.time() - 5000,
            }

        def heartbeat(self, sid):
            pass

    with (
        patch(
            "zephyr.security.access_control.session_concurrency.SessionRegistry",
            _FakeRegistry,
        ),
        patch("zephyr.gov_enforcement.rule_bridge.heartbeat_daemon._INITIAL_DELAY", 0.05),
        patch("zephyr.gov_enforcement.rule_bridge.heartbeat_daemon._MAX_IDLE_SECONDS", 1800),
        patch("scripts.commit_queue.resolve_queue_root", lambda _root=None: queue_root),
    ):
        rc = run_daemon("sess-c355-a", tmp_path, interval=0.05, max_iterations=2)

    assert rc == 0
    hb = heartbeat_file_path(tmp_path, "sess-c355-a")
    recs = [json.loads(line) for line in hb.read_text(encoding="utf-8").strip().splitlines()]
    keepalives = [r for r in recs if r["status"] == "alive" and r.get("keepalive") == "commit_queue_wait"]
    assert keepalives, "队列等待期应有 keepalive=commit_queue_wait 留痕"
    assert "idle timeout" not in [r.get("reason") for r in recs if r["status"] == "exited"], (
        "有队列待落项时不得以 idle timeout 自退"
    )


def test_idle_daemon_still_exits_when_queue_empty(tmp_path: Path) -> None:
    """idle 4000s + 队列无本会话项 → 照旧 idle timeout 自退（治本零回退）。"""
    queue_root = tmp_path / "queue"
    queue_root.mkdir()
    _make_queue_item(queue_root, "pending", "sess-someone-else", qid="q-x9")

    class _FakeRegistry:
        def __init__(self, root):
            pass

        def get_session(self, sid):
            return {
                "session_id": sid,
                "last_activity": time.time() - 4000,
                "start_time": time.time() - 5000,
            }

        def heartbeat(self, sid):
            pass

    with (
        patch(
            "zephyr.security.access_control.session_concurrency.SessionRegistry",
            _FakeRegistry,
        ),
        patch("zephyr.gov_enforcement.rule_bridge.heartbeat_daemon._INITIAL_DELAY", 0.05),
        patch("zephyr.gov_enforcement.rule_bridge.heartbeat_daemon._MAX_IDLE_SECONDS", 1800),
        patch("scripts.commit_queue.resolve_queue_root", lambda _root=None: queue_root),
    ):
        rc = run_daemon("sess-c355-b", tmp_path, interval=0.05)

    assert rc == 0
    hb = heartbeat_file_path(tmp_path, "sess-c355-b")
    recs = [json.loads(line) for line in hb.read_text(encoding="utf-8").strip().splitlines()]
    exited = [r for r in recs if r["status"] == "exited"]
    assert exited and exited[0]["reason"] == "idle timeout"
    assert not [r for r in recs if r["status"] == "alive" and r.get("keepalive") == "commit_queue_wait"]
