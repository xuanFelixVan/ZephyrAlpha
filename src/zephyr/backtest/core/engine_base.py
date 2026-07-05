# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.core.engine_base
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-BT-001-engine_base | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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
from typing import Any, ClassVar

# ==== BEGIN CODGEN:CTR-P1-016 ====
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.backtest.core.engine_base
# [DOMAIN] D_INFRASTRUCTURE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] frozen dataclass; SSoT=cross_layer_contracts.yaml; DO NOT EDIT (codegen)
# [TTL] permanent
# [TTL] permanent
# [MODIFY-GUARD] cross_layer_contracts.yaml; generate_contracts.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
from dataclasses import dataclass, field

from datetime import datetime, timezone
from typing import Optional

from zephyr.shared.contracts.core.trace_context import TraceContext
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-07-02"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/engine_base.py

CTR-P1-016: BacktestResult / 回测结果

D_BACKTEST域产出的标准化回测结果契约。包含绩效指标、交易统计、净值曲线引用。下游D_PORTFOLIO_CORE组合构建层用于策略遴选,D_RISK风控层用于风险预算校准,遥测运维层用于回测任务监控。

SSoT: cross_layer_contracts.yaml -> CTR-P1-016
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    当回测引擎完成一次运行后,MUST 产出 BacktestResult。 strategy_id 必须对应策略注册表中已注册的策略 key。 所有收益率指标(total_return/annual_return/sharpe_ratio/max_drawdown)使用 float 类型——这些是聚合指标,非逐笔价格,允许 float。 trades_count 是总交易笔数,win_rate 是胜率(0.0-1.0)。 D_PORTFOLIO_CORE 组合构建层使用此结果做策略遴选(sharpe_ratio > 阈值才纳入候选池)。 D_RISK 风控层使用 max_drawdown 做风险预算校准。 若 overfitting_flag = True,下游应降低该策略权重或拒绝采纳。
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
    benchmark_symbol: Optional[str] = None
    overfitting_flag: bool = False
    schema_version: str = "1.0"
    trace_context: Optional[TraceContext] = None

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


__all__ = ["BacktestEngineBase", "BacktestResult", "FactorDiscovery"]
