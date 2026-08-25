# [BLUEPRINT] MOD-RK-32 | docs/03_modules/_domain_risk/crowding_response_engine/blueprint.md | §test
# [A_test] module_id: MOD-RK-32 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""CrowdingResponseEngine 单元测试 (MOD-RK-32, C-045 深度增强 MVP)。

覆盖: 低拥挤零动作 / 拥挤超阈自动降杠杆降仓+漏斗降权 / 策略逻辑指纹 DTW 相似度
(同形态判拥挤/异形态不判) / 拥挤-回撤正反馈悖论防护(熔断式退出) / 非拥挤不触发
悖论防护 / 指纹不足两路 None / Fail-Closed 校验 / frozen 不可变。
"""

from __future__ import annotations

import dataclasses

import numpy as np
import pytest

from zephyr.risk.core.crowding_response_engine import (
    CrowdingResponseAction,
    CrowdingResponseConfig,
    InvalidCrowdingResponseConfigError,
    InvalidCrowdingResponseInputError,
    assess_crowding_response,
)


def _similar_fingerprints(n: int = 60) -> dict[str, list[float]]:
    """两路同形态 PnL 指纹（同相正弦）。"""
    x = np.linspace(0, 4 * np.pi, n)
    return {
        "s1": np.sin(x).tolist(),
        "s2": (np.sin(x) * 1.8 + 0.3).tolist(),  # 幅度/平移不同, 形态相同
    }


def _dissimilar_fingerprints(n: int = 60) -> dict[str, list[float]]:
    """两路异形态 PnL 指纹（一升一降镜像）。"""
    return {
        "s1": np.linspace(0.0, 1.0, n).tolist(),
        "s2": np.linspace(1.0, 0.0, n).tolist(),
    }


# ── 基础响应 ──────────────────────────────────────────────────────────────────


def test_calm_no_action() -> None:
    res = assess_crowding_response(0.2)
    assert isinstance(res, CrowdingResponseAction)
    assert res.is_crowded is False
    assert res.leverage_scale == pytest.approx(1.0)
    assert res.position_scale == pytest.approx(1.0)
    assert res.weight_penalty == pytest.approx(0.0)
    assert res.paradox_guard_triggered is False
    assert res.forced_exit is False
    assert res.logic_similarity_max is None


def test_crowded_score_triggers_deleverage() -> None:
    res = assess_crowding_response(0.75)
    assert res.is_crowded is True
    assert res.leverage_scale == pytest.approx(0.5)
    assert res.position_scale == pytest.approx(0.5)
    assert res.weight_penalty == pytest.approx(0.5)
    assert any("拥挤" in r for r in res.reasons)


# ── 逻辑指纹相似度 ────────────────────────────────────────────────────────────


def test_similar_fingerprints_mark_crowded() -> None:
    res = assess_crowding_response(0.1, fingerprints=_similar_fingerprints())
    assert res.logic_similarity_max is not None
    assert res.logic_similarity_max >= 0.8
    assert res.is_crowded is True
    assert any("指纹" in r for r in res.reasons)


def test_dissimilar_fingerprints_not_crowded() -> None:
    res = assess_crowding_response(0.1, fingerprints=_dissimilar_fingerprints())
    assert res.logic_similarity_max is not None
    assert res.logic_similarity_max < 0.8
    assert res.is_crowded is False


def test_single_fingerprint_similarity_none() -> None:
    res = assess_crowding_response(0.1, fingerprints={"only": [0.1, 0.2, 0.3]})
    assert res.logic_similarity_max is None
    assert res.is_crowded is False


# ── 拥挤-回撤正反馈悖论防护 ────────────────────────────────────────────────────


def test_paradox_guard_forced_exit() -> None:
    res = assess_crowding_response(0.75, drawdown_pct=0.12, drawdown_slope=0.02)
    assert res.paradox_guard_triggered is True
    assert res.forced_exit is True
    assert res.position_scale == 0.0
    assert any("悖论" in r or "正反馈" in r for r in res.reasons)


def test_paradox_guard_requires_crowding() -> None:
    res = assess_crowding_response(0.2, drawdown_pct=0.12, drawdown_slope=0.02)
    assert res.paradox_guard_triggered is False
    assert res.forced_exit is False


def test_paradox_guard_requires_worsening_slope() -> None:
    res = assess_crowding_response(0.75, drawdown_pct=0.12, drawdown_slope=-0.01)
    assert res.paradox_guard_triggered is False
    assert res.forced_exit is False


# ── Fail-Closed 校验 ──────────────────────────────────────────────────────────


@pytest.mark.parametrize("score", [-0.1, 1.2, float("nan"), float("inf")])
def test_invalid_crowding_score(score: float) -> None:
    with pytest.raises(InvalidCrowdingResponseInputError):
        assess_crowding_response(score)


def test_invalid_drawdown_pct() -> None:
    with pytest.raises(InvalidCrowdingResponseInputError):
        assess_crowding_response(0.5, drawdown_pct=-0.01)


def test_empty_fingerprint_series() -> None:
    with pytest.raises(InvalidCrowdingResponseInputError):
        assess_crowding_response(0.5, fingerprints={"a": [], "b": [0.1]})


@pytest.mark.parametrize(
    "kwargs",
    [
        {"crowded_threshold": 0.0},
        {"crowded_threshold": 1.5},
        {"similarity_threshold": 0.0},
        {"similarity_threshold": 2.0},
        {"leverage_when_crowded": 0.0},
        {"position_when_crowded": 1.5},
        {"weight_penalty_when_crowded": -0.1},
        {"weight_penalty_when_crowded": 1.0},
        {"paradox_drawdown_threshold": 0.0},
    ],
)
def test_invalid_config_fail_closed(kwargs: dict) -> None:
    with pytest.raises(InvalidCrowdingResponseConfigError):
        CrowdingResponseConfig(**kwargs)


# ── 不可变 ────────────────────────────────────────────────────────────────────


def test_result_frozen() -> None:
    res = assess_crowding_response(0.2)
    with pytest.raises(dataclasses.FrozenInstanceError):
        res.forced_exit = True  # type: ignore[misc]
