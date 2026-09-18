# [TTL] permanent
"""sector_strength_wiring 接线适配层单元测试（night-gw-2300 接线批）。

红蓝手法：红-边界（空池/缺维度/集中度零分母/平票）/红-契约（rank 归一 0-100/
CLIMAX 优先）/红-前视（无墙钟）/红-竞态（frozen+确定性）。
"""

from __future__ import annotations

import json

import pytest

from zephyr.signal_ashare.core.sector_ecology_judge import (
    ECOLOGY_CLIMAX,
    ECOLOGY_MAINLINE_CLEAR,
)
from zephyr.signal_ashare.core.sector_strength_wiring import (
    SectorWiringInputError,
    wire_from_report,
)


def _report(n: int = 5, lead: int | None = 3, flows: list[float] | None = None) -> dict:
    entries = []
    fl = flows or [0.2, 0.5, 1.0, 2.0, 3.0][: max(1, min(n, 5))]
    for i in range(n):
        entries.append(
            {
                "sector_name": f"板块{i}",
                "strength_score": 50.0 + i * 5,
                "ranking_score": 60.0 - i * 5,
                "momentum_score": 0.2 + i * 0.1,
                "main_net_inflow": fl[i % len(fl)],
                "limit_up_ratio": 0.03,
            }
        )
    rep: dict = {"top_sectors": entries}
    if lead is not None:
        rep["lead_streak"] = lead
    return rep


class TestContract:
    def test_non_dict_fail_closed(self) -> None:
        with pytest.raises(SectorWiringInputError, match="非映射"):
            wire_from_report(["not", "a", "dict"])  # type: ignore[arg-type]

    def test_missing_top_sectors_fail_closed(self) -> None:
        with pytest.raises(SectorWiringInputError, match="top_sectors"):
            wire_from_report({"lead_streak": 3})


class TestWiring:
    def test_pool_and_ecology_happy_path(self) -> None:
        r = wire_from_report(_report(5, lead=3), trade_date="2026-09-12")
        assert len(r.pool) == 5
        assert sum(1 for s in r.pool if s.in_candidate_pool) >= 1
        assert r.ecology is not None
        assert r.trade_date == "2026-09-12"

    def test_rank_normalization_spans_full_range(self) -> None:
        """rank-based：等差输入归一后最强板块分应显著高于最弱。"""
        r = wire_from_report(_report(5))
        comps = [s.composite for s in r.pool]
        assert max(comps) - min(comps) > 30

    def test_missing_dimension_sector_skipped_with_note(self) -> None:
        rep = _report(3, lead=3)
        rep["top_sectors"][1]["ranking_score"] = None  # 缺动量活跃维
        r = wire_from_report(rep)
        assert len(r.pool) == 2
        assert any("缺维度剔除" in n for n in r.notes)

    def test_ecology_none_when_lead_missing(self) -> None:
        r = wire_from_report(_report(4, lead=None))
        assert r.ecology is None
        assert any("生态不判定" in n for n in r.notes)

    def test_climax_via_breadth_label(self) -> None:
        """高潮分代理=涨停比分档映射（极强→95）。"""
        rep = _report(4, lead=3)
        rep["breadth_label"] = "极强"
        r = wire_from_report(rep)
        assert r.ecology is not None
        assert r.ecology.climax_score == 95.0


class TestPurity:
    def test_deterministic(self) -> None:
        a = wire_from_report(_report(5, lead=2))
        b = wire_from_report(_report(5, lead=2))
        assert a == b

    def test_frozen(self) -> None:
        r = wire_from_report(_report(3))
        with pytest.raises(Exception):
            r.pool = ()  # type: ignore[misc]

    def test_to_dict_json_round_trip(self) -> None:
        d = wire_from_report(_report(4, lead=3)).to_dict()
        restored = json.loads(json.dumps(d, ensure_ascii=False))
        assert restored["ecology"]["ecology"] in (ECOLOGY_CLIMAX, ECOLOGY_MAINLINE_CLEAR)
