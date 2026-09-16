# [BLUEPRINT] MOD-PA-031 | docs/03_modules/_domain_portfolio_alloc/regime_meta_allocator/blueprint.md
# [MODULE] zephyr.pf_alloc.allocation_inputs
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] zephyr.pf_alloc.allocation_config; zephyr.pf_alloc.core.regime_meta_allocator(静态评分法);
#   schemas.categories.alloc_budget_daily / alloc_shrinkage_daily(读模板真源);
#   zephyr.infrastructure.database_service(reader 角色); PyYAML(TDM 先验只读)
# [CONSUMERS] zephyr.pf_alloc.allocation_orchestrator
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 本模块=分配链三处"输入缺口"的唯一供件面（PFA-4 三实物缺口 + PFA-3 regime 零消费）：
#   ① base_weights 先验真源=PP-001 sleeves（只读，禁在本模块硬编码权重）；
#   ② PerformanceScore 生产者=钱包净值序列 → MOD-PA-007 规范静态映射（唯一口径）；
#   ③ regime/Shrinkage 输入=regime_snapshot_history PIT（trade_date≤当日 的最近快照）；
#   所有外部读经注入 reader（默认 DatabaseService reader 角色），SQL 模板一律取 schemas 真源；
#   fail-closed 方向=无教材时概率退化平坦分布（ConfidenceSignal 落最低档 0.30），禁 1.0/禁 flat 满部署
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError(日期字面量非法/入参越界)；读库失败由 DatabaseService 抛出（不静默吞）；
#   无教材/无净值不抛错——按 fail-closed 缺省口径产出并在 source 字段如实登记
# [TESTS] tests/pf_alloc/test_allocation_orchestrator.py; tests/pf_alloc/test_pf_alloc_e2e.py
# [A_module] module_id=MOD-PA-031 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] allocation-inputs-mod-pa-031-20260916
"""allocation_inputs——组合分配链的输入供件层（车道 D 实盘接线，2026-09-16）。

真源：docs/_working/full-auto-chain/S11_assembled_backtest/nodes/pf_alloc_consumer_mining.md
  PFA-3（regime/Shrinkage 在实盘分配里零消费，"实盘连被压缩的分配器都没有"；
        注记 "regime_snapshot_history 已有 shrinkage 列可作分配输入真源"）
  PFA-4（三实物缺口：base_weights 无源 / 月度再权无调度体 / PerformanceScore 无生产者）

[ALGO_FLOW]
输入: 业务交易日 trade_date + 策略宇宙（注册表 sim 条目）+ 注入式 reader（CH 只读）
前置检查: trade_date 必须匹配 _DATE_RE（防裸串入 SQL）；reader 可调用；TDM 文件存在才读先验
执行: ① PP-001 sleeves -> base_weights（未命中策略用已知先验均值补齐，逐条登记来源）
      ② sim_pocket_daily 净值序列 -> 日收益率 -> MOD-PA-007 规范 PerformanceScore（含样本天数）
      ③ regime_snapshot_history PIT 快照 -> 7 维概率 + RiskSignal（直取/反演/中性三档口径）
      ④ alloc_budget_daily 历史 -> previous effective_budgets（防抖对照）+ 孤儿钱包集合
输出: BaseWeightTable / PerformanceScoreTable / RegimeInput / 历史 budget 映射（全纯数据）
降级: 无教材 -> 平坦概率 + neutral_fail_closed；无净值 -> 中性 1.0 + 0 样本（冷启动由分配器把关）
不变量: 概率向量长度恒 7（r1..r4 + r10..r12 顺序）；Σprobs≈1；risk_signal∈[0.30,1.00]；
        同一 (数据, 日期) 输入 -> 同一输出（纯函数，无墙钟依赖，RULE-SCHEMA-TZ）
[/ALGO_FLOW]
"""

from __future__ import annotations

import math
import re
import sys
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

try:
    from zephyr.shared.io.paths import REPO_ROOT as _REPO_ROOT
except Exception:  # noqa: BLE001 — 仅路径解析降级
    _REPO_ROOT = Path(__file__).resolve().parents[2]

# schemas/ 是仓根的 DDL-as-Code 真源包（不在 src 包内）。本模块可能被 cwd 不定的子进程
# （sim_paper_ledger 事件链）导入，故显式把仓根挂上 sys.path——与 scripts/ch/apply_*.py
# 同一先例，目的是**不复制表结构常量**（复制=两份真源=漂移）。
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from schemas.categories.alloc_budget_daily import (  # noqa: E402
    SQL_LATEST_EFFECTIVE_BUDGETS,
    TABLE_NAME as ALLOC_BUDGET_TABLE,
)
from schemas.categories.alloc_shrinkage_daily import (  # noqa: E402
    SQL_LATEST_REGIME_SNAPSHOT,
)
from zephyr.pf_alloc.allocation_config import AllocationConfig  # noqa: E402

# ── 常量（口径真源，禁散落）──────────────────────────────────────────

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# regime_snapshot_history 概率列顺序（与 DDL 列序一致，7 维：4 HMM 态 + 3 overlay 态）
REGIME_PROB_COLUMNS: tuple[str, ...] = (
    "p_r1",
    "p_r2",
    "p_r3",
    "p_r4",
    "p_r10",
    "p_r11",
    "p_r12",
)
CRISIS_STATE = "r10"  # overlay CRISIS 态键（D-SIGNAL-68）

# 无教材时的平坦分布（7 态等概率 → max(P)=1/7<0.60 → ConfidenceSignal 落最低档 0.30）
FLAT_PROBABILITIES: tuple[float, ...] = tuple([round(1.0 / len(REGIME_PROB_COLUMNS), 6)] * len(REGIME_PROB_COLUMNS))

# RiskSignal 反演区间（MOD-PA-007 RISK_SIGNAL_MIN/MAX 同口径，此处仅用于 clamp 兜底）
RISK_SIGNAL_MIN = 0.30
RISK_SIGNAL_MAX = 1.00

# 策略类型派生关键字（BudgetChangeHandler 收敛窗口键：打板 2d/事件驱动 3d/多因子 4d）
STRATEGY_TYPE_KEYWORDS: tuple[tuple[str, str], ...] = (
    ("DABAN", "打板"),
    ("daban", "打板"),
    ("打板", "打板"),
    ("EVENT", "事件驱动"),
    ("event", "事件驱动"),
    ("事件", "事件驱动"),
)
DEFAULT_STRATEGY_TYPE = "多因子"

Reader = Callable[[str], Sequence[Any]]


class AllocationInputError(ValueError):
    """分配链输入非法（日期/概率向量等契约违反）。"""

    error_code = "ZA-PA-0031"


def validate_date_literal(value: str | date) -> str:
    """把业务日期规整为 **已校验** 的 'YYYY-MM-DD' 字面量（SQL 模板入参前置门）。"""
    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")
    text = str(value).strip()
    if not _DATE_RE.match(text):
        raise AllocationInputError(f"日期字面量 {value!r} 非 YYYY-MM-DD（禁裸串入 SQL）")
    return text


def _date_or_none(raw: Any) -> date | None:
    if raw is None:
        return None
    if isinstance(raw, date):
        return raw
    text = str(raw)[:10]
    if not _DATE_RE.match(text):
        return None
    y, m, d = (int(x) for x in text.split("-"))
    return date(y, m, d)


def _default_reader(sql: str) -> Sequence[Any]:
    """默认只读通道：DatabaseService reader 角色（宪法 §9.1 禁裸 duckdb/裸连接散落）。"""
    from zephyr.infrastructure.database_service import get_db_service

    conn = get_db_service().get_clickhouse_conn(role="reader")
    return conn.execute(sql)


def resolve_reader(reader: Reader | None) -> Reader:
    return _default_reader if reader is None else reader


def derive_strategy_type(*hints: str | None) -> str:
    """从 strategy_id / sleeve / entry_logic 等提示派生策略类型（确定性，无外部依赖）。"""
    for hint in hints:
        if not hint:
            continue
        text = str(hint)
        for keyword, mapped in STRATEGY_TYPE_KEYWORDS:
            if keyword in text:
                return mapped
    return DEFAULT_STRATEGY_TYPE


# ── ① base_weights：PP-001 sleeve 先验（PFA-4 缺口 1）────────────────


@dataclass(frozen=True)
class BaseWeightTable:
    """先验权重表（未归一——MOD-PA-007 allocate() 内部归一并做 floor/cap）。"""

    weights: dict[str, float]
    sources: dict[str, str]  # strategy_id -> pp001_sleeve|pp001_mean_prior_fill|equal_weight
    max_single_sleeve: float | None = None  # PP-001 aggregator 真值（裁决层用）
    max_total_position: float | None = None
    plan_id: str = ""
    source_path: str = ""

    def as_allocator_weights(self) -> dict[str, float]:
        return dict(self.weights)


SOURCE_PP001 = "pp001_sleeve"
SOURCE_PP001_FILL = "pp001_mean_prior_fill"
SOURCE_EQUAL = "equal_weight"


def load_pp001_plan(tdm_path: str | Path) -> tuple[dict[str, float], dict[str, float], str]:
    """只读 TDM 的 portfolio_plan 段 -> (sleeve 权重, aggregator 上限, plan_id)。

    缺失文件/缺失段 -> 空表（调用方据此走等权补齐，并如实登记来源）。
    """
    path = Path(tdm_path)
    if not path.exists():
        return {}, {}, ""
    import yaml

    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    plan = doc.get("portfolio_plan") or {}
    if not isinstance(plan, Mapping):
        raise AllocationInputError(f"{path} portfolio_plan 根节点非映射")
    weights: dict[str, float] = {}
    for sleeve in plan.get("sleeves") or []:
        if not isinstance(sleeve, Mapping):
            continue
        ref = str(sleeve.get("strategy_ref") or "").strip()
        raw_w = sleeve.get("weight")
        if not ref or raw_w is None:
            continue
        try:
            w = float(raw_w)
        except (TypeError, ValueError) as exc:
            raise AllocationInputError(f"PP-001 sleeve {ref} weight={raw_w!r} 非数值") from exc
        if w <= 0:
            continue
        weights[ref] = weights.get(ref, 0.0) + w
    aggregator = {
        k: float(v)
        for k, v in (plan.get("aggregator") or {}).items()
        if isinstance(v, (int, float)) and not isinstance(v, bool)
    }
    return weights, aggregator, str(plan.get("plan_id") or "")


def build_base_weights(
    strategy_ids: Iterable[str],
    config: AllocationConfig,
) -> BaseWeightTable:
    """构造分配链先验：PP-001 命中用命中值，未命中用已知先验均值补齐。

    未命中策略为何用"均值"而非 0 或小值：PerformanceScore 才是后验主驱动，先验只需
    不给未登记策略以系统性歧视；均值是尺度无关的中性选择（allocator 归一后只剩相对差）。
    """
    ids = [str(s) for s in strategy_ids]
    priors, aggregator, plan_id = load_pp001_plan(config.tdm_full_path)
    weights: dict[str, float] = {}
    sources: dict[str, str] = {}
    matched = [w for sid, w in priors.items() if sid in set(ids)]
    fill = (sum(matched) / len(matched)) if matched else 0.0
    for sid in ids:
        if sid in priors:
            weights[sid] = float(priors[sid])
            sources[sid] = SOURCE_PP001
        elif fill > 0:
            weights[sid] = fill
            sources[sid] = SOURCE_PP001_FILL
        else:  # PP-001 完全不可用 -> 等权（分配器亦会在 None 时等权，此处显式登记）
            weights[sid] = 1.0
            sources[sid] = SOURCE_EQUAL
    return BaseWeightTable(
        weights=weights,
        sources=sources,
        max_single_sleeve=aggregator.get("max_single_sleeve"),
        max_total_position=aggregator.get("max_total_position"),
        plan_id=plan_id,
        source_path=str(config.tdm_full_path),
    )


# ── ② PerformanceScore：钱包净值 → 规范映射（PFA-4 缺口 3）──────────


@dataclass(frozen=True)
class PerformanceInput:
    """单策略绩效输入（净值可得性 + 分数）。"""

    strategy_id: str
    performance_score: float
    sortino: float
    sharpe: float
    sample_days: int  # 净值观测天数（<30 → 分配器冷启动中性）
    live_start_date: date | None
    returns_used: int
    note: str = ""


@dataclass(frozen=True)
class PerformanceScoreTable:
    scores: dict[str, float]
    sample_days: dict[str, int]
    details: dict[str, PerformanceInput] = field(default_factory=dict)


def _equity_sql(strategy_id: str, trade_date: str, limit: int) -> str:
    sid = strategy_id.replace("'", "")
    return (
        "SELECT trade_date, equity FROM c1_backtest.sim_pocket_daily FINAL "
        f"WHERE strategy_id = '{sid}' AND trade_date <= '{trade_date}' "
        f"ORDER BY trade_date DESC LIMIT {int(limit)}"
    )


def _first_equity_date_sql(strategy_id: str) -> str:
    sid = strategy_id.replace("'", "")
    return (
        "SELECT min(trade_date) FROM c1_backtest.sim_pocket_daily "
        f"WHERE strategy_id = '{sid}'"
    )


def daily_returns_from_equity(equity_asc: Sequence[float]) -> list[float]:
    """净值升序 → 日收益率（跳过非正值/前值，防除零与 NaN 污染 Sortino 分母）。"""
    returns: list[float] = []
    prev: float | None = None
    for value in equity_asc:
        v = float(value)
        if not math.isfinite(v) or v <= 0:
            continue
        if prev is not None and prev > 0:
            returns.append(v / prev - 1.0)
        prev = v
    return returns


def load_performance_scores(
    strategy_ids: Iterable[str],
    trade_date: str | date,
    config: AllocationConfig,
    *,
    reader: Reader | None = None,
    compute_score: Callable[..., tuple[float, float, float]] | None = None,
) -> PerformanceScoreTable:
    """钱包净值序列 → MOD-PA-007 规范 PerformanceScore（唯一口径，禁另起炉灶）。

    数据可得性口径：
      - 净值行数 <2 行 → 无收益率 → 冷启动中性 1.0（分配器再按 sample_days<30 复核）；
      - trading_days_live 用**全量净值行数**（首日起算的上线时长），收益率窗口用最近
        perf_lookback_days 行——两者分离是 §3.2.2 冷启动门槛的正确语义。
    """
    day = validate_date_literal(trade_date)
    rd = resolve_reader(reader)
    from zephyr.pf_alloc.core.regime_meta_allocator import RegimeMetaAllocator

    scorer = compute_score or RegimeMetaAllocator.compute_performance_score
    scores: dict[str, float] = {}
    samples: dict[str, int] = {}
    details: dict[str, PerformanceInput] = {}
    for sid in strategy_ids:
        sid = str(sid)
        rows = list(rd(_equity_sql(sid, day, config.perf_lookback_days + 1)))
        equity_desc = [float(r[1]) for r in rows]
        live_start = None
        live_rows = list(rd(_first_equity_date_sql(sid)))
        if live_rows and live_rows[0][0] is not None:
            live_start = _date_or_none(live_rows[0][0])
        equity_asc = list(reversed(equity_desc))
        returns = daily_returns_from_equity(equity_asc)
        days_live = len(equity_asc)
        if live_start is not None:
            days_live = max(days_live, _approx_trading_days(live_start, _date_or_none(day)))
        perf, sortino, sharpe = scorer(returns, trading_days_live=days_live)
        note = "" if returns else "无净值序列→中性 1.0（冷启动）"
        scores[sid] = float(perf)
        samples[sid] = int(days_live)
        details[sid] = PerformanceInput(
            strategy_id=sid,
            performance_score=float(perf),
            sortino=float(sortino),
            sharpe=float(sharpe),
            sample_days=int(days_live),
            live_start_date=live_start,
            returns_used=len(returns),
            note=note,
        )
    return PerformanceScoreTable(scores=scores, sample_days=samples, details=details)


def _approx_trading_days(start: date | None, end: date | None) -> int:
    """自然日→交易日粗估（×5/7，只用于冷启动时长下界，不做精细日历）。"""
    if start is None or end is None or end < start:
        return 0
    return max(0, int((end - start).days * 5 // 7))


# ── ③ regime 输入：教材 PIT 快照（PFA-3）────────────────────────────


@dataclass(frozen=True)
class RegimeInput:
    """分配链的 regime 侧输入（含来源口径，供 alloc_shrinkage_daily 溯源列）。"""

    probabilities: tuple[float, ...]
    dominant: str
    source_run_id: str
    source_date: date | None
    lag_days: int
    snapshot_shrinkage: float | None  # None=无教材
    risk_signal: float
    risk_signal_source: str  # snapshot_direct|snapshot_decomposed|neutral_fail_closed
    is_crisis: bool
    max_probability: float
    raw: Mapping[str, Any] = field(default_factory=dict)

    @property
    def has_snapshot(self) -> bool:
        return self.source_date is not None


def confidence_signal_from_max_prob(max_p: float) -> float:
    """ConfidenceSignal 四档（与 MOD-PA-007 CONFIDENCE_THRESHOLDS 同口径的独立复核）。"""
    from zephyr.pf_alloc.core.regime_meta_allocator import CONFIDENCE_THRESHOLDS

    for upper, signal in CONFIDENCE_THRESHOLDS:
        if max_p < upper:
            return float(signal)
    return float(CONFIDENCE_THRESHOLDS[-1][1])


def _as_probability_vector(row: Mapping[str, Any]) -> tuple[float, ...]:
    vec: list[float] = []
    for col in REGIME_PROB_COLUMNS:
        raw = row.get(col)
        try:
            val = float(raw)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            val = 0.0
        vec.append(val if math.isfinite(val) and val > 0 else 0.0)
    total = sum(vec)
    if total <= 0:
        return FLAT_PROBABILITIES
    return tuple(round(v / total, 8) for v in vec)


def resolve_risk_signal(
    snapshot: Mapping[str, Any] | None,
    probs: Sequence[float],
    mode: str,
) -> tuple[float, str]:
    """RiskSignal 三档口径（PFA-3：教材 risk_signal 列在产数据为 0.0=未填）。

    - snapshot_direct：教材 risk_signal 列可用（0<rs≤1）→ 直取；
    - snapshot_decomposed：教材只给了 EMA 后的 shrinkage → 用当日 ConfidenceSignal
      档值反演 risk≈shrinkage/confidence（clamp[0.30,1.00]）；
    - neutral_fail_closed：无教材 → risk=1.0 且概率平坦（conf 落最低档）→ 总节流 0.30。
    """
    if snapshot is None or mode == "neutral_fail_closed":
        return RISK_SIGNAL_MAX, "neutral_fail_closed"
    raw = snapshot.get("risk_signal")
    try:
        rs = float(raw)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        rs = 0.0
    if mode in ("auto", "snapshot_direct") and math.isfinite(rs) and 0 < rs <= 1:
        return max(RISK_SIGNAL_MIN, min(RISK_SIGNAL_MAX, rs)), "snapshot_direct"
    if mode in ("auto", "snapshot_decomposed"):
        try:
            shrink = float(snapshot.get("shrinkage"))  # type: ignore[arg-type]
        except (TypeError, ValueError):
            shrink = 0.0
        conf = confidence_signal_from_max_prob(max(float(x) for x in probs))
        if math.isfinite(shrink) and shrink > 0 and conf > 0:
            return max(RISK_SIGNAL_MIN, min(RISK_SIGNAL_MAX, shrink / conf)), "snapshot_decomposed"
    return RISK_SIGNAL_MAX, "neutral_fail_closed"


def load_regime_input(
    trade_date: str | date,
    config: AllocationConfig,
    *,
    reader: Reader | None = None,
) -> RegimeInput:
    """PIT 读 regime_snapshot_history：trade_date ≤ 当日的最近快照（禁未来函数）。"""
    day = validate_date_literal(trade_date)
    sql = SQL_LATEST_REGIME_SNAPSHOT.format(table="c1_backtest.regime_snapshot_history", date=day)
    rows = list(resolve_reader(reader)(sql))
    if not rows:
        probs = FLAT_PROBABILITIES
        risk, risk_src = resolve_risk_signal(None, probs, config.risk_signal_mode)
        return RegimeInput(
            probabilities=probs,
            dominant="unknown",
            source_run_id="synthetic_fail_closed",
            source_date=None,
            lag_days=-1,
            snapshot_shrinkage=None,
            risk_signal=risk,
            risk_signal_source=risk_src,
            is_crisis=False,
            max_probability=max(probs),
            raw={},
        )
    cols = (
        "run_id",
        "trade_date",
        "p_r1",
        "p_r2",
        "p_r3",
        "p_r4",
        "p_r10",
        "p_r11",
        "p_r12",
        "dominant",
        "confidence",
        "confidence_signal",
        "risk_signal",
        "shrinkage",
        "probs_json",
    )
    snapshot = dict(zip(cols, rows[0]))
    probs = _as_probability_vector(snapshot)
    risk, risk_src = resolve_risk_signal(snapshot, probs, config.risk_signal_mode)
    source_day = _date_or_none(snapshot.get("trade_date"))
    biz_day = _date_or_none(day)
    lag = (biz_day - source_day).days if (biz_day and source_day) else -1
    dominant = str(snapshot.get("dominant") or "") or (
        REGIME_PROB_COLUMNS[max(range(len(probs)), key=lambda i: probs[i])][2:]
    )
    try:
        shrink = float(snapshot.get("shrinkage"))  # type: ignore[arg-type]
    except (TypeError, ValueError):
        shrink = float("nan")
    return RegimeInput(
        probabilities=probs,
        dominant=dominant,
        source_run_id=str(snapshot.get("run_id") or ""),
        source_date=source_day,
        lag_days=int(lag),
        snapshot_shrinkage=shrink if math.isfinite(shrink) else None,
        risk_signal=risk,
        risk_signal_source=risk_src,
        is_crisis=dominant == CRISIS_STATE,
        max_probability=max(probs),
        raw=snapshot,
    )


# ── ④ 历史 budget（防抖对照）与宇宙来源 ─────────────────────────────


def load_previous_effective_budgets(
    trade_date: str | date,
    *,
    reader: Reader | None = None,
) -> dict[str, float]:
    """读 alloc_budget_daily 严格早于当日的每策略最近 effective_budget（防抖对照）。"""
    day = validate_date_literal(trade_date)
    sql = SQL_LATEST_EFFECTIVE_BUDGETS.format(table=ALLOC_BUDGET_TABLE, date=day)
    out: dict[str, float] = {}
    for sid, budget in resolve_reader(reader)(sql):
        try:
            out[str(sid)] = float(budget)
        except (TypeError, ValueError):
            continue
    return out


def universe_from_registry(
    registry_loader: Callable[[], Mapping[str, Any]] | None = None,
    lifecycle_status: str = "sim",
) -> list[dict[str, Any]]:
    """策略宇宙真源=策略注册表（与 sim_paper_ledger 同一 loader，RULE-SSOT 不另建路径）。"""
    if registry_loader is None:
        from zephyr.strategy_pipeline import intake as _intake

        registry_loader = _intake._load_registry
    reg = registry_loader() or {}
    out: list[dict[str, Any]] = []
    for entry in reg.get("strategies") or []:
        if not isinstance(entry, Mapping):
            continue
        if str(entry.get("lifecycle_status") or "") != lifecycle_status:
            continue
        sid = str(entry.get("strategy_id") or "").strip()
        if not sid:
            continue
        out.append(
            {
                "strategy_id": sid,
                "strategy_type": derive_strategy_type(
                    sid, entry.get("strategy_class"), entry.get("sleeve"), entry.get("entry_logic")
                ),
                "code_path": str(entry.get("code_path") or ""),
                "live_start_date": _date_or_none(entry.get("created_at")),
            }
        )
    return out
