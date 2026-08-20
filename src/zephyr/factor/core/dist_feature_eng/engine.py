# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-CORE-DFE
# [MODULE] zephyr.factor.core.dist_feature_eng.engine
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.core.factor_dag; zephyr.factor.core.backpressure; zephyr.factor.factor_base
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 层间串行（依赖约束）；层内跨标的并行（ProcessPoolExecutor）；max_workers=1 退化为串行；INV-004 PIT 铁律——子进程仅用传入的同期数据
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单标的失败不阻断其他标的；子进程入口 compute_factor_for_symbol 必须可 pickle；因子未注册返回 error
# [TESTS] tests/factor/test_dist_feature_eng.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D_FACTOR core dist_feature_eng.engine——分布式特征工程引擎。

用 ProcessPoolExecutor 跨进程并行计算因子（绕开 GIL，适合 CPU 密集计算）。
按标的分片，每片在子进程内独立调用因子 compute。

调度策略：
- 外层：dag.topological_layers() 串行推进
- 内层：对当前层每个 factor_id，跨 symbols 用 ProcessPoolExecutor 并行
- backpressure：acquire/release 控制在途 futures 数量

与 dag_manager 的边界：
- dag_manager 用 ThreadPoolExecutor（IO/轻计算，GIL 下够用）
- dist_feature_eng 用 ProcessPoolExecutor（CPU 密集，绕 GIL）
- 两者并存供调用方按场景选

退化模式（max_workers<=1）：
- 不再起子进程，主进程内同步串行调用 compute_factor_for_symbol
- 用途：单测/调试/轻量数据；避开 spawn 模式子进程无法继承运行时注册表的问题

子进程注册约定（max_workers>1 时）：
- compute_factor_for_symbol 内通过 FactorRegistry.get(factor_id) 查询因子类
- 子进程必须能 import 到因子类（@FactorRegistry.register 在 import 时触发）
- 调用方须在主进程 import 因子模块（如 zephyr.factor.momentum_factor），
  子进程通过 fork/spawn 继承注册表（spawn 模式下子进程会重新 import 主模块）
- 运行时动态注册的因子（非 import 时注册）在 spawn 子进程不可见，须用 max_workers<=1
"""

from __future__ import annotations

import logging
import time
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeout
from dataclasses import dataclass, field

import pandas as pd

from zephyr.factor.core.backpressure.limiter import BackpressureLimiter
from zephyr.factor.core.config_manager.loader import get_section
from zephyr.factor.core.factor_dag.dag import FactorDAG
from zephyr.factor.factor_base import FactorRegistry

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class DistEngConfig:
    """分布式引擎配置。

    Attributes:
        max_workers: ProcessPoolExecutor 工作进程数（1=退化为串行）
        factor_timeout_s: 单标的因子计算超时秒数
    """

    max_workers: int = 4
    factor_timeout_s: float = 120.0


def _default_config() -> DistEngConfig:
    """从 core/_config.yaml 的 dist_feature_eng 节构建默认配置（真源=YAML，缺省回退常量）。"""
    s = get_section("dist_feature_eng")
    return DistEngConfig(
        max_workers=int(s.get("max_workers", 4)),
        factor_timeout_s=float(s.get("factor_timeout_s", 120.0)),
    )


@dataclass
class DistEngResult:
    """单因子分布式执行结果。

    Attributes:
        factor_id: 因子 ID
        panel: 因子面板（index=date, columns=symbol）
        failed_symbols: 失败标的列表
        duration_s: 本因子执行时长（秒）
    """

    factor_id: str
    panel: pd.DataFrame
    failed_symbols: list[str] = field(default_factory=list)
    duration_s: float = 0.0


def compute_factor_for_symbol(
    factor_id: str,
    symbol: str,
    data: pd.DataFrame,
    kwargs: dict | None = None,
) -> tuple[str, str, pd.Series | None, str]:
    """子进程入口纯函数：单标的单因子计算。

    必须是模块级函数（pickle 要求）。子进程通过 FactorRegistry.get 查询因子类。

    Args:
        factor_id: 已注册的因子 ID
        symbol: 标的代码
        data: 单标的的 OHLCV 数据（index=date）
        kwargs: 传给 compute 的额外参数

    Returns:
        (symbol, factor_id, series, error)
        - 成功：series=因子值 pd.Series，error=""
        - 失败：series=None，error=失败原因
    """
    try:
        factor_cls = FactorRegistry.get(factor_id)
        factor = factor_cls()
        series = factor.compute(data, **(kwargs or {}))
        return (symbol, factor_id, series, "")
    except KeyError:
        return (symbol, factor_id, None, f"factor '{factor_id}' not registered")
    except Exception as e:  # noqa: BLE001 — 子进程入口纯函数：单标的失败须回传 error 不抛出（进程池边界容错契约）
        return (symbol, factor_id, None, f"compute error: {e}")


class DistributedFeatureEngine:
    """分布式特征工程引擎——跨标的并行计算因子。

    Usage::

        dag = build_dag_from_registry(["momentum_20d", "value_5d"])
        engine = DistributedFeatureEngine(DistEngConfig(max_workers=4))
        results = engine.execute(dag, history_data)
        # results["momentum_20d"].panel 是 (date, symbol) 面板
    """

    def __init__(
        self,
        config: DistEngConfig | None = None,
        backpressure: BackpressureLimiter | None = None,
    ) -> None:
        self._config = config or _default_config()
        self._bp = backpressure

    def execute(
        self,
        dag: FactorDAG,
        data: pd.DataFrame,
        extra_kwargs: dict[str, dict] | None = None,
    ) -> dict[str, DistEngResult]:
        """分层并行 + 跨标的并行执行。

        Args:
            dag: FactorDAG 实例
            data: MultiIndex (symbol, date) 的行情数据
            extra_kwargs: factor_id -> kwargs 映射

        Returns:
            factor_id -> DistEngResult 映射

        Notes:
            - data 必须是 MultiIndex (symbol, date)，否则抛 ValueError
            - max_workers=1 时退化为串行（仍走 ProcessPoolExecutor 接口）
            - 单标的失败不阻断其他标的，记入 failed_symbols
        """
        if not isinstance(data.index, pd.MultiIndex):
            raise ValueError(f"data 必须是 MultiIndex (symbol, date)，实际收到 {type(data.index).__name__}")
        if "symbol" not in data.index.names or "trade_date" not in data.index.names:
            # 兼容 "date" 别名
            names_lower = [n.lower() for n in data.index.names]
            if "symbol" not in names_lower or not any(n in ("trade_date", "date") for n in names_lower):
                raise ValueError(
                    f"data.index.names 必须含 'symbol' 和 'trade_date'（或 'date'），实际 {data.index.names}"
                )

        kwargs_map = extra_kwargs or {}
        layers = dag.topological_layers()
        results: dict[str, DistEngResult] = {}

        if self._config.max_workers <= 1:
            # 退化模式：主进程内同步串行，不子进程化
            # 用途：单测/调试/轻量数据；避开 spawn 子进程无法继承运行时注册表
            for layer in layers:
                for fid in layer:
                    results[fid] = self._execute_one_factor_serial(fid, data, kwargs_map.get(fid, {}))
            return results

        # ProcessPoolExecutor 在整个 execute 期间复用（避免每层重建开销）
        with ProcessPoolExecutor(max_workers=self._config.max_workers) as pool:
            for layer in layers:
                for fid in layer:
                    result = self._execute_one_factor(pool, fid, data, kwargs_map.get(fid, {}))
                    results[fid] = result

        return results

    def _execute_one_factor(
        self,
        pool: ProcessPoolExecutor,
        factor_id: str,
        data: pd.DataFrame,
        kwargs: dict,
    ) -> DistEngResult:
        """执行单因子：跨标的并行计算。"""
        start_ts = time.monotonic()
        symbols = data.index.get_level_values("symbol").unique().tolist()

        # 提交所有标的的 future
        futures: dict = {}  # future -> symbol
        for symbol in symbols:
            symbol_data = data.xs(symbol, level="symbol")
            if self._bp is not None:
                if not self._bp.acquire():
                    log.warning("dist_feature_eng: backpressure 拒绝 %s/%s", factor_id, symbol)
                    continue
            future = pool.submit(compute_factor_for_symbol, factor_id, str(symbol), symbol_data, kwargs)
            futures[future] = symbol

        # 收集结果
        series_map: dict[str, pd.Series] = {}
        failed: list[str] = []
        for future in futures:
            symbol = futures[future]
            try:
                sym, fid, series, error = future.result(timeout=self._config.factor_timeout_s)
                if series is not None and not error:
                    series_map[sym] = series
                else:
                    failed.append(sym)
                    log.warning("dist_feature_eng: %s/%s 失败: %s", factor_id, sym, error)
            except FutureTimeout:
                failed.append(symbol)
                log.warning("dist_feature_eng: %s/%s 超时", factor_id, symbol)
            except Exception as e:  # noqa: BLE001 — 单标的失败不阻断其他标的（错误契约：记入 failed_symbols）
                failed.append(symbol)
                log.warning("dist_feature_eng: %s/%s 异常: %s", factor_id, symbol, e)
            finally:
                if self._bp is not None:
                    self._bp.release()

        # 组装面板（index=date, columns=symbol）
        if series_map:
            panel = pd.DataFrame(series_map)
        else:
            panel = pd.DataFrame()

        return DistEngResult(
            factor_id=factor_id,
            panel=panel,
            failed_symbols=failed,
            duration_s=time.monotonic() - start_ts,
        )

    def _execute_one_factor_serial(
        self,
        factor_id: str,
        data: pd.DataFrame,
        kwargs: dict,
    ) -> DistEngResult:
        """退化模式（max_workers<=1）：主进程内同步串行执行单因子。

        与 _execute_one_factor 行为一致，但直接调用 compute_factor_for_symbol，
        不经过 ProcessPoolExecutor，从而：
        - 避开 spawn 子进程无法继承运行时注册表的问题
        - backpressure 仍按 acquire/release 控制（虽然串行下 inflight 至多 1）
        """
        start_ts = time.monotonic()
        symbols = data.index.get_level_values("symbol").unique().tolist()

        series_map: dict[str, pd.Series] = {}
        failed: list[str] = []
        for symbol in symbols:
            symbol_data = data.xs(symbol, level="symbol")
            if self._bp is not None and not self._bp.acquire():
                log.warning("dist_feature_eng: backpressure 拒绝 %s/%s", factor_id, symbol)
                failed.append(str(symbol))
                continue
            try:
                sym, _fid, series, error = compute_factor_for_symbol(factor_id, str(symbol), symbol_data, kwargs)
                if series is not None and not error:
                    series_map[sym] = series
                else:
                    failed.append(sym)
                    log.warning("dist_feature_eng: %s/%s 失败: %s", factor_id, sym, error)
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                failed.append(str(symbol))
                log.warning("dist_feature_eng: %s/%s 异常: %s", factor_id, symbol, e)
            finally:
                if self._bp is not None:
                    self._bp.release()

        if series_map:
            panel = pd.DataFrame(series_map)
        else:
            panel = pd.DataFrame()

        return DistEngResult(
            factor_id=factor_id,
            panel=panel,
            failed_symbols=failed,
            duration_s=time.monotonic() - start_ts,
        )
