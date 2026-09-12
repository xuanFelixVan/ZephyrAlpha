# [A_test] module_id: MOD-SIG-066 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SIG-066 | 待统筹登记 | 缺口总账 GAP-F-06 + 45号 §4 W1
# [MODULE] tests.signal_ashare.test_war_pool_generator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""WarPoolGenerator (MOD-SIG-066) 施工验证测试。

覆盖：
- 交集纪律：主线候选板块龙头 × 个股催化剂交集才入池；无催化剂龙头不入池；
  催化剂股不在主线板块龙头位不入池。
- 出池规模：pool_target 截断（默认 3）、不足 pool_min 留痕、空交集 no_pool_flag。
- 排序：pool_score 降序（角色分×0.5+主线分×0.3+催化剂×0.2 默认权重）；确定性 tie-break。
- 中军开关：include_backbones=True 时中军补位。
- 适配器：sectors_from_probability（064）/sectors_from_candidates（061）。
- 装配层：注入 probability_result/leader_board/catalyst_provider 全内存跑通；
  064 降级 → 整体 degraded；催化剂 provider 缺省 → 空池注解不强行出池。
- 契约：to_dict JSON 可序列化；非法输入 fail-closed。
全程内存构造，无 DB 无 CH。
"""

from __future__ import annotations

import json

import pytest

from zephyr.signal_ashare.mainline_candidates import MainlineCandidate, MainlineCandidatesResult
from zephyr.signal_ashare.mainline_probability import (
    MainlineProbabilityItem,
    MainlineProbabilityResult,
)
from zephyr.signal_ashare.sector_leader import SectorLeaderBoard, SectorRoleGroup, StockRoleEntry
from zephyr.signal_ashare.war_pool_generator import (
    CatalystRecord,
    WarPoolConfig,
    WarPoolResult,
    generate_war_pool,
    sectors_from_candidates,
    sectors_from_probability,
    select_war_pool,
)

TRADE_DATE = "2026-08-24"


def _entry(symbol: str, sector: str, role: str = "leader", score: float = 80.0, consec: int = 2) -> StockRoleEntry:
    return StockRoleEntry(
        symbol=symbol,
        sector_code=sector,
        role=role,
        weight=1.0,
        score=score,
        consec_limit=consec,
        amount=1e9,
        pct_change=5.0,
        ret_5d=0.08,
        ret_20d=0.15,
    )


def _group(sector: str, leader: str | None, backbones: tuple[str, ...] = (), score: float = 80.0) -> SectorRoleGroup:
    return SectorRoleGroup(
        sector_code=sector,
        leader=_entry(leader, sector, score=score) if leader else None,
        backbones=[_entry(s, sector, role="backbone", score=60.0, consec=0) for s in backbones],
    )


def _prob(sectors: list[tuple[str, str, float | None]]) -> MainlineProbabilityResult:
    return MainlineProbabilityResult(
        date=TRADE_DATE,
        items=[
            MainlineProbabilityItem(
                sector_code=code,
                sector_name=name,
                probability_pct=pct,
                rrg_score=None,
                relay_score=None,
                fund_score=None,
                echelon_score=None,
                weight_mode="static",
            )
            for code, name, pct in sectors
        ],
    )


def _board(*groups: SectorRoleGroup) -> SectorLeaderBoard:
    return SectorLeaderBoard(trade_date=TRADE_DATE, sectors=list(groups), n_sectors=len(groups), n_stocks=10)


def _cat(symbol: str, strength: float = 0.8, ctype: str = "EARNINGS") -> CatalystRecord:
    return CatalystRecord(symbol=symbol, catalyst_type=ctype, strength=strength, source="test", name="业绩预告预增")


# ── 输入校验 ──


def test_catalyst_strength_out_of_range() -> None:
    with pytest.raises(ValueError):
        CatalystRecord(symbol="600000.SH", catalyst_type="NEWS", strength=1.5, source="t")


def test_config_pool_target_invalid() -> None:
    with pytest.raises(ValueError):
        WarPoolConfig(pool_target=0)


def test_config_weights_invalid() -> None:
    with pytest.raises(ValueError):
        WarPoolConfig(w_role=-0.1)


# ── 交集纪律 ──


def test_intersection_only_catalyst_leaders() -> None:
    sectors = [("880001.SH", "半导体", 70.0), ("880002.SH", "医药", 60.0)]
    groups = {"880001.SH": _group("880001.SH", "600001.SH"), "880002.SH": _group("880002.SH", "600002.SH")}
    catalysts = [_cat("600001.SH")]  # 600002 无催化剂
    result = select_war_pool(sectors, groups, catalysts, trade_date=TRADE_DATE)
    assert [e.symbol for e in result.entries] == ["600001.SH"]
    assert result.entries[0].role == "leader"
    assert result.no_pool_flag is False


def test_catalyst_stock_outside_mainline_excluded() -> None:
    sectors = [("880001.SH", "半导体", 70.0)]
    groups = {"880001.SH": _group("880001.SH", "600001.SH")}
    catalysts = [_cat("600099.SH")]  # 催化剂股不在主线板块
    result = select_war_pool(sectors, groups, catalysts, trade_date=TRADE_DATE)
    assert result.entries == []
    assert result.no_pool_flag is True


def test_empty_catalysts_no_pool_annotation() -> None:
    sectors = [("880001.SH", "半导体", 70.0)]
    groups = {"880001.SH": _group("880001.SH", "600001.SH")}
    result = select_war_pool(sectors, groups, [], trade_date=TRADE_DATE)
    assert result.no_pool_flag is True
    assert any("催化剂" in a for a in result.annotations)


def test_empty_sectors_no_pool() -> None:
    result = select_war_pool([], {}, [_cat("600001.SH")], trade_date=TRADE_DATE)
    assert result.no_pool_flag is True


# ── 排序与规模 ──


def test_ranking_and_truncation_to_pool_target() -> None:
    sectors = [("880001.SH", "半导体", 90.0)]
    groups = {
        "880001.SH": SectorRoleGroup(
            sector_code="880001.SH",
            leader=_entry("600001.SH", "880001.SH", score=95.0),
            backbones=[
                _entry("600002.SH", "880001.SH", role="backbone", score=80.0, consec=0),
                _entry("600003.SH", "880001.SH", role="backbone", score=70.0, consec=0),
                _entry("600004.SH", "880001.SH", role="backbone", score=60.0, consec=0),
            ],
        )
    }
    catalysts = [_cat(s) for s in ("600001.SH", "600002.SH", "600003.SH", "600004.SH")]
    cfg = WarPoolConfig(pool_target=3, include_backbones=True)
    result = select_war_pool(sectors, groups, catalysts, config=cfg, trade_date=TRADE_DATE)
    assert len(result.entries) == 3  # pool_target 截断
    scores = [e.pool_score for e in result.entries]
    assert scores == sorted(scores, reverse=True)
    assert result.entries[0].symbol == "600001.SH"  # 龙头角色分最高


def test_below_pool_min_note() -> None:
    sectors = [("880001.SH", "半导体", 70.0)]
    groups = {"880001.SH": _group("880001.SH", "600001.SH")}
    result = select_war_pool(sectors, groups, [_cat("600001.SH")], trade_date=TRADE_DATE)
    assert len(result.entries) == 1
    assert any("不足" in n for n in result.notes)


def test_min_catalyst_strength_filter() -> None:
    sectors = [("880001.SH", "半导体", 70.0)]
    groups = {"880001.SH": _group("880001.SH", "600001.SH")}
    cfg = WarPoolConfig(min_catalyst_strength=0.5)
    weak = select_war_pool(sectors, groups, [_cat("600001.SH", strength=0.3)], config=cfg, trade_date=TRADE_DATE)
    assert weak.no_pool_flag is True
    strong = select_war_pool(sectors, groups, [_cat("600001.SH", strength=0.9)], config=cfg, trade_date=TRADE_DATE)
    assert len(strong.entries) == 1


def test_mainline_pct_none_neutral_50() -> None:
    # 主线概率缺维（None）→ 中性 50 参与合成（不拉低不出伪分）
    sectors = [("880001.SH", "半导体", None)]
    groups = {"880001.SH": _group("880001.SH", "600001.SH", score=80.0)}
    result = select_war_pool(sectors, groups, [_cat("600001.SH", strength=1.0)], trade_date=TRADE_DATE)
    e = result.entries[0]
    assert e.mainline_pct is None
    # 0.5*80 + 0.3*50 + 0.2*100 = 40+15+20 = 75
    assert e.pool_score == pytest.approx(75.0)


def test_catalyst_strength_takes_max_when_multiple() -> None:
    sectors = [("880001.SH", "半导体", 50.0)]
    groups = {"880001.SH": _group("880001.SH", "600001.SH", score=100.0)}
    cats = [_cat("600001.SH", strength=0.4, ctype="NEWS"), _cat("600001.SH", strength=0.9, ctype="EARNINGS")]
    result = select_war_pool(sectors, groups, cats, trade_date=TRADE_DATE)
    assert result.entries[0].catalyst_strength == pytest.approx(0.9)
    assert len(result.entries[0].catalysts) == 2  # 双催化剂留痕


# ── 适配器 ──


def test_sectors_from_probability_adapter() -> None:
    result = _prob([("880001.SH", "半导体", 70.0), ("880002.SH", "医药", None)])
    sectors = sectors_from_probability(result)
    assert sectors == [("880001.SH", "半导体", 70.0), ("880002.SH", "医药", None)]


def test_sectors_from_candidates_adapter() -> None:
    cand = MainlineCandidatesResult(
        date=TRADE_DATE,
        candidates=[
            MainlineCandidate(
                sector_code="880001.SH",
                sector_name="半导体",
                score=4,
                q3_percentile=0.9,
                rrg_quadrant="LEADING",
                reasons=[],
            ),
        ],
    )
    sectors = sectors_from_candidates(cand)
    assert sectors == [("880001.SH", "半导体", None)]


# ── 装配层 ──


def test_generate_war_pool_full_injection() -> None:
    prob = _prob([("880001.SH", "半导体", 80.0)])
    board = _board(_group("880001.SH", "600001.SH"))
    result = generate_war_pool(
        trade_date=TRADE_DATE,
        probability_result=prob,
        leader_board=board,
        catalyst_provider=lambda d: [_cat("600001.SH")],
    )
    assert [e.symbol for e in result.entries] == ["600001.SH"]
    assert result.date == TRADE_DATE
    assert result.degraded is False


def test_generate_war_pool_degraded_propagation() -> None:
    prob = MainlineProbabilityResult(date=TRADE_DATE, degraded=True, notes=["候选榜降级"])
    board = _board(_group("880001.SH", "600001.SH"))
    result = generate_war_pool(
        trade_date=TRADE_DATE,
        probability_result=prob,
        leader_board=board,
        catalyst_provider=lambda d: [_cat("600001.SH")],
    )
    assert result.degraded is True
    assert result.entries == []


def test_generate_war_pool_default_no_catalyst_provider() -> None:
    prob = _prob([("880001.SH", "半导体", 80.0)])
    board = _board(_group("880001.SH", "600001.SH"))
    result = generate_war_pool(trade_date=TRADE_DATE, probability_result=prob, leader_board=board)
    assert result.no_pool_flag is True
    assert any("催化剂" in n or "catalyst" in n for n in result.notes)


def test_generate_war_pool_no_mainline_flag() -> None:
    prob = MainlineProbabilityResult(date=TRADE_DATE, no_mainline_flag=True)
    board = _board(_group("880001.SH", "600001.SH"))
    result = generate_war_pool(
        trade_date=TRADE_DATE,
        probability_result=prob,
        leader_board=board,
        catalyst_provider=lambda d: [_cat("600001.SH")],
    )
    assert result.no_pool_flag is True
    assert result.entries == []


# ── 契约 ──


def test_result_to_dict_json_serializable() -> None:
    sectors = [("880001.SH", "半导体", 70.0)]
    groups = {"880001.SH": _group("880001.SH", "600001.SH")}
    result = select_war_pool(sectors, groups, [_cat("600001.SH")], trade_date=TRADE_DATE)
    payload = result.to_dict()
    json.dumps(payload, ensure_ascii=False)
    assert payload["date"] == TRADE_DATE
    assert payload["entries"][0]["symbol"] == "600001.SH"
    assert isinstance(result, WarPoolResult)
