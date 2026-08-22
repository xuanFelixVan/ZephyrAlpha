"""MOD-SIG-063 相似日 KNN 剩余走势推演单元测试（44号 §9.3，合成历史库注入不触库）"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from zephyr.signal_ashare.similar_day_inference import (
    SimilarDayConfig,
    infer_remaining_session,
    update_hit_rate_stats,
)

OPEN_MIN, CLOSE_MIN, NOW_MIN = 570, 900, 840  # 09:30 / 15:00 / 14:00（当前时刻钉定）
N_MINUTES = CLOSE_MIN - OPEN_MIN + 1  # 331 个分钟点（连续时钟轴，午休不剔除）


def _minutes() -> np.ndarray:
    return OPEN_MIN + np.arange(N_MINUTES).astype(float)


def _base_shape() -> dict[str, np.ndarray]:
    """相似日簇的共同曲线形态（五维，当前时刻前段）。"""
    x = np.linspace(0.0, 1.0, N_MINUTES)
    return {
        "breadth_vel": 2.0 * x,
        "lu_net": 30.0 * x,
        "vol_extrap_ratio": 1.2 - 0.2 * x,
        "yw_spread": 0.001 + 0.002 * x,
        "if_basis": -5.0 + 3.0 * x,
    }


def _mk_day(
    rng: np.random.Generator,
    *,
    shape: dict[str, np.ndarray] | None,
    tail_ret: float,
    with_basis: bool = True,
    noise: float = 0.01,
) -> pd.DataFrame:
    """合成一个历史交易日分钟快照帧；index_price 平走 100、收盘跳到 100*(1+tail_ret)。"""
    n = N_MINUTES
    shape = shape if shape is not None else _base_shape()
    data: dict[str, np.ndarray] = {"ts": _minutes()}
    for name, curve in shape.items():
        if name == "if_basis" and not with_basis:
            continue
        scale = max(abs(curve).max(), 1e-6)
        data[name] = curve + rng.normal(0.0, noise, n) * scale
    prices = np.full(n, 100.0)
    prices[-1] = 100.0 * (1.0 + tail_ret)
    data["index_price"] = prices
    return pd.DataFrame(data)


def _mk_today(rng: np.random.Generator, *, with_basis: bool = True, upto_min: int = NOW_MIN) -> pd.DataFrame:
    """合成当日 09:30→当前时刻快照帧（无 index_price，对齐生产消费口径）。"""
    n = upto_min - OPEN_MIN + 1
    shape = {name: curve[:n] for name, curve in _base_shape().items()}
    data: dict[str, np.ndarray] = {"ts": _minutes()[:n]}
    for name, curve in shape.items():
        if name == "if_basis" and not with_basis:
            continue
        scale = max(abs(curve).max(), 1e-6)
        data[name] = curve + rng.normal(0.0, 0.01, n) * scale
    return pd.DataFrame(data)


def _random_shape(rng: np.random.Generator) -> dict[str, np.ndarray]:
    """与基线簇形态无关的随机游走曲线族。"""
    return {
        "breadth_vel": np.cumsum(rng.normal(0.0, 1.0, N_MINUTES)),
        "lu_net": np.cumsum(rng.normal(0.0, 5.0, N_MINUTES)),
        "vol_extrap_ratio": 1.0 + np.cumsum(rng.normal(0.0, 0.02, N_MINUTES)),
        "yw_spread": np.cumsum(rng.normal(0.0, 0.0005, N_MINUTES)),
        "if_basis": np.cumsum(rng.normal(0.0, 1.0, N_MINUTES)),
    }


def _similar_store(rng: np.random.Generator, n_similar: int, n_random: int, tail_ret: float = 0.01):
    """合成历史库：n_similar 个与今日同形态且尾盘走强 + n_random 个随机形态混合尾向日。"""
    days = [_mk_day(rng, shape=None, tail_ret=tail_ret) for _ in range(n_similar)]
    for _ in range(n_random):
        days.append(_mk_day(rng, shape=_random_shape(rng), tail_ret=float(rng.uniform(-0.02, 0.02))))
    rng.shuffle(days)
    return days


CFG_NOW = SimilarDayConfig(now="14:00")


def test_knn_cluster_tail_probs():
    """D=100 含已知尾盘走向相似日簇 → 三档概率由近邻占比给出（走强主导，Σ=1）。"""
    rng = np.random.default_rng(42)
    store = _similar_store(rng, n_similar=60, n_random=40, tail_ret=0.01)
    res = infer_remaining_session(_mk_today(rng), history_store=store, config=CFG_NOW)
    assert res.enabled and not res.fallback_used
    assert res.n_history_days == 100 and res.n_neighbors == 10
    assert res.features_used == ["breadth_vel", "lu_net", "vol_extrap_ratio", "yw_spread", "if_basis"]
    assert res.mean_neighbor_distance is not None and res.mean_neighbor_distance < 0.35
    assert res.prob_strong >= 0.8  # k=10 近邻基本全落相似簇（tail=+1% > +0.3%）
    assert res.prob_strong + res.prob_flat + res.prob_weak == pytest.approx(1.0)
    assert res.dominant_scenario == "走强"


def test_insufficient_history_fallback():
    """D=30 < 60 → 退化五阶段转移先验；FERMENTING 先验 = 对角 0.6 + 邻阶各 0.2。"""
    rng = np.random.default_rng(7)
    store = _similar_store(rng, n_similar=30, n_random=0)
    cfg = SimilarDayConfig(now="14:00", current_phase="FERMENTING")
    res = infer_remaining_session(_mk_today(rng), history_store=store, config=cfg)
    assert res.fallback_used and res.fallback_reason.startswith("insufficient_history")
    assert res.n_neighbors == 0 and res.mean_neighbor_distance is None
    assert res.phase_transition_prob == pytest.approx({"冰点": 0.0, "反核": 0.2, "主升": 0.6, "疯狂": 0.2, "退潮": 0.0})
    # 主升→疯狂 为升温边（走强 0.2）；主升→反核 为降温边（转弱 0.2）；停留 0.6 持平
    assert (res.prob_strong, res.prob_flat, res.prob_weak) == (
        pytest.approx(0.2),
        pytest.approx(0.6),
        pytest.approx(0.2),
    )
    assert res.current_phase == "主升"


def test_distance_threshold_fallback():
    """近邻平均距离超阈（历史全为镜像形态 corr≈-1）→ 退化先验。"""
    rng = np.random.default_rng(11)
    mirror = {name: -curve for name, curve in _base_shape().items()}
    store = [_mk_day(rng, shape=mirror, tail_ret=0.01) for _ in range(100)]
    res = infer_remaining_session(_mk_today(rng), history_store=store, config=CFG_NOW)
    assert res.fallback_used and res.fallback_reason.startswith("mean_neighbor_distance")
    assert res.n_history_days == 100


def test_missing_basis_dim_reweights():
    """今日/历史缺 if_basis 列 → 该维剔除重配权重，KNN 路径仍正常出概率。"""
    rng = np.random.default_rng(23)
    store = [_mk_day(rng, shape=None, tail_ret=0.01, with_basis=False) for _ in range(70)]
    today = _mk_today(rng, with_basis=True)  # 今日有基差、历史无 → 共同维剔除
    res = infer_remaining_session(today, history_store=store, config=CFG_NOW)
    assert not res.fallback_used
    assert "if_basis" not in res.features_used and len(res.features_used) == 4
    assert any("if_basis" in note for note in res.notes) or res.prob_strong > 0.5
    assert res.prob_strong + res.prob_flat + res.prob_weak == pytest.approx(1.0)


def test_walkforward_hit_rate_disables():
    """walk-forward 命中率 <55% → enabled=False + disabled 标注（仍出先验概率兜底）。"""
    rng = np.random.default_rng(31)
    store = _similar_store(rng, n_similar=60, n_random=40)
    cfg = SimilarDayConfig(now="14:00", walkforward_hit_rate=0.50)
    res = infer_remaining_session(_mk_today(rng), history_store=store, config=cfg)
    assert not res.enabled and res.disabled_reason is not None and "自动停用" in res.disabled_reason
    assert res.prob_strong + res.prob_flat + res.prob_weak == pytest.approx(1.0)


def test_zero_history_fallback_and_json():
    """零数据积累（history_store=None）→ 恒走先验兜底；to_dict JSON 可序列化。"""
    rng = np.random.default_rng(5)
    res = infer_remaining_session(_mk_today(rng), history_store=None, config=CFG_NOW)
    assert res.fallback_used and res.n_history_days == 0
    # current_phase=None → 均匀五阶段先验 + 三档各 1/3，dominant 平票宁标持平
    assert all(v == pytest.approx(0.2) for v in res.phase_transition_prob.values())
    assert (res.prob_strong, res.prob_flat, res.prob_weak) == (
        pytest.approx(1 / 3),
        pytest.approx(1 / 3),
        pytest.approx(1 / 3),
    )
    assert res.dominant_scenario == "持平"
    payload = json.loads(json.dumps(res.to_dict(), ensure_ascii=False))
    assert payload["fallback_used"] is True and payload["dominant_scenario"] == "持平"


def test_today_empty_and_bad_ts():
    """今日快照空 → 兜底不抛；缺 ts 列 → ValueError（调用方契约违例 fail-closed）。"""
    res = infer_remaining_session(pd.DataFrame(), history_store=None, config=CFG_NOW)
    assert res.fallback_used and res.fallback_reason == "today_series_empty"
    with pytest.raises(ValueError):
        infer_remaining_session(pd.DataFrame({"breadth_vel": [1.0, 2.0]}), config=CFG_NOW)


def test_hit_rate_stats_stub():
    """命中率统计接口为 stub（数据期校准），当前抛 NotImplementedError。"""
    with pytest.raises(NotImplementedError):
        update_hit_rate_stats([], [])
