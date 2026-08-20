# [BLUEPRINT] MOD-RK-26 | docs/03_modules/_domain_risk/fhs_engine/blueprint.md
# [MODULE] zephyr.risk.core.fhs_engine
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.shared.foundation.errors; numpy; scipy
# [CONSUMERS] 无(设计契约消费者=RiskLayerOrchestrator RECALIBRATE 动作4,远期接线,见 CAND-AUTONOMYCORE-002)
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] VaR≥0且ES≥0;ES≥VaR(尾部均值≤实有分位点构造性成立);样本<min_history→抛InsufficientFHSHistoryError;非有限值占比超max_nonfinite_ratio→抛ExcessiveFHSNonFiniteDataError(Fail-Closed);GARCH不收敛→回退historical(fallback_to_historical=True时)并标记garch_converged=False;置信度∈(0,1);holding_period≥1;α+β<1平稳性守卫
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidFHSConfigError;InsufficientFHSHistoryError;ExcessiveFHSNonFiniteDataError;GarchConvergenceError
# [TESTS] tests/risk/test_fhs_engine.py
# [A_module] module_id=MOD-RK-26 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


FHS Engine — Filtered Historical Simulation 引擎 (MOD-RK-26, MVP)

GARCH(1,1) 残差重采样 VaR/ES。memo 36 §3.16 施工规约落地
(CAND-AUTONOMYCORE-002 远期候选转正, 2026-08-18 AI-FHS-001)。

定位 (并列方法论, 独立模块):
    - var_calculator (MOD-RK-05): 参数法 + 历史模拟 + conservative_max — Phase 1
    - fhs_engine (MOD-RK-26, 本模块): FHS — 第三方法论, 独立模块
    - 零代码耦合: 不 import/不修改 var_calculator; conservative_max 取大链不改动;
      第三法纳入取大链/RECALIBRATE 动作 4 的启用裁决属 RiskLayerOrchestrator 层
      (远期接线, memo 36 §3.10 动作 4 + §3.16 冷却期规约, 本 MVP 不实现)

算法 (Barone-Adesi FHS):
    1. 去均值: eps_t = r_t - mu_hat (两阶段估计, mu_hat = 样本均值)
    2. GARCH(1,1) QMLE: sigma_t^2 = omega + alpha*eps_{t-1}^2 + beta*sigma_{t-1}^2
       约束 omega>0, alpha>=0, beta>=0, alpha+beta<1 (平稳性守卫, 二次罚项)
    3. 标准化残差: z_t = eps_t / sigma_t
    4. 一日波动率预测: sigma_{T+1}^2 = omega + alpha*eps_T^2 + beta*sigma_T^2
    5. 残差重采样: z* ~ iid bootstrap(z), 逐日递归
       eps*_s = sigma*_s * z*_s, sigma*_{s+1}^2 = omega + alpha*eps*_s^2 + beta*sigma*_s^2
    6. 累积收益 r* = prod(1 + mu_hat + eps*_s) - 1 (多日复利, 非 sqrt(T) 缩放)
    7. VaR = -quantile(r*, 1-c, method='lower')*V, ES = -mean(r*[r* <= q])*V, 下限 0

GARCH 不收敛 → 回退 historical + 标记 garch_converged=False
(memo 36 §3.16 "GARCH 不收敛→回退 historical+标记 FHS 不可用");
fallback_to_historical=False 时抛 GarchConvergenceError 供编排层显式处理。

GARCH 参数估计方法裁定 (AI-FHS-001 #1):
    自研 QMLE (scipy.optimize.minimize L-BFGS-B), 不引入 arch 库——
    零新增依赖 (不动 pyproject/requirements, 避免并发批次依赖文件冲突);
    GARCH(1,1) 仅 3 参数 (mu 两阶段分离估计), 高斯 QMLE 为行业标准且对厚尾稳健;
    可解释性优先 (个人系统); CPU 即可。平稳性约束 alpha+beta<1 经二次罚项执行
    (GARCH 估计标准做法)。若后续发现数值问题可再评估 arch (CAND 留痕)。

    优化器勘正 (2026-08-18 Qwen 审查线 P0 修复): 原 SLSQP+不等式约束实现存在
    早停病灶——约束容差与 ftol 相互作用下 nit=5 即宣布收敛且停在起点
    (多种子估计精确钉在两个起点上, 似然比真参数点低 39.5), 未真正优化。
    改 L-BFGS-B (无约束优化, 避开约束容差早停) + 持续性二次罚项, 独立验证
    失败案例 nll 由 -7283.3 (起点) 改善至 -7325.3 (优于真参数点 -7322.7)。

属 A 类基础设施 (QMLE + bootstrap, 数学逻辑明确), 置信度/持有期/模拟数为 C 类可调参数。
设计真源: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/36_var_es_monitoring.md §3.16
SSoT: depgraph MOD-RK-26
Version: 0.1.0 (MVP)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 日收益序列 np.ndarray
#   fields: 1维日收益率数组, 非有限值(NaN/±Inf)过滤+计数nan_dropped(占比超阈值raise), 需>=min_history(30)有效样本
#   code: compute() returns 校验段
# - id: I2
#   name: 组合价值 标量
#   fields: portfolio_value 当前组合价值(NAV元), 必须为正
#   code: compute() portfolio_value 参数
# - id: I3
#   name: FHS配置 FHSConfig
#   fields: confidence_level置信水平 + holding_period_days持有期 + min_history + garch_min_history(60) + n_simulations + random_seed + fallback_to_historical + max_nonfinite_ratio
#   code: FHSConfig 配置段
# 层: 算法
# - id: A1
#   name_zh: ① GARCH(1,1) QMLE 拟合
#   name_en: _fit_garch_11
#   intro: 去均值后对准对数似然做L-BFGS-B优化估omega/alpha/beta
#   desc: eps=r-mu_hat; sigma_t^2=omega+alpha*eps_{t-1}^2+beta*sigma_{t-1}^2; 约束omega>0,alpha>=0,beta>=0,alpha+beta<1(二次罚项); L-BFGS-B双起点取较优; 不收敛返回None
#   inputs: I1 I3
#   outputs: GarchParams(omega/alpha/beta/mu/sigma_T/loglik) 或 None
#   invariant: alpha+beta<1(平稳性)
# - id: A2
#   name_zh: ② 标准化残差与波动率预测
#   name_en: _standardized_residuals
#   intro: 用拟合的条件波动率把残差标准化并预测下一日sigma
#   desc: z_t=eps_t/sigma_t; sigma_{T+1}^2=omega+alpha*eps_T^2+beta*sigma_T^2
#   inputs: A1 I1
#   outputs: z残差序列 + sigma_{T+1}
#   invariant: sigma_{T+1}>0且有限
# - id: A3
#   name_zh: ③ 残差重采样FHS模拟
#   name_en: _simulate_fhs
#   intro: 对z做有放回重采样逐日递归GARCH方程产出模拟收益分布
#   desc: z*~bootstrap(z); eps*_s=sigma*_s*z*_s; sigma*_{s+1}^2=omega+alpha*eps*_s^2+beta*sigma*_s^2; r*=prod(1+mu+eps*)-1; n_simulations条路径
#   inputs: A1 A2 I3
#   outputs: 模拟累积收益数组(B条路径)
#   invariant: 同日同种子结果可复现
# - id: A4
#   name_zh: ④ FHS VaR/ES分位取数
#   name_en: _var_es_from_simulation
#   intro: 从模拟分布取下侧分位数当VaR,尾部均值当ES
#   desc: q=quantile(r*,1-c,method='lower'); VaR=-q*V下限0; ES=-mean(r*[r*<=q])*V下限0
#   inputs: A3 I2 I3
#   outputs: fhs_var + fhs_es
#   invariant: VaR>=0; ES>=VaR(构造性)
# - id: A5
#   name_zh: ⑤ 历史模拟法对照与不收敛回退
#   name_en: _historical_benchmark
#   intro: 同窗口算历史模拟VaR/ES作对照,GARCH不收敛时回退它
#   desc: hs_var=-quantile(r,1-c)*V*sqrt(T); hs_es=-mean(r[r<=q_lower])*V*sqrt(T); 不收敛→method_used=HISTORICAL_FALLBACK+garch_converged=False+warning
#   inputs: I1 I2 I3
#   outputs: historical_var + historical_es (+回退时的最终值)
#   invariant: 回退时 var==historical_var 且 es==historical_es
# 层: 输出
# - id: O1
#   name_zh: FHS计算结果
#   name_en: FHSResult
#   intro: 含FHS VaR/ES/方法标记/GARCH参数/sigma预测/HS对照/样本数的frozen结果对象
#   invariant: VaR>=0且ES>=0;ES>=VaR
#   downstream: 无下游(设计契约消费者=RiskLayerOrchestrator RECALIBRATE 动作4,远期接线)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# I1 --> A5
# I2 --> A4
# I2 --> A5
# I3 --> A1
# I3 --> A3
# I3 --> A4
# I3 --> A5
# A1 --> A2
# A1 --> A3
# A2 --> A3
# A3 --> A4
# A4 --> O1
# A5 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import numpy as np
from scipy.optimize import minimize

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "FHSMethod",
    "FHSConfig",
    "GarchParams",
    "FHSResult",
    "FHSEngine",
    "InvalidFHSConfigError",
    "InsufficientFHSHistoryError",
    "ExcessiveFHSNonFiniteDataError",
    "GarchConvergenceError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class FHSMethod(str, Enum):
    """FHS 结果实际产出的方法。"""

    FHS = "fhs"  # GARCH(1,1) 残差重采样正常产出
    HISTORICAL_FALLBACK = "historical_fallback"  # GARCH 不收敛回退历史模拟


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidFHSConfigError(ZephyrBaseError):
    """FHS 配置非法 (如置信度不在 (0,1))。"""

    error_code = "ZA-RK-0026"


class InsufficientFHSHistoryError(ZephyrBaseError):
    """历史收益样本不足 (< min_history), 无法计算 FHS/对照 VaR。"""

    error_code = "ZA-RK-0027"


class ExcessiveFHSNonFiniteDataError(ZephyrBaseError):
    """收益序列非有限值 (NaN/±Inf) 占比超阈值——数据缺口期间拒绝出 VaR (Fail-Closed)。

    口径对齐 var_calculator 双轮审查 F2+F4 裁定 (2026-08-16): 静默过滤会让数据洞
    期间 (停牌/极端行情恰是高波动日) 风险被系统性低估且无任何信号。
    """

    error_code = "ZA-RK-0028"


class GarchConvergenceError(ZephyrBaseError):
    """GARCH(1,1) 拟合不收敛 (fallback_to_historical=False 时抛出)。"""

    error_code = "ZA-RK-0029"


# ──────────────────────────────────────────────────────────────────────────────
# 配置 (C 类可调参数)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class FHSConfig:
    """FHS 计算配置 (memo 36 §3.16 + §3.7 数据窗口)。

    Attributes:
        confidence_level: 置信水平, 默认 0.95, 必须 ∈ (0,1)
        holding_period_days: 持有期(天), 默认 1 (日 VaR)。多日走 GARCH 递归模拟
            (非 sqrt(T) 缩放)——FHS 的全部意义在于前向波动率聚集传播
        min_history: 最少样本数 (低于此连历史模拟对照也不可靠), 默认 30
        garch_min_history: GARCH 拟合最小样本数, 默认 60 (memo §3.7 窗口 +
            CAND tech_notes "60 日小样本 GARCH 拟合稳定性需最小样本守卫");
            min_history <= n < garch_min_history 时不尝试拟合直接回退 historical
        n_simulations: 残差重采样模拟路径数, 默认 10000
        random_seed: 随机种子 (None=每次随机, 种子值入 FHSResult.random_seed_used 留痕)
        max_nonfinite_ratio: 非有限值 (NaN/±Inf) 占比上限, 默认 0.05 (Fail-Closed)
        fallback_to_historical: GARCH 不收敛时回退历史模拟, 默认 True
            (memo §3.16 "GARCH 不收敛→回退 historical+标记 FHS 不可用");
            False 时抛 GarchConvergenceError 供编排层显式处理
        annualization_factor: 年化因子 (供 annualized_vol 诊断), 默认 252 (A股交易日)
    """

    confidence_level: float = 0.95
    holding_period_days: int = 1
    min_history: int = 30
    garch_min_history: int = 60
    n_simulations: int = 10_000
    random_seed: int | None = None
    max_nonfinite_ratio: float = 0.05
    fallback_to_historical: bool = True
    annualization_factor: int = 252

    def __post_init__(self) -> None:
        if not 0 < self.confidence_level < 1:
            raise InvalidFHSConfigError(f"confidence_level must be in (0,1), got {self.confidence_level}")
        if self.holding_period_days < 1:
            raise InvalidFHSConfigError(f"holding_period_days must be >=1, got {self.holding_period_days}")
        if self.min_history < 2:
            raise InvalidFHSConfigError(f"min_history must be >=2, got {self.min_history}")
        if self.garch_min_history < self.min_history:
            raise InvalidFHSConfigError(
                f"garch_min_history must be >= min_history, got {self.garch_min_history} < {self.min_history}"
            )
        if self.n_simulations < 100:
            raise InvalidFHSConfigError(f"n_simulations must be >=100, got {self.n_simulations}")
        if not 0.0 <= self.max_nonfinite_ratio < 1.0:
            raise InvalidFHSConfigError(f"max_nonfinite_ratio must be in [0,1), got {self.max_nonfinite_ratio}")
        if self.annualization_factor < 1:
            raise InvalidFHSConfigError(f"annualization_factor must be >=1, got {self.annualization_factor}")


# ──────────────────────────────────────────────────────────────────────────────
# GARCH 拟合结果
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class GarchParams:
    """GARCH(1,1) 拟合参数 (QMLE)。

    Attributes:
        omega: 常数项 (>0)
        alpha: ARCH 项系数 (>=0)
        beta: GARCH 项系数 (>=0)
        mu: 条件均值 (两阶段估计: 样本均值)
        persistence: 持续性 alpha+beta (<1, 平稳性)
        sigma_t_last: 样本末日条件波动率 sigma_T
        sigma_forecast: 下一日条件波动率预测 sigma_{T+1}
        log_likelihood: 高斯准对数似然
        sample_size: 拟合样本数
    """

    omega: float
    alpha: float
    beta: float
    mu: float
    persistence: float
    sigma_t_last: float
    sigma_forecast: float
    log_likelihood: float
    sample_size: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "omega": self.omega,
            "alpha": self.alpha,
            "beta": self.beta,
            "mu": self.mu,
            "persistence": self.persistence,
            "sigma_t_last": self.sigma_t_last,
            "sigma_forecast": self.sigma_forecast,
            "log_likelihood": self.log_likelihood,
            "sample_size": self.sample_size,
        }


# ──────────────────────────────────────────────────────────────────────────────
# 计算结果
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class FHSResult:
    """FHS VaR/ES 计算结果。

    所有金额字段单位与传入的 portfolio_value 一致 (如 NAV 元)。
    VaR/ES 以正数表示潜在损失额 (>=0)。

    Attributes:
        var: FHS VaR (回退时 = historical_var)
        es: FHS ES (回退时 = historical_es)
        var_pct / es_pct: 占 portfolio_value 比例 (>=0)
        method_used: 实际产出方法 (FHS / HISTORICAL_FALLBACK)
        garch_converged: GARCH(1,1) 是否收敛
        garch_params: 拟合参数 (未尝试或不收敛为 None)
        historical_var / historical_es: 历史模拟对照 (始终计算, 供合理性比对)
        fallback_reason: 回退原因 (未回退为 None)
        confidence_level / holding_period_days / portfolio_value: 输入回显
        sample_size: 有效样本数 (过滤非有限值后)
        nan_dropped: 过滤掉的非有限值样本数
        n_simulations / random_seed_used: 模拟参数留痕
        timestamp: 计算时间
    """

    var: float
    es: float
    var_pct: float
    es_pct: float
    method_used: FHSMethod
    garch_converged: bool
    garch_params: GarchParams | None
    historical_var: float
    historical_es: float
    fallback_reason: str | None
    confidence_level: float
    holding_period_days: int
    portfolio_value: float
    sample_size: int
    nan_dropped: int
    n_simulations: int
    random_seed_used: int
    timestamp: datetime

    def to_dict(self) -> dict[str, Any]:
        """转为字典 (供事件/日志/审计)。"""
        return {
            "var": self.var,
            "es": self.es,
            "var_pct": self.var_pct,
            "es_pct": self.es_pct,
            "method_used": self.method_used.value,
            "garch_converged": self.garch_converged,
            "garch_params": (self.garch_params.to_dict() if self.garch_params is not None else None),
            "historical_var": self.historical_var,
            "historical_es": self.historical_es,
            "fallback_reason": self.fallback_reason,
            "confidence_level": self.confidence_level,
            "holding_period_days": self.holding_period_days,
            "portfolio_value": self.portfolio_value,
            "sample_size": self.sample_size,
            "nan_dropped": self.nan_dropped,
            "n_simulations": self.n_simulations,
            "random_seed_used": self.random_seed_used,
        }


# ──────────────────────────────────────────────────────────────────────────────
# FHS 引擎
# ──────────────────────────────────────────────────────────────────────────────


class FHSEngine:
    """Filtered Historical Simulation 引擎 (GARCH(1,1) 残差重采样 VaR/ES)。

    用法:
        engine = FHSEngine()
        returns = np.array([...])  # 日收益序列
        result = engine.compute(returns, portfolio_value=1_000_000.0)
        print(result.var, result.es)           # 95% 日 VaR/ES (元)
        print(result.method_used)              # fhs / historical_fallback
        print(result.historical_var)           # 历史模拟对照

    Args:
        config: 计算配置, 默认 95% 日 VaR, 10000 路径, 不收敛回退 historical
    """

    # 平稳性约束上限 (alpha+beta 严格 <1, 留数值余量)
    _PERSISTENCE_CAP = 1.0 - 1e-6
    # 持续性二次罚项系数 (alpha+beta 超上限时惩罚, GARCH 估计标准做法)
    _PERSISTENCE_PENALTY = 1e6

    def __init__(self, config: FHSConfig | None = None) -> None:
        self._config = config or FHSConfig()

    @property
    def config(self) -> FHSConfig:
        return self._config

    # ── 公开 API ──

    def compute(
        self,
        returns: np.ndarray,
        portfolio_value: float = 1.0,
        now: datetime | None = None,
    ) -> FHSResult:
        """对单序列收益计算 FHS VaR/ES。

        Args:
            returns: 日收益序列 (1D array), 如组合净值日收益率
            portfolio_value: 当前组合价值 (如 NAV 元), 必须为正
            now: 时间戳

        Returns:
            FHSResult (含 HS 对照; GARCH 不收敛时 method_used=HISTORICAL_FALLBACK)

        Raises:
            InsufficientFHSHistoryError: 有效样本数 < min_history
            InvalidFHSConfigError: portfolio_value 非正
            ExcessiveFHSNonFiniteDataError: 非有限值占比 > max_nonfinite_ratio
            GarchConvergenceError: GARCH 不收敛且 fallback_to_historical=False
        """
        returns, nan_dropped = self._validate_returns(returns)
        if portfolio_value <= 0:
            raise InvalidFHSConfigError(f"portfolio_value must be positive, got {portfolio_value}")
        now = now or datetime.now(timezone.utc)

        # HS 对照始终计算 (诊断 + 回退兜底)
        hs_var, hs_es = self._historical_benchmark(returns, portfolio_value)

        seed = self._resolve_seed()
        garch: GarchParams | None = None
        z_residuals: np.ndarray | None = None
        fallback_reason: str | None = None

        if len(returns) < self._config.garch_min_history:
            fallback_reason = (
                f"sample {len(returns)} < garch_min_history "
                f"{self._config.garch_min_history} (小样本守卫, 不尝试 GARCH 拟合)"
            )
        else:
            garch, z_residuals, fit_fail = self._try_fit_garch(returns)
            if fit_fail is not None:
                fallback_reason = fit_fail

        if fallback_reason is not None:
            if not self._config.fallback_to_historical:
                raise GarchConvergenceError(f"GARCH(1,1) 拟合不可用: {fallback_reason} (fallback_to_historical=False)")
            logger.warning(
                "FHS 回退 historical: %s (n=%d, 标记 garch_converged=False)",
                fallback_reason,
                len(returns),
            )
            method = FHSMethod.HISTORICAL_FALLBACK
            var, es = hs_var, hs_es
            garch = None
        else:
            assert garch is not None and z_residuals is not None
            simulated = self._simulate_fhs(garch, z_residuals, seed)
            var, es = self._var_es_from_simulation(simulated, portfolio_value)
            method = FHSMethod.FHS

        var_pct = var / portfolio_value
        es_pct = es / portfolio_value

        logger.info(
            "FHS computed: method=%s var=%.2f (%.4f%%) es=%.2f (%.4f%%) "
            "hs_var=%.2f hs_es=%.2f converged=%s n=%d sims=%d seed=%d",
            method.value,
            var,
            var_pct * 100,
            es,
            es_pct * 100,
            hs_var,
            hs_es,
            fallback_reason is None,
            len(returns),
            self._config.n_simulations,
            seed,
        )

        return FHSResult(
            var=var,
            es=es,
            var_pct=var_pct,
            es_pct=es_pct,
            method_used=method,
            garch_converged=fallback_reason is None,
            garch_params=garch,
            historical_var=hs_var,
            historical_es=hs_es,
            fallback_reason=fallback_reason,
            confidence_level=self._config.confidence_level,
            holding_period_days=self._config.holding_period_days,
            portfolio_value=portfolio_value,
            sample_size=len(returns),
            nan_dropped=nan_dropped,
            n_simulations=self._config.n_simulations,
            random_seed_used=seed,
            timestamp=now,
        )

    # ── 内部: GARCH 拟合 ──

    def _try_fit_garch(self, returns: np.ndarray) -> tuple[GarchParams | None, np.ndarray | None, str | None]:
        """尝试 GARCH(1,1) QMLE 拟合, 返回 (params, z_residuals, fail_reason)。

        fail_reason 非 None 表示不收敛 (params/z 为 None)。
        """
        mu = float(np.mean(returns))
        eps = returns - mu
        var0 = float(np.var(eps, ddof=1))
        if not np.isfinite(var0) or var0 <= 0:
            return None, None, (f"收益方差非正/非有限 (var={var0}), GARCH 无可拟合波动结构")

        best: tuple[float, np.ndarray] | None = None  # (neg_loglik, params)
        starts = [
            np.array([var0 * 0.05, 0.05, 0.90]),
            np.array([var0 * 0.10, 0.10, 0.80]),
        ]
        for x0 in starts:
            nll, params = self._optimize_once(eps, var0, x0)
            if params is None:
                continue
            if best is None or nll < best[0]:
                best = (nll, params)

        if best is None:
            return None, None, "L-BFGS-B 双起点均未收敛 (迭代超限/方差非正)"

        omega, alpha, beta = (float(best[1][0]), float(best[1][1]), float(best[1][2]))
        sigma2 = self._filter_sigma2(eps, omega, alpha, beta, var0)
        if not np.all(np.isfinite(sigma2)) or np.any(sigma2 <= 0):
            return None, None, "滤波后方差序列非正/非有限 (数值不稳定)"

        sigma_t_last = float(np.sqrt(sigma2[-1]))
        sigma2_forecast = omega + alpha * float(eps[-1] ** 2) + beta * float(sigma2[-1])
        if not np.isfinite(sigma2_forecast) or sigma2_forecast <= 0:
            return None, None, "一日波动率预测非正/非有限"

        z = eps / np.sqrt(sigma2)
        loglik = -best[0]
        params = GarchParams(
            omega=omega,
            alpha=alpha,
            beta=beta,
            mu=mu,
            persistence=alpha + beta,
            sigma_t_last=sigma_t_last,
            sigma_forecast=float(np.sqrt(sigma2_forecast)),
            log_likelihood=loglik,
            sample_size=len(eps),
        )
        return params, z, None

    def _optimize_once(self, eps: np.ndarray, var0: float, x0: np.ndarray) -> tuple[float, np.ndarray | None]:
        """单起点 L-BFGS-B 优化, 返回 (neg_loglik, params|None)。

        平稳性约束 alpha+beta<1 经二次罚项执行 (非不等式约束)——
        2026-08-18 Qwen 审查线 P0 勘正: SLSQP+不等式约束存在早停病灶
        (约束容差与 ftol 相互作用下 nit=5 即宣布收敛且停在起点, 未真正优化)。
        """

        def neg_loglik(p: np.ndarray) -> float:
            omega, alpha, beta = p
            if omega <= 0 or alpha < 0 or beta < 0:
                return 1e12
            sigma2 = self._filter_sigma2(eps, omega, alpha, beta, var0)
            if not np.all(np.isfinite(sigma2)) or np.any(sigma2 <= 0):
                return 1e12
            v = float(0.5 * np.sum(np.log(2.0 * np.pi) + np.log(sigma2) + eps**2 / sigma2))
            excess = alpha + beta - self._PERSISTENCE_CAP
            if excess > 0:
                v += self._PERSISTENCE_PENALTY * excess * excess
            return v

        res = minimize(
            neg_loglik,
            x0,
            method="L-BFGS-B",
            bounds=[(1e-12, None), (1e-8, 1.0), (1e-8, 1.0)],
            options={"maxiter": 500, "ftol": 1e-12},
        )
        if not res.success or not np.all(np.isfinite(res.x)):
            return float("inf"), None
        omega, alpha, beta = (float(res.x[0]), float(res.x[1]), float(res.x[2]))
        if omega <= 0 or alpha < 0 or beta < 0 or alpha + beta >= 1.0:
            return float("inf"), None
        nll = float(res.fun)
        if not np.isfinite(nll) or nll >= 1e12:
            return float("inf"), None
        return nll, res.x

    @staticmethod
    def _filter_sigma2(eps: np.ndarray, omega: float, alpha: float, beta: float, var0: float) -> np.ndarray:
        """GARCH(1,1) 方差滤波: sigma_t^2 = omega + alpha*eps_{t-1}^2 + beta*sigma_{t-1}^2。"""
        n = len(eps)
        sigma2 = np.empty(n, dtype=float)
        sigma2[0] = var0
        for t in range(1, n):
            sigma2[t] = omega + alpha * eps[t - 1] ** 2 + beta * sigma2[t - 1]
        return sigma2

    # ── 内部: FHS 模拟 ──

    def _simulate_fhs(self, garch: GarchParams, z: np.ndarray, seed: int) -> np.ndarray:
        """残差重采样 + 逐日递归 GARCH 方程, 返回 (n_sims,) 累积收益。

        多日 horizon 走递归模拟 (Barone-Adesi 原版 FHS), 非 sqrt(T) 缩放——
        前向波动率聚集传播正是 FHS 相对 HS 的增量价值。
        """
        horizon = self._config.holding_period_days
        n_sims = self._config.n_simulations
        rng = np.random.default_rng(seed)

        z_star = z[rng.integers(0, len(z), size=(n_sims, horizon))]
        sigma2 = np.full(n_sims, garch.sigma_forecast**2, dtype=float)
        cum = np.ones(n_sims, dtype=float)
        for s in range(horizon):
            eps_s = np.sqrt(sigma2) * z_star[:, s]
            cum *= 1.0 + garch.mu + eps_s
            if s < horizon - 1:
                sigma2 = garch.omega + garch.alpha * eps_s**2 + garch.beta * sigma2
        return cum - 1.0

    def _var_es_from_simulation(self, simulated: np.ndarray, portfolio_value: float) -> tuple[float, float]:
        """从模拟累积收益分布取 VaR/ES (method='lower' 口径, 下限 0)。

        ES 口径对齐 memo 36 v1.11.0 F1 裁定: 分位数取 method='lower' (实有样本点,
        不线性插值), 尾部均值 <= 分位点 → ES >= VaR 构造性成立。
        """
        c = self._config.confidence_level
        q = float(np.quantile(simulated, 1.0 - c, method="lower"))
        tail = simulated[simulated <= q]
        var = -q * portfolio_value
        es = -float(np.mean(tail)) * portfolio_value if len(tail) > 0 else var
        return max(0.0, var), max(0.0, es)

    # ── 内部: HS 对照 ──

    def _historical_benchmark(self, returns: np.ndarray, portfolio_value: float) -> tuple[float, float]:
        """历史模拟 VaR/ES 对照 (口径对齐 var_calculator._historical + memo ES 'lower')。

        VaR = -quantile(r, 1-c)*V*sqrt(T); ES = -mean(r[r <= q_lower])*V*sqrt(T)。
        多日按 sqrt(T) 缩放 (历史模拟无波动率聚集结构, 与 var_calculator 同近似)。
        """
        c = self._config.confidence_level
        t_scale = float(np.sqrt(self._config.holding_period_days))
        q_var = float(np.quantile(returns, 1.0 - c))
        q_es = float(np.quantile(returns, 1.0 - c, method="lower"))
        tail = returns[returns <= q_es]
        hs_var = -q_var * portfolio_value * t_scale
        hs_es = -float(np.mean(tail)) * portfolio_value * t_scale if len(tail) > 0 else hs_var
        return max(0.0, hs_var), max(0.0, hs_es)

    # ── 内部: 校验与种子 ──

    def _resolve_seed(self) -> int:
        """解析随机种子 (None → 随机取一枚并入结果留痕, 保证可复现审计)。"""
        if self._config.random_seed is not None:
            return int(self._config.random_seed)
        return int(np.random.default_rng().integers(0, 2**31 - 1))

    def _validate_returns(self, returns: np.ndarray) -> tuple[np.ndarray, int]:
        """校验并规范化收益序列, 返回 (有效序列, 过滤掉的非有限值样本数)。

        口径对齐 var_calculator 双轮审查 F2+F4 裁定: NaN/±Inf 一并过滤,
        占比 > max_nonfinite_ratio 抛 ExcessiveFHSNonFiniteDataError (Fail-Closed)。
        """
        arr = np.asarray(returns, dtype=float)
        if arr.ndim != 1:
            raise InvalidFHSConfigError(f"returns must be 1D, got shape {arr.shape}")
        finite_mask = np.isfinite(arr)
        nan_dropped = int(len(arr) - int(np.count_nonzero(finite_mask)))
        if nan_dropped > 0:
            ratio = nan_dropped / len(arr) if len(arr) > 0 else 1.0
            if ratio > self._config.max_nonfinite_ratio:
                raise ExcessiveFHSNonFiniteDataError(
                    f"non-finite (NaN/±Inf) ratio {ratio:.2%} > "
                    f"max_nonfinite_ratio {self._config.max_nonfinite_ratio:.2%} "
                    f"({nan_dropped}/{len(arr)}) — 数据缺口过大, 拒绝出 VaR (Fail-Closed)"
                )
            logger.warning(
                "FHS 输入含 %d/%d 非有限值 (NaN/±Inf, %.2f%%), 已过滤并计数 "
                "(数据缺口期间风险可能低估, 超 %.2f%% 将 raise)",
                nan_dropped,
                len(arr),
                ratio * 100,
                self._config.max_nonfinite_ratio * 100,
            )
            arr = arr[finite_mask]
        if len(arr) < self._config.min_history:
            raise InsufficientFHSHistoryError(f"need >= {self._config.min_history} valid returns, got {len(arr)}")
        return arr, nan_dropped
