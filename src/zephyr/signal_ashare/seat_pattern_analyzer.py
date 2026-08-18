# [BLUEPRINT] MOD-SIG-056 | docs/03_modules/_domain_signal/seat_pattern_analyzer/blueprint.md
# [MODULE] zephyr.signal_ashare.seat_pattern_analyzer
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] docs/01_policies_and_standards/_registry/catalogs/seat_registry.yaml
# [CONSUMERS] （MVP 阶段无——候选消费方：strategy_registry daban 类策略、factor_registry 席位溢价因子）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] follow_score ∈ [0, 100]; direction ∈ {long, neutral, avoid}; 无龙虎榜数据时 MUST 返回 degraded=True 不臆造信号
# [MODIFY-GUARD] docs/03_modules/_domain_signal/seat_pattern_analyzer/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SeatPatternDataError
# [TESTS] tests/signal_ashare/test_seat_pattern_analyzer.py
# [A_module] module_id=MOD-SIG-056 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""
MOD-SIG-056 — 龙虎榜席位形态分析器（CAND-SEAT-001 转正 MVP）

管"谁在买"：基于交易所每日龙虎榜披露（c1_market.dragon_tiger_seat），
识别上榜席位的身份/风格/资金结构，输出三类产物：
  ① 席位画像 SeatProfile——单席位身份识别+当日行为（seat_registry 15 席位匹配）
  ② 席位联动 SeatLinkage——同标的多席位共现（机构+游资同买=强；量化+散户同买=弱）
  ③ 跟随信号 FollowSignal——follow_score(0-100)+direction(long/neutral/avoid)

与 chart_pattern_registry 正交：图形形态管"怎么买"（价格形态），本模块管"谁在买"（结构化披露数据）。

分析框架真源：seat_registry.yaml §seat_analysis_framework 六维（定性/资金力度/位置/题材/结构/连续性）。
MVP 裁剪（第一性原理）：维度3（股价位置）/维度4（题材）依赖外部域输入，v0.2 接入；
维度6（连续性三日榜）依赖历史窗口聚合，v0.2 接入。v0.1 落地维度1/2/5。

数据源：DS-080 market_data.lhb_detail（JOB-076 ingest.akshare_lhb，东财口径）。
席位胜率字段（history_win_rate/avg_premium）当前 registry 为 null——v0.1 不用胜率，只用身份/风格/结构。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 龙虎榜席位明细行 列表
#   fields: symbol/trade_date/seat_name/buy_amount/sell_amount/net_amount/buy_rank/sell_rank/reason
#   code: SeatRecord L120
# - id: I2
#   name: seat_registry 席位档案
#   fields: seat_id/seat_name/seat_type/seat_style/aliases/max_holding_days
#   code: seat_registry.yaml seats:
# 层: 特征
# - id: F1
#   name_zh: 净买入占比
#   name_en: net_buy_ratio
#   intro: 席位净买入额占该票当日龙虎榜总成交额比例 >10%强势 <5%诱多
#   formula: net_amount / total_turnover
#   code: seat_pattern_analyzer.py SeatProfile.net_buy_ratio
#   registry: factor_registry: 无FCT条目（候选 seat_premium 因子前置特征）
#   is_break: true
# - id: F2
#   name_zh: 买一买二集中度
#   name_en: top2_concentration
#   intro: 买一+买二净买入占买方前五合计比例 40-60%最佳 >70%独食危险
#   formula: (net_rank1+net_rank2)/Σnet_buy_top5
#   code: seat_pattern_analyzer.py SeatLinkage.top2_concentration
#   registry: factor_registry: 无FCT条目
#   is_break: true
# 层: 算法
# - id: A1
#   name_zh: ① 席位身份识别
#   name_en: identify_seat
#   intro: seat_name/aliases 匹配 registry→命中取档案；未命中回退 provider 粗分类（institution/connect/broker）
#   desc: 精确匹配 seat_name → aliases 匹配 → provider seat_type 回退 → unknown
#   inputs: I1 I2
#   outputs: SeatProfile（含 matched_registry 标记）
# - id: A2
#   name_zh: ② 席位联动分析
#   name_en: analyze_linkage
#   intro: 同票同日多席位共现矩阵：机构+游资同买加分 量化+散户同买减分
#   desc: type_set 组合规则：{institution,youzi}=强势接力 {quant,retail}=绞肉机回避 {retail}独大=散户接盘
#   inputs: A1
#   outputs: SeatLinkage（type_set/top2_concentration/institution_net/youzi_net/quant_net/retail_net）
# - id: A3
#   name_zh: ③ 跟随信号合成
#   name_en: synthesize_follow_signal
#   intro: 基准50分+身份加减分+结构加减分+风格修正→0-100 分三档映射 direction
#   desc: institution 净买>0 +15 / 知名游资(龙头连板/首板)净买>0 +10 / quant 净买占比>30% -20 / retail 净买占比>30% -15 / top2>70% -10 / ≥60=long ≤40=avoid 其余 neutral
#   inputs: A1 A2 F1 F2
#   outputs: FollowSignal（follow_score/direction/reasons）
# 层: 输出
# - id: O1
#   name_zh: 席位形态分析结果
#   name_en: SeatPatternResult
#   intro: 三件套聚合：profiles+linkage+follow_signal+degraded 标记
#   downstream: strategy daban 类（候选）/ factor seat_premium（候选）
# [/ALGO_FLOW]
#
# 边:
# I1,I2 --> A1
# A1 --> A2
# A1,A2 --> A3
# A1,A2,A3 --> O1
"""

from __future__ import annotations

import logging
from enum import Enum
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

__all__ = [
    "FollowDirection",
    "FollowSignal",
    "SeatLinkage",
    "SeatPatternAnalyzer",
    "SeatPatternConfig",
    "SeatPatternDataError",
    "SeatPatternResult",
    "SeatProfile",
    "SeatRecord",
]

_SEAT_REGISTRY_PATH = (
    Path(__file__).resolve().parents[3]
    / "docs/01_policies_and_standards/_registry/catalogs/seat_registry.yaml"
)


class SeatPatternDataError(Exception):
    """输入数据契约违规（字段缺失/类型错误/金额为负）。"""


class FollowDirection(str, Enum):
    LONG = "long"
    NEUTRAL = "neutral"
    AVOID = "avoid"


class SeatRecord(BaseModel):
    """c1_market.dragon_tiger_seat 单行（东财口径 Top5 买卖席位合并去重）。"""

    symbol: str = Field(..., description="6 位证券代码")
    trade_date: str = Field(..., description="YYYY-MM-DD")
    seat_name: str = Field(..., description="交易营业部名称")
    buy_amount: float = Field(default=0.0, ge=0.0, description="买入额（元）")
    sell_amount: float = Field(default=0.0, ge=0.0, description="卖出额（元）")
    net_amount: float = Field(default=0.0, description="净买入额（元，可负）")
    buy_rank: int | None = Field(default=None, ge=1, le=5, description="买方排名 1-5")
    sell_rank: int | None = Field(default=None, ge=1, le=5, description="卖方排名 1-5")
    provider_seat_type: str = Field(
        default="broker", description="provider 粗分类：institution/connect/broker"
    )
    reason: str = Field(default="", description="上榜原因")


class SeatProfile(BaseModel):
    """单席位画像：身份识别结果 + 当日行为。"""

    seat_name: str
    seat_id: str | None = Field(default=None, description="registry 命中 seat_id，未命中 None")
    seat_type: str = Field(..., description="institution/youzi/quant/northbound/retail/connect/broker/unknown")
    seat_style: str = Field(default="", description="registry 操盘风格，未命中空串")
    matched_registry: bool = Field(..., description="是否命中 seat_registry 档案")
    buy_amount: float = 0.0
    sell_amount: float = 0.0
    net_amount: float = 0.0
    net_buy_ratio: float = Field(default=0.0, description="净买入占该票龙虎榜总成交额比例")


class SeatLinkage(BaseModel):
    """席位联动：同票同日多席位共现结构。"""

    type_set: list[str] = Field(..., description="上榜席位类型集合（去重排序）")
    buyer_count: int = Field(default=0, description="买方净买入为正的上榜席位数（独食判定需≥3）")
    top2_concentration: float = Field(default=0.0, description="买一买二净买入占买方合计比例")
    institution_net: float = 0.0
    youzi_net: float = 0.0
    quant_net: float = 0.0
    retail_net: float = 0.0
    linkage_tag: str = Field(..., description="institution_youzi_relay/quant_retail_grinder/retail_dominated/balanced")


class FollowSignal(BaseModel):
    """跟随信号：分数+方向+理由链。"""

    follow_score: float = Field(..., ge=0.0, le=100.0)
    direction: FollowDirection
    reasons: list[str] = Field(default_factory=list, description="加减分理由链（可追溯）")


class SeatPatternResult(BaseModel):
    """三件套聚合输出。"""

    symbol: str
    trade_date: str
    profiles: list[SeatProfile]
    linkage: SeatLinkage | None
    follow_signal: FollowSignal
    degraded: bool = Field(default=False, description="无数据/数据不全时为 True，信号不可用于决策")


class SeatPatternConfig(BaseModel):
    """阈值配置——默认值取自 seat_registry §seat_analysis_framework 六维框架。"""

    registry_path: str = Field(default=str(_SEAT_REGISTRY_PATH))
    strong_net_buy_ratio: float = Field(default=0.10, description="净买入占比>10% 强势（维度2）")
    weak_net_buy_ratio: float = Field(default=0.05, description="净买入占比<5% 诱多嫌疑（维度2）")
    top2_danger: float = Field(default=0.70, description="买一买二集中度>70% 独食危险（维度5）")
    quant_share_danger: float = Field(default=0.30, description="量化净买占绝对值比>30% 回避（维度1）")
    retail_share_danger: float = Field(default=0.30, description="散户净买占绝对值比>30% 回避（维度1）")
    score_long: float = Field(default=60.0, description="≥60 long")
    score_avoid: float = Field(default=40.0, description="≤40 avoid")
    youzi_follow_styles: tuple[str, ...] = Field(
        default=("龙头连板", "首板"), description="可跟随的游资风格白名单"
    )


class SeatPatternAnalyzer:
    """龙虎榜席位形态分析器——纯函数式，无内部状态。"""

    def __init__(self, config: SeatPatternConfig | None = None) -> None:
        self._config = config or SeatPatternConfig()
        self._registry = self._load_registry(self._config.registry_path)

    @staticmethod
    def _load_registry(path: str) -> dict[str, dict]:
        """加载 seat_registry.yaml → {seat_name 或 alias 小写: 席位档案}。"""
        p = Path(path)
        if not p.is_file():
            logger.warning("seat_registry 不存在，降级为空档案: %s", path)
            return {}
        try:
            data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as e:
            logger.warning("seat_registry 解析失败，降级为空档案: %s", e)
            return {}
        table: dict[str, dict] = {}
        for seat in data.get("seats") or []:
            name = str(seat.get("seat_name") or "").strip()
            if not name:
                continue
            table[name.lower()] = seat
            for alias in seat.get("aliases") or []:
                a = str(alias).strip().lower()
                if a:
                    table.setdefault(a, seat)
        return table

    def identify_seat(self, record: SeatRecord, total_turnover: float) -> SeatProfile:
        """A1 席位身份识别：精确名→别名→provider 粗分类→unknown。"""
        hit = self._registry.get(record.seat_name.strip().lower())
        if hit is not None:
            seat_type = str(hit.get("seat_type") or "unknown")
            seat_style = str(hit.get("seat_style") or "")
            seat_id = str(hit.get("seat_id") or "") or None
            matched = True
        else:
            seat_type = record.provider_seat_type or "unknown"
            seat_style = ""
            seat_id = None
            matched = False
        ratio = record.net_amount / total_turnover if total_turnover > 0 else 0.0
        return SeatProfile(
            seat_name=record.seat_name,
            seat_id=seat_id,
            seat_type=seat_type,
            seat_style=seat_style,
            matched_registry=matched,
            buy_amount=record.buy_amount,
            sell_amount=record.sell_amount,
            net_amount=record.net_amount,
            net_buy_ratio=ratio,
        )

    @staticmethod
    def _net_by_type(profiles: list[SeatProfile], seat_type: str) -> float:
        return sum(p.net_amount for p in profiles if p.seat_type == seat_type)

    def analyze_linkage(self, profiles: list[SeatProfile], records: list[SeatRecord]) -> SeatLinkage:
        """A2 席位联动分析：类型共现 + 买一买二集中度。"""
        type_set = sorted({p.seat_type for p in profiles})
        buyers = sorted(
            (r for r in records if r.buy_rank is not None and r.net_amount > 0),
            key=lambda r: r.buy_rank or 99,
        )
        total_buy_net = sum(r.net_amount for r in buyers)
        top2_net = sum(r.net_amount for r in buyers[:2])
        top2 = top2_net / total_buy_net if total_buy_net > 0 else 0.0

        inst_net = self._net_by_type(profiles, "institution")
        youzi_net = self._net_by_type(profiles, "youzi")
        quant_net = self._net_by_type(profiles, "quant")
        retail_net = self._net_by_type(profiles, "retail")

        ts = set(type_set)
        if "institution" in ts and "youzi" in ts and inst_net > 0 and youzi_net > 0:
            tag = "institution_youzi_relay"
        elif "quant" in ts and "retail" in ts:
            tag = "quant_retail_grinder"
        elif retail_net > 0 and retail_net >= max(inst_net, youzi_net, 0.0):
            tag = "retail_dominated"
        else:
            tag = "balanced"

        return SeatLinkage(
            type_set=type_set,
            buyer_count=len(buyers),
            top2_concentration=top2,
            institution_net=inst_net,
            youzi_net=youzi_net,
            quant_net=quant_net,
            retail_net=retail_net,
            linkage_tag=tag,
        )

    def synthesize_follow_signal(
        self,
        profiles: list[SeatProfile],
        linkage: SeatLinkage,
        total_turnover: float,
    ) -> FollowSignal:
        """A3 跟随信号合成：基准 50 + 身份/结构加减分 → 三档方向。"""
        cfg = self._config
        score = 50.0
        reasons: list[str] = []

        net_total = sum(p.net_amount for p in profiles)
        abs_net = sum(abs(p.net_amount) for p in profiles)

        if linkage.institution_net > 0:
            score += 15
            reasons.append("+15 机构净买入>0（席位定性最优）")
        known_youzi_net = sum(
            p.net_amount
            for p in profiles
            if p.seat_type == "youzi" and p.matched_registry and p.seat_style in cfg.youzi_follow_styles
        )
        if known_youzi_net > 0:
            score += 10
            reasons.append("+10 知名游资（龙头连板/首板风格）净买入>0")
        if abs_net > 0 and abs(linkage.quant_net) / abs_net > cfg.quant_share_danger and linkage.quant_net != 0:
            score -= 20
            reasons.append("-20 量化席位主导（T0 绞肉，跟随无溢价）")
        if abs_net > 0 and linkage.retail_net > 0 and linkage.retail_net / abs_net > cfg.retail_share_danger:
            score -= 15
            reasons.append("-15 散户席位（拉萨系）主导买入（接盘风险）")
        if linkage.buyer_count >= 3 and linkage.top2_concentration > cfg.top2_danger:
            score -= 10
            reasons.append("-10 买一买二集中度>70%（独食，次日砸盘风险）")

        net_ratio = net_total / total_turnover if total_turnover > 0 else 0.0
        if net_ratio > cfg.strong_net_buy_ratio:
            score += 10
            reasons.append("+10 净买入占比>10%（资金力度强势）")
        elif 0 < net_ratio < cfg.weak_net_buy_ratio:
            score -= 5
            reasons.append("-5 净买入占比<5%（诱多嫌疑）")

        if linkage.linkage_tag == "institution_youzi_relay":
            score += 5
            reasons.append("+5 机构+游资同买（强势接力结构）")
        elif linkage.linkage_tag == "quant_retail_grinder":
            score -= 10
            reasons.append("-10 量化+散户共现（绞肉机结构）")
        elif linkage.linkage_tag == "retail_dominated":
            score -= 5
            reasons.append("-5 散户主导（接盘结构）")

        score = max(0.0, min(100.0, score))
        if score >= cfg.score_long:
            direction = FollowDirection.LONG
        elif score <= cfg.score_avoid:
            direction = FollowDirection.AVOID
        else:
            direction = FollowDirection.NEUTRAL
        return FollowSignal(follow_score=round(score, 2), direction=direction, reasons=reasons)

    def analyze(self, records: list[SeatRecord]) -> SeatPatternResult:
        """主入口：单票单日龙虎榜席位明细 → 三件套结果。

        执行流程: ①校验非空+契约 → ②A1 逐席位识别 → ③A2 联动 → ④A3 信号合成
        关键决策点: 空输入/总成交额=0 → degraded=True 返回中性信号（不臆造）。
        """
        if not records:
            return SeatPatternResult(
                symbol="",
                trade_date="",
                profiles=[],
                linkage=None,
                follow_signal=FollowSignal(
                    follow_score=50.0,
                    direction=FollowDirection.NEUTRAL,
                    reasons=["无龙虎榜数据，降级中性"],
                ),
                degraded=True,
            )
        first = records[0]
        for r in records:
            if r.symbol != first.symbol or r.trade_date != first.trade_date:
                raise SeatPatternDataError(
                    f"输入混含多票/多日数据: {first.symbol}@{first.trade_date} vs {r.symbol}@{r.trade_date}"
                )
        total_turnover = sum(r.buy_amount + r.sell_amount for r in records)
        profiles = [self.identify_seat(r, total_turnover) for r in records]
        linkage = self.analyze_linkage(profiles, records)
        signal = self.synthesize_follow_signal(profiles, linkage, total_turnover)
        return SeatPatternResult(
            symbol=first.symbol,
            trade_date=first.trade_date,
            profiles=profiles,
            linkage=linkage,
            follow_signal=signal,
            degraded=total_turnover <= 0,
        )
