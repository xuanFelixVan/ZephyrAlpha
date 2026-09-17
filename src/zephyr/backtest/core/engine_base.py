# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.core.engine_base
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES]zephyr.shared.contracts.core.trace_context
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/backtest/test_engine_base.py
# [TTL] permanent
"""
L_BACKTEST — Backtest Engine Layer

回测引擎层。负责离线研究、回测、策略孵化与知识沉淀。

核心职责：
  - 因子挖掘与验证（IC / IR / t-stat）
  - 策略回测引擎（walk-forward / cross-validation）
  - 实验管理（实验注册、结果追踪、A/B 对比）
  - 知识库沉淀（将验证通过的因子提升至 D_FACTOR/D_SIGNAL 管线）

跨层契约：
  CTR-001  NormalizedMarketData           ← D_DATA（消费者——行情数据上下文）
  CTR-P1-014  ExperimentResult             ← 实验（消费者——实验结论指导研究方向）
  CTR-P1-010  SystemConfiguration          ← 基础设施（全局配置消费者）

SSoT: cross_layer_contracts.yaml v3.0
"""

from __future__ import annotations

import abc

# ==== BEGIN CODGEN:CTR-P1-016 ====
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.backtest.core.engine_base
# [DOMAIN] D_INFRASTRUCTURE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] frozen dataclass; SSoT=cross_layer_contracts.yaml; DO NOT EDIT (codegen)
# [MODIFY-GUARD] cross_layer_contracts.yaml; generate_contracts.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, ClassVar, Optional

from zephyr.shared.contracts.core.trace_context import TraceContext

# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-08-02"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/engine_base.py

CTR-P1-016: BacktestResult / 回测结果

D_BACKTEST域产出的标准化回测结果契约。包含绩效指标、交易统计、净值曲线引用。下游Portfolio组合构建层用于策略遴选,Risk风控层用于风险预算校准,Telemetry运维层用于回测任务监控。

SSoT: cross_layer_contracts.yaml -> CTR-P1-016
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    当回测引擎完成一次运行后,MUST 产出 BacktestResult。 strategy_id 必须对应策略注册表中已注册的策略 key。 所有收益率指标(total_return/annual_return/sharpe_ratio/max_drawdown)使用 float 类型——这些是聚合指标,非逐笔价格,允许 float。 trades_count 是总交易笔数,win_rate 是胜率(0.0-1.0)。 Portfolio 组合构建层使用此结果做策略遴选(sharpe_ratio > 阈值才纳入候选池)。 Risk 风控层使用 max_drawdown 做风险预算校准。 若 overfitting_flag = True,下游应降低该策略权重或拒绝采纳。
"""


@dataclass(frozen=True)
class BacktestResult:
    annual_return: float
    end_date: datetime
    idempotency_key: str
    max_drawdown: float
    sharpe_ratio: float
    start_date: datetime
    strategy_id: str
    timestamp: datetime
    total_return: float
    trades_count: int
    win_rate: float
    benchmark_symbol: str | None = None
    map_snapshot: str = ""
    overfitting_flag: bool = False
    schema_version: str = "1.0"
    trace_context: TraceContext | None = None


# ==== END CODGEN:CTR-P1-016 ====
@dataclass(frozen=True)
class FactorDiscovery:
    """因子发现记录"""

    factor_id: str
    name: str
    ic_mean: float
    ic_ir: float
    t_stat: float
    status: str = "candidate"  # candidate | validated | promoted | rejected


_map_snapshot_cache: str | None = None


def current_map_snapshot() -> str:
    """当前地图快照 commit 号（git rev-parse --short HEAD，进程内缓存一次）。

    PB-06 轻量快照绑定（真源 docs/_working/2026-09-09-node-backtest-governance.md §7.1）：
    回测 run 结果自动带一行 commit 号，不做门禁不做必填；git 不可用/超时降级空串。
    进程内缓存：同一进程内 HEAD 不变（commit 是会话级动作），零循环 git 开销。
    """
    global _map_snapshot_cache
    if _map_snapshot_cache is None:
        try:
            import subprocess
            from zephyr.shared.io.paths import REPO_ROOT
            _map_snapshot_cache = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=5,
            ).stdout.strip() or ""
        except Exception:   # noqa: BLE001 — 快照绑定是尽力而为，git 环境异常不阻断回测
            _map_snapshot_cache = ""
    return _map_snapshot_cache


class BacktestEngineBase(abc.ABC):
    """
    回测引擎基类（OCP 扩展点）

    实现者要求：接收信号序列 + 价格数据，输出标准回测报告。
    """

    _registry: ClassVar[dict[str, type[BacktestEngineBase]]] = {}

    @abc.abstractmethod
    def run(self, signals: list[Any], prices: list[Any]) -> BacktestResult:
        """执行回测，返回标准化结果"""
        ...


class LookaheadExecutionError(Exception):
    """前视执行防护异常（P0-1，2026-09-14 外部审查整改）。

    日频引擎默认强制 signal(T) → fill(T+1) 次根成交：
      - ``execution_lag_days < 1`` 且未显式 ``allow_same_bar_execution=True``
        时构造/运行即抛本异常（硬断言，无直觉例外）。
    同 bar 成交（当日信号按当日收盘价成交）是回测收益虚高的头号根因；
    确需同 bar 对照实验必须显式 allow_same_bar_execution=True，前视风险自担。
    """

    error_code = "ZA-BT-0040"


class ImplausibleBacktestError(Exception):
    """回测合理性护栏异常（P0-4，2026-09-14 外部审查整改）。

    触发条件（引擎默认全开，BacktestConfig.sanity_guard=False 可显式关闭）：
      - 极端收益：total_return 超出合理带（默认 -95% ~ +300%，30x 类失真必拦；
        数值单一真源=本模块 MAX/MIN_PLAUSIBLE_TOTAL_RETURN）；
      - 空跑：trades_count == 0 且未显式 allow_empty_trades=True。
    产物层配套：io.result_repository.save_artifact 对失真产物自动隔离至
    quarantine/ 目录，不进正库（ArtifactQuarantinedError）。
    """

    error_code = "ZA-BT-0041"


#: 合理性护栏收益带——**单一真源**（H5-F 治本 2026-09-17）。
#:
#: 病根：引擎层（本函数默认 10.0=+1000%）与产物层（io.result_repository 落盘兜底写死
#: 11.0x/0.05x）各持一套字面量，互不知情——"上限"有两个数，改一个漏一个，等于没有上限。
#: 现两层的数都从这两个常量推出来（倍数带 = 1+收益带），改口径只有一个落点。
#:
#: 为什么从 +1000% 收到 +300%：现网 52 份回测产物实证 total_return 最大 1.187（+118.7%）、
#: 净值首尾倍数最大 2.187x、最小 0.470x——收到 3.0/−0.95（=4.0x/0.05x）对现网零隔离，
#: 只砍掉"30x 神话"那段谁也解释不了的失真带。放宽/再收紧都要走裁定登记，禁在下游复述数值。
MAX_PLAUSIBLE_TOTAL_RETURN = 3.0
MIN_PLAUSIBLE_TOTAL_RETURN = -0.95


def plausible_equity_multiple_bounds() -> tuple[float, float]:
    """收益带换算成净值首尾倍数带 `(上, 下)`（产物层用，禁再写字面量）。

    净值曲线倍数=1+total_return 的同一条线，只是口径对 fraction/multiple 两种 metrics
    都稳健，故落盘兜底按倍数判、数值仍由本模块的收益带推出。
    """
    return (1.0 + MAX_PLAUSIBLE_TOTAL_RETURN, 1.0 + MIN_PLAUSIBLE_TOTAL_RETURN)


def enforce_result_plausibility(
    *,
    total_return: float,
    trades_count: int,
    max_plausible_total_return: float = MAX_PLAUSIBLE_TOTAL_RETURN,
    min_plausible_total_return: float = MIN_PLAUSIBLE_TOTAL_RETURN,
    allow_empty_trades: bool = False,
    result_id: str = "",
) -> list[str]:
    """回测结果合理性护栏（P0-4 共享真源，vectorized/event_driven 两引擎共同消费）。

    Args:
        total_return: 总收益率（小数口径，0.10=10%）
        trades_count: 成交笔数
        max_plausible_total_return: 收益合理上限（小数；默认=MAX_PLAUSIBLE_TOTAL_RETURN，
            数值与产物层同源，改口径只改本模块常量）
        min_plausible_total_return: 收益合理下限（默认=MIN_PLAUSIBLE_TOTAL_RETURN=-95%，
            无杠杆 long-only 不可能亏穿）
        allow_empty_trades: 显式放行 trades=0 空跑（对照实验用）
        result_id: 结果 id（仅用于报错信息定位）

    Returns:
        违规清单（空 list=通过）

    Raises:
        ImplausibleBacktestError: 存在违规（fail-closed，失真结果不产出）
    """
    violations: list[str] = []
    tr = float(total_return)
    if tr > float(max_plausible_total_return):
        violations.append(
            f"total_return={tr:.4f} 超过合理上限 +{float(max_plausible_total_return) * 100:.0f}%"
            "（前视/无限流动性失真嫌疑）"
        )
    if tr < float(min_plausible_total_return):
        violations.append(
            f"total_return={tr:.4f} 低于合理下限 {float(min_plausible_total_return) * 100:.0f}%"
            "（无杠杆 long-only 不可能）"
        )
    if int(trades_count) == 0 and not allow_empty_trades:
        violations.append(
            "trades_count=0 空跑（信号/撮合/配置失真嫌疑；确需空跑对照请 allow_empty_trades=True）"
        )
    if violations:
        raise ImplausibleBacktestError(
            f"回测合理性护栏拦截 (result_id={result_id or '-'}): " + "; ".join(violations)
        )
    return violations


__all__ = [
    "BacktestEngineBase",
    "BacktestResult",
    "FactorDiscovery",
    "current_map_snapshot",
    "LookaheadExecutionError",
    "ImplausibleBacktestError",
    "enforce_result_plausibility",
    "MAX_PLAUSIBLE_TOTAL_RETURN",
    "MIN_PLAUSIBLE_TOTAL_RETURN",
    "plausible_equity_multiple_bounds",
]
