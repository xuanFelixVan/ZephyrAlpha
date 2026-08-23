# [BLUEPRINT] MOD-SIG-071 | 待统筹登记（blueprint 未建，真源=缺口总账 GAP-F-15 行）
# [MODULE] tests.signal_ashare.test_index_contribution_decomposer
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.index_contribution_decomposer
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] testing
# [INVARIANTS] 合成数据不触库不触网；pytest filterwarnings=error 兼容
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=贡献度拆解逻辑缺陷
# [TESTS] 本文件
# [A_module] module_id=MOD-SIG-071_test | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-SIG-071 大盘分时贡献度拆解 单元测试（GAP-F-15，合成数据不触库）。

覆盖：3秒快照分钟重采样（末价/空输入/跨分钟）、分钟收益、贡献恒等式
（Σ板块+残差=指数）、等权降级留痕、注入权重归一、缺分钟计 0 贡献、
日聚合榜排序、指数序列不足 degraded、主入口降级链、JSON 可序列化。
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import date, datetime

import pytest

from zephyr.signal_ashare.index_contribution_decomposer import (
    ContributionConfig,
    decompose_index_contribution,
    decompose_intraday_contribution,
    resample_quotes_to_minute,
)

TD = date(2026, 8, 21)


def _quotes() -> list[tuple[datetime, float]]:
    # 3 秒快照：两个分钟桶 + 第三分钟单点
    return [
        (datetime(2026, 8, 21, 9, 31, 3), 3000.0),
        (datetime(2026, 8, 21, 9, 31, 57), 3003.0),  # 09:31 末价 3003
        (datetime(2026, 8, 21, 9, 32, 6), 3006.0),
        (datetime(2026, 8, 21, 9, 32, 54), 3009.0),  # 09:32 末价 3009
        (datetime(2026, 8, 21, 9, 33, 30), 3009.0),  # 09:33 平
    ]


def _sector_series() -> dict[str, list[tuple[str, float]]]:
    return {
        "880201.SH": [("2026-08-21 09:31", 100.0), ("2026-08-21 09:32", 101.0), ("2026-08-21 09:33", 100.5)],
        "880301.SH": [("2026-08-21 09:31", 200.0), ("2026-08-21 09:32", 199.0), ("2026-08-21 09:33", 199.0)],
    }


# ------------------------------------------------------------------
# resample_quotes_to_minute
# ------------------------------------------------------------------


def test_resample_minute_last_price():
    series = resample_quotes_to_minute(_quotes())
    assert series == [
        ("2026-08-21 09:31", 3003.0),
        ("2026-08-21 09:32", 3009.0),
        ("2026-08-21 09:33", 3009.0),
    ]


def test_resample_empty():
    assert resample_quotes_to_minute([]) == []


def test_resample_str_timestamp():
    series = resample_quotes_to_minute([("2026-08-21 09:31:03", 100.0), ("2026-08-21 09:31:59", 101.0)])
    assert series == [("2026-08-21 09:31", 101.0)]


# ------------------------------------------------------------------
# decompose_index_contribution 纯函数核
# ------------------------------------------------------------------


def test_contribution_identity_holds():
    # 恒等式：Σ板块贡献 + 残差 = 指数分钟涨跌（逐分钟）
    result = decompose_index_contribution(
        resample_quotes_to_minute(_quotes()), _sector_series(),
        weights={"880201.SH": 0.6, "880301.SH": 0.4},
    )
    assert result.degraded is False
    for m in result.minutes:
        total = sum(m.sector_contrib_pct.values()) + m.residual_pct
        assert total == pytest.approx(m.index_ret_pct, abs=1e-5)


def test_minute_contribution_values():
    result = decompose_index_contribution(
        resample_quotes_to_minute(_quotes()), _sector_series(),
        weights={"880201.SH": 0.6, "880301.SH": 0.4},
    )
    m1 = result.minutes[0]  # 09:32：指数 3003→3009 = +0.1998%；半导体 +1%，交通 -0.5025%
    assert m1.ts == "2026-08-21 09:32"
    assert m1.sector_contrib_pct["880201.SH"] == pytest.approx(0.6 * 1.0, abs=1e-4)
    assert m1.sector_contrib_pct["880301.SH"] == pytest.approx(0.4 * (-0.5025), abs=1e-3)


def test_equal_weights_degrade_note():
    result = decompose_index_contribution(resample_quotes_to_minute(_quotes()), _sector_series())
    assert result.weight_mode == "equal_weights"
    assert any("等权" in n for n in result.notes)
    w = result.sector_board[0].weight
    assert w == pytest.approx(0.5)


def test_missing_minute_zero_contribution():
    series = _sector_series()
    series["880201.SH"] = series["880201.SH"][:-1]  # 半导体缺 09:33
    result = decompose_index_contribution(
        resample_quotes_to_minute(_quotes()), series, weights={"880201.SH": 1.0},
    )
    last = result.minutes[-1]
    assert "880201.SH" not in last.sector_contrib_pct  # 缺分钟无贡献项
    board = {b.sector_code: b for b in result.sector_board}
    assert board["880201.SH"].covered_minutes == 1


def test_day_board_sorted_and_aggregated():
    result = decompose_index_contribution(
        resample_quotes_to_minute(_quotes()), _sector_series(),
        weights={"880201.SH": 0.6, "880301.SH": 0.4},
    )
    assert result.sector_board[0].sector_code == "880201.SH"  # 正贡献居首
    semi = result.sector_board[0]
    # 日贡献=分钟贡献求和：0.6×1.0% + 0.6×(-0.4950%)
    assert semi.day_contribution_pct == pytest.approx(0.6 * 1.0 + 0.6 * (100.5 / 101.0 - 1) * 100, abs=1e-3)
    assert semi.day_ret_pct == pytest.approx(0.5, abs=1e-3)
    # 全天：指数 3003→3009 +0.1998%；残差=总涨跌-Σ板块贡献
    assert result.total_index_move_pct == pytest.approx((3009.0 / 3003.0 - 1) * 100, abs=1e-3)
    assert result.residual_day_pct == pytest.approx(
        result.total_index_move_pct - sum(b.day_contribution_pct for b in result.sector_board), abs=1e-4,
    )


def test_short_index_series_degraded():
    result = decompose_index_contribution([("2026-08-21 09:31", 3000.0)], _sector_series())
    assert result.degraded is True
    assert result.minutes == []


def test_zero_weight_sum_all_residual():
    result = decompose_index_contribution(
        resample_quotes_to_minute(_quotes()), _sector_series(), weights={"880201.SH": 0.0, "880301.SH": 0.0},
    )
    assert all(m.sector_contrib_pct == {} or all(v == 0 for v in m.sector_contrib_pct.values()) for m in result.minutes)
    assert any("权重和为 0" in n for n in result.notes)


# ------------------------------------------------------------------
# 主入口（注入位 + 降级链）
# ------------------------------------------------------------------


def test_main_entry_injected():
    result = decompose_intraday_contribution(
        TD,
        index_series=resample_quotes_to_minute(_quotes()),
        sector_series=_sector_series(),
        weights={"880201.SH": 0.6, "880301.SH": 0.4},
    )
    assert result.date == "2026-08-21"
    assert result.degraded is False
    assert len(result.minutes) == 2


def test_main_entry_client_unavailable_degraded(monkeypatch):
    monkeypatch.setattr(
        "zephyr.signal_ashare.index_contribution_decomposer._default_client", lambda: None
    )
    result = decompose_intraday_contribution(TD)
    assert result.degraded is True


def test_main_entry_sector_leg_exception_degrade():
    class _Client:
        def execute(self, sql, params):
            if "index_quote" in sql:
                return [(datetime(2026, 8, 21, 9, 31, 0), 3000.0), (datetime(2026, 8, 21, 9, 32, 0), 3003.0)]
            raise RuntimeError("boom")

    result = decompose_intraday_contribution(TD, ch_client=_Client())
    assert result.degraded is False
    assert any("板块腿降级" in n for n in result.notes)
    assert any("重采样" in n for n in result.notes)


def test_main_entry_bad_date_fail_closed():
    with pytest.raises(ValueError):
        decompose_intraday_contribution("08-21", index_series=[], sector_series={})


def test_result_json_serializable():
    result = decompose_intraday_contribution(
        TD, index_series=resample_quotes_to_minute(_quotes()), sector_series=_sector_series(),
    )
    json.dumps(asdict(result), ensure_ascii=False)
