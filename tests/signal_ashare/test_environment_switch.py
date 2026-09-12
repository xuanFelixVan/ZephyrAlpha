# [BLUEPRINT] MOD-SIG-038 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""MOD-SIG-138 environment_switch 单元测试（长城夜班 night-gw-2300，Owner 立项）。

红蓝手法覆盖：红-边界（未知状态/负值/NaN/8000 阈值边界）/红-契约（六段封闭集）
/红-前视（无墙钟，输出封闭键集）/红-竞态（frozen 不可变）。
"""

from __future__ import annotations

import json

import pytest

from zephyr.signal_ashare.core.environment_switch import (
    LOW_TURNOVER_THRESHOLD_YI,
    SIX_STATES,
    EnvironmentSwitchInputError,
    evaluate_environment_switches,
)


class TestContract:
    def test_six_states_closed_set(self) -> None:
        assert SIX_STATES == (
            "capitulation",
            "accumulation",
            "ignition",
            "expansion",
            "euphoria",
            "distribution",
        )

    def test_unknown_state_fail_closed(self) -> None:
        with pytest.raises(EnvironmentSwitchInputError, match="未知情绪状态"):
            evaluate_environment_switches("主升", 9000.0)  # 中文五阶段名不收（调用方归并）

    def test_negative_turnover_fail_closed(self) -> None:
        with pytest.raises(EnvironmentSwitchInputError, match="成交额非法"):
            evaluate_environment_switches("expansion", -1.0)

    def test_nan_turnover_fail_closed(self) -> None:
        with pytest.raises(EnvironmentSwitchInputError, match="成交额非法"):
            evaluate_environment_switches("expansion", float("nan"))


class TestSwitchTable:
    def test_capitulation_short_term_chain_full_stop(self) -> None:
        """冰点=短线链全停只留波段链（节点真源）。"""
        s = evaluate_environment_switches("capitulation", 12000.0)
        assert s.short_term_chain_on is False
        assert s.swing_chain_on is True
        assert s.first_board_filter_on is False
        assert s.tighten_risk is False

    def test_euphoria_tighten_only(self) -> None:
        """极端高潮=反向收紧（不止链）。"""
        s = evaluate_environment_switches("euphoria", 15000.0)
        assert s.tighten_risk is True
        assert s.short_term_chain_on is True

    def test_expansion_all_on(self) -> None:
        s = evaluate_environment_switches("expansion", 12000.0)
        assert (s.first_board_filter_on, s.short_term_chain_on, s.swing_chain_on) == (
            True,
            True,
            True,
        )
        assert s.tighten_risk is False

    def test_distribution_cuts_short_keeps_swing(self) -> None:
        s = evaluate_environment_switches("distribution", 9000.0)
        assert s.short_term_chain_on is False
        assert s.swing_chain_on is True


class TestTurnoverGate:
    def test_low_turnover_stops_first_board_even_in_expansion(self) -> None:
        """两市成交<8000 亿=首板筛选器停（节点真源，实证：地量首板次日溢价为负）。"""
        s = evaluate_environment_switches("expansion", 7000.0)
        assert s.first_board_filter_on is False
        assert any("地量首板" in n for n in s.notes)

    def test_boundary_exactly_8000_yi_stays_on(self) -> None:
        """阈值边界：恰为 8000 亿不触发（< 严格小于）。"""
        assert LOW_TURNOVER_THRESHOLD_YI == 8000.0
        s = evaluate_environment_switches("expansion", 8000.0)
        assert s.first_board_filter_on is True

    def test_just_below_boundary_stops(self) -> None:
        s = evaluate_environment_switches("expansion", 7999.99)
        assert s.first_board_filter_on is False


class TestPurity:
    def test_deterministic(self) -> None:
        a = evaluate_environment_switches("capitulation", 7000.0)
        b = evaluate_environment_switches("capitulation", 7000.0)
        assert a == b

    def test_frozen(self) -> None:
        s = evaluate_environment_switches("expansion", 9000.0)
        with pytest.raises(Exception):
            s.tighten_risk = True  # type: ignore[misc]

    def test_to_dict_json_round_trip(self) -> None:
        payload = evaluate_environment_switches("euphoria", 6000.0).to_dict()
        restored = json.loads(json.dumps(payload, ensure_ascii=False))
        assert restored["tighten_risk"] is True
        assert restored["first_board_filter_on"] is False
        assert set(restored) == {
            "state",
            "turnover_amount_yi",
            "first_board_filter_on",
            "short_term_chain_on",
            "swing_chain_on",
            "tighten_risk",
            "notes",
        }
