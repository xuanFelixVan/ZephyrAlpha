# [BLUEPRINT] MOD-RK-25 | docs/03_modules/MOD-RK-25/
# [MODULE] zephyr.risk.core.risk_data_pipeline
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.shared.contracts.market_data; zephyr.shared.contracts.position; zephyr.shared.contracts.fill; zephyr.shared.contracts.risk_limits; zephyr.shared.foundation.errors
# [CONSUMERS] MOD-RK-22(Agent Risk Monitor) ; MOD-RK-24(Risk Veto Engine) ; MOD-EX-024(Pre-Execution Checker)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] nav=cash+Σ可得市价市值; nav<=0→RiskDataPipelineError(Fail-Closed); 持仓数量<0→RiskDataPipelineError; 缺价/缺限额/缺成交→degraded=True不静默补零; 快照frozen不可变; 持仓/成交/限价数据全部经provider注入(禁自造数据管道)
# [MODIFY-GUARD] docs/03_modules/MOD-RK-25/
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RiskDataPipelineError
# [TESTS] tests/risk/core/test_risk_data_pipeline.py
# [A_module] module_id=MOD-RK-25 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
Risk Data Pipeline — 风控数据底座 (MOD-RK-25)

汇总行情 / 持仓 / 成交 / 限额为统一风控快照 (RiskSnapshot)，供下游消费：
  - MOD-RK-22 AgentRiskMonitor（agent 风险监控）
  - MOD-RK-24 RiskVetoEngine（风险否决引擎）
  - MOD-EX-024 PreExecutionChecker（执行前检查）

数据真源纪律（禁自造管道）：
  - 行情  ← MarketDataProvider 协议注入（CTR-001 NormalizedMarketData，D_DATA 既有数据层）
  - 持仓  ← PositionProvider 协议注入（CTR-006 PositionSnapshot，D_EX_CORE OMS/Tracker）
  - 成交  ← FillProvider 协议注入（CTR-005 Fill，D_EX_CORE 成交回报）
  - 限额  ← RiskLimitsProvider 协议注入（CTR-003 RiskLimits，D_RISK 限额引擎）
本模块只做装配与纯函数派生计算，不直接连接任何数据源。

Fail-Closed 语义：
  - 持仓快照不可得 → 抛 RiskDataPipelineError（无持仓真源不出快照，防止空仓错觉）
  - 行情/限额/成交部分缺失 → degraded=True + data_warnings 留痕，缺价持仓不静默补零

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: snapshot_input 参数
#   fields: 参数 snapshot_input，类型注解 RiskSnapshotInput
#   code: risk_data_pipeline.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① PositionProvider
#   name_en: PositionProvider
#   intro: 持仓真源协议（生产接线: ex_core PositionTracker / OMS）。
#   desc: 持仓真源协议（生产接线: ex_core PositionTracker / OMS）。；公共方法（定义序）: get_position_snapshot；源码 L148-L153
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② MarketDataProvider
#   name_en: MarketDataProvider
#   intro: 行情真源协议（生产接线: D_DATA 数据层查询接口）。
#   desc: 行情真源协议（生产接线: D_DATA 数据层查询接口）。；公共方法（定义序）: get_latest_quotes；源码 L156-L161
#   inputs: 无参数
#   outputs: 返回值
# - id: A3
#   name_zh: ③ FillProvider
#   name_en: FillProvider
#   intro: 成交真源协议（生产接线: ex_core 成交回报/审计日志）。
#   desc: 成交真源协议（生产接线: ex_core 成交回报/审计日志）。；公共方法（定义序）: get_fills_since；源码 L164-L169
#   inputs: 无参数
#   outputs: 返回值
# - id: A4
#   name_zh: ④ RiskLimitsProvider
#   name_en: RiskLimitsProvider
#   intro: 限额真源协议（生产接线: D_RISK 限额计算引擎）。
#   desc: 限额真源协议（生产接线: D_RISK 限额计算引擎）。；公共方法（定义序）: get_current_limits；源码 L172-L177
#   inputs: 无参数
#   outputs: 返回值
# - id: A5
#   name_zh: ⑤ assemble_risk_snapshot
#   name_en: assemble_risk_snapshot
#   intro: 装配统一风控快照（纯函数：同输入必同输出，可独立单测）。
#   desc: 装配统一风控快照（纯函数：同输入必同输出，可独立单测）。 不变量： - nav = cash + Σ(可得市价的持仓市值)；nav <= 0 → RiskDataPipeline…；源码 L268-L374
#   inputs: snapshot_input
#   outputs: RiskSnapshot
# - id: A6
#   name_zh: ⑥ RiskDataPipeline
#   name_en: RiskDataPipeline
#   intro: 风控数据管道：从注入的数据真源拉取并装配 RiskSnapshot。
#   desc: 风控数据管道：从注入的数据真源拉取并装配 RiskSnapshot。；公共方法（定义序）: build_snapshot；源码 L382-L455
#   inputs: position_provider market_data_provider fill_provider limits_provider
#   outputs: 返回值
#   （注：A6 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: RiskSnapshot
#   name_en: RiskSnapshot
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-RK-22(Agent Risk Monitor) ; MOD-RK-24(Risk Veto Engine) ; MOD-EX-024(Pre-Ex…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> O1
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from typing import Final, Protocol

from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.market_data import NormalizedMarketData
from zephyr.shared.contracts.position import PositionSnapshot
from zephyr.shared.contracts.risk_limits import RiskLimits
from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)

__all__: Final = [
    "FillsWindowSummary",
    "FillProvider",
    "MarketDataProvider",
    "PositionProvider",
    "PositionRiskView",
    "RiskDataPipeline",
    "RiskDataPipelineError",
    "RiskLimitsProvider",
    "RiskSnapshot",
    "RiskSnapshotInput",
    "assemble_risk_snapshot",
]


class RiskDataPipelineError(ZephyrBaseError):
    """风控数据底座错误（持仓真源缺失 / 快照装配不变量违例）。"""

    error_code = "ZA-RK-0069"


# ──────────────────────────────────────────────────────────────────────────────
# 数据真源协议（依赖注入位；运行时接线到既有 data/ex_core 层实现）
# ──────────────────────────────────────────────────────────────────────────────


class PositionProvider(Protocol):
    """持仓真源协议（生产接线: ex_core PositionTracker / OMS）。"""

    def get_position_snapshot(self) -> PositionSnapshot:
        """返回当前持仓快照（CTR-006）。"""
        ...


class MarketDataProvider(Protocol):
    """行情真源协议（生产接线: D_DATA 数据层查询接口）。"""

    def get_latest_quotes(self, symbols: Sequence[str]) -> Mapping[str, NormalizedMarketData]:
        """返回指定标的的最新行情（CTR-001），缺失标的可不出现在结果中。"""
        ...


class FillProvider(Protocol):
    """成交真源协议（生产接线: ex_core 成交回报/审计日志）。"""

    def get_fills_since(self, start: datetime) -> Sequence[Fill]:
        """返回 start 以来的成交回报列表（CTR-005）。"""
        ...


class RiskLimitsProvider(Protocol):
    """限额真源协议（生产接线: D_RISK 限额计算引擎）。"""

    def get_current_limits(self) -> RiskLimits:
        """返回当前生效的风险限额（CTR-003）。"""
        ...


# ──────────────────────────────────────────────────────────────────────────────
# 快照契约
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class PositionRiskView:
    """单标的持仓风控视图。"""

    symbol: str
    quantity: Decimal
    price_available: bool
    last_price: Decimal | None = None
    market_value: Decimal | None = None
    weight: float | None = None
    sellable_quantity: Decimal | None = None  # T+1 可卖数量接口位（无真源时 None）


@dataclass(frozen=True)
class FillsWindowSummary:
    """成交窗口聚合摘要（CTR-005 无 side 字段，不做买卖方向推断）。"""

    window_start: datetime
    window_end: datetime
    fill_count: int
    total_notional: Decimal
    total_commission: Decimal
    symbols: tuple[str, ...]


@dataclass(frozen=True)
class RiskSnapshot:
    """统一风控快照（frozen；下游 RK-22/RK-24/EX-024 消费的唯一数据入口）。"""

    snapshot_id: str
    as_of: datetime
    portfolio_id: str
    cash: Decimal
    nav: Decimal
    total_market_value: Decimal
    gross_leverage: float
    positions: tuple[PositionRiskView, ...]
    fills_summary: FillsWindowSummary
    limits: RiskLimits | None
    missing_price_symbols: tuple[str, ...]
    suspended_held_symbols: tuple[str, ...]
    degraded: bool
    data_warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class RiskSnapshotInput:
    """快照装配输入（>7 参数收 dataclass 纪律）。"""

    position_snapshot: PositionSnapshot
    quotes: Mapping[str, NormalizedMarketData]
    fills: Iterable[Fill]
    limits: RiskLimits | None
    as_of: datetime
    sellable_quantities: Mapping[str, Decimal] | None = None
    snapshot_id: str | None = None
    initial_warnings: tuple[str, ...] = ()


# ──────────────────────────────────────────────────────────────────────────────
# 纯函数装配核心（可单测）
# ──────────────────────────────────────────────────────────────────────────────


def _summarize_fills(fills: Iterable[Fill], *, window_start: datetime, window_end: datetime) -> FillsWindowSummary:
    fill_list = list(fills)
    total_notional = Decimal("0")
    total_commission = Decimal("0")
    symbols: set[str] = set()
    for fill in fill_list:
        total_notional += fill.fill_price * fill.filled_quantity
        total_commission += fill.commission
        symbols.add(fill.symbol)
    return FillsWindowSummary(
        window_start=window_start,
        window_end=window_end,
        fill_count=len(fill_list),
        total_notional=total_notional,
        total_commission=total_commission,
        symbols=tuple(sorted(symbols)),
    )


def assemble_risk_snapshot(snapshot_input: RiskSnapshotInput) -> RiskSnapshot:
    """装配统一风控快照（纯函数：同输入必同输出，可独立单测）。

    不变量：
      - nav = cash + Σ(可得市价的持仓市值)；nav <= 0 → RiskDataPipelineError
      - 持仓 quantity < 0 → RiskDataPipelineError（B-018 纯多头体系，负持仓=账本异常）
      - 缺价持仓 market_value/weight=None 且计入 missing_price_symbols（不静默补零）
      - quantity == 0 的持仓条目不计入快照视图
    """
    pos_snap = snapshot_input.position_snapshot
    quotes = snapshot_input.quotes
    warnings: list[str] = list(snapshot_input.initial_warnings)

    views: list[PositionRiskView] = []
    missing: list[str] = []
    suspended_held: list[str] = []
    total_market_value = Decimal("0")

    for symbol in sorted(pos_snap.holdings):
        quantity = pos_snap.holdings[symbol]
        if quantity < 0:
            raise RiskDataPipelineError(
                f"持仓数量异常: {symbol} quantity={quantity}（纯多头体系不允许负持仓）",
                details={"symbol": symbol, "quantity": str(quantity)},
            )
        if quantity == 0:
            continue
        quote = quotes.get(symbol)
        sellable = (
            snapshot_input.sellable_quantities.get(symbol) if snapshot_input.sellable_quantities is not None else None
        )
        if quote is None:
            missing.append(symbol)
            views.append(
                PositionRiskView(
                    symbol=symbol,
                    quantity=quantity,
                    price_available=False,
                    sellable_quantity=sellable,
                )
            )
            continue
        market_value = quantity * quote.close
        total_market_value += market_value
        if quote.is_suspended:
            suspended_held.append(symbol)
        views.append(
            PositionRiskView(
                symbol=symbol,
                quantity=quantity,
                price_available=True,
                last_price=quote.close,
                market_value=market_value,
                sellable_quantity=sellable,
            )
        )

    nav = pos_snap.cash + total_market_value
    if nav <= 0:
        raise RiskDataPipelineError(
            f"组合净值非正: nav={nav}（无法派生权重/杠杆，Fail-Closed）",
            details={"nav": str(nav), "cash": str(pos_snap.cash)},
        )

    if missing:
        warnings.append(f"missing_prices:{','.join(missing)}")
    if suspended_held:
        warnings.append(f"suspended_held:{','.join(suspended_held)}")
    if snapshot_input.limits is None:
        warnings.append("limits_unavailable")

    # 权重二次派生（nav 确定后回填，保持视图 frozen 语义：重建替换）
    finalized_views: list[PositionRiskView] = []
    for view in views:
        weight = float(view.market_value / nav) if view.market_value is not None else None
        finalized_views.append(
            PositionRiskView(
                symbol=view.symbol,
                quantity=view.quantity,
                price_available=view.price_available,
                last_price=view.last_price,
                market_value=view.market_value,
                weight=weight,
                sellable_quantity=view.sellable_quantity,
            )
        )

    as_of = snapshot_input.as_of
    window_start = as_of.replace(hour=0, minute=0, second=0, microsecond=0)
    degraded = bool(missing) or snapshot_input.limits is None or bool(snapshot_input.initial_warnings)

    return RiskSnapshot(
        snapshot_id=snapshot_input.snapshot_id or f"rs-{uuid.uuid4().hex[:12]}",
        as_of=as_of,
        portfolio_id=pos_snap.portfolio_id,
        cash=pos_snap.cash,
        nav=nav,
        total_market_value=total_market_value,
        gross_leverage=float(total_market_value / nav),
        positions=tuple(finalized_views),
        fills_summary=_summarize_fills(snapshot_input.fills, window_start=window_start, window_end=as_of),
        limits=snapshot_input.limits,
        missing_price_symbols=tuple(missing),
        suspended_held_symbols=tuple(suspended_held),
        degraded=degraded,
        data_warnings=tuple(warnings),
    )


# ──────────────────────────────────────────────────────────────────────────────
# 编排层（provider 接线 → 纯函数装配；只编排不重造）
# ──────────────────────────────────────────────────────────────────────────────


class RiskDataPipeline:
    """风控数据管道：从注入的数据真源拉取并装配 RiskSnapshot。"""

    def __init__(
        self,
        position_provider: PositionProvider,
        market_data_provider: MarketDataProvider,
        fill_provider: FillProvider,
        limits_provider: RiskLimitsProvider,
    ) -> None:
        self._position_provider = position_provider
        self._market_data_provider = market_data_provider
        self._fill_provider = fill_provider
        self._limits_provider = limits_provider

    def build_snapshot(
        self,
        as_of: datetime | None = None,
        *,
        sellable_quantities: Mapping[str, Decimal] | None = None,
    ) -> RiskSnapshot:
        """构建当前时刻统一风控快照。

        Fail-Closed 分级：
          - 持仓真源失败 → RiskDataPipelineError（不出快照）
          - 行情/成交/限额失败 → degraded 快照 + data_warnings（缺价不补零）
        """
        as_of = as_of or datetime.now(UTC)
        warnings: list[str] = []

        try:
            position_snapshot = self._position_provider.get_position_snapshot()
        except Exception as exc:  # noqa: BLE001 — Fail-Closed 包装后上抛
            raise RiskDataPipelineError(
                f"持仓真源不可用，拒绝产出风控快照: {exc}",
                details={"provider_error": str(exc)},
            ) from exc

        held_symbols = [s for s, q in sorted(position_snapshot.holdings.items()) if q > 0]
        quotes: Mapping[str, NormalizedMarketData]
        try:
            quotes = self._market_data_provider.get_latest_quotes(held_symbols)
        except Exception as exc:  # noqa: BLE001 — 降级为空行情
            _logger.error("RISK_PIPELINE_MARKET_DATA_UNAVAILABLE error=%s", exc)
            warnings.append("market_data_unavailable")
            quotes = {}

        try:
            day_start = as_of.replace(hour=0, minute=0, second=0, microsecond=0)
            fills: Iterable[Fill] = self._fill_provider.get_fills_since(day_start)
        except Exception as exc:  # noqa: BLE001 — 降级为空成交
            _logger.error("RISK_PIPELINE_FILLS_UNAVAILABLE error=%s", exc)
            warnings.append("fills_unavailable")
            fills = ()

        limits: RiskLimits | None
        try:
            limits = self._limits_provider.get_current_limits()
        except Exception as exc:  # noqa: BLE001 — 降级为无限额
            _logger.error("RISK_PIPELINE_LIMITS_UNAVAILABLE error=%s", exc)
            warnings.append("limits_provider_error")
            limits = None

        return assemble_risk_snapshot(
            RiskSnapshotInput(
                position_snapshot=position_snapshot,
                quotes=quotes,
                fills=fills,
                limits=limits,
                as_of=as_of,
                sellable_quantities=sellable_quantities,
                initial_warnings=tuple(warnings),
            )
        )
