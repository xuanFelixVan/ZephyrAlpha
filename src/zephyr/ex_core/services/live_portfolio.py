# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.services.live_portfolio
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.risk.core.risk_data_pipeline; zephyr.shared.foundation.errors
# [CONSUMERS] MOD-L06-001(TradingSession 组合视图) ; 前端看板(持仓/可用/净值)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 数据唯一入口=MOD-RK-25 RiskSnapshot(snapshot_supplier注入,禁自造数据管道); 快照装配失败→LivePortfolioError不出视图(Fail-Closed,防空仓/零净值错觉); 视图frozen不可变; 缺价持仓market_value=None不静默补零(degraded透传); 本服务只读,不改任何交易链路状态
# [MODIFY-GUARD] docs/03_modules/_domain_execution_core/blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] LivePortfolioError(ZA-EX-0021)
# [TESTS] tests/ex_core/test_live_portfolio.py
# [A_module] module_id=MOD-L06-001_live_portfolio | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
Live Portfolio Service — 实盘组合服务 (MOD-L06-001)

持仓 / 可用资金 / 净值视图。数据唯一入口为 MOD-RK-25 统一风控快照
（RiskSnapshot 契约，snapshot_supplier 注入——生产接线
RiskDataPipeline.build_snapshot，本服务不自造数据管道、不直连
miniQMT/数据库）。

Fail-Closed：快照装配失败（持仓真源不可用/nav≤0 等）→ LivePortfolioError，
不出视图（防空仓错觉导致的错误下单决策）；缺价持仓 market_value=None
透传 + degraded 标记，不静默补零。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: snapshot_supplier 参数
#   fields: 参数 snapshot_supplier（无注解）
#   code: live_portfolio.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① LivePortfolioService
#   name_en: LivePortfolioService
#   intro: 实盘组合服务（持仓/可用/净值视图，数据走 RiskSnapshot 真源注入）。
#   desc: 实盘组合服务（持仓/可用/净值视图，数据走 RiskSnapshot 真源注入）。 Args: snapshot_supplier: 风控快照供给器（生产接线 RiskDataP…；公共方法（定义序）: current…
#   inputs: snapshot_supplier
#   outputs: 返回值
#   （注：A1 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: LivePortfolioService
#   downstream: MOD-L06-001(TradingSession 组合视图) ; 前端看板(持仓/可用/净值)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Final

from zephyr.risk.core.risk_data_pipeline import RiskSnapshot
from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)

__all__: Final = [
    "LivePortfolioError",
    "LivePortfolioService",
    "LivePortfolioView",
    "LivePositionView",
]


class LivePortfolioError(ZephyrBaseError):
    """实盘组合服务错误（快照真源不可用，Fail-Closed 不出视图）。"""

    error_code = "ZA-EX-0021"


@dataclass(frozen=True)
class LivePositionView:
    """单标的实盘持仓视图（缺价标的 market_value/weight=None 不补零）。"""

    symbol: str
    quantity: Decimal
    last_price: Decimal | None
    market_value: Decimal | None
    weight: float | None
    sellable_quantity: Decimal | None  # T+1 可卖数量（无真源时 None）


@dataclass(frozen=True)
class LivePortfolioView:
    """实盘组合视图（frozen；净值/市值/现金/持仓/degraded 标记）。"""

    portfolio_id: str
    as_of: datetime
    cash: Decimal
    nav: Decimal
    total_market_value: Decimal
    gross_leverage: float
    positions: tuple[LivePositionView, ...]
    missing_price_symbols: tuple[str, ...]
    degraded: bool
    data_warnings: tuple[str, ...]


class LivePortfolioService:
    """实盘组合服务（持仓/可用/净值视图，数据走 RiskSnapshot 真源注入）。

    Args:
        snapshot_supplier: 风控快照供给器（生产接线
            RiskDataPipeline.build_snapshot；异常一律包装为
            LivePortfolioError 上抛，Fail-Closed）。
    """

    def __init__(self, snapshot_supplier: Callable[[], RiskSnapshot]) -> None:
        self._snapshot_supplier = snapshot_supplier

    def current_view(self) -> LivePortfolioView:
        """当前组合视图。快照不可用→LivePortfolioError（Fail-Closed）。"""
        snapshot = self._load_snapshot()
        return LivePortfolioView(
            portfolio_id=snapshot.portfolio_id,
            as_of=snapshot.as_of,
            cash=snapshot.cash,
            nav=snapshot.nav,
            total_market_value=snapshot.total_market_value,
            gross_leverage=snapshot.gross_leverage,
            positions=tuple(
                LivePositionView(
                    symbol=pos.symbol,
                    quantity=pos.quantity,
                    last_price=pos.last_price,
                    market_value=pos.market_value,
                    weight=pos.weight,
                    sellable_quantity=pos.sellable_quantity,
                )
                for pos in snapshot.positions
            ),
            missing_price_symbols=snapshot.missing_price_symbols,
            degraded=snapshot.degraded,
            data_warnings=snapshot.data_warnings,
        )

    def available_cash(self) -> Decimal:
        """可用资金（当前口径=快照现金；资金冻结真源就绪后在此扣减）。"""
        return self._load_snapshot().cash

    def position_of(self, symbol: str) -> LivePositionView | None:
        """单标的持仓视图；未持仓返回 None（未持仓≠持仓为 0，调用方可区分）。"""
        view = self.current_view()
        for position in view.positions:
            if position.symbol == symbol:
                return position
        return None

    def _load_snapshot(self) -> RiskSnapshot:
        try:
            return self._snapshot_supplier()
        except Exception as exc:  # noqa: BLE001 — Fail-Closed 包装后上抛
            _logger.error("组合快照真源不可用(拒绝产出组合视图): %s", type(exc).__name__)
            raise LivePortfolioError(
                f"组合快照真源不可用，拒绝产出组合视图: {exc}",
                details={"supplier_error": str(exc)},
            ) from exc
