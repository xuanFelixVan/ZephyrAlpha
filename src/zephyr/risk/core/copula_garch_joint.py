# [BLUEPRINT] MOD-RK-33 | docs/03_modules/_domain_risk/copula_garch_joint/blueprint.md
# [MODULE] zephyr.risk.core.copula_garch_joint
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.position.core.covariance_estimator(MOD-POS-011); zephyr.shared.foundation.errors; numpy; scipy
# [CONSUMERS] D_RISK(组合风险仪表盘/限额下发); CAND-RSK-037 系统性风险分级预警(联合 VaR/CVaR 输入候选)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 标的数≤max_assets(默认50,★硬约束); 边缘GARCH(1,1)方差定向过滤+DCC(a+b<1)盘后批算; Gaussian Copula经验PIT(不假设边缘正态); 尾部依赖=下尾共超限经验概率∈[0,1]对角=1; MC固定种子可复现; ES≥VaR同置信度; 非法输入Fail-Closed拒绝
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CopulaGarchJointError
# [TESTS] tests/risk/core/test_copula_garch_joint.py
# [A_module] module_id=MOD-RK-33 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Copula-GARCH Joint Model — Copula-GARCH 联合分布建模 (MOD-RK-33, CAND-RSK-036)

单标的 VaR 与账面分散化看不到"多只持仓同时暴跌"的联合尾部风险。本模块按
F=C(F₁..F_N) 分解：边缘（GARCH(1,1) 方差定向过滤，或调用方注入条件密度预测
μ/σ）+ Gaussian Copula（DCC 动态相关，盘后批算），产出：

  1. 联合尾部依赖矩阵——经验下尾共超限 P(u_i<q, u_j<q)/q（q 默认 0.05）；
  2. DCC 一步相关预测 R_{T+1}（Q 递归 + 标准化，奇异性抖动兜底）；
  3. 联合 VaR/ES——Cholesky(R) 相关正态 → 经验边缘逆 CDF → 组合损失分布
     （固定种子 Monte Carlo，可复现）。

工程约束（候选登记真源）：持仓 ≤50 只（RTX3090 上 50 只 DCC≈5 分钟盘后批算）；
纯计算、无 IO、数据由调用方注入（禁自造数据管道）；边缘密度预测由
MOD-SIG-043 conditional_density_predictor 产出、调用方映射为 MarginalForecast 注入
（本模块不反向依赖信号域，三维解耦）。

依据: blueprint.md（MOD-RK-33）§3 核心规则；Engle (2002) DCC；Sklar (1959) Copula
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 多标的收益率 {symbol: 序列}
#   fields: N∈[2,max_assets] 个标的等长 T≥min_history 日收益率, 全有限值, 无零方差
#   code: fit_portfolio_risk() returns 参数
# - id: I2
#   name: 组合权重 {symbol: w}
#   fields: 与收益率同标的集, 有限值, Σ|w|>0(内部归一)
#   code: fit_portfolio_risk() weights 参数
# - id: I3
#   name: 边缘一步预测(可选) {symbol: MarginalForecast}
#   fields: mu/sigma(>0), 缺省用 GARCH 一步预测(均值=样本均值, σ=√σ²_{T+1})
#   code: MarginalForecast
# - id: I4
#   name: 配置 CopulaGarchConfig
#   fields: max_assets=50/min_history=60/dcc_a=0.04/dcc_b=0.94/garch_α=0.06/garch_β=0.92/tail_q=0.05/confidence=(0.95,0.99)/n_sim=20000/seed
#   code: CopulaGarchConfig
# 层: 算法
# - id: A1
#   name_zh: ① GARCH(1,1) 边缘过滤
#   name_en: _garch_filter
#   intro: 方差定向 ω=(1-α-β)σ̄² 递推 σ²_t, 产标准化残差 z
# - id: A2
#   name_zh: ② DCC 动态相关
#   name_en: _dcc_forecast
#   intro: Q̄=MOD-POS-011收缩协方差标准化, Q_t=(1-a-b)Q̄+a·zz′+b·Q_{t-1}, 一步预测标准化为 R
# - id: A3
#   name_zh: ③ 经验PIT+下尾依赖
#   name_en: _tail_dependence
#   intro: u=rank/(T+1), λ_ij=P(u_i<q,u_j<q)/q, 对角=1
# - id: A4
#   name_zh: ④ Gaussian-Copula MC 联合VaR/ES
#   name_en: _simulate_joint_loss
#   intro: Cholesky(R)(奇异加抖动)相关正态→Φ→经验逆CDF×σ+μ→组合损失→VaR/ES
# 层: 输出
# - id: O1
#   name: JointRiskReport
#   fields: symbols/tail_dependence_matrix/dcc_correlation/joint_var/joint_es/n_assets/n_observations/simulations
# 边:
# I1 --> A1
# I2 --> A4
# I3 --> A4
# I4 --> A1
# I4 --> A2
# I4 --> A3
# I4 --> A4
# A1 --> A2
# A1 --> A3
# A1 --> A4
# A2 --> A4
# A3 --> O1
# A4 --> O1
# [/ALGO_FLOW]
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Final

import numpy as np
from scipy.stats import norm

from zephyr.position.core.covariance_estimator import estimate_covariance
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "CopulaGarchConfig",
    "CopulaGarchJointError",
    "CopulaGarchJointModel",
    "JointRiskReport",
    "MarginalForecast",
]

_CHOL_JITTER: Final = 1e-10
_CHOL_MAX_ATTEMPTS: Final = 5


class CopulaGarchJointError(ZephyrBaseError):
    """Copula-GARCH 联合分布建模输入/配置非法（Fail-Closed）。"""


@dataclass(frozen=True)
class MarginalForecast:
    """单标的下一步边缘预测（调用方自 conditional_density_predictor 映射注入）。"""

    mu: float
    sigma: float

    def __post_init__(self) -> None:
        if not (math.isfinite(self.mu) and math.isfinite(self.sigma)):
            raise CopulaGarchJointError(f"边缘预测必须有限: mu={self.mu} sigma={self.sigma}")
        if self.sigma <= 0:
            raise CopulaGarchJointError(f"边缘预测 sigma 必须为正: {self.sigma}")


@dataclass(frozen=True)
class CopulaGarchConfig:
    """Copula-GARCH 联合模型配置（C 类可调参数集中地）。"""

    max_assets: int = 50  # ★硬约束：>50 需双 RTX4090，本模型直接拒绝
    min_history: int = 60
    dcc_a: float = 0.04
    dcc_b: float = 0.94
    garch_alpha: float = 0.06
    garch_beta: float = 0.92
    tail_quantile: float = 0.05
    confidence_levels: tuple[float, ...] = (0.95, 0.99)
    n_simulations: int = 20000
    random_seed: int = 20260825

    def __post_init__(self) -> None:
        if self.max_assets < 2:
            raise CopulaGarchJointError(f"max_assets 必须 ≥2: {self.max_assets}")
        if self.min_history < 10:
            raise CopulaGarchJointError(f"min_history 必须 ≥10: {self.min_history}")
        if not (0.0 < self.dcc_a < 1.0 and 0.0 < self.dcc_b < 1.0) or self.dcc_a + self.dcc_b >= 1.0:
            raise CopulaGarchJointError(
                f"DCC 参数须满足 a>0,b>0,a+b<1: a={self.dcc_a} b={self.dcc_b}"
            )
        if not (0.0 < self.garch_alpha < 1.0 and 0.0 < self.garch_beta < 1.0) or self.garch_alpha + self.garch_beta >= 1.0:
            raise CopulaGarchJointError(
                f"GARCH 参数须满足 α>0,β>0,α+β<1: α={self.garch_alpha} β={self.garch_beta}"
            )
        if not (0.0 < self.tail_quantile < 0.5):
            raise CopulaGarchJointError(f"tail_quantile 须 ∈(0,0.5): {self.tail_quantile}")
        if not self.confidence_levels or any(not (0.0 < c < 1.0) for c in self.confidence_levels):
            raise CopulaGarchJointError(f"confidence_levels 须全 ∈(0,1): {self.confidence_levels}")
        if self.n_simulations < 100:
            raise CopulaGarchJointError(f"n_simulations 必须 ≥100: {self.n_simulations}")


@dataclass(frozen=True)
class JointRiskReport:
    """联合风险报告（frozen 不可变）。"""

    symbols: tuple[str, ...]
    tail_dependence_matrix: tuple[tuple[float, ...], ...]
    dcc_correlation: tuple[tuple[float, ...], ...]
    joint_var: dict[float, float]
    joint_es: dict[float, float]
    n_assets: int
    n_observations: int
    simulations: int


def _require_finite_series(symbol: str, series: Sequence[float]) -> np.ndarray:
    arr = np.asarray([float(v) for v in series], dtype=float)
    if not np.all(np.isfinite(arr)):
        raise CopulaGarchJointError(f"标的 {symbol} 收益率含非有限值（NaN/±Inf），拒绝建模")
    return arr


def _garch_filter(returns: np.ndarray, alpha: float, beta: float) -> tuple[np.ndarray, float, float]:
    """GARCH(1,1) 方差定向过滤。返回 (标准化残差 z, 一步 μ 预测, 一步 σ 预测)。"""
    t = returns.shape[0]
    mu = float(np.mean(returns))
    centered = returns - mu
    uncond_var = float(np.var(centered, ddof=0))
    if uncond_var <= 0.0:
        raise CopulaGarchJointError("收益率序列零方差（常数序列），无波动结构可估")
    omega = (1.0 - alpha - beta) * uncond_var
    var = np.empty(t, dtype=float)
    var[0] = uncond_var
    for i in range(1, t):
        var[i] = omega + alpha * centered[i - 1] ** 2 + beta * var[i - 1]
    sigma = np.sqrt(var)
    z = centered / sigma
    var_next = omega + alpha * centered[-1] ** 2 + beta * var[-1]
    return z, mu, math.sqrt(var_next)


def _dcc_forecast(z: np.ndarray, q_bar: np.ndarray, a: float, b: float) -> np.ndarray:
    """DCC(1,1) 一步相关预测。z: T×N 标准化残差；q_bar: N×N 目标相关。"""
    n = z.shape[1]
    q = q_bar.copy()
    for t in range(z.shape[0]):
        zt = z[t].reshape(n, 1)
        q = (1.0 - a - b) * q_bar + a * (zt @ zt.T) + b * q
    d = np.sqrt(np.diag(q))
    d[d <= 0.0] = 1.0
    r = q / np.outer(d, d)
    np.fill_diagonal(r, 1.0)
    return r


def _empirical_pit(z: np.ndarray) -> np.ndarray:
    """经验 CDF 概率积分变换 u=rank/(T+1)（不假设边缘分布形状）。"""
    t = z.shape[0]
    ranks = np.empty_like(z)
    for j in range(z.shape[1]):
        order = np.argsort(z[:, j], kind="mergesort")
        ranks[order, j] = np.arange(1, t + 1, dtype=float)
    return ranks / (t + 1.0)


def _tail_dependence(u: np.ndarray, q: float) -> np.ndarray:
    """下尾共超限经验概率 λ_ij=P(u_i<q,u_j<q)/q；对角=1。"""
    n = u.shape[1]
    exceed = u < q
    lam = np.eye(n)
    for i in range(n):
        for j in range(i + 1, n):
            co = float(np.mean(exceed[:, i] & exceed[:, j])) / q
            lam[i, j] = lam[j, i] = min(co, 1.0)
    return lam


def _cholesky_with_jitter(r: np.ndarray) -> np.ndarray:
    """相关矩阵 Cholesky；奇异/近奇异时逐级加对角抖动兜底（完全相关资产不崩）。"""
    jitter = 0.0
    for _ in range(_CHOL_MAX_ATTEMPTS):
        try:
            return np.linalg.cholesky(r + jitter * np.eye(r.shape[0]))
        except np.linalg.LinAlgError:
            jitter = _CHOL_JITTER if jitter == 0.0 else jitter * 10.0
    # 最后兜底：特征值裁剪
    eigvals, eigvecs = np.linalg.eigh(r)
    eigvals = np.clip(eigvals, _CHOL_JITTER, None)
    fixed = eigvecs @ np.diag(eigvals) @ eigvecs.T
    d = np.sqrt(np.diag(fixed))
    fixed = fixed / np.outer(d, d)
    return np.linalg.cholesky(fixed + _CHOL_JITTER * np.eye(r.shape[0]))


class CopulaGarchJointModel:
    """Copula-GARCH 联合分布模型（≤50 标的，DCC 盘后批算）。"""

    def __init__(self, config: CopulaGarchConfig | None = None) -> None:
        self._config = config or CopulaGarchConfig()

    @property
    def config(self) -> CopulaGarchConfig:
        return self._config

    def fit_portfolio_risk(
        self,
        returns: Mapping[str, Sequence[float]],
        weights: Mapping[str, float],
        marginal_forecasts: Mapping[str, MarginalForecast] | None = None,
        portfolio_value: float = 1.0,
    ) -> JointRiskReport:
        """拟合边缘+DCC 并 Monte Carlo 产出联合尾部依赖矩阵与联合 VaR/ES。

        Args:
            returns: {symbol: 等长日收益率序列}，N∈[2,max_assets]，T≥min_history
            weights: {symbol: 权重}，标的集与 returns 完全一致，Σ|w|>0（内部归一）
            marginal_forecasts: 可选 {symbol: MarginalForecast} 一步边缘预测注入
            portfolio_value: 组合价值（>0），VaR/ES 金额口径缩放

        Returns:
            JointRiskReport（联合尾部依赖矩阵/DCC 一步相关/联合 VaR/ES）

        Raises:
            CopulaGarchJointError: 任一前置校验失败（Fail-Closed）
        """
        cfg = self._config
        symbols = tuple(sorted(returns))
        n = len(symbols)
        if n < 2:
            raise CopulaGarchJointError(f"标的数不足（须 N≥2 才有联合结构）: {n}")
        if n > cfg.max_assets:
            raise CopulaGarchJointError(
                f"标的数 {n} 超过 max_assets={cfg.max_assets}（★≤50 只硬约束，>50 需双 RTX4090 另行评审）"
            )
        if not math.isfinite(portfolio_value) or portfolio_value <= 0:
            raise CopulaGarchJointError(f"portfolio_value 必须为正有限值: {portfolio_value}")

        z_cols: list[np.ndarray] = []
        mu_next: dict[str, float] = {}
        sigma_next: dict[str, float] = {}
        t_len: int | None = None
        for s in symbols:
            arr = _require_finite_series(s, returns[s])
            if t_len is None:
                t_len = arr.shape[0]
            elif arr.shape[0] != t_len:
                raise CopulaGarchJointError(f"标的 {s} 序列长度 {arr.shape[0]} 与其余 {t_len} 不齐")
            z, mu, sig = _garch_filter(arr, cfg.garch_alpha, cfg.garch_beta)
            z_cols.append(z)
            mu_next[s] = mu
            sigma_next[s] = sig
        assert t_len is not None
        if t_len < cfg.min_history:
            raise CopulaGarchJointError(f"样本长度 {t_len} 不足 min_history={cfg.min_history}")

        w_raw = {}
        for s in symbols:
            if s not in weights:
                raise CopulaGarchJointError(f"权重缺少标的 {s}（权重标的集须与收益率完全一致）")
            w = float(weights[s])
            if not math.isfinite(w):
                raise CopulaGarchJointError(f"标的 {s} 权重非有限值: {w}")
            w_raw[s] = w
        extra = set(weights) - set(symbols)
        if extra:
            raise CopulaGarchJointError(f"权重含收益率外标的: {sorted(extra)}")
        total = sum(abs(v) for v in w_raw.values())
        if total <= 0.0:
            raise CopulaGarchJointError("权重绝对值之和为 0（无法归一化组合）")
        w = np.array([w_raw[s] / total for s in symbols], dtype=float)

        if marginal_forecasts is not None:
            missing = [s for s in symbols if s not in marginal_forecasts]
            if missing:
                raise CopulaGarchJointError(f"边缘预测缺少标的: {missing}")
            for s in symbols:
                fc = marginal_forecasts[s]
                if not isinstance(fc, MarginalForecast):
                    raise CopulaGarchJointError(f"标的 {s} 边缘预测类型非法: {type(fc).__name__}")
                mu_next[s] = fc.mu
                sigma_next[s] = fc.sigma

        z_mat = np.column_stack(z_cols)  # T×N

        # ② DCC：Q̄ 复用 MOD-POS-011 收缩协方差（标准化为相关）
        z_map = {s: z_mat[:, i].tolist() for i, s in enumerate(symbols)}
        cov_est = estimate_covariance(z_map)
        cov = np.asarray(cov_est.matrix, dtype=float)
        std = np.sqrt(np.diag(cov))
        std[std <= 0.0] = 1.0
        q_bar = cov / np.outer(std, std)
        np.fill_diagonal(q_bar, 1.0)
        r_next = _dcc_forecast(z_mat, q_bar, cfg.dcc_a, cfg.dcc_b)

        # ③ 经验 PIT + 下尾依赖
        u = _empirical_pit(z_mat)
        lam = _tail_dependence(u, cfg.tail_quantile)

        # ④ Gaussian-Copula MC 联合损失
        chol = _cholesky_with_jitter(r_next)
        rng = np.random.default_rng(cfg.random_seed)
        eps = rng.standard_normal((cfg.n_simulations, n))
        z_sim = eps @ chol.T
        u_sim = norm.cdf(z_sim)
        r_sim = np.empty_like(u_sim)
        for j, s in enumerate(symbols):
            # 经验逆 CDF：标准化残差池分位数 → 还原为收益率尺度
            z_pool = np.sort(z_mat[:, j])
            quantiles = (np.arange(1, t_len + 1, dtype=float) - 0.5) / t_len
            z_emp = np.interp(u_sim[:, j], quantiles, z_pool)
            r_sim[:, j] = mu_next[s] + sigma_next[s] * z_emp
        port_loss = -(r_sim @ w) * portfolio_value  # 损失为正口径

        joint_var: dict[float, float] = {}
        joint_es: dict[float, float] = {}
        sorted_loss = np.sort(port_loss)
        for c in cfg.confidence_levels:
            var_c = float(np.quantile(port_loss, c))
            tail = sorted_loss[sorted_loss >= var_c]
            joint_var[c] = max(var_c, 0.0)
            joint_es[c] = max(float(np.mean(tail)) if tail.size else var_c, joint_var[c])

        return JointRiskReport(
            symbols=symbols,
            tail_dependence_matrix=tuple(tuple(float(v) for v in row) for row in lam),
            dcc_correlation=tuple(tuple(float(v) for v in row) for row in r_next),
            joint_var=joint_var,
            joint_es=joint_es,
            n_assets=n,
            n_observations=t_len,
            simulations=cfg.n_simulations,
        )
