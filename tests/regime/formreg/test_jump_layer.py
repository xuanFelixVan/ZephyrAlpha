# [TEST] tests/regime/formreg/test_jump_layer.py
# [TTL] task_bound
# 覆盖: jump_layer（MOD-REGIME-017 两态 jump 概率层封装+锚定重排，隔离施工）
# 纪律: 合成数据纯内存（零 IO 零 CH 依赖，零生产路径写入）
"""jump_layer 单元测试（合成两态收益数据）。

覆盖面：
  - anchored_two_state_order：纯函数槽位序/守卫（K≠2、锚列越界、NaN 死组件→None）
  - fit/transform：持久态标签、后验行和=1、槽位语义（up=高锚列 centers）
  - 锚定抗 label switching：多随机种子下语义槽位稳定
  - fail-closed：空帧/NaN/锚列越界/死组件（超高 λ）→ValueError；未 fit→RuntimeError
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.regime.formreg import jump_layer as jl

# ---------------------------------------------------------------- fixtures


def _two_regime_features(n_per: int = 150, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    ret = np.concatenate(
        [
            rng.normal(-0.02, 0.01, n_per),
            rng.normal(0.03, 0.012, n_per),
        ]
    )
    idx = pd.date_range("2015-01-02", periods=2 * n_per, freq="B")
    return pd.DataFrame({"ret": ret, "vol": np.abs(ret) + rng.normal(0.0, 0.002, 2 * n_per)}, index=idx)


# ---------------------------------------------------------------- anchored order


def test_anchored_order_basic_and_guards():
    centers = np.array([[-0.9, 0.2], [0.9, -0.2]])
    assert jl.anchored_two_state_order(centers, anchor_col=0) == [0, 1]
    assert jl.anchored_two_state_order(centers, anchor_col=1) == [1, 0]
    # K≠2
    assert jl.anchored_two_state_order(np.zeros((3, 2))) is None
    # 锚列越界
    assert jl.anchored_two_state_order(centers, anchor_col=5) is None
    # 死组件 NaN
    assert jl.anchored_two_state_order(np.array([[0.1, 0.0], [np.nan, 0.0]])) is None
    # 平局（两组件锚列同值）不可锚定
    assert jl.anchored_two_state_order(np.array([[0.5, 0.0], [0.5, 0.0]])) is None


# ---------------------------------------------------------------- fit/transform


def test_fit_transform_semantics_and_posterior():
    feats = _two_regime_features()
    res = jl.TwoStateJumpLayer(jump_penalty=10.0).fit_transform(feats)
    assert list(res.posterior.columns) == list(jl.TWO_STATE_SLOTS) == ["down", "up"]
    assert np.allclose(res.posterior.to_numpy().sum(axis=1), 1.0, atol=1e-6)
    # 槽位语义：up 的 ret centers > down
    assert float(res.centers.loc["up", "ret"]) > float(res.centers.loc["down", "ret"])
    # 分段标签：前半 down、后半 up（合成两态）
    assert res.labels_segment.iloc[0] == "down"
    assert res.labels_segment.iloc[-1] == "up"
    # 持久性：分段标签切换数 ≤2（合成单变点）
    switches = int((res.labels_segment != res.labels_segment.shift()).sum())
    assert switches <= 2
    assert int((res.labels_online != res.labels_online.shift()).sum()) <= 4


def test_anchored_reorder_seed_invariance():
    """锚定重排抗 label switching：多种子拟合下语义槽位稳定（裁定#304 方法论移植）。"""
    feats = _two_regime_features()
    ups = set()
    for seed in (0, 1, 42):
        res = jl.TwoStateJumpLayer(jump_penalty=10.0, random_state=seed).fit_transform(feats)
        ups.add(round(float(res.centers.loc["up", "ret"]), 2))
        assert res.labels_segment.iloc[-1] == "up"
    assert len(ups) == 1  # 不同种子的 up 槽位 centers 一致（语义锚定稳定）


def test_transform_uses_frozen_scalar_pit():
    """transform 用 fit 冻结的 scaler（walk-forward 调用方切窗时的 PIT 前提）。"""
    train = _two_regime_features(80)
    layer = jl.TwoStateJumpLayer(jump_penalty=10.0).fit(train)
    full = _two_regime_features(150)
    res = layer.transform(full)  # 全帧打分不重拟合
    assert res.posterior.shape == (300, 2)


# ---------------------------------------------------------------- fail-closed


def test_fail_closed_inputs():
    feats = _two_regime_features(50)
    layer = jl.TwoStateJumpLayer(jump_penalty=10.0)
    with pytest.raises(RuntimeError):
        layer.transform(feats)  # 未 fit
    with pytest.raises(ValueError):
        layer.fit(pd.DataFrame())
    bad = feats.copy()
    bad.iloc[0, 0] = np.nan
    with pytest.raises(ValueError):
        layer.fit(bad)
    with pytest.raises(ValueError):  # 锚列越界（单列特征帧 anchor_col=3）
        jl.TwoStateJumpLayer(anchor_col=3).fit(feats[["ret"]])
    with pytest.raises(ValueError):
        jl.TwoStateJumpLayer(jump_penalty=-1.0)


def test_dead_component_high_penalty_fail_closed():
    """超高 λ 下组件塌缩（死组件 NaN centers）→ 锚定失败显式抛错，禁静默无锚定。"""
    feats = _two_regime_features(60)
    with pytest.raises(ValueError, match="锚定重排失败"):
        jl.TwoStateJumpLayer(jump_penalty=1e6).fit(feats)
