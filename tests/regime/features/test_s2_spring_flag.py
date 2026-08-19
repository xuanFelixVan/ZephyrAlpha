# [A_test] module_id: MOD-TEST-S2-SPRING | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §4 P1-E9c
# [MODULE] tests.regime.features.test_s2_spring_flag
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.regime.features.overlay_features; pandas; numpy; pytest
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError->fail
# [TESTS] tests/regime/features/test_s2_spring_flag.py
# [TTL] permanent
# [ARCH-REF] #P1-E9c #14_regime_s2_diagnosis §4.3
# [ALGO_FLOW]
# 层: 输入
# - I1: close 必需 + high/low 可选（缺失回退 close 简化版）+ volume 预留 + ATR 参数
# 层: 算法
# - A1: 刺破判定 low<rolling_min(low,60).shift(1) + 穿透深度 (支撑-low)/支撑
# - A2: velocity 收回分级（当日/次日/第3日 close>支撑，flag 标在收回确认日）
# - A3: 0.5×ATR 失效边距（收回前收盘 < 刺破日 low-0.5×ATR → 失效）
# - A4: 深度分级 <1%→1 / 1-3%→2 / >3%→3
# 层: 输出
# - O1: pd.Series ∈ {0,1,2,3}（0=无 Spring；warmup 期 0）
"""test_s2_spring_flag.py — P1-E9c spring 深度分级 + velocity + ATR 失效边距单元测试。

覆盖（14_regime_s2_diagnosis §4.3 + §4.5 step 1 stub 要求）：
  1. 跌破支撑判定 + 当日收回（velocity=1）→ flag 标在收回日
  2. velocity 分级：次日收回（v2）/ 第 3 日收回（v3 边界）/ 超 3 日未收回 → 0
  3. 深度分级：<1%→1（minor）/ 1-3%→2（moderate）/ >3%→3（major）
  4. 0.5×ATR 失效边距：收回前收盘跌破 刺破日 low−0.5×ATR → 0
  5. 降级：high/low 缺失 → 原 close 跨日简化版（0/1）
  6. warmup 期 / 常态无信号

依据: 14_regime_s2_diagnosis v0.4.5 §4.3 / §4.5
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from zephyr.regime.features.overlay_features import s2_spring_flag

# ---------------------------------------------------------------------------
# 辅助
# ---------------------------------------------------------------------------

_N = 80  # > window(60) + 事件日


def _base(n: int = _N) -> dict[str, np.ndarray]:
    """常态：支撑明确——low 恒 100，close 105，high 106（rolling_min=100）。"""
    return {
        "open": np.full(n, 105.0),
        "high": np.full(n, 106.0),
        "low": np.full(n, 100.0),
        "close": np.full(n, 105.0),
        "volume": np.full(n, 1e8),
    }


def _series(d: dict[str, np.ndarray]) -> dict[str, pd.Series]:
    return {k: pd.Series(v, dtype=float) for k, v in d.items()}


def _run(d: dict[str, np.ndarray], **kw) -> pd.Series:
    s = _series(d)
    return s2_spring_flag(s["close"], s["high"], s["low"], s["volume"], **kw)


def _penetrate(d: dict[str, np.ndarray], i: int, pen_low: float, pen_close: float) -> None:
    """把第 i 日改成刺破日：low=pen_low（破支撑 100），close=pen_close。"""
    d["low"][i] = pen_low
    d["close"][i] = pen_close
    d["high"][i] = max(106.0, pen_close + 1.0)
    d["open"][i] = pen_close


# ---------------------------------------------------------------------------
# 1. 深度分级（当日收回 velocity=1）
# ---------------------------------------------------------------------------


class TestDepthGrading:
    def test_minor_depth_1(self):
        """穿透 <1%（low=99.5，depth=0.5%）当日收回 → 1（minor）。"""
        d = _base()
        _penetrate(d, 65, pen_low=99.5, pen_close=104.0)  # 收 > 支撑 100
        out = _run(d)
        assert out.iloc[65] == 1.0
        assert out.iloc[64] == 0.0 and out.iloc[66] == 0.0

    def test_moderate_depth_2(self):
        """穿透 1-3%（low=98，depth=2%）当日收回 → 2（moderate）。"""
        d = _base()
        _penetrate(d, 65, pen_low=98.0, pen_close=104.0)
        assert _run(d).iloc[65] == 2.0

    def test_major_depth_3(self):
        """穿透 >3%（low=95，depth=5%）当日收回 → 3（major，强制清算级）。"""
        d = _base()
        _penetrate(d, 65, pen_low=95.0, pen_close=104.0)
        assert _run(d).iloc[65] == 3.0


# ---------------------------------------------------------------------------
# 2. velocity 分级（收回速度）
# ---------------------------------------------------------------------------


class TestVelocity:
    def test_next_day_recovery_v2(self):
        """次日收回（velocity=2）：刺破日收在支撑下（未失效），次日收 > 支撑 → flag 标在次日。"""
        d = _base()
        _penetrate(d, 65, pen_low=98.0, pen_close=99.0)  # 收 99 < 支撑 100，未失效
        d["close"][66] = 104.0  # 次日收回
        out = _run(d)
        assert out.iloc[65] == 0.0, "刺破日未收回不应标 flag"
        assert out.iloc[66] == 2.0, "次日收回 → moderate（depth=2%）"

    def test_third_day_recovery_v3(self):
        """第 3 日收回（velocity=3 边界）：中间两日收在支撑下但未失效 → flag 标在第 3 日。"""
        d = _base()
        _penetrate(d, 65, pen_low=98.0, pen_close=99.5)
        d["close"][66] = 99.5  # 仍 < 支撑，但未失效（≥ 98−0.5×ATR）
        d["close"][67] = 104.0  # 第 3 日收回
        out = _run(d)
        assert out.iloc[67] == 2.0

    def test_no_recovery_within_3_days_zero(self):
        """超 3 日未收回 → 不成立（缓慢阴跌=假信号）。"""
        d = _base()
        _penetrate(d, 65, pen_low=98.0, pen_close=99.0)
        for i in (66, 67, 68, 69):
            d["close"][i] = 99.0  # 持续支撑下（但未失效）
        d["close"][70] = 104.0  # 第 5 日才收回 → 太晚
        out = _run(d)
        assert out.iloc[70] == 0.0
        assert (out == 0.0).all()


# ---------------------------------------------------------------------------
# 3. 0.5×ATR 失效边距
# ---------------------------------------------------------------------------


class TestAtrInvalidation:
    def test_close_below_fail_level_invalidates(self):
        """收回前收盘 < 刺破日 low − 0.5×ATR → Spring 失效（防假突破持续跌破）。"""
        d = _base()
        # 常态 TR=6 → ATR≈6；刺破日 TR 增大使 ATR≈7：fail≈98−0.5×7≈94.5
        _penetrate(d, 65, pen_low=98.0, pen_close=93.0)  # 收 93 < fail → 失效
        d["close"][66] = 104.0  # 次日收回也没用（刺破日已失效）
        out = _run(d)
        assert out.iloc[66] == 0.0
        assert (out == 0.0).all()

    def test_close_above_fail_level_valid(self):
        """刺破日收盘 ≥ 失效线 → 不失效，次日收回正常给分。"""
        d = _base()
        _penetrate(d, 65, pen_low=98.0, pen_close=97.0)  # ≥ fail(≈94.5)
        d["close"][66] = 104.0
        assert _run(d).iloc[66] == 2.0


# ---------------------------------------------------------------------------
# 4. 降级 + 常态
# ---------------------------------------------------------------------------


class TestFallbackAndNormal:
    def test_legacy_close_only_fallback(self):
        """缺 high/low → 回退 close 跨日简化版：前日收破前低 + 当日收回 → 1。"""
        n = 40
        close = pd.Series(np.full(n, 100.0))
        close.iloc[30] = 95.0  # 跌破前 20 日最低（100）
        close.iloc[31] = 101.0  # 当日收回
        out = s2_spring_flag(close)
        assert out.iloc[31] == 1.0
        assert out.sum() == 1.0

    def test_legacy_no_spring(self):
        """降级路径常态平盘 → 全 0。"""
        out = s2_spring_flag(pd.Series(np.full(40, 100.0)))
        assert (out == 0.0).all()

    def test_normal_market_all_zero(self):
        """常态（无刺破）→ 全 0。"""
        assert (_run(_base()) == 0.0).all()

    def test_warmup_period_zero(self):
        """warmup（前 60 日支撑未形成）→ 0。"""
        d = _base()
        _penetrate(d, 30, pen_low=95.0, pen_close=104.0)  # 第 30 日窗口不足
        out = _run(d)
        assert out.iloc[30] == 0.0
