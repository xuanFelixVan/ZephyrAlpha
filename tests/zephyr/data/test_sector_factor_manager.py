# [BLUEPRINT] MOD-L00-004 | tests/zephyr/data/test_sector_factor_manager.py
# [MODULE] tests.zephyr.data.test_sector_factor_manager
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.sector_factor_manager
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS]
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L00-004 | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""SectorFactorManager 单元测试——板块因子数据管理器（CAND-DAT-011 / B1-00598）。

覆盖：
    1. 覆盖完整性校验：应到日期 vs 实到日期，缺失留痕
    2. 成分映射挂接：注入式 provider，未映射板块留痕不炸
    3. 板块轮动因子：相对强度/横截面排名/排名变化/资金流入/复合分
    4. 板块数据质量评分：覆盖度+新鲜度+资金流齐备加权
    5. 边界：空输入、窗口不足、基准缺失
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from zephyr.data.sector_factor_manager import (
    SectorDailyBar,
    SectorFactorManager,
    SectorFundFlow,
)

# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------

_DAYS = [date(2026, 8, 17) + timedelta(days=i) for i in range(7)]  # 7 个交易日


def _bars(code: str, closes: list[str], days: list[date] | None = None) -> list[SectorDailyBar]:
    ds = days or _DAYS
    return [
        SectorDailyBar(sector_code=code, trade_date=d, close=Decimal(c))
        for d, c in zip(ds, closes)
    ]


def _manager() -> SectorFactorManager:
    return SectorFactorManager()


# ---------------------------------------------------------------------------
# 1. 覆盖完整性校验
# ---------------------------------------------------------------------------


class TestCoverageCheck:
    def test_full_coverage(self):
        bars = _bars("880301", ["10", "11", "12", "13", "14", "15", "16"])
        infos = _manager().check_coverage(bars, _DAYS)
        assert len(infos) == 1
        assert infos[0].ratio == 1.0
        assert infos[0].missing == ()

    def test_missing_days_traced(self):
        bars = _bars("880301", ["10", "11", "12"], days=[_DAYS[0], _DAYS[2], _DAYS[4]])
        infos = _manager().check_coverage(bars, _DAYS)
        assert infos[0].actual == 3
        assert infos[0].expected == 7
        assert _DAYS[1] in infos[0].missing
        assert abs(infos[0].ratio - 3 / 7) < 1e-9

    def test_empty_bars(self):
        assert _manager().check_coverage([], _DAYS) == []


# ---------------------------------------------------------------------------
# 2. 成分映射挂接
# ---------------------------------------------------------------------------


class TestConstituentMapping:
    def test_mapping_attached(self):
        provider = {"880301": ["600000.SH", "600001.SH"], "880302": ["000001.SZ"]}
        result = _manager().attach_constituent_map(
            ["880301", "880302"], provider.get
        )
        assert result.mapping["880301"] == ("600000.SH", "600001.SH")
        assert result.unmapped == ()

    def test_unmapped_traced_not_raised(self):
        result = _manager().attach_constituent_map(
            ["880301", "880999"],
            lambda c: ["600000.SH"] if c == "880301" else None,
        )
        assert result.mapping["880301"] == ("600000.SH",)
        assert result.mapping["880999"] == ()
        assert result.unmapped == ("880999",)


# ---------------------------------------------------------------------------
# 3. 板块轮动因子
# ---------------------------------------------------------------------------


class TestRotationFactors:
    def _sector_set(self):
        strong = _bars("880301", ["10", "11", "12", "13", "14", "15", "16"])  # 持续走强
        weak = _bars("880302", ["16", "15", "14", "13", "12", "11", "10"])   # 持续走弱
        bench = _bars("880001", ["10", "10", "10", "10", "10", "10", "10"])  # 基准横盘
        return strong + weak, bench

    def test_relative_strength_vs_benchmark(self):
        sectors, bench = self._sector_set()
        recs = _manager().compute_rotation_factors(sectors, bench, window=2)
        last = _DAYS[-1]
        r301 = next(r for r in recs if r.sector_code == "880301" and r.trade_date == last)
        r302 = next(r for r in recs if r.sector_code == "880302" and r.trade_date == last)
        # 强板块 2 日收益 (16/14-1)≈0.1429，基准 0
        assert r301.relative_strength > 0.14
        assert r302.relative_strength < -0.14

    def test_cross_section_rank_and_change(self):
        sectors, bench = self._sector_set()
        recs = _manager().compute_rotation_factors(sectors, bench, window=2)
        last = _DAYS[-1]
        r301 = next(r for r in recs if r.sector_code == "880301" and r.trade_date == last)
        r302 = next(r for r in recs if r.sector_code == "880302" and r.trade_date == last)
        assert r301.rank == 1
        assert r302.rank == 2
        # 两板块各自趋势稳定 → 排名无变化
        assert r301.rank_change == 0

    def test_rank_change_positive_when_climbing(self):
        # 前段弱后段强：排名从第2升到第1
        climber = _bars("880303", ["10", "10", "10", "10", "10", "10", "20"])
        laggard = _bars("880304", ["10", "11", "12", "13", "14", "15", "15.1"])
        bench = _bars("880001", ["10"] * 7)
        recs = _manager().compute_rotation_factors(climber + laggard, bench, window=2)
        last = _DAYS[-1]
        r303 = next(r for r in recs if r.sector_code == "880303" and r.trade_date == last)
        assert r303.rank == 1
        assert r303.rank_change > 0

    def test_fund_inflow_attached(self):
        sectors, bench = self._sector_set()
        flows = [SectorFundFlow(sector_code="880301", net_amount=Decimal("5.5"))]
        recs = _manager().compute_rotation_factors(sectors, bench, fund_flows=flows, window=2)
        last = _DAYS[-1]
        r301 = next(r for r in recs if r.sector_code == "880301" and r.trade_date == last)
        assert r301.fund_inflow == 5.5
        r302 = next(r for r in recs if r.sector_code == "880302" and r.trade_date == last)
        assert r302.fund_inflow == 0.0

    def test_window_warmup_skipped(self):
        sectors, bench = self._sector_set()
        recs = _manager().compute_rotation_factors(sectors, bench, window=2)
        # 前 2 日窗口不足，不出因子记录
        assert all(r.trade_date >= _DAYS[2] for r in recs)

    def test_benchmark_missing_fail_closed(self):
        sectors, _ = self._sector_set()
        recs = _manager().compute_rotation_factors(sectors, [], window=2)
        assert recs == []


# ---------------------------------------------------------------------------
# 4. 数据质量评分
# ---------------------------------------------------------------------------


class TestQualityScore:
    def test_perfect_score(self):
        bars = _bars("880301", ["10"] * 7)
        infos = _manager().check_coverage(bars, _DAYS)
        score = _manager().score_data_quality(
            infos[0], latest_date=_DAYS[-1], as_of=_DAYS[-1], fund_flow_present=True
        )
        assert score.score == 1.0
        assert score.issues == ()

    def test_stale_data_penalized(self):
        bars = _bars("880301", ["10"] * 7)
        infos = _manager().check_coverage(bars, _DAYS)
        score = _manager().score_data_quality(
            infos[0],
            latest_date=_DAYS[-1],
            as_of=_DAYS[-1] + timedelta(days=5),
            fund_flow_present=True,
        )
        assert score.score < 1.0
        assert any("新鲜度" in i for i in score.issues)

    def test_missing_fund_flow_penalized(self):
        bars = _bars("880301", ["10"] * 7)
        infos = _manager().check_coverage(bars, _DAYS)
        score = _manager().score_data_quality(
            infos[0], latest_date=_DAYS[-1], as_of=_DAYS[-1], fund_flow_present=False
        )
        assert score.score < 1.0
        assert any("资金流" in i for i in score.issues)

    def test_low_coverage_penalized(self):
        bars = _bars("880301", ["10"], days=[_DAYS[0]])
        infos = _manager().check_coverage(bars, _DAYS)
        score = _manager().score_data_quality(
            infos[0], latest_date=_DAYS[0], as_of=_DAYS[-1], fund_flow_present=True
        )
        assert score.score <= 0.5
        assert any("覆盖" in i for i in score.issues)
