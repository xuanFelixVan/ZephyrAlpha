# [BLUEPRINT] MOD-L00-006 | docs/03_modules/_domain_data/wal_codec_blueprint.md
# [TTL] permanent
"""数据归一化器（MOD-L00-006 data/normalizers/）单元测试——抽象契约 + OhlcvNormalizer 具体实现。"""

from __future__ import annotations

import pytest

from zephyr.data.normalizers import DataNormalizer, OhlcvNormalizer


def _rec(**kw) -> dict:
    base = {
        "symbol": "600519",
        "trade_date": "2026-08-21",
        "open": 1700.0,
        "high": 1715.0,
        "low": 1690.0,
        "close": 1710.0,
        "volume": 12345.0,
    }
    base.update(kw)
    return base


class TestOhlcvNormalize:
    def test_happy_path_sorted(self):
        n = OhlcvNormalizer()
        out = n.normalize([_rec(symbol="B", trade_date="2026-08-21"), _rec(symbol="A", trade_date="2026-08-20")])
        assert out.dropped == 0
        assert [r["symbol"] for r in out.records] == ["A", "B"]  # (symbol, date) 排序

    def test_column_aliases_cn_and_variants(self):
        n = OhlcvNormalizer()
        rec = {
            "代码": "000001",
            "日期": "20260821",
            "开盘": "11.0",
            "最高": "11.5",
            "最低": "10.9",
            "收盘": "11.4",
            "成交量": "999",
            "成交额": "1e8",
        }
        out = n.normalize([rec])
        assert out.dropped == 0
        r = out.records[0]
        assert r["symbol"] == "000001"
        assert r["trade_date"] == "2026-08-21"  # YYYYMMDD → ISO
        assert r["close"] == pytest.approx(11.4)
        assert r["amount"] == pytest.approx(1e8)

    def test_missing_required_dropped_with_issue(self):
        n = OhlcvNormalizer()
        bad = _rec()
        del bad["close"]
        out = n.normalize([bad, _rec()])
        assert out.dropped == 1
        assert len(out.records) == 1
        assert any("必需字段缺失" in i for i in out.issues)

    @pytest.mark.parametrize(
        "bad_kw",
        [
            {"close": -1.0},  # 负价
            {"volume": -5.0},  # 负量
            {"high": 100.0, "low": 200.0},  # high<low
            {"trade_date": "not-a-date"},  # 日期不可解析
            {"close": "abc"},  # 类型不可转
        ],
    )
    def test_bad_records_dropped(self, bad_kw):
        n = OhlcvNormalizer()
        out = n.normalize([_rec(**bad_kw), _rec()])
        assert out.dropped == 1
        assert len(out.records) == 1
        assert len(out.issues) == 1

    def test_dedup_keep_last(self):
        """同 (symbol, trade_date) 后者覆盖先到（修正记录）。"""
        n = OhlcvNormalizer()
        out = n.normalize([_rec(close=1700.0), _rec(close=1705.0)])
        assert len(out.records) == 1
        assert out.records[0]["close"] == pytest.approx(1705.0)
        assert out.dropped == 1
        assert any("dedup" in i for i in out.issues)

    def test_idempotent(self):
        n = OhlcvNormalizer()
        recs = [_rec(), _rec(symbol="A")]
        first = n.normalize(recs)
        second = n.normalize([dict(r) for r in first.records])
        assert first.records == second.records

    def test_input_not_mutated(self):
        n = OhlcvNormalizer()
        recs = [_rec()]
        snapshot = [dict(r) for r in recs]
        n.normalize(recs)
        assert recs == snapshot

    def test_empty(self):
        out = OhlcvNormalizer().normalize([])
        assert out.records == ()
        assert out.dropped == 0


class TestAbstraction:
    def test_ohlcv_is_data_normalizer(self):
        assert isinstance(OhlcvNormalizer(), DataNormalizer)
        assert OhlcvNormalizer().name == "ohlcv"

    def test_abc_not_instantiable(self):
        with pytest.raises(TypeError):
            DataNormalizer()  # type: ignore[abstract]
