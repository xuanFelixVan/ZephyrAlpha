# [BLUEPRINT] MOD-RUNTIME-INTRADAY | self-contained (runtime entry) | §
# [MODULE] zephyr.runtime.intraday_main
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.data.tick_subscriber; zephyr.data.tick_redis_cache; zephyr.factor.core.intraday_factor_loop; zephyr.infrastructure.database_service; zephyr.data.trading_calendar
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
# [TTL] permanent
"""盘中运行时编排器——单进程串起 tick_subscriber + IntradayFactorLoop。

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
"""
from __future__ import annotations

import argparse
import logging
import signal as sig_module
import sys
import time
from typing import TYPE_CHECKING

from zephyr.data.tick_redis_cache import TickRedisCache
from zephyr.data.tick_subscriber import TickSubscriber
from zephyr.data.trading_calendar import is_trading_day
from zephyr.factor.core.intraday_factor_loop import IntradayFactorLoop
from zephyr.infrastructure.database_service import DatabaseService

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
    ):
        """初始化盘中运行时。

        Args:
            symbols: 订阅标的列表（None=tick_subscriber 自动获取全市场）。
            force: 非交易日强制运行（跳过 is_trading_day 守卫）。
            cycle_seconds: 因子循环周期（秒，默认3.0）。
            redis_conn: Redis 连接（None=start 时通过 DatabaseService 获取；测试可注入）。
            tick_subscriber: TickSubscriber 实例（None=start 时创建；测试可注入 mock）。
            factor_loop: IntradayFactorLoop 实例（None=start 时创建；测试可注入 mock）。
        """
        self._symbols = symbols
        self._force = force
        self._cycle_seconds = cycle_seconds
        self._redis_conn = redis_conn
        self._tick_subscriber = tick_subscriber
        self._factor_loop = factor_loop
        self._tick_cache: TickRedisCache | None = None
        self._running = False

    def start(self) -> bool:
        """启动盘中运行时——拉起 tick_subscriber + IntradayFactorLoop。

        Returns:
            True 如果启动成功，False 如果非交易日守卫拦截或组件启动失败。
        """
        if self._running:
            logger.warning("IntradayRuntime: 已在运行")
            return True

        # ① 交易日守卫
        if not self._force and not is_trading_day():
            logger.warning(
                "IntradayRuntime: 今日非交易日，跳过启动（--force 可强制运行）"
            )
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
            self._tick_subscriber = TickSubscriber(
                symbols=self._symbols,
                tick_cache=self._tick_cache,
            )
        logger.info("IntradayRuntime: 启动 TickSubscriber（等 QMT 就绪 + 订阅 + 预热）...")
        if not self._tick_subscriber.start():
            logger.error("IntradayRuntime: TickSubscriber 启动失败，退出")
            return False

        # ⑤ 从 subscriber 拿实际订阅标的（传给因子循环作为 tick 读取范围）
        symbols = sorted(self._tick_subscriber.subscribed_symbols)
        if not symbols:
            logger.warning(
                "IntradayRuntime: 无已订阅标的，因子循环将以空 symbols 启动"
            )
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
            logger.error(
                "IntradayRuntime: IntradayFactorLoop 启动失败，回滚 TickSubscriber"
            )
            self._tick_subscriber.stop()
            return False

        self._running = True
        logger.info(
            "IntradayRuntime: 盘中运行时已启动（tick→Redis→因子→H1 端到端贯通）"
        )
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
