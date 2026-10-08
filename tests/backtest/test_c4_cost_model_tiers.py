# [BLUEPRINT] MOD-BT-191 | docs/03_modules/_domain_backtest/blueprint.md | §成本档适配器
# [MODULE] tests.backtest.test_c4_cost_model_tiers
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; scripts/backtest/cost_model.py; scripts/backtest/translated/_c4_engine.py
# [CONSUMERS] C4 成本档选档质量守卫（resolve_from_env 选档/legacy 零漂移/未知档 fail-closed/
#   _net_line 标量注入点）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 纯合成数据零 CH 零生产路径写；断言常量经引擎模块常量（COMMISSION_BP/
#   STAMP_BP/SLIPPAGE_BP）禁字面量；legacy 缺席=零行为红线钉死
# [MODIFY-GUARD] scripts/backtest/cost_model.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest 断言失败即红
# [TESTS] self
# [TTL] task_bound
# [TEST] tests/backtest/test_c4_cost_model_tiers.py
# 覆盖（收尾清欠重建，对现行遗失重建适配器契约）：env 选档（缺席/legacy/空串→None）、
#   未知档 fail-closed（禁伪造档位语义）、legacy 占位标量路径禁入、verbatim 冻结土规
#   零漂移（佣金双边+印花单腿+滑点双边，引擎常量）、显式注入标量 κ 路径与 env 旁路。
# 铁律：不连 CH、不写 data/，全纯函数面。
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

_REPO = Path(__file__).resolve().parents[2]
_TRANSLATED = _REPO / "scripts" / "backtest" / "translated"
for _p in (str(_REPO / "src"), str(_TRANSLATED), str(_REPO / "scripts" / "backtest")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import _c4_engine as eng  # noqa: E402

_ENV_KEY = "ZEPHYR_C4_COST_MODEL"


def _adapter():
    """经引擎自身装载缝取适配器模块（同 file-location 面，测引擎真实消费的对象）。"""
    return eng._cost_model_adapter()


def _series(value: float) -> pd.Series:
    return pd.Series([value, value, value], index=pd.Index(["d1", "d2", "d3"]))


# ---------- resolve_from_env 选档 ----------


def test_resolve_unset_returns_none(monkeypatch):
    """缺席=零行为：引擎冻结土规 verbatim 路径（零漂移红线）。"""
    monkeypatch.delenv(_ENV_KEY, raising=False)
    assert _adapter().resolve_from_env() is None


def test_resolve_legacy_returns_none(monkeypatch):
    monkeypatch.setenv(_ENV_KEY, "legacy")
    assert _adapter().resolve_from_env() is None


def test_resolve_empty_string_returns_none(monkeypatch):
    monkeypatch.setenv(_ENV_KEY, "")
    assert _adapter().resolve_from_env() is None


def test_resolve_whitespace_case_normalized(monkeypatch):
    monkeypatch.setenv(_ENV_KEY, "  LEGACY ")
    assert _adapter().resolve_from_env() is None


def test_resolve_known_legacy_set_contract(monkeypatch):
    monkeypatch.delenv(_ENV_KEY, raising=False)
    assert {"", "legacy"} == _adapter()._KNOWN_LEGACY


def test_resolve_unknown_tier_fail_closed(monkeypatch):
    """非 legacy 档名（原件 calibrated/participation 语义不可考）→fail-closed 抛错，
    禁凭记忆伪造标定口径=第二真源红线。"""
    monkeypatch.setenv(_ENV_KEY, "calibrated")
    with pytest.raises(RuntimeError) as ei:
        _adapter().resolve_from_env()
    assert _ENV_KEY in str(ei.value)


def test_resolve_synthetic_unknown_tier_fail_closed(monkeypatch):
    monkeypatch.setenv(_ENV_KEY, "flat10")
    with pytest.raises(RuntimeError):
        _adapter().resolve_from_env()


# ---------- legacy 占位与 verbatim 零漂移 ----------


def test_legacy_placeholder_scalar_path_forbidden():
    """legacy 档不走适配器标量路径（round_trip_bps 抛错=引擎 verbatim 分支承担）。"""
    with pytest.raises(RuntimeError):
        _adapter().LegacyPassthroughCostModel().round_trip_bps(slippage_bp=5.0)


def test_verbatim_zero_drift_formula(monkeypatch):
    """None 路径=冻结土规逐位原式：cost=turnover×(佣金×2+印花+滑点×2)/1e4（常量经引擎）。"""
    monkeypatch.delenv(_ENV_KEY, raising=False)
    gross, turnover = _series(0.001), _series(0.5)
    for slip in (None, 20.0):
        net = eng._net_line(gross, turnover, slip)
        s = eng.SLIPPAGE_BP if slip is None else float(slip)
        expect = gross - turnover * (eng.COMMISSION_BP * 2 + eng.STAMP_BP + s * 2) / 10000.0
        pd.testing.assert_series_equal(net, expect)


def test_env_legacy_bit_identical_to_none(monkeypatch):
    """env=legacy 与缺席逐位一致（选档不得改变缺省口径）。"""
    gross, turnover = _series(0.002), _series(0.8)
    monkeypatch.delenv(_ENV_KEY, raising=False)
    base = eng._net_line(gross, turnover, 5.0)
    monkeypatch.setenv(_ENV_KEY, "legacy")
    legacy = eng._net_line(gross, turnover, 5.0)
    pd.testing.assert_series_equal(base, legacy)


# ---------- 标量注入点 ----------


def test_scalar_injection_path(monkeypatch):
    """非 None cost_model→κ=round_trip_bps(slippage_bp=...) 标量注入，成本式形状不变。"""
    monkeypatch.delenv(_ENV_KEY, raising=False)
    seen: dict = {}

    class _FixedTier:
        def round_trip_bps(self, slippage_bp: float | None = None) -> float:
            seen["slippage_bp"] = slippage_bp
            return 42.0

    gross, turnover = _series(0.003), _series(0.4)
    net = eng._net_line(gross, turnover, 7.0, cost_model=_FixedTier())
    assert seen["slippage_bp"] == 7.0  # 引擎档覆盖透传注入对象
    expect = gross - turnover * 42.0 / 10000.0
    pd.testing.assert_series_equal(net, expect)


def test_explicit_model_bypasses_env_resolution(monkeypatch):
    """显式注入不反查环境变量（env 即使是未知毒档也不拦显式接线）。"""
    monkeypatch.setenv(_ENV_KEY, "poison-tier")

    class _Ok:
        def round_trip_bps(self, slippage_bp: float | None = None) -> float:
            return 0.0

    gross, turnover = _series(0.001), _series(0.3)
    net = eng._net_line(gross, turnover, 5.0, cost_model=_Ok())
    pd.testing.assert_series_equal(net, gross)  # κ=0 → 零成本净线=毛线
