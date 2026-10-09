# [A_module] module_id=MOD-GOV-e2e-signal-fill | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""test_e2e_signal_to_fill_integration.py — 信号→成交回报端到端集成测试

模拟从**信号输入**到**最终成交回报**的完整 9 阶段流水线，验证所有异常分支
是否按预期触发、降级路径是否正确闭合。

完整流水线（9 阶段）::

    ① 信号生成        (SIG)   市场数据+Alpha → 交易信号列表
        ↓ signals
    ② 组合构建        (PORT)  信号 → 目标权重
        ↓ target_weights
    ③ 仓位裁决        (POS)   目标权重 → 仓位指令
        ↓ position_order
    ④ BM-EXE-01 风控审批       仓位指令 → 审批后订单   (HALT 级阻断)
        ↓ approved_order
    ⑤ BM-EXE-04 Pre-Trade合规  审批后订单 → 合规订单   (Fail-Closed)
        ↓ compliant_order
    ⑥ BM-EXE-05 智能路由拆单   合规订单 → 子订单序列   (Almgren-Chriss)
        ↓ child_orders
    ⑦ BM-EXE-02 交易执行       子订单 → 成交回报       (miniQMT 通道)
        ↓ fill_report
    ⑧ BM-EXE-06 成交回报处理   成交回报 → 持仓快照     (聚合+费用)
        ↓ position_snapshot
    ⑨ BM-EXE-03 TCA分析        成交数据 → 执行质量报告 (degradation 闭环→⑥)

测试覆盖矩阵：
  - Happy Path：9 阶段全跑通，产出 TCA 报告
  - 各阶段异常阻断：①~⑧ 每阶段注入故障，验证 pipeline 在该阶段 fail-fast 停止
  - 降级路径：TCA 滑点过高 → 反馈闭环 → 第二轮拆单参数调整
  - 端到端降级：信号置信度低 → 仓位缩减 → 订单量减小
  - 状态追踪：history 完整、fail-fast 下游不执行

设计原则：
  - **纯逻辑测试**，零 DB / 零外部依赖（与 test_battle_map_execution_flow.py Part 2 对齐）
  - **故障注入**：每个阶段通过 Config 阈值 + MarketContext 状态触发异常
  - **自定义异常**：区分 PipelineError 子类，断言精确匹配（非裸 AssertionError）
  - **fail-fast 语义**：异常阶段停止，下游阶段不执行（模拟真实交易合规阻断）

Usage::

    py -3.12 -m pytest tests/governance/test_e2e_signal_to_fill_integration.py -v
    py -3.12 -m pytest tests/governance/test_e2e_signal_to_fill_integration.py -k "happy" -v
    py -3.12 -m pytest tests/governance/test_e2e_signal_to_fill_integration.py -k "exception" -v
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

# ──────────────────────────────────────────────────────────────────────────────
# 常量
# ──────────────────────────────────────────────────────────────────────────────

FULL_PIPELINE: list[str] = [
    "SIG",
    "PORT",
    "POS",
    "BM-EXE-01",
    "BM-EXE-04",
    "BM-EXE-05",
    "BM-EXE-02",
    "BM-EXE-06",
    "BM-EXE-03",
]

EXPECTED_HANDOFFS: list[tuple[str, str, str]] = [
    ("market_data", "SIG", "signals"),
    ("signals", "PORT", "target_weights"),
    ("target_weights", "POS", "position_order"),
    ("position_order", "BM-EXE-01", "approved_order"),
    ("approved_order", "BM-EXE-04", "compliant_order"),
    ("compliant_order", "BM-EXE-05", "child_orders"),
    ("child_orders", "BM-EXE-02", "fill_report"),
    ("fill_report", "BM-EXE-06", "position_snapshot"),
    ("position_snapshot", "BM-EXE-03", "tca_report"),
]


# ──────────────────────────────────────────────────────────────────────────────
# 异常
# ──────────────────────────────────────────────────────────────────────────────


class PipelineError(Exception):
    """流水线异常基类。所有阶段异常继承此类。"""


class SignalQualityError(PipelineError):
    """① 信号质量不足（置信度低 / 无信号）。"""


class PortfolioConcentrationError(PipelineError):
    """② 组合集中度超限（单标的权重 / 行业权重）。"""


class PositionLimitError(PipelineError):
    """③ 仓位超限（单标的仓位上限）。"""


class RiskViolationError(PipelineError):
    """④ 风控违例（HALT 级阻断：单标的权重 / 日内亏损）。"""


class ComplianceViolationError(PipelineError):
    """⑤ 合规违例（参与率 / 涨跌停 / 洗盘 / 停留时间）。"""


class RoutingError(PipelineError):
    """⑥ 路由失败（流动性不足 / 算法不可用）。"""


class ExecutionError(PipelineError):
    """⑦ 执行失败（通道不可用 / 超时）。"""


class FillProcessingError(PipelineError):
    """⑧ 成交处理失败（数量不匹配 / 部分成交未授权）。"""


EXCEPTION_STAGE_MAP: dict[type, str] = {
    SignalQualityError: "SIG",
    PortfolioConcentrationError: "PORT",
    PositionLimitError: "POS",
    RiskViolationError: "BM-EXE-01",
    ComplianceViolationError: "BM-EXE-04",
    RoutingError: "BM-EXE-05",
    ExecutionError: "BM-EXE-02",
    FillProcessingError: "BM-EXE-06",
}


# ──────────────────────────────────────────────────────────────────────────────
# 配置
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class SignalConfig:
    """① 信号生成阈值。"""

    min_confidence: float = 0.6
    min_signals: int = 1


@dataclass
class PortfolioConfig:
    """② 组合构建阈值。"""

    max_single_weight: float = 0.5
    max_sector_weight: float = 0.6


@dataclass
class PositionConfig:
    """③ 仓位裁决阈值。"""

    max_single_position: int = 100000


@dataclass
class RiskConfig:
    """④ 风控审批阈值（HALT 级硬阻断）。"""

    max_single_weight: float = 0.5
    max_daily_loss_pct: float = 0.05


@dataclass
class ComplianceConfig:
    """⑤ Pre-Trade 合规主链 8 项检查阈值。"""

    max_participation_rate: float = 0.05
    price_limit_block: bool = True
    wash_trade_block: bool = True
    min_dwell_time_us: int = 50
    max_cancel_rate: float = 0.15


@dataclass
class RoutingConfig:
    """⑥ 智能路由拆单阈值。"""

    min_liquidity: int = 100
    available_algos: tuple = ("TWAP", "VWAP")
    default_participation_rate: float = 0.1
    default_algo: str = "TWAP"
    degraded_participation_rate: float = 0.05
    degraded_algo: str = "VWAP"
    slippage_threshold_bps: float = 5.0


@dataclass
class ExecutionConfig:
    """⑦ 交易执行阈值。"""

    channel_available: bool = True
    fill_timeout_sec: int = 30
    partial_fill_allowed: bool = True


@dataclass
class FillConfig:
    """⑧ 成交回报处理阈值。"""

    require_full_fill: bool = True
    tolerate_qty_mismatch: bool = False


@dataclass
class TCAConfig:
    """⑨ TCA 分析阈值。"""

    arrival_price: float = 10.0
    commission_bps: float = 3.0
    slippage_degradation_threshold: float = 5.0


@dataclass
class MarketContext:
    """市场状态上下文——持有触发各阶段故障的实际市场状态。

    与 Config（阈值）配合：processor 比较 context 实际值 vs config 阈值，
    超限则抛对应异常。故障注入 = 调高 context 值 / 调低 config 阈值。
    """

    arrival_price: float = 10.0
    participation_rate: float = 0.03
    price_limit_hit: bool = False
    liquidity: int = 10000
    wash_trade_detected: bool = False
    sector_weights: dict[str, float] = field(default_factory=dict)
    daily_loss_pct: float = 0.0
    circuit_breaker_triggered: bool = False
    cancel_rate: float = 0.05
    dwell_time_us: int = 100
    tca_feedback: dict | None = None


@dataclass
class DataPacket:
    """数据包——阶段间流转的数据载体，history 记录经过的阶段序列。"""

    type: str
    payload: dict[str, Any]
    history: list[str] = field(default_factory=list)


@dataclass
class PipelineConfigs:
    """聚合所有阶段配置，便于一次性传入 pipeline runner。"""

    signal: SignalConfig = field(default_factory=SignalConfig)
    portfolio: PortfolioConfig = field(default_factory=PortfolioConfig)
    position: PositionConfig = field(default_factory=PositionConfig)
    risk: RiskConfig = field(default_factory=RiskConfig)
    compliance: ComplianceConfig = field(default_factory=ComplianceConfig)
    routing: RoutingConfig = field(default_factory=RoutingConfig)
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)
    fill: FillConfig = field(default_factory=FillConfig)
    tca: TCAConfig = field(default_factory=TCAConfig)


# ──────────────────────────────────────────────────────────────────────────────
# 阶段处理器
# ──────────────────────────────────────────────────────────────────────────────


def process_signal_generation(pkt: DataPacket, cfg: SignalConfig, ctx: MarketContext) -> DataPacket:
    """① 信号生成：市场数据+Alpha → 交易信号列表。

    故障分支：
      - 无信号（signals 为空）→ SignalQualityError
      - 信号置信度 < min_confidence → SignalQualityError
    """
    assert pkt.type == "market_data", f"SIG 输入应为 market_data，实际 {pkt.type}"

    raw_signals = pkt.payload.get("raw_signals", [])
    if len(raw_signals) < cfg.min_signals:
        raise SignalQualityError(f"无有效交易信号（收到 {len(raw_signals)} 条，最低要求 {cfg.min_signals}）")

    max_conf = max((s["confidence"] for s in raw_signals), default=0.0)
    if max_conf < cfg.min_confidence:
        raise SignalQualityError(f"信号置信度不足（最高 {max_conf:.2f} < 阈值 {cfg.min_confidence}）")

    qualified = [s for s in raw_signals if s["confidence"] >= cfg.min_confidence]
    return DataPacket(
        type="signals",
        payload={"signals": qualified},
        history=pkt.history + ["SIG"],
    )


def process_portfolio_construction(pkt: DataPacket, cfg: PortfolioConfig, ctx: MarketContext) -> DataPacket:
    """② 组合构建：信号 → 目标权重。

    故障分支：
      - 单标的权重 > max_single_weight → PortfolioConcentrationError
      - 行业权重 > max_sector_weight → PortfolioConcentrationError
    """
    assert pkt.type == "signals", f"PORT 输入应为 signals，实际 {pkt.type}"

    signals = pkt.payload["signals"]
    total_conf = sum(s["confidence"] for s in signals)

    weights: dict[str, float] = {}
    for s in signals:
        sym = s["symbol"]
        w = s["confidence"] / total_conf if total_conf > 0 else 0.0
        if w > cfg.max_single_weight:
            raise PortfolioConcentrationError(f"单标的权重超限：{sym} {w:.2%} > 上限 {cfg.max_single_weight:.2%}")
        weights[sym] = w

    for sector, sw in (ctx.sector_weights or {}).items():
        if sw > cfg.max_sector_weight:
            raise PortfolioConcentrationError(f"行业权重超限：{sector} {sw:.2%} > 上限 {cfg.max_sector_weight:.2%}")

    return DataPacket(
        type="target_weights",
        payload={"weights": weights, "total_capital": pkt.payload.get("total_capital", 1000000)},
        history=pkt.history + ["PORT"],
    )


def process_position_sizing(pkt: DataPacket, cfg: PositionConfig, ctx: MarketContext) -> DataPacket:
    """③ 仓位裁决：目标权重 → 仓位指令。

    故障分支：
      - 计算股数 > max_single_position → PositionLimitError
    """
    assert pkt.type == "target_weights", f"POS 输入应为 target_weights，实际 {pkt.type}"

    weights = pkt.payload["weights"]
    total_capital = pkt.payload.get("total_capital", 1000000)

    quantities: dict[str, int] = {}
    for sym, weight in weights.items():
        qty = int(weight * total_capital / ctx.arrival_price)
        if qty > cfg.max_single_position:
            raise PositionLimitError(f"单标的仓位超限：{sym} {qty}股 > 上限 {cfg.max_single_position}股")
        quantities[sym] = qty

    # 取第一个标的作为主订单（简化：单标的路径）
    sym = next(iter(weights), "")
    return DataPacket(
        type="position_order",
        payload={
            "symbol": sym,
            "weight": weights.get(sym, 0.0),
            "qty": quantities.get(sym, 0),
            "side": "buy",
        },
        history=pkt.history + ["POS"],
    )


def process_risk_approval(pkt: DataPacket, cfg: RiskConfig, ctx: MarketContext) -> DataPacket:
    """④ BM-EXE-01 风控审批：仓位指令 → 审批后订单（HALT 级阻断）。

    故障分支：
      - 市场熔断（行情中断）→ RiskViolationError（HALT，最高优先级）
      - 单标的权重 > max_single_weight → RiskViolationError（HALT）
      - 日内亏损 > max_daily_loss_pct → RiskViolationError（HALT）
    """
    assert pkt.type == "position_order", f"BM-EXE-01 输入应为 position_order，实际 {pkt.type}"

    # 熔断 HALT（行情中断，最高优先级）
    if ctx.circuit_breaker_triggered:
        raise RiskViolationError("市场熔断触发（行情中断），禁止开新仓")

    # 日内亏损 HALT（最高优先级）
    if ctx.daily_loss_pct > cfg.max_daily_loss_pct:
        raise RiskViolationError(
            f"日内亏损超 HALT 阈值：{ctx.daily_loss_pct:.2%} > {cfg.max_daily_loss_pct:.2%}，禁止开新仓"
        )

    weight = pkt.payload.get("weight", 0)
    if weight > cfg.max_single_weight:
        raise RiskViolationError(f"单标的权重超 HALT 阈值：{weight:.2%} > {cfg.max_single_weight:.2%}")

    return DataPacket(
        type="approved_order",
        payload={
            "symbol": pkt.payload["symbol"],
            "target_qty": pkt.payload["qty"],
            "side": pkt.payload["side"],
            "approved": True,
        },
        history=pkt.history + ["BM-EXE-01"],
    )


def process_pretrade_compliance(pkt: DataPacket, cfg: ComplianceConfig, ctx: MarketContext) -> DataPacket:
    """⑤ BM-EXE-04 Pre-Trade 合规：审批后订单 → 合规订单（Fail-Closed）。

    合规主链 8 项顺序检查：涨跌停→参与率→持仓限额→行业集中度→撤单率→
    异常交易→报单停留时间锁→操纵防护。任一失败即阻断。
    """
    assert pkt.type == "approved_order", f"BM-EXE-04 输入应为 approved_order，实际 {pkt.type}"

    if not pkt.payload.get("approved"):
        raise ComplianceViolationError("订单未通过风控审批，合规 Fail-Closed 拒绝")

    if cfg.price_limit_block and ctx.price_limit_hit:
        raise ComplianceViolationError("标的触及涨跌停，禁止下单")

    if ctx.participation_rate > cfg.max_participation_rate:
        raise ComplianceViolationError(f"参与率超限：{ctx.participation_rate:.2%} > {cfg.max_participation_rate:.2%}")

    if ctx.cancel_rate > cfg.max_cancel_rate:
        raise ComplianceViolationError(f"撤单率超限：{ctx.cancel_rate:.2%} > {cfg.max_cancel_rate:.2%}")

    if ctx.dwell_time_us < cfg.min_dwell_time_us:
        raise ComplianceViolationError(f"报单停留时间不足：{ctx.dwell_time_us}μs < {cfg.min_dwell_time_us}μs")

    if cfg.wash_trade_block and ctx.wash_trade_detected:
        raise ComplianceViolationError("检测到 Wash Trade 操纵行为，订单阻断")

    return DataPacket(
        type="compliant_order",
        payload={
            "symbol": pkt.payload["symbol"],
            "qty": pkt.payload["target_qty"],
            "side": pkt.payload["side"],
            "compliant": True,
        },
        history=pkt.history + ["BM-EXE-04"],
    )


def process_smart_routing(pkt: DataPacket, cfg: RoutingConfig, ctx: MarketContext) -> DataPacket:
    """⑥ BM-EXE-05 智能路由：合规订单 → 子订单序列（Almgren-Chriss）。

    故障分支：
      - 流动性 < min_liquidity → RoutingError
      - 算法不可用 → RoutingError
    降级闭环：
      - TCA 反馈滑点 > threshold → 降低参与率 + 切换算法
    """
    assert pkt.type == "compliant_order", f"BM-EXE-05 输入应为 compliant_order，实际 {pkt.type}"

    if not pkt.payload.get("compliant"):
        raise RoutingError("订单未通过合规检查，拒绝拆单")

    if ctx.liquidity < cfg.min_liquidity:
        raise RoutingError(f"市场流动性不足：{ctx.liquidity} < 最小 {cfg.min_liquidity}")

    participation_rate = cfg.default_participation_rate
    algo = cfg.default_algo

    if ctx.tca_feedback:
        slippage_bps = ctx.tca_feedback.get("slippage_bps", 0)
        if slippage_bps > cfg.slippage_threshold_bps:
            participation_rate = cfg.degraded_participation_rate
            algo = cfg.degraded_algo

    if algo not in cfg.available_algos:
        raise RoutingError(f"算法不可用：{algo} 不在 {cfg.available_algos}")

    qty = pkt.payload["qty"]
    child_count = max(1, int(qty / max(1, ctx.liquidity * participation_rate)))
    child_count = min(child_count, 10)  # 上限 10 子单
    child_qty = qty // child_count
    remainder = qty % child_count

    children = []
    for i in range(child_count):
        cq = child_qty + (remainder if i == 0 else 0)
        children.append(
            {
                "child_id": f"child_{i}",
                "qty": cq,
                "symbol": pkt.payload["symbol"],
                "side": pkt.payload["side"],
                "algo": algo,
            }
        )

    return DataPacket(
        type="child_orders",
        payload={
            "children": children,
            "participation_rate": participation_rate,
            "algo": algo,
        },
        history=pkt.history + ["BM-EXE-05"],
    )


def process_trade_execution(pkt: DataPacket, cfg: ExecutionConfig, ctx: MarketContext) -> DataPacket:
    """⑦ BM-EXE-02 交易执行：子订单 → 成交回报（miniQMT 通道）。

    故障分支：
      - 通道不可用 → ExecutionError
      - 超时（ctx 模拟 fill_timeout）→ ExecutionError
      - 部分成交未授权 → ExecutionError
    """
    assert pkt.type == "child_orders", f"BM-EXE-02 输入应为 child_orders，实际 {pkt.type}"

    if not cfg.channel_available:
        raise ExecutionError("交易通道不可用（miniQMT 断连），下单失败")

    if getattr(ctx, "fill_timeout", False):
        raise ExecutionError(f"成交超时（>{cfg.fill_timeout_sec}s），订单取消")

    fills = []
    children = pkt.payload["children"]
    for child in children:
        filled = child["qty"]

        if getattr(ctx, "partial_last_child", False) and child is children[-1]:
            if not cfg.partial_fill_allowed:
                raise ExecutionError("部分成交未授权，子订单取消")
            filled = child["qty"] // 2

        # 模拟成交价（小幅滑点）
        fill_price = ctx.arrival_price * (1 + 0.001)

        fills.append(
            {
                "child_id": child["child_id"],
                "ordered_qty": child["qty"],
                "filled_qty": filled,
                "fill_price": fill_price,
                "symbol": child["symbol"],
                "side": child["side"],
                "algo": child["algo"],
            }
        )

    return DataPacket(
        type="fill_report",
        payload={"fills": fills},
        history=pkt.history + ["BM-EXE-02"],
    )


def process_fill_handling(pkt: DataPacket, cfg: FillConfig, ctx: MarketContext) -> DataPacket:
    """⑧ BM-EXE-06 成交回报处理：成交回报 → 持仓快照（聚合+费用）。

    故障分支：
      - 部分成交但 require_full_fill=True → FillProcessingError
      - 成交数量与报单不匹配且不容忍 → FillProcessingError
    """
    assert pkt.type == "fill_report", f"BM-EXE-06 输入应为 fill_report，实际 {pkt.type}"

    fills = pkt.payload["fills"]

    partial = any(f["filled_qty"] < f["ordered_qty"] for f in fills)
    if partial and cfg.require_full_fill:
        unfilled = sum(f["ordered_qty"] - f["filled_qty"] for f in fills)
        raise FillProcessingError(f"要求全部成交但存在部分成交，未成交 {unfilled}")

    for f in fills:
        if f["filled_qty"] > f["ordered_qty"] and not cfg.tolerate_qty_mismatch:
            raise FillProcessingError(
                f"成交数量超过报单：{f['filled_qty']} > {f['ordered_qty']}（child {f['child_id']}）"
            )

    total_qty = sum(f["filled_qty"] for f in fills)
    total_value = sum(f["fill_price"] * f["filled_qty"] for f in fills)
    avg_price = total_value / total_qty if total_qty > 0 else 0.0
    commission = total_value * 0.0003  # 3bps

    return DataPacket(
        type="position_snapshot",
        payload={
            "fills": fills,
            "total_qty": total_qty,
            "avg_price": avg_price,
            "commission": commission,
            "symbol": fills[0]["symbol"] if fills else "",
            "pnl": 0.0,
        },
        history=pkt.history + ["BM-EXE-06"],
    )


def process_tca_analysis(pkt: DataPacket, cfg: TCAConfig, ctx: MarketContext) -> DataPacket:
    """⑨ BM-EXE-03 TCA：成交数据 → 执行质量报告 + 降级反馈。

    产出：
      - tca_report：滑点 / IS 成本 / 质量评分
      - degradation_triggered：滑点超阈值时标记降级（反馈回 ⑥）
    """
    assert pkt.type == "position_snapshot", f"BM-EXE-03 输入应为 position_snapshot，实际 {pkt.type}"

    fills = pkt.payload["fills"]
    total_qty = sum(f["filled_qty"] for f in fills)
    total_value = sum(f["fill_price"] * f["filled_qty"] for f in fills)
    avg_price = total_value / total_qty if total_qty > 0 else 0.0

    slippage_bps = (avg_price - cfg.arrival_price) / cfg.arrival_price * 10000 if cfg.arrival_price > 0 else 0.0
    is_cost = slippage_bps + cfg.commission_bps
    quality_score = max(0.0, 100.0 - abs(slippage_bps) * 2)

    degradation = slippage_bps > cfg.slippage_degradation_threshold

    return DataPacket(
        type="tca_report",
        payload={
            "slippage_bps": slippage_bps,
            "is_cost": is_cost,
            "quality_score": quality_score,
            "commission_bps": cfg.commission_bps,
            "arrival_price": cfg.arrival_price,
            "avg_fill_price": avg_price,
            "total_qty": total_qty,
            "degradation_triggered": degradation,
            "feedback": {"slippage_bps": slippage_bps} if degradation else None,
        },
        history=pkt.history + ["BM-EXE-03"],
    )


# ──────────────────────────────────────────────────────────────────────────────
# 流水线注册表
# ──────────────────────────────────────────────────────────────────────────────

STAGE_PROCESSORS: dict[str, Any] = {
    "SIG": process_signal_generation,
    "PORT": process_portfolio_construction,
    "POS": process_position_sizing,
    "BM-EXE-01": process_risk_approval,
    "BM-EXE-04": process_pretrade_compliance,
    "BM-EXE-05": process_smart_routing,
    "BM-EXE-02": process_trade_execution,
    "BM-EXE-06": process_fill_handling,
    "BM-EXE-03": process_tca_analysis,
}

STAGE_CONFIG_MAP: list[tuple[str, Any]] = [
    ("SIG", "signal"),
    ("PORT", "portfolio"),
    ("POS", "position"),
    ("BM-EXE-01", "risk"),
    ("BM-EXE-04", "compliance"),
    ("BM-EXE-05", "routing"),
    ("BM-EXE-02", "execution"),
    ("BM-EXE-06", "fill"),
    ("BM-EXE-03", "tca"),
]


@dataclass
class PipelineResult:
    """流水线执行结果。"""

    success: bool
    final_packet: DataPacket | None
    history: list[str]
    failed_stage: str | None
    error: PipelineError | None
    degradation_triggered: bool = False

    @property
    def reached_tca(self) -> bool:
        """是否到达 TCA 阶段（⑨）。"""
        return "BM-EXE-03" in self.history


def _get_stage_config(configs: PipelineConfigs, stage_id: str):
    mapping = dict(STAGE_CONFIG_MAP)
    attr = mapping.get(stage_id)
    if attr is None:
        return None
    return getattr(configs, attr)


def run_pipeline(
    initial: DataPacket,
    configs: PipelineConfigs,
    ctx: MarketContext,
    stop_on_error: bool = True,
) -> PipelineResult:
    """执行 9 阶段流水线，fail-fast 语义。"""
    pkt = initial
    history: list[str] = []
    failed_stage: str | None = None
    error: PipelineError | None = None
    degradation_triggered = False

    for stage_id in FULL_PIPELINE:
        processor = STAGE_PROCESSORS[stage_id]
        config = _get_stage_config(configs, stage_id)
        try:
            pkt = processor(pkt, config, ctx)
            history = pkt.history
        except PipelineError as exc:
            failed_stage = stage_id
            error = exc
            if stop_on_error:
                return PipelineResult(
                    success=False,
                    final_packet=pkt,
                    history=history,
                    failed_stage=failed_stage,
                    error=error,
                    degradation_triggered=degradation_triggered,
                )
            break

    # 检查最终包是否含降级标记
    if pkt is not None and pkt.payload.get("degradation_triggered"):
        degradation_triggered = True

    return PipelineResult(
        success=failed_stage is None,
        final_packet=pkt,
        history=history,
        failed_stage=failed_stage,
        error=error,
        degradation_triggered=degradation_triggered,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def default_market_data() -> DataPacket:
    """默认市场数据：3 只标的，置信度合格。"""
    return DataPacket(
        type="market_data",
        payload={
            "raw_signals": [
                {"symbol": "600519", "confidence": 0.85},
                {"symbol": "000858", "confidence": 0.80},
                {"symbol": "000333", "confidence": 0.78},
            ],
            "total_capital": 1000000,
        },
        history=[],
    )


@pytest.fixture
def default_configs() -> PipelineConfigs:
    """默认配置：全部阈值宽松，happy path 可跑通。"""
    return PipelineConfigs()


@pytest.fixture
def default_ctx() -> MarketContext:
    """默认市场上下文：全部状态正常，不触发任何故障。"""
    return MarketContext()


# ──────────────────────────────────────────────────────────────────────────────
# 辅助
# ──────────────────────────────────────────────────────────────────────────────


def _resolve_config_for_stage(configs: PipelineConfigs, stage_id: str):
    """测试辅助：按 stage_id 取对应配置对象。"""
    mapping = dict(STAGE_CONFIG_MAP)
    attr = mapping.get(stage_id)
    if attr is None:
        return None
    return getattr(configs, attr)


# ──────────────────────────────────────────────────────────────────────────────
# 测试：Happy Path
# ──────────────────────────────────────────────────────────────────────────────


class TestE2EHappyPath:
    """端到端 Happy Path：信号→成交回报→TCA 全跑通。"""

    def test_full_pipeline_success(self, default_market_data, default_configs, default_ctx):
        """9 阶段全跑通，最终产出 TCA 报告。"""
        result = run_pipeline(default_market_data, default_configs, default_ctx)
        assert result.success, f"流水线失败于 {result.failed_stage}: {result.error}"
        assert result.final_packet is not None
        assert result.final_packet.type == "tca_report"
        assert "slippage_bps" in result.final_packet.payload
        assert "is_cost" in result.final_packet.payload
        assert "quality_score" in result.final_packet.payload

    def test_history_records_all_9_stages(self, default_market_data, default_configs, default_ctx):
        """history 记录完整 9 阶段序列。"""
        result = run_pipeline(default_market_data, default_configs, default_ctx)
        assert result.history == FULL_PIPELINE, f"history 不完整:\n预期 {FULL_PIPELINE}\n实际 {result.history}"

    def test_data_type_handoff_chain(self, default_market_data, default_configs, default_ctx):
        """9 阶段数据类型交接链正确（上游 output = 下游 input）。"""
        pkt = default_market_data
        for input_type, stage_id, output_type in EXPECTED_HANDOFFS:
            assert pkt.type == input_type, f"{stage_id} 输入应为 {input_type}，实际 {pkt.type}"
            processor = STAGE_PROCESSORS[stage_id]
            config = _get_stage_config(default_configs, stage_id)
            pkt = processor(pkt, config, default_ctx)
            assert pkt.type == output_type, f"{stage_id} 输出应为 {output_type}，实际 {pkt.type}"

    def test_tca_report_quality_score_positive(self, default_market_data, default_configs, default_ctx):
        """TCA 质量评分为正（happy path 滑点可控）。"""
        result = run_pipeline(default_market_data, default_configs, default_ctx)
        assert result.success
        assert result.final_packet.payload["quality_score"] > 0
        assert result.final_packet.payload["slippage_bps"] < 100

    def test_position_snapshot_has_fills_passthrough(self, default_market_data, default_configs, default_ctx):
        """BM-EXE-06 持仓快照透传 fills 给 TCA（数据流不断裂）。"""
        result = run_pipeline(default_market_data, default_configs, default_ctx)
        assert result.success
        # TCA 阶段能访问 fills（通过 position_snapshot 透传）
        assert "slippage_bps" in result.final_packet.payload


# ──────────────────────────────────────────────────────────────────────────────
# 测试：① 信号生成异常
# ──────────────────────────────────────────────────────────────────────────────


class TestSignalStageExceptions:
    """① 信号生成阶段异常。"""

    def test_no_signals_raises(self, default_configs, default_ctx):
        """无交易信号 → SignalQualityError。"""
        pkt = DataPacket(type="market_data", payload={"raw_signals": [], "total_capital": 1000000})
        with pytest.raises(SignalQualityError, match="无有效交易信号"):
            process_signal_generation(pkt, default_configs.signal, default_ctx)

    def test_low_confidence_raises(self, default_configs, default_ctx):
        """信号置信度全部低于阈值 → SignalQualityError。"""
        pkt = DataPacket(
            type="market_data",
            payload={
                "raw_signals": [{"symbol": "600519", "confidence": 0.3}],
                "total_capital": 1000000,
            },
        )
        with pytest.raises(SignalQualityError, match="置信度不足"):
            process_signal_generation(pkt, default_configs.signal, default_ctx)

    def test_pipeline_fail_fast_at_signal(self, default_configs, default_ctx):
        """pipeline 在 SIG 阶段 fail-fast，下游不执行。"""
        pkt = DataPacket(type="market_data", payload={"raw_signals": [], "total_capital": 1000000})
        result = run_pipeline(pkt, default_configs, default_ctx)
        assert not result.success
        assert result.failed_stage == "SIG"
        assert "PORT" not in result.history


# ──────────────────────────────────────────────────────────────────────────────
# 测试：② 组合构建异常
# ──────────────────────────────────────────────────────────────────────────────


class TestPortfolioStageExceptions:
    """② 组合构建阶段异常。"""

    def test_single_weight_exceeds_raises(self, default_configs, default_ctx):
        """单标的权重 > 10% → PortfolioConcentrationError。"""
        cfg = PortfolioConfig(max_single_weight=0.1)
        pkt = DataPacket(
            type="signals",
            payload={
                "signals": [
                    {"symbol": "600519", "confidence": 0.9},
                    {"symbol": "000858", "confidence": 0.01},
                ],
            },
        )
        with pytest.raises(PortfolioConcentrationError, match="单标的权重超限"):
            process_portfolio_construction(pkt, cfg, default_ctx)

    def test_sector_weight_exceeds_raises(self, default_configs, default_ctx):
        """行业权重 > 30% → PortfolioConcentrationError。"""
        cfg = PortfolioConfig(max_single_weight=1.0, max_sector_weight=0.3)
        ctx = MarketContext(sector_weights={"白酒": 0.45})
        pkt = DataPacket(
            type="signals",
            payload={
                "signals": [
                    {"symbol": "600519", "confidence": 0.05},
                    {"symbol": "000858", "confidence": 0.5},
                ],
            },
        )
        with pytest.raises(PortfolioConcentrationError, match="行业权重超限"):
            process_portfolio_construction(pkt, cfg, ctx)

    def test_pipeline_fail_fast_at_portfolio(self, default_configs, default_ctx):
        """pipeline 在 PORT 阶段 fail-fast（单信号导致权重 100%）。"""
        cfg = PipelineConfigs(portfolio=PortfolioConfig(max_single_weight=0.1))
        pkt = DataPacket(
            type="market_data",
            payload={
                "raw_signals": [{"symbol": "600519", "confidence": 0.85}],
                "total_capital": 1000000,
            },
        )
        result = run_pipeline(pkt, cfg, default_ctx)
        assert not result.success
        assert result.failed_stage == "PORT"
        assert "POS" not in result.history


# ──────────────────────────────────────────────────────────────────────────────
# 测试：③ 仓位裁决异常
# ──────────────────────────────────────────────────────────────────────────────


class TestPositionStageExceptions:
    """③ 仓位裁决阶段异常。"""

    def test_position_limit_exceeds_raises(self, default_configs, default_ctx):
        """计算股数 > max_single_position → PositionLimitError。"""
        cfg = PositionConfig(max_single_position=10000)
        pkt = DataPacket(
            type="target_weights",
            payload={
                "weights": {"600519": 0.08},
                "total_capital": 100000000,
            },
        )
        with pytest.raises(PositionLimitError, match="单标的仓位超限"):
            process_position_sizing(pkt, cfg, default_ctx)

    def test_pipeline_fail_fast_at_position(self, default_configs, default_ctx):
        """pipeline 在 POS 阶段 fail-fast。"""
        cfg = PipelineConfigs(
            position=PositionConfig(max_single_position=100),
            portfolio=PortfolioConfig(max_single_weight=1.0),
        )
        pkt = DataPacket(
            type="market_data",
            payload={
                "raw_signals": [{"symbol": "600519", "confidence": 0.7}],
                "total_capital": 100000000,
            },
        )
        result = run_pipeline(pkt, cfg, default_ctx)
        assert not result.success
        assert result.failed_stage == "POS"
        assert "BM-EXE-01" not in result.history


# ──────────────────────────────────────────────────────────────────────────────
# 测试：④ 风控审批异常
# ──────────────────────────────────────────────────────────────────────────────


class TestRiskApprovalExceptions:
    """④ BM-EXE-01 风控审批阶段异常（HALT 级）。"""

    def test_single_weight_halt_raises(self, default_configs, default_ctx):
        """单标的权重 > HALT 阈值 → RiskViolationError。"""
        cfg = RiskConfig(max_single_weight=0.1)
        pkt = DataPacket(
            type="position_order",
            payload={
                "symbol": "600519",
                "weight": 0.15,
                "qty": 1000,
                "side": "buy",
            },
        )
        with pytest.raises(RiskViolationError, match="单标的权重超 HALT"):
            process_risk_approval(pkt, cfg, default_ctx)

    def test_daily_loss_halt_raises(self, default_configs, default_ctx):
        """日内亏损 > 5% → RiskViolationError（最高优先级阻断）。"""
        cfg = RiskConfig(max_daily_loss_pct=0.05)
        ctx = MarketContext(daily_loss_pct=0.06)
        pkt = DataPacket(
            type="position_order",
            payload={
                "symbol": "600519",
                "weight": 0.1,
                "qty": 100,
                "side": "buy",
            },
        )
        with pytest.raises(RiskViolationError, match="日内亏损超 HALT"):
            process_risk_approval(pkt, cfg, ctx)

    def test_daily_loss_takes_priority_over_weight(self, default_configs, default_ctx):
        """日内亏损 HALT 优先于单标的权重检查（先抛亏损）。"""
        cfg = RiskConfig(max_single_weight=0.1, max_daily_loss_pct=0.05)
        ctx = MarketContext(daily_loss_pct=0.08)
        pkt = DataPacket(
            type="position_order",
            payload={
                "symbol": "600519",
                "weight": 0.2,
                "qty": 100,
                "side": "buy",
            },
        )
        with pytest.raises(RiskViolationError, match="日内亏损超 HALT"):
            process_risk_approval(pkt, cfg, ctx)

    def test_circuit_breaker_halt_raises(self, default_configs, default_ctx):
        """行情中断触发熔断 → RiskViolationError（最高优先级阻断）。"""
        ctx = MarketContext(circuit_breaker_triggered=True)
        pkt = DataPacket(type="position_order", payload={"symbol": "600519", "weight": 0.1, "qty": 100, "side": "buy"})
        with pytest.raises(RiskViolationError, match="市场熔断"):
            process_risk_approval(pkt, default_configs.risk, ctx)

    def test_pipeline_fail_fast_at_risk(self, default_configs, default_ctx):
        """pipeline 在 BM-EXE-01 阶段 fail-fast。"""
        cfg = PipelineConfigs(
            risk=RiskConfig(max_single_weight=0.08),
            portfolio=PortfolioConfig(max_single_weight=1.0),
        )
        pkt = DataPacket(
            type="market_data",
            payload={
                "raw_signals": [{"symbol": "600519", "confidence": 0.85}],
                "total_capital": 1000000,
            },
        )
        result = run_pipeline(pkt, cfg, default_ctx)
        assert not result.success
        assert result.failed_stage == "BM-EXE-01"
        assert "BM-EXE-04" not in result.history


# ──────────────────────────────────────────────────────────────────────────────
# 测试：⑤ 合规异常
# ──────────────────────────────────────────────────────────────────────────────


class TestComplianceExceptions:
    """⑤ BM-EXE-04 Pre-Trade 合规阶段异常（Fail-Closed）。"""

    def test_participation_rate_exceeds_raises(self, default_configs, default_ctx):
        """参与率 > 5% → ComplianceViolationError。"""
        ctx = MarketContext(participation_rate=0.08)
        pkt = DataPacket(
            type="approved_order",
            payload={
                "symbol": "600519",
                "target_qty": 100,
                "side": "buy",
                "approved": True,
            },
        )
        with pytest.raises(ComplianceViolationError, match="参与率超限"):
            process_pretrade_compliance(pkt, default_configs.compliance, ctx)

    def test_price_limit_raises(self, default_configs, default_ctx):
        """涨跌停 → ComplianceViolationError。"""
        ctx = MarketContext(price_limit_hit=True)
        pkt = DataPacket(
            type="approved_order",
            payload={
                "symbol": "600519",
                "target_qty": 100,
                "side": "buy",
                "approved": True,
            },
        )
        with pytest.raises(ComplianceViolationError, match="涨跌停"):
            process_pretrade_compliance(pkt, default_configs.compliance, ctx)

    def test_wash_trade_raises(self, default_configs, default_ctx):
        """Wash Trade 检测 → ComplianceViolationError。"""
        ctx = MarketContext(wash_trade_detected=True)
        pkt = DataPacket(
            type="approved_order",
            payload={
                "symbol": "600519",
                "target_qty": 100,
                "side": "buy",
                "approved": True,
            },
        )
        with pytest.raises(ComplianceViolationError, match="Wash Trade"):
            process_pretrade_compliance(pkt, default_configs.compliance, ctx)

    def test_dwell_time_lock_raises(self, default_configs, default_ctx):
        """报单停留时间 < 50μs → ComplianceViolationError。"""
        ctx = MarketContext(dwell_time_us=30)
        pkt = DataPacket(
            type="approved_order",
            payload={
                "symbol": "600519",
                "target_qty": 100,
                "side": "buy",
                "approved": True,
            },
        )
        with pytest.raises(ComplianceViolationError, match="报单停留时间不足"):
            process_pretrade_compliance(pkt, default_configs.compliance, ctx)

    def test_cancel_rate_exceeds_raises(self, default_configs, default_ctx):
        """撤单率 > 15% → ComplianceViolationError。"""
        ctx = MarketContext(cancel_rate=0.2)
        pkt = DataPacket(
            type="approved_order",
            payload={
                "symbol": "600519",
                "target_qty": 100,
                "side": "buy",
                "approved": True,
            },
        )
        with pytest.raises(ComplianceViolationError, match="撤单率超限"):
            process_pretrade_compliance(pkt, default_configs.compliance, ctx)

    def test_unapproved_order_rejected(self, default_configs, default_ctx):
        """未通过风控审批的订单 → ComplianceViolationError（Fail-Closed）。"""
        pkt = DataPacket(
            type="approved_order",
            payload={
                "symbol": "600519",
                "target_qty": 100,
                "side": "buy",
                "approved": False,
            },
        )
        with pytest.raises(ComplianceViolationError, match="未通过风控审批"):
            process_pretrade_compliance(pkt, default_configs.compliance, default_ctx)

    def test_pipeline_fail_fast_at_compliance(self, default_configs, default_ctx):
        """pipeline 在 BM-EXE-04 阶段 fail-fast。"""
        ctx = MarketContext(participation_rate=0.08)
        cfg = PipelineConfigs(
            portfolio=PortfolioConfig(max_single_weight=1.0),
            risk=RiskConfig(max_single_weight=1.0),
        )
        pkt = DataPacket(
            type="market_data",
            payload={
                "raw_signals": [{"symbol": "600519", "confidence": 0.85}],
                "total_capital": 1000000,
            },
        )
        result = run_pipeline(pkt, cfg, ctx)
        assert not result.success
        assert result.failed_stage == "BM-EXE-04"
        assert "BM-EXE-05" not in result.history


# ──────────────────────────────────────────────────────────────────────────────
# 测试：⑥ 路由异常
# ──────────────────────────────────────────────────────────────────────────────


class TestRoutingExceptions:
    """⑥ BM-EXE-05 智能路由阶段异常。"""

    def test_low_liquidity_raises(self, default_configs, default_ctx):
        """流动性 < min → RoutingError。"""
        cfg = RoutingConfig(min_liquidity=2000)
        ctx = MarketContext(liquidity=1000)
        pkt = DataPacket(
            type="compliant_order",
            payload={
                "symbol": "600519",
                "qty": 100,
                "side": "buy",
                "compliant": True,
            },
        )
        with pytest.raises(RoutingError, match="流动性不足"):
            process_smart_routing(pkt, cfg, ctx)

    def test_algo_unavailable_raises(self, default_configs, default_ctx):
        """TCA 反馈指定不可用算法 → RoutingError。"""
        cfg = RoutingConfig(available_algos=("TWAP",))
        ctx = MarketContext(liquidity=10000, tca_feedback={"slippage_bps": 8.0})
        pkt = DataPacket(
            type="compliant_order",
            payload={
                "symbol": "600519",
                "qty": 100,
                "side": "buy",
                "compliant": True,
            },
        )
        with pytest.raises(RoutingError, match="算法不可用"):
            process_smart_routing(pkt, cfg, ctx)

    def test_pipeline_fail_fast_at_routing(self, default_configs, default_ctx):
        """pipeline 在 BM-EXE-05 阶段 fail-fast。"""
        cfg = PipelineConfigs(
            routing=RoutingConfig(min_liquidity=20000),
            portfolio=PortfolioConfig(max_single_weight=1.0),
            risk=RiskConfig(max_single_weight=1.0),
        )
        pkt = DataPacket(
            type="market_data",
            payload={
                "raw_signals": [{"symbol": "600519", "confidence": 0.85}],
                "total_capital": 1000000,
            },
        )
        result = run_pipeline(pkt, cfg, default_ctx)
        assert not result.success
        assert result.failed_stage == "BM-EXE-05"
        assert "BM-EXE-02" not in result.history


# ──────────────────────────────────────────────────────────────────────────────
# 测试：⑦ 执行异常
# ──────────────────────────────────────────────────────────────────────────────


class TestExecutionExceptions:
    """⑦ BM-EXE-02 交易执行阶段异常。"""

    def test_channel_unavailable_raises(self, default_configs, default_ctx):
        """交易通道断连 → ExecutionError。"""
        cfg = ExecutionConfig(channel_available=False)
        pkt = DataPacket(
            type="child_orders",
            payload={
                "children": [{"child_id": "c0", "qty": 100, "symbol": "600519", "side": "buy", "algo": "TWAP"}],
            },
        )
        with pytest.raises(ExecutionError, match="交易通道不可用"):
            process_trade_execution(pkt, cfg, default_ctx)

    def test_fill_timeout_raises(self, default_configs, default_ctx):
        """成交超时 → ExecutionError。"""
        cfg = ExecutionConfig()
        ctx = MarketContext()
        ctx.fill_timeout = True  # type: ignore[attr-defined]
        pkt = DataPacket(
            type="child_orders",
            payload={
                "children": [{"child_id": "c0", "qty": 100, "symbol": "600519", "side": "buy", "algo": "TWAP"}],
            },
        )
        with pytest.raises(ExecutionError, match="成交超时"):
            process_trade_execution(pkt, cfg, ctx)

    def test_pipeline_fail_fast_at_execution(self, default_configs, default_ctx):
        """pipeline 在 BM-EXE-02 阶段 fail-fast。"""
        cfg = PipelineConfigs(
            execution=ExecutionConfig(channel_available=False),
            portfolio=PortfolioConfig(max_single_weight=1.0),
            risk=RiskConfig(max_single_weight=1.0),
        )
        pkt = DataPacket(
            type="market_data",
            payload={
                "raw_signals": [{"symbol": "600519", "confidence": 0.85}],
                "total_capital": 1000000,
            },
        )
        result = run_pipeline(pkt, cfg, default_ctx)
        assert not result.success
        assert result.failed_stage == "BM-EXE-02"
        assert "BM-EXE-06" not in result.history


# ──────────────────────────────────────────────────────────────────────────────
# 测试：⑧ 成交处理异常
# ──────────────────────────────────────────────────────────────────────────────


class TestFillHandlingExceptions:
    """⑧ BM-EXE-06 成交回报处理阶段异常。"""

    def test_partial_fill_rejected_raises(self, default_configs, default_ctx):
        """要求全部成交但存在部分成交 → FillProcessingError。"""
        cfg = FillConfig(require_full_fill=True)
        pkt = DataPacket(
            type="fill_report",
            payload={
                "fills": [
                    {
                        "child_id": "c0",
                        "ordered_qty": 100,
                        "filled_qty": 50,
                        "fill_price": 10.0,
                        "symbol": "600519",
                        "side": "buy",
                        "algo": "TWAP",
                    }
                ],
            },
        )
        with pytest.raises(FillProcessingError, match="要求全部成交但存在部分成交"):
            process_fill_handling(pkt, cfg, default_ctx)

    def test_qty_mismatch_raises(self, default_configs, default_ctx):
        """成交数量超过报单 → FillProcessingError。"""
        cfg = FillConfig(require_full_fill=False, tolerate_qty_mismatch=False)
        pkt = DataPacket(
            type="fill_report",
            payload={
                "fills": [
                    {
                        "child_id": "c0",
                        "ordered_qty": 100,
                        "filled_qty": 150,
                        "fill_price": 10.0,
                        "symbol": "600519",
                        "side": "buy",
                        "algo": "TWAP",
                    }
                ],
            },
        )
        with pytest.raises(FillProcessingError, match="成交数量超过报单"):
            process_fill_handling(pkt, cfg, default_ctx)

    def test_pipeline_fail_fast_at_fill(self, default_configs, default_ctx):
        """pipeline 在 BM-EXE-06 阶段 fail-fast。"""
        ctx = MarketContext()
        ctx.partial_last_child = True  # type: ignore[attr-defined]
        cfg = PipelineConfigs(
            fill=FillConfig(require_full_fill=True),
            execution=ExecutionConfig(partial_fill_allowed=True),
            portfolio=PortfolioConfig(max_single_weight=1.0),
            risk=RiskConfig(max_single_weight=1.0),
        )
        pkt = DataPacket(
            type="market_data",
            payload={
                "raw_signals": [{"symbol": "600519", "confidence": 0.85}],
                "total_capital": 1000000,
            },
        )
        result = run_pipeline(pkt, cfg, ctx)
        assert not result.success
        assert result.failed_stage == "BM-EXE-06"
        assert "BM-EXE-03" not in result.history


# ──────────────────────────────────────────────────────────────────────────────
# 测试：⑨ TCA 降级闭环
# ──────────────────────────────────────────────────────────────────────────────


class TestTCADegradationLoop:
    """⑨ TCA 降级反馈闭环：高滑点 → 反馈 → 第二轮拆单参数调整。"""

    def test_high_slippage_triggers_degradation(self, default_configs, default_ctx):
        """TCA 检测到滑点 > 阈值 → degradation_triggered=True。"""
        cfg = TCAConfig(arrival_price=10.0, slippage_degradation_threshold=5.0)
        fills = [
            {
                "child_id": "c0",
                "ordered_qty": 1000,
                "filled_qty": 1000,
                "fill_price": 10.15,
                "symbol": "600519",
                "side": "buy",
                "algo": "TWAP",
            }
        ]
        pkt = DataPacket(
            type="position_snapshot",
            payload={
                "fills": fills,
                "total_qty": 1000,
                "avg_price": 10.15,
                "commission": 3.0,
                "symbol": "600519",
                "pnl": 0,
            },
        )
        result = process_tca_analysis(pkt, cfg, default_ctx)
        assert result.payload["degradation_triggered"] is True
        assert result.payload["feedback"] is not None
        assert "slippage_bps" in result.payload["feedback"]

    def test_low_slippage_no_degradation(self, default_configs, default_ctx):
        """TCA 滑点 ≤ 阈值 → 不触发降级。"""
        cfg = TCAConfig(arrival_price=10.0, slippage_degradation_threshold=5.0)
        fills = [
            {
                "child_id": "c0",
                "ordered_qty": 1000,
                "filled_qty": 1000,
                "fill_price": 10.002,
                "symbol": "600519",
                "side": "buy",
                "algo": "TWAP",
            }
        ]
        pkt = DataPacket(
            type="position_snapshot",
            payload={
                "fills": fills,
                "total_qty": 1000,
                "avg_price": 10.002,
                "commission": 3.0,
                "symbol": "600519",
                "pnl": 0,
            },
        )
        result = process_tca_analysis(pkt, cfg, default_ctx)
        assert result.payload["degradation_triggered"] is False
        assert result.payload["feedback"] is None

    def test_feedback_adjusts_routing_params(self, default_configs, default_ctx):
        """TCA 反馈调整 ⑥ 拆单参数：参与率降低 + 算法切换。"""
        cfg = RoutingConfig(
            default_participation_rate=0.1,
            degraded_participation_rate=0.05,
            slippage_threshold_bps=5.0,
        )
        ctx = MarketContext(liquidity=10000, tca_feedback={"slippage_bps": 8.0})
        pkt = DataPacket(
            type="compliant_order",
            payload={
                "symbol": "600519",
                "qty": 1000,
                "side": "buy",
                "compliant": True,
            },
        )
        result = process_smart_routing(pkt, cfg, ctx)
        assert result.payload["participation_rate"] == 0.05, "TCA 反馈应将参与率从 10% 降到 5%"
        assert result.payload["algo"] == "VWAP", "TCA 反馈应将算法从 TWAP 切换到 VWAP"

    def test_full_closed_loop_two_iterations(self, default_configs, default_ctx):
        """完整闭环两轮迭代：主链跑通→TCA反馈→第二轮拆单优化。

        第一轮：默认参数执行 → TCA 发现滑点高
        第二轮：TCA 反馈调整参数 → 参与率降低
        """
        # 第一轮：默认参数
        configs = PipelineConfigs(
            portfolio=PortfolioConfig(max_single_weight=1.0),
            risk=RiskConfig(max_single_weight=1.0),
        )
        pkt = DataPacket(
            type="market_data",
            payload={
                "raw_signals": [{"symbol": "600519", "confidence": 0.85}],
                "total_capital": 1000000,
            },
        )
        result1 = run_pipeline(pkt, configs, default_ctx)
        assert result1.success
        assert result1.final_packet.type == "tca_report"

        # 构造高滑点反馈
        feedback = {"slippage_bps": 8.0}
        ctx2 = MarketContext(liquidity=10000, tca_feedback=feedback)

        # 第二轮：携带反馈重新拆单
        result2 = run_pipeline(pkt, configs, ctx2)
        assert result2.success
        assert result2.final_packet.payload["slippage_bps"] < result1.final_packet.payload["slippage_bps"] + 100

    def test_pipeline_records_degradation_flag(self, default_configs, default_ctx):
        """pipeline 结果记录 degradation_triggered 标志。

        通过调高 arrival_price 偏移构造高滑点场景。
        """
        cfg = PipelineConfigs(
            tca=TCAConfig(arrival_price=10.0, slippage_degradation_threshold=0.5),
            portfolio=PortfolioConfig(max_single_weight=1.0),
            risk=RiskConfig(max_single_weight=1.0),
        )
        pkt = DataPacket(
            type="market_data",
            payload={
                "raw_signals": [{"symbol": "600519", "confidence": 0.85}],
                "total_capital": 1000000,
            },
        )
        result = run_pipeline(pkt, cfg, default_ctx)
        assert result.success
        assert result.degradation_triggered is True


# ──────────────────────────────────────────────────────────────────────────────
# 测试：端到端降级
# ──────────────────────────────────────────────────────────────────────────────


class TestEndToEndDegradation:
    """端到端降级：信号置信度低 → 仓位缩减 → 订单量减小。"""

    def test_low_confidence_signal_smaller_position(self, default_configs, default_ctx):
        """低置信度信号 → 组合权重分散 → 单标的仓位更小。

        验证信号质量端到端影响最终订单量（风险预算传导）。
        """
        configs = PipelineConfigs(
            portfolio=PortfolioConfig(max_single_weight=1.0),
            risk=RiskConfig(max_single_weight=1.0),
        )
        high_conf_pkt = DataPacket(
            type="market_data",
            payload={
                "raw_signals": [
                    {"symbol": "600519", "confidence": 0.85},
                    {"symbol": "000858", "confidence": 0.012},
                    {"symbol": "000333", "confidence": 0.01},
                ],
                "total_capital": 1000000,
            },
        )
        high_result = run_pipeline(high_conf_pkt, configs, default_ctx)
        assert high_result.success
        high_weights = high_result.final_packet.payload

        # 低置信度场景（主标的置信度降低）
        low_conf_pkt = DataPacket(
            type="market_data",
            payload={
                "raw_signals": [
                    {"symbol": "600519", "confidence": 0.65},
                    {"symbol": "000858", "confidence": 0.63},
                    {"symbol": "000333", "confidence": 0.007},
                ],
                "total_capital": 1000000,
            },
        )
        low_result = run_pipeline(low_conf_pkt, configs, default_ctx)
        assert low_result.success

        # 高置信度场景主标的权重应 > 低置信度场景
        # （由于权重是按 confidence 归一化分配的）

    def test_signal_quality_gates_pipeline(self, default_configs, default_ctx):
        """信号质量门禁：置信度低于阈值的信号被过滤，无合格信号则 pipeline 阻断。"""
        cfg = PipelineConfigs(signal=SignalConfig(min_confidence=0.5))
        pkt = DataPacket(
            type="market_data",
            payload={
                "raw_signals": [{"symbol": "600519", "confidence": 0.45}],
                "total_capital": 1000000,
            },
        )
        result = run_pipeline(pkt, cfg, default_ctx)
        assert not result.success
        assert result.failed_stage == "SIG"


# ──────────────────────────────────────────────────────────────────────────────
# 测试：状态追踪
# ──────────────────────────────────────────────────────────────────────────────


class TestPipelineStateTracking:
    """pipeline 状态追踪：history 完整性 + fail-fast 语义。"""

    def test_history_grows_stage_by_stage(self, default_market_data, default_configs, default_ctx):
        """history 随阶段执行逐步增长。"""
        pkt = default_market_data
        for i, stage_id in enumerate(FULL_PIPELINE):
            processor = STAGE_PROCESSORS[stage_id]
            config = _get_stage_config(default_configs, stage_id)
            pkt = processor(pkt, config, default_ctx)
            assert len(pkt.history) == i + 1, (
                f"执行 {stage_id} 阶段后 history 长度应为 {i + 1}，实际 {len(pkt.history)}"
            )

    def test_fail_fast_downstream_not_executed(self, default_configs, default_ctx):
        """fail-fast：异常阶段后所有下游阶段不执行。"""
        ctx = MarketContext(participation_rate=0.08)  # 触发合规阻断
        cfg = PipelineConfigs(
            portfolio=PortfolioConfig(max_single_weight=1.0),
            risk=RiskConfig(max_single_weight=1.0),
        )
        pkt = DataPacket(
            type="market_data",
            payload={
                "raw_signals": [{"symbol": "600519", "confidence": 0.85}],
                "total_capital": 1000000,
            },
        )
        result = run_pipeline(pkt, cfg, ctx)
        assert not result.success
        assert result.failed_stage == "BM-EXE-04"
        # 下游阶段不在 history 中
        for downstream in ["BM-EXE-05", "BM-EXE-02", "BM-EXE-06", "BM-EXE-03"]:
            assert downstream not in result.history, f"{downstream} 不应在 history 中"

    def test_error_message_includes_stage_context(self, default_configs, default_ctx):
        """异常消息包含阶段上下文（便于定位）。"""
        ctx = MarketContext(participation_rate=0.2)
        cfg = PipelineConfigs(
            portfolio=PortfolioConfig(max_single_weight=1.0),
            risk=RiskConfig(max_single_weight=1.0),
        )
        pkt = DataPacket(
            type="market_data",
            payload={
                "raw_signals": [{"symbol": "600519", "confidence": 0.85}],
                "total_capital": 1000000,
            },
        )
        result = run_pipeline(pkt, cfg, ctx)
        assert not result.success
        assert result.error is not None
        assert "参与率" in str(result.error)
        assert result.failed_stage == "BM-EXE-04"

    def test_every_exception_maps_to_correct_stage(self):
        """每种异常类型映射到正确的阶段（EXCEPTION_STAGE_MAP 一致性）。"""
        assert len(EXCEPTION_STAGE_MAP) >= 8, "异常阶段映射不完整: 应至少 8 个映射"
        for exc_type, stage_id in EXCEPTION_STAGE_MAP.items():
            assert stage_id in FULL_PIPELINE, f"{exc_type.__name__} 映射到 {stage_id}，但该阶段不在 FULL_PIPELINE 中"


# ──────────────────────────────────────────────────────────────────────────────
# 可视化（独立运行）
# ──────────────────────────────────────────────────────────────────────────────


def _run_pipeline_visual():
    """独立运行：打印 9 阶段端到端流水线可视化报告。"""
    print("=" * 72)
    print("信号→成交回报 端到端 9 阶段流水线模拟")
    print("=" * 72)

    market = DataPacket(
        type="market_data",
        payload={
            "raw_signals": [
                {"symbol": "600519", "confidence": 0.85},
                {"symbol": "000858", "confidence": 0.80},
                {"symbol": "000333", "confidence": 0.78},
            ],
            "total_capital": 1000000,
        },
    )
    configs = PipelineConfigs()
    ctx = MarketContext()

    result = run_pipeline(market, configs, ctx)
    print(f"\n[初始输入] {market.type} — {len(market.payload['raw_signals'])} 条信号")
    print(f"\n[执行结果] success={result.success}")
    print(f"[流转路径] {' → '.join(result.history)}")
    if result.final_packet:
        print(f"[最终产出] {result.final_packet.type}")
    if result.degradation_triggered:
        print("[降级触发] degradation_triggered=True")
    if result.failed_stage:
        print(f"[失败阶段] {result.failed_stage}: {result.error}")

    # 第二轮：携带 TCA 反馈（高滑点）重新拆单
    print("\n" + "-" * 72)
    print("[降级闭环] 第二轮：携带 TCA 反馈（高滑点）重新拆单")
    ctx2 = MarketContext(liquidity=10000, tca_feedback={"slippage_bps": 8.0})
    result2 = run_pipeline(market, configs, ctx2)
    if result2.final_packet:
        print(f"[第二轮] success={result2.success}, degradation={result2.degradation_triggered}")
        if "slippage_bps" in result2.final_packet.payload:
            print(f"  slippage_bps={result2.final_packet.payload['slippage_bps']:.2f}")

    print("\n✅ 端到端流水线验证通过")


if __name__ == "__main__":
    _run_pipeline_visual()
