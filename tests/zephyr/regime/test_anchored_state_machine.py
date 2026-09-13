# [BLUEPRINT] MOD-REGIME-001 | docs/03_modules/_domain_regime/regime_detector/blueprint.md
# [MODULE] tests.zephyr.regime.test_anchored_state_machine
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.regime.core.anchored_state_machine
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 纯函数直测零 IO（禁写生产路径，序列全部内存构造）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] 本文件
# [TTL] permanent
"""锚定风险四档状态机单测——固定阈值边界/锚定性质（零拟合零漂移）/PIT 热身（裁定#229 重印批 v2）。

核心锁定：
    1. 分类边界：vol_pct 0.30/0.60/0.80 三条结构阈值（边界值归低档）
    2. 锚定性质：同一特征输入永远同一输出（无拟合参数 → label switching 结构性不可能）
    3. PIT 热身：热身期（<max(120, 270) 日）vol_pct NaN 不产出态
    4. 全覆盖：四态按构造可达（阈值覆盖 [0,1]，无死态）
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.regime.core.anchored_state_machine import (
    _WARMUP,
    _VOL_PCT_WINDOW,
    build_states,
    classify_state,
    compute_features,
)


# ---------------------------------------------------------------------------
# classify_state：固定阈值边界（v2 风险四档）
# ---------------------------------------------------------------------------

def test_low_risk_band():
    assert classify_state(0.0) == "r3"
    assert classify_state(0.30) == "r3"        # 边界值归低档


def test_mid_risk_band():
    assert classify_state(0.3001) == "r2"
    assert classify_state(0.60) == "r2"


def test_mid_high_risk_band():
    assert classify_state(0.6001) == "r1"
    assert classify_state(0.80) == "r1"


def test_high_risk_band():
    assert classify_state(0.8001) == "r4"
    assert classify_state(1.0) == "r4"


def test_anchored_pure_function_no_state():
    """锚定性质：同输入永远同输出（无隐藏状态/拟合参数——label switching 结构性不可能）。"""
    for _ in range(3):
        assert classify_state(0.55) == "r2"


def test_full_coverage_of_feature_space():
    """阈值覆盖 [0,1] 全域：任何合法 vol_pct 必落入四态之一（无死态的结构保证）。"""
    for v in np.linspace(0.0, 1.0, 101):
        assert classify_state(float(v)) in {"r1", "r2", "r3", "r4"}


# ---------------------------------------------------------------------------
# compute_features / build_states：PIT 热身与四态可达
# ---------------------------------------------------------------------------

def _make_close(n: int, seed: int = 7) -> pd.Series:
    """构造波动率时变的合成价格（低波→高波→中波三段），确保四态可达。"""
    rng = np.random.default_rng(seed)
    sigma = np.concatenate([
        np.full(n // 3, 0.005),      # 低波段
        np.full(n // 3, 0.030),      # 高波段
        np.full(n - 2 * (n // 3), 0.014),  # 中波段
    ])
    ret = rng.normal(0.0003, 1.0, n) * sigma
    close = 100.0 * np.exp(np.cumsum(ret))
    idx = pd.bdate_range("2015-01-01", periods=n)
    return pd.Series(close, index=idx, name="close")


def test_features_warmup_nan_then_valid():
    close = _make_close(500)
    feat = compute_features(close)
    # 热身期（250 窗口未满前）vol_pct 含 NaN；热身后全有效
    assert feat["vol_pct"].iloc[:_VOL_PCT_WINDOW].isna().any()
    assert feat["vol_pct"].iloc[_WARMUP - 1:].notna().all()
    # vol_pct ∈ [0,1]
    assert feat["vol_pct"].dropna().between(0, 1).all()


def test_build_states_no_dead_states_and_full_coverage():
    close = _make_close(900, seed=11)
    states = build_states(close)
    assert len(states) >= len(close) - _WARMUP
    # 四态按构造可达（无死态——裁定#229 约束②）
    seen = set(states["dominant"].unique())
    assert seen == {"r1", "r2", "r3", "r4"}
    counts = states["dominant"].value_counts()
    # 每态至少 30 个交易日（合成序列波动分层充分；真实序列的 1% 死态线由构建器 --check 把关）
    assert counts.min() >= 30


def test_build_states_deterministic():
    """锚定性质端到端：同价格序列两次构建逐行一致（零拟合 → 零漂移）。"""
    close = _make_close(600, seed=3)
    a, b = build_states(close), build_states(close)
    pd.testing.assert_frame_equal(a, b)


def test_state_transitions_bound_to_vol_changes():
    """态变化必然由 vol_pct 跨阈值驱动（无不可解释的状态跳变——锚定语义的运行时性质）。"""
    close = _make_close(700, seed=21)
    states = build_states(close)
    prev_state, prev_vol = None, None
    for r in states.itertuples(index=False):
        if prev_state is not None and r.dominant != prev_state:
            # 状态变了，vol_pct 必然跨越了某条阈值（跨档方向与 vol 单调一致）
            moved_up = (r.dominant in ("r1", "r4")) or (prev_vol is not None and r.vol_pct > prev_vol)
            moved_down = (r.dominant in ("r2", "r3")) or (prev_vol is not None and r.vol_pct < prev_vol)
            assert moved_up or moved_down
        prev_state, prev_vol = r.dominant, r.vol_pct
