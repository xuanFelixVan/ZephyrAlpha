# [BLUEPRINT] MOD-SIM-003 | docs/03_modules/_domain_simulation/risk_simulator/blueprint.md
# [MODULE] zephyr.simulation.risk_simulator
# [DOMAIN] D_SIMULATION
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] zephyr.simulation.result_analyzer
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 所有dataclass frozen不可变; VaR/CVaR正数=损失; max_drawdown<=0; MC固定seed可复现; 纯math无第三方依赖
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SimulationError(ZA-SIM-0003)
# [TESTS] tests/simulation/test_risk_simulator.py
# [A_module] module_id=MOD-SIM-003 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D_SIMULATION — Risk Simulator (风控仿真器)

VaR(风险价值)模拟 + 回撤模拟 + 熔断模拟。基于收益率序列计算多方法 VaR/CVaR、
最大回撤及恢复期、熔断触发判定, 供风控评估和压力测试使用。

属 A 类基础设施(确定性计算), 纯基础层不涉及策略。

设计真源: depgraph MOD-SIM-003
蓝图: docs/03_modules/_domain_simulation/risk_simulator/blueprint.md

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 收益率序列 returns
#   fields: 每期收益率 list[float]（空序列/样本<2拒绝）
#   code: calculate_var(returns) L191
# - id: I2
#   name: 风控仿真配置 RiskConfig
#   fields: VaR置信水平(95%/99%) + 蒙特卡洛路径数10000 + 固定随机种子42 + 年化频率252
#   code: RiskConfig L60
# - id: I3
#   name: 仿真参数
#   fields: VaR计算方法method(historical/parametric/monte_carlo) + 熔断触发阈值trigger_level(默认-10%)
#   code: run_full_simulation(method, trigger_level) L408
# 层: 算法
# - id: A1
#   name_zh: ① 历史法VaR
#   name_en: _historical_var
#   intro: 用经验分位数直接数尾部损失
#   desc: 排序收益率 → var=-sorted[floor((1-conf)·n)] → CVaR=尾部均值(正数=损失)
#   inputs: I1 I2
#   outputs: VaRResult(VaR/CVaR)
#   invariant: VaR/CVaR正数=损失
# - id: A2
#   name_zh: ② 参数法VaR
#   name_en: _parametric_var
#   intro: 假设收益率正态分布，用均值方差推VaR
#   desc: var=-μ+z·σ（z=Φ⁻¹(conf)，如95%→1.645）；CVaR=-μ+σ·φ(z)/(1-α)；σ=0时退化var=max(0,-μ)
#   inputs: I1 I2
#   outputs: VaRResult(VaR/CVaR)
# - id: A3
#   name_zh: ③ 蒙特卡洛VaR
#   name_en: _monte_carlo_var
#   intro: 拟合正态N(μ,σ)后用固定种子模拟万条路径再算分位数
#   desc: rng=Random(seed=42) → gauss(μ,σ)×10000路径 → 走历史法分位数 → 改标MONTE_CARLO方法
#   inputs: I1 I2
#   outputs: VaRResult(VaR/CVaR)
#   invariant: 固定seed可复现
# - id: A4
#   name_zh: ④ 回撤模拟
#   name_en: simulate_drawdown
#   intro: 复利财富指数跟踪峰谷，算最大回撤/持续期/恢复期
#   desc: wealth逐期×(1+r) → 跟踪峰值 → dd=(wealth-peak)/peak取最小 → 持续期=峰到谷，恢复期=谷后重回峰值期数，当前回撤相对全局峰
#   inputs: I1
#   outputs: DrawdownResult
#   invariant: max_drawdown≤0
# - id: A5
#   name_zh: ⑤ 熔断模拟
#   name_en: simulate_circuit_breaker
#   intro: 逐点回撤越过阈值即记一次熔断触发（连续段计1次）
#   desc: 重算逐点回撤序列 → dd≤trigger_level的连续段数=hit_count → triggered=(max_drawdown≤阈值)
#   inputs: I1 I3 A4
#   outputs: CircuitBreakerResult
# - id: A6
#   name_zh: ⑥ 全量风控仿真编排
#   name_en: run_full_simulation
#   intro: 一次跑齐VaR+回撤+熔断并打包结果
#   desc: calculate_var(按method三选一) + simulate_drawdown + simulate_circuit_breaker → RiskSimulationResult
#   inputs: I1 I3 A1 A2 A3 A4 A5
#   outputs: RiskSimulationResult
# - id: A7
#   name_zh: ⑦ 审计摘要生成
#   name_en: audit_summary
#   intro: 把风控仿真结果格式化成人类可读审计文本
#   desc: 样本数/方法行 + 各置信水平VaR/CVaR + 回撤4指标 + 熔断状态/阈值/次数
#   inputs: A6
#   outputs: 审计摘要字符串
# 层: 输出
# - id: O1
#   name_zh: 全量风控仿真结果 RiskSimulationResult
#   name_en: RiskSimulationResult
#   intro: 打包各置信水平VaR/CVaR+回撤+熔断结果的不可变对象
#   invariant: frozen不可变；VaR/CVaR正数=损失；max_drawdown≤0
#   downstream: zephyr.simulation.result_analyzer（[CONSUMERS]）
# - id: O2
#   name_zh: 风控审计摘要文本
#   name_en: audit summary str
#   intro: 人类可读的风控仿真审计报告
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I1 --> A2
# I2 --> A2
# I1 --> A3
# I2 --> A3
# I1 --> A4
# I1 --> A5
# I3 --> A5
# A4 --> A5
# I1 --> A6
# I3 --> A6
# A1 --> A6
# A2 --> A6
# A3 --> A6
# A4 --> A6
# A5 --> A6
# A6 --> O1
# A6 --> A7
# A7 --> O2
"""

from __future__ import annotations

import logging
import math
import random
import statistics
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable

from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)

_SQRT_2PI = math.sqrt(2.0 * math.pi)


class SimulationError(ZephyrBaseError):
    """仿真计算异常——输入非法。"""

    error_code = "ZA-SIM-0003"


class RiskMethod(str, Enum):
    """VaR 计算方法。"""

    HISTORICAL = "historical"
    PARAMETRIC = "parametric"
    MONTE_CARLO = "monte_carlo"


@dataclass(frozen=True)
class RiskConfig:
    """风控仿真配置——不可变。

    Attributes:
        confidence_levels: VaR 置信水平(默认 95%/99%)。
        mc_paths: 蒙特卡洛模拟路径数。
        mc_seed: 蒙特卡洛随机种子(可复现)。
        periods_per_year: 年化频率(A股日度=252)。
    """

    confidence_levels: tuple[float, ...] = (0.95, 0.99)
    mc_paths: int = 10000
    mc_seed: int = 42
    periods_per_year: int = 252


@dataclass(frozen=True)
class VaRResult:
    """单置信水平 VaR 结果——不可变。

    Attributes:
        confidence: 置信水平。
        var: Value at Risk(正数=损失)。
        cvar: 条件 VaR / 预期短缺(正数=损失)。
        method: 计算方法。
    """

    confidence: float
    var: float
    cvar: float
    method: RiskMethod


@dataclass(frozen=True)
class DrawdownResult:
    """回撤模拟结果——不可变。

    Attributes:
        max_drawdown: 最大回撤(<=0)。
        max_dd_duration: 最大回撤持续期数(峰到谷)。
        recovery_duration: 恢复期数(谷到回升至峰, None=未恢复)。
        current_drawdown: 当前回撤(末尾)。
    """

    max_drawdown: float
    max_dd_duration: int
    recovery_duration: int | None
    current_drawdown: float


@dataclass(frozen=True)
class CircuitBreakerResult:
    """熔断模拟结果——不可变。

    Attributes:
        triggered: 是否触发熔断。
        trigger_level: 熔断触发回撤阈值。
        hit_count: 触发次数(连续段数)。
        worst_drawdown: 最差回撤。
    """

    triggered: bool
    trigger_level: float
    hit_count: int
    worst_drawdown: float


@dataclass(frozen=True)
class RiskSimulationResult:
    """全量风控仿真结果——不可变。

    Attributes:
        var_results: 各置信水平 VaR 结果。
        drawdown: 回撤结果。
        circuit_breaker: 熔断结果。
        method: VaR 计算方法。
        num_obs: 样本数。
    """

    var_results: list[VaRResult] = field(default_factory=list)
    drawdown: DrawdownResult | None = None
    circuit_breaker: CircuitBreakerResult | None = None
    method: RiskMethod = RiskMethod.HISTORICAL
    num_obs: int = 0


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def _std(values: list[float], ddof: int = 1) -> float:
    n = len(values)
    if n <= ddof:
        return 0.0
    m = _mean(values)
    return math.sqrt(sum((v - m) ** 2 for v in values) / (n - ddof))


def _normal_pdf(z: float) -> float:
    """标准正态概率密度 φ(z)。"""
    return math.exp(-0.5 * z * z) / _SQRT_2PI


def _normal_inv_cdf(p: float) -> float:
    """标准正态分位数函数 Φ^(-1)(p) (用 statistics.NormalDist)。"""
    return statistics.NormalDist().inv_cdf(p)


class RiskSimulator:
    """风控仿真器——VaR + 回撤 + 熔断模拟。

    Usage:
        sim = RiskSimulator()
        result = sim.run_full_simulation(returns, method=RiskMethod.HISTORICAL)
        for vr in result.var_results:
            print(f"VaR@{vr.confidence}: {vr.var:.4f} CVaR: {vr.cvar:.4f}")
        print(f"最大回撤: {result.drawdown.max_drawdown:.4f}")
        print(sim.audit_summary(result))
    """

    def __init__(self, config: RiskConfig | None = None) -> None:
        self._config = config if config is not None else RiskConfig()

    @property
    def config(self) -> RiskConfig:
        """配置(只读)。"""
        return self._config

    # ------------------------------------------------------------------
    # VaR 计算
    # ------------------------------------------------------------------
    def calculate_var(
        self,
        returns: list[float],
        confidence_levels: list[float] | None = None,
        method: RiskMethod = RiskMethod.HISTORICAL,
    ) -> list[VaRResult]:
        """计算多置信水平 VaR/CVaR。

        Args:
            returns: 收益率序列。
            confidence_levels: 置信水平, None=用 config 默认。
            method: 计算方法。

        Returns:
            list[VaRResult]

        Raises:
            SimulationError: 空序列 / 样本不足。
        """
        if not returns:
            raise SimulationError("returns 不能为空")
        if len(returns) < 2:
            raise SimulationError(
                f"样本数不足: {len(returns)} < 2(无法计算 VaR)",
                details={"num_obs": len(returns)},
            )
        levels = confidence_levels if confidence_levels is not None else list(self._config.confidence_levels)
        results: list[VaRResult] = []
        for conf in levels:
            if method == RiskMethod.HISTORICAL:
                vr = self._historical_var(returns, conf)
            elif method == RiskMethod.PARAMETRIC:
                vr = self._parametric_var(returns, conf)
            else:
                vr = self._monte_carlo_var(returns, conf)
            results.append(vr)
        return results

    def _historical_var(self, returns: list[float], confidence: float) -> VaRResult:
        """历史 VaR: 经验分位数。"""
        n = len(returns)
        sorted_r = sorted(returns)
        # (1-confidence) 分位数; +1e-9 修正浮点误差(如 (1-0.80)*5=0.9999...→floor 得 0)
        idx = int(math.floor((1.0 - confidence) * n + 1e-9))
        idx = min(max(idx, 0), n - 1)
        var = -sorted_r[idx]
        # CVaR: 尾部均值
        tail = sorted_r[: idx + 1]
        cvar = -(_mean(tail)) if tail else var
        return VaRResult(
            confidence=confidence,
            var=var,
            cvar=cvar,
            method=RiskMethod.HISTORICAL,
        )

    def _parametric_var(self, returns: list[float], confidence: float) -> VaRResult:
        """参数 VaR: 正态假设。"""
        mu = _mean(returns)
        sigma = _std(returns, ddof=1)
        if sigma == 0:
            return VaRResult(
                confidence=confidence,
                var=max(0.0, -mu),
                cvar=max(0.0, -mu),
                method=RiskMethod.PARAMETRIC,
            )
        z = _normal_inv_cdf(confidence)  # 正数(如 95%→1.645)
        var = -mu + z * sigma
        # CVaR (Expected Shortfall, 正态): -μ + σ·φ(z)/(1-α)
        cvar = -mu + sigma * _normal_pdf(z) / (1.0 - confidence)
        return VaRResult(
            confidence=confidence,
            var=var,
            cvar=cvar,
            method=RiskMethod.PARAMETRIC,
        )

    def _monte_carlo_var(self, returns: list[float], confidence: float) -> VaRResult:
        """蒙特卡洛 VaR: 拟合正态后模拟。"""
        mu = _mean(returns)
        sigma = _std(returns, ddof=1)
        if sigma == 0:
            return VaRResult(
                confidence=confidence,
                var=max(0.0, -mu),
                cvar=max(0.0, -mu),
                method=RiskMethod.MONTE_CARLO,
            )
        rng = random.Random(self._config.mc_seed)
        simulated = [rng.gauss(mu, sigma) for _ in range(self._config.mc_paths)]
        hist_result = self._historical_var(simulated, confidence)
        return VaRResult(
            confidence=hist_result.confidence,
            var=hist_result.var,
            cvar=hist_result.cvar,
            method=RiskMethod.MONTE_CARLO,
        )

    # ------------------------------------------------------------------
    # 回撤模拟
    # ------------------------------------------------------------------
    def simulate_drawdown(self, returns: list[float]) -> DrawdownResult:
        """模拟最大回撤及恢复期。

        Args:
            returns: 收益率序列。

        Returns:
            DrawdownResult

        Raises:
            SimulationError: 空序列。
        """
        if not returns:
            raise SimulationError("returns 不能为空")
        n = len(returns)
        # 财富指数: 初始资本 1.0, 逐期复利
        wealth = [0.0] * n
        w = 1.0
        for i, r in enumerate(returns):
            w *= 1.0 + r
            wealth[i] = w
        peak = wealth[0]
        peak_pos = 0
        max_dd = 0.0
        max_dd_peak_pos = 0
        max_dd_trough_pos = 0
        for i in range(n):
            if wealth[i] > peak:
                peak = wealth[i]
                peak_pos = i
            dd = (wealth[i] - peak) / peak if peak > 0 else 0.0
            if dd < max_dd:
                max_dd = dd
                max_dd_peak_pos = peak_pos
                max_dd_trough_pos = i
        # 持续期 = 峰到谷
        duration = max_dd_trough_pos - max_dd_peak_pos
        # 恢复期: 谷之后 wealth 是否回到峰
        recovery: int | None = None
        peak_value = wealth[max_dd_peak_pos]
        for i in range(max_dd_trough_pos + 1, n):
            if wealth[i] >= peak_value:
                recovery = i - max_dd_trough_pos
                break
        # 当前回撤(相对全局峰)
        global_peak = max(wealth)
        current_dd = (wealth[-1] - global_peak) / global_peak if global_peak > 0 else 0.0
        return DrawdownResult(
            max_drawdown=max_dd,
            max_dd_duration=duration,
            recovery_duration=recovery,
            current_drawdown=current_dd,
        )

    # ------------------------------------------------------------------
    # 熔断模拟
    # ------------------------------------------------------------------
    def simulate_circuit_breaker(
        self,
        returns: list[float],
        trigger_level: float = -0.10,
    ) -> CircuitBreakerResult:
        """模拟熔断触发。

        Args:
            returns: 收益率序列。
            trigger_level: 熔断触发回撤阈值(负数, 如 -0.10=-10%)。

        Returns:
            CircuitBreakerResult

        Raises:
            SimulationError: 空序列。
        """
        if not returns:
            raise SimulationError("returns 不能为空")
        dd_result = self.simulate_drawdown(returns)
        # 重新计算逐点回撤以计 hit_count
        n = len(returns)
        wealth = [0.0] * n
        w = 1.0
        for i, r in enumerate(returns):
            w *= 1.0 + r
            wealth[i] = w
        peak = wealth[0]
        drawdowns = [0.0] * n
        for i in range(n):
            if wealth[i] > peak:
                peak = wealth[i]
            drawdowns[i] = (wealth[i] - peak) / peak if peak > 0 else 0.0
        # hit_count: 连续触发段数
        hit_count = 0
        in_hit = False
        for dd in drawdowns:
            if dd <= trigger_level:
                if not in_hit:
                    hit_count += 1
                    in_hit = True
            else:
                in_hit = False
        triggered = dd_result.max_drawdown <= trigger_level
        return CircuitBreakerResult(
            triggered=triggered,
            trigger_level=trigger_level,
            hit_count=hit_count,
            worst_drawdown=dd_result.max_drawdown,
        )

    # ------------------------------------------------------------------
    # 全量仿真
    # ------------------------------------------------------------------
    def run_full_simulation(
        self,
        returns: list[float],
        method: RiskMethod = RiskMethod.HISTORICAL,
        trigger_level: float = -0.10,
    ) -> RiskSimulationResult:
        """运行全量风控仿真(VaR + 回撤 + 熔断)。

        Args:
            returns: 收益率序列。
            method: VaR 计算方法。
            trigger_level: 熔断触发阈值。

        Returns:
            RiskSimulationResult
        """
        var_results = self.calculate_var(returns, method=method)
        drawdown = self.simulate_drawdown(returns)
        breaker = self.simulate_circuit_breaker(returns, trigger_level)
        result = RiskSimulationResult(
            var_results=var_results,
            drawdown=drawdown,
            circuit_breaker=breaker,
            method=method,
            num_obs=len(returns),
        )
        _logger.debug(
            "风控仿真: method=%s VaR95=%s maxDD=%.4f breaker=%s",
            method.value,
            f"{var_results[0].var:.4f}" if var_results else "N/A",
            drawdown.max_drawdown,
            breaker.triggered,
        )
        return result

    # ------------------------------------------------------------------
    # 审计摘要
    # ------------------------------------------------------------------
    def audit_summary(self, result: RiskSimulationResult) -> str:
        """生成审计摘要文本。"""
        lines: list[str] = []
        lines.append("=== 风控仿真审计 ===")
        lines.append(f"样本数: {result.num_obs} | VaR方法: {result.method.value}")
        if result.var_results:
            lines.append("")
            lines.append("VaR / CVaR:")
            for vr in result.var_results:
                lines.append(f"  @{vr.confidence:.0%}: VaR={vr.var:.4f} CVaR={vr.cvar:.4f}")
        if result.drawdown:
            dd = result.drawdown
            rec = f"{dd.recovery_duration}" if dd.recovery_duration is not None else "未恢复"
            lines.append("")
            lines.append("回撤:")
            lines.append(
                f"  最大回撤: {dd.max_drawdown:.4f} | 持续: {dd.max_dd_duration}期 | "
                f"恢复: {rec} | 当前: {dd.current_drawdown:.4f}"
            )
        if result.circuit_breaker:
            cb = result.circuit_breaker
            verdict = "触发" if cb.triggered else "未触发"
            lines.append("")
            lines.append("熔断:")
            lines.append(
                f"  状态: {verdict} | 阈值: {cb.trigger_level:.2%} | "
                f"触发次数: {cb.hit_count} | 最差回撤: {cb.worst_drawdown:.4f}"
            )
        return "\n".join(lines)


__all__ = [
    "CircuitBreakerResult",
    "DrawdownResult",
    "RiskConfig",
    "RiskMethod",
    "RiskSimulationResult",
    "RiskSimulator",
    "SimulationError",
    "VaRResult",
]
