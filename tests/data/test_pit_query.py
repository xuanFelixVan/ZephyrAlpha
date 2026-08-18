# [A_test] module_id=MOD-TEST-pit-query | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §pit
# [MODULE] tests.data.test_pit_query
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.pit_query
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] PIT三公理对齐；SQL构建纯函数可单测；白名单非法表抛PITQueryError
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound
"""#ARCH-CH-021 P0-5: 财报 PIT 查询能力测试。

覆盖三类：
  1. 纯函数 SQL 构建（无 DB 依赖，确定性）
  2. 查询方法（mock ch_reader.query 捕获 SQL + 返回固定 TSV）
  3. TSV 解析 + 白名单校验
"""
from __future__ import annotations

from datetime import date, datetime
from unittest.mock import patch

import pytest

from zephyr.data import pit_query
from zephyr.data.pit_query import (
    FINANCIAL_PIT_TABLES,
    FinancialPITQuery,
    PITQueryConfig,
    PITQueryError,
    tsv_to_dataframe,
    tsv_to_records,
)


# ============================================================================
# 1. 纯函数：查询时点格式化
# ============================================================================
class TestFmtQueryTime:
    def test_date_object(self):
        assert pit_query.fmt_query_time(date(2026, 6, 1)) == "2026-06-01"

    def test_datetime_object(self):
        assert pit_query.fmt_query_time(datetime(2026, 6, 1, 14, 30)) == "2026-06-01"

    def test_string_iso(self):
        assert pit_query.fmt_query_time("2026-06-01") == "2026-06-01"

    def test_string_with_time(self):
        assert pit_query.fmt_query_time("2026-06-01T14:30:00") == "2026-06-01"


# ============================================================================
# 2. 纯函数：标的代码转义
# ============================================================================
class TestEscapeSymbol:
    def test_normal_symbol(self):
        assert pit_query.escape_symbol("000001.SZ") == "000001.SZ"

    def test_quote_injection(self):
        # 单引号被转义，防 SQL 注入
        assert pit_query.escape_symbol("x' OR 1=1") == "x\\' OR 1=1"

    def test_non_string(self):
        assert pit_query.escape_symbol(123) == "123"


class TestFormatSymbols:
    def test_multiple(self):
        out = pit_query.format_symbols(["000001.SZ", "600000.SH"])
        assert out == "'000001.SZ','600000.SH'"

    def test_empty_raises(self):
        with pytest.raises(PITQueryError, match="不能为空"):
            pit_query.format_symbols([])

    def test_filters_empty_strings(self):
        out = pit_query.format_symbols(["000001.SZ", "", "  "])
        assert "000001.SZ" in out


# ============================================================================
# 3. 纯函数：embargo / limit_by 子句
# ============================================================================
class TestEmbargoClause:
    def test_zero(self):
        assert pit_query.embargo_clause(0) == ""

    def test_negative(self):
        assert pit_query.embargo_clause(-3) == ""

    def test_positive(self):
        assert pit_query.embargo_clause(5) == " - INTERVAL 5 DAY"


class TestLimitByClause:
    def test_with_period(self):
        out = pit_query.limit_by_clause("report_period")
        assert out == " LIMIT 1 BY symbol, report_period"

    def test_without_period(self):
        # repurchase 无报告期列，不做版本去重
        assert pit_query.limit_by_clause(None) == ""

    def test_dividend_year(self):
        out = pit_query.limit_by_clause("dividend_year")
        assert out == " LIMIT 1 BY symbol, dividend_year"


# ============================================================================
# 4. 纯函数：白名单表解析
# ============================================================================
class TestResolveTable:
    def test_logical_name(self):
        qualified, period = pit_query.resolve_table("balance_sheet")
        assert qualified == FINANCIAL_PIT_TABLES["balance_sheet"]
        assert period == "report_period"

    def test_repurchase_no_period(self):
        qualified, period = pit_query.resolve_table("repurchase")
        assert period is None

    def test_non_whitelist_raises(self):
        with pytest.raises(PITQueryError, match="不在财报 PIT 白名单"):
            pit_query.resolve_table("kline_daily")

    def test_dividend_period_is_dividend_year(self):
        _q, period = pit_query.resolve_table("dividend")
        assert period == "dividend_year"


# ============================================================================
# 5. SQL 构建（捕获生成的 SQL，验证三公理）
# ============================================================================
class TestBuildAsOfSql:
    def setup_method(self):
        self.pit = FinancialPITQuery()

    def test_single_symbol_basic(self):
        sql = self.pit.build_as_of_sql(
            "balance_sheet", ["000001.SZ"], "2026-06-01", "*", single=True
        )
        assert "FROM " + FINANCIAL_PIT_TABLES["balance_sheet"] in sql
        assert "symbol = '000001.SZ'" in sql
        assert "announce_date <= toDate('2026-06-01')" in sql
        assert "ORDER BY announce_date DESC" in sql
        assert "LIMIT 1 BY symbol, report_period" in sql
        # 无 embargo
        assert "INTERVAL" not in sql

    def test_panel_symbols(self):
        sql = self.pit.build_as_of_sql(
            "income_statement", ["000001.SZ", "600000.SH"], "2026-06-01", "symbol,report_period,total_assets", single=False
        )
        assert "symbol IN ('000001.SZ','600000.SH')" in sql
        assert "LIMIT 1 BY symbol, report_period" in sql

    def test_embargo_applied(self):
        pit = FinancialPITQuery(PITQueryConfig(embargo_days=5))
        sql = pit.build_as_of_sql(
            "balance_sheet", ["000001.SZ"], "2026-06-01", "*", single=True
        )
        assert "announce_date <= toDate('2026-06-01') - INTERVAL 5 DAY" in sql

    def test_repurchase_no_limit_by(self):
        sql = self.pit.build_as_of_sql(
            "repurchase", ["000001.SZ"], "2026-06-01", "*", single=True
        )
        assert "LIMIT 1 BY" not in sql

    def test_non_whitelist_raises(self):
        with pytest.raises(PITQueryError):
            self.pit.build_as_of_sql(
                "kline_daily", ["000001.SZ"], "2026-06-01", "*", single=True
            )

    def test_sql_injection_blocked(self):
        # 恶意 symbol 被转义
        sql = self.pit.build_as_of_sql(
            "balance_sheet", ["x' OR '1'='1"], "2026-06-01", "*", single=True
        )
        assert "\\'" in sql
        assert "OR '1'='1" not in sql or "\\'" in sql


# ============================================================================
# 6. 查询方法（mock ch_reader.query）
# ============================================================================
class TestQueryMethods:
    def setup_method(self):
        self.pit = FinancialPITQuery()
        self.patcher = patch("zephyr.data.pit_query.ch_reader.query")
        self.mock_query = self.patcher.start()

    def teardown_method(self):
        self.patcher.stop()

    def test_as_of_returns_tsv(self):
        self.mock_query.return_value = "000001.SZ\t2025-12-31\t2026-03-30\n"
        out = self.pit.as_of("balance_sheet", "000001.SZ", "2026-06-01")
        assert "000001.SZ" in out
        # 验证调用 SQL 含关键子句
        called_sql = self.mock_query.call_args[0][0]
        assert "announce_date <= toDate('2026-06-01')" in called_sql
        assert "LIMIT 1 BY symbol, report_period" in called_sql

    def test_as_of_panel(self):
        self.mock_query.return_value = "000001.SZ\n600000.SH\n"
        self.pit.as_of_panel("balance_sheet", ["000001.SZ", "600000.SH"], "2026-06-01")
        called_sql = self.mock_query.call_args[0][0]
        assert "symbol IN ('000001.SZ','600000.SH')" in called_sql

    def test_as_of_latest_returns_single_row(self):
        self.mock_query.return_value = "000001.SZ\t2025-12-31\t2026-03-30\n"
        self.pit.as_of_latest("balance_sheet", "000001.SZ", "2026-06-01")
        called_sql = self.mock_query.call_args[0][0]
        assert "ORDER BY report_period DESC, announce_date DESC LIMIT 1" in called_sql

    def test_as_of_latest_no_period_raises(self):
        # repurchase 无报告期列，as_of_latest 不适用
        with pytest.raises(PITQueryError, match="无报告期"):
            self.pit.as_of_latest("repurchase", "000001.SZ", "2026-06-01")

    def test_as_of_latest_dividend_uses_dividend_year(self):
        # dividend 的 period_col 是 dividend_year，as_of_latest 应动态使用
        self.mock_query.return_value = "000001.SZ\t2025\t2026-06-10\n"
        self.pit.as_of_latest("dividend", "000001.SZ", "2026-06-01")
        called_sql = self.mock_query.call_args[0][0]
        assert "ORDER BY dividend_year DESC, announce_date DESC LIMIT 1" in called_sql

    def test_empty_result(self):
        self.mock_query.return_value = ""
        out = self.pit.as_of("balance_sheet", "999999.SZ", "2026-06-01")
        assert out == ""


# ============================================================================
# 7. 幸存者偏差标的池
# ============================================================================
class TestSurvivorshipUniverse:
    def setup_method(self):
        self.pit = FinancialPITQuery()
        self.patcher = patch("zephyr.data.pit_query.ch_reader.query")
        self.mock_query = self.patcher.start()

    def teardown_method(self):
        self.patcher.stop()

    def test_returns_symbol_list(self):
        self.mock_query.return_value = "000001.SZ\n600000.SH\n000002.SZ\n"
        out = self.pit.survivorship_universe("2026-06-01")
        assert out == ["000001.SZ", "600000.SH", "000002.SZ"]

    def test_sql_contains_scd2_filter(self):
        self.mock_query.return_value = ""
        self.pit.survivorship_universe("2026-06-01")
        called_sql = self.mock_query.call_args[0][0]
        assert "valid_from <= toDate('2026-06-01')" in called_sql
        assert "valid_to IS NULL" in called_sql
        assert "valid_to = toDate('1900-01-01')" in called_sql
        assert "valid_to > toDate('2026-06-01')" in called_sql

    def test_empty_returns_empty_list(self):
        self.mock_query.return_value = ""
        assert self.pit.survivorship_universe("2026-06-01") == []

    def test_strips_whitespace(self):
        self.mock_query.return_value = "  000001.SZ  \n  600000.SH \n"
        out = self.pit.survivorship_universe("2026-06-01")
        assert out == ["000001.SZ", "600000.SH"]


# ============================================================================
# 8. TSV 解析
# ============================================================================
class TestTsvParsing:
    def test_records_with_columns(self):
        tsv = "000001.SZ\t2025-12-31\t2026-03-30\n600000.SH\t2025-12-31\t2026-03-31\n"
        cols = ["symbol", "report_period", "announce_date"]
        recs = tsv_to_records(tsv, cols)
        assert len(recs) == 2
        assert recs[0]["symbol"] == "000001.SZ"
        assert recs[1]["announce_date"] == "2026-03-31"

    def test_records_without_columns(self):
        tsv = "a\tb\nc\td\n"
        recs = tsv_to_records(tsv)
        assert recs[0]["col_0"] == "a"
        assert recs[1]["col_1"] == "d"

    def test_empty_tsv(self):
        assert tsv_to_records("") == []
        assert tsv_to_records("   \n  \n") == []

    def test_dataframe(self):
        tsv = "000001.SZ\t100\n600000.SH\t200\n"
        df = tsv_to_dataframe(tsv, ["symbol", "total_assets"])
        assert len(df) == 2
        assert list(df.columns) == ["symbol", "total_assets"]

    def test_dataframe_empty(self):
        df = tsv_to_dataframe("", ["symbol"])
        assert len(df) == 0


# ============================================================================
# 9. 配置 & 常量
# ============================================================================
class TestConfig:
    def test_default_no_embargo(self):
        cfg = PITQueryConfig()
        assert cfg.embargo_days == 0

    def test_frozen(self):
        cfg = PITQueryConfig(embargo_days=3)
        with pytest.raises(Exception):
            cfg.embargo_days = 5  # type: ignore[misc]

    def test_embargo_propagates_to_sql(self):
        pit = FinancialPITQuery(PITQueryConfig(embargo_days=10))
        sql = pit.build_as_of_sql(
            "balance_sheet", ["000001.SZ"], "2026-06-01", "*", single=True
        )
        assert "INTERVAL 10 DAY" in sql


class TestFinancialPitTables:
    def test_all_tables_resolved(self):
        # 所有白名单表都能解析为全限定名
        for name, qualified in FINANCIAL_PIT_TABLES.items():
            assert "." in qualified, f"{name} 未解析为全限定名: {qualified}"

    def test_expected_count(self):
        # 9 张财报表：7 报表 + dividend + repurchase
        assert len(FINANCIAL_PIT_TABLES) == 9

    def test_balance_sheet_in_fundamental_db(self):
        assert FINANCIAL_PIT_TABLES["balance_sheet"].startswith("c3_fundamental.")
