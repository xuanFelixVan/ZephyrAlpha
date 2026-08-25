# [BLUEPRINT] MOD-DAT-FIN-PARSER | tests/zephyr/data/test_financial_parser.py
# [MODULE] tests.zephyr.data.test_financial_parser
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.financial_parser
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS]
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-DAT-FIN-PARSER | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""FinancialParser 单元测试——财报结构化解析器（CAND-DAT-017 / B13-04263 / D-DATA-80）。

覆盖：
    1. ReportRef 校验：空 symbol/未知 report_type/空 period → ValueError
    2. 解析路径阶梯：XBRL(0.95) > 表格(0.80) > LLM 兜底(0.60)；三路皆无 fail-closed
    3. 指标标准化：METRIC_MAP 映射；未识别指标入 unmapped_keys 留痕
    4. 数值清洗：千分位/括号负数/万元亿元倍率归一
    5. quality_flag 置信度分级（≥0.90 good / ≥0.70 degraded / else poor）
"""

from __future__ import annotations

import pytest

from zephyr.data.financial_parser import (
    METRIC_MAP,
    FinancialParser,
    ReportRef,
)


def _report(**kw) -> ReportRef:
    base = {"symbol": "600519", "report_type": "annual", "period": "2025FY"}
    base.update(kw)
    return ReportRef(**base)


# ── 1. ReportRef 校验 ──


def test_empty_symbol_fail_closed():
    fp = FinancialParser()
    with pytest.raises(ValueError):
        fp.parse_report(_report(symbol="", xbrl_facts={"营业收入": "1"}))


def test_unknown_report_type_fail_closed():
    fp = FinancialParser()
    with pytest.raises(ValueError):
        fp.parse_report(_report(report_type="monthly", xbrl_facts={"营业收入": "1"}))


def test_empty_period_fail_closed():
    fp = FinancialParser()
    with pytest.raises(ValueError):
        fp.parse_report(_report(period="", xbrl_facts={"营业收入": "1"}))


def test_report_types_accepted():
    fp = FinancialParser()
    for rt in ("annual", "quarterly", "express", "correction"):
        out = fp.parse_report(_report(report_type=rt, xbrl_facts={"营业收入": "100"}))
        assert out.report_type == rt


# ── 2. 解析路径阶梯 ──


def test_xbrl_path_highest_confidence():
    fp = FinancialParser()
    out = fp.parse_report(_report(xbrl_facts={"营业收入": "1500亿元", "归母净利润": "700亿元"}))
    assert out.parser_used == "xbrl"
    assert out.confidence == pytest.approx(0.95)
    assert out.quality_flag == "good"
    assert out.metrics["revenue"] == pytest.approx(1500e8)
    assert out.metrics["net_profit"] == pytest.approx(700e8)


def test_table_path_when_no_xbrl():
    fp = FinancialParser()
    tables = [[["指标", "2025年"], ["营业收入", "1,234.56万元"], ["净利润", "500万元"]]]
    out = fp.parse_report(_report(raw_tables=tables))
    assert out.parser_used == "table"
    assert out.confidence == pytest.approx(0.80)
    assert out.quality_flag == "degraded"
    assert out.metrics["revenue"] == pytest.approx(1234.56e4)


def test_injected_pdf_extractor_used_when_no_raw_tables():
    fp = FinancialParser(pdf_extractor=lambda path: [[["营业收入", "100万元"]]])
    out = fp.parse_report(_report(pdf_path="data/reports/600519_2025.pdf"))
    assert out.parser_used == "table"
    assert out.metrics["revenue"] == pytest.approx(100e4)


def test_llm_fallback_for_non_standard():
    fp = FinancialParser(llm_fallback=lambda text: {"revenue": 1.5e8, "net_profit": 3e7})
    out = fp.parse_report(_report(report_type="express", text="业绩快报：营收1.5亿…"))
    assert out.parser_used == "llm"
    assert out.confidence == pytest.approx(0.60)
    assert out.quality_flag == "poor"


def test_no_path_available_fail_closed():
    fp = FinancialParser()
    with pytest.raises(ValueError):
        fp.parse_report(_report())


# ── 3. 指标标准化 ──


def test_metric_map_standardization_and_unmapped():
    fp = FinancialParser()
    out = fp.parse_report(
        _report(
            xbrl_facts={
                "营业收入": "100",
                "归属于母公司股东的净利润": "30",
                "经营活动产生的现金流量净额": "50",
                "某非标指标": "7",
            }
        )
    )
    assert out.metrics["revenue"] == pytest.approx(100.0)
    assert out.metrics["net_profit"] == pytest.approx(30.0)
    assert out.metrics["operating_cashflow"] == pytest.approx(50.0)
    assert "某非标指标" in out.unmapped_keys


def test_metric_map_covers_core_metrics():
    for canonical in ("revenue", "net_profit", "total_assets", "total_liabilities", "operating_cashflow", "eps"):
        assert canonical in set(METRIC_MAP.values())


# ── 4. 数值清洗 ──


def test_numeric_cleaning_thousands_and_paren_negative():
    fp = FinancialParser()
    out = fp.parse_report(_report(xbrl_facts={"营业收入": "1,234.5", "归母净利润": "(500)"}))
    assert out.metrics["revenue"] == pytest.approx(1234.5)
    assert out.metrics["net_profit"] == pytest.approx(-500.0)


def test_numeric_cleaning_unit_multiplier():
    fp = FinancialParser()
    out = fp.parse_report(
        _report(xbrl_facts={"营业收入": "12万元", "归母净利润": "3亿元", "总资产": "800"})
    )
    assert out.metrics["revenue"] == pytest.approx(12e4)
    assert out.metrics["net_profit"] == pytest.approx(3e8)
    assert out.metrics["total_assets"] == pytest.approx(800.0)


def test_unparseable_value_skipped_not_crash():
    fp = FinancialParser()
    out = fp.parse_report(_report(xbrl_facts={"营业收入": "不适用"}))
    assert "revenue" not in out.metrics
    assert "营业收入" in out.unmapped_keys
