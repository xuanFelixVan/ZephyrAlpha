# [BLUEPRINT] MOD-BT-017 | docs/03_modules/_domain_backtest/blueprint.md | §D-BACKTEST BT-17
# [MODULE] zephyr.backtest.services.scheduler
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.core.engine_base
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] FIFO队列; 参数网格正确展开; 结果按strategy_id聚合
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空队列run_all返回空列表; 无结果get_summary返回空摘要
# [TESTS] tests/backtest/test_scheduler.py
# [A_module] module_id=MOD-BT-017 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D-BACKTEST BT-17 回测自动调度器——批量+参数网格+队列管理+结果聚合。

职责：
  - 参数网格展开：将 {param: [v1, v2, ...]} 展开为所有组合
  - FIFO队列管理：按提交顺序执行
  - 并发控制：ThreadPoolExecutor + max_workers
  - 结果聚合：按 strategy_id 分组，输出最优/最差/均值

用法示例：
    scheduler = BacktestScheduler(engine_factory=my_factory)
    scheduler.submit_grid("strat_a", data, signals, {"horizon": [5, 10, 20]})
    results = scheduler.run_all(max_workers=4)
    summary = scheduler.get_summary("strat_a")
"""
from __future__ import annotations

import itertools
import logging
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any, Callable
from uuid import uuid4

import pandas as pd

from zephyr.backtest.core.engine_base import BacktestResult

log = logging.getLogger(__name__)


@dataclass
class BacktestTask:
    """回测任务。

    Attributes:
        task_id: 任务唯一ID
        strategy_id: 策略ID
        data: 回测数据
        signals: 信号数据
        params: 引擎参数（传给 engine_factory）
    """

    task_id: str
    strategy_id: str
    data: pd.DataFrame
    signals: pd.DataFrame
    params: dict[str, Any] = field(default_factory=dict)


@dataclass
class GridSearchSummary:
    """参数网格搜索结果摘要。"""

    strategy_id: str
    total_runs: int
    best_result: BacktestResult | None
    best_params: dict
    worst_result: BacktestResult | None
    worst_params: dict
    mean_sharpe: float
    mean_return: float
    all_results: list[tuple[dict, BacktestResult]]


def _expand_param_grid(param_grid: dict[str, list]) -> list[dict]:
    """将参数网格展开为所有参数组合的列表。"""
    if not param_grid:
        return [{}]
    keys = list(param_grid.keys())
    values = list(param_grid.values())
    return [dict(zip(keys, combo)) for combo in itertools.product(*values)]


def _build_summary(
    strategy_id: str,
    results: list[tuple[dict, BacktestResult]],
) -> GridSearchSummary:
    """从结果列表构建摘要。"""
    if not results:
        return GridSearchSummary(
            strategy_id, 0, None, {}, None, {}, 0.0, 0.0, []
        )
    best = max(results, key=lambda r: r[1].sharpe_ratio)
    worst = min(results, key=lambda r: r[1].sharpe_ratio)
    mean_sharpe = sum(r[1].sharpe_ratio for r in results) / len(results)
    mean_return = sum(r[1].total_return for r in results) / len(results)
    return GridSearchSummary(
        strategy_id=strategy_id,
        total_runs=len(results),
        best_result=best[1],
        best_params=best[0],
        worst_result=worst[1],
        worst_params=worst[0],
        mean_sharpe=mean_sharpe,
        mean_return=mean_return,
        all_results=results,
    )


class BacktestScheduler:
    """回测自动调度器——批量+参数网格+队列管理+结果聚合。

    Args:
        engine_factory: 可调用对象，接受 **params 返回 BacktestEngineBase 实例。
                        默认使用 DefaultBacktestEngine。
    """

    def __init__(
        self,
        engine_factory: Callable[..., Any] | None = None,
    ) -> None:
        self._engine_factory = engine_factory
        self._queue: deque[BacktestTask] = deque()
        self._results: dict[str, BacktestResult] = {}
        self._task_meta: dict[str, tuple[str, dict]] = {}

    def run_task(self, task) -> BacktestResult:
        """公共接口：run_task（Stage 4 公共化）。"""
        return self._run_task(task)


    def submit(
        self,
        strategy_id: str,
        data: pd.DataFrame,
        signals: pd.DataFrame,
        params: dict[str, Any] | None = None,
    ) -> str:
        """提交单个回测任务到队列。

        Returns:
            task_id
        """
        task_id = f"task-{uuid4().hex[:8]}"
        task = BacktestTask(
            task_id=task_id,
            strategy_id=strategy_id,
            data=data,
            signals=signals,
            params=params or {},
        )
        self._queue.append(task)
        self._task_meta[task_id] = (strategy_id, params or {})
        return task_id

    def submit_grid(
        self,
        strategy_id: str,
        data: pd.DataFrame,
        signals: pd.DataFrame,
        param_grid: dict[str, list],
    ) -> list[str]:
        """提交参数网格批量回测。

        将 param_grid 展开为所有组合，每个组合生成一个任务。

        Args:
            param_grid: 参数网格，如 {"horizon": [5, 10], "threshold": [0.01, 0.02]}

        Returns:
            task_id 列表
        """
        combos = _expand_param_grid(param_grid)
        return [
            self.submit(strategy_id, data, signals, combo) for combo in combos
        ]

    def run_all(self, max_workers: int = 4) -> list[BacktestResult]:
        """执行队列中所有任务（FIFO），返回结果列表。

        Args:
            max_workers: 最大并发数

        Returns:
            BacktestResult 列表（完成顺序，非提交顺序）
        """
        if not self._queue:
            return []
        results: list[BacktestResult] = []
        tasks = list(self._queue)
        self._queue.clear()
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_map = {
                executor.submit(self._run_task, task): task.task_id
                for task in tasks
            }
            for future in as_completed(future_map):
                task_id = future_map[future]
                try:
                    result = future.result()
                except Exception as exc:  # noqa: BLE001
                    log.error("回测任务 %s 失败: %s", task_id, exc)
                    continue
                self._results[task_id] = result
                results.append(result)
        return results

    def get_result(self, task_id: str) -> BacktestResult | None:
        """获取单个任务结果。"""
        return self._results.get(task_id)

    def get_summary(self, strategy_id: str) -> GridSearchSummary:
        """获取策略的网格搜索摘要。"""
        results: list[tuple[dict, BacktestResult]] = []
        for task_id, (sid, params) in self._task_meta.items():
            if sid != strategy_id:
                continue
            result = self._results.get(task_id)
            if result is not None:
                results.append((params, result))
        return _build_summary(strategy_id, results)

    @property
    def queue_size(self) -> int:
        """当前队列中待执行任务数。"""
        return len(self._queue)

    def _run_task(self, task: BacktestTask) -> BacktestResult:
        """执行单个回测任务。"""
        if self._engine_factory is not None:
            engine = self._engine_factory(**task.params)
        else:
            from zephyr.backtest.implementations.vectorized_engine import (
                DefaultBacktestEngine,
            )
            engine = DefaultBacktestEngine()
        return engine.run(task.data, task.signals)
