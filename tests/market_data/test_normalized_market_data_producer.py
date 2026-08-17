# [A_test] module_id: MOD-GOV_normalized_market_data_producer | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-MKT_DATA | docs/03_modules/MOD-MKT_DATA/ | §test
# [MODULE] tests.market_data.test_normalized_market_data_producer
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/market_data/test_normalized_market_data_producer.py
# [TTL] task_bound
"""NormalizedMarketData 生产者测试——producer.load_kline + produce。

覆盖：
- load_kline: 空标的 / mock ch_reader / TSV 解析 / Decimal 转换 / 质量标记映射 / 停牌判定
- produce: 语义别名
- _row_to_record: 单行转换 / 解析失败返回 None
- _format_symbols / _to_decimal / _to_int 辅助函数
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pandas as pd
import pytest

producer = pytest.importorskip("zephyr.market_data.normalized_market_data_producer.producer")
from zephyr.shared.contracts.market_data import NormalizedMarketData  # noqa: E402

load_kline = producer.load_kline
produce = producer.produce
_row_to_record = producer.row_to_record
_format_symbols = producer.format_symbols
_to_decimal = producer.to_decimal
_to_int = producer.to_int
_normalize_symbol = producer.normalize_symbol
_strip_symbol_suffix = producer.strip_symbol_suffix


def _make_tsv(n_days: int = 5, symbols: list[str] | None = None) -> str:
    """构造合成日K TSV（11列：trade_date,symbol,ohlc,volume,amount,adj_factor,data_source,quality_flag）。

    不同标的采用不同基础价，含一条 volume=0 的停牌行。
    """
    if symbols is None:
        symbols = ["600519.SH", "000001.SZ"]
    rows = []
    for sym in symbols:
        base = 100.0 if sym == "600519.SH" else 50.0
        for i in range(n_days):
            date = f"2026-01-{i + 1:02d}"
            close = base + i * 0.5
            volume = 0 if i == 2 else 1000 + i * 10  # 第3天停牌
            qflag = 0 if i == 1 else 1  # 第2天质量异常
            row = "\t".join([
                date, sym,
                str(close - 0.3), str(close + 0.3), str(close - 0.6), str(close),
                str(volume), str(100000 + i * 1000), "1.0", "miniqmt", str(qflag),
            ])
            rows.append(row)
    return "\n".join(rows) + "\n"


class TestFormatSymbols:
    def test_basic(self):
        assert _format_symbols(["A", "B"]) == "'A','B'"

    def test_empty(self):
        assert _format_symbols([]) == ""

    def test_escape_quote(self):
        assert "\\'" in _format_symbols(["A'B"])


class TestToDecimal:
    def test_valid(self):
        assert _to_decimal("100.5") == Decimal("100.5")

    def test_none(self):
        assert _to_decimal(None) is None

    def test_empty(self):
        assert _to_decimal("") is None

    def test_invalid(self):
        assert _to_decimal("abc") is None

    def test_none_string(self):
        assert _to_decimal("None") is None

    def test_clickhouse_null_literal(self):
        # ClickHouse TSV 中 NULL 表示为 \N（adj_factor Nullable 列）
        assert _to_decimal("\\N") is None


class TestToInt:
    def test_valid(self):
        assert _to_int("1") == 1

    def test_none(self):
        assert _to_int(None, default=1) == 1

    def test_empty(self):
        assert _to_int("", default=1) == 1

    def test_invalid(self):
        assert _to_int("abc", default=1) == 1

    def test_default_zero(self):
        assert _to_int("abc", default=0) == 0


class TestRowToRecord:
    def _make_row(self, **overrides) -> pd.Series:
        defaults = {
            "trade_date": pd.Timestamp("2026-01-01"),
            "symbol": "600519.SH",
            "open": "100.0",
            "high": "101.0",
            "low": "99.0",
            "close": "100.5",
            "volume": "1000",
            "amount": "100000",
            "adj_factor": "1.0",
            "data_source": "miniqmt",
            "quality_flag": "1",
        }
        defaults.update(overrides)
        return pd.Series(defaults)

    def test_basic_conversion(self):
        rec = _row_to_record(self._make_row())
        assert rec is not None
        assert rec.symbol == "600519.SH"
        assert rec.close == Decimal("100.5")
        assert rec.open == Decimal("100.0")
        assert rec.volume == Decimal("1000")

    def test_decimal_types(self):
        rec = _row_to_record(self._make_row())
        assert isinstance(rec.close, Decimal)
        assert isinstance(rec.open, Decimal)
        assert isinstance(rec.volume, Decimal)

    def test_timestamp_has_timezone(self):
        rec = _row_to_record(self._make_row())
        assert rec.timestamp.tzinfo is not None

    def test_quality_flag_to_score_pass(self):
        rec = _row_to_record(self._make_row(quality_flag="1"))
        assert rec.quality_score == 1.0

    def test_quality_flag_to_score_anomaly(self):
        rec = _row_to_record(self._make_row(quality_flag="0"))
        assert rec.quality_score == 0.5

    def test_volume_zero_is_suspended(self):
        rec = _row_to_record(self._make_row(volume="0"))
        assert rec.is_suspended is True

    def test_volume_nonzero_not_suspended(self):
        rec = _row_to_record(self._make_row(volume="1000"))
        assert rec.is_suspended is False

    def test_idempotency_key_format(self):
        rec = _row_to_record(self._make_row())
        assert rec.idempotency_key == "600519.SH:20260101"

    def test_close_none_returns_none(self):
        rec = _row_to_record(self._make_row(close=""))
        assert rec is None

    def test_amount_optional(self):
        rec = _row_to_record(self._make_row(amount=""))
        assert rec is not None
        assert rec.amount is None

    def test_adj_factor_optional(self):
        rec = _row_to_record(self._make_row(adj_factor=""))
        assert rec is not None
        assert rec.adj_factor is None

    def test_data_source_propagated(self):
        rec = _row_to_record(self._make_row(data_source="akshare"))
        assert rec.data_source == "akshare"


class TestLoadKline:
    def test_empty_symbols(self):
        assert load_kline([], "2026-01-01", "2026-01-31") == []

    def test_mock_ch_reader(self, monkeypatch):
        tsv = _make_tsv(n_days=5)
        monkeypatch.setattr(producer.ch_reader, "query", lambda sql, timeout=30: tsv)
        records = load_kline(["600519.SH", "000001.SZ"], "2026-01-01", "2026-01-05")
        assert len(records) == 10  # 2标的 × 5天

    def test_empty_result(self, monkeypatch):
        monkeypatch.setattr(producer.ch_reader, "query", lambda sql, timeout=30: "")
        assert load_kline(["A.SH"], "2026-01-01", "2026-01-10") == []

    def test_returns_normalized_market_data_type(self, monkeypatch):
        tsv = _make_tsv(n_days=1, symbols=["A.SH"])
        monkeypatch.setattr(producer.ch_reader, "query", lambda sql, timeout=30: tsv)
        records = load_kline(["A.SH"], "2026-01-01", "2026-01-01")
        assert len(records) == 1
        assert isinstance(records[0], NormalizedMarketData)

    def test_suspended_detected(self, monkeypatch):
        # 第3天(i=2) volume=0 → 停牌
        tsv = _make_tsv(n_days=5, symbols=["600519.SH"])
        monkeypatch.setattr(producer.ch_reader, "query", lambda sql, timeout=30: tsv)
        records = load_kline(["600519.SH"], "2026-01-01", "2026-01-05")
        suspended = [r for r in records if r.is_suspended]
        assert len(suspended) == 1
        assert suspended[0].timestamp.day == 3

    def test_quality_anomaly_detected(self, monkeypatch):
        # 第2天(i=1) quality_flag=0 → quality_score=0.5
        tsv = _make_tsv(n_days=5, symbols=["600519.SH"])
        monkeypatch.setattr(producer.ch_reader, "query", lambda sql, timeout=30: tsv)
        records = load_kline(["600519.SH"], "2026-01-01", "2026-01-05")
        anomaly = [r for r in records if r.quality_score < 1.0]
        assert len(anomaly) == 1
        assert anomaly[0].quality_score == 0.5

    def test_idempotency_keys_unique(self, monkeypatch):
        tsv = _make_tsv(n_days=5, symbols=["600519.SH", "000001.SZ"])
        monkeypatch.setattr(producer.ch_reader, "query", lambda sql, timeout=30: tsv)
        records = load_kline(["600519.SH", "000001.SZ"], "2026-01-01", "2026-01-05")
        keys = {r.idempotency_key for r in records}
        assert len(keys) == len(records)

    def test_sql_injection_escape(self, monkeypatch):
        captured_sql = []
        def fake_query(sql, timeout=30):
            captured_sql.append(sql)
            return ""
        monkeypatch.setattr(producer.ch_reader, "query", fake_query)
        load_kline(["A'B.SH"], "2026-01-01", "2026-01-10")
        assert "\\'" in captured_sql[0]


class TestProduceAlias:
    def test_produce_equals_load_kline(self, monkeypatch):
        tsv = _make_tsv(n_days=3, symbols=["A.SH"])
        monkeypatch.setattr(producer.ch_reader, "query", lambda sql, timeout=30: tsv)
        r1 = load_kline(["A.SH"], "2026-01-01", "2026-01-03")
        r2 = produce(["A.SH"], "2026-01-01", "2026-01-03")
        assert len(r1) == len(r2)
        assert [r.idempotency_key for r in r1] == [r.idempotency_key for r in r2]


# === 裁定#ARCH-SYMBOL-NORMALIZE-001 测试（2026-07-25）===


class TestNormalizeSymbol:
    """symbol 标准化：纯数字 → 契约格式（600519.SH）。"""

    def test_sh_main_board(self):
        assert _normalize_symbol("600519") == "600519.SH"

    def test_sh_star_market(self):
        assert _normalize_symbol("688981") == "688981.SH"

    def test_sh_b_share(self):
        assert _normalize_symbol("900901") == "900901.SH"

    def test_sz_main_board(self):
        assert _normalize_symbol("000001") == "000001.SZ"

    def test_sz_gem(self):
        assert _normalize_symbol("300750") == "300750.SZ"

    def test_bj_exchange(self):
        assert _normalize_symbol("830879") == "830879.BJ"

    def test_bj_exchange_4_prefix(self):
        assert _normalize_symbol("430047") == "430047.BJ"

    def test_already_has_suffix_idempotent(self):
        assert _normalize_symbol("600519.SH") == "600519.SH"

    def test_already_has_sz_suffix_idempotent(self):
        assert _normalize_symbol("000001.SZ") == "000001.SZ"

    def test_empty_string(self):
        assert _normalize_symbol("") == ""

    def test_none(self):
        assert _normalize_symbol(None) is None

    def test_unknown_prefix_no_suffix(self):
        # 未知前缀（7xxxxx 在 TRAE-082 分层前缀映射中无归属）原样返回，不擅自添加后缀
        # 2026-08-17 AI-04：5xxxxx 已由真源 symbol_normalizer 归为 SH（沪市基金/ETF），
        # 本用例改用 7 前缀保持"未知前缀"语义。
        assert _normalize_symbol("799999") == "799999"

    def test_strips_whitespace(self):
        assert _normalize_symbol("  600519  ") == "600519.SH"


class TestStripSymbolSuffix:
    """symbol 后缀去除：契约格式 → 纯数字（查 DB 用）。"""

    def test_sh_suffix(self):
        assert _strip_symbol_suffix("600519.SH") == "600519"

    def test_sz_suffix(self):
        assert _strip_symbol_suffix("000001.SZ") == "000001"

    def test_bj_suffix(self):
        assert _strip_symbol_suffix("830879.BJ") == "830879"

    def test_no_suffix_idempotent(self):
        assert _strip_symbol_suffix("600519") == "600519"

    def test_empty(self):
        assert _strip_symbol_suffix("") == ""

    def test_none(self):
        assert _strip_symbol_suffix(None) is None

    def test_strips_whitespace(self):
        assert _strip_symbol_suffix("  600519.SH  ") == "600519"


class TestFormatSymbolsStripsSuffix:
    """_format_symbols 自动去除交易所后缀，匹配 kline_daily 纯数字存储。"""

    def test_strips_sh_suffix(self):
        # 600519.SH → '600519'
        result = _format_symbols(["600519.SH"])
        assert result == "'600519'"

    def test_strips_sz_suffix(self):
        result = _format_symbols(["000001.SZ"])
        assert result == "'000001'"

    def test_mixed_formats(self):
        # 混合契约格式和纯数字
        result = _format_symbols(["600519.SH", "000001"])
        assert result == "'600519','000001'"

    def test_pure_numeric_unchanged(self):
        result = _format_symbols(["600519", "000001"])
        assert result == "'600519','000001'"

    def test_escape_after_strip(self):
        # 去后缀后仍要转义单引号
        result = _format_symbols(["600'519.SH"])
        assert "\\'" in result
        assert ".SH" not in result  # 后缀已去除


class TestRowToRecordSymbolNormalization:
    """_row_to_record 对纯数字 symbol 自动标准化为契约格式。"""

    def _make_row(self, symbol: str, **overrides) -> pd.Series:
        defaults = {
            "trade_date": pd.Timestamp("2026-01-01"),
            "symbol": symbol,
            "open": "100.0",
            "high": "101.0",
            "low": "99.0",
            "close": "100.5",
            "volume": "1000",
            "amount": "100000",
            "adj_factor": "1.0",
            "data_source": "miniqmt",
            "quality_flag": "1",
        }
        defaults.update(overrides)
        return pd.Series(defaults)

    def test_pure_numeric_sh_symbol_normalized(self):
        rec = _row_to_record(self._make_row(symbol="600519"))
        assert rec is not None
        assert rec.symbol == "600519.SH"

    def test_pure_numeric_sz_symbol_normalized(self):
        rec = _row_to_record(self._make_row(symbol="000001"))
        assert rec is not None
        assert rec.symbol == "000001.SZ"

    def test_pure_numeric_bj_symbol_normalized(self):
        rec = _row_to_record(self._make_row(symbol="830879"))
        assert rec is not None
        assert rec.symbol == "830879.BJ"

    def test_already_suffixed_symbol_idempotent(self):
        rec = _row_to_record(self._make_row(symbol="600519.SH"))
        assert rec is not None
        assert rec.symbol == "600519.SH"

    def test_idempotency_key_uses_normalized_symbol(self):
        rec = _row_to_record(self._make_row(symbol="600519"))
        assert rec is not None
        assert rec.idempotency_key == "600519.SH:20260101"


class TestRowToRecordAdjFactorZero:
    """_row_to_record 对 adj_factor=0 视为 None（无效值）。

    裁定#ARCH-ADJFACTOR-NULL-001：adj_factor=0 是 bdpan_qfq ad-hoc writer 的
    placeholder，数学上无效（复权因子=0 意味价格归零），视为缺失（None）。
    """

    def _make_row(self, **overrides) -> pd.Series:
        defaults = {
            "trade_date": pd.Timestamp("2026-01-01"),
            "symbol": "600519",
            "open": "100.0",
            "high": "101.0",
            "low": "99.0",
            "close": "100.5",
            "volume": "1000",
            "amount": "100000",
            "adj_factor": "0",
            "data_source": "bdpan_qfq",
            "quality_flag": "1",
        }
        defaults.update(overrides)
        return pd.Series(defaults)

    def test_adj_factor_zero_becomes_none(self):
        rec = _row_to_record(self._make_row(adj_factor="0"))
        assert rec is not None
        assert rec.adj_factor is None

    def test_adj_factor_zero_decimal_becomes_none(self):
        rec = _row_to_record(self._make_row(adj_factor="0.0"))
        assert rec is not None
        assert rec.adj_factor is None

    def test_adj_factor_zero_string_becomes_none(self):
        rec = _row_to_record(self._make_row(adj_factor="0.00000000"))
        assert rec is not None
        assert rec.adj_factor is None

    def test_adj_factor_nonzero_preserved(self):
        rec = _row_to_record(self._make_row(adj_factor="0.95"))
        assert rec is not None
        assert rec.adj_factor == Decimal("0.95")

    def test_adj_factor_one_preserved(self):
        rec = _row_to_record(self._make_row(adj_factor="1.0"))
        assert rec is not None
        assert rec.adj_factor == Decimal("1.0")

    def test_adj_factor_empty_becomes_none(self):
        rec = _row_to_record(self._make_row(adj_factor=""))
        assert rec is not None
        assert rec.adj_factor is None

    def test_adj_factor_none_becomes_none(self):
        rec = _row_to_record(self._make_row(adj_factor=None))
        assert rec is not None
        assert rec.adj_factor is None

    def test_bdpan_qfq_data_with_zero_adj_factor(self):
        """模拟 bdpan_qfq 场景：data_source='bdpan_qfq', adj_factor=0 → None。"""
        rec = _row_to_record(self._make_row(
            adj_factor="0", data_source="bdpan_qfq"
        ))
        assert rec is not None
        assert rec.adj_factor is None
        assert rec.data_source == "bdpan_qfq"
        assert rec.symbol == "600519.SH"  # 纯数字已标准化


class TestLoadKlineSymbolConversion:
    """load_kline 双向 symbol 转换：入参带后缀 → 查DB纯数字 → 产出带后缀。"""

    def test_input_with_suffix_queries_stripped(self, monkeypatch):
        """入参 600519.SH → SQL 用 '600519' 查 DB。"""
        captured_sql = []

        def fake_query(sql, timeout=30):
            captured_sql.append(sql)
            # 返回纯数字 symbol 的 TSV（模拟 DB 存储）
            return "\t".join([
                "2026-01-01", "600519", "100.0", "101.0", "99.0", "100.5",
                "1000", "100000", "1.0", "miniqmt", "1",
            ]) + "\n"

        monkeypatch.setattr(producer.ch_reader, "query", fake_query)
        records = load_kline(["600519.SH"], "2026-01-01", "2026-01-01")
        assert len(records) == 1
        # SQL 中应该是纯数字 '600519'，不是 '600519.SH'
        assert "'600519'" in captured_sql[0]
        assert "'600519.SH'" not in captured_sql[0]

    def test_output_symbol_has_suffix(self, monkeypatch):
        """DB 返回纯数字 symbol → 产出 NormalizedMarketData.symbol 带后缀。"""
        tsv = "\t".join([
            "2026-01-01", "600519", "100.0", "101.0", "99.0", "100.5",
            "1000", "100000", "1.0", "miniqmt", "1",
        ]) + "\n"
        monkeypatch.setattr(producer.ch_reader, "query", lambda sql, timeout=30: tsv)
        records = load_kline(["600519"], "2026-01-01", "2026-01-01")
        assert len(records) == 1
        assert records[0].symbol == "600519.SH"

    def test_mixed_input_formats(self, monkeypatch):
        """入参混合格式（600519.SH 和 000001）都能正确查询。"""
        captured_sql = []

        def fake_query(sql, timeout=30):
            captured_sql.append(sql)
            return ""  # 空结果即可，只验证 SQL 构造

        monkeypatch.setattr(producer.ch_reader, "query", fake_query)
        load_kline(["600519.SH", "000001"], "2026-01-01", "2026-01-01")
        assert "'600519'" in captured_sql[0]
        assert "'000001'" in captured_sql[0]
        assert ".SH" not in captured_sql[0]  # 后缀已去除
