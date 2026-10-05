# [MODULE] tests.zephyr.data.test_divergence_stats
# [DOMAIN] D_DATA
"""多源分歧率统计器测试（#423 形态锁第二段供数件）。

钉住的判据：
  ①四字段行（日期/表/分歧类型/计数）+分母 total_symbols 随行；
  ②details 精确归并优先，details 空走差值推算且 derived=true 如实标注；
  ③upsert=同键覆盖（重测非增量），异键追加；
  ④入参非法/落盘失败 fail-loud（禁静默丢数）。
输出一律 tmp_path（禁写生产 data/——宪法 §9.6）。
"""
# [TTL] permanent
# [STARTUP] manual

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from zephyr.data import divergence_stats as dvs
from zephyr.data.cross_source_validator import ValidationReport

REF = date(2026, 9, 28)
TABLE = "c1_market.market_tick"


def _report(
    *,
    details: list[dict] | None = None,
    total_symbols: int = 10,
    passed: int = 0,
    warnings: int = 0,
    failures: int = 0,
    missing_backup: int = 0,
    missing_primary: int = 0,
) -> ValidationReport:
    r = ValidationReport(check_time=__import__("datetime").datetime(2026, 9, 28, 23, 15))
    r.total_symbols = total_symbols
    r.passed = passed
    r.warnings = warnings
    r.failures = failures
    r.missing_in_backup = missing_backup
    r.missing_in_primary = missing_primary
    if details is not None:
        r.details = details
    return r


def _read_rows(path: Path) -> list[dict]:
    return [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def test_exact_counts_from_details(tmp_path: Path) -> None:
    """details 逐条归并：price fail×2、volume warn×1、missing×各 1——精确计数非推算。"""
    details = [
        {"symbol": "a", "metric": "price", "status": "fail", "deviation": 0.01},
        {"symbol": "b", "metric": "price", "status": "fail", "deviation": 0.02},
        {"symbol": "c", "metric": "price", "status": "pass", "deviation": 0.0},
        {"symbol": "d", "metric": "volume", "status": "warn", "deviation": 0.06},
        {"symbol": "e", "metric": "volume", "status": "pass", "deviation": 0.0},
    ]
    report = _report(details=details, total_symbols=8, failures=3, warnings=2, missing_backup=1, missing_primary=1)
    dvs.record_report_stats(report, stats_path=tmp_path / "stats.jsonl", ref_date=REF, table=TABLE)
    rows = _read_rows(tmp_path / "stats.jsonl")
    by_type = {r["divergence_type"]: r["count"] for r in rows}
    assert by_type == {
        "price_deviation_fail": 2,
        "volume_deviation_warn": 1,
        "missing_in_backup": 1,
        "missing_in_primary": 1,
    }
    for row in rows:
        assert row["date"] == REF.isoformat()
        assert row["table"] == TABLE
        assert row["total_symbols"] == 8
        assert row["derived"] is False
        # 四字段齐备：日期/表/分歧类型/计数（#423 观察供数契约）
        assert {"date", "table", "divergence_type", "count"} <= set(row)


def test_derived_fallback_when_details_empty(tmp_path: Path) -> None:
    """旧版校验器 details 空：差值保守推算 + derived=true 如实标注（禁冒充精读）。"""
    report = _report(details=[], total_symbols=6, failures=3, warnings=2, missing_backup=1, missing_primary=1)
    dvs.record_report_stats(report, stats_path=tmp_path / "stats.jsonl", ref_date=REF, table=TABLE)
    by_type = {r["divergence_type"]: r for r in _read_rows(tmp_path / "stats.jsonl")}
    assert by_type["price_deviation_fail"]["count"] == 2  # 3 failures - 1 missing_in_primary
    assert by_type["volume_deviation_warn"]["count"] == 1  # 2 warnings - 1 missing_in_backup
    assert by_type["price_deviation_fail"]["derived"] is True


def test_upsert_same_key_replaces_not_sums(tmp_path: Path) -> None:
    """同（date,table,type）键覆盖：cross_validation 重跑=同窗重测，禁 sum 双计。"""
    first = _report(details=[{"symbol": "a", "metric": "price", "status": "fail", "deviation": 0.1}], total_symbols=5)
    second = _report(
        details=[
            {"symbol": "a", "metric": "price", "status": "fail", "deviation": 0.1},
            {"symbol": "b", "metric": "price", "status": "fail", "deviation": 0.2},
        ],
        total_symbols=5,
    )
    path = tmp_path / "stats.jsonl"
    dvs.record_report_stats(first, stats_path=path, ref_date=REF, table=TABLE)
    out = dvs.record_report_stats(second, stats_path=path, ref_date=REF, table=TABLE)
    price_rows = [r for r in _read_rows(path) if r["divergence_type"] == "price_deviation_fail"]
    assert len(price_rows) == 1, "同键重复行=双计（观察口径被污染）"
    assert price_rows[0]["count"] == 2
    assert out["appended"] == 0 and out["upserted"] == 4


def test_different_date_appends(tmp_path: Path) -> None:
    path = tmp_path / "stats.jsonl"
    dvs.record_report_stats(_report(details=[]), stats_path=path, ref_date=REF, table=TABLE)
    dvs.record_report_stats(_report(details=[]), stats_path=path, ref_date=date(2026, 9, 29), table=TABLE)
    dates = {r["date"] for r in _read_rows(path)}
    assert dates == {REF.isoformat(), "2026-09-29"}


def test_bad_report_type_fails_loud(tmp_path: Path) -> None:
    with pytest.raises(dvs.DivergenceStatsError):
        dvs.record_report_stats({"total_symbols": 1}, stats_path=tmp_path / "s.jsonl")  # type: ignore[arg-type]


def test_write_failure_fails_loud(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """落盘失败必须可见（禁静默丢观察数）。"""

    def boom(*args, **kwargs):
        raise OSError("disk full（测试注入）")

    monkeypatch.setattr(dvs, "safe_write_text", boom)
    with pytest.raises(dvs.DivergenceStatsError):
        dvs.record_report_stats(_report(details=[]), stats_path=tmp_path / "s.jsonl", ref_date=REF, table=TABLE)


def test_default_table_resolves_from_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    """表名真源=table_registry（禁硬编码表名）。"""
    monkeypatch.setattr(dvs, "_resolve_tick_table", lambda: "c1_market.market_tick_reg")
    rows = dvs.report_to_rows(_report(details=[]), ref_date=REF)
    assert rows and all(r["table"] == "c1_market.market_tick_reg" for r in rows)


def test_corrupt_lines_skipped_not_fatal(tmp_path: Path) -> None:
    """档案坏行跳过不致命（不中断 upsert），好行保留。"""
    path = tmp_path / "stats.jsonl"
    path.write_text("not-json\n", encoding="utf-8")
    dvs.record_report_stats(_report(details=[]), stats_path=path, ref_date=REF, table=TABLE)
    rows = _read_rows(path)
    assert rows and all(r["date"] == REF.isoformat() for r in rows)
