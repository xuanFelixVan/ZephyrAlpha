# [BLUEPRINT] MOD-REGIME-017 | 待统筹登记（CONDAXIS-CAMPAIGN 两态线 formreg 包；挖矿真源 docs/_working/condaxis/formreg/4_turning_signal.md）
# [MODULE] zephyr.regime.formreg.bocpd_online
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; pandas; scipy
# [CONSUMERS] （隔离打靶：docs/_working/condaxis/formreg/8_prereg_targeting.md 冒烟；拐点灰度 p(r_t=0) 消费面接线冻结——裁定#229 未裁）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] Adams-MacKay 2007 在线贝叶斯变点检测：run-length 后验消息传递全程 log 空间
#              （数值稳定）；观测模型=Normal-Inverse-Gamma 共轭→Student-t 预测（robust 防厚尾，
#              挖矿簿 4 台账行 3）；hazard=常数 1/λ 默认 1/250（AM2007 论文示例值，A 股重标=呈批项）；
#              p(r_t=0)=拐点灰度输出（连续量，检测阈值不内建——阈值=ARL 预算标定面禁自拟）；
#              输入建议 z 标准化（与 jump_layer 同纪律，先验为弱信息 NIG）；纯在线序贯零回看
# [MODIFY-GUARD] tests/regime/formreg/test_bocpd_online.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 输入空/非 DatetimeIndex/非升序/含 NaN/非有限值→ValueError（fail-closed，
#                  调用方先丢热身段）；内存 O(T²)（全 run-length 矩阵，月频/数百日级冒烟量级适用）
# [TESTS] tests/regime/formreg/test_bocpd_online.py
# [TTL] permanent
"""bocpd_online — BOCPD 在线变点检测（Adams & MacKay 2007，Student-t 观测模型）。

条件轴总包战役两态线环节[4]施工产出（P2 车道 st-cdx-formreg-20261013）。
仓内在册零实现（grep bocpd 全仓唯一命中=position/core/strategy_book.py:158 接口
占位注释，挖矿簿 4 台账行 3）——本件是该空白的隔离实现。

方法（AM2007 §3 消息传递，log 空间实现）：
    状态=run length r_t（距上一次变点的步数）；hazard H(r)=1/λ 常数（默认 1/250
    =AM2007 论文示例值；A 股重标定=呈批项）。
    观测模型：x_t | r_t ~ NIG 后验预测=Student-t
        df=2α_r, loc=μ_r, scale=√(β_r(κ_r+1)/(α_r κ_r))
    递推（纯在线，t 步只用 ≤t 信息——PIT 天然成立）：
        growth:  log P(r_t=r+1, x_t) = log P(r_{t-1}=r) + log(1−H) + log pred_r(x_t)
        cp:      log P(r_t=0,  x_t) = logsumexp_r(log P(r_{t-1}=r)+log pred_r(x_t)) + log H
        归一化得 run-length 后验 R_t；p_change_t = R_t[0] 即拐点灰度。

输出：DataFrame[date, p_change, runlength_map, runlength_mean]＋全 R 矩阵
（R[t, r]=P(r_t=r|x_1..t)）。检测阈值不内建（ARL 预算标定面，8_prereg_targeting.md §3）。

先验（弱信息，输入建议 z 标准化——与 jump_layer 同纪律）：
    μ₀=0, κ₀=1, α₀=1, β₀=1（标准化量纲下 Student-t 先验 df=2/scale≈1.41）。

# [ALGO_FLOW] external: docs/03_modules/_domain_regime/algo_flow/bocpd_online.yaml
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import numpy as np
import pandas as pd
from scipy.special import logsumexp
from scipy.stats import t as student_t

__all__: Final = ["BOCPDParams", "BOCPDResult", "run_bocpd"]


# ---------------------------------------------------------------------------
# 结构常数区
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class BOCPDParams:
    """BOCPD 参数组（默认=AM2007 论文示例/弱信息先验；A 股重标定=呈批项禁自拟）。

    Attributes:
        hazard_lambda: 常数 hazard 的尺度 λ（H=1/λ；默认 250=AM2007 论文示例值——
            期望变点间隔约 250 步）。
        mu0: NIG 先验均值（输入建议 z 标准化）。
        kappa0: NIG 先验伪计数。
        alpha0: NIG 先验形状。
        beta0: NIG 先验尺度。
    """

    hazard_lambda: float = 250.0
    mu0: float = 0.0
    kappa0: float = 1.0
    alpha0: float = 1.0
    beta0: float = 1.0


@dataclass(frozen=True)
class BOCPDResult:
    """BOCPD 输出。

    Attributes:
        frame: DataFrame[date, p_change(R_t[0]=拐点灰度), runlength_map, runlength_mean]。
        runlength_posterior: 全 R 矩阵（np.ndarray (T, T)，行=步 t 列=run length r）。
        params: 生效参数组。
    """

    frame: pd.DataFrame
    runlength_posterior: np.ndarray
    params: BOCPDParams


def run_bocpd(series: pd.Series, params: BOCPDParams | None = None) -> BOCPDResult:
    """BOCPD 在线递推（纯函数核：同输入同输出，零随机零 IO）。

    Args:
        series: 监测量序列（DatetimeIndex 升序；建议 z 标准化后输入；须无 NaN）。
        params: BOCPDParams（None=论文示例默认）。

    Returns:
        BOCPDResult。

    Raises:
        ValueError: 空/非 DatetimeIndex/非升序/含 NaN 或非有限值（fail-closed）。
    """
    p = params or BOCPDParams()
    if series is None or len(series) == 0:
        raise ValueError("series 不能为空")
    if not isinstance(series.index, pd.DatetimeIndex):
        raise ValueError("series 必须为 DatetimeIndex")
    if not bool(series.index.is_monotonic_increasing):
        raise ValueError("series 必须按日期升序")
    x = series.to_numpy(dtype=float)
    if not np.all(np.isfinite(x)):
        raise ValueError("series 含 NaN/非有限值（fail-closed：调用方先丢热身段）")
    if p.hazard_lambda <= 1.0:
        raise ValueError("hazard_lambda 必须 >1（H=1/λ<1；数值禁入消息文本）")

    n = len(x)
    log_h = float(np.log(1.0 / p.hazard_lambda))
    log_1mh = float(np.log1p(-1.0 / p.hazard_lambda))

    # 每步维护各 run length 的 NIG 后验参数（向量）；R 行后写入全矩阵
    r_matrix = np.zeros((n, n), dtype=float)
    p_change = np.zeros(n, dtype=float)
    rl_map = np.zeros(n, dtype=int)
    rl_mean = np.zeros(n, dtype=float)

    # 初始化（AM2007 约定）：x[0] 确定性开启首段——P(r_0=0)=1，其 NIG 后验=先验吸收 x[0]；
    # 边界处 p_change[0]=0（首观测无"变点前史"，非变点证据）。递推自 t=1 起。
    mu = np.array([(p.kappa0 * p.mu0 + x[0]) / (p.kappa0 + 1.0)], dtype=float)
    kappa = np.array([p.kappa0 + 1.0], dtype=float)
    alpha = np.array([p.alpha0 + 0.5], dtype=float)
    beta = np.array([p.beta0 + 0.5 * p.kappa0 * (x[0] - p.mu0) ** 2 / (p.kappa0 + 1.0)], dtype=float)
    log_r = np.array([0.0], dtype=float)
    r_matrix[0, 0] = 1.0

    for i in range(1, n):
        # 1) 各 run length 的 Student-t 预测 log 密度
        df = 2.0 * alpha
        scale = np.sqrt(beta * (kappa + 1.0) / (alpha * kappa))
        with np.errstate(divide="ignore", invalid="ignore"):
            log_pred = student_t.logpdf(x[i], df, loc=mu, scale=scale)
        log_pred = np.where(np.isfinite(log_pred), log_pred, -np.inf)
        # 2) growth + cp（log 空间；AM2007：cp 枝的似然=**新段先验预测** π⁰(x_t)，
        #    非 r_{t-1} 枝的后验预测——若误用后者则 p(r_t=0)≡H 代数退化（本车道实测坑））
        log_growth = log_r + log_1mh + log_pred  # 新 run length 1..m
        df0 = 2.0 * p.alpha0
        scale0 = float(np.sqrt(p.beta0 * (p.kappa0 + 1.0) / (p.alpha0 * p.kappa0)))
        log_pred_fresh = float(student_t.logpdf(x[i], df0, loc=p.mu0, scale=scale0))
        log_cp = logsumexp(log_r) + log_h + log_pred_fresh  # 新 run length 0
        log_r_new = np.concatenate(([log_cp], log_growth))
        log_z = logsumexp(log_r_new)
        log_r_new = log_r_new - log_z
        log_r = log_r_new
        # 3) NIG 后验更新（两条枝都要吸收 x[i]——r_t=0 意为"当前段自 t 起，含 x_t 本身"）：
        #    growth 枝：r_{t-1}=k 存活 → r_t=k+1，后验=旧后验+x_i；
        #    cp 枝：r_t=0，后验=先验+x_i（禁裸先验——新段含当前观测）。
        kappa_next = kappa + 1.0
        mu_next = (kappa * mu + x[i]) / kappa_next
        alpha_next = alpha + 0.5
        beta_next = beta + 0.5 * kappa * (x[i] - mu) ** 2 / kappa_next
        mu = np.concatenate(
            (
                [(p.kappa0 * p.mu0 + x[i]) / (p.kappa0 + 1.0)],
                mu_next,
            )
        )
        kappa = np.concatenate(([p.kappa0 + 1.0], kappa_next))
        alpha = np.concatenate(([p.alpha0 + 0.5], alpha_next))
        beta = np.concatenate(
            (
                [p.beta0 + 0.5 * p.kappa0 * (x[i] - p.mu0) ** 2 / (p.kappa0 + 1.0)],
                beta_next,
            )
        )
        # 4) 记录
        r_post = np.exp(log_r)
        r_matrix[i, : len(r_post)] = r_post
        p_change[i] = float(r_post[0])
        rl_map[i] = int(np.argmax(r_post))
        rl_mean[i] = float(np.dot(np.arange(len(r_post), dtype=float), r_post))

    frame = pd.DataFrame(
        {
            "date": series.index.strftime("%Y-%m-%d"),
            "p_change": np.round(p_change, 8),
            "runlength_map": rl_map,
            "runlength_mean": np.round(rl_mean, 3),
        }
    )
    return BOCPDResult(frame=frame, runlength_posterior=r_matrix, params=p)
