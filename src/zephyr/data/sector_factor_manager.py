# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.sector_factor_manager
# [DOMAIN] D_DATA
# [DEPENDENCIES] 无（纯计算；K线/资金流/成分映射全部注入式，复用 sector_* 采集器产出不重建）
# [CONSUMERS] （P1 接线：因子库写入方 + sector_report_builder）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 纯函数不触网不触库；基准缺失 fail-closed 返回空；窗口预热期不出记录；未映射板块留痕不炸； frozen dataclass 输出
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 基准为空→compute_rotation_factors 返回 []；窗口不足日期→跳过；映射 provider 返回 None→unmapped 留痕
# [TESTS] tests/zephyr/data/test_sector_factor_manager.py
# [A_module] module_id=MOD-L00-004 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
板块因子数据管理器（CAND-DAT-011 / B1-00598，86 板块因子数据管理器）。

深挖裁定=做(P1)：880板块K线下载/快照/排名/盘中聚合已建（sector_kline_downloader
/sector_snapshot_collector/sector_ranking_engine/sector_intraday_aggregator），
但成分映射挂接、板块轮动因子化输出与板块数据质量评分未收口。本模块收口四件事：

1. 覆盖完整性校验：``check_coverage`` 应到交易日 vs 实到 K线，缺失日期留痕。
2. 成分映射挂接：``attach_constituent_map`` 注入式 provider（37 概念因子映射
   引擎产出位的挂接点），未映射板块进 unmapped 留痕不炸。
3. 板块轮动因子：``compute_rotation_factors`` 相对强度（对基准 window 收益差）
   /横截面排名/排名变化/资金流入/复合分，输出因子库形态记录。
4. 板块数据质量评分：``score_data_quality`` 覆盖度 0.6 + 新鲜度 0.3 + 资金流齐备 0.1。

复用纪律：不直读 CH/不直采网络——K线行/资金流/成分映射全部注入，
采集面复用 sector_kline_downloader / sector_fund_flow_collector 现有产出。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: sector_factor_manager.py
# 层: 算法
# - id: A1
#   name_zh: ① SectorFactorManager
#   name_en: SectorFactorManager
#   intro: 板块因子数据管理器——完整性校验/成分挂接/轮动因子/质量评分。
#   desc: 板块因子数据管理器——完整性校验/成分挂接/轮动因子/质量评分。；公共方法（定义序）: check_coverage, attach_constituent_map, compute_rotation_factors…
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（7 定义）
#   name_en: public defs
#   intro: SectorFactorManager
#   downstream: （P1 接线：因子库写入方 + sector_report_builder）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Callable, Iterable, Mapping, Sequence

log = logging.getLogger(__name__)

__all__ = [
    "ConstituentMapResult",
    "CoverageInfo",
    "RotationFactorRecord",
    "SectorDailyBar",
    "SectorFactorManager",
    "SectorFundFlow",
    "SectorQualityScore",
]


# ---------------------------------------------------------------------------
# 输入/输出模型
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SectorDailyBar:
    """板块日线行（注入，对齐 kline_sector_880 口径）。"""

    sector_code: str
    trade_date: date
    close: Decimal


@dataclass(frozen=True)
class SectorFundFlow:
    """板块资金流快照（注入，对齐 sector_fund_flow_collector 净额口径，亿元）。"""

    sector_code: str
    net_amount: Decimal


@dataclass(frozen=True)
class CoverageInfo:
    """单板块覆盖完整性。"""

    sector_code: str
    expected: int
    actual: int
    ratio: float
    missing: tuple[date, ...]


@dataclass(frozen=True)
class ConstituentMapResult:
    """成分映射挂接结果。"""

    mapping: Mapping[str, tuple[str, ...]]
    unmapped: tuple[str, ...]


@dataclass(frozen=True)
class RotationFactorRecord:
    """板块轮动因子记录（因子库写入形态）。

    Attributes:
        relative_strength: 板块 window 收益 − 基准 window 收益
        rank: 当日横截面排名（1=最强）
        rank_change: 前 window 日 rank − 当日 rank（正=排名上升）
        fund_inflow: 当日净流入（亿元，无资金流数据=0.0）
        composite: 复合分 = 0.6×相对强度分位 + 0.4×资金流入分位
    """

    sector_code: str
    trade_date: date
    relative_strength: float
    rank: int
    rank_change: int
    fund_inflow: float
    composite: float


@dataclass(frozen=True)
class SectorQualityScore:
    """板块数据质量评分（0~1）。"""

    sector_code: str
    coverage_ratio: float
    freshness_lag_days: int
    fund_flow_present: bool
    score: float
    issues: tuple[str, ...]


# ---------------------------------------------------------------------------
# 管理器
# ---------------------------------------------------------------------------


class SectorFactorManager:
    """板块因子数据管理器——完整性校验/成分挂接/轮动因子/质量评分。"""

    # -- 1. 覆盖完整性 ----------------------------------------------------

    def check_coverage(
        self,
        bars: Iterable[SectorDailyBar],
        expected_dates: Sequence[date],
    ) -> list[CoverageInfo]:
        """板块日线覆盖完整性校验：应到日期 vs 实到日期，缺失留痕。"""
        expected_set = set(expected_dates)
        by_sector: dict[str, set[date]] = {}
        for b in bars:
            by_sector.setdefault(b.sector_code, set()).add(b.trade_date)
        infos: list[CoverageInfo] = []
        for code in sorted(by_sector):
            actual = by_sector[code] & expected_set
            missing = tuple(sorted(expected_set - actual))
            total = len(expected_set)
            infos.append(
                CoverageInfo(
                    sector_code=code,
                    expected=total,
                    actual=len(actual),
                    ratio=(len(actual) / total) if total else 0.0,
                    missing=missing,
                )
            )
        return infos

    # -- 2. 成分映射挂接（37 产出注入位） --------------------------------

    def attach_constituent_map(
        self,
        sector_codes: Iterable[str],
        mapping_provider: Callable[[str], Sequence[str] | None],
    ) -> ConstituentMapResult:
        """挂接板块成分映射；provider 返回 None/空 → unmapped 留痕不炸。"""
        mapping: dict[str, tuple[str, ...]] = {}
        unmapped: list[str] = []
        for code in sector_codes:
            members = mapping_provider(code)
            if members:
                mapping[code] = tuple(members)
            else:
                mapping[code] = ()
                unmapped.append(code)
        if unmapped:
            log.warning("成分映射缺失板块 %d 个: %s", len(unmapped), unmapped[:10])
        return ConstituentMapResult(mapping=mapping, unmapped=tuple(unmapped))

    # -- 3. 板块轮动因子 --------------------------------------------------

    def compute_rotation_factors(
        self,
        bars: Iterable[SectorDailyBar],
        benchmark_bars: Iterable[SectorDailyBar],
        fund_flows: Iterable[SectorFundFlow] | None = None,
        window: int = 5,
    ) -> list[RotationFactorRecord]:
        """计算板块轮动因子（相对强度/排名/排名变化/资金流入/复合分）。

        基准缺失 fail-closed 返回 []；窗口预热期（前 window 个交易日）不出记录。
        """
        bench = self._to_close_map(benchmark_bars)
        if not bench:
            log.error("基准行情为空，轮动因子计算 fail-closed")
            return []
        bench_dates = sorted(bench)
        close_by_sector = self._group_closes(bars)
        flow_map = {f.sector_code: float(f.net_amount) for f in (fund_flows or ())}

        # 每日横截面相对强度
        rel_by_date: dict[date, dict[str, float]] = {}
        for i in range(window, len(bench_dates)):
            day, prev = bench_dates[i], bench_dates[i - window]
            bench_ret = float(bench[day] / bench[prev]) - 1.0
            rels: dict[str, float] = {}
            for code, closes in close_by_sector.items():
                c_now, c_prev = closes.get(day), closes.get(prev)
                if c_now is None or c_prev is None or c_prev == 0:
                    continue
                rels[code] = (float(c_now / c_prev) - 1.0) - bench_ret
            if rels:
                rel_by_date[day] = rels

        # 横截面排名（rank 1=最强）与资金流入分位
        days = sorted(rel_by_date)
        rank_by_date = {d: self._rank_map(rel_by_date[d]) for d in days}
        records: list[RotationFactorRecord] = []
        for i, day in enumerate(days):
            rels = rel_by_date[day]
            n = len(rels)
            flow_pcts = self._percentile_map({c: flow_map.get(c, 0.0) for c in rels})
            prev_day = days[i - 1] if i >= 1 else None
            for code, rel in rels.items():
                rank = rank_by_date[day][code]
                prev_rank = rank_by_date[prev_day].get(code) if prev_day else None
                rank_change = (prev_rank - rank) if prev_rank is not None else 0
                rel_pct = 1.0 - (rank - 1) / max(n - 1, 1)
                composite = 0.6 * rel_pct + 0.4 * flow_pcts[code]
                records.append(
                    RotationFactorRecord(
                        sector_code=code,
                        trade_date=day,
                        relative_strength=rel,
                        rank=rank,
                        rank_change=rank_change,
                        fund_inflow=flow_map.get(code, 0.0),
                        composite=composite,
                    )
                )
        return records

    # -- 4. 数据质量评分 --------------------------------------------------

    def score_data_quality(
        self,
        coverage: CoverageInfo,
        latest_date: date,
        as_of: date,
        fund_flow_present: bool,
    ) -> SectorQualityScore:
        """板块数据质量评分 = 覆盖度×0.6 + 新鲜度×0.3 + 资金流齐备×0.1。"""
        issues: list[str] = []
        if coverage.ratio < 0.95:
            issues.append(f"覆盖度不足: {coverage.actual}/{coverage.expected}（缺失 {len(coverage.missing)} 日）")
        lag = (as_of - latest_date).days
        freshness = max(0.0, 1.0 - 0.2 * max(lag - 1, 0))
        if lag > 1:
            issues.append(f"新鲜度滞后: 最近数据 {latest_date}，距基准日 {lag} 天")
        if not fund_flow_present:
            issues.append("资金流数据缺失")
        score = 0.6 * coverage.ratio + 0.3 * freshness + 0.1 * (1.0 if fund_flow_present else 0.0)
        return SectorQualityScore(
            sector_code=coverage.sector_code,
            coverage_ratio=coverage.ratio,
            freshness_lag_days=lag,
            fund_flow_present=fund_flow_present,
            score=round(score, 6),
            issues=tuple(issues),
        )

    # -- 内部工具 ----------------------------------------------------------

    @staticmethod
    def _to_close_map(bars: Iterable[SectorDailyBar]) -> dict[date, Decimal]:
        out: dict[date, Decimal] = {}
        for b in bars:
            out[b.trade_date] = b.close
        return out

    @staticmethod
    def _group_closes(
        bars: Iterable[SectorDailyBar],
    ) -> dict[str, dict[date, Decimal]]:
        out: dict[str, dict[date, Decimal]] = {}
        for b in bars:
            out.setdefault(b.sector_code, {})[b.trade_date] = b.close
        return out

    @staticmethod
    def _rank_map(values: Mapping[str, float]) -> dict[str, int]:
        ordered = sorted(values.items(), key=lambda kv: kv[1], reverse=True)
        return {code: i + 1 for i, (code, _) in enumerate(ordered)}

    @staticmethod
    def _percentile_map(values: Mapping[str, float]) -> dict[str, float]:
        n = len(values)
        if n <= 1:
            return {c: 1.0 for c in values}
        ordered = sorted(values.items(), key=lambda kv: kv[1])
        return {code: i / (n - 1) for i, (code, _) in enumerate(ordered)}
