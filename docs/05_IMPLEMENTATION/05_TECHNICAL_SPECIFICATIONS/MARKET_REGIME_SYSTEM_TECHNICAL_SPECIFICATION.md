---
module_id: MARKET_REGIME_SYSTEM_001
version: 1.0.0
spec_version: 1.0
status: Active
parent_doc: ../01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md
last_updated: 2026-04-03
created_date: 2026-04-03
layer: Layer 2-4 (中观策略层) | 业务架构: 三级时间框架融合架构
index: MARKET_REGIME_001
estimated_hours: 160h
review_status: Pending
reviewer: 首席技术评审官
review_date: 2026-04-03
owner: 中观策略层负责人
standard_type: 专业量化机构技术规格书
applicable_scope: 全系统
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
---

# 市场状态识别系统技术规格书 v1.0

> 清风量化系统 v5.2 - 市场状态识别系统详细技术设计
> **索引**: `MARKET_REGIME_001`
> **开发时间**: 160h
> **核心定位**: 基于HMM模型和技术指标融合识别市场状态，为文艺复兴模式提供市场环境判断能力

---

## 1. 概述

### 1.1 设计背景与业务目标

**业务需求**：
- 当前系统缺失市场层面的状态识别能力，无法实现文艺复兴基金的统计套利策略
- 策略执行层缺乏对市场环境的感知，导致策略在不同市场状态下表现不稳定
- 需要实现跨市场状态的稳定超额收益，降低策略失效风险

**技术痛点**：
- 无市场状态识别模型
- 无多时间框架状态融合机制
- 无状态转换预警机制
- 无基于市场状态的策略选择建议

**预期价值**：
- 实现对市场状态的准确识别（准确率≥70%）
- 提前3-5天预警市场状态转换
- 为策略选择提供市场环境上下文
- 降低策略在不同市场状态下的失效风险

### 1.2 技术定位与架构层归属

**Layer定位**: Layer 2-4 - 中观策略层

**模块类别**: 核心模块

**架构角色**: 
- 作为文艺复兴模式的核心组件，为Alpha因子工厂提供市场状态上下文
- 作为中观层面的风险控制系统，为策略选择提供市场环境判断
- 作为日线组合优化的决策依据，指导权重调整

### 1.3 版本信息与变更记录

| 版本 | 日期 | 作者 | 变更说明 | 状态 |
|------|------|------|----------|------|
| v1.0 | 2026-04-03 | 首席技术评审官 | 初始版本 | Draft |

---

## 2. 详细架构设计

### 2.1 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                    市场状态识别系统架构                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  数据输入层                                                     │
│     ├── 日线价格数据 (OHLCV)                                    │
│     ├── 技术指标数据 (MA/MACD/RSI)                              │
│     ├── 市场微观结构数据 (订单簿/成交流)                        │
│     └── 宏观经济数据 (来自宏观配置层)                           │
│           ↓                                                     │
│  特征工程层                                                     │
│     ├── 价格特征提取                                            │
│     ├── 技术指标计算                                            │
│     ├── 微观结构特征                                            │
│     └── 宏观特征融合                                            │
│           ↓                                                     │
│  模型推理层                                                     │
│     ├── HMM隐马尔可夫模型                                       │
│     ├── 技术指标状态识别                                        │
│     ├── 微观结构分析                                            │
│     └── 多源融合决策                                            │
│           ↓                                                     │
│  输出层                                                         │
│     ├── 市场状态判断 (牛市/熊市/震荡市/转折市)                  │
│     ├── 状态置信度                                              │
│     ├── 持续时间估计                                            │
│     └── 策略建议                                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Layer定位详细说明

**Layer归属**: Layer 2-4 - 中观策略层

**职责范围**: 
- 识别当前市场状态（牛市/熊市/震荡市/转折市）
- 预测市场状态转换概率
- 评估市场状态持续时间
- 提供策略选择建议

**上下层接口**: 
- 上层依赖: 接收宏观配置层的经济范式判断
- 下层依赖: 为Alpha因子工厂提供市场状态上下文

### 2.3 模块职责与边界定义

**核心职责**: 市场状态识别与预测

**职责边界**: 
- ✅ 本模块负责: 市场状态识别、状态转换预测、策略建议生成
- ❌ 本模块不负责: 具体交易决策、仓位管理、风险控制

**接口契约**: 遵循 [INTERFACE_CONTRACT_BLUEPRINT.md](../../01_FRAMEWORK/INTERFACE_CONTRACT_BLUEPRINT.md) 中定义的 `IMarketRegimeSystem` 接口

### 2.4 依赖关系与集成点

| 依赖模块 | 依赖类型 | 接口方式 | 版本要求 | 备注 |
|----------|----------|----------|----------|------|
| **宏观配置层** | 弱依赖 | API调用 | v1.0+ | 接收经济范式判断 |
| **数据源层** | 强依赖 | 数据库查询 | v1.0+ | 获取市场数据 |
| **Alpha因子工厂** | 下游依赖 | 事件发布 | v1.0+ | 提供市场状态 |
| **绩效归因层** | 弱依赖 | 日志记录 | v1.0+ | 记录决策过程 |

---

## 3. 接口定义

### 3.1 API接口规范

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd

@dataclass
class MarketDataInput:
    """市场数据输入"""
    price_data: pd.DataFrame             # 价格数据 (OHLCV)
    volume_data: pd.DataFrame            # 成交量数据
    technical_indicators: Dict[str, pd.Series]  # 技术指标
    microstructure_data: Optional[Dict]  # 市场微观结构数据
    timestamp: datetime                  # 时间戳

@dataclass
class MarketStateOutput:
    """市场状态输出"""
    market_regime: str                   # 市场状态 (bull/bear/sideways/transition)
    trend_strength: float                # 趋势强度 [0, 1]
    volatility_level: float              # 波动率水平 [0, 1]
    liquidity_score: float               # 流动性评分 [0, 1]
    confidence: float                    # 置信度 [0, 1]
    duration_estimate: int               # 持续时间估计(天)
    transition_probability: Dict[str, float]  # 状态转换概率
    recommended_strategies: List[str]    # 推荐策略
    timestamp: datetime                  # 时间戳

class IMarketRegimeSystem(ABC):
    """市场状态识别系统接口"""
    
    @abstractmethod
    def identify_regime(self, market_data: MarketDataInput) -> MarketStateOutput:
        """识别市场状态
        
        Args:
            market_data: 市场数据输入
            
        Returns:
            MarketStateOutput: 市场状态输出
            
        Raises:
            DataValidationError: 数据验证失败
            ModelInferenceError: 模型推理失败
        """
        pass
    
    @abstractmethod
    def get_regime_probability(self, regime: str) -> float:
        """获取状态概率
        
        Args:
            regime: 市场状态
            
        Returns:
            float: 状态概率
        """
        pass
    
    @abstractmethod
    def predict_transition(self, horizon_days: int = 5) -> Dict[str, float]:
        """预测状态转换
        
        Args:
            horizon_days: 预测时间范围(天)
            
        Returns:
            Dict[str, float]: 各状态转换概率
        """
        pass
    
    @abstractmethod
    def get_regime_history(self, start_date: datetime, 
                          end_date: datetime) -> pd.DataFrame:
        """获取状态历史
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            pd.DataFrame: 状态历史数据
        """
        pass
```

### 3.2 数据格式规范

#### 3.2.1 输入数据格式

```json
{
  "price_data": {
    "open": [10.5, 10.6, 10.7],
    "high": [10.8, 10.9, 11.0],
    "low": [10.4, 10.5, 10.6],
    "close": [10.7, 10.8, 10.9],
    "volume": [1000000, 1200000, 1100000]
  },
  "technical_indicators": {
    "MA20": [10.5, 10.6, 10.7],
    "MA60": [10.3, 10.4, 10.5],
    "MACD": [0.02, 0.03, 0.04],
    "RSI": [65.5, 67.2, 69.1]
  },
  "timestamp": "2026-04-03T09:30:00Z"
}
```

#### 3.2.2 输出数据格式

```json
{
  "market_regime": "bull",
  "trend_strength": 0.75,
  "volatility_level": 0.45,
  "liquidity_score": 0.80,
  "confidence": 0.85,
  "duration_estimate": 15,
  "transition_probability": {
    "bull": 0.70,
    "bear": 0.10,
    "sideways": 0.15,
    "transition": 0.05
  },
  "recommended_strategies": [
    "momentum_strategy",
    "trend_following",
    "breakout_strategy"
  ],
  "timestamp": "2026-04-03T09:30:00Z"
}
```

### 3.3 性能指标

| 性能指标 | 目标值 | 测量方法 |
|---------|--------|---------|
| **识别延迟** | ≤ 1秒 | 从数据输入到结果输出 |
| **吞吐量** | ≥ 100次/分钟 | 并发识别能力 |
| **准确率** | ≥ 70% | 历史回测验证 |
| **可用性** | ≥ 99.9% | 系统正常运行时间 |

---

## 4. 数据模型与存储

### 4.1 数据表结构

#### 4.1.1 市场状态识别结果表 (market_regime_results)

```sql
CREATE TABLE market_regime_results (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    trade_date DATE NOT NULL COMMENT '交易日期',
    market_regime VARCHAR(20) NOT NULL COMMENT '市场状态',
    trend_strength DECIMAL(5,4) COMMENT '趋势强度',
    volatility_level DECIMAL(5,4) COMMENT '波动率水平',
    liquidity_score DECIMAL(5,4) COMMENT '流动性评分',
    confidence DECIMAL(5,4) COMMENT '置信度',
    duration_estimate INT COMMENT '持续时间估计',
    transition_probability JSON COMMENT '状态转换概率',
    recommended_strategies JSON COMMENT '推荐策略',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_trade_date (trade_date),
    INDEX idx_market_regime (market_regime)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='市场状态识别结果表';
```

#### 4.1.2 市场状态历史表 (market_regime_history)

```sql
CREATE TABLE market_regime_history (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    trade_date DATE NOT NULL COMMENT '交易日期',
    actual_regime VARCHAR(20) COMMENT '实际状态',
    predicted_regime VARCHAR(20) COMMENT '预测状态',
    prediction_accuracy DECIMAL(5,4) COMMENT '预测准确率',
    model_version VARCHAR(20) COMMENT '模型版本',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_trade_date (trade_date),
    INDEX idx_model_version (model_version)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='市场状态历史表';
```

### 4.2 数据流设计

```
数据源 (Layer 0)
    ├── iFind日线数据
    ├── 计算技术指标
    └── 获取微观结构数据
          ↓
数据预处理 (Layer 1)
    ├── 数据清洗
    ├── 特征工程
    └── 数据标准化
          ↓
模型推理 (Layer 2-4)
    ├── HMM模型推理
    ├── 技术指标分析
    └── 多源融合决策
          ↓
结果存储 (Layer 1)
    ├── 存储识别结果
    ├── 更新历史记录
    └── 发布状态变更事件
```

### 4.3 缓存策略

| 缓存类型 | 缓存内容 | 过期时间 | 更新策略 |
|---------|---------|---------|---------|
| **Redis缓存** | 当日市场状态 | 1天 | 每日更新 |
| **内存缓存** | 模型参数 | 1周 | 模型重新训练时更新 |
| **本地缓存** | 技术指标 | 1小时 | 实时计算更新 |

---

## 5. 算法实现说明

### 5.1 HMM隐马尔可夫模型

#### 5.1.1 算法原理

使用隐马尔可夫模型(HMM)识别市场状态，假设市场存在4种隐状态：
- **牛市 (Bull)**: 价格上涨趋势明显
- **熊市 (Bear)**: 价格下跌趋势明显
- **震荡市 (Sideways)**: 价格波动范围有限
- **转折市 (Transition)**: 市场状态转换期

#### 5.1.2 模型参数

```python
class HMMRegimeClassifier:
    """HMM市场状态分类器"""
    
    def __init__(self, n_states: int = 4):
        self.n_states = n_states
        self.model = None
        
    def train(self, price_data: pd.DataFrame):
        """训练HMM模型
        
        Args:
            price_data: 价格数据 (包含收益率序列)
        """
        from hmmlearn import hmm
        
        # 计算收益率序列
        returns = price_data['close'].pct_change().dropna()
        
        # 训练HMM模型
        self.model = hmm.GaussianHMM(
            n_components=self.n_states,
            covariance_type='full',
            n_iter=1000,
            random_state=42
        )
        
        self.model.fit(returns.values.reshape(-1, 1))
        
    def predict(self, price_data: pd.DataFrame) -> tuple:
        """预测市场状态
        
        Args:
            price_data: 价格数据
            
        Returns:
            tuple: (状态标签, 状态概率)
        """
        returns = price_data['close'].pct_change().dropna()
        state_sequence = self.model.predict(returns.values.reshape(-1, 1))
        state_probs = self.model.predict_proba(returns.values.reshape(-1, 1))
        
        # 映射状态标签
        state_mapping = {0: 'bull', 1: 'bear', 2: 'sideways', 3: 'transition'}
        current_state = state_mapping[state_sequence[-1]]
        current_prob = state_probs[-1].max()
        
        return current_state, current_prob
```

#### 5.1.3 复杂度分析

- **训练复杂度**: O(T × N² × M)，其中T为时间序列长度，N为状态数，M为迭代次数
- **推理复杂度**: O(T × N²)，实时推理时间 ≤ 100ms

### 5.2 技术指标状态识别

#### 5.2.1 算法原理

使用技术指标组合识别市场状态，包括：
- **趋势指标**: MA20、MA60、MACD
- **动量指标**: RSI、Stochastic、CCI
- **波动率指标**: ATR、Bollinger Band

#### 5.2.2 实现代码

```python
class TechnicalRegimeIndicator:
    """技术指标状态识别"""
    
    def analyze(self, trend_indicators: List[str],
                momentum_indicators: List[str],
                volatility_indicators: List[str]) -> TechnicalState:
        """分析技术指标状态
        
        Args:
            trend_indicators: 趋势指标列表
            momentum_indicators: 动量指标列表
            volatility_indicators: 波动率指标列表
            
        Returns:
            TechnicalState: 技术指标状态
        """
        # 计算趋势得分
        trend_score = self._calculate_trend_score(trend_indicators)
        
        # 计算动量得分
        momentum_score = self._calculate_momentum_score(momentum_indicators)
        
        # 计算波动率得分
        volatility_score = self._calculate_volatility_score(volatility_indicators)
        
        # 综合判断市场状态
        if trend_score > 0.6 and momentum_score > 0.6:
            regime = 'bull'
        elif trend_score < 0.4 and momentum_score < 0.4:
            regime = 'bear'
        elif volatility_score < 0.3:
            regime = 'sideways'
        else:
            regime = 'transition'
            
        return TechnicalState(
            regime=regime,
            trend_score=trend_score,
            momentum_score=momentum_score,
            volatility_score=volatility_score,
            confidence=self._calculate_confidence(trend_score, momentum_score)
        )
```

### 5.3 多源融合决策

#### 5.3.1 融合策略

使用加权投票机制融合多个信号源：

```python
def _fuse_decisions(self, hmm_state: str, hmm_prob: float,
                   tech_state: TechnicalState,
                   microstructure: Dict) -> str:
    """多源融合决策
    
    Args:
        hmm_state: HMM识别状态
        hmm_prob: HMM置信度
        tech_state: 技术指标状态
        microstructure: 微观结构分析结果
        
    Returns:
        str: 最终市场状态
    """
    # 权重分配
    weights = {
        'hmm': 0.4,
        'technical': 0.35,
        'microstructure': 0.25
    }
    
    # 状态投票
    state_votes = {
        'bull': 0.0,
        'bear': 0.0,
        'sideways': 0.0,
        'transition': 0.0
    }
    
    # HMM投票
    state_votes[hmm_state] += weights['hmm'] * hmm_prob
    
    # 技术指标投票
    state_votes[tech_state.regime] += weights['technical'] * tech_state.confidence
    
    # 微观结构投票
    micro_state = microstructure.get('regime', 'sideways')
    micro_conf = microstructure.get('confidence', 0.5)
    state_votes[micro_state] += weights['microstructure'] * micro_conf
    
    # 返回最高票数状态
    return max(state_votes, key=state_votes.get)
```

---

## 6. 实施技术栈

### 6.1 语言框架

| 技术组件 | 技术选型 | 版本要求 | 用途 |
|---------|---------|---------|------|
| **编程语言** | Python | 3.9+ | 主要开发语言 |
| **机器学习框架** | scikit-learn | 1.3+ | 模型训练与推理 |
| **HMM库** | hmmlearn | 0.3+ | HMM模型实现 |
| **数据处理** | pandas | 2.0+ | 数据处理与分析 |
| **数值计算** | numpy | 1.24+ | 数值计算 |

### 6.2 第三方依赖

```txt
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
hmmlearn>=0.3.0
scipy>=1.10.0
ta-lib>=0.4.28
redis>=4.5.0
sqlalchemy>=2.0.0
```

### 6.3 环境要求

| 环境类型 | CPU | 内存 | 存储 | 备注 |
|---------|-----|------|------|------|
| **开发环境** | 4核 | 16GB | 100GB SSD | 本地开发 |
| **测试环境** | 4核 | 16GB | 100GB SSD | 功能测试 |
| **生产环境** | 8核 | 32GB | 500GB SSD | 高可用部署 |

---

## 7. 测试策略

### 7.1 单元测试

| 测试模块 | 测试内容 | 覆盖率要求 |
|---------|---------|-----------|
| **HMM模型** | 训练、推理、状态映射 | ≥ 90% |
| **技术指标** | 指标计算、状态识别 | ≥ 85% |
| **融合决策** | 投票机制、权重分配 | ≥ 90% |
| **数据验证** | 输入验证、异常处理 | ≥ 95% |

### 7.2 集成测试

```python
def test_market_regime_identification():
    """测试市场状态识别流程"""
    # 1. 准备测试数据
    market_data = prepare_test_data()
    
    # 2. 调用识别接口
    result = market_regime_system.identify_regime(market_data)
    
    # 3. 验证结果
    assert result.market_regime in ['bull', 'bear', 'sideways', 'transition']
    assert 0 <= result.confidence <= 1
    assert len(result.recommended_strategies) > 0
```

### 7.3 性能测试

| 测试场景 | 性能指标 | 通过标准 |
|---------|---------|---------|
| **单次识别** | 延迟 | ≤ 1秒 |
| **并发识别** | 吞吐量 | ≥ 100次/分钟 |
| **历史回测** | 准确率 | ≥ 70% |
| **状态转换预测** | 提前天数 | ≥ 3天 |

---

## 8. 风险与约束

### 8.1 技术风险

| 风险项 | 风险等级 | 影响 | 缓解措施 |
|--------|---------|------|---------|
| **模型过拟合** | P2 | 识别准确率下降 | 交叉验证、正则化 |
| **数据质量差** | P2 | 识别结果不准确 | 数据清洗、异常检测 |
| **状态转换滞后** | P2 | 错过最佳调仓时机 | 多源融合、实时监控 |
| **极端市场失效** | P1 | 识别完全失效 | 人工干预、应急预案 |

### 8.2 实施约束

| 约束类型 | 约束内容 | 应对策略 |
|---------|---------|---------|
| **数据约束** | 需要至少3年历史数据 | 分阶段实施，先积累数据 |
| **计算约束** | HMM训练需要较多计算资源 | 使用云计算资源 |
| **时间约束** | 识别延迟必须≤1秒 | 优化算法、使用缓存 |

---

## 9. 验收标准

### 9.1 功能验收

| 验收项 | 验收标准 | 验证方法 |
|--------|---------|---------|
| **市场状态识别** | 准确率≥70% | 历史回测 |
| **状态转换预测** | 提前≥3天预警 | 事件验证 |
| **策略建议** | 推荐策略夏普比率≥1.5 | 策略回测 |
| **接口完整性** | 所有接口正常工作 | 接口测试 |

### 9.2 性能验收

| 验收项 | 验收标准 | 验证方法 |
|--------|---------|---------|
| **识别延迟** | ≤1秒 | 性能测试 |
| **吞吐量** | ≥100次/分钟 | 压力测试 |
| **可用性** | ≥99.9% | 监控统计 |

### 9.3 质量验收

| 验收项 | 验收标准 | 验证方法 |
|--------|---------|---------|
| **代码覆盖率** | ≥85% | 单元测试 |
| **文档完整性** | 100% | 文档审查 |
| **代码规范** | 符合PEP8 | 代码审查 |

---

## 10. 实施路线图

### 10.1 分阶段实施计划

#### Phase 1: 数据层开发 (Week 1-2)

| 任务 | 交付物 | 工时 | 优先级 |
|------|--------|------|--------|
| 数据采集模块 | 数据采集脚本 | 16h | P0 |
| 数据预处理模块 | 数据清洗脚本 | 12h | P0 |
| 技术指标计算模块 | 指标计算库 | 20h | P0 |

#### Phase 2: 模型开发 (Week 3-5)

| 任务 | 交付物 | 工时 | 优先级 |
|------|--------|------|--------|
| HMM模型训练 | HMM模型文件 | 24h | P0 |
| 技术指标分析模块 | 分析模块 | 16h | P0 |
| 多源融合决策模块 | 融合算法 | 20h | P0 |

#### Phase 3: 系统集成 (Week 6-7)

| 任务 | 交付物 | 工时 | 优先级 |
|------|--------|------|--------|
| API接口开发 | REST API | 16h | P0 |
| 数据库设计与实现 | 数据库表 | 12h | P0 |
| 缓存机制实现 | Redis缓存 | 8h | P1 |

#### Phase 4: 测试与优化 (Week 8)

| 任务 | 交付物 | 工时 | 优先级 |
|------|--------|------|--------|
| 单元测试 | 测试用例 | 12h | P0 |
| 集成测试 | 测试报告 | 8h | P0 |
| 性能优化 | 优化报告 | 8h | P1 |

### 10.2 关键里程碑

| 里程碑 | 时间 | 交付物 | 验收标准 |
|--------|------|--------|----------|
| **M1: 数据层完成** | Week 2 | 数据采集与预处理模块 | 数据质量≥95% |
| **M2: 模型开发完成** | Week 5 | HMM模型与融合算法 | 准确率≥65% |
| **M3: 系统集成完成** | Week 7 | 完整系统 | 所有接口正常 |
| **M4: 测试通过** | Week 8 | 测试报告 | 所有测试通过 |

### 10.3 资源需求

**人力资源**:
- 算法工程师: 1人（全职，8周）
- 后端工程师: 1人（全职，8周）
- 数据工程师: 1人（兼职，4周）
- 测试工程师: 1人（兼职，2周）

**硬件资源**:
- 开发服务器: 1台（8核CPU，32GB内存，500GB SSD）
- 测试服务器: 1台（4核CPU，16GB内存，200GB SSD）
- 生产服务器: 1台（8核CPU，32GB内存，1TB SSD）

---

## 附录

### A. 参考文献

1. **HMM模型理论**:
   - Rabiner, L.R. (1989). "A Tutorial on Hidden Markov Models and Selected Applications in Speech Recognition"
   - Hamilton, J.D. (1989). "A New Approach to the Economic Analysis of Nonstationary Time Series and the Business Cycle"

2. **市场状态识别**:
   - Renaissance Technologies. "Statistical Arbitrage and Market Regime Detection"
   - Kritzman, M. (2012). "Regime Shifts: Implications for Dynamic Strategies"

3. **开源项目参考**:
   - hmmlearn: https://github.com/hmmlearn/hmmlearn
   - TA-Lib: https://github.com/TA-Lib/ta-lib-python

### B. 术语表

| 术语 | 定义 | 上下文 |
|------|------|--------|
| **HMM** | 隐马尔可夫模型 | 市场状态识别模型 |
| **市场状态** | 市场的整体运行状态 | 牛市、熊市、震荡市、转折市 |
| **状态转换** | 市场从一个状态转换到另一个状态 | 转换预警 |
| **多源融合** | 多个信号源的融合决策 | 提高识别准确率 |

### C. 变更记录

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|----------|------|
| v1.0 | 2026-04-03 | 初始版本 | 首席技术评审官 |

---

**技术规格书版本**: v1.0 | **创建日期**: 2026-04-03 | **状态**: Draft | **下一步**: 技术评审
