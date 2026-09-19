# -*- coding: utf-8 -*-
# [BLUEPRINT] MOD-L00-004 | docs/_working/residual_construction/wo5_cohort_ledger_workbook.md §4 | §test
# [TTL] permanent
# [A_test] module_id: MOD-DATA-COHORT-LEDGER-BUILDER | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.alt_data.test_cohort_daily_ledger
# [STABILITY] volatile
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [TESTS] src/zephyr/alt_data/cohort_daily_ledger.py
# [SCOPE] zephyr.alt_data.cohort_daily_ledger（WO-5 投资者行为日账本一期结算层）
# [INVARIANTS] 测试隔离：fake reader 注入，零 CH 连接、零生产路径写入；行结构仅内存断言
# ttl: permanent
# completes_when: zephyr.alt_data.cohort_daily_ledger 退役时同步退役
"""cohort_daily_ledger 五人群聚合器单测（tmp_path/fake reader，零 CH 依赖）。

覆盖：
1. 聚合口径正确性（等权求和/截面中位数/余额日变化/折价率 JOIN 口径）。
2. state 一期规则（阈值=0：净正/净负/中性）。
3. 缺源日降级（proxy_source=missing 不抛，metric_value=0 + detail.missing 标记）。
"""

from __future__ import annotations

import json
from decimal import Decimal

import pytest

from zephyr.alt_data.cohort_daily_ledger import build_cohort_daily
from schemas.categories.cohort_daily_ledger import (
    COHORT_HOT_MONEY,
    COHORT_INST_CONFIG,
    COHORT_LEVERAGE,
    COHORT_RETAIL,
    PROXY_MISSING,
    STATE_NET_NEG,
    STATE_NET_POS,
    STATE_NEUTRAL,
)

DAY = "2026-09-17"
PREV = "2026-09-16"


class FakeReader:
    """SQL 片段路由 -> 预置 TSV 输出（模拟 ch_reader.query 返回契约，无 header、\\N=NULL）。"""

    def __init__(self, routes: dict[str, str]):
        self.routes = routes
        self.calls: list[str] = []

    def query(self, sql: str) -> str:
        self.calls.append(sql)
        for pattern, tsv in self.routes.items():
            if pattern in sql:
                return tsv
        return ""


def _index(rows, cohort, metric):
    for r in rows:
        if r["cohort_id"] == cohort and r["metric_id"] == metric:
            return r
    pytest.fail(f"row not found: {cohort}/{metric}")


# ================= 1. 聚合口径正确性 =================

def test_retail_sum_and_median():
    """小单净流入 [100, -50, 30] -> sum=80 median=30（等权求和+截面中位数，万元）。"""
    fake = FakeReader({
        "small_net_inflow": "100.00\n-50.00\n30.00\n",
        "attention_index": "\\N\n7.5\n2.5\n",
    })
    rows = build_cohort_daily(DAY, reader=fake)
    s = _index(rows, COHORT_RETAIL, "net_inflow_sum")
    m = _index(rows, COHORT_RETAIL, "net_inflow_median")
    a = _index(rows, COHORT_RETAIL, "attention_median")
    assert s["metric_value"] == Decimal("80.0000")
    assert m["metric_value"] == Decimal("30.0000")
    # 注意力中位数忽略 \N 行：median(7.5, 2.5)=5.0
    assert a["metric_value"] == Decimal("5.0000")
    assert s["state"] == STATE_NET_POS
    assert json.loads(s["detail"])["unit"] == "万元"


def test_leverage_sum_and_balance_delta():
    """融资买入额合计 + 余额日变化（源表单位=元，聚合折万元 S4）。"""
    fake = FakeReader({
        "DISTINCT trade_date": f"{DAY}\n{PREV}\n",
        "margin_buy FROM": "10.00\n20.00\n30.00\n",
        f"trade_date = '{DAY}'": "100.00\n200.00\n",
        f"trade_date = '{PREV}'": "150.00\n100.00\n",
    })
    rows = build_cohort_daily(DAY, reader=fake)
    # (10+20+30)元 = 60元 = 0.0060 万元
    assert _index(rows, COHORT_LEVERAGE, "margin_buy_sum")["metric_value"] == Decimal("0.0060")
    # (100+200-150-100)元 = 50元 = 0.0050 万元
    assert _index(rows, COHORT_LEVERAGE, "margin_balance_delta")["metric_value"] == Decimal("0.0050")


def test_hot_money_sum_top3_seat_board():
    """龙虎榜 net_buy 合计（源表单位=元折万元）+ 申万板块分布 top3 + 席位行数 + 连板高度。"""
    fake = FakeReader({
        "SELECT net_buy FROM": "500.00\n-200.00\n100.00\n",
        "industry_sw": "电力\t450.00\n农业\t100.00\n玻璃基板\t-200.00\n",
        "dragon_tiger_seat": "42\n",
        "consec_limit": "12\t5\n",
    })
    rows = build_cohort_daily(DAY, reader=fake)
    s = _index(rows, COHORT_HOT_MONEY, "net_buy_sum")
    # (500-200+100)元 = 400元 = 0.0400 万元
    assert s["metric_value"] == Decimal("0.0400")
    top3 = json.loads(s["detail"])["sector_top3"]
    assert [t["sector"] for t in top3] == ["电力", "农业", "玻璃基板"]
    assert float(top3[0]["net_buy"]) == 0.045
    assert _index(rows, COHORT_HOT_MONEY, "activity_count")["metric_value"] == Decimal("42.0000")
    assert _index(rows, COHORT_HOT_MONEY, "board_height_max")["metric_value"] == Decimal("5.0000")


def test_inst_config_amount_and_discount_rate():
    """大宗合计金额（源表单位=元折万元）+ 折价率均值=(1-price/close)*100 截面均值（正=折价）。"""
    fake = FakeReader({
        "bt.amount": "1000.00\t10.50\t11.00\n2000.00\t9.80\t10.00\n",
    })
    rows = build_cohort_daily(DAY, reader=fake)
    a = _index(rows, COHORT_INST_CONFIG, "block_amount_sum")
    d = _index(rows, COHORT_INST_CONFIG, "discount_rate_avg")
    # 3000元 = 0.3000 万元
    assert a["metric_value"] == Decimal("0.3000")
    # (1-10.5/11)*100=4.545454..% ; (1-9.8/10)*100=2% -> mean≈3.2727%
    assert abs(float(d["metric_value"]) - 3.2727) < 0.001
    assert d["state"] == STATE_NET_POS


# ================= 2. state 一期规则（阈值=0） =================

@pytest.mark.parametrize("value,expected", [
    (123.45, STATE_NET_POS),
    (-0.01, STATE_NET_NEG),
    (0.0, STATE_NEUTRAL),
])
def test_state_threshold_zero(value, expected):
    fake = FakeReader({"small_net_inflow": f"{value}\n",
                       "attention_index": ""})
    rows = build_cohort_daily(DAY, reader=fake)
    assert _index(rows, COHORT_RETAIL, "net_inflow_sum")["state"] == expected


# ================= 3. 缺源日降级（不抛） =================

def test_missing_source_degrades_without_raise():
    """全源缺数：proxy_source=missing 行如实产出，metric_value=0、state=中性、不抛异常。"""
    fake = FakeReader({})  # 全部查询返回空
    rows = build_cohort_daily(DAY, reader=fake)
    assert rows, "缺源日仍应产出 missing 降级行"
    for r in rows:
        assert r["proxy_source"] == PROXY_MISSING
        assert r["metric_value"] == Decimal("0.0000")
        assert r["state"] == STATE_NEUTRAL
        detail = json.loads(r["detail"])
        assert detail.get("missing") is True and detail.get("reason")


def test_leverage_missing_prev_day_marks_delta_only():
    """仅一个交易日：margin_buy_sum 正常产出，余额日变化降级 missing。"""
    fake = FakeReader({
        "DISTINCT trade_date": f"{DAY}\n",
        "margin_buy FROM": "10.00\n",
        f"trade_date = '{DAY}'": "100.00\n",
    })
    rows = build_cohort_daily(DAY, reader=fake)
    assert _index(rows, COHORT_LEVERAGE, "margin_buy_sum")["metric_value"] == Decimal("0.0010")
    delta = _index(rows, COHORT_LEVERAGE, "margin_balance_delta")
    assert delta["proxy_source"] == PROXY_MISSING
    assert json.loads(delta["detail"])["reason"] == "margin_prev_day_absent"


def test_leverage_lagged_source_marks_missing():
    """源数据滞后(最新可用日<账本日)：两融行如实 missing，不冒名顶替。"""
    fake = FakeReader({
        "DISTINCT trade_date": f"{PREV}\n{DAY.replace(PREV, '2026-09-15')}\n",
        "margin_buy FROM": "10.00\n",
        f"trade_date = '{PREV}'": "100.00\n",
    })
    rows = build_cohort_daily(DAY, reader=fake)
    for metric in ("margin_buy_sum", "margin_balance_delta"):
        r = _index(rows, COHORT_LEVERAGE, metric)
        assert r["proxy_source"] == PROXY_MISSING
        assert json.loads(r["detail"])["reason"].startswith("margin_lag_latest=")


def test_reader_exception_degrades_not_raises():
    """reader 抛异常 = 单源降级 missing（ERROR_CONTRACT 契约）。"""
    class BoomReader:
        def query(self, sql):
            raise ConnectionError("CH down")

    rows = build_cohort_daily(DAY, reader=BoomReader())
    assert rows
    assert all(r["proxy_source"] == PROXY_MISSING for r in rows)


def test_industry_cohort_absent_phase1():
    """industry 一期留行位不产出（M-8）。"""
    fake = FakeReader({"small_net_inflow": "1.00\n"})
    rows = build_cohort_daily(DAY, reader=fake)
    assert all(r["cohort_id"] != "industry" for r in rows)


def test_row_schema_alignment():
    """行键与 schemas 真源 INSERT_COLUMNS 一一对应（禁复制列名漂移）。"""
    from schemas.categories.cohort_daily_ledger import INSERT_COLUMNS
    cols = INSERT_COLUMNS.strip("()").split(", ")
    fake = FakeReader({"small_net_inflow": "1.00\n"})
    rows = build_cohort_daily(DAY, reader=fake)
    for r in rows:
        assert set(r.keys()) == set(cols)
