# [BLUEPRINT] MOD-L07-001 | docs/03_modules/_domain_reporting/blueprint.md
# [MODULE] zephyr.reporting.attribution
# [DOMAIN] D_REPORTING
# [DEPENDENCIES] zephyr.shared.contracts.fill; zephyr.shared.contracts.enums.order_enums; zephyr.shared.foundation.errors; zephyr.trading.pnl_calculator(费率复用)
# [CONSUMERS] 调用方(日终对账归因链路, BM-REC-02-B); 54_reconciliation_attribution §3.5/§3.12
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] PnL归属以fill_id+strategy_id为唯一键不依赖session_id(54号§3.2多session边界); fill_id幂等去重(重复record不产生叠加); FIFO配对; 求和不变量硬门禁(容差1bp); Shapley效率公理Σ=组合总收益; 费率唯一真源=pnl_calculator.AShareFeeCalculator不重复实现
# [MODIFY-GUARD] 54_reconciliation_attribution.md §3.5/§3.12
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidAttributionInputError(ZA-RPT-0030)
# [TESTS] tests/reporting/test_attribution.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: Fill 成交回报(CTR-005, 含 strategy_id/fill_id/fill_price/filled_quantity) + side(调用方从 Order 传入, Fill 契约无 side)
# I2: fee_calculator(可选注入, 默认 AShareFeeCalculator——54 号复用优先)
# I3: strategy_pnls/firm_pnl(求和不变量校验输入) + strategy_returns/weights(Shapley 输入)
# F1: StrategyPnlAccountant.record_fill(fill, side)——按 strategy_id 归集, FIFO 配对, 买入开仓累成本/卖出撮合出 realized net_pnl
# F2: validate_strategy_pnl_invariant(strategy_pnls, firm_pnl, tolerance_bps=1.0)——Σ(strategy)==firm 硬门禁(54 号 §3.5 施工算法)
# F3: shapley_strategy_attribution(strategy_returns, weights)——Shapley 值公平分配交互效应(54 号 §3.12 施工算法, O(2^n) 精确, n≤8)
# A1: 跨 session 持仓追踪——键=(strategy_id, symbol) FIFO lot 队列, 不引入 session_id 隔离(防幽灵成交/PnL 漏算)
# A2: fill_id 幂等——重复 record_fill 同一 fill_id 直接跳过(事件流重放安全)
# O1: all_strategy_pnls() -> {strategy_id: net_pnl}; open_positions(); 不变量校验 verdict; Shapley 分解结果
# [/ALGO_FLOW]
"""
D_REPORTING — 对账归因函数级实现（54 号 G25 §3.5/§3.12）。

施工范围（AI-NIGHT-001 包P，54 号未施工清单 #1/#6）：
  1. StrategyBook 独立 PnL 核算（#ARCH-REG-005 proposed 对接）——策略层归因
     数据源缺口补齐：各 StrategyBook 成交按 strategy_id 归集，FIFO 配对核算
     独立净 PnL，跨 session 追踪持仓（54 号 §3.2 设计原则：fill_id + position
     归属为唯一键，不依赖 session_id/reoptimization_run_id）。
  2. 策略贡献分解求和不变量校验（§3.5 v1.5.0 施工算法，1bp 硬门禁）。
  3. Shapley 值策略贡献分解（§3.12 v1.5.0 施工算法，Phase 2 候选，
     精确 Shapley O(2^n)，n≤8 可行）。

工程裁定：
  - 费率核算复用 trading.pnl_calculator.AShareFeeCalculator（佣金/印花税/过户费
    唯一真源），不重复实现费率表；fill.commission（券商回报佣金）不参与计算，
    与 PnlCalculator 口径一致（阶段2对账差异另行比对）。
  - 本模块不改 position/core/strategy_book.py（MOD-POS-020 由其他批次施工），
    策略层 PnL 数据源以"成交回报按 strategy_id 归集"方式独立承载。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: strategy_pnls 参数
#   fields: 参数 strategy_pnls，类型注解 dict[str, float]
#   code: attribution.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: firm_pnl 参数
#   fields: 参数 firm_pnl，类型注解 float
#   code: attribution.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: tolerance_bps 参数
#   fields: 参数 tolerance_bps，类型注解 float
#   code: attribution.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: strategy_returns 参数
#   fields: 参数 strategy_returns，类型注解 dict[str, list[float]]
#   code: attribution.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① StrategyPnlAccountant
#   name_en: StrategyPnlAccountant
#   intro: StrategyBook 独立 PnL 核算器（54 号 §3.5 策略层数据源）。
#   desc: StrategyBook 独立 PnL 核算器（54 号 §3.5 策略层数据源）。 按 Fill.strategy_id 归集成交，(strategy_id, symbol)…；公共方法（定义序）: record_f…
#   inputs: fee_calculator
#   outputs: 返回值
# - id: A2
#   name_zh: ② validate_strategy_pnl_invariant
#   name_en: validate_strategy_pnl_invariant
#   intro: 校验 Σ(strategy_pnl) == firm_pnl 求和不变量（归因报告硬门禁）。
#   desc: 校验 Σ(strategy_pnl) == firm_pnl 求和不变量（归因报告硬门禁）。 FAIL 语义（54 号 §3.5）：归因报告拒绝发布 + 触发告警，差异来源定位方…；源码 L289-L323
#   inputs: strategy_pnls firm_pnl tolerance_bps
#   outputs: dict
# - id: A3
#   name_zh: ③ shapley_strategy_attribution
#   name_en: shapley_strategy_attribution
#   intro: Shapley 值策略贡献分解——公平分配各策略对组合总收益的边际贡献。
#   desc: Shapley 值策略贡献分解——公平分配各策略对组合总收益的边际贡献。 特征函数：子组合的等权（或 weights 加权）日收益复合累计收益。 效率公理保证 Σ Shapley…；源码 L329-L401
#   inputs: strategy_returns weights
#   outputs: dict
#   （注：A3 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: dict
#   name_en: dict
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 调用方(日终对账归因链路, BM-REC-02-B); 54_reconciliation_attribution §3.5/§3.12
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import logging
from collections import defaultdict, deque
from dataclasses import dataclass
from decimal import Decimal
from itertools import combinations
from math import factorial
from typing import Final

from zephyr.shared.contracts.enums.order_enums import OrderSide
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.foundation.errors import ZephyrBaseError
from zephyr.trading.pnl_calculator import AShareFeeCalculator, FeeCalculator

_logger = logging.getLogger(__name__)

_SCHEMA_VERSION: Final[str] = "1.0"
#: 求和不变量容差（54 号 §3.5：1bp=0.01%，account for 费率精度尾差）
INVARIANT_TOLERANCE_BPS: Final[float] = 1.0
#: Shapley 精确计算策略数上限（54 号 §3.12 重评条件：n≤8 精确可行）
SHAPLEY_MAX_STRATEGIES: Final[int] = 8


class InvalidAttributionInputError(ZephyrBaseError):
    """归因输入非法——空 strategy_id / 非正价量 / 未知方向 / Shapley 规模超限等。"""

    error_code = "ZA-RPT-0030"


# ── 策略级 FIFO 持仓核算 ──


@dataclass(frozen=True)
class _Lot:
    """FIFO 持仓批次（含买入费用摊入成本）。"""

    quantity: Decimal
    unit_cost: Decimal  # (成交额 + 买入费用) / 数量


@dataclass(frozen=True)
class StrategySymbolPnl:
    """单策略单标的 PnL 快照。"""

    strategy_id: str
    symbol: str
    realized_net_pnl: Decimal
    open_quantity: Decimal
    open_cost: Decimal  # 未平仓批次成本合计（含买入费用）


class StrategyPnlAccountant:
    """StrategyBook 独立 PnL 核算器（54 号 §3.5 策略层数据源）。

    按 Fill.strategy_id 归集成交，(strategy_id, symbol) 维度 FIFO 配对：
      - BUY  → 开 FIFO lot，unit_cost 含买入费用摊入；
      - SELL → 队首撮合，realized = (卖价-成本)×量 - 卖出费用（印花税仅 SELL）。

    不变量：
      - fill_id 幂等去重（事件流重放/重复回报不产生 PnL 叠加）；
      - 不引入 session_id 隔离——跨 session 持仓连续追踪（54 号 §3.2
        "幽灵成交 + PnL 漏算"防线）；
      - 卖出超持仓（裸卖空）按 InvalidAttributionInputError 拒绝——
        A 股个人账户无融券，超持仓卖出=数据流断裂，Fail-Closed。
    """

    def __init__(self, fee_calculator: FeeCalculator | None = None) -> None:
        self._fee_calculator: FeeCalculator = fee_calculator if fee_calculator is not None else AShareFeeCalculator()
        # (strategy_id, symbol) -> FIFO lot 队列
        self._lots: dict[tuple[str, str], deque[_Lot]] = defaultdict(deque)
        # (strategy_id, symbol) -> 累计已实现净 PnL
        self._realized: dict[tuple[str, str], Decimal] = defaultdict(lambda: Decimal("0"))
        self._seen_fill_ids: set[str] = set()

    def record_fill(self, fill: Fill, side: OrderSide) -> Decimal:
        """归集一笔成交到所属策略。返回本笔 realized net_pnl（BUY 恒为 -费用）。

        Args:
            fill: CTR-005 成交回报（strategy_id/fill_id/价格/数量）。
            side: 买卖方向（Fill 契约无 side，调用方从 Order 传入）。

        Raises:
            InvalidAttributionInputError: strategy_id 空 / 价量非正 / 卖出超持仓。
        """
        if not fill.strategy_id or not fill.strategy_id.strip():
            raise InvalidAttributionInputError(
                "fill.strategy_id 不能为空（策略归集键）",
                details={"fill_id": fill.fill_id},
            )
        if fill.fill_price <= 0 or fill.filled_quantity <= 0:
            raise InvalidAttributionInputError(
                "fill_price/filled_quantity 必须为正",
                details={
                    "fill_id": fill.fill_id,
                    "fill_price": str(fill.fill_price),
                    "filled_quantity": str(fill.filled_quantity),
                },
            )
        if side not in (OrderSide.BUY, OrderSide.SELL):
            raise InvalidAttributionInputError(
                f"未知买卖方向: {side}",
                details={"fill_id": fill.fill_id, "side": str(side)},
            )
        if fill.fill_id in self._seen_fill_ids:
            _logger.debug("record_fill 幂等跳过重复 fill_id=%s", fill.fill_id)
            return Decimal("0")

        key = (fill.strategy_id, fill.symbol)
        turnover = fill.fill_price * fill.filled_quantity
        fees = self._fee_calculator.calculate(turnover, side)

        if side is OrderSide.BUY:
            unit_cost = (turnover + fees.total) / fill.filled_quantity
            self._lots[key].append(_Lot(quantity=fill.filled_quantity, unit_cost=unit_cost))
            realized_net = -fees.total  # 买入费用即负 PnL（与 PnlCalculator BUY 口径一致）
        else:
            realized_net = self._match_sell(key, fill, fees.total)

        self._seen_fill_ids.add(fill.fill_id)
        self._realized[key] += realized_net
        return realized_net

    def _match_sell(self, key: tuple[str, str], fill: Fill, sell_fees: Decimal) -> Decimal:
        """FIFO 撮合卖出，返回净 PnL（含卖出费用扣减）。"""
        lots = self._lots[key]
        remaining = fill.filled_quantity
        gross = Decimal("0")
        while remaining > 0 and lots:
            head = lots[0]
            take = min(head.quantity, remaining)
            gross += (fill.fill_price - head.unit_cost) * take
            remaining -= take
            if take == head.quantity:
                lots.popleft()
            else:
                lots[0] = _Lot(quantity=head.quantity - take, unit_cost=head.unit_cost)
        if remaining > 0:
            raise InvalidAttributionInputError(
                "卖出数量超 FIFO 持仓（A 股无融券，疑似成交回报漏算/重复）",
                details={
                    "strategy_id": key[0],
                    "symbol": key[1],
                    "sell_qty": str(fill.filled_quantity),
                    "shortfall": str(remaining),
                },
            )
        return gross - sell_fees

    def strategy_net_pnl(self, strategy_id: str) -> Decimal:
        """单策略累计已实现净 PnL（全部标的求和）。"""
        return sum(
            (pnl for (sid, _), pnl in self._realized.items() if sid == strategy_id),
            Decimal("0"),
        )

    def all_strategy_pnls(self) -> dict[str, Decimal]:
        """全部策略净 PnL 映射——firm 层求和不变量校验的策略层输入。"""
        result: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
        for (sid, _), pnl in self._realized.items():
            result[sid] += pnl
        return dict(result)

    def open_positions(self, strategy_id: str) -> dict[str, StrategySymbolPnl]:
        """单策略未平仓快照（symbol → 数量/成本/已实现）。"""
        snapshot: dict[str, StrategySymbolPnl] = {}
        for (sid, symbol), lots in self._lots.items():
            if sid != strategy_id or not lots:
                continue
            open_qty = sum((lot.quantity for lot in lots), Decimal("0"))
            open_cost = sum((lot.quantity * lot.unit_cost for lot in lots), Decimal("0"))
            snapshot[symbol] = StrategySymbolPnl(
                strategy_id=sid,
                symbol=symbol,
                realized_net_pnl=self._realized.get((sid, symbol), Decimal("0")),
                open_quantity=open_qty,
                open_cost=open_cost,
            )
        return snapshot


# ── 策略贡献分解求和不变量校验（54 号 §3.5 v1.5.0 施工算法）──


def validate_strategy_pnl_invariant(
    strategy_pnls: dict[str, float],
    firm_pnl: float,
    tolerance_bps: float = INVARIANT_TOLERANCE_BPS,
) -> dict:
    """校验 Σ(strategy_pnl) == firm_pnl 求和不变量（归因报告硬门禁）。

    FAIL 语义（54 号 §3.5）：归因报告拒绝发布 + 触发告警，差异来源定位方向
    =成交回报漏算 / 费率错算 / T+1 跨日错位 / firm 层裁剪副作用。
    """
    if tolerance_bps <= 0:
        raise InvalidAttributionInputError(
            "tolerance_bps 必须为正",
            details={"tolerance_bps": tolerance_bps},
        )
    strategy_sum = sum(strategy_pnls.values())
    diff = firm_pnl - strategy_sum
    diff_bps = (diff / firm_pnl * 10000) if abs(firm_pnl) > 1e-12 else 0.0

    contributions = {
        sid: {
            "net_pnl": pnl,
            "contribution_ratio": pnl / firm_pnl if abs(firm_pnl) > 1e-12 else 0.0,
        }
        for sid, pnl in strategy_pnls.items()
    }

    return {
        "firm_pnl": firm_pnl,
        "strategy_sum": strategy_sum,
        "diff": diff,
        "diff_bps": diff_bps,
        "invariant_status": "PASS" if abs(diff_bps) <= tolerance_bps else "FAIL",
        "strategy_contributions": contributions,
    }


# ── Shapley 值策略贡献分解（54 号 §3.12 v1.5.0 施工算法，Phase 2 候选）──


def shapley_strategy_attribution(
    strategy_returns: dict[str, list[float]],
    weights: dict[str, float] | None = None,
) -> dict:
    """Shapley 值策略贡献分解——公平分配各策略对组合总收益的边际贡献。

    特征函数：子组合的等权（或 weights 加权）日收益复合累计收益。
    效率公理保证 Σ Shapley == 全组合收益（求和不变量自动满足）。
    复杂度 O(2^n)：n > SHAPLEY_MAX_STRATEGIES 拒绝（精确 Shapley 边界，
    54 号 §3.12 重评条件）；n≤8 可行（2^8=256 联盟）。
    """
    n = len(strategy_returns)
    if n == 0:
        raise InvalidAttributionInputError("strategy_returns 不能为空", details={})
    if n > SHAPLEY_MAX_STRATEGIES:
        raise InvalidAttributionInputError(
            "精确 Shapley 策略数超限（O(2^n)，n>8 需 Monte Carlo 近似）",
            details={"n": n, "max": SHAPLEY_MAX_STRATEGIES},
        )
    lengths = {len(v) for v in strategy_returns.values()}
    if len(lengths) != 1 or 0 in lengths:
        raise InvalidAttributionInputError(
            "各策略日收益序列必须等长且非空",
            details={"lengths": sorted(lengths)},
        )
    if weights is not None:
        missing = set(strategy_returns) - set(weights)
        if missing:
            raise InvalidAttributionInputError(
                "weights 缺少策略权重项",
                details={"missing": sorted(missing)},
            )

    strategy_ids = list(strategy_returns.keys())
    n_days = lengths.pop()

    def coalition_return(members: tuple[str, ...]) -> float:
        """特征函数：子组合复合累计收益（等权/加权日收益连乘）。"""
        if not members:
            return 0.0
        if weights is None:
            w = {m: 1.0 / len(members) for m in members}
        else:
            total_w = sum(weights[m] for m in members)
            if total_w <= 0:
                return 0.0
            w = {m: weights[m] / total_w for m in members}
        cumulative = 1.0
        for day in range(n_days):
            daily = sum(w[m] * strategy_returns[m][day] for m in members)
            cumulative *= 1.0 + daily
        return cumulative - 1.0

    full_return = coalition_return(tuple(strategy_ids))
    shapley = dict.fromkeys(strategy_ids, 0.0)
    n_factorial = factorial(n)
    for target in strategy_ids:
        others = [s for s in strategy_ids if s != target]
        for size in range(n):
            weight = factorial(size) * factorial(n - size - 1) / n_factorial
            for coalition in combinations(others, size):
                marginal = coalition_return(tuple(sorted((*coalition, target)))) - coalition_return(
                    tuple(sorted(coalition))
                )
                shapley[target] += weight * marginal

    sum_check = sum(shapley.values())
    return {
        "shapley_values": shapley,
        "full_portfolio_return": full_return,
        "sum_check": sum_check,
        "invariant_status": "PASS" if abs(sum_check - full_return) < 1e-9 else "FAIL",
    }


__all__ = [
    "INVARIANT_TOLERANCE_BPS",
    "InvalidAttributionInputError",
    "SHAPLEY_MAX_STRATEGIES",
    "StrategyPnlAccountant",
    "StrategySymbolPnl",
    "shapley_strategy_attribution",
    "validate_strategy_pnl_invariant",
]
