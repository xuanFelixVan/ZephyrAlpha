---
module_id: FACTOR_DOC_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构师
standard_type: 专业量化机构因子标准
applicable_scope: 因子研究与管理
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行中
---

# 5900因子筛选策略 (Factor Screening Strategy)

> **版本**: v1.0
> **创建日期**: 2026-03-30
> **Layer**: Layer 2 (因子层)
> **目标**: 从5900个iFinD因子中筛选出20-30个有效因子
> **索引**: F.02.METHOD.008

---

## 1. 概述

### 1.1 背景

ZephyrAlpha使用iFinD数据源的5900+预计算因子，这些因子包括：
- 技术指标（均线、MACD、RSI等）
- 基本面因子（PE、PB、ROE等）
- 资金流因子（北向资金、融资融券等）
- 另类因子（舆情、搜索指数等）

### 1.2 筛选目标

| 阶段 | 目标 | 说明 |
|------|------|------|
| **初筛** | 5900 → 200-300 | 基于IC初步筛选 |
| **复筛** | 300 → 50-100 | 基于ICIR和稳定性 |
| **精选** | 100 → 20-30 | 最终有效因子库 |

### 1.3 资金规模约束

| 项目 | 数值 | 说明 |
|------|------|------|
| **实盘资金** | 45万人民币 | ~6万美元 |
| **股票持仓上限** | 10-15只 | 单只仓位3-5万 |
| **因子数量上限** | 20-30个 | 分散度过高不利管理 |

---

## 2. 筛选流程

### 2.1 整体流程图

```
┌─────────────────────────────────────────────────────────────────────┐
│                    5900因子筛选流程                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    阶段1: 初筛 (5900 → 300)                   │   │
│  │  ├── 数据完整性检查 (缺失率 < 10%)                           │   │
│  │  ├── IC均值筛选 (IC > 0.02)                                 │   │
│  │  └── 去极值处理                                             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              ↓                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    阶段2: 复筛 (300 → 80)                     │   │
│  │  ├── ICIR筛选 (ICIR > 0.3)                                  │   │
│  │  ├── IC稳定性检验 (滚动IC胜率 > 55%)                         │   │
│  │  ├── IC衰减测试 (近60天 vs 历史)                            │   │
│  │  └── 相关性去重 (与现有因子相关性 < 0.85)                    │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              ↓                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    阶段3: 精选 (80 → 25)                     │   │
│  │  ├── 分层确定 (核心/卫星/实验)                               │   │
│  │  ├── 因子组合IC验证                                          │   │
│  │  ├── 单因子回测验证                                          │   │
│  │  └── 人工审核 (可选)                                         │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              ↓                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    阶段4: 入库与监控                          │   │
│  │  ├── 因子注册表更新                                          │   │
│  │  ├── IC监控配置                                              │   │
│  │  └── 生命周期启动                                            │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. 阶段1: 初筛 (5900 → 300)

### 3.1 数据完整性检查

```python
def check_data_completeness(factor_data: pd.DataFrame) -> dict:
    """检查数据完整性

    筛选条件: 缺失率 < 10%
    """
    total_expected = len(factor_data) * len(factor_data.columns)
    total_actual = factor_data.count().sum()
    missing_ratio = 1 - total_actual / total_expected

    return {
        'missing_ratio': missing_ratio,
        'passed': missing_ratio < 0.10
    }
```

### 3.2 IC均值筛选

```python
def screen_by_ic_mean(factor_data: pd.DataFrame,
                      returns: pd.Series,
                      ic_threshold: float = 0.02) -> List[str]:
    """基于IC均值的筛选

    筛选条件: IC均值 > 0.02
    """
    valid_factors = []

    for factor_id in factor_data.columns:
        ic_series = calculate_ic_series(factor_data[factor_id], returns)
        ic_mean = ic_series.mean()

        if ic_mean > ic_threshold:
            valid_factors.append(factor_id)

    return valid_factors
```

### 3.3 去极值处理

```python
def winsorize_factor(factor_values: pd.Series,
                    lower: float = 0.01,
                    upper: float = 0.99) -> pd.Series:
    """去极值处理

    使用分位数去极值，避免极端值影响IC计算
    """
    lower_bound = factor_values.quantile(lower)
    upper_bound = factor_values.quantile(upper)

    return factor_values.clip(lower_bound, upper_bound)
```

---

## 4. 阶段2: 复筛 (300 → 80)

### 4.1 ICIR筛选

```python
def screen_by_icir(ic_series: pd.Series, icir_threshold: float = 0.3) -> bool:
    """基于ICIR的筛选

    ICIR = IC均值 / IC标准差
    筛选条件: ICIR > 0.3
    """
    ic_mean = ic_series.mean()
    ic_std = ic_series.std()

    if ic_std == 0:
        return False

    icir = ic_mean / ic_std
    return icir > icir_threshold
```

### 4.2 IC稳定性检验

```python
def check_ic_stability(ic_series: pd.Series,
                       window: int = 20,
                       win_rate_threshold: float = 0.55) -> bool:
    """IC稳定性检验

    筛选条件: 滚动窗口胜率 > 55%
    """
    rolling_positive = ic_series.rolling(window).apply(
        lambda x: (x > 0).mean(), raw=False
    )

    avg_win_rate = rolling_positive.mean()
    return avg_win_rate > win_rate_threshold
```

### 4.3 IC衰减测试

```python
def check_ic_decay(ic_series: pd.Series,
                   recent_window: int = 60,
                   baseline_window: int = 252) -> dict:
    """IC衰减测试

    检测因子是否正在衰减
    """
    recent_ic = ic_series.tail(recent_window).mean()
    baseline_ic = ic_series.tail(baseline_window).mean()

    if baseline_ic == 0:
        return {'decay_rate': 0, 'is_decaying': False}

    decay_rate = (baseline_ic - recent_ic) / baseline_ic

    return {
        'recent_ic': recent_ic,
        'baseline_ic': baseline_ic,
        'decay_rate': decay_rate,
        'is_decaying': decay_rate > 0.3  # 衰减超过30%视为衰减
    }
```

### 4.4 相关性去重

```python
def remove_correlated_factors(factor_data: pd.DataFrame,
                               correlation_threshold: float = 0.85) -> List[str]:
    """相关性去重

    筛选条件: 与现有因子相关性 < 0.85
    保留IC更高的因子
    """
    correlation_matrix = factor_data.corr()
    selected_factors = []
    rejected_factors = []

    for factor_id in factor_data.columns:
        is_redundant = False

        for selected_id in selected_factors:
            corr = correlation_matrix.loc[factor_id, selected_id]

            if abs(corr) > correlation_threshold:
                is_redundant = True
                rejected_factors.append(factor_id)
                break

        if not is_redundant:
            selected_factors.append(factor_id)

    return selected_factors
```

---

## 5. 阶段3: 精选 (80 → 25)

### 5.1 分层确定

```python
def assign_tier(ic_mean: float, ic_ir: float,
                stability_score: float) -> str:
    """因子分层

    Returns:
        'core' / 'satellite' / 'experimental'
    """
    # 核心因子: IC > 0.05 且 ICIR > 0.5 且稳定
    if ic_mean > 0.05 and ic_ir > 0.5 and stability_score > 0.6:
        return 'core'

    # 卫星因子: IC > 0.03 且 ICIR > 0.3
    if ic_mean > 0.03 and ic_ir > 0.3:
        return 'satellite'

    # 实验因子: IC > 0.02
    if ic_mean > 0.02:
        return 'experimental'

    return 'reject'
```

### 5.2 因子组合IC验证

```python
def validate_factor_combination(factor_data: pd.DataFrame,
                                returns: pd.Series,
                                max_combination_ic_drop: float = 0.2) -> bool:
    """因子组合IC验证

    验证多因子组合后的IC是否在可接受范围内
    """
    # 计算等权组合因子值
    combined_factor = factor_data.mean(axis=1)

    # 计算组合IC
    combined_ic = calculate_ic_series(combined_factor, returns).mean()

    # 计算单因子平均IC
    single_ic_list = [
        calculate_ic_series(factor_data[col], returns).mean()
        for col in factor_data.columns
    ]
    avg_single_ic = np.mean(single_ic_list)

    # IC下降不超过20%
    ic_drop = (avg_single_ic - combined_ic) / avg_single_ic
    return ic_drop < max_combination_ic_drop
```

### 5.3 单因子回测验证

```python
def single_factor_backtest(factor_data: pd.DataFrame,
                          returns: pd.Series,
                          top_pct: float = 0.2,
                          holding_period: int = 5) -> dict:
    """单因子回测验证

    简单的多空组合回测
    """
    results = []

    for date in factor_data.index:
        if date not in returns.index:
            continue

        # 获取当日因子值
        factor_values = factor_data.loc[date].dropna()

        # 获取top 20%的因子值
        threshold = factor_values.quantile(1 - top_pct)
        long_symbols = factor_values[factor_values >= threshold].index

        # 获取后5日收益
        future_returns = returns.loc[date:].head(holding_period).mean()

        results.append({
            'date': date,
            'long_return': future_returns.mean(),
            'n_positions': len(long_symbols)
        })

    results_df = pd.DataFrame(results)

    return {
        'avg_return': results_df['long_return'].mean(),
        'sharpe_ratio': results_df['long_return'].mean() / results_df['long_return'].std(),
        'win_rate': (results_df['long_return'] > 0).mean()
    }
```

---

## 6. 筛选参数配置

### 6.1 三阶段筛选参数

```yaml
# config/factor_screening.yaml

factor_screening:
  # 阶段1: 初筛
  stage1:
    data_completeness_threshold: 0.10  # 缺失率 < 10%
    ic_mean_threshold: 0.02            # IC均值 > 0.02

  # 阶段2: 复筛
  stage2:
    icir_threshold: 0.3                 # ICIR > 0.3
    stability_window: 20               # 滚动窗口
    stability_win_rate: 0.55           # 胜率 > 55%
    decay_threshold: 0.30              # 衰减 < 30%
    correlation_threshold: 0.85        # 相关性 < 0.85

  # 阶段3: 精选
  stage3:
    # 分层阈值
    core_ic_mean: 0.05
    core_icir: 0.5
    satellite_ic_mean: 0.03
    satellite_icir: 0.3
    experimental_ic_mean: 0.02

    # 组合验证
    max_ic_drop: 0.20                  # IC下降 < 20%

    # 回测参数
    top_pct: 0.20                      # top 20%
    holding_period: 5                   # 持有5日
    min_sharpe: 0.5                    # 夏普 > 0.5

  # 最终因子数量
  target_factors:
    core: 5-10
    satellite: 20-30
    experimental: 20
    total_active: 50
    recommended: 25
```

---

## 7. 预期结果

### 7.1 筛选漏斗

```
┌─────────────────────────────────────────────────────────────────────┐
│                        筛选漏斗                                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│    5900  ████████████████████████████████████████████████████      │
│          │                                                   │      │
│          ▼                                                   │      │
│     300  ████████████  (5%)                                  │      │
│          │ 阶段1初筛: 数据完整性 + IC均值                      │      │
│          ▼                                                   │      │
│      80  ████████  (1.4%)                                   │      │
│          │ 阶段2复筛: ICIR + 稳定性 + 衰减 + 相关性            │      │
│          ▼                                                   │      │
│      25  ████  (0.4%)                                       │      │
│          │ 阶段3精选: 分层 + 组合验证 + 回测                    │      │
│          ▼                                                   │      │
│      20-30  有效因子库                                         │      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 7.2 分层预期

| 层级 | 预期数量 | IC范围 | 仓位权重 |
|------|----------|--------|----------|
| **核心因子** | 5-10个 | 0.05+ | 30% |
| **卫星因子** | 15-20个 | 0.03-0.05 | 50% |
| **实验因子** | 5-10个 | 0.02-0.03 | 20% |

---

## 8. 筛选时间估计

| 阶段 | 数据量 | 计算时间(估算) |
|------|--------|----------------|
| **阶段1** | 5900因子 | ~30分钟 |
| **阶段2** | 300因子 | ~15分钟 |
| **阶段3** | 80因子 | ~10分钟 |
| **总计** | - | ~1小时 |

---

## 9. 索引

| 文档 | 说明 |
|------|------|
| [因子库总览](../README.md) | 因子库整体介绍 |
| [因子管理标准](./FACTOR_MANAGEMENT_STANDARD.md) | 专业机构做法（分层/IC阈值/生命周期） |
| [因子监控](../07_FACTOR_MONITORING/factor_monitoring.md) | IC监控/衰减预警 |

---

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-30 | 初始版本 |
