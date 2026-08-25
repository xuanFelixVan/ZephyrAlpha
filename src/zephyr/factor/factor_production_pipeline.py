# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] zephyr.factor.factor_production_pipeline
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] 盘前/盘中调度器（运行时装配批接线）
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 双模(盘前全量/盘中增量); 分块编排单块失败降级不中断; 算力预算耗尽后续块跳过; 单块超时标记timeout(无法真中断结果仍落库); 容量规划7000+标的×N_max-4因子; 计算/落库/广播全委托注入不重建既有件
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] compute_executor不可调用->PipelineConfigError; 单块异常->该块降级(verdict.degraded=True,不抛)
# [TESTS] tests/factor/test_factor_production_pipeline.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C-009 因子与信号生产管线（CAND-FAC-009 / B1-00144）。

双模管线编排：盘前全量批算（分块调度）+ 盘中增量（事件驱动 mode），因子值落
feature_store 并广播，算力预算与超时降级，7000+标的×N_max-4 因子容量规划。

查重裁定（不重复既有件）：
  - 盘中 3 秒 tick 循环执行体已有 intraday_factor_loop（production）；因子 DAG
    计算已有 factor_dag/dag_manager（production）；长表落库已有
    feature_store_writer（管道就位）。本件是"批算编排+算力预算+容量治理"层：
    计算经 compute_executor 注入委托（DagExecutor 语义），落库经 store_writer
    注入委托（feature_store_writer.write_feature_values 语义），广播经
    broadcast_sink 注入（H1 Redis sink 语义）——不重建任何计算/存储本体。
  - 与 C-027 因子工厂（factor_factory）分工：工厂管单因子 9 阶段生命周期，
    本件管全市场因子矩阵的日常批量生产。

依据: §功能域模块·D-FACTOR；construction_backlog_dig.tsv B1-00144。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Iterable, Mapping, Sequence

from zephyr.shared.foundation.errors import ZephyrBaseError

log = logging.getLogger(__name__)

__all__ = [
    "BatchVerdict",
    "CapacityPlan",
    "ComputeMode",
    "FactorProductionPipeline",
    "PipelineConfigError",
]

# 容量默认：7000+标的 × N_max-4因子（backlog 口径）
DEFAULT_MAX_SYMBOLS = 7500
DEFAULT_MAX_FACTORS = 4
DEFAULT_CHUNK_SIZE = 500


class PipelineConfigError(ZephyrBaseError):
    """管线配置失败（错误码未登，纪律⑦留错误码对账批）。"""


class ComputeMode(str, Enum):
    """双模计算。"""

    PREMARKET_FULL = "premarket_full"
    INTRADAY_INCREMENTAL = "intraday_incremental"


@dataclass(frozen=True)
class CapacityPlan:
    """容量规划校验结果。

    Attributes:
        symbols: 标的数。
        factors: 因子数。
        estimated_cells: 估算计算单元数（symbols×factors）。
        within_budget: 是否在容量预算内。
        max_symbols: 标的容量上限。
        max_factors: 因子容量上限。
        reason: 超限理由。
    """

    symbols: int
    factors: int
    estimated_cells: int
    within_budget: bool
    max_symbols: int
    max_factors: int
    reason: str = ""


@dataclass(frozen=True)
class BatchVerdict:
    """一批计算编排裁定。

    Attributes:
        mode: 计算模式。
        symbols_done: 实际完成标的数。
        degraded: 是否存在降级（块失败/预算耗尽/超时）。
        timeout_count: 超时块数。
        rows_persisted: 落库行数。
        reason: 降级理由汇总。
    """

    mode: ComputeMode
    symbols_done: int
    degraded: bool
    timeout_count: int = 0
    rows_persisted: int = 0
    reason: str = ""


class FactorProductionPipeline:
    """因子与信号生产管线编排器。

    Args:
        compute_executor: 计算执行委托
            ``executor(symbols, factor_ids, mode) -> list[长表行dict]``
            （DagExecutor 语义，注入式，本件不重建 DAG 计算）。
        store_writer: 落库委托 ``writer(rows)``（feature_store_writer 语义）。
        broadcast_sink: 广播委托 ``sink(summary: dict)``（H1 因子广播语义）。
        chunk_size: 盘前批算分块大小（标的数/块）。
        max_symbols: 标的容量上限（默认 7500，7000+口径）。
        max_factors: 因子容量上限（默认 4，N_max-4 口径）。
        compute_budget_seconds: 单轮批算算力预算秒（累计超时后续块降级跳过）。
        batch_timeout_seconds: 单块超时阈值秒（标记降级，结果仍落库）。
        clock: 时钟注入（秒，测试可控）。
    """

    def __init__(
        self,
        *,
        compute_executor: Callable[[Sequence[str], Sequence[str], ComputeMode], list[dict]],
        store_writer: Callable[[Iterable[dict]], Any] | None = None,
        broadcast_sink: Callable[[dict], Any] | None = None,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        max_symbols: int = DEFAULT_MAX_SYMBOLS,
        max_factors: int = DEFAULT_MAX_FACTORS,
        compute_budget_seconds: float = 1800.0,
        batch_timeout_seconds: float = 300.0,
        clock: Callable[[], float] | None = None,
    ) -> None:
        if not callable(compute_executor):
            raise PipelineConfigError("compute_executor 必须为可调用对象（计算委托注入式）")
        import time as _time

        self._executor = compute_executor
        self._store_writer = store_writer
        self._broadcast_sink = broadcast_sink
        self._chunk_size = max(1, int(chunk_size))
        self._max_symbols = int(max_symbols)
        self._max_factors = int(max_factors)
        self._compute_budget = float(compute_budget_seconds)
        self._batch_timeout = float(batch_timeout_seconds)
        self._clock = clock or _time.monotonic

    # -------------------------------------------------------------- 容量规划

    def capacity_plan(self, symbols: Sequence[str], factor_ids: Sequence[str]) -> CapacityPlan:
        """7000+标的×N_max-4因子容量规划校验。"""
        n_symbols, n_factors = len(symbols), len(factor_ids)
        reason = ""
        if n_symbols > self._max_symbols:
            reason = f"标的数 {n_symbols} 超容量上限 {self._max_symbols}"
        elif n_factors > self._max_factors:
            reason = f"因子数 {n_factors} 超容量上限 {self._max_factors}（N_max-4 口径）"
        return CapacityPlan(
            symbols=n_symbols,
            factors=n_factors,
            estimated_cells=n_symbols * n_factors,
            within_budget=reason == "",
            max_symbols=self._max_symbols,
            max_factors=self._max_factors,
            reason=reason,
        )

    # -------------------------------------------------------------- 批算编排

    @staticmethod
    def _chunks(symbols: Sequence[str], size: int) -> Iterable[tuple[str, ...]]:
        for i in range(0, len(symbols), size):
            yield tuple(symbols[i : i + size])

    def _run(
        self, symbols: Sequence[str], factor_ids: Sequence[str], mode: ComputeMode
    ) -> BatchVerdict:
        if not symbols or not factor_ids:
            return BatchVerdict(mode=mode, symbols_done=0, degraded=False)

        done = 0
        rows_total = 0
        timeout_count = 0
        reasons: list[str] = []
        started = self._clock()

        for chunk in self._chunks(list(symbols), self._chunk_size):
            elapsed = self._clock() - started
            if elapsed >= self._compute_budget:
                reasons.append(
                    f"算力预算耗尽（{elapsed:.1f}s≥{self._compute_budget:.1f}s），"
                    f"剩余 {len(symbols) - done} 标的降级跳过"
                )
                break
            chunk_start = self._clock()
            try:
                rows = self._executor(chunk, factor_ids, mode)
            except Exception as exc:  # noqa: BLE001 — 单块失败降级不中断
                log.warning("factor_production_pipeline: 块计算失败降级: %s", exc)
                reasons.append(f"块计算失败: {exc}")
                continue
            chunk_elapsed = self._clock() - chunk_start
            if chunk_elapsed > self._batch_timeout:
                timeout_count += 1
                reasons.append(
                    f"块超时（{chunk_elapsed:.1f}s>{self._batch_timeout:.1f}s）结果仍落库并标记"
                )
            if self._store_writer is not None and rows:
                try:
                    self._store_writer(rows)
                    rows_total += len(rows)
                except Exception as exc:  # noqa: BLE001 — 落库失败降级不中断
                    log.warning("factor_production_pipeline: 落库失败降级: %s", exc)
                    reasons.append(f"落库失败: {exc}")
            done += len(chunk)

        if self._broadcast_sink is not None:
            summary = {
                "mode": mode.value,
                "symbols_done": done,
                "rows": rows_total,
                "degraded": bool(reasons),
            }
            try:
                self._broadcast_sink(summary)
            except Exception:  # noqa: BLE001 — 广播失败不阻断
                log.warning("factor_production_pipeline: 广播失败", exc_info=True)

        return BatchVerdict(
            mode=mode,
            symbols_done=done,
            degraded=bool(reasons),
            timeout_count=timeout_count,
            rows_persisted=rows_total,
            reason="；".join(reasons),
        )

    def run_premarket(self, symbols: Sequence[str], factor_ids: Sequence[str]) -> BatchVerdict:
        """盘前全量批算（分块编排+算力预算+超时降级）。"""
        return self._run(symbols, factor_ids, ComputeMode.PREMARKET_FULL)

    def run_intraday(
        self,
        symbols: Sequence[str],
        factor_ids: Sequence[str],
        event: Mapping[str, Any] | None = None,
    ) -> BatchVerdict:
        """盘中增量（事件驱动；event 为触发事件载荷，执行体可据此缩小计算面）。"""
        del event  # MVP：事件载荷透传执行体语义留运行时装配批；mode 即增量标记
        return self._run(symbols, factor_ids, ComputeMode.INTRADAY_INCREMENTAL)
