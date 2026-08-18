# [BLUEPRINT] MOD-PA-006 | docs/03_modules/_domain_pf_alloc/batched_position_builder/blueprint.md
# [MODULE] zephyr.pf_alloc.batched_position_builder
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] zephyr.position.core.firm_risk_aggregator(FirmTargetPortfolio); zephyr.compliance.discipline_prohibition_checker
# [CONSUMERS] 40_execution_broker(订单执行); 42_sell_flow(突破失败降级联动)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 批次比例和=1.0; 首仓比例∈[0.30,1.0]; 放行需2/3条件; 限价单为主市价仅应急; 不读市场态(只消费budget数字); 每批下单前必过 BM-BUY-08 纪律闸(41 §2.3 硬约束不得绕过)
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] gate_batch_order 透传 DisciplineGuardError（闸未接线 Fail-Closed）；build_plan/clip_to_available_capital 不抛领域异常（资金不足以 _degrade_reason 降级标记返回，41 §3.6）。2026-08-17 勘正：移除幻影声明 BatchPlanError(ZA-PA-0006)/InsufficientCapitalError(ZA-PA-0007)——类从未实例化且 ZA-PA-0007 与 MOD-PA-007 AllocationError 撞号（#ARCH-ERRCODE-001）
# [TESTS] tests/pf_alloc/test_batched_position_builder.py
# [A_module] module_id=MOD-PA-006 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


BatchedPositionBuilder — 分批建仓引擎 (MOD-PA-006)

BM-BUY-04 分批建仓核心模块。消费 31 号产出的 FirmTargetPortfolio，
把目标权重拆成"什么时候下多少单"——分批节奏、时序、价格锚定、资金协同。

核心设计（41_buy_flow §3.1-§3.6）：
    - 置信度驱动 2 批（C-031 ≥ 阈值→激进 1 批 / < 阈值→分批 2 批）
    - 尾盘集中执行（14:50-14:57 主窗口 + 14:57-15:00 收盘竞价兜底）
    - 限价锚定（突破略低/回踩略高/兜底 min(目标价, VWAP)）
    - 资金不足 pro-rata 削减（保持相对排序）
    - 多标的排序（流动性差+高置信度优先）

不做什么：不重算仓位（归 31 号）/ 不读市场态（归 G15）/
         不执行卖出（归 42 号）/ 不做 TWAP/VWAP 拆单（MVP 不做，§5.2 阶段 4）

依据: 41_buy_flow §3.2-§3.6 + 31_position_sizing §2.6
SSoT: depgraph MOD-PA-006
Version: 1.1.0（2026-08-15 AI-ASM-001 装配批：BM-BUY-08 纪律闸 gate_batch_order 接线，43 号 §4.3）

# [ALGO_FLOW]
# 输入: FirmTargetPortfolio(holdings={symbol: weight}), confidence_scores, liquidity_scores, available_cash, total_account_value
# 特征: C-031 置信度, 板块回踩质量 A/B/C, 流动性评分(近20日日均成交额), 当日VWAP
# 算法: compute_batch_split(置信度→批次比例) → clip_to_available_capital(pro-rata削减) → rank_buy_orders(多标的排序)
#       → schedule_buy_orders(时序调度) → compute_anchor_price(限价锚定) → detect_breakout_failure(突破失败降级)
# 输出: BatchedEntryPlan(batches=[Batch]), 排序后标的列表, 锚定价格, 降级信号

"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import date, datetime, time
from typing import Any, Final, Protocol

from zephyr.compliance.discipline_prohibition_checker import (
    DisciplineAction,
    DisciplineContext,
    DisciplineGuard,
    DisciplineGuardError,
    DisciplineVerdict,
    KillSwitchLite,
    OrderRequest,
)

_logger = logging.getLogger(__name__)

# ── 持仓对象 Protocol（GATE-ANY-ABUSE 修复：裸 Any → 结构化类型）──


class _PositionLike(Protocol):
    """持仓对象最小契约：入场价 + 收盘价序列 + 最低价序列。"""

    @property
    def entry_price(self) -> float: ...
    @property
    def close_prices(self) -> list[float]: ...
    @property
    def low_prices(self) -> list[float]: ...


# ── 常量（参数来源：41_buy_flow §3.2.1/§3.4/§3.5）──

# C-031 置信度→激进阈值（按策略类型差异化，待 G04 校准）
AGGRESSIVE_THRESHOLD: Final = {
    "daban": 0.75,
    "multifactor": 0.65,
    "event": 0.70,
}
DEFAULT_THRESHOLD = 0.70

# 板块回踩质量 A/B/C → 置信度调节（22_sector_rotation §3.1②，v1.4.0 集成）
QUALITY_ADJUSTMENT: Final = {
    "A": 0.1,
    "B": 0.0,
    "C": -0.1,
}

# 执行窗口（41 §3.4，对齐上交所 2026 修订规则）
WINDOW_PLACE_LIMIT_START = time(14, 50)
WINDOW_PLACE_LIMIT_END = time(14, 55)
WINDOW_AMEND_END = time(14, 57)
WINDOW_CLOSING_AUCTION_END = time(15, 0)
WINDOW_AFTER_HOURS_START = time(15, 5)
WINDOW_AFTER_HOURS_END = time(15, 30)

# 突破失败检测参数（41 §3.3）
DEFAULT_LOOKBACK_DAYS = 10
DEFAULT_CONFIRM_BARS = 2


# ── 数据契约（41 §3.2.3）──


@dataclass(frozen=True)
class Batch:
    """分批建仓单批次。

    依据: 41_buy_flow §3.2.3 输出契约。
    """

    batch_id: int                       # 1=首仓, 2=确认仓
    weight_fraction: float              # 占 total_weight 的比例（和=1.0）
    trigger_conditions: list[str]       # 2/3 条件（41 §3.2.2）
    status: str = "PENDING"             # PENDING / FILLED / DEGRADED / CANCELLED


@dataclass(frozen=True)
class BatchedEntryPlan:
    """分批建仓计划（41 §3.2.3 输出契约）。

    消费 FirmTargetPortfolio 的目标权重，产出按时序排列的批次列表。
    """

    symbol: str
    total_weight: float                 # 来自 FirmTargetPortfolio（31 产出）
    batches: list[Batch]                # 按时序排列
    confidence_tier: str                # AGGRESSIVE / SCALED（C-031 驱动）
    degrade_reason: str | None = None   # A/B/C 未就绪等降级标记


# ── 核心算法（41 §3.2.1/§3.3/§3.4/§3.5/§3.6）──


def compute_batch_split(
    confidence_score_c031: float,
    strategy_type: str,
    sector_quality: str | None = None,
) -> dict[str, Any]:
    """C-031 置信度→首仓比例映射（41 §3.2.1，MVP 2 批/激进 1 批）。

    Args:
        confidence_score_c031: C-031 置信度评分，范围 [0, 1]。
        strategy_type: 策略类型（"daban"/"multifactor"/"event"），决定激进阈值。
        sector_quality: 板块回踩质量 A/B/C（22号 §3.1②，22号 active 后注入）。
            A→置信度+0.1（浅回踩38.2-50%+缩量+板块强≥70，激进建仓倾向）
            B→置信度±0.0（深回踩50-61.8%+混合量能+板块中40-70，中性）
            C→置信度-0.1（破位>61.8%+放量+板块弱<40，分批或放弃倾向）
            None→不调整（22号未就绪降级，MVP 兼容，与§4.2 过度工程审查一致）

    Returns:
        dict: {mode, batches, first_pct, confidence_source, sector_quality, adjusted_confidence}

    依据: 41_buy_flow §3.2.1 C-031 置信度→批次比例映射算法
    """
    # A/B/C 板块回踩质量调节置信度（22号 v1.8.0 active 后启用，v1.4.0 集成）
    if confidence_score_c031 != confidence_score_c031:  # NaN 自检
        confidence_score_c031 = 0.0
    quality_adjustment = QUALITY_ADJUSTMENT.get(sector_quality, 0.0)
    adjusted_confidence = min(max(confidence_score_c031 + quality_adjustment, 0.0), 1.0)

    # C-031 置信度范围 [0, 1]，阈值按策略类型差异化
    threshold = AGGRESSIVE_THRESHOLD.get(strategy_type, DEFAULT_THRESHOLD)

    if adjusted_confidence >= threshold:
        # 高置信度→激进建仓，首仓 70-100%，实质 1 批
        first_pct = min(0.70 + (adjusted_confidence - threshold) * 1.0, 1.0)
        return {
            "mode": "AGGRESSIVE",
            "batches": 1,
            "first_pct": first_pct,
            "confidence_source": confidence_score_c031,
            "sector_quality": sector_quality,
            "adjusted_confidence": adjusted_confidence,
        }
    else:
        # 低置信度→分批建仓，首仓 30-50%
        first_pct = 0.30 + (adjusted_confidence / threshold) * 0.20
        return {
            "mode": "SCALED",
            "batches": 2,
            "first_pct": first_pct,
            "confidence_source": confidence_score_c031,
            "sector_quality": sector_quality,
            "adjusted_confidence": adjusted_confidence,
        }


def detect_breakout_failure(
    position: _PositionLike,
    lookback_days: int = DEFAULT_LOOKBACK_DAYS,
    confirm_bars: int = DEFAULT_CONFIRM_BARS,
) -> tuple[str, str, str] | None:
    """突破失败检测：收盘价跌破首仓入场价，且连续 confirm_bars 根 K 线确认（41 §3.3）。

    Args:
        position: 持仓对象，须有 entry_price / low_prices / close_prices 属性。
        lookback_days: 前低定义回看天数（默认 10 日，待 G04 校准）。
        confirm_bars: 连续确认 K 线根数（默认 2 根，防日内假跌破）。

    Returns:
        None: 未触发降级。
        tuple: (降级类型, 动作, 联动)，如 ("BREAKOUT_FAILED", "暂停确认仓", "→ BM-SELL-01 止损评估")。

    依据: 41_buy_flow §3.3 突破失败检测算法
    """
    # 前低定义：首仓入场前 lookback_days 日最低价
    prior_low = min(position.low_prices[-lookback_days:])
    # 连续 confirm_bars 根确认（防日内假跌破）
    recent_closes = position.close_prices[-confirm_bars:]
    # 支撑破位（更严重）：收盘价 < 前低 → 先检查（收盘 < 前低必然也 < 入场价）
    if all(c < prior_low for c in recent_closes):
        return ("SUPPORT_BROKEN", "暂停全部后续批次", "→ BM-SELL-04-B 止损卖出")
    # 突破失败：收盘价 < 入场价（但 ≥ 前低）
    if all(c < position.entry_price for c in recent_closes):
        return ("BREAKOUT_FAILED", "暂停确认仓", "→ BM-SELL-01 止损评估")
    return None


def schedule_buy_orders(
    batched_plan: BatchedEntryPlan,
    current_time: time,
) -> tuple[str, str]:
    """买入时序调度：14:50-14:55 挂单→14:55-14:57 检查→14:57 收盘竞价补单（41 §3.4）。

    合规基线：上交所交易规则 2026 修订 §2.4.2——
        9:15-9:25 开盘集合竞价 / 9:30-11:30、13:00-14:57 连续竞价 /
        14:57-15:00 收盘集合竞价（不可撤单）/ 15:05-15:30 盘后固定价格交易。

    Args:
        batched_plan: 分批建仓计划（本函数只读取不修改）。
        current_time: 当前时间。

    Returns:
        tuple: (指令, 说明)，如 ("PLACE_LIMIT", "挂限价单，锚 VWAP/支撑位")。

    依据: 41_buy_flow §3.4 执行时序算法
    """
    if current_time < WINDOW_PLACE_LIMIT_START:
        return ("WAIT", "未到尾盘窗口，盘前只生成信号不下单")
    if WINDOW_PLACE_LIMIT_START <= current_time < WINDOW_PLACE_LIMIT_END:
        return ("PLACE_LIMIT", "挂限价单，锚 VWAP/支撑位")
    if WINDOW_PLACE_LIMIT_END <= current_time < WINDOW_AMEND_END:
        return ("CHECK_AND_AMEND", "未成交单可撤改挂，防 14:57 后无法撤单")
    if WINDOW_AMEND_END <= current_time < WINDOW_CLOSING_AUCTION_END:
        return ("CLOSING_AUCTION_ONLY", "收盘竞价段不可撤单，仅补未成交兜底单")
    return ("AFTER_HOURS", "15:05-15:30 盘后固定价格交易仅人工大额，自动策略不参与")


def compute_anchor_price(
    symbol: str,
    buy_type: str,
    level_price: float,
    intraday_bars: list[Any],
    current_time: time,
) -> float:
    """买入限价锚定价格计算（41 §3.5，突破/回踩/兜底三档）。

    VWAP 锚定：当日 VWAP = Σ(分钟成交价 × 分钟成交量) / Σ(分钟成交量)。
    14:50 时点用 9:30-14:50 的累计 VWAP 作锚，收盘竞价单锚全天 VWAP 预测值。

    Args:
        symbol: 标的代码。
        buy_type: "BREAKOUT"（突破买入）/ "PULLBACK"（回踩买入）/ 其他（通用兜底）。
        level_price: 技术位价格（压力位/支撑位/目标价）。
        intraday_bars: 当日分钟 K 线列表，须有 close / volume 属性。
        current_time: 当前时间。

    Returns:
        float: 锚定限价。

    依据: 41_buy_flow §3.5 VWAP 锚定计算 + 价格锚定算法
    """
    # 当日累计 VWAP（9:30 至 current_time）
    cum_value = sum(bar.close * bar.volume for bar in intraday_bars)
    cum_volume = sum(bar.volume for bar in intraday_bars)
    vwap = cum_value / cum_volume if cum_volume > 0 else level_price

    if buy_type == "BREAKOUT":
        # 突破买入：锚压力位，略低 0.5% 防追高（确定性偏移——2026-08-17 裁定：
        # 原 random.uniform(0.99,1.00) 非确定性破坏回测=实盘一致性，取区间中点）
        return level_price * 0.995
    if buy_type == "PULLBACK":
        # 回踩买入：锚支撑位，略高 0.5% 确保成交（同上，确定性偏移）
        return level_price * 1.005
    # 通用兜底：min(目标价, 当日 VWAP)，避免被动追涨
    return min(level_price, vwap)


def clip_to_available_capital(
    target_holdings: dict[str, float],
    available_cash: float,
    total_account_value: float,
) -> dict[str, float]:
    """资金不足时按权重 pro-rata 削减（41 §3.6，保持相对排序）。

    实盘中账户可用资金可能因前日卖出未到账/冻结/手续费占用而
    小于 FirmTargetPortfolio 的目标权重和。本函数做兜底削减，
    与 31 §2.5.2 总仓位裁剪一致——按比例削保持各标的相对权重不变。

    Args:
        target_holdings: 目标持仓权重 {symbol: weight}，含 "CASH" 键。
        available_cash: 可用资金（T+1 口径）。
        total_account_value: 账户总值。

    Returns:
        dict: 削减后持仓权重（含 "CASH" 键和 "_degrade_reason" 标记）。

    依据: 41_buy_flow §3.6 资金不足 pro-rata 削减算法
    """
    if not math.isfinite(available_cash) or available_cash < 0:
        _logger.warning("available_cash=%s 非法（负/NaN/Inf）——按零资金降级", available_cash)
        available_cash = 0.0
    target_invest = sum(w for s, w in target_holdings.items() if s != "CASH") * total_account_value
    if target_invest <= available_cash:
        return target_holdings  # 资金充足，原样执行
    # 资金不足：按比例削减非 CASH 权重，CASH 对应增加
    scale = available_cash / target_invest
    clipped = {s: (w * scale if s != "CASH" else w) for s, w in target_holdings.items()}
    clipped["CASH"] = 1.0 - sum(w for s, w in clipped.items() if s != "CASH")
    clipped["_degrade_reason"] = (
        f"available_cash={available_cash} < target_invest={target_invest}, scale={scale:.3f}"
    )
    return clipped


def rank_buy_orders(
    target_holdings: dict[str, float],
    confidence_scores: dict[str, float],
    liquidity_scores: dict[str, float],
) -> list[str]:
    """多标的下单排序：流动性差+高置信度优先（41 §3.6）。

    MVP 尾盘 14:50-14:57 窗口集中下单多标的，下单顺序影响成交质量——
    流动性差的标的先挂（防尾盘挂单后无人接单），高置信度标的先挂（防错过窗口）。

    排序键（三级）：
        1. 流动性评分升序（流动性差→成交量小→先挂，防尾盘无对手盘）
        2. 置信度降序（高置信度先挂，防错过窗口）
        3. 权重降序（大仓先挂，资金占用优先确认）

    Args:
        target_holdings: 目标持仓权重 {symbol: weight}，含 "CASH" 键。
        confidence_scores: C-031 置信度评分 {symbol: score}。
        liquidity_scores: 流动性评分 {symbol: score}（近 20 日日均成交额代理）。

    Returns:
        list[str]: 排序后标的代码列表（不含 CASH）。

    依据: 41_buy_flow §3.6 多标的下单排序算法
    """
    symbols = [
        s
        for s in target_holdings
        if s != "CASH" and not s.startswith("_")  # 排除 "_degrade_reason" 等元数据键（clip_to_available_capital 产出可含，防 KeyError）
    ]
    return sorted(
        symbols,
        key=lambda s: (
            liquidity_scores[s],           # 1. 流动性升序（差→先挂）
            -confidence_scores[s],         # 2. 置信度降序（高→先挂）
            -target_holdings[s],           # 3. 权重降序（大→先挂）
        ),
    )


# ── 编排入口 ──


class BatchedPositionBuilder:
    """分批建仓引擎（MOD-PA-006）。

    消费 FirmTargetPortfolio → 分批方案 → 时序调度 → 限价锚定 → 产出订单计划。
    每批下单前须过 BM-BUY-08 纪律闸（追高/补仓/骄傲/报复四项严禁检测）——
    41 §2.3 硬约束"buy_flow 不得绕过"，由 ``gate_batch_order`` 承载
    （2026-08-15 AI-ASM-001 装配批接线，43_compliance_discipline §4.3）。

    Args:
        discipline_guard: 四项严禁检测引擎（MOD-CMP-002）。None=未接线，
            此时调用 gate_batch_order 抛 DisciplineGuardError（Fail-Closed：
            闸不可用即拒，41 §2.3 不得绕过）。
        kill_switch: KillSwitchLite 策略级熔断（43 号 §4.3）；None=不检查熔断。
    """

    def __init__(
        self,
        discipline_guard: DisciplineGuard | None = None,
        kill_switch: KillSwitchLite | None = None,
    ) -> None:
        """初始化分批建仓引擎。"""
        self._discipline_guard = discipline_guard
        self._kill_switch = kill_switch

    def gate_batch_order(
        self,
        order: OrderRequest,
        ctx: DisciplineContext,
        *,
        today: date | None = None,
    ) -> DisciplineVerdict:
        """每批下单前过 BM-BUY-08 纪律闸（41 §2.3/§3.1：每批重新过闸防变相追高）。

        调用方契约：每个批次的订单提交执行层（40 号）前必须调用本方法；
        返回 HARD_BLOCK → 取消该批及后续批次并记录违规（41 §3.3 降级表）。

        Args:
            order: 本批待下订单（最小契约）。
            ctx: 纪律检测上下文（信号参考价/持仓盈亏/连续盈亏/当日盈亏/基线）。
            today: 交易日（KillSwitchLite 熔断判定）；None=当日。

        Returns:
            DisciplineVerdict：PASS / WARNING（骄傲，不阻断）/ HARD_BLOCK。

        Raises:
            DisciplineGuardError: 纪律闸未注入（Fail-Closed：闸不可用即拒）。
        """
        if self._discipline_guard is None:
            raise DisciplineGuardError(
                "BM-BUY-08 纪律闸未接线（discipline_guard=None）——41 §2.3 "
                "硬约束买入下单前必过四项严禁检测，buy_flow 不得绕过，Fail-Closed 拒单"
            )
        if self._kill_switch is not None and self._kill_switch.is_blocked(
            order.strategy_id, today or date.today()
        ):
            return DisciplineVerdict(
                behavior=None,
                action=DisciplineAction.HARD_BLOCK,
                detail=f"KillSwitchLite 熔断：策略 {order.strategy_id} 当日禁止新开仓（43 号 §4.3）",
                kill_switch_triggered=True,
            )
        return self._discipline_guard.check(order, ctx)

    def build_plan(
        self,
        symbol: str,
        total_weight: float,
        confidence_score_c031: float,
        strategy_type: str,
        sector_quality: str | None = None,
    ) -> BatchedEntryPlan:
        """构建分批建仓计划。

        Args:
            symbol: 标的代码。
            total_weight: 目标权重（来自 FirmTargetPortfolio）。
            confidence_score_c031: C-031 置信度评分。
            strategy_type: 策略类型。
            sector_quality: 板块回踩质量 A/B/C（None=降级）。

        Returns:
            BatchedEntryPlan: 分批建仓计划。
        """
        split = compute_batch_split(confidence_score_c031, strategy_type, sector_quality)
        degrade_reason = None
        if sector_quality is None:
            degrade_reason = "sector_quality=None（22号未就绪降级，纯C-031驱动）"

        if split["mode"] == "AGGRESSIVE":
            batches = [
                Batch(batch_id=1, weight_fraction=split["first_pct"], trigger_conditions=[]),
            ]
        else:
            batches = [
                Batch(
                    batch_id=1,
                    weight_fraction=split["first_pct"],
                    trigger_conditions=[],
                ),
                Batch(
                    batch_id=2,
                    weight_fraction=1.0 - split["first_pct"],
                    trigger_conditions=[
                        "① 调整周期到位（进度≥80%）或距首仓≥1交易日",
                        "② 二次回落不破首仓入场价",
                        "③ 缩量企稳（量比<1）",
                    ],
                ),
            ]

        return BatchedEntryPlan(
            symbol=symbol,
            total_weight=total_weight,
            batches=batches,
            confidence_tier=split["mode"],
            degrade_reason=degrade_reason,
        )

    def check_batch2_release(
        self,
        plan: BatchedEntryPlan,
        position: _PositionLike,
        volume_ratio: float,
        days_since_first_batch: int,
    ) -> bool:
        """检查确认仓放行条件（41 §3.2.2，2/3 条件）。

        Args:
            plan: 分批建仓计划。
            position: 持仓对象（须有 entry_price / close_prices）。
            volume_ratio: 量比（BM-SEL-02 产出）。
            days_since_first_batch: 距首仓交易日数。

        Returns:
            bool: 是否放行确认仓。
        """
        if len(plan.batches) < 2:
            return False  # 激进模式无确认仓

        conditions_met = 0
        # ① 调整周期到位（降级：距首仓≥1交易日）
        if days_since_first_batch >= 1:
            conditions_met += 1
        # ② 二次回落不破首仓入场价（证据不足不计票——Fail-Closed）
        recent_closes = position.close_prices[-2:]
        if len(recent_closes) >= 2 and all(c >= position.entry_price for c in recent_closes):
            conditions_met += 1
        # ③ 缩量企稳（量比<1）
        if volume_ratio < 1.0:
            conditions_met += 1

        return conditions_met >= 2

    def check_degrade(
        self,
        position: _PositionLike,
        lookback_days: int = DEFAULT_LOOKBACK_DAYS,
        confirm_bars: int = DEFAULT_CONFIRM_BARS,
    ) -> tuple[str, str, str] | None:
        """检查突破失败降级条件（41 §3.3）。

        Args:
            position: 持仓对象。
            lookback_days: 前低回看天数。
            confirm_bars: 连续确认 K 线根数。

        Returns:
            None: 未触发降级。
            tuple: (降级类型, 动作, 联动)。
        """
        return detect_breakout_failure(position, lookback_days, confirm_bars)
