# [BLUEPRINT] MOD-H1_REDIS_HOT | docs/03_modules/_cross_layer/database/sub_blueprints/h1_redis_hot.md
# [MODULE] zephyr.infrastructure.h1_redis_hot.h1_integration
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.h1_redis_hot.h1_redis_writer; zephyr.infrastructure.h1_redis_hot.h1_redis_reader
# [CONSUMERS] zephyr.factor.core.dag_manager.executor; zephyr.signal_fundamental; zephyr.risk
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] dag_report_to_cross_section 仅提取 success=True 的因子; H1 写入失败不阻断因子管道(降级日志); 回调接口与 DagExecutor 解耦
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] H1WriteBatchFailed(写入失败,调用方决定重试/降级); H1RedisUnavailable(读取失败,调用方降级 CP-02)
# [TESTS] tests/zephyr/infrastructure/h1_redis_hot/test_h1_integration.py
# [A_module] module_id=MOD-H1_REDIS_HOT | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
H1 Redis 集成适配器——连接 D-FACTOR/SIGNAL/RISK 与 H1 热缓存。

蓝图 §9 集成点的实现层，提供三组接口：

1. D-FACTOR → H1（写）：
   - dag_report_to_cross_section(): 将 DagExecutionReport 转为 {symbol: {factor_name: value}}
   - write_dag_results_to_h1(): 便捷函数——转换 + 写入一步到位
   - create_h1_factor_sink(): 工厂——返回 DagExecutor.execute(on_results_callback=...) 的回调

2. D-SIGNAL ← H1（读因子）：
   - create_h1_reader(): 工厂——返回 H1RedisReader 供信号模块读取因子截面

3. D-RISK ← H1（读持仓/风控）：
   - 复用 create_h1_reader()，调用 reader.get_position()/get_risk_status()

设计原则：
   - 非破坏性集成——H1 不可用时降级（日志 warning），不阻断因子管道
   - 解耦——DagExecutor 通过 on_results_callback 回调接口与 H1 解耦，不直接 import H1
   - 幂等——同一截面重复写入覆盖旧值（HSET 语义），无副作用

SSoT: docs/03_modules/_cross_layer/database/sub_blueprints/h1_redis_hot.md §9

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: results 参数
#   fields: 参数 results，类型注解 dict[str, Any]
#   code: h1_integration.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: redis_conn 参数
#   fields: 参数 redis_conn，类型注解 redis_lib.Redis
#   code: h1_integration.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: factor_version 参数
#   fields: 参数 factor_version，类型注解 str
#   code: h1_integration.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① dag_report_to_cross_section
#   name_en: dag_report_to_cross_section
#   intro: 将 DagExecutionReport.results 转为 H1RedisWriter 所需的截面格式。
#   desc: 将 DagExecutionReport.results 转为 H1RedisWriter 所需的截面格式。 DagExecutionReport.results 是 {fact…；源码 L119-L161
#   inputs: results
#   outputs: dict[str, dict[str, float]]
# - id: A2
#   name_zh: ② write_dag_results_to_h1
#   name_en: write_dag_results_to_h1
#   intro: 将 DagExecutionReport.results 写入 H1 Redis 热缓存（便捷函数）。
#   desc: 将 DagExecutionReport.results 写入 H1 Redis 热缓存（便捷函数）。 内部调用 dag_report_to_cross_section() 转换…；源码 L164-L203
#   inputs: results redis_conn factor_version
#   outputs: int
# - id: A3
#   name_zh: ③ create_h1_factor_sink
#   name_en: create_h1_factor_sink
#   intro: 工厂——创建 DagExecutor.execute(on_results_callback=...) 的 H1 写入…
#   desc: 工厂——创建 DagExecutor.execute(on_results_callback=...) 的 H1 写入回调。 返回一个闭包，接收 DagExecutionRepo…；源码 L206-L233
#   inputs: redis_conn factor_version
#   outputs: Callable[[dict[str, Any]], None]
# - id: A4
#   name_zh: ④ create_h1_reader
#   name_en: create_h1_reader
#   intro: 工厂——创建 H1RedisReader 供 D-SIGNAL/D-RISK 读取因子/持仓/风控数据。
#   desc: 工厂——创建 H1RedisReader 供 D-SIGNAL/D-RISK 读取因子/持仓/风控数据。 Usage: >>> from zephyr.infrastructur…；源码 L236-L255
#   inputs: redis_conn
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: dict[str, dict[str, float]]
#   name_en: dict[str, dict[str, float]]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.factor.core.dag_manager.executor; zephyr.signal_fundamental; zephyr.risk
# - id: O2
#   name_zh: int
#   name_en: int
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.factor.core.dag_manager.executor; zephyr.signal_fundamental; zephyr.risk
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> O1
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd
    import redis as redis_lib

logger = logging.getLogger(__name__)


def dag_report_to_cross_section(
    results: dict[str, Any],
) -> dict[str, dict[str, float]]:
    """将 DagExecutionReport.results 转为 H1RedisWriter 所需的截面格式。

    DagExecutionReport.results 是 {factor_id: FactorExecutionResult}，
    其中 FactorExecutionResult.series 是 pd.Series（index=symbol, values=factor_score）。
    本函数将其转为 {symbol: {factor_name: float_value}} 供 H1RedisWriter 使用。

    Args:
        results: DagExecutionReport.results 字典（factor_id → FactorExecutionResult）。
                 FactorExecutionResult 需有 .success (bool) 和 .series (pd.Series|None) 属性。

    Returns:
        {symbol: {factor_name: factor_value}} 截面字典。
        仅包含 success=True 且 series 非 None 的因子；NaN 值被跳过。

    Example:
        >>> # report = executor.execute(dag, data)
        >>> # cross_section = dag_report_to_cross_section(report.results)
        >>> # writer.write_factor_cross_section(cross_section)
    """
    import math

    cross_section: dict[str, dict[str, float]] = {}

    for factor_id, result in results.items():
        # Duck-typing：兼容 FactorExecutionResult 和任何有 .success/.series 的对象
        success = getattr(result, "success", False)
        series = getattr(result, "series", None)
        if not success or series is None:
            continue

        for idx, val in series.items():
            symbol = str(idx)
            # 跳过 NaN/None 值（pd.Series 可能含 NaN）
            if val is None or (isinstance(val, float) and math.isnan(val)):
                continue
            if symbol not in cross_section:
                cross_section[symbol] = {}
            cross_section[symbol][factor_id] = float(val)

    return cross_section


def write_dag_results_to_h1(
    results: dict[str, Any],
    redis_conn: redis_lib.Redis,
    factor_version: str = "v1",
) -> int:
    """将 DagExecutionReport.results 写入 H1 Redis 热缓存（便捷函数）。

    内部调用 dag_report_to_cross_section() 转换格式，然后调用 H1RedisWriter 写入。
    写入失败时 log error 但不抛异常（降级——因子管道继续运行，H1 数据可能过期）。

    Args:
        results: DagExecutionReport.results 字典。
        redis_conn: redis.Redis 连接实例（来自 DatabaseService.get_redis_conn()）。
        factor_version: 因子版本号（默认 v1，与 Writer 对齐）。

    Returns:
        写入的 symbol 数量（0 表示无数据或写入失败）。
    """
    from zephyr.infrastructure.h1_redis_hot.h1_redis_writer import H1RedisWriter

    cross_section = dag_report_to_cross_section(results)
    if not cross_section:
        logger.debug("write_dag_results_to_h1: 截面为空，跳过写入")
        return 0

    writer = H1RedisWriter(redis_conn)
    try:
        written = writer.write_factor_cross_section(cross_section, factor_version)
        logger.info(
            "write_dag_results_to_h1: 成功写入 %d symbols, %d factors → H1",
            written,
            len(cross_section),
        )
        return written
    except Exception as exc:  # noqa: BLE001 — 降级：H1 写入失败不阻断因子管道
        logger.error(
            "write_dag_results_to_h1: H1 写入失败（降级——因子管道继续，H1 数据可能过期）: %s",
            exc,
        )
        return 0


def create_h1_factor_sink(
    redis_conn: redis_lib.Redis,
    factor_version: str = "v1",
) -> Callable[[dict[str, Any]], None]:
    """工厂——创建 DagExecutor.execute(on_results_callback=...) 的 H1 写入回调。

    返回一个闭包，接收 DagExecutionReport.results 字典，写入 H1。
    用于 DagExecutor 的 on_results_callback 参数（蓝图 §9 D-FACTOR → H1 集成点）。

    Usage:
        >>> from zephyr.infrastructure.database_service import DatabaseService
        >>> from zephyr.infrastructure.h1_redis_hot.h1_integration import create_h1_factor_sink
        >>> ds = DatabaseService()
        >>> sink = create_h1_factor_sink(ds.get_redis_conn())
        >>> report = executor.execute(dag, data, on_results_callback=sink)

    Args:
        redis_conn: redis.Redis 连接实例。
        factor_version: 因子版本号（默认 v1）。

    Returns:
        回调函数 (results: dict) -> None。
    """

    def _sink(results: dict[str, Any]) -> None:
        write_dag_results_to_h1(results, redis_conn, factor_version)

    return _sink


def create_h1_reader(redis_conn: redis_lib.Redis):
    """工厂——创建 H1RedisReader 供 D-SIGNAL/D-RISK 读取因子/持仓/风控数据。

    Usage:
        >>> from zephyr.infrastructure.database_service import DatabaseService
        >>> from zephyr.infrastructure.h1_redis_hot.h1_integration import create_h1_reader
        >>> ds = DatabaseService()
        >>> reader = create_h1_reader(ds.get_redis_conn())
        >>> features = reader.get_online_features("000001.SZ", ["momentum_20d", "close"])
        >>> position = reader.get_position("000001.SZ")

    Args:
        redis_conn: redis.Redis 连接实例。

    Returns:
        H1RedisReader 实例。
    """
    from zephyr.infrastructure.h1_redis_hot.h1_redis_reader import H1RedisReader

    return H1RedisReader(redis_conn)


__all__ = [
    "dag_report_to_cross_section",
    "write_dag_results_to_h1",
    "create_h1_factor_sink",
    "create_h1_reader",
]
