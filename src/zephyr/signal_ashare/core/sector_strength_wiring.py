# [BLUEPRINT] MOD-SIG-144 | docs/03_modules/_domain_signal/sector_strength_wiring/blueprint.md
# [MODULE] zephyr.signal_ashare.core.sector_strength_wiring
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.core.sector_strength_aggregator（MOD-SIG-142）; zephyr.signal_ashare.core.sector_ecology_judge（MOD-SIG-143）; 输入=sector_report_builder（MOD-L00-009）日频报告 JSON
# [CONSUMERS] TDM-E-L2-01（板块强度综合生产接线）；TDM-E-L2-04（板块级市场状态生产接线）；IDX-02 板块页（候选消费方）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 纯适配零 IO（接线 MOD-SIG-142/143 两核的-producer 适配层，本体不重复聚合/判定算法）（报告 dict 由调用方注入，读盘归 sector_report_builder）; 四维跨截面百分位排名归一 0-100（rank-based 方案=Quantpedia/研究复核裁定，抗离群）; 缺任一维度的板块剔除并记 note（保守不入池）; 集中度=Top2 主力净流入/全池主力净流入（0-1）; 高潮分代理=全市场涨停比分档映射（极强95/强70/中40/弱15，sector_breadth 既有分档口径，proposed）; lead_streak 缺失→ecology=None 不判定; 同输入必同输出（frozen+纯函数）; 适配层阈值映射为 proposed
# [MODIFY-GUARD] 地图节点 TDM-E-L2-01/TDM-E-L2-04
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] report 非法（非 dict/缺 top_sectors）→ SectorWiringInputError（fail-closed）
# [TESTS] tests/signal_ashare/test_sector_strength_wiring.py
# [TTL] permanent
"""SectorStrengthWiring — L2-01/L2-04 生产接线适配层。

数据链（接线后）：
  sector_report_builder（MOD-L00-009，日频盘后）
    → 本件：四维（结构强度/动量活跃/多周期动量/资金流）跨截面排名归一
      → aggregate_sector_strength（MOD-SIG-142）逐板块合成
      → select_candidate_pool（Top-15%）
    → judge_sector_ecology（MOD-SIG-143）三态生态
    → WiringResult（池+生态+notes）

四维源字段（报告 top_sectors 条目）：
  结构强度=strength_score（0-100 直用）、动量活跃=ranking_score（5 因子复合）、
  多周期动量=momentum_score（[0,1]×100）、资金流=main_net_inflow（亿元，排名归一）。
生态三输入：lead_streak（报告顶层透传）、集中度=Top2 主力净流入占比、
高潮分代理=全市场涨停比分档映射（极强95/强70/中40/弱15，sector_breadth 既有分档）。
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Final, Mapping

from zephyr.signal_ashare.core.sector_ecology_judge import (
    SectorEcology,
    SectorEcologyInputError,
    judge_sector_ecology,
)
from zephyr.signal_ashare.core.sector_strength_aggregator import (
    SectorStrength,
    SectorStrengthInputError,
    aggregate_sector_strength,
    select_candidate_pool,
)


class SectorWiringInputError(ValueError):
    """报告结构非法（缺 top_sectors/条目非 dict）——fail-closed。"""


#: 高潮分代理：全市场涨停比分档 → 0-100 分（口径=sector_breadth 既有分档，proposed）
BREADTH_CLIMAX_MAP: Final[dict[str, float]] = {
    "极强": 95.0,
    "强": 70.0,
    "中": 40.0,
    "弱": 15.0,
}


@dataclass(frozen=True)
class WiringResult:
    """接线输出（池+生态+诊断，frozen，JSON 可序列化经 to_dict）。"""

    trade_date: str | None
    pool: tuple[SectorStrength, ...]  # 全量板块（in_candidate_pool=True 为 Top-15%）
    ecology: SectorEcology | None  # 三态生态（lead_streak 或集中度缺失时 None）
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "trade_date": self.trade_date,
            "pool": [s.to_dict() for s in self.pool],
            "ecology": self.ecology.to_dict() if self.ecology is not None else None,
            "notes": list(self.notes),
        }


def _percentile_scores(values: list[float]) -> list[float]:
    """跨截面百分位排名归一到 0-100（平均秩处理平票；rank-based 方案）。"""
    n = len(values)
    if n == 0:
        return []
    order = sorted(range(n), key=lambda i: values[i])
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg_rank = (i + j) / 2.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg_rank
        i = j + 1
    denom = max(1, n - 1)
    return [r / denom * 100.0 for r in ranks]


def _collect_rows(entries: list[Any]) -> tuple[list[dict], list[str]]:
    """条目收集与维度补全（缺维度板块剔除+notes）。"""
    rows: list[dict] = []
    skipped: list[str] = []
    for e in entries:
        if not isinstance(e, dict):
            notes_flag = "skip-non-dict"
            continue
        name = e.get("sector_name") or e.get("sector_code")
        if not name:
            continue
        vals = {
            "structure": e.get("strength_score"),
            "activity": e.get("ranking_score"),
            "momentum": e.get("momentum_score"),
            "flow": e.get("main_net_inflow"),
        }
        missing = [k for k, v in vals.items() if v is None]
        if missing:
            skipped.append(f"{name}:{'+'.join(missing)}")
            continue
        momentum = float(vals["momentum"])
        rows.append(
            {
                "sector": str(name),
                "structure": float(vals["structure"]),
                "activity": float(vals["activity"]),
                "momentum": (momentum * 100.0) if momentum <= 1.0 else momentum,
                "flow": float(vals["flow"]),
            }
        )
    notes = [f"跳过非 dict 条目"] if False else []
    if skipped:
        notes.append(f"缺维度剔除 {len(skipped)} 板块: {', '.join(skipped[:5])}" + ("…" if len(skipped) > 5 else ""))
    return rows, notes


def _derive_ecology(
    report: Mapping[str, Any], rows: list[dict]
) -> SectorEcology | None:
    """生态三输入派生（lead_streak 透传 + 集中度 + 高潮分代理）。"""
    lead = report.get("lead_streak")
    flows = sorted(
        (float(r["flow"]) for r in rows if r["flow"] > 0),
        reverse=True,
    )
    total_flow = sum(flows)
    if not isinstance(lead, int) or total_flow <= 0 or len(flows) < 2:
        return None
    concentration = (flows[0] + flows[1]) / total_flow
    breadth_label = str(report.get("breadth_label") or "")
    climax = next(
        (v for k, v in BREADTH_CLIMAX_MAP.items() if k in breadth_label),
        40.0,
    )
    return judge_sector_ecology(
        lead_streak=lead,
        turnover_concentration=round(concentration, 4),
        climax_score=climax,
    )


def wire_from_report(
    report: Mapping[str, Any],
    trade_date: str | None = None,
) -> WiringResult:
    """生产接线主入口：报告 dict → 强度池 + 三态生态。

    Raises:
        SectorWiringInputError: report 结构非法或派生输入越界。
    """
    if not isinstance(report, Mapping):
        raise SectorWiringInputError("report 非映射（dict）")
    entries = report.get("top_sectors")
    if not isinstance(entries, list):
        raise SectorWiringInputError("report 缺 top_sectors 列表")

    rows, notes = _collect_rows(entries)
    pool: tuple[SectorStrength, ...] = ()
    if rows:
        norm = {
            dim: _percentile_scores([r[dim] for r in rows])
            for dim in ("structure", "activity", "momentum", "flow")
        }
        strengths = [
            aggregate_sector_strength(
                sector=r["sector"],
                structure_score=norm["structure"][i],
                momentum_activity=norm["activity"][i],
                multi_period_momentum=norm["momentum"][i],
                capital_flow=norm["flow"][i],
            )
            for i, r in enumerate(rows)
        ]
        pool = tuple(select_candidate_pool(strengths))
    else:
        notes.append("无有效板块行 → 空池")

    ecology = _derive_ecology(report, rows)
    if ecology is None:
        notes.append("lead_streak 缺失或主力净流入不足 → 生态不判定")

    return WiringResult(
        trade_date=str(report.get("trade_date")) if report.get("trade_date") else trade_date,
        pool=pool,
        ecology=ecology,
        notes=notes,
    )
