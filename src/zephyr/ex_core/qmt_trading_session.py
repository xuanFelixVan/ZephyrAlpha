# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint_qmt_file_bridge.md
# [MODULE] zephyr.ex_core.qmt_trading_session
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.adapters.qmt_file_bridge_integration; zephyr.ex_core.order_manager; zephyr.governance.strategies.strategy_base
# [CONSUMERS] scripts.construction.test_qmt_file_bridge_full; scripts.start_paper_session
# [STARTUP] manual
# [MATURITY] draft
# [INVARIANTS] env 校验先行(ValueError); start 才连接; 策略层只面对 Session 不面对 Broker
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/ex_core/test_qmt_trading_session.py
# [A_module] module_id=MOD-L06-001-QMTFB | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
QMT Trading Session——QMT 文件桥交易会话（一键装配）

职责:
  - 策略层无感知入口：env + universe + strategy + 两个 provider 即可起跑
  - 内部装配 OrderManager + QmtFileBridgeAssembly（broker + 可选算法队列）
  - 生命周期：start() 连接全部通道，stop() 全部断开

约束:
  - env="real"(实盘) / env="sim"(模拟)，构造期校验（ValueError）
  - 价格/信号均为 Callable 注入，不耦合具体数据源

SSoT: docs/03_modules/_domain_execution_core/blueprint_qmt_file_bridge.md

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: env 参数
#   fields: 参数 env（无注解）
#   code: qmt_trading_session.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: universe 参数
#   fields: 参数 universe（无注解）
#   code: qmt_trading_session.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: strategy 参数
#   fields: 参数 strategy（无注解）
#   code: qmt_trading_session.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: signal_provider 参数
#   fields: 参数 signal_provider（无注解）
#   code: qmt_trading_session.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① QmtTradingSession
#   name_en: QmtTradingSession
#   intro: QMT 文件桥交易会话
#   desc: QMT 文件桥交易会话 Usage: session = QmtTradingSession( env="sim", universe=["510300.SH"], strate…；公共方法（定义序）: order_m…
#   inputs: env universe strategy signal_provider price_provider options
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: QmtTradingSession
#   downstream: scripts.construction.test_qmt_file_bridge_full; scripts.start_paper_session
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
from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal

from zephyr.ex_core.adapters.qmt_file_bridge_integration import QmtFileBridgeAssembly
from zephyr.ex_core.order_manager import OrderManager
from zephyr.governance.strategies.strategy_base import StrategyBase
from zephyr.shared.contracts.position import PositionSnapshot

_logger = logging.getLogger(__name__)

_VALID_ENVS: tuple[str, ...] = ("real", "sim")


@dataclass(frozen=True)
class QmtSessionOptions:
    """会话可选参数（调优项，默认值即生产配置）"""

    enable_algo_queue: bool = False  # 是否启用算法单本地排队
    queue_interval: float = 180.0  # 队列默认发送间隔（秒）
    sync_interval: float = 3.0  # 柜台同步轮询间隔（秒）


class QmtTradingSession:
    """QMT 文件桥交易会话

    Usage:
        session = QmtTradingSession(
            env="sim",
            universe=["510300.SH"],
            strategy=my_strategy,
            signal_provider=my_signal_fn,
            price_provider=my_price_fn,
            options=QmtSessionOptions(enable_algo_queue=True, queue_interval=180.0),
        )
        session.start()
        snapshot = session.get_positions()
        session.stop()
    """

    def __init__(
        self,
        env: str,
        universe: list[str],
        strategy: StrategyBase,
        signal_provider: Callable[[list[str]], dict[str, float]],
        price_provider: Callable[[list[str]], dict[str, Decimal]],
        options: QmtSessionOptions | None = None,
    ):
        """初始化会话

        Args:
            env: 环境标识 "real"(实盘) 或 "sim"(模拟)
            universe: 交易标的池
            strategy: 策略实例（StrategyBase）
            signal_provider: 信号函数 symbols -> {symbol: signal}
            price_provider: 价格函数 symbols -> {symbol: price}
            options: 可选调优参数（QmtSessionOptions）

        Raises:
            ValueError: 非法环境标识
        """
        if env not in _VALID_ENVS:
            raise ValueError(f"非法环境标识: {env}，必须是 'real' 或 'sim'")

        opts = options or QmtSessionOptions()
        self._env = env
        self._broker_id = f"qmt_{env}"
        self._universe = list(universe)
        self._strategy = strategy
        self._signal_provider = signal_provider
        self._price_provider = price_provider

        self._order_manager = OrderManager()
        self._assembly = QmtFileBridgeAssembly(
            self._order_manager,
            enable_real=(env == "real"),
            enable_sim=(env == "sim"),
            sync_interval=opts.sync_interval,
            enable_algo_queue=opts.enable_algo_queue,
            queue_interval=opts.queue_interval,
        )
        self._started = False

    # ── 暴露给上层/测试的组件 ──

    @property
    def order_manager(self) -> OrderManager:
        return self._order_manager

    @property
    def assembly(self) -> QmtFileBridgeAssembly:
        return self._assembly

    @property
    def universe(self) -> list[str]:
        return list(self._universe)

    @property
    def strategy(self) -> StrategyBase:
        return self._strategy

    # ── 生命周期 ──

    def start(self) -> bool:
        """装配并连接全部通道，返回是否全部连接成功"""
        self._assembly.assemble()
        results = self._assembly.connect_all()
        for broker_id, ok in results.items():
            _logger.info("QmtTradingSession connect %s: %s", broker_id, "OK" if ok else "FAIL")
        self._started = all(results.values())
        if not self._started:
            _logger.error("QmtTradingSession start 部分连接失败: %s", results)
        return self._started

    def stop(self) -> None:
        """断开全部通道"""
        self._assembly.disconnect_all()
        self._started = False
        _logger.info("QmtTradingSession stopped env=%s", self._env)

    # ── 查询 ──

    def get_positions(self) -> PositionSnapshot:
        """持仓快照（走当前 env 的 broker）"""
        broker = self._assembly.get_broker(self._broker_id)
        if broker is None:
            raise RuntimeError(f"broker 未装配: {self._broker_id}")
        return broker.get_positions()


if __name__ == "__main__":
    # 冒烟：仅验证构造与 env 校验
    from unittest.mock import MagicMock

    s = QmtTradingSession(
        env="sim",
        universe=["510300.SH"],
        strategy=MagicMock(),
        signal_provider=MagicMock(),
        price_provider=MagicMock(),
    )
    print("QmtTradingSession smoke ok:", s._broker_id)
