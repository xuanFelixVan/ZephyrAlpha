# [BLUEPRINT] MOD-L09-001 | docs/03_modules/_domain-research/research-core/blueprint.md
# [MODULE] zephyr.research.simulation.backtest_base
# [DOMAIN] D-SIMULATION
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_backtest_base | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
L09 — Research & Innovation Layer

研究与创新层。负责离线研究、回测、策略孵化与知识沉淀。

核心职责：
  - 因子挖掘与验证（IC / IR / t-stat）
  - 策略回测引擎（walk-forward / cross-validation）
  - 实验管理（实验注册、结果追踪、A/B 对比）
  - 知识库沉淀（将验证通过的因子提升至 L02/L03 管线）

跨层契约：
  CTR-001  NormalizedMarketData           ← L00（消费者——行情数据上下文）
  CTR-P1-014  ExperimentResult             ← L13（消费者——实验结论指导研究方向）
  CTR-P1-010  SystemConfiguration          ← L01（全局配置消费者）

SSoT: cross_layer_contracts.yaml v3.0
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar


@dataclass(frozen=True)
class BacktestResult:
    """回测结果"""

    strategy_id: str
    start_date: str
    end_date: str
    total_return: float
    annual_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    trades_count: int
    timestamp: datetime = field(default_factory=datetime.utcnow)


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
