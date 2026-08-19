"""三级放行门槛 + 水温→板块信号响应映射 单元测试（22 号 spec §3.1⑩⑪）"""

import pytest

from zephyr.signal_ashare.sector_gate import (
    GATE_BLOCKED,
    GATE_CORE_HOT,
    GATE_SECONDARY,
    GATE_WILDCARD,
    RRG_FILTER_ALL,
    RRG_FILTER_IMPROVING_ONLY,
    RRG_FILTER_LEADING_ONLY,
    RRG_FILTER_NONE,
    GateThresholds,
    WaterTemp,
    admission_gate,
    apply_rrg_filter,
    water_temp_response,
)

TOP = frozenset({"880101.SH", "880102.SH"})
RETAINED = frozenset({"880101.SH", "880102.SH", "880201.SH", "880202.SH"})


class TestWaterTempResponse:
    @pytest.mark.parametrize(
        ("temp", "weight", "level2", "level3", "rrg_filter"),
        [
            (WaterTemp.NEUTRAL, 1.0, 0.60, 0.80, RRG_FILTER_ALL),
            (WaterTemp.RISK_ON, 0.5, 0.60, 0.80, RRG_FILTER_ALL),
            (WaterTemp.PANIC_REPAIR, 0.5, 0.50, 0.70, RRG_FILTER_IMPROVING_ONLY),
            (WaterTemp.RISK_OFF, 0.3, 0.80, 0.90, RRG_FILTER_LEADING_ONLY),
            (WaterTemp.CRASH, 0.0, 1.01, 1.01, RRG_FILTER_NONE),
        ],
    )
    def test_five_tiers(self, temp, weight, level2, level3, rrg_filter):
        resp = water_temp_response(temp)
        assert resp.signal_weight == weight
        assert resp.gate_thresholds.level2 == level2
        assert resp.gate_thresholds.level3 == level3
        assert resp.rrg_filter == rrg_filter

    def test_string_input_accepted(self):
        assert water_temp_response("NEUTRAL").signal_weight == 1.0

    def test_unknown_temp_raises(self):
        with pytest.raises(ValueError, match="未知水温档位"):
            water_temp_response("LUKWARM")

    def test_risk_on_consensus_climax_double_suppression(self):
        """RISK_ON + CONSENSUS_CLIMAX → 0.5×0.5=0.25 双重抑制过热追高"""
        resp = water_temp_response(WaterTemp.RISK_ON, consensus_climax=True)
        assert resp.signal_weight == pytest.approx(0.25)

    def test_climax_flag_ignored_on_other_tiers(self):
        """CONSENSUS_CLIMAX 标志只在 RISK_ON 档生效"""
        resp = water_temp_response(WaterTemp.NEUTRAL, consensus_climax=True)
        assert resp.signal_weight == 1.0


class TestAdmissionGate:
    def test_core_hot_passthrough_even_zero_score(self):
        """级别1：核心热门板块直通（不看个股强度）"""
        assert admission_gate("880101.SH", 0.0, TOP) == (True, GATE_CORE_HOT)

    def test_secondary_level_boundary(self):
        """级别2：非核心热门 + 个股强度 ≥0.60（v2.1 标准）"""
        assert admission_gate("880999.SH", 0.60, TOP) == (True, GATE_SECONDARY)
        assert admission_gate("880999.SH", 0.59, TOP) == (False, GATE_BLOCKED)

    def test_wildcard_super_stock(self):
        """级别3：超强个股通配（无视板块限制）≥0.80"""
        assert admission_gate("880999.SH", 0.85, TOP) == (True, GATE_WILDCARD)

    def test_blocked(self):
        assert admission_gate("880999.SH", 0.30, TOP) == (False, GATE_BLOCKED)

    def test_retained_sector_required_when_provided(self):
        """提供保留板块集时：级别2 要求板块在保留集内；不在保留集只能靠通配"""
        # 板块在保留集（非 Top）+ 0.65 → SECONDARY
        assert admission_gate("880201.SH", 0.65, TOP, retained_sectors=RETAINED) == (
            True,
            GATE_SECONDARY,
        )
        # 板块不在保留集 + 0.65 → 不满足级别2；0.65<0.80 → BLOCKED
        assert admission_gate("880999.SH", 0.65, TOP, retained_sectors=RETAINED) == (
            False,
            GATE_BLOCKED,
        )
        # 板块不在保留集 + 0.85 → WILDCARD
        assert admission_gate("880999.SH", 0.85, TOP, retained_sectors=RETAINED) == (
            True,
            GATE_WILDCARD,
        )

    def test_risk_off_thresholds_tightened(self):
        """水温联动：RISK_OFF 阈值 0.80/0.90（仅强个股放行）"""
        th = water_temp_response(WaterTemp.RISK_OFF).gate_thresholds
        assert admission_gate("880999.SH", 0.79, TOP, th) == (False, GATE_BLOCKED)
        assert admission_gate("880999.SH", 0.85, TOP, th) == (True, GATE_SECONDARY)
        assert admission_gate("880999.SH", 0.95, TOP, th) == (True, GATE_WILDCARD)

    def test_panic_repair_thresholds_relaxed(self):
        """水温联动：PANIC_REPAIR 阈值放宽 0.50/0.70（超跌反弹期）"""
        th = water_temp_response(WaterTemp.PANIC_REPAIR).gate_thresholds
        assert admission_gate("880999.SH", 0.55, TOP, th) == (True, GATE_SECONDARY)
        assert admission_gate("880999.SH", 0.75, TOP, th) == (True, GATE_WILDCARD)

    def test_crash_thresholds_unreachable(self):
        """CRASH：阈值 1.01 不可达 → 非核心热门全拦截"""
        th = water_temp_response(WaterTemp.CRASH).gate_thresholds
        assert admission_gate("880999.SH", 1.0, TOP, th) == (False, GATE_BLOCKED)
        # 但板块归属直通仍有效——CRASH 全拦截由 signal_weight=0 + rrg_filter=NONE 承担
        assert admission_gate("880101.SH", 0.0, TOP, th) == (True, GATE_CORE_HOT)

    def test_default_thresholds_v21(self):
        """默认阈值 = v2.1 标准 0.60/0.80"""
        th = GateThresholds()
        assert th.level2 == 0.60
        assert th.level3 == 0.80


class TestApplyRrgFilter:
    @pytest.mark.parametrize(
        ("rrg_filter", "quadrant", "expected"),
        [
            (RRG_FILTER_ALL, "LEADING", True),
            (RRG_FILTER_ALL, "LAGGING", True),
            (RRG_FILTER_IMPROVING_ONLY, "IMPROVING", True),
            (RRG_FILTER_IMPROVING_ONLY, "LEADING", False),
            (RRG_FILTER_LEADING_ONLY, "LEADING", True),
            (RRG_FILTER_LEADING_ONLY, "WEAKENING", False),
            (RRG_FILTER_NONE, "LEADING", False),
            (RRG_FILTER_NONE, "IMPROVING", False),
        ],
    )
    def test_filters(self, rrg_filter, quadrant, expected):
        assert apply_rrg_filter(quadrant, rrg_filter) is expected
