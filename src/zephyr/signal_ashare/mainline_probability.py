# [BLUEPRINT] MOD-SIG-064 | 待统筹登记（blueprint 未建，真源=缺口总账 GAP-F-12 + 45号作战手册 §5 数据契约 MOD-SIG-061/062 消费层）
# [MODULE] zephyr.signal_ashare.mainline_probability
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.mainline_candidates（MOD-SIG-061 复用）; zephyr.signal_ashare.sector_leader（MOD-SIG-062 复用）; c1_market.money_flow（只读）; c1_market.sector_constituent（只读）
# [CONSUMERS] zephyr.signal_ashare.position_sector_context（MOD-SIG-065）; （候选：板块 Top10 页主线概率列、45号 W2 板块层、GAP-F-30 持仓板块语境）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 不预测纪律：输出为四因子启发式合成相对评分（0-100 标注"主线概率%"供前端契约），非校准概率、不出方向/点位；probability_pct ∈ [0,100]；缺维因子按可用权重重归一（不留 0 拉低）；无主线混沌（MOD-SIG-061 lead_streak<2）→ 空榜+注解不强行出分；PIT（全部数据 ≤ trade_date，成分股 SCD-2 时点过滤）；候选/资金/梯队三维独立降级互不累及；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-12 行
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 查询异常/客户端不可用→对应维度降级 notes 留痕不抛；MOD-SIG-061 候选 degraded→整体 degraded=True；trade_date 格式非法→ValueError（调用方契约违例，fail-closed）；weight_overrides 键非法→ValueError
# [TESTS] tests/signal_ashare/test_mainline_probability.py
# [A_module] module_id=MOD-SIG-064 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""MOD-SIG-064 — 主线概率综合评分（GAP-F-12 = 前端改版设计文档缺口①收口）。

四因子合成（先静态权重 MVP，权重全部走 config 可配置常量，weight_overrides 为
动态化接口位——后续接动态权重模型时按 sector 注入覆盖权重即可，评分核不动）：

| 因子 | 数据真源（全部复用已在码产出） | 子分口径 |
|---|---|---|
| RRG 象限 | MOD-SIG-061 MainlineCandidate.rrg_quadrant（sector_rrg 已确认象限） | LEADING 1.0 / IMPROVING 0.7 / WEAKENING 0.3 / LAGGING 0.1；数据积累期 None→缺维重归一 |
| 接力阶段 | MOD-SIG-062 板块龙头连板高度（板块内接力梯队阶段代理）+ MOD-SIG-061 市场 5 状态语境 | 无龙头 0.1（有中军 0.2）/ 首板 0.4 / 2板 0.6 / 3板 0.75 / ≥4板 0.9；市场=CONSENSUS_CLIMAX/DISTRIBUTION_RISK 见顶派发期 ×0.6 降档 |
| 资金持续性 | money_flow × sector_constituent 板块主力净流入逐日序列（MOD-SIG-060 虹吸腿同口径聚合） | 0.6×正流入日占比 + 0.4×尾部连续正流入日数占比（窗默认 10 交易日）；样本 <fund_min_periods → None 缺维 |
| 梯队完整度 | MOD-SIG-062 SectorRoleGroup 四档（leader/backbone/follower） | 龙头在 0.4 + 中军≥1 0.3 + 跟风 min(n/follower_full_count,1)×0.3 |

合成：probability_pct = Σ w_i·s_i / Σ w_i(可用) × 100；四维默认等权附近微调
（RRG 0.30/接力 0.25/资金 0.20/梯队 0.25，初拍待实盘标定）。全因子缺维 →
probability_pct=None + notes 留痕（不出伪分）。

评分宇宙 = MOD-SIG-061 主线候选榜（score≥2 入榜板块）；无主线混沌期候选榜空 →
本模块空榜。观测层消费不接交易（与 MOD-SIG-061/062 同纪律）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: MOD-SIG-061 主线候选榜（复用产出，含 RRG 象限/市场 5 状态/无主线标记）
#   fields: candidates(sector_code/sector_name/rrg_quadrant)/rotation_state/no_mainline_flag
# - id: I2
#   name: MOD-SIG-062 龙头识别榜（复用产出，含四档分组）
#   fields: sectors(sector_code/leader.consec_limit/backbones/followers)/degraded
# - id: I3
#   name: 板块成分映射（sector_constituent，SCD-2 时点有效）
#   fields: sector_code/stock_code
# - id: I4
#   name: 个股主力资金流窗（money_flow，资金持续性腿）
#   fields: trade_date/symbol_canonical/main_net_inflow
# 层: 特征
# - id: F1
#   name_zh: RRG 象限子分
#   formula: LEADING 1.0/IMPROVING 0.7/WEAKENING 0.3/LAGGING 0.1；None 缺维
# - id: F2
#   name_zh: 接力阶段子分
#   formula: 连板梯队映射(0.1/0.2/0.4/0.6/0.75/0.9)；市场见顶派发期 ×0.6
# - id: F3
#   name_zh: 资金持续性子分
#   formula: 0.6×pos_ratio + 0.4×streak_ratio（板块日净流入序列，streak=尾部连正日数）
# - id: F4
#   name_zh: 梯队完整度子分
#   formula: 龙头0.4 + 中军0.3 + min(跟风数/3,1)×0.3
# 层: 算法
# - id: A1
#   name_zh: 四因子加权合成
#   desc: pct=Σw·s/Σw(可用)×100；weight_overrides 动态接口位覆盖静态权重
# 层: 输出
# - id: O1
#   name_zh: MainlineProbabilityResult
#   intro: date/items(sector_code/probability_pct/四子分/reasons)/no_mainline_flag/degraded/notes/annotations；frozen dataclass asdict JSON 可序列化
# [/ALGO_FLOW]
#
# 边:
# I1 --> F1
# I1,I2 --> F2
# I3,I4 --> F3
# I2 --> F4
# F1,F2,F3,F4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any, Final, Mapping

from zephyr.signal_ashare.mainline_candidates import (
    MainlineCandidatesResult,
    compute_mainline_candidates,
)
from zephyr.signal_ashare.sector_leader import (
    SectorLeaderBoard,
    SectorRoleGroup,
    identify_sector_leaders,
)

logger = logging.getLogger(__name__)

__all__: Final = [
    "MainlineProbabilityConfig",
    "MainlineProbabilityItem",
    "MainlineProbabilityResult",
    "SectorFactorInput",
    "compute_mainline_probability",
    "score_echelon_completeness",
    "score_fund_persistence",
    "score_relay_stage",
    "score_rrg_quadrant",
    "score_sector_mainline",
]

#: RRG 象限 → 子分映射（sector_rrg 已确认象限口径）
_RRG_SCORE: Final = {
    "LEADING": 1.0,
    "IMPROVING": 0.7,
    "WEAKENING": 0.3,
    "LAGGING": 0.1,
}

#: 市场见顶/派发风险态（接力分降档触发，对齐 MOD-SIG-060 top_risk 口径）
_MARKET_RISK_STATES: Final = frozenset({"CONSENSUS_CLIMAX", "DISTRIBUTION_RISK"})

#: 动态权重接口位合法键（weight_overrides 白名单，fail-closed 校验）
_WEIGHT_KEYS: Final = frozenset({"rrg", "relay", "fund", "echelon"})

# SQL 集中化（§5.160.2）：模块级 SQL_* 常量，参数化查询禁 f-string 插值
SQL_SECTOR_CONSTITUENTS: Final = """
SELECT sector_code, stock_code
FROM c1_market.sector_constituent
WHERE valid_from <= %(trade_date)s AND (valid_to IS NULL OR valid_to > %(trade_date)s)
"""

SQL_MONEY_FLOW_WINDOW: Final = """
SELECT trade_date, symbol_canonical, main_net_inflow
FROM c1_market.money_flow
WHERE trade_date <= %(trade_date)s AND trade_date >= %(start_date)s
"""


@dataclass(frozen=True, slots=True)
class MainlineProbabilityConfig:
    """评分配置——静态权重 MVP（初拍值待实盘标定），weight_overrides 为动态化接口位。"""

    w_rrg: float = 0.30  # RRG 象限权重
    w_relay: float = 0.25  # 接力阶段权重
    w_fund: float = 0.20  # 资金持续性权重
    w_echelon: float = 0.25  # 梯队完整度权重
    fund_lookback_days: int = 10  # 资金持续性观察窗（交易日）
    fund_lookback_calendar_days: int = 30  # 资金查询自然日窗（覆盖 10 交易日）
    fund_min_periods: int = 5  # 资金序列最小样本（不足 → 缺维重归一）
    follower_full_count: int = 3  # 梯队跟风满分家数
    risk_state_relay_discount: float = 0.6  # 市场见顶/派发期接力分降档乘数
    top_k: int = 10  # 输出上限（板块 Top10 页契约）
    weight_overrides: Mapping[str, float] | None = None  # 动态化接口位：{因子键: 权重}，None=静态


@dataclass(frozen=True, slots=True)
class SectorFactorInput:
    """单板块四因子输入（参数 >7 收 dataclass 纪律）。"""

    sector_code: str
    sector_name: str
    rrg_quadrant: str | None  # 已确认 RRG 象限；数据不足 → None
    leader_consec: int | None  # 板块龙头连板高度；梯队榜降级 → None
    has_backbone: bool
    n_backbones: int
    n_followers: int
    fund_inflow_series: list[float] | None  # 板块日主力净流入序列（升序）；缺失 → None
    rotation_state: str | None  # 市场 5 状态（接力分语境降档）
    leader_board_missing: bool = False  # 梯队榜整体降级标记（True → relay/echelon 缺维）


@dataclass(frozen=True, slots=True)
class MainlineProbabilityItem:
    """单板块主线概率条目（启发式合成评分，非校准概率）。"""

    sector_code: str
    sector_name: str
    probability_pct: float | None  # 合成评分 0-100；全因子缺维 → None
    rrg_score: float | None
    relay_score: float | None
    fund_score: float | None
    echelon_score: float | None
    weight_mode: str  # static / override（动态权重接口位留痕）
    reasons: list[str] = field(default_factory=list)  # 评分明细理由链（中文可审计）
    notes: list[str] = field(default_factory=list)  # 缺维/降级留痕


@dataclass(frozen=True, slots=True)
class MainlineProbabilityResult:
    """主线概率综合评分输出契约（T 日盘后计算，观测层消费，不接交易）。"""

    date: str  # 数据日 YYYY-MM-DD
    items: list[MainlineProbabilityItem] = field(default_factory=list)
    no_mainline_flag: bool = False  # 无主线混沌（MOD-SIG-061 透传）→ 空榜
    degraded: bool = False  # 候选榜降级 → True（结果不可用于决策）
    annotations: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


# ------------------------------------------------------------------
# 因子子分（纯函数，不触库，可单测）
# ------------------------------------------------------------------


def score_rrg_quadrant(quadrant: str | None) -> float | None:
    """RRG 象限 → 子分；未知/缺数据 → None（缺维重归一）。"""
    if quadrant is None:
        return None
    return _RRG_SCORE.get(quadrant)


def score_relay_stage(
    leader_consec: int,
    has_backbone: bool,
    rotation_state: str | None = None,
    config: MainlineProbabilityConfig | None = None,
) -> float:
    """接力阶段子分：板块龙头连板高度梯队映射 + 市场见顶/派发期降档。

    无龙头：有中军 0.2 / 无中军 0.1；首板 0.4 / 2板 0.6 / 3板 0.75 / ≥4板 0.9。
    市场 5 状态 ∈ {CONSENSUS_CLIMAX, DISTRIBUTION_RISK} → ×risk_state_relay_discount。
    """
    cfg = config or MainlineProbabilityConfig()
    if leader_consec <= 0:
        base = 0.2 if has_backbone else 0.1
    elif leader_consec == 1:
        base = 0.4
    elif leader_consec == 2:
        base = 0.6
    elif leader_consec == 3:
        base = 0.75
    else:
        base = 0.9
    if rotation_state in _MARKET_RISK_STATES:
        return base * cfg.risk_state_relay_discount
    return base


def score_fund_persistence(
    daily_net_inflows: list[float] | None,
    config: MainlineProbabilityConfig | None = None,
) -> float | None:
    """资金持续性子分 = 0.6×正流入日占比 + 0.4×尾部连续正流入日数占比。

    样本 < fund_min_periods / None → None（缺维重归一，不出伪分）。
    """
    cfg = config or MainlineProbabilityConfig()
    if not daily_net_inflows:
        return None
    series = [float(x) for x in daily_net_inflows][-cfg.fund_lookback_days :]
    if len(series) < cfg.fund_min_periods:
        return None
    n = len(series)
    pos_ratio = sum(1 for x in series if x > 0) / n
    streak = 0
    for x in reversed(series):
        if x > 0:
            streak += 1
        else:
            break
    return 0.6 * pos_ratio + 0.4 * (streak / n)


def score_echelon_completeness(
    has_leader: bool,
    n_backbones: int,
    n_followers: int,
    config: MainlineProbabilityConfig | None = None,
) -> float:
    """梯队完整度子分 = 龙头 0.4 + 中军 0.3 + 跟风 min(n/follower_full_count,1)×0.3。"""
    cfg = config or MainlineProbabilityConfig()
    score = 0.4 if has_leader else 0.0
    if n_backbones >= 1:
        score += 0.3
    score += min(n_followers / cfg.follower_full_count, 1.0) * 0.3
    return score


def score_sector_mainline(
    factors: SectorFactorInput,
    config: MainlineProbabilityConfig | None = None,
) -> MainlineProbabilityItem:
    """四因子合成核（纯函数）：缺维重归一，weight_overrides 动态接口位。

    Raises:
        ValueError: weight_overrides 含白名单外因子键（调用方契约违例，fail-closed）。
    """
    cfg = config or MainlineProbabilityConfig()
    weights = {"rrg": cfg.w_rrg, "relay": cfg.w_relay, "fund": cfg.w_fund, "echelon": cfg.w_echelon}
    weight_mode = "static"
    if cfg.weight_overrides is not None:
        bad = set(cfg.weight_overrides) - _WEIGHT_KEYS
        if bad:
            raise ValueError(f"weight_overrides 含非法因子键: {sorted(bad)}（合法={sorted(_WEIGHT_KEYS)}）")
        weights = {k: float(cfg.weight_overrides.get(k, 0.0)) for k in _WEIGHT_KEYS}
        weight_mode = "override"

    notes: list[str] = []
    reasons: list[str] = []

    rrg = score_rrg_quadrant(factors.rrg_quadrant)
    if rrg is None:
        notes.append("RRG 象限缺数据（板块 K 线积累期），该维缺位重归一")
    else:
        reasons.append(f"RRG象限={factors.rrg_quadrant}（子分{rrg:.1f}）")

    relay: float | None = None
    echelon: float | None = None
    if factors.leader_board_missing or factors.leader_consec is None:
        notes.append("梯队榜降级，接力/梯队两维缺位重归一")
    else:
        relay = score_relay_stage(factors.leader_consec, factors.has_backbone, factors.rotation_state, cfg)
        reasons.append(
            f"接力阶段=龙头{factors.leader_consec}板（子分{relay:.2f}"
            + (f"，市场{factors.rotation_state}降档" if factors.rotation_state in _MARKET_RISK_STATES else "")
            + "）"
        )
        echelon = score_echelon_completeness(
            factors.leader_consec >= 1, factors.n_backbones, factors.n_followers, cfg
        )
        reasons.append(
            f"梯队=龙头{'有' if factors.leader_consec >= 1 else '无'}/中军{factors.n_backbones}/"
            f"跟风{factors.n_followers}（子分{echelon:.2f}）"
        )

    fund = score_fund_persistence(factors.fund_inflow_series, cfg)
    if fund is None:
        notes.append("资金持续性样本不足/缺失，该维缺位重归一")
    else:
        reasons.append(f"资金持续性子分{fund:.2f}")

    scores = {"rrg": rrg, "relay": relay, "fund": fund, "echelon": echelon}
    avail = [(weights[k], s) for k, s in scores.items() if s is not None]
    pct: float | None = None
    if not avail:
        notes.append("无可评因子（全维缺位），不出伪分")
    else:
        wsum = sum(w for w, _ in avail)
        if wsum <= 0:
            notes.append("可用因子权重和为 0（weight_overrides 全零），不出伪分")
        else:
            pct = round(sum(w * s for w, s in avail) / wsum * 100.0, 1)

    return MainlineProbabilityItem(
        sector_code=factors.sector_code,
        sector_name=factors.sector_name,
        probability_pct=pct,
        rrg_score=rrg,
        relay_score=relay,
        fund_score=fund,
        echelon_score=echelon,
        weight_mode=weight_mode,
        reasons=reasons,
        notes=notes,
    )


# ------------------------------------------------------------------
# 主入口（三维组装 + 合成）
# ------------------------------------------------------------------


def _normalize_date(trade_date: str | date | datetime) -> date:
    """归一化交易日（str 须 YYYY-MM-DD，非法格式抛 ValueError）。"""
    if isinstance(trade_date, datetime):
        return trade_date.date()
    if isinstance(trade_date, date):
        return trade_date
    return datetime.strptime(str(trade_date), "%Y-%m-%d").date()


def _default_client() -> Any | None:
    """延迟加载默认 CH 客户端（不可用时返回 None，由主入口转 degraded）。"""
    try:
        from zephyr.data.ch_writer import get_client

        return get_client()
    except Exception:  # noqa: BLE001 — 连接/依赖问题一律降级
        logger.warning("ch_writer 默认客户端不可用，主线概率评分降级", exc_info=True)
        return None


def _as_date(v: Any) -> date:
    """CH 日期行值归一（date 原样返回，str 按 YYYY-MM-DD 解析）。"""
    return v if isinstance(v, date) else _normalize_date(v)


def _fund_inflow_series(
    client: Any,
    sector_codes: set[str],
    current_date: date,
    cfg: MainlineProbabilityConfig,
) -> tuple[dict[str, list[float]], list[str]]:
    """资金持续性腿：money_flow × sector_constituent 聚合板块日主力净流入序列。

    Returns:
        ({板块: 逐日净流入升序序列}, notes)；查询异常 → ({}, [降级说明]) 独立降级。
    """
    try:
        constituents: dict[str, list[str]] = {}
        for row in client.execute(SQL_SECTOR_CONSTITUENTS, {"trade_date": current_date}):
            code = str(row[0])
            if code in sector_codes:
                constituents.setdefault(code, []).append(str(row[1]))
        start = current_date - timedelta(days=cfg.fund_lookback_calendar_days)
        mf_rows = client.execute(SQL_MONEY_FLOW_WINDOW, {"trade_date": current_date, "start_date": start})
    except Exception as e:  # noqa: BLE001 — 数据层异常独立降级不炸
        return {}, [f"money_flow/sector_constituent 查询异常，资金维降级: {e!r}"]

    flow_by_symbol_day: dict[tuple[date, str], float] = {}
    for row in mf_rows:
        flow_by_symbol_day[(_as_date(row[0]), str(row[1]))] = float(row[2] or 0.0)
    days = sorted({d for d, _ in flow_by_symbol_day if d <= current_date})
    out: dict[str, list[float]] = {}
    for code in sector_codes:
        stocks = constituents.get(code)
        if not stocks:
            continue
        out[code] = [
            sum(flow_by_symbol_day.get((d, s), 0.0) for s in stocks) for d in days
        ]
    if not out:
        return out, ["资金窗内候选板块无成分/资金流数据，资金维降级"]
    return out, []


def _degraded_result(date_str: str, note: str) -> MainlineProbabilityResult:
    logger.warning("主线概率评分降级: %s", note)
    return MainlineProbabilityResult(date=date_str, degraded=True, notes=[note])


def compute_mainline_probability(
    trade_date: str | date | datetime | None = None,
    ch_client: Any | None = None,
    config: MainlineProbabilityConfig | None = None,
    candidates_result: MainlineCandidatesResult | None = None,
    leader_board: SectorLeaderBoard | None = None,
) -> MainlineProbabilityResult:
    """主入口：主线概率四因子综合评分（复用 MOD-SIG-061/062 已在码产出）。

    Args:
        trade_date: 数据日；None 时由 MOD-SIG-061 候选榜取最新数据日（PIT 口径）。
        ch_client: clickhouse-driver 鸭子类型；None 时延迟取 ch_writer.get_client，
            不可得 → degraded。
        config: 评分配置（None 用默认静态权重 MVP）。
        candidates_result: 预计算 MOD-SIG-061 候选榜（测试/编排注入位）；None 现算。
        leader_board: 预计算 MOD-SIG-062 龙头榜（注入位）；None 现算。

    Returns:
        MainlineProbabilityResult；候选榜 degraded → 整体 degraded；
        资金/梯队维异常独立降级互不累及（notes 留痕）。
    """
    cfg = config or MainlineProbabilityConfig()
    if trade_date is not None:
        d = _normalize_date(trade_date)  # ValueError fail-closed（调用方契约违例）
    else:
        d = None

    client = ch_client if ch_client is not None else _default_client()
    if client is None and (candidates_result is None or leader_board is None):
        ds = (d or date.today()).isoformat()
        return _degraded_result(ds, "ch_client 未注入且默认客户端不可用")

    candidates = candidates_result or compute_mainline_candidates(d, ch_client=client)
    if candidates.degraded:
        return _degraded_result(candidates.date, f"主线候选榜降级: {'; '.join(candidates.notes)}")
    date_str = candidates.date
    notes: list[str] = list(candidates.notes)
    annotations: list[str] = list(candidates.annotations)

    if candidates.no_mainline_flag or not candidates.candidates:
        annotations.append("无主线混沌/候选榜空，主线概率不出分（不强行出榜）")
        return MainlineProbabilityResult(
            date=date_str,
            no_mainline_flag=candidates.no_mainline_flag,
            annotations=annotations,
            notes=notes,
        )

    board = leader_board
    if board is None:
        board = identify_sector_leaders(date_str, ch_client=client)
    board_missing = board.degraded
    if board_missing:
        notes.append(f"龙头识别榜降级，接力/梯队维缺位: {'; '.join(board.notes)}")
    groups: dict[str, SectorRoleGroup] = {g.sector_code: g for g in board.sectors}

    sector_codes = {c.sector_code for c in candidates.candidates}
    fund_series: dict[str, list[float]] = {}
    if client is not None:
        fund_series, fund_notes = _fund_inflow_series(client, sector_codes, _normalize_date(date_str), cfg)
        notes.extend(fund_notes)
    else:
        notes.append("ch_client 不可用，资金维降级")

    items: list[MainlineProbabilityItem] = []
    for cand in candidates.candidates:
        group = groups.get(cand.sector_code)
        leader_consec: int | None = None
        has_backbone = False
        n_backbones = 0
        n_followers = 0
        if group is not None and not board_missing:
            leader_consec = group.leader.consec_limit if group.leader is not None else 0
            has_backbone = bool(group.backbones)
            n_backbones = len(group.backbones)
            n_followers = len(group.followers)
        item = score_sector_mainline(
            SectorFactorInput(
                sector_code=cand.sector_code,
                sector_name=cand.sector_name,
                rrg_quadrant=cand.rrg_quadrant,
                leader_consec=leader_consec,
                has_backbone=has_backbone,
                n_backbones=n_backbones,
                n_followers=n_followers,
                fund_inflow_series=fund_series.get(cand.sector_code),
                rotation_state=candidates.rotation_state,
                leader_board_missing=board_missing or group is None,
            ),
            config=cfg,
        )
        items.append(item)

    items.sort(
        key=lambda it: (it.probability_pct is not None, it.probability_pct or 0.0, it.sector_code),
        reverse=True,
    )
    items = items[: cfg.top_k]
    if items:
        annotations.append(
            f"主线概率 Top{len(items)} 已出分（四因子启发式合成，静态权重 MVP，非校准概率）"
        )
    return MainlineProbabilityResult(
        date=date_str,
        items=items,
        no_mainline_flag=False,
        degraded=False,
        annotations=annotations,
        notes=notes,
    )
