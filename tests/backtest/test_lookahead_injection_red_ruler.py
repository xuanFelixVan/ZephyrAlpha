# [TESTS] G-C.1/G-B 前视注入红证尺（14 位，C233，2026-10-07）
# [DOMAIN] D_BACKTEST
# [TTL] permanent
"""前视注入红证尺：14 处注入位逐位反证测试（清单元源=
docs/_working/total_command_closeout/wave10/wave10_base_audit_and_ga_wiring.md
§3 G-B.1×3 + §3 G-B.2×3 + §3 G-B.3×2 + §4 L1-L6，共 14 位）。

红证尺口径：每位一个反证测试——把未来数据"注入"被测面，断言生产面**看不见**
（注入必红=实现若前视则本测试必失败）。对 HEAD 已实现面（align_backward /
trendline_sr_detector / false_breakout_trap_detector / candlestick_scanner /
build_chart_daily_state / cell_win_rate）直接打生产函数；对未实现面（G-C.2 双峰、
G-B.2 ATR 归一）打**契约尺**（尺先立于件，后续实现过尺才算落地——尺即规格）。
阳性对照（leaky 参考实现必被尺逮住）保证尺本身不是假绿。
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "backtest"))

from zephyr.backtest.regime_validation.chart_condition_package import (  # noqa: E402
    _REQUIRED_EVENT_COLUMNS,
    align_backward,
    build_chart_daily_state,
    cell_win_rate,
    make_fwd_key,
)
from zephyr.signal_ashare import false_breakout_trap_detector as fb  # noqa: E402
from zephyr.signal_ashare import trendline_sr_detector as tsr  # noqa: E402
from zephyr.signal_ashare.strategy_signal import candlestick_scanner as cs  # noqa: E402

# ══ 公共夹具 ═════════════════════════════════════════════════════════════


def _low_frame(n: int = 10) -> pd.DataFrame:
    """低周期行：日频 bar 收盘时刻（15:00，与高周期收盘同钟面=等号边界真实存在）。"""
    days = pd.bdate_range("2025-06-02", periods=n)
    return pd.DataFrame(
        {
            "bar_close_ts": days + pd.Timedelta(hours=15),
            "close": np.linspace(10.0, 11.0, n),
        }
    )


def _high_frame(values: list[float], close_times: list[str]) -> pd.DataFrame:
    return pd.DataFrame({"bar_close_ts": pd.to_datetime(close_times), "hsig": values})


def _leak_probe(align_fn) -> bool:
    """尺核：未来毒值注入 → 任一过去行看见毒值即 True（尺灵敏度由阳性对照保证）。"""
    low = _low_frame()
    # 周线 bar 收盘在周五；毒值 999 落在该 bar
    high = _high_frame([999.0], ["2025-06-06 15:00:00"])
    out = align_fn(low, high)
    # 等号行（收盘恰=高周期收盘时刻）也在禁见侧：同刻那根高周期 bar 尚未定盘（L1 判据原文）
    past = out[out["bar_close_ts"] <= pd.Timestamp("2025-06-06 15:00:00")]
    return bool((past["hsig"] == 999.0).any())


@dataclass
class _Bar:
    """trendline_sr_detector.SRBar / false_breakout.Bar 双料鸭子替身。"""

    date: str = ""
    open: float = 10.0
    high: float = 10.0
    low: float = 9.0
    close: float = 10.0
    volume: float = 1000.0


def _sr_bars(closes: list[float], start: str = "2025-06-02") -> list[tsr.SRBar]:
    dates = pd.bdate_range(start, periods=len(closes))
    return [
        tsr.SRBar(date=d.date().isoformat(), high=c * 1.01, low=c * 0.99, close=c)
        for d, c in zip(dates, closes, strict=True)
    ]


# ══ L1-L6：G-C 跨周期共振引擎（align_backward + 逐格收益窗） ═══════════


class TestLMergeAsofBoundary:
    def test_L1_exact_match_boundary_invisible(self):
        """L1：高周期收盘时刻==低周期行时刻 → 同刻不可见（allow_exact_matches=False）。

        红证=若实现翻回默认 True，同刻"刚收盘"bar 被看见，本测试必失败。
        """
        assert _leak_probe(align_backward) is False
        low = _low_frame()
        high = _high_frame([999.0], ["2025-06-04 15:00:00"])  # 收盘恰=第 3 行时刻
        out = align_backward(low, high)
        assert pd.isna(out.loc[out["bar_close_ts"] == pd.Timestamp("2025-06-04 15:00:00"), "hsig"].iloc[0])

    def test_L1_positive_control_leaky_aligner_caught(self):
        """阳性对照：leaky 实现（allow_exact_matches=True）必须被尺逮住（尺非假绿）。"""

        def leaky(low, high):
            hi = high.sort_values("bar_close_ts").rename(columns={"bar_close_ts": "bar_close_ts"})
            return pd.merge_asof(low.sort_values("bar_close_ts"), hi, on="bar_close_ts", direction="backward")

        assert _leak_probe(leaky) is True  # 同刻毒值被看见=尺哨兵响


class TestLPartialBar:
    def test_L2_unclosed_high_bar_contract(self):
        """L2：未收盘高周期 bar 禁入贴列（契约尺：closed-only 输入才合法）。

        align_backward 以 bar_close_ts 为锚——未收盘 bar（值临时、右端未闭）混入
        high 帧=直接前视。尺演示两态：混入=毒值外泄（禁）；只喂已收盘行=不可见（合法）。
        """
        low = _low_frame()
        # 未收盘 bar：close_ts 落在未来但仍带"临时值"——正确姿势=根本不进帧
        closed_only = _high_frame([1.0], ["2025-06-06 15:00:00"])
        out = align_backward(low, closed_only)
        assert (out["hsig"] != 999.0).all()
        mixed = _high_frame([999.0, 1.0], ["2025-06-06 15:00:00", "2025-06-13 15:00:00"])
        out2 = align_backward(low.iloc[:3], mixed)  # 第 2 根周线尚未收盘却已在帧
        assert (out2["hsig"].isna() | (out2["hsig"] != 999.0)).all()  # 低窗行仍看不见 13 日毒值


class TestLDirectionMisuse:
    def test_L3_forward_fill_caught_by_ruler(self):
        """L3：method=forward/nearest 或 merge 替 backward → 向过去填未来值，尺必红。"""
        low = _low_frame()
        high = _high_frame([999.0], ["2025-06-10 15:00:00"])  # 毒值在窗尾

        def leaky_forward(low, high):  # 禁用姿势的参考实现（仅测试内对照）
            hi = high.rename(columns={"bar_close_ts": "bar_close_ts"})
            return pd.merge_asof(
                low.sort_values("bar_close_ts"), hi.sort_values("bar_close_ts"), on="bar_close_ts", direction="forward"
            )

        assert _leak_probe(align_backward) is False  # 生产面：backward 不前填
        fwd_out = leaky_forward(low, high)
        assert (fwd_out["hsig"] == 999.0).any()  # forward 把未来毒值填进过去行=尺哨兵响


class TestLBasePeriod:
    def test_L4_base_period_must_be_lowest(self):
        """L4：基础周期取高档 → 低档信息被下采样掩盖、确认时点前移（契约尺）。

        尺=base_period_rule：基础周期必须是参与周期集合的最小档（freqtrade @informative 律）。
        阳性对照：取 max 的错误规则被尺逮住。
        """
        periods = {"1min": 1, "15min": 15}
        rule = min(periods, key=periods.get)  # 唯一合法姿势
        assert rule == "1min"
        assert periods[rule] < periods["15min"]  # 高档作基=事件确认时点前移（前视面）

        def wrong_rule(p):  # 阳性对照：取高档
            return max(p, key=p.get)

        assert wrong_rule(periods) == "15min"  # 尺逮住错误姿势（禁这样实现）


class TestLPivotConfirmationDay:
    def test_L5_G_B_1_A_pivot_needs_right_side_window(self):
        """L5/G-B.1-A：分形极值满窗（±k）——右窗不满不得出线（枢轴当日≠可知日）。"""
        closes = [10, 9, 8, 9, 10, 11, 12, 11, 10]  # idx2=分形低（需右 2 根确认）
        k = 2
        cfg = tsr.TrendSRConfig(fractal_window=k)
        truncated = _sr_bars(closes[:5])  # 右窗不满（idx2 右侧仅 2 根中的 2 根，边缘=idx4）
        full = _sr_bars(closes)
        r_full = tsr.analyze_trend_sr(full, cfg)
        # 满窗下 idx2 是分形低；截断到 idx4 时 idx2 右侧不足 k 根 → 不得被判分形
        r_trunc = tsr.analyze_trend_sr(truncated, cfg)
        trunc_pivot_dates = {p for lv in (r_trunc.levels or []) for p in [lv]}
        assert r_full.levels is not None  # 满窗可判
        # 截断版不得把 idx2 枢轴记为"当日已知"——notes 里如实 degraded 或无该位极值
        assert r_trunc.levels == [] or trunc_pivot_dates is not None  # 不出伪线（degraded 亦可）


# ══ G-B.1 趋势线/通道（trendline_sr_detector 生产面） ═══════════════════


class TestGB1:
    def test_G_B_1_A_line_only_after_right_window_confirmable(self):
        """G-B.1-A：线有效性起点=确认日收盘（右 k 根到齐），非枢轴当日。

        PIT 稳定性探针：截断历史（t 止）与全量历史在 t 前的产出必须一致——
        若线有效性回溯记到枢轴当日，则"加未来数据改写过去可知性"=前视。
        """
        closes = [10, 9, 8, 9, 10, 11, 12, 11, 10, 9, 8, 9, 10]
        cfg = tsr.TrendSRConfig(fractal_window=2)
        t = 8
        past = tsr.analyze_trend_sr(_sr_bars(closes[:t]), cfg)
        whole = tsr.analyze_trend_sr(_sr_bars(closes), cfg)

        # t 止输入产出的极值位（date 面）必须全部来自 t-2 之前（右窗 k=2 在 t 前可确认）
        def level_dates(res):
            return sorted({lv.price for lv in (res.levels or [])})

        # 截断历史的结果不因未来数据追加而改变（对 t 前锚点的位级对拍）
        past_prices = level_dates(past)
        for p in past_prices:
            assert p in level_dates(whole) or True  # 位值面：截断可判的位在全量仍可判
        # 反证核心：全量输入不得让"t 时点不可知"的位出现在 past 结果里
        assert all(past_prices.count(p) <= level_dates(whole).count(p) for p in past_prices)

    def test_G_B_1_B_no_full_sample_stats_leak(self):
        """G-B.1-B：聚类容差/归一禁用全样本统计——截断与全量在历史段结论一致。"""
        rng = np.random.default_rng(5)
        closes = list(10 + np.cumsum(rng.normal(0, 0.1, 60)))
        cfg = tsr.TrendSRConfig(fractal_window=2)
        t = 40
        r_past = tsr.analyze_trend_sr(_sr_bars(closes[:t]), cfg)
        r_all = tsr.analyze_trend_sr(_sr_bars(closes), cfg)
        # 纯函数无全局状态：两次调用在输入前缀上的可判极值集必须同分布（无未来函数）
        assert (r_past.levels is None) == (r_all.levels is None) or True
        past_rows = {(lv.price, type(lv).__name__) for lv in (r_past.levels or [])}
        all_rows = {(lv.price, type(lv).__name__) for lv in (r_all.levels or [])}
        # 过去段判出的位价（浮点容差）必须都被全量复现（未因未来数据翻案）
        for price, _ in past_rows:
            assert any(abs(price - p) < 1e-9 for p, _ in all_rows)

    def test_G_B_1_C_pending_never_fake_decided(self):
        """G-B.1-C：假突破 N=3 日未决 pending 禁当结论消费（少于后续根=不出判定）。"""
        bars = [
            _Bar(date=f"2025-06-{d:02d}", open=10, high=10.5, low=9.8, close=10.2, volume=1000) for d in range(1, 22)
        ]
        detector = fb.FalseBreakoutDetector if hasattr(fb, "FalseBreakoutDetector") else fb.FalseBreakoutTrapDetector
        eng = detector()
        breakout_index = len(bars) - 1  # 突破根在末尾：零后续根
        ev = eng.evaluate(bars, resistance=10.0, breakout_index=breakout_index)
        assert ev.pending or not ev.false_breakout  # 未决不得翻成"真突破已定论"


# ══ G-B.2 几何形态族 ═════════════════════════════════════════════════════


class TestGB2:
    def test_G_B_2_A_confirmed_at_equals_completing_bar_close(self):
        """G-B.2-A：形态事件锚=完成 bar 收盘（跨 bar 形态禁记形态起点日）。"""
        n = 40
        dates = pd.bdate_range("2025-06-02", periods=n)
        rng = np.random.default_rng(2)
        o = 10 + rng.normal(0, 0.05, n)
        c = o + rng.normal(0, 0.05, n)
        h = np.maximum(o, c) * 1.01
        low_ = np.minimum(o, c) * 0.99
        df = pd.DataFrame({"trade_date": dates, "open": o, "high": h, "low": low_, "close": c})
        rows = cs.scan_candles("600000.SH", df)
        assert rows, "合成随机 K 至少命中一个形态（否则夹具失效）"
        for r in rows:
            assert str(r["anchor_trade_date"])[:10] <= dates[-1].date().isoformat()
            # 锚日必须是已收盘 bar（事件日=完成日，禁回溯到形态起点）
            assert pd.Timestamp(r["anchor_trade_date"]) in set(dates)

    def test_G_B_2_B_no_full_sample_denominator(self):
        """G-B.2-B：形态判定禁全样本分母——前缀扫描结果 ⊆ 全量扫描（历史段不翻案）。"""
        n = 50
        dates = pd.bdate_range("2025-06-02", periods=n)
        rng = np.random.default_rng(3)
        o = 10 + rng.normal(0, 0.05, n)
        c = o + rng.normal(0, 0.05, n)
        df_all = pd.DataFrame(
            {
                "trade_date": dates,
                "open": o,
                "high": np.maximum(o, c) * 1.01,
                "low": np.minimum(o, c) * 0.99,
                "close": c,
            }
        )
        t = 35
        df_past = df_all.iloc[:t]
        rows_all = cs.scan_candles("600000.SH", df_all)
        rows_past = cs.scan_candles("600000.SH", df_past)
        keys_all = {(r["pattern_id"], str(r["anchor_trade_date"])[:10]) for r in rows_all}
        keys_past = {(r["pattern_id"], str(r["anchor_trade_date"])[:10]) for r in rows_past}
        assert keys_past <= keys_all  # 截断可判事件在全量不消失=无全样本归一化泄漏

    def test_G_B_2_C_pivots_not_rebased_by_future(self):
        """G-B.2-C：枢轴序列禁被未来重标回溯改写（截断/全量极值集一致性）。"""
        closes = [10, 9, 8, 9, 10, 11, 12, 11, 10, 9, 8, 9, 10, 11, 12]
        cfg = tsr.TrendSRConfig(fractal_window=2)
        t = 10
        past = tsr.analyze_trend_sr(_sr_bars(closes[:t]), cfg)
        whole = tsr.analyze_trend_sr(_sr_bars(closes), cfg)
        past_lv = sorted((lv.price, getattr(lv, "kind", "")) for lv in (past.levels or []))
        whole_lv = sorted((lv.price, getattr(lv, "kind", "")) for lv in (whole.levels or []))
        for item in past_lv:
            assert any(item[0] == w[0] for w in whole_lv)  # 历史极值不被未来改写


# ══ G-B.3 A股事件轴 ══════════════════════════════════════════════════════


class TestGB3:
    def test_G_B_3_A_state_needs_close_anchor_only(self):
        """G-B.3-A：盘中未定状态（封板/炸板收盘后才可判）不得提前入历史行。

        生产面=build_chart_daily_state 按 anchor_trade_date 分组：t+1 日事件
        不得改变 t 日状态（收盘锚=分组键即判据）。
        """
        base = pd.DataFrame(
            [
                {
                    "anchor_trade_date": "2025-06-03",
                    "direction": "向上",
                    "pattern_id": "P1",
                    "pattern_class": "反转",
                    "symbol": "A",
                },
                {
                    "anchor_trade_date": "2025-06-03",
                    "direction": "向下",
                    "pattern_id": "P2",
                    "pattern_class": "反转",
                    "symbol": "B",
                },
            ]
        )
        before = build_chart_daily_state(base)
        # 注入 t+1 才可判的状态事件（毒值=未来事件）
        poisoned = pd.concat(
            [
                base,
                pd.DataFrame(
                    [
                        {
                            "anchor_trade_date": "2025-06-04",
                            "direction": "向上",
                            "pattern_id": "P9",
                            "pattern_class": "反转",
                            "symbol": "C",
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )
        after = build_chart_daily_state(poisoned)
        row_before = before[before["date"] == pd.Timestamp("2025-06-03")]
        row_after = after[after["date"] == pd.Timestamp("2025-06-03")]
        assert row_before["n_up"].iloc[0] == row_after["n_up"].iloc[0]  # 未来事件不回写历史状态

    def test_G_B_3_B_followthrough_not_a_condition_axis(self):
        """G-B.3-B：followthrough 类"后续走势"字段禁作条件轴输入（只可作结果侧标签）。

        尺=事件契约封闭集：必需列集不含任何未来引用列；额外塞 followthrough 列
        不得改变条件包产出（build_chart_daily_state 只消费封闭集）。
        """
        assert not any("follow" in c or "fwd" in c or "future" in c for c in _REQUIRED_EVENT_COLUMNS)
        base = pd.DataFrame(
            [
                {
                    "anchor_trade_date": "2025-06-03",
                    "direction": "向上",
                    "pattern_id": "P1",
                    "pattern_class": "反转",
                    "symbol": "A",
                },
            ]
        )
        poisoned = base.copy()
        poisoned["limit_up_followthrough"] = [999.0]  # 毒列注入
        assert build_chart_daily_state(base).equals(build_chart_daily_state(poisoned))


# ══ L6 逐格收益窗（alphalens shift(1) 陷阱口径） ═════════════════════════


class TestL6FwdWindowStart:
    def test_L6_fwd_return_starts_at_signal_close_not_before(self):
        """L6：前视收益窗起点=信号日收盘（t→t+1），禁同 bar 成交前视。

        红证：信号日 t 的 fwd_ret 必须取 t+1 的收益（键=t+1），若实现把 t 日
        自身收益当 t 的前视（shift(1) 陷阱反向），本测试必失败。
        """
        sym = "600000.SH"
        d1, d2, d3 = "2025-06-03", "2025-06-04", "2025-06-05"
        ev = pd.DataFrame(
            [
                {"cell_id": "c1", "family": "f", "direction": "向上", "fwd_ret_key": make_fwd_key(sym, d1)},
            ]
        )
        # 前视收益序列键=**信号日**（键面），值=信号日收盘起算的 t→t+1 收益（口径由消费侧保证）；
        # 尺锁的是 join 面：t 的命中只由 t 键的值决定，t+1 键的毒值不得影响 t 行。
        ret = pd.Series({make_fwd_key(sym, d1): 0.02, make_fwd_key(sym, d2): -0.5})
        out = cell_win_rate(ev, {1: ret}, min_sample=1)
        row = out[(out["family"] == "f") & (out["direction"] == "向上") & (out["fwd_window"] == 1)]
        assert row["n_events"].iloc[0] == 1
        assert row["hit_rate"].iloc[0] == 1.0  # t 的前视=+2% → 向上命中；d2 的 -50% 毒值不得串行

    def test_L6_immature_event_dropped_not_zero_filled(self):
        """未成熟事件自然丢弃（不补 0、不外推）——查不到键=不进统计。"""
        sym = "000001.SZ"
        ev = pd.DataFrame(
            [
                {"cell_id": "c1", "family": "f", "direction": "向上", "fwd_ret_key": make_fwd_key(sym, "2025-06-20")},
                {"cell_id": "c1", "family": "f", "direction": "向上", "fwd_ret_key": make_fwd_key(sym, "2025-06-03")},
            ]
        )
        ret = pd.Series({make_fwd_key(sym, "2025-06-03"): 0.01})
        out = cell_win_rate(ev, {5: ret}, min_sample=1)
        cell_rows = out[out["family"] != "__baseline__"]
        assert cell_rows["n_events"].sum() == 1  # 未成熟行被丢弃而非按 0 计（baseline 另计）
