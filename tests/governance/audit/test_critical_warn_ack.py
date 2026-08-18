# [BLUEPRINT] MOD-TEST-282 | (auto-injected by S4 reconciler) | §
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
    ReconcileResult,
    _check_recent_critical_warns,
    _log_reconcile_results,
    acknowledge_critical_warns,
    backfill_auto_ack_healed,
    cleanup_reconcile_log,
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


def _str_ts(delta: timedelta) -> str:
    """str() 格式时间戳（空格分隔），与 _log_reconcile_results 存储格式对齐。

    _log_reconcile_results 经 now_utc()（datetime 对象）写入 SQLite，存储为
    空格分隔（'2026-07-23 09:52:09.276624+00:00'）。直接 SQL 插入的 warn 若用
    _iso()（'T' 分隔），与 clean 的空格格式做 logged_at > 比较时同日会误判
    （'T'(84) > ' '(32)），故 warn 也须用 str() 格式。
    """
    return str(datetime.now(timezone.utc) + delta)


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


class TestAutoAckHealedInline:
    """#AUTO-ACK-HEALED-WARN 治本：_log_reconcile_results 插入 clean 时自动 ack 前置已愈合 warn。"""

    def test_clean_auto_acks_preceding_healed_warn(self, tmp_path: Path) -> None:
        """同 gate 的前置 critical_warn（有后续 clean）被自动 ack。"""
        import sqlite3

        _init_db(tmp_path)
        # 直接 SQL 插入一条历史 critical_warn（str 格式，早于即将插入的 clean）
        _insert(tmp_path, "GATE-AUTO-1", "critical_warn", _str_ts(timedelta(hours=-2)), "rc-auto-w1")
        # 插入 clean（经 _log_reconcile_results，触发内联 auto-ack）
        _log_reconcile_results(
            tmp_path,
            [ReconcileResult(action="clean", detail="healed", gate_id="GATE-AUTO-1")],
            "sess-auto-1",
            trigger_source="post_commit",
        )
        conn = sqlite3.connect(str(_db_path(tmp_path)))
        try:
            ack = conn.execute(
                "SELECT acknowledged_at FROM reconcile_execution_log WHERE log_id='rc-auto-w1'"
            ).fetchone()
            assert ack is not None and ack[0] is not None, "前置 critical_warn 应被自动 ack"
        finally:
            conn.close()

    def test_truly_active_warn_not_acked(self, tmp_path: Path) -> None:
        """无后续 clean 的真正活跃 critical_warn 保持 unack（不被误伤）。"""
        import sqlite3

        _init_db(tmp_path)
        # GATE-AUTO-2 只有 critical_warn，无 clean（真正活跃）
        _insert(tmp_path, "GATE-AUTO-2", "critical_warn", _str_ts(timedelta(hours=-1)), "rc-auto-w2")
        # 为另一个 gate 插入 clean（不应影响 GATE-AUTO-2）
        _log_reconcile_results(
            tmp_path,
            [ReconcileResult(action="clean", detail="ok", gate_id="GATE-AUTO-OTHER")],
            "sess-auto-2",
            trigger_source="post_commit",
        )
        conn = sqlite3.connect(str(_db_path(tmp_path)))
        try:
            ack = conn.execute(
                "SELECT acknowledged_at FROM reconcile_execution_log WHERE log_id='rc-auto-w2'"
            ).fetchone()
            assert ack is not None and ack[0] is None, "真正活跃 critical_warn 不应被 ack"
        finally:
            conn.close()

    def test_auto_ack_idempotent(self, tmp_path: Path) -> None:
        """重复 clean 不重复 ack（acknowledged_at IS NULL 过滤幂等）。"""
        import sqlite3

        _init_db(tmp_path)
        _insert(tmp_path, "GATE-AUTO-3", "critical_warn", _str_ts(timedelta(hours=-2)), "rc-auto-w3")
        _log_reconcile_results(
            tmp_path,
            [ReconcileResult(action="clean", gate_id="GATE-AUTO-3")],
            "sess-auto-3a",
            trigger_source="post_commit",
        )
        # 第二次 clean（warn 已 ack，EXISTS 仍匹配但 acknowledged_at IS NULL 过滤掉）
        _log_reconcile_results(
            tmp_path,
            [ReconcileResult(action="clean", gate_id="GATE-AUTO-3")],
            "sess-auto-3b",
            trigger_source="post_commit",
        )
        conn = sqlite3.connect(str(_db_path(tmp_path)))
        try:
            # 只有一条 critical_warn，acknowledged_at 已设置一次即可
            row = conn.execute(
                "SELECT acknowledged_at FROM reconcile_execution_log WHERE log_id='rc-auto-w3'"
            ).fetchone()
            assert row[0] is not None
            # clean 记录应有 2 条
            n_clean = conn.execute(
                "SELECT COUNT(*) FROM reconcile_execution_log WHERE gate_id='GATE-AUTO-3' AND action='clean'"
            ).fetchone()[0]
            assert n_clean == 2
        finally:
            conn.close()


class TestBackfillAutoAckHealed:
    """#AUTO-ACK-HEALED-WARN 治本：backfill_auto_ack_healed 一次性回填历史自愈 warn。"""

    def test_backfill_acks_healed_leaves_active(self, tmp_path: Path) -> None:
        """回填：已愈合 warn 全部 ack，真正活跃 warn 保持 unack。"""
        import sqlite3

        _init_db(tmp_path)
        # G1: warn + clean（已愈合）
        _insert(tmp_path, "GB1", "critical_warn", _str_ts(timedelta(hours=-3)), "rc-bf-w1")
        _insert(tmp_path, "GB1", "clean", _str_ts(timedelta(hours=-2)), "rc-bf-c1")
        # G2: warn + clean（已愈合）
        _insert(tmp_path, "GB2", "critical_warn", _str_ts(timedelta(hours=-3)), "rc-bf-w2")
        _insert(tmp_path, "GB2", "clean", _str_ts(timedelta(hours=-2)), "rc-bf-c2")
        # G3: warn only（真正活跃）
        _insert(tmp_path, "GB3", "critical_warn", _str_ts(timedelta(hours=-1)), "rc-bf-w3")

        result = backfill_auto_ack_healed(tmp_path)
        assert result["error"] is None
        assert result["acknowledged"] == 2, f"应 ack 2 条已愈合 warn，实际 {result['acknowledged']}"

        conn = sqlite3.connect(str(_db_path(tmp_path)))
        try:
            for wid in ("rc-bf-w1", "rc-bf-w2"):
                ack = conn.execute(
                    "SELECT acknowledged_at FROM reconcile_execution_log WHERE log_id=?", (wid,)
                ).fetchone()[0]
                assert ack is not None, f"{wid} 应已 ack"
            ack3 = conn.execute(
                "SELECT acknowledged_at FROM reconcile_execution_log WHERE log_id='rc-bf-w3'"
            ).fetchone()[0]
            assert ack3 is None, "真正活跃 warn 不应被 ack"
        finally:
            conn.close()

    def test_backfill_idempotent(self, tmp_path: Path) -> None:
        """重复回填幂等（第二次 ack 0）。"""
        _init_db(tmp_path)
        _insert(tmp_path, "GBI", "critical_warn", _str_ts(timedelta(hours=-2)), "rc-bi-w")
        _insert(tmp_path, "GBI", "clean", _str_ts(timedelta(hours=-1)), "rc-bi-c")
        first = backfill_auto_ack_healed(tmp_path)
        second = backfill_auto_ack_healed(tmp_path)
        assert first["acknowledged"] == 1
        assert second["acknowledged"] == 0, "幂等：重复回填不应再 ack"

    def test_backfill_empty_db(self, tmp_path: Path) -> None:
        """空库回填不报错。"""
        result = backfill_auto_ack_healed(tmp_path)
        assert result["acknowledged"] == 0
        assert result["error"] is None


class TestCleanupReconcileLog:
    """#RECONCILE-LOG-RETENTION 治本：cleanup_reconcile_log 删除过期记录。"""

    def test_cleanup_deletes_old_records(self, tmp_path: Path) -> None:
        """删除 retention_days 天前的记录，保留新记录。"""
        import sqlite3

        _init_db(tmp_path)
        # 200 天前的记录（应删）
        _insert(tmp_path, "GC1", "clean", _str_ts(timedelta(days=-200)), "rc-old-1")
        _insert(tmp_path, "GC1", "warn", _str_ts(timedelta(days=-200)), "rc-old-2")
        # 10 天前的记录（应保留，<180 天）
        _insert(tmp_path, "GC2", "clean", _str_ts(timedelta(days=-10)), "rc-new-1")

        result = cleanup_reconcile_log(tmp_path, retention_days=180)
        assert result["error"] is None
        assert result["deleted"] == 2, f"应删 2 条 >180d 记录，实际 {result['deleted']}"

        conn = sqlite3.connect(str(_db_path(tmp_path)))
        try:
            remaining = conn.execute("SELECT COUNT(*) FROM reconcile_execution_log").fetchone()[0]
            assert remaining == 1, f"应剩 1 条新记录，实际 {remaining}"
            log_id = conn.execute("SELECT log_id FROM reconcile_execution_log").fetchone()[0]
            assert log_id == "rc-new-1"
        finally:
            conn.close()

    def test_cleanup_custom_retention(self, tmp_path: Path) -> None:
        """自定义保留天数生效。"""
        _init_db(tmp_path)
        _insert(tmp_path, "GC3", "clean", _str_ts(timedelta(days=-5)), "rc-c-1")
        # 保留 3 天 → 5 天前的记录应删
        result = cleanup_reconcile_log(tmp_path, retention_days=3)
        assert result["deleted"] == 1
        assert result["retention_days"] == 3

    def test_cleanup_empty_db(self, tmp_path: Path) -> None:
        """库不存在时不报错。"""
        result = cleanup_reconcile_log(tmp_path)
        assert result["deleted"] == 0
        assert result["error"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
