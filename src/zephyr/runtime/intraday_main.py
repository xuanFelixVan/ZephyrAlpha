# [BLUEPRINT] MOD-RUNTIME_INTRADAY | self-contained (runtime entry) | §
# [MODULE] zephyr.runtime.intraday_main
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.data.tick_subscriber; zephyr.data.tick_redis_cache; zephyr.factor.core.intraday_factor_loop; zephyr.infrastructure.database_service; zephyr.data.calendar; zephyr.data.redundant_source.heartbeat_monitor; zephyr.data.alerter
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 单进程串起 tick_subscriber + IntradayFactorLoop; 启动顺序=先订阅tick再启因子循环; 停止顺序=先停因子循环再停订阅; 非交易日可--force强制运行
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] tick_subscriber启动失败->退出码1; factor_loop启动失败->停subscriber退出码1; SIGINT/SIGTERM->优雅停止退出码0
# [TESTS] tests/zephyr/runtime/test_intraday_main.py
# [A_module] module_id=MOD-RUNTIME_INTRADAY | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

盘中运行时编排器——单进程串起 tick_subscriber + IntradayFactorLoop。

把 D-DATA (tick_subscriber) → H1 Redis (tick_redis_cache) → D-FACTOR
(intraday_factor_loop) 串成端到端盘中数据流::

    QMT tick → tick_subscriber → [WAL→ClickHouse + Redis tick:{symbol}:latest]
                                         ↓
                        IntradayFactorLoop (3秒周期)
                                         ↓
                        DagExecutor 算因子 → H1 feature:{symbol}
                                         ↓
                        D-SIGNAL/D-RISK <5ms 读取

启动顺序（关键）:
    1. tick_subscriber 先启动——等 QMT 就绪 + 订阅全市场 + 预热首个 tick
       （预热完成后 Redis 里已有 tick 数据）
    2. 从 subscriber.subscribed_symbols 拿实际订阅标的
    3. IntradayFactorLoop 后启动——读 Redis tick 算因子写 H1

停止顺序（反序，保证 WAL flush 完整）:
    1. IntradayFactorLoop 先停（停止因子计算）
    2. tick_subscriber 后停（flush 残留 WAL + 取消订阅）

用法::

    python -m zephyr.runtime.intraday_main              # 交易日自动运行
    python -m zephyr.runtime.intraday_main --force      # 非交易日强制运行
    python -m zephyr.runtime.intraday_main --symbols 000001.SZ 600000.SH

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 命令行参数 argv
#   fields: --force 非交易日强制运行 + --symbols 订阅标的列表 + --cycle-seconds 因子循环周期（默认3.0秒）
#   code: main L248-270
# - id: I2
#   name: 交易日历状态
#   fields: is_trading_day() 今日是否交易日 bool
#   code: start 守卫段（模块级 is_trading_day → data.calendar 包 ASHareCalendar 委托真源）
# - id: I3
#   name: Redis 连接（H1 实例）
#   fields: redis.Redis 连接句柄（None 时经 DatabaseService 获取，测试可注入）
#   code: start L139-141
# - id: I4
#   name: QMT 全市场 tick 推送流
#   fields: TickSubscriber 订阅的 (symbol, tick dict) 推送 + subscribed_symbols 实际订阅标的
#   code: start L162-167（TickSubscriber.start）
# 层: 算法
# - id: A1
#   name_zh: ① 交易日守卫
#   name_en: IntradayRuntime.start（守卫段）
#   intro: 非交易日且未加 --force 就拒绝启动，防止空跑
#   desc: 已在运行直接返回 True；not force and not is_trading_day() 则 warning 并 return False（L127-136）
#   inputs: I1 I2
#   outputs: 启动许可 bool
# - id: A2
#   name_zh: ② 组件装配与按序启动
#   name_en: IntradayRuntime.start（编排段）
#   intro: 先起 tick 订阅预热 Redis，再起因子循环读 tick 算因子，失败回滚
#   desc: 取 Redis 连接→建 TickRedisCache→建 HeartbeatMonitor+Alerter+TickSubscriber 并 start（预热首个 tick）→取 subscribed_symbols→建 IntradayFactorLoop 并 start，因子循环启动失败则回滚停 subscriber 返回 False（L138-196）；显式 import intraday_snapshot_factors 触发因子注册（L66）
#   inputs: I1 I3 I4 A1
#   outputs: 运行中的 tick→Redis→因子→H1 双组件管线
#   invariant: 启动顺序=先订阅tick再启因子循环
# - id: A3
#   name_zh: ③ 常驻主循环
#   name_en: IntradayRuntime.run_forever
#   intro: 挂 SIGINT/SIGTERM 处理器，每 60 秒打印一次聚合 stats 直到收到退出信号
#   desc: start 失败直接返回 1；注册 _signal_handler 把信号转 KeyboardInterrupt；while _running 循环 sleep 60s + log stats()（聚合 subscriber+factor_loop 统计）（L219-245）
#   inputs: A2
#   outputs: 周期运行统计日志
# - id: A4
#   name_zh: ④ 优雅停止（反序）
#   name_en: IntradayRuntime.stop
#   intro: 先停因子循环再停 tick 订阅，保证 WAL flush 完整
#   desc: _running=False→factor_loop.stop()→tick_subscriber.stop()（flush 残留 WAL+取消订阅）（L198-208）；在 run_forever 的 finally 中调用
#   inputs: A3
#   outputs: 停止完成 + 进程退出码 0/1
#   invariant: 停止顺序=先停因子循环再停订阅（反序）
# 层: 输出
# - id: O1
#   name_zh: 端到端盘中数据面贯通
#   name_en: tick→Redis→因子→H1 管线
#   intro: tick 双写 WAL/ClickHouse+Redis tick:{symbol}:latest，因子循环写 H1 feature:{symbol} 供信号/风控层 5ms 内读取
#   downstream: 无 Python 导入下游（[CONSUMERS] 空，进程入口）；数据面供 D-SIGNAL/D-RISK 读 H1 feature
# - id: O2
#   name_zh: 进程退出码与运行统计
#   name_en: exit code + stats dict
#   intro: 0=优雅退出 1=启动失败；stats 聚合 tick_subscriber 与 factor_loop 计数
#   invariant: tick_subscriber启动失败→退出码1；SIGINT/SIGTERM→优雅停止退出码0
#   downstream: 无下游/内部使用（运维日志）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I1 --> A2
# I3 --> A2
# I4 --> A2
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A2 --> O1
# A4 --> O2
"""

from __future__ import annotations

import argparse
import datetime
import logging
import signal as sig_module
import sys
import time
from typing import TYPE_CHECKING, Final

# 治本（2026-08-03 实地演练发现 FactorRegistry 为空）：
# intraday_main 启动时未导入任何因子模块，IntradayFactorLoop._build_dag 读
# FactorRegistry.registry.keys() 拿到空列表 → "无因子可计算" → 链路空转。
# 此处显式导入盘中横截面因子模块触发 @FactorRegistry.register 注册，
# 保证 _build_dag 时注册表非空。新增盘中因子时在此追加 import 即可。
import zephyr.factor.intraday_snapshot_factors  # noqa: F401 — 注册副作用
from zephyr.data.calendar import MarketCalendar, get_market_calendar
from zephyr.data.tick_redis_cache import TickRedisCache
from zephyr.data.tick_subscriber import TickSubscriber
from zephyr.factor.core.intraday_factor_loop import IntradayFactorLoop
from zephyr.infrastructure.database_service import DatabaseService

# 向后兼容别名：保留 is_trading_day 模块级函数（测试 mock 目标）
_DEFAULT_CALENDAR: Final = get_market_calendar("ashare")


def is_trading_day(day: datetime.date | None = None) -> bool:
    """A 股交易日判定（向后兼容接口，测试 mock 目标）。"""
    return _DEFAULT_CALENDAR.is_trading_day(day)


if TYPE_CHECKING:
    import redis

logger = logging.getLogger(__name__)

# 常驻主循环 stats 日志间隔（秒）
_STATS_LOG_INTERVAL = 60.0

# 默认因子循环周期（秒，对应 miniQMT 3秒 Tick）
_DEFAULT_CYCLE_SECONDS = 3.0


class IntradayRuntime:
    """盘中运行时编排器——拉起 tick_subscriber + IntradayFactorLoop 单进程常驻。

    生命周期:
        start() → 启动 tick 订阅 + 因子循环 → run_forever() 常驻 → stop() 优雅停止

    启动顺序: tick_subscriber 先（预热 Redis tick）→ IntradayFactorLoop 后（读 Redis 算因子）。
    停止顺序: IntradayFactorLoop 先停 → tick_subscriber 后停（反序，保证 WAL flush 完整）。

    依赖注入: redis_conn / tick_subscriber / factor_loop 均可外部注入，便于测试。
    """

    def __init__(
        self,
        symbols: list[str] | None = None,
        force: bool = False,
        cycle_seconds: float = _DEFAULT_CYCLE_SECONDS,
        redis_conn: redis.Redis | None = None,
        tick_subscriber: TickSubscriber | None = None,
        factor_loop: IntradayFactorLoop | None = None,
        calendar: MarketCalendar | None = None,
    ):
        """初始化盘中运行时。

        Args:
            symbols: 订阅标的列表（None=tick_subscriber 自动获取全市场）。
            force: 非交易日强制运行（跳过 is_trading_day 守卫）。
            cycle_seconds: 因子循环周期（秒，默认3.0）。
            redis_conn: Redis 连接（None=start 时通过 DatabaseService 获取；测试可注入）。
            tick_subscriber: TickSubscriber 实例（None=start 时创建；测试可注入 mock）。
            factor_loop: IntradayFactorLoop 实例（None=start 时创建；测试可注入 mock）。
            calendar: 市场日历注入（None=ASHareCalendar 默认，零行为变化）。
        """
        self._symbols = symbols
        self._force = force
        self._cycle_seconds = cycle_seconds
        self._redis_conn = redis_conn
        self._tick_subscriber = tick_subscriber
        self._factor_loop = factor_loop
        self._calendar = calendar or get_market_calendar("ashare")
        self._tick_cache: TickRedisCache | None = None
        self._heartbeat = None  # P0-2: CH 健康探针 + tick 心跳（IntradayRuntime 内创建）
        self._running = False

    def start(self) -> bool:
        """启动盘中运行时——拉起 tick_subscriber + IntradayFactorLoop。

        Returns:
            True 如果启动成功，False 如果非交易日守卫拦截或组件启动失败。
        """
        if self._running:
            logger.warning("IntradayRuntime: 已在运行")
            return True

        # ① 交易日守卫（按注入日历判定，默认 A 股日历）
        # 注意：is_trading_day 模块级函数保留供测试 mock；self._calendar 供注入扩展
        if not self._force and not is_trading_day():
            logger.warning("IntradayRuntime: 今日非交易日，跳过启动（--force 可强制运行）")
            return False

        # ② 获取 Redis 连接
        if self._redis_conn is None:
            ds = DatabaseService()
            self._redis_conn = ds.get_redis_conn()
        logger.info("IntradayRuntime: Redis 连接已建立")

        # ③ 创建 TickRedisCache（tick→Redis 双写适配器）
        self._tick_cache = TickRedisCache(self._redis_conn)

        # ④ 创建并启动 TickSubscriber（先启动，预热 Redis tick 数据）
        if self._tick_subscriber is None:
            # P0-2: 启用心跳检测 + CH 健康监控（R4a Alerter 集成）
            # TickSubscriber 内部管理 heartbeat 生命周期（start/record_tick/stop）
            from zephyr.data.alerter import Alerter
            from zephyr.data.redundant_source.heartbeat_monitor import HeartbeatMonitor

            self._heartbeat = HeartbeatMonitor(alerter=Alerter())
            self._tick_subscriber = TickSubscriber(
                symbols=self._symbols,
                tick_cache=self._tick_cache,
                heartbeat=self._heartbeat,
            )
            logger.info("IntradayRuntime: 已启用 CH 心跳探针 + tick 中断检测（P0-2）")
        logger.info("IntradayRuntime: 启动 TickSubscriber（等 QMT 就绪 + 订阅 + 预热）...")
        if not self._tick_subscriber.start():
            logger.error("IntradayRuntime: TickSubscriber 启动失败，退出")
            return False

        # ⑤ 从 subscriber 拿实际订阅标的（传给因子循环作为 tick 读取范围）
        symbols = sorted(self._tick_subscriber.subscribed_symbols)
        if not symbols:
            logger.warning("IntradayRuntime: 无已订阅标的，因子循环将以空 symbols 启动")
            symbols = self._symbols or []
        logger.info(
            "IntradayRuntime: TickSubscriber 已订阅 %d 只标的，启动因子循环",
            len(symbols),
        )

        # ⑥ 创建并启动 IntradayFactorLoop（后启动，读 Redis tick 算因子）
        if self._factor_loop is None:
            self._factor_loop = IntradayFactorLoop(
                redis_conn=self._redis_conn,
                symbols=symbols,
                cycle_seconds=self._cycle_seconds,
            )
        if not self._factor_loop.start():
            logger.error("IntradayRuntime: IntradayFactorLoop 启动失败，回滚 TickSubscriber")
            self._tick_subscriber.stop()
            return False

        self._running = True
        logger.info("IntradayRuntime: 盘中运行时已启动（tick→Redis→因子→H1 端到端贯通）")
        return True

    def stop(self) -> None:
        """优雅停止——反序停止（因子循环先停，tick 订阅后停）。"""
        self._running = False
        # 反序：先停因子循环（停止读 Redis 算因子）
        if self._factor_loop is not None:
            self._factor_loop.stop()
            logger.info("IntradayRuntime: IntradayFactorLoop 已停止")
        # 后停 tick 订阅（flush 残留 WAL + 取消订阅）
        if self._tick_subscriber is not None:
            self._tick_subscriber.stop()
            logger.info("IntradayRuntime: TickSubscriber 已停止")

    def stats(self) -> dict:
        """获取运行统计（聚合 subscriber + factor_loop）。"""
        result: dict = {"running": self._running}
        if self._tick_subscriber is not None:
            result["tick_subscriber"] = self._tick_subscriber.stats()
        if self._factor_loop is not None:
            result["factor_loop"] = self._factor_loop.stats()
        return result

    def run_forever(self) -> int:
        """常驻主循环——周期性打印 stats，直到收到信号优雅退出。

        Returns:
            0=正常退出，1=启动失败。
        """
        if not self.start():
            return 1

        def _signal_handler(signum, frame):
            logger.info("收到信号 %s，准备优雅退出", signum)
            raise KeyboardInterrupt()

        sig_module.signal(sig_module.SIGINT, _signal_handler)
        sig_module.signal(sig_module.SIGTERM, _signal_handler)

        logger.info("IntradayRuntime: 进入常驻主循环（Ctrl+C 退出）")
        try:
            while self._running:
                time.sleep(_STATS_LOG_INTERVAL)
                logger.info("运行统计: %s", self.stats())
        except KeyboardInterrupt:
            logger.info("收到退出信号")
        finally:
            self.stop()
            logger.info("=== IntradayRuntime 已退出 ===")
        return 0


def main(argv: list[str] | None = None) -> int:
    """命令行入口——启动盘中运行时并常驻直到 Ctrl+C。"""
    parser = argparse.ArgumentParser(
        description="盘中运行时编排器——tick→Redis→因子→H1 端到端",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="非交易日强制运行（跳过 is_trading_day 守卫）",
    )
    parser.add_argument(
        "--symbols",
        nargs="*",
        default=None,
        help="订阅标的列表（默认 tick_subscriber 自动获取全市场）",
    )
    parser.add_argument(
        "--cycle-seconds",
        type=float,
        default=_DEFAULT_CYCLE_SECONDS,
        help=f"因子循环周期秒（默认 {_DEFAULT_CYCLE_SECONDS}）",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logger.info("=== IntradayRuntime 启动 ===")

    runtime = IntradayRuntime(
        symbols=args.symbols,
        force=args.force,
        cycle_seconds=args.cycle_seconds,
    )
    return runtime.run_forever()


if __name__ == "__main__":
    sys.exit(main())
