# [BLUEPRINT] MOD-PLAN-009 | 待统筹登记（45号 §4 W0 + 缺口总账 GAP-F-07②）
# [MODULE] zephyr.plan_engine.scenario_attribution_stats
# [DOMAIN] D_PLAN
# [DEPENDENCIES] zephyr.reporting.prediction_log_writer(query_predictions)
# [CONSUMERS] 作战室 W0 昨日预案验证（三维归因表）; W6 历史预案库; GAP-F-01 情景概率分布模型（分情景命中率=概率模型训练/验证样本）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 统计核心纯函数（不依赖 DB，可单测）; 只聚合不判定（hit 真值由回写方产出，44号 §12.1 M4-④ 裁定二）; 只读 prediction_log（经 query_predictions 公共 API，零裸 SQL）; 契约字段缺失/类型错的 outcome 行计 skipped_invalid 不混入样本; 输入校验 fail-closed
# [MODIFY-GUARD] blueprint.md
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError（module/window_days/records 非法 fail-closed）; query_predictions 的 sqlite3.Error 透传
# [TESTS] tests/plan_engine/test_scenario_attribution_stats.py
# [A_module] module_id=MOD-PLAN-009 | layer=module | stability=testing | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

ScenarioAttributionStats — 预案三维归因统计器 (MOD-PLAN-009)

45号作战手册 §4 W0 + 缺口总账 GAP-F-07② 落码：验证闭环三维归因——
"预测对≠执行对≠赚钱，三者分开统计"（45号 §2 第一性原理五则之五）。

三维口径（写清）：
    - 情景分支（scenario）：9 情景格子（SCENARIO_LIST 语义），回答"哪格预案准/不准"。
    - 维度（dimension）：prediction（预测命中）/ execution（执行一致）/ pnl（预案
      盈利）——本模块对取值保持口径无关（自由字符串），维度真值由各回写方产出
      （prediction 维已由 MOD-PLAN-008 回写；execution/pnl 维待执行链接入）。
    - 信号源（signal_source）：产出预测的信号家族标识（如
      "MOD-PLAN-005.scenario_planner"），回答"哪路信号源的预案可信"。

输出=三维边际桶（by_scenario/by_dimension/by_signal_source）+ 三维复合桶
（by_cell，"scenario|dimension|signal_source" 组合键），每桶 sample_size/
hit_count/hit_rate。W0 默认窗口近 20 日（45号 §4 W0"近 20 日校准度"口径）。

数据契约（消费 MOD-PLAN-008 outcome payload 字段）：prediction_log outcome 族
（prediction_type="outcome"）payload_json 须含 hit:bool + scenario:str +
dimension:str + signal_source:str 四键；缺/错类型 → skipped_invalid 计数，
不混入样本（数据质量观察量，与 MOD-RPT-029 invalid_outcome_count 同族口径）。

不做什么：不判定 hit（回写方职责）/不写库/不出调参建议（归 MOD-RPT-029
         校准触发器）/不做概率校准（归 MOD-PLAN-010 Brier）。

依据: 45_warroom_playbook §2 五则之五 + §4 W0；44号 §12.1 M4-④ 裁定二
SSoT: depgraph MOD-PLAN-009（待统筹登记）
Version: 0.1.0

# [ALGO_FLOW]
# 输入: prediction_log outcome 族行（window 过滤）/ 或直接注入 AttributionRecord 序列
# 特征: scenario / dimension / signal_source / hit 四元组
# 算法: 三维边际分桶 + 三维复合分桶 → 每桶命中计数与命中率
# 输出: AttributionReport（纯 frozen dataclass，JSON 可序列化）

"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Final, Iterable

from zephyr.reporting.prediction_log_writer import query_predictions

__all__: Final = [
    "DEFAULT_WINDOW_DAYS",
    "AttributionBucket",
    "AttributionRecord",
    "AttributionReport",
    "compute_attribution",
    "compute_scenario_attribution",
    "load_attribution_records",
]

# ── 口径常量 ──

DEFAULT_WINDOW_DAYS: Final = 20  # W0 归因默认窗口（45号 §4 W0"近 20 日"口径）
OUTCOME_PREDICTION_TYPE: Final = "outcome"  # outcome 族（prediction_log 单一账本，裁定一）
_STATS_QUERY_LIMIT: Final = 10000  # 窗口内单模块行数上限（骨架期远大于实际量级）

# outcome payload 契约字段（与 MOD-PLAN-008 回写契约对齐）
_KEY_HIT: Final = "hit"
_KEY_SCENARIO: Final = "scenario"
_KEY_DIMENSION: Final = "dimension"
_KEY_SIGNAL_SOURCE: Final = "signal_source"


# ── 数据契约 ──


@dataclass(frozen=True)
class AttributionRecord:
    """归因样本（四元组）：情景分支 × 维度 × 信号源 × 命中。"""

    scenario: str  # 情景分支（9 情景语义，自由字符串不门控）
    dimension: str  # 维度（prediction/execution/pnl ...）
    signal_source: str  # 信号源标识
    hit: bool  # 命中真值（回写方产出）


@dataclass(frozen=True)
class AttributionBucket:
    """单桶统计：键 + 样本量 + 命中数 + 命中率。"""

    key: str  # 桶键（边际桶=维度取值；复合桶="scenario|dimension|signal_source"）
    sample_size: int
    hit_count: int
    hit_rate: float  # hit_count/sample_size（桶存在即 sample_size≥1，恒非 None）


@dataclass(frozen=True)
class AttributionReport:
    """三维归因报告（统计器输出，纯数据不判定，JSON 可序列化）。"""

    module: str  # 统计对象模块标识（""=纯函数注入模式未指定）
    window_days: int
    window_start: str  # 闭区间起（YYYY-MM-DD；纯函数注入模式可为 ""）
    window_end: str  # 闭区间止
    sample_size: int  # 总样本量
    by_scenario: tuple[AttributionBucket, ...]  # 情景分支边际桶（键升序）
    by_dimension: tuple[AttributionBucket, ...]  # 维度边际桶（键升序）
    by_signal_source: tuple[AttributionBucket, ...]  # 信号源边际桶（键升序）
    by_cell: tuple[AttributionBucket, ...]  # 三维复合桶（键升序）
    skipped_invalid: int = 0  # 契约字段缺失/类型错被剔除的行数（数据质量观察量）

    def to_dict(self) -> dict[str, Any]:
        """JSON 可序列化字典（W0 前端/复盘页消费契约）。"""

        def _buckets(bs: tuple[AttributionBucket, ...]) -> list[dict[str, Any]]:
            return [
                {
                    "key": b.key,
                    "sample_size": b.sample_size,
                    "hit_count": b.hit_count,
                    "hit_rate": b.hit_rate,
                }
                for b in bs
            ]

        return {
            "module": self.module,
            "window_days": self.window_days,
            "window_start": self.window_start,
            "window_end": self.window_end,
            "sample_size": self.sample_size,
            "by_scenario": _buckets(self.by_scenario),
            "by_dimension": _buckets(self.by_dimension),
            "by_signal_source": _buckets(self.by_signal_source),
            "by_cell": _buckets(self.by_cell),
            "skipped_invalid": self.skipped_invalid,
        }


# ── 统计核心（纯函数，不依赖 DB）──


def _bucketize(pairs: Iterable[tuple[str, bool]]) -> tuple[AttributionBucket, ...]:
    """(key, hit) 序列 → 分桶统计（键升序，确定性输出）。"""
    counts: dict[str, list[int]] = {}
    for key, hit in pairs:
        bucket = counts.setdefault(key, [0, 0])
        bucket[0] += 1
        bucket[1] += 1 if hit else 0
    return tuple(
        AttributionBucket(
            key=k,
            sample_size=v[0],
            hit_count=v[1],
            hit_rate=v[1] / v[0],
        )
        for k, v in sorted(counts.items())
    )


def compute_attribution(
    records: Iterable[AttributionRecord],
    *,
    module: str = "",
    window_days: int = 0,
    window_start: str = "",
    window_end: str = "",
    skipped_invalid: int = 0,
) -> AttributionReport:
    """三维归因统计核心（纯函数）：records → 三维边际桶 + 三维复合桶。

    Args:
        records: 归因样本序列（AttributionRecord；其他类型 fail-closed）。
        module/window_days/window_start/window_end: 报告元信息（读库组合入口回填）。
        skipped_invalid: 读库阶段剔除的非法行数（组合入口回填）。

    Returns:
        AttributionReport（桶键升序，与输入顺序无关的确定性输出）。

    Raises:
        ValueError: 任一 record 非 AttributionRecord（fail-closed）。
    """
    recs = list(records)
    for r in recs:
        if not isinstance(r, AttributionRecord):
            raise ValueError(f"records 元素非法（须 AttributionRecord）: {type(r).__name__}")

    return AttributionReport(
        module=module,
        window_days=window_days,
        window_start=window_start,
        window_end=window_end,
        sample_size=len(recs),
        by_scenario=_bucketize((r.scenario, r.hit) for r in recs),
        by_dimension=_bucketize((r.dimension, r.hit) for r in recs),
        by_signal_source=_bucketize((r.signal_source, r.hit) for r in recs),
        by_cell=_bucketize((f"{r.scenario}|{r.dimension}|{r.signal_source}", r.hit) for r in recs),
        skipped_invalid=skipped_invalid,
    )


# ── 读库器（prediction_log outcome 族 → AttributionRecord）──


def _validate_module(module: object) -> str:
    """module 校验：非空字符串（fail-closed）。"""
    if not isinstance(module, str) or not module.strip():
        raise ValueError(f"module 非法（须非空字符串）: {module!r}")
    return module.strip()


def _validate_window_days(window_days: object) -> int:
    """window_days 校验：正整数（fail-closed）。"""
    if isinstance(window_days, bool) or not isinstance(window_days, int) or window_days < 1:
        raise ValueError(f"window_days 非法（须正整数）: {window_days!r}")
    return window_days


def load_attribution_records(
    module: str,
    window_days: int = DEFAULT_WINDOW_DAYS,
    db_path: str | Path | None = None,
    as_of: date | None = None,
) -> tuple[list[AttributionRecord], int]:
    """从 prediction_log 读 outcome 族行 → 归因样本（窗口过滤+契约校验）。

    口径：样本=窗口内 outcome 行且 payload 四契约字段（hit:bool/scenario:str/
    dimension:str/signal_source:str）齐全；缺/错 → skipped_invalid 计数不混入。
    本模块不做 prediction 行匹配校验（孤儿观察归 MOD-RPT-029 口径族）。

    Args:
        module: 统计对象模块标识（非空字符串，fail-closed）。
        window_days: 统计窗口天数（正整数；含 as_of 当日的自然日闭区间）。
        db_path: 库路径；None=DB_PATH SSoT（测试注入临时库）。
        as_of: 窗口基准日（None=date.today()；测试注入固定日期保确定性）。

    Returns:
        (records, skipped_invalid)。

    Raises:
        ValueError: module/window_days 非法（fail-closed）。
        sqlite3.Error: 库级异常透传。
    """
    v_module = _validate_module(module)
    v_window = _validate_window_days(window_days)
    end = as_of if as_of is not None else date.today()
    window_start = (end - timedelta(days=v_window - 1)).isoformat()
    window_end = end.isoformat()

    rows = query_predictions(
        module=v_module,
        prediction_type=OUTCOME_PREDICTION_TYPE,
        limit=_STATS_QUERY_LIMIT,
        db_path=db_path,
    )

    records: list[AttributionRecord] = []
    skipped = 0
    for row in rows:
        if not (window_start <= row["trade_date"] <= window_end):
            continue
        try:
            payload = json.loads(row["payload_json"])
        except (json.JSONDecodeError, TypeError):
            skipped += 1
            continue
        if not isinstance(payload, dict):
            skipped += 1
            continue
        hit = payload.get(_KEY_HIT)
        scenario = payload.get(_KEY_SCENARIO)
        dimension = payload.get(_KEY_DIMENSION)
        source = payload.get(_KEY_SIGNAL_SOURCE)
        if (
            not isinstance(hit, bool)
            or not isinstance(scenario, str)
            or not scenario.strip()
            or not isinstance(dimension, str)
            or not dimension.strip()
            or not isinstance(source, str)
            or not source.strip()
        ):
            skipped += 1
            continue
        records.append(
            AttributionRecord(
                scenario=scenario,
                dimension=dimension,
                signal_source=source,
                hit=hit,
            )
        )
    return records, skipped


def compute_scenario_attribution(
    module: str,
    window_days: int = DEFAULT_WINDOW_DAYS,
    db_path: str | Path | None = None,
    as_of: date | None = None,
) -> AttributionReport:
    """组合主入口（MOD-PLAN-009）：读库 → 三维归因报告。

    Args:
        module: 统计对象模块标识（如 "plan_engine.scenario_planner"）。
        window_days: 统计窗口天数（默认 20，45号 §4 W0 口径）。
        db_path: 库路径；None=DB_PATH SSoT（测试注入临时库）。
        as_of: 窗口基准日（None=date.today()）。

    Returns:
        AttributionReport（JSON 可序列化，W0 三维归因表消费契约）。

    Raises:
        ValueError: module/window_days 非法（fail-closed）。
        sqlite3.Error: 库级异常透传。
    """
    v_module = _validate_module(module)
    v_window = _validate_window_days(window_days)
    end = as_of if as_of is not None else date.today()
    window_start = (end - timedelta(days=v_window - 1)).isoformat()
    records, skipped = load_attribution_records(
        v_module,
        window_days=v_window,
        db_path=db_path,
        as_of=end,
    )
    return compute_attribution(
        records,
        module=v_module,
        window_days=v_window,
        window_start=window_start,
        window_end=end.isoformat(),
        skipped_invalid=skipped,
    )
