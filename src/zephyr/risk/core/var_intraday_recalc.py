# [BLUEPRINT] MOD-RK-05D | (36号 §3.12 盘中重算) | §
# [TTL] permanent
# [MODULE] zephyr.risk.core.var_intraday_recalc
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.shared.foundation.errors; numpy; MOD-RK-05(VaR Calculator); MOD-RK-15(Tail Risk Monitor); MOD-RK-05C(VaR Breach 状态机,可选注入)
# [CONSUMERS] 35号 §3.13 intraday_risk_loop(盘中循环检测触发后调用,设计契约); RiskLayerOrchestrator(编排注入)
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] 7条触发任一满足即重算; 多触发去重(返回首个命中按优先级: 政策>涨跌停潮>传导>相关性>波动率>回撤>亏损, reason记录全部命中); 冷却期5分钟内不重算(suppressed留痕); 单日最多6次(达上限freq_cap_hit告警); 条件1基于clean NAV; var_change_ratio>20%→significant; 计数器日切重置
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidIntradayRecalcConfigError
# [TESTS] tests/risk/test_var_intraday_recalc.py
# [TTL] permanent

# [ALGO_FLOW]
# I1: IntradayTriggerInput(opening_nav/current_nav(clean NAV)/var_baseline_pct/回撤/5类布尔事件)
# I2: current_returns(盘中最新收益序列) + current_nav + premarket_baseline(盘前基线,可空)
# I3: IntradayRecalcConfig(亏损0.5×VaR/回撤8%/显著20%/冷却300s/日限6次)
# A1: intraday_var_recalc_trigger(7条件检测→优先级去重→冷却期/日频上限防抖→suppressed留痕)
# A2: intraday_var_recalc(var_calculator+tail_monitor重算→基线对比var_change_ratio>20%显著→breach状态机更新→recalc_log累积)
# O1: IntradayRecalcTrigger(triggered/first_trigger/reason/suppressed)
# O2: IntradayVarResult(var_95/cvar_95/breach_state/significant_change) → 35号 §3.13 重新 evaluate 覆盖盘前 response
# [/ALGO_FLOW]
"""

Intraday VaR Recalc — 盘中 VaR/ES 重算触发与执行 (36号 §3.12)

7 条触发条件 (任一满足即重算):
    1. 当前亏损 > 日内 VaR 的 50% (预警线, current_loss 基于 clean NAV 不含未实现 MtM)
    2. 当前回撤 > 8% (回撤 Protocol 一级阈值, 与 35号 §3.1 协同)
    3. 涨跌停潮 (与 G18 §3.5 涨跌停检测协同)
    4. 波动率 regime shift (30 分钟波动率 > 60 日均值 3σ, 上游检测)
    5. 相关性崩塌 (BS-002 前兆)
    6. 跨市场传导 (BS-005 前兆)
    7. 政策事件 (BS-006)

去重与防抖 (§3.12 v1.4.0):
    - 去重: 返回首个命中 trigger (优先级: 政策事件 > 涨跌停潮 > 跨市场传导 >
      相关性崩塌 > 波动率 regime shift > 回撤 > 亏损); 多条件同时满足只重算一次,
      trigger.reason 记录所有命中条件 (逗号分隔)
    - 冷却期: 重算后 5 分钟内不再重算; 冷却期内触发记入 suppressed_triggers 供审计
    - 频率上限: 单日最多重算 6 次; 达上限仅记录 intraday_recalc_freq_cap_hit 告警

执行 + 结果反馈链 (§3.12 D2): var_calculator.calculate + tail_risk_monitor.assess
重算 → 与盘前基线对比 (var_change_ratio > 0.20 → significant_change) →
更新 §3.15 breach 状态机 (注入时) → intraday_recalc_log 内存累积
(§3.18 阶段 3 由调用方经 backtest_store 持久化)。返回 IntradayVarResult 供
35号 §3.13 用新 var_cvar 重新调用 drawdown_controller.evaluate() 覆盖盘前 response
(取最严 = position_cap 取 min, 非 level 取 max)。

SSoT: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/36_var_es_monitoring.md §3.12
Version: 0.1.0
"""

from __future__ import annotations

import logging
import math
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any, Final

import numpy as np

from zephyr.risk.core.var_breach_state_machine import VarBreachStateMachine
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "IntradayRecalcConfig",
    "IntradayTriggerInput",
    "IntradayRecalcTrigger",
    "IntradayVarResult",
    "IntradayVarRecalcController",
    "InvalidIntradayRecalcConfigError",
]

logger = logging.getLogger(__name__)


class InvalidIntradayRecalcConfigError(ZephyrBaseError):
    """盘中重算配置/输入非法。"""

    error_code = "ZA-RK-0031"


@dataclass(frozen=True)
class IntradayRecalcConfig:
    """盘中重算配置 (C 类可调参数, §3.12)。

    Attributes:
        loss_var_ratio: 条件 1 预警线比例 (亏损 > 日内 VaR × 本比例, 默认 0.5)
        drawdown_threshold: 条件 2 回撤阈值 (默认 0.08=8%, 与 35号 §3.1 一级阈值协同)
        significant_change_ratio: 基线对比显著变化阈值 (var_change_ratio > 0.20)
        cooldown_seconds: 冷却期秒数 (默认 300=5 分钟)
        max_recalc_per_day: 单日重算频率上限 (默认 6, 约每 40 分钟一次覆盖 4 小时)
    """

    loss_var_ratio: float = 0.5
    drawdown_threshold: float = 0.08
    significant_change_ratio: float = 0.20
    cooldown_seconds: float = 300.0
    max_recalc_per_day: int = 6

    def __post_init__(self) -> None:
        if self.loss_var_ratio <= 0:
            raise InvalidIntradayRecalcConfigError(
                f"loss_var_ratio must be >0, got {self.loss_var_ratio}"
            )
        if not 0.0 < self.drawdown_threshold < 1.0:
            raise InvalidIntradayRecalcConfigError(
                f"drawdown_threshold must be in (0,1), got {self.drawdown_threshold}"
            )
        if self.significant_change_ratio <= 0:
            raise InvalidIntradayRecalcConfigError(
                f"significant_change_ratio must be >0, got {self.significant_change_ratio}"
            )
        if self.cooldown_seconds < 0:
            raise InvalidIntradayRecalcConfigError(
                f"cooldown_seconds must be >=0, got {self.cooldown_seconds}"
            )
        if self.max_recalc_per_day < 1:
            raise InvalidIntradayRecalcConfigError(
                f"max_recalc_per_day must be >=1, got {self.max_recalc_per_day}"
            )


@dataclass(frozen=True)
class IntradayTriggerInput:
    """盘中重算触发输入 (7 条件原料, §3.12)。

    Attributes:
        opening_nav: 当日开盘净值 (clean NAV, 不含未实现 MtM)
        current_nav: 当前净值 (clean NAV)
        var_baseline_pct: 盘前 VaR 占净值比 (None=首次启动无基线, 条件 1 跳过)
        current_drawdown_pct: 当前回撤率 (≤0, 如 -0.09=回撤 9%)
        limit_tide: 涨跌停潮 (37号 §3.5 上游检测)
        vol_regime_shift: 波动率 regime shift (30 分钟波动率 > 60 日均值 3σ, 上游检测)
        correlation_breakdown: 相关性崩塌 (BS-002 前兆, 上游检测)
        contagion: 跨市场传导 (BS-005 前兆, 上游检测)
        policy_event: 政策事件 (BS-006, 人工/新闻 API 输入)
    """

    opening_nav: float
    current_nav: float
    var_baseline_pct: float | None = None
    current_drawdown_pct: float = 0.0
    limit_tide: bool = False
    vol_regime_shift: bool = False
    correlation_breakdown: bool = False
    contagion: bool = False
    policy_event: bool = False


@dataclass(frozen=True)
class IntradayRecalcTrigger:
    """触发判定结果 (§3.12 去重口径)。

    Attributes:
        triggered: 是否放行重算 (命中且未受防抖抑制)
        first_trigger: 首个命中条件 (优先级最高者; 未命中="")
        reason: 全部命中条件 (优先级序逗号分隔; 未命中="")
        suppressed: 命中但被冷却期/日频上限抑制 (留痕审计)
        n_hits: 命中条件数
    """

    triggered: bool
    first_trigger: str
    reason: str
    suppressed: bool
    n_hits: int


@dataclass(frozen=True)
class IntradayVarResult:
    """盘中重算结果 (§3.12 D2 反馈链, 供 35号 §3.13 重新裁决)。

    Attributes:
        var_95: 重算 VaR 占净值比 (≥0)
        cvar_95: 重算 CVaR/ES 占净值比 (≥ var_95)
        breach_state: §3.15 breach 状态机更新后状态值 (未注入状态机=None)
        significant_change: 基线对比显著变化 (var_change_ratio > 20%)
        var_change_ratio: 相对盘前基线的 VaR 变化率 (无基线=None, §3.19 冷启动跳过)
    """

    var_95: float
    cvar_95: float
    breach_state: str | None
    significant_change: bool
    var_change_ratio: float | None


#: 触发条件优先级序 (§3.12: 政策 > 涨跌停潮 > 传导 > 相关性 > 波动率 > 回撤 > 亏损)
_TRIGGER_PRIORITY: Final = (
    "policy_event",
    "limit_tide",
    "contagion",
    "correlation_breakdown",
    "vol_regime_shift",
    "drawdown",
    "loss",
)


class IntradayVarRecalcController:
    """盘中 VaR/ES 重算控制器 (36号 §3.12)。

    用法::

        ctl = IntradayVarRecalcController(var_calculator, tail_monitor, breach_machine=machine)
        trig = ctl.intraday_var_recalc_trigger(inputs, now)
        if trig.triggered:
            result = ctl.intraday_var_recalc(returns, nav, premarket_baseline=baseline, trigger=trig, now=now)
            # → 35号 §3.13 用 result.var_95/cvar_95 重新 evaluate 覆盖盘前 response

    状态: 冷却/日频计数/suppressed/recalc_log 为日内内存态 (日切自动重置);
    recalc_log 由调用方于 §3.18 阶段 3 经 backtest_store 持久化。
    """

    def __init__(
        self,
        var_calculator: Any,
        tail_risk_monitor: Any,
        *,
        breach_machine: VarBreachStateMachine | None = None,
        config: IntradayRecalcConfig | None = None,
        clock: Any = None,
    ) -> None:
        self._var_calc = var_calculator
        self._tail_monitor = tail_risk_monitor
        self._machine = breach_machine
        self._config = config or IntradayRecalcConfig()
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._last_recalc_at: datetime | None = None
        self._recalc_count = 0
        self._recalc_date: date | None = None
        self._suppressed: list[dict[str, Any]] = []
        self._recalc_log: list[dict[str, Any]] = []

    @property
    def recalc_log(self) -> tuple[dict[str, Any], ...]:
        """当日盘中重算日志 (§3.18 阶段 3 持久化载荷)。"""
        return tuple(self._recalc_log)

    @property
    def suppressed_triggers(self) -> tuple[dict[str, Any], ...]:
        """被冷却期/日频上限抑制的触发留痕 (§3.12 审计)。"""
        return tuple(self._suppressed)

    @property
    def recalc_count_today(self) -> int:
        return self._recalc_count

    # ── 触发检测 (7 条件 + 去重 + 防抖) ──

    def intraday_var_recalc_trigger(
        self,
        inputs: IntradayTriggerInput,
        now: datetime | None = None,
    ) -> IntradayRecalcTrigger:
        """7 条触发检测 + 优先级去重 + 冷却期/日频上限防抖。"""
        now = now or self._clock()
        hits = self._detect_hits(inputs)
        if not hits:
            return IntradayRecalcTrigger(False, "", "", False, 0)
        first = hits[0]
        reason = ",".join(hits)
        self._roll_day(now)
        # 冷却期: 重算后 5 分钟内不再重算, 抑制留痕
        if (
            self._last_recalc_at is not None
            and 0 <= (now - self._last_recalc_at).total_seconds() < self._config.cooldown_seconds
        ):
            self._record_suppressed(now, reason, "cooldown")
            return IntradayRecalcTrigger(False, first, reason, True, len(hits))
        # 频率上限: 单日最多 6 次, 达上限仅记录告警
        if self._recalc_count >= self._config.max_recalc_per_day:
            self._record_suppressed(now, reason, "freq_cap")
            logger.warning(
                "intraday_recalc_freq_cap_hit date=%s count=%d reason=%s",
                now.date().isoformat(),
                self._recalc_count,
                reason,
            )
            return IntradayRecalcTrigger(False, first, reason, True, len(hits))
        return IntradayRecalcTrigger(True, first, reason, False, len(hits))

    def _detect_hits(self, inputs: IntradayTriggerInput) -> list[str]:
        """7 条件求值, 按优先级序返回命中键列表。"""
        fired: dict[str, bool] = {
            "policy_event": inputs.policy_event,
            "limit_tide": inputs.limit_tide,
            "contagion": inputs.contagion,
            "correlation_breakdown": inputs.correlation_breakdown,
            "vol_regime_shift": inputs.vol_regime_shift,
            "drawdown": inputs.current_drawdown_pct < -self._config.drawdown_threshold,
            "loss": self._loss_triggered(inputs),
        }
        return [key for key in _TRIGGER_PRIORITY if fired[key]]

    def _loss_triggered(self, inputs: IntradayTriggerInput) -> bool:
        """条件 1: 当前亏损 > 日内 VaR × loss_var_ratio (clean NAV 口径)。

        盘前基线缺失 (var_baseline_pct=None/≤0) → 跳过 (§3.19 冷启动无基线对比)。
        """
        if inputs.var_baseline_pct is None or inputs.var_baseline_pct <= 0:
            return False
        if not math.isfinite(inputs.opening_nav) or inputs.opening_nav <= 0:
            return False
        loss = (inputs.opening_nav - inputs.current_nav) / inputs.opening_nav
        return loss > self._config.loss_var_ratio * inputs.var_baseline_pct

    # ── 重算执行 + 结果反馈 (§3.12 D2) ──

    def intraday_var_recalc(
        self,
        current_returns: np.ndarray,
        current_nav: float,
        *,
        premarket_baseline: Mapping[str, float] | None = None,
        trigger: IntradayRecalcTrigger | None = None,
        now: datetime | None = None,
    ) -> IntradayVarResult:
        """盘中重算 VaR/ES 并反馈 (§3.12 D2)。

        ① var_calculator.calculate + tail_risk_monitor.assess 重算 (占净值比口径);
        ② 与盘前基线对比 var_change_ratio > 0.20 → significant_change
          (调用方按 §3.12 补记审计 + §3.16 FHS 触发 3 连续计数);
        ③ 更新 §3.15 breach 状态机 (注入时);
        ④ 登记冷却/日频计数 + intraday_recalc_log 内存累积
          (§3.18 阶段 3 由调用方经 backtest_store 持久化)。
        """
        if not math.isfinite(current_nav) or current_nav <= 0:
            raise InvalidIntradayRecalcConfigError(
                f"current_nav must be positive finite, got {current_nav}"
            )
        now = now or self._clock()
        var_result = self._var_calc.calculate(current_returns, portfolio_value=current_nav, now=now)
        tail = self._tail_monitor.assess(current_returns, portfolio_value=current_nav, now=now)
        var_pct = var_result.value_pct
        cvar_pct = max(tail.expected_shortfall / current_nav, var_pct)

        # 基线对比 (无基线 → 跳过, §3.19 冷启动)
        significant = False
        var_change_ratio: float | None = None
        baseline_var = (premarket_baseline or {}).get("var_95")
        if baseline_var is not None and baseline_var > 0:
            var_change_ratio = (var_pct - baseline_var) / baseline_var
            if var_change_ratio > self._config.significant_change_ratio:
                significant = True
                logger.warning(
                    "intraday_recalc_significant var_change_ratio=%.1f%% (baseline=%.4f → %.4f)",
                    var_change_ratio * 100,
                    baseline_var,
                    var_pct,
                )

        # breach 状态机更新 (注入时, §3.12 ③)
        breach_state: str | None = None
        if self._machine is not None:
            breach_state = self._machine.transition(var_pct, today=now.date()).value

        # 登记冷却/计数 + 日志 (§3.12 ④)
        self._roll_day(now)
        self._last_recalc_at = now
        self._recalc_count += 1
        self._recalc_log.append(
            {
                "timestamp": now.isoformat(),
                "var_95": var_pct,
                "cvar_95": cvar_pct,
                "var_change_ratio": var_change_ratio,
                "significant_change": significant,
                "breach_state": breach_state,
                "trigger_reason": trigger.reason if trigger is not None else "",
                "recalc_count": self._recalc_count,
            }
        )
        return IntradayVarResult(
            var_95=var_pct,
            cvar_95=cvar_pct,
            breach_state=breach_state,
            significant_change=significant,
            var_change_ratio=var_change_ratio,
        )

    # ── 内部: 日切/留痕 ──

    def _roll_day(self, now: datetime) -> None:
        """日切重置计数器 (冷却时间戳保留——跨日冷却自然过期)。"""
        day = now.date()
        if self._recalc_date != day:
            self._recalc_date = day
            self._recalc_count = 0

    def _record_suppressed(self, now: datetime, reason: str, cause: str) -> None:
        self._suppressed.append(
            {"timestamp": now.isoformat(), "reason": reason, "cause": cause}
        )
        logger.info(
            "intraday_recalc_suppressed cause=%s reason=%s", cause, reason
        )
