# [MODULE] tests.data.data.db.test_ch_write_guard
# [DOMAIN] D_DATA
# [TTL] permanent
# [STARTUP] imported_by_pytest
# [CONSUMERS] none（本件只被 pytest 采集；GATE-PRECOMMIT-RUN/gate-test 钩子间接执行）
"""①丙 写口只读开关验收单（统筹裁定 2026-10-13，考试案卷"测试进程写生产 CH"三条待判定之①丙）。

覆盖六条判据，全部 mock、**零真库连接**（get_client/get_http_host 一律被打桩，
断言里显式检查 HTTPConnection 未被调用）：

- enforce＋测试进程 → 四个写入口全抛 ClickHouseWriteGuardBlocked，且传输层一次都没被碰；
- enforce＋非测试进程 → 放行（本开关不是生产刹车，翻 enforce 不会让采集链停摆）；
- shadow＋测试进程 → 不抛，只留痕 .runtime/gate_audit/ch_write_guard.jsonl 一行 would_block；
- 只读语句（SELECT/DESCRIBE/…）不进闸；
- 开关优先级 env > flags.yaml > shadow，未知值/读不到都退 shadow（绝不静默 off）；
- 留痕逐条带 pid＋session_id＋op＋target＋state＋action，同 (state,op,target) 每进程只落一条。

真源指针：判据注释在 src/zephyr/data/ch_writer.py 的"①丙 写口只读开关"段；
开关出厂态在 config/flags.yaml flags.ch_write_guard。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from zephyr.data import ch_writer as cw  # noqa: E402

_INSERT_SQL = "INSERT INTO c1_market.kline_daily (symbol, trade_date) FORMAT TSV"


class _NoTransport:
    """任何真传输层被碰到就立即失败——本件必须零连库（让路窗与 §9.6 双重红线）。"""

    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003 — 打桩替身
        self.calls += 1
        raise AssertionError("测试不得触碰 CH 传输层（http.client.HTTPConnection 被调用）")


@pytest.fixture(autouse=True)
def _isolate_guard(monkeypatch, tmp_path):
    """审计面改指 tmp_path（测试禁写生产路径），并把传输层两根管子钉死。"""
    monkeypatch.setattr(cw, "_GUARD_REPO_ROOT", tmp_path)
    monkeypatch.setattr(cw, "get_client", lambda: None)
    monkeypatch.setattr(cw, "get_http_host", lambda: "")
    cw._write_guard_audited.clear()
    yield tmp_path
    cw._write_guard_audited.clear()


def _audit_rows(root: Path) -> list[dict]:
    log = root / cw._WRITE_GUARD_AUDIT_REL
    if not log.exists():
        return []
    return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_state_env_wins_and_unknown_falls_back_to_flags(monkeypatch):
    for value in ("off", "shadow", "enforce"):
        monkeypatch.setenv(cw._WRITE_GUARD_ENV, value)
        assert cw._write_guard_state() == value
    monkeypatch.setenv(cw._WRITE_GUARD_ENV, "banana")
    # 未知值 → 改读 flags 真源（本件用真仓根读出厂态，必须仍是三态之一，不得静默 off）
    monkeypatch.setattr(cw, "_GUARD_REPO_ROOT", _PROJECT_ROOT)
    assert cw._write_guard_state() in cw._WRITE_GUARD_STATES


def test_state_read_failure_is_shadow_not_off(monkeypatch, tmp_path):
    monkeypatch.delenv(cw._WRITE_GUARD_ENV, raising=False)
    monkeypatch.setattr(cw, "_GUARD_REPO_ROOT", tmp_path / "nope")
    assert cw._write_guard_state() == "shadow"


def test_enforce_test_process_blocks_all_four_write_openings(monkeypatch):
    monkeypatch.setenv(cw._WRITE_GUARD_ENV, "enforce")
    monkeypatch.setattr(cw, "_test_process_detected", lambda: True)
    spy = _NoTransport()
    monkeypatch.setattr(cw.http.client, "HTTPConnection", spy)

    with pytest.raises(cw.ClickHouseWriteGuardBlocked):
        cw.http_insert(_INSERT_SQL, b"000300.SH\t2026-01-05\n")
    with pytest.raises(cw.ClickHouseWriteGuardBlocked):
        cw.query("OPTIMIZE TABLE c1_market.kline_daily FINAL")
    with pytest.raises(cw.ClickHouseWriteGuardBlocked):
        cw.delete_where("c1_market.kline_daily", "trade_date = '2026-01-05'")
    with pytest.raises(cw.ClickHouseWriteGuardBlocked):
        cw.ensure_database("c1_market")
    assert spy.calls == 0


def test_enforce_non_test_process_is_not_blocked(monkeypatch):
    """生产面语义：本开关只咬测试进程，非测试进程一律放行（放行不等于写成功）。"""
    monkeypatch.setenv(cw._WRITE_GUARD_ENV, "enforce")
    monkeypatch.setattr(cw, "_test_process_detected", lambda: False)
    assert cw.http_insert(_INSERT_SQL, b"000300.SH\t2026-01-05\n") is False
    assert cw.delete_where("c1_market.kline_daily", "trade_date = '2026-01-05'") is False
    assert _audit_rows(cw._GUARD_REPO_ROOT) == []


def test_shadow_records_would_block_without_raising(monkeypatch):
    monkeypatch.setenv(cw._WRITE_GUARD_ENV, "shadow")
    monkeypatch.setattr(cw, "_test_process_detected", lambda: True)
    assert cw.http_insert(_INSERT_SQL, b"000300.SH\t2026-01-05\n") is False
    rows = _audit_rows(cw._GUARD_REPO_ROOT)
    assert len(rows) == 1
    assert rows[0]["action"] == "would_block"
    assert rows[0]["op"] == "http_insert"
    assert rows[0]["target"] == "c1_market.kline_daily"


def test_audit_carries_attribution_and_dedupes_per_process(monkeypatch):
    monkeypatch.setenv(cw._WRITE_GUARD_ENV, "shadow")
    monkeypatch.setenv("ZEPHYR_SESSION_ID", "st-maint4-20261013")
    monkeypatch.setattr(cw, "_test_process_detected", lambda: True)
    for _ in range(3):
        cw.http_insert(_INSERT_SQL, b"x\t1\n")
    cw.delete_where("c1_market.kline_daily", "1")
    rows = _audit_rows(cw._GUARD_REPO_ROOT)
    assert len(rows) == 2  # 同 (state,op,target) 只落一条，防 #ARCH-258 式洪峰
    assert {r["op"] for r in rows} == {"http_insert", "alter_delete"}
    for r in rows:
        assert r["session_id"] == "st-maint4-20261013"
        assert r["pid"] == __import__("os").getpid()
        assert {"ts", "state", "action", "target"} <= set(r)


def test_readonly_statements_never_enter_the_guard(monkeypatch):
    monkeypatch.setenv(cw._WRITE_GUARD_ENV, "enforce")
    monkeypatch.setattr(cw, "_test_process_detected", lambda: True)
    seen: list[tuple[str, str]] = []
    monkeypatch.setattr(cw, "_assert_write_allowed", lambda op, target, sql="": seen.append((op, target)))
    for stmt in (
        "SELECT 1",
        "DESCRIBE TABLE c1_market.kline_daily",
        "SHOW TABLES",
        "SYSTEM FLUSH LOGS",
        "WITH 1 AS x SELECT x",
        "EXPLAIN SELECT 1",
    ):
        assert cw.query(stmt) == ""
    assert seen == []
    assert cw.query("INSERT INTO c1_market.kline_daily FORMAT TSV") == ""
    assert seen and seen[0][0] == "query"


def test_sql_target_extraction_and_first_word_fallback():
    assert cw._sql_target(_INSERT_SQL) == "c1_market.kline_daily"
    assert cw._sql_target("ALTER TABLE c3_fundamental.share_unlock DELETE WHERE 1") == "c3_fundamental.share_unlock"
    assert cw._sql_target("CREATE DATABASE IF NOT EXISTS c9_meta") == "c9_meta"
    assert cw._sql_target("OPTIMIZE TABLE a.b FINAL") == "a.b"
    assert cw._sql_target("NONSENSE blah") == "NONSENSE"
    assert cw._sql_target("") == "<empty>"


def test_test_process_detection_three_signals(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.delenv("ZEPHYR_TEST_PG", raising=False)
    # 本件正跑在 pytest 里，sys.modules 有 pytest ⇒ 天然 True（自然样本，不打桩）
    assert "pytest" in sys.modules and cw._test_process_detected() is True
    monkeypatch.setenv("ZEPHYR_TEST_PG", "1")
    assert cw._test_process_detected() is True
    monkeypatch.delenv("ZEPHYR_TEST_PG", raising=False)
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "tests/data/data/db/test_ch_write_guard.py::x (call)")
    assert cw._test_process_detected() is True
