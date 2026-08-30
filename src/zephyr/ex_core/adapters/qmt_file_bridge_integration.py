# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint_qmt_file_bridge.md
# [MODULE] zephyr.ex_core.adapters.qmt_file_bridge_integration
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.adapters.qmt_file_bridge_broker; zephyr.ex_core.local_order_queue; zephyr.ex_core.order_manager
# [CONSUMERS] zephyr.ex_core.qmt_trading_session; scripts.construction.test_qmt_file_bridge_e2e
# [STARTUP] manual
# [MATURITY] draft
# [INVARIANTS] 双实例物理隔离(enable_real/enable_sim); 装配即注册; 连接即启动同步+队列
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] scripts.construction.test_qmt_file_bridge_e2e
# [A_module] module_id=MOD-L06-001-QMTFB | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
QMT File Bridge Assembly——文件桥一键装配器

职责:
  - 创建并注册 QmtFileBridgeBroker 双实例（real/sim 物理隔离）
  - 可选创建 LocalOrderQueue（算法单排队）
  - 成交回调接线：broker → OrderManager._on_fill
  - 统一连接/断开生命周期

SSoT: docs/03_modules/_domain_execution_core/blueprint_qmt_file_bridge.md

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: order_manager 参数
#   fields: 参数 order_manager（无注解）
#   code: qmt_file_bridge_integration.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: enable_real 参数
#   fields: 参数 enable_real（无注解）
#   code: qmt_file_bridge_integration.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: enable_sim 参数
#   fields: 参数 enable_sim（无注解）
#   code: qmt_file_bridge_integration.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: sync_interval 参数
#   fields: 参数 sync_interval（无注解）
#   code: qmt_file_bridge_integration.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① QmtFileBridgeAssembly
#   name_en: QmtFileBridgeAssembly
#   intro: QMT 文件桥装配器
#   desc: QMT 文件桥装配器 Usage: order_manager = OrderManager() assembly = QmtFileBridgeAssembly( order_…；公共方法（定义序）: broker_…
#   inputs: order_manager enable_real enable_sim sync_interval enable_algo_queue…
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: QmtFileBridgeAssembly
#   downstream: zephyr.ex_core.qmt_trading_session; scripts.construction.test_qmt_file_bridge_e…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging

from zephyr.ex_core.adapters.qmt_file_bridge_broker import (
    QmtFileBridgeBroker,
    check_broker_health,
)
from zephyr.ex_core.adapters.qmt_file_bridge_quote import QmtFileBridgeQuoteProvider
from zephyr.ex_core.local_order_queue import LocalOrderQueue
from zephyr.ex_core.order_manager import OrderManager

_logger = logging.getLogger(__name__)


class QmtFileBridgeAssembly:
    """QMT 文件桥装配器

    Usage:
        order_manager = OrderManager()
        assembly = QmtFileBridgeAssembly(
            order_manager, enable_real=False, enable_sim=True, sync_interval=3.0,
        )
        assembly.assemble()
        results = assembly.connect_all()   # {"qmt_sim": True}
        broker = assembly.get_broker("qmt_sim")
        queue = assembly.get_queue("qmt_sim")
        assembly.disconnect_all()
    """

    def __init__(
        self,
        order_manager: OrderManager,
        enable_real: bool = False,
        enable_sim: bool = True,
        sync_interval: float = 3.0,
        enable_algo_queue: bool = False,
        queue_interval: float = 180.0,
    ):
        """初始化装配器

        Args:
            order_manager: 订单管理器（broker 注册与成交回填终点）
            enable_real: 是否启用实盘实例（默认关闭，安全）
            enable_sim: 是否启用模拟实例
            sync_interval: 柜台同步轮询间隔（秒）
            enable_algo_queue: 是否为各实例创建 LocalOrderQueue
            queue_interval: 队列默认发送间隔（秒）
        """
        self._order_manager = order_manager
        self._enable_real = enable_real
        self._enable_sim = enable_sim
        self._sync_interval = sync_interval
        self._enable_algo_queue = enable_algo_queue
        self._queue_interval = queue_interval

        self._brokers: dict[str, QmtFileBridgeBroker] = {}
        self._queues: dict[str, LocalOrderQueue] = {}
        self._quotes: dict[str, QmtFileBridgeQuoteProvider] = {}
        self._assembled = False

    @property
    def broker_ids(self) -> list[str]:
        return list(self._brokers.keys())

    def assemble(self) -> None:
        """创建并注册 broker/queue 实例"""
        envs: list[str] = []
        if self._enable_sim:
            envs.append("sim")
        if self._enable_real:
            envs.append("real")

        for env in envs:
            broker = QmtFileBridgeBroker(env=env, sync_interval=self._sync_interval)
            # 成交回调接线：broker → OrderManager._on_fill
            broker.register_fill_callback(self._order_manager._on_fill)
            self._order_manager.register_broker(broker.broker_id, broker)
            self._brokers[broker.broker_id] = broker

            if self._enable_algo_queue:
                queue = LocalOrderQueue(
                    self._order_manager,
                    broker_id=broker.broker_id,
                    default_interval=self._queue_interval,
                )
                self._queues[broker.broker_id] = queue

        self._assembled = True
        _logger.info(
            "QmtFileBridgeAssembly assembled brokers=%s queues=%s",
            list(self._brokers),
            list(self._queues),
        )

    def connect_all(self) -> dict[str, bool]:
        """连接所有 broker 并启动队列"""
        if not self._assembled:
            self.assemble()
        results: dict[str, bool] = {}
        for broker_id, broker in self._brokers.items():
            ok = broker.connect()
            results[broker_id] = ok
            if ok and broker_id in self._queues:
                self._queues[broker_id].start()
        return results

    def disconnect_all(self) -> None:
        """停止队列并断开所有 broker"""
        for queue in self._queues.values():
            queue.stop()
        for broker in self._brokers.values():
            broker.disconnect()

    def get_broker(self, broker_id: str) -> QmtFileBridgeBroker | None:
        """按 broker_id 取 broker 实例（未装配返回 None 并告警）"""
        broker = self._brokers.get(broker_id)
        if broker is None:
            _logger.warning("get_broker 未装配: %s", broker_id)
        return broker

    def get_queue(self, broker_id: str) -> LocalOrderQueue | None:
        """按 broker_id 取订单队列（未启用算法队列返回 None）"""
        return self._queues.get(broker_id)

    def get_quote_provider(self, broker_id: str) -> QmtFileBridgeQuoteProvider | None:
        """按 broker_id 取反向行情桥 Provider（懒创建，env 自 broker_id 派生）

        行情文件由 QMT 端 ZEPHYR_QUOTE v15 策略写入，未启动时 connect 会
        抛出 QmtFileBridgeQuoteError（调用方负责确认 QMT 端就绪）。
        """
        if broker_id not in self._brokers:
            return None
        if broker_id not in self._quotes:
            env = broker_id.removeprefix("qmt_")
            self._quotes[broker_id] = QmtFileBridgeQuoteProvider(env=env)
        return self._quotes[broker_id]

    def health_check(self) -> dict:
        """装配体健康检查（前端监控数据源，聚合所有组件）

        等级聚合规则：任一组件 down 则整体 down，任一 degraded 则整体 degraded。
        行情 Provider 仅在显式调用过 get_quote_provider 后纳入监控。
        """
        components: dict[str, dict] = {}
        for broker_id, broker in self._brokers.items():
            components[broker_id] = check_broker_health(broker)
        for broker_id, queue in self._queues.items():
            components[f"queue_{broker_id}"] = queue.health_check()
        for broker_id, quote in self._quotes.items():
            components[f"quote_{broker_id}"] = quote.health_check()

        levels = [c["level"] for c in components.values()]
        if "down" in levels:
            level = "down"
        elif "degraded" in levels:
            level = "degraded"
        else:
            level = "ok"
        return {
            "component": "qmt_file_bridge_assembly",
            "type": "assembly",
            "ok": level == "ok",
            "level": level,
            "components": components,
        }
