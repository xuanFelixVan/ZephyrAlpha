# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] tests.factor.test_offline_store
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.offline_store; pyarrow; duckdb
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] production
# [INVARIANTS] tmp_path 真实 Parquet 写入 + duckdb 真实读取；不触网不触生产库；7列Schema fail-closed
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=7列校验/分区映射/幂等写/DuckDB读取/去重取最新逻辑缺陷
# [TESTS] 本文件
# [TTL] permanent
"""OfflineStore 单元测试（CAND-FAC-015 / B13-04144，离线存储 Offline Store）。

覆盖（min_build_spec）：
- 7 列 Schema 校验（trade_date/symbol/factor_name/value/version/computed_at/quality_flag，fail-closed）
- 三目录分区映射（daily/intraday 按日、snapshots 按月）
- Parquet 分区落盘（内容寻址批文件名，同批重写幂等）
- DuckDB 读取 API（因子/日期区间/质量标记过滤；默认排除 quarantined）
- 重算去重：同 (trade_date,symbol,factor_name,version) 取 computed_at 最新
"""

from __future__ import annotations

import duckdb
import pytest

from zephyr.factor.offline_store import (
    OfflineStore,
    partition_path,
    validate_rows,
)


def _row(
    trade_date: str = "2026-08-25",
    symbol: str = "sh.600000",
    factor_name: str = "momentum_20d",
    value: float | None = 0.12,
    version: str = "1.0.0",
    computed_at: str = "2026-08-25T15:30:00+00:00",
    quality_flag: str = "ok",
) -> dict:
    return {
        "trade_date": trade_date,
        "symbol": symbol,
        "factor_name": factor_name,
        "value": value,
        "version": version,
        "computed_at": computed_at,
        "quality_flag": quality_flag,
    }


# ---------------------------------------------------------------- 7 列校验


def test_validate_rows_happy_path() -> None:
    rows = validate_rows([_row(), _row(value=None)])
    assert len(rows) == 2
    assert rows[0].factor_name == "momentum_20d"
    assert rows[1].value is None  # 预热期 NULL 原貌


def test_validate_rows_missing_column_raises() -> None:
    bad = _row()
    del bad["quality_flag"]
    with pytest.raises(ValueError, match="缺列"):
        validate_rows([bad])


def test_validate_rows_bad_quality_flag_raises() -> None:
    with pytest.raises(ValueError, match="quality_flag"):
        validate_rows([_row(quality_flag="mystery")])


def test_validate_rows_bad_trade_date_raises() -> None:
    with pytest.raises(ValueError, match="trade_date"):
        validate_rows([_row(trade_date="2026/08/25")])


def test_validate_rows_bad_computed_at_raises() -> None:
    with pytest.raises(ValueError, match="computed_at"):
        validate_rows([_row(computed_at="not-a-timestamp")])


def test_validate_rows_empty_factor_name_raises() -> None:
    with pytest.raises(ValueError):
        validate_rows([_row(factor_name="")])


# ---------------------------------------------------------------- 分区映射


def test_partition_path_daily_and_intraday_by_day() -> None:
    assert partition_path("daily", "2026-08-25") == "trade_date=2026-08-25"
    assert partition_path("intraday", "2026-08-25") == "trade_date=2026-08-25"


def test_partition_path_snapshots_by_month() -> None:
    assert partition_path("snapshots", "2026-08-25") == "year=2026/month=08"


def test_partition_path_invalid_layer_raises() -> None:
    with pytest.raises(ValueError, match="layer"):
        partition_path("weekly", "2026-08-25")


# ---------------------------------------------------------------- 写入/读取闭环


def test_write_then_read_roundtrip(tmp_path) -> None:
    store = OfflineStore(tmp_path)
    batch = [_row(), _row(symbol="sz.000001", value=-0.03), _row(factor_name="rsi_14", value=61.5)]
    receipt = store.write(batch, "daily")
    assert receipt.rows_written == 3
    assert receipt.files_written == 1
    assert receipt.layer == "daily"
    out = store.read("daily", conn=duckdb.connect(":memory:"))
    assert len(out) == 3
    assert {r["factor_name"] for r in out} == {"momentum_20d", "rsi_14"}
    first = next(r for r in out if r["symbol"] == "sz.000001")
    assert first["value"] == pytest.approx(-0.03)
    assert first["version"] == "1.0.0"
    assert first["quality_flag"] == "ok"
    assert first["computed_at"] == "2026-08-25T15:30:00+00:00"


def test_write_same_batch_idempotent(tmp_path) -> None:
    store = OfflineStore(tmp_path)
    r1 = store.write([_row()], "daily")
    r2 = store.write([_row()], "daily")
    assert r2.files_written == 0  # 内容寻址：同批重写幂等，零新文件
    assert r1.partition_files == r2.partition_files
    out = store.read("daily", conn=duckdb.connect(":memory:"))
    assert len(out) == 1


def test_write_partitions_split_by_day(tmp_path) -> None:
    store = OfflineStore(tmp_path)
    store.write([_row(trade_date="2026-08-24"), _row(trade_date="2026-08-25")], "daily")
    out = store.read("daily", conn=duckdb.connect(":memory:"))
    assert {r["trade_date"] for r in out} == {"2026-08-24", "2026-08-25"}


def test_snapshots_month_partition(tmp_path) -> None:
    store = OfflineStore(tmp_path)
    store.write([_row(trade_date="2026-08-25"), _row(trade_date="2026-08-31")], "snapshots")
    out = store.read("snapshots", conn=duckdb.connect(":memory:"))
    assert len(out) == 2
    assert (tmp_path / "snapshots" / "year=2026" / "month=08").is_dir()


def test_read_filters_factor_and_date_range(tmp_path) -> None:
    store = OfflineStore(tmp_path)
    store.write(
        [
            _row(trade_date="2026-08-22", factor_name="a"),
            _row(trade_date="2026-08-24", factor_name="a"),
            _row(trade_date="2026-08-25", factor_name="b"),
        ],
        "daily",
    )
    conn = duckdb.connect(":memory:")
    out = store.read("daily", conn=conn, factor_names=["a"], start="2026-08-23", end="2026-08-25")
    assert len(out) == 1
    assert out[0]["trade_date"] == "2026-08-24"


def test_read_default_excludes_quarantined_override_includes(tmp_path) -> None:
    store = OfflineStore(tmp_path)
    store.write([_row(factor_name="good"), _row(factor_name="bad", quality_flag="quarantined")], "daily")
    conn = duckdb.connect(":memory:")
    default_out = store.read("daily", conn=conn)
    assert {r["factor_name"] for r in default_out} == {"good"}
    all_out = store.read("daily", conn=conn, quality=("ok", "degraded", "quarantined"))
    assert {r["factor_name"] for r in all_out} == {"good", "bad"}


def test_read_dedup_keeps_latest_computed_at(tmp_path) -> None:
    store = OfflineStore(tmp_path)
    store.write([_row(value=0.10, computed_at="2026-08-25T15:30:00+00:00")], "daily")
    store.write([_row(value=0.99, computed_at="2026-08-25T16:45:00+00:00")], "daily")
    out = store.read("daily", conn=duckdb.connect(":memory:"))
    assert len(out) == 1
    assert out[0]["value"] == pytest.approx(0.99)  # 同键重算取 computed_at 最新


def test_read_empty_store_returns_empty(tmp_path) -> None:
    store = OfflineStore(tmp_path)
    assert store.read("daily", conn=duckdb.connect(":memory:")) == []


def test_write_invalid_layer_raises(tmp_path) -> None:
    store = OfflineStore(tmp_path)
    with pytest.raises(ValueError):
        store.write([_row()], "weekly")


def test_write_empty_batch_zero(tmp_path) -> None:
    store = OfflineStore(tmp_path)
    receipt = store.write([], "daily")
    assert receipt.rows_written == 0
    assert receipt.files_written == 0
