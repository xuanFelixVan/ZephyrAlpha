# [BLUEPRINT] MOD-RES-001 | docs/03_modules/_domain_research/sell_news_event_study/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-RES-001 | layer=test | stability=volatile | safety=L | ai_autonomy=human_gated
# [MODULE] tests.research.test_sell_news_event_study
# [TESTS] src/zephyr/research/sell_news_event_study.py
"""MOD-RES-001 单元测试：sell_news_event_study 高位利好落地事件研究。

合成数据已知答案验证（纯内存，不触网不触真实 CH）：
- 高位组事前 +2%/日 x 20 日、落地后 -1%/日 -> CAR_5=-5% 且 priced_in 成立；
- 对照组全程 0% -> CAR 恒 0；
- 基准 +0.2%/日场景验证 AR=个股收益-基准收益口径；
- 事件日落非交易日 -> T0 顺延次一交易日；
- 配置/输入非法与分组失败 Fail-Closed（ZA-RE-0032）。
"""

from __future__ import annotations

import math

import pandas as pd
import pytest

from zephyr.research.sell_news_event_study import (
    SellNewsStudyConfig,
    SellNewsStudyError,
    run_sell_news_study,
)

_T0: int = 25  # 事件落地交易日索引（事前窗 21 根+事后窗 10 根均满足）
_N_DAYS: int = 40


def _calendar(n: int = _N_DAYS) -> pd.DatetimeIndex:
    return pd.bdate_range("2026-01-05", periods=n)


def _symbol_frame(symbol: str, cal: pd.DatetimeIndex, day_rets: dict[int, float]) -> pd.DataFrame:
    """按"日索引->当日收益"构造收盘价序列（close[0]=100）。"""
    closes = [100.0]
    for d in range(1, len(cal)):
        closes.append(closes[-1] * (1.0 + day_rets.get(d, 0.0)))
    return pd.DataFrame({"symbol": symbol, "date": cal, "close": closes})


def _flat_benchmark(cal: pd.DatetimeIndex, daily_ret: float = 0.0) -> pd.DataFrame:
    closes = [1000.0]
    for _ in range(1, len(cal)):
        closes.append(closes[-1] * (1.0 + daily_ret))
    return pd.DataFrame({"date": cal, "close": closes})


def _main_fixture() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """主场景：5 高位（事前+2%/日，事后-1%/日）+ 5 对照（全程 0%），基准平盘。"""
    cal = _calendar()
    high_rets = {d: 0.02 for d in range(_T0 - 20, _T0)}
    high_rets.update({d: -0.01 for d in range(_T0 + 1, _T0 + 11)})
    frames = [_symbol_frame(f"H{i}", cal, high_rets) for i in range(5)]
    frames += [_symbol_frame(f"C{i}", cal, {}) for i in range(5)]
    event_date = cal[_T0]
    events = pd.DataFrame(
        {
            "symbol": [f"H{i}" for i in range(5)] + [f"C{i}" for i in range(5)],
            "event_date": [event_date] * 10,
            "event_type": ["express_report"] * 5 + ["earnings_forecast"] * 5,
        }
    )
    return events, pd.concat(frames, ignore_index=True), _flat_benchmark(cal)


def _stats_of(report, group: str, horizon: int):
    for s in report.stats:
        if s.group == group and s.horizon == horizon:
            return s
    raise AssertionError(f"缺统计项 group={group} horizon={horizon}")


def test_high_group_priced_in_detected() -> None:
    """已知答案：高位组 CAR_5=-5%、对照组 0 -> 利好出尽成立。"""
    events, prices, benchmark = _main_fixture()
    report = run_sell_news_study(events, prices, benchmark)

    assert report.n_events_input == 10
    assert report.n_events_used == 10
    assert report.n_events_dropped == 0
    assert report.event_type_counts == {"earnings_forecast": 5, "express_report": 5}
    assert report.benchmark_name == "csi_all"
    assert report.pre_return_threshold == pytest.approx(1.02**20 - 1, abs=1e-9)

    high5 = _stats_of(report, "high", 5)
    assert high5.count == 5
    assert high5.mean == pytest.approx(-0.05, abs=1e-12)
    assert high5.median == pytest.approx(-0.05, abs=1e-12)
    assert high5.negative_share == pytest.approx(1.0)
    assert math.isinf(high5.t_stat) and high5.t_stat < 0  # 恒定样本确定性负偏离

    control5 = _stats_of(report, "control", 5)
    assert control5.count == 5
    assert control5.mean == pytest.approx(0.0, abs=1e-12)
    assert control5.negative_share == pytest.approx(0.0)

    assert _stats_of(report, "high", 1).mean == pytest.approx(-0.01, abs=1e-12)
    assert _stats_of(report, "high", 10).mean == pytest.approx(-0.10, abs=1e-12)

    primary = report.primary_verdict
    assert primary.horizon == 5
    assert primary.priced_in is True
    assert primary.significant is True
    assert primary.spread == pytest.approx(-0.05, abs=1e-12)
    assert report.priced_in is True
    assert "priced-in" in report.suggestion


def test_benchmark_subtraction_known_answer() -> None:
    """基准口径：基准 +0.2%/日、个股事后平盘 -> AR=-0.2%/日、CAR_5=-1%。"""
    cal = _calendar()
    high_rets = {d: 0.02 for d in range(_T0 - 20, _T0)}  # 事后 0%/日
    frames = [_symbol_frame(f"H{i}", cal, high_rets) for i in range(3)]
    frames += [_symbol_frame(f"C{i}", cal, {}) for i in range(3)]
    events = pd.DataFrame(
        {
            "symbol": [f"H{i}" for i in range(3)] + [f"C{i}" for i in range(3)],
            "event_date": [cal[_T0]] * 6,
            "event_type": ["express_report"] * 6,
        }
    )
    report = run_sell_news_study(events, pd.concat(frames, ignore_index=True), _flat_benchmark(cal, 0.002))
    assert _stats_of(report, "high", 5).mean == pytest.approx(-0.01, abs=1e-12)
    assert _stats_of(report, "control", 5).mean == pytest.approx(-0.01, abs=1e-12)


def test_event_on_non_trading_day_rolls_to_next_session() -> None:
    """事件日落周六 -> T0 顺延周一；CAR_1 用周二收益（已知答案 +4%）。"""
    cal = _calendar()
    saturday = cal[_T0 - 1] + pd.Timedelta(days=1)  # cal[24]=周五（2026-02-06）-> 周六
    high_rets = {d: 0.02 for d in range(_T0 - 20, _T0)}
    high_rets[_T0 + 1] = 0.04  # T0(周一) 次一日 +4%
    frames = [_symbol_frame(f"H{i}", cal, high_rets) for i in range(2)]
    frames += [_symbol_frame(f"C{i}", cal, {}) for i in range(2)]
    events = pd.DataFrame(
        {
            "symbol": ["H0", "H1", "C0", "C1"],
            "event_date": [saturday] * 4,
            "event_type": ["express_report"] * 4,
        }
    )
    report = run_sell_news_study(events, pd.concat(frames, ignore_index=True), _flat_benchmark(cal))
    assert report.n_events_used == 4
    assert _stats_of(report, "high", 1).mean == pytest.approx(0.04, abs=1e-12)


def test_dropped_events_counted() -> None:
    """未知标的/窗口不足事件剔除并计数，不污染统计。"""
    events, prices, benchmark = _main_fixture()
    extra = pd.DataFrame(
        {
            "symbol": ["UNKNOWN_A", "UNKNOWN_B"],
            "event_date": [events["event_date"].iloc[0]] * 2,
            "event_type": ["express_report"] * 2,
        }
    )
    report = run_sell_news_study(pd.concat([events, extra], ignore_index=True), prices, benchmark)
    assert report.n_events_input == 12
    assert report.n_events_used == 10
    assert report.n_events_dropped == 2


def test_determinism_same_input_same_output() -> None:
    """同输入必同输出（含浮点逐位一致）。"""
    events, prices, benchmark = _main_fixture()
    first = run_sell_news_study(events, prices, benchmark)
    second = run_sell_news_study(events, prices, benchmark)
    assert first == second


def test_invalid_config_fail_closed() -> None:
    """配置非法 Fail-Closed（错误码 ZA-RE-0032）。"""
    events, prices, benchmark = _main_fixture()
    with pytest.raises(SellNewsStudyError) as exc_info:
        run_sell_news_study(events, prices, benchmark, SellNewsStudyConfig(high_quantile=1.5))
    assert exc_info.value.error_code == "ZA-RE-0032"
    with pytest.raises(SellNewsStudyError):
        run_sell_news_study(events, prices, benchmark, SellNewsStudyConfig(pre_window=0))
    with pytest.raises(SellNewsStudyError):
        run_sell_news_study(events, prices, benchmark, SellNewsStudyConfig(horizons=(5, 1)))
    with pytest.raises(SellNewsStudyError):
        run_sell_news_study(events, prices, benchmark, SellNewsStudyConfig(horizons=(3, 0)))


def test_missing_columns_and_empty_events_fail_closed() -> None:
    """必需列缺失/事件清单为空 Fail-Closed。"""
    events, prices, benchmark = _main_fixture()
    with pytest.raises(SellNewsStudyError):
        run_sell_news_study(events.drop(columns=["event_type"]), prices, benchmark)
    empty = events.iloc[0:0]
    with pytest.raises(SellNewsStudyError):
        run_sell_news_study(empty, prices, benchmark)


def test_all_dropped_or_degenerate_groups_fail_closed() -> None:
    """全剔除（事件日越界）与分组退化（事前涨幅零区分度）Fail-Closed。"""
    events, prices, benchmark = _main_fixture()
    future = pd.DataFrame(
        {
            "symbol": [f"H{i}" for i in range(5)] + [f"C{i}" for i in range(5)],
            "event_date": [pd.Timestamp("2027-06-01")] * 10,
            "event_type": ["express_report"] * 10,
        }
    )
    with pytest.raises(SellNewsStudyError):
        run_sell_news_study(future, prices, benchmark)

    cal = _calendar()
    flat_frames = [_symbol_frame(f"F{i}", cal, {}) for i in range(6)]
    flat_events = pd.DataFrame(
        {
            "symbol": [f"F{i}" for i in range(6)],
            "event_date": [cal[_T0]] * 6,
            "event_type": ["express_report"] * 6,
        }
    )
    with pytest.raises(SellNewsStudyError):
        run_sell_news_study(flat_events, pd.concat(flat_frames, ignore_index=True), benchmark)


def test_control_group_not_priced_in() -> None:
    """反向已知答案：高位组事后继续上行 -> priced_in 不成立。"""
    cal = _calendar()
    high_rets = {d: 0.02 for d in range(_T0 - 20, _T0)}
    high_rets.update({d: 0.01 for d in range(_T0 + 1, _T0 + 11)})  # 事后继续 +1%/日
    frames = [_symbol_frame(f"H{i}", cal, high_rets) for i in range(5)]
    frames += [_symbol_frame(f"C{i}", cal, {}) for i in range(5)]
    events = pd.DataFrame(
        {
            "symbol": [f"H{i}" for i in range(5)] + [f"C{i}" for i in range(5)],
            "event_date": [cal[_T0]] * 10,
            "event_type": ["express_report"] * 10,
        }
    )
    report = run_sell_news_study(events, pd.concat(frames, ignore_index=True), _flat_benchmark(cal))
    assert report.priced_in is False
    assert report.primary_verdict.priced_in is False
    assert "不建议" in report.suggestion
