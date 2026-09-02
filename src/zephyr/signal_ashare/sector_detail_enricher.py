# [BLUEPRINT] MOD-SIG-081 | 待统筹登记（blueprint 未建，真源=缺口总账 GAP-F-17 行 + GAP-F-D1 核查）
# [MODULE] zephyr.signal_ashare.sector_detail_enricher
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] （纯函数聚合层：输入由各生产侧注入——MOD-SIG-079 量能偏离/limit_up_down 涨停计数/news_data 新闻/analyst_forecast 业绩证据）
# [CONSUMERS] （候选：板块详情页「周期定位」「拉升原因」两维度）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 周期五态封闭（蛰伏/启动/发酵/高潮/退潮）；拉升原因五类封闭（政策催化/业绩驱动/题材联动/资金推动/无明确原因）；业绩证据超窗（analyst_forecast 覆盖窗约 1 个月，GAP-F-D1 实证）不作有效原因仅 window_notes 留痕；高潮/发酵次日转弱→退潮（状态机平滑）；证据样本截断留痕；输入校验 fail-closed；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-17 行
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] metrics/news/as_of 非法→ValueError（fail-closed）；单新闻字段缺失按空串参与不抛
# [TESTS] tests/signal_ashare/test_sector_detail_enricher.py
# [A_module] module_id=MOD-SIG-081 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""MOD-SIG-081 — 板块详情补充维度（GAP-F-17，板块详情页两维度后端）。

两件套（均为纯函数聚合，输入由各生产侧注入）：
1. **TDX 周期表定位状态机**：五态封闭 蛰伏→启动→发酵→高潮→退潮。
   快照规则（初拍阈值待实盘标定）：高潮=涨停≥5 或（涨幅≥5%且涨停≥3）；
   发酵=涨停≥2 或（涨幅≥2%且量偏≥30%）；启动=涨幅≥0.5%且量偏≥0 且
   （涨停≥1 或涨幅≥1%）；退潮=涨幅≤−0.5% 且（前态=高潮/发酵 或 涨停=0）；
   其余=蛰伏（MVP 不出第六态「分歧」，高位涨跌互现归蛰伏留痕）。
   prev_phase 注入实现状态机平滑（高潮次日转弱直接退潮）。
2. **拉升原因聚合器**：新闻（title+content）×板块名/关键词命中 →
   政策催化/业绩驱动/题材联动三类证据计数；新闻无命中但量能显著放大 →
   资金推动（候选口径）；全无证据 → 无明确原因（不硬编）。
   **窗口限制留痕（GAP-F-D1）**：analyst_forecast 覆盖窗约 1 个月——业绩证据
   latest_date 距 as_of 超 earnings_stale_days（默认 35 天）即判超窗，
   不作有效原因，仅 window_notes 留痕（防陈旧业绩误导）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1 板块指标 SectorMetricsInput（涨幅/涨停数/量偏）
# - id: I2 新闻窗 list[NewsItemInput]
# - id: I3 业绩证据 EarningsEvidence（注入位，可 None）
# 层: 算法
# - id: A1 周期定位状态机（快照规则+prev 平滑）
# - id: A2 原因聚合（关键词命中计数+超窗守卫）
# 层: 输出
# - id: O1 SectorDetailEnrichment（cycle_phase + rally_reasons + window_notes）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1,I2,I3 --> A2
# A1,A2 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Final, Mapping, Sequence

logger = logging.getLogger(__name__)

__all__: Final = [
    "PHASE_CLIMAX",
    "PHASE_DORMANT",
    "PHASE_FERMENT",
    "PHASE_RETREAT",
    "PHASE_START",
    "REASON_EARNINGS",
    "REASON_FUND_FLOW",
    "REASON_NONE",
    "REASON_POLICY",
    "REASON_THEME",
    "CyclePhaseVerdict",
    "EarningsEvidence",
    "NewsItemInput",
    "RallyReason",
    "RallyReasonResult",
    "SectorDetailConfig",
    "SectorDetailEnrichment",
    "SectorMetricsInput",
    "aggregate_rally_reasons",
    "enrich_sector_detail",
    "locate_cycle_phase",
]

#: 周期五态（封闭集合）
PHASE_DORMANT: Final[str] = "蛰伏"
PHASE_START: Final[str] = "启动"
PHASE_FERMENT: Final[str] = "发酵"
PHASE_CLIMAX: Final[str] = "高潮"
PHASE_RETREAT: Final[str] = "退潮"

#: 拉升原因五类（封闭集合）
REASON_POLICY: Final[str] = "政策催化"
REASON_EARNINGS: Final[str] = "业绩驱动"
REASON_THEME: Final[str] = "题材联动"
REASON_FUND_FLOW: Final[str] = "资金推动"
REASON_NONE: Final[str] = "无明确原因"

#: 政策关键词（MVP 经验口径，可 config 覆盖）
_DEFAULT_POLICY_KEYWORDS: Final[tuple[str, ...]] = (
    "政策",
    "国务院",
    "发改委",
    "工信部",
    "财政部",
    "央行",
    "证监会",
    "补贴",
    "规划",
    "试点",
    "降准",
    "降息",
    "稳增长",
    "扶持",
)

#: 业绩关键词（MVP 经验口径）
_DEFAULT_EARNINGS_KEYWORDS: Final[tuple[str, ...]] = (
    "业绩预告",
    "预增",
    "扭亏",
    "业绩快报",
    "净利润增长",
    "订单",
    "中标",
    "签合同",
)

#: 题材关键词（板块拉升题材线索；与 MOD-SIG-066 词典同源语义、本模块自维护小集）
_DEFAULT_THEME_KEYWORDS: Final[dict[str, tuple[str, ...]]] = {
    "国产化": ("国产化", "自主可控", "光刻", "信创"),
    "AI算力": ("大模型", "算力", "人工智能", "AIGC"),
    "新能源": ("锂电", "光伏", "储能", "固态电池"),
    "低空军工": ("低空经济", "商业航天", "军工"),
    "涨价": ("涨价", "提价", "供不应求"),
}


# ------------------------------------------------------------------
# 配置 / 输入 / 输出
# ------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class SectorDetailConfig:
    """板块详情配置（MVP 初拍值，待实盘标定）。"""

    climax_min_limit_ups: int = 5  # 高潮：涨停家数阈值
    climax_min_ret_pct: float = 5.0  # 高潮：涨幅阈值（且涨停≥climax_ret_min_limit_ups）
    climax_ret_min_limit_ups: int = 3
    ferment_min_limit_ups: int = 2  # 发酵：涨停家数阈值
    ferment_min_ret_pct: float = 2.0  # 发酵：涨幅阈值（且量偏≥ferment_min_dev）
    ferment_min_dev_pct: float = 30.0
    start_min_ret_pct: float = 0.5  # 启动：涨幅下限（且量偏≥0 且[涨停≥1 或 涨幅≥start_strong_ret]）
    start_strong_ret_pct: float = 1.0
    retreat_max_ret_pct: float = -0.5  # 退潮：涨幅上限（且[前态高潮/发酵 或 涨停=0]）
    fund_flow_min_dev_pct: float = 50.0  # 资金推动候选：量偏阈值（且无新闻命中）
    earnings_stale_days: int = 35  # 业绩证据超窗（analyst_forecast 覆盖窗约 1 个月，GAP-F-D1）
    max_samples_per_reason: int = 3  # 单原因样本留痕条数上限
    policy_keywords: tuple[str, ...] = _DEFAULT_POLICY_KEYWORDS
    earnings_keywords: tuple[str, ...] = _DEFAULT_EARNINGS_KEYWORDS
    theme_keywords: Mapping[str, tuple[str, ...]] | None = None  # None=默认题材小集


@dataclass(frozen=True, slots=True)
class SectorMetricsInput:
    """板块当日指标（各生产侧注入：涨幅/涨停数/量偏）。"""

    sector_code: str
    sector_name: str
    day_ret_pct: float = 0.0  # 当日涨幅 %
    limit_up_count: int = 0  # 板块内涨停家数
    amount_deviation_pct: float = 0.0  # 成交额偏离 %（MOD-SIG-079 口径）


@dataclass(frozen=True, slots=True)
class NewsItemInput:
    """新闻输入（news_data 行映射）。"""

    news_id: str
    title: str = ""
    content: str = ""
    publish_time: str = ""


@dataclass(frozen=True, slots=True)
class EarningsEvidence:
    """业绩证据（analyst_forecast/业绩预告聚合注入位）。"""

    latest_date: str  # 最新证据日（YYYY-MM-DD；超窗守卫基准）
    summary: str = ""


@dataclass(frozen=True, slots=True)
class CyclePhaseVerdict:
    """周期定位输出。"""

    phase: str  # 五态封闭
    prev_phase: str = ""
    evidence: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class RallyReason:
    """单条拉升原因。"""

    reason: str  # 五类封闭
    evidence_count: int = 0
    sample_news_ids: list[str] = field(default_factory=list)
    note: str = ""


@dataclass(frozen=True, slots=True)
class RallyReasonResult:
    """拉升原因聚合输出。"""

    reasons: list[RallyReason] = field(default_factory=list)
    window_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class SectorDetailEnrichment:
    """板块详情补充维度组合卡（观测层消费，不接交易）。"""

    sector_code: str
    sector_name: str
    cycle_phase: str
    phase_evidence: list[str] = field(default_factory=list)
    rally_reasons: list[RallyReason] = field(default_factory=list)
    window_notes: list[str] = field(default_factory=list)
    degraded: bool = False
    notes: list[str] = field(default_factory=list)


# ------------------------------------------------------------------
# 周期定位状态机
# ------------------------------------------------------------------


def locate_cycle_phase(
    metrics: SectorMetricsInput,
    prev_phase: str | None = None,
    config: SectorDetailConfig | None = None,
) -> CyclePhaseVerdict:
    """TDX 周期表定位（快照规则 + prev_phase 状态机平滑）。

    Args:
        metrics: 板块当日指标（fail-closed）。
        prev_phase: 前一日相位（五态之一或 None；非法值按 None 处理+evidence 留痕）。
        config: 配置（None 用默认）。

    Returns:
        CyclePhaseVerdict（phase + evidence 留痕）。

    Raises:
        ValueError: metrics 类型非法（fail-closed）。
    """
    if not isinstance(metrics, SectorMetricsInput):
        raise ValueError(f"metrics 非法（须 SectorMetricsInput）: {type(metrics).__name__}")
    cfg = config or SectorDetailConfig()
    m = metrics
    evidence: list[str] = [
        f"涨幅 {m.day_ret_pct:.2f}% / 涨停 {m.limit_up_count} 家 / 量偏 {m.amount_deviation_pct:.1f}%"
    ]
    valid_phases = {PHASE_DORMANT, PHASE_START, PHASE_FERMENT, PHASE_CLIMAX, PHASE_RETREAT}
    prev = prev_phase if prev_phase in valid_phases else ""
    if prev_phase and not prev:
        evidence.append(f"prev_phase 非法值 {prev_phase!r} 按无前态处理")

    if m.limit_up_count >= cfg.climax_min_limit_ups or (
        m.day_ret_pct >= cfg.climax_min_ret_pct and m.limit_up_count >= cfg.climax_ret_min_limit_ups
    ):
        phase = PHASE_CLIMAX
        evidence.append(
            f"涨停 {m.limit_up_count}≥{cfg.climax_min_limit_ups} 或涨幅≥{cfg.climax_min_ret_pct}%且涨停≥{cfg.climax_ret_min_limit_ups} → 高潮"
        )
    elif m.limit_up_count >= cfg.ferment_min_limit_ups or (
        m.day_ret_pct >= cfg.ferment_min_ret_pct and m.amount_deviation_pct >= cfg.ferment_min_dev_pct
    ):
        phase = PHASE_FERMENT
        evidence.append(
            f"涨停 {m.limit_up_count}≥{cfg.ferment_min_limit_ups} 或涨幅≥{cfg.ferment_min_ret_pct}%且量偏≥{cfg.ferment_min_dev_pct}% → 发酵"
        )
    elif m.day_ret_pct <= cfg.retreat_max_ret_pct and (prev in (PHASE_CLIMAX, PHASE_FERMENT) or m.limit_up_count == 0):
        phase = PHASE_RETREAT
        evidence.append(
            f"涨幅 {m.day_ret_pct:.2f}%≤{cfg.retreat_max_ret_pct}% 且（前态={prev or '无'}∈高潮/发酵 或 涨停=0）→ 退潮"
        )
    elif (
        m.day_ret_pct >= cfg.start_min_ret_pct
        and m.amount_deviation_pct >= 0.0
        and (m.limit_up_count >= 1 or m.day_ret_pct >= cfg.start_strong_ret_pct)
    ):
        phase = PHASE_START
        evidence.append(f"涨幅≥{cfg.start_min_ret_pct}% 且量偏≥0 且（涨停≥1 或涨幅≥{cfg.start_strong_ret_pct}%）→ 启动")
    else:
        phase = PHASE_DORMANT
        evidence.append("无命中规则 → 蛰伏（高位分歧不出第六态，MVP 归蛰伏留痕）")
    return CyclePhaseVerdict(phase=phase, prev_phase=prev, evidence=evidence)


# ------------------------------------------------------------------
# 拉升原因聚合器
# ------------------------------------------------------------------


def _hits(text: str, keywords: Sequence[str]) -> bool:
    return any(kw in text for kw in keywords)


def aggregate_rally_reasons(
    sector_name: str,
    news_items: Sequence[NewsItemInput],
    earnings: EarningsEvidence | None,
    metrics: SectorMetricsInput,
    config: SectorDetailConfig | None = None,
    as_of: str | date | None = None,
) -> RallyReasonResult:
    """拉升原因聚合（政策/业绩/题材新闻命中 + 资金推动候选 + 无明确原因兜底）。

    Args:
        sector_name: 板块名（新闻关联底本：标题/内容含板块名的新闻优先归属；
            MVP 口径=关键词命中即计，板块名过滤由调用方预筛留痕）。
        news_items: 新闻窗（NewsItemInput 序列）。
        earnings: 业绩证据注入位（None=无业绩腿）；超窗（>earnings_stale_days）
            不作有效原因，仅 window_notes 留痕（GAP-F-D1：analyst_forecast
            覆盖窗约 1 个月）。
        metrics: 板块指标（资金推动候选需量偏）。
        config: 配置（None 用默认）。
        as_of: 超窗判定基准日（None=今日；str YYYY-MM-DD / date）。

    Returns:
        RallyReasonResult（reasons 按证据计数降序 + window_notes）。

    Raises:
        ValueError: metrics/news 元素类型非法 / as_of 非真实日期（fail-closed）。
    """
    if not isinstance(metrics, SectorMetricsInput):
        raise ValueError(f"metrics 非法（须 SectorMetricsInput）: {type(metrics).__name__}")
    cfg = config or SectorDetailConfig()
    if as_of is None:
        anchor = date.today()
    elif isinstance(as_of, date):
        anchor = as_of
    else:
        try:
            anchor = date.fromisoformat(str(as_of))
        except ValueError as exc:
            raise ValueError(f"as_of 非真实日期: {as_of!r}") from exc

    policy_ids: list[str] = []
    earnings_ids: list[str] = []
    theme_ids: list[str] = []
    theme_hits: set[str] = set()
    themes = cfg.theme_keywords or _DEFAULT_THEME_KEYWORDS
    for n in news_items:
        if not isinstance(n, NewsItemInput):
            raise ValueError(f"news_items 元素非法（须 NewsItemInput）: {type(n).__name__}")
        text = f"{n.title} {n.content}"
        if _hits(text, cfg.policy_keywords):
            policy_ids.append(n.news_id)
        if _hits(text, cfg.earnings_keywords):
            earnings_ids.append(n.news_id)
        for theme, kws in themes.items():
            if _hits(text, kws):
                theme_ids.append(n.news_id)
                theme_hits.add(theme)

    reasons: list[RallyReason] = []
    window_notes: list[str] = []
    if policy_ids:
        reasons.append(
            RallyReason(
                reason=REASON_POLICY,
                evidence_count=len(policy_ids),
                sample_news_ids=policy_ids[: cfg.max_samples_per_reason],
            )
        )
    # 业绩腿：新闻命中 + 注入证据（超窗守卫）
    earnings_count = len(earnings_ids)
    earnings_note = ""
    if earnings is not None:
        try:
            latest = date.fromisoformat(earnings.latest_date)
        except ValueError:
            latest = None
        if latest is None:
            window_notes.append(f"业绩证据日期非法 {earnings.latest_date!r}，业绩注入腿忽略")
        elif (anchor - latest).days > cfg.earnings_stale_days:
            window_notes.append(
                f"业绩证据超窗（最新 {earnings.latest_date}，距今 {(anchor - latest).days} 天 > "
                f"{cfg.earnings_stale_days} 天；analyst_forecast 覆盖窗约 1 个月，GAP-F-D1 实证），不作有效原因"
            )
        else:
            earnings_count += 1
            earnings_note = earnings.summary
    if earnings_count > 0:
        reasons.append(
            RallyReason(
                reason=REASON_EARNINGS,
                evidence_count=earnings_count,
                sample_news_ids=earnings_ids[: cfg.max_samples_per_reason],
                note=earnings_note,
            )
        )
    if theme_ids:
        reasons.append(
            RallyReason(
                reason=REASON_THEME,
                evidence_count=len(theme_ids),
                sample_news_ids=theme_ids[: cfg.max_samples_per_reason],
                note="命中题材: " + "/".join(sorted(theme_hits)),
            )
        )
    if not reasons and metrics.amount_deviation_pct >= cfg.fund_flow_min_dev_pct:
        reasons.append(
            RallyReason(
                reason=REASON_FUND_FLOW,
                evidence_count=0,
                note=f"无新闻命中但量偏 {metrics.amount_deviation_pct:.1f}%≥{cfg.fund_flow_min_dev_pct}%（候选口径，无直接证据）",
            )
        )
    if not reasons:
        reasons.append(RallyReason(reason=REASON_NONE, note="无新闻/业绩/资金证据，不硬编原因"))
    reasons.sort(key=lambda r: (-r.evidence_count, r.reason))
    return RallyReasonResult(reasons=reasons, window_notes=window_notes)


# ------------------------------------------------------------------
# 组合卡
# ------------------------------------------------------------------


def enrich_sector_detail(
    metrics: SectorMetricsInput,
    news_items: Sequence[NewsItemInput],
    earnings: EarningsEvidence | None,
    prev_phase: str | None,
    config: SectorDetailConfig | None = None,
    as_of: str | date | None = None,
) -> SectorDetailEnrichment:
    """板块详情补充维度组合入口（周期定位 × 拉升原因）。

    Args:
        metrics: 板块当日指标（fail-closed）。
        news_items: 新闻窗。
        earnings: 业绩证据注入位（None=无业绩腿）。
        prev_phase: 前一日相位（状态机平滑）。
        config: 配置（None 用默认）。
        as_of: 超窗判定基准日（None=今日；非法 fail-closed）。

    Returns:
        SectorDetailEnrichment。
    """
    cfg = config or SectorDetailConfig()
    phase_v = locate_cycle_phase(metrics, prev_phase, cfg)
    reasons = aggregate_rally_reasons(metrics.sector_name, news_items, earnings, metrics, cfg, as_of)
    return SectorDetailEnrichment(
        sector_code=metrics.sector_code,
        sector_name=metrics.sector_name,
        cycle_phase=phase_v.phase,
        phase_evidence=phase_v.evidence,
        rally_reasons=reasons.reasons,
        window_notes=reasons.window_notes,
        degraded=False,
        notes=[],
    )
