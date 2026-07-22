# [BLUEPRINT] MOD-TEST-282 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_test] module_id: SRC-TST-2401 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_critical_warn_ack.py — critical_warn 告警消解语义单测

权威依据：reconciliation_registry.py（GATE-DEPGRAPH-OPS 治本 Phase 2/3）
- acknowledge_critical_warns: 手动 ack 消音（acknowledged_at 列）
- _check_recent_critical_warns: 活跃告警查询（ack 消音 + clean 自愈消音）
- _ensure_ack_column: 老库幂等迁移（2026-07-19 前的库无 ack 列）
- _governance_db_path: 观测库锚定主仓库根（strip_session_worktree）

测试组：
- TestAckColumnMigration: 老库（无 ack 列）读写路径自动补列
- TestSelfHealingSilence: 同 gate_id 之后 clean 记录 → 旧 warn 自动消音
- TestAcknowledge: 手动 ack 消音 / 幂等 / 按 gate_id 过滤
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from zephyr.governance.audit.reconciliation_registry import (
    SQL_INSERT_RECONCILE_LOG,
    _check_recent_critical_warns,
    acknowledge_critical_warns,
)

# 老 schema（2026-07-19 前）：无 acknowledged_at 列
_SQL_CREATE_OLD = (
    "CREATE TABLE IF NOT EXISTS reconcile_execution_log ("
    "log_id TEXT PRIMARY KEY, logged_at TEXT NOT NULL, gate_id TEXT NOT NULL, "
    "session_id TEXT, trigger_source TEXT, action TEXT NOT NULL, detail TEXT, "
    "committed_files_summary TEXT)"
)


def _iso(delta: timedelta) -> str:
    return (datetime.now(timezone.utc) + delta).isoformat()


def _db_path(root: Path) -> Path:
    return root / "data" / "databases" / "governance.db"


def _init_db(root: Path, old_schema: bool = False) -> Path:
    """建 tmp 观测库。old_schema=True 模拟无 ack 列的老库。"""
    db = _db_path(root)
    db.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db))
    try:
        if old_schema:
            conn.execute(_SQL_CREATE_OLD)
        else:
            conn.execute(_SQL_CREATE_OLD[:-1] + ", acknowledged_at TEXT)")
        conn.commit()
    finally:
        conn.close()
    return db


def _insert(root: Path, gate_id: str, action: str, logged_at: str, log_id: str) -> None:
    conn = sqlite3.connect(str(_db_path(root)), timeout=10.0)
    try:
        conn.execute(
            SQL_INSERT_RECONCILE_LOG,
            (log_id, logged_at, gate_id, "sess-test", "pytest", action,
             f"{action} detail for {gate_id}", "x.py"),
        )
        conn.commit()
    finally:
        conn.close()


class TestAckColumnMigration:
    """老库（无 acknowledged_at 列）读写路径幂等补列。"""

    def test_check_active_warns_on_old_schema(self, tmp_path: Path) -> None:
        _init_db(tmp_path, old_schema=True)
        _insert(tmp_path, "GATE-X", "critical_warn", _iso(timedelta(hours=-1)), "rc-old1")
        warns = _check_recent_critical_warns(tmp_path, hours=24)
        assert len(warns) == 1
        assert warns[0]["gate_id"] == "GATE-X"
        # 列已补上（幂等，第二次查询不报错）
        assert _check_recent_critical_warns(tmp_path, hours=24) == warns

    def test_ack_on_old_schema(self, tmp_path: Path) -> None:
        _init_db(tmp_path, old_schema=True)
        _insert(tmp_path, "GATE-X", "critical_warn", _iso(timedelta(hours=-1)), "rc-old2")
        result = acknowledge_critical_warns(tmp_path)
        assert result["error"] is None
        assert result["acknowledged"] == 1
        assert _check_recent_critical_warns(tmp_path, hours=24) == []


class TestSelfHealingSilence:
    """同 gate_id 之后有 clean 记录 → 旧 critical_warn 自愈消音（无需 ack）。"""

    def test_clean_after_warn_silences(self, tmp_path: Path) -> None:
        _init_db(tmp_path)
        _insert(tmp_path, "GATE-DEPGRAPH-OPS", "critical_warn",
                _iso(timedelta(hours=-2)), "rc-w1")
        _insert(tmp_path, "GATE-DEPGRAPH-OPS", "clean",
                _iso(timedelta(hours=-1)), "rc-c1")
        assert _check_recent_critical_warns(tmp_path, hours=24) == []

    def test_clean_before_warn_does_not_silence(self, tmp_path: Path) -> None:
        _init_db(tmp_path)
        _insert(tmp_path, "GATE-X", "clean", _iso(timedelta(hours=-2)), "rc-c2")
        _insert(tmp_path, "GATE-X", "critical_warn",
                _iso(timedelta(hours=-1)), "rc-w2")
        warns = _check_recent_critical_warns(tmp_path, hours=24)
        assert len(warns) == 1

    def test_clean_of_other_gate_does_not_silence(self, tmp_path: Path) -> None:
        _init_db(tmp_path)
        _insert(tmp_path, "GATE-X", "critical_warn",
                _iso(timedelta(hours=-2)), "rc-w3")
        _insert(tmp_path, "GATE-Y", "clean", _iso(timedelta(hours=-1)), "rc-c3")
        warns = _check_recent_critical_warns(tmp_path, hours=24)
        assert len(warns) == 1
        assert warns[0]["gate_id"] == "GATE-X"


class TestAcknowledge:
    """手动 ack：消音 / 幂等 / gate_id 过滤 / 窗口过滤。"""

    def test_manual_ack_silences(self, tmp_path: Path) -> None:
        _init_db(tmp_path)
        _insert(tmp_path, "GATE-X", "critical_warn", _iso(timedelta(hours=-1)), "rc-m1")
        assert len(_check_recent_critical_warns(tmp_path, hours=24)) == 1
        result = acknowledge_critical_warns(tmp_path)
        assert result == {"acknowledged": 1, "gate_id": None, "error": None}
        assert _check_recent_critical_warns(tmp_path, hours=24) == []

    def test_ack_idempotent(self, tmp_path: Path) -> None:
        _init_db(tmp_path)
        _insert(tmp_path, "GATE-X", "critical_warn", _iso(timedelta(hours=-1)), "rc-m2")
        first = acknowledge_critical_warns(tmp_path)
        second = acknowledge_critical_warns(tmp_path)
        assert first["acknowledged"] == 1
        assert second["acknowledged"] == 0  # 幂等：重复 ack 不再 UPDATE
        assert second["error"] is None

    def test_ack_by_gate_id(self, tmp_path: Path) -> None:
        _init_db(tmp_path)
        _insert(tmp_path, "G1", "critical_warn", _iso(timedelta(hours=-1)), "rc-g1")
        _insert(tmp_path, "G2", "critical_warn", _iso(timedelta(hours=-1)), "rc-g2")
        result = acknowledge_critical_warns(tmp_path, gate_id="G1")
        assert result["acknowledged"] == 1
        warns = _check_recent_critical_warns(tmp_path, hours=24)
        assert len(warns) == 1
        assert warns[0]["gate_id"] == "G2"

    def test_ack_window_filter(self, tmp_path: Path) -> None:
        _init_db(tmp_path)
        _insert(tmp_path, "GATE-OLD", "critical_warn",
                _iso(timedelta(hours=-72)), "rc-old3")
        result = acknowledge_critical_warns(tmp_path, hours=24)
        assert result["acknowledged"] == 0  # 72h 前不在 24h 窗口内

    def test_ack_empty_db(self, tmp_path: Path) -> None:
        # 空库（表不存在）→ CREATE 兜底建表，ack 0 条不报错
        result = acknowledge_critical_warns(tmp_path)
        assert result["acknowledged"] == 0
        assert result["error"] is None


class TestGovernanceDbPathAnchor:
    """_governance_db_path 锚定主仓库根（Phase 3 观测数据单一定位）。"""

    def test_worktree_path_stripped_to_main(self, tmp_path: Path) -> None:
        from zephyr.governance.audit.reconciliation_registry import _governance_db_path

        fake_wt = tmp_path / ".aidrafts" / "sess-xyz"
        fake_wt.mkdir(parents=True)
        anchored = _governance_db_path(fake_wt)
        assert ".aidrafts" not in anchored
        assert anchored.endswith(str(Path("data") / "databases" / "governance.db"))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
