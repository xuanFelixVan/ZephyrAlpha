# [BLUEPRINT] MOD-SIG-065 | 待统筹登记（blueprint 未建，真源=缺口总账 GAP-F-30 + 45号作战手册 §5 数据契约）
# [MODULE] tests.signal_ashare.test_position_sector_context
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.position_sector_context
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] testing
# [INVARIANTS] 合成数据不触库不触网；pytest filterwarnings=error 兼容
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=持仓板块语境关联逻辑缺陷
# [TESTS] 本文件
# [A_module] module_id=MOD-SIG-065_test | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-SIG-065 持仓×板块语境关联查询 单元测试（GAP-F-30，合成数据不触库）。

覆盖：持仓股→板块归属（sector_constituent SCD-2）→主线概率/排名（MOD-SIG-064 复用）
→板内角色（MOD-SIG-062 复用）关联链；symbol 归一化；空仓/非法输入 fail-closed；
主线概率缺失独立降级；JSON 可序列化。
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import date

import pytest

from zephyr.signal_ashare.mainline_probability import (
    MainlineProbabilityItem,
    MainlineProbabilityResult,
)
from zephyr.signal_ashare.position_sector_context import (
    PositionHoldingInput,
    query_position_sector_context,
)
from zephyr.signal_ashare.sector_leader import (
    ROLE_BACKBONE,
    ROLE_LEADER,
    SectorLeaderBoard,
    SectorRoleGroup,
    StockRoleEntry,
)

TD = date(2026, 8, 21)


class _FakeCH:
    """鸭子类型 ch_client：仅答 sector_constituent / 最新板块数据日。"""

    def __init__(self, constituent_rows=None, latest: date | None = TD, exc_on: str | None = None):
        self._constituent = constituent_rows or []
        self._latest = latest
        self._exc_on = exc_on

    def execute(self, sql, params=None):
        if self._exc_on and self._exc_on in sql:
            raise RuntimeError(f"合成故障: {self._exc_on}")
        if "sector_constituent" in sql:
            return list(self._constituent)
        if "max(trade_date)" in sql:
            return [(self._latest,)]
        return []


def _entry(symbol: str, sector: str, role: str, consec: int = 0) -> StockRoleEntry:
    return StockRoleEntry(
        symbol=symbol,
        sector_code=sector,
        role=role,
        weight=1.0,
        score=80.0,
        consec_limit=consec,
        amount=1e8,
        pct_change=5.0,
        ret_5d=0.1,
        ret_20d=0.2,
        reasons=["合成"],
    )


def _prob(pct: float, code: str) -> MainlineProbabilityItem:
    return MainlineProbabilityItem(
        sector_code=code,
        sector_name=f"板块{code}",
        probability_pct=pct,
        rrg_score=1.0,
        relay_score=0.75,
        fund_score=1.0,
        echelon_score=1.0,
        weight_mode="static",
        reasons=["合成"],
    )


PROB = MainlineProbabilityResult(
    date=TD.isoformat(),
    items=[_prob(85.0, "881319.SH"), _prob(60.0, "881338.SH")],
)

BOARD = SectorLeaderBoard(
    trade_date=TD.isoformat(),
    sectors=[
        SectorRoleGroup(
            sector_code="881319.SH",
            leader=_entry("600000.SH", "881319.SH", ROLE_LEADER, consec=3),
            backbones=[_entry("600001.SH", "881319.SH", ROLE_BACKBONE)],
        )
    ],
    n_sectors=1,
    n_stocks=2,
)

CONSTITUENTS = [
    ("881319.SH", "600000.SH"),
    ("881319.SH", "600001.SH"),
    ("881338.SH", "600001.SH"),
]


class TestQueryPositionSectorContext:
    def test_happy_path(self):
        result = query_position_sector_context(
            trade_date=TD,
            positions=[PositionHoldingInput(symbol="600000"), PositionHoldingInput(symbol="600001.SH", weight=0.5)],
            ch_client=_FakeCH(CONSTITUENTS),
            probability_result=PROB,
            leader_board=BOARD,
        )
        assert not result.degraded
        assert result.date == TD.isoformat()
        by_symbol = {it.symbol: it for it in result.items}
        # 600000：半导体龙头，主线概率 85 排名第 1
        e0 = by_symbol["600000.SH"]
        assert e0.best_sector_code == "881319.SH"
        s0 = e0.sectors[0]
        assert s0.mainline_probability_pct == 85.0
        assert s0.mainline_rank == 1
        assert s0.role_in_sector == ROLE_LEADER
        assert s0.leader_consec == 3
        # 600001：双板块归属（半导体中军 + 通信设备无角色）
        e1 = by_symbol["600001.SH"]
        codes = {s.sector_code for s in e1.sectors}
        assert codes == {"881319.SH", "881338.SH"}
        semi = next(s for s in e1.sectors if s.sector_code == "881319.SH")
        assert semi.role_in_sector == ROLE_BACKBONE
        comm = next(s for s in e1.sectors if s.sector_code == "881338.SH")
        assert comm.mainline_probability_pct == 60.0
        assert comm.mainline_rank == 2
        assert comm.role_in_sector is None  # 该板无此股角色记录
        json.dumps(asdict(result), ensure_ascii=False)

    def test_symbol_without_sector(self):
        """持仓股不属于任何板块 → 空语境+留痕，不炸。"""
        result = query_position_sector_context(
            trade_date=TD,
            positions=[PositionHoldingInput(symbol="000001")],
            ch_client=_FakeCH(CONSTITUENTS),
            probability_result=PROB,
            leader_board=BOARD,
        )
        item = result.items[0]
        assert item.symbol == "000001.SZ"
        assert item.sectors == []
        assert item.best_sector_code is None
        assert any("无板块归属" in n for n in item.notes)

    def test_positions_none_fail_closed(self):
        """positions=None → ValueError（CH 无持仓表真源，调用方必须显式供给）。"""
        with pytest.raises(ValueError):
            query_position_sector_context(trade_date=TD, positions=None, ch_client=_FakeCH())

    def test_positions_empty(self):
        result = query_position_sector_context(
            trade_date=TD,
            positions=[],
            ch_client=_FakeCH(CONSTITUENTS),
            probability_result=PROB,
            leader_board=BOARD,
        )
        assert result.items == []
        assert not result.degraded
        assert any("空仓" in a for a in result.annotations)

    def test_invalid_symbol_skipped(self):
        result = query_position_sector_context(
            trade_date=TD,
            positions=[PositionHoldingInput(symbol="ABC"), PositionHoldingInput(symbol="600000")],
            ch_client=_FakeCH(CONSTITUENTS),
            probability_result=PROB,
            leader_board=BOARD,
        )
        assert [it.symbol for it in result.items] == ["600000.SH"]
        assert any("ABC" in n for n in result.notes)

    def test_probability_missing_degrades_independently(self):
        """主线概率降级 → 排名/概率字段 None，板块归属与角色仍出。"""
        degraded_prob = MainlineProbabilityResult(date=TD.isoformat(), degraded=True, notes=["候选降级"])
        result = query_position_sector_context(
            trade_date=TD,
            positions=[PositionHoldingInput(symbol="600000")],
            ch_client=_FakeCH(CONSTITUENTS),
            probability_result=degraded_prob,
            leader_board=BOARD,
        )
        s0 = result.items[0].sectors[0]
        assert s0.sector_code == "881319.SH"
        assert s0.mainline_probability_pct is None
        assert s0.mainline_rank is None
        assert s0.role_in_sector == ROLE_LEADER
        assert any("主线概率" in n for n in result.notes)

    def test_constituent_query_failure_degraded(self):
        result = query_position_sector_context(
            trade_date=TD,
            positions=[PositionHoldingInput(symbol="600000")],
            ch_client=_FakeCH(exc_on="sector_constituent"),
            probability_result=PROB,
            leader_board=BOARD,
        )
        assert result.degraded
        assert result.items == []

    def test_trade_date_format_fail_closed(self):
        with pytest.raises(ValueError):
            query_position_sector_context(
                trade_date="2026/08/21",
                positions=[],
                ch_client=_FakeCH(),
            )
