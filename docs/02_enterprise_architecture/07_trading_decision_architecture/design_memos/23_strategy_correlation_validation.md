---
ttl: permanent
doc_type: architecture_view
title: 策略间相关性验证
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.1.1"
date: 2026-08-10
topic: strategy_correlation_validation
scope: 07_trading_decision_architecture
---

# 策略间相关性验证

> **性质**：由 [00_index_trading_decision](00_index_trading_decision.md) G07 主题组派生，将 [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §6.2 的"施工前必做项"落地为可执行的验证 spec + 伪代码。
> **施工图纪律**：本文档 status=active，对应验证模块允许施工；流程见 [01_design_memo_management_spec](01_design_memo_management_spec.md) §2.2。
> **2026-08 研究整合**：Morwane block-bootstrap 时序保留重采样范式（stationary block-bootstrap, Politis & Romano 1994, block_size=21 天保留自相关结构，本项目 A 股情绪周期自相关更短，取 5-10 天）；López de Prado (2018) Advances in Financial Machine Learning——相关性虚假发现控制（多重检验膨胀假阳性、CI 下界稳健判定）；Ledoit-Wolf 协方差收缩（小样本稳定化）；DCC-GARCH 动态条件相关（Phase 1.5+ 评估）；Partial correlation 偏相关（去除共同因子后的纯策略相关，区分"真相关"vs"共受情绪驱动"）；copula 尾部相依（Nelsen 2006——上/下尾相关系数 λ_upper/λ_lower、经验 copula 非参数估计；Joe 1997 多变量相依模型）；Koenker (2005) 分位数回归——极端分位（τ=0.05/0.95）检测尾部相关性突变；CUSUM 变点检测（Page 1954 / Killick et al. 2012 PELT）——滚动相关性的结构性断裂检测；DASH 归因稳定性不可能性定理（arXiv:2605.21492, Lean 4 机器验证——collinearity 下 SHAP 排名结构性不稳定，68% 数据集受影响，M>=5 跨模型聚合降至 <1%）；因子冗余检查三维度（EntroPy 2026-05 signal/return/exposure correlation，对标 62_business_registry_construction §4.7 E16）。；Deflated Sharpe Ratio（DSR，Bailey & Lopez de Prado 2014）——多重检验+策略间相关性双重调整的 Sharpe 虚假发现控制，5 策略 10 对多重比较时裸 Sharpe 排名高估显著性，DSR 收缩向 deflated benchmark SR0 约 1.63（年化）噪声天花板，对齐 §3.5 阈值判定的统计严谨性；Soloviov DSR 鲁棒性带（2026-07）——有效 trial 数非单一数值（5 估计器相差两个数量级 1.6-370），相关搜索场景（参数网格/同源变体）禁用裸 DSR 须用 White Reality Check/Hansen SPA bootstrap，MVP 阶段 5 候选策略非参数网格搜索 trial_correlated=false 时裸 DSR 可用；causal-quant 因果验证（2026-07）——相关性不等于因果性，两策略相关可能因 confounder（情绪周期共同驱动）或 collider（past_return 碰撞变量，系数符号可翻转 +0.08 到 -0.04）而非真 alpha 重叠，策略注册时声明因果图 DAG 避免事后合理化，对齐 §3.4 偏相关区分真相关 vs 共受情绪驱动；A 股 mask-first 设计（arXiv:2507.07107v2 2026-05 Yimin Du USTC）——涨跌停板使部分收盘价不可执行，标准实现先读价格再过滤行导致 upstream contamination（MA/correlation/rank 静默传播虚假相关，实证虚增 IC 18%），mask-first 在收益序列加载时构造 tradability mask 贯穿每个算子，是 A 股相关性验证的前置 MUST 而非可选。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G07 策略间相关性验证 |
| 所属 | 30_multi_strategy_concurrency §6.2（施工前必做） |
| 依赖 | G04（需策略定义才能算相关，[20_first_batch_strategies](20_first_batch_strategies.md) v1.2.4 已定稿）/ G21（情绪周期阶段标签，[28_sentiment_cycle_trading](28_sentiment_cycle_trading.md) 待讨论）/ [10_regime_detector_spec](10_regime_detector_spec.md) §3.3（情绪周期 5 阶段映射，分层依据） |
| 对标 | Morwane block-bootstrap 相关性验证（stationary block-bootstrap / 21-day blocks / 2000× resample / OOS 2013-2026 ρ=+0.03 弱相关 sleeve 范式）/ López de Prado 虚假发现控制 / Politis & Romano (1994) 稳态 block-bootstrap |
| 正交性 | ✅ 与 regime 正交（验证层不依赖 regime 输出，但分层维度借用情绪周期，与 G21 协同） |
| 优先级 | P1（G04 后立即，是首批 3 策略施工前的最后一道门控） |
| 状态 | ✅ active — 12 算法定型：相关矩阵(Pearson/Spearman/Kendall)+block-bootstrap+情绪周期分层+阈值门控+滚动CUSUM+DCC-GARCH(Phase 2.0+)+尾部相依+Ledoit-Wolf收缩+RMT噪声过滤+多重共线性检测+情绪beta污染检测+验证报告 |

## 2. 背景

### 2.1 项目处境

ZephyrAlpha 已完成多策略并发架构定型（Model A：独立账本 + firm 聚合 + regime 风险节流，[30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) v1.3.3）与首批 3 策略定义（打板 + 多因子 + 事件驱动，[20_first_batch_strategies](20_first_batch_strategies.md) v1.2.4）。在 StrategyBook/FirmRiskAggregator 模块施工前，必须验证 5 候选策略两两相关性是否真正分散——这是 Model A "加法替代优化器"哲学成立的前提（[30_multi_strategy_concurrency §2.3](30_multi_strategy_concurrency.md)）。

5 候选策略清单（[20_first_batch_strategies §2.1](20_first_batch_strategies.md) 裁定）：
1. **打板（daban）** — 高换手 / 小容量 / 情绪驱动（首批）
2. **多因子（multifactor）** — 低换手 / 大容量 / 横截面（首批）
3. **事件驱动（event_driven）** — 中换手 / 中容量 / 离散事件（首批）
4. **价值反转（value_reversal）** — 第二批次（首批 track record 后）
5. **动量趋势（momentum_trend）** — 第二批次（首批 track record 后）

### 2.2 核心问题

1. **5 候选策略两两相关矩阵怎么算**：5 策略即 10 对，需输出 Pearson + Spearman 双口径相关矩阵。Pearson 检测线性相关，Spearman 抗异常值与非正态（A 股收益分布厚尾，Spearman 是必备交叉验证）。
2. **如何保留时序结构做重采样**：金融收益序列存在自相关、波动率聚集、情绪周期持续性——iid bootstrap 会低估方差、置信区间过窄。需用 Morwane 范式 block-bootstrap（block_size 取 5-10 天，对齐 A 股情绪周期短期自相关）。
3. **按情绪周期分层看相关性**：情绪周期（冰点/反核/主升/疯狂/退潮）是所有短周期策略的共同隐形驱动（[30_multi_strategy_concurrency §1.3](30_multi_strategy_concurrency.md)）。若各阶段相关性均 >0.6，则"多策略实为情绪 beta 穿多件衣服"——需重新审视策略组合（[30_multi_strategy_concurrency §6.2](30_multi_strategy_concurrency.md)）。
4. **区分"真相关"vs"共受情绪驱动"**：两策略相关可能因 alpha 重叠（真相关），也可能因共受情绪周期驱动（伪相关）。需用偏相关去除共同因子后看纯策略相关。
5. **验证报告如何标准化**：5 个候选策略 × 5 个情绪阶段 × Pearson/Spearman 双口径 × 2000 次 bootstrap → 输出量爆炸，必须模板化呈现，给人决策一个清晰的 PASS/FAIL 判定。

### 2.3 约束条件

- **A 股 T+1 结算、不能做空、涨跌停限制** → 策略收益分布厚尾、有涨跌停日跳变，Spearman 与 block-bootstrap 是必备而非可选
- **5 候选策略中仅首批 3 策略有回测数据**：价值反转 / 动量趋势是第二批次，本期验证只能用首批 3 策略的真实回测收益 + 第二批 2 策略的设计意图估算收益（标 low_confidence）。5×5 矩阵的右下 2×2 块（价值反转↔动量趋势）及跨块（首批↔二批）的相关性为低置信度，仅作设计阶段预警
- **block_size 选择**：Morwane 用 21 天（美股自相关结构）；A 股情绪周期短周期自相关约 3-7 天，block_size 取 5-10 天既保留时序结构又避免块内周期过长导致块间样本独立性丧失
- **样本量约束**：A 股每年约 244 个交易日，3 年 ≈ 732 个样本；5 阶段分层后每阶段样本数取决于情绪周期分布（主升/退潮常见，疯狂/冰点稀有）——稀有阶段可能不足 30 个样本，需 fallback 为 NaN 并标记 INSUFFICIENT_SAMPLES
- **与 G21 的协同边界**：情绪周期定位器准确率由 G21 评估（[28_sentiment_cycle_trading](28_sentiment_cycle_trading.md) 待讨论），本 spec 假设定位器输出已就绪（phase_labels 数组），定位误差对相关性结论的影响在 §6 待裁定-3 跟踪
- **施工前必做**：本验证是首批 3 策略 StrategyBook 施工的门控——验证未通过则须重新审视策略组合，不可强行施工

## 3. 决策

### 3.1 架构定义

策略间相关性验证是一个**离线一次性 + 周期性复验**的验证 pipeline，由 12 个核心算法（含 1 个 Phase 2.0+评估项）串联，输出标准化验证报告：

```
[策略收益矩阵] ──→ ① compute_correlation_matrix ──→ 整体相关矩阵（Pearson+Spearman+Kendall Tau）
                          │
                          ↓
                   ② block_bootstrap_correlation ──→ 置信区间 + 显著性检验
                          │
                          ↓
[情绪周期标签] ──→ ③ layered_correlation_by_sentiment ──→ 5 阶段分层相关矩阵
                          │
                          ↓
                   ④ check_correlation_threshold ──→ 违规对清单 + 响应动作
                          │
                          ↓
                   ⑤ rolling_correlation_changepoint ──→ 滚动相关性 + CUSUM 变点检测
                          │
                          ↓
                   ⑥ dcc_garch_correlation ──→ DCC-GARCH 动态条件相关（Phase 2.0+评估）
                          │
                          ↓
                   ⑦ tail_dependence_analysis ──→ copula 尾部相依 + 分位数回归
                          │
                          ↓
                   ⑧ ledoit_wolf_shrinkage_covariance ──→ Ledoit-Wolf 收缩协方差（小样本稳定化）
                          │
                          ↓
                   ⑨ filter_rmt_noise_eigenvalues ──→ RMT 噪声过滤（Marchenko-Pastur）
                          │
                          ↓
                   ⑩ detect_multicollinearity_condition_number ──→ 条件数多重共线性检测
                          │
                          ↓
                   ⑪ detect_sentiment_beta_contamination ──→ 情绪 beta 污染检测（多证据融合）
                          │
                          ↓
                   ⑫ generate_validation_report ──→ 标准化报告（PASS/FAIL 判定）
```

**核心模块定位**：
- 验证模块属于 G23 回测框架对接（[52_backtest_framework_docking](52_backtest_framework_docking.md)）的下游消费者，不进入实盘信号路径
- 输入：各策略 backtest 收益序列（对齐到交易日）+ 情绪周期阶段标签（来自 G21 BM-SEL-23-B）
- 输出：标准化报告 dict，可序列化为 markdown / json，进入 G24 模拟实盘验证路径（[53_simulation_live_path](53_simulation_live_path.md)）的门控判断

**判定规则（核心纪律）**：

| 判定 | 条件 | 动作 |
|---|---|---|
| **PASS** | 所有策略对 |ρ| < 0.6 且 95% CI 上界 < 0.6 | 进入 StrategyBook 施工 |
| **CONDITIONAL_PASS** | 存在 0.6 ≤ ρ < 0.7 的对，但非"全阶段超阈值" | 允许施工，但需持续监控 + 复核 alpha 独立性 |
| **FAIL** | 任一 ρ ≥ 0.8，或任一对在所有 5 情绪阶段均 > 0.6 | 重新审视策略组合：合并 / 退役 / 差异化重设计 |

### 3.2 算法 ①：compute_correlation_matrix —— 5 候选策略两两相关矩阵（日/周/月三频率 × Pearson+Spearman+Kendall Tau 三维度）

```python
import numpy as np
from typing import Literal
from scipy.stats import kendalltau


def compute_correlation_matrix(
    strategy_returns: dict[str, np.ndarray],
    method: Literal["pearson", "spearman", "kendall", "all"] = "all",
    min_overlap: int = 60,
) -> dict:
    """
    计算 N 个策略两两相关矩阵（Pearson + Spearman 双口径）。

    Args:
        strategy_returns: {strategy_id: daily_returns_array}
            - 数组需已按交易日对齐（同一交易日索引）
            - 缺失日用 NaN 填充（如策略未上线日）
            - 推荐顺序: daban / multifactor / event_driven / value_reversal / momentum_trend
        method: "pearson" (线性相关) | "spearman" (秩相关，抗异常值/厚尾) | "kendall" (Kendall Tau 一致性) | "all" (默认三口径)
        min_overlap: 最小有效重叠样本数 (默认 60 交易日 ≈ 3 个月)
            - A 股 3 年回测 ≈ 732 交易日，60 是稳健下限
            - 低于此值的策略对留 NaN，标记 sample_insufficient

    Returns:
        {
            "pearson_matrix": np.ndarray,     # N×N Pearson 相关矩阵
            "spearman_matrix": np.ndarray,    # N×N Spearman 秩相关矩阵
            "kendall_matrix": np.ndarray,     # N×N Kendall Tau 相关矩阵
            "strategy_order": list[str],      # 策略顺序（与矩阵行列对齐）
            "n_overlap": np.ndarray,          # N×N 两两有效样本数矩阵
            "method_used": str,
        }

    设计依据:
        - Pearson 检测线性相关，但 A 股收益厚尾 → 异常值敏感
        - Spearman 秩相关抗异常值，是非正态分布的必备交叉验证
        - 两者差异大 → 提示存在异常值驱动的关系（如涨跌停日跳变）
    """
    strategy_ids = list(strategy_returns.keys())
    n = len(strategy_ids)

    # 构建对齐矩阵 (T × N)，NaN 填充缺失日
    max_len = max(len(r) for r in strategy_returns.values())
    R = np.full((max_len, n), np.nan)
    for j, sid in enumerate(strategy_ids):
        arr = np.asarray(strategy_returns[sid], dtype=float)
        R[: len(arr), j] = arr

    pearson = np.full((n, n), np.nan)
    spearman = np.full((n, n), np.nan)
    kendall = np.full((n, n), np.nan)
    n_overlap = np.zeros((n, n), dtype=int)

    for i in range(n):
        for j in range(i, n):
            # 仅取两策略都有有效收益的交易日
            mask = ~(np.isnan(R[:, i]) | np.isnan(R[:, j]))
            n_ov = int(mask.sum())
            n_overlap[i, j] = n_overlap[j, i] = n_ov
            if n_ov < min_overlap:
                continue  # 样本不足，留 NaN
            xi, xj = R[mask, i], R[mask, j]

            # Pearson: 线性相关
            if method in ("pearson", "both"):
                p = np.corrcoef(xi, xj)[0, 1]
                pearson[i, j] = pearson[j, i] = p

            # Spearman: 对秩做 Pearson（抗异常值）
            if method in ("spearman", "all"):
                ri = np.argsort(np.argsort(xi)).astype(float)
                rj = np.argsort(np.argsort(xj)).astype(float)
                s = np.corrcoef(ri, rj)[0, 1]
                spearman[i, j] = spearman[j, i] = s

            # Kendall Tau: 一致性对比例（小样本更稳，抗非线性）
            if method in ("kendall", "all"):
                from scipy.stats import kendalltau
                k, _ = kendalltau(xi, xj)
                kendall[i, j] = kendall[j, i] = k

    # 对角线自相关恒为 1
    np.fill_diagonal(pearson, 1.0)
    np.fill_diagonal(spearman, 1.0)
    np.fill_diagonal(kendall, 1.0)

    return {
        "pearson_matrix": pearson,
        "spearman_matrix": spearman,
        "kendall_matrix": kendall,
        "strategy_order": strategy_ids,
        "n_overlap": n_overlap,
        "method_used": method,
    }
```

#### 3.2.1 多频率收益聚合——日/周/月三频率

```python
from enum import Enum


class ReturnFrequency(Enum):
    """收益序列频率——多频率相关性验证的频率维度。

    换手率差异驱动的多频率必要性（20_first_batch_strategies §2.5）：
    - 打板换手 1-2 天 / 持仓 1-3 天 → 日度收益最能反映其 alpha 节奏
    - 多因子换手 3-5 天 / 持仓 5-20 天 → 周度收益更匹配其调仓周期
    - 事件驱动换手 2-3 天 / 持仓 2-10 天 → 日度/周度均可
    - 月度收益：消除日内噪声，暴露底层情绪 beta 共同驱动

    T+1 约束下的口径调整：
    - T+1 使日度收益存在 1 日滞后（当日信号次日才能执行）
    - 日度相关性可能因 T+1 滞后而低估真实共动（信号日错位）
    - 周度/月度聚合天然平滑 T+1 滞后，是更稳健的相关性估计口径
    - 三频率交叉验证：若日度低但月度高 → T+1 噪声掩盖了底层 beta 穿透
    """
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


def aggregate_returns_to_frequency(
    daily_returns: np.ndarray,
    trading_dates: np.ndarray,
    frequency: ReturnFrequency,
) -> tuple[np.ndarray, np.ndarray]:
    """
    将日度收益聚合为周度/月度收益——多频率相关性验证的数据基础。

    聚合方法：对数收益累加（乘法聚合），非简单算术求和。
    - 日度收益 r_t → 周期收益 R = ∏(1 + r_t) − 1
    - 等价于对数收益求和：ln(1 + R) = Σ ln(1 + r_t)

    频率对齐规则：
    - weekly：按日历周（W-FRI，周五收盘）聚合
    - monthly：按日历月（ME，月末最后交易日）聚合
    """
    import pandas as pd

    if frequency == ReturnFrequency.DAILY:
        return daily_returns, trading_dates

    df = pd.DataFrame(daily_returns, index=trading_dates)
    log_returns = np.log1p(df)

    if frequency == ReturnFrequency.WEEKLY:
        resampled = log_returns.resample("W-FRI").sum()
    elif frequency == ReturnFrequency.MONTHLY:
        resampled = log_returns.resample("ME").sum()
    else:
        raise ValueError(f"未知频率: {frequency}")

    resampled = resampled.dropna(how="all")
    agg_matrix = np.expm1(resampled.values)
    agg_dates = resampled.index

    return agg_matrix, agg_dates


def compute_multifrequency_correlation(
    daily_returns: np.ndarray,
    trading_dates: np.ndarray,
    strategy_ids: list[str],
    min_overlap: int = 60,
) -> dict:
    """
    计算日度/周度/月度三频率的两两相关矩阵。

    多频率交叉验证逻辑：
    - 日度低 + 月度高 → T+1 滞后/日内噪声掩盖了底层 beta 共动
    - 日度高 + 月度低 → 短线联动但中线独立（真差异化 alpha）
    - 三频率都高 → 稳健的结构性高相关（最危险，情绪 beta 深度穿透）

    判定取 max 的理由（López de Prado 虚假发现控制）：
    - 不同频率可能暴露不同的相关结构
    - 取 max 是保守策略：任一频率显示高相关即视为风险信号

    Returns:
        {
            "daily": compute_correlation_matrix 输出,
            "weekly": compute_correlation_matrix 输出,
            "monthly": compute_correlation_matrix 输出,
            "frequency_max": np.ndarray,  # (N,N) 三频率逐对取 max
            "frequency_disagreement": np.ndarray,  # (N,N) 三频率极差
            "dominant_frequency": dict,  # {(i,j): ReturnFrequency}
        }
    """
    freq_results = {}
    for freq in ReturnFrequency:
        agg_matrix, agg_dates = aggregate_returns_to_frequency(
            daily_returns, trading_dates, freq
        )
        returns_dict = {
            sid: agg_matrix[:, j] for j, sid in enumerate(strategy_ids)
        }
        freq_results[freq] = compute_correlation_matrix(
            returns_dict, method="all", min_overlap=min_overlap
        )

    n = len(strategy_ids)
    daily_max = freq_results[ReturnFrequency.DAILY]["pearson_matrix"].copy()
    weekly_max = freq_results[ReturnFrequency.WEEKLY]["pearson_matrix"].copy()
    monthly_max = freq_results[ReturnFrequency.MONTHLY]["pearson_matrix"].copy()

    stacked = np.stack([daily_max, weekly_max, monthly_max])
    freq_max = np.nanmax(stacked, axis=0)
    freq_disagree = np.nanmax(stacked, axis=0) - np.nanmin(stacked, axis=0)

    dominant = {}
    for i in range(n):
        for j in range(i + 1, n):
            vals = {
                ReturnFrequency.DAILY: daily_max[i, j],
                ReturnFrequency.WEEKLY: weekly_max[i, j],
                ReturnFrequency.MONTHLY: monthly_max[i, j],
            }
            dominant[(i, j)] = max(
                vals, key=lambda k: vals[k] if not np.isnan(vals[k]) else -1
            )

    return {
        "daily": freq_results[ReturnFrequency.DAILY],
        "weekly": freq_results[ReturnFrequency.WEEKLY],
        "monthly": freq_results[ReturnFrequency.MONTHLY],
        "frequency_max": freq_max,
        "frequency_disagreement": freq_disagree,
        "dominant_frequency": dominant,
    }
```
### 3.3 算法 ②：block_bootstrap_correlation —— Morwane 范式时序保留重采样

```python
def block_bootstrap_correlation(
    returns: np.ndarray,
    block_size: int = 10,
    n_bootstrap: int = 2000,
    confidence_levels: tuple[float, ...] = (0.90, 0.95),
    rng_seed: int | None = 42,
) -> dict:
    """
    Morwane 范式 block-bootstrap 相关性验证。

    保留时序结构（自相关、波动率聚集、情绪周期持续性）的重采样，比 iid
    bootstrap 更适合金融收益序列——iid bootstrap 会低估方差、置信区间过窄。

    本函数返回 N×N 相关矩阵的 bootstrap 分布与置信区间，用于:
        - 评估点估计相关系数是否统计显著（CI 是否含 0）
        - 评估相关性估计的稳定性（CI 宽度）
        - 对齐 Morwane OOS 2013-2026 验证范式（21-day blocks / 2000× resample）

    Args:
        returns: T × N 日度收益矩阵（列对齐各策略，已按交易日对齐）
        block_size: 块大小（默认 10 天）
            - Morwane 用 21 天（美股自相关结构较长）
            - A 股情绪周期短期自相关约 3-7 天，block_size 取 5-10 天
              既保留自相关结构，又避免块内周期过长导致块间独立性丧失
            - 建议敏感性分析: block_size ∈ {5, 7, 10}
        n_bootstrap: 重采样次数（默认 2000，Morwane 范式）
        confidence_levels: 置信水平（默认 90% + 95%）
        rng_seed: 随机种子（可复现）

    Returns:
        {
            "point_estimate": np.ndarray,    # N×N 点估计相关矩阵
            "bootstrap_means": np.ndarray,   # N×N bootstrap 均值
            "bootstrap_stds": np.ndarray,    # N×N bootstrap 标准差
            "ci_90": np.ndarray,             # N×N×2 90% CI (lower, upper)
            "ci_95": np.ndarray,             # N×N×2 95% CI (lower, upper)
            "p_value_zero": np.ndarray,      # N×N P(ρ ≤ 0) 单边检验
            "n_bootstrap": int,
            "block_size": int,
        }

    设计依据:
        - 金融收益序列自相关 → iid bootstrap 方差估计偏低
        - block-bootstrap 保留块内时序结构，块间有放回抽样
        - 百分位法 CI 比正态假设 CI 更鲁棒（相关系数分布偏斜，非正态）
    """
    rng = np.random.default_rng(rng_seed)
    T, N = returns.shape

    # 去除任一列含 NaN 的行（保持列对齐）
    valid = ~np.isnan(returns).any(axis=1)
    R = returns[valid]
    T_valid = R.shape[0]
    n_blocks = int(np.ceil(T_valid / block_size))

    # 点估计
    point_est = np.corrcoef(R, rowvar=False)
    np.fill_diagonal(point_est, 1.0)

    boot_samples = np.zeros((n_bootstrap, N, N))
    for b in range(n_bootstrap):
        # 随机抽取块起始位置（有放回），拼接成 bootstrap 样本
        starts = rng.integers(0, T_valid - block_size + 1, size=n_blocks)
        idx = np.concatenate([np.arange(s, s + block_size) for s in starts])
        idx = idx[:T_valid]  # 截断至原长度
        Rb = R[idx]

        # 防退化：块内常数或零方差时跳过本次
        stds = Rb.std(axis=0, ddof=1)
        if (stds < 1e-10).any():
            continue
        cb = np.corrcoef(Rb, rowvar=False)
        if not np.isnan(cb).any():
            boot_samples[b] = cb

    boot_means = boot_samples.mean(axis=0)
    boot_stds = boot_samples.std(axis=0, ddof=1)
    np.fill_diagonal(boot_means, 1.0)
    np.fill_diagonal(boot_stds, 0.0)

    # 置信区间（百分位法，比正态假设鲁棒）
    cis = {}
    for cl in confidence_levels:
        alpha = (1 - cl) / 2
        lo = np.percentile(boot_samples, 100 * alpha, axis=0)
        hi = np.percentile(boot_samples, 100 * (1 - alpha), axis=0)
        np.fill_diagonal(lo, 1.0)
        np.fill_diagonal(hi, 1.0)
        cis[f"ci_{int(cl * 100)}"] = np.stack([lo, hi], axis=-1)  # N×N×2

    # 单边检验 P(ρ > 0)：bootstrap 样本中 ρ ≤ 0 的比例
    p_zero = (boot_samples <= 0).mean(axis=0)
    np.fill_diagonal(p_zero, 0.0)

    return {
        "point_estimate": point_est,
        "bootstrap_means": boot_means,
        "bootstrap_stds": boot_stds,
        **cis,
        "p_value_zero": p_zero,
        "n_bootstrap": n_bootstrap,
        "block_size": block_size,
    }
```

### 3.4 算法 ③：layered_correlation_by_sentiment —— 按情绪周期 5 阶段分层

```python
SENTIMENT_PHASES = ("freezing", "reversal", "main_upthrust", "mania", "retreat")
# 中文映射: 冰点 / 反核 / 主升 / 疯狂 / 退潮
# 来自 BM-SEL-23-B 情绪周期 4+1 阶段定位器（G21 待评估准确率）


def layered_correlation_by_sentiment(
    strategy_returns: dict[str, np.ndarray],
    sentiment_phases: dict,
    min_samples_per_phase: int = 20,
    method: Literal["pearson", "spearman"] = "pearson",
    use_soft_assignment: bool = True,
) -> dict:
    """
    按情绪周期 5 阶段（冰点/反核/主升/疯狂/退潮）分层计算策略相关矩阵。

    情绪周期是所有短周期策略的"隐形驱动"（30_multi_strategy_concurrency §1.3）。
    若各阶段相关性均 >0.6，则"多策略实为情绪 beta 穿多件衣服"——需重新审视
    策略组合是否真正分散（30_multi_strategy_concurrency §6.2 核心判据）。

    分层逻辑:
        - 在每个阶段子集内重新计算相关矩阵
        - 关注"情绪极端态"（疯狂/退潮）的相关性——这些是情绪 beta 集中暴露期
        - 跨阶段一致性检验: 若所有阶段均 >0.6 → 情绪 beta 穿多件衣服（FAIL）
        - 若仅个别阶段 >0.6 → 情绪放大效应，可监控（CONDITIONAL_PASS）

    Args:
        strategy_returns: {strategy_id: T 日收益数组}
        sentiment_phases: {
            "phase_labels": np.ndarray[T] 硬标签 (0-4),
            "phase_probs": np.ndarray[T×5] 软概率 (可选, use_soft_assignment=True 时启用)
        }
            phase 顺序: 0=冰点, 1=反核, 2=主升, 3=疯狂, 4=退潮
            - 软概率来自情绪周期定位器灰度输出（对齐 regime 12 态灰度范式）
            - 软分配按 phase_prob > 0.5 判定主属阶段，避免硬切换样本损失
        min_samples_per_phase: 每阶段最少样本数（默认 20 日）
            - 不足则该阶段标 NaN，状态 INSUFFICIENT_SAMPLES
            - 疯狂/冰点为稀有阶段，可能不足 20 日 → 用软分配缓解
        method: "pearson" | "spearman"
        use_soft_assignment: 是否使用软概率分配（推荐 True，对齐灰度范式）

    Returns:
        {
            "phase_matrices": {phase_name: np.ndarray},      # 各阶段 N×N 相关矩阵
            "phase_sample_counts": {phase_name: int},         # 各阶段样本数
            "phase_above_threshold": {phase_name: np.ndarray},# 各阶段 >0.6 标志矩阵
            "max_phase_correlation": np.ndarray,              # N×N 各对在所有阶段的最大值
            "consistent_above_threshold": np.ndarray,         # N×N 是否所有阶段均 >0.6
                                                              # （情绪 beta 穿多件衣服的严格判定）
            "strategy_order": list[str],
        }

    设计依据:
        - 情绪周期是隐形驱动 → 整体相关矩阵可能掩盖阶段性集中暴露
        - 主升/疯狂态: 情绪 beta 高浓度期，相关性可能飙升
        - 冰点/退潮态: 情绪冷却，相关性回落 → 真 alpha 差异显现
        - 跨阶段一致性是"情绪 beta 穿多件衣服"的核心判据
    """
    phase_labels = sentiment_phases["phase_labels"]
    phase_probs = sentiment_phases.get("phase_probs")

    strategy_ids = list(strategy_returns.keys())
    n = len(strategy_ids)
    T = len(phase_labels)

    # 对齐收益矩阵
    R = np.full((T, n), np.nan)
    for j, sid in enumerate(strategy_ids):
        arr = np.asarray(strategy_returns[sid], dtype=float)
        R[: len(arr), j] = arr

    phase_matrices = {}
    phase_counts = {}
    phase_above = {}
    max_corr = np.full((n, n), np.nan)
    all_above = np.ones((n, n), dtype=bool)  # 默认 True，遇任一阶段 <0.6 即置 False

    for ph_idx, ph_name in enumerate(SENTIMENT_PHASES):
        # 软分配: 主属该阶段（prob > 0.5）；硬分配: label == ph_idx
        if use_soft_assignment and phase_probs is not None:
            mask = phase_probs[:, ph_idx] > 0.5
        else:
            mask = (phase_labels == ph_idx)

        n_ph = int(mask.sum())
        phase_counts[ph_name] = n_ph

        if n_ph < min_samples_per_phase:
            # 样本不足，标 NaN，无法判定 → 视为不通过（保守）
            phase_matrices[ph_name] = np.full((n, n), np.nan)
            phase_above[ph_name] = np.full((n, n), False)
            all_above[:, :] = False
            continue

        R_ph = R[mask]
        # 复用算法 ① 的成对相关计算（处理 NaN + min_overlap）
        sub = compute_correlation_matrix(
            {sid: R_ph[:, j] for j, sid in enumerate(strategy_ids)},
            method=method,
            min_overlap=min_samples_per_phase,
        )
        M = sub["pearson_matrix"] if method == "pearson" else sub["spearman_matrix"]
        phase_matrices[ph_name] = M

        # 阈值检查（跳过对角线）
        above = (M > 0.6)
        np.fill_diagonal(above, False)
        phase_above[ph_name] = above

        off_diag = M.copy()
        np.fill_diagonal(off_diag, np.nan)
        # 跨阶段累计最大值
        with np.errstate(invalid="ignore"):
            max_corr = np.nanmax(
                np.stack([max_corr, off_diag], axis=0),
                axis=0,
            )
        # 跨阶段一致性: 所有阶段（样本充足）均 >0.6 才为 True
        all_above &= (off_diag > 0.6)

    return {
        "phase_matrices": phase_matrices,
        "phase_sample_counts": phase_counts,
        "phase_above_threshold": phase_above,
        "max_phase_correlation": max_corr,
        "consistent_above_threshold": all_above,
        "strategy_order": strategy_ids,
    }
```

### 3.5 算法 ④：check_correlation_threshold —— "情绪 beta 穿多件衣服"检测

```python
def check_correlation_threshold(
    corr_matrix: np.ndarray,
    threshold: float = 0.6,
    strategy_ids: list[str] | None = None,
    check_type: Literal["any_above", "majority_above", "all_phases_above"] = "any_above",
) -> list[dict]:
    """
    相关性阈值检查——检测"多策略实为情绪 beta 穿多件衣服"。

    阈值 0.6 的依据:
        - 30_multi_strategy_concurrency §6.2 明确 ">0.6 需重新审视"
        - 行业经验: 策略两两相关 >0.6 时分散化收益急剧衰减
          （5 策略有效 N 从 5 降至 ~2）
        - Morwane 范式: 两 sleeve 弱相关 (ρ=+0.03) 是多策略价值的根基

    检查模式:
        - "any_above": 任一对 > threshold 即报警（保守，用于整体相关矩阵）
        - "majority_above": 过半数对 > threshold 报警（用于整体相关矩阵）
        - "all_phases_above": 配合 layered_correlation_by_sentiment 使用，
          所有情绪阶段均 > threshold 才报警——这是"情绪 beta 穿多件衣服"
          的严格判定（输入应为 consistent_above_threshold 矩阵）

    Args:
        corr_matrix: N×N 相关矩阵
            - 整体检查: 用 pearson_matrix / spearman_matrix
            - 跨阶段检查: 用 layered["consistent_above_threshold"]
            - 极值检查: 用 layered["max_phase_correlation"]
        threshold: 阈值（默认 0.6）
        strategy_ids: 策略 ID 列表（与矩阵行列对齐）
        check_type: "any_above" | "majority_above" | "all_phases_above"

    Returns:
        违规对列表，每项含:
        {
            "strategy_pair": tuple[str, str],
            "correlation": float,
            "violation_type": str,
            "threshold": float,
            "severity": "low" | "medium" | "high",
            "action_required": str,
        }

    严重度分级:
        - low:    0.6 < ρ ≤ 0.7   → 持续监控，复核 alpha 独立性
        - medium: 0.7 < ρ ≤ 0.8   → 须论证 alpha 差异性或下调权重
        - high:   ρ > 0.8         → 强烈建议合并或退役其一
    """
    n = corr_matrix.shape[0]
    if strategy_ids is None:
        strategy_ids = [f"S{i}" for i in range(n)]

    violations = []
    n_pairs = 0
    n_above = 0

    for i in range(n):
        for j in range(i + 1, n):
            rho = corr_matrix[i, j]
            if np.isnan(rho):
                continue
            n_pairs += 1
            if rho > threshold:
                n_above += 1
                violations.append({
                    "strategy_pair": (strategy_ids[i], strategy_ids[j]),
                    "correlation": float(rho),
                    "violation_type": check_type,
                    "threshold": threshold,
                    "severity": _severity_level(rho),
                    "action_required": _action_for_violation(rho, check_type),
                })

    # majority 模式: 仅当过半数对超阈值时整体报警
    if check_type == "majority_above" and n_pairs > 0 and n_above <= n_pairs / 2:
        violations = []

    return violations


def _severity_level(rho: float) -> str:
    """根据相关系数确定严重度。"""
    if rho > 0.8:
        return "high"
    if rho > 0.7:
        return "medium"
    return "low"


def _action_for_violation(rho: float, check_type: str) -> str:
    """根据相关系数与检查类型决定响应动作。"""
    if check_type == "all_phases_above":
        return (
            "REVIEW_STRATEGY_COMBINATION: 所有情绪阶段均 >0.6 → "
            "多策略实为情绪 beta 穿多件衣服，需重新审视（合并/退役/差异化重设计）"
        )
    if rho > 0.8:
        return "MERGE_OR_RETIRE: ρ>0.8 → 强烈建议合并或退役其一"
    if rho > 0.7:
        return "DIFFERENTIATE_OR_DEWEIGHT: ρ>0.7 → 须论证 alpha 差异性或下调 sleeve 权重"
    return "MONITOR: ρ>0.6 → 持续监控，复核 alpha 来源是否真正独立"
```

### 3.6 算法 ⑤：rolling_correlation_changepoint —— 60 日滚动相关性 + CUSUM 变点检测

```python
def rolling_correlation_changepoint(
    returns: np.ndarray,
    window: int = 60,
    high_threshold: float = 0.6,
    cusum_threshold: float = 5.0,
    min_distance: int = 30,
    strategy_ids: list[str] | None = None,
) -> list[dict]:
    """
    60 日滚动相关性 + CUSUM 变点检测——揭露相关性随时间的漂移与结构性断裂。

    价值（López de Prado 相关性非平稳性 + Page 1954 / Killick et al. 2012 PELT）：
    - 整体相关矩阵是全样本均值，可能掩盖"近期相关性上升"的趋势
    - 例：2024 年相关性 0.2，2025 年升至 0.7——全样本看 0.4（中风险），
      但实际已演变为高风险。滚动窗口揭露这种漂移
    - 60 日窗口（≈3 个月）：平衡灵敏度与稳定性
    - CUSUM 检测滚动序列的结构性变点：策略 alpha 漂移 / 情绪周期切换 /
      市场结构性变化（如 2024-09 行情切换）导致的相关性断裂

    与 §3.4 分层 + §3.8 尾部相关性的关系：
    - 分层按情绪周期切（横切），滚动按时间切（纵切），尾部按极端值切（尾切）
    - 三者正交互补，三重证据都显示高相关 → 稳健判定
    - 变点检测定位"何时相关性发生突变"，给后续归因（G25）提供时间锚点

    CUSUM 算法（Page 1954）：
    - 对滚动相关序列 r_t，计算偏离均值的累积和
    - S_t = max(0, S_{t-1} + (r_t - mu - k))  （上升变点检测）
    - S_t = max(0, S_{t-1} + (-r_t + mu - k)) （下降变点检测）
    - 当 S_t > h（阈值）时报警变点
    - k = 0.5*sigma（容差），h = 5*sigma（报警阈值）——工业控制经典参数

    Args:
        returns: T × N 日度收益矩阵（列对齐各策略）
        window: 滚动窗口（默认 60 日 ≈ 3 个月）
        high_threshold: 高风险阈值（默认 0.6，对齐 §3.5 check_correlation_threshold）
        cusum_threshold: CUSUM 报警阈值（默认 5.0，即 5 倍标准差）
            - 工业控制经典值 h=4~5，金融序列噪声大取 5.0
        min_distance: 相邻变点最小间距（默认 30 日，避免密集变点）
        strategy_ids: 策略 ID 列表

    Returns:
        每个策略对的滚动+变点分析结果列表:
        {
            "strategy_pair": tuple[str, str],
            "window": int,
            "rolling_series": np.ndarray,       # T 长度滚动相关序列（前 window-1 个为 NaN）
            "max_rolling": float,               # 滚动序列最大值
            "mean_rolling": float,               # 滚动序列均值
            "is_increasing": bool,               # 是否呈上升趋势（线性回归斜率 > 0.001）
            "crossed_high_threshold": bool,       # 是否曾越过 0.6
            "cross_ratio": float,                # 越过 0.6 的样本比例
            "change_points": list[int],          # CUSUM 检测到的变点位置（交易日索引）
            "n_change_points": int,              # 变点数量
            "segment_means": list[float],        # 各变点分段的相关性均值
            "max_segment_jump": float,           # 相邻分段均值最大跳变幅度
            "stability_verdict": str,            # "stable" | "drifting" | "regime_shift"
        }

    稳定性判定规则:
        - "stable":        无变点 + 不上升 + 未越阈值 → 相关性结构稳定
        - "drifting":      有上升趋势或越过阈值但无变点 → 渐进漂移，监控
        - "regime_shift":  有变点且分段均值跳变 >0.15 → 结构性断裂，须归因
    """
    T, N = returns.shape
    if strategy_ids is None:
        strategy_ids = [f"S{i}" for i in range(N)]

    results = []
    for i in range(N):
        for j in range(i + 1, N):
            x, y = returns[:, i], returns[:, j]
            rc = np.full(T, np.nan)
            for t in range(window, T):
                xw, yw = x[t - window:t], y[t - window:t]
                mask = ~(np.isnan(xw) | np.isnan(yw))
                if mask.sum() >= window * 0.8:
                    rc[t] = np.corrcoef(xw[mask], yw[mask])[0, 1]

            valid_mask = ~np.isnan(rc)
            valid = rc[valid_mask]
            if len(valid) == 0:
                continue

            valid_idx = np.where(valid_mask)[0]
            # 趋势检测：线性回归斜率
            slope = np.polyfit(np.arange(len(valid)), valid, 1)[0]
            is_increasing = slope > 0.001

            crossed = valid > high_threshold
            cross_ratio = float(crossed.mean()) if len(crossed) > 0 else 0.0

            # ===== CUSUM 变点检测 =====
            change_points = _cusum_changepoint_detection(
                valid, threshold=cusum_threshold, min_distance=min_distance
            )
            # 映射回原始时间索引
            change_points = [int(valid_idx[cp]) for cp in change_points]

            # 分段均值
            segment_means = _compute_segment_means(valid, change_points)
            max_jump = 0.0
            for k in range(1, len(segment_means)):
                jump = abs(segment_means[k] - segment_means[k - 1])
                max_jump = max(max_jump, jump)

            # 稳定性判定
            if len(change_points) == 0 and not is_increasing and not crossed.any():
                verdict = "stable"
            elif len(change_points) > 0 and max_jump > 0.15:
                verdict = "regime_shift"
            else:
                verdict = "drifting"

            results.append({
                "strategy_pair": (strategy_ids[i], strategy_ids[j]),
                "window": window,
                "rolling_series": rc,
                "max_rolling": float(np.nanmax(valid)),
                "mean_rolling": float(np.nanmean(valid)),
                "is_increasing": bool(is_increasing),
                "crossed_high_threshold": bool(crossed.any()),
                "cross_ratio": cross_ratio,
                "change_points": change_points,
                "n_change_points": len(change_points),
                "segment_means": segment_means,
                "max_segment_jump": float(max_jump),
                "stability_verdict": verdict,
            })

    return results


def _cusum_changepoint_detection(
    series: np.ndarray,
    threshold: float = 5.0,
    min_distance: int = 30,
) -> list[int]:
    """
    CUSUM 变点检测算法（Page 1954）。

    双边 CUSUM：
        S_high_t = max(0, S_high_{t-1} + (x_t - mu - k))   检测上升变点
        S_low_t  = max(0, S_low_{t-1} + (-x_t + mu - k))   检测下降变点
        当 S > h 时报警变点，重置 S=0

    参数:
        k = 0.5 * sigma  （容差，吸收正常波动）
        h = threshold * sigma  （报警阈值，默认 5 sigma）

    变点后向后跳 min_distance 个样本再继续检测，避免密集变点。

    返回变点在 series 中的索引列表。
    """
    if len(series) < 10:
        return []

    sigma = np.std(series, ddof=1)
    if sigma < 1e-10:
        return []

    mu = np.mean(series)
    k = 0.5 * sigma
    h = threshold * sigma

    s_high = 0.0
    s_low = 0.0
    change_points = []
    last_cp = -min_distance

    for t in range(len(series)):
        s_high = max(0.0, s_high + (series[t] - mu - k))
        s_low = max(0.0, s_low + (-series[t] + mu - k))

        if s_high > h or s_low > h:
            if t - last_cp >= min_distance:
                change_points.append(t)
                last_cp = t
            s_high = 0.0
            s_low = 0.0

    return change_points


def _compute_segment_means(series: np.ndarray, change_points: list[int]) -> list[float]:
    """计算变点分段后的各段均值。"""
    if len(change_points) == 0:
        return [float(np.mean(series))]

    boundaries = [0] + change_points + [len(series)]
    means = []
    for k in range(len(boundaries) - 1):
        seg = series[boundaries[k]:boundaries[k + 1]]
        if len(seg) > 0:
            means.append(float(np.mean(seg)))
    return means
```

### 3.7 算法 ⑥：dcc_garch_correlation —— DCC-GARCH 动态条件相关（Phase 2.0+ 评估）

> **Phase 标记**：本算法为 Phase 2.0+ 参数化动态相关增强项（§6 待裁定-4），首批 3 策略施工前 NOT MUST。伪代码预置以便 track record 满 6 个月后直接落码。

**动机**：滚动窗口（算法 ⑤）是非参数的局部估计（60 日滑动），无法分离波动率聚集（GARCH 效应）与相关性动态。Engle (2002) DCC-GARCH 两阶段法——先逐列拟合 GARCH(1,1) 标准化残差剥离波动率聚集，再对标准化残差做动态条件相关滤波——系统化检测相关性时变结构。

```python
def dcc_garch_correlation(
    returns: np.ndarray,
    strategy_ids: list[str] | None = None,
    sentiment_phases: dict | None = None,
    alpha_dcc: float = 0.02,
    beta_dcc: float = 0.94,
) -> dict:
    """
    DCC-GARCH 动态条件相关（Engle 2002）。

    两阶段法：
      Stage 1: 逐列拟合 GARCH(1,1)，取标准化残差 z_t = eps_t / sigma_t
      Stage 2: 对 z_t 做 DCC 滤波，得动态相关矩阵序列 R_t

    Parameters
    ----------
    returns : (T, N) 日度收益率矩阵
    strategy_ids : 策略 ID 列表
    sentiment_phases : 情绪周期阶段标签（可选，用于分层均值）
    alpha_dcc, beta_dcc : DCC 参数（典型值 a=0.02, b=0.94）

    Returns
    -------
    dynamic_correlations : (T, N, N) 动态相关矩阵序列
    phase_mean_corr : 各情绪阶段平均相关矩阵
    emotion_beta_penetration : 情绪 beta 穿透检测结果
    """
    T, N = returns.shape
    strategy_ids = strategy_ids or [f"S{i}" for i in range(N)]

    # -- Stage 1: 逐列 GARCH(1,1) 标准化残差 --
    z = np.zeros_like(returns)
    cond_vol = np.zeros_like(returns)
    for i in range(N):
        z[:, i], cond_vol[:, i] = _fit_univariate_garch11(returns[:, i])

    # -- Stage 2: DCC 滤波 --
    Q_bar = np.cov(z.T)  # (N, N)
    Q = Q_bar.copy()
    R_series = np.zeros((T, N, N))

    for t in range(T):
        if t > 0:
            z_lag = z[t - 1].reshape(-1, 1)  # (N, 1)
            Q = (1 - alpha_dcc - beta_dcc) * Q_bar \
                + alpha_dcc * (z_lag @ z_lag.T) \
                + beta_dcc * Q
        d_inv = 1.0 / np.sqrt(np.diag(Q))
        R_series[t] = Q * d_inv[:, None] * d_inv[None, :]

    # -- 按情绪周期分层求均值相关 --
    phase_names = ["freezing", "reversal", "main_upthrust", "mania", "retreat"]
    phase_mean = {}
    if sentiment_phases:
        phase_labels = sentiment_phases["phase_labels"]
        for ph_idx, ph_name in enumerate(phase_names):
            mask = phase_labels == ph_idx
            if mask.sum() >= 5:
                phase_mean[ph_name] = np.nanmean(R_series[mask], axis=0)

    # -- 情绪 beta 穿透检测 --
    is_penetration = False
    if phase_mean:
        is_penetration = (alpha_dcc + beta_dcc > 0.9) and any(
            np.nanmax(mat[~np.eye(mat.shape[0], dtype=bool)]) > 0.6
            for mat in phase_mean.values()
        )

    return {
        "dynamic_correlations": R_series,
        "phase_mean_corr": phase_mean,
        "emotion_beta_penetration": {
            "is_penetration": is_penetration,
            "dcc_alpha": alpha_dcc,
            "dcc_beta": beta_dcc,
            "persistence": alpha_dcc + beta_dcc,
        },
    }


def _fit_univariate_garch11(
    returns: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """
    单变量 GARCH(1,1) 拟合（Bollerslev 1986）。

    sigma2_t = omega + alpha * eps2_{t-1} + beta * sigma2_{t-1}
    z_t = eps_t / sigma_t  （标准化残差）

    参数估计用 MLE（正态假设），小样本下退化为样本方差 + GARCH 参数典型值。
    Phase 2.0+ 落码时替换为 arch 库的 MLE 估计。
    """
    T = len(returns)
    eps = returns - np.nanmean(returns)
    var_uncond = np.nanvar(returns)
    omega = var_uncond * 0.01
    alpha_g = 0.05
    beta_g = 0.90

    sigma2 = np.full(T, var_uncond)
    for t in range(1, T):
        if not np.isnan(eps[t - 1]):
            sigma2[t] = omega + alpha_g * eps[t - 1] ** 2 + beta_g * sigma2[t - 1]
        else:
            sigma2[t] = sigma2[t - 1]

    cond_vol = np.sqrt(sigma2)
    z = np.where(cond_vol > 0, eps / cond_vol, 0.0)
    return z, cond_vol
```

**关键约束**：
- **小样本过拟合风险**：5 策略 × <252 天样本下，DCC 参数 (a, b) MLE 估计不稳定，首批 Phase 1.0 不启用
- **与算法 ⑤ 的分工**：滚动窗口是非参数的（60 日滑动），DCC 是参数化的（全样本估动态）；Phase 1.0 用非参数滚动，Phase 2.0+ 加 DCC 对比
- **Phase 启用条件**：track record 满 6 个月 + 策略数 >= 5（§6 待裁定-4）

**与算法 ④（情绪 beta 穿透检测）的协同**：
- 算法 ④ 用静态分层相关矩阵检测穿透（全样本分层）
- 算法 ⑥ 用动态相关矩阵的分层均值检测穿透（时变分层）
- 两者交叉验证：若静态检测 PASS 但动态检测 FAIL -> 相关性虽当前低但时变结构有穿透风险

### 3.8 算法 ⑦：tail_dependence_analysis —— copula 尾部相依 + 分位数回归


```python
def tail_dependence_analysis(
    returns: np.ndarray,
    strategy_ids: list[str] | None = None,
    quantiles: tuple[float, ...] = (0.05, 0.25, 0.75, 0.95),
    tail_threshold: float = 0.3,
    n_bootstrap: int = 1000,
    rng_seed: int | None = 42,
) -> list[dict]:
    """
    尾部相关性分析——copula 尾部相依系数 + 分位数回归。

    价值（Nelsen 2006 / Joe 1997 / Koenker 2005）：
    - 整体相关系数（Pearson/Spearman）描述"平均"相关性，但极端行情下相关性
      可能飙升（"尾部相依"）——这正是多策略同时亏损的风险源头
    - 2008 金融危机 / 2015 A 股股灾 / 2024-09 行情切换：极端日所有策略同步
      下跌，整体相关 0.3 但尾部相依 0.8 → 真正的尾部风险被掩盖
    - copula 尾部相依系数 lambda_upper/lambda_lower 量化极端共动概率
    - 分位数回归在 tau=0.05/0.95 检测极端分位下的条件关系斜率

    copula 尾部相依定义（Nelsen 2006）：
        lambda_upper = lim_{u->1} P(U > u | V > u)   （上尾相依）
        lambda_lower = lim_{u->0} P(U < u | V < u)   （下尾相依）
        lambda > 0 = 尾部相依；lambda = 0 = 尾部独立
        经验 copula 估计：取极端分位样本的条件频率

    分位数回归（Koenker 2005）：
        Q_tau(y | x) = alpha_tau + beta_tau * x
        tau=0.05（左尾）、tau=0.95（右尾）的 beta_tau 显著大于 tau=0.5（中位数）
        → 尾部相关性突变的证据
        beta_tau(0.95) - beta_tau(0.5) > delta → 上尾相关性增强
        beta_tau(0.05) - beta_tau(0.5) > delta → 下尾相关性增强（共跌风险）

    与 §3.3 block-bootstrap + §3.6 滚动相关性的关系：
    - block-bootstrap 估 CI（整体相关显著性）
    - 滚动窗口检测时间漂移（时变结构）
    - 尾部相依检测极端态共动（尾部风险结构）
    - 三者正交：均值层 / 时间层 / 尾部层，三重证据都高 → 最危险

    Args:
        returns: T × N 日度收益矩阵
        strategy_ids: 策略 ID 列表
        quantiles: 分位数回归的分位水平（默认 0.05/0.25/0.75/0.95）
            tau=0.05/0.95 是尾部检测核心；tau=0.25/0.75 是对照
        tail_threshold: 尾部相依系数的报警阈值（默认 0.3）
            - lambda > 0.3 → 显著尾部相依（共跌/共涨风险）
            - 经验：lambda > 0.5 为高尾部相依，策略组合在极端态无分散效果
        n_bootstrap: 尾部相依系数的 bootstrap 次数（估 CI）
        rng_seed: 随机种子

    Returns:
        每个策略对的尾部分析结果列表:
        {
            "strategy_pair": tuple[str, str],
            "lambda_upper": float,           # 上尾相依系数
            "lambda_lower": float,           # 下尾相依系数
            "lambda_upper_ci": tuple,        # 上尾相依 95% CI
            "lambda_lower_ci": tuple,        # 下尾相依 95% CI
            "tail_dependent": bool,          # 是否尾部相依（lambda > tail_threshold）
            "quantile_slopes": dict,         # {tau: beta_tau} 各分位回归斜率
            "tail_asymmetry": float,         # beta(0.95) - beta(0.05) 尾部不对称性
            "extreme_co_move_probability": float,  # 极端共动概率 P(both<5%ile)
            "tail_risk_verdict": str,        # "tail_independent" | "tail_dependent" | "asymmetric_tail"
        }

    尾部风险判定规则:
        - "tail_independent":  lambda_upper < 0.3 且 lambda_lower < 0.3 → 尾部独立，分散有效
        - "tail_dependent":    lambda_upper >= 0.3 或 lambda_lower >= 0.3 → 尾部相依，极端态分散失效
        - "asymmetric_tail":   |beta(0.95) - beta(0.05)| > 0.2 → 尾部不对称（共跌不共涨或反之）
    """
    rng = np.random.default_rng(rng_seed)
    T, N = returns.shape
    if strategy_ids is None:
        strategy_ids = [f"S{i}" for i in range(N)]

    results = []
    for i in range(N):
        for j in range(i + 1, N):
            x, y = returns[:, i], returns[:, j]
            mask = ~(np.isnan(x) | np.isnan(y))
            x_clean, y_clean = x[mask], y[mask]
            if len(x_clean) < 60:
                continue

            # ===== 1. 经验 copula 尾部相依系数 =====
            lam_upper, lam_lower = _empirical_tail_dependence(x_clean, y_clean)

            # bootstrap CI for tail dependence
            lam_up_boot = np.zeros(n_bootstrap)
            lam_lo_boot = np.zeros(n_bootstrap)
            for b in range(n_bootstrap):
                idx = rng.integers(0, len(x_clean), size=len(x_clean))
                lu, ll = _empirical_tail_dependence(x_clean[idx], y_clean[idx])
                lam_up_boot[b] = lu
                lam_lo_boot[b] = ll
            lam_upper_ci = (
                float(np.percentile(lam_up_boot, 2.5)),
                float(np.percentile(lam_up_boot, 97.5)),
            )
            lam_lower_ci = (
                float(np.percentile(lam_lo_boot, 2.5)),
                float(np.percentile(lam_lo_boot, 97.5)),
            )

            # ===== 2. 分位数回归（Koenker 2005）=====
            slopes = {}
            for tau in quantiles:
                beta_tau = _quantile_regression_slope(x_clean, y_clean, tau)
                slopes[tau] = float(beta_tau)

            # 尾部不对称性
            if 0.05 in slopes and 0.95 in slopes:
                tail_asymmetry = slopes[0.95] - slopes[0.05]
            else:
                tail_asymmetry = 0.0

            # 极端共动概率 P(both < 5%ile)
            q5_x = np.percentile(x_clean, 5)
            q5_y = np.percentile(y_clean, 5)
            extreme_co = float(np.mean((x_clean < q5_x) & (y_clean < q5_y)))

            # 判定
            tail_dependent = lam_upper >= tail_threshold or lam_lower >= tail_threshold
            if not tail_dependent and abs(tail_asymmetry) > 0.2:
                verdict = "asymmetric_tail"
            elif tail_dependent:
                verdict = "tail_dependent"
            else:
                verdict = "tail_independent"

            results.append({
                "strategy_pair": (strategy_ids[i], strategy_ids[j]),
                "lambda_upper": float(lam_upper),
                "lambda_lower": float(lam_lower),
                "lambda_upper_ci": lam_upper_ci,
                "lambda_lower_ci": lam_lower_ci,
                "tail_dependent": bool(tail_dependent),
                "quantile_slopes": slopes,
                "tail_asymmetry": float(tail_asymmetry),
                "extreme_co_move_probability": extreme_co,
                "tail_risk_verdict": verdict,
            })

    return results


def _empirical_tail_dependence(
    x: np.ndarray,
    y: np.ndarray,
    threshold_quantile: float = 0.95,
) -> tuple[float, float]:
    """
    经验 copula 尾部相依系数估计（Nelsen 2006 第5.4节）。

    lambda_upper = P(X > F_X^{-1}(u) | Y > F_Y^{-1}(u))   u -> 1
    lambda_lower = P(X < F_X^{-1}(u) | Y < F_Y^{-1}(u))   u -> 0

    经验估计：取 u = threshold_quantile（如 0.95），
    用样本频率估计条件概率。

    Args:
        x, y: 对齐的收益序列
        threshold_quantile: 尾部阈值分位（默认 0.95）
            - 0.95 对应 5% 极端样本
            - 样本不足时降低至 0.90（但置信度下降）

    Returns:
        (lambda_upper, lambda_lower)
    """
    n = len(x)
    if n < 30:
        return 0.0, 0.0

    # 上尾：X 超过 95%ile 时 Y 也超过 95%ile 的条件概率
    q_x_up = np.quantile(x, threshold_quantile)
    q_y_up = np.quantile(y, threshold_quantile)
    x_up = x > q_x_up
    y_up = y > q_y_up
    n_x_up = int(x_up.sum())
    if n_x_up > 0:
        lam_upper = float(np.sum(x_up & y_up) / n_x_up)
    else:
        lam_upper = 0.0

    # 下尾：X 低于 5%ile 时 Y 也低于 5%ile 的条件概率
    q_x_lo = np.quantile(x, 1 - threshold_quantile)
    q_y_lo = np.quantile(y, 1 - threshold_quantile)
    x_lo = x < q_x_lo
    y_lo = y < q_y_lo
    n_x_lo = int(x_lo.sum())
    if n_x_lo > 0:
        lam_lower = float(np.sum(x_lo & y_lo) / n_x_lo)
    else:
        lam_lower = 0.0

    return lam_upper, lam_lower


def _quantile_regression_slope(
    x: np.ndarray,
    y: np.ndarray,
    tau: float,
) -> float:
    """
    分位数回归斜率（Koenker 2005）——非参数估计 beta_tau。

    Q_tau(y | x) = alpha_tau + beta_tau * x

    通过最小化加权绝对偏差求解：
        min_{alpha,beta} Sum rho_tau(y_i - alpha - beta*x_i)
        rho_tau(u) = u * (tau - I(u < 0))

    实现用 scipy.optimize 或 statsmodels.api.quantreg（此处伪代码用
    简化迭代）。

    tau 的含义:
        - tau=0.05: y 的 5% 分位对 x 的条件关系（左尾相依）
        - tau=0.50: 中位数关系（对应整体相关性）
        - tau=0.95: y 的 95% 分位对 x 的条件关系（右尾相依）
    """
    # 简化实现：用分位数比值的近似（实际用 statsmodels.quantreg）
    # 伪代码——实际施工用 statsmodels.regression.quantile_regression.QuantReg
    try:
        from statsmodels.regression.quantile_regression import QuantReg
        import statsmodels.tools.tools as sm
        X = sm.add_constant(x)
        model = QuantReg(y, X)
        result = model.fit(q=tau, max_iter=1000)
        return float(result.params[1])
    except Exception:
        # fallback: 近似估计
        mask_hi = x > np.quantile(x, 0.75)
        mask_lo = x < np.quantile(x, 0.25)
        if mask_hi.sum() > 5 and mask_lo.sum() > 5:
            slope_hi = np.mean(y[mask_hi])
            slope_lo = np.mean(y[mask_lo])
            x_hi = np.mean(x[mask_hi])
            x_lo = np.mean(x[mask_lo])
            if abs(x_hi - x_lo) > 1e-10:
                return float((slope_hi - slope_lo) / (x_hi - x_lo))
        return 0.0
```

### 3.9 算法 ⑧：ledoit_wolf_shrinkage_covariance —— Ledoit-Wolf 收缩协方差估计（小样本稳定化）

```python
from dataclasses import dataclass, field


@dataclass
class ShrinkageResult:
    """Ledoit-Wolf 收缩估计结果——小样本协方差稳定化输出。"""
    shrunk_covariance: np.ndarray          # N*N 收缩后协方差矩阵
    shrunk_correlation: np.ndarray         # N*N 收缩后相关矩阵
    shrinkage_intensity: float             # 收缩强度 delta in [0, 1]（0=纯样本, 1=纯目标）
    target_type: str                       # 收缩目标类型
    sample_covariance: np.ndarray          # 原始样本协方差
    target_covariance: np.ndarray          # 目标协方差矩阵
    condition_number_before: float         # 收缩前条件数
    condition_number_after: float          # 收缩后条件数（应显著降低）
    strategy_names: list[str] = field(default_factory=list)


def ledoit_wolf_shrinkage_covariance(
    returns: np.ndarray,
    target: Literal["identity", "constant_correlation", "diagonal"] = "constant_correlation",
    strategy_ids: list[str] | None = None,
) -> ShrinkageResult:
    """Ledoit-Wolf 收缩协方差估计——小样本稳定化（Ledoit & Wolf 2004）。详见正文。"""
    T, N = returns.shape
    if strategy_ids is None:
        strategy_ids = [f"S{i}" for i in range(N)]
    valid = ~np.isnan(returns).any(axis=1)
    R = returns[valid]
    T_valid = R.shape[0]
    S = np.cov(R, rowvar=False, ddof=1)
    D = np.sqrt(np.diag(S))
    D_safe = np.where(D > 1e-12, D, 1e-12)
    sample_corr = S / np.outer(D_safe, D_safe)
    np.fill_diagonal(sample_corr, 1.0)
    if target == "identity":
        avg_var = np.mean(np.diag(S))
        F = np.eye(N) * avg_var
    elif target == "diagonal":
        F = np.diag(np.diag(S))
    else:
        avg_var = np.mean(np.diag(S))
        off_diag_mask = ~np.eye(N, dtype=bool)
        avg_corr = np.mean(sample_corr[off_diag_mask])
        F = np.eye(N) * avg_var
        for i in range(N):
            for j in range(N):
                if i != j:
                    F[i, j] = avg_corr * np.sqrt(S[i, i] * S[j, j])
    pi_val = 0.0
    rho_val = 0.0
    gamma_val = 0.0
    for i in range(N):
        for j in range(N):
            col_i = R[:, i]
            col_j = R[:, j]
            s_ij = S[i, j]
            f_ij = F[i, j]
            mean_prod = np.mean(col_i * col_j)
            mean_prod_sq2 = np.mean((col_i * col_j) ** 2)
            var_s_ij = (1.0 / T_valid) * (mean_prod_sq2 - mean_prod ** 2)
            pi_val += var_s_ij
            rho_val += var_s_ij
            gamma_val += (f_ij - s_ij) ** 2
    if gamma_val > 1e-15:
        delta = max(0.0, min(1.0, (pi_val - rho_val) / gamma_val))
    else:
        delta = 0.0
    Sigma_shrunk = delta * F + (1 - delta) * S
    D_shrunk = np.sqrt(np.diag(Sigma_shrunk))
    D_shrunk_safe = np.where(D_shrunk > 1e-12, D_shrunk, 1e-12)
    corr_shrunk = Sigma_shrunk / np.outer(D_shrunk_safe, D_shrunk_safe)
    np.fill_diagonal(corr_shrunk, 1.0)
    cn_before = _compute_condition_number(S)
    cn_after = _compute_condition_number(Sigma_shrunk)
    return ShrinkageResult(
        shrunk_covariance=Sigma_shrunk,
        shrunk_correlation=corr_shrunk,
        shrinkage_intensity=float(delta),
        target_type=target,
        sample_covariance=S,
        target_covariance=F,
        condition_number_before=float(cn_before),
        condition_number_after=float(cn_after),
        strategy_names=strategy_ids,
    )


def _compute_condition_number(matrix: np.ndarray) -> float:
    """计算矩阵条件数 kappa = lambda_max / lambda_min（仅正特征值）。"""
    eigenvalues = np.linalg.eigvalsh(matrix)
    pos_ev = eigenvalues[eigenvalues > 1e-15]
    if len(pos_ev) == 0:
        return float("inf")
    return float(pos_ev.max() / pos_ev.min())
```

### 3.10 算法 ⑨：filter_rmt_noise_eigenvalues —— RMT 噪声过滤（Marchenko-Pastur）

```python
@dataclass
class RMTFilterResult:
    """RMT 噪声过滤结果——区分信号与噪声特征值。"""
    filtered_correlation: np.ndarray      # N*N 过滤后相关矩阵
    original_correlation: np.ndarray      # N*N 原始相关矩阵
    eigenvalues: np.ndarray              # 降序排列的特征值
    eigenvectors: np.ndarray             # 对应特征向量
    mp_lambda_min: float                 # Marchenko-Pastur 噪声带下界
    mp_lambda_max: float                 # Marchenko-Pastur 噪声带上界
    n_signal_eigenvalues: int            # 信号特征值数（> lambda_max）
    n_noise_eigenvalues: int             # 噪声特征值数（<= lambda_max）
    signal_ratio: float                  # 信号比例 = n_signal / N
    complexity_gap: float                # 复杂度间隙（Mukhia 2026）
    strategy_names: list[str] = field(default_factory=list)


def filter_rmt_noise_eigenvalues(
    correlation_matrix: np.ndarray,
    sample_ratio: float,
    variance: float = 1.0,
    strategy_ids: list[str] | None = None,
) -> RMTFilterResult:
    """RMT 噪声过滤——Marchenko-Pastur 分布区分信号与噪声特征值。详见正文。"""
    N = correlation_matrix.shape[0]
    if strategy_ids is None:
        strategy_ids = [f"S{i}" for i in range(N)]
    inv_q = 1.0 / sample_ratio
    lambda_min = variance * (1 + inv_q - 2 * np.sqrt(inv_q))
    lambda_max = variance * (1 + inv_q + 2 * np.sqrt(inv_q))
    eigenvalues, eigenvectors = np.linalg.eigh(correlation_matrix)
    idx_sort = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx_sort]
    eigenvectors = eigenvectors[:, idx_sort]
    is_signal = eigenvalues > lambda_max
    is_noise = ~is_signal
    n_signal = int(is_signal.sum())
    n_noise = int(is_noise.sum())
    eigenvalues_filtered = eigenvalues.copy()
    if n_noise > 0:
        noise_mean = max(eigenvalues[is_noise].mean(), lambda_min)
        eigenvalues_filtered[is_noise] = noise_mean
    filtered_corr = eigenvectors @ np.diag(eigenvalues_filtered) @ eigenvectors.T
    filtered_corr = (filtered_corr + filtered_corr.T) / 2
    D = np.sqrt(np.diag(filtered_corr))
    D_safe = np.where(D > 1e-12, D, 1e-12)
    filtered_corr = filtered_corr / np.outer(D_safe, D_safe)
    np.fill_diagonal(filtered_corr, 1.0)
    lambda_max_normalized = eigenvalues[0] / N
    off_diag_mask = ~np.eye(N, dtype=bool)
    avg_corr = np.mean(correlation_matrix[off_diag_mask])
    complexity_gap = float(lambda_max_normalized - avg_corr)
    return RMTFilterResult(
        filtered_correlation=filtered_corr,
        original_correlation=correlation_matrix,
        eigenvalues=eigenvalues,
        eigenvectors=eigenvectors,
        mp_lambda_min=float(lambda_min),
        mp_lambda_max=float(lambda_max),
        n_signal_eigenvalues=n_signal,
        n_noise_eigenvalues=n_noise,
        signal_ratio=n_signal / N,
        complexity_gap=complexity_gap,
        strategy_names=strategy_ids,
    )
```

### 3.11 算法 ⑩：detect_multicollinearity_condition_number —— 条件数多重共线性检测

```python
@dataclass
class ConditionNumberResult:
    """条件数多重共线性检测结果。"""
    condition_number: float               # 条件数 kappa = lambda_max / lambda_min
    max_eigenvalue: float                 # 最大特征值
    min_eigenvalue: float                 # 最小特征值（正）
    eigenvalues: np.ndarray               # 全部特征值（降序）
    dominant_eigenvector: np.ndarray      # 最大特征值对应特征向量（主成分载荷）
    dominant_strategy: str                # 主成分载荷最大的策略
    multicollinearity_level: str          # "low" | "moderate" | "high" | "severe"
    variance_inflation_max: float         # 最大 VIF（方差膨胀因子）
    effective_diversification: float       # 有效分散度 N_eff = (Sum lambda)^2 / Sum(lambda^2)
    strategy_names: list[str] = field(default_factory=list)


def detect_multicollinearity_condition_number(
    correlation_matrix: np.ndarray,
    strategy_ids: list[str] | None = None,
    thresholds: tuple[float, ...] = (10.0, 30.0, 100.0),
) -> ConditionNumberResult:
    """Condition Number 多重共线性检测——相关矩阵条件数诊断。详见正文。"""
    N = correlation_matrix.shape[0]
    if strategy_ids is None:
        strategy_ids = [f"S{i}" for i in range(N)]
    eigenvalues, eigenvectors = np.linalg.eigh(correlation_matrix)
    idx_sort = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx_sort]
    eigenvectors = eigenvectors[:, idx_sort]
    ev_max = eigenvalues[0]
    pos_ev = eigenvalues[eigenvalues > 1e-15]
    ev_min = pos_ev.min() if len(pos_ev) > 0 else 1e-15
    condition_number = ev_max / ev_min
    if condition_number < thresholds[0]:
        level = "low"
    elif condition_number < thresholds[1]:
        level = "moderate"
    elif condition_number < thresholds[2]:
        level = "high"
    else:
        level = "severe"
    dominant_vec = np.abs(eigenvectors[:, 0])
    dominant_idx = int(np.argmax(dominant_vec))
    dominant_strategy = strategy_ids[dominant_idx]
    sum_lambda = np.sum(eigenvalues)
    sum_lambda_sq = np.sum(eigenvalues ** 2)
    n_eff = (sum_lambda ** 2) / sum_lambda_sq if sum_lambda_sq > 1e-15 else 0.0
    vif_max = 0.0
    for i in range(N):
        others = np.delete(np.arange(N), i)
        if len(others) < 2:
            continue
        y = correlation_matrix[i, others]
        X = correlation_matrix[others][:, others]
        try:
            coeffs, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
            y_pred = X @ coeffs
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r_squared = 1 - ss_res / ss_tot if ss_tot > 1e-15 else 0.0
            vif = 1.0 / max(1.0 - r_squared, 1e-10)
            vif_max = max(vif_max, vif)
        except np.linalg.LinAlgError:
            continue
    return ConditionNumberResult(
        condition_number=float(condition_number),
        max_eigenvalue=float(ev_max),
        min_eigenvalue=float(ev_min),
        eigenvalues=eigenvalues,
        dominant_eigenvector=eigenvectors[:, 0],
        dominant_strategy=dominant_strategy,
        multicollinearity_level=level,
        variance_inflation_max=float(vif_max),
        effective_diversification=float(n_eff),
        strategy_names=strategy_ids,
    )
```

### 3.12 算法 ⑪：detect_sentiment_beta_contamination —— 情绪 beta 污染检测（多证据融合）

```python
@dataclass
class SentimentBetaContaminationResult:
    """情绪 beta 污染检测结果——多证据融合判定。"""
    strategy_pair: tuple[str, str]
    is_contaminated: bool                 # 是否判定为情绪 beta 污染
    contamination_score: float            # 污染评分 [0, 1]（多证据加权）
    contamination_level: str              # "none" | "low" | "moderate" | "high" | "severe"
    evidence: dict                        # 各证据项明细
    primary_driver: str                   # 主要污染来源
    recommendation: str                   # 处置建议


def detect_sentiment_beta_contamination(
    strategy_pair: tuple[int, int],
    overall_corr: np.ndarray,
    layered_result: dict,
    dcc_result: dict | None = None,
    rmt_result: RMTFilterResult | None = None,
    condition_number_result: ConditionNumberResult | None = None,
    rolling_results: list[dict] | None = None,
    tail_results: list[dict] | None = None,
    strategy_ids: list[str] | None = None,
    threshold: float = 0.6,
) -> SentimentBetaContaminationResult:
    """情绪 beta 污染检测——多证据融合判定'多策略实为情绪 beta 穿多件衣服'。详见正文。"""
    i, j = strategy_pair
    N = overall_corr.shape[0]
    if strategy_ids is None:
        strategy_ids = [f"S{k}" for k in range(N)]
    pair_name = (strategy_ids[i], strategy_ids[j])
    evidence = {}
    score = 0.0
    # 证据 1: 跨阶段一致性高相关 (weight=0.30)
    consistent_matrix = layered_result.get("consistent_above_threshold")
    if consistent_matrix is not None and consistent_matrix.size > 0:
        is_consistent = bool(consistent_matrix[i, j])
    else:
        is_consistent = False
    max_phase = layered_result.get("max_phase_correlation")
    max_phase_val = float(max_phase[i, j]) if max_phase is not None and not np.isnan(max_phase[i, j]) else 0.0
    n_phases_above = 0
    phase_matrices = layered_result.get("phase_matrices", {})
    for phase_name, M in phase_matrices.items():
        if not np.isnan(M).all() and not np.isnan(M[i, j]) and M[i, j] > threshold:
            n_phases_above += 1
    n_total_phases = len(phase_matrices) if phase_matrices else 5
    phase_above_ratio = n_phases_above / max(n_total_phases, 1)
    evidence["cross_phase_consistent"] = is_consistent
    evidence["max_phase_correlation"] = max_phase_val
    evidence["phases_above_threshold"] = f"{n_phases_above}/{n_total_phases}"
    score += (1.0 if is_consistent else phase_above_ratio * 0.5) * 0.30
    # 证据 2: 危机窗口相关飙升 (weight=0.20)
    if dcc_result is not None:
        dyn_corr = dcc_result.get("dynamic_correlations")
        penetration = dcc_result.get("emotion_beta_penetration", {})
        is_penetration = penetration.get("is_penetration", False)
        if dyn_corr is not None and dyn_corr.size > 0:
            mean_dcc = float(np.nanmean(dyn_corr[:, i, j]))
            pair_corr_ts = dyn_corr[:, i, j]
            crisis_thresh = float(np.nanpercentile(pair_corr_ts, 90))
            crisis_mask = pair_corr_ts >= crisis_thresh
            crisis_val = float(np.nanmean(pair_corr_ts[crisis_mask])) if crisis_mask.sum() > 0 else 0.0
        else:
            mean_dcc = 0.0
            crisis_val = 0.0
        crisis_spike = bool(is_penetration or (crisis_val > threshold and crisis_val > mean_dcc * 1.3))
        evidence["crisis_window_correlation"] = crisis_val
        evidence["mean_dcc_correlation"] = mean_dcc
        evidence["dcc_emotion_penetration"] = is_penetration
        evidence["crisis_spike"] = crisis_spike
        score += (1.0 if crisis_spike else 0.0) * 0.20
    else:
        evidence["crisis_window_correlation"] = None
        evidence["crisis_spike"] = False
    # 证据 3: 整体相关水平 (weight=0.15)
    rho_pearson = float(overall_corr[i, j]) if not np.isnan(overall_corr[i, j]) else 0.0
    evidence["overall_pearson"] = rho_pearson
    if abs(rho_pearson) > threshold:
        score += 1.0 * 0.15
    elif abs(rho_pearson) > 0.3:
        score += ((abs(rho_pearson) - 0.3) / (threshold - 0.3)) * 0.15
    # 证据 4: 滚动变点 (weight=0.15)
    if rolling_results is not None:
        pair_rolling = None
        for r in rolling_results:
            sp = r.get("strategy_pair")
            if sp is not None and set(sp) == set(pair_name):
                pair_rolling = r
                break
        if pair_rolling is not None:
            verdict_r = pair_rolling.get("stability_verdict", "unknown")
            is_regime_shift = verdict_r == "regime_shift"
            is_drifting = verdict_r == "drifting"
            evidence["rolling_stability_verdict"] = verdict_r
            evidence["rolling_crossed_threshold"] = pair_rolling.get("crossed_high_threshold", False)
            score += (1.0 if is_regime_shift else (0.5 if is_drifting else 0.0)) * 0.15
        else:
            evidence["rolling_stability_verdict"] = None
    else:
        evidence["rolling_stability_verdict"] = None
    # 证据 5: 尾部相依 (weight=0.10)
    if tail_results is not None:
        pair_tail = None
        for t in tail_results:
            sp = t.get("strategy_pair")
            if sp is not None and set(sp) == set(pair_name):
                pair_tail = t
                break
        if pair_tail is not None:
            tail_dep = pair_tail.get("tail_dependent", False)
            evidence["tail_dependent"] = tail_dep
            evidence["lambda_upper"] = pair_tail.get("lambda_upper")
            evidence["lambda_lower"] = pair_tail.get("lambda_lower")
            score += (1.0 if tail_dep else 0.0) * 0.10
        else:
            evidence["tail_dependent"] = None
    else:
        evidence["tail_dependent"] = None
    # 证据 6: RMT 信号比例 (weight=0.05)
    if rmt_result is not None:
        signal_ratio = rmt_result.signal_ratio
        evidence["rmt_signal_ratio"] = signal_ratio
        score += (1.0 if signal_ratio > 0.4 and rho_pearson > threshold else 0.0) * 0.05
    else:
        evidence["rmt_signal_ratio"] = None
    # 证据 7: 条件数 (weight=0.05)
    if condition_number_result is not None:
        level = condition_number_result.multicollinearity_level
        evidence["condition_number"] = condition_number_result.condition_number
        evidence["multicollinearity_level"] = level
        evidence["effective_diversification"] = condition_number_result.effective_diversification
        score += (1.0 if level in ("high", "severe") else (0.5 if level == "moderate" else 0.0)) * 0.05
    else:
        evidence["condition_number"] = None
    score = min(score, 1.0)
    if score < 0.2:
        level = "none"
    elif score < 0.4:
        level = "low"
    elif score < 0.6:
        level = "moderate"
    elif score < 0.8:
        level = "high"
    else:
        level = "severe"
    is_contaminated = level in ("moderate", "high", "severe")
    primary_driver = "none"
    if is_consistent:
        primary_driver = "cross_phase_consistent"
    elif evidence.get("crisis_spike"):
        primary_driver = "crisis_window_spike"
    elif abs(rho_pearson) > threshold:
        primary_driver = "overall_high_correlation"
    elif evidence.get("rolling_stability_verdict") == "regime_shift":
        primary_driver = "regime_shift"
    elif evidence.get("tail_dependent"):
        primary_driver = "tail_dependence"
    if level == "none":
        rec = "无情绪 beta 污染，策略组合分散有效"
    elif level == "low":
        rec = "轻微污染，持续监控 + 季度复验"
    elif level == "moderate":
        rec = "中度污染，须论证 alpha 差异性或下调 sleeve 权重"
    elif level == "high":
        rec = "高度污染，建议合并或退役其一"
    else:
        rec = "严重污染，必须重新审视策略组合（合并/退役/差异化重设计）"
    return SentimentBetaContaminationResult(
        strategy_pair=pair_name,
        is_contaminated=is_contaminated,
        contamination_score=float(score),
        contamination_level=level,
        evidence=evidence,
        primary_driver=primary_driver,
        recommendation=rec,
    )
```


### 3.13 算法 ⑫：generate_validation_report —— 验证报告模板生成

```python
from datetime import datetime, timezone


def generate_validation_report(
    corr_results: dict,
    report_version: str = "1.0",
) -> dict:
    """
    生成策略间相关性验证报告（模板化输出）。

    报告结构对齐 30_multi_strategy_concurrency §6.2 与 20_first_batch_strategies
    §2.5 差异化矩阵——验证策略组合是否真正分散，给出 PASS/FAIL 判定。

    整合 12 算法输出:
        1  compute_correlation_matrix             -> overall_correlation
        2  block_bootstrap_correlation            -> bootstrap_ci_summary
        3  layered_correlation_by_sentiment        -> layered_by_sentiment
        4  check_correlation_threshold             -> violations
        5  rolling_correlation_changepoint         -> rolling_stability
        6  dcc_garch_correlation                   -> dcc_dynamic_corr (Phase 2.0+)
        7  tail_dependence_analysis               -> tail_risk_profile
        8  ledoit_wolf_shrinkage_covariance        -> shrinkage_result
        9  filter_rmt_noise_eigenvalues            -> rmt_filter_result
        10 detect_multicollinearity_condition_number -> condition_number_result
        11 detect_sentiment_beta_contamination     -> sentiment_beta_contamination
        12 generate_validation_report             -> 本报告（聚合）

    Args:
        corr_results: 包含以下 key 的 dict:
            - "overall":    compute_correlation_matrix 输出
            - "bootstrap":  block_bootstrap_correlation 输出
            - "layered":    layered_correlation_by_sentiment 输出
            - "violations": check_correlation_threshold 输出列表
            - "rolling":    rolling_correlation_changepoint 输出列表（算法 5）
            - "tail":       tail_dependence_analysis 输出列表（算法 6）
            - "config":     验证配置
                {
                    "data_window": (start_date, end_date),
                    "block_size": int,
                    "n_bootstrap": int,
                    "threshold": float,
                    "strategies_confidence": {
                        sid: "high" | "low"  # high=首批3策略真实回测, low=二批设计估算
                    },
                }
        report_version: 报告模板版本

    Returns:
        标准化报告 dict，可直接序列化为 markdown / json:
        {
            "report_version": str,
            "generated_at": str (ISO 8601),
            "config": {...},
            "executive_summary": {
                "verdict": "PASS" | "CONDITIONAL_PASS" | "FAIL",
                "n_strategies": int,
                "n_pairs": int,
                "max_correlation": float,
                "n_violations": int,
                "n_high_severity": int,
                "n_tail_dependent_pairs": int,
                "n_regime_shift_pairs": int,
            },
            "overall_correlation": matrix_table,         # Pearson + Spearman 双口径
            "bootstrap_ci_summary": list[dict],          # 每对的 CI 与显著性
            "layered_by_sentiment": {...},               # 5 阶段分层
            "rolling_stability": list[dict],             # 滚动相关性+变点检测
            "tail_risk_profile": list[dict],             # 尾部相依+分位数回归
            "violations": list[dict],
            "next_actions": list[str],
        }
    """
    cfg = corr_results.get("config", {})
    overall = corr_results["overall"]
    bootstrap = corr_results.get("bootstrap", {})
    layered = corr_results.get("layered", {})
    violations = corr_results.get("violations", [])
    rolling = corr_results.get("rolling", [])
    tail = corr_results.get("tail", [])

    strategy_ids = overall["strategy_order"]
    pearson = overall["pearson_matrix"]
    spearman = overall.get("spearman_matrix")

    # 1. 执行摘要
    n_strategies = len(strategy_ids)
    n_pairs = n_strategies * (n_strategies - 1) // 2
    off_diag_mask = ~np.eye(n_strategies, dtype=bool)
    max_rho = float(np.nanmax(pearson[off_diag_mask])) if n_pairs > 0 else 0.0
    n_violations = len(violations)
    n_high = sum(1 for v in violations if v["severity"] == "high")
    n_consistent = (
        int(layered.get("consistent_above_threshold", np.zeros(0)).sum())
        if layered else 0
    )
    n_tail_dependent = sum(1 for t in tail if t.get("tail_dependent", False))
    n_regime_shift = sum(
        1 for r in rolling if r.get("stability_verdict") == "regime_shift"
    )

    if n_violations == 0 and n_tail_dependent == 0 and n_regime_shift == 0:
        verdict = "PASS: 策略组合分散性达标，可进入 StrategyBook 施工"
    elif n_high > 0 or n_consistent > 0 or n_tail_dependent > 0:
        verdict = (
            "FAIL: 检测到高相关性(ρ>0.8)/情绪 beta 跨阶段集中暴露/尾部相依/"
            "结构性变点，须重新审视策略组合（合并/退役/差异化重设计）"
        )
    else:
        verdict = (
            "CONDITIONAL_PASS: 存在中低度相关(0.6≤ρ<0.8)或滚动漂移，"
            "允许施工但需持续监控 + 复核 alpha 独立性"
        )

    # 2. 相关矩阵表格（Pearson + Spearman 双口径）
    matrix_table = _format_matrix_table(pearson, strategy_ids, spearman=spearman)

    # 3. bootstrap CI 表格
    ci_summary = []
    if bootstrap:
        ci95 = bootstrap.get("ci_95", np.empty(0))
        p_zero = bootstrap.get("p_value_zero", np.empty(0))
        for i in range(n_strategies):
            for j in range(i + 1, n_strategies):
                ci_summary.append({
                    "pair": (strategy_ids[i], strategy_ids[j]),
                    "point_estimate": float(pearson[i, j]),
                    "ci_95_lower": float(ci95[i, j, 0]) if ci95.size else None,
                    "ci_95_upper": float(ci95[i, j, 1]) if ci95.size else None,
                    # 显著性: 95% CI 下界 > 0 → 显著正相关
                    "significant_positive": bool(ci95.size and ci95[i, j, 0] > 0),
                    "p_value_zero": float(p_zero[i, j]) if p_zero.size else None,
                })

    # 4. 分层相关矩阵（情绪周期 5 阶段）
    layered_summary = {}
    if layered:
        for phase, M in layered["phase_matrices"].items():
            n_samples = layered["phase_sample_counts"].get(phase, 0)
            if np.isnan(M).all():
                layered_summary[phase] = {
                    "n_samples": n_samples,
                    "status": "INSUFFICIENT_SAMPLES",
                }
                continue
            off_diag = M.copy()
            np.fill_diagonal(off_diag, np.nan)
            layered_summary[phase] = {
                "n_samples": n_samples,
                "max_correlation": float(np.nanmax(off_diag)),
                "above_threshold_count": int(layered["phase_above_threshold"][phase].sum()),
                "matrix": _format_matrix_table(M, strategy_ids),
                "status": "OK",
            }
        consistent = layered.get("consistent_above_threshold")
        if consistent is not None:
            layered_summary["cross_phase_consistent_above_threshold"] = {
                "count": int(consistent.sum()),
                "verdict": (
                    "情绪 beta 穿多件衣服" if consistent.any()
                    else "无跨阶段一致高相关"
                ),
            }

    # 5. 滚动相关性+变点检测摘要（算法 5 输出）
    rolling_summary = []
    for r in rolling:
        rolling_summary.append({
            "pair": r["strategy_pair"],
            "max_rolling": r.get("max_rolling"),
            "mean_rolling": r.get("mean_rolling"),
            "is_increasing": r.get("is_increasing"),
            "crossed_high_threshold": r.get("crossed_high_threshold"),
            "cross_ratio": r.get("cross_ratio"),
            "n_change_points": r.get("n_change_points", 0),
            "change_points": r.get("change_points", []),
            "segment_means": r.get("segment_means", []),
            "max_segment_jump": r.get("max_segment_jump", 0.0),
            "stability_verdict": r.get("stability_verdict", "unknown"),
        })

    # 6. 尾部相依+分位数回归摘要（算法 6 输出）
    tail_summary = []
    for t in tail:
        tail_summary.append({
            "pair": t["strategy_pair"],
            "lambda_upper": t.get("lambda_upper"),
            "lambda_lower": t.get("lambda_lower"),
            "lambda_upper_ci": t.get("lambda_upper_ci"),
            "lambda_lower_ci": t.get("lambda_lower_ci"),
            "tail_dependent": t.get("tail_dependent", False),
            "quantile_slopes": t.get("quantile_slopes", {}),
            "tail_asymmetry": t.get("tail_asymmetry", 0.0),
            "extreme_co_move_probability": t.get("extreme_co_move_probability", 0.0),
            "tail_risk_verdict": t.get("tail_risk_verdict", "unknown"),
        })

    # 7. 违规明细
    violation_details = [{
        "pair": v["strategy_pair"],
        "correlation": v["correlation"],
        "severity": v["severity"],
        "action": v["action_required"],
    } for v in violations]

    return {
        "report_version": report_version,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "config": {
            "strategies": strategy_ids,
            "strategies_confidence": cfg.get("strategies_confidence", {}),
            "data_window": cfg.get("data_window"),
            "block_size": cfg.get("block_size", 10),
            "n_bootstrap": cfg.get("n_bootstrap", 2000),
            "threshold": cfg.get("threshold", 0.6),
            "sentiment_phases": list(SENTIMENT_PHASES),
        },
        "executive_summary": {
            "verdict": verdict,
            "n_strategies": n_strategies,
            "n_pairs": n_pairs,
            "max_correlation": max_rho,
            "n_violations": n_violations,
            "n_high_severity": n_high,
            "n_tail_dependent_pairs": n_tail_dependent,
            "n_regime_shift_pairs": n_regime_shift,
        },
        "overall_correlation": matrix_table,
        "bootstrap_ci_summary": ci_summary,
        "layered_by_sentiment": layered_summary,
        "rolling_stability": rolling_summary,
        "tail_risk_profile": tail_summary,
        "violations": violation_details,
        "next_actions": _derive_next_actions(
            verdict, violations, layered_summary, rolling_summary, tail_summary
        ),
    }


def _format_matrix_table(
    matrix: np.ndarray,
    strategy_ids: list[str],
    spearman: np.ndarray | None = None,
) -> list[list]:
    """格式化相关矩阵为可读表格（含 Spearman 交叉验证列）。"""
    n = len(strategy_ids)
    table = []
    for i in range(n):
        row = {"strategy": strategy_ids[i]}
        for j in range(n):
            val = matrix[i, j]
            key = f"{strategy_ids[j]}_pearson"
            row[key] = None if np.isnan(val) else round(float(val), 3)
            if spearman is not None:
                sval = spearman[i, j]
                row[f"{strategy_ids[j]}_spearman"] = (
                    None if np.isnan(sval) else round(float(sval), 3)
                )
        table.append(row)
    return table


def _derive_next_actions(
    verdict: str,
    violations: list[dict],
    layered_summary: dict,
    rolling_summary: list[dict] | None = None,
    tail_summary: list[dict] | None = None,
) -> list[str]:
    """根据判定结果派生下一步行动清单（整合 12 算法证据）。"""
    actions = []
    if verdict.startswith("PASS"):
        actions.append("进入 StrategyBook 施工（30_multi_strategy_concurrency §4.2 第一阶段）")
        actions.append("周期性复验: 每季度重跑本 pipeline，监控相关性漂移")
        return actions

    if verdict.startswith("FAIL"):
        actions.append("暂停施工，重新审视策略组合（合并/退役/差异化重设计）")
        if layered_summary.get("cross_phase_consistent_above_threshold", {}).get("count", 0) > 0:
            actions.append(
                "诊断情绪 beta 集中暴露: 用偏相关去除情绪因子后复核（§6 待裁定-2）"
            )
        # 尾部相依归因
        if tail_summary:
            tail_dep_pairs = [t for t in tail_summary if t.get("tail_dependent")]
            if tail_dep_pairs:
                actions.append(
                    f"尾部相依归因: {len(tail_dep_pairs)} 对策略在极端态共动，"
                    "须检查是否共持同一风险因子（如小盘/高波动/情绪 beta）"
                )
        # 变点归因
        if rolling_summary:
            regime_pairs = [r for r in rolling_summary if r.get("stability_verdict") == "regime_shift"]
            if regime_pairs:
                actions.append(
                    f"结构性变点归因: {len(regime_pairs)} 对策略相关性发生断裂，"
                    "须对齐变点时间与市场事件（行情切换/政策变化/策略调参）"
                )
        actions.append("若合并/退役后仍无法达标，考虑引入新 alpha 源（G11 第二批次提前）")
        return actions

    # CONDITIONAL_PASS
    actions.append("允许施工，但标记高相关对为风险点")
    actions.append("复核 alpha 来源独立性: 检查信号源/持仓周期/选股池是否真差异化")
    actions.append("上线后加强该对的 PnL 归因监控（54_reconciliation_attribution）")
    actions.append("每季度复验 + 情绪周期定位器准确率更新后重跑分层验证")
    # 滚动漂移监控
    if rolling_summary:
        drift_pairs = [r for r in rolling_summary if r.get("stability_verdict") == "drifting"]
        if drift_pairs:
            actions.append(
                f"滚动漂移监控: {len(drift_pairs)} 对策略相关性呈上升趋势，"
                "上线后缩短复验周期至月度"
            )
    return actions
```



### 3.14 与 G04 / G21 的协同

#### 3.14.1 与 G04（首批 3 策略定义）的协同

- **输入依赖**：本验证的输入是 G04 定义的 5 候选策略的回测收益序列。[20_first_batch_strategies §2.5](20_first_batch_strategies.md) 差异化矩阵已给出"相关性预期"（打板↔事件驱动可能偏高，其余低），本验证是"预期 vs 实测"的对账。
- **置信度分级**：
  - **高置信度**（首批 3 策略 daban/multifactor/event_driven）：真实回测收益，可直接进入 5×5 矩阵
  - **低置信度**（第二批次 value_reversal/momentum_trend）：仅有设计意图估算收益或因子原型回测，5×5 矩阵的右下 2×2 块及跨块（首批↔二批）相关性仅供设计阶段预警，不作为施工门控依据
- **门控关系**：本验证是首批 3 策略 StrategyBook 施工的**前置门控**。验证未达 PASS / CONDITIONAL_PASS，则须先回到 G04 重新审视策略组合，不可绕过施工。

#### 3.14.2 与 G21（情绪周期×交易决策）的协同

- **输入依赖**：算法 ③ layered_correlation_by_sentiment 依赖 G21 的情绪周期阶段标签（phase_labels / phase_probs）。G21 待讨论（[28_sentiment_cycle_trading](28_sentiment_cycle_trading.md) 骨架 v0.1.0），故本验证在 G21 定稿前只能用 BM-SEL-23-B 定位器的当前输出，定位误差对结论的影响在 §6 待裁定-3 跟踪。
- **正交边界**：
  - G21 = sleeve 内 alpha 择时（决定买卖什么），情绪周期是 sleeve 内信号
  - G07 = sleeve 间相关性验证（决定策略组合是否分散），情绪周期是分层维度
  - 两者共用情绪周期标签但职责正交——G21 用它生成信号，G07 用它做相关性分层
- **定位器准确率传递**：G21 评估的定位器准确率若 <60%，本验证的分层结论置信度同步降低，须 fallback 到整体相关矩阵 + bootstrap CI 作为主判据（保守降级）。

### 3.15 验证数据区间与执行节奏

| 项 | 规格 | 理由 |
|---|---|---|
| **数据区间** | 近 3 年（约 732 交易日） | 覆盖至少 2 个完整情绪周期（冰点→主升→退潮）；A 股 3 年含牛熊切换样本 |
| **数据频率** | 日度收益（收盘对收盘） | T+1 结算下日内翻转难，日度是策略真实持有周期粒度 |
| **首批 3 策略** | 真实回测收益（高置信度） | daban/multifactor/event_driven 均有 production 信号链（20_first_batch_strategies §2.2-2.4） |
| **二批 2 策略** | 设计估算收益（低置信度） | 价值反转/动量趋势仅原型，相关结论仅供参考 |
| **执行时机** | G04 定稿后立即 / G21 阶段标签就绪后 / 首批施工前 | 30_multi_strategy_concurrency §6.2 施工前必做 |
| **复验节奏** | 每季度 + 情绪周期定位器更新后 + 第二批次上线前 | 监控相关性漂移与定位器迭代影响 |
| **block_size 敏感性** | block_size ∈ {5, 7, 10} 各跑一遍 | A 股情绪周期自相关长度不确定，敏感性分析锁定鲁棒区间 |

## 4. 考虑过的替代方案

### 4.1 iid bootstrap（非分块重采样） —— 拒绝

- **拒绝理由**：金融收益序列存在自相关、波动率聚集、情绪周期持续性——iid bootstrap 假设样本独立，会**低估方差、置信区间过窄**，导致过度自信地判定相关性显著。
- **Morwane 范式**：21-day blocks / 2000× resample 是经过 OOS 2013-2026 验证的时序保留重采样标准做法。本项目 A 股情绪周期自相关更短，取 5-10 天 block_size 适配本土结构。
- **保留位**：block_size 敏感性分析（§3.3）作为鲁棒性校验，不作为主判据。

### 4.2 仅用 Pearson 单口径 —— 拒绝

- **拒绝理由**：A 股收益分布厚尾、有涨跌停日跳变，Pearson 对异常值敏感。仅用 Pearson 会因个别极端日（如跌停潮）高估相关性。
- **Spearman 必备**：秩相关抗异常值，是非正态分布的标配交叉验证。Pearson 与 Spearman 差异大时提示异常值驱动，须人工复核。
- **保留**：报告模板同时输出双口径（算法 ⑤ _format_matrix_table），由人决策以哪个为主判据。

### 4.3 仅看整体相关矩阵（不分情绪阶段） —— 拒绝

- **拒绝理由**：[30_multi_strategy_concurrency §1.3](30_multi_strategy_concurrency.md) 明确"情绪周期是所有短周期策略的共同隐形驱动"——整体相关矩阵可能掩盖阶段性集中暴露。例如打板↔事件驱动在主升态可能 ρ=0.8（情绪 beta 集中），但在冰点态 ρ=0.2（真 alpha 差异），整体看可能 ρ=0.5 误判为分散。
- **分层必要性**：算法 ③ 的"跨阶段一致性"（consistent_above_threshold）是"情绪 beta 穿多件衣服"的严格判定——只有所有阶段都高相关才 FAIL，仅个别阶段高相关属情绪放大效应可监控。

### 4.4 直接用协方差矩阵替代相关矩阵 —— 拒绝

- **拒绝理由**：协方差矩阵包含方差信息，而本验证关注的是**策略间相关结构**（去方差后的相关系数）。直接用协方差会因各策略波动率差异（打板高波动 vs 多因子低波动）混淆"相关"与"波动率"。
- **关联**：协方差矩阵是 G13 FirmRiskAggregator 拒绝 MVO 的核心难点（[30_multi_strategy_concurrency §3.1](30_multi_strategy_concurrency.md)），本验证不引入此复杂度。Ledoit-Wolf 协方差收缩已前移至 §3.9 算法 ⑧ 实现伪代码，用于 RMT 过滤前置稳定化；firm 层风险预算的协方差应用在 §6 待裁定-1 跟踪。

### 4.5 滚动窗口动态相关（rolling correlation） —— 采纳为算法 ⑤

- **采纳决定**：滚动窗口动态相关已采纳为算法 ⑤ rolling_correlation_changepoint（§3.6），补充 CUSUM 变点检测（Page 1954）定位结构性断裂。
- **采纳理由**：整体相关矩阵是全样本均值，可能掩盖"近期相关性上升"趋势。60 日滚动窗口 + CUSUM 变点检测能揭露相关性漂移与结构性断裂，是 block-bootstrap CI（时间维度）与情绪周期分层（横切维度）的正交补充。
- **CUSUM 价值**：变点检测定位"何时相关性发生突变"，给后续归因（G25）提供时间锚点——是策略 alpha 漂移、情绪周期切换还是市场结构性变化。
- **与 DCC-GARCH 的分工**：滚动窗口是非参数的（60 日滑动），DCC 是参数化的（全样本估动态）。本期用非参数滚动（Phase 1.0），DCC-GARCH 已在 §3.7 实现伪代码（Phase 2.0+ 评估），参数用典型值待 MLE 替换。

### 4.6 机器学习降维（PCA / t-SNE 看策略聚类） —— 拒绝

- **拒绝理由**：PCA 等降维方法在 5 策略小样本下解释力弱（5 维本来就可视化），且主成分解释需额外归因（PC1 是什么？情绪？市场？）。
- **保留**：策略数 >8 后（远期 G11+ 扩容）可重新评估降维方法。本期 5 策略两两 10 对直接看矩阵更清晰。

### 4.7 DCCA / MF-DXA 去趋势互相关分析 —— 拒绝（远期评估）

- **方法说明**：DCCA（Detrended Cross-Correlation Analysis, Podobnik & Stanley 2008）和 MF-DXA（Multifractal Detrended Cross-Correlation Analysis, Zhou 2008）是 2026-08 研究整合中搜索到的新相关性估计方法，用于检测非平稳时间序列的长程互相关与多分形特征。
- **拒绝理由**：DCCA/MF-DXA 适用于超长序列（>5000 日）的长程相关结构分析，A 股 3 年 732 日样本量不足以支撑可靠的多分形估计。且本验证关注的是策略间短中期相关结构（block-bootstrap + DCC-GARCH 已覆盖），而非长程记忆效应。
- **保留**：策略数扩充至 >10 且 track record >5 年后（Phase 3.0+）可重新评估。本期 5 策略短样本下 DCCA/MF-DXA 的边际增益不足以抵消过拟合风险。

## 5. 上限定义

### 5.1 系统上限

- **策略数上限**：本验证 pipeline 设计支持 ≤10 个策略（10×10 矩阵 = 45 对，人脑可读上限）。超过 10 策略须引入分层聚类或因子模型降维（远期）。
- **情绪阶段粒度上限**：当前 5 阶段（冰点/反核/主升/疯狂/退潮）。若 G21 细化到 >10 阶段，每阶段样本数会跌破 min_samples_per_phase=20，须合并稀有阶段或用软分配缓解。
- **block_size 范围**：5-15 天。低于 5 天接近 iid bootstrap（失去时序保留意义），高于 15 天块内周期过长（块间独立性丧失）。
- **n_bootstrap 上限**：5000 次。超过此值 CI 边际精度提升 <0.5%，算力浪费。
- **CUSUM 阈值范围**：4.0-6.0 倍标准差。低于 4.0 噪声过多误报，高于 6.0 漏报结构性变点。默认 5.0（工业控制经典值）。
- **尾部相依分位阈值**：0.90-0.97。0.95 为默认值（5% 极端样本），低于 0.90 样本过多失去尾部意义，高于 0.97 样本不足置信度下降。
- **分位数回归分位水平**：tau ∈ {0.05, 0.25, 0.75, 0.95}。0.05/0.95 是尾部检测核心，0.25/0.75 是中段对照。
- **Ledoit-Wolf 收缩强度范围**：delta ∈ [0, 1]。delta→0 纯样本估计，delta→1 纯目标矩阵。典型金融数据 delta 0.1-0.5（小样本分层阶段可能升至 0.5-0.8）。
- **RMT 信号比例阈值**：signal_ratio < 0.3 提示噪声主导（小样本伪相关），> 0.5 提示真实信号相关。
- **条件数分级阈值**：κ < 10 良好 / 10-30 中度 / 30-100 高度 / ≥100 严重。N_eff < N/2 提示策略组合冗余。
- **情绪 beta 污染评分阈值**：score ≥ 0.4（moderate）为污染警告，≥ 0.6（high）建议合并/退役，≥ 0.8（severe）必须重新审视。

### 5.2 演进路径

| 阶段 | 时机 | 增量能力 |
|---|---|---|
| **Phase 1.0（本期）** | G04 定稿后立即 | 12 算法 + 整体相关矩阵 + block-bootstrap CI + 5 阶段分层 + 阈值检查 + 滚动相关性+CUSUM变点 + DCC-GARCH(Phase 2.0+伪代码预置) + copula尾部相依 + Ledoit-Wolf收缩 + RMT噪声过滤 + 条件数多重共线性 + 情绪beta污染多证据融合 + 报告模板 |
| **Phase 1.5** | 首批 3 策略实盘 3 个月 track record 后 | Partial correlation 偏相关（区分真相关 vs 共受情绪驱动） |
| **Phase 2.0** | 首批 track record 满 6 个月 + 第二批次上线前 | 加入 DCC-GARCH 动态条件相关（检测相关性时变结构）+ 实盘收益 vs 回测收益相关性对账 |
| **Phase 3.0（远期）** | 策略数 >8 或 AUM 显著增长 | 因子模型降维 + DCC-GARCH 参数化动态相关 + 多资产相关性扩展（若引入港股/期权） |

### 5.3 为何这是上限而非妥协

- **12 算法已覆盖施工前必做项的全部判据**：整体相关（①）+ 时序保留显著性（②）+ 情绪分层（③）+ 阈值门控（④）+ 滚动相关性+CUSUM变点（⑤）+ DCC-GARCH（⑥）+ copula尾部相依（⑦）+ Ledoit-Wolf收缩（⑧）+ RMT噪声过滤（⑨）+ 条件数多重共线性（⑩）+ 情绪beta污染多证据融合（⑪）+ 标准化报告（⑫），对齐 Morwane 范式且适配 A 股情绪周期特性。
- **DCC-GARCH / Ledoit-Wolf / Partial correlation 是研究增强而非施工前置**：本验证的 PASS/FAIL 判定不依赖这些进阶方法——12 算法在 block-bootstrap CI + 跨阶段一致性 + CUSUM 变点 + 尾部相依 + RMT 信号过滤 + 条件数 + 多证据融合上已足够稳健。进阶方法用于解释"为何高相关"而非"是否高相关"。
- **个人 + AI 开发约束**（[30_multi_strategy_concurrency §1.3](30_multi_strategy_concurrency.md)）：算法复杂度须与研究带宽匹配。12 算法是单人可维护的合理上限（含 4 个进阶诊断算法的伪代码预置），超过此规模须团队化。

## 6. 待裁定

> 以下项目暂不施工，**非永久禁止**。Phase 1.5+ 评估，满足重评条件时重新讨论。

| 暂缓项 | 暂缓理由 | 重评条件 | 阶段 |
|---|---|---|---|
| 1. ~~Ledoit-Wolf 协方差收缩~~ | ~~已前移至 §3.9 算法 ⑧ 实现伪代码~~。原暂缓理由（block-bootstrap 间接处理小样本）仍成立，但 2026-08 研究整合要求作为 RMT 过滤前置稳定化 | 分层阶段样本不足时启用收缩后矩阵替代原始矩阵 | Phase 1.5+ |
| 2. Partial correlation 偏相关 | 去除共同因子（情绪/市场/规模）后的纯策略相关，可区分"真相关"（alpha 重叠）vs"共受情绪驱动"（伪相关）。但需先定义共同因子集（情绪周期指数/市场收益/市值因子），因子选择本身是研究课题 | G21 情绪周期定位器准确率 >70% + 因子集定义成熟 | Phase 1.5+ |
| 3. 情绪周期定位器误差对分层结论的影响 | 算法 ③ 依赖 G21 阶段标签，定位器误差会污染分层相关矩阵。本期假设标签就绪，误差影响未量化 | G21 评估完成（[28_sentiment_cycle_trading](28_sentiment_cycle_trading.md) 待讨论）+ 定位器准确率有数 | Phase 1.5+ |
| 4. DCC-GARCH 动态条件相关 | 检测相关性是否随时间变化（时变相关结构），比 block-bootstrap CI 更系统化。伪代码已预置于 §3.7 算法 ⑥，但 DCC-GARCH 参数估计复杂（GARCH 残差+似然优化），5 策略小样本下过拟合风险高 | 首批 track record 满 6 个月 + 策略数 ≥5（含二批）+ 样本量 >1000 日 | Phase 2.0+ |
| 5. 实盘 vs 回测相关性对账 | 回测相关性通过后，实盘相关性可能因滑点/执行延迟/资金约束而漂移。须建立实盘复验机制 | 首批 3 策略实盘满 3 个月，实盘 PnL 数据足够 | Phase 2.0+ |
| 6. 第二批次 2 策略（价值反转/动量趋势）真实相关性 | 本期 5×5 矩阵的右下 2×2 块及跨块为低置信度（设计估算）。须二批策略真实回测后重跑 | G11 第二批次策略定义定稿 + 真实回测收益产出 | Phase 2.0+ |

## 7. 待定问题对齐

> 以下来自 [00_index_trading_decision](00_index_trading_decision.md) §3 G07 讨论要点，本 spec 已逐项对齐并落入 §3 决策。

- [x] ① 5 候选策略两两相关矩阵 → §3.2 算法 ① compute_correlation_matrix（Pearson + Spearman 双口径，5 策略 10 对）
- [x] ② 按情绪周期分层看相关性 → §3.4 算法 ③ layered_correlation_by_sentiment（5 阶段分层 + 跨阶段一致性判定）
- [x] ③ 若各阶段相关性 >0.6 则"多策略实为情绪 beta 穿多件衣服"→ 重新审视 → §3.5 算法 ④ check_correlation_threshold（all_phases_above 模式 + consistent_above_threshold 严格判定 + FAIL 判定规则）
- [x] ④ 验证数据区间 → §3.15 验证数据区间与执行节奏（近 3 年 732 交易日 / 日度 / block_size 敏感性 ∈ {5,7,10} / 季度复验）
- [x] ⑤ 验证报告模板 → §3.13 算法 ⑫ generate_validation_report（标准化报告 dict + PASS/CONDITIONAL_PASS/FAIL 判定 + next_actions 行动清单 + 整合 12 算法证据）

- [x] ⑥ 滚动相关性稳定性分析（rolling window + 变点检测） → §3.6 算法 ⑤ rolling_correlation_changepoint（60 日滚动窗口 + CUSUM 变点检测 + stability_verdict 判定）
- [x] ⑦ 尾部相关性分析（copula-based + quantile regression） → §3.8 算法 ⑦ tail_dependence_analysis（经验 copula 尾部相依系数 lambda_upper/lambda_lower + Koenker 分位数回归 + tail_risk_verdict 判定）
- [x] ⑧ DCC-GARCH 动态条件相关（Phase 2.0+ 评估） → §3.7 算法 ⑥ dcc_garch_correlation（Engle 2002 两阶段法：GARCH(1,1) 标准化残差 + DCC 滤波 + 情绪周期分层均值 + 情绪 beta 穿透检测）
- [x] ⑨ Ledoit-Wolf 收缩协方差估计 → §3.9 算法 ⑧ ledoit_wolf_shrinkage_covariance（Ledoit and Wolf 2004 解析收缩强度 + constant correlation target + 条件数收缩前后对比）
- [x] ⑩ RMT 噪声过滤 → §3.10 算法 ⑨ filter_rmt_noise_eigenvalues（Marchenko-Pastur 噪声带 + 信号噪声特征值分类 + Mukhia 2026 complexity gap）
- [x] ⑪ 条件数多重共线性检测 → §3.11 算法 ⑩ detect_multicollinearity_condition_number（条件数 kappa=lambda_max/lambda_min + VIF 方差膨胀因子 + N_eff 有效分散度 + 主成分载荷）
- [x] ⑫ 情绪 beta 污染检测（多证据融合） → §3.12 算法 ⑪ detect_sentiment_beta_contamination（7 证据加权评分 → none/low/moderate/high/severe 判定）

## 8. 引用

### 8.1 相关设计备忘
- [00_index_trading_decision.md](00_index_trading_decision.md) §3 G07（主题组讨论要点）
- [30_multi_strategy_concurrency.md](30_multi_strategy_concurrency.md) §1.3（情绪周期隐形驱动）/ §2.3（自然叠加替代优化器）/ §6.2（施工前必做项）
- [20_first_batch_strategies.md](20_first_batch_strategies.md) §2.1（5 候选清单裁定）/ §2.5（差异化矩阵与相关性预期）/ §2.6（选股池交集前置假设）
- [28_sentiment_cycle_trading.md](28_sentiment_cycle_trading.md)（G21 情绪周期×交易决策，待讨论——分层标签来源）
- [52_backtest_framework_docking.md](52_backtest_framework_docking.md)（G23 回测框架对接，验证 pipeline 上游）
- [53_simulation_live_path.md](53_simulation_live_path.md)（G24 模拟实盘路径，验证报告门控下游）
- [54_reconciliation_attribution.md](54_reconciliation_attribution.md)（G25 对账归因，高相关对的 PnL 归因监控下游）

### 8.2 开源实证参考
- [Morwane/multi-strategy-alpha-book](https://github.com/Morwane/multi-strategy-alpha-book) — 核心范式来源。两个弱相关 alpha sleeve（ρ=+0.03）经 inverse-vol risk parity 组合，block-bootstrap 2000×（21-day blocks），risk-throttle Sharpe 90% CI [+1.01, +1.87]。本 spec 算法 ② 直接对齐其 block-bootstrap 范式，block_size 适配 A 股情绪周期缩短至 5-10 天。
- Ledoit-Wolf 协方差收缩（Ledoit & Wolf 2004, "A well-conditioned estimator for large-dimensional covariance matrices"）— 小样本协方差稳定化经典方法。本 spec §3.9 算法 ⑧ 已实现伪代码（constant correlation target + 解析收缩强度），用于 RMT 过滤前置稳定化。
- DCC-GARCH（Engle 2002, "Dynamic Conditional Correlation"）— 动态条件相关模型，检测相关性时变结构。本 spec §3.7 算法 ⑥ 已实现伪代码（GARCH(1,1) 标准化残差 + DCC 滤波），Phase 2.0+ track record 满 6 个月后落码。
- Partial correlation（Baba, Shibata & Sibuya 2004）— 偏相关系数，去除共同因子后的纯相关。本 spec §6 待裁定-2 评估用于 Phase 1.5+ 区分真相关 vs 共受情绪驱动。
- Copula 尾部相依（Nelsen 2006, "An Introduction to Copulas" 第5.4节 / Joe 1997, "Multivariate Models and Dependence Concepts"）— 经验 copula 非参数估计上/下尾相依系数 lambda_upper/lambda_lower。本 spec 算法 ⑦ tail_dependence_analysis 用于检测极端态共动风险。
- 分位数回归（Koenker 2005, "Quantile Regression"）— 极端分位（tau=0.05/0.95）检测尾部相关性突变。本 spec 算法 ⑦ 用于区分均值相关与尾部相关。
- CUSUM 变点检测（Page 1954, "Continuous Inspection Schemes" / Killick et al. 2012, "Optimal Detection of Changepoints with a Linear Computational Cost" PELT）— 滚动相关性序列的结构性断裂检测。本 spec 算法 ⑤ rolling_correlation_changepoint 用于定位相关性 regime shift。
- RMT 随机矩阵理论（Laloux 2000, Plerou 2002）— Marchenko-Pastur 分布区分相关矩阵信号与噪声特征值，过滤噪声后重构稳定相关矩阵。本 spec §3.10 算法 ⑨ filter_rmt_noise_eigenvalues 已实现伪代码（MP 噪声带边界 + complexity gap Mukhia 2026）。
- Condition Number 多重共线性检测（Belsley, Kuh and Welsch 1980）— 条件数 kappa=lambda_max/lambda_min 检测策略组合冗余度，VIF 方差膨胀因子量化单策略可被其他策略线性组合解释的程度。本 spec §3.11 算法 ⑩ detect_multicollinearity_condition_number 已实现伪代码（N_eff 有效分散度 + 主成分载荷分析）。
- Deflated Sharpe Ratio（Bailey & Lopez de Prado 2014）— 多重检验+相关性双重调整的 Sharpe 虚假发现控制。5 策略 10 对多重比较时裸 Sharpe 排名高估显著性，DSR 收缩向 deflated benchmark SR0 约 1.63（年化）噪声天花板。本 spec 3.5 阈值判定的统计严谨性对标。
- Soloviov DSR 鲁棒性带（Soloviov 2026-07）— 有效 trial 数非单一数值（5 估计器相差两个数量级 1.6-370）。相关搜索场景（参数网格/同源变体）禁用裸 DSR，须用 White Reality Check/Hansen SPA bootstrap。MVP 阶段 5 候选策略 trial_correlated=false 时裸 DSR 可用。
- causal-quant 因果验证（causal-quant 2026-07）— 相关性不等于因果性，两策略相关可能因 confounder（情绪周期共同驱动）或 collider（past_return 碰撞变量，系数符号可翻转 +0.08 到 -0.04）而非真 alpha 重叠。策略注册时声明因果图 DAG 避免事后合理化。本 spec 3.4 偏相关对标。
- A 股 mask-first 设计（Yimin Du USTC, arXiv:2507.07107v2 2026-05）— 正负10%/正负20% 涨跌停板使部分收盘价不可执行，先读价格再过滤行导致 upstream contamination（MA/correlation/rank 静默传播虚假相关，实证虚增 IC 18%）。mask-first 在收益序列加载时构造 tradability mask 贯穿每个算子，A 股相关性验证前置 MUST。

### 8.3 相关作战地图
- [battle_map_05_stock_selection.md](../battle_map/battle_map_05_stock_selection.md) BM-SEL-23-B（情绪周期 4+1 阶段定位器，分层标签来源）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G07 讨论要点占位，待讨论填空 |
| 2026-08-10 | 1.0.0 | 骨架→active 完整 spec | 7 算法定型（① compute_correlation_matrix / ② block_bootstrap_correlation / ③ layered_correlation_by_sentiment / ④ check_correlation_threshold / ⑤ rolling_correlation_changepoint / ⑥ dcc_garch_correlation / ⑦ tail_dependence_analysis / ⑧ generate_validation_report）+ 验证数据区间 + 与 G04/G21 协同边界 + 6 项待裁定（Ledoit-Wolf/Partial correlation/DCC-GARCH 等进阶方法 Phase 1.5+ 评估）+ 7 项讨论要点全数对齐落 §3 决策。整合 2026-08 研究：Morwane block-bootstrap 时序保留重采样（block_size 5-10 天适配 A 股情绪周期）+ CUSUM 变点检测（Page 1954）+ copula 尾部相依（Nelsen 2006 / Joe 1997）+ Koenker 分位数回归 + Ledoit-Wolf 协方差收缩 + DCC-GARCH 动态条件相关 + Partial correlation 偏相关 |
| 2026-08-10 | 1.0.1 | 研究整合补全 | 补全 2026-08 研究整合 4 项遗漏：Lopez de Prado DSR（Deflated Sharpe Ratio 多重检验虚假发现控制）+ Soloviov DSR 鲁棒性带（有效 trial 数 1.6-370 相关搜索场景 bootstrap）+ causal-quant 因果验证（confounder/collider 区分真相关 vs 共受情绪驱动）+ A 股 mask-first 设计（arXiv:2507.07107v2 涨跌停板 upstream contamination 前置 MUST）。同步更新 8.2 引用 4 条 |
| 2026-08-10 | 1.0.2 | DCC-GARCH 算法补全 | 补充算法 ⑥ dcc_garch_correlation（Engle 2002 DCC-GARCH 两阶段法：GARCH(1,1) 标准化残差 + DCC 滤波 + 情绪周期分层均值 + 情绪 beta 穿透检测），Phase 2.0+ 评估项伪代码预置。同步重编号 §3.7-§3.10 → §3.8-§3.11，更新全部交叉引用 + §7 新增 ⑧ DCC-GARCH 条目 |
| 2026-08-10 | 1.1.0 | 新增 4 算法 + 交叉引用修复 | 新增 §3.9 算法 ⑧ ledoit_wolf_shrinkage_covariance（Ledoit-Wolf 2004 收缩协方差估计）+ §3.10 算法 ⑨ filter_rmt_noise_eigenvalues（RMT Marchenko-Pastur 噪声过滤 Laloux 2000/Plerou 2002/Mukhia 2026 complexity gap）+ §3.11 算法 ⑩ detect_multicollinearity_condition_number（条件数 κ + VIF + N_eff 有效分散度）+ §3.12 算法 ⑪ detect_sentiment_beta_contamination（7 证据加权融合判定 none/low/moderate/high/severe）。原 §3.9-§3.11 顺延至 §3.13-§3.15。§6 待裁定-1/4 标记已前移。§7 新增 ⑨-⑫ 讨论要点。§8.2 新增 RMT + Condition Number 引用。 |
| 2026-08-10 | 1.1.1 | 一致性修复 | 修复架构图遗漏 DCC-GARCH 算法导致 8 → 12 算法显示不一致；修复 v1.0.0 修订记录中混入 ASCII art（│/↓）的损坏条目；算法计数 7→12 同步更新；修订记录按 semver 时序重排（v1.0.1→v1.0.2→v1.1.0→v1.1.1） |
