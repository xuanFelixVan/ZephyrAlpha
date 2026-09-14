# [BLUEPRINT] MOD-SIG-148 | tests/signal_ashare/strategy_signal/test_pattern_evidence_certifier.py
# [MODULE] tests.signal_ashare.strategy_signal.test_pattern_evidence_certifier
# [DOMAIN] D_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.strategy_signal.pattern_evidence_certifier
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 教科书已知值向量（二项 p/BH 例/收缩例）+状态机迁移+Fail-Closed；不触库
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败->测试失败
# [TESTS] pytest tests/signal_ashare/strategy_signal/test_pattern_evidence_certifier.py
# [TTL] permanent
"""pattern_evidence_certifier 单测（W-CA）——四闸纯函数教科书向量+状态机迁移。"""

from __future__ import annotations

import math

import pytest

from zephyr.signal_ashare.strategy_signal.pattern_evidence_certifier import (
    bh_adjust,
    binomial_ge_pvalue,
    certify_family,
    effective_n,
    load_family_rows,
    shrunk_rate,
    within_regime_edge,
)

_FAKE_ROWS = [
    ("双顶", "", 0.60, 5000, 0),          # 池化强形态
    ("双顶", "r1", 0.63, 4500, 0),
    ("双顶", "r2", 0.10, 500, 0),
    ("幸运小样本", "", 1.00, 76, 0),        # n_eff<30
    ("弱样本", "", 0.90, 8, 1),            # low_sample=不进认定
    ("__baseline__", "", 0.50, 100000, 0),
    ("__baseline__", "r1", 0.50, 80000, 0),
    ("__baseline__", "r2", 0.50, 20000, 0),
]


class _FakeClient:
    def execute(self, sql, params=None):
        return _FAKE_ROWS


# ── 闸A：二项精确检验 ────────────────────────────────────────────────────────


def test_binomial_known_value():
    """P(X≥70|n=100,p=0.5)≈3.9e-5（教科书单侧值带内）。"""
    p = binomial_ge_pvalue(70, 100, 0.5)
    assert 1e-6 < p < 1e-4


def test_binomial_mid_is_halfish():
    """恰好均值处：P(X≥50|n=100,p=0.5)≈0.54（含离散半格）。"""
    p = binomial_ge_pvalue(50, 100, 0.5)
    assert 0.45 <= p <= 0.60


def test_binomial_edge_cases():
    assert binomial_ge_pvalue(0, 100, 0.5) == 1.0
    assert binomial_ge_pvalue(0, 0, 0.5) == 1.0
    assert binomial_ge_pvalue(101, 100, 0.5) == 0.0
    with pytest.raises(ValueError):
        binomial_ge_pvalue(10, 100, 1.5)


def test_binomial_far_tail_underflows_to_zero():
    """远尾下溢=精确零（0.5^3862 量级，float 下溢语义可接受）。"""
    p = binomial_ge_pvalue(5000, 5000, 0.5)
    assert p == 0.0


# ── 闸A：BH-FDR（经典四 p 例） ───────────────────────────────────────────────


def test_bh_adjust_classic_example():
    """p=[0.01,0.04,0.03,0.005]→q=[0.02,0.04,0.04,0.02]（BH step-up 教科书例）。"""
    q = bh_adjust([0.01, 0.04, 0.03, 0.005])
    assert q == pytest.approx([0.02, 0.04, 0.04, 0.02])


def test_bh_adjust_empty_and_monotone():
    assert bh_adjust([]) == []
    q = bh_adjust([0.5, 0.01])
    assert q[1] <= q[0]  # 小 p 的 q 不大于大 p


# ── 闸B/D：n_eff 与收缩 ──────────────────────────────────────────────────────


def test_effective_n_discount():
    assert effective_n(500, 10) == 50.0
    assert effective_n(0, 10) == 0.0
    assert effective_n(100, 0) == 100.0  # window<1 视为 1
    with pytest.raises(ValueError):
        effective_n(-1, 10)


def test_shrunk_rate_pulls_to_baseline():
    """100%/76 的 shrunk 读数应贴近基线而非 1.0（闸D 核心语义）。"""
    s = shrunk_rate(1.00, 7.6, 0.50, k=100)
    assert s == pytest.approx((1.0 * 7.6 + 100 * 0.5) / 107.6)
    assert 0.5 <= s <= 0.55
    assert shrunk_rate(0.72, 0, 0.5) == pytest.approx(0.5)  # 无样本=基线
    with pytest.raises(ValueError):
        shrunk_rate(1.2, 10, 0.5)


# ── 闸C：分 regime 加权 edge ─────────────────────────────────────────────────


def test_within_regime_edge_weighted_and_concentration():
    slices = [
        {"regime_tag": "r1", "hit_rate": 0.70, "n_events": 100},
        {"regime_tag": "r2", "hit_rate": 0.40, "n_events": 100},
    ]
    bases = {"r1": 0.5, "r2": 0.5}
    edge, share = within_regime_edge(slices, bases)
    assert edge == pytest.approx(0.05)
    assert share == pytest.approx(1.0)  # 正 edge 只有一源=集中度满格


def test_within_regime_edge_two_positive_sources():
    slices = [
        {"regime_tag": "r1", "hit_rate": 0.70, "n_events": 100},
        {"regime_tag": "r2", "hit_rate": 0.55, "n_events": 100},
    ]
    edge, share = within_regime_edge(slices, {"r1": 0.5, "r2": 0.5})
    assert edge == pytest.approx(0.125)
    assert share == pytest.approx(20 / 25)


def test_within_regime_edge_empty_passes():
    """无 regime 切片=闸C 无反证放行（share 0.0）。"""
    edge, share = within_regime_edge([], {})
    assert (edge, share) == (0.0, 0.0)


# ── 状态机 ───────────────────────────────────────────────────────────────────


def test_certify_family_three_states():
    """同族三形态：certified/failed/probation 各归其位（Fail-Closed 滤 low_sample）。"""
    pooled = [
        {"pattern_id": "双顶", "hit_rate": 0.60, "n_events": 5000},
        {"pattern_id": "幸运小样本", "hit_rate": 1.00, "n_events": 76},
        {"pattern_id": "池化好但regime混", "hit_rate": 0.60, "n_events": 1000},
    ]
    regime = {
        "双顶": [
            {"regime_tag": "r1", "hit_rate": 0.62, "n_events": 3000},
            {"regime_tag": "r2", "hit_rate": 0.56, "n_events": 2000},
        ],
        "池化好但regime混": [
            {"regime_tag": "r1", "hit_rate": 0.63, "n_events": 900},
            {"regime_tag": "r2", "hit_rate": 0.10, "n_events": 100},
        ],
    }
    records = certify_family(
        pooled, regime, baseline_pooled=0.5,
        baseline_by_regime={"r1": 0.5, "r2": 0.5, "__pooled__": 0.5},
        fwd_window=10, timeframe="day", direction="向上",
    )
    by_id = {r.pattern_id: r for r in records}
    assert by_id["双顶"].state == "certified"
    assert by_id["幸运小样本"].state == "failed"  # n_eff=7.6<30
    assert by_id["池化好但regime混"].state == "probation"  # 正 edge 单切片集中=1.0
    assert by_id["双顶"].q_value < 0.05


def test_load_family_rows_filters_baseline_and_low_sample():
    """读家族行：baseline 进基线字典、low_sample 不进认定集。"""
    pooled, regime, base_pooled, bases = load_family_rows(_FakeClient(), timeframe="day", direction="向上", fwd_window=10)
    assert base_pooled == pytest.approx(0.5)
    assert bases.get("r1") == pytest.approx(0.5)
    ids = [r["pattern_id"] for r in pooled]
    assert "弱样本" not in ids and "__baseline__" not in ids
    assert set(regime) == {"双顶"}
