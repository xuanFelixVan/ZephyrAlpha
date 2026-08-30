# [BLUEPRINT] MOD-SIG-045 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/91_density_prediction.md §3
# [MODULE] zephyr.signal_ashare.survival_time_predictor
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] numpy
# [CONSUMERS] (待 BM-POS-01 仓位时间预算 / 止盈止损时点消费层)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] durations>0 且 events∈{0,1}；AFT 仅右删失；KM 生存函数单调不增；纯函数无副作用
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 非法输入（长度不一致/durations≤0/events∉{0,1}）→ ValueError；MLE 不收敛 → RuntimeError
# [TESTS] tests/signal_ashare/test_survival_time_predictor.py
# [A_module] module_id=MOD-SIG-045 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: 持有期 durations + 事件指示 events（1=止盈止损发生，0=右删失）+ 协变量 X（市场状态等，可空）
# A1: kaplan_meier——非参数基线生存曲线（分层校准用）
# A2: WeibullAFTModel.fit——AFT 参数生存模型 MLE（解析梯度/Hessian Newton 法，y=log t 参数化）
# A3: 预测件——中位时间/S(t)/horizon 内事件概率/期望时间（Γ 闭式）
# O1: SurvivalCurve / WeibullAFTModel（coef/intercept/sigma/loglik）
# [/ALGO_FLOW]
"""
Survival 止盈止损时间预测（BM-SEL-15，MOD-SIG-045）。

预测止盈止损还有多久发生——不是固定 N 天，而是时间概率分布。

选型按 91 号 memo §3 三选一裁定落地：
  首选 **AFT**（Accelerated Failure Time，Weibull 参数族）——直接建模"事件发生
  时间"的对数线性回归，输出可解释持有期分布参数，与仓位时间预算直接对接；
  不依赖 Cox 比例风险假设（市场状态切换下 PH 假设大概率不成立）；参数少
  （两参族），个人系统样本量可估。**Kaplan-Meier 作非参数基线**（校准 AFT 拟合
  优度）。Cox 协变量诊断/时变协变量/竞争风险列 Phase 3+ 远期，不落地。

轻量实现纪律：numpy 单一依赖，MLE 用解析梯度+Hessian 的 Newton 法（y=log t
参数化，ll 对 β 凹），不引入 lifelines/scipy 重依赖。

激活条件注记（91 号 §3）：本模块为密度预测体系配套件，当前以合成/历史序列
自验证；消费 BM-SEL-03 市场状态作协变量的接线待密度预测验证通过后激活。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: durations 参数
#   fields: 参数 durations，类型注解 Iterable[float]
#   code: survival_time_predictor.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: events 参数
#   fields: 参数 events，类型注解 Iterable[int]
#   code: survival_time_predictor.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① SurvivalCurve
#   name_en: SurvivalCurve
#   intro: KM 生存曲线（阶跃）：times[i] 处生存率降为 survival[i]。
#   desc: KM 生存曲线（阶跃）：times[i] 处生存率降为 survival[i]。；公共方法（定义序）: survival_at, median_time；源码 L106-L128
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② kaplan_meier
#   name_en: kaplan_meier
#   intro: Kaplan-Meier 非参数生存曲线（右删失，AFT 校准基线）。
#   desc: Kaplan-Meier 非参数生存曲线（右删失，AFT 校准基线）。 S(t) = Π_{t_i≤t} (1 − d_i/n_i)，d_i=t_i 时刻事件数，n_i=风险集大…；源码 L145-L161
#   inputs: durations events
#   outputs: SurvivalCurve
# - id: A3
#   name_zh: ③ WeibullAFTModel
#   name_en: WeibullAFTModel
#   intro: Weibull AFT 参数生存模型（右删失 MLE，Newton 法）。
#   desc: Weibull AFT 参数生存模型（右删失 MLE，Newton 法）。 参数化（y=log t 极值分布形式）：log T = x·β + σ·W，W ~ 标准最小极值分布。…；公共方法（定义序）: sigma,…
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: SurvivalCurve
#   name_en: SurvivalCurve
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: (待 BM-POS-01 仓位时间预算 / 止盈止损时点消费层)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final, Iterable

import numpy as np

__all__: Final = [
    "SurvivalCurve",
    "WeibullAFTModel",
    "kaplan_meier",
]


@dataclass(frozen=True)
class SurvivalCurve:
    """KM 生存曲线（阶跃）：times[i] 处生存率降为 survival[i]。"""

    times: tuple[float, ...]
    survival: tuple[float, ...]
    n_at_risk_start: int

    def survival_at(self, t: float) -> float:
        """t 时刻生存率（阶跃右连续口径：最后 ≤t 事件点的生存率，之前为 1）。"""
        s = 1.0
        for ti, si in zip(self.times, self.survival, strict=False):
            if ti <= t:
                s = si
            else:
                break
        return s

    def median_time(self) -> float | None:
        """中位生存时间（首个 S≤0.5 的事件时刻）；未达 0.5 返回 None。"""
        for ti, si in zip(self.times, self.survival, strict=False):
            if si <= 0.5:
                return ti
        return None


def _validate_inputs(durations: list[float], events: list[int]) -> tuple[np.ndarray, np.ndarray]:
    d = np.asarray(durations, dtype=float)
    e = np.asarray(events, dtype=float)
    if d.shape != e.shape:
        raise ValueError(f"durations 与 events 长度不一致: {len(d)} vs {len(e)}")
    if len(d) == 0:
        raise ValueError("输入为空")
    if (d <= 0).any():
        raise ValueError("durations 必须全为正")
    if ((e != 0.0) & (e != 1.0)).any():
        raise ValueError("events 必须 ∈ {0,1}")
    return d, e


def kaplan_meier(durations: Iterable[float], events: Iterable[int]) -> SurvivalCurve:
    """Kaplan-Meier 非参数生存曲线（右删失，AFT 校准基线）。

    S(t) = Π_{t_i≤t} (1 − d_i/n_i)，d_i=t_i 时刻事件数，n_i=风险集大小。
    """
    d, e = _validate_inputs(list(durations), list(events))
    event_times = np.unique(d[e == 1.0])
    times: list[float] = []
    surv: list[float] = []
    s = 1.0
    for t in event_times:
        at_risk = float((d >= t).sum())
        n_events = float(((d == t) & (e == 1.0)).sum())
        s *= 1.0 - n_events / at_risk
        times.append(float(t))
        surv.append(s)
    return SurvivalCurve(times=tuple(times), survival=tuple(surv), n_at_risk_start=len(d))


class WeibullAFTModel:
    """Weibull AFT 参数生存模型（右删失 MLE，Newton 法）。

    参数化（y=log t 极值分布形式）：log T = x·β + σ·W，W ~ 标准最小极值分布。
    S(t|x) = exp(−exp(z))，z = (log t − x·β)/σ。
    ll_i = δ_i·(z_i − exp(z_i) − log σ) − (1−δ_i)·exp(z_i)。
    """

    def __init__(self) -> None:
        self.coef: np.ndarray | None = None  # β（不含截距）
        self.intercept: float = 0.0  # β0
        self.log_sigma: float = 0.0  # τ = log σ
        self.loglik: float = 0.0
        self.n_iter: int = 0

    @property
    def sigma(self) -> float:
        return math.exp(self.log_sigma)

    # ---------- 内部：对数似然与解析导数 ----------
    def _ll_grad_hess(
        self, theta: np.ndarray, y: np.ndarray, delta: np.ndarray, x: np.ndarray
    ) -> tuple[float, np.ndarray, np.ndarray]:
        """返回 (ll, grad, hess)。theta = [β..., τ]；x 含截距列。

        数值护栏：z 截断 ±40（exp(z) 溢出防护；远离最优解的坏区域 ll 保持有限，
        由外层步长回退拒绝），良态区域 |z| 远小于截断点不受影响。
        """
        p = x.shape[1]
        beta = theta[:p]
        tau = float(np.clip(theta[p], -20.0, 20.0))
        sigma = math.exp(tau)
        z = np.clip((y - x @ beta) / sigma, -40.0, 40.0)
        ez = np.exp(z)
        ll = float((delta * (z - ez - tau) - (1.0 - delta) * ez).sum())
        # 解析梯度
        resid = ez - delta  # (e − δ)
        grad_beta = (x * (resid / sigma)[:, None]).sum(axis=0)
        grad_tau = float((z * resid - delta).sum())
        grad = np.concatenate([grad_beta, [grad_tau]])
        # 解析 Hessian
        hess_bb = -(x * ez[:, None]).T @ x / (sigma**2)
        hess_bt = -(x * ((ez - delta + ez * z) / sigma)[:, None]).sum(axis=0)
        hess_tt = float((-z * (ez - delta) - (z**2) * ez).sum())
        hess = np.empty((p + 1, p + 1))
        hess[:p, :p] = hess_bb
        hess[:p, p] = hess_bt
        hess[p, :p] = hess_bt
        hess[p, p] = hess_tt
        return ll, grad, hess

    def fit(
        self,
        durations: Iterable[float],
        events: Iterable[int],
        covariates: Iterable[Iterable[float]] | None = None,
        *,
        max_iter: int = 200,
        tol: float = 1e-8,
        ridge: float = 1e-6,
        max_step: float = 2.0,
    ) -> WeibullAFTModel:
        """MLE 拟合（阻尼 Newton：信赖域步长上限 + 步长回退 + 对角岭正则）。

        Args:
            durations: 持有期（>0）
            events: 事件指示（1=止盈止损发生，0=右删失）
            covariates: 协变量矩阵（n×p，如市场状态变量）；None → 仅截距
            max_iter / tol / ridge: Newton 控制参数
            max_step: 信赖域步长范数上限（location-scale 族 ll 非全局二次，
                裸 Newton 首步易过冲——限步长保证单调上升路径）

        Raises:
            ValueError: 输入非法；covariates 行数与 durations 不一致。
            RuntimeError: 达到 max_iter 仍未收敛。
        """
        d, e = _validate_inputs(list(durations), list(events))
        y = np.log(d)
        n = len(d)
        if covariates is None:
            x = np.ones((n, 1))
        else:
            x_raw = np.asarray([list(row) for row in covariates], dtype=float)
            if x_raw.ndim != 2 or x_raw.shape[0] != n:
                raise ValueError(f"covariates 行数与 durations 不一致: {x_raw.shape} vs n={n}")
            x = np.column_stack([np.ones(n), x_raw])
        p = x.shape[1]
        theta = np.zeros(p + 1)
        theta[0] = float(y.mean())  # 截距初值=log 时间均值
        ll_old, _, _ = self._ll_grad_hess(theta, y, e, x)
        for it in range(max_iter):
            _, grad, hess = self._ll_grad_hess(theta, y, e, x)
            # Levenberg 阻尼 Newton：λ 自适应放大直到 (H−λI) 负定且 ll 单调上升
            # （H 在远离最优解处可非负定，裸 Newton 方向不保证上升——λ 兜底方向性）
            lam = ridge
            accepted = False
            for _ in range(12):
                try:
                    step = np.linalg.solve(hess - lam * np.eye(p + 1), -grad)
                except np.linalg.LinAlgError:
                    lam *= 10.0
                    continue
                # 信赖域：步长范数上限（防过冲到 exp 爆炸区）
                step_norm = float(np.linalg.norm(step))
                if step_norm > max_step:
                    step = step * (max_step / step_norm)
                theta_new = theta + step
                ll_new, _, _ = self._ll_grad_hess(theta_new, y, e, x)
                if ll_new >= ll_old:
                    accepted = True
                    break
                lam *= 10.0
            if not accepted:
                raise RuntimeError("WeibullAFT MLE 阻尼方向兜底失败（12 次 λ 放大仍无上升步）")
            theta = theta_new
            self.n_iter = it + 1
            if abs(ll_new - ll_old) < tol:
                ll_old = ll_new
                break
            ll_old = ll_new
        else:
            raise RuntimeError(f"WeibullAFT MLE 未收敛（max_iter={max_iter}）")
        self.intercept = float(theta[0])
        self.coef = theta[1:p].copy()
        self.log_sigma = float(theta[p])
        self.loglik = ll_old
        return self

    # ---------- 预测件 ----------
    def _xb(self, x: Iterable[float] | None) -> float:
        if x is None:
            return self.intercept
        if self.coef is None or len(self.coef) == 0:
            raise ValueError("模型无协变量（fit 时 covariates=None），predict 禁止传 x")
        xv = np.asarray(list(x), dtype=float)
        if xv.shape != self.coef.shape:
            raise ValueError(f"协变量维度不一致: {xv.shape} vs {self.coef.shape}")
        return self.intercept + float(xv @ self.coef)

    def survival_prob(self, t: float, x: Iterable[float] | None = None) -> float:
        """S(t|x) = exp(−exp(z))，持有超过 t 的概率。t≤0 → 1.0。"""
        if t <= 0:
            return 1.0
        z = (math.log(t) - self._xb(x)) / self.sigma
        return math.exp(-math.exp(z))

    def prob_event_within(self, horizon: float, x: Iterable[float] | None = None) -> float:
        """horizon 内止盈止损发生概率 = 1 − S(horizon)。"""
        return 1.0 - self.survival_prob(horizon, x)

    def median_time(self, x: Iterable[float] | None = None) -> float:
        """中位持有期 = exp(x·β)·(ln 2)^σ。"""
        return math.exp(self._xb(x)) * math.pow(math.log(2.0), self.sigma)

    def expected_time(self, x: Iterable[float] | None = None) -> float:
        """期望持有期 = exp(x·β)·Γ(1+σ)（Weibull 均值闭式）。"""
        return math.exp(self._xb(x)) * math.gamma(1.0 + self.sigma)
