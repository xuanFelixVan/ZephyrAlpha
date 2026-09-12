# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c3_fundamental_clickhouse.md
# [MODULE] tests.zephyr.data.test_financial_derived_compute
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.implementations.financial_derived_compute
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 纯函数核直测零 IO（禁写生产路径，store 全部内存构造）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] 本文件
# [TTL] permanent
"""financial_derived 计算核单测——单季/TTM/增长率/PIT as-of/对齐事件语义（消费端 F1-M1）。

核心场景 fixture：600519 四季跨年数据 + 三类修正公告事件，锁定：
    1. 单季拆分（Q1=累计、Q2+ 累计差分、非季末→NULL）
    2. TTM（上年FY+本期累计−去年同季累计；FY期=累计；历史缺失→NULL）
    3. 增长率 (cur-base)/|base|（基期缺失/零→NULL）
    4. PIT as-of：期后修正公告不污染已公告时点（e2 行），已到时点采用修正版（e3 行）
    5. 对齐事件=三方公告日并集（修正公告独立成行，与源表同构）
    6. 三方未齐不成行（2024-09-30 只有 income → 无行）
"""

from __future__ import annotations

import datetime as dt

import pytest

from zephyr.data.implementations.financial_derived_compute import (
    build_symbol_rows,
    fiscal_prev,
    growth,
    safe_div,
    shift_quarter,
    visible,
)


def _d(s: str) -> dt.date:
    return dt.date.fromisoformat(s)


def _v(ann: str, **vals) -> tuple[dt.date, dict]:
    return (_d(ann), vals)


@pytest.fixture()
def store_600519() -> dict:
    """四季跨年 fixture（值即期望的算术基底，断言内显式写出算式）。"""
    inc = {
        _d("2024-03-31"): [_v("2024-04-18", operating_revenue="90", operating_cost="54",
                              net_profit_incl_minority="18")],
        _d("2024-06-30"): [_v("2024-08-20", operating_revenue="200", operating_cost="120",
                              net_profit_incl_minority="40", total_profit="48", income_tax="6")],
        _d("2024-09-30"): [_v("2024-10-25", operating_revenue="350", operating_cost="210",
                              net_profit_incl_minority="70")],
        _d("2024-12-31"): [_v("2025-04-10", operating_revenue="500", operating_cost="300",
                              net_profit_incl_minority="100", total_profit="120", income_tax="15")],
        # Q1-2025 带 09-15 修正公告（PIT 语义主考题）
        _d("2025-03-31"): [_v("2025-04-20", operating_revenue="100", operating_cost="60",
                              net_profit_incl_minority="20"),
                           _v("2025-09-15", operating_revenue="105", operating_cost="63",
                              net_profit_incl_minority="21")],
        # H1-2025 带 09-01 修正公告
        _d("2025-06-30"): [_v("2025-08-20", operating_revenue="260", operating_cost="150",
                              net_profit_incl_minority="52", total_profit="60", income_tax="8"),
                           _v("2025-09-01", operating_revenue="270", operating_cost="155",
                              net_profit_incl_minority="54")],
        _d("2025-09-30"): [_v("2025-10-20", operating_revenue="400", operating_cost="230",
                              net_profit_incl_minority="80")],
        # 非季末期（历史脏数据形态）：宽表成行但不拆分
        _d("2025-05-31"): [_v("2025-06-18", operating_revenue="180", operating_cost="100",
                              net_profit_incl_minority="36")],
    }
    bal = {
        _d("2024-06-30"): [_v("2024-08-22", total_assets="900", total_liabilities="450")],
        _d("2024-12-31"): [_v("2025-04-12", total_assets="1000", total_liabilities="500")],
        _d("2025-03-31"): [_v("2025-04-22", total_assets="1000", total_liabilities="500")],
        _d("2025-06-30"): [_v("2025-08-25", total_assets="1100", total_liabilities="550")],
        _d("2025-09-30"): [_v("2025-10-22", total_assets="1150", total_liabilities="560")],
        _d("2025-05-31"): [_v("2025-06-18", total_assets="1050", total_liabilities="520")],
    }
    cfs = {
        _d("2024-03-31"): [_v("2024-04-19", ocf_net="12")],
        _d("2024-06-30"): [_v("2024-08-21", ocf_net="30")],
        _d("2024-12-31"): [_v("2025-04-11", ocf_net="80")],
        _d("2025-03-31"): [_v("2025-04-21", ocf_net="60")],
        _d("2025-06-30"): [_v("2025-08-21", ocf_net="150")],
        _d("2025-09-30"): [_v("2025-10-21", ocf_net="240")],
        _d("2025-05-31"): [_v("2025-06-18", ocf_net="120")],
    }
    return {"income_statement": inc, "balance_sheet": bal, "cashflow_statement": cfs}


# ---------------------------------------------------------------------------
# 助手纯函数
# ---------------------------------------------------------------------------

def test_shift_quarter_keeps_quarter_end():
    assert shift_quarter(_d("2026-03-31"), -1) == _d("2025-12-31")
    assert shift_quarter(_d("2026-03-31"), -4) == _d("2025-03-31")
    assert shift_quarter(_d("2025-12-31"), 1) == _d("2026-03-31")


def test_shift_quarter_non_quarter_end_clamps_day():
    assert shift_quarter(_d("2025-05-31"), -1) == _d("2025-02-28")  # −1 季=−3 月，日钳位月末
    assert shift_quarter(_d("2025-05-31"), -4) == _d("2024-05-31")


def test_fiscal_prev():
    assert fiscal_prev(_d("2026-03-31")) is None          # Q1 无同年上期
    assert fiscal_prev(_d("2026-06-30")) == _d("2026-03-31")
    assert fiscal_prev(_d("2026-12-31")) == _d("2026-09-30")
    assert fiscal_prev(_d("2026-05-31")) is None          # 非季末不拆分


def test_growth_abs_base():
    assert growth(160.0, 110.0) == pytest.approx(50 / 110)
    assert growth(10.0, -50.0) == pytest.approx(1.2)      # |base| 防负值翻转
    assert growth(None, 10.0) is None
    assert growth(10.0, None) is None
    assert growth(10.0, 0.0) is None


def test_safe_div_zero_and_none():
    assert safe_div(1.0, 0.0) is None
    assert safe_div(None, 2.0) is None
    assert safe_div(3.0, 6.0) == 0.5


def test_visible_as_of_picks_latest_not_later():
    versions = [_v("2025-04-20", x="1"), _v("2025-09-15", x="2")]
    assert visible(versions, _d("2025-08-01"))["x"] == "1"   # 修正版尚未公告
    assert visible(versions, _d("2025-09-15"))["x"] == "2"   # 已到修正时点
    assert visible(versions, _d("2025-01-01")) is None
    assert visible(None, _d("2025-09-15")) is None


# ---------------------------------------------------------------------------
# build_symbol_rows：对齐事件 + PIT 语义主场景
# ---------------------------------------------------------------------------

def test_alignment_events_and_row_count(store_600519):
    rows = build_symbol_rows("600519", store_600519)
    # 8 行：2024-06-30 / 2024-12-31 / 2025-03-31×2(原版+修正版事件) / 2025-05-31 /
    #       2025-06-30×2 / 2025-09-30
    assert len(rows) == 8
    # 2024-09-30 只有 income（bal/cfs 缺）——三方不齐不成行
    assert all(r["report_period"] != "2024-09-30" for r in rows)


def test_single_quarter_split(store_600519):
    by = {(r["report_period"], r["announce_date"]): r
          for r in build_symbol_rows("600519", store_600519)}
    q1 = by[("2025-03-31", "2025-04-22")]
    assert q1["rev_q"] == pytest.approx(100)             # Q1=累计本身
    h1 = by[("2025-06-30", "2025-08-25")]
    assert h1["rev_q"] == pytest.approx(260 - 100)
    assert h1["cost_q"] == pytest.approx(150 - 60)
    assert h1["np_q"] == pytest.approx(52 - 20)
    assert h1["ocf_q"] == pytest.approx(150 - 60)


def test_ttm_rolling_four_quarters(store_600519):
    by = {(r["report_period"], r["announce_date"]): r
          for r in build_symbol_rows("600519", store_600519)}
    h1 = by[("2025-06-30", "2025-08-25")]
    assert h1["rev_ttm"] == pytest.approx(500 + 260 - 200)
    assert h1["np_ttm"] == pytest.approx(100 + 52 - 40)
    assert h1["ocf_ttm"] == pytest.approx(80 + 150 - 30)
    fy = by[("2024-12-31", "2025-04-12")]
    assert fy["rev_ttm"] == pytest.approx(500)           # FY 期 TTM=累计本身
    q3 = by[("2025-09-30", "2025-10-22")]
    assert q3["rev_ttm"] == pytest.approx(500 + 400 - 350)
    # 历史缺失 → NULL（2024H1 事件时点无 FY2023）
    old = by[("2024-06-30", "2024-08-22")]
    assert old["rev_ttm"] is None


def test_ratios(store_600519):
    by = {(r["report_period"], r["announce_date"]): r
          for r in build_symbol_rows("600519", store_600519)}
    h1 = by[("2025-06-30", "2025-08-25")]
    assert h1["accrual_ttm"] == pytest.approx((112 - 200) / 1100)      # (np_ttm-ocf_ttm)/ta
    assert h1["gpoa_ttm"] == pytest.approx((560 - 330) / 1100)
    assert h1["gross_margin_q"] == pytest.approx((160 - 90) / 160)
    assert h1["eff_tax_rate_ttm"] == pytest.approx(17 / 132)
    assert h1["debt_ratio"] == pytest.approx(0.5)


def test_growth_fields(store_600519):
    by = {(r["report_period"], r["announce_date"]): r
          for r in build_symbol_rows("600519", store_600519)}
    h1 = by[("2025-06-30", "2025-08-25")]
    assert h1["rev_q_yoy"] == pytest.approx((160 - 110) / 110)   # 去年同期单季=200-90
    assert h1["np_q_yoy"] == pytest.approx((32 - 22) / 22)
    assert h1["ocf_q_yoy"] == pytest.approx((90 - 18) / 18)
    assert h1["rev_q_qoq"] == pytest.approx((160 - 100) / 100)   # 上季=Q1 累计
    assert h1["np_q_qoq"] == pytest.approx((32 - 20) / 20)


def test_pit_no_lookahead_from_later_restatement(store_600519):
    """期后修正公告不得污染已公告时点（D1/D2 PIT 铁律）。"""
    by = {(r["report_period"], r["announce_date"]): r
          for r in build_symbol_rows("600519", store_600519)}
    # H1 原版事件（08-25）：Q1 修正版（09-15）不可见 → 单季按原版 Q1=100 拆分
    h1_orig = by[("2025-06-30", "2025-08-25")]
    assert h1_orig["rev_q"] == pytest.approx(160)
    # H1 修正版事件（09-01）：Q1 修正版（09-15）仍不可见
    h1_re = by[("2025-06-30", "2025-09-01")]
    assert h1_re["rev_q"] == pytest.approx(270 - 100)
    # Q3 事件（10-22）：Q1 修正版与 H1 修正版均已可见 → 用修正版
    q3 = by[("2025-09-30", "2025-10-22")]
    assert q3["rev_q"] == pytest.approx(400 - 270)
    # Q1 修正公告独立成行（与源表同构）
    q1_re = by[("2025-03-31", "2025-09-15")]
    assert q1_re["rev_q"] == pytest.approx(105)


def test_non_quarter_end_period_wide_only(store_600519):
    by = {(r["report_period"], r["announce_date"]): r
          for r in build_symbol_rows("600519", store_600519)}
    odd = by[("2025-05-31", "2025-06-18")]
    assert odd["revenue_cum"] == pytest.approx(180)
    assert odd["rev_q"] is None
    assert odd["rev_ttm"] is None
