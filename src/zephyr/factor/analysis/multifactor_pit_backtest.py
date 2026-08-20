# [BLUEPRINT] MOD-L02-015 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-ANA-13
# [MODULE] zephyr.factor.analysis.multifactor_pit_backtest
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] multifactor_degradation_chain(§3.7#1)
# [CONSUMERS] 多因子 sleeve 首批回测
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] INV-004: PIT铁律——5层PIT断言(factor/ic_weight/synthesis/covariance/industry); 违规即抛PITViolationError不静默
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PIT违规->PITViolationError(fail-closed); 数据缺失->当日记录skipped继续
# [TESTS] tests/factor/test_multifactor_pit_backtest.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: decision_dates + 注入式数据回调(load_factors/load_ic_history/load_covariance/load_industry) + PITBacktestParams(ic_window=60/cov_window=60)
# F1: 5层PIT断言(assert_factor_pit/assert_ic_weight_pit/assert_covariance_pit/assert_industry_pit, 违规抛错)
# F2: run_backtest主循环(①因子值AS OF JOIN+断言 ②IC历史截止t-1+断言 ③降级链决策(forward_returns=None防前瞻) ④合成因子分 ⑤协方差+断言 ⑥组合优化+仲裁(注入) ⑦换仓触发(首次=INIT) ⑧非换仓日持仓偏差监控(critical→DRIFT_CRITICAL强制换仓) ⑨记录)
# O1: list[BacktestDayRecord](日期/方法/触发器/偏差警报数/skipped)
# [/ALGO_FLOW]
"""25号memo §3.7#7 多因子 PIT 安全回测框架（MultifactorPITBacktestFramework，MOD-L02-015）。

与 24 号 DabanPITBacktestFramework 对称的回测验证基础设施——多因子 PIT 更复杂，
5 层 PIT 断言防回测虚高（PIT 违规=回测虚高+实盘失效）：

  | 层 | 规则 |
  | factor_value | AS OF JOIN：t 日决策只用 t 日及之前因子值 |
  | ic_weight | ROLLING t-1：IC 权重来自 t-1 日及之前历史 IC |
  | synthesis_weight | t 因子 + t-1 权重 |
  | covariance | ROLLING t-1：协方差用 t-1 日及之前数据 |
  | industry_class | AS OF JOIN：行业分类 t 日及之前 |

注入式骨架：数据加载/组合优化/换仓触发/偏差监控均经回调注入，
本框架只编排主循环 + 强制 5 层 PIT 断言（首批回测前必做）。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Callable

import pandas as pd

from zephyr.factor.analysis.multifactor_degradation_chain import (
    synthesize_with_degradation,
    SynthesisDecision,
)

log = logging.getLogger(__name__)

__all__ = [
    "PITViolationError",
    "PITBacktestParams",
    "BacktestDayRecord",
    "assert_factor_pit",
    "assert_ic_weight_pit",
    "assert_covariance_pit",
    "assert_industry_pit",
    "MultifactorPITBacktestFramework",
]


class PITViolationError(Exception):
    """PIT 违规——未来函数检测（fail-closed，回测立即中止）。"""


@dataclass(frozen=True)
class PITBacktestParams:
    """PIT 回测参数（25号memo §3.7#7）。"""

    ic_window: int = 60  # IC 滚动窗口
    cov_window: int = 60  # 协方差滚动窗口


def assert_factor_pit(factor_date: pd.Timestamp, decision_date: pd.Timestamp) -> None:
    """factor_value 层：t 日决策只用 t 日及之前因子值（AS OF JOIN）。"""
    if pd.Timestamp(factor_date) > pd.Timestamp(decision_date):
        raise PITViolationError(f"factor_value PIT 违规: factor_date {factor_date} > decision_date {decision_date}")


def assert_ic_weight_pit(ic_window_end: pd.Timestamp, decision_date: pd.Timestamp) -> None:
    """ic_weight 层：IC 窗口截止日 < 决策日（ROLLING t-1，防 t 日 IC 算 t 日权重）。"""
    if pd.Timestamp(ic_window_end) >= pd.Timestamp(decision_date):
        raise PITViolationError(f"ic_weight PIT 违规: ic_window_end {ic_window_end} >= decision_date {decision_date}")


def assert_covariance_pit(cov_window_end: pd.Timestamp, decision_date: pd.Timestamp) -> None:
    """covariance 层：协方差截止日 < 决策日（ROLLING t-1）。"""
    if pd.Timestamp(cov_window_end) >= pd.Timestamp(decision_date):
        raise PITViolationError(
            f"covariance PIT 违规: cov_window_end {cov_window_end} >= decision_date {decision_date}"
        )


def assert_industry_pit(industry_date: pd.Timestamp, decision_date: pd.Timestamp) -> None:
    """industry_class 层：行业分类 AS OF JOIN（t 日及之前）。"""
    if pd.Timestamp(industry_date) > pd.Timestamp(decision_date):
        raise PITViolationError(
            f"industry_class PIT 违规: industry_date {industry_date} > decision_date {decision_date}"
        )


@dataclass(frozen=True)
class BacktestDayRecord:
    """单决策日回测记录。"""

    date: pd.Timestamp
    method: str = ""  # 合成方法（regression/ic_weighted/equal_weight）
    trigger: str = ""  # 换仓触发器（INIT/TIME/DRIFT/SIGNAL/HOLD/DRIFT_CRITICAL）
    drift_alerts: int = 0  # 持仓偏差警报数
    skipped: bool = False  # 数据缺失当日跳过
    note: str = ""


class MultifactorPITBacktestFramework:
    """多因子 PIT 安全回测框架——注入式主循环 + 5 层 PIT 断言。

    数据回调契约（全部注入，框架不直接读数仓）：
      load_factors(date) -> (factor_values: dict[str, pd.Series], factor_date)
      load_ic_history(date, ic_window) -> (ic_history: dict[str, list[float]], ic_window_end)
      load_covariance(date, cov_window) -> (covariance, cov_window_end)
      load_industry(date) -> (industry_map, industry_date)
      optimize_fn(signal, covariance, industry_map) -> target_weights（§3.5 七约束链+§3.7#2 仲裁）
      rebalance_fn(days_since_last, drift, rank_change) -> 触发器名（§3.7#6；None→仅保底）
      drift_monitor_fn(current_weights, target_weights) -> (alerts, critical_count)（§3.7#8）
    """

    def __init__(
        self,
        load_factors: Callable,
        load_ic_history: Callable,
        load_covariance: Callable | None = None,
        load_industry: Callable | None = None,
        optimize_fn: Callable | None = None,
        rebalance_fn: Callable | None = None,
        drift_monitor_fn: Callable | None = None,
        params: PITBacktestParams | None = None,
    ) -> None:
        self._load_factors = load_factors
        self._load_ic_history = load_ic_history
        self._load_covariance = load_covariance
        self._load_industry = load_industry
        self._optimize_fn = optimize_fn
        self._rebalance_fn = rebalance_fn
        self._drift_monitor_fn = drift_monitor_fn
        self._params = params or PITBacktestParams()

    def run_backtest(self, decision_dates: list[pd.Timestamp]) -> list[BacktestDayRecord]:
        """回测主循环（每决策日 9 步，memo §3.7#7）。"""
        records: list[BacktestDayRecord] = []
        days_since_last = 0
        initialized = False  # 首次有效决策日=INIT 建仓（骨架模式与 optimize_fn 解耦）
        current_weights: dict[str, float] = {}
        for date in decision_dates:
            date = pd.Timestamp(date)
            # ① 因子值 AS OF JOIN 加载 + 断言
            factor_values, factor_date = self._load_factors(date)
            if not factor_values:
                records.append(BacktestDayRecord(date, skipped=True, note="因子值缺失"))
                days_since_last += 1
                continue
            assert_factor_pit(factor_date, date)
            # ② IC 历史加载（窗口截止 t-1）+ 断言
            ic_history, ic_end = self._load_ic_history(date, self._params.ic_window)
            assert_ic_weight_pit(ic_end, date)
            # ③ 合成降级链决策（forward_returns=None 避免前瞻）
            signal, decision = synthesize_with_degradation(factor_values, ic_history, forward_returns=None)
            # ⑤ 协方差加载 + 断言（提供时）
            covariance = None
            if self._load_covariance is not None:
                covariance, cov_end = self._load_covariance(date, self._params.cov_window)
                assert_covariance_pit(cov_end, date)
            # 行业分类 AS OF JOIN（提供时）
            industry_map = None
            if self._load_industry is not None:
                industry_map, ind_date = self._load_industry(date)
                assert_industry_pit(ind_date, date)
            # ⑦ 换仓触发（首次建仓=INIT）
            if not initialized:
                trigger = "INIT"
            elif self._rebalance_fn is not None:
                trigger = str(self._rebalance_fn(days_since_last, 0.0, 0.0))
            else:
                trigger = "TIME" if days_since_last >= 5 else "HOLD"
            # ⑧ 非换仓日跑持仓偏差监控，critical→DRIFT_CRITICAL 强制换仓
            drift_alerts = 0
            if trigger == "HOLD" and self._drift_monitor_fn is not None:
                alerts, critical = self._drift_monitor_fn(current_weights, {})
                drift_alerts = len(alerts)
                if critical > 0:
                    trigger = "DRIFT_CRITICAL"
            # ⑥ 组合优化（换仓日且注入优化器时）
            if trigger != "HOLD":
                initialized = True
                if self._optimize_fn is not None:
                    current_weights = self._optimize_fn(signal, covariance, industry_map) or {}
                days_since_last = 0
            else:
                days_since_last += 1
            # ⑨ 记录
            records.append(
                BacktestDayRecord(
                    date=date,
                    method=decision.method,
                    trigger=trigger,
                    drift_alerts=drift_alerts,
                )
            )
        return records
