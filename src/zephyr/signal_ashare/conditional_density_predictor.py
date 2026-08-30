# [BLUEPRINT] MOD-SIG-043 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/91_density_prediction.md §1
# [MODULE] zephyr.signal_ashare.conditional_density_predictor
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] numpy
# [CONSUMERS] zephyr.signal_ashare.fine_scoring_engine（密度要素摘要）; zephyr.signal_ashare.conformal_predictor（PDF 分位数输入）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 分位数网格单调不减；VaR/CVaR 为负值口径（亏损为负）；条件桶样本不足 → 回退全样本 degraded=True；仅用传入历史序列无未来函数
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 输入长度 <2 → ValueError；空条件桶不回退时报头由 predict 统一兜底
# [TESTS] tests/signal_ashare/test_conditional_density_predictor.py
# [A_module] module_id=MOD-SIG-043 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: 历史收益率序列 + 平行条件标签（波动率分桶/regime 标签，可空）
# A1: 条件分桶——按条件值分组，组内 trailing window 经验分布
# A2: 矩估计——均值/标准差/偏度/超额峰度（Fisher）+ 经验分位数网格 P1/P5/P25/P50/P75/P95/P99
# A3: 尾部派生——VaR95（5% 分位）/CVaR95（≤VaR 的均值）/前瞻VaR%/负偏度/超额峰度摘要
# O1: DensityForecast（矩+分位数+尾部+样本数+degraded）；crps_empirical 评估件
# [/ALGO_FLOW]
"""
收益率条件密度预测（BM-SEL-13，MOD-SIG-043）。

不只预测"明天涨多少"，而是预测明天收益率的完整概率分布——偏多少、尾巴多厚、
极端情况多罕见（偏度/峰度/VaR/CVaR/P1~P99 分位数网格）。

轻量实现裁定（91 号 memo：单一路线收敛，轻量密度头；禁重模型依赖）：
  条件经验分布法——按条件标签（波动率分桶/regime 状态）分组，组内取 trailing
  window 历史收益率的经验分布：矩估计 + 经验分位数 + 尾部 VaR/CVaR。条件桶样本
  不足 min_samples 时回退全样本（degraded=True，与 memo"未就绪→离散估计无分布
  增强"降级路径同构）。

下游契约：BM-SEL-18 精筛密度要素（neg_skewness/excess_kurtosis/forward_var_pct
三属性鸭子类型摘要，见 density_summary()）；BM-SEL-14 共形预测消费 PDF 分位数。
评估：CRPS 为核心指标（91 号原始内容），crps_empirical 提供经验分布闭式实现。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: returns 参数
#   fields: 参数 returns，类型注解 Iterable[float]
#   code: conditional_density_predictor.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: conditions 参数
#   fields: 参数 conditions，类型注解 Sequence[str] | None
#   code: conditional_density_predictor.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: condition 参数
#   fields: 参数 condition（无注解）
#   code: conditional_density_predictor.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: conditional_density_predictor.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① DensityForecast
#   name_en: DensityForecast
#   intro: 条件密度预测输出。
#   desc: 条件密度预测输出。；公共方法（定义序）: density_summary；源码 L150-L170
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② conditional_density
#   name_en: conditional_density
#   intro: 条件密度预测主入口。
#   desc: 条件密度预测主入口。 Args: returns: 历史收益率序列（trailing 截 window） conditions: 与 returns 平行的条件标签序列（如波动率…；源码 L209-L250
#   inputs: returns conditions condition config
#   outputs: DensityForecast
# - id: A3
#   name_zh: ③ crps_empirical
#   name_en: crps_empirical
#   intro: 经验分布 CRPS（连续分级概率评分，越小越好）。
#   desc: 经验分布 CRPS（连续分级概率评分，越小越好）。 CRPS = E|X−y| − 0.5·E|X−X'|（经验分布闭式，X/X' 为样本独立抽样）。 样本均值绝对偏差项 O(n…；源码 L253-L267
#   inputs: samples actual
#   outputs: float
#   （注：A3 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: DensityForecast
#   name_en: DensityForecast
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.signal_ashare.fine_scoring_engine（密度要素摘要）; zephyr.signal_ashare.conforma…
# - id: O2
#   name_zh: float
#   name_en: float
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.signal_ashare.fine_scoring_engine（密度要素摘要）; zephyr.signal_ashare.conforma…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final, Iterable, Sequence

import numpy as np

__all__: Final = [
    "ConditionalDensityConfig",
    "DensityForecast",
    "DensitySummary",
    "conditional_density",
    "crps_empirical",
]

#: 默认经验分位数网格（P1~P99 七点，覆盖 BM-SEL-13 派生量所需尾部/中位）
_DEFAULT_QUANTILES: Final = (0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99)


@dataclass(frozen=True)
class ConditionalDensityConfig:
    """条件密度配置。

    Attributes:
        window: trailing 窗口长度（只用最近 window 个样本）
        min_samples: 条件桶最小样本数（不足回退全样本 degraded）
        quantiles: 经验分位数网格（0-1 小数，单调递增）
        var_level: VaR/CVaR 置信水平（默认 0.95 → 5% 尾）
    """

    window: int = 250
    min_samples: int = 60
    quantiles: tuple[float, ...] = _DEFAULT_QUANTILES
    var_level: float = 0.95


@dataclass(frozen=True)
class DensitySummary:
    """密度要素摘要（BM-SEL-18 精筛扣分项输入，鸭子类型契约三属性）。"""

    neg_skewness: float  # 负偏度幅度 max(0, −skew)
    excess_kurtosis: float  # 超额峰度 max(0, kurtosis−3)
    forward_var_pct: float  # 前瞻 VaR 幅度 %（正数=亏损幅度）


@dataclass(frozen=True)
class DensityForecast:
    """条件密度预测输出。"""

    condition: str  # 条件桶标签（无条件时 "ALL"）
    n_samples: int
    mean: float
    std: float
    skewness: float
    excess_kurtosis: float  # Fisher 超额峰度（正态=0）
    quantiles: dict[float, float] = field(default_factory=dict)  # {分位水平: 分位值}
    var_95: float = 0.0  # VaR（负值=亏损）
    cvar_95: float = 0.0  # CVaR/ES（≤VaR 样本均值，负值=亏损）
    degraded: bool = False  # True=条件桶样本不足，回退全样本

    def density_summary(self) -> DensitySummary:
        """BM-SEL-18 密度要素摘要（负偏度/超额峰度/前瞻 VaR%）。"""
        return DensitySummary(
            neg_skewness=max(0.0, -self.skewness),
            excess_kurtosis=max(0.0, self.excess_kurtosis),
            forward_var_pct=abs(self.var_95) * 100.0,
        )


def _moments(samples: np.ndarray) -> tuple[float, float, float, float]:
    """均值/标准差/偏度/超额峰度（Fisher）。常数序列偏度峰度按 0。"""
    mean = float(samples.mean())
    std = float(samples.std())
    if std < 1e-12:
        return mean, 0.0, 0.0, 0.0
    z = (samples - mean) / std
    skew = float((z**3).mean())
    excess_kurt = float((z**4).mean() - 3.0)
    return mean, std, skew, excess_kurt


def _forecast_from_samples(
    samples: np.ndarray, *, condition: str, cfg: ConditionalDensityConfig, degraded: bool
) -> DensityForecast:
    """从经验样本构造 DensityForecast（矩 + 分位数网格 + VaR/CVaR）。"""
    mean, std, skew, excess_kurt = _moments(samples)
    qs = {p: float(np.quantile(samples, p)) for p in cfg.quantiles}
    tail_p = 1.0 - cfg.var_level
    var = float(np.quantile(samples, tail_p))
    tail = samples[samples <= var]
    cvar = float(tail.mean()) if len(tail) > 0 else var
    return DensityForecast(
        condition=condition,
        n_samples=int(len(samples)),
        mean=mean,
        std=std,
        skewness=skew,
        excess_kurtosis=excess_kurt,
        quantiles=qs,
        var_95=var,
        cvar_95=cvar,
        degraded=degraded,
    )


def conditional_density(
    returns: Iterable[float],
    conditions: Sequence[str] | None = None,
    *,
    condition: str | None = None,
    config: ConditionalDensityConfig | None = None,
) -> DensityForecast:
    """条件密度预测主入口。

    Args:
        returns: 历史收益率序列（trailing 截 window）
        conditions: 与 returns 平行的条件标签序列（如波动率桶 "LOW"/"HIGH"）；
            None → 无条件全样本密度
        condition: 目标条件值；conditions 提供时必填——输出该条件桶的密度；
            桶样本 < min_samples → 回退全样本（degraded=True）
        config: 配置（None → 默认）

    Returns:
        DensityForecast

    Raises:
        ValueError: 样本长度 <2；conditions 与 returns 长度不一致；
            conditions 提供但 condition 未指定。
    """
    cfg = config or ConditionalDensityConfig()
    r_list = list(returns)
    if len(r_list) < 2:
        raise ValueError(f"收益率样本长度不足: {len(r_list)} < 2")
    r = np.asarray(r_list, dtype=float)[-cfg.window :]
    if conditions is None:
        return _forecast_from_samples(r, condition="ALL", cfg=cfg, degraded=False)
    c = list(conditions)
    if len(c) != len(r_list):
        raise ValueError(f"conditions 与 returns 长度不一致: {len(c)} vs {len(r_list)}")
    if condition is None:
        raise ValueError("conditions 提供时 condition 必填（目标条件桶）")
    c = c[-cfg.window :]
    mask = np.asarray([x == condition for x in c])
    bucket = r[mask]
    if len(bucket) >= cfg.min_samples:
        return _forecast_from_samples(bucket, condition=condition, cfg=cfg, degraded=False)
    return _forecast_from_samples(r, condition=condition, cfg=cfg, degraded=True)


def crps_empirical(samples: Iterable[float], actual: float) -> float:
    """经验分布 CRPS（连续分级概率评分，越小越好）。

    CRPS = E|X−y| − 0.5·E|X−X'|（经验分布闭式，X/X' 为样本独立抽样）。
    样本均值绝对偏差项 O(n)，两两差项 O(n²)——trailing window ≤250 下开销可忽略。

    Raises:
        ValueError: 空样本。
    """
    s = np.asarray(list(samples), dtype=float)
    if len(s) == 0:
        raise ValueError("CRPS 样本为空")
    term1 = float(np.abs(s - actual).mean())
    pairwise = np.abs(s[:, None] - s[None, :]).mean()
    return term1 - 0.5 * float(pairwise)
