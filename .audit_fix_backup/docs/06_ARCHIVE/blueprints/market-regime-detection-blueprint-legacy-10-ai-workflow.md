---
module_id: MARKET_REGIME_DETECTION_BLUEPRINT_LEGACY_10_AI_WORKFLOW
version: 1.0.0
status: Active
created_date: 2026-04-13
last_updated: 2026-04-13
owner: 首席文档架构师
layer: layer_00
responsibility: 20260410_c2_market_regime_detection
---







> **归档说明（2026-04-10）**：删除前 `10_AI_WORKFLOW` 稿快照。**正式蓝图**：MARKET_REGIME_DETECTION_BLUEPRINT；**工作流入口 stub**：MARKET_REGIME_DETECTION_AI_WORKFLOW_ENTRY。

---
module_id: MARKET_REGIME_DETECTION_AI_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: '2026-04-07'
owner: 首席蓝图架构师
responsibility:
- 市场状态识别蓝图 (MARKET_REGIME_DETECTION)文档
layer: Layer 7 (AI报告层)
standard_type: 专业量化机构蓝图
applicable_scope: 市场状态识别与分类
compliance_level: 顶级专业标准
parent_document: INDEX.md
implementation_status: 蓝图阶段
reference_models: null
open_source_solution: hmmlearn + 自研
priority: P1
---
## 文档职责说明

**本文档职责**: 市场状态识别蓝图
- 牛熊识别、波动率状态、趋势判断、市场转折点检测

# 市场状态识别蓝图 (MARKET_REGIME_DETECTION)

> **版本**: v1.0
> **创建日期**: 2026-04-07
> **Layer**: Layer 7 (AI报告层)
> **开源替代**: hmmlearn + 自研
> **成熟度**: ⭐⭐⭐⭐⭐ (顶级专业标准)

---

## 一、模块概述

### 1.1 定位与目标

**核心定位**: 识别市场当前状态（牛市/熊市/震荡），为策略选择和风险控制提供依据。

**业务价值**:
- ✅ **策略适配**: 不同市场状态使用不同策略
- ✅ **风险预警**: 提前识别市场转折
- ✅ **仓位调整**: 根据市场状态调整仓位
- ✅ **收益优化**: 优化不同市场状态下的收益

### 1.2 专业机构对标

| 机构 | 实现方式 | 本方案 |
|-----|---------|-------|
| Renaissance | 市场状态模型 | HMM + 自研 |
| Two Sigma | Regime分类系统 | hmmlearn |
| Citadel | 市场环境识别 | 自研 |

---

## 二、架构设计

### 2.1 市场状态分类

```
┌─────────────────────────────────────────────────────────────────────┐
│                       市场状态分类体系                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  趋势状态 (Trend Regime)                                            │
│  ├── 牛市 (Bull Market)                                            │
│  │   └── 特征: 上涨趋势、低波动、高成交量                           │
│  ├── 熊市 (Bear Market)                                            │
│  │   └── 特征: 下跌趋势、高波动、恐慌情绪                           │
│  └── 震荡 (Sideways)                                               │
│      └── 特征: 无明显趋势、中等波动                                 │
│                                                                     │
│  波动率状态 (Volatility Regime)                                     │
│  ├── 低波动 (Low Volatility)                                       │
│  │   └── 特征: 波动率低于历史均值                                   │
│  ├── 中波动 (Medium Volatility)                                    │
│  │   └── 特征: 波动率接近历史均值                                   │
│  └── 高波动 (High Volatility)                                      │
│      └── 特征: 波动率高于历史均值                                   │
│                                                                     │
│  流动性状态 (Liquidity Regime)                                      │
│  ├── 高流动性 (High Liquidity)                                     │
│  ├── 中流动性 (Medium Liquidity)                                   │
│  └── 低流动性 (Low Liquidity)                                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 系统架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                    市场状态识别系统架构                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    数据输入层 (Data Input)                   │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │   │
│  │  │价格数据  │  │成交量    │  │波动率    │  │技术指标  │    │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    模型层 (Model Layer)                      │   │
│  │  ┌──────────────────┐  ┌──────────────────┐                 │   │
│  │  │  HMM模型         │  │  规则引擎        │                 │   │
│  │  │  (hmmlearn)      │  │  (自研)          │                 │   │
│  │  └──────────────────┘  └──────────────────┘                 │   │
│  │  ┌──────────────────┐  ┌──────────────────┐                 │   │
│  │  │  变点检测        │  │  集成模型        │                 │   │
│  │  │  (ruptures)      │  │  (自研)          │                 │   │
│  │  └──────────────────┘  └──────────────────┘                 │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    输出层 (Output Layer)                     │   │
│  │  ┌──────────────────┐  ┌──────────────────┐                 │   │
│  │  │  状态识别        │  │  转换预警        │                 │   │
│  │  │  (自研)          │  │  (预警系统)      │                 │   │
│  │  └──────────────────┘  └──────────────────┘                 │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 三、技术实现

### 3.1 开源组件选型

| 组件 | 开源项目 | 版本 | 功能 | 成熟度 |
|-----|---------|------|------|-------|
| HMM模型 | hmmlearn | 0.3+ | 隐马尔可夫模型 | ⭐⭐⭐⭐ |
| 变点检测 | ruptures | 1.1+ | 变点检测算法 | ⭐⭐⭐⭐ |
| 信号处理 | scipy | 1.11+ | 信号滤波 | ⭐⭐⭐⭐⭐ |

### 3.2 HMM市场状态识别

```python
from hmmlearn import hmm
import numpy as np

class MarketRegimeHMM:
    def __init__(self, n_states=3):
        self.model = hmm.GaussianHMM(
            n_components=n_states,
            covariance_type="full",
            n_iter=1000
        )
        
    def fit(self, returns, volatility):
        """训练HMM模型"""
        features = np.column_stack([returns, volatility])
        self.model.fit(features)
        
    def predict(self, returns, volatility):
        """预测市场状态"""
        features = np.column_stack([returns, volatility])
        states = self.model.predict(features)
        return states
    
    def get_state_probability(self, returns, volatility):
        """获取状态概率"""
        features = np.column_stack([returns, volatility])
        probs = self.model.predict_proba(features)
        return probs
```

### 3.3 规则引擎状态识别

```python
def detect_trend_regime(prices, window=20):
    """基于规则的趋势状态识别"""
    ma = prices.rolling(window).mean()
    current_price = prices.iloc[-1]
    current_ma = ma.iloc[-1]
    
    # 计算趋势强度
    trend_strength = (current_price - current_ma) / current_ma
    
    if trend_strength > 0.05:
        return 'BULL'
    elif trend_strength < -0.05:
        return 'BEAR'
    else:
        return 'SIDEWAYS'

def detect_volatility_regime(returns, window=20):
    """基于规则的波动率状态识别"""
    vol = returns.rolling(window).std()
    current_vol = vol.iloc[-1]
    vol_percentile = (vol < current_vol).mean()
    
    if vol_percentile > 0.8:
        return 'HIGH_VOL'
    elif vol_percentile < 0.2:
        return 'LOW_VOL'
    else:
        return 'MEDIUM_VOL'
```

---

## 四、功能模块

### 4.1 牛熊市场识别

| 功能 | 描述 | 技术实现 |
|-----|------|---------|
| 趋势识别 | 识别市场趋势方向 | HMM + 规则 |
| 牛市判断 | 判断是否处于牛市 | 多指标综合 |
| 熊市判断 | 判断是否处于熊市 | 多指标综合 |
| 震荡判断 | 判断是否处于震荡 | 多指标综合 |

### 4.2 波动率状态分类

| 功能 | 描述 | 技术实现 |
|-----|------|---------|
| 波动率计算 | 计算历史波动率 | pandas |
| 状态分类 | 波动率状态分类 | HMM + 规则 |
| 趋势预测 | 波动率趋势预测 | 时间序列模型 |
| 异常检测 | 波动率异常检测 | 统计检验 |

### 4.3 趋势判断

| 功能 | 描述 | 技术实现 |
|-----|------|---------|
| 趋势强度 | 计算趋势强度 | 技术指标 |
| 趋势方向 | 判断趋势方向 | 多指标投票 |
| 趋势持续性 | 评估趋势持续性 | 自研 |
| 趋势转折 | 检测趋势转折点 | 变点检测 |

### 4.4 市场转折点检测

| 功能 | 描述 | 技术实现 |
|-----|------|---------|
| 变点检测 | 检测市场结构变化 | ruptures |
| 转折预警 | 市场转折预警 | 自研 |
| 历史分析 | 历史转折点分析 | 自研 |
| 概率估计 | 转折概率估计 | HMM |

---

## 五、接口定义

### 5.1 核心API

```python
class MarketRegimeDetector:
    def detect_regime(self, market_data: DataFrame) -> RegimeResult:
        """检测市场状态"""
        pass
    
    def get_regime_probability(self, market_data: DataFrame) -> Dict[str, float]:
        """获取状态概率"""
        pass
    
    def detect_regime_change(self, market_data: DataFrame) -> List[ChangePoint]:
        """检测状态转换点"""
        pass
    
    def get_regime_history(self, start_date: date, end_date: date) -> List[RegimeResult]:
        """获取历史状态"""
        pass
```

### 5.2 数据结构

```python
class RegimeResult(BaseModel):
    timestamp: datetime
    trend_regime: str  # BULL, BEAR, SIDEWAYS
    volatility_regime: str  # HIGH_VOL, MEDIUM_VOL, LOW_VOL
    liquidity_regime: str  # HIGH_LIQ, MEDIUM_LIQ, LOW_LIQ
    confidence: float
    state_probability: Dict[str, float]

class ChangePoint(BaseModel):
    timestamp: datetime
    from_regime: str
    to_regime: str
    confidence: float
    detection_method: str
```

---

## 六、实施路径

### 6.1 Phase 1: 基础识别（1周）

- [ ] HMM模型实现
- [ ] 规则引擎实现
- [ ] 基础状态识别
- [ ] 结果存储

### 6.2 Phase 2: 高级功能（1周）

- [ ] 变点检测集成
- [ ] 多模型融合
- [ ] 状态转换预警
- [ ] 历史分析

### 6.3 Phase 3: 应用集成（1周）

- [ ] 与策略系统集成
- [ ] 与风控系统集成
- [ ] 可视化展示
- [ ] 文档完善

---

## 七、质量指标

| 指标 | 目标值 | 监控方式 |
|-----|-------|---------|
| 状态识别准确率 | >70% | 回测验证 |
| 转折点检测延迟 | <5天 | 统计分析 |
| 模型稳定性 | 高 | 滚动验证 |
| 预警及时性 | <1天 | 日志监控 |

---

## 八、风险评估

| 风险 | 影响 | 缓解措施 |
|-----|------|---------|
| 模型误判 | 高 | 多模型融合 + 人工确认 |
| 检测延迟 | 中 | 实时监控 + 预警 |
| 过拟合 | 中 | 交叉验证 + 正则化 |
| 市场变化 | 中 | 定期更新模型 |

---

**版本**: v1.0 | **更新**: 2026-04-07 | **状态**: ✅ 蓝图完成
