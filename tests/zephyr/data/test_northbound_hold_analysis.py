# [A_test] module_id: MOD-TEST-NB-ANALYSIS | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | 19 号 §6.3/§6.5
# [MODULE] tests.zephyr.data.test_northbound_hold_analysis
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.northbound_hold_analysis; pandas; numpy; pytest
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError->fail
# [TESTS] tests/zephyr/data/test_northbound_hold_analysis.py
# [TTL] permanent
# [ARCH-REF] #19_northbound_hold_snapshot §6.3 个股增减持排名 / §6.5 季度净流入估算
# [ALGO_FLOW]
# 层: 输入
# - I1: 季度持仓快照 DataFrame(trade_date/ts_code/hold_share) + 当季 VWAP Series
# 层: 算法
# - A1: compute_quarter_position_changes：Δ持股×当季VWAP（退出=负持仓全减/新进=全仓计入）
# - A2: top_position_changes：top 加仓/减仓排名
# - A3: estimate_quarterly_net_inflow：Σ Δ持股×VWAP（准北向净流入）
# 层: 输出
# - O1: 变化明细 DataFrame（delta_amount 降序）/ top dict / 净流入 float
"""test_northbound_hold_analysis.py — 19 号 §6.3/§6.5 MVP 分析层单元测试。

覆盖：
  1. 增减持金额计算：加仓/减仓/不变/退出（负全仓）/新进（全仓）五态
  2. top 加仓/减仓排名排序与 top_n 截断
  3. 季度净流入 = Σ Δ持股×VWAP（含符号）
  4. 缺 VWAP 标的剔除（宁缺毋错，不虚构金额）
  5. 退化：同季度比较 / 空季度 → ValueError

依据: 19_northbound_hold_snapshot §6.3/§6.5（Δ持股数量 × 当季 VWAP 单公式）
"""

from __future__ import annotations

import pandas as pd
import pytest

from zephyr.data.northbound_hold_analysis import (
    compute_quarter_position_changes,
    estimate_quarterly_net_inflow,
    top_position_changes,
)

Q0 = "2025-12-31"
Q1 = "2026-03-31"


def _snapshot() -> pd.DataFrame:
    rows = [
        # A 加仓 100→150；B 减仓 200→100；C 不变 300→300
        (Q0, "000001.SZ", 100),
        (Q1, "000001.SZ", 150),
        (Q0, "000002.SZ", 200),
        (Q1, "000002.SZ", 100),
        (Q0, "000003.SZ", 300),
        (Q1, "000003.SZ", 300),
        # D 退出（Q1 无记录）；E 新进（Q0 无记录）
        (Q0, "000004.SZ", 50),
        (Q1, "000005.SZ", 80),
    ]
    return pd.DataFrame(rows, columns=["trade_date", "ts_code", "hold_share"])


def _vwap() -> pd.Series:
    return pd.Series(
        {
            "000001.SZ": 10.0,
            "000002.SZ": 20.0,
            "000003.SZ": 30.0,
            "000004.SZ": 5.0,
            "000005.SZ": 8.0,
        }
    )


class TestComputeQuarterPositionChanges:
    def test_five_states(self):
        chg = compute_quarter_position_changes(_snapshot(), Q0, Q1, _vwap())
        m = chg.set_index("ts_code")
        assert m.loc["000001.SZ", "delta_share"] == 50  # 加仓
        assert m.loc["000002.SZ", "delta_share"] == -100  # 减仓
        assert m.loc["000003.SZ", "delta_share"] == 0  # 不变
        assert m.loc["000004.SZ", "delta_share"] == -50  # 退出=负全仓
        assert m.loc["000005.SZ", "delta_share"] == 80  # 新进=全仓

    def test_delta_amount(self):
        chg = compute_quarter_position_changes(_snapshot(), Q0, Q1, _vwap())
        m = chg.set_index("ts_code")["delta_amount"]
        assert m["000001.SZ"] == pytest.approx(500.0)
        assert m["000002.SZ"] == pytest.approx(-2000.0)
        assert m["000004.SZ"] == pytest.approx(-250.0)
        assert m["000005.SZ"] == pytest.approx(640.0)

    def test_sorted_desc_by_amount(self):
        chg = compute_quarter_position_changes(_snapshot(), Q0, Q1, _vwap())
        assert chg["delta_amount"].is_monotonic_decreasing

    def test_missing_vwap_dropped(self):
        vwap = _vwap().drop("000002.SZ")
        chg = compute_quarter_position_changes(_snapshot(), Q0, Q1, vwap)
        assert "000002.SZ" not in set(chg["ts_code"])
        assert len(chg) == 4

    def test_same_quarter_raises(self):
        with pytest.raises(ValueError, match="不同"):
            compute_quarter_position_changes(_snapshot(), Q1, Q1, _vwap())

    def test_empty_quarter_raises(self):
        with pytest.raises(ValueError, match="无记录"):
            compute_quarter_position_changes(_snapshot(), Q0, "2026-06-30", _vwap())


class TestTopPositionChanges:
    def test_top_add_and_reduce(self):
        chg = compute_quarter_position_changes(_snapshot(), Q0, Q1, _vwap())
        tops = top_position_changes(chg, top_n=2)
        assert tops["top_add"]["ts_code"].tolist() == ["000005.SZ", "000001.SZ"]
        assert tops["top_reduce"]["ts_code"].tolist() == ["000002.SZ", "000004.SZ"]

    def test_zero_change_excluded(self):
        chg = compute_quarter_position_changes(_snapshot(), Q0, Q1, _vwap())
        tops = top_position_changes(chg, top_n=10)
        assert "000003.SZ" not in set(tops["top_add"]["ts_code"])
        assert "000003.SZ" not in set(tops["top_reduce"]["ts_code"])


class TestEstimateQuarterlyNetInflow:
    def test_net_inflow_sum(self):
        """净流入 = 500 - 2000 - 250 + 640 = -1110（C 不变不计）。"""
        net = estimate_quarterly_net_inflow(_snapshot(), Q0, Q1, _vwap())
        assert net == pytest.approx(-1110.0)

    def test_all_add_positive(self):
        snap = pd.DataFrame(
            [(Q0, "000001.SZ", 100), (Q1, "000001.SZ", 300)],
            columns=["trade_date", "ts_code", "hold_share"],
        )
        net = estimate_quarterly_net_inflow(snap, Q0, Q1, pd.Series({"000001.SZ": 10.0}))
        assert net == pytest.approx(2000.0)
