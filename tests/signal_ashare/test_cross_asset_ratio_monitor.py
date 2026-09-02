# [A_test] module_id: MOD-SIG-075 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SIG-075 | 待统筹登记 | 缺口总账 GAP-F-41 行
# [MODULE] tests.signal_ashare.test_cross_asset_ratio_monitor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""跨资产比价衍生计算（MOD-SIG-075，GAP-F-41）施工验证测试。

覆盖：
- 四比价齐备（金银比/金油比/铜金比/金铜比），比率=分子价/分母价逐日对齐；
- z-score 与分档：尾部陡升序列 → |z|≥2 极端档+宏观含义标注；平稳序列 → 中性；
- 日期对齐：两源日期错位仅取交集（n_points=交集数，as_of=最新共同日）；
- fail-closed：缺资产/非正价/交集不足/窗口非法/非法日期；
- 契约：frozen、to_dict JSON 可序列化、同输入同输出。
全程注入式内存数据，零外网零 DB。
"""

from __future__ import annotations

import dataclasses
import json

import numpy as np
import pytest

from zephyr.signal_ashare.cross_asset_ratio_monitor import (
    RATIO_DEFS,
    CrossAssetRatioConfig,
    CrossAssetRatioResult,
    compute_cross_asset_ratios,
)


def _dates(n: int, start: str = "2026-01-05") -> list[str]:
    import datetime as dt

    d0 = dt.date.fromisoformat(start)
    return [(d0 + dt.timedelta(days=i)).isoformat() for i in range(n)]


def _series(dates: list[str], values: np.ndarray) -> list[tuple[str, float]]:
    return list(zip(dates, [float(x) for x in values]))


def _calm_prices(n: int = 260) -> dict[str, list[tuple[str, float]]]:
    """平稳价格比（金银比恒定 ~80）。"""
    rng = np.random.default_rng(5)
    d = _dates(n)
    gold = 2000.0 + rng.standard_normal(n) * 5
    silver = gold / 80.0
    oil = 80.0 + rng.standard_normal(n) * 1
    copper = 4.0 + rng.standard_normal(n) * 0.05
    return {
        "gold": _series(d, gold),
        "silver": _series(d, silver),
        "oil": _series(d, oil),
        "copper": _series(d, copper),
    }


def _spike_prices(n: int = 260) -> dict[str, list[tuple[str, float]]]:
    """金银比尾部陡升（末 30 日白银暴跌）→ z 极端高。"""
    pack = _calm_prices(n)
    silver_vals = np.array([v for _, v in pack["silver"]])
    silver_vals[-30:] *= np.linspace(1.0, 0.6, 30)
    pack["silver"] = _series([d for d, _ in pack["silver"]], silver_vals)
    return pack


class TestRatios:
    def test_four_ratios_present(self) -> None:
        res = compute_cross_asset_ratios(_calm_prices())
        assert [r.key for r in res.ratios] == list(RATIO_DEFS)
        for r in res.ratios:
            assert r.latest > 0
            assert r.n_points >= 30

    def test_ratio_value_correct(self) -> None:
        res = compute_cross_asset_ratios(_calm_prices())
        gs = next(r for r in res.ratios if r.key == "gold_silver")
        gold_last = _calm_prices()["gold"][-1][1]
        silver_last = _calm_prices()["silver"][-1][1]
        assert gs.latest == pytest.approx(gold_last / silver_last, rel=1e-6)

    def test_calm_is_neutral(self) -> None:
        res = compute_cross_asset_ratios(_calm_prices())
        for r in res.ratios:
            assert r.band == "中性"
            assert abs(r.zscore) < 1.0

    def test_spike_extreme_band_and_annotation(self) -> None:
        res = compute_cross_asset_ratios(_spike_prices())
        gs = next(r for r in res.ratios if r.key == "gold_silver")
        assert gs.zscore >= 2.0
        assert gs.band == "极高"
        assert "避险" in gs.annotation


class TestAlignment:
    def test_inner_join_dates(self) -> None:
        pack = _calm_prices(60)
        pack["silver"] = pack["silver"][5:]  # 白银缺前 5 日
        res = compute_cross_asset_ratios(pack, config=CrossAssetRatioConfig(zscore_window=40, min_points=30))
        gs = next(r for r in res.ratios if r.key == "gold_silver")
        assert gs.n_points == 55
        assert gs.as_of == pack["silver"][-1][0]

    def test_deterministic(self) -> None:
        a = compute_cross_asset_ratios(_calm_prices())
        b = compute_cross_asset_ratios(_calm_prices())
        assert a.to_dict() == b.to_dict()


class TestValidation:
    def test_missing_asset_rejected(self) -> None:
        pack = _calm_prices()
        del pack["silver"]
        with pytest.raises(ValueError, match="silver"):
            compute_cross_asset_ratios(pack)

    def test_non_positive_price_rejected(self) -> None:
        pack = _calm_prices(60)
        d, _ = pack["gold"][10]
        pack["gold"][10] = (d, -1.0)
        with pytest.raises(ValueError, match="gold"):
            compute_cross_asset_ratios(pack)

    def test_insufficient_overlap_rejected(self) -> None:
        pack = _calm_prices(40)
        pack["oil"] = pack["oil"][-20:]  # 与金仅 20 日交集 < min_points 30
        with pytest.raises(ValueError, match="交集"):
            compute_cross_asset_ratios(pack)

    def test_bad_window_rejected(self) -> None:
        with pytest.raises(ValueError, match="zscore_window"):
            CrossAssetRatioConfig(zscore_window=5)


class TestContract:
    def test_to_dict_json_serializable(self) -> None:
        res = compute_cross_asset_ratios(_calm_prices())
        text = json.dumps(res.to_dict(), ensure_ascii=False)
        assert "gold_silver" in text

    def test_frozen(self) -> None:
        res = compute_cross_asset_ratios(_calm_prices())
        assert isinstance(res, CrossAssetRatioResult)
        with pytest.raises(dataclasses.FrozenInstanceError):
            res.ratios = ()  # type: ignore[misc]
