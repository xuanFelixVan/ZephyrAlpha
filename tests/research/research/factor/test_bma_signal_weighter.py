# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] tests.factor.test_bma_signal_weighter
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.analysis.bma_signal_weighter
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] production
# [INVARIANTS] 纯函数核测试，不触网不触库；权重归一/门禁出局/平滑/不操作语义逐项锁定
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=BMA后验权重/门禁/平滑α/一致性置信度逻辑缺陷
# [TESTS] 本文件
# [TTL] permanent
"""BmaSignalWeighter 单元测试（CAND-FAC-013 / B10-01481，模块48 动态信号权重模型）。

覆盖（min_build_spec）：
- 信号预测力门禁：IC>0.03 有效 / ICIR>0.5 稳定（不稳定降权）/ IC 衰减>50% 权重降0 / 体制条件IC≤0 出局
- BMA 后验权重（softmax 伪似然 MVP，Σ=1 且单调：IC×ICIR 高者权重高）
- 平滑 α=0.9：w_t = 0.9·w_prev + 0.1·w_raw 后归一
- 一致性置信度 + 不操作裁定：一致性低 + 无主导信号（双低）→ NO_TRADE
"""

from __future__ import annotations

import pytest

from zephyr.factor.analysis.bma_signal_weighter import (
    BmaSignalWeighter,
    BmaWeighterConfig,
    SignalEvaluation,
    compute_bma_weights,
)


def _ev(
    sid: str,
    ic: float = 0.05,
    icir: float = 0.8,
    decay: float = 0.1,
    direction: int = 1,
    regime_ic: float | None = None,
) -> SignalEvaluation:
    return SignalEvaluation(
        signal_id=sid,
        ic=ic,
        icir=icir,
        ic_decay_ratio=decay,
        direction=direction,
        regime_ic=regime_ic,
    )


# ---------------------------------------------------------------- 门禁


def test_ic_below_floor_gated_out() -> None:
    report = compute_bma_weights([_ev("a", ic=0.02), _ev("b", ic=0.06)])
    assert "a" in report.gated_out
    assert report.gated_out["a"] == "ic_below_floor"
    assert set(report.weights) == {"b"}
    assert report.weights["b"] == pytest.approx(1.0)


def test_ic_above_floor_survives() -> None:
    # 边界语义对齐注册表“IC>0.03 有效”：恰好 0.03 出局（见 test_ic_below_floor_gated_out），0.031 留存
    report = compute_bma_weights([_ev("a", ic=0.031), _ev("b", ic=0.06)])
    assert "a" not in report.gated_out


def test_decay_over_half_drops_to_zero() -> None:
    report = compute_bma_weights([_ev("a", decay=0.51), _ev("b")])
    assert report.gated_out["a"] == "ic_decay_exceeded"


def test_decay_at_threshold_survives() -> None:
    report = compute_bma_weights([_ev("a", decay=0.5), _ev("b")])
    assert "a" not in report.gated_out


def test_unstable_icir_downweighted_not_gated() -> None:
    # 同 IC，a 不稳定（icir<0.5 → ×0.5 降权），b 稳定 → b 权重显著高于 a
    report = compute_bma_weights([_ev("a", ic=0.05, icir=0.3), _ev("b", ic=0.05, icir=0.8)])
    assert "a" not in report.gated_out
    assert report.weights["b"] > report.weights["a"]


def test_regime_ic_nonpositive_gated_out() -> None:
    report = compute_bma_weights([_ev("a", regime_ic=0.0), _ev("b", regime_ic=0.04), _ev("c")])
    assert report.gated_out["a"] == "regime_ic_nonpositive"
    assert set(report.weights) == {"b", "c"}


# ---------------------------------------------------------------- 后验权重


def test_weights_sum_to_one_and_monotone() -> None:
    report = compute_bma_weights(
        [
            _ev("strong", ic=0.08, icir=1.2),
            _ev("mid", ic=0.05, icir=0.8),
            _ev("weak", ic=0.035, icir=0.6),
        ]
    )
    assert sum(report.weights.values()) == pytest.approx(1.0)
    assert report.weights["strong"] > report.weights["mid"] > report.weights["weak"]


def test_equal_signals_equal_weights() -> None:
    report = compute_bma_weights([_ev("a"), _ev("b"), _ev("c")])
    for w in report.weights.values():
        assert w == pytest.approx(1.0 / 3)


# ---------------------------------------------------------------- 平滑


def test_smoothing_alpha_blends_previous() -> None:
    weighter = BmaSignalWeighter()
    first = weighter.update([_ev("a", ic=0.08, icir=1.0), _ev("b", ic=0.04, icir=0.6)])
    # 第二轮 raw 与首轮相同 → 平滑后权重不变（0.9·w + 0.1·w）
    second = weighter.update([_ev("a", ic=0.08, icir=1.0), _ev("b", ic=0.04, icir=0.6)])
    assert second.weights["a"] == pytest.approx(first.weights["a"])
    # 第三轮 b 出局 → 平滑后 b 仍有 0.9 残影但未归一主导，a 趋近 1
    third = weighter.update([_ev("a", ic=0.08, icir=1.0), _ev("b", ic=0.01)])
    assert "b" in third.gated_out
    assert third.weights["a"] == pytest.approx(1.0)
    assert sum(third.weights.values()) == pytest.approx(1.0)


def test_smoothing_converges_to_new_regime() -> None:
    cfg = BmaWeighterConfig()
    weighter = BmaSignalWeighter(config=cfg)
    weighter.update([_ev("a", ic=0.08, icir=1.0), _ev("b", ic=0.04, icir=0.6)])
    for _ in range(60):
        report = weighter.update([_ev("a", ic=0.04, icir=0.6), _ev("b", ic=0.08, icir=1.0)])
    # α=0.9 多次迭代后收敛到新 raw 权重（b 主导）
    assert report.weights["b"] > report.weights["a"]


# ---------------------------------------------------------------- 一致性置信度与不操作


def test_empty_evaluations_no_trade() -> None:
    report = compute_bma_weights([])
    assert report.weights == {}
    assert report.decision == "NO_TRADE"
    assert report.confidence == 0.0
    assert report.direction == 0


def test_all_gated_no_trade() -> None:
    report = compute_bma_weights([_ev("a", ic=0.01), _ev("b", ic=0.02)])
    assert report.decision == "NO_TRADE"
    assert report.weights == {}


def test_double_low_no_trade() -> None:
    # 四信号两两对冲（一致性≈0.5 低）且等权分散（无主导信号 低）→ NO_TRADE
    report = compute_bma_weights(
        [
            _ev("l1", direction=1),
            _ev("l2", direction=1),
            _ev("s1", direction=-1),
            _ev("s2", direction=-1),
        ]
    )
    assert report.decision == "NO_TRADE"


def test_high_agreement_dominant_trade() -> None:
    report = compute_bma_weights(
        [
            _ev("a", ic=0.09, icir=1.2, direction=1),
            _ev("b", ic=0.04, icir=0.6, direction=1),
            _ev("c", ic=0.035, icir=0.55, direction=-1),
        ]
    )
    assert report.decision == "TRADE"
    assert report.direction == 1
    assert report.agreement > 0.6
    assert report.confidence > 0.0


def test_agreement_reflects_directional_weight_share() -> None:
    report = compute_bma_weights(
        [
            _ev("a", ic=0.09, icir=1.2, direction=-1),
            _ev("b", ic=0.04, icir=0.6, direction=1),
        ]
    )
    assert report.direction == -1
    assert report.agreement == pytest.approx(report.weights["a"] / (report.weights["a"] + report.weights["b"]))


# ---------------------------------------------------------------- 输入校验


def test_invalid_direction_raises() -> None:
    with pytest.raises(ValueError):
        _ev("a", direction=0)


def test_invalid_decay_raises() -> None:
    with pytest.raises(ValueError):
        _ev("a", decay=1.5)


def test_empty_signal_id_raises() -> None:
    with pytest.raises(ValueError):
        _ev("")


def test_invalid_smoothing_alpha_raises() -> None:
    with pytest.raises(ValueError):
        BmaWeighterConfig(smoothing_alpha=1.5)


def test_report_is_frozen() -> None:
    report = compute_bma_weights([_ev("a")])
    with pytest.raises(AttributeError):
        report.decision = "TRADE"  # type: ignore[misc]
