# [A_test] module_id: MOD-SIG-089 | layer=test | stability=volatile | safety=M | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SIG-089 | docs/03_modules/_domain_signal/auction_microstructure_analyzer/blueprint.md
# [MODULE] tests.signal_ashare.test_auction_microstructure_analyzer
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] permanent

"""开盘竞价微结构分析（MOD-SIG-089，B1-00171）施工验证测试。

覆盖：
- 特征提取：价漂移/量斜率/撤单率/封单变化/9:20 后量占比；
- 行为分类：抢筹/诱多/压价/中性四族规则与置信度口径；
- fail-closed：空快照/时间戳非递增/负价量/非法配置；
- 退化路径：单快照 NEUTRAL+notes、申报量 0 撤单率 0+notes；
- 契约：frozen、to_dict JSON 可序列化。
全程内存合成数据，无 DB。
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from zephyr.signal_ashare.auction_microstructure_analyzer import (
    AuctionBehavior,
    AuctionMicroConfig,
    AuctionSnapshot,
    analyze_auction,
)


def _snap(
    minute: int,
    price: float,
    vol: float,
    buy1: float,
    placed: float,
    canceled: float,
) -> AuctionSnapshot:
    # 9:15+minute 分钟偏移（minute 0~10 → 9:15~9:25）
    return AuctionSnapshot(
        ts=f"2026-08-25 09:{15 + minute:02d}:00",
        indicative_price=price,
        indicative_volume=vol,
        buy1_volume=buy1,
        placed_volume=placed,
        canceled_volume=canceled,
    )


def _grab_snaps() -> list[AuctionSnapshot]:
    # 抢筹：价稳升 + 撤单率低 + 封单持续增加
    return [
        _snap(0, 10.00, 1000, 500, 2000, 100),
        _snap(3, 10.05, 1500, 800, 3000, 150),
        _snap(6, 10.10, 2200, 1200, 4200, 180),
        _snap(10, 10.20, 3000, 2000, 6000, 200),
    ]


def _bait_snaps() -> list[AuctionSnapshot]:
    # 诱多：早段价升 + 高撤单 + 9:20 后封单塌陷
    return [
        _snap(0, 10.00, 1000, 1500, 2000, 800),
        _snap(3, 10.15, 1500, 2000, 3500, 1600),
        _snap(6, 10.12, 1200, 600, 4200, 2100),
        _snap(10, 10.02, 900, 200, 5000, 2600),
    ]


def _press_snaps() -> list[AuctionSnapshot]:
    # 压价：价跌 + 封单缩
    return [
        _snap(0, 10.00, 1000, 800, 2000, 100),
        _snap(5, 9.95, 1200, 500, 3000, 150),
        _snap(10, 9.90, 1500, 300, 4000, 200),
    ]


class TestValidation:
    def test_empty_snapshots_rejected(self) -> None:
        with pytest.raises(ValueError):
            analyze_auction("600000.SH", [])

    def test_non_monotonic_ts_rejected(self) -> None:
        snaps = [_snap(5, 10.0, 100, 100, 1000, 0), _snap(3, 10.0, 100, 100, 1100, 0)]
        with pytest.raises(ValueError, match="递增"):
            analyze_auction("600000.SH", snaps)

    def test_negative_values_rejected(self) -> None:
        with pytest.raises(ValueError):
            _snap(0, -10.0, 100, 100, 1000, 0)
        with pytest.raises(ValueError):
            _snap(0, 10.0, -1, 100, 1000, 0)
        with pytest.raises(ValueError):
            _snap(0, 10.0, 100, 100, 1000, 2000)  # 撤单>申报

    def test_empty_symbol_rejected(self) -> None:
        with pytest.raises(ValueError):
            analyze_auction("", _grab_snaps())

    def test_single_snapshot_degrades_neutral(self) -> None:
        sig = analyze_auction("600000.SH", [_snap(0, 10.0, 100, 100, 1000, 0)])
        assert sig.behavior is AuctionBehavior.NEUTRAL
        assert any("单快照" in n for n in sig.notes)


class TestFeatures:
    def test_feature_extraction(self) -> None:
        sig = analyze_auction("600000.SH", _grab_snaps())
        f = sig.features
        assert f.price_drift_pct == pytest.approx(2.0)  # 10.00→10.20
        assert f.cancel_rate == pytest.approx(200 / 6000)
        assert f.seal_change_pct == pytest.approx(300.0)  # 500→2000
        assert 0.0 <= f.late_volume_ratio <= 1.0

    def test_zero_placed_cancel_rate_zero(self) -> None:
        snaps = [_snap(0, 10.0, 100, 100, 0, 0), _snap(5, 10.1, 200, 200, 0, 0)]
        sig = analyze_auction("600000.SH", snaps)
        assert sig.features.cancel_rate == 0.0
        assert any("申报量" in n for n in sig.notes)


class TestBehaviorClassification:
    def test_grab(self) -> None:
        sig = analyze_auction("600000.SH", _grab_snaps())
        assert sig.behavior is AuctionBehavior.GRAB
        assert sig.direction == "LONG"
        assert sig.confidence > 0.5

    def test_bait(self) -> None:
        sig = analyze_auction("600000.SH", _bait_snaps())
        assert sig.behavior is AuctionBehavior.BAIT
        assert sig.direction == "SHORT"
        assert sig.confidence > 0.5

    def test_press(self) -> None:
        sig = analyze_auction("600000.SH", _press_snaps())
        assert sig.behavior is AuctionBehavior.PRESS
        assert sig.direction == "SHORT"

    def test_neutral_when_no_rule_dominant(self) -> None:
        snaps = [
            _snap(0, 10.00, 1000, 500, 2000, 100),
            _snap(10, 10.01, 1100, 520, 3000, 150),
        ]
        sig = analyze_auction("600000.SH", snaps)
        assert sig.behavior is AuctionBehavior.NEUTRAL
        assert sig.direction == "NEUTRAL"


class TestContract:
    def test_frozen_and_json(self) -> None:
        sig = analyze_auction("600000.SH", _grab_snaps())
        with pytest.raises(dataclasses.FrozenInstanceError):
            sig.confidence = 0.0  # type: ignore[misc]
        json.dumps(sig.to_dict(), ensure_ascii=False)

    def test_config_thresholds_adjustable(self) -> None:
        cfg = AuctionMicroConfig(grab_min_drift_pct=5.0)  # 抬高抢筹漂移阈值
        sig = analyze_auction("600000.SH", _grab_snaps(), cfg)
        assert sig.behavior is not AuctionBehavior.GRAB
