# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint_qmt_file_bridge.md
# [MODULE] zephyr.ex_core.adapters.qmt_file_bridge_integration
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.adapters.qmt_file_bridge_broker; zephyr.ex_core.local_order_queue; zephyr.ex_core.order_manager; zephyr.ex_core.adapters.qmt_file_bridge_quote; zephyr.ex_core.execution_report_producer(断点E4生产端)
# [CONSUMERS] zephyr.ex_core.qmt_trading_session; scripts.construction.test_qmt_file_bridge_e2e
# [STARTUP] manual
# [MATURITY] draft
# [INVARIANTS] 双实例物理隔离(enable_real/enable_sim); 装配即注册; 连接即启动同步+队列; execution_report 生产端默认接线(断点E4闭合, configure_execution_report 可关/可注入 writer)
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

# [ALGO_FLOW] external: docs/03_modules/_domain_execution_core/algo_flow/qmt_file_bridge_integration.yaml
"""

from __future__ import annotations

import logging

from zephyr.ex_core.adapters.qmt_file_bridge_broker import (
    QmtFileBridgeBroker,
    check_broker_health,
)
from zephyr.ex_core.adapters.qmt_file_bridge_quote import QmtFileBridgeQuoteProvider
from zephyr.ex_core.execution_report_producer import ExecutionReportProducer
from zephyr.ex_core.local_order_queue import LocalOrderQueue
from zephyr.ex_core.order_manager import OrderManager
from zephyr.governance.adapters.risk_validation_bridge import RiskValidationPort

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
        risk_validator: RiskValidationPort | None = None,
    ):
        """初始化装配器

        Args:
            order_manager: 订单管理器（broker 注册与成交回填终点）
            enable_real: 是否启用实盘实例（默认关闭，安全）
            enable_sim: 是否启用模拟实例
            sync_interval: 柜台同步轮询间隔（秒）
            enable_algo_queue: 是否为各实例创建 LocalOrderQueue
            queue_interval: 队列默认发送间隔（秒）
            risk_validator: 风控校验端口（R-H5E-1，可选）。仅注入 sim 实例——
                sim 订单进桥前强制前置校验（fail-closed）；real 实例**显式不注入**
                （保持现状，实盘账户启用=Owner 门，裁定 #338⑤）。
        """
        self._order_manager = order_manager
        self._enable_real = enable_real
        self._enable_sim = enable_sim
        self._sync_interval = sync_interval
        self._enable_algo_queue = enable_algo_queue
        self._queue_interval = queue_interval
        self._risk_validator = risk_validator

        self._brokers: dict[str, QmtFileBridgeBroker] = {}
        self._queues: dict[str, LocalOrderQueue] = {}
        self._quotes: dict[str, QmtFileBridgeQuoteProvider] = {}
        self._producers: dict[str, ExecutionReportProducer] = {}
        self._assembled = False
        # 断点 E4：execution_report 生产端接线默认**开**（表在/DDL 在/契约在/
        # build_execution_report 在，唯缺生产调用方 → 台账面恒 0 行）。
        # 开关不放进 __init__ 参数位（该签名已 7 参，再加撞 NO-LONG-PARAM-LIST），
        # 走 configure_execution_report()；测试用 writer 注入即可零接触生产库。
        self._enable_execution_report = True
        self._execution_report_writer = None

    def configure_execution_report(
        self,
        enabled: bool = True,
        writer: object | None = None,
    ) -> None:
        """配置 execution_report 生产端（assemble 前调用生效）。

        Args:
            enabled: 是否在装配时接线生产端（默认开=断点 E4 闭合态）。
            writer: TSV 写入函数注入位（测试用假 writer 零接触生产库）；
                None = 生产路径 ``ch_writer.write_tsv_outcome``。
        """
        self._enable_execution_report = enabled
        self._execution_report_writer = writer

    @property
    def execution_report_producers(self) -> dict[str, ExecutionReportProducer]:
        """只读：各 broker 的生产端实例（未接线/未装配为空 dict）。"""
        return dict(self._producers)

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
            # R-H5E-1：风控校验仅注入 sim 实例（sim 进桥前 fail-closed 闸）；
            # real 实例显式不注入——实盘路径保持现状，启用=Owner 门（裁定 #338⑤）
            broker = QmtFileBridgeBroker(
                env=env,
                sync_interval=self._sync_interval,
                risk_validator=self._risk_validator if env == "sim" else None,
            )
            # 成交回调接线：broker → OrderManager._on_fill
            broker.register_fill_callback(self._order_manager._on_fill)
            self._order_manager.register_broker(broker.broker_id, broker)
            self._brokers[broker.broker_id] = broker

            # 断点 E4：execution_report 生产端接线（订单终态 → c1_market.execution_report）
            if self._enable_execution_report:
                producer = ExecutionReportProducer(
                    venue=broker.broker_id,
                    writer=self._execution_report_writer,
                    board_lot=100,
                )
                # 成交面走 fill 回调累积（佣金/VWAP/时间窗），订单面走同步线程轮询
                broker.register_fill_callback(producer.on_fill)
                broker.attach_execution_report_producer(producer)
                self._producers[broker.broker_id] = producer
                _logger.info("execution_report 生产端接线 broker=%s", broker.broker_id)

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
            # 断点 E4 可观测面：各 broker 生产端计数（emitted/write_failed/abandoned...）
            "execution_report": {
                bid: p.stats.as_dict() for bid, p in self._producers.items()
            },
        }
