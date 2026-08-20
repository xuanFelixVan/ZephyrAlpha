# [BLUEPRINT] MOD-EX-050 | docs/03_modules/_domain_execution_core/repository_interface/blueprint.md
# [MODULE] zephyr.ex_core.repository_interface
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.shared.contracts.order; zephyr.shared.contracts.position; zephyr.shared.contracts.enums.order_enums
# [CONSUMERS] D_EX_CORE域内模块 ; OrderManager (阶段2集成) ; PositionTracker (阶段2集成)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] ABC不可直接实例化; save幂等; 仓储不负责业务校验; Decimal全程
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RepositoryError(ZA-EX-050-01); OrderNotFoundError(ZA-EX-050-02); SnapshotNotFoundError(ZA-EX-050-03)
# [TESTS] tests/ex_core/test_repository_interface.py
# [A_module] module_id=MOD-EX-050 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D_EX_CORE — Repository Interface (执行域仓储接口)

D_EX_CORE 域的持久化抽象层——定义 Order (CTR-004) 和 PositionSnapshot (CTR-006)
的仓储接口，提供内存实现供开发/测试使用。上层业务模块（OrderManager / PositionTracker）
将来可通过依赖注入替换具体实现，实现持久化策略可替换。

遵循 DDD Repository 模式：仓储只负责聚合根的存取，不负责业务逻辑（状态转换/校验等）。

设计真源: D-EX-CORE-50 "Order/Position聚合根持久化仓储接口"
蓝图: docs/03_modules/_domain_execution_core/repository_interface/blueprint.md
SSoT: depgraph MOD-EX-050

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 订单聚合根 Order（CTR-004）
#   fields: order_id + status + symbol + side + quantity + limit_price 等
#   code: OrderRepository.save(order) L101
# - id: I2
#   name: 持仓快照 PositionSnapshot（CTR-006）
#   fields: portfolio_id + as_of_timestamp + cash + holdings + market_values
#   code: PositionSnapshotRepository.save(snapshot) L142
# - id: I3
#   name: 存储后端选择 backend
#   fields: 字符串，当前仅支持 "memory"（阶段2扩展 sqlite/postgres）
#   code: create_order_repository(backend) L266
# 层: 算法
# - id: A1
#   name_zh: ① 仓储抽象接口定义
#   name_en: OrderRepository / PositionSnapshotRepository（ABC）
#   intro: 用抽象基类定义订单和持仓快照的存取契约，不含任何业务逻辑
#   desc: DDD Repository模式：save/get/get_by_status/get_open_orders/delete/count 等抽象方法；仓储只负责聚合根存取，不负责状态转换/业务校验
#   inputs: I1 I2
#   outputs: 抽象接口契约
#   invariant: ABC不可直接实例化；save幂等；仓储不负责业务校验
# - id: A2
#   name_zh: ② 内存仓储实现
#   name_en: InMemoryOrderRepository / InMemoryPositionSnapshotRepository
#   intro: 用字典实现开发/测试用的内存版仓储，快照按时间升序存历史
#   desc: 订单 dict[order_id, Order] 同ID覆盖（幂等）；快照 dict[portfolio_id, list] 追加后按 as_of_timestamp 排序；get_open_orders 按 _OPEN_STATUSES(PENDING/SUBMITTED/PARTIAL) 过滤
#   inputs: I1 I2 A1
#   outputs: 查询结果（Order/快照 单个或列表）
# - id: A3
#   name_zh: ③ 仓储工厂函数
#   name_en: create_order_repository / create_position_snapshot_repository
#   intro: 按backend字符串创建仓储实例，不支持的backend抛异常
#   desc: backend=="memory" 返回内存实现；否则抛 RepositoryError（阶段2扩展 sqlite/postgres）
#   inputs: I3
#   outputs: Repository 实例
# 层: 输出
# - id: O1
#   name_zh: 订单查询结果
#   name_en: Order / list[Order]
#   intro: 按ID/状态/开放单/全量查到的订单，不存在返回None
#   downstream: 聚合根管理器 MOD-EX-049（注入使用）；OrderManager（阶段2集成）
# - id: O2
#   name_zh: 持仓快照查询结果
#   name_en: PositionSnapshot / list[PositionSnapshot]
#   intro: 指定组合的最新快照或按时间升序的历史快照列表
#   downstream: D_EX_CORE域内模块；PositionTracker（阶段2集成）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I1 --> A2
# I2 --> A2
# A1 --> A2
# I3 --> A3
# A3 --> A2
# A2 --> O1
# A2 --> O2
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Final

from zephyr.shared.contracts.enums.order_enums import OrderStatus
from zephyr.shared.contracts.order import Order
from zephyr.shared.contracts.position import PositionSnapshot
from zephyr.shared.foundation.errors import ZephyrBaseError

logger = logging.getLogger(__name__)

__all__: Final = [
    "OrderRepository",
    "PositionSnapshotRepository",
    "InMemoryOrderRepository",
    "InMemoryPositionSnapshotRepository",
    "create_order_repository",
    "create_position_snapshot_repository",
    "RepositoryError",
    "OrderNotFoundError",
    "SnapshotNotFoundError",
]


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class RepositoryError(ZephyrBaseError):
    """仓储操作异常基类。"""

    error_code = "ZA-EX-050-01"


class OrderNotFoundError(RepositoryError):
    """订单不存在。"""

    error_code = "ZA-EX-050-02"


class SnapshotNotFoundError(RepositoryError):
    """持仓快照不存在。"""

    error_code = "ZA-EX-050-03"


# ──────────────────────────────────────────────────────────────────────────────
# 开放订单状态集合
# ──────────────────────────────────────────────────────────────────────────────

_OPEN_STATUSES: Final[frozenset[OrderStatus]] = frozenset(
    {OrderStatus.PENDING, OrderStatus.SUBMITTED, OrderStatus.PARTIAL}
)


# ──────────────────────────────────────────────────────────────────────────────
# OrderRepository 抽象接口
# ──────────────────────────────────────────────────────────────────────────────


class OrderRepository(ABC):
    """订单仓储接口——抽象持久化层。

    遵循 DDD Repository 模式：只负责 Order 聚合根的存取，
    不负责业务逻辑（状态转换/风控校验等）。
    """

    @abstractmethod
    def save(self, order: Order) -> None:
        """保存订单（幂等——相同 order_id 覆盖旧值）。"""

    @abstractmethod
    def get(self, order_id: str) -> Order | None:
        """按 order_id 查询订单，不存在返回 None。"""

    @abstractmethod
    def get_by_status(self, status: OrderStatus) -> list[Order]:
        """按状态查询订单列表。"""

    @abstractmethod
    def get_open_orders(self) -> list[Order]:
        """查询所有开放订单（PENDING/SUBMITTED/PARTIAL）。"""

    @abstractmethod
    def get_all(self) -> list[Order]:
        """查询所有订单。"""

    @abstractmethod
    def delete(self, order_id: str) -> bool:
        """删除订单，返回是否删除成功。"""

    @abstractmethod
    def count(self) -> int:
        """订单总数。"""


# ──────────────────────────────────────────────────────────────────────────────
# PositionSnapshotRepository 抽象接口
# ──────────────────────────────────────────────────────────────────────────────


class PositionSnapshotRepository(ABC):
    """持仓快照仓储接口——抽象持久化层。

    管理 PositionSnapshot (CTR-006) 的存取，支持按 portfolio_id
    查询最新快照和历史快照列表。
    """

    @abstractmethod
    def save(self, snapshot: PositionSnapshot) -> None:
        """保存持仓快照（追加到历史列表）。"""

    @abstractmethod
    def get_latest(self, portfolio_id: str) -> PositionSnapshot | None:
        """获取指定组合的最新快照，不存在返回 None。"""

    @abstractmethod
    def get_history(self, portfolio_id: str) -> list[PositionSnapshot]:
        """获取指定组合的快照历史（按时间升序）。"""

    @abstractmethod
    def get_all(self) -> list[PositionSnapshot]:
        """查询所有组合的最新快照。"""

    @abstractmethod
    def delete(self, portfolio_id: str) -> bool:
        """删除指定组合的所有快照，返回是否删除成功。"""

    @abstractmethod
    def count(self) -> int:
        """快照总数（所有组合）。"""


# ──────────────────────────────────────────────────────────────────────────────
# InMemoryOrderRepository
# ──────────────────────────────────────────────────────────────────────────────


class InMemoryOrderRepository(OrderRepository):
    """内存订单仓储——开发/测试用。

    使用 dict 存储 Order 对象引用（不做深拷贝）。
    线程安全：阶段1不加锁（单线程使用），阶段2可加 threading.Lock。
    """

    def __init__(self) -> None:
        self._orders: dict[str, Order] = {}

    def save(self, order: Order) -> None:
        self._orders[order.order_id] = order
        logger.debug("订单保存: order_id=%s status=%s", order.order_id, order.status)

    def get(self, order_id: str) -> Order | None:
        return self._orders.get(order_id)

    def get_by_status(self, status: OrderStatus) -> list[Order]:
        return [o for o in self._orders.values() if o.status == status]

    def get_open_orders(self) -> list[Order]:
        return [o for o in self._orders.values() if o.status in _OPEN_STATUSES]

    def get_all(self) -> list[Order]:
        return list(self._orders.values())

    def delete(self, order_id: str) -> bool:
        if order_id in self._orders:
            del self._orders[order_id]
            logger.debug("订单删除: order_id=%s", order_id)
            return True
        return False

    def count(self) -> int:
        return len(self._orders)


# ──────────────────────────────────────────────────────────────────────────────
# InMemoryPositionSnapshotRepository
# ──────────────────────────────────────────────────────────────────────────────


class InMemoryPositionSnapshotRepository(PositionSnapshotRepository):
    """内存持仓快照仓储——开发/测试用。

    使用 dict[str, list[PositionSnapshot]] 存储，每个 portfolio_id 对应一个
    按时间升序排列的快照列表。
    """

    def __init__(self) -> None:
        self._snapshots: dict[str, list[PositionSnapshot]] = {}

    def save(self, snapshot: PositionSnapshot) -> None:
        history = self._snapshots.setdefault(snapshot.portfolio_id, [])
        history.append(snapshot)
        # 按时间戳排序（升序）
        history.sort(key=lambda s: s.as_of_timestamp)
        logger.debug(
            "快照保存: portfolio_id=%s timestamp=%s (history=%d)",
            snapshot.portfolio_id,
            snapshot.as_of_timestamp,
            len(history),
        )

    def get_latest(self, portfolio_id: str) -> PositionSnapshot | None:
        history = self._snapshots.get(portfolio_id)
        if not history:
            return None
        return history[-1]

    def get_history(self, portfolio_id: str) -> list[PositionSnapshot]:
        return list(self._snapshots.get(portfolio_id, []))

    def get_all(self) -> list[PositionSnapshot]:
        """返回所有组合的最新快照。"""
        return [history[-1] for history in self._snapshots.values() if history]

    def delete(self, portfolio_id: str) -> bool:
        if portfolio_id in self._snapshots:
            del self._snapshots[portfolio_id]
            logger.debug("快照删除: portfolio_id=%s", portfolio_id)
            return True
        return False

    def count(self) -> int:
        return sum(len(h) for h in self._snapshots.values())


# ──────────────────────────────────────────────────────────────────────────────
# 工厂函数
# ──────────────────────────────────────────────────────────────────────────────


def create_order_repository(backend: str = "memory") -> OrderRepository:
    """创建订单仓储。

    Args:
        backend: 存储后端（"memory" = 内存，阶段2扩展 "sqlite"/"postgres"）。

    Returns:
        OrderRepository 实例。

    Raises:
        RepositoryError: 不支持的 backend。
    """
    if backend == "memory":
        return InMemoryOrderRepository()
    raise RepositoryError(f"不支持的订单仓储后端: {backend!r}（当前仅支持 'memory'）")


def create_position_snapshot_repository(
    backend: str = "memory",
) -> PositionSnapshotRepository:
    """创建持仓快照仓储。

    Args:
        backend: 存储后端（"memory" = 内存，阶段2扩展 "sqlite"/"postgres"）。

    Returns:
        PositionSnapshotRepository 实例。

    Raises:
        RepositoryError: 不支持的 backend。
    """
    if backend == "memory":
        return InMemoryPositionSnapshotRepository()
    raise RepositoryError(f"不支持的快照仓储后端: {backend!r}（当前仅支持 'memory'）")
