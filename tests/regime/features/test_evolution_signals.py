# [A_test] module_id: MOD-TEST-EVO-SIGNALS | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §4.6
# [MODULE] tests.regime.features.test_evolution_signals
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.regime.features.evolution_signals; pandas; numpy; pytest
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError->fail
# [TESTS] tests/regime/features/test_evolution_signals.py
# [TTL] permanent
# [ARCH-REF] #14_regime_s2_diagnosis §4.6 演进方向 #3 滞回触发器 / #5 EVR / #6 flush
# [ALGO_FLOW]
# 层: 输入
# - I1: 衰减信号 Series（滞回）/ OHLCV 五序列（EVR、flush）
# 层: 算法
# - A1: hysteresis_edge_trigger 双阈值状态机（>=enter 置 1，<=exit 置 0，区间保持）
# - A2: s2_evr_score 四分量取 max：EVR 核心(60)/ADL 经典背离(80)/吸筹脉冲(70)/隐形吸筹(50)
# - A3: s2_flush_flag 四条件合取：N日新低+收盘回前日区间+下影>50%+量>2x均量
# 层: 输出
# - O1: 滞回状态 Series{0,1} / EVR 评分 0-100 / flush flag{0,1}
"""test_evolution_signals.py — 14 号 §4.6 演进方向小型组（滞回/EVR/flush）单元测试。

覆盖：
  1. 滞回边沿触发器：阈值附近震荡不再反复触发（arXiv:2606.19386 实证语义）；
     边界 enter<=exit 拒绝 / NaN 保持状态 / 空序列
  2. EVR：核心（量>1.6x+平盘）/ ADL 经典背离（价新低+ADL 更高低+收盘位置改善）/
     吸筹脉冲（大跌日 ADL 暴增）/ 隐形吸筹（价阴跌 7-10 日 ADL 走平微升）；无信号=0
  3. flush：四条件共振=1；缺任一条件=0；预热期=0

依据: 14_regime_s2_diagnosis v0.5.2 §4.6 #3/#5/#6
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.regime.features.evolution_signals import (
    hysteresis_edge_trigger,
    s2_evr_score,
    s2_flush_flag,
)

# ---------------------------------------------------------------------------
# 1. 滞回边沿触发器
# ---------------------------------------------------------------------------


class TestHysteresisEdgeTrigger:
    def test_flickering_signal_suppressed(self):
        """阈值附近震荡：普通阈值触发 6 次跳变，滞回仅 2 次（进 1 次 + 出 1 次）。"""
        sig = pd.Series([55.0, 62.0, 58.0, 62.0, 58.0, 39.0, 55.0, 62.0])
        state = hysteresis_edge_trigger(sig, enter=60.0, exit=40.0)
        assert state.tolist() == [0.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0]
        plain = (sig >= 60.0).astype(float)
        assert plain.diff().abs().sum() > state.diff().abs().sum()

    def test_never_reaches_enter_stays_zero(self):
        sig = pd.Series([10.0, 59.9, 50.0])
        assert (hysteresis_edge_trigger(sig) == 0.0).all()

    def test_exit_crossed_only_below(self):
        """40 < signal < 60 区间保持；恰好 40 解除（<=exit）。"""
        sig = pd.Series([70.0, 45.0, 40.0, 55.0])
        state = hysteresis_edge_trigger(sig, enter=60.0, exit=40.0)
        assert state.tolist() == [1.0, 1.0, 0.0, 0.0]

    def test_nan_holds_state(self):
        sig = pd.Series([70.0, np.nan, 55.0, np.nan, 30.0])
        state = hysteresis_edge_trigger(sig, enter=60.0, exit=40.0)
        assert state.tolist() == [1.0, 1.0, 1.0, 1.0, 0.0]

    def test_enter_le_exit_raises(self):
        with pytest.raises(ValueError, match="enter"):
            hysteresis_edge_trigger(pd.Series([1.0]), enter=40.0, exit=60.0)

    def test_empty_series(self):
        out = hysteresis_edge_trigger(pd.Series(dtype=float))
        assert len(out) == 0


# ---------------------------------------------------------------------------
# 共用 OHLCV 构造
# ---------------------------------------------------------------------------


def _bar(o: float, h: float, l: float, c: float, v: float) -> dict:
    return {"open": o, "high": h, "low": l, "close": c, "volume": v}


def _flat_bars(n: int, close: float = 100.0, volume: float = 1000.0) -> list[dict]:
    """平盘 bar（mfm≈0，ADL 走平）：high=close+0.5 / low=close-0.5 / open=close。"""
    return [_bar(close, close + 0.5, close - 0.5, close, volume) for _ in range(n)]


def _to_ohlcv(bars: list[dict]) -> dict[str, pd.Series]:
    df = pd.DataFrame(bars, dtype=float)
    return {c: df[c] for c in ("open", "high", "low", "close", "volume")}


class TestEvrScore:
    def test_evr_core_tiny_body_huge_volume(self):
        """EVR 核心：量 >1.6×均量 + 实体极小（平盘）→ 60（主力暗中吸筹）。"""
        bars = _flat_bars(260)
        # 末 bar：量 3000（>1.6×1000），实体 |100.05-100|/100≈0.05% 平盘
        bars.append(_bar(100.0, 100.8, 99.5, 100.05, 3000.0))
        d = _to_ohlcv(bars)
        s = s2_evr_score(d["open"], d["high"], d["low"], d["close"], d["volume"])
        assert s.iloc[-1] == 60

    def test_no_signal_flat_market(self):
        bars = _flat_bars(120)
        d = _to_ohlcv(bars)
        s = s2_evr_score(d["open"], d["high"], d["low"], d["close"], d["volume"])
        assert (s == 0).all()

    def test_adl_classic_divergence(self):
        """ADL 经典背离：价格新低 + ADL 更高低 + 收盘位置改善至上 50% → 80。"""
        bars = _flat_bars(240)
        # 第一谷 bar240：收近低位（mfm<0，ADL 下挫），收盘位置 0.33（下 25% 区间外沿）
        bars.append(_bar(95.5, 96.0, 94.5, 95.0, 1500.0))
        # 修复 bar241-250：每日收近高位（mfm>0，ADL 持续回升），价格回到 98
        price = 95.0
        for _ in range(10):
            price += 0.3
            bars.append(_bar(price - 0.2, price + 0.3, price - 0.6, price, 1200.0))
        # 第二谷 bar251-259：价格跌破前低（94 < 95）但每日收近高位+放量（ADL 更高低）
        price = 98.0
        for i in range(9):
            price -= 0.45
            # 收近当日高位：close 位置 > 0.5
            bars.append(_bar(price - 0.1, price + 0.4, price - 0.8, price + 0.3, 1500.0))
        d = _to_ohlcv(bars)
        s = s2_evr_score(d["open"], d["high"], d["low"], d["close"], d["volume"])
        assert s.iloc[-1] == 80

    def test_adl_accumulation_pulse(self):
        """吸筹脉冲：大跌日（<-3%）ADL 暴增（收近高位+巨量）→ 70。"""
        bars = _flat_bars(250)
        bars.append(_bar(104.5, 105.0, 103.5, 104.0, 1000.0))   # bar250 抬高基准
        # bar251：大跌 -3.85% 但收近当日高位 + 巨量 → mfm≈0.89×20000，ADL 暴增
        bars.append(_bar(95.0, 100.4, 93.0, 100.0, 20000.0))
        d = _to_ohlcv(bars)
        s = s2_evr_score(d["open"], d["high"], d["low"], d["close"], d["volume"])
        assert s.iloc[-1] == 70

    def test_adl_hidden_accumulation(self):
        """隐形吸筹：价格阴跌 7-10 日 + ADL 走平/微升 → 50。"""
        # 前置构造一个更低的价格低点（bar200 附近 98.0）防误判经典背离（price_ll 须 False）
        bars = _flat_bars(180)
        bars.append(_bar(98.5, 99.0, 97.8, 98.0, 1500.0))       # bar180 深谷 98.0
        price = 98.0
        for _ in range(70):                                      # 回升到 100.5
            price += 0.036
            bars.append(_bar(price, price + 0.5, price - 0.5, price, 1000.0))
        # 8 日阴跌（每日 -0.2）但每日收近高位（mfm>0）→ ADL 微升
        for _ in range(8):
            price -= 0.2
            bars.append(_bar(price + 0.3, price + 0.5, price - 1.0, price, 1000.0))
        d = _to_ohlcv(bars)
        s = s2_evr_score(d["open"], d["high"], d["low"], d["close"], d["volume"])
        assert s.iloc[-1] == 50

    def test_score_series_no_nan(self):
        bars = _flat_bars(80)
        d = _to_ohlcv(bars)
        s = s2_evr_score(d["open"], d["high"], d["low"], d["close"], d["volume"])
        assert not s.isna().any()


# ---------------------------------------------------------------------------
# 3. flush 桥接信号
# ---------------------------------------------------------------------------


class TestFlushFlag:
    def _base(self, n: int = 260) -> list[dict]:
        return _flat_bars(n)

    def test_flush_all_conditions(self):
        """四条件共振：N日新低 + 收盘回前日区间 + 下影>50% + 量>2x均量 → 1。"""
        bars = self._base()
        # 前一日：常规 bar（low=99.5, high=100.5）
        # flush 日：low 98 创 60 日新低；close=100 回前日区间 [99.5,100.5]；
        # 下影 (min(99,100)-98)/(101-98)=1/3... 需>0.5：open=100, close=100, low=98, high=100.5
        # → 下影 (100-98)/(100.5-98)=2/2.5=0.8>0.5；量 3000>2×1000
        bars.append(_bar(100.0, 100.5, 98.0, 100.0, 3000.0))
        d = _to_ohlcv(bars)
        f = s2_flush_flag(d["open"], d["high"], d["low"], d["close"], d["volume"])
        assert f.iloc[-1] == 1.0

    def test_no_new_low_no_flush(self):
        bars = self._base()
        bars.append(_bar(100.0, 100.5, 99.6, 100.0, 3000.0))  # low 99.6 未创新低
        d = _to_ohlcv(bars)
        f = s2_flush_flag(d["open"], d["high"], d["low"], d["close"], d["volume"])
        assert f.iloc[-1] == 0.0

    def test_close_not_recovered_no_flush(self):
        bars = self._base()
        # close 98.5 < 前日 low 99.5（未收回前日区间）
        bars.append(_bar(100.0, 100.5, 98.0, 98.5, 3000.0))
        d = _to_ohlcv(bars)
        f = s2_flush_flag(d["open"], d["high"], d["low"], d["close"], d["volume"])
        assert f.iloc[-1] == 0.0

    def test_short_wick_no_flush(self):
        bars = self._base()
        # 下影 (min(99.0,99.6)-98)/(100.5-98)=1.0/2.5=0.4 < 0.5；其余三条件均满足
        bars.append(_bar(99.0, 100.5, 98.0, 99.6, 3000.0))
        d = _to_ohlcv(bars)
        f = s2_flush_flag(d["open"], d["high"], d["low"], d["close"], d["volume"])
        assert f.iloc[-1] == 0.0

    def test_normal_volume_no_flush(self):
        bars = self._base()
        bars.append(_bar(100.0, 100.5, 98.0, 100.0, 1200.0))  # 量不足 2x
        d = _to_ohlcv(bars)
        f = s2_flush_flag(d["open"], d["high"], d["low"], d["close"], d["volume"])
        assert f.iloc[-1] == 0.0

    def test_warmup_no_flush(self):
        bars = _flat_bars(30)
        bars.append(_bar(100.0, 100.5, 98.0, 100.0, 3000.0))
        d = _to_ohlcv(bars)
        f = s2_flush_flag(d["open"], d["high"], d["low"], d["close"], d["volume"], window=60)
        assert (f == 0.0).all()
