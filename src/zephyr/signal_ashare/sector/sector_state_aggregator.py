# [BLUEPRINT] MOD-SIG-026 supplement | docs/_working/archive/2026-09/design_memos/22_sector_rotation_spec.md §3.1①④⑧⑨ + docs/_working/sector_line/sector_layer_skeleton_v0.md
# [MODULE] zephyr.signal_ashare.sector.sector_state_aggregator
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.sector.sector_momentum（q3/q5/q20 多TF+percentile_ranks）; zephyr.signal_ashare.sector.sector_rrg（DualEma 10/26 四象限+whipsaw 确认）; zephyr.signal_ashare.sector.sector_breadth（涨停比 0-40 分）; zephyr.signal_ashare.sector.sector_rotation_state（5 状态+HHI+watch_score）; dataclasses/json
# [CONSUMERS] 批2 落库编排器（close_final 盘后定格→c1_market.sector_state/sector_preference）；daily_gate_snapshot._collect_l2（L2 门三原料供料，批2 接线）；plan_engine 板块门（乙档治本）
# [STARTUP] imported（纯函数库，无独立进程；编排调用方注入数据面板）
# [MATURITY] testing
# [INVARIANTS] 纯函数零 IO（CH 读取/落库归编排调用方）；算法全部指认 22 号 spec 公式级条目不重造
#              （momentum=§3.1⑧ 0.4/0.3/0.3；RRG=§3.1④ DualEma 10/26+连续 2 日确认；强度=§3.1①
#              涨停比 40%+梯队 30%+趋势 30%，涨停比=涨停数/成分数 v1.8.0 归一化口径；5 状态=§3.1⑨
#              4 维规则映射）；净流入分位=percentile_ranks 通用截面归一；板块热度禁回灌 emotion_index
#              （防循环红线，骨架稿§1）；短史/缺料成分如实 status=insufficient/missing 禁硬凑（骨架稿§7）；
#              preference tilt∈[0.8,1.2] 阈值 frozen（考试卡 D2 预承诺，改阈值=升版+重考）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单板块成分异常隔离（try 边界，缺史板块 quadrant=missing 不中断整体截面）；
#                  映射表未知 regime 档归 NEUTRAL 震荡行+axis_status='unknown_regime' 如实标注
# [TESTS] tests/signal_ashare/sector/test_sector_state_aggregator.py
# [TTL] permanent
"""板块状态聚合器（S10 强弱量化层 + D2 偏好映射层，v0 最小五成分）。

算法真源=22 号 spec v1.9.8 公式级条目（§3.1①④⑧⑨）+ 骨架稿 v0（集成编排不重造算法）。
本模块只做两件事：
  1. assemble_sector_states：把日K 面板/涨停/成分/资金四类已查好的数据面板
     组装成每板块每日 sector_state 行（momentum_pct/rrg_quadrant/strength/
     net_inflow_pct 五成分 + 市场级 rotation_state）；
  2. map_preference：大盘×情绪双轴 → 板块偏好标签（5 档）+tilt+禁入象限，
     情绪轴开发期用契约形态 mock（0.5 温和档），axis_status='mock' 如实留痕。

调用方（批2 编排器）负责：CH 面板查询（closes 62+ 日升序、涨停成分反查、
money_flow 板块聚合）、ReplacingMergeTree 落库、close_final/pre_open 两 stage 时点。
PIT 纪律：所有输入=「T 日收盘可见」数据；T 日收盘态=T+1 盘前输入（禁吃 T+1 信息）。
# [ALGO_FLOW] external: docs/03_modules/_domain_signal/algo_flow/sector_state_aggregator.yaml
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date

from zephyr.signal_ashare.sector.sector_breadth import limit_up_breadth_score, sector_limit_up_ratio
from zephyr.signal_ashare.sector.sector_momentum import multi_tf_momentum, percentile_ranks
from zephyr.signal_ashare.sector.sector_rotation_state import (
    RotationState,
    classify_rotation_state,
    top_n_hhi,
)
from zephyr.signal_ashare.sector.sector_rotation_state import (
    watch_score as state_watch_score,
)
from zephyr.signal_ashare.sector.sector_rrg import (
    RRGQuadrant,
    compute_rrg_series,
    confirm_quadrant_series,
)

#: 语义化版本（骨架稿§7：成分或阈值变更升 minor，映射结构变更升 major）
AGGREGATOR_VERSION = "0.1.0"

#: RRG 最小数据量 = long×2+short = 62 日（spec §3.1④，compute_rrg_series 同款）
RRG_MIN_LEN = 62

#: 强度-趋势维度阈值（=sector_analyzer.SectorAnalysisConfig 默认，小数口径）
_TREND_STRONG = 0.03
_TREND_WEAK = -0.02

#: 电风扇速度计 P90 分位（spec §3.1⑨ 轮转速度辅助指标）
_ROTATION_SPEED_P90 = 0.90

#: 情绪轴三档（骨架稿§4 frozen：≤0.4 低温 / 0.4-0.7 温和 / ≥0.7 高温）
_EMOTION_LOW = 0.40
_EMOTION_HIGH = 0.70

#: 大盘轴三档合并（骨架稿§4；dominant 实测值域 {r1,r2,r3,r4,r10,r11,r12}）
_REGIME_GROUPS: dict[str, str] = {
    "r1": "osc",
    "r2": "osc",  # 震荡
    "r3": "up",
    "r12": "up",  # 上行
    "r4": "down",
    "r10": "down",
    "r11": "down",  # 下行修复
}

#: 偏好标签 5 档（frozen，D2 卡）
LABEL_DEFENSIVE = "DEFENSIVE"
LABEL_BALANCED = "BALANCED"
LABEL_OFFENSIVE = "OFFENSIVE"
LABEL_FOLLOW = "FOLLOW"
LABEL_WARN = "CROWDING_WARN"

#: 契约 mock 情绪指数（开发期情绪班成品未出；0.5=温和档中性位，D2 期如实 INSUFFICIENT）
MOCK_EMOTION_INDEX = 0.5


@dataclass
class SectorPanelInputs:
    """可选面板封装（涨停/梯队/成分/资金流/名称/领涨史，None=该成分如实降档）。"""

    amount_panel: dict[str, list[float]] | None = None
    limit_up_by_sector: dict[str, int] | None = None
    tier_by_sector: dict[str, tuple[int, int]] | None = None
    constituents_by_sector: dict[str, int] | None = None
    sector_main_inflow: dict[str, float] | None = None
    sector_names: dict[str, str] | None = None
    leader_history: list[str] | None = None


@dataclass
class SectorStateRow:
    """单板块单日 sector_state 行（五成分+观察列+逐成分 status）。"""

    trade_date: date
    sector_code: str
    sector_name: str = ""
    momentum_pct: float | None = None
    rrg_quadrant: str | None = None
    strength: float | None = None
    net_inflow_pct: float | None = None
    capital_score: float | None = None  # 观察列（v0 无个股资金性质生产源，如实缺）
    watch_score: float | None = None  # 市场级调节分冗余存（单表回放用，观察列）
    components: list[dict] = field(default_factory=list)


@dataclass
class MarketState:
    """市场级轮动状态（spec §3.1⑨ 4 维输入+5 状态输出+电风扇速度计）。"""

    rotation_state: str = RotationState.NEUTRAL_MIXED.value
    watch_score: float = 0.0
    up_ratio: float = 0.0
    hhi_top5: float = 0.0
    lead_streak: int = 0
    disp_signal: int = 0
    rotation_speed: float = 0.0
    fast_rotation: bool = False


@dataclass
class PreferenceResult:
    """偏好映射输出（骨架稿§4：标签+倾斜系数+禁入象限+轴态留痕）。"""

    preference_label: str
    tilt: float
    banned_quadrant: str = ""
    regime_group: str = ""
    emotion_band: str = ""
    axis_status: str = "ok"  # ok / mock / unknown_regime / insufficient
    note: str = ""


def _trend_points(day_pct_chg: float) -> float:
    """板块指数当日涨跌幅 → 趋势维度得分（30 分制，阈值=SectorAnalysisConfig 默认）。"""
    if day_pct_chg >= _TREND_STRONG:
        return 30.0
    if day_pct_chg >= 0.0:
        return 15.0
    if day_pct_chg >= _TREND_WEAK:
        return 5.0
    return 0.0


def _tier_points(tier2_count: int, tier3_count: int) -> float:
    """梯队维度得分（30 分制；镜像 evaluate_strength：有三板=30/有二板=20/仅首板=10）。"""
    if tier3_count > 0:
        return 30.0
    if tier2_count > 0:
        return 20.0
    return 10.0


def _day_pct(closes: list[float]) -> float | None:
    """日K 收盘序列 → 当日涨跌幅（小数口径；不足 2 日 None）。"""
    if len(closes) < 2 or closes[-2] <= 0:
        return None
    return closes[-1] / closes[-2] - 1.0


def _rotation_speed_series(amount_panel: dict[str, list[float]]) -> list[float]:
    """成交额份额日变化速度计序列（spec §3.1⑨：0.5×Σ|share_i(t)−share_i(t-1)|）。

    输入：板块 → 成交额序列（升序、逐板块等长对齐由调用方保证；短序列板块忽略）。
    """
    codes = [c for c, seq in amount_panel.items() if len(seq) >= 2]
    if not codes:
        return []
    n = min(len(amount_panel[c]) for c in codes)
    speeds: list[float] = []
    for t in range(1, n):
        shares_prev = [amount_panel[c][t - 1] for c in codes]
        shares_curr = [amount_panel[c][t] for c in codes]
        s_prev = sum(shares_prev)
        s_curr = sum(shares_curr)
        if s_prev <= 0 or s_curr <= 0:
            speeds.append(0.0)
            continue
        diff = sum(abs(b / s_curr - a / s_prev) for a, b in zip(shares_prev, shares_curr, strict=True))
        speeds.append(0.5 * diff)
    return speeds


def _percentile_of(values: list[float], x: float) -> float:
    """x 在 values 中的分位（0-1；空序列 0.0）。"""
    if not values:
        return 0.0
    return sum(1 for v in values if v <= x) / len(values)


def _leader_and_streak(day_pct_by_sector: dict[str, float], leader_history: list[str] | None) -> tuple[str, int]:
    """领涨板块（当日涨幅 Top1）与连续领涨天数（leader_history 末位=今日；新王=1）。"""
    leader = max(day_pct_by_sector, key=lambda c: day_pct_by_sector[c])
    if not leader_history:
        return leader, 1
    if leader_history[-1] != leader:
        return leader, 1
    streak = 0
    for name in reversed(leader_history):
        if name != leader:
            break
        streak += 1
    return leader, streak


def _dispatch_signal(
    amount_panel: dict[str, list[float]],
    leader: str,
    leader_pct: float,
    prev_pct: float | None,
) -> int:
    """派发识别：领涨板块放量（>5日均量×1.2）且滞涨（涨幅<前日×0.5）。"""
    seq = amount_panel.get(leader) or []
    if len(seq) < 6 or prev_pct is None:
        return 0
    avg5_prev = sum(seq[-6:-1]) / 5.0
    if avg5_prev > 0 and seq[-1] > avg5_prev * 1.2:
        if leader_pct < prev_pct * 0.5:
            return 1
    return 0


def compute_market_state(
    day_pct_by_sector: dict[str, float],
    amount_panel: dict[str, list[float]],
    *,
    leader_history: list[str] | None = None,
    prev_day_pct_by_sector: dict[str, float] | None = None,
) -> MarketState:
    """市场级 5 状态判定（spec §3.1⑨ 4 维输入）。

    Args:
        day_pct_by_sector: 板块 → 当日涨跌幅（小数）。
        amount_panel: 板块 → 成交额升序序列（≥6 日，供 HHI/放量判别/速度计）。
        leader_history: 近 N 日领涨板块序列（旧→今，末位=今日；缺省按当日涨幅 Top1 推）。
        prev_day_pct_by_sector: 板块 → 前一日涨跌幅（派发判别"滞涨"用；缺省无法判派发）。

    Returns:
        MarketState（rotation_state/watch_score/4 维输入/速度计）。
    """
    codes = list(day_pct_by_sector)
    if not codes:
        return MarketState()
    up_ratio = sum(1 for v in day_pct_by_sector.values() if v > 0) / len(codes)

    turns_today = {c: (amount_panel.get(c) or [0.0])[-1] for c in codes}
    hhi = top_n_hhi(list(turns_today.values()), n=5)

    leader, streak = _leader_and_streak(day_pct_by_sector, leader_history)
    disp_signal = _dispatch_signal(
        amount_panel,
        leader,
        day_pct_by_sector[leader],
        (prev_day_pct_by_sector or {}).get(leader),
    )

    # 电风扇速度计：快轮动期（>P90）放宽 CONSENSUS_CLIMAX 阈值
    speeds = _rotation_speed_series(amount_panel)
    speed_now = speeds[-1] if speeds else 0.0
    p90 = sorted(speeds)[int(_ROTATION_SPEED_P90 * (len(speeds) - 1))] if speeds else 0.0
    fast = bool(speeds) and speed_now > p90

    state = classify_rotation_state(up_ratio, hhi, streak, disp_signal, fast_rotation=fast)
    return MarketState(
        rotation_state=state.value,
        watch_score=state_watch_score(state),
        up_ratio=up_ratio,
        hhi_top5=hhi,
        lead_streak=streak,
        disp_signal=disp_signal,
        rotation_speed=speed_now,
        fast_rotation=fast,
    )


def _market_state_from_closes(
    closes_panel: dict[str, list[float]],
    amount_panel: dict[str, list[float]],
    leader_history: list[str] | None,
) -> tuple[dict[str, float], dict[str, float], MarketState]:
    """由收盘面板派生当日/前日涨幅截面并判定市场级状态。"""
    day_pcts = {code: _day_pct(seq) for code, seq in closes_panel.items()}
    day_pcts = {c: p for c, p in day_pcts.items() if p is not None}
    prev_day_pcts = {code: (_day_pct(seq[:-1]) if len(seq) >= 2 else None) for code, seq in closes_panel.items()}
    prev_day_pcts = {c: p for c, p in prev_day_pcts.items() if p is not None}
    market = compute_market_state(
        day_pcts,
        amount_panel or closes_panel,
        leader_history=leader_history,
        prev_day_pct_by_sector=prev_day_pcts,
    )
    return day_pcts, prev_day_pcts, market


def assemble_sector_states(
    closes_panel: dict[str, list[float]],
    *,
    trade_date: date,
    benchmark_closes: list[float],
    panels: SectorPanelInputs | None = None,
    version: str = AGGREGATOR_VERSION,
) -> tuple[list[SectorStateRow], MarketState]:
    """组装每板块每日 sector_state 截面（S10 五成分，纯函数）。

    Args:
        closes_panel: 板块码 → 日K 收盘序列（时间升序；RRG 需 ≥62 日，不足该板块
            quadrant 如实 missing）。
        trade_date: 截面交易日 T（调用方保证所有序列末位=T 日）。
        benchmark_closes: 基准收盘序列（880001.SH 升序；与面板序列对齐由调用方保证）。
        amount_panel: 板块 → 成交额序列（市场级 HHI/速度计/派发判别；可缺）。
        limit_up_by_sector: 板块 → T 日涨停数（成分股反查口径）。
        tier_by_sector: 板块 → (二板数, 三板以上数)（consec_limit≥2/≥3）。
        constituents_by_sector: 板块 → T 日有效成分数（涨停比分母）。
        sector_main_inflow: 板块 → money_flow 主力净流入聚合值（量纲无关，仅取截面分位）。
        sector_names: 板块码 → 板块名（可缺）。
        leader_history: 近 N 日领涨板块（旧→今）。
        version: 语义化版本（缺省 AGGREGATOR_VERSION）。

    Returns:
        (sector_state 行列表, 市场级 MarketState)。
    """
    panels = panels or SectorPanelInputs()
    amount_panel = panels.amount_panel or {}
    limit_up_by_sector = panels.limit_up_by_sector or {}
    tier_by_sector = panels.tier_by_sector or {}
    constituents_by_sector = panels.constituents_by_sector or {}
    sector_main_inflow = panels.sector_main_inflow or {}
    sector_names = panels.sector_names or {}
    leader_history = panels.leader_history

    # ① 动量分位（spec §3.1⑧：0.4×q20+0.3×q5+0.3×q3，截面百分位）
    momentum = multi_tf_momentum(closes_panel)

    # ② 净流入截面分位（percentile_ranks 通用归一）
    inflow_pct = percentile_ranks(sector_main_inflow) if sector_main_inflow else {}

    # ③ 市场级状态（前日涨幅面板供派发判别"滞涨"维度）
    day_pcts, prev_day_pcts, market = _market_state_from_closes(closes_panel, amount_panel, leader_history)

    rows: list[SectorStateRow] = []
    for code, closes in closes_panel.items():
        mom = momentum.get(code)
        components: list[dict] = [
            {
                "name": "momentum_pct",
                "raw_value": mom,
                "weight": 0.4,
                "status": "ok" if mom is not None else "missing",
            }
        ]
        quadrant, quad_comp = _rrg_component(closes, benchmark_closes)
        components.append(quad_comp)
        strength, strength_comps = _strength_component(
            code, limit_up_by_sector, tier_by_sector, constituents_by_sector, day_pcts
        )
        components.extend(strength_comps)
        nif = inflow_pct.get(code)
        components.append(
            {
                "name": "net_inflow_pct",
                "raw_value": nif,
                "weight": None,
                "status": "ok" if nif is not None else "missing",
            }
        )
        components.append(
            {
                "name": "capital_score",
                "raw_value": None,
                "weight": None,
                "status": "missing",  # v0 无个股资金性质生产源（观察列，如实缺）
            }
        )
        rows.append(
            SectorStateRow(
                trade_date=trade_date,
                sector_code=code,
                sector_name=sector_names.get(code, ""),
                momentum_pct=mom,
                rrg_quadrant=quadrant,
                strength=strength,
                net_inflow_pct=nif,
                capital_score=None,
                watch_score=market.watch_score,
                components=components,
            )
        )
    return rows, market


def _rrg_component(closes: list[float], benchmark_closes: list[float]) -> tuple[str | None, dict]:
    """单板块 RRG 象限成分（缺史=insufficient / 计算异常=missing，落库小写契约）。"""
    if len(closes) < RRG_MIN_LEN or len(benchmark_closes) < RRG_MIN_LEN:
        return None, {"name": "rrg_quadrant", "raw_value": None, "weight": None, "status": "insufficient"}
    try:
        n = min(len(closes), len(benchmark_closes))
        series = compute_rrg_series(closes[-n:], benchmark_closes[-n:])
        confirmed = confirm_quadrant_series([p.quadrant for p in series])
        # 落库契约=骨架稿§5 DDL 小写口径（sector_rrg 枚举大写→lower 归一）
        quadrant = confirmed[-1].value.lower()
        return quadrant, {"name": "rrg_quadrant", "raw_value": quadrant, "weight": None, "status": "ok"}
    except (ValueError, ZeroDivisionError):
        return None, {"name": "rrg_quadrant", "raw_value": None, "weight": None, "status": "missing"}


def _strength_component(
    code: str,
    limit_up_by_sector: dict[str, int],
    tier_by_sector: dict[str, tuple[int, int]],
    constituents_by_sector: dict[str, int],
    day_pcts: dict[str, float],
) -> tuple[float | None, list[dict]]:
    """强度成分（涨停比 40%+梯队 30%+趋势 30%，spec §3.1① v1.8.0 归一化口径）。"""
    ratio = sector_limit_up_ratio(limit_up_by_sector.get(code, 0), constituents_by_sector.get(code, 0))
    if constituents_by_sector.get(code, 0) <= 0:
        return None, [{"name": "strength", "raw_value": None, "weight": 1.0, "status": "missing"}]
    t2, t3 = tier_by_sector.get(code, (0, 0))
    pct_day = day_pcts.get(code)
    tier_pts = _tier_points(t2, t3)
    trend_pts = _trend_points(pct_day) if pct_day is not None else 0.0
    breadth_pts = limit_up_breadth_score(ratio)
    strength = round(breadth_pts + tier_pts + trend_pts, 2)
    return strength, [
        {"name": "strength", "raw_value": strength, "weight": 1.0, "status": "ok"},
        {"name": "limit_up_ratio", "raw_value": ratio, "weight": None, "status": "ok"},
    ]


# ----------------------------------------------------------------------
# D2 偏好映射层（大盘×情绪双轴，frozen 规则表 v0）
# ----------------------------------------------------------------------

#: 3×3 frozen 规则表（骨架稿§4）：{emotion_band: {regime_group: (label, tilt, banned, note)}}
#: tilt∈[0.8,1.2] frozen（D2 卡预承诺）；banned=该档禁入 RRG 象限（∅=不禁入）。
_PREFERENCE_TABLE: dict[str, dict[str, tuple[str, float, str, str]]] = {
    "low": {
        "osc": (LABEL_DEFENSIVE, 0.8, "lagging", "低波高股息倾斜（RISK_OFF 同构：lagging 禁入）"),
        "up": (LABEL_BALANCED, 1.0, "", "均衡"),
        "down": (LABEL_DEFENSIVE, 0.8, "lagging", "超跌改善象限优先（PANIC_REPAIR 同构：improving 观察）"),
    },
    "mid": {
        "osc": (LABEL_FOLLOW, 1.0, "", "主线跟随（HEALTHY_MAINLINE 加分同构）"),
        "up": (LABEL_OFFENSIVE, 1.2, "lagging", "进攻：领先象限+动量 Top"),
        "down": (LABEL_BALANCED, 0.9, "", "均衡偏防御"),
    },
    "high": {
        "osc": (LABEL_WARN, 0.9, "", "拥挤警示（CONSENSUS_CLIMAX 扣分同构）"),
        "up": (LABEL_OFFENSIVE, 1.1, "lagging", "进攻+拥挤双示警（watch_score 抑制）"),
        "down": (LABEL_DEFENSIVE, 0.8, "lagging", "分歧回调防御（DISAGREEMENT_PULLBACK 同构）"),
    },
}


def emotion_band(value: float | None) -> str:
    """情绪指数 → 三档（≤0.4 低温 / 0.4-0.7 温和 / ≥0.7 高温）。"""
    if value is None:
        return "mid"  # 契约 mock 位（MOCK_EMOTION_INDEX=0.5）
    if value <= _EMOTION_LOW:
        return "low"
    if value >= _EMOTION_HIGH:
        return "high"
    return "mid"


def regime_group(dominant: str | None) -> str:
    """dominant 档（r1~r12）→ 三档合并组；未知档归震荡组（axis_status 由调用方标注）。"""
    if dominant is None:
        return "osc"
    return _REGIME_GROUPS.get(dominant, "osc")


def map_preference(
    regime_dominant: str | None,
    emotion_index: float | None = None,
) -> PreferenceResult:
    """大盘×情绪 → 板块偏好（D2 映射层纯函数，frozen 规则表 v0）。

    情绪轴开发期 mock（emotion_index=None 时按契约 mock 0.5 温和档处理，
    axis_status='mock' 如实留痕——D2 考试该段判 INSUFFICIENT 禁放行）。
    T 日收盘态=T+1 盘前输入；本函数不读任何行情（防循环红线）。
    """
    grp = regime_group(regime_dominant)
    band = emotion_band(emotion_index)
    label, tilt, banned, note = _PREFERENCE_TABLE[band][grp]
    status = "ok"
    notes: list[str] = [note]
    if emotion_index is None:
        status = "mock"
        notes.append("emotion_axis=contract_mock(0.5)——真值集成前该轴判 INSUFFICIENT")
    if regime_dominant is not None and regime_dominant not in _REGIME_GROUPS:
        status = "unknown_regime"
        notes.append(f"dominant={regime_dominant} 不在实测值域，归震荡组")
    if not math.isfinite(tilt) or not 0.8 <= tilt <= 1.2:  # pragma: no cover — frozen 表自检
        raise ValueError(f"tilt 越 frozen 界 [0.8,1.2]: {tilt}")
    return PreferenceResult(
        preference_label=label,
        tilt=tilt,
        banned_quadrant=banned,
        regime_group=grp,
        emotion_band=band,
        axis_status=status,
        note="；".join(notes),
    )


def quadrant_admits(banned_quadrant: str, quadrant: str | RRGQuadrant | None) -> bool:
    """偏好禁入象限判别（L2 门/选股漏斗消费的放行原语；小写契约归一）。"""
    if not banned_quadrant or quadrant is None:
        return True
    q = quadrant.value if isinstance(quadrant, RRGQuadrant) else str(quadrant)
    return q.lower() != banned_quadrant.lower()
