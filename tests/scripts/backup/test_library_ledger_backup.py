# [BLUEPRINT] MOD-INF-043 | docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/blueprint.md | §3
# [MODULE] tests.scripts.backup.test_library_ledger_backup
# [DOMAIN] D_INFRASTRUCTURE
# [DEPENDENCIES] scripts.backup.library_ledger_backup
# [CONSUMERS] pytest suite
# [STARTUP] imported
# [MATURITY] production
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] assertion failure only
# [TESTS] self
# [A_module] module_id=MOD-INF-043 | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_library_ledger_backup.py — 备份/演练全链测试（fake conn + tmp_path，零生产路径）。"""

from __future__ import annotations

import gzip
import io
import json
from datetime import datetime
from pathlib import Path

import pytest

from scripts.backup.library_ledger_backup import (
    LIB_TABLES,
    run_backup,
    run_drill,
    run_status,
)


class _FakeCursor:
    """模拟 psycopg2 cursor：copy_expert 写出两行假数据 CSV。"""

    def __init__(self, rows: dict[str, list[tuple]]):
        self._rows = rows
        self.rowcount = 0

    def copy_expert(self, sql: str, fh: io.TextIOBase) -> None:
        for table in LIB_TABLES:
            if f"COPY {table}" in sql:
                cols = {"lib_assets": "asset_id,kind,status,home", "lib_events": "event_id,asset_id,action"}[table]
                fh.write(cols + "\n")
                for row in self._rows[table]:
                    fh.write(",".join(str(c) for c in row) + "\n")
                self.rowcount = len(self._rows[table])
                return
        raise AssertionError(f"unexpected COPY sql: {sql}")


class _FakeConn:
    def __init__(self, rows: dict[str, list[tuple]]):
        self._rows = rows

    def cursor(self) -> _FakeCursor:
        return _FakeCursor(self._rows)

    def close(self) -> None:
        pass


@pytest.fixture()
def fake_env(tmp_path: Path):
    rows = {
        "lib_assets": [("TBL:ch:c1.market.kline", "table", "active", "ch:c1.market.kline")],
        "lib_events": [("EVT-1", "TBL:ch:c1.market.kline", "register")],
    }
    return rows, tmp_path / "primary", tmp_path / "mirror"


def test_backup_writes_dual_chain_and_manifest(fake_env) -> None:
    rows, primary, mirror = fake_env
    now = datetime(2026, 9, 24, 3, 30)
    manifest = run_backup(
        conn_factory=lambda: _FakeConn(rows),
        primary_root=primary,
        mirror_root=mirror,
        now=now,
    )
    assert manifest["tables"]["lib_assets"]["rows"] == 1
    assert manifest["tables"]["lib_events"]["rows"] == 1
    assert manifest["degraded"] == []
    for root in (primary, mirror):
        day_dir = root / "20260924"
        assert (day_dir / "lib_assets.csv.gz").exists()
        assert (day_dir / "lib_events.csv.gz").exists()
        assert (day_dir / "manifest.json").exists()
    with gzip.open(day_dir / "lib_assets.csv.gz", "rt", encoding="utf-8") as fh:
        assert "TBL:ch:c1.market.kline" in fh.read()


def test_backup_mirror_failure_degrades_not_blocks(fake_env) -> None:
    rows, primary, _ = fake_env
    mirror = Path("Q:/nonexistent_drive/lib")
    manifest = run_backup(
        conn_factory=lambda: _FakeConn(rows),
        primary_root=primary,
        mirror_root=mirror,
    )
    assert manifest["degraded"], "mirror failure must be recorded"
    assert (primary / sorted(p.name for p in primary.iterdir())[0] / "manifest.json").exists()


def test_drill_passes_on_fresh_backup(fake_env) -> None:
    rows, primary, _ = fake_env
    run_backup(conn_factory=lambda: _FakeConn(rows), primary_root=primary, mirror_root=fake_env[2])
    report = run_drill(primary_root=primary, report_root=fake_env[1].parent / "reports")
    assert report["verdict"] == "PASS"
    assert len(report["checks"]) == 6  # 2 tables x (sha+rows+sample); manifest check only on missing


def test_drill_fails_when_row_count_drifts(fake_env, tmp_path: Path) -> None:
    rows, primary, _ = fake_env
    day_dir = primary / "20260924"
    now = datetime(2026, 9, 24, 3, 30)
    run_backup(conn_factory=lambda: _FakeConn(rows), primary_root=primary, mirror_root=fake_env[2], now=now)
    manifest = json.loads((day_dir / "manifest.json").read_text(encoding="utf-8"))
    manifest["tables"]["lib_assets"]["rows"] = 999
    (day_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(SystemExit):
        run_drill(primary_root=primary, report_root=tmp_path / "reports")


def test_status_reports_latest(fake_env) -> None:
    rows, primary, mirror = fake_env
    run_backup(conn_factory=lambda: _FakeConn(rows), primary_root=primary, mirror_root=mirror)
    out = run_status(primary_root=primary, mirror_root=mirror)
    assert out["latest_day"] is not None
    assert out["latest_tables"]["lib_assets"] == 1


def test_monthly_pin_survives_prune(fake_env) -> None:
    rows, primary, _ = fake_env
    now = datetime(2026, 9, 24, 3, 30)
    run_backup(conn_factory=lambda: _FakeConn(rows), primary_root=primary, mirror_root=fake_env[2], now=now)
    pin = primary / "20260901"
    pin.mkdir(parents=True)
    old = primary / "20260615"
    old.mkdir(parents=True)
    from scripts.backup.library_ledger_backup import _prune_old_backups

    _prune_old_backups(primary)
    assert pin.exists(), "monthly pin must survive"
    assert not old.exists(), "stale day beyond retention must go"
