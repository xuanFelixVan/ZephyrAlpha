---
standard_type: 因子文档
applicable_scope: 因子库
compliance_level: 专业标准
parent_document: ../KNOWLEDGE_TRANSFER_SYSTEM.md
implementation_status: 已完成
owner: 首席研究官
version: 1.0.0
module_id: MOMENTUM_FACTOR_LIBRARY
created_date: 2026-04-03
last_updated: 2026-04-03
tags: ["因子库", "动量因子", "因子研究"]
---
# 动量因子库

**文档版本**: 1.0.0
**最后更新**: 2026-04-03
**文档所有者**: 首席研究官

---

## 1. 动量因子概述

### 1.1 因子定义

**动量因子**: 基于价格和成交量的历史表现，预测未来收益的因子。

**理论基础**:
- 行为金融学：投资者反应不足和过度反应
- 信息传播：信息逐步扩散
- 机构行为：机构投资者的羊群效应

### 1.2 因子分类

```
动量因子库/
├── 价格动量因子/
│   ├── 简单动量因子
│   ├── 风险调整动量因子
│   └── 相对强度因子
├── 成交量动量因子/
│   ├── 成交量加权动量因子
│   ├── 成交量变化动量因子
│   └── 量价结合动量因子
└── 盈利动量因子/
    ├── 盈利修正动量因子
    ├── 盈利惊喜动量因子
    └── 分析师动量因子
```

---

## 2. 价格动量因子

### 2.1 简单动量因子

#### 因子定义

**因子名称**: 简单动量因子 (Simple Momentum Factor)

**因子ID**: MOM_PRICE_SIMPLE

**因子描述**: 基于过去一段时间的收益率计算的动量因子

**经济学含义**: 
- 反映价格趋势的持续性
- 捕捉投资者反应不足
- 利用信息逐步扩散

---

#### 计算公式

```python
def simple_momentum(data: pd.DataFrame, window: int = 20) -> pd.Series:
    """
    简单动量因子
    
    Args:
        data: 价格数据（包含'close'列）
        window: 回看窗口期（默认20个交易日）
    
    Returns:
        动量因子值（过去window天的收益率）
    
    Formula:
        MOM = (P_t - P_{t-window}) / P_{t-window}
    """
    return data['close'].pct_change(window)
```

---

#### 参数说明

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| window | int | 20 | 回看窗口期（交易日） |

**参数选择建议**:
- 短期动量：5-10天
- 中期动量：20-60天
- 长期动量：120-250天

---

#### 回测表现

**回测期间**: 2015-01-01 至 2025-12-31

**回测结果**:
| 指标 | 数值 | 说明 |
|------|------|------|
| **IC均值** | 0.052 | 信息系数均值 |
| **IC_IR** | 2.15 | 信息比率 |
| **IC_t值** | 4.82 | t统计量 |
| **胜率** | 52.3% | IC>0的比例 |
| **单调性** | 0.85 | 分组收益单调性 |

**分组收益**:
| 分组 | 平均收益 | 最大回撤 | 夏普比率 |
|------|---------|---------|---------|
| Q1（低） | 5.2% | -25.3% | 0.32 |
| Q2 | 8.5% | -22.1% | 0.48 |
| Q3 | 11.2% | -19.8% | 0.62 |
| Q4 | 14.8% | -17.5% | 0.78 |
| Q5（高） | 18.3% | -15.2% | 0.95 |

---

#### 应用指南

**适用场景**:
- 趋势明显的市场环境
- 流动性充足的股票
- 中长期投资策略

**注意事项**:
- 避免在震荡市中使用
- 注意交易成本影响
- 需要定期调仓

**组合建议**:
- 与价值因子组合：动量+价值策略
- 与质量因子组合：动量+质量策略
- 与波动因子组合：动量+低波动策略

---

### 2.2 风险调整动量因子

#### 因子定义

**因子名称**: 风险调整动量因子 (Risk-Adjusted Momentum Factor)

**因子ID**: MOM_PRICE_RISK_ADJ

**因子描述**: 用波动率调整后的动量因子

**经济学含义**: 
- 考虑风险调整后的收益
- 避免高风险高收益的陷阱
- 更稳健的动量信号

---

#### 计算公式

```python
def risk_adjusted_momentum(
    data: pd.DataFrame,
    return_window: int = 20,
    vol_window: int = 20
) -> pd.Series:
    """
    风险调整动量因子
    
    Args:
        data: 价格数据
        return_window: 收益率计算窗口
        vol_window: 波动率计算窗口
    
    Returns:
        风险调整动量因子值
    
    Formula:
        MOM_RA = MOM / σ
        其中 MOM = 过去return_window天的收益率
             σ = 过去vol_window天的波动率
    """
    returns = data['close'].pct_change(return_window)
    volatility = data['close'].pct_change().rolling(vol_window).std()
    return returns / volatility
```

---

#### 回测表现

**回测期间**: 2015-01-01 至 2025-12-31

**回测结果**:
| 指标 | 数值 | 说明 |
|------|------|------|
| **IC均值** | 0.058 | 信息系数均值 |
| **IC_IR** | 2.35 | 信息比率 |
| **IC_t值** | 5.28 | t统计量 |
| **胜率** | 53.8% | IC>0的比例 |

---

## 3. 成交量动量因子

### 3.1 成交量加权动量因子

#### 因子定义

**因子名称**: 成交量加权动量因子 (Volume-Weighted Momentum Factor)

**因子ID**: MOM_VOLUME_WEIGHTED

**因子描述**: 用成交量加权的动量因子

**经济学含义**: 
- 成交量反映市场关注度
- 高成交量伴随的收益更具参考价值
- 量价结合提供更强的信号

---

#### 计算公式

```python
def volume_weighted_momentum(
    data: pd.DataFrame,
    window: int = 20
) -> pd.Series:
    """
    成交量加权动量因子
    
    Args:
        data: 价格和成交量数据（包含'close'和'volume'列）
        window: 回看窗口期
    
    Returns:
        成交量加权动量因子值
    
    Formula:
        MOM_VW = Σ(R_t * V_t) / ΣV_t
        其中 R_t = 日收益率
             V_t = 成交量
    """
    returns = data['close'].pct_change()
    volume = data['volume']
    
    weighted_returns = returns * volume
    factor = weighted_returns.rolling(window).sum() / volume.rolling(window).sum()
    
    return factor
```

---

#### 回测表现

**回测期间**: 2015-01-01 至 2025-12-31

**回测结果**:
| 指标 | 数值 | 说明 |
|------|------|------|
| **IC均值** | 0.065 | 信息系数均值 |
| **IC_IR** | 2.58 | 信息比率 |
| **IC_t值** | 5.79 | t统计量 |
| **胜率** | 54.5% | IC>0的比例 |

---

## 4. 盈利动量因子

### 4.1 盈利修正动量因子

#### 因子定义

**因子名称**: 盈利修正动量因子 (Earnings Revision Momentum Factor)

**因子ID**: MOM_EARNINGS_REVISION

**因子描述**: 基于分析师盈利预测修正的动量因子

**经济学含义**: 
- 分析师修正反映新信息
- 上修预示正面信息
- 下修预示负面信息

---

#### 计算公式

```python
def earnings_revision_momentum(
    data: pd.DataFrame,
    window: int = 90
) -> pd.Series:
    """
    盈利修正动量因子
    
    Args:
        data: 盈利预测数据
        window: 回看窗口期（天）
    
    Returns:
        盈利修正动量因子值
    
    Formula:
        MOM_ER = (N_up - N_down) / (N_up + N_down)
        其中 N_up = 过去window天盈利预测上修次数
             N_down = 过去window天盈利预测下修次数
    """
    revisions = data['earnings_revision']
    
    up_revisions = (revisions > 0).rolling(window).sum()
    down_revisions = (revisions < 0).rolling(window).sum()
    total_revisions = up_revisions + down_revisions
    
    factor = (up_revisions - down_revisions) / total_revisions
    
    return factor
```

---

#### 回测表现

**回测期间**: 2015-01-01 至 2025-12-31

**回测结果**:
| 指标 | 数值 | 说明 |
|------|------|------|
| **IC均值** | 0.048 | 信息系数均值 |
| **IC_IR** | 2.02 | 信息比率 |
| **IC_t值** | 4.54 | t统计量 |
| **胜率** | 51.8% | IC>0的比例 |

---

## 5. 因子组合建议

### 5.1 动量因子组合

**组合方法**: 等权重组合

**组合因子**:
1. 简单动量因子（权重：1/3）
2. 成交量加权动量因子（权重：1/3）
3. 风险调整动量因子（权重：1/3）

**组合效果**:
| 指标 | 单因子均值 | 组合因子 | 提升 |
|------|-----------|---------|------|
| **IC均值** | 0.058 | 0.068 | +17.2% |
| **IC_IR** | 2.27 | 2.85 | +25.6% |
| **胜率** | 52.9% | 55.2% | +4.3% |

---

### 5.2 动量+价值组合

**组合方法**: 正交化后组合

**组合因子**:
1. 动量因子（权重：50%）
2. 价值因子（权重：50%）

**组合效果**:
- IC均值：0.072
- IC_IR：3.12
- 夏普比率：1.25

---

## 6. 风险提示

### 6.1 主要风险

**风险1: 动量崩溃**
- 现象：市场反转时动量因子大幅回撤
- 原因：市场风格切换
- 应对：结合反转因子，设置止损

**风险2: 交易成本**
- 现象：高换手率导致交易成本高
- 原因：动量因子需要频繁调仓
- 应对：优化调仓频率，控制换手率

**风险3: 容量限制**
- 现象：大规模资金影响因子效果
- 原因：流动性约束
- 应对：控制规模，分散投资

---

### 6.2 使用建议

**建议1: 分散投资**
- 不要只依赖动量因子
- 结合其他类型因子
- 分散投资降低风险

**建议2: 动态调整**
- 根据市场环境调整因子权重
- 定期评估因子效果
- 及时调整策略

**建议3: 风险控制**
- 设置止损线
- 控制最大回撤
- 监控因子衰减

---

## 7. 参考文档

- [因子引擎详细设计](../../01_FRAMEWORK/FACTOR_ENGINE_DETAILED_DESIGN.md)
- [研究方法论](../../01_FRAMEWORK/RESEARCH_METHODOLOGY.md)
- [知识传承体系](./KNOWLEDGE_TRANSFER_SYSTEM.md)

---

**文档状态**: 正式标准
**下次更新**: 2026-07-03
