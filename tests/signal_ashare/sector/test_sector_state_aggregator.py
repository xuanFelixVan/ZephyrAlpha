# [TEST] sector_state_aggregator——S10 五成分组装 + D2 偏好映射纯函数单测
# [TTL] permanent
# 真源：22 号 spec §3.1①④⑧⑨ + 骨架稿 v0；全合成面板零 CH 依赖（测试隔离铁律）。
import math
from datetime import date

import pytest

from zephyr.signal_ashare.sector.sector_state_aggregator import (
    AGGREGATOR_VERSION,
    MOCK_EMOTION_INDEX,
    SectorPanelInputs,
    assemble_sector_states,
    compute_market_state,
    emotion_band,
    map_preference,
    quadrant_admits,
    regime_group,
)

T = date(2026, 9, 22)


def _linear_panel(codes_and_drift: list[tuple[str, float]], n: int = 70) -> dict[str, list[float]]:
    """等长日K 面板：close_t = 100 × (1+drift)^t（确定性，无随机）。"""
    return {code: [100.0 * ((1.0 + drift) ** t) for t in range(n)] for code, drift in codes_and_drift}


# ----------------------------------------------------------------------
# S10 五成分
# ----------------------------------------------------------------------


class TestAssembleSectorStates:
    def test_momentum_orders_by_drift(self):
        panel = _linear_panel([("A", 0.01), ("B", 0.0), ("C", -0.01)])
        rows, _ = assemble_sector_states(panel, trade_date=T, benchmark_closes=[100.0] * 70)
        mom = {r.sector_code: r.momentum_pct for r in rows}
        assert None not in mom.values()
        assert mom["A"] > mom["B"] > mom["C"]
        assert all(0.0 <= v <= 1.0 for v in mom.values())

    def test_rrg_leading_for_outperformer_and_insufficient_short(self):
        panel = _linear_panel([("WIN", 0.008), ("FLAT", 0.0)])
        panel["SHORT"] = [100.0, 101.0]  # 2 日 < 62 日 → rrg insufficient
        rows, _ = assemble_sector_states(panel, trade_date=T, benchmark_closes=[100.0] * 70)
        by = {r.sector_code: r for r in rows}
        assert by["WIN"].rrg_quadrant == "leading"
        assert by["FLAT"].rrg_quadrant in {"lagging", "improving"}
        comp_short = [c for c in by["SHORT"].components if c["name"] == "rrg_quadrant"][0]
        assert comp_short["status"] == "insufficient"

    def test_strength_missing_without_constituents(self):
        panel = _linear_panel([("A", 0.005)])
        rows, _ = assemble_sector_states(
            panel,
            trade_date=T,
            benchmark_closes=[100.0] * 70,
            panels=SectorPanelInputs(limit_up_by_sector={"A": 3}),  # 无成分分母 → strength missing
        )
        assert rows[0].strength is None
        comp = [c for c in rows[0].components if c["name"] == "strength"][0]
        assert comp["status"] == "missing"

    def test_strength_full_components(self):
        panel = _linear_panel([("A", 0.05)])  # 当日涨幅 5% > 3% → 趋势 30 分
        rows, _ = assemble_sector_states(
            panel,
            trade_date=T,
            benchmark_closes=[100.0] * 70,
            panels=SectorPanelInputs(
                limit_up_by_sector={"A": 10},
                tier_by_sector={"A": (2, 1)},  # 有三板 → 30 分
                constituents_by_sector={"A": 50},  # 涨停比 0.2 >10% → 极强 40 分
            ),
        )
        # 40(涨停比极强) + 30(梯队完整) + 30(趋势强) = 100
        assert rows[0].strength == 100.0
        assert rows[0].watch_score is not None
        names = {c["name"] for c in rows[0].components}
        assert {"momentum_pct", "rrg_quadrant", "strength", "net_inflow_pct", "capital_score"} <= names

    def test_net_inflow_percentile(self):
        panel = _linear_panel([("A", 0.001), ("B", 0.001), ("C", 0.001)])
        rows, _ = assemble_sector_states(
            panel,
            trade_date=T,
            benchmark_closes=[100.0] * 70,
            panels=SectorPanelInputs(sector_main_inflow={"A": 100.0, "B": 0.0, "C": -100.0}),
        )
        nif = {r.sector_code: r.net_inflow_pct for r in rows}
        assert nif["A"] == 1.0 and nif["C"] == 0.0
        cap = [c for c in rows[0].components if c["name"] == "capital_score"][0]
        assert cap["status"] == "missing"  # v0 观察列如实缺

    def test_market_state_consensus_climax(self):
        # 8 板块：6 涨 2 跌（up_ratio=0.75>0.70），两只巨量（hhi>0.30）→ CONSENSUS_CLIMAX
        panel = _linear_panel([(f"S{i}", 0.02 if i < 6 else -0.01) for i in range(8)])
        pct = {f"S{i}": (0.05 if i < 6 else -0.02) for i in range(8)}
        amounts = {f"S{i}": [10.0] * 10 for i in range(8)}
        amounts["S0"][-1] = 200.0
        amounts["S1"][-1] = 200.0
        ms = compute_market_state(pct, amounts)
        assert ms.up_ratio == pytest.approx(0.75)
        assert ms.hhi_top5 > 0.30
        assert ms.rotation_state == "CONSENSUS_CLIMAX"
        assert ms.watch_score == -0.08

    def test_market_state_healthy_mainline(self):
        # 单一主线连续领涨：S0 恒强、成交额分散（hhi<0.20）
        panel = _linear_panel([(f"S{i}", 0.001 * (8 - i)) for i in range(8)])
        pct = {f"S{i}": 0.01 * (8 - i) for i in range(8)}
        amounts = {f"S{i}": [100.0] * 10 for i in range(8)}
        ms = compute_market_state(
            pct,
            amounts,
            leader_history=["S0", "S0", "S0"],
            prev_day_pct_by_sector={c: 0.01 for c in pct},
        )
        assert ms.lead_streak == 3
        assert ms.hhi_top5 < 0.20
        assert ms.rotation_state == "HEALTHY_MAINLINE"
        assert ms.watch_score == 0.03

    def test_version_tagged(self):
        panel = _linear_panel([("A", 0.005)])
        rows, _ = assemble_sector_states(panel, trade_date=T, benchmark_closes=[100.0] * 70)
        assert AGGREGATOR_VERSION == "0.1.0"
        assert rows  # 非空


# ----------------------------------------------------------------------
# D2 偏好映射
# ----------------------------------------------------------------------


class TestMapPreference:
    def test_all_nine_cells(self):
        expect = {
            ("low", "osc"): "DEFENSIVE",
            ("low", "up"): "BALANCED",
            ("low", "down"): "DEFENSIVE",
            ("mid", "osc"): "FOLLOW",
            ("mid", "up"): "OFFENSIVE",
            ("mid", "down"): "BALANCED",
            ("high", "osc"): "CROWDING_WARN",
            ("high", "up"): "OFFENSIVE",
            ("high", "down"): "DEFENSIVE",
        }
        for (band, grp), label in expect.items():
            emo = {"low": 0.2, "mid": 0.55, "high": 0.85}[band]
            reg = {"osc": "r1", "up": "r3", "down": "r4"}[grp]
            pref = map_preference(reg, emo)
            assert pref.preference_label == label, (band, grp)
            assert 0.8 <= pref.tilt <= 1.2  # frozen 界
            assert pref.axis_status == "ok"

    def test_regime_groups(self):
        assert regime_group("r2") == "osc" and regime_group("r12") == "up"
        assert regime_group("r10") == "down" and regime_group("r11") == "down"
        assert regime_group("r7") == "osc"  # 未观测档归震荡

    def test_emotion_bands(self):
        assert emotion_band(0.4) == "low"
        assert emotion_band(0.41) == "mid"
        assert emotion_band(0.7) == "high"
        assert emotion_band(None) == "mid"

    def test_mock_axis_status(self):
        pref = map_preference("r3", None)
        assert pref.axis_status == "mock"
        assert pref.emotion_band == "mid"
        assert "INSUFFICIENT" in pref.note
        assert MOCK_EMOTION_INDEX == 0.5

    def test_banned_quadrant_admission(self):
        pref = map_preference("r3", 0.55)  # 温和×上行 → OFFENSIVE, lagging 禁入
        assert pref.banned_quadrant == "lagging"
        assert quadrant_admits(pref.banned_quadrant, "leading")
        assert not quadrant_admits(pref.banned_quadrant, "lagging")
        assert quadrant_admits("", "lagging")  # 无禁入=全放行
        assert quadrant_admits("lagging", None)  # 无象限=放行

    def test_unknown_regime_flagged(self):
        pref = map_preference("r9", 0.55)
        assert pref.regime_group == "osc"
        assert pref.axis_status == "unknown_regime"

    def test_no_future_input(self):
        """防循环红线：映射只吃两轴输入，不触任何行情参数（签名级自证）。"""
        import inspect

        sig = inspect.signature(map_preference)
        assert list(sig.parameters) == ["regime_dominant", "emotion_index"]
        assert math.isfinite(map_preference("r1", 0.3).tilt)
