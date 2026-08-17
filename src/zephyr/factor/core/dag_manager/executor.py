# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-CORE-DM
# [MODULE] zephyr.factor.core.dag_manager.executor
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.core.factor_dag; zephyr.factor.core.backpressure; zephyr.factor.factor_base
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 层间串行（依赖约束）；层内并行（ThreadPoolExecutor）；上游失败下游跳过；INV-004 PIT 铁律——因子计算仅用同期数据
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单因子失败不阻断同层其他因子；下游因子标记 upstream failed: <id>；超时标记 timeout
# [TESTS] tests/factor/test_dag_manager.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D_FACTOR core dag_manager.executor——DAG 调度执行器。

输入 FactorDAG + 数据，按拓扑层串行推进、层内并发执行因子计算（ThreadPoolExecutor），
受 BackpressureLimiter 限流。

调度策略：
- 层间串行：第 N 层全部完成后才进入第 N+1 层（依赖约束）
- 层内并行：同一层因子无依赖关系，用 ThreadPoolExecutor 并发执行
- backpressure：每个因子计算前 acquire，计算后 release（防止过载）
- 容错：单因子失败不阻断同层其他因子；下游因子标记 "upstream failed: <id>"

双模运行（ADR-FAC-002）：
- batch 模式（盘前全量 03:00-09:15）：调用 factor.compute(data) 全量计算
- incremental 模式（盘中增量 09:30-15:00）：调用 factor.incremental_compute(data, cached=...) 增量计算

适用场景：IO 密集或轻量计算（GIL 下 ThreadPool 够用）。CPU 密集场景用 dist_feature_eng。
"""
from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeout
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable

import pandas as pd

from zephyr.factor.core.backpressure.limiter import BackpressureLimiter
from zephyr.factor.core.config_manager.loader import get_section
from zephyr.factor.core.factor_dag.dag import FactorDAG
from zephyr.factor.factor_base import FactorRegistry

log = logging.getLogger(__name__)

# 双模运行常量（ADR-FAC-002）
BATCH = "batch"
INCREMENTAL = "incremental"

# A股时间窗口（分钟数，用于 determine_mode）
_BATCH_START = 3 * 60       # 03:00
_BATCH_END = 9 * 60 + 15    # 09:15
_INCR_START = 9 * 60 + 30   # 09:30
_INCR_END = 15 * 60         # 15:00


def determine_mode(now: datetime | None = None) -> str:
    """根据当前时间判断 Pipeline 运行模式。

    03:00-09:15 → batch（盘前全量）
    09:30-15:00 → incremental（盘中增量）
    其他时段 → batch（默认安全）

    Args:
        now: 当前时间（None 时取 datetime.now()）

    Returns:
        "batch" 或 "incremental"
    """
    now = now or datetime.now()
    time_min = now.hour * 60 + now.minute
    if _BATCH_START <= time_min < _BATCH_END:
        return BATCH
    if _INCR_START <= time_min < _INCR_END:
        return INCREMENTAL
    return BATCH


@dataclass(frozen=True)
class DagExecutorConfig:
    """DAG 执行器配置。

    Attributes:
        max_workers: 层内 ThreadPoolExecutor 并发数
        factor_timeout_s: 单因子计算超时秒数
    """

    max_workers: int = 4
    factor_timeout_s: float = 60.0


def _default_config() -> DagExecutorConfig:
    """从 core/_config.yaml 的 dag_manager 节构建默认配置（真源=YAML，缺省回退常量）。"""
    s = get_section("dag_manager")
    return DagExecutorConfig(
        max_workers=int(s.get("max_workers", 4)),
        factor_timeout_s=float(s.get("factor_timeout_s", 60.0)),
    )


def _get_max_layers() -> int:
    """从 core/_config.yaml 的 factor_dag 节读取单 DAG 最大拓扑层数（防环+防爆炸）。"""
    return int(get_section("factor_dag").get("max_layers", 20))


@dataclass
class FactorExecutionResult:
    """单因子执行结果。

    Attributes:
        factor_id: 因子 ID
        success: 是否成功
        series: 成功时的因子截面得分（pd.Series），失败时为 None
        error: 失败原因（成功时为空字符串）
    """

    factor_id: str
    success: bool
    series: pd.Series | None
    error: str = ""


@dataclass
class DagExecutionReport:
    """DAG 执行报告。

    Attributes:
        dag_id: DAG 唯一标识
        layer_count: 拓扑层数
        results: factor_id -> FactorExecutionResult 映射
        duration_s: 总执行时长（秒）
        failed_factors: 失败因子 ID 列表
        mode: 执行模式 ("batch" / "incremental")
    """

    dag_id: str
    layer_count: int
    results: dict[str, FactorExecutionResult] = field(default_factory=dict)
    duration_s: float = 0.0
    failed_factors: list[str] = field(default_factory=list)
    mode: str = BATCH


class DagExecutor:
    """DAG 调度执行器——分层并行执行因子计算。

    Usage::

        dag = build_dag_from_registry(["a", "b", "c"])
        executor = DagExecutor(DagExecutorConfig(max_workers=4))
        report = executor.execute(dag, data)
        # report.results["a"].series 是因子 a 的截面得分
    """

    def __init__(
        self,
        config: DagExecutorConfig | None = None,
        backpressure: BackpressureLimiter | None = None,
    ) -> None:
        self._config = config or _default_config()
        self._bp = backpressure  # None 时不限流

    def execute(
        self,
        dag: FactorDAG,
        data: pd.DataFrame,
        extra_kwargs: dict[str, dict] | None = None,
        mode: str = BATCH,
        cached_results: dict[str, pd.Series] | None = None,
        on_results_callback: Callable[[dict[str, FactorExecutionResult]], None] | None = None,
    ) -> DagExecutionReport:
        """执行 DAG：分层并行计算因子。

        Args:
            dag: FactorDAG 实例（须已通过 validate / topological_layers）
            data: 输入行情数据（传给每个因子的 compute 方法）
            extra_kwargs: factor_id -> kwargs 映射，传给 compute 的额外参数
            mode: 执行模式 "batch"（全量）或 "incremental"（增量）
            cached_results: 增量模式下的缓存结果 (factor_id -> pd.Series)
            on_results_callback: 因子计算完成后的回调（可选）。
                接收 results 字典（factor_id → FactorExecutionResult），
                用于 H1 Redis 热缓存写入等后处理（蓝图 §9 D-FACTOR → H1 集成点）。
                回调异常不阻断返回 report（log error 后继续）。

        Returns:
            DagExecutionReport，含每个因子的执行结果。

        Notes:
            - batch 模式调用 factor.compute(data)
            - incremental 模式调用 factor.incremental_compute(data, cached=...)
            - 上游因子失败时，下游因子标记 success=False, error="upstream failed: <id>"
            - 因子计算超时标记 success=False, error="timeout"
            - backpressure acquire 失败标记 success=False, error="backpressure rejected"
        """
        start_ts = time.monotonic()
        kwargs_map = extra_kwargs or {}
        cache = cached_results or {}
        layers = dag.topological_layers()
        max_layers = _get_max_layers()
        if len(layers) > max_layers:
            raise ValueError(
                f"DAG 拓扑层数 {len(layers)} 超过上限 max_layers={max_layers}（core/_config.yaml factor_dag 节）"
            )
        results: dict[str, FactorExecutionResult] = {}
        failed_set: set[str] = set()

        for layer in layers:
            to_execute = self._filter_layer(dag, layer, results, failed_set)
            if not to_execute:
                continue
            with ThreadPoolExecutor(max_workers=self._config.max_workers) as pool:
                futures = {
                    pool.submit(
                        self._compute_factor, fid, data, kwargs_map.get(fid, {}),
                        mode, cache.get(fid),
                    ): fid
                    for fid in to_execute
                }
                for future in futures:
                    fid = futures[future]
                    try:
                        result = future.result(timeout=self._config.factor_timeout_s)
                        results[fid] = result
                        if not result.success:
                            failed_set.add(fid)
                    except FutureTimeout:
                        results[fid] = FactorExecutionResult(
                            fid, success=False, series=None, error="timeout"
                        )
                        failed_set.add(fid)
                    except Exception as e:
                        log.exception("dag_manager: 因子 %s 执行异常", fid)
                        results[fid] = FactorExecutionResult(
                            fid, success=False, series=None, error=f"exception: {e}"
                        )
                        failed_set.add(fid)

        duration = time.monotonic() - start_ts

        # H1 集成回调（蓝图 §9 D-FACTOR → H1）：因子计算完成后调用 on_results_callback
        # 回调异常不阻断返回 report（降级——因子管道继续，H1 写入失败由回调内部处理）
        if on_results_callback is not None:
            try:
                on_results_callback(results)
            except Exception as exc:  # noqa: BLE001 — 回调异常不阻断因子管道
                log.error("dag_manager: on_results_callback 执行失败（降级）: %s", exc)

        return DagExecutionReport(
            dag_id=dag.dag_id,
            layer_count=len(layers),
            results=results,
            duration_s=duration,
            failed_factors=sorted(failed_set),
            mode=mode,
        )

    def _filter_layer(
        self, dag: FactorDAG, layer: list[str],
        results: dict[str, FactorExecutionResult], failed_set: set[str],
    ) -> list[str]:
        """过滤层内因子：跳过上游失败的因子，返回可执行列表。"""
        to_execute: list[str] = []
        for fid in layer:
            node = next((n for n in dag.nodes if n.factor_id == fid), None)
            if node is None:
                results[fid] = FactorExecutionResult(
                    fid, success=False, series=None, error="node not found in DAG"
                )
                failed_set.add(fid)
                continue
            failed_deps = [d for d in node.dependencies if d in failed_set]
            if failed_deps:
                results[fid] = FactorExecutionResult(
                    fid, success=False, series=None,
                    error=f"upstream failed: {','.join(failed_deps)}",
                )
                failed_set.add(fid)
            else:
                to_execute.append(fid)
        return to_execute

    def _compute_factor(
        self, factor_id: str, data: pd.DataFrame, kwargs: dict,
        mode: str = BATCH, cached: pd.Series | None = None,
    ) -> FactorExecutionResult:
        """单因子计算（线程池工作函数）。

        1. backpressure acquire（若配置）
        2. FactorRegistry.get(factor_id) 实例化
        3. batch 模式: factor.compute(data, **kwargs)
           incremental 模式: factor.incremental_compute(data, cached=cached)
        4. backpressure release
        """
        if self._bp is not None:
            if not self._bp.acquire():
                return FactorExecutionResult(
                    factor_id, success=False, series=None,
                    error="backpressure rejected",
                )
        try:
            factor_cls = FactorRegistry.get(factor_id)
            factor = factor_cls()
            if mode == INCREMENTAL and cached is not None:
                series = factor.incremental_compute(data, cached=cached)
            else:
                series = factor.compute(data, **kwargs)
            return FactorExecutionResult(
                factor_id, success=True, series=series, error=""
            )
        except KeyError:
            return FactorExecutionResult(
                factor_id, success=False, series=None,
                error=f"factor '{factor_id}' not registered",
            )
        except Exception as e:  # noqa: BLE001 — 单因子失败不阻断同层其他因子（错误契约：记入 FactorExecutionResult.error）
            log.warning("dag_manager: 因子 %s 计算失败: %s", factor_id, e)
            return FactorExecutionResult(
                factor_id, success=False, series=None, error=f"compute error: {e}"
            )
        finally:
            if self._bp is not None:
                self._bp.release()
