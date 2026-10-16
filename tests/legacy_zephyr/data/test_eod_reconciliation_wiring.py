# [MODULE] tests.zephyr.data.test_eod_reconciliation_wiring
# [DOMAIN] D_DATA
# [DEPENDENCIES] pytest; zephyr.data.scheduler; zephyr.trading.recon_runner
# [CONSUMERS] DSC-15/D13-29 断链接线守卫（eod_reconciliation 槽 skip 路径必须留 run 台账——跑没跑可证）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] monkeypatch 全替身（零真 QMT/零真 CH/不写真 governance.db）；run 台账落 tmp 库
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest 断言失败即红
# [TESTS] self
# [A_module] module_id=TEST-MOD-L00-004-TEST_EOD_RECONCILIATION_WIRING | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""DSC-15/D13-29 接线测试：eod_reconciliation 特殊槽 skip/error 路径入 run 台账（三态可分）。

SDSC-15 fail 收口件：15:40 槽"无任务→APScheduler success"假通道已由 2026-10-07
分派分支接线修复；本测试守 skip/WARN 路径的 run 台账留痕（skipped_no_artifact /
skipped_broker_error / error）——没跑出声不蒸发，跑没跑当日可查。
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
import yaml

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT / "src"))

from zephyr.data import scheduler as sched  # noqa: E402
from zephyr.trading import recon_runner as rr  # noqa: E402


class _FakeScheduler:
    def __init__(self):
        self._alerter = MagicMock()


@pytest.fixture()
def ledger_db(tmp_path, monkeypatch):
    """run 台账 SSoT 重定向到 tmp 库（record_recon_run db_path=None 落此处）。"""
    db = tmp_path / "governance_test.db"
    monkeypatch.setattr(rr, "DB_PATH", db)
    return db


def _read_run_rows(db: Path) -> list[sqlite3.Row]:
    try:
        conn = sqlite3.connect(str(db))
    except sqlite3.OperationalError:
        return []
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute("SELECT * FROM reconciliation_runs ORDER BY id").fetchall()
    except sqlite3.OperationalError:
        return []
    finally:
        conn.close()


def test_no_artifact_skips_with_warn_and_ledger(ledger_db, monkeypatch):
    """无当日回测产物：WARN 出声不硬跑 + run 台账 skipped_no_artifact 入账（不蒸发）。"""
    monkeypatch.setattr(sched, "_resolve_eod_recon_run_id", lambda td: (None, None))
    fake = _FakeScheduler()
    out = sched._run_special_schedule(fake, "eod_reconciliation")
    assert out == {"eod_reconciliation": False}
    fake._alerter.notify.assert_called_once()
    assert fake._alerter.notify.call_args.kwargs["level"] == "WARN"
    rows = _read_run_rows(ledger_db)
    assert len(rows) == 1
    assert rows[0]["verdict"] == "skipped_no_artifact"
    assert rows[0]["run_id"] is None


def test_broker_failure_ledgers_skipped_broker_error(ledger_db, monkeypatch):
    """柜台侧不可达：ERROR 告警 + run 台账 skipped_broker_error 入账。"""
    monkeypatch.setattr(sched, "_resolve_eod_recon_run_id", lambda td: ("bt-x1", "2026-10-15"))

    class _BoomBroker:
        def __init__(self, *a, **k):
            raise RuntimeError("qmt down")

    monkeypatch.setattr("zephyr.ex_core.adapters.miniqmt_broker.MiniQmtBroker", _BoomBroker)
    fake = _FakeScheduler()
    out = sched._run_special_schedule(fake, "eod_reconciliation")
    assert out == {"eod_reconciliation": False}
    fake._alerter.notify.assert_called_once()
    assert fake._alerter.notify.call_args.kwargs["level"] == "ERROR"
    rows = _read_run_rows(ledger_db)
    assert rows[0]["verdict"] == "skipped_broker_error"
    assert rows[0]["run_id"] == "bt-x1"
    assert "qmt down" in (rows[0]["detail"] or "")


def test_run_exception_ledgers_error(ledger_db, monkeypatch):
    """对账执行异常：ERROR 告警 + run 台账 error 入账（跑砸了也有账）。"""
    monkeypatch.setattr(sched, "_resolve_eod_recon_run_id", lambda td: ("bt-x1", "2026-10-15"))

    class _OkBroker:
        def __init__(self, *a, **k):
            pass

        def connect(self):
            pass

        def disconnect(self):
            pass

    monkeypatch.setattr("zephyr.ex_core.adapters.miniqmt_broker.MiniQmtBroker", _OkBroker)

    def _boom(**k):
        raise RuntimeError("artifact corrupt")

    monkeypatch.setattr(rr, "run_daily_reconciliation", _boom)
    fake = _FakeScheduler()
    out = sched._run_special_schedule(fake, "eod_reconciliation")
    assert out == {"eod_reconciliation": False}
    rows = _read_run_rows(ledger_db)
    assert rows[0]["verdict"] == "error"
    assert "artifact corrupt" in (rows[0]["detail"] or "")


def test_success_path_green_without_alert(ledger_db, monkeypatch):
    """全绿路径：返回 True，C 类空时零告警（ran 行由 recon_runner 本体落，recon_runner 测试覆盖）。"""
    monkeypatch.setattr(sched, "_resolve_eod_recon_run_id", lambda td: ("bt-x1", "2026-10-15"))

    class _OkBroker:
        def __init__(self, *a, **k):
            pass

        def connect(self):
            pass

        def disconnect(self):
            pass

    monkeypatch.setattr("zephyr.ex_core.adapters.miniqmt_broker.MiniQmtBroker", _OkBroker)
    monkeypatch.setattr(
        rr,
        "run_daily_reconciliation",
        lambda **k: SimpleNamespace(c_class_items=(), rows_written=0, db_error=None),
    )
    fake = _FakeScheduler()
    out = sched._run_special_schedule(fake, "eod_reconciliation")
    assert out == {"eod_reconciliation": True}
    fake._alerter.notify.assert_not_called()


def test_c_class_items_alerts_error(ledger_db, monkeypatch):
    """C 类缺失成交：当日必告警（56号文 C10 契约）。"""
    monkeypatch.setattr(sched, "_resolve_eod_recon_run_id", lambda td: ("bt-x1", "2026-10-15"))

    class _OkBroker:
        def __init__(self, *a, **k):
            pass

        def connect(self):
            pass

        def disconnect(self):
            pass

    monkeypatch.setattr("zephyr.ex_core.adapters.miniqmt_broker.MiniQmtBroker", _OkBroker)
    c_item = SimpleNamespace(symbol="600000.SH", drift_type="missing_in_broker", detail="回测有实盘无")
    monkeypatch.setattr(
        rr,
        "run_daily_reconciliation",
        lambda **k: SimpleNamespace(c_class_items=(c_item,), rows_written=1, db_error=None),
    )
    fake = _FakeScheduler()
    out = sched._run_special_schedule(fake, "eod_reconciliation")
    assert out == {"eod_reconciliation": True}  # C 类告警不翻转槽结论（契约=告警非失败）
    fake._alerter.notify.assert_called_once()
    assert "C 类缺失成交" in fake._alerter.notify.call_args.args[1]
    assert fake._alerter.notify.call_args.kwargs["level"] == "ERROR"


def test_slot_registered_in_schedule_yaml():
    doc = yaml.safe_load((sched._DEFAULT_CONFIG_DIR / "schedule.yaml").read_text(encoding="utf-8"))
    slot = doc["schedules"]["eod_reconciliation"]
    assert slot["cron"] == "40 15 * * 0-4"
    assert slot["max_instances"] == 1


def test_slot_is_trading_day_guarded():
    from zephyr.data.trading_calendar import TRADING_DAY_GUARDED_SCHEDULES

    assert "eod_reconciliation" in TRADING_DAY_GUARDED_SCHEDULES
