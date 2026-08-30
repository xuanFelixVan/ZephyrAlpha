# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-04
# [MODULE] zephyr.factor.core.intraday_factor_loop
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.core.dag_manager.executor; zephyr.factor.core.factor_dag; zephyr.factor.factor_base; zephyr.infrastructure.h1_redis_hot.h1_integration; zephyr.infrastructure.h1_redis_hot.h1_redis_schema
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 3秒拉tick→DataFrame→DagExecutor→H1; PIPELINE批量读tick; 单周期失败不中断循环; determine_mode自动切换batch/incremental
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单周期失败->log+继续; Redis故障->空DataFrame+skip; DAG构建失败->start返回False
# [TESTS] tests/factor/test_intraday_factor_loop.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
盘中因子调度循环——3秒拉 tick → DataFrame → DagExecutor → H1 Redis。

真源：
    - D-FACTOR 蓝图 §D-FACTOR-04 Pipeline（双模运行：盘前全量/盘中增量）
    - 数据架构.md §8.2 流式路径（miniQMT 3秒Tick触发）
    - 数据架构.md §8.3 CP-01（Tick→Redis ≤3秒）/ CP-02（Redis因子→信号 ≤5秒）
    - H1 蓝图 §9 集成点（D-FACTOR → H1）

职责：
    每 cycle_seconds（默认3秒）从 Redis 读 tick:{symbol}:latest，
    构造 pd.DataFrame（index=symbol），调 DagExecutor.execute(
        mode=determine_mode(),
        on_results_callback=create_h1_factor_sink(redis_conn)
    )。

    DagExecutor 的 on_results_callback 回调将因子截面写入 H1 Redis
    feature:{symbol}，供 D-SIGNAL/D-RISK 读取（<5ms SLA）。

线程模型：
    - 主线程：start() 构建 DAG + 创建 H1 sink，启动 daemon 线程
    - 循环线程：_loop → _tick_cycle（读tick→DataFrame→execute→H1写入）

用法::

    from zephyr.infrastructure.database_service import DatabaseService
    from zephyr.factor.core.intraday_factor_loop import IntradayFactorLoop

    ds = DatabaseService()
    loop = IntradayFactorLoop(
        redis_conn=ds.get_redis_conn(),
        symbols=["000001.SZ", "600000.SH"],
    )
    loop.start()  # 启动3秒循环
    # ... 运行中 ...
    loop.stop()   # 优雅停止

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: redis_conn 参数
#   fields: 参数 redis_conn（无注解）
#   code: intraday_factor_loop.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: symbols 参数
#   fields: 参数 symbols（无注解）
#   code: intraday_factor_loop.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: factor_ids 参数
#   fields: 参数 factor_ids（无注解）
#   code: intraday_factor_loop.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: cycle_seconds 参数
#   fields: 参数 cycle_seconds（无注解）
#   code: intraday_factor_loop.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① IntradayFactorLoop
#   name_en: IntradayFactorLoop
#   intro: 盘中因子调度循环——3秒拉 tick → DataFrame → DagExecutor → H1。
#   desc: 盘中因子调度循环——3秒拉 tick → DataFrame → DagExecutor → H1。 蓝图 §D-FACTOR-04 Pipeline 双模运行的盘中增量路径实现。；公共方法（定义序）: read_ti…
#   inputs: redis_conn symbols factor_ids cycle_seconds dag_executor
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: IntradayFactorLoop
#   downstream: 见模块头 [CONSUMERS]
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
import threading
import time
from typing import TYPE_CHECKING

import pandas as pd

from zephyr.factor.core.dag_manager.executor import (
    BATCH,
    DagExecutor,
    DagExecutorConfig,
    determine_mode,
)
from zephyr.factor.core.factor_dag import build_dag_from_registry
from zephyr.factor.factor_base import FactorRegistry
from zephyr.infrastructure.h1_redis_hot.h1_integration import create_h1_factor_sink
from zephyr.infrastructure.h1_redis_hot.h1_redis_schema import tick_latest_key

if TYPE_CHECKING:
    import redis

logger = logging.getLogger(__name__)

# 默认循环周期（秒，对应 miniQMT 3秒 Tick 推送频率）
_DEFAULT_CYCLE_SECONDS = 3.0

# tick:{symbol}:latest Hash → DataFrame 列映射
_TICK_FIELD_MAP = {
    "price": "close",
    "volume": "volume",
    "amount": "amount",
}


def _parse_tick_hash(tick_hash: dict[str, str]) -> dict[str, float | int] | None:
    """Redis tick:{symbol}:latest Hash → DataFrame 行字典。

    Args:
        tick_hash: Redis HGETALL 返回的 {field: str_value}（decode_responses=True）

    Returns:
        {close: float, volume: int, amount: float} 或 None（空 tick）
    """
    if not tick_hash or "price" not in tick_hash:
        return None
    try:
        return {
            "close": float(tick_hash.get("price", 0)),
            "volume": int(float(tick_hash.get("volume", 0))),
            "amount": float(tick_hash.get("amount", 0)),
        }
    except (TypeError, ValueError):
        return None


class IntradayFactorLoop:
    """盘中因子调度循环——3秒拉 tick → DataFrame → DagExecutor → H1。

    蓝图 §D-FACTOR-04 Pipeline 双模运行的盘中增量路径实现。
    """

    def __init__(
        self,
        redis_conn: redis.Redis,
        symbols: list[str],
        factor_ids: list[str] | None = None,
        cycle_seconds: float = _DEFAULT_CYCLE_SECONDS,
        dag_executor: DagExecutor | None = None,
    ):
        """初始化盘中因子调度循环。

        Args:
            redis_conn: redis.Redis 连接实例（decode_responses=True）。
            symbols: 要读取 tick 的标的列表（QMT 格式如 "000001.SZ"）。
            factor_ids: 要计算的因子 ID 列表（None=FactorRegistry 全部已注册因子）。
            cycle_seconds: 循环周期（秒，默认3.0，对应 miniQMT Tick 频率）。
            dag_executor: DagExecutor 实例（None=默认配置创建）。
        """
        self._redis = redis_conn
        self._symbols = symbols
        self._factor_ids = factor_ids
        self._cycle_seconds = cycle_seconds
        self._executor = dag_executor or DagExecutor(DagExecutorConfig(max_workers=4))
        self._dag = None  # 延迟构建（start 时）
        self._sink = None  # H1 写入回调（start 时创建）
        self._running = False
        self._thread: threading.Thread | None = None
        self._cycle_count = 0
        self._last_error: str = ""

    def _build_dag(self) -> bool:
        """从 FactorRegistry 构建 FactorDAG。

        Returns:
            True 如果 DAG 构建成功，False 如果无注册因子或构建失败。
        """
        factor_ids = self._factor_ids or list(FactorRegistry.registry.keys())
        if not factor_ids:
            logger.error("IntradayFactorLoop: FactorRegistry 为空，无因子可计算")
            return False
        try:
            self._dag = build_dag_from_registry(factor_ids, dag_id="intraday")
            logger.info("IntradayFactorLoop: DAG 构建成功，%d 个因子", len(factor_ids))
            return True
        except Exception as exc:  # noqa: BLE001 — DAG 构建失败是致命错误
            logger.error("IntradayFactorLoop: DAG 构建失败: %s", exc)
            return False

    def read_ticks_to_dataframe(self) -> pd.DataFrame:
        """PIPELINE 批量读 Redis tick:{symbol}:latest → 构造 DataFrame。

        Returns:
            DataFrame（index=symbol, columns=close/volume/amount）。
            空结果返回空 DataFrame。
        """
        if not self._symbols:
            return pd.DataFrame()

        # PIPELINE 批量 HGETALL（单次 RTT 读所有 symbol）
        pipe = self._redis.pipeline(transaction=False)
        for symbol in self._symbols:
            pipe.hgetall(tick_latest_key(symbol))
        try:
            raw_ticks = pipe.execute()
        except Exception as exc:  # noqa: BLE001 — Redis 故障降级
            logger.warning("IntradayFactorLoop: 批量读 tick 失败（降级）: %s", exc)
            return pd.DataFrame()

        rows: dict[str, dict[str, float | int]] = {}
        for symbol, tick_hash in zip(self._symbols, raw_ticks, strict=False):
            parsed = _parse_tick_hash(tick_hash)
            if parsed is not None:
                rows[symbol] = parsed

        if not rows:
            return pd.DataFrame()

        df = pd.DataFrame.from_dict(rows, orient="index")
        df.index.name = "symbol"
        return df

    def tick_cycle(self) -> int:
        """单次3秒周期：读 tick → DataFrame → DagExecutor → H1。

        Returns:
            DagExecutor 执行的因子数（0=无数据或执行失败）。
        """
        data = self.read_ticks_to_dataframe()
        if data.empty:
            logger.debug("IntradayFactorLoop: 无 tick 数据，跳过本轮")
            return 0

        mode = determine_mode()
        try:
            report = self._executor.execute(
                self._dag,
                data,
                mode=mode,
                on_results_callback=self._sink,
            )
            self._cycle_count += 1
            if report.failed_factors:
                logger.warning(
                    "IntradayFactorLoop: 周期 #%d 完成, mode=%s, %d 因子, %d 失败",
                    self._cycle_count,
                    mode,
                    len(report.results),
                    len(report.failed_factors),
                )
            else:
                logger.debug(
                    "IntradayFactorLoop: 周期 #%d 完成, mode=%s, %d 因子, %.3fs",
                    self._cycle_count,
                    mode,
                    len(report.results),
                    report.duration_s,
                )
            return len(report.results)
        except Exception as exc:  # noqa: BLE001 — 单周期失败不中断循环
            self._last_error = str(exc)
            logger.exception("IntradayFactorLoop: 周期执行失败（继续循环）")
            return 0

    def _loop(self) -> None:
        """循环线程主函数。"""
        logger.info(
            "IntradayFactorLoop: 循环启动, %d symbols, %.1fs 周期",
            len(self._symbols),
            self._cycle_seconds,
        )
        while self._running:
            self.tick_cycle()
            if self._running:
                time.sleep(self._cycle_seconds)
        logger.info("IntradayFactorLoop: 循环结束, 共 %d 周期", self._cycle_count)

    def start(self) -> bool:
        """启动盘中因子调度循环。

        构建 DAG + 创建 H1 sink + 启动 daemon 线程。

        Returns:
            True 如果启动成功，False 如果 DAG 构建失败。
        """
        if self._running:
            logger.warning("IntradayFactorLoop: 已在运行")
            return True

        if not self._build_dag():
            return False

        self._sink = create_h1_factor_sink(self._redis)
        self._running = True
        self._cycle_count = 0
        self._thread = threading.Thread(target=self._loop, daemon=True, name="intraday-factor-loop")
        self._thread.start()
        logger.info("IntradayFactorLoop: 已启动")
        return True

    def stop(self) -> None:
        """停止循环线程。"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=10)
            self._thread = None
        logger.info("IntradayFactorLoop: 已停止, stats=%s", self.stats())

    def stats(self) -> dict:
        """获取运行统计。"""
        return {
            "running": self._running,
            "cycle_count": self._cycle_count,
            "symbols": len(self._symbols),
            "last_error": self._last_error,
        }
