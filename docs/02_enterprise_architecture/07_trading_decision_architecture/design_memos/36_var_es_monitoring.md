---
ttl: permanent
doc_type: architecture_view
title: VaR/ES 与波动率监控
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.1.0"
date: 2026-08-10
topic: var_es_monitoring
scope: 07_trading_decision_architecture
---

# VaR/ES 与波动率监控

> **性质**：由 [00_index_trading_decision](00_index_trading_decision.md) G17 主题组派生，将 [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.5.4 的 VaR/ES 辅助监控框架落地为可施工的 spec + 伪代码。
> **施工图纪律**：本文档 status=active，对应模块允许施工。
> **2026-08 研究整合**：FRTB 97.5% ES + 可变流动性期限（Basel III.1）；GARCH-FHS 过滤历史模拟（arXiv:2505.05646 Xin 2025 对比实证）；EVT POT/GPD 尾部估计（ECB WP3166 2026 单参数动态）；E-backtesting e-value 框架（arXiv:2209.00991v6 Wang 2026）；动态因子半参数 VaR-ES（arXiv:2601.01142 Fu 2026）；L-VaR 流动性调整（Amihud + Kyle λ）。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G17 VaR/ES 与波动率监控 |
| 所属 | 作战地图 09 + 30_multi_strategy_concurrency §2.5.4 |
| 依赖 | G16（[35_drawdown_protocol_impl](35_drawdown_protocol_impl.md) 已定稿 v1.0.0） |
| 对标 | 赢牛资管 VaR-ES / Sina 量化风控 / FRTB IMA |
| 正交性 | ✅ 与 regime 正交 |
| 优先级 | P3 |
| 状态 | ✅ active — VaR/ES/FHS/EVT/L-VaR/波动率调整算法已定稿 |

## 2. 背景

### 2.1 项目处境

VaR/ES 是回撤 Protocol 的**辅助监控层**（非主风控）。回撤 Protocol（G16）管"已实现生存风险"，VaR/ES 管"预期尾部风险"。两者互补：回撤是事实，VaR/ES 是预测。

### 2.2 核心问题

1. **VaR 计算方法选择**：历史模拟（HS）、参数法（正态）、蒙特卡洛（MC）各有缺陷——HS 无法外推超过历史最坏损失，正态低估肥尾，MC 依赖分布假设。
2. **ES 的回测难题**：ES 不可单独 elicitable，传统 Kupiec/Christoffersen 回测仅适用于 VaR 频率检验，无法检验 ES 的尾部严重度。
3. **A 股流动性调整**：标准 VaR 假设可按中间价即时清算，A 股涨跌停+T+1 下大单 self-impact 压价，需 L-VaR。
4. **波动率时变性**：A 股波动率聚类显著，静态 VaR 在高波动期低估风险，需 GARCH 过滤或波动率缩放。
5. **与回撤 Protocol 的协同**：§2.5.4 定义了 VaR>1.2×减仓 20%、ES>1.3×再减仓 20% 的触发动作，需明确"入场基准"的计算口径。

### 2.3 约束条件

- **MVP 简化原则**：不过度工程，先建全+全 log，实盘 6-12 月后裁剪未触发项（project_memory 过度工程处理原则）
- **A 股 T+1**：VaR 持有期至少 1 天（T+1 结算约束），不可假设日内平仓
- **数据窗口**：MVP 阶段使用 252 交易日（1 年）历史窗口
- **FRTB 对标**：97.5% ES + 可变流动性期限是行业新标准（Basel III.1），但 MVP 阶段先用 95% VaR + 95% ES 简化

## 3. 决策

### 3.1 架构定义

VaR/ES 监控作为独立风控模块，每日盘后计算，输出到回撤 Protocol 和 Kill Switch 作为辅助触发信号：

```
每日盘后 → 收益率序列 → [GARCH-FHS VaR/ES 计算] → 风险监控面板
                                    ↓
                    [L-VaR 流动性调整] → 触发动作判定
                                    ↓
                    [波动率缩放] → 仓位调整信号 → 回撤 Protocol 联动
```

**核心模块**：
- `VaRCalculator`：GARCH-FHS 方法计算 VaR
- `ESCalculator`：基于 VaR 尾部均值计算 ES
- `EVT tail Estimator`：POT/GPD 极值理论估计深尾
- `LVaRCalculator`：流动性调整 VaR（Amihud + Kyle λ）
- `VolatilityScaler`：30 日波动率调整
- `ESBacktester`：e-value 框架 ES 回测

### 3.2 GARCH-FHS VaR/ES 计算算法

```python
import numpy as np
from dataclasses import dataclass
from typing import Optional

@dataclass
class VaRESResult:
    """VaR/ES 计算结果。"""
    var_95: float           # 95% VaR（正数表示损失）
    var_99: float           # 99% VaR
    es_95: float            # 95% ES（超过 VaR_95 时的预期平均损失）
    es_99: float            # 99% ES
    method: str             # "GARCH-FHS" / "EVT-POT" / "HS"
    volatility_forecast: float  # GARCH 一步波动率预测
    liquidity_adjusted_var: Optional[float]  # L-VaR（含流动性成本）


def calc_garch_fhs_var_es(
    returns: np.ndarray,           # 历史日收益率序列（至少 252 天）
    confidence_levels: list[float] = None,  # [0.95, 0.99]
    holding_period: int = 1,       # 持有期（天），A 股 T+1 最小 1
    n_simulations: int = 10000,    # FHS 重采样次数
) -> VaRESResult:
    """GARCH-FHS 过滤历史模拟 VaR/ES 计算。

    方法（arXiv:2505.05646 Xin 2025 实证最优）：
    1. GARCH(1,1) 拟合收益率序列 → 标准化残差 z_t（近 i.i.d.）
    2. 对残差按历史日期整体重采样（保留分布形状，不假设正态）
    3. 用当前波动率预测 σ_{t+1} 重新膨胀：r_sim = μ + σ_{t+1} × z
    4. 组合分布取下分位 = VaR，尾部均值 = ES

    为何优于朴素方法：
    - HS（历史模拟）无法捕捉波动率时变性，高波动期低估风险
    - GARCH-N（正态假设）低估肥尾，arXiv:2505.05646 实证：5 日 VaR
      GARCH-N=5.93% vs FHS=11.18%，高斯严重低估
    - FHS 结合 GARCH 的波动率时变 + 历史残差的真实分布形状
    """
    if confidence_levels is None:
        confidence_levels = [0.95, 0.99]

    # 步骤 1：GARCH(1,1) 拟合（使用 arch 包或手动实现）
    # μ = 均值，σ²_t = ω + α·ε²_{t-1} + β·σ²_{t-1}
    mu, omega, alpha, beta = _fit_garch11(returns)
    residuals, conditional_vol = _extract_garch_residuals(returns, mu, omega, alpha, beta)

    # 步骤 2：标准化残差（近 i.i.d.）
    z = residuals / conditional_vol

    # 步骤 3：一步波动率预测
    sigma_forecast = np.sqrt(omega + alpha * residuals[-1]**2 + beta * conditional_vol[-1]**2)

    # 步骤 4：FHS 重采样——从标准化残差中随机抽取，用 σ_forecast 重新膨胀
    simulated_returns = np.zeros(n_simulations)
    for i in range(n_simulations):
        z_sample = np.random.choice(z, size=holding_period, replace=True)
        simulated_returns[i] = mu * holding_period + sigma_forecast * np.sum(z_sample)

    # 步骤 5：计算 VaR 和 ES
    results = {}
    for cl in confidence_levels:
        var = -np.percentile(simulated_returns, (1 - cl) * 100)  # 正数表示损失
        tail_losses = -simulated_returns[simulated_returns < -var]
        es = np.mean(tail_losses) if len(tail_losses) > 0 else var
        results[cl] = (var, es)

    var_95, es_95 = results[0.95]
    var_99, es_99 = results[0.99]

    return VaRESResult(
        var_95=var_95, var_99=var_99,
        es_95=es_95, es_99=es_99,
        method="GARCH-FHS",
        volatility_forecast=sigma_forecast,
        liquidity_adjusted_var=None,  # 由 LVaR 模块单独计算
    )


def _fit_garch11(returns: np.ndarray) -> tuple[float, float, float, float]:
    """GARCH(1,1) 参数拟合——MLE 最大似然估计。

    σ²_t = ω + α·ε²_{t-1} + β·σ²_{t-1}
    约束：ω>0, α≥0, β≥0, α+β<1（平稳性）

    实现策略：
    1. 优先调用 arch 包（arch.arch_model），生产环境推荐
    2. arch 包不可用时回退到 scipy.optimize MLE（本函数内联实现）

    2026-08 研究整合：
    - marketmaker.cc (2026-07) vol targeting 实证：GARCH(1,1) 一步预测 σ̂_t
      用于 1/σ² 缩放可提升 Sharpe 并控制回撤（Moreira & Muir 2017 机制）
    - arXiv:2606.09478 (2026-06) 中文高频实证：MS-GJR-GARCH（非对称+regime切换）
      优于标准 GARCH(1,1)，Phase 1.5+ 评估升级
    - arXiv:2606.06190 (2026-06) MS-GARCH TVTP：三时间框架（1D/4H/1H）27 维联合概率张量
      DM=+4.70 统计显著优于 GARCH(1,1)，Phase 2+ 远期候选
    """
    # 策略 1：优先使用 arch 包（生产推荐）
    try:
        from arch import arch_model
        model = arch_model(returns * 100, mean='Constant', vol='Garch', p=1, q=1,
                           dist='normal', rescale=False)
        res = model.fit(disp='off')
        mu = res.params['mu'] / 100.0
        omega = res.params['omega'] / 10000.0  # arch 包以百分比拟合，方差需 /10000
        alpha = res.params['alpha[1]']
        beta = res.params['beta[1]']
        # 平稳性校验
        if alpha + beta >= 1.0 or omega <= 0:
            raise ValueError("arch fit violated stationarity constraints")
        return mu, omega, alpha, beta
    except Exception:
        pass  # 回退到策略 2

    # 策略 2：scipy.optimize MLE 内联实现
    from scipy.optimize import minimize

    mu = float(np.mean(returns))
    eps = returns - mu

    def _garch_neg_loglik(params):
        """GARCH(1,1) 负对数似然（正态创新假设）。"""
        omega_p, alpha_p, beta_p = params
        # 参数化约束：通过 exp/sigmoid 变换保证 ω>0, α≥0, β≥0, α+β<1
        omega = np.exp(omega_p)  # ω>0
        alpha = alpha_p ** 2 / (1 + alpha_p ** 2) * 0.5  # α∈[0,0.5)
        beta = beta_p ** 2 / (1 + beta_p ** 2) * (0.99 - alpha)  # β∈[0, 0.99-α)
        if alpha + beta >= 0.999:
            return 1e10

        n = len(eps)
        cond_var = np.zeros(n)
        cond_var[0] = np.var(returns)
        for t in range(1, n):
            cond_var[t] = omega + alpha * eps[t - 1] ** 2 + beta * cond_var[t - 1]
            if cond_var[t] <= 0:
                return 1e10

        # 对数似然：-0.5 * Σ[ln(2π) + ln(σ²_t) + ε²_t/σ²_t]
        loglik = -0.5 * np.sum(np.log(2 * np.pi) + np.log(cond_var) + eps ** 2 / cond_var)
        return -loglik  # 返回负值用于 minimize

    # 初始值：ω=样本方差×0.05, α=0.10, β=0.85（典型 A 股参数）
    init_var = float(np.var(returns))
    x0 = [np.log(init_var * 0.05), 0.316, 2.646]  # 反变换后约 α=0.10, β=0.85
    result = minimize(_garch_neg_loglik, x0, method='Nelder-Mead',
                      options={'maxiter': 2000, 'xatol': 1e-6})

    omega_p, alpha_p, beta_p = result.x
    omega = np.exp(omega_p)
    alpha = alpha_p ** 2 / (1 + alpha_p ** 2) * 0.5
    beta = beta_p ** 2 / (1 + beta_p ** 2) * (0.99 - alpha)

    return mu, omega, alpha, beta


def _extract_garch_residuals(returns, mu, omega, alpha, beta):
    """提取 GARCH 条件残差和条件波动率。"""
    n = len(returns)
    residuals = np.zeros(n)
    cond_vol = np.zeros(n)
    cond_vol[0] = np.std(returns)

    for t in range(1, n):
        residuals[t] = returns[t] - mu
        cond_vol[t] = np.sqrt(omega + alpha * residuals[t-1]**2 + beta * cond_vol[t-1]**2)

    return residuals, cond_vol
```

### 3.3 EVT 极值理论尾部估计算法

```python
def calc_evt_pot_es(
    returns: np.ndarray,
    threshold_quantile: float = 0.90,  # POT 阈值分位数
    confidence_level: float = 0.995,   # 深尾分位数
) -> tuple[float, float]:
    """EVT POT/GPD 极值理论尾部估计——用于 99.5%+ 深尾分位。

    方法（ECB WP3166 2026 / arXiv:2605.01909 Engelke 2026）：
    Pickands-Balkema-de Haan 定理：超过阈值 u 的超额 ~ GPD(σ, ξ)
    P(L-u ≤ y | L>u) = 1 - (1 + ξ·y/σ)^(-1/ξ)

    闭式解：
    VaR_q = u + (σ/ξ)·[((1-q)·N/N_u)^(-ξ) - 1]
    ES_q  = (VaR_q + σ - ξ·u) / (1-ξ)        # ξ<1

    为何优于 HS：
    - HS 无法外推超过历史最坏损失
    - 正态 VaR 在 99.9% 处比 EVT 低约 50%
    - EVT 是唯一能给出 99.5%+ 深尾分位的统计基础
    """
    losses = -returns  # 转为损失（正数）
    u = np.percentile(losses, threshold_quantile * 100)  # 阈值
    excess = losses[losses > u] - u  # 超过阈值的超额

    if len(excess) < 30:
        # 样本不足，退回 FHS
        return 0.0, 0.0

    # GPD 参数估计（最大似然）
    xi, sigma = _fit_gpd(excess)

    if xi >= 1:
        # 形状参数 >=1 时 ES 无限，退化处理
        return 0.0, 0.0

    N = len(losses)
    N_u = len(excess)

    # POT 闭式解
    var_q = u + (sigma / xi) * (((1 - confidence_level) * N / N_u) ** (-xi) - 1)
    es_q = (var_q + sigma - xi * u) / (1 - xi)

    return var_q, es_q


def _fit_gpd(excess: np.ndarray) -> tuple[float, float]:
    """GPD 参数拟合（简化版——MVP 阶段可用 scipy.stats.genpareto）。"""
    # 使用 scipy.stats.genpareto.fit(excess) 拟合
    # 返回 (xi, sigma) 形状参数和尺度参数
    from scipy.stats import genpareto
    xi, loc, sigma = genpareto.fit(excess, floc=0)
    return xi, sigma
```

### 3.4 L-VaR 流动性调整 VaR 算法

```python
def calc_lvar(
    var: float,                    # 基础 VaR（来自 GARCH-FHS）
    position_value: float,         # 仓位价值（元）
    amihud_illiq: float,           # Amihud 非流动性比率
    kyle_lambda: float,            # Kyle λ 价格冲击系数
    half_spread: float,            # 半价差（相对值）
    volume: float,                 # 拟平仓量（股）
) -> float:
    """L-VaR 流动性调整 VaR——加入流动性成本。

    方法（O'Connell 2026 / 1998 LTCM 教训）：
    LVaR = VaR + Liquidity_Cost × Position_Size
    Liquidity_Cost = ILLIQ × Volume × Kyle_λ + ½·Spread

    为何需要 L-VaR：
    - 标准 VaR 假设可按中间价即时清算
    - 实际上 bid 价低于 mid，大单 self-impact 进一步压价
    - 1998 LTCM 与 2008 危机核心 = 市场流动性 + 融资流动性正反馈螺旋
      （margin call → 抛售 → 价差扩大 → 更多 margin call）

    A 股特定：
    - 涨跌停板下大单无法成交，L-VaR 需额外加流动性黑洞溢价
    - T+1 约束下持有期至少 1 天，不可假设日内平仓
    """
    # 流动性成本 = Amihud 冲击 + Kyle λ 冲击 + 半价差
    amihud_cost = amihud_illiq * volume * kyle_lambda
    spread_cost = half_spread * position_value
    liquidity_cost = amihud_cost + spread_cost

    # L-VaR = 基础 VaR + 流动性成本
    lvar = var * position_value + liquidity_cost

    # A 股涨跌停流动性黑洞溢价（简化：+20% 安全边际）
    lvar *= 1.2

    return lvar


def calc_amihud_illiq(returns: np.ndarray, dollar_volumes: np.ndarray) -> float:
    """Amihud 非流动性比率（Micro Alphas 2026-06）。

    ILLIQ = mean_t(|r_t| / DollarVolume_t) × 10^6

    特点：日频即可，长历史，跨市场可得，Kyle λ 的低频代理。
    """
    valid = dollar_volumes > 0
    ratios = np.abs(returns[valid]) / dollar_volumes[valid]
    return np.mean(ratios) * 1e6


def calc_kyle_lambda(price_changes: np.ndarray, order_flows: np.ndarray) -> float:
    """Kyle λ 价格冲击系数（O'Connell 2026）。

    ΔP_t = λ · OrderFlow_t + ε
    λ = Cov(ΔP, OF) / Var(OF)

    特点：精细战术单券冲击，需订单流数据（Level-2 或龙虎榜代理）。
    """
    cov = np.cov(price_changes, order_flows)[0, 1]
    var_of = np.var(order_flows)
    return cov / var_of if var_of > 0 else 0.0
```

### 3.5 波动率调整算法

```python
def calc_volatility_adjustment(
    current_vol_30d: float,         # 当前 30 日波动率
    baseline_vol: float,            # 入场基准波动率
    position_cap: float,            # 当前仓位上限
) -> tuple[float, str]:
    """30 日波动率调整——每增 10% → 仓位减 20%（LedgerMind 2026-05）。

    Returns: (adjusted_position_cap, adjustment_reason)
    """
    if baseline_vol <= 0:
        return position_cap, "no_baseline"

    vol_ratio = current_vol_30d / baseline_vol
    vol_increase = (vol_ratio - 1.0)  # 正值表示波动率上升

    if vol_increase <= 0:
        return position_cap, "vol_stable_or_decreasing"

    # 每增 10% → 仓位减 20%
    n_10pct_increments = int(vol_increase / 0.10)
    reduction = 0.20 * n_10pct_increments
    reduction = min(reduction, 0.80)  # 最多减 80%

    adjusted_cap = position_cap * (1 - reduction)
    reason = f"vol_up_{vol_increase:.1%}_reduce_{reduction:.0%}"
    return adjusted_cap, reason
```

### 3.6 VaR/ES 触发动作算法

```python
@dataclass
class RiskTrigger:
    """VaR/ES 触发动作（30_multi_strategy_concurrency §2.5.4）。"""
    triggered: bool
    action: str         # "reduce_20pct" / "reduce_20pct_more" / "vol_adjust" / "none"
    reason: str
    adjusted_position_cap: float


def evaluate_var_es_triggers(
    current_var: VaRESResult,
    baseline_var: VaRESResult,       # 入场时 VaR/ES 基准
    current_vol_30d: float,
    baseline_vol: float,
    position_cap: float,
) -> RiskTrigger:
    """VaR/ES 触发动作判定。

    §2.5.4 规则：
    - VaR > 1.2×入场 VaR → 减仓 20%
    - ES > 1.3×入场 ES → 再减仓 20%
    - 30 日波动率每增 10% → 仓位减 20%
    """
    # 规则 1：VaR > 1.2×入场 VaR → 减仓 20%
    if current_var.var_95 > 1.2 * baseline_var.var_95:
        # 规则 2：ES > 1.3×入场 ES → 再减仓 20%
        if current_var.es_95 > 1.3 * baseline_var.es_95:
            return RiskTrigger(
                triggered=True,
                action="reduce_20pct_more",
                reason=f"var={current_var.var_95:.4f}>1.2×{baseline_var.var_95:.4f}, "
                       f"es={current_var.es_95:.4f}>1.3×{baseline_var.es_95:.4f}",
                adjusted_position_cap=position_cap * 0.8 * 0.8,  # 减 20% 再减 20%
            )
        return RiskTrigger(
            triggered=True,
            action="reduce_20pct",
            reason=f"var={current_var.var_95:.4f}>1.2×{baseline_var.var_95:.4f}",
            adjusted_position_cap=position_cap * 0.8,
        )

    # 规则 3：波动率调整
    adjusted_cap, vol_reason = calc_volatility_adjustment(
        current_vol_30d, baseline_vol, position_cap
    )
    if adjusted_cap < position_cap:
        return RiskTrigger(
            triggered=True,
            action="vol_adjust",
            reason=vol_reason,
            adjusted_position_cap=adjusted_cap,
        )

    return RiskTrigger(triggered=False, action="none", reason="", adjusted_position_cap=position_cap)
```

### 3.7 E-backtesting ES 回测算法

```python
def e_backtest_es(
    actual_returns: np.ndarray,     # 实际收益率序列
    var_forecasts: np.ndarray,      # VaR 预测序列（同长度）
    es_forecasts: np.ndarray,       # ES 预测序列（同长度）
    alpha: float = 0.05,            # 显著性水平
) -> dict:
    """E-backtesting——基于 e-value 的 model-free ES 回测（arXiv:2209.00991v6 Wang 2026）。

    为何优于传统 Kupiec/Christoffersen：
    - 传统方法仅数 VaR 违反次数，无法检验 ES 的尾部严重度
    - e-value 框架是 model-free 的，能同时检验 VaR 频率与 ES 严重度
    - 支持结构变化检测与"蓄意高估"博弈识别

    核心思路：
    - 构造 backtest e-statistics → e-processes
    - e-process > 1/α 时拒绝模型（模型不合格）
    """
    n = len(actual_returns)
    violations = actual_returns < -var_forecasts  # VaR 违反

    # 计算 e-values：在违反日，实际损失与 ES 预测的比值
    e_values = np.ones(n)
    for t in range(n):
        if violations[t]:
            # 违反日：实际损失 / ES 预测（比值越大说明 ES 低估越严重）
            actual_loss = -actual_returns[t]
            es_pred = es_forecasts[t]
            if es_pred > 0:
                e_values[t] = actual_loss / es_pred

    # e-process 累积
    e_process = np.cumprod(e_values)

    # 检验：e_process 最大值是否超过 1/α
    reject_threshold = 1.0 / alpha
    max_e = np.max(e_process)
    rejected = max_e > reject_threshold

    # 违反率统计
    violation_rate = np.mean(violations)

    return {
        "violation_rate": violation_rate,
        "expected_violation_rate": alpha,
        "max_e_value": max_e,
        "reject_threshold": reject_threshold,
        "model_rejected": rejected,
        "n_violations": int(np.sum(violations)),
        "n_observations": n,
    }
```

### 3.8 入场 VaR/ES 基准计算口径

| 因素 | 处理方式 | 理由 |
|---|---|---|
| **计算时点** | 策略首次上线日盘后计算 | 作为后续监控的基准 |
| **数据窗口** | 上线前 252 交易日 | 1 年完整周期 |
| **方法** | GARCH-FHS | §3.2 实证最优 |
| **持有期** | 1 天 | A 股 T+1 最小持有期 |
| **置信水平** | 95% VaR + 95% ES | MVP 简化；Phase 1.5+ 升级 97.5% ES（FRTB 对标） |
| **更新频率** | 每日盘后重算 | 捕捉波动率时变性 |

## 4. 考虑过的替代方案

| 方案 | 描述 | 拒绝理由 |
|---|---|---|
| **纯历史模拟（HS）** | 直接取历史收益分位 | 无法捕捉波动率时变性；arXiv:2505.05646 实证：HS 经验违反率远超理论 |
| **参数法（正态）** | 假设正态分布，σ×z_α | 低估肥尾；A 股收益率显著 leptokurtosis |
| **蒙特卡洛（MC）** | 假设分布模型，模拟路径 | 依赖分布假设，模型风险高 |
| **97.5% ES（FRTB 全套）** | 直接采用 FRTB IMA 全套标准 | MVP 阶段过度合规；Phase 1.5+ 实盘后再对标 FRTB |
| **多模型组合（MCS）** | 32 个模型组合预测（arXiv:2406.06235） | MVP 阶段过度工程；先 GARCH-FHS 单模型，Phase 1.5+ 再组合 |
| **VaR 替代 ES 作主指标** | 用 VaR 而非 ES | ES 是 coherent risk measure（满足次加性），VaR 在重尾下可违反次加性；FRTB 已用 ES 替代 VaR |

## 5. 上限定义

| 上限 | 值 | 理由 |
|---|---|---|
| **VaR 触发线** | 1.2×入场 VaR | §2.5.4 行业基准 |
| **ES 触发线** | 1.3×入场 ES | §2.5.4 行业基准 |
| **波动率触发** | 每增 10% → 仓位减 20% | LedgerMind 2026-05 |
| **最大减仓** | 80% | 波动率调整最多减 80%，留 20% 底仓 |
| **回测违反率** | <5%（95% VaR） | 超过则模型不合格（e-backtest 拒绝） |

**演进路径**：
- MVP：95% VaR + 95% ES，GARCH-FHS，252 天窗口
- Phase 1.5：升级 97.5% ES（FRTB 对标），引入 EVT 深尾估计
- Phase 2：多模型组合（MCS），动态因子半参数模型（arXiv:2601.01142）

## 6. 待裁定

| 项 | 暂缓理由 | 重评条件 |
|---|---|---|
| **97.5% ES FRTB 全套** | MVP 阶段简化为 95% | Phase 1.5+ 实盘 6 月后对标 FRTB |
| **多模型组合（MCS）** | 单模型 GARCH-FHS 已足够 | Phase 1.5+ 模型不确定性显著时 |
| **动态因子半参数模型** | 高频 realized measures 数据未接入 | Phase 2+ 高频数据层就绪后 |
| **Anytime-Valid Conformal 校正** | 多次重校准序列检验校正 | Phase 2+ 季度重校准成为常规时 |
| **5 级 VaR + 7 黑天鹅降级** | project_memory 已裁定降级为监控层 | 先全建+全 log，实盘 6-12 月后裁剪未触发项 |

## 7. 待定问题（讨论要点对齐）

- [x] ① VaR_95 计算（历史模拟/参数法）→ §3.2 GARCH-FHS（实证最优）
- [x] ② ES_95 计算 → §3.2 FHS 尾部均值 + §3.3 EVT POT/GPD 深尾
- [x] ③ 入场 VaR/ES 基准 → §3.8 口径表
- [x] ④ 触发动作（VaR>1.2×减仓20%/ES>1.3×再减20%）→ §3.6 `evaluate_var_es_triggers`
- [x] ⑤ 30 日波动率调整（每增10%→仓位减20%）→ §3.5 `calc_volatility_adjustment`
- [x] ⑥ 数据窗口 → 252 交易日（1 年）
- [x] ⑦ 与回撤 Protocol 的协同 → VaR/ES 是辅助监控层，触发动作通过 `adjusted_position_cap` 联动回撤 Protocol

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G17
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.5.4
- [35_drawdown_protocol_impl](35_drawdown_protocol_impl.md)（G16，依赖项，已定稿 v1.0.0）
- [37_liquidity_crisis_protocol](37_liquidity_crisis_protocol.md)（G18，L-VaR 流动性因子来源）
- battle_map_09_risk_control（当前状态快照）
- **2026-08 研究引用**：
  - Xin (2025) "Comparative Evaluation of VaR Models" arXiv:2505.05646 — GARCH-FHS 实证最优
  - Fu (2026) "Dynamic factor semiparametric VaR-ES" arXiv:2601.01142 — realized measures 驱动
  - Gerlach, Naimoli, Storti (2025) "QFHS multi-step ahead" arXiv:2502.20978
  - Wang, Wang, Ziegel (2026) "E-backtesting" arXiv:2209.00991v6 — e-value ES 回测
  - ECB WP3166 (2026) D'Innocenzo et al. — 单参数动态 EVT
  - Engelke et al. (2026) "EVT + ML extrapolation" arXiv:2605.01909
  - Amendola et al. (2026) "MCS Combination" arXiv:2406.06235v2
  - Hultberg, Bates, Candès (2026) "Anytime-Valid CRC" arXiv:2602.04364
  - O'Connell (2026) "L-VaR" — Amihud + Kyle λ
  - Micro Alphas (2026) "Amihud Illiquidity Ratio"
  - frmquizbank.com (2026-08) "ES vs VaR — FRTB Shift"

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行 |
| 2026-08-10 | 1.0.0 | 落地 spec 定稿 | GARCH-FHS VaR/ES+EVT POT/GPD 深尾+L-VaR 流动性调整+波动率缩放+e-value 回测算法化；整合 2026-08 研究（FRTB/GARCH-FHS/EVT/E-backtesting/L-VaR） |
| 2026-08-10 | 1.1.0 | GARCH(1,1) 参数拟合从占位值改为 MLE 落地实现 | `_fit_garch11` 双策略实现：优先 arch 包（生产推荐），回退 scipy.optimize MLE（Nelder-Mead + 参数化约束变换）；整合 2026-08 研究（marketmaker.cc vol targeting + arXiv:2606.09478 中文高频 GJR-GARCH + arXiv:2606.06190 MS-GARCH TVTP） |
