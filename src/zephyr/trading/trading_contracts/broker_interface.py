# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.trading.trading_contracts.broker_interface
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.trading_contracts.execution.fill; zephyr.trading.trading_contracts.execution.order; zephyr.trading.trading_contracts.execution.position
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L06-001-broker_interface | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# ARCH-GOV-SHIM-001 阶段2：从 governance/trading_contracts/broker_interface.py 迁移至 canonical 路径

# ---
# domain: ex_core
# category: broker_interface
# status: active
# created: "2026-05-05"
# ---

"""D_EXECUTION_CORE — BrokerInterface

Hand-maintained OCP extension point. DO NOT overwrite via codegen.

CTR 契约：
  OCP-003  BrokerInterface   券商扩展点

SSoT: cross_layer_contracts.yaml v3.0 -> OCP-003
"""

from __future__ import annotations

import abc
from collections.abc import Callable

from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.order import Order
from zephyr.shared.contracts.position import PositionSnapshot

FillCallback = Callable[[Fill], None]


class BrokerInterface(abc.ABC):
    """券商接口抽象基类（OCP-003 OCP 扩展点）

    所有券商适配器 MUST 实现此接口。
    支持同时接入多家券商，通过 SOR 路由选择最优执行通道。
    """

    @property
    @abc.abstractmethod
    def broker_id(self) -> str:
        """券商唯一标识（如 ib, futu, longport, simulation）"""
        ...

    @abc.abstractmethod
    def connect(self) -> bool:
        """建立连接。返回 True = 成功。"""
        ...

    @abc.abstractmethod
    def disconnect(self) -> None:
        """断开连接"""
        ...

    @abc.abstractmethod
    def submit_order(self, order: Order) -> str:
        """发送委托。返回 broker_order_id。"""
        ...

    @abc.abstractmethod
    def cancel_order(self, broker_order_id: str) -> bool:
        """撤单。返回 True = 成功。"""
        ...

    @abc.abstractmethod
    def query_order(self, broker_order_id: str) -> Order | None:
        """查询委托状态"""
        ...

    @abc.abstractmethod
    def get_positions(self) -> PositionSnapshot:
        """查询当前持仓"""
        ...

    def register_fill_callback(self, callback: FillCallback) -> None:
        """注册成交回调（可选）"""
        pass


__all__ = ["BrokerInterface", "FillCallback"]
