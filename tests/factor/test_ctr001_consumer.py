# [A_test] module_id: MOD-GOV_ctr001_consumer | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §test
# [MODULE] tests.factor.test_ctr001_consumer
# [DOMAIN] D_FACTOR
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/factor/test_ctr001_consumer.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""CTR-001 NormalizedMarketData 消费者测试——converter + filter_quality。

覆盖：
- to_dataframe: 空输入 / Decimal→float / MultiIndex / 排序
- filter_quality: 悬停过滤 / 质量分过滤 / 自定义阈值 / 无列降级
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pandas as pd
import pytest

converter = pytest.importorskip("zephyr.factor.core.ctr001_consumer.converter")
from zephyr.shared.contracts.market_data import NormalizedMarketData  # noqa: E402

to_dataframe = converter.to_dataframe
filter_quality = converter.filter_quality


def _make_record(
    symbol: str = "600519.SH",
    timestamp: datetime | None = None,
    close: str = "100.5",
    quality_score: float = 1.0,
    is_suspended: bool = False,
) -> NormalizedMarketData:
    """构造单条 NormalizedMarketData（合成数据）。"""
    if timestamp is None:
        timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return NormalizedMarketData(
        symbol=symbol,
        timestamp=timestamp,
        open=Decimal("100.0"),
        high=Decimal("101.0"),
        low=Decimal("99.0"),
        close=Decimal(close),
        volume=Decimal("1000"),
        amount=Decimal("100000"),
        adj_factor=Decimal("1.0"),
        data_source="test",
        idempotency_key=f"{symbol}:{timestamp:%Y%m%d}",
        quality_score=quality_score,
        is_suspended=is_suspended,
    )


class TestToDataframe:
    def test_empty_list(self):
        df = to_dataframe([])
        assert df.empty

    def test_none_input(self):
        df = to_dataframe(None)
        assert df.empty

    def test_single_record(self):
        df = to_dataframe([_make_record()])
        assert len(df) == 1
        assert list(df.index.names) == ["symbol", "timestamp"]

    def test_multiple_records_multiindex(self):
        recs = [
            _make_record(symbol="000001.SZ", timestamp=datetime(2026, 1, 2, tzinfo=timezone.utc)),
            _make_record(symbol="600519.SH", timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc)),
        ]
        df = to_dataframe(recs)
        assert len(df) == 2
        assert df.index.names == ["symbol", "timestamp"]

    def test_decimal_to_float(self):
        df = to_dataframe([_make_record(close="100.5")])
        assert df["close"].dtype == float
        assert df["close"].iloc[0] == 100.5
        assert isinstance(df["close"].iloc[0], float)

    def test_numeric_columns_present(self):
        df = to_dataframe([_make_record()])
        for col in ("open", "high", "low", "close", "volume", "amount", "adj_factor"):
            assert col in df.columns
        for col in ("quality_score", "is_suspended"):
            assert col in df.columns

    def test_sorted_by_index(self):
        recs = [
            _make_record(symbol="600519.SH", timestamp=datetime(2026, 1, 3, tzinfo=timezone.utc)),
            _make_record(symbol="600519.SH", timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc)),
            _make_record(symbol="000001.SZ", timestamp=datetime(2026, 1, 2, tzinfo=timezone.utc)),
        ]
        df = to_dataframe(recs)
        symbols = [idx[0] for idx in df.index]
        assert symbols == sorted(symbols)

    def test_preserves_symbol_and_timestamp(self):
        ts = datetime(2026, 6, 15, 9, 30, tzinfo=timezone.utc)
        df = to_dataframe([_make_record(symbol="000001.SZ", timestamp=ts)])
        assert df.index[0][0] == "000001.SZ"
        assert df.index[0][1] == ts


class TestFilterQuality:
    def test_empty_dataframe(self):
        assert filter_quality(pd.DataFrame()).empty

    def test_filters_suspended(self):
        df = to_dataframe(
            [
                _make_record(symbol="A.SH", is_suspended=False),
                _make_record(symbol="B.SH", is_suspended=True),
            ]
        )
        filtered = filter_quality(df)
        assert "B.SH" not in [idx[0] for idx in filtered.index]
        assert "A.SH" in [idx[0] for idx in filtered.index]

    def test_filters_low_quality(self):
        df = to_dataframe(
            [
                _make_record(symbol="A.SH", quality_score=0.9),
                _make_record(symbol="B.SH", quality_score=0.5),
            ]
        )
        filtered = filter_quality(df, min_score=0.7)
        assert "B.SH" not in [idx[0] for idx in filtered.index]

    def test_custom_min_score(self):
        df = to_dataframe(
            [
                _make_record(symbol="A.SH", quality_score=0.8),
                _make_record(symbol="B.SH", quality_score=0.6),
            ]
        )
        # 阈值 0.5 时两条都通过
        assert len(filter_quality(df, min_score=0.5)) == 2
        # 阈值 0.7 时只剩 A
        assert len(filter_quality(df, min_score=0.7)) == 1

    def test_no_quality_columns_returns_as_is(self):
        df = pd.DataFrame({"close": [1.0, 2.0]})
        df.index = pd.MultiIndex.from_tuples([("A.SH", 1), ("B.SH", 2)], names=["symbol", "timestamp"])
        result = filter_quality(df)
        assert len(result) == 2

    def test_high_quality_passes(self):
        df = to_dataframe([_make_record(quality_score=1.0, is_suspended=False)])
        assert len(filter_quality(df)) == 1
