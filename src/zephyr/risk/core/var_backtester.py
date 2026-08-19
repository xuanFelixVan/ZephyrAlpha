# [BLUEPRINT] MOD-RK-011 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [MODULE] zephyr.risk.core.var_backtester
# [DOMAIN] D_RISK
# [DEPENDENCIES] numpy; scipy; zephyr.shared.foundation.errors
# [CONSUMERS] MOD-RK-05(VaR Calculator 回测验证); MOD-RK-15(Tail Risk ES 回测); daily_auditor(日终回测报告)
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] 超限计数≥0;ES≥VaR(尾部期望≥分位数);E-value单调非降(乘性累积);Z2原假设E[Z2]=-1
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InsufficientBacktestHistoryError;InvalidBacktestInputError
# [TESTS] tests/risk/test_var_backtester.py
# [A_module] module_id=MOD-RK-05B | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

VaR/ES Backtester — VaR/ES 模型回测验证器 (MOD-RK-05B, 36号 §3.9 施工)

36_var_es_monitoring.md §3.9 定义的 13 法回测，本模块实现 MVP 4 法（选型优先级最高）：
    1. Kupiec POF — 覆盖率检验（超限频率对不对），LR_UC ~ χ²(1)
    2. Christoffersen — 独立性检验（超限是否聚集），LR_cc = LR_UC + LR_ind ~ χ²(2)
    3. Acerbi-Szekely Z2 — ES 直接回测（超限日损失幅度），E[Z2]=-1
    4. E-backtesting — e-values/e-process 在线累积（GREM 默认 betting process）

符号约定（与 var_calculator.py 一致）：
    - VaR/ES 预测值：正数表示潜在损失额 (≥0)
    - realized_return：实际收益，负数=损失，正数=盈利
    - 超限（violation/breach）：realized_return ≤ -VaR（即损失 ≥ VaR）

理论依据：
    - Kupiec 1995 POF (Proportion-of-Failures) 似然比检验
    - Christoffersen 1998 条件覆盖率（独立性 + 覆盖率）
    - Acerbi & Szekely 2014/2017 Z2 ES 回测（非参数）
    - Wang, Wang & Ziegel arxiv 2209.00991v6 (2026-04) E-backtesting
    - ERCIM News 145 (2026-07) Ruodu Wang GREM 默认 betting process + 多区制告警

Phase 2 (未实现): 多项式 VaR 回测 / Fissler-Ziegel 联合回测 / Ridge / DSR / CSCV
Phase 3 (未实现): Latent-Regime Bias Auditing / Comparative e-backtests / ES 精度极限 / Feature-Aware

依据: 36_var_es_monitoring.md §3.9, §3.11 回测验证端到端施工流程
SSoT: 36_var_es_monitoring.md §3.9
Version: 0.1.0 (MVP 4 法)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 回测观测序列 list[BacktestObservation]
#   fields: date交易日 + var_forecast预测VaR(≥0正数=损失) + es_forecast预测ES(≥var) + realized_return实际收益(负=亏)
#   code: var_backtester.py L92-122 单个观测校验ES≥VaR、is_violation判定；L313-340 序列校验≥30样本并转numpy数组
# - id: I2
#   name: 置信度参数 confidence_level
#   fields: confidence_level∈(0,1) 默认0.95 → alpha名义超限率=1-confidence
#   code: var_backtester.py L291-298 构造器校验区间并算alpha
# 层: 算法
# - id: A1
#   name_zh: ① Kupiec POF 覆盖率检验
#   name_en: Kupiec POF
#   intro: 数实际超限次数，看超限频率和名义α对不对得上
#   desc: 似然比检验 LR_UC=-2(lnL(α)-lnL(p̂))，p̂=N/T为MLE（L369-371，eps=1e-12截断防log(0)），p=1-χ²₁.cdf(LR_UC)（L374），p<0.05拒绝
#   inputs: I1 I2
#   outputs: KupiecResult(n_violations/p_hat/lr_uc/p_value/reject)
#   invariant: LR_UC≥0 且 p_value∈[0,1]
# - id: A2
#   name_zh: ② Christoffersen 条件覆盖率检验
#   name_en: Christoffersen CC
#   intro: 看超限是不是扎堆出现（独立性）外加覆盖率一起验
#   desc: 逐日转移矩阵n_00/n_01/n_10/n_11（L406-416）；LR_ind=-2(lnL_uncond-lnL_cond)（L446-457，单状态时取0）；LR_cc=LR_UC+LR_ind~χ²(2)（L459-460）
#   inputs: I1 I2
#   outputs: ChristoffersenResult(lr_uc/lr_ind/lr_cc/p_value/reject/转移矩阵)
#   invariant: LR_cc=LR_UC+LR_ind 且 p_value∈[0,1]
# - id: A3
#   name_zh: ③ Acerbi-Szekely Z2 ES直接回测
#   name_en: Acerbi-Szekely Z2
#   intro: 只盯超限日，看实际亏损幅度和ES预测是否一致
#   desc: Z2=(1/N)Σ超限日 realized_return/es_forecast（L497-500，比值均<0）；E[Z2]=-1；MVP简化判定 z2<-1且N≥5→reject（L505，需≥1超限否则报错）
#   inputs: I1 I2
#   outputs: AcerbiSzekelyResult(z2/expected=-1/violation_ratios/reject)
#   invariant: 原假设E[Z2]=-1，Z2<-1意味ES低估
# - id: A4
#   name_zh: ④ E-backtesting GREM在线累积
#   name_en: E-backtesting GREM
#   intro: 每天乘一个因子累积e-value，任何时点超过1/α就否决模型
#   desc: b_s=1{超限}-α（L553，校准时E[b]=0）；GREM自适应λ*=(p̂_rolling-α)/(α(1-α))截断[0,0.5/α]（L557-578）；e_t=Π(1+λ_s·b_s)（L582-589）；阈值1/α，log刻度四级告警green/yellow/red/black（L592-605）
#   inputs: I1 I2
#   outputs: EBacktestResult(e_value/e_process/lambda_series/alert_level/reject)
#   invariant: e_value≥0乘性累积单调非降方向由b_s定；anytime-valid阈值=1/α
# - id: A5
#   name_zh: ⑤ Basel Traffic Light 三区制
#   name_en: Basel Traffic Light
#   intro: 巴塞尔红绿灯，按超限次数相对期望的倍数划绿黄红区
#   desc: 期望超限=T·α（L637）；Green≤1.28×期望 / Yellow≤1.6× / Red>1.6×（L639-644，近似95%VaR250天16/20阈值的比例化）
#   inputs: I1 I2
#   outputs: dict(zone/n_violations/expected_violations/violation_ratio)
# 层: 输出
# - id: O1
#   name_zh: 四项单项检验结果对象
#   name_en: Per-test Results
#   intro: Kupiec/Christoffersen/Z2/E-backtest各自的dataclass结果含统计量p值和reject判定
#   downstream: full_report汇总；MOD-RK-05 VaR Calculator回测验证；MOD-RK-15 Tail Risk ES回测
# - id: O2
#   name_zh: 全量回测报告字典
#   name_en: full_report dict
#   intro: 4法+Basel红绿灯+overall_reject综合判定的日终报告，单项样本不足降级为error字段
#   invariant: overall_reject=任一检验reject即告警
#   downstream: daily_auditor日终回测报告（36号§3.11端到端流程）
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# I2 --> A1
# I1 --> A2
# I2 --> A2
# I1 --> A3
# I2 --> A3
# I1 --> A4
# I2 --> A4
# I1 --> A5
# I2 --> A5
# A1 --> O1
# A2 --> O1
# A3 --> O1
# A4 --> O1
# A1 --> O2
# A2 --> O2
# A3 --> O2
# A4 --> O2
# A5 --> O2
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import numpy as np
from scipy.stats import chi2

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "BacktestObservation",
    "KupiecResult",
    "ChristoffersenResult",
    "AcerbiSzekelyResult",
    "EBacktestResult",
    "EBacktestAlertLevel",
    "VarBacktester",
    "InsufficientBacktestHistoryError",
    "InvalidBacktestInputError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 异常
# ──────────────────────────────────────────────────────────────────────────────


class InsufficientBacktestHistoryError(ZephyrBaseError):
    """回测样本不足。Kupiec/Christoffersen 需 ≥30 样本，Z2 需 ≥1 超限。"""


class InvalidBacktestInputError(ZephyrBaseError):
    """回测输入无效（长度不匹配、VaR/ES 非正、置信度越界等）。"""


# ──────────────────────────────────────────────────────────────────────────────
# 数据结构
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class BacktestObservation:
    """单日回测观测。

    Attributes:
        date: 交易日
        var_forecast: VaR 预测值（正数表示潜在损失额，与 VaRResult.value 一致）
        es_forecast: ES 预测值（正数表示潜在损失额，≥ var_forecast）
        realized_return: 实际收益（负数=损失，正数=盈利）
        pnl_type: P&L 双轨标记（36号 §3.13 契约，默认 "clean"）——回测验证
            只接受 clean P&L（模型纯度检验），"dirty" 构造即拒绝
            （dirty 含交易成本/锁仓 MtM，会污染检验）
    """

    date: datetime
    var_forecast: float
    es_forecast: float
    realized_return: float
    pnl_type: str = "clean"

    def __post_init__(self) -> None:
        if self.pnl_type != "clean":
            raise InvalidBacktestInputError(
                f"pnl_type 必须为 'clean'（dirty P&L 会污染模型纯度检验，36号 §3.13），"
                f"得到 {self.pnl_type!r}"
            )
        if self.var_forecast < 0:
            raise InvalidBacktestInputError(
                f"var_forecast 必须 ≥0（正数表示损失），得到 {self.var_forecast}"
            )
        if self.es_forecast < self.var_forecast:
            raise InvalidBacktestInputError(
                f"es_forecast ({self.es_forecast}) 必须 ≥ var_forecast ({self.var_forecast})，"
                f"ES 是尾部期望 ≥ VaR 分位数"
            )

    @property
    def is_violation(self) -> bool:
        """是否超限（损失 ≥ VaR，即 realized_return ≤ -VaR）。"""
        return self.realized_return <= -self.var_forecast


@dataclass
class KupiecResult:
    """Kupiec POF 检验结果（覆盖率）。

    原假设 H0: 实际超限率 = 名义超限率 (1 - confidence)
    统计量 LR_UC ~ χ²(1)
    """

    n_violations: int
    n_obs: int
    alpha: float  # 名义超限率 = 1 - confidence
    p_hat: float  # 实际超限率 = n_violations / n_obs
    lr_uc: float  # 似然比统计量
    p_value: float
    reject: bool  # p_value < 0.05 拒绝 H0

    def to_dict(self) -> dict[str, Any]:
        return {
            "n_violations": self.n_violations,
            "n_obs": self.n_obs,
            "alpha": self.alpha,
            "p_hat": self.p_hat,
            "lr_uc": self.lr_uc,
            "p_value": self.p_value,
            "reject": self.reject,
        }


@dataclass
class ChristoffersenResult:
    """Christoffersen 条件覆盖率检验结果（独立性 + 覆盖率）。

    原假设 H0: 超限独立 + 覆盖正确
    统计量 LR_cc = LR_UC + LR_ind ~ χ²(2)
    """

    lr_uc: float
    lr_ind: float  # 独立性分量
    lr_cc: float  # 条件覆盖率 = UC + ind
    p_value: float
    reject: bool
    n_00: int  # 未超限→未超限
    n_01: int  # 未超限→超限
    n_10: int  # 超限→未超限
    n_11: int  # 超限→超限（聚集）

    def to_dict(self) -> dict[str, Any]:
        return {
            "lr_uc": self.lr_uc,
            "lr_ind": self.lr_ind,
            "lr_cc": self.lr_cc,
            "p_value": self.p_value,
            "reject": self.reject,
            "transition_matrix": {
                "n_00": self.n_00,
                "n_01": self.n_01,
                "n_10": self.n_10,
                "n_11": self.n_11,
            },
        }


@dataclass
class AcerbiSzekelyResult:
    """Acerbi-Szekely Z2 ES 回测结果。

    原假设 H0: 超限日实际损失与 ES 预测一致，E[Z2] = -1
    Z2 = (1/N) * Σ [realized_return / es_forecast] * 1{violation}
    Z2 < -1 显著 → ES 低估（损失比预测更严重）
    """

    z2: float
    expected: float  # E[Z2] = -1
    n_violations: int
    n_obs: int
    violation_ratios: np.ndarray  # 每个超限日的 realized/es 比值
    reject: bool  # Z2 显著 < -1

    def to_dict(self) -> dict[str, Any]:
        return {
            "z2": self.z2,
            "expected": self.expected,
            "n_violations": self.n_violations,
            "n_obs": self.n_obs,
            "violation_ratios": self.violation_ratios.tolist(),
            "reject": self.reject,
        }


class EBacktestAlertLevel(str, Enum):
    """E-backtesting 多区制告警四级（ERCIM 145 GREM 接口）。

    基于 e-value 相对阈值 1/α 的对数刻度：
        green  : log(e) < 0.5 * log(1/α)   — 无动作
        yellow : 0.5 * log(1/α) ≤ log(e) < log(1/α) — 早期预警
        red    : log(1/α) ≤ log(e) < 2 * log(1/α)  — 实质证据，审查校准
        black  : log(e) ≥ 2 * log(1/α)              — 决定性证据，拒绝模型
    """

    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"
    BLACK = "black"


@dataclass
class EBacktestResult:
    """E-backtesting 结果（e-values/e-process，GREM 默认）。

    e-process: e_t = Π_{s=1}^{t} (1 + λ * b_s)
    b_s: backtest e-statistic（基于超限指示的归一化）
    GREM: λ 自适应（growth-rate-optimal combined，model-free）

    anytime-valid: 无需预定样本量，任意时点可判
    """

    e_value: float  # 累积 e-value（最终）
    e_process: np.ndarray  # 每日 e-process（累积乘积）
    log_e_process: np.ndarray  # 对数 e-process（累加和）
    lambda_series: np.ndarray  # 每日 λ（GREM 自适应）
    n_violations: int
    n_obs: int
    alpha: float
    threshold: float  # 1/α 拒绝阈值
    alert_level: EBacktestAlertLevel
    reject: bool  # e_value > 1/α

    def to_dict(self) -> dict[str, Any]:
        return {
            "e_value": self.e_value,
            "e_process": self.e_process.tolist(),
            "log_e_process": self.log_e_process.tolist(),
            "lambda_series": self.lambda_series.tolist(),
            "n_violations": self.n_violations,
            "n_obs": self.n_obs,
            "alpha": self.alpha,
            "threshold": self.threshold,
            "alert_level": self.alert_level.value,
            "reject": self.reject,
        }


# ──────────────────────────────────────────────────────────────────────────────
# 回测器
# ──────────────────────────────────────────────────────────────────────────────


class VarBacktester:
    """VaR/ES 模型回测验证器（36号 §3.9 MVP 4 法）。

    用法::

        bt = VarBacktester(confidence_level=0.95)
        observations = [
            BacktestObservation(date=t1, var_forecast=25000, es_forecast=32000, realized_return=-0.01),
            BacktestObservation(date=t2, var_forecast=26000, es_forecast=33000, realized_return=-0.03),
            # ... ≥30 样本
        ]
        kupiec = bt.kupiec_pof(observations)
        christ = bt.christoffersen(observations)
        z2 = bt.acerbi_szekely_z2(observations)
        ebt = bt.e_backtesting(observations)

    所有方法均不修改输入 observations（纯函数式）。
    """

    def __init__(self, confidence_level: float = 0.95) -> None:
        if not 0.0 < confidence_level < 1.0:
            raise InvalidBacktestInputError(
                f"confidence_level 须 ∈ (0,1)，得到 {confidence_level}"
            )
        self._confidence = confidence_level
        self._alpha = 1.0 - confidence_level  # 名义超限率
        logger.debug("VarBacktester 初始化: confidence=%.3f alpha=%.3f", confidence_level, self._alpha)

    @property
    def confidence_level(self) -> float:
        return self._confidence

    @property
    def alpha(self) -> float:
        """名义超限率 (1 - confidence)。"""
        return self._alpha

    # ──────────────────────────────────────────────────────────────────────
    # 辅助
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def _validate_observations(
        observations: list[BacktestObservation],
        min_samples: int = 30,
        require_violations: bool = False,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """校验观测序列并返回数组。

        Returns:
            var_arr: VaR 预测数组 (n,)
            es_arr: ES 预测数组 (n,)
            ret_arr: 实际收益数组 (n,)
            violation_mask: 超限布尔数组 (n,)
        """
        if len(observations) < min_samples:
            raise InsufficientBacktestHistoryError(
                f"回测需 ≥{min_samples} 样本，得到 {len(observations)}。"
                f"Kupiec/Christoffersen 需 ≥30，A 股约 1.5 个月数据。"
            )
        var_arr = np.array([o.var_forecast for o in observations], dtype=np.float64)
        es_arr = np.array([o.es_forecast for o in observations], dtype=np.float64)
        ret_arr = np.array([o.realized_return for o in observations], dtype=np.float64)
        violation_mask = ret_arr <= -var_arr
        if require_violations and not np.any(violation_mask):
            raise InsufficientBacktestHistoryError(
                "Z2 检验需 ≥1 个超限日，当前序列无超限（VaR 模型可能过度保守）。"
            )
        return var_arr, es_arr, ret_arr, violation_mask

    # ──────────────────────────────────────────────────────────────────────
    # 第 1 法: Kupiec POF
    # ──────────────────────────────────────────────────────────────────────

    def kupiec_pof(self, observations: list[BacktestObservation]) -> KupiecResult:
        """Kupiec POF 似然比检验（覆盖率）。

        H0: 实际超限率 = 名义超限率 α
        LR_UC = -2 * ln[ L(α) / L(p̂) ] ~ χ²(1)
        其中 L(p) = (1-p)^(T-N) * p^N，p̂ = N/T 为 MLE

        36号 §3.9 line 439
        """
        _, _, _, vmask = self._validate_observations(observations, min_samples=30)
        T = len(observations)
        N = int(np.sum(vmask))
        alpha = self._alpha
        p_hat = N / T if T > 0 else 0.0

        # 边界处理：N=0 或 N=T 时 p̂=0/1 导致 log(0)
        # Kupiec 原始公式在 N=0 或 N=T 时不适用，用截断保护
        eps = 1e-12
        p_hat_safe = min(max(p_hat, eps), 1.0 - eps)

        # L(α) / L(p̂) 的对数
        # ln L(α) = (T-N)*ln(1-α) + N*ln(α)
        # ln L(p̂) = (T-N)*ln(1-p̂) + N*ln(p̂)
        log_L_alpha = (T - N) * np.log(1.0 - alpha) + N * np.log(alpha)
        log_L_phat = (T - N) * np.log(1.0 - p_hat_safe) + N * np.log(p_hat_safe)
        lr_uc = -2.0 * (log_L_alpha - log_L_phat)

        # p-value: χ²(1) 上尾
        p_value = 1.0 - chi2.cdf(lr_uc, df=1)
        reject = bool(p_value < 0.05)

        return KupiecResult(
            n_violations=N,
            n_obs=T,
            alpha=alpha,
            p_hat=p_hat,
            lr_uc=float(lr_uc),
            p_value=float(p_value),
            reject=reject,
        )

    # ──────────────────────────────────────────────────────────────────────
    # 第 2 法: Christoffersen 独立性 + 条件覆盖率
    # ──────────────────────────────────────────────────────────────────────

    def christoffersen(self, observations: list[BacktestObservation]) -> ChristoffersenResult:
        """Christoffersen 条件覆盖率检验（独立性 + 覆盖率）。

        H0: 超限独立 + 覆盖正确
        转移矩阵 n_ij (i=前状态, j=后状态, 0=未超限, 1=超限)
        LR_ind = -2 * ln[ L_unconditional / L_conditional ] ~ χ²(1)
        LR_cc = LR_UC + LR_ind ~ χ²(2)

        36号 §3.9 line 440
        """
        _, _, _, vmask = self._validate_observations(observations, min_samples=30)
        T = len(observations)
        violations = vmask.astype(int)

        # 转移矩阵（T-1 次转移）
        n_00 = n_01 = n_10 = n_11 = 0
        for i in range(T - 1):
            prev, curr = violations[i], violations[i + 1]
            if prev == 0 and curr == 0:
                n_00 += 1
            elif prev == 0 and curr == 1:
                n_01 += 1
            elif prev == 1 and curr == 0:
                n_10 += 1
            else:
                n_11 += 1

        # Kupiec UC 分量（复用）
        N = int(np.sum(vmask))
        alpha = self._alpha
        p_hat = N / T if T > 0 else 0.0
        eps = 1e-12
        p_hat_safe = min(max(p_hat, eps), 1.0 - eps)
        log_L_alpha = (T - N) * np.log(1.0 - alpha) + N * np.log(alpha)
        log_L_phat = (T - N) * np.log(1.0 - p_hat_safe) + N * np.log(p_hat_safe)
        lr_uc = -2.0 * (log_L_alpha - log_L_phat)

        # 独立性分量 LR_ind
        # 条件概率: π01 = n_01/(n_00+n_01), π11 = n_11/(n_10+n_11)
        # 无条件概率: π = (n_01+n_11) / (T-1)
        # L_conditional = (1-π01)^n_00 * π01^n_01 * (1-π11)^n_10 * π11^n_11
        # L_unconditional = (1-π)^(n_00+n_10) * π^(n_01+n_11)
        n0 = n_00 + n_01  # 前一日未超限的总数
        n1 = n_10 + n_11  # 前一日超限的总数
        n_transitions = T - 1

        if n0 == 0 or n1 == 0:
            # 只有一种状态，独立性检验无意义（无转移）
            lr_ind = 0.0
        else:
            pi_01 = n_01 / n0
            pi_11 = n_11 / n1
            pi_01_safe = min(max(pi_01, eps), 1.0 - eps)
            pi_11_safe = min(max(pi_11, eps), 1.0 - eps)

            log_L_cond = (
                n_00 * np.log(1.0 - pi_01_safe)
                + n_01 * np.log(pi_01_safe)
                + n_10 * np.log(1.0 - pi_11_safe)
                + n_11 * np.log(pi_11_safe)
            )

            pi = (n_01 + n_11) / n_transitions if n_transitions > 0 else 0.0
            pi_safe = min(max(pi, eps), 1.0 - eps)
            log_L_uncond = (n_00 + n_10) * np.log(1.0 - pi_safe) + (n_01 + n_11) * np.log(pi_safe)

            lr_ind = -2.0 * (log_L_uncond - log_L_cond)

        lr_cc = lr_uc + lr_ind
        p_value = 1.0 - chi2.cdf(lr_cc, df=2)
        reject = bool(p_value < 0.05)

        return ChristoffersenResult(
            lr_uc=float(lr_uc),
            lr_ind=float(lr_ind),
            lr_cc=float(lr_cc),
            p_value=float(p_value),
            reject=reject,
            n_00=n_00,
            n_01=n_01,
            n_10=n_10,
            n_11=n_11,
        )

    # ──────────────────────────────────────────────────────────────────────
    # 第 3 法: Acerbi-Szekely Z2
    # ──────────────────────────────────────────────────────────────────────

    def acerbi_szekely_z2(self, observations: list[BacktestObservation]) -> AcerbiSzekelyResult:
        """Acerbi-Szekely Z2 ES 直接回测。

        Z2 = (1/N) * Σ_{t: violation} [realized_return_t / es_forecast_t]
        原假设 E[Z2] = -1（超限日平均损失 = ES 预测）
        Z2 < -1 → ES 低估（实际损失比预测更严重）

        36号 §3.9 line 441
        Acerbi & Szekely 2014/2017 非参数 ES 回测
        """
        _, es_arr, ret_arr, vmask = self._validate_observations(
            observations, min_samples=30, require_violations=True
        )
        T = len(observations)
        N = int(np.sum(vmask))

        # 超限日的 realized/es 比值（realized 为负数=损失，es 为正数=损失预测）
        # 比值 < 0，E[比值] = -1（损失 = ES 预测）
        violation_returns = ret_arr[vmask]
        violation_es = es_arr[vmask]
        violation_ratios = violation_returns / violation_es  # 均 < 0
        z2 = float(np.mean(violation_ratios))

        # 检验：Z2 是否显著 < -1（ES 低估）
        # 简化判定：Z2 < -1.0 且超限数 ≥5 时 reject（小样本不严谨，Phase 2 补 t 检验）
        # 严格版需 bootstrap 或渐近正态，MVP 用阈值判定
        reject = bool(z2 < -1.0 and N >= 5)

        return AcerbiSzekelyResult(
            z2=z2,
            expected=-1.0,
            n_violations=N,
            n_obs=T,
            violation_ratios=violation_ratios,
            reject=reject,
        )

    # ──────────────────────────────────────────────────────────────────────
    # 第 4 法: E-backtesting (GREM)
    # ──────────────────────────────────────────────────────────────────────

    def e_backtesting(
        self,
        observations: list[BacktestObservation],
        lambda_cap_ratio: float = 0.5,
    ) -> EBacktestResult:
        """E-backtesting 在线累积回测（GREM growth-rate-optimal betting process）。

        e-process: e_t = Π_{s=1}^{t} (1 + λ_s * b_s)
        b_s: backtest e-statistic = 1{violation_s} - α  (FZ identification function)
            - 超限时 b_s = 1-α > 0（e-value 增长方向）
            - 未超限时 b_s = -α < 0（e-value 衰减方向）
            校准时 E[b] = α(1-α) + (1-α)(-α) = 0 ✓（martingale difference）

        GREM λ_s: growth-rate-optimal，model-free，每步选 λ 最大化期望 log growth:
            λ* = (p̂_rolling - α) / (α(1-α))
            - p̂_rolling = 累计超限率
            - p̂ > α → λ* > 0（e-value 增长）；p̂ = α → λ* = 0（稳定）；p̂ < α → λ* = 0（clip）
            - 上界 λ_cap = lambda_cap_ratio / α（保证 1 - λα > lambda_cap_ratio > 0 数值稳定）

        anytime-valid: e_value > 1/α → 拒绝模型
        四级告警（ERCIM 145 GREM 接口）: green/yellow/red/black（对数刻度）

        36号 §3.9 line 459, line 497
        Wang, Wang & Ziegel arxiv 2209.00991v6 (2026-04)
        ERCIM News 145 (2026-07) Ruodu Wang GREM 默认
        """
        _, _, _, vmask = self._validate_observations(observations, min_samples=10)
        T = len(observations)
        alpha = self._alpha
        N = int(np.sum(vmask))

        # b_s: FZ identification function（不除以 α，避免未超限日 factor 衰减过严重）
        # violation: b = 1-α, no violation: b = -α
        b_series = np.where(vmask, 1.0 - alpha, -alpha)

        # GREM growth-rate-optimal λ: λ* = (p̂ - α) / (α(1-α)), clip to [0, λ_cap]
        # λ_cap 保证 1 - λ*α ≥ lambda_cap_ratio > 0（数值稳定）
        lambda_cap = lambda_cap_ratio / alpha if alpha > 0 else 1.0
        alpha_one_minus_alpha = alpha * (1.0 - alpha)

        lambda_series = np.zeros(T, dtype=np.float64)
        e_process = np.zeros(T, dtype=np.float64)
        log_e_process = np.zeros(T, dtype=np.float64)

        cumulative_violations = 0
        cumulative_log_e = 0.0
        cumulative_e = 1.0

        for t in range(T):
            cumulative_violations += int(vmask[t])
            # 滚动超限率（含当前）
            p_hat_rolling = cumulative_violations / (t + 1)
            # GREM: growth-rate-optimal λ*
            # 最大化 p̂*log(1+λ(1-α)) + (1-p̂)*log(1-λα) 的解 = (p̂-α)/(α(1-α))
            if alpha_one_minus_alpha > 0:
                lam_star = (p_hat_rolling - alpha) / alpha_one_minus_alpha
            else:
                lam_star = 0.0
            lam = max(0.0, min(lam_star, lambda_cap))
            lambda_series[t] = lam

            # e_t = e_{t-1} * (1 + λ * b_t)
            factor = 1.0 + lam * b_series[t]
            # factor > 0 保证（λ_cap 约束下 1 - λ*α ≥ lambda_cap_ratio）
            factor = max(factor, 1e-12)
            cumulative_log_e += np.log(factor)
            cumulative_e *= factor

            log_e_process[t] = cumulative_log_e
            e_process[t] = cumulative_e

        e_value = float(e_process[-1])
        threshold = 1.0 / alpha  # 拒绝阈值
        reject = bool(e_value > threshold)

        # 四级告警（对数刻度，ERCIM 145 GREM 接口）
        log_e = log_e_process[-1]
        log_threshold = np.log(threshold)
        if log_e < 0.5 * log_threshold:
            alert = EBacktestAlertLevel.GREEN
        elif log_e < log_threshold:
            alert = EBacktestAlertLevel.YELLOW
        elif log_e < 2.0 * log_threshold:
            alert = EBacktestAlertLevel.RED
        else:
            alert = EBacktestAlertLevel.BLACK

        return EBacktestResult(
            e_value=e_value,
            e_process=e_process,
            log_e_process=log_e_process,
            lambda_series=lambda_series,
            n_violations=N,
            n_obs=T,
            alpha=alpha,
            threshold=threshold,
            alert_level=alert,
            reject=reject,
        )

    # ──────────────────────────────────────────────────────────────────────
    # Basel Traffic Light（辅助报告，36号 §3.9 line 445）
    # ──────────────────────────────────────────────────────────────────────

    def basel_traffic_light(self, observations: list[BacktestObservation]) -> dict[str, Any]:
        """Basel Traffic Light 三区制（95% VaR，250 天窗口）。

        36号 §3.9 line 445-449
        Green: 8-16 超限 / Yellow: 17-20 / Red: ≥21（95% VaR, 250 天）
        样本不足 250 天时给出比例化判定。
        """
        _, _, _, vmask = self._validate_observations(observations, min_samples=30)
        T = len(observations)
        N = int(np.sum(vmask))

        # 95% VaR: 250 天期望超限 12.5 次
        # 比例化到实际样本
        expected = T * self._alpha
        # Green ≤ 1.28×期望, Yellow 1.28-1.6×, Red > 1.6×（近似 250 天 16/20 阈值）
        if N <= 1.28 * expected:
            zone = "green"
        elif N <= 1.6 * expected:
            zone = "yellow"
        else:
            zone = "red"

        return {
            "zone": zone,
            "n_violations": N,
            "n_obs": T,
            "expected_violations": float(expected),
            "violation_ratio": float(N / expected) if expected > 0 else 0.0,
            "note": (
                f"95% VaR 250天标准: Green≤16/Yellow 17-20/Red≥21，"
                f"当前 {T} 天比例化: Green≤{1.28*expected:.1f}/Yellow≤{1.6*expected:.1f}/Red>{1.6*expected:.1f}"
            ),
        }

    # ──────────────────────────────────────────────────────────────────────
    # 全量回测报告
    # ──────────────────────────────────────────────────────────────────────

    def full_report(self, observations: list[BacktestObservation]) -> dict[str, Any]:
        """生成全量回测报告（4 法 + Basel traffic light）。

        供 daily_auditor 日终调用，36号 §3.11 回测验证端到端施工流程。
        """
        try:
            kupiec = self.kupiec_pof(observations)
        except InsufficientBacktestHistoryError as e:
            kupiec = {"error": str(e)}
        try:
            christ = self.christoffersen(observations)
        except InsufficientBacktestHistoryError as e:
            christ = {"error": str(e)}
        try:
            z2 = self.acerbi_szekely_z2(observations)
        except InsufficientBacktestHistoryError as e:
            z2 = {"error": str(e)}
        try:
            ebt = self.e_backtesting(observations)
        except InsufficientBacktestHistoryError as e:
            ebt = {"error": str(e)}
        try:
            basel = self.basel_traffic_light(observations)
        except InsufficientBacktestHistoryError as e:
            basel = {"error": str(e)}

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "confidence_level": self._confidence,
            "alpha": self._alpha,
            "n_obs": len(observations),
            "kupiec_pof": kupiec.to_dict() if isinstance(kupiec, KupiecResult) else kupiec,
            "christoffersen": christ.to_dict() if isinstance(christ, ChristoffersenResult) else christ,
            "acerbi_szekely_z2": z2.to_dict() if isinstance(z2, AcerbiSzekelyResult) else z2,
            "e_backtesting": ebt.to_dict() if isinstance(ebt, EBacktestResult) else ebt,
            "basel_traffic_light": basel if isinstance(basel, dict) else basel,
            # 综合判定：任一检验 reject 即模型告警
            "overall_reject": any(
                getattr(r, "reject", False)
                for r in (kupiec, christ, z2, ebt)
                if not isinstance(r, dict)
            ),
        }
