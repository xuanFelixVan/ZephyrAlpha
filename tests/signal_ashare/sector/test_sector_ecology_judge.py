# [BLUEPRINT] MOD-SIG-038 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""MOD-SIG-143 sector_ecology_judge 单元测试（night-gw-2300 自裁批）。

红蓝手法：红-边界（负连击/集中度越界/阈值 2·0.30·90 精确边界）/红-契约（三态封闭集）
/红-优先级（CLIMAX > MAINLINE > CHAOS）/红-前视（无墙钟）/红-竞态（frozen+确定性）。
"""

from __future__ import annotations

import json

import pytest

from zephyr.signal_ashare.core.sector_ecology_judge import (
    CLIMAX_SCORE_MIN,
    ECOLOGY_CHAOS,
    ECOLOGY_CLIMAX,
    ECOLOGY_MAINLINE_CLEAR,
    LEAD_STREAK_MIN,
    TURNOVER_CONCENTRATION_MIN,
    SectorEcologyInputError,
    judge_sector_ecology,
)


class TestContract:
    def test_thresholds_match_documented_values(self) -> None:
        """阈值全部取自已锚定模块文档值（零自创）。"""
        assert LEAD_STREAK_MIN == 2  # MOD-SIG-064 无主线判据反向
        assert TURNOVER_CONCENTRATION_MIN == 0.30  # 节点真源"吸走 30%+成交额"
        assert CLIMAX_SCORE_MIN == 90.0  # sector_rotation_state 高潮≥90

    def test_negative_streak_fail_closed(self) -> None:
        with pytest.raises(SectorEcologyInputError, match="连击为负"):
            judge_sector_ecology(-1, 0.5, 50.0)

    def test_concentration_out_of_range_fail_closed(self) -> None:
        with pytest.raises(SectorEcologyInputError, match="越界"):
            judge_sector_ecology(3, 1.5, 50.0)

    def test_nan_climax_fail_closed(self) -> None:
        with pytest.raises(SectorEcologyInputError, match="非有限"):
            judge_sector_ecology(3, 0.5, float("nan"))


class TestTrichotomy:
    def test_mainline_clear(self) -> None:
        """梯队连击≥2 + 集中度≥30% → 主线清晰。"""
        s = judge_sector_ecology(3, 0.35, 50.0)
        assert s.ecology == ECOLOGY_MAINLINE_CLEAR
        assert "聚焦" in s.reason

    def test_climax_priority_over_mainline(self) -> None:
        """高潮与主线同时成立 → 高潮优先（风险方向优先）。"""
        s = judge_sector_ecology(5, 0.60, 95.0)
        assert s.ecology == ECOLOGY_CLIMAX

    def test_chaos_when_no_mainline_no_climax(self) -> None:
        s = judge_sector_ecology(1, 0.20, 40.0)
        assert s.ecology == ECOLOGY_CHAOS
        assert "降仓等待" in s.reason

    def test_high_concentration_alone_is_not_mainline(self) -> None:
        """集中度高但梯队连击不足 → 仍混沌。"""
        s = judge_sector_ecology(1, 0.50, 30.0)
        assert s.ecology == ECOLOGY_CHAOS

    def test_degraded_chains_not_chaos_by_default(self) -> None:
        """连击足但集中度不足 → 混沌（主线瓦解）。"""
        s = judge_sector_ecology(4, 0.10, 50.0)
        assert s.ecology == ECOLOGY_CHAOS


class TestBoundaries:
    def test_streak_exactly_2_with_concentration(self) -> None:
        s = judge_sector_ecology(2, 0.35, 50.0)
        assert s.ecology == ECOLOGY_MAINLINE_CLEAR

    def test_streak_1_conc_exactly_30_is_chaos(self) -> None:
        s = judge_sector_ecology(1, 0.30, 50.0)
        assert s.ecology == ECOLOGY_CHAOS

    def test_climax_exactly_90(self) -> None:
        s = judge_sector_ecology(3, 0.50, 90.0)
        assert s.ecology == ECOLOGY_CLIMAX

    def test_climax_89_not_climax(self) -> None:
        s = judge_sector_ecology(0, 0.50, 89.0)
        assert s.ecology == ECOLOGY_CHAOS


class TestPurity:
    def test_deterministic(self) -> None:
        a = judge_sector_ecology(3, 0.35, 50.0)
        b = judge_sector_ecology(3, 0.35, 50.0)
        assert a == b

    def test_frozen(self) -> None:
        s = judge_sector_ecology(3, 0.35, 50.0)
        with pytest.raises(Exception):
            s.ecology = "X"  # type: ignore[misc]

    def test_to_dict_json_round_trip(self) -> None:
        payload = judge_sector_ecology(3, 0.35, 50.0).to_dict()
        restored = json.loads(json.dumps(payload, ensure_ascii=False))
        assert restored["ecology"] == ECOLOGY_MAINLINE_CLEAR
        assert set(restored) == {
            "ecology", "lead_streak", "turnover_concentration", "climax_score", "reason",
        }

    def test_no_wall_clock_in_output(self) -> None:
        d = judge_sector_ecology(3, 0.35, 50.0).to_dict()
        assert not any(k.lower().startswith(("ts", "time", "now", "date")) for k in d)
