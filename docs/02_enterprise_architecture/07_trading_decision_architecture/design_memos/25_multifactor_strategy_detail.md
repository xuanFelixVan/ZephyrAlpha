---
ttl: permanent
doc_type: architecture_view
title: 多因子策略细节
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-08-10
topic: multifactor_strategy_detail
scope: 07_trading_decision_architecture
---

# 多因子策略细节

> **性质**：由 [00_index_trading_decision](00_index_trading_decision.md) G09 主题组派生，将多因子策略的讨论要点落地为可施工的 spec + 伪代码。
> **施工图纪律**：本文档 status=active，对应模块允许施工。
> **2026-08 研究整合**：对称正交 Löwdin（年化超额+5%，IR 1.7→2.6）；华泰筹码分层 AI 因子（2026-06 RankIC 12.3%）；华泰残差动量改进版（2026-03 年化超额 12.90%）；因子拥挤度门限测试（华泰 2026-03 95%阈值+兴业/MSCI 五维度）；IT 因子知情交易微观行为（西部 2026-03 RankIC 0.064）；华泰全频段融合因子+GPT 因子工厂 2.0（2026-07 IR 3.01）。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G09 多因子策略细节 |
| 所属 | 作战地图 05 |
| 依赖 | G04、G05、G01（因子工程 [15_data_feature_layer_spec](15_data_feature_layer_spec.md)） |
| 对标 | WorldQuant / Numerai 多因子 / 华泰金工多因子 |
| 正交性 | ✅ 与 regime 正交 |
| 优先级 | P2 |
| 状态 | ✅ active — 因子组合+正交化+行业中性化+拥挤度监控+衰减监控算法已定稿 |

## 2. 背景

### 2.1 项目处境

多因子策略是 ZephyrAlpha 首批策略中容量最大的策略，可承载主资金。核心逻辑：通过多个 alpha 因子的组合选股，获取横截面超额收益。A 股多因子面临因子衰减、因子拥挤、行业偏移等挑战，需系统化的因子组合和监控框架。

### 2.2 核心问题

1. **因子组合方式选择**：打分法简单但忽略因子相关性；IC 加权考虑因子预测力但不处理共线性；正交化处理共线性但改变因子经济含义。
2. **行业中性化**：A 股行业收益差异大，不中性化会导致因子暴露被行业 beta 污染。
3. **因子衰减监控**：因子 alpha 随时间衰减（市场学习、套利消减），需持续监控 IC 趋势。
4. **因子拥挤度**：拥挤 ≠ "持有资金多"，而是"采用相似信号/模型的资本规模 > 策略容量"（兴业 2026-08）。高拥挤未来 6-12 月收益偏弱。
5. **多因子容量**：多因子换手率低（3-5 天 convergence），容量较大，可承载主资金。

### 2.3 约束条件

- **换手率**：低（3-5 天 convergence），交易成本敏感
- **容量**：较大，可承载主资金
- **行业分布**：需行业中性化，避免行业 beta 污染
- **MVP 简化**：先对称正交+IC 加权，Phase 1.5+ 再考虑 ML 组合

## 3. 决策

### 3.1 架构定义

多因子策略由因子层、组合层、监控层三层构成：

```
因子层: 原始因子 → 去极值 → 标准化 → 行业中性化 → 对称正交
                                                        ↓
组合层: IC 加权合成 → 综合得分 → 分层选股 → 权重优化
                                                        ↓
监控层: IC 衰减监控 → 拥挤度监测 → 换手率控制 → 容量管理
```

### 3.2 因子预处理算法

```python
import numpy as np
from dataclasses import dataclass

@dataclass
class FactorPreprocessResult:
    """因子预处理结果。"""
    factor_matrix: np.ndarray       # (N_stocks, N_factors) 预处理后因子矩阵
    factor_names: list[str]
    industry_dummies: np.ndarray    # 行业哑变量矩阵


def preprocess_factors(
    raw_factors: dict[str, np.ndarray],   # {因子名: (N_stocks,) 原始因子值}
    industry_labels: np.ndarray,           # (N_stocks,) 行业标签
    factor_names: list[str] = None,
) -> FactorPreprocessResult:
    """因子预处理——去极值→标准化→行业中性化→对称正交。

    流程：
    1. 去极值（MAD 法）：中位数 ± 5×MAD 截断
    2. 标准化（Z-score）：(x - mean) / std
    3. 行业中性化：因子值对行业哑变量回归，取残差
    4. 对称正交（Löwdin）：F̃ = F · (FᵀF)^{-1/2}，使 F̃ᵀF̃ = I

    对称正交优势（因子正交全攻略 2026-07）：
    - 正交前后矩阵距离最小，可解释性高
    - 不依赖历史数据与收益数据
    - 计算高效
    - 年化超额提升约 5%，信息比从 1.7 提升至 2.6+
    """
    if factor_names is None:
        factor_names = list(raw_factors.keys())

    n_stocks = len(next(iter(raw_factors.values())))
    n_factors = len(factor_names)

    # 步骤 1：构建因子矩阵
    F = np.zeros((n_stocks, n_factors))
    for i, name in enumerate(factor_names):
        F[:, i] = raw_factors[name]

    # 步骤 2：去极值（MAD 法）
    for j in range(n_factors):
        col = F[:, j]
        median = np.median(col[~np.isnan(col)])
        mad = np.median(np.abs(col[~np.isnan(col)] - median))
        if mad > 0:
            lower = median - 5 * mad
            upper = median + 5 * mad
            F[:, j] = np.clip(col, lower, upper)

    # 步骤 3：标准化（Z-score）
    for j in range(n_factors):
        col = F[:, j]
        valid = ~np.isnan(col)
        if valid.sum() > 0:
            mean = np.mean(col[valid])
            std = np.std(col[valid])
            if std > 0:
                F[:, j] = (col - mean) / std

    # 步骤 4：行业中性化——因子值对行业哑变量回归取残差
    industries = np.unique(industry_labels[~np.isnan(industry_labels.astype(float))])
    industry_dummies = np.zeros((n_stocks, len(industries)))
    for i, ind in enumerate(industries):
        industry_dummies[:, i] = (industry_labels == ind).astype(float)

    # 加截距项
    X = np.hstack([np.ones((n_stocks, 1)), industry_dummies])

    for j in range(n_factors):
        col = F[:, j]
        valid = ~np.isnan(col)
        if valid.sum() > len(industries) + 1:
            # OLS 回归取残差
            beta = np.linalg.lstsq(X[valid], col[valid], rcond=None)[0]
            predicted = X @ beta
            F[:, j] = col - predicted

    # 步骤 5：对称正交（Löwdin）
    # F̃ = F · (FᵀF)^{-1/2}
    FtF = F.T @ F
    # 矩阵平方根逆（通过特征分解）
    eigvals, eigvecs = np.linalg.eigh(FtF)
    eigvals = np.maximum(eigvals, 1e-10)  # 数值稳定性
    FtF_inv_sqrt = eigvecs @ np.diag(1.0 / np.sqrt(eigvals)) @ eigvecs.T
    F_orthogonalized = F @ FtF_inv_sqrt

    return FactorPreprocessResult(
        factor_matrix=F_orthogonalized,
        factor_names=factor_names,
        industry_dummies=industry_dummies,
    )
```

### 3.3 IC 加权因子合成算法

```python
@dataclass
class FactorWeight:
    """因子权重计算结果。"""
    factor_names: list[str]
    weights: np.ndarray             # IC 加权权重
    recent_ic: np.ndarray           # 近期 IC 值
    ic_ir: np.ndarray               # IC 信息比（IC 均值/IC 标准差）


def calc_ic_weighted_factors(
    factor_matrix: np.ndarray,       # (N_stocks, N_factors) 预处理后因子
    forward_returns: np.ndarray,     # (N_stocks,) 未来收益率
    factor_names: list[str],
    ic_window: int = 20,             # IC 计算窗口（交易日）
    ic_history: np.ndarray = None,   # 历史 IC 矩阵 (T, N_factors)，若有
) -> tuple[np.ndarray, FactorWeight]:
    """IC 加权因子合成——根据因子近期预测力分配权重。

    方法：
    1. 计算各因子近 ic_window 日的 Rank IC（Spearman 秩相关）
    2. IC 权重 = IC_IR / Σ|IC_IR|（IC 信息比加权）
    3. 综合得分 = Σ(weight_i × factor_i)

    IC IR 优于纯 IC 均值：考虑了 IC 的稳定性
    """
    n_factors = factor_matrix.shape[1]

    if ic_history is not None and len(ic_history) >= ic_window:
        # 使用历史 IC
        recent_ic = np.mean(ic_history[-ic_window:], axis=0)
        ic_std = np.std(ic_history[-ic_window:], axis=0)
        ic_ir = np.where(ic_std > 0, recent_ic / ic_std, 0.0)
    else:
        # 降级：用当前截面 IC 近似
        from scipy.stats import spearmanr
        recent_ic = np.zeros(n_factors)
        for j in range(n_factors):
            valid = ~np.isnan(factor_matrix[:, j]) & ~np.isnan(forward_returns)
            if valid.sum() > 10:
                ic, _ = spearmanr(factor_matrix[valid, j], forward_returns[valid])
                recent_ic[j] = ic
        ic_ir = recent_ic  # 无历史时退化为 IC 本身

    # IC IR 加权（符号保留：正 IC 因子做多，负 IC 因子做空/反向）
    weights = ic_ir / (np.sum(np.abs(ic_ir)) + 1e-10)

    # 综合得分
    combined_score = factor_matrix @ weights

    factor_weight = FactorWeight(
        factor_names=factor_names,
        weights=weights,
        recent_ic=recent_ic,
        ic_ir=ic_ir,
    )

    return combined_score, factor_weight
```

### 3.4 因子拥挤度监测算法

```python
@dataclass
class CrowdingSignal:
    """因子拥挤度信号。"""
    factor_name: str
    crowding_level: str        # "LOW" / "MEDIUM" / "HIGH" / "EXTREME"
    triggered_indicators: list[str]
    risk_flag: bool            # 高拥挤风险标记


def monitor_factor_crowding(
    factor_name: str,
    # 华泰门限测试 4 个量价指标（2026-03）
    indicator_values: dict[str, float],    # {指标名: 当前值}
    indicator_history: dict[str, np.ndarray],  # {指标名: 历史序列}
    threshold_quantile: float = 0.95,      # 95% 分位数触发
    min_indicators_for_high: int = 3,      # 3-4 个触发 = 高拥挤
) -> CrowdingSignal:
    """因子拥挤度监测——华泰门限测试 + 兴业/MSCI 综合模型。

    华泰模型（2026-03-17《量化行业轮动崎岖之路》）：
    - 基于门限测试精选 4 个量价指标
    - 单指标滚动分位数达 95% 阈值触发拥挤信号
    - 3-4 个指标触发 = 行业高拥挤
    - 2026 年初成功预警国防军工、工业金属、贵金属三个行业阶段性高点

    兴业证券/MSCI 综合模型（2026-08-05）五维度：
    1. 估值价差（Valuation Spread）
    2. 卖空价差/利息
    3. 组内异常相关性（Pairwise Abnormal Correlation）
    4. 相对因子波动率
    5. 过去 3 年累计收益

    核心结论（兴业 2026-08）：
    - 拥挤 ≠ "持有资金多"，而是"采用相似信号/模型的资本规模 > 策略容量"
    - 拥挤度是风险状态指标而非机械择时信号
    - 高拥挤未来 6-12 月收益偏弱、回撤概率高，但短期可能继续积累
    """
    triggered = []

    for ind_name, current_val in indicator_values.items():
        history = indicator_history.get(ind_name)
        if history is not None and len(history) > 20:
            threshold = np.percentile(history, threshold_quantile * 100)
            if current_val > threshold:
                triggered.append(f"{ind_name}_{current_val:.2f}>p{threshold_quantile:.0%}={threshold:.2f}")

    n_triggered = len(triggered)

    if n_triggered >= min_indicators_for_high:
        level = "HIGH"
        risk_flag = True
    elif n_triggered >= 2:
        level = "MEDIUM"
        risk_flag = False
    elif n_triggered >= 1:
        level = "LOW"
        risk_flag = False
    else:
        level = "LOW"
        risk_flag = False

    # 极端拥挤：4 个全触发
    if n_triggered >= 4:
        level = "EXTREME"
        risk_flag = True

    return CrowdingSignal(
        factor_name=factor_name,
        crowding_level=level,
        triggered_indicators=triggered,
        risk_flag=risk_flag,
    )


def apply_crowding_throttle(crowding: CrowdingSignal, position_cap: float) -> float:
    """根据拥挤度缩窄仓位上限。"""
    if crowding.crowding_level == "EXTREME":
        return position_cap * 0.3   # 极端拥挤减仓 70%
    elif crowding.crowding_level == "HIGH":
        return position_cap * 0.6   # 高拥挤减仓 40%
    elif crowding.crowding_level == "MEDIUM":
        return position_cap * 0.8   # 中度拥挤减仓 20%
    else:
        return position_cap         # 低拥挤不缩窄
```

### 3.5 因子衰减监控算法

```python
@dataclass
class FactorDecayStatus:
    """因子衰减监控状态。"""
    factor_name: str
    recent_ic_20d: float        # 近 20 日 IC 均值
    long_term_ic_250d: float    # 长 250 日 IC 均值
    decay_ratio: float          # 衰减比 = recent / long_term
    status: str                 # "HEALTHY" / "DECAYING" / "DEAD" / "RECOVERING"


def monitor_factor_decay(
    factor_name: str,
    ic_history: np.ndarray,     # IC 历史序列（每日 IC 值）
) -> FactorDecayStatus:
    """因子衰减监控——持续跟踪 IC 趋势。

    判定标准：
    - HEALTHY: decay_ratio > 0.7（近期 IC ≥ 长期 70%）
    - DECAYING: 0.3 < decay_ratio ≤ 0.7（IC 显著衰减但未消失）
    - DEAD: decay_ratio ≤ 0.3（因子失效）
    - RECOVERING: 近 5 日 IC > 近 20 日 IC（衰减后回升）
    """
    if len(ic_history) < 250:
        long_term_ic = np.mean(ic_history)
        recent_ic = np.mean(ic_history[-20:]) if len(ic_history) >= 20 else np.mean(ic_history)
    else:
        long_term_ic = np.mean(ic_history[-250:])
        recent_ic = np.mean(ic_history[-20:])

    decay_ratio = recent_ic / long_term_ic if abs(long_term_ic) > 1e-6 else 0.0

    # 恢复判定
    if len(ic_history) >= 25:
        ic_5d = np.mean(ic_history[-5:])
        ic_20d = np.mean(ic_history[-20:])
        recovering = ic_5d > ic_20d and decay_ratio < 0.7
    else:
        recovering = False

    if recovering:
        status = "RECOVERING"
    elif decay_ratio > 0.7:
        status = "HEALTHY"
    elif decay_ratio > 0.3:
        status = "DECAYING"
    else:
        status = "DEAD"

    return FactorDecayStatus(
        factor_name=factor_name,
        recent_ic_20d=float(recent_ic),
        long_term_ic_250d=float(long_term_ic),
        decay_ratio=float(decay_ratio),
        status=status,
    )
```

### 3.6 分层选股与权重优化

```python
def select_stocks_by_quantile(
    combined_scores: np.ndarray,    # (N_stocks,) 综合得分
    stock_names: list[str],
    n_quantiles: int = 5,           # 分层数
    long_quantile: int = 5,         # 做多第几层（默认最高层）
    short_quantile: int = 1,        # 做空第几层（A 股不可做空，仅排除）
) -> dict:
    """分层选股——按综合得分分 N 层，做多最高层。

    A 股约束：不可做空，short_quantile 仅用于排除（不入选）
    """
    valid = ~np.isnan(combined_scores)
    valid_scores = combined_scores[valid]
    valid_names = [stock_names[i] for i in range(len(stock_names)) if valid[i]]

    quantile_edges = np.percentile(valid_scores, np.linspace(0, 100, n_quantiles + 1))

    # 多头：最高分位
    long_mask = valid_scores >= quantile_edges[-2]
    long_stocks = [valid_names[i] for i in range(len(valid_names)) if long_mask[i]]

    # 排除：最低分位
    short_mask = valid_scores <= quantile_edges[1]
    excluded_stocks = [valid_names[i] for i in range(len(valid_names)) if short_mask[i]]

    return {
        "long_stocks": long_stocks,
        "excluded_stocks": excluded_stocks,
        "quantile_edges": quantile_edges,
    }
```

### 3.7 多因子容量与换手率管理

| 维度 | 参数 | 理由 |
|---|---|---|
| **换手率** | 3-5 天 convergence | 30_multi_strategy_concurrency §6.4 |
| **单标的上限** | ≤ 5% | 多因子容量较大，但仍需分散 |
| **行业偏离** | ≤ ±5%（相对基准） | 行业中性化后的偏离控制 |
| **容量估算** | ADV 参与率 ≤ 10% | 基于个股日均成交额估算可承载资金 |

## 4. 考虑过的替代方案

| 方案 | 描述 | 拒绝理由 |
|---|---|---|
| **等权打分法** | 因子分值简单等权相加 | 忽略因子预测力差异和共线性；IC 加权更优 |
| **施密特正交** | 按指定顺序逐列正交 | 依赖顺序，有偏；对称正交不依赖顺序 |
| **PCA 正交** | 主成分分析旋转 | 解释方差递减，因子经济含义丢失 |
| **ML 组合（XGBoost/LightGBM）** | 机器学习非线性组合 | MVP 阶段过度工程；先 IC 加权，Phase 1.5+ 再 ML |
| **华泰 GPT 因子工厂 2.0** | 多智能体 LLM 因子挖掘 | MVP 无 LLM 基础设施；Phase 2+ |
| **筹码分层 AI 因子** | CNN+GRU 筹码分布 | Phase 1.5+ 深度学习平台就绪后 |
| **LLM-FADT 文本因子** | 6 类文本输入 XGBoost | Phase 1.5+ LLM 层就绪后 |

## 5. 上限定义

| 上限 | 值 | 理由 |
|---|---|---|
| **因子数量** | 10-30 个 | 太少不够分散，太多增加噪声 |
| **换手率** | 3-5 天 convergence | 30_multi_strategy_concurrency §6.4 |
| **行业偏离** | ≤ ±5% | 行业中性化后偏离控制 |
| **拥挤减仓** | HIGH 拥挤减 40%，EXTREME 减 70% | 华泰门限测试 |

**演进路径**：
- MVP：对称正交 + IC 加权 + 行业中性化 + 拥挤度门限监控
- Phase 1.5：ML 组合（XGBoost/LightGBM）+ 筹码分层 AI 因子
- Phase 2：GPT 因子工厂 + LLM-FADT 文本因子 + Hubble 闭环挖掘

## 6. 待裁定

| 项 | 暂缓理由 | 重评条件 |
|---|---|---|
| **ML 因子组合** | MVP 先 IC 加权 | Phase 1.5+ 积累 6 月 IC 数据后 |
| **筹码分层 AI 因子** | 需 CNN+GRU 平台 | Phase 1.5+ 深度学习就绪 |
| **GPT 因子工厂** | 需 LLM 基础设施 | Phase 2+ |
| **残差动量改进版** | 华泰 2026-03 年化超额 12.90% | Phase 1.5+ 因子库扩展时 |
| **IT 因子** | 西部 2026-03 RankIC 0.064 | Phase 1.5+ Level-2 数据就绪 |

## 7. 待定问题（讨论要点对齐）

- [x] ① 因子组合方式（打分/IC加权/正交化）→ §3.2 对称正交 + §3.3 IC 加权
- [x] ② 行业中性化 → §3.2 步骤 4 行业哑变量回归取残差
- [x] ③ 因子衰减监控 → §3.5 `monitor_factor_decay` IC 趋势跟踪
- [x] ④ 多因子换手率（低，3-5 天 convergence）→ §3.7 容量与换手率管理
- [x] ⑤ 多因子容量（较大，可承载主资金）→ §3.7 ADV 参与率 ≤ 10%
- [x] ⑥ 与打板策略的相关性 → 30_multi_strategy_concurrency §4.3 已定义策略间相关性管理

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G09
- [20_first_batch_strategies](20_first_batch_strategies.md)（G04 产出物，必先读）
- [15_data_feature_layer_spec](15_data_feature_layer_spec.md)（G01 因子工程，依赖项）
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §6.4（换手率差异化）
- battle_map_05_stock_selection（当前状态快照）
- **2026-08 研究引用**：
  - 因子正交全攻略 (2026-07) — 对称正交 Löwdin，年化超额+5%，IR 1.7→2.6
  - 华泰金工 (2026-06-09) "筹码分层结构端到端 AI 因子" — RankIC 12.3%
  - 华泰金工 (2026-03-17) "量化行业轮动崎岖之路" — 残差动量改进版 12.90% + 拥挤度门限
  - 兴业证券 (2026-08-05) "因子拥挤的形成机制、度量体系与风险含义" — MSCI 五维度
  - 华泰金工 (2026-07-13) "AI 模型超额收益持续修复" — 全频段融合 IR 3.01
  - 西部证券 (2026-03-17) "知情交易微观行为 IT 因子" — RankIC 0.064
  - Shi et al. (2026-03) "Hubble LLM 闭环 Alpha 因子发现" arXiv:2604.09601
  - Wang et al. (2025-09) "Alpha-GPT 2.0" arXiv:2308.00016 — WorldQuant IQC Top-10

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行 |
| 2026-08-10 | 1.0.0 | 落地 spec 定稿 | 因子预处理(去极值+标准化+行业中性化+对称正交)+IC加权合成+拥挤度门限监测+衰减监控+分层选股算法化；整合 2026-08 研究（对称正交Löwdin/华泰拥挤度门限/兴业MSCI五维度/华泰筹码分层/IT因子） |
