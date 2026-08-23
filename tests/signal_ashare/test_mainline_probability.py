# [BLUEPRINT] MOD-SIG-064 | 待统筹登记（blueprint 未建，真源=缺口总账 GAP-F-12 + 45号作战手册 §5 数据契约 MOD-SIG-061/062 消费层）
# [MODULE] tests.signal_ashare.test_mainline_probability
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.mainline_probability
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] testing
# [INVARIANTS] 合成数据不触库不触网；pytest filterwarnings=error 兼容
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=主线概率评分逻辑缺陷
# [TESTS] 本文件
# [A_module] module_id=MOD-SIG-064_test | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-SIG-064 主线概率综合评分 单元测试（GAP-F-12，合成数据不触库）。

覆盖：四因子子分（RRG 象限/接力阶段/资金持续性/梯队完整度）映射、静态权重合成与
缺维重归一、动态权重接口位（weight_overrides）、无主线混沌空榜、主入口降级链
（客户端不可用/候选降级/资金腿异常独立降级）、PIT 与 JSON 可序列化。
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import date, timedelta

import pytest

from zephyr.signal_ashare.mainline_candidates import (
    MainlineCandidate,
    MainlineCandidatesResult,
)
from zephyr.signal_ashare.mainline_probability import (
    MainlineProbabilityConfig,
    SectorFactorInput,
    compute_mainline_probability,
    score_echelon_completeness,
    score_fund_persistence,
    score_relay_stage,
    score_rrg_quadrant,
    score_sector_mainline,
)
from zephyr.signal_ashare.sector_leader import (
    ROLE_BACKBONE,
    ROLE_FOLLOWER,
    ROLE_LEADER,
    SectorLeaderBoard,
    SectorRoleGroup,
    StockRoleEntry,
)

D0 = date(2026, 8, 3)
TD = date(2026, 8, 21)


def _days(n: int) -> list[date]:
    return [D0 + timedelta(days=i) for i in range(n)]


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


def _group(
    sector: str,
    consec: int = 0,
    n_backbone: int = 0,
    n_follower: int = 0,
) -> SectorRoleGroup:
    leader = _entry("600000.SH", sector, ROLE_LEADER, consec) if consec >= 1 else None
    return SectorRoleGroup(
        sector_code=sector,
        leader=leader,
        backbones=[_entry(f"60001{i}.SH", sector, ROLE_BACKBONE) for i in range(n_backbone)],
        followers=[_entry(f"60002{i}.SH", sector, ROLE_FOLLOWER) for i in range(n_follower)],
        n_neutral_total=0,
        annotation=None if leader else "无龙头",
    )


def _candidates(cands: list[MainlineCandidate], **kw) -> MainlineCandidatesResult:
    return MainlineCandidatesResult(
        date=TD.isoformat(),
        rotation_state=kw.get("rotation_state", "HEALTHY_MAINLINE"),
        no_mainline_flag=kw.get("no_mainline_flag", False),
        candidates=cands,
        degraded=kw.get("degraded", False),
        notes=kw.get("notes", []),
        annotations=kw.get("annotations", []),
    )


def _cand(code: str, quadrant: str | None = "LEADING", streak: int = 0) -> MainlineCandidate:
    return MainlineCandidate(
        sector_code=code,
        sector_name=f"板块{code}",
        score=3,
        reasons=["合成候选"],
        lead_streak=streak,
        q3_percentile=0.9,
        rrg_quadrant=quadrant,
    )


# ---------- 因子子分（纯函数） ----------


class TestFactorSubScores:
    def test_rrg_quadrant_mapping(self):
        assert score_rrg_quadrant("LEADING") == pytest.approx(1.0)
        assert score_rrg_quadrant("IMPROVING") == pytest.approx(0.7)
        assert score_rrg_quadrant("WEAKENING") == pytest.approx(0.3)
        assert score_rrg_quadrant("LAGGING") == pytest.approx(0.1)
        assert score_rrg_quadrant(None) is None
        assert score_rrg_quadrant("UNKNOWN_Q") is None

    def test_relay_stage_tiers(self):
        # 无龙头：有中军 0.2，无中军 0.1
        assert score_relay_stage(0, has_backbone=True) == pytest.approx(0.2)
        assert score_relay_stage(0, has_backbone=False) == pytest.approx(0.1)
        # 连板梯队：首板 0.4 / 2板 0.6 / 3板 0.75 / ≥4板 0.9
        assert score_relay_stage(1, has_backbone=True) == pytest.approx(0.4)
        assert score_relay_stage(2, has_backbone=True) == pytest.approx(0.6)
        assert score_relay_stage(3, has_backbone=True) == pytest.approx(0.75)
        assert score_relay_stage(5, has_backbone=True) == pytest.approx(0.9)

    def test_relay_stage_market_risk_discount(self):
        # 派发/高潮期接力分打折
        base = score_relay_stage(3, has_backbone=True)
        discounted = score_relay_stage(3, has_backbone=True, rotation_state="DISTRIBUTION_RISK")
        assert discounted == pytest.approx(base * 0.6)
        climax = score_relay_stage(3, has_backbone=True, rotation_state="CONSENSUS_CLIMAX")
        assert climax == pytest.approx(base * 0.6)
        # 健康主线不打折
        healthy = score_relay_stage(3, has_backbone=True, rotation_state="HEALTHY_MAINLINE")
        assert healthy == pytest.approx(base)

    def test_fund_persistence(self):
        # 10 日全净流入 + 连续 10 日 → 满分
        assert score_fund_persistence([1.0] * 10) == pytest.approx(1.0)
        # 全流出 → 0
        assert score_fund_persistence([-1.0] * 10) == pytest.approx(0.0)
        # 4 正 6 负、尾段连正 3 日：0.6×0.4 + 0.4×0.3 = 0.36
        series = [-1.0] * 5 + [1.0, -1.0, 1.0, 1.0, 1.0]
        assert score_fund_persistence(series) == pytest.approx(0.6 * 0.4 + 0.4 * 0.3)

    def test_fund_persistence_insufficient(self):
        cfg = MainlineProbabilityConfig(fund_min_periods=5)
        assert score_fund_persistence([1.0, 2.0, 3.0], config=cfg) is None
        assert score_fund_persistence([], config=cfg) is None
        assert score_fund_persistence(None, config=cfg) is None

    def test_echelon_completeness(self):
        # 龙头+中军+3跟风 = 1.0
        assert score_echelon_completeness(True, 1, 3) == pytest.approx(1.0)
        # 仅龙头 = 0.4
        assert score_echelon_completeness(True, 0, 0) == pytest.approx(0.4)
        # 龙头+中军+1跟风 = 0.4+0.3+0.1 = 0.8
        assert score_echelon_completeness(True, 2, 1) == pytest.approx(0.8)
        # 空梯队 = 0
        assert score_echelon_completeness(False, 0, 0) == pytest.approx(0.0)


# ---------- 合成核（纯函数） ----------


class TestScoreSectorMainline:
    def test_full_weights_static(self):
        factors = SectorFactorInput(
            sector_code="881319.SH",
            sector_name="半导体",
            rrg_quadrant="LEADING",  # 1.0
            leader_consec=3,  # 0.75
            has_backbone=True,
            n_backbones=1,
            n_followers=3,  # echelon 1.0
            fund_inflow_series=[1.0] * 10,  # 1.0
            rotation_state="HEALTHY_MAINLINE",
        )
        item = score_sector_mainline(factors)
        # 0.30×1.0 + 0.25×0.75 + 0.20×1.0 + 0.25×1.0 = 0.9375 → 93.8
        assert item.probability_pct == pytest.approx(93.8, abs=0.05)
        assert item.rrg_score == pytest.approx(1.0)
        assert item.relay_score == pytest.approx(0.75)
        assert item.fund_score == pytest.approx(1.0)
        assert item.echelon_score == pytest.approx(1.0)
        assert item.weight_mode == "static"
        assert item.reasons  # 理由链非空

    def test_missing_factor_renormalize(self):
        """RRG 缺维（数据积累期）→ 按可用三维权重重归一，不留 0 拉低。"""
        factors = SectorFactorInput(
            sector_code="881319.SH",
            sector_name="半导体",
            rrg_quadrant=None,  # 缺维
            leader_consec=2,  # relay 0.6
            has_backbone=True,
            n_backbones=1,
            n_followers=0,  # echelon 0.7
            fund_inflow_series=[1.0] * 6 + [-1.0] * 4,  # 0.6×0.6+0.4×0=0.36
            rotation_state=None,
        )
        item = score_sector_mainline(factors)
        assert item.rrg_score is None
        expected = (0.25 * 0.6 + 0.20 * 0.36 + 0.25 * 0.7) / (0.25 + 0.20 + 0.25) * 100
        assert item.probability_pct == pytest.approx(expected, abs=0.05)

    def test_all_factors_missing_gives_none(self):
        factors = SectorFactorInput(
            sector_code="880999.SH",
            sector_name="",
            rrg_quadrant=None,
            leader_consec=None,  # 梯队板缺 → relay/echelon 缺
            has_backbone=False,
            n_backbones=0,
            n_followers=0,
            fund_inflow_series=None,
            rotation_state=None,
            leader_board_missing=True,
        )
        item = score_sector_mainline(factors)
        assert item.probability_pct is None
        assert any("无可评因子" in n for n in item.notes)

    def test_weight_overrides_dynamic_hook(self):
        """动态化接口位：weight_overrides 覆盖静态权重并留痕 weight_mode。"""
        factors = SectorFactorInput(
            sector_code="881319.SH",
            sector_name="半导体",
            rrg_quadrant="LEADING",
            leader_consec=2,
            has_backbone=True,
            n_backbones=1,
            n_followers=3,
            fund_inflow_series=[1.0] * 10,
            rotation_state="HEALTHY_MAINLINE",
        )
        cfg = MainlineProbabilityConfig(weight_overrides={"rrg": 0.0, "fund": 1.0})
        item = score_sector_mainline(factors, config=cfg)
        assert item.weight_mode == "override"
        # 仅 fund=1.0 与 rrg=0.0 参与：覆盖权重键外的因子按 0 处理
        assert item.probability_pct == pytest.approx(100.0)

    def test_frozen_dataclass_json_serializable(self):
        factors = SectorFactorInput(
            sector_code="881319.SH",
            sector_name="半导体",
            rrg_quadrant="LEADING",
            leader_consec=3,
            has_backbone=True,
            n_backbones=1,
            n_followers=3,
            fund_inflow_series=[1.0] * 10,
            rotation_state="HEALTHY_MAINLINE",
        )
        item = score_sector_mainline(factors)
        json.dumps(asdict(item), ensure_ascii=False)


# ---------- 主入口（合成 ch_client 不触库） ----------


class _FakeCH:
    """鸭子类型 ch_client：按 SQL 子串路由（money_flow / sector_constituent）。"""

    def __init__(self, mf_rows=None, constituent_rows=None, exc_on: str | None = None):
        self._mf = mf_rows or []
        self._constituent = constituent_rows or []
        self._exc_on = exc_on

    def execute(self, sql, params=None):
        if self._exc_on and self._exc_on in sql:
            raise RuntimeError(f"合成故障: {self._exc_on}")
        if "money_flow" in sql:
            return list(self._mf)
        if "sector_constituent" in sql:
            return list(self._constituent)
        return []


def _mf_rows(sector_stocks: dict[str, list[str]], nets: dict[str, list[float]], n: int = 12) -> list[tuple]:
    """合成 money_flow 行：nets[sector]=该板块成分股共用的逐日净流入序列。"""
    rows: list[tuple] = []
    for sector, series in nets.items():
        for stock in sector_stocks[sector]:
            for i, d in enumerate(_days(n)):
                rows.append((d, stock, series[i]))
    return rows


class TestComputeMainlineProbability:
    def _run(self, **over):
        cands = over.get("candidates") or _candidates([_cand("881319.SH"), _cand("881338.SH", "IMPROVING")])
        board = over.get("leader_board") or SectorLeaderBoard(
            trade_date=TD.isoformat(),
            sectors=[_group("881319.SH", consec=3, n_backbone=1, n_follower=3)],
            n_sectors=1,
            n_stocks=5,
        )
        stocks = {"881319.SH": ["600000.SH"], "881338.SH": ["600001.SH"]}
        mf = over.get("mf_rows") or _mf_rows(stocks, {"881319.SH": [1.0] * 12, "881338.SH": [-1.0] * 12})
        constituent = [("881319.SH", "600000.SH"), ("881338.SH", "600001.SH")]
        client = over.get("ch_client") or _FakeCH(mf_rows=mf, constituent_rows=constituent)
        return compute_mainline_probability(
            trade_date=TD,
            ch_client=client,
            candidates_result=cands,
            leader_board=board,
        )

    def test_happy_path_ranking(self):
        result = self._run()
        assert not result.degraded
        assert result.date == TD.isoformat()
        assert len(result.items) == 2
        top = result.items[0]
        assert top.sector_code == "881319.SH"  # 全因子强 → 居首
        assert top.probability_pct is not None and top.probability_pct > 80
        weak = result.items[1]
        assert weak.sector_code == "881338.SH"  # 资金全流出+无梯队 → 靠后
        assert weak.probability_pct is not None and weak.probability_pct < top.probability_pct
        json.dumps(asdict(result), ensure_ascii=False)

    def test_no_mainline_empty(self):
        result = self._run(
            candidates=_candidates([], no_mainline_flag=True, annotations=["无主线混沌"]),
        )
        assert result.items == []
        assert result.no_mainline_flag
        assert any("无主线" in a for a in result.annotations)

    def test_candidates_degraded_propagates(self):
        result = self._run(candidates=_candidates([], degraded=True, notes=["候选降级"]))
        assert result.degraded
        assert result.items == []

    def test_fund_leg_failure_degrades_independently(self):
        """money_flow 查询异常 → 资金维缺位重归一，整体不炸。"""
        cands = _candidates([_cand("881319.SH")])
        board = SectorLeaderBoard(
            trade_date=TD.isoformat(),
            sectors=[_group("881319.SH", consec=3, n_backbone=1, n_follower=3)],
            n_sectors=1,
            n_stocks=5,
        )
        client = _FakeCH(
            constituent_rows=[("881319.SH", "600000.SH")],
            exc_on="money_flow",
        )
        result = compute_mainline_probability(
            trade_date=TD,
            ch_client=client,
            candidates_result=cands,
            leader_board=board,
        )
        assert not result.degraded
        assert result.items[0].fund_score is None
        assert any("money_flow" in n for n in result.notes)

    def test_leader_board_missing_degrades_relay_echelon(self):
        """梯队榜降级 → relay/echelon 缺位，RRG+资金两维重归一。"""
        cands = _candidates([_cand("881319.SH", "LEADING")])
        board = SectorLeaderBoard(trade_date=TD.isoformat(), degraded=True, notes=["stk_limit 缺"])
        stocks = {"881319.SH": ["600000.SH"]}
        mf = _mf_rows(stocks, {"881319.SH": [1.0] * 12})
        client = _FakeCH(mf_rows=mf, constituent_rows=[("881319.SH", "600000.SH")])
        result = compute_mainline_probability(
            trade_date=TD,
            ch_client=client,
            candidates_result=cands,
            leader_board=board,
        )
        item = result.items[0]
        assert item.relay_score is None
        assert item.echelon_score is None
        # RRG 1.0 ×0.30 + fund 1.0 ×0.20 重归一 → 100
        assert item.probability_pct == pytest.approx(100.0)

    def test_no_client_degraded(self, monkeypatch):
        """ch_client 未注入且默认客户端不可用 → degraded 不炸。"""
        from zephyr.signal_ashare import mainline_probability as mod

        monkeypatch.setattr(mod, "_default_client", lambda: None)
        result = compute_mainline_probability(trade_date=TD, ch_client=None)
        assert result.degraded
        assert result.items == []

    def test_trade_date_format_fail_closed(self):
        with pytest.raises(ValueError):
            compute_mainline_probability(trade_date="2026/08/21", ch_client=_FakeCH())
