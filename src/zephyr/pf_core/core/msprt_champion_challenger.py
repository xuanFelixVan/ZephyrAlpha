# [BLUEPRINT] MOD-PF-008 | docs/03_modules/_domain_portfolio_core/msprt_champion_challenger/blueprint.md
# [MODULE] zephyr.pf_core.core.msprt_champion_challenger
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] numpy
# [CONSUMERS] 晋升编排层(未建,BM-MT-02 通道统计内核)
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] threshold==1/alpha 且 lower_boundary==alpha;log_m 轨迹增量望远镜求和恒等;σ 仅用最近 window_size 笔;窗满(n>=window_size)前不终局判定
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError(alpha/tau/window_size 参数非法)
# [TESTS] tests/pf_core/test_msprt_champion_challenger.py
# [A_module] module_id=MOD-PF-008 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
mSPRT Champion-Challenger — 序贯晋升统计组件 (MOD-PF-008)

61 号 design memo §3.3 纪律 1 施工（BM-MT-02 Champion-Challenger 晋升通道统计内核）。
H0: δ ≤ 0（Challenger 无改善） vs H1: δ > 0（有改善）；混合先验 = 0 点质量 + N(0, τ²)。
逐笔累加高斯 mixture 闭式边际似然比（e-process），Ville 不等式保证 anytime-valid：
P(sup_n M_n ≥ 1/α) ≤ α 在所有停时成立，可任意频次查看无"偷看惩罚"。

核心三要素（memo）：
    1. 似然比累加：log M_n = ½·log(σ²/(σ²+nτ²)) + n²τ²x̄²/(2σ²(σ²+nτ²))，
       逐步累加 log（与累乘 M_n = ∏E_i 等价），轨迹全程留痕。
    2. tau 标定：历史 OOS 效应量 std（≥5 点），冷启动 <5 点兜底 0.2，
       下限 max(τ, 0.1·median) 防退化为固定效应 SPRT。
    3. 边界判定：M ≥ 1/α = 20 且 x̄>0 → 晋升；M ≥ 20 且 x̄<0 → 淘汰；
       n ≥ 30 且 M ≤ α = 0.05 → 淘汰（无效应证据）；否则维持 Champion（默认动作）。

裁定留痕（memo 歧义 → 统计第一性原理，蓝图 §3.2 同步）：
    1. memo 伪代码 lr 公式维度不一致（n→∞ 时 M 永不越界）→ 采用 Johari et al. 2022
       标准闭式形（H1 下 log M ≈ nδ²/2σ² 线性增长，H0 下 -½·log n 衰减）。
    2. memo 的 max_sample_size 未定义（属性从未赋值）；且 n<30 时 30 笔滚动 σ 未满窗，
       2-3 笔的插值 σ 可使指数爆炸（实证：δ=+0.5σ 合成序列 n=2 即误晋升）→ 终局判定
       （晋升/淘汰）最小样本 := window_size（30），窗满前一律 RETAIN。对齐 memo §3.3
       纪律 2"至少 30-50 笔影子交易才具备统计意义"（SR 26-02 金融业 4-12 周并行验证）。
    3. 统计量含 x̄²（双侧）而假设为单侧 → 决策层符号门控，防止"显著为负"误判晋升。

x̄ = 全历史 delta 均值（memo）；σ = 最近 30 笔滚动窗标准差（ddof=0，下限 1e-6，memo）。
delta 提取契约接口 ChampionChallengerDeltaExtractor 为 Protocol 预留对接位——
ExecutionReport 契约（BM-REC-02-B）建成前 delta 为合成/外部计算源，本组件不实现提取。

依据: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/61_lifecycle_multi_ai.md §3.3
SSoT: depgraph MOD-PF-008
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: alpha 参数
#   fields: 参数 alpha（无注解）
#   code: msprt_champion_challenger.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: tau 参数
#   fields: 参数 tau（无注解）
#   code: msprt_champion_challenger.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: historical_effects 参数
#   fields: 参数 historical_effects（无注解）
#   code: msprt_champion_challenger.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: window_size 参数
#   fields: 参数 window_size（无注解）
#   code: msprt_champion_challenger.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ChampionChallengerDeltaExtractor
#   name_en: ChampionChallengerDeltaExtractor
#   intro: delta 提取契约接口——ExecutionReport 对接位（BM-REC-02-B 阻塞，不实现）。
#   desc: delta 提取契约接口——ExecutionReport 对接位（BM-REC-02-B 阻塞，不实现）。 未来由 champion/challenger 配对的 Execut…；公共方法（定义序）: extract…
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② MSPRTChampionChallenger
#   name_en: MSPRTChampionChallenger
#   intro: mSPRT Champion-Challenger 序贯晋升（Johari et al. 2022 高斯 mixtur…
#   desc: mSPRT Champion-Challenger 序贯晋升（Johari et al. 2022 高斯 mixture 闭式解）。 alpha: Type I 错误率上限（SR…；公共方法（定义序）: calibra…
#   inputs: alpha tau historical_effects window_size
#   outputs: 返回值
#   （注：A2 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: ChampionChallengerDeltaExtractor, MSPRTChampionChallenger
#   downstream: 晋升编排层(未建,BM-MT-02 通道统计内核)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Protocol, Sequence, runtime_checkable

import numpy as np

logger = logging.getLogger(__name__)

__all__ = [
    "ChampionChallengerDecision",
    "ChampionChallengerDeltaExtractor",
    "MSPRTChampionChallenger",
    "MSPRTStepResult",
]


class ChampionChallengerDecision(str, Enum):
    """Champion-Challenger 序贯判定三态（晋升/维持/淘汰）。"""

    PROMOTE_CHALLENGER = "PROMOTE_CHALLENGER"
    RETAIN_CHAMPION = "RETAIN_CHAMPION"
    ELIMINATE_CHALLENGER = "ELIMINATE_CHALLENGER"

    @property
    def is_terminal(self) -> bool:
        """晋升/淘汰为终局判定（序贯实验停止）；维持=证据不足继续观察。"""
        return self is not ChampionChallengerDecision.RETAIN_CHAMPION


@dataclass(frozen=True)
class MSPRTStepResult:
    """单步判定结果（似然比轨迹步）。

    log_lr_increment: 当步对数似然比增量（Δlog M_n = log M_n − log M_{n−1}）。
    log_m: 累计对数边际似然比（= Σ log_lr_increment，望远镜求和恒等）。
    m: e-value M_n = exp(log_m)；log_m 超双精度指数上限时为 inf。
    """

    n: int
    delta: float
    mean_delta: float
    sigma: float
    log_lr_increment: float
    log_m: float
    m: float
    decision: ChampionChallengerDecision


@runtime_checkable
class ChampionChallengerDeltaExtractor(Protocol):
    """delta 提取契约接口——ExecutionReport 对接位（BM-REC-02-B 阻塞，不实现）。

    未来由 champion/challenger 配对的 ExecutionReport（同标的同窗口成交回报）
    提取逐笔 delta = challenger_pnl − champion_pnl。契约建成前 delta 为
    合成/外部计算源，组件仅消费已计算的 float 序列。
    """

    def extract_delta(self, champion_report: object, challenger_report: object) -> float:
        """从配对成交回报提取逐笔收益差（预留签名，组件内不调用）。"""
        ...


class MSPRTChampionChallenger:
    """mSPRT Champion-Challenger 序贯晋升（Johari et al. 2022 高斯 mixture 闭式解）。

    alpha: Type I 错误率上限（SR 26-2 频率学派偏好，默认 0.05）。
    tau: 混合先验宽度（历史 OOS 效应量标定）；显式传入 > historical_effects 标定 > 冷启动 0.2。
    window_size: σ 滚动窗口（memo 30 笔语义）。
    """

    _SIGMA_FLOOR = 1e-6
    _COLD_START_TAU = 0.2
    _MIN_HISTORY_FOR_CALIBRATION = 5

    def __init__(
        self,
        *,
        alpha: float = 0.05,
        tau: float | None = None,
        historical_effects: Sequence[float] | None = None,
        window_size: int = 30,
    ) -> None:
        if not 0.0 < alpha < 1.0:
            raise ValueError(f"alpha 必须在 (0, 1) 区间内: {alpha}")
        if window_size < 2:
            raise ValueError(f"window_size 必须 ≥ 2（方差可估）: {window_size}")
        self.alpha = float(alpha)
        self.threshold = 1.0 / self.alpha  # Ville 不等式边界（α=0.05 → 20）
        self.lower_boundary = self.alpha  # 接受 H0 边界 = 1/threshold（α=0.05 → 0.05）
        self.window_size = int(window_size)
        if tau is not None:
            if tau <= 0.0:
                raise ValueError(f"tau 必须 > 0（mixture 先验宽度）: {tau}")
            self.tau = float(tau)
        elif historical_effects is not None:
            self.tau = self.calibrate_tau(historical_effects)
        else:
            self.tau = self._COLD_START_TAU

        self.n = 0  # 已观测交易笔数
        self.log_m = 0.0  # test martingale log 初始化（M_0 = 1，E_{H0}[E] ≤ 1）
        self.delta_history: list[float] = []  # 增量收益差序列（Challenger − Champion）
        self.trajectory: list[MSPRTStepResult] = []

    @staticmethod
    def calibrate_tau(historical_effects: Sequence[float]) -> float:
        """tau 标定流程（一次性，部署前完成）——memo 警告"tau 标定错误会严重失效"。

        ≥5 个历史 OOS 效应量取 std（ddof=0，同 memo np.std）；
        下限保护 max(τ, 0.1·median)——tau 过小退化为固定效应 SPRT，失去 mixture 任意时刻有效性；
        冷启动（<5 点）兜底 0.2。
        """
        effects = [float(e) for e in historical_effects]
        if len(effects) < MSPRTChampionChallenger._MIN_HISTORY_FOR_CALIBRATION:
            return MSPRTChampionChallenger._COLD_START_TAU
        tau = float(np.std(effects))  # mixture 先验宽度对齐历史效应分布
        return max(tau, 0.1 * float(np.median(effects)))

    @property
    def window_deltas(self) -> list[float]:
        """最近 window_size 笔 delta（滚动窗，σ 估计口径）。"""
        return self.delta_history[-self.window_size :]

    @property
    def m(self) -> float:
        """当前 e-value M_n = exp(log_m)（log_m ≥ 709 时返回 inf 防溢出）。"""
        return math.exp(self.log_m) if self.log_m < 709.0 else math.inf

    def update(self, delta: float) -> MSPRTStepResult:
        """每笔交易后更新（anytime-valid，可任意频次查看无偷看惩罚）。

        delta = challenger_pnl − champion_pnl（由调用方/DeltaExtractor 契约计算）。
        """
        delta = float(delta)
        self.n += 1
        self.delta_history.append(delta)

        sigma = max(float(np.std(self.window_deltas)), self._SIGMA_FLOOR)  # 滚动波动率（30 笔窗口）
        mean_delta = float(np.mean(self.delta_history))

        log_m_new = self._log_marginal_likelihood_ratio(self.n, mean_delta, sigma)
        log_lr_increment = log_m_new - self.log_m  # 逐步累加 log（与累乘 E_i 等价）
        self.log_m = log_m_new
        m = self.m
        decision = self._decide(mean_delta, m)

        step = MSPRTStepResult(
            n=self.n,
            delta=delta,
            mean_delta=mean_delta,
            sigma=sigma,
            log_lr_increment=log_lr_increment,
            log_m=self.log_m,
            m=m,
            decision=decision,
        )
        self.trajectory.append(step)
        if decision is ChampionChallengerDecision.PROMOTE_CHALLENGER:
            logger.info("mSPRT 晋升 Challenger: n=%d, M=%.3f ≥ %.1f", self.n, m, self.threshold)
        elif decision is ChampionChallengerDecision.ELIMINATE_CHALLENGER:
            logger.info("mSPRT 淘汰 Challenger: n=%d, M=%.3f, mean_delta=%.6f", self.n, m, mean_delta)
        return step

    def evaluate(self, deltas: Iterable[float]) -> MSPRTStepResult:
        """批量馈入 delta 序列；达终局判定（晋升/淘汰）即早停——序贯检验核心语义。

        空序列 → n=0 / M=1.0 / RETAIN_CHAMPION（证据不足默认保留 Champion）。
        序列耗尽仍未越界 → 返回末步（RETAIN_CHAMPION，继续观察）。
        """
        for delta in deltas:
            step = self.update(delta)
            if step.decision.is_terminal:
                return step
        if self.trajectory:
            return self.trajectory[-1]
        return MSPRTStepResult(
            n=0,
            delta=0.0,
            mean_delta=0.0,
            sigma=0.0,
            log_lr_increment=0.0,
            log_m=0.0,
            m=1.0,
            decision=ChampionChallengerDecision.RETAIN_CHAMPION,
        )

    def _log_marginal_likelihood_ratio(self, n: int, mean_delta: float, sigma: float) -> float:
        """高斯 mixture 闭式边际似然比 log M_n（Johari et al. 2022 标准形）。

        H0: δ = 0（点质量） vs H1: δ ~ N(0, τ²)；x̄ | δ ~ N(δ, σ²/n)。
        log M_n = ½·log(σ²/(σ²+nτ²)) + n²τ²x̄² / (2σ²(σ²+nτ²))
        H1 下 ≈ nδ²/(2σ²) 线性增长；H0 下 -½·log n 衰减 + χ²₁/2 波动（Ville 限界 sup 越界概率 ≤ α）。
        """
        var = sigma * sigma
        tau2 = self.tau * self.tau
        log_prefactor = 0.5 * math.log(var / (var + n * tau2))
        exponent = (n * n * tau2 * mean_delta * mean_delta) / (2.0 * var * (var + n * tau2))
        return log_prefactor + exponent

    def _decide(self, mean_delta: float, m: float) -> ChampionChallengerDecision:
        """边界判定（Ville anytime-valid）+ 单侧符号门控 + 满窗最小样本门（裁定 2/3）。"""
        if self.n < self.window_size:
            return ChampionChallengerDecision.RETAIN_CHAMPION  # 窗不满不终局判定（裁定 2）
        if m >= self.threshold:  # M ≥ 1/α → 拒绝 H0
            if mean_delta > 0.0:
                return ChampionChallengerDecision.PROMOTE_CHALLENGER  # 显著改善 → 晋升
            if mean_delta < 0.0:
                return ChampionChallengerDecision.ELIMINATE_CHALLENGER  # 显著有害 → 淘汰
            return ChampionChallengerDecision.RETAIN_CHAMPION  # x̄=0 无方向，不判定
        if m <= self.lower_boundary:
            return ChampionChallengerDecision.ELIMINATE_CHALLENGER  # 满窗无效应证据 → 淘汰
        return ChampionChallengerDecision.RETAIN_CHAMPION  # 证据不足默认保留 Champion
