# [BLUEPRINT] MOD-RK-043 | docs/03_modules/_domain_risk/var_data_prefetcher/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-RK-043 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.risk.test_var_data_prefetcher
# [TESTS] src/zephyr/risk/var_data_prefetcher.py
"""MOD-RK-043 单元测试：var_data_prefetcher VaR 数据预取器。

蓝图验收（B13-04254/CAND-RSK-047，A3 D-DATA-44）：
DuckDB 读 Parquet 批量预取（真 duckdb + tmp_path parquet）+ 内存环形缓冲容量
护栏（FIFO 逐出）+ prefetch 命中率/IO 耗时指标 + 缓存语义（键=标的+窗口）。
连接/单调时钟全注入，不触网。
"""

from __future__ import annotations

from decimal import Decimal

import pytest

duckdb = pytest.importorskip("duckdb", reason="duckdb not installed")
pytest.importorskip(
    "zephyr.risk.var_data_prefetcher",
    reason="var_data_prefetcher not importable",
)

from zephyr.risk.var_data_prefetcher import (  # noqa: E402
    VarDataPrefetcher,
    VarPrefetchError,
)


class _FakeClock:
    """确定性单调时钟替身：每次调用前进 0.5 秒。"""

    def __init__(self) -> None:
        self.t = 100.0

    def __call__(self) -> float:
        self.t += 0.5
        return self.t


@pytest.fixture()
def parquet_path(tmp_path):
    path = tmp_path / "returns.parquet"
    conn = duckdb.connect(":memory:")
    conn.execute(
        """
        COPY (
            SELECT * FROM (
                VALUES
                    ('000001', '2026-08-20', 0.010),
                    ('000001', '2026-08-21', -0.020),
                    ('000001', '2026-08-22', 0.030),
                    ('000002', '2026-08-20', 0.005),
                    ('000002', '2026-08-21', 0.007),
                    ('600000', '2026-08-22', -0.011)
            ) AS t(symbol, trade_date, ret)
        ) TO ? (FORMAT PARQUET)
        """,
        [str(path)],
    )
    conn.close()
    return str(path)


@pytest.fixture()
def conn():
    c = duckdb.connect(":memory:")
    yield c
    c.close()


def _prefetcher(conn, parquet_path, **overrides) -> VarDataPrefetcher:
    kwargs = {
        "duckdb_conn": conn,
        "parquet_path": parquet_path,
        "capacity": 8,
        "time_source": _FakeClock(),
    }
    kwargs.update(overrides)
    return VarDataPrefetcher(**kwargs)


# ──────────────────────────────────────────────────────────────────────────────
# 构造 Fail-Closed
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_non_positive_capacity_raises(self, parquet_path) -> None:
        with pytest.raises(VarPrefetchError):
            _prefetcher(None, parquet_path, capacity=0)
        with pytest.raises(VarPrefetchError):
            _prefetcher(None, parquet_path, capacity=-3)

    def test_empty_parquet_path_raises(self, conn) -> None:
        with pytest.raises(VarPrefetchError):
            _prefetcher(conn, "")


# ──────────────────────────────────────────────────────────────────────────────
# 批量预取（真 duckdb + tmp parquet）
# ──────────────────────────────────────────────────────────────────────────────


class TestPrefetch:
    def test_conn_not_injected_raises(self, parquet_path) -> None:
        p = _prefetcher(None, parquet_path)
        with pytest.raises(VarPrefetchError):
            p.prefetch(["000001"], 30)

    def test_empty_symbols_raises(self, conn, parquet_path) -> None:
        p = _prefetcher(conn, parquet_path)
        with pytest.raises(VarPrefetchError):
            p.prefetch([], 30)
        with pytest.raises(VarPrefetchError):
            p.prefetch(["", ""], 30)

    def test_non_positive_window_raises(self, conn, parquet_path) -> None:
        p = _prefetcher(conn, parquet_path)
        with pytest.raises(VarPrefetchError):
            p.prefetch(["000001"], 0)

    def test_prefetch_loads_sorted_series(self, conn, parquet_path) -> None:
        p = _prefetcher(conn, parquet_path)
        report = p.prefetch(["000001", "000002"], 30)
        assert report.symbols_loaded == 2
        assert report.rows_loaded == 5
        assert report.evicted == 0
        # (symbol, trade_date) 排序确定性
        assert p.get_returns("000001", 3) == (
            Decimal("0.01"),
            Decimal("-0.02"),
            Decimal("0.03"),
        )
        assert p.get_returns("000002", 2) == (Decimal("0.005"), Decimal("0.007"))

    def test_prefetch_window_tail_trim(self, conn, parquet_path) -> None:
        p = _prefetcher(conn, parquet_path)
        p.prefetch(["000001"], 2)
        # 仅保留最近 2 行
        assert p.get_returns("000001", 2) == (Decimal("-0.02"), Decimal("0.03"))

    def test_missing_parquet_file_wrapped(self, conn, tmp_path) -> None:
        p = _prefetcher(conn, str(tmp_path / "ghost.parquet"))
        with pytest.raises(VarPrefetchError):
            p.prefetch(["000001"], 30)

    def test_io_metrics_accumulate(self, conn, parquet_path) -> None:
        clock = _FakeClock()
        p = _prefetcher(conn, parquet_path, time_source=clock)
        p.prefetch(["000001"], 30)
        p.prefetch(["000002"], 30)
        m = p.metrics()
        assert m.io_calls == 2
        assert m.io_seconds == pytest.approx(1.0)  # 假时钟每次 0.5s × 2
        assert m.buffered_symbols == 2


# ──────────────────────────────────────────────────────────────────────────────
# 环形缓冲容量护栏（FIFO 逐出）
# ──────────────────────────────────────────────────────────────────────────────


class TestRingBufferGuard:
    def test_capacity_eviction_fifo(self, conn, parquet_path) -> None:
        p = _prefetcher(conn, parquet_path, capacity=2)
        report = p.prefetch(["000001", "000002", "600000"], 30)
        assert report.evicted == 1
        assert not p.contains("000001")  # 最旧逐出
        assert p.contains("000002")
        assert p.contains("600000")
        assert p.metrics().evictions == 1

    def test_re_prefetch_refreshes_position(self, conn, parquet_path) -> None:
        p = _prefetcher(conn, parquet_path, capacity=2)
        p.prefetch(["000001"], 30)
        p.prefetch(["000002"], 30)
        p.prefetch(["000001"], 30)  # 刷新位置
        p.prefetch(["600000"], 30)  # 逐出 000002 而非 000001
        assert p.contains("000001")
        assert not p.contains("000002")

    def test_hit_refreshes_recency(self, conn, parquet_path) -> None:
        p = _prefetcher(conn, parquet_path, capacity=2)
        p.prefetch(["000001", "000002"], 30)
        p.get_returns("000001", 1)  # 命中刷新
        p.prefetch(["600000"], 30)  # 逐出 000002
        assert p.contains("000001")
        assert not p.contains("000002")


# ──────────────────────────────────────────────────────────────────────────────
# 缓存语义 + 命中率指标
# ──────────────────────────────────────────────────────────────────────────────


class TestCacheSemantics:
    def test_hit_and_miss_counting(self, conn, parquet_path) -> None:
        p = _prefetcher(conn, parquet_path)
        p.prefetch(["000001"], 30)
        assert p.get_returns("000001", 2) is not None
        assert p.get_returns("ghost", 2) is None
        m = p.metrics()
        assert m.hits == 1
        assert m.misses == 1
        assert m.hit_rate == pytest.approx(0.5)

    def test_insufficient_window_is_miss(self, conn, parquet_path) -> None:
        p = _prefetcher(conn, parquet_path)
        p.prefetch(["000001"], 30)  # 缓冲 3 行
        assert p.get_returns("000001", 10) is None
        assert p.metrics().misses == 1

    def test_get_returns_invalid_input_raises(self, conn, parquet_path) -> None:
        p = _prefetcher(conn, parquet_path)
        with pytest.raises(VarPrefetchError):
            p.get_returns("", 1)
        with pytest.raises(VarPrefetchError):
            p.get_returns("000001", 0)

    def test_clear_keeps_metrics(self, conn, parquet_path) -> None:
        p = _prefetcher(conn, parquet_path)
        p.prefetch(["000001"], 30)
        p.get_returns("000001", 1)
        p.clear()
        m = p.metrics()
        assert m.buffered_symbols == 0
        assert m.io_calls == 1
        assert m.hits == 1

    def test_hit_rate_zero_when_no_query(self, conn, parquet_path) -> None:
        p = _prefetcher(conn, parquet_path)
        assert p.metrics().hit_rate == 0.0

    def test_determinism_same_input_same_output(self, conn, parquet_path) -> None:
        p1 = _prefetcher(conn, parquet_path)
        p2 = _prefetcher(conn, parquet_path)
        p1.prefetch(["000001", "000002"], 30)
        p2.prefetch(["000001", "000002"], 30)
        assert p1.get_returns("000001", 3) == p2.get_returns("000001", 3)
