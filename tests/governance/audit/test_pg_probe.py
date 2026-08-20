# [A_test] module_id: MOD-GOV_pg_probe | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.audit.test_pg_probe
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH] ARCH-119
"""test_pg_probe.py — PG 可用性前置探针 + DB 降级留痕统一入口单测（tracker #116 / #ARCH-119）

权威依据：src/zephyr/governance/audit/pg_probe.py

测试组：
- TestProbePgTcp: 纯 TCP 探测（真实监听端口→可达；关闭端口→不可达不抛异常）
- TestRefreshState: 状态文件写入/读取（reachable=True/False、first_offline_at 锚点保留、原子写）
- TestReadState: 缺失/损坏 JSON → None
- TestProbeShowsOffline: 新鲜离线→True；陈旧离线→False；在线→False；缺失→False
- TestOfflineBeyond: first_offline_at 超阈→True；不足→False；在线→False；缺失→False
- TestLogDbFailopen: DB_OFFLINE 落盘+当日同签名去重；REAL_ERROR 逐次留痕；
  受影响文件清单入 detail；project_root 无效→跳过不落盘

测试隔离：tmp_path 作 project_root；TCP 探测用真实 loopback socket/关闭端口；
governance.db 落 tmp_path/data/databases/（anchor_main_root 对非 worktree 原样返回）。
"""

from __future__ import annotations

import json
import socket
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.governance.audit.pg_probe import (  # noqa: E402
    PG_PROBE_STATE_REL,
    log_db_failopen,
    pg_offline_beyond,
    pg_probe_shows_offline,
    probe_pg_tcp,
    read_pg_probe_state,
    refresh_pg_probe_state,
)

_UTC = timezone.utc


def _now_iso() -> str:
    return datetime.now(_UTC).isoformat()


def _write_state(project_root: Path, **overrides) -> dict:
    """直接写探针状态文件（绕过探测）。"""
    state = {
        "reachable": False,
        "checked_at": _now_iso(),
        "host": "localhost",
        "port": 5432,
        "error": "ConnectionRefusedError: refused",
        "last_reachable_at": None,
        "first_offline_at": _now_iso(),
    }
    state.update(overrides)
    path = project_root / PG_PROBE_STATE_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state), encoding="utf-8")
    return state


def _read_log_rows(project_root: Path) -> list[tuple]:
    """读取 tmp governance.db 的 reconcile_execution_log 全部行。"""
    db_path = project_root / "data" / "databases" / "governance.db"
    if not db_path.is_file():
        return []
    conn = sqlite3.connect(str(db_path))
    try:
        return conn.execute("SELECT gate_id, action, detail FROM reconcile_execution_log").fetchall()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# TestProbePgTcp
# ---------------------------------------------------------------------------


class TestProbePgTcp:
    """纯 TCP 探测。"""

    def test_reachable_when_listening(self) -> None:
        """真实监听端口 → 可达。"""
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.bind(("127.0.0.1", 0))
        srv.listen(1)
        try:
            port = srv.getsockname()[1]
            reachable, error = probe_pg_tcp("127.0.0.1", port, timeout=2.0)
            assert reachable is True
            assert error == ""
        finally:
            srv.close()

    def test_unreachable_closed_port(self) -> None:
        """关闭端口 → 不可达 + 错误信息，不抛异常。"""
        # 找一个确定未监听的端口：先绑再关，端口释放后极大概率仍空闲
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.bind(("127.0.0.1", 0))
        port = srv.getsockname()[1]
        srv.close()
        reachable, error = probe_pg_tcp("127.0.0.1", port, timeout=1.0)
        assert reachable is False
        assert error != ""


# ---------------------------------------------------------------------------
# TestRefreshState
# ---------------------------------------------------------------------------


class TestRefreshState:
    """refresh_pg_probe_state 状态文件读写。"""

    def test_refresh_offline_writes_state(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """端点不可达 → reachable=False 落盘，可读回。"""
        monkeypatch.setattr(
            "zephyr.governance.audit.pg_probe._resolve_pg_endpoint",
            lambda: ("127.0.0.1", 1),  # 端口 1 确定未监听
        )
        state = refresh_pg_probe_state(tmp_path)
        assert state["reachable"] is False
        assert state["error"] != ""
        assert state["first_offline_at"] is not None
        on_disk = read_pg_probe_state(tmp_path)
        assert on_disk is not None
        assert on_disk["reachable"] is False

    def test_refresh_online_clears_offline_anchor(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """离线后恢复可达 → first_offline_at 清空、last_reachable_at 更新。"""
        _write_state(tmp_path, reachable=False)
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.bind(("127.0.0.1", 0))
        srv.listen(1)
        try:
            port = srv.getsockname()[1]
            monkeypatch.setattr(
                "zephyr.governance.audit.pg_probe._resolve_pg_endpoint",
                lambda: ("127.0.0.1", port),
            )
            state = refresh_pg_probe_state(tmp_path)
        finally:
            srv.close()
        assert state["reachable"] is True
        assert state["first_offline_at"] is None
        assert state["last_reachable_at"] is not None

    def test_refresh_offline_keeps_first_offline_anchor(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """持续离线 → first_offline_at 保留首次观测值（不被刷新）。"""
        old_anchor = (datetime.now(_UTC) - timedelta(hours=30)).isoformat()
        _write_state(tmp_path, reachable=False, first_offline_at=old_anchor)
        monkeypatch.setattr(
            "zephyr.governance.audit.pg_probe._resolve_pg_endpoint",
            lambda: ("127.0.0.1", 1),
        )
        state = refresh_pg_probe_state(tmp_path)
        assert state["reachable"] is False
        assert state["first_offline_at"] == old_anchor

    def test_refresh_config_failure_never_raises(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """配置解析失败 → reachable=False 落盘（config_unresolved），不抛异常。"""

        def _raise():
            raise FileNotFoundError("no config")

        monkeypatch.setattr(
            "zephyr.governance.audit.pg_probe._resolve_pg_endpoint",
            _raise,
        )
        state = refresh_pg_probe_state(tmp_path)
        assert state["reachable"] is False
        assert "config_unresolved" in state["error"]


# ---------------------------------------------------------------------------
# TestReadState
# ---------------------------------------------------------------------------


class TestReadState:
    """read_pg_probe_state 容错。"""

    def test_missing_returns_none(self, tmp_path: Path) -> None:
        assert read_pg_probe_state(tmp_path) is None

    def test_corrupt_returns_none(self, tmp_path: Path) -> None:
        path = tmp_path / PG_PROBE_STATE_REL
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{not json", encoding="utf-8")
        assert read_pg_probe_state(tmp_path) is None


# ---------------------------------------------------------------------------
# TestProbeShowsOffline
# ---------------------------------------------------------------------------


class TestProbeShowsOffline:
    """pg_probe_shows_offline 判定。"""

    def test_fresh_offline_true(self, tmp_path: Path) -> None:
        _write_state(tmp_path, reachable=False)
        assert pg_probe_shows_offline(tmp_path) is True

    def test_stale_offline_false(self, tmp_path: Path) -> None:
        old = (datetime.now(_UTC) - timedelta(hours=2)).isoformat()
        _write_state(tmp_path, reachable=False, checked_at=old)
        assert pg_probe_shows_offline(tmp_path) is False

    def test_reachable_false(self, tmp_path: Path) -> None:
        _write_state(tmp_path, reachable=True)
        assert pg_probe_shows_offline(tmp_path) is False

    def test_missing_false(self, tmp_path: Path) -> None:
        assert pg_probe_shows_offline(tmp_path) is False


# ---------------------------------------------------------------------------
# TestOfflineBeyond
# ---------------------------------------------------------------------------


class TestOfflineBeyond:
    """pg_offline_beyond 豁免判据。"""

    def test_beyond_threshold_true(self, tmp_path: Path) -> None:
        old = (datetime.now(_UTC) - timedelta(hours=25)).isoformat()
        _write_state(tmp_path, reachable=False, first_offline_at=old)
        assert pg_offline_beyond(tmp_path, 24 * 3600) is True

    def test_under_threshold_false(self, tmp_path: Path) -> None:
        recent = (datetime.now(_UTC) - timedelta(hours=1)).isoformat()
        _write_state(tmp_path, reachable=False, first_offline_at=recent)
        assert pg_offline_beyond(tmp_path, 24 * 3600) is False

    def test_reachable_false(self, tmp_path: Path) -> None:
        _write_state(tmp_path, reachable=True, first_offline_at=None)
        assert pg_offline_beyond(tmp_path, 24 * 3600) is False

    def test_missing_false(self, tmp_path: Path) -> None:
        assert pg_offline_beyond(tmp_path, 24 * 3600) is False


# ---------------------------------------------------------------------------
# TestLogDbFailopen
# ---------------------------------------------------------------------------


class TestLogDbFailopen:
    """log_db_failopen 统一留痕（critical_warn + 签名 + 去重）。"""

    def test_offline_persists_critical_warn(self, tmp_path: Path) -> None:
        """DB 离线降级 → critical_warn 落盘，含 gate_id/原因/受影响文件/签名。"""
        log_db_failopen(
            tmp_path,
            "RENAME-DEPGRAPH-SYNC",
            db_offline=True,
            reason="depgraph 查询失败，降级放行（探针证实 PG 离线）",
            affected_files=["a.py -> b.py"],
            session_id="sess-x",
        )
        rows = _read_log_rows(tmp_path)
        assert len(rows) == 1
        gate_id, action, detail = rows[0]
        assert gate_id == "RENAME-DEPGRAPH-SYNC"
        assert action == "critical_warn"
        assert "DB 离线降级" in detail
        assert "a.py -> b.py" in detail
        assert "failover_sig=RENAME-DEPGRAPH-SYNC:DB_OFFLINE" in detail

    def test_offline_dedup_same_day(self, tmp_path: Path) -> None:
        """同签名当日去重——两次调用只落一条（防 PG 长期离线告警疲劳）。"""
        for _ in range(2):
            log_db_failopen(
                tmp_path,
                "NEW-FILE-DEPGRAPH-ENFORCEMENT",
                db_offline=True,
                reason="降级放行（探针证实 PG 离线）",
                affected_files=["x.py"],
            )
        rows = _read_log_rows(tmp_path)
        assert len(rows) == 1

    def test_real_error_not_deduped(self, tmp_path: Path) -> None:
        """探针在线而 gate 失败=真实错误 → 逐次留痕（不静默，不去重）。"""
        for _ in range(2):
            log_db_failopen(
                tmp_path,
                "RENAME-DEPGRAPH-SYNC",
                db_offline=False,
                reason="探针未证实离线——真实连接错误",
                affected_files=["a.py -> b.py"],
            )
        rows = _read_log_rows(tmp_path)
        assert len(rows) == 2
        assert all("真实错误" in r[2] for r in rows)

    def test_invalid_project_root_skips(self, tmp_path: Path) -> None:
        """project_root 非真实目录 → 跳过不落盘、不抛异常。"""
        log_db_failopen(
            tmp_path / "nonexistent" / "deep",
            "GATE-X",
            db_offline=True,
            reason="test",
        )
        assert not (tmp_path / "nonexistent").exists()
