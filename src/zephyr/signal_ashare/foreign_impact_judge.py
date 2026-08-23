# [BLUEPRINT] MOD-SIG-038 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/90_methodology_open_questions.md §22.3（supplement：GAP-F-24 通道映射规则层，CAND-RSK-021 语义）
# [MODULE] zephyr.signal_ashare.foreign_impact_judge
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.data.foreign_market_coverage（FOREIGN_WATCHLIST/覆盖门控消费，MOD-DAT-foreign_coverage）; c1_market.us_index（只读，三大美股指数日频变动）
# [CONSUMERS] （候选：外盘页 12 迷你卡对A股利好/利空标签 + 6 通道整体分析表 + 综合判定）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 12 标的方向约定封闭（美股/港股/A50/日经/KOSPI 涨=利好；美元指数/离岸人民币/美债10Y/WTI 涨=利空；黄金=中性观察）；6 通道封闭（情绪/资金/行业/利率/避险/成本）；强度三档封闭（强≥2%/中≥1%/弱，与 MOD-SIG-038 异动分档同带）；missing 标的不参评 notes 留痕；综合判定=Σ(方向×强度×权重) 阈值化；未知标的忽略留痕；输入校验 fail-closed；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-24 行
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] changes 元素数值非法→ValueError（fail-closed）；us_index 查询异常→ValueError（加载腿 fail-closed）；判定核单标的不抛
# [TESTS] tests/signal_ashare/test_foreign_impact_judge.py
# [A_module] module_id=MOD-SIG-038_judge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""MOD-SIG-038 supplement — 外盘对 A 股影响判定引擎（GAP-F-24，外盘页整体分析后端）。

通道映射规则 + 传导强度分级（规则 MVP，CAND-RSK-021 语义）：
- **与 MOD-SIG-038 的边界**（消歧）：cross_market_conduction_sensor=相关/回归
  系数量化层（SPX/DJI/IXIC→000300 统计传导幅度）；本模块=12 标的 × 6 通道
  **规则判定层**（每标的利好/利空标签 + 通道强度 + 综合判定），规则显式可解释，
  两产出口径正交（系数 vs 规则标签）。
- **6 通道**：情绪（美股/港股/A50/日经/KOSPI）、资金（美元指数/离岸人民币）、
  利率（美债10Y）、成本（WTI）、避险（黄金）、行业（预留——商品→周期板块
  映射，MVP 由成本/避险通道承载，行业通道位预留不出伪映射）。
- **方向约定**：美股族/A50 涨=利好；美元指数/离岸人民币涨=利空（资金流出/
  人民币贬值）；美债10Y 涨=利空（收益率升压制成长估值）；WTI 涨=利空
  （输入成本/通胀压力，油气板块反向受益 note 留痕）；黄金=中性观察
  （涨跌仅标注避险情绪，不直接定多空）。
- **强度三档**（与 MOD-SIG-038 异动分档 1%/2% 同带）：|chg|≥2% 强 / ≥1% 中 /
  其余弱。
- **覆盖门控**：消费 MOD-DAT-foreign_coverage 产出——covered/stale 参评，
  missing 剔除+notes 留痕（available_keys_from_coverage 助手）。
- **综合判定**：score=Σ(sign×strength_mult×weight)；≥bull_threshold 偏多 /
  ≤bear_threshold 偏空 / 其间中性；影响强度=|score| 三档；summary 形如
  「偏空·弱影响」（L11 设计稿口径）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1 标的涨跌幅 {target_key: chg_pct}（注入/us_index 加载）
# - id: I2 覆盖键集 available_keys（覆盖门控）
# 层: 算法
# - id: A1 单标的方向约定×强度分档×通道映射
# - id: A2 加权聚合 → 综合判定
# 层: 输出
# - id: O1 ForeignImpactJudgement（verdicts + channel_scores + summary）
# [/ALGO_FLOW]
#
# 边:
# I1,I2 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Final, Mapping

logger = logging.getLogger(__name__)

__all__: Final = [
    "CHANNEL_CAPITAL",
    "CHANNEL_COST",
    "CHANNEL_HEDGE",
    "CHANNEL_INDUSTRY",
    "CHANNEL_RATE",
    "CHANNEL_SENTIMENT",
    "ForeignImpactConfig",
    "ForeignImpactJudgement",
    "ForeignImpactRule",
    "ForeignImpactVerdict",
    "TARGET_RULES",
    "available_keys_from_coverage",
    "compute_changes_from_us_index",
    "judge_foreign_impact",
]

#: 6 通道（封闭集合；行业通道 MVP 预留——商品→周期板块映射由成本/避险承载）
CHANNEL_SENTIMENT: Final[str] = "情绪"
CHANNEL_CAPITAL: Final[str] = "资金"
CHANNEL_INDUSTRY: Final[str] = "行业"
CHANNEL_RATE: Final[str] = "利率"
CHANNEL_HEDGE: Final[str] = "避险"
CHANNEL_COST: Final[str] = "成本"

#: 方向约定（封闭）：涨=利好 / 涨=利空 / 中性观察
_DIR_UP_POSITIVE: Final[str] = "up_positive"
_DIR_UP_NEGATIVE: Final[str] = "up_negative"
_DIR_NEUTRAL_WATCH: Final[str] = "neutral_watch"

#: 强度倍数（聚合权重）
_STRENGTH_MULT: Final[dict[str, float]] = {"强": 1.0, "中": 0.6, "弱": 0.3}

#: us_index 加载 SQL（TSV：symbol \t trade_date \t close，按 symbol, trade_date DESC）
_SQL_US_INDEX_RECENT: Final = (
    "SELECT symbol, trade_date, close FROM c1_market.us_index "
    "WHERE symbol IN ('DJI', 'IXIC', 'SPX') ORDER BY symbol, trade_date DESC"
)
_US_INDEX_KEY_MAP: Final[dict[str, str]] = {"DJI": "dow_jones", "IXIC": "nasdaq", "SPX": "sp500"}


@dataclass(frozen=True, slots=True)
class ForeignImpactRule:
    """单标的判定规则（12 标的静态映射）。"""

    key: str
    name_zh: str
    channel: str
    direction_mode: str  # up_positive/up_negative/neutral_watch
    weight: float
    note: str = ""


#: 12 标的规则表（方向约定真源；权重初拍待实盘标定，A50/汇率锚定 A 股最直接权重最高）
TARGET_RULES: Final[tuple[ForeignImpactRule, ...]] = (
    ForeignImpactRule("dow_jones", "道琼斯", CHANNEL_SENTIMENT, _DIR_UP_POSITIVE, 1.0),
    ForeignImpactRule("nasdaq", "纳斯达克", CHANNEL_SENTIMENT, _DIR_UP_POSITIVE, 1.0),
    ForeignImpactRule("sp500", "标普500", CHANNEL_SENTIMENT, _DIR_UP_POSITIVE, 1.0),
    ForeignImpactRule("hsi", "恒生指数", CHANNEL_SENTIMENT, _DIR_UP_POSITIVE, 0.8),
    ForeignImpactRule("nikkei", "日经225", CHANNEL_SENTIMENT, _DIR_UP_POSITIVE, 0.5),
    ForeignImpactRule("kospi", "KOSPI", CHANNEL_SENTIMENT, _DIR_UP_POSITIVE, 0.5),
    ForeignImpactRule("a50", "富时A50", CHANNEL_SENTIMENT, _DIR_UP_POSITIVE, 1.2),
    ForeignImpactRule("dxy", "美元指数", CHANNEL_CAPITAL, _DIR_UP_NEGATIVE, 0.8,
                      note="强美元→新兴市场资金流出压力"),
    ForeignImpactRule("usdcnh", "离岸人民币", CHANNEL_CAPITAL, _DIR_UP_NEGATIVE, 1.0,
                      note="人民币贬值→北向资金/风险偏好承压"),
    ForeignImpactRule("wti", "WTI原油", CHANNEL_COST, _DIR_UP_NEGATIVE, 0.6,
                      note="输入成本/通胀压力（油气产业链反向受益留痕）"),
    ForeignImpactRule("gold", "黄金", CHANNEL_HEDGE, _DIR_NEUTRAL_WATCH, 0.4,
                      note="避险情绪观察（黄金股反向受益留痕）"),
    ForeignImpactRule("ust10y", "美债10Y", CHANNEL_RATE, _DIR_UP_NEGATIVE, 0.8,
                      note="收益率升→成长估值压制"),
)


@dataclass(frozen=True, slots=True)
class ForeignImpactConfig:
    """判定配置（阈值初拍，与 MOD-SIG-038 异动分档 1%/2% 同带）。"""

    strength_mild_pct: float = 1.0  # 中强度下限
    strength_severe_pct: float = 2.0  # 强强度下限
    bull_threshold: float = 0.5  # 偏多总分阈值
    bear_threshold: float = -0.5  # 偏空总分阈值
    impact_strong: float = 1.5  # 强影响 |score| 阈值
    impact_mild: float = 0.7  # 中影响 |score| 阈值


@dataclass(frozen=True, slots=True)
class ForeignImpactVerdict:
    """单标的影响判定。"""

    key: str
    name_zh: str
    chg_pct: float
    label: str  # 利好/利空/中性
    channel: str
    strength: str  # 强/中/弱
    weight: float
    contribution: float  # sign×strength_mult×weight
    note: str = ""


@dataclass(frozen=True, slots=True)
class ForeignImpactJudgement:
    """对 A 股影响综合判定输出（观测层消费，不接交易）。"""

    verdicts: list[ForeignImpactVerdict] = field(default_factory=list)
    channel_scores: dict[str, float] = field(default_factory=dict)
    total_score: float = 0.0
    direction: str = "中性"  # 偏多/偏空/中性
    impact: str = "弱影响"  # 强影响/中影响/弱影响
    summary: str = "中性·弱影响"
    degraded: bool = False
    notes: list[str] = field(default_factory=list)


# ------------------------------------------------------------------
# 覆盖门控助手（消费 MOD-DAT-foreign_coverage 产出）
# ------------------------------------------------------------------


def available_keys_from_coverage(report: Any) -> set[str]:
    """从 ForeignCoverageReport 提取参评键集（covered/stale 参评，missing 剔除）。

    Args:
        report: zephyr.data.foreign_market_coverage.ForeignCoverageReport 鸭型
            （items 元素含 key/status 属性）。

    Returns:
        参评 target_key 集合。
    """
    return {
        str(item.key)
        for item in getattr(report, "items", [])
        if getattr(item, "status", "") in ("covered", "stale")
    }


# ------------------------------------------------------------------
# us_index 日频变动加载（query_fn 注入，TSV 解析同 coverage 模块口径）
# ------------------------------------------------------------------


def compute_changes_from_us_index(
    query_fn: Callable[[str], str],
) -> dict[str, float]:
    """三大美股指数最新日变动 %（us_index 最后两行价差）。

    Args:
        query_fn: SQL→TSV 查询函数（zephyr.data.ch_reader.query 鸭型）。

    Returns:
        {target_key: chg_pct}（dow_jones/nasdaq/sp500；单行的标的跳过不出伪变动）。

    Raises:
        ValueError: 查询异常（加载腿 fail-closed）。
    """
    try:
        tsv = query_fn(_SQL_US_INDEX_RECENT)
    except Exception as exc:  # noqa: BLE001 — 加载腿 fail-closed
        raise ValueError(f"us_index 查询异常: {exc!r}") from exc
    by_symbol: dict[str, list[float]] = {}
    for line in (tsv or "").splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        try:
            by_symbol.setdefault(parts[0], []).append(float(parts[2]))
        except ValueError:
            continue
    changes: dict[str, float] = {}
    for symbol, closes in by_symbol.items():
        key = _US_INDEX_KEY_MAP.get(symbol)
        if key is None or len(closes) < 2 or closes[1] <= 0:
            continue
        changes[key] = round((closes[0] / closes[1] - 1.0) * 100.0, 4)
    return changes


# ------------------------------------------------------------------
# 判定核（纯函数）
# ------------------------------------------------------------------


def _strength_of(abs_chg: float, cfg: ForeignImpactConfig) -> str:
    if abs_chg >= cfg.strength_severe_pct:
        return "强"
    if abs_chg >= cfg.strength_mild_pct:
        return "中"
    return "弱"


def judge_foreign_impact(
    changes: Mapping[str, float],
    available_keys: set[str] | frozenset[str] | None = None,
    config: ForeignImpactConfig | None = None,
) -> ForeignImpactJudgement:
    """对 A 股影响判定主核（纯函数，不触库）。

    Args:
        changes: {target_key: chg_pct}（日涨跌幅 %；注入或
            compute_changes_from_us_index 产出）。
        available_keys: 参评键集（None=全部参评；覆盖门控由
            available_keys_from_coverage 生成）。
        config: 配置（None 用默认）。

    Returns:
        ForeignImpactJudgement；无有效标的 → degraded。

    Raises:
        ValueError: changes 元素数值非法（fail-closed）。
    """
    cfg = config or ForeignImpactConfig()
    rule_map = {r.key: r for r in TARGET_RULES}
    notes: list[str] = []
    verdicts: list[ForeignImpactVerdict] = []
    for key, raw in changes.items():
        rule = rule_map.get(key)
        if rule is None:
            notes.append(f"未知标的 {key!r} 忽略（不在 12 标的规则表）")
            continue
        if available_keys is not None and key not in available_keys:
            notes.append(f"{key}（{rule.name_zh}）数据缺失（missing），不参评")
            continue
        try:
            chg = float(raw)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"changes[{key!r}] 数值非法: {raw!r}") from exc
        strength = _strength_of(abs(chg), cfg)
        if rule.direction_mode == _DIR_NEUTRAL_WATCH or chg == 0.0:
            label, sign = "中性", 0.0
        elif rule.direction_mode == _DIR_UP_POSITIVE:
            label, sign = ("利好", 1.0) if chg > 0 else ("利空", -1.0)
        else:
            label, sign = ("利空", -1.0) if chg > 0 else ("利好", 1.0)
        contribution = sign * _STRENGTH_MULT[strength] * rule.weight
        note = rule.note
        if rule.direction_mode == _DIR_NEUTRAL_WATCH and abs(chg) >= cfg.strength_severe_pct:
            note = (note + "；" if note else "") + ("避险升温" if chg > 0 else "避险降温")
        verdicts.append(
            ForeignImpactVerdict(
                key=key, name_zh=rule.name_zh, chg_pct=round(chg, 4),
                label=label, channel=rule.channel, strength=strength,
                weight=rule.weight, contribution=round(contribution, 6), note=note,
            )
        )
    if not verdicts:
        return ForeignImpactJudgement(
            direction="中性", impact="弱影响", summary="中性·弱影响",
            degraded=True, notes=notes + ["无有效参评标的，整体降级"],
        )

    channel_scores: dict[str, float] = {}
    for v in verdicts:
        channel_scores[v.channel] = round(channel_scores.get(v.channel, 0.0) + v.contribution, 6)
    total = round(sum(v.contribution for v in verdicts), 6)
    if total >= cfg.bull_threshold:
        direction = "偏多"
    elif total <= cfg.bear_threshold:
        direction = "偏空"
    else:
        direction = "中性"
    abs_total = abs(total)
    if abs_total >= cfg.impact_strong:
        impact = "强影响"
    elif abs_total >= cfg.impact_mild:
        impact = "中影响"
    else:
        impact = "弱影响"
    return ForeignImpactJudgement(
        verdicts=verdicts,
        channel_scores=channel_scores,
        total_score=total,
        direction=direction,
        impact=impact,
        summary=f"{direction}·{impact}",
        degraded=False,
        notes=notes,
    )
