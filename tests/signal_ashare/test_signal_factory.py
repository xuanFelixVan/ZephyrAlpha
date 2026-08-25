# [A_test] module_id: MOD-SIG-087 | layer=test | stability=volatile | safety=M | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SIG-087 | docs/03_modules/_domain_signal/signal_factory/blueprint.md
# [MODULE] tests.signal_ashare.test_signal_factory
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] permanent

"""C-028 信号工厂（MOD-SIG-087，B1-00149）施工验证测试。

覆盖：
- 注册：合法 draft 入册为 DRAFT；重复 id/空 id/非法方向/强度越界 fail-closed；
- 9 阶段主链逐跳推进：不可跳跃、终态 EXPIRED→RETIRED；
- 密度增强跳：缺 density 拒绝；degraded 密度置信度降档；
- 质量门/拥挤度门：低于阈值/高于上限阻断推进并留 notes；
- 漏斗批量：仅 FUNNELED 阶段产出；
- 契约：frozen、to_dict JSON 可序列化、history 留痕。
全程内存合成数据，无 DB。
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from zephyr.signal_ashare.conditional_density_predictor import DensityForecast
from zephyr.signal_ashare.signal_factory import (
    SignalDraft,
    SignalFactory,
    SignalFactoryConfig,
    SignalStage,
)


def _density(degraded: bool = False) -> DensityForecast:
    return DensityForecast(
        condition="ALL",
        n_samples=60,
        mean=0.01,
        std=0.02,
        skewness=0.1,
        excess_kurtosis=0.2,
        quantiles={0.05: -0.02, 0.5: 0.01, 0.95: 0.04},
        var_95=-0.02,
        cvar_95=-0.03,
        degraded=degraded,
    )


def _factory() -> SignalFactory:
    return SignalFactory(
        SignalFactoryConfig(min_quality_score=0.4, max_crowding_score=0.8)
    )


def _draft(signal_id: str = "SIG-1") -> SignalDraft:
    return SignalDraft(
        signal_id=signal_id,
        symbol="600000.SH",
        direction="LONG",
        strength=0.7,
        source="unit_test",
    )


class TestRegister:
    def test_register_ok(self) -> None:
        f = _factory()
        rec = f.register(_draft())
        assert rec.stage is SignalStage.DRAFT
        assert rec.symbol == "600000.SH"

    def test_register_duplicate_id_rejected(self) -> None:
        f = _factory()
        f.register(_draft())
        with pytest.raises(ValueError, match="重复"):
            f.register(_draft())

    @pytest.mark.parametrize(
        "kw",
        [
            {"signal_id": ""},
            {"symbol": ""},
            {"direction": "SIDEWAYS"},
            {"strength": 1.5},
            {"strength": -0.1},
        ],
    )
    def test_register_invalid_fail_closed(self, kw: dict) -> None:
        base = {
            "signal_id": "SIG-X",
            "symbol": "600000.SH",
            "direction": "LONG",
            "strength": 0.5,
            "source": "unit_test",
        }
        base.update(kw)
        with pytest.raises(ValueError):
            _factory().register(SignalDraft(**base))


class TestAdvanceChain:
    def test_nine_stages_closed_set(self) -> None:
        assert len(SignalStage) == 9

    def test_full_chain_to_released(self) -> None:
        f = _factory()
        f.register(_draft())
        f.advance("SIG-1")  # DRAFT -> VALIDATED
        f.advance("SIG-1", density=_density())  # -> DENSITY_ENHANCED
        f.advance("SIG-1", quality_score=0.9)  # -> QUALITY_GATED
        f.advance("SIG-1", crowding_score=0.3)  # -> CROWDING_GATED
        rec = f.advance("SIG-1")  # -> FUNNELED
        assert rec.stage is SignalStage.FUNNELED
        rec = f.advance("SIG-1")  # -> RELEASED
        assert rec.stage is SignalStage.RELEASED
        assert rec.quantiles[0.95] == pytest.approx(0.04)
        assert rec.quality_score == pytest.approx(0.9)
        assert rec.crowding_score == pytest.approx(0.3)

    def test_density_required_fail_closed(self) -> None:
        f = _factory()
        f.register(_draft())
        f.advance("SIG-1")
        with pytest.raises(ValueError, match="density"):
            f.advance("SIG-1")

    def test_degraded_density_lowers_confidence(self) -> None:
        f = _factory()
        f.register(_draft())
        f.advance("SIG-1")
        rec = f.advance("SIG-1", density=_density(degraded=True))
        assert rec.confidence < 1.0
        f2 = _factory()
        f2.register(_draft())
        f2.advance("SIG-1")
        rec2 = f2.advance("SIG-1", density=_density(degraded=False))
        assert rec2.confidence > rec.confidence

    def test_quality_gate_blocks_and_notes(self) -> None:
        f = _factory()
        f.register(_draft())
        f.advance("SIG-1")
        f.advance("SIG-1", density=_density())
        rec = f.advance("SIG-1", quality_score=0.1)  # 低于 0.4 阈值
        assert rec.stage is SignalStage.DENSITY_ENHANCED  # 未推进
        assert any("质量门" in n for n in rec.notes)

    def test_crowding_gate_blocks_and_notes(self) -> None:
        f = _factory()
        f.register(_draft())
        f.advance("SIG-1")
        f.advance("SIG-1", density=_density())
        f.advance("SIG-1", quality_score=0.9)
        rec = f.advance("SIG-1", crowding_score=0.95)  # 高于 0.8 上限
        assert rec.stage is SignalStage.QUALITY_GATED
        assert any("拥挤度门" in n for n in rec.notes)

    def test_terminal_expire_retire(self) -> None:
        f = _factory()
        f.register(_draft())
        f.advance("SIG-1")
        f.advance("SIG-1", density=_density())
        f.advance("SIG-1", quality_score=0.9)
        f.advance("SIG-1", crowding_score=0.3)
        f.advance("SIG-1")
        f.advance("SIG-1")  # RELEASED
        rec = f.expire("SIG-1")
        assert rec.stage is SignalStage.EXPIRED
        rec = f.retire("SIG-1")
        assert rec.stage is SignalStage.RETIRED
        with pytest.raises(ValueError):
            f.advance("SIG-1")  # 终态不可再推进

    def test_expire_before_release_rejected(self) -> None:
        f = _factory()
        f.register(_draft())
        with pytest.raises(ValueError):
            f.expire("SIG-1")

    def test_unknown_id_fail_closed(self) -> None:
        f = _factory()
        with pytest.raises(ValueError):
            f.advance("NOPE")
        with pytest.raises(ValueError):
            f.get("NOPE")


class TestFunnelAndContract:
    def test_funnel_batch_only_funneled(self) -> None:
        f = _factory()
        for sid in ("A", "B"):
            f.register(_draft(sid))
        f.advance("A")
        f.advance("A", density=_density())
        f.advance("A", quality_score=0.9)
        f.advance("A", crowding_score=0.3)
        f.advance("A")  # A -> FUNNELED
        batch = f.funnel_batch()
        assert [r.signal_id for r in batch] == ["A"]

    def test_record_frozen_and_json_serializable(self) -> None:
        f = _factory()
        rec = f.register(_draft())
        with pytest.raises(dataclasses.FrozenInstanceError):
            rec.stage = SignalStage.RETIRED  # type: ignore[misc]
        json.dumps(rec.to_dict(), ensure_ascii=False)

    def test_history_accumulates(self) -> None:
        f = _factory()
        f.register(_draft())
        f.advance("SIG-1")
        rec = f.advance("SIG-1", density=_density())
        assert rec.history[:1] == (SignalStage.DRAFT.value,)
        assert rec.history[-1] == SignalStage.DENSITY_ENHANCED.value
