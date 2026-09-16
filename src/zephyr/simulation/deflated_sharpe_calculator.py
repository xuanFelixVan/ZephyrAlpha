# [BLUEPRINT] MOD-SIM-024 | docs/03_modules/_domain_simulation/deflated_sharpe_calculator/blueprint.md
# [MODULE] zephyr.simulation.deflated_sharpe_calculator
# [DOMAIN] D_SIMULATION
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] zephyr.simulation.sharpe_calculator_fixer; zephyr.simulation.result_analyzer
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] DSRResult/DSRConfig/DSRTrendPoint frozen不可变; DSR∈[0,1](退化态恒=DSR_UNDECIDABLE=0.0 且 degenerate=True); 样本<3拒绝; num_trials<1拒绝; float计算非Decimal; 仅stdlib(math/statistics)无第三方依赖; 峰度入参全仓统一超额口径(正态=0),V[SR]内部转Pearson(+3)且唯一真源在本模块; 退化态fail-closed(不判显著+出声WARNING)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SimulationError(ZA-SIM-0024)
# [TESTS] tests/simulation/test_deflated_sharpe_calculator.py
# [A_module] module_id=MOD-SIM-024 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D_SIMULATION — Deflated Sharpe Ratio Calculator (DSR 计算器)

多重测试偏差修正的 Sharpe 比率。基于 Bailey & López de Prado (2014) 论文,
修正回测中"试了 N 次取最好"导致的 Sharpe 虚高。

属 A 类基础设施(确定性数学计算), 纯基础层不涉及策略。

设计真源: depgraph MOD-SIM-024
蓝图: docs/03_modules/_domain_simulation/deflated_sharpe_calculator/blueprint.md

## 全仓 DSR 唯一真源（SDC-3/SDC-4 施工，2026-09-17）

同族三处算 DSR（本件 = 活件 SSOT / `backtest.core.overfitting_adjudicator` /
`backtest.core.metrics.calculate_full_metrics`）。口径分叉是已知病，故 V[SR]、
E[max(Z_N)]、退化判定三者一律以本模块公共函数为准，他处只准委托不准另写公式：

- **峰度口径（SDC-3）**：`variance_of_sharpe` 的 SR² 项按 Lo(2002)/Harvey-Liu-Zhu /
  Bailey & López de Prado(2014) 原式要求 **Pearson 峰度**（正态=3），而全仓入参统一
  **超额峰度**（正态=0）⇒ 内部恒 `+3` 转换。iid 正态边界须回落到
  `V=(1+SR²/2)/(T−1)`（该边界即本口径的机检锚点）。
- **E[max(Z_N)]（同族口径）**：用论文闭式 `(1−γ)Φ⁻¹(1−1/N)+γΦ⁻¹(1−1/(N·e))`。
  原 Euler–Maclaurin 式是 N→∞ 渐近展开，被用在 N=2 这类小样本上会**超折减**
  （实测 N=2 偏 +0.283 个 z 单位，真值 1/√π=0.5642），故一并治。
- **退化态（SDC-4）**：V[SR] 非正/NaN、收益零方差、矩不可估 ⇒ "没有信息"，
  绝不映射成"极显著"：`dsr=DSR_UNDECIDABLE` + `degenerate=True` + 出声 WARNING。

# [ALGO_FLOW] external: docs/03_modules/_domain_simulation/algo_flow/deflated_sharpe_calculator.yaml
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from statistics import NormalDist

from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)
_norm_std = NormalDist()


class SimulationError(ZephyrBaseError):
    """仿真计算异常——输入非法(空序列/样本不足/试次数非法)。"""

    error_code = "ZA-SIM-0024"


# #14 裁定（2026-08-20）：DSR 阈值常量唯一真源（SSoT）——分级语义对齐社区惯例：
# 显著性放行线 0.95（类比 p<0.05）；运气中值否决线 0.5（低于此=无超出运气的证据）。
# 消费方：本模块 DSRConfig 默认值 / backtest.core.metrics.calculate_full_metrics is_overfitting。
DSR_SIGNIFICANCE_THRESHOLD = 0.95
DSR_OVERFITTING_FLOOR = 0.5

#: V[SR] 的 SR² 项要求 **Pearson 峰度**（正态=3），全仓入参统一为**超额峰度**（正态=0），
#: 故转换常数恒为 3.0（SDC-3 唯一真源）。机检锚点=Lo(2002) iid 正态边界
#: `V[SR]=(1+SR²/2)/(T−1)`：超额峰度 0 代入本常数 → SR² 系数 (3−1)/4=+1/2 ✓。
#: 曾因把超额峰度直接喂进该式，系数变成 (0−1)/4=−1/4（符号相反），iid 边界实测
#: 方差被砍半 → DSR 恒偏高（=缺陷 SDC-3）。改此常数=改全仓 DSR 口径，须走裁定。
KURTOSIS_PEARSON_NORMAL: float = 3.0

#: Euler–Mascheroni 常数 γ（Bailey & López de Prado 2014 E[max] 闭式系数；唯一真源在本模块）
EULER_MASCHERONI: float = 0.5772156649015329

#: 退化态（估计失效/无信息）下 DSR 的取值——Fail-Closed 地板（SDC-4）。
#: 语义不是"算出来不显著"而是"判不了"，故取最不利于放行的一侧：
#: 任何 threshold∈(0,1) 下 is_significant 恒 False；metrics 的
#: is_overfitting(dsr<0.5) 因此为 True → 阻断晋级。真判据读 DSRResult.degenerate。
DSR_UNDECIDABLE: float = 0.0

#: 矩可估样本下限：`_skewness` n<3、`_kurtosis` n<4 时返回 0.0 占位值——
#: "0 峰度"≠"无厚尾信息"而是"没算出来"，故 n<4 一律判退化（不是新阈值，
#: 是本文件既有可估性下限的直接推论）。
_MIN_OBS_FOR_MOMENTS: int = 4


@dataclass(frozen=True)
class DSRConfig:
    """DSR 配置——不可变。

    Attributes:
        significance_threshold: DSR 显著性阈值(默认 DSR_SIGNIFICANCE_THRESHOLD=0.95)
        periods_per_year: 年化频率(A股日度=252)
        risk_free_rate: 默认无风险利率(默认 0.0)
    """

    significance_threshold: float = DSR_SIGNIFICANCE_THRESHOLD
    periods_per_year: int = 252
    risk_free_rate: float = 0.0


@dataclass(frozen=True)
class DSRResult:
    """DSR 计算结果——不可变。

    Attributes:
        sharpe: 非年化 Sharpe 比率
        sharpe_annualized: 年化 Sharpe 比率
        dsr: Deflated Sharpe Ratio ∈ [0, 1]；degenerate=True 时恒为 DSR_UNDECIDABLE
        num_trials: 试次数 N
        num_obs: 样本数 T
        skewness: 收益率偏度 γ（正态=0）
        kurtosis: 收益率**超额**峰度 κ（正态=0；Pearson 口径=κ+3，转换在 V[SR] 内做）
        var_sr: Sharpe 估计量方差 V[SR]
        expected_max: 多重测试期望最大值 E[max(Z_N)]（z 单位，无量纲）
        is_significant: DSR 是否达到显著性阈值（退化态恒 False）
        degenerate: True=估计失效/无信息 ⇒ dsr 是"不可判定"而非"测得不显著"（SDC-4）
    """

    sharpe: float
    sharpe_annualized: float
    dsr: float
    num_trials: int
    num_obs: int
    skewness: float
    kurtosis: float
    var_sr: float
    expected_max: float
    is_significant: bool
    degenerate: bool = False


@dataclass(frozen=True)
class DSRTrendPoint:
    """DSR 趋势追踪点——不可变。

    Attributes:
        index: 滚动窗口结束位置
        dsr: 该窗口的 DSR 值
        sharpe: 该窗口的年化 Sharpe
    """

    index: int
    dsr: float
    sharpe: float


def _normal_cdf(x: float) -> float:
    """标准正态分布 CDF Φ(x), 使用 math.erf 实现。

    Φ(x) = 0.5 * (1 + erf(x / sqrt(2)))
    """
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _inverse_normal_cdf(p: float) -> float:
    """标准正态逆 CDF Φ⁻¹(p)（stdlib statistics.NormalDist，精度 ~1e-13）。

    Args:
        p: 概率，须落在开区间 (0, 1)

    Returns:
        x 使 Φ(x) = p

    Raises:
        SimulationError: p 越出 (0, 1)——Φ⁻¹ 在该定义域外无定义，不猜值。
    """
    if not (0.0 < p < 1.0):
        raise SimulationError(
            f"Φ⁻¹ 定义域为 (0,1): p={p}",
            details={"p": p},
        )
    return _norm_std.inv_cdf(p)


def _mean(values: list[float]) -> float:
    """算术均值。"""
    return sum(values) / len(values)


def _variance(values: list[float], ddof: int = 1) -> float:
    """样本方差(ddof=1 为无偏估计)。"""
    n = len(values)
    if n <= ddof:
        return 0.0
    m = _mean(values)
    return sum((v - m) ** 2 for v in values) / (n - ddof)


def _std(values: list[float], ddof: int = 1) -> float:
    """样本标准差。"""
    return math.sqrt(_variance(values, ddof))


def _skewness(values: list[float]) -> float:
    """样本偏度(Fisher-Pearson, 有偏估计)。

    γ = m3 / m2^(3/2)
    其中 mk = (1/n) * Σ(xi - mean)^k

    n<3 返回 0.0 是**占位值**（不是"测得对称"），消费方须按退化态处理。
    """
    n = len(values)
    if n < 3:
        return 0.0
    m = _mean(values)
    m2 = sum((v - m) ** 2 for v in values) / n
    m3 = sum((v - m) ** 3 for v in values) / n
    if m2 == 0:
        return 0.0
    return m3 / (m2**1.5)


def _kurtosis(values: list[float]) -> float:
    """样本峰度(**超额**峰度, excess kurtosis; 正态=0)。

    κ = m4 / m2² - 3

    全仓 DSR 入参统一用本口径；需要 Pearson 峰度（正态=3）的公式（V[SR]）
    自己做 +3 转换（见 `variance_of_sharpe`），两头口径不得各写各的（SDC-3）。
    n<4 返回 0.0 是**占位值**（不是"测得薄尾"），消费方须按退化态处理。
    """
    n = len(values)
    if n < 4:
        return 0.0
    m = _mean(values)
    m2 = sum((v - m) ** 2 for v in values) / n
    m4 = sum((v - m) ** 4 for v in values) / n
    if m2 == 0:
        return 0.0
    return m4 / (m2**2) - 3.0


def expected_max_sharpe_z(num_trials: int) -> float:
    """多重测试期望最大值 E[max(Z_N)]（全仓唯一真源）。

    论文闭式 (Bailey & López de Prado 2014；Harvey-Liu-Zhu 2021 同式)::

        E[max(Z_N)] ≈ (1−γ)·Φ⁻¹(1−1/N) + γ·Φ⁻¹(1−1/(N·e)),  γ=Euler–Mascheroni

    N≤1: 0（无多重测试修正）

    原实现用 Euler–Maclaurin 渐近式 √(2lnN)−(lnπ+lnlnN)/(2√(2lnN))，该式只在
    N→∞ 收敛；实测对照精确积分值 E[max]=∫x·N·φ(x)·Φ(x)^{N−1}dx：
    N=2 偏 +0.283（真值 1/√π=0.5642，旧值 0.8469=超折减 50%）、N=10 偏 +0.146、
    N=4497 偏 +0.052 ⇒ 小 N 处系统性过度折减，与本模块另一侧的欠折减（SDC-3）
    在生产大 N 处部分对消，故历史数字"看着还行"但两头都不对。

    注意：本闭式**仍是近似**，不得当作精确值。同一精确积分对拍下本式偏差
    N=2 −0.0444、N=3 +0.0065、N=10 +0.0358、N=50 +0.0272、N=4497 +0.0103
    （绝对值 ≤0.045 个 z 单位，比被废弃的渐近式小 4~27 倍）。故测试用例按解析
    真值 + 容差对拍，禁止把断言改回"钉在本函数自身输出上"（同义反复，永不失败）。

    Args:
        num_trials: 试次数 N

    Returns:
        E[max(Z_N)]（z 单位，无量纲），随 N 单调不减
    """
    if num_trials <= 1:
        return 0.0
    n = float(num_trials)
    return (1.0 - EULER_MASCHERONI) * _inverse_normal_cdf(1.0 - 1.0 / n) + EULER_MASCHERONI * _inverse_normal_cdf(
        1.0 - 1.0 / (n * math.e)
    )


#: 向后兼容私有名（`scripts/backtest/dsr_recalc_backfill.py` 按此名导入）
_expected_max_sharpe = expected_max_sharpe_z


def variance_of_sharpe(sharpe: float, skewness: float, excess_kurtosis: float, num_obs: int) -> float:
    """Sharpe 估计量方差 V[SR]（非正态修正，全仓唯一真源）。

    Lo(2002) / Bailey & López de Prado (2014) 原式（**κ_p 为 Pearson 峰度**）::

        V[SR] = (1 − γ·SR + (κ_p − 1)/4 · SR²) / (T − 1)

    本模块入参口径是**超额**峰度（正态=0），故 κ_p = excess_kurtosis + 3，即
    SR² 系数 = (excess_kurtosis + 2)/4 —— 这一步 +3 转换就是 SDC-3 的病灶：
    旧码把超额峰度直接当 Pearson 用，iid 正态下系数取成 −1/4 而非 +1/2，
    方差被低估一半 ⇒ DSR 恒偏高（反保守）。

    口径自检锚点（iid 正态，γ=0，excess=0）：V[SR]=(1+SR²/2)/(T−1)。
    另注：由 Pearson 不等式 κ_p ≥ γ²+1 ⇒ excess ≥ γ²−2 ⇒ SR² 系数恒 ≥0，
    故本式在**互斥矩输入**（如 γ=3 而 excess=0）下才可能返回非正值。

    Args:
        sharpe: 非年化 Sharpe（每期）
        skewness: 偏度 γ（正态=0）
        excess_kurtosis: **超额**峰度 κ（正态=0）
        num_obs: 样本数 T

    Returns:
        V[SR]；T≤1 时无法估计，返回 0.0（由 `sharpe_variance_is_degenerate` 判退化）
    """
    if num_obs <= 1:
        return 0.0
    sr = float(sharpe)
    kurt_pearson = float(excess_kurtosis) + KURTOSIS_PEARSON_NORMAL
    var_term = 1.0 - float(skewness) * sr + (kurt_pearson - 1.0) / 4.0 * sr * sr
    return var_term / (num_obs - 1)


#: 向后兼容私有名（既有测试/外部按此名导入）
_variance_of_sharpe = variance_of_sharpe


def sharpe_variance_is_degenerate(var_sr: float) -> bool:
    """V[SR] 是否退化（True=方差估计失效 ⇒ DSR 不可判定）。

    判据写成 `not (var_sr > 0.0)` 而非 `var_sr <= 0`——后者对 NaN 恒 False，
    会把"不认识"误判成"不退化"。姿态对齐仓内既有范式
    （`ops_alert_feed._check_status`：不认识的条件下绝不触发）。
    """
    return not (var_sr > 0.0)


def deflated_sharpe_from_moments(
    sharpe: float,
    num_trials: int,
    num_obs: int,
    skewness: float = 0.0,
    excess_kurtosis: float = 0.0,
) -> tuple[float, float, float, bool]:
    """DSR 内核（全仓唯一真源，三处实现皆经此）：由矩算 DSR。

    ``DSR = Φ(SR/√V[SR] − E[max(Z_N)])``，V[SR] 与 E[max] 见各自函数。

    Fail-Closed（SDC-4）：V[SR] 非正/NaN 时**不出数**——返回
    ``dsr = DSR_UNDECIDABLE`` + ``degenerate = True`` 并出声 WARNING。
    旧行为 `1.0 if sr > 0 else 0.5` 把自己的估计失败翻译成"以 N 次试验折减
    口径仍极显著"，是假策略晋级的单点通道；占位值把"没有信息"伪装成结论，
    比报错更坏。

    Args:
        sharpe: 非年化 Sharpe（每期）
        num_trials: 试次数 N
        num_obs: 样本数 T
        skewness: 偏度 γ（正态=0）
        excess_kurtosis: **超额**峰度 κ（正态=0）

    Returns:
        (var_sr, dsr, expected_max_z, degenerate)
    """
    var_sr = variance_of_sharpe(sharpe, skewness, excess_kurtosis, num_obs)
    expected_max = expected_max_sharpe_z(num_trials)
    if sharpe_variance_is_degenerate(var_sr):
        _logger.warning(
            "DSR 退化态→不可判定: SR=%.6g γ=%.6g κ_超额=%.6g T=%d N=%d 的 V[SR]=%.6g "
            "非正(矩输入互斥/样本不足=估计失效)，按 Fail-Closed 置 dsr=%.1f 且不判显著"
            "（勿读作'测得不显著'，真判据见 degenerate）",
            sharpe,
            skewness,
            excess_kurtosis,
            num_obs,
            num_trials,
            var_sr,
            DSR_UNDECIDABLE,
        )
        return var_sr, DSR_UNDECIDABLE, expected_max, True
    z_stat = float(sharpe) / math.sqrt(var_sr) - expected_max
    return var_sr, _normal_cdf(z_stat), expected_max, False


def _return_side_degeneracy(std_ret: float, num_obs: int) -> str | None:
    """收益序列侧退化因由（None=可判）。

    `not (std_ret > 0.0)` 同时吃掉 0/负/NaN：零方差序列的样本 SR 本身就无定义
    （旧码把 rf 之后的均值除 0 保护成 sr=0.0，再往下走会得出 Φ(0−E[max]) 这种
    看着像结论的数——同样是把"没有信息"翻译成数字）。
    """
    if not (std_ret > 0.0):
        return "收益率标准差为 0/非法(样本 Sharpe 无定义)"
    if num_obs < _MIN_OBS_FOR_MOMENTS:
        return f"样本 {num_obs} < {_MIN_OBS_FOR_MOMENTS}(偏度/峰度取占位值 0.0，非测得薄尾)"
    return None


class DeflatedSharpeCalculator:
    """Deflated Sharpe Ratio 计算器。

    基于 Bailey & López de Prado (2014) 修正多重测试偏差。
    无第三方依赖（仅 stdlib math/statistics）, 确定性纯计算。

    Usage:
        calc = DeflatedSharpeCalculator(DSRConfig(periods_per_year=252))

        # 单次回测(无多重测试修正)
        result = calc.calculate(returns, num_trials=1)

        # 试了50次取最好的 Sharpe
        result = calc.calculate(returns, num_trials=50)
        print(result.dsr)           # DSR 值
        print(result.is_significant)  # 是否显著(>= 0.95)

        # 趋势追踪(滚动窗口)
        trend = calc.track_trend(returns, num_trials=50, window=60)
    """

    def __init__(self, config: DSRConfig | None = None) -> None:
        self._config = config if config is not None else DSRConfig()

    @property
    def config(self) -> DSRConfig:
        """配置(只读)。"""
        return self._config

    def calculate(
        self,
        returns: list[float],
        num_trials: int = 1,
        risk_free_rate: float | None = None,
    ) -> DSRResult:
        """计算 Deflated Sharpe Ratio。

        Args:
            returns: 收益率序列(每期收益率, 非年化)
            num_trials: 试次数 N(回测尝试了多少策略/参数组合), 默认 1
            risk_free_rate: 每期无风险利率, None=用 config 默认值

        Returns:
            DSRResult；退化态（V[SR] 非正/零方差/矩不可估）下
            degenerate=True、dsr=DSR_UNDECIDABLE(=0.0)、is_significant=False，
            并出声 WARNING——调用方须先读 degenerate 再读 dsr

        Raises:
            SimulationError: 空序列 / 样本不足(<3) / num_trials<1
        """
        if not returns:
            raise SimulationError("returns 不能为空")
        if len(returns) < 3:
            raise SimulationError(
                f"样本数不足: {len(returns)} < 3(无法计算偏度/峰度)",
                details={"num_obs": len(returns)},
            )
        if num_trials < 1:
            raise SimulationError(
                f"num_trials 不能 < 1: {num_trials}",
                details={"num_trials": num_trials},
            )

        rf = risk_free_rate if risk_free_rate is not None else self._config.risk_free_rate
        n = len(returns)

        # 1. 基本 Sharpe (非年化)
        mean_ret = _mean(returns)
        std_ret = _std(returns, ddof=1)
        if std_ret > 0.0:
            sr = (mean_ret - rf) / std_ret
        else:
            # 零/非法方差: 样本 SR 无定义, 报 0.0 仅为占位——序列侧退化见 _return_side_degeneracy
            sr = 0.0

        sr_annual = sr * math.sqrt(self._config.periods_per_year)

        # 2. 偏度/峰度（超额口径；不足样本时是占位值 0.0）
        gamma = _skewness(returns)
        kappa = _kurtosis(returns)

        # 3+4+5. DSR 内核（V[SR] + E[max(Z_N)] + DSR + 退化判定，全仓唯一真源）
        var_sr, dsr, expected_max, degenerate = deflated_sharpe_from_moments(
            sr,
            num_trials,
            n,
            skewness=gamma,
            excess_kurtosis=kappa,
        )

        # 6. 收益侧退化（标准差为 0/NaN、矩根本不可估）——同样不可判定，不用占位值出结论
        reason = _return_side_degeneracy(std_ret, n)
        if reason is not None:
            if not degenerate:
                _logger.warning(
                    "DSR 退化态→不可判定: %s (T=%d N=%d) → 置 dsr=%.1f 且不判显著"
                    "（degenerate=True，勿读作'测得不显著'）",
                    reason,
                    n,
                    num_trials,
                    DSR_UNDECIDABLE,
                )
            degenerate = True
            dsr = DSR_UNDECIDABLE

        is_significant = bool(not degenerate and dsr >= self._config.significance_threshold)

        result = DSRResult(
            sharpe=sr,
            sharpe_annualized=sr_annual,
            dsr=dsr,
            num_trials=num_trials,
            num_obs=n,
            skewness=gamma,
            kurtosis=kappa,
            var_sr=var_sr,
            expected_max=expected_max,
            is_significant=is_significant,
            degenerate=degenerate,
        )
        _logger.debug(
            "DSR计算: SR=%.4f SR_ann=%.4f DSR=%.4f N=%d T=%d significant=%s degenerate=%s",
            sr,
            sr_annual,
            dsr,
            num_trials,
            n,
            is_significant,
            degenerate,
        )
        return result

    def track_trend(
        self,
        returns: list[float],
        num_trials: int = 1,
        window: int = 60,
    ) -> list[DSRTrendPoint]:
        """滚动窗口 DSR 趋势追踪。

        从 window-1 位置开始, 每个位置取前 window 期收益率计算 DSR,
        形成 DSR 趋势序列。

        Args:
            returns: 完整收益率序列
            num_trials: 试次数
            window: 滚动窗口大小(默认 60)

        Returns:
            list[DSRTrendPoint], 长度 = len(returns) - window + 1

        Raises:
            SimulationError: 窗口 < 3 / 序列短于窗口
        """
        if window < 3:
            raise SimulationError(
                f"window 不能 < 3: {window}",
                details={"window": window},
            )
        if len(returns) < window:
            raise SimulationError(
                f"序列长度 {len(returns)} < 窗口 {window}",
                details={"len": len(returns), "window": window},
            )

        trend: list[DSRTrendPoint] = []
        for i in range(window, len(returns) + 1):
            window_returns = returns[i - window : i]
            result = self.calculate(window_returns, num_trials=num_trials)
            trend.append(
                DSRTrendPoint(
                    index=i - 1,
                    dsr=result.dsr,
                    sharpe=result.sharpe_annualized,
                )
            )
        return trend


__all__ = [
    "DSRConfig",
    "DSRResult",
    "DSRTrendPoint",
    "DSR_OVERFITTING_FLOOR",
    "DSR_SIGNIFICANCE_THRESHOLD",
    "DSR_UNDECIDABLE",
    "DeflatedSharpeCalculator",
    "EULER_MASCHERONI",
    "KURTOSIS_PEARSON_NORMAL",
    "SimulationError",
    "deflated_sharpe_from_moments",
    "expected_max_sharpe_z",
    "sharpe_variance_is_degenerate",
    "variance_of_sharpe",
]
