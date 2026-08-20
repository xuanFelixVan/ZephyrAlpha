# [A_test] module_id: MOD-TEST-S2-THREE-YANG | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §4 P1-E9e
# [MODULE] tests.regime.features.test_s2_three_yang_flag
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.regime.features.overlay_features; pandas; numpy; pytest
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError->fail
# [TESTS] tests/regime/features/test_s2_three_yang_flag.py
# [TTL] permanent
# [ARCH-REF] #P1-E9e #14_regime_s2_diagnosis §4.4b
# [ALGO_FLOW]
# 层: 输入
# - I1: OHLCV 五序列 + window=60（位置判定窗）
# 层: 算法
# - A1: 6 维判定（实体递增 1.5×/开盘在前根实体内/上影≤5%/量能递增+第三根2×均量/
#       位置 60 日跌幅>30%/失效总涨幅>15%）
# - A2: 分级 0/1/2/3（1=弱缺量能 / 2=标准 / 3=三个白武士 实体2×+近乎光头）
# 层: 输出
# - O1: pd.Series ∈ {0,1,2,3}（strong_confirm 门槛 ≥2）
"""test_s2_three_yang_flag.py — P1-E9e 红三兵 6 维量化分级单元测试。

覆盖（14_regime_s2_diagnosis §4.4b + §4.5 step 1 stub 要求）：
  1. 6 维全达标 + 量能确认 → 2（标准红三兵）
  2. 缺量能确认 → 1（弱红三兵）；三个白武士（实体 2×+光头）→ 3
  3. 三种假红三兵排除：高位（未跌 30%）→ 0 / 下跌中继（非 3 阳或位置不符）→ 0 /
     缩量 → 1（不到 2）
  4. 失效：三根总涨幅 >15% → 0（动能透支）
  5. 维度单项破坏：非 3 阳 / 实体不递增 / 开盘跳空 / 上影过长 → 0
  6. warmup / 常态全 0

依据: 14_regime_s2_diagnosis v0.4.5 §4.4b / §4.5
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from zephyr.regime.features.overlay_features import s2_three_yang_flag

# ---------------------------------------------------------------------------
# 辅助
# ---------------------------------------------------------------------------

_N = 70


def _decline_base(n: int = _N) -> dict[str, np.ndarray]:
    """底部位置：前 60 日 3000→1500 线性下跌（60 日跌幅 50%>30%），量恒 1e8。"""
    close = np.linspace(3000.0, 1500.0, n)
    return {
        "open": close * 1.001,
        "high": close * 1.002,
        "low": close * 0.999,
        "close": close,
        "volume": np.full(n, 1e8),
    }


def _set_yang(d: dict[str, np.ndarray], i: int, o: float, c: float, v: float) -> None:
    """设置第 i 日为近光头阳线（上影≈0）。"""
    d["open"][i] = o
    d["close"][i] = c
    d["high"][i] = c + (c - o) * 0.01  # 上影 = 实体 1%（<5%）
    d["low"][i] = min(o, c) * 0.999
    d["volume"][i] = v


def _standard_three_yang(d: dict[str, np.ndarray], start: int = 67) -> None:
    """在 start..start+2 放标准红三兵（实体 40→60→110，量 1.0→1.15→2.2e8）。

    末日：实体 110 ≥ 1.5×60 ✓ / 开盘 1540∈(1500,1560) ✓ / 收 1650 逐日新高 ✓ /
    总涨幅 1650/1520-1=8.6%<15% ✓ / 量 2.2e8 > 前两根均量 2×=2.15e8 ✓ 且非巨量 ✓。
    """
    _set_yang(d, start, 1480.0, 1520.0, 1.00e8)  # 实体 40
    _set_yang(d, start + 1, 1500.0, 1560.0, 1.15e8)  # 实体 60 > 40
    _set_yang(d, start + 2, 1540.0, 1650.0, 2.20e8)  # 实体 110 ≥ 1.5×60


def _run(d: dict[str, np.ndarray]) -> pd.Series:
    s = {k: pd.Series(v, dtype=float) for k, v in d.items()}
    return s2_three_yang_flag(s["open"], s["high"], s["low"], s["close"], s["volume"])


# ---------------------------------------------------------------------------
# 1. 分级：弱(1) / 标准(2) / 白武士(3)
# ---------------------------------------------------------------------------


class TestGrading:
    def test_standard_three_yang_2(self):
        """6 维全达标 → 2（标准红三兵，flag 标在第三根 K 线日）。"""
        d = _decline_base()
        _standard_three_yang(d)
        out = _run(d)
        assert out.iloc[69] == 2.0
        assert out.iloc[68] == 0.0, "前两根不构成三根序列"

    def test_weak_without_volume_1(self):
        """缺量能确认（量平 1e8，vol_inc/vol_surge 不满足）→ 1（弱红三兵）。"""
        d = _decline_base()
        _standard_three_yang(d)
        d["volume"][67] = d["volume"][68] = d["volume"][69] = 1e8
        out = _run(d)
        assert out.iloc[69] == 1.0

    def test_white_warriors_3(self):
        """三个白武士：第三根实体 ≥2× 第二根 + 近乎光头（上影<1%）→ 3。"""
        d = _decline_base()
        _standard_three_yang(d)
        # 第三根实体放大到 125（≥2×60=120）且光头
        _set_yang(d, 69, 1540.0, 1665.0, 2.20e8)
        d["high"][69] = 1665.0 + 125.0 * 0.005  # 上影=实体 0.5%<1%
        out = _run(d)
        assert out.iloc[69] == 3.0


# ---------------------------------------------------------------------------
# 2. 三种假红三兵排除
# ---------------------------------------------------------------------------


class TestFakePatternsExcluded:
    def test_high_position_excluded(self):
        """高位红三兵（无 30% 跌幅，诱多）→ 0。"""
        n = _N
        close = np.full(n, 3000.0)
        d = {
            "open": close.copy(),
            "high": close.copy(),
            "low": close.copy(),
            "close": close.copy(),
            "volume": np.full(n, 1e8),
        }
        _set_yang(d, 67, 3000.0, 3040.0, 1.00e8)
        _set_yang(d, 68, 3020.0, 3080.0, 1.15e8)
        _set_yang(d, 69, 3060.0, 3170.0, 2.20e8)
        out = _run(d)
        assert out.iloc[69] == 0.0

    def test_shrinking_volume_not_standard(self):
        """缩量红三兵（量递减 1.2→1.1→1.05e8）→ 1（不到 2，买盘后继无力）。"""
        d = _decline_base()
        _standard_three_yang(d)
        d["volume"][67] = 1.20e8
        d["volume"][68] = 1.10e8
        d["volume"][69] = 1.05e8
        out = _run(d)
        assert out.iloc[69] == 1.0

    def test_mid_decline_pause_excluded(self):
        """下跌中继三连小阳（第三根实体未递增 1.5×）→ 0。"""
        d = _decline_base()
        _set_yang(d, 67, 1480.0, 1520.0, 1.00e8)  # 实体 40
        _set_yang(d, 68, 1500.0, 1530.0, 1.15e8)  # 实体 30 < 40（递减）
        _set_yang(d, 69, 1510.0, 1550.0, 2.20e8)  # 实体 40 < 1.5×30=45? 40<45 ✗
        out = _run(d)
        assert out.iloc[69] == 0.0

    def test_overbought_total_gain_excluded(self):
        """三根总涨幅 >15%（动能透支，失效维度 6）→ 0。"""
        d = _decline_base()
        _set_yang(d, 67, 1480.0, 1500.0, 1.00e8)  # 实体 20
        _set_yang(d, 68, 1490.0, 1600.0, 1.15e8)  # 实体 110 > 20
        _set_yang(d, 69, 1590.0, 1760.0, 2.60e8)  # 实体 170 ≥ 1.5×110=165 ✓
        # 总涨幅 1760/1500-1=17.3%>15%
        out = _run(d)
        assert out.iloc[69] == 0.0


# ---------------------------------------------------------------------------
# 3. 维度单项破坏
# ---------------------------------------------------------------------------


class TestDimensionBreaks:
    def test_not_three_yang(self):
        """中间一根阴线 → 0。"""
        d = _decline_base()
        _standard_three_yang(d)
        d["close"][68] = 1490.0  # 第二根变阴线（close<open=1500）
        out = _run(d)
        assert out.iloc[69] == 0.0

    def test_open_gap_up_excluded(self):
        """第三根跳空高开（开盘 1580 > 前根实体顶 1560，不在实体内）→ 0。"""
        d = _decline_base()
        _standard_three_yang(d)
        _set_yang(d, 69, 1580.0, 1690.0, 2.20e8)
        out = _run(d)
        assert out.iloc[69] == 0.0

    def test_long_upper_wick_excluded(self):
        """第三根上影过长（>实体 5%，非光头）→ 0（卖压未消）。"""
        d = _decline_base()
        _standard_three_yang(d)
        d["high"][69] = 1650.0 + 110.0 * 0.10  # 上影=实体 10%
        out = _run(d)
        assert out.iloc[69] == 0.0

    def test_giant_volume_excluded(self):
        """第三根巨量（>前 5 日均量 2×，一日游风险）→ 1（不到 2）。"""
        d = _decline_base()
        _standard_three_yang(d)
        d["volume"][69] = 3.0e8  # 前 5 日均量≈(1+1+1+1.15+3)/5=1.43e8×2=2.86e8 < 3e8 → 巨量
        out = _run(d)
        assert out.iloc[69] == 1.0


# ---------------------------------------------------------------------------
# 4. warmup / 常态
# ---------------------------------------------------------------------------


class TestNormalMarket:
    def test_declining_market_no_pattern(self):
        """持续下跌无三连阳 → 全 0。"""
        out = _run(_decline_base())
        assert (out == 0.0).all()

    def test_return_domain(self):
        """值域 ⊆ {0,1,2,3}。"""
        d = _decline_base()
        _standard_three_yang(d)
        out = _run(d)
        assert set(out.unique()).issubset({0.0, 1.0, 2.0, 3.0})
