# [BLUEPRINT] MOD-ML-006 | docs/03_modules/_domain_machine_learning_train/blueprint.md
# [MODULE] zephyr.ml_train.strategy_digital_twin
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES] numpy
# [CONSUMERS] （策略上线前沙盘推演消费方）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] T+1 执行无未来函数——第 t 日信号吃 t→t+1 收益；信号 ∈ [-1,1]；价格必须为正有限；纯计算无副作用
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DigitalTwinError(ZA-MLT-0010)——长度不符/序列过短/价格非正/信号越界/非有限值
# [TESTS] tests/ml_train/test_strategy_digital_twin.py
# [A_module] module_id=MOD-ML-006 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
策略数字孪生（MOD-ML-006）——轻量可单测实现。

策略上线前的沙盘镜像：给定信号序列（[-1,1] 目标仓位）与价格序列，按 T+1 语义
（当日信号次日生效，与 A 股 T+1 交割约束四一致）推演权益曲线，产出总收益/
最大回撤/Sharpe/换手次数。不含成本模型（成本属回测域统一框架，见宪章 §3 约束一，
本孪生只做信号-路径形态验证）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: strategy_digital_twin.py
# 层: 算法
# - id: A1
#   name_zh: ① StrategyDigitalTwin
#   name_en: StrategyDigitalTwin
#   intro: 策略数字孪生（T+1 无未来函数沙盘）。
#   desc: 策略数字孪生（T+1 无未来函数沙盘）。；公共方法（定义序）: simulate；源码 L88-L128
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: StrategyDigitalTwin
#   downstream: （策略上线前沙盘推演消费方）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import numpy as np

__all__: Final = [
    "DigitalTwinError",
    "StrategyDigitalTwin",
    "TwinSimulationResult",
]

_TRADING_DAYS_PER_YEAR: Final[int] = 252
_MIN_LENGTH: Final[int] = 2


class DigitalTwinError(Exception):
    """ZA-MLT-0010: 数字孪生仿真输入非法。"""

    error_code = "ZA-MLT-0010"


@dataclass(frozen=True)
class TwinSimulationResult:
    """数字孪生推演结果。"""

    equity_curve: np.ndarray
    total_return: float
    max_drawdown: float
    sharpe: float
    n_trades: int


class StrategyDigitalTwin:
    """策略数字孪生（T+1 无未来函数沙盘）。"""

    def simulate(self, signals: np.ndarray, prices: np.ndarray) -> TwinSimulationResult:
        s = np.asarray(signals, dtype=float).ravel()
        p = np.asarray(prices, dtype=float).ravel()
        if s.shape != p.shape:
            raise DigitalTwinError(f"信号/价格长度不符: {s.size} vs {p.size}")
        if s.size < _MIN_LENGTH:
            raise DigitalTwinError(f"序列过短（≥{_MIN_LENGTH}）: {s.size}")
        if not np.all(np.isfinite(s)) or not np.all(np.isfinite(p)):
            raise DigitalTwinError("输入含非有限值")
        if np.any(p <= 0.0):
            raise DigitalTwinError("价格必须为正")
        if np.any((s < -1.0) | (s > 1.0)):
            raise DigitalTwinError("信号必须 ∈ [-1,1]")

        # T+1：第 t 日信号吃 t→t+1 收益（position[t] = signal[t-1]，首日无仓位）
        returns = p[1:] / p[:-1] - 1.0
        position = s[:-1]
        strategy_returns = position * returns
        equity = np.concatenate([[1.0], np.cumprod(1.0 + strategy_returns)])

        running_max = np.maximum.accumulate(equity)
        drawdowns = equity / running_max - 1.0
        max_drawdown = float(drawdowns.min())

        if strategy_returns.std() > 0.0:
            sharpe = float(strategy_returns.mean() / strategy_returns.std() * np.sqrt(_TRADING_DAYS_PER_YEAR))
        else:
            sharpe = 0.0

        position_changes = int(np.count_nonzero(np.diff(s) != 0.0))

        return TwinSimulationResult(
            equity_curve=equity,
            total_return=float(equity[-1] - 1.0),
            max_drawdown=max_drawdown,
            sharpe=sharpe,
            n_trades=position_changes,
        )
