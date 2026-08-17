# [BLUEPRINT] MOD-SIG-024 | docs/03_modules/_domain_signal/blueprint.md
# [MODULE] zephyr.signal_ashare.intraday_buy_sell_point_analyzer
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.institutional_behavior_analyzer; zephyr.signal_ashare.capital_flow_pattern_analyzer
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 6买6卖模式枚举固定; 3重确认全过才放行买入; 降级路径必须有日志
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/signal_ashare/test_intraday_buy_sell_point_analyzer.py
# [A_module] module_id=MOD-SIG-024 | layer=module | stability=stable | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: ashare_signal
# category: signal_analyzer
# status: active
# created: "2026-08-02"
# ---

r"""


D-SIGNAL-24 A股日内买卖点引擎

6种买入模式(突破买点/回调买点/逆向资金买点/竞价弱转强/分时突破/回封打板)
+ 6种卖出模式(目标价位止盈/趋势破位止盈/利好兑现止盈/封单减少止盈/龙头丧失止盈/强分歧止盈)
+ 3重确认(大盘环境/板块强度/资金流向)。

理论依据：技术分析 / 日内交易 / 分时分析。

设计文档默认值可配置——所有阈值通过 IntradayBuySellConfig 调整，
默认值取自 D:\临时工作区\依赖图-D-SIGNAL-信号域.md §D-SIGNAL-24。

依赖方向：D-SIGNAL-21(主力行为) + D-SIGNAL-22(资金线) -> D-SIGNAL-24 -> 下游执行层

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 日内行情与资金明细 IntradayBuySellInput数据类
#   fields: 现价/阻力位/均线价/量比/当日涨跌幅/资金净流入/开盘涨幅/竞价量比/前日烂板/前高/开板与回封/封单金额/流通市值/目标价/板块排名/连板数等
#   code: IntradayBuySellInput L145
# - id: I2
#   name: 上游确认分 标量分数
#   fields: 大盘情绪分(来自D-SIGNAL-25) + 板块强度分(来自D-SIGNAL-26/20) + 资金净流入(来自D-SIGNAL-22)
#   code: market_sentiment_score/sector_strength_score/capital_flow_inflow L188-L190
# 层: 特征
# - id: F1
#   name_zh: 突破涨幅
#   name_en: breakout_pct
#   intro: 现价相对阻力位涨了多少个百分点
#   formula: (现价-阻力位)/阻力位×100 ≥2% 且量比≥1.5 才命中
#   code: intraday_buy_sell_point_analyzer.py L355
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F2
#   name_zh: 回踩均线偏离度
#   name_en: deviation_pct
#   intro: 现价在均线上方但贴近均线的偏离百分比
#   formula: (现价-均线价)/均线价×100 ∈(0,3%] 且回调量比≤0.7
#   code: intraday_buy_sell_point_analyzer.py L376
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F3
#   name_zh: 封流比
#   name_en: seal_ratio
#   intro: 封单金额占流通市值的比例 衡量封板强度
#   formula: 封单金额/(流通市值×10000) ≥5%
#   code: intraday_buy_sell_point_analyzer.py L463
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F4
#   name_zh: 封单缩减比
#   name_en: decrease_ratio
#   intro: 当前封单相对初始封单还剩几成
#   formula: 当前封单/初始封单 ≤0.5 触发
#   code: intraday_buy_sell_point_analyzer.py L559
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F5
#   name_zh: 板块排名降幅
#   name_en: rank_drop
#   intro: 个股在板块内的排名掉了几名
#   formula: 当前板块排名-前次板块排名 ≥3 触发
#   code: intraday_buy_sell_point_analyzer.py L573
#   registry: factor_registry: 无FCT条目
#   is_break: true
# 层: 算法
# - id: A1
#   name_zh: ① 6种买入模式检测
#   name_en: detect_buy_points
#   intro: 扫描突破/回调/逆向资金/竞价弱转强/分时突破/回封打板6类买点
#   desc: 6条阈值规则逐条判定 命中生成BuySignal confidence=min(100, 基线50~60+涨幅与量比加权)
#   inputs: I1 F1 F2 F3
#   outputs: buy_signals 列表
# - id: A2
#   name_zh: ② 6种卖出模式检测
#   name_en: detect_sell_points
#   intro: 扫描目标价/趋势破位/利好兑现/封单减少/龙头丧失/强分歧6类卖点
#   desc: 6条阈值规则逐条判定 命中生成SellSignal confidence=min(100, 基线+幅度加权)
#   inputs: I1 F4 F5
#   outputs: sell_signals 列表
# - id: A3
#   name_zh: ③ 3重确认
#   name_en: check_confirmations
#   intro: 大盘环境/板块强度/资金流向3道闸门 全过才放行买入
#   desc: 大盘情绪≥40 且 板块强度≥60 且 资金净流入>0
#   inputs: I2
#   outputs: confirmations + all_passed
# - id: A4
#   name_zh: ④ 综合建议
#   name_en: _make_recommendation
#   intro: 卖出信号优先 买入需确认全过 否则等待或观望
#   desc: sell_conf≥60且≥buy_conf→sell; 有买信号+确认全过+conf≥50→buy; 确认未过→wait(conf×0.5); 无信号→hold
#   inputs: A1 A2 A3
#   outputs: recommendation + overall_confidence
# 层: 输出
# - id: O1
#   name_zh: 日内买卖点分析结果
#   name_en: IntradayBuySellResult
#   intro: 买卖信号清单+3重确认结果+综合建议 buy/sell/hold/wait
#   invariant: 6买6卖模式枚举固定 3重确认全过才放行买入 降级路径必须有日志
#   downstream: 无下游/内部使用（设计文档指向下游执行层）
# [/ALGO_FLOW]
#
# 边:
# I1 -.->|断点| F1
# I1 -.->|断点| F2
# I1 -.->|断点| F3
# I1 -.->|断点| F4
# I1 -.->|断点| F5
# I1 --> A1
# I1 --> A2
# I2 --> A3
# F1 --> A1
# F2 --> A1
# F3 --> A1
# F4 --> A2
# F5 --> A2
# A1 --> A4
# A2 --> A4
# A3 --> A4
# A4 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ============================================================================
# 枚举
# ============================================================================


class BuyPointType(str, Enum):
    """6种买入模式。"""

    BREAKOUT = "突破买点"  # 突破阻力位+放量
    PULLBACK = "回调买点"  # 上涨中回踩均线+缩量
    CONTRARIAN_CAPITAL = "逆向资金买点"  # 价跌但资金流入
    AUCTION_WEAK_TO_STRONG = "竞价弱转强"  # 前日烂板→次日竞价高开
    INTRADAY_BREAKOUT = "分时突破"  # 分时突破前高+放量
    RE_SEAL_BOARD = "回封打板"  # 开板后快速回封


class SellPointType(str, Enum):
    """6种卖出模式。"""

    TARGET_PRICE = "目标价位止盈"  # 到达目标价
    TREND_BREAK = "趋势破位止盈"  # 跌破趋势线/均线
    NEWS_REALIZED = "利好兑现止盈"  # 利好已兑现
    SEAL_DECREASE = "封单减少止盈"  # 封单大幅减少
    LEADER_LOSS = "龙头丧失止盈"  # 不再是板块龙头
    STRONG_DIVERGENCE = "强分歧止盈"  # 多次开板=强分歧


class ConfirmationType(str, Enum):
    """3重确认。"""

    MARKET_ENVIRONMENT = "大盘环境确认"
    SECTOR_STRENGTH = "板块强度确认"
    CAPITAL_FLOW = "资金流向确认"


# ============================================================================
# 配置
# ============================================================================


@dataclass(frozen=True)
class IntradayBuySellConfig:
    """日内买卖点可配置阈值——默认值取自设计文档 §D-SIGNAL-24。"""

    # ── 买入: 突破买点 ──
    breakout_volume_ratio_min: float = 1.5  # 量比>=1.5
    breakout_price_pct_min: float = 2.0  # 突破涨幅>=2%

    # ── 买入: 回调买点 ──
    pullback_to_ma_max_pct: float = 3.0  # 距均线<=3%
    pullback_volume_shrink_max: float = 0.7  # 缩量<=0.7倍

    # ── 买入: 逆向资金买点 ──
    contrarian_price_drop_min: float = -2.0  # 价跌<=-2%
    contrarian_capital_inflow_min: float = 0.0  # 资金净流入>0

    # ── 买入: 竞价弱转强 ──
    auction_open_pct_min: float = 3.0  # 高开>=3%
    auction_volume_ratio_min: float = 5.0  # 竞价量/流通股>=5%

    # ── 买入: 分时突破 ──
    intraday_breakout_volume_min: float = 2.0  # 量比>=2.0
    intraday_breakout_high_pct: float = 1.0  # 突破前高>=1%

    # ── 买入: 回封打板 ──
    re_seal_time_max_minutes: int = 15  # 15分钟内回封
    re_seal_seal_ratio_min: float = 0.05  # 封流比>=5%

    # ── 卖出: 目标价位止盈 ──
    target_price_reach_pct: float = 98.0  # 达到目标价98%

    # ── 卖出: 趋势破位止盈 ──
    trend_break_below_ma_pct: float = -1.0  # 跌破均线1%

    # ── 卖出: 封单减少止盈 ──
    seal_decrease_ratio: float = 0.5  # 封单缩减到50%

    # ── 卖出: 龙头丧失止盈 ──
    leader_loss_rank_drop_min: int = 3  # 板块排名下降3+

    # ── 卖出: 强分歧止盈 ──
    strong_divergence_open_count: int = 2  # 开板>=2次

    # ── 3重确认阈值 ──
    market_sentiment_min: float = 40.0  # 大盘情绪>=40
    sector_strength_min: float = 60.0  # 板块强度>=60
    capital_inflow_min: float = 0.0  # 资金净流入>0


# ============================================================================
# 输入 / 输出
# ============================================================================


@dataclass
class IntradayBuySellInput:
    """日内买卖点分析输入数据。"""

    symbol: str
    current_price: float
    # ── 突破买点 ──
    resistance_price: float = 0.0  # 阻力位
    volume_ratio: float = 1.0  # 量比
    # ── 回调买点 ──
    ma_price: float = 0.0  # 均线价
    pullback_volume_ratio: float = 1.0  # 回调时量比
    # ── 逆向资金买点 ──
    price_change_pct: float = 0.0  # 当日涨跌幅%
    capital_net_inflow: float = 0.0  # 资金净流入(万元)
    # ── 竞价弱转强 ──
    open_pct: float = 0.0  # 开盘涨幅%
    auction_volume_ratio: float = 0.0  # 竞价量比
    prev_bad_board: bool = False  # 前日是否烂板
    # ── 分时突破 ──
    prev_intraday_high: float = 0.0  # 前高
    intraday_volume_ratio: float = 1.0  # 分时量比
    # ── 回封打板 ──
    opened_board: bool = False  # 是否开过板
    re_seal_minutes: int = 0  # 回封用时(分钟)
    seal_order_amount: float = 0.0  # 封单金额(万元)
    float_market_cap: float = 0.0  # 流通市值(亿元)
    # ── 卖出: 目标价 ──
    target_price: float = 0.0
    # ── 卖出: 趋势破位 ──
    below_ma_pct: float = 0.0  # 距均线偏离%(负=跌破)
    # ── 卖出: 封单减少 ──
    initial_seal_amount: float = 0.0  # 初始封单
    current_seal_amount: float = 0.0  # 当前封单
    is_limit_up: bool = False  # 是否涨停
    # ── 卖出: 龙头丧失 ──
    prev_sector_rank: int = 1
    current_sector_rank: int = 1
    # ── 卖出: 强分歧 ──
    open_board_count: int = 0  # 开板次数
    consecutive_limit_ups: int = 0  # 连板数
    # ── 卖出: 利好兑现 ──
    news_realized: bool = False  # 利好是否已兑现
    # ── 3重确认 ──
    market_sentiment_score: float = 50.0  # 来自 D-SIGNAL-25
    sector_strength_score: float = 50.0  # 来自 D-SIGNAL-26/20
    capital_flow_inflow: float = 0.0  # 来自 D-SIGNAL-22


@dataclass
class BuySignal:
    """买入信号。"""

    point_type: str
    confidence: float  # 0~100
    reference_price: float
    reason: str


@dataclass
class SellSignal:
    """卖出信号。"""

    point_type: str
    confidence: float  # 0~100
    reference_price: float
    reason: str


@dataclass
class ConfirmationResult:
    """确认结果。"""

    confirmation_type: str
    passed: bool
    actual_value: float
    threshold: float
    reason: str


@dataclass
class IntradayBuySellResult:
    """日内买卖点分析结果。"""

    symbol: str
    buy_signals: list[BuySignal] = field(default_factory=list)
    sell_signals: list[SellSignal] = field(default_factory=list)
    confirmations: list[ConfirmationResult] = field(default_factory=list)
    all_confirmations_passed: bool = False
    # 综合建议: buy/sell/hold/wait
    recommendation: str = "wait"
    overall_confidence: float = 0.0
    audit_trail: list[dict[str, Any]] = field(default_factory=list)
    is_degraded: bool = False


# ============================================================================
# 分析器
# ============================================================================


class IntradayBuySellAnalyzer:
    """
    A股日内买卖点引擎（D-SIGNAL-24）。

    3维度分析：
      1. 6种买入模式检测
      2. 6种卖出模式检测
      3. 3重确认（大盘/板块/资金）
    """

    def __init__(self, config: IntradayBuySellConfig | None = None) -> None:
        self._config = config or IntradayBuySellConfig()

    # ------------------------------------------------------------------
    # 公开入口
    # ------------------------------------------------------------------

    def analyze(self, input_data: IntradayBuySellInput) -> IntradayBuySellResult:
        """执行日内买卖点分析。"""
        if not self._validate_input(input_data):
            logger.warning("IntradayBuySellAnalyzer: 输入数据不合法，返回降级结果")
            return self._degraded_result(input_data.symbol, "输入数据校验失败")

        audit_trail: list[dict[str, Any]] = []

        # ── 维度1: 6种买入模式 ──
        buy_signals = self.detect_buy_points(input_data)
        audit_trail.append(
            {
                "dimension": "buy_points",
                "count": len(buy_signals),
                "types": [s.point_type for s in buy_signals],
            }
        )

        # ── 维度2: 6种卖出模式 ──
        sell_signals = self.detect_sell_points(input_data)
        audit_trail.append(
            {
                "dimension": "sell_points",
                "count": len(sell_signals),
                "types": [s.point_type for s in sell_signals],
            }
        )

        # ── 维度3: 3重确认 ──
        confirmations = self.check_confirmations(input_data)
        all_passed = all(c.passed for c in confirmations)
        audit_trail.append(
            {
                "dimension": "confirmations",
                "all_passed": all_passed,
                "results": [{"type": c.confirmation_type, "passed": c.passed} for c in confirmations],
            }
        )

        # ── 综合建议 ──
        recommendation, overall_conf = self._make_recommendation(buy_signals, sell_signals, all_passed)

        return IntradayBuySellResult(
            symbol=input_data.symbol,
            buy_signals=buy_signals,
            sell_signals=sell_signals,
            confirmations=confirmations,
            all_confirmations_passed=all_passed,
            recommendation=recommendation,
            overall_confidence=overall_conf,
            audit_trail=audit_trail,
        )

    # ------------------------------------------------------------------
    # 维度1: 6种买入模式检测
    # ------------------------------------------------------------------

    def detect_buy_points(self, input_data: IntradayBuySellInput) -> list[BuySignal]:
        """检测6种买入模式，返回命中的买入信号列表。"""
        signals: list[BuySignal] = []

        # 1. 突破买点
        sig = self._check_breakout_buy(input_data)
        if sig:
            signals.append(sig)
        # 2. 回调买点
        sig = self._check_pullback_buy(input_data)
        if sig:
            signals.append(sig)
        # 3. 逆向资金买点
        sig = self._check_contrarian_capital_buy(input_data)
        if sig:
            signals.append(sig)
        # 4. 竞价弱转强
        sig = self._check_auction_weak_to_strong(input_data)
        if sig:
            signals.append(sig)
        # 5. 分时突破
        sig = self._check_intraday_breakout(input_data)
        if sig:
            signals.append(sig)
        # 6. 回封打板
        sig = self._check_re_seal_board(input_data)
        if sig:
            signals.append(sig)

        return signals

    def _check_breakout_buy(self, input_data: IntradayBuySellInput) -> BuySignal | None:
        """突破买点：价格突破阻力位 + 放量。"""
        cfg = self._config
        if input_data.resistance_price <= 0 or input_data.current_price <= 0:
            return None
        breakout_pct = (input_data.current_price - input_data.resistance_price) / input_data.resistance_price * 100.0
        if breakout_pct < cfg.breakout_price_pct_min:
            return None
        if input_data.volume_ratio < cfg.breakout_volume_ratio_min:
            return None
        confidence = min(
            100.0,
            50.0 + breakout_pct * 5.0 + (input_data.volume_ratio - 1.0) * 20.0,
        )
        return BuySignal(
            point_type=BuyPointType.BREAKOUT.value,
            confidence=round(confidence, 2),
            reference_price=input_data.resistance_price,
            reason=f"突破阻力位{input_data.resistance_price}，涨幅{breakout_pct:.1f}%，量比{input_data.volume_ratio:.1f}",
        )

    def _check_pullback_buy(self, input_data: IntradayBuySellInput) -> BuySignal | None:
        """回调买点：上涨中回踩均线 + 缩量。"""
        cfg = self._config
        if input_data.ma_price <= 0 or input_data.current_price <= 0:
            return None
        deviation_pct = (input_data.current_price - input_data.ma_price) / input_data.ma_price * 100.0
        # 价格在均线上方但接近均线（回踩）
        if deviation_pct < 0 or deviation_pct > cfg.pullback_to_ma_max_pct:
            return None
        if input_data.pullback_volume_ratio > cfg.pullback_volume_shrink_max:
            return None
        confidence = min(
            100.0,
            60.0 + (cfg.pullback_to_ma_max_pct - deviation_pct) * 10.0,
        )
        return BuySignal(
            point_type=BuyPointType.PULLBACK.value,
            confidence=round(confidence, 2),
            reference_price=input_data.ma_price,
            reason=f"回踩均线{input_data.ma_price}，偏离{deviation_pct:.1f}%，缩量比{input_data.pullback_volume_ratio:.1f}",
        )

    def _check_contrarian_capital_buy(self, input_data: IntradayBuySellInput) -> BuySignal | None:
        """逆向资金买点：价跌但资金净流入。"""
        cfg = self._config
        if input_data.price_change_pct > cfg.contrarian_price_drop_min:
            return None  # 跌幅不够
        if input_data.capital_net_inflow <= cfg.contrarian_capital_inflow_min:
            return None  # 资金未流入
        confidence = min(
            100.0,
            50.0 + abs(input_data.price_change_pct) * 5.0 + min(input_data.capital_net_inflow / 100.0, 50.0),
        )
        return BuySignal(
            point_type=BuyPointType.CONTRARIAN_CAPITAL.value,
            confidence=round(confidence, 2),
            reference_price=input_data.current_price,
            reason=f"价跌{input_data.price_change_pct:.1f}%但资金净流入{input_data.capital_net_inflow:.0f}万",
        )

    def _check_auction_weak_to_strong(self, input_data: IntradayBuySellInput) -> BuySignal | None:
        """竞价弱转强：前日烂板→次日竞价高开+竞价量放大。"""
        cfg = self._config
        if not input_data.prev_bad_board:
            return None
        if input_data.open_pct < cfg.auction_open_pct_min:
            return None
        if input_data.auction_volume_ratio < cfg.auction_volume_ratio_min:
            return None
        confidence = min(
            100.0,
            60.0 + input_data.open_pct * 5.0 + (input_data.auction_volume_ratio - 5.0) * 3.0,
        )
        return BuySignal(
            point_type=BuyPointType.AUCTION_WEAK_TO_STRONG.value,
            confidence=round(confidence, 2),
            reference_price=input_data.current_price,
            reason=f"前日烂板→竞价高开{input_data.open_pct:.1f}%，竞价量比{input_data.auction_volume_ratio:.1f}",
        )

    def _check_intraday_breakout(self, input_data: IntradayBuySellInput) -> BuySignal | None:
        """分时突破：分时突破前高 + 放量。"""
        cfg = self._config
        if input_data.prev_intraday_high <= 0 or input_data.current_price <= 0:
            return None
        breakout_pct = (
            (input_data.current_price - input_data.prev_intraday_high) / input_data.prev_intraday_high * 100.0
        )
        if breakout_pct < cfg.intraday_breakout_high_pct:
            return None
        if input_data.intraday_volume_ratio < cfg.intraday_breakout_volume_min:
            return None
        confidence = min(
            100.0,
            55.0 + breakout_pct * 10.0 + (input_data.intraday_volume_ratio - 1.0) * 15.0,
        )
        return BuySignal(
            point_type=BuyPointType.INTRADAY_BREAKOUT.value,
            confidence=round(confidence, 2),
            reference_price=input_data.prev_intraday_high,
            reason=f"分时突破前高{input_data.prev_intraday_high}，涨幅{breakout_pct:.1f}%，量比{input_data.intraday_volume_ratio:.1f}",
        )

    def _check_re_seal_board(self, input_data: IntradayBuySellInput) -> BuySignal | None:
        """回封打板：开板后快速回封 + 封单够强。"""
        cfg = self._config
        if not input_data.opened_board:
            return None
        if input_data.re_seal_minutes > cfg.re_seal_time_max_minutes:
            return None
        if input_data.float_market_cap <= 0:
            return None
        seal_ratio = input_data.seal_order_amount / (input_data.float_market_cap * 10000.0)
        if seal_ratio < cfg.re_seal_seal_ratio_min:
            return None
        confidence = min(
            100.0,
            60.0 + (cfg.re_seal_time_max_minutes - input_data.re_seal_minutes) * 2.0 + seal_ratio * 100.0,
        )
        return BuySignal(
            point_type=BuyPointType.RE_SEAL_BOARD.value,
            confidence=round(confidence, 2),
            reference_price=input_data.current_price,
            reason=f"开板后{input_data.re_seal_minutes}分钟回封，封流比{seal_ratio * 100:.1f}%",
        )

    # ------------------------------------------------------------------
    # 维度2: 6种卖出模式检测
    # ------------------------------------------------------------------

    def detect_sell_points(self, input_data: IntradayBuySellInput) -> list[SellSignal]:
        """检测6种卖出模式，返回命中的卖出信号列表。"""
        signals: list[SellSignal] = []

        # 1. 目标价位止盈
        sig = self._check_target_price_sell(input_data)
        if sig:
            signals.append(sig)
        # 2. 趋势破位止盈
        sig = self._check_trend_break_sell(input_data)
        if sig:
            signals.append(sig)
        # 3. 利好兑现止盈
        sig = self._check_news_realized_sell(input_data)
        if sig:
            signals.append(sig)
        # 4. 封单减少止盈
        sig = self._check_seal_decrease_sell(input_data)
        if sig:
            signals.append(sig)
        # 5. 龙头丧失止盈
        sig = self._check_leader_loss_sell(input_data)
        if sig:
            signals.append(sig)
        # 6. 强分歧止盈
        sig = self._check_strong_divergence_sell(input_data)
        if sig:
            signals.append(sig)

        return signals

    def _check_target_price_sell(self, input_data: IntradayBuySellInput) -> SellSignal | None:
        """目标价位止盈：价格达到目标价。"""
        cfg = self._config
        if input_data.target_price <= 0 or input_data.current_price <= 0:
            return None
        reach_pct = input_data.current_price / input_data.target_price * 100.0
        if reach_pct < cfg.target_price_reach_pct:
            return None
        confidence = min(100.0, 50.0 + (reach_pct - 98.0) * 25.0)
        return SellSignal(
            point_type=SellPointType.TARGET_PRICE.value,
            confidence=round(confidence, 2),
            reference_price=input_data.target_price,
            reason=f"价格{input_data.current_price}达目标价{input_data.target_price}的{reach_pct:.1f}%",
        )

    def _check_trend_break_sell(self, input_data: IntradayBuySellInput) -> SellSignal | None:
        """趋势破位止盈：跌破均线。"""
        cfg = self._config
        if input_data.below_ma_pct > cfg.trend_break_below_ma_pct:
            return None
        confidence = min(100.0, 60.0 + abs(input_data.below_ma_pct) * 10.0)
        return SellSignal(
            point_type=SellPointType.TREND_BREAK.value,
            confidence=round(confidence, 2),
            reference_price=input_data.current_price,
            reason=f"跌破均线{input_data.below_ma_pct:.1f}%",
        )

    def _check_news_realized_sell(self, input_data: IntradayBuySellInput) -> SellSignal | None:
        """利好兑现止盈：利好已兑现。"""
        if not input_data.news_realized:
            return None
        return SellSignal(
            point_type=SellPointType.NEWS_REALIZED.value,
            confidence=75.0,
            reference_price=input_data.current_price,
            reason="利好已兑现，后续上涨动力减弱",
        )

    def _check_seal_decrease_sell(self, input_data: IntradayBuySellInput) -> SellSignal | None:
        """封单减少止盈：涨停封单大幅减少。"""
        cfg = self._config
        if not input_data.is_limit_up:
            return None
        if input_data.initial_seal_amount <= 0:
            return None
        decrease_ratio = input_data.current_seal_amount / input_data.initial_seal_amount
        if decrease_ratio > cfg.seal_decrease_ratio:
            return None
        confidence = min(100.0, 60.0 + (1.0 - decrease_ratio) * 40.0)
        return SellSignal(
            point_type=SellPointType.SEAL_DECREASE.value,
            confidence=round(confidence, 2),
            reference_price=input_data.current_price,
            reason=f"封单从{input_data.initial_seal_amount:.0f}万减至{input_data.current_seal_amount:.0f}万（{decrease_ratio * 100:.0f}%）",
        )

    def _check_leader_loss_sell(self, input_data: IntradayBuySellInput) -> SellSignal | None:
        """龙头丧失止盈：板块排名大幅下降。"""
        cfg = self._config
        rank_drop = input_data.current_sector_rank - input_data.prev_sector_rank
        if rank_drop < cfg.leader_loss_rank_drop_min:
            return None
        confidence = min(100.0, 60.0 + rank_drop * 8.0)
        return SellSignal(
            point_type=SellPointType.LEADER_LOSS.value,
            confidence=round(confidence, 2),
            reference_price=input_data.current_price,
            reason=f"板块排名从第{input_data.prev_sector_rank}降至第{input_data.current_sector_rank}",
        )

    def _check_strong_divergence_sell(self, input_data: IntradayBuySellInput) -> SellSignal | None:
        """强分歧止盈：多次开板。"""
        cfg = self._config
        if input_data.consecutive_limit_ups == 0:
            return None
        if input_data.open_board_count < cfg.strong_divergence_open_count:
            return None
        confidence = min(100.0, 65.0 + input_data.open_board_count * 10.0)
        return SellSignal(
            point_type=SellPointType.STRONG_DIVERGENCE.value,
            confidence=round(confidence, 2),
            reference_price=input_data.current_price,
            reason=f"连板{input_data.consecutive_limit_ups}板开板{input_data.open_board_count}次=强分歧",
        )

    # ------------------------------------------------------------------
    # 维度3: 3重确认
    # ------------------------------------------------------------------

    def check_confirmations(self, input_data: IntradayBuySellInput) -> list[ConfirmationResult]:
        """3重确认：大盘环境 + 板块强度 + 资金流向。"""
        cfg = self._config
        results: list[ConfirmationResult] = []

        # 1. 大盘环境确认
        market_passed = input_data.market_sentiment_score >= cfg.market_sentiment_min
        results.append(
            ConfirmationResult(
                confirmation_type=ConfirmationType.MARKET_ENVIRONMENT.value,
                passed=market_passed,
                actual_value=input_data.market_sentiment_score,
                threshold=cfg.market_sentiment_min,
                reason=f"大盘情绪{input_data.market_sentiment_score:.0f}{'>=' if market_passed else '<'}阈值{cfg.market_sentiment_min}",
            )
        )

        # 2. 板块强度确认
        sector_passed = input_data.sector_strength_score >= cfg.sector_strength_min
        results.append(
            ConfirmationResult(
                confirmation_type=ConfirmationType.SECTOR_STRENGTH.value,
                passed=sector_passed,
                actual_value=input_data.sector_strength_score,
                threshold=cfg.sector_strength_min,
                reason=f"板块强度{input_data.sector_strength_score:.0f}{'>=' if sector_passed else '<'}阈值{cfg.sector_strength_min}",
            )
        )

        # 3. 资金流向确认
        capital_passed = input_data.capital_flow_inflow > cfg.capital_inflow_min
        results.append(
            ConfirmationResult(
                confirmation_type=ConfirmationType.CAPITAL_FLOW.value,
                passed=capital_passed,
                actual_value=input_data.capital_flow_inflow,
                threshold=cfg.capital_inflow_min,
                reason=f"资金净流入{input_data.capital_flow_inflow:.0f}万{'>' if capital_passed else '<='}阈值{cfg.capital_inflow_min}",
            )
        )

        return results

    # ------------------------------------------------------------------
    # 综合建议
    # ------------------------------------------------------------------

    def _make_recommendation(
        self,
        buy_signals: list[BuySignal],
        sell_signals: list[SellSignal],
        all_confirmations_passed: bool,
    ) -> tuple[str, float]:
        """生成综合建议: buy/sell/hold/wait。"""
        buy_conf = max((s.confidence for s in buy_signals), default=0.0)
        sell_conf = max((s.confidence for s in sell_signals), default=0.0)

        # 卖出信号优先（风控优先）
        if sell_conf >= 60.0 and sell_conf >= buy_conf:
            return "sell", round(sell_conf, 2)

        # 买入信号 + 确认全过
        if buy_signals and all_confirmations_passed and buy_conf >= 50.0:
            return "buy", round(buy_conf, 2)

        # 有买入信号但确认未过 → 等待
        if buy_signals and not all_confirmations_passed:
            return "wait", round(buy_conf * 0.5, 2)

        # 无信号 → 观望
        return "hold", 0.0

    # ------------------------------------------------------------------
    # 辅助
    # ------------------------------------------------------------------

    def _validate_input(self, data: IntradayBuySellInput) -> bool:
        if not data.symbol:
            return False
        if data.current_price < 0:
            return False
        return True

    def _degraded_result(self, symbol: str, reason: str) -> IntradayBuySellResult:
        return IntradayBuySellResult(
            symbol=symbol,
            recommendation="wait",
            overall_confidence=0.0,
            is_degraded=True,
            audit_trail=[{"dimension": "degraded", "reason": reason}],
        )


__all__ = [
    "BuyPointType",
    "BuySignal",
    "ConfirmationResult",
    "ConfirmationType",
    "IntradayBuySellAnalyzer",
    "IntradayBuySellConfig",
    "IntradayBuySellInput",
    "IntradayBuySellResult",
    "SellPointType",
    "SellSignal",
]
