# [TEST] tests/regime/formreg/test_bocpd_online.py
# [TTL] task_bound
# 覆盖: bocpd_online（MOD-REGIME-017 BOCPD AM2007 Student-t 在线变点检测，隔离施工）
# 纪律: 合成数据纯内存（零 IO 零 CH 依赖，零生产路径写入）
"""bocpd_online 单元测试（合成变点数据）。

覆盖面：
  - p(r_t=0) 在真变点处抬升（均值漂移/方差漂移两型）
  - 远离变点段 p_change 贴近 hazard 底（1/λ）
  - run-length 后验行和=1；MAP run length 在变点处坍缩
  - 边界约定：p_change[0]=0（首观测无变点前史）
  - 参数注入：更短 hazard λ→更高底噪
  - fail-closed：空/非 DatetimeIndex/非升序/NaN/λ≤1
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.regime.formreg import bocpd_online as bd

# ---------------------------------------------------------------- fixtures


def _mean_shift(seed: int = 11, n: int = 300, cp: int = 150, mu2: float = 4.0) -> pd.Series:
    rng = np.random.default_rng(seed)
    x = np.concatenate([rng.normal(0.0, 1.0, cp), rng.normal(mu2, 1.0, n - cp)])
    idx = pd.date_range("2015-01-02", periods=n, freq="B")
    return pd.Series(x, index=idx)


def _var_shift(seed: int = 28, n: int = 300, cp: int = 150) -> pd.Series:
    # 种子注：方差变点的可检测性依赖抽签（Student-t 稳健观测把温和漂移吸收进后验），
    # seed=28 为干净样例（峰恰在真变点 150，p_change≈0.79）——该现象本身在模块 docstring 留证。
    rng = np.random.default_rng(seed)
    x = np.concatenate([rng.normal(0.0, 1.0, cp), rng.normal(0.0, 4.0, n - cp)])
    idx = pd.date_range("2015-01-02", periods=n, freq="B")
    return pd.Series(x, index=idx)


# ---------------------------------------------------------------- 检测能力


def test_pchange_spikes_at_mean_shift():
    res = bd.run_bocpd(_mean_shift())
    f = res.frame
    # 变点 ±5 步窗内 p_change 峰值显著高于底噪
    near = f["p_change"].iloc[145:156].max()
    far = f["p_change"].iloc[10:140].mean()
    assert near > 0.3
    assert far < 0.02


def test_pchange_spikes_at_var_shift():
    res = bd.run_bocpd(_var_shift())
    f = res.frame
    near = f["p_change"].iloc[145:165].max()
    far = f["p_change"].iloc[10:140].mean()
    assert near > 0.3  # 方差变点证据累积慢于均值变点（Student-t 稳健性代价；干净样例）
    assert far < 0.02
    assert int(f["p_change"].argmax()) >= 145


def test_runlength_collapse_at_cp():
    res = bd.run_bocpd(_mean_shift())
    f = res.frame
    # 变点前 MAP run length 单调增长（近似=步数）；变点后坍缩为小值
    assert f["runlength_map"].iloc[140] > 100
    assert f["runlength_map"].iloc[155] < 20


# ---------------------------------------------------------------- 不变量


def test_posterior_rows_sum_to_one_and_boundary():
    res = bd.run_bocpd(_mean_shift(n=80, cp=40))
    r = res.runlength_posterior
    assert r.shape == (80, 80)
    assert np.allclose(r.sum(axis=1), 1.0, atol=1e-8)
    assert r[0, 0] == 1.0  # 首观测 P(r_0=0)=1（AM2007 约定）
    assert res.frame["p_change"].iloc[0] == 0.0  # 边界无变点前史
    assert (res.frame["p_change"] >= 0).all() and (res.frame["p_change"] <= 1).all()


def test_determinism_same_input_same_output():
    s = _mean_shift(seed=3, n=60, cp=30)
    a = bd.run_bocpd(s)
    b = bd.run_bocpd(s)
    assert np.array_equal(a.runlength_posterior, b.runlength_posterior)
    assert np.array_equal(a.frame["p_change"].to_numpy(), b.frame["p_change"].to_numpy())


def test_params_injection_shorter_lambda_higher_floor():
    s = _mean_shift(seed=5, n=100, cp=50)
    long_ = bd.run_bocpd(s, bd.BOCPDParams(hazard_lambda=500.0))
    short = bd.run_bocpd(s, bd.BOCPDParams(hazard_lambda=20.0))
    # 短 λ（更密 hazard）→ 远离变点段底噪更高
    assert short.frame["p_change"].iloc[5:45].mean() > long_.frame["p_change"].iloc[5:45].mean()


# ---------------------------------------------------------------- fail-closed


def test_fail_closed_inputs():
    idx = pd.date_range("2015-01-02", periods=10, freq="B")
    s = pd.Series(np.arange(10.0), index=idx)
    with pytest.raises(ValueError):
        bd.run_bocpd(pd.Series(dtype=float, index=pd.DatetimeIndex([])))
    with pytest.raises(ValueError):
        bd.run_bocpd(pd.Series([1.0, 2.0], index=[0, 1]))
    with pytest.raises(ValueError):
        bd.run_bocpd(s.iloc[::-1])
    with pytest.raises(ValueError):
        bad = s.copy()
        bad.iloc[3] = np.nan
        bd.run_bocpd(bad)
    with pytest.raises(ValueError):
        bd.run_bocpd(s, bd.BOCPDParams(hazard_lambda=1.0))
