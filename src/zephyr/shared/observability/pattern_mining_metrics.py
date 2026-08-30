# [BLUEPRINT] MOD-INF-055 | docs/03_modules/MOD-INF-055/
# [MODULE] zephyr.shared.observability.pattern_mining_metrics
# [DOMAIN] D_SHARED
# [DEPENDENCIES] json, pathlib, collections, dataclasses
# [CONSUMERS] 仪表板 / 治理审计脚本
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 纯函数，无副作用；不修改源文件；只读 .jsonl 报告
# [MODIFY-GUARD] 修改需同步更新头部 + 调用方
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PatternMiningMetricsError(ZA-OBS-0001)
# [TESTS] tests/observability/test_pattern_mining_metrics.py
# [A_module] module_id=MOD-INF-055 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
pattern_mining_metrics.py —— 修复模式挖掘报告消费与汇总模块（P2-1 观测架子）

消费 ``.runtime/security_ops/pattern_mining_reports.jsonl``，产出：
  1. 日维度命中率汇总（按 ts 日期分组）
  2. 累计命中率汇总（全量统计）
  3. 建议类别分布统计（PROMOTE/REVIEW/ENRICH_DIAGNOSIS）

设计原则：
  - 纯函数：无副作用，输入 list[dict] → 输出 dict
  - 只读：不修改源文件，不写入任何文件
  - 零依赖：只用标准库（json/pathlib/collections/dataclasses）

数据格式（pattern_mining_reports.jsonl 每行）：
  {
    "report_id": "abc123",
    "ts": "2026-08-30T09:00:00+08:00",
    "total_records": 42,
    "skipped_records": 0,
    "diagnose": {
      "total_records": 42,
      "matched_records": 30,
      "hit_rate": 0.714,
      "by_fault_class": {"F001": 0.8, "F002": 0.6}
    },
    "suggestions": [
      {"kind": "promote_pattern", "cluster_key": "F001|auto_fix", "frequency": 5, "success_rate": 0.9}
    ]
  }

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: path 参数
#   fields: 参数 path，类型注解 Path | str
#   code: pattern_mining_metrics.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: reports 参数
#   fields: 参数 reports，类型注解 list[dict[str, Any]]
#   code: pattern_mining_metrics.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① load_reports_from_jsonl
#   name_en: load_reports_from_jsonl
#   intro: 从 JSONL 文件加载报告列表。
#   desc: 从 JSONL 文件加载报告列表。 Args: path: JSONL 文件路径（默认 .runtime/security_ops/pattern_mining_reports.…；源码 L186-L219
#   inputs: path
#   outputs: list[dict[str, Any]]
# - id: A2
#   name_zh: ② compute_daily_hit_rates
#   name_en: compute_daily_hit_rates
#   intro: 按日分组计算命中率。
#   desc: 按日分组计算命中率。 Args: reports: 报告字典列表（从 load_reports_from_jsonl 加载） Returns: DailyHitRate 列表，按…；源码 L222-L260
#   inputs: reports
#   outputs: list[DailyHitRate]
# - id: A3
#   name_zh: ③ compute_cumulative_stats
#   name_en: compute_cumulative_stats
#   intro: 计算累计命中率（全量统计）。
#   desc: 计算累计命中率（全量统计）。 Args: reports: 报告字典列表 Returns: CumulativeStats 实例；源码 L263-L300
#   inputs: reports
#   outputs: CumulativeStats
# - id: A4
#   name_zh: ④ compute_suggestion_kind_stats
#   name_en: compute_suggestion_kind_stats
#   intro: 计算建议类别分布。
#   desc: 计算建议类别分布。 Args: reports: 报告字典列表 Returns: SuggestionKindStats 实例；源码 L303-L332
#   inputs: reports
#   outputs: SuggestionKindStats
# - id: A5
#   name_zh: ⑤ summarize_reports
#   name_en: summarize_reports
#   intro: 汇总报告：日维度 + 累计 + 建议分布。
#   desc: 汇总报告：日维度 + 累计 + 建议分布。 Args: reports: 报告字典列表（可选，与 path 二选一） path: JSONL 文件路径（可选，与 reports…；源码 L335-L405
#   inputs: reports path
#   outputs: dict[str, Any]
#   （注：A5 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: list[dict[str, Any]]
#   name_en: list[dict[str, Any]]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 仪表板 / 治理审计脚本
# - id: O2
#   name_zh: list[DailyHitRate]
#   name_en: list[DailyHitRate]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 仪表板 / 治理审计脚本
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> O1
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

__all__: Final = [
    "DailyHitRate",
    "CumulativeStats",
    "SuggestionKindStats",
    "PatternMiningMetricsError",
    "compute_daily_hit_rates",
    "compute_cumulative_stats",
    "compute_suggestion_kind_stats",
    "load_reports_from_jsonl",
    "summarize_reports",
]

DEFAULT_REPORTS_PATH: Final[Path] = Path(".runtime/security_ops/pattern_mining_reports.jsonl")


class PatternMiningMetricsError(Exception):
    """ZA-OBS-0001: 修复模式挖掘指标计算错误（输入数据非法/文件不可读）。"""

    error_code = "ZA-OBS-0001"

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.details: dict[str, Any] = details or {}


@dataclass(frozen=True)
class DailyHitRate:
    """单日命中率统计。"""

    date: str
    total_records: int
    matched_records: int
    hit_rate: float
    skipped_records: int
    report_count: int


@dataclass(frozen=True)
class CumulativeStats:
    """累计命中率统计（全量）。"""

    total_reports: int
    total_records: int
    matched_records: int
    hit_rate: float
    skipped_records: int
    first_report_ts: str
    last_report_ts: str


@dataclass(frozen=True)
class SuggestionKindStats:
    """建议类别分布统计。"""

    promote_count: int
    review_count: int
    enrich_diagnosis_count: int
    total_suggestions: int


def load_reports_from_jsonl(path: Path | str) -> list[dict[str, Any]]:
    """从 JSONL 文件加载报告列表。

    Args:
        path: JSONL 文件路径（默认 .runtime/security_ops/pattern_mining_reports.jsonl）

    Returns:
        报告字典列表，每行一个 dict

    Raises:
        PatternMiningMetricsError: 文件不可读 / JSON 解析失败 / 非 dict 行
    """
    path = Path(path)
    if not path.exists():
        raise PatternMiningMetricsError("报告文件不存在", details={"path": str(path)})

    reports: list[dict[str, Any]] = []
    try:
        with open(path, encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    blob = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise PatternMiningMetricsError(f"JSON 解析失败 (行 {line_no}): {exc}") from exc
                if not isinstance(blob, dict):
                    raise PatternMiningMetricsError(f"行 {line_no} 不是 dict: {type(blob)}")
                reports.append(blob)
    except OSError as exc:
        raise PatternMiningMetricsError("文件不可读", details={"path": str(path), "os_error": str(exc)}) from exc

    return reports


def compute_daily_hit_rates(reports: list[dict[str, Any]]) -> list[DailyHitRate]:
    """按日分组计算命中率。

    Args:
        reports: 报告字典列表（从 load_reports_from_jsonl 加载）

    Returns:
        DailyHitRate 列表，按日期升序排列
    """
    # 按日期分组
    by_date: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for report in reports:
        ts = report.get("ts", "")
        if not ts:
            continue
        # 提取日期部分 (YYYY-MM-DD)
        date = ts[:10] if len(ts) >= 10 else ts
        by_date[date].append(report)

    result: list[DailyHitRate] = []
    for date in sorted(by_date.keys()):
        day_reports = by_date[date]
        total = sum(r.get("diagnose", {}).get("total_records", 0) for r in day_reports)
        matched = sum(r.get("diagnose", {}).get("matched_records", 0) for r in day_reports)
        skipped = sum(r.get("skipped_records", 0) for r in day_reports)
        hit_rate = matched / total if total else 0.0

        result.append(
            DailyHitRate(
                date=date,
                total_records=total,
                matched_records=matched,
                hit_rate=round(hit_rate, 4),
                skipped_records=skipped,
                report_count=len(day_reports),
            )
        )

    return result


def compute_cumulative_stats(reports: list[dict[str, Any]]) -> CumulativeStats:
    """计算累计命中率（全量统计）。

    Args:
        reports: 报告字典列表

    Returns:
        CumulativeStats 实例
    """
    if not reports:
        return CumulativeStats(
            total_reports=0,
            total_records=0,
            matched_records=0,
            hit_rate=0.0,
            skipped_records=0,
            first_report_ts="",
            last_report_ts="",
        )

    total = sum(r.get("diagnose", {}).get("total_records", 0) for r in reports)
    matched = sum(r.get("diagnose", {}).get("matched_records", 0) for r in reports)
    skipped = sum(r.get("skipped_records", 0) for r in reports)
    hit_rate = matched / total if total else 0.0

    # 提取首尾时间戳
    ts_list = [r.get("ts", "") for r in reports if r.get("ts")]
    ts_list.sort()

    return CumulativeStats(
        total_reports=len(reports),
        total_records=total,
        matched_records=matched,
        hit_rate=round(hit_rate, 4),
        skipped_records=skipped,
        first_report_ts=ts_list[0] if ts_list else "",
        last_report_ts=ts_list[-1] if ts_list else "",
    )


def compute_suggestion_kind_stats(reports: list[dict[str, Any]]) -> SuggestionKindStats:
    """计算建议类别分布。

    Args:
        reports: 报告字典列表

    Returns:
        SuggestionKindStats 实例
    """
    promote = 0
    review = 0
    enrich = 0

    for report in reports:
        suggestions = report.get("suggestions", [])
        for sug in suggestions:
            kind = sug.get("kind", "")
            if kind == "promote_pattern":
                promote += 1
            elif kind == "review_pattern":
                review += 1
            elif kind == "enrich_diagnosis":
                enrich += 1

    return SuggestionKindStats(
        promote_count=promote,
        review_count=review,
        enrich_diagnosis_count=enrich,
        total_suggestions=promote + review + enrich,
    )


def summarize_reports(
    reports: list[dict[str, Any]] | None = None,
    *,
    path: Path | str | None = None,
) -> dict[str, Any]:
    """汇总报告：日维度 + 累计 + 建议分布。

    Args:
        reports: 报告字典列表（可选，与 path 二选一）
        path: JSONL 文件路径（可选，与 reports 二选一；默认 .runtime/security_ops/pattern_mining_reports.jsonl）

    Returns:
        dict 包含:
            - daily: list[DailyHitRate] 按日分组
            - cumulative: CumulativeStats 累计统计
            - suggestion_kinds: SuggestionKindStats 建议分布
            - summary_text: str 人类可读摘要

    Raises:
        PatternMiningMetricsError: 输入非法（reports 和 path 都为空 / 都非空）
    """
    if reports is None and path is None:
        path = DEFAULT_REPORTS_PATH

    if reports is not None and path is not None:
        raise PatternMiningMetricsError("reports 和 path 二选一，不能同时提供")

    if reports is None:
        reports = load_reports_from_jsonl(path)

    daily = compute_daily_hit_rates(reports)
    cumulative = compute_cumulative_stats(reports)
    kinds = compute_suggestion_kind_stats(reports)

    summary_lines = [
        f"累计报告: {cumulative.total_reports} 份",
        f"累计记录: {cumulative.total_records} 条 (命中 {cumulative.matched_records}, 命中率 {cumulative.hit_rate:.1%})",
        f"跳过记录: {cumulative.skipped_records} 条",
        f"时间范围: {cumulative.first_report_ts} ~ {cumulative.last_report_ts}",
        f"建议分布: PROMOTE={kinds.promote_count} REVIEW={kinds.review_count} ENRICH={kinds.enrich_diagnosis_count}",
    ]

    return {
        "daily": [
            {
                "date": d.date,
                "total_records": d.total_records,
                "matched_records": d.matched_records,
                "hit_rate": d.hit_rate,
                "skipped_records": d.skipped_records,
                "report_count": d.report_count,
            }
            for d in daily
        ],
        "cumulative": {
            "total_reports": cumulative.total_reports,
            "total_records": cumulative.total_records,
            "matched_records": cumulative.matched_records,
            "hit_rate": cumulative.hit_rate,
            "skipped_records": cumulative.skipped_records,
            "first_report_ts": cumulative.first_report_ts,
            "last_report_ts": cumulative.last_report_ts,
        },
        "suggestion_kinds": {
            "promote_count": kinds.promote_count,
            "review_count": kinds.review_count,
            "enrich_diagnosis_count": kinds.enrich_diagnosis_count,
            "total_suggestions": kinds.total_suggestions,
        },
        "summary_text": "\n".join(summary_lines),
    }
