---
module_id: LIQUIDITY_MANAGEMENT_SYSTEM_SPEC_001
version: 1.0.0
spec_version: 1.0
status: Active
parent_doc: ../01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md
last_updated: 2026-04-02
created_date: 2026-04-02
layer: Layer 5 (中观策略层) | 业务架构: 三级时间框架融合架构
index: LIQUIDITY_MGMT_001
estimated_hours: 80h
review_status: Pending
reviewer: 首席技术评审官
review_date: 2026-04-02
owner: 个人开发者
standard_type: 专业量化机构技术规格书
applicable_scope: 全系统
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
---

# 流动性管理系统技术规格书 v1.0

> 清风量化系统 v5.2 - 流动性管理系统详细技术设计
> **索引**: `LIQUIDITY_MGMT_001`
> **开发时间**: 80h
> **核心定位**: 监控资金流动性，预测资金需求，优化资金配置，实现桥水模式的流动性管理能力

---

## 1. 概述

### 1.1 设计背景与业务目标

**业务需求**：
- 当前系统缺乏流动性管理能力，无法预测资金需求
- 资金使用效率低，闲置资金过多或资金紧张
- 缺乏流动性风险预警机制
- 需要实现桥水模式的流动性管理能力

**技术痛点**：
- 无资金流动性监控系统
- 无现金流预测模型
- 无流动性风险预警机制
- 无资金优化配置系统

**预期价值**：
- 实时监控资金流动性，提前预警资金风险
- 预测资金需求，优化资金配置
- 提高资金使用效率20-30%
- 实现桥水模式的流动性管理能力

### 1.2 技术定位与架构层归属

**Layer定位**: Layer 5 - 策略执行层（中观策略层）

**模块类别**: 核心模块（P1级）

**架构角色**: 
- 作为中观策略层的基础设施，监控和管理资金流动性
- 作为风险控制的重要环节，预防流动性风险
- 作为桥水模式的关键实现，提供流动性管理能力
- 作为资金优化系统，提高资金使用效率

### 1.3 版本信息与变更记录

| 版本 | 日期 | 作者 | 变更说明 | 状态 |
|------|------|------|----------|------|
| v1.0 | 2026-04-02 | 首席技术评审官 | 初始版本 | Draft |

---

## 2. 详细架构设计

### 2.1 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                    流动性管理系统架构                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              资金数据采集层                                │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │  │
│  │  │ 账户余额 │  │ 交易流水 │  │ 资金划转 │  │ 费用数据 │ │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          ↓                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              流动性分析层                                  │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │  │
│  │  │ 流入流出 │  │ 资金周转 │  │ 流动比率 │  │ 现金流   │ │  │
│  │  │ 分析     │  │ 率分析   │  │ 计算     │  │ 预测     │ │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          ↓                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              风险预警与决策层                              │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │  │
│  │  │ 风险评估 │  │ 预警生成 │  │ 资金调配 │  │ 应急预案 │ │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          ↓                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              报告与优化层                                  │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │  │
│  │  │ 报告生成 │  │ 效率分析 │  │ 优化建议 │  │ 历史对比 │ │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Layer定位详细说明

**Layer归属**: Layer 5 - 策略执行层（中观策略层）

**职责范围**: 
- 资金流动性监控
- 现金流预测
- 流动性风险预警
- 资金优化配置

**上下层接口**:
- **上层依赖**: Layer 6组合优化层（资金需求）、Layer 4风险管理（风险控制）
- **下层依赖**: Layer 0数据源层（账户数据）、Layer 5策略执行层（交易执行）

### 2.3 模块职责与边界定义

**核心职责**: 监控资金流动性，预测资金需求，优化资金配置，实现桥水模式的流动性管理能力

**职责边界**:
- ✅ 本模块负责:
  - 资金流动性监控和分析
  - 现金流预测
  - 流动性风险预警
  - 资金优化配置建议
  
- ❌ 本模块不负责:
  - 组合优化（由PortfolioOptimizer负责）
  - 风险控制决策（由风险管理模块负责）
  - 具体交易执行（由QMTExecutor负责）
  - 账户数据采集（由数据源模块负责）

**接口契约**: 提供统一的流动性管理API接口

### 2.4 依赖关系与集成点

| 依赖模块 | 依赖类型 | 接口方式 | 版本要求 | 备注 |
|----------|----------|----------|----------|------|
| **账户数据** | 强依赖 | 数据库 | v1.0+ | 账户余额、流水 |
| **交易数据** | 强依赖 | 数据库 | v1.0+ | 交易流水 |
| **组合数据** | 中依赖 | 数据库 | v1.0+ | 持仓数据 |
| **通知系统** | 中依赖 | API | v1.0+ | 预警通知 |

---

## 3. 接口定义

### 3.1 核心API接口

#### 3.1.1 流动性监控接口

```python
def monitor_liquidity(
    account_id: str
) -> LiquidityMonitorResult:
    """
    监控流动性
    
    参数:
    - account_id: 账户ID
    
    返回:
    - LiquidityMonitorResult: 流动性监控结果
      - available_fund: 可用资金
      - frozen_fund: 冻结资金
      - total_asset: 总资产
      - cash_ratio: 现金比例
      - turnover_ratio: 周转率
      - liquidity_ratio: 流动比率
      - risk_level: 风险级别
      - timestamp: 时间戳
    
    性能要求:
    - 响应时间: <50ms
    - 并发能力: ≥10个账户同时监控
    """
    pass
```

#### 3.1.2 现金流预测接口

```python
def predict_cash_flow(
    account_id: str,
    forecast_days: int = 30
) -> CashFlowForecast:
    """
    预测现金流
    
    参数:
    - account_id: 账户ID
    - forecast_days: 预测天数
    
    返回:
    - CashFlowForecast: 现金流预测
      - daily_forecasts: 每日预测列表
      - total_inflow: 总流入预测
      - total_outflow: 总流出预测
      - net_flow: 净流量预测
      - confidence: 预测置信度
    
    性能要求:
    - 响应时间: <1秒
    - 预测准确率: ≥70%
    """
    pass
```

#### 3.1.3 流动性预警接口

```python
def generate_liquidity_warning(
    account_id: str
) -> LiquidityWarning:
    """
    生成流动性预警
    
    参数:
    - account_id: 账户ID
    
    返回:
    - LiquidityWarning: 流动性预警
      - warning_level: 预警级别（GREEN/YELLOW/RED）
      - warning_items: 预警项列表
      - recommendations: 建议措施
      - timestamp: 时间戳
    
    性能要求:
    - 响应时间: <500ms
    - 预警准确率: ≥85%
    """
    pass
```

#### 3.1.4 资金优化建议接口

```python
def optimize_fund_allocation(
    account_id: str,
    target_return: float = 0.0
) -> FundAllocationOptimization:
    """
    优化资金配置
    
    参数:
    - account_id: 账户ID
    - target_return: 目标收益率
    
    返回:
    - FundAllocationOptimization: 资金配置优化建议
      - current_allocation: 当前配置
      - optimal_allocation: 最优配置
      - expected_improvement: 预期改善
      - action_items: 行动项
    
    性能要求:
    - 响应时间: <2秒
    """
    pass
```

### 3.2 数据格式定义

#### 3.2.1 流动性监控数据格式

```python
@dataclass
class LiquidityMonitorResult:
    account_id: str                  # 账户ID
    available_fund: float            # 可用资金
    frozen_fund: float               # 冻结资金
    total_asset: float               # 总资产
    cash_ratio: float                # 现金比例
    turnover_ratio: float            # 周转率
    liquidity_ratio: float           # 流动比率
    daily_inflow: float              # 日流入
    daily_outflow: float             # 日流出
    net_flow: float                  # 净流量
    risk_level: str                  # 风险级别（LOW/MEDIUM/HIGH）
    risk_score: float                # 风险得分（0-100）
    timestamp: datetime              # 时间戳
```

#### 3.2.2 现金流预测数据格式

```python
@dataclass
class CashFlowForecast:
    account_id: str                  # 账户ID
    forecast_days: int               # 预测天数
    daily_forecasts: List[DailyForecast]  # 每日预测
    total_inflow: float              # 总流入预测
    total_outflow: float             # 总流出预测
    net_flow: float                  # 净流量预测
    confidence: float                # 预测置信度
    forecast_time: datetime          # 预测时间

@dataclass
class DailyForecast:
    date: date                       # 预测日期
    predicted_inflow: float          # 预测流入
    predicted_outflow: float         # 预测流出
    predicted_net_flow: float        # 预测净流量
```

#### 3.2.3 流动性预警数据格式

```python
@dataclass
class LiquidityWarning:
    account_id: str                  # 账户ID
    warning_level: str               # 预警级别（GREEN/YELLOW/RED）
    warning_items: List[WarningItem]  # 预警项
    recommendations: List[str]       # 建议措施
    timestamp: datetime              # 时间戳

@dataclass
class WarningItem:
    warning_type: str                # 预警类型（CASH_RATIO/AVAILABLE_FUND/OUTFLOW_PRESSURE）
    current_value: float             # 当前值
    threshold: float                 # 阈值
    severity: str                    # 严重程度（LOW/MEDIUM/HIGH）
```

---

## 4. 数据模型与存储

### 4.1 数据存储设计

#### 4.1.1 资金流水记录表

```sql
CREATE TABLE fund_flows (
    flow_id VARCHAR(50) PRIMARY KEY,
    account_id VARCHAR(50) NOT NULL,
    flow_type VARCHAR(20) NOT NULL,  -- INFLOW/OUTFLOW
    amount DECIMAL(15, 2) NOT NULL,
    balance_before DECIMAL(15, 2) NOT NULL,
    balance_after DECIMAL(15, 2) NOT NULL,
    source VARCHAR(50),              -- 资金来源/去向
    description VARCHAR(200),
    flow_time TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_account_id (account_id),
    INDEX idx_flow_time (flow_time)
);
```

#### 4.1.2 流动性监控记录表

```sql
CREATE TABLE liquidity_monitoring (
    monitor_id VARCHAR(50) PRIMARY KEY,
    account_id VARCHAR(50) NOT NULL,
    available_fund DECIMAL(15, 2) NOT NULL,
    frozen_fund DECIMAL(15, 2) NOT NULL,
    total_asset DECIMAL(15, 2) NOT NULL,
    cash_ratio DECIMAL(10, 6),
    turnover_ratio DECIMAL(10, 6),
    liquidity_ratio DECIMAL(10, 6),
    risk_level VARCHAR(20) NOT NULL,
    risk_score DECIMAL(5, 2),
    monitor_time TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_account_id (account_id),
    INDEX idx_monitor_time (monitor_time)
);
```

#### 4.1.3 现金流预测记录表

```sql
CREATE TABLE cash_flow_forecasts (
    forecast_id VARCHAR(50) PRIMARY KEY,
    account_id VARCHAR(50) NOT NULL,
    forecast_date DATE NOT NULL,
    predicted_inflow DECIMAL(15, 2),
    predicted_outflow DECIMAL(15, 2),
    predicted_net_flow DECIMAL(15, 2),
    actual_inflow DECIMAL(15, 2),
    actual_outflow DECIMAL(15, 2),
    actual_net_flow DECIMAL(15, 2),
    prediction_error DECIMAL(10, 6),
    forecast_time TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_account_id (account_id),
    INDEX idx_forecast_date (forecast_date)
);
```

#### 4.1.4 流动性预警记录表

```sql
CREATE TABLE liquidity_warnings (
    warning_id VARCHAR(50) PRIMARY KEY,
    account_id VARCHAR(50) NOT NULL,
    warning_level VARCHAR(20) NOT NULL,
    warning_items JSON NOT NULL,
    recommendations JSON,
    is_handled BOOLEAN DEFAULT FALSE,
    handled_time TIMESTAMP,
    warning_time TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_account_id (account_id),
    INDEX idx_warning_time (warning_time)
);
```

### 4.2 数据流设计

```
账户数据 → 流水记录 → 流动性分析 → 风险评估 → 预警生成
    ↓           ↓           ↓           ↓           ↓
 余额快照   流水存储   指标计算   风险得分   预警记录
    ↓
现金流预测 → 资金优化 → 行动建议 → 效果评估
    ↓           ↓           ↓           ↓
 预测存储   优化方案   行动记录   效果报告
```

---

## 5. 算法实现说明

### 5.1 资金周转率计算算法

#### 5.1.1 算法原理

**资金周转率**衡量资金使用效率，反映资金的活跃程度。

**数学模型**:
```
Turnover Ratio = Total Trading Volume / Average Capital
```

其中：
- Total Trading Volume: 总交易金额
- Average Capital: 平均资金占用

#### 5.1.2 实现方法

```python
class TurnoverRatioCalculator:
    """资金周转率计算器"""
    
    def calculate_turnover_ratio(
        self,
        fund_data: FundDataset,
        period: int = 30
    ) -> float:
        """
        计算资金周转率
        
        步骤:
        1. 计算周期内总交易金额
        2. 计算周期内平均资金占用
        3. 计算周转率
        
        复杂度:
        - 时间复杂度: O(N)，N为计算周期天数
        - 空间复杂度: O(1)
        
        返回:
        - turnover_ratio: 资金周转率
        """
        total_trading_volume = 0.0
        for i in range(period):
            daily_volume = fund_data.get_daily_trading_volume(i)
            total_trading_volume += daily_volume
        
        capital_sum = 0.0
        for i in range(period):
            daily_capital = fund_data.get_daily_capital(i)
            capital_sum += daily_capital
        
        average_capital = capital_sum / period
        turnover_ratio = total_trading_volume / average_capital
        
        return turnover_ratio
```

### 5.2 现金流预测算法

#### 5.2.1 算法原理

**现金流预测**基于历史数据预测未来的资金流入流出。

**预测方法**:
1. **历史平均法**: 简单但不够准确
2. **时间序列模型**: ARIMA/Prophet，适合周期性数据
3. **机器学习模型**: LSTM，适合复杂模式

#### 5.2.2 历史平均法实现

```python
class CashFlowPredictor:
    """现金流预测器"""
    
    def predict_cash_flow_simple(
        self,
        historical_data: pd.DataFrame,
        forecast_days: int = 30
    ) -> CashFlowForecast:
        """
        简单现金流预测（历史平均法）
        
        步骤:
        1. 计算历史平均日流入
        2. 计算历史平均日流出
        3. 预测未来每日现金流
        
        复杂度:
        - 时间复杂度: O(N)，N为历史数据量
        - 空间复杂度: O(N)
        
        返回:
        - CashFlowForecast: 现金流预测
        """
        avg_daily_inflow = historical_data['inflow'].mean()
        avg_daily_outflow = historical_data['outflow'].mean()
        
        daily_forecasts = []
        for i in range(forecast_days):
            daily_forecast = DailyForecast(
                date=datetime.now().date() + timedelta(days=i),
                predicted_inflow=avg_daily_inflow,
                predicted_outflow=avg_daily_outflow,
                predicted_net_flow=avg_daily_inflow - avg_daily_outflow
            )
            daily_forecasts.append(daily_forecast)
        
        return CashFlowForecast(
            forecast_days=forecast_days,
            daily_forecasts=daily_forecasts,
            total_inflow=avg_daily_inflow * forecast_days,
            total_outflow=avg_daily_outflow * forecast_days,
            net_flow=(avg_daily_inflow - avg_daily_outflow) * forecast_days,
            confidence=0.6  # 历史平均法置信度较低
        )
```

### 5.3 流动性风险评估算法

#### 5.3.1 算法原理

**流动性风险评估**综合多个指标评估流动性风险。

**评估维度**:
1. **现金比例**: 可用资金/总资产
2. **可用资金**: 绝对金额是否充足
3. **流出压力**: 预期流出是否过大
4. **周转率**: 资金活跃度

#### 5.3.2 风险评分计算

```python
class LiquidityRiskAssessor:
    """流动性风险评估器"""
    
    def calculate_liquidity_risk_score(
        self,
        liquidity_report: LiquidityReport
    ) -> float:
        """
        计算流动性风险得分
        
        评分维度:
        1. 现金比例（权重30%）: <10%高风险，10-20%中风险，>20%低风险
        2. 可用资金（权重30%）: <10万高风险，10-50万中风险，>50万低风险
        3. 流出压力（权重20%）: 流出/流入>1高风险
        4. 周转率（权重20%）: 过高或过低都有风险
        
        复杂度:
        - 时间复杂度: O(1)
        - 空间复杂度: O(1)
        
        返回:
        - risk_score: 风险得分（0-100）
        """
        score = 0.0
        
        # 现金比例评分
        if liquidity_report.cash_ratio < 0.1:
            score += 30
        elif liquidity_report.cash_ratio < 0.2:
            score += 15
        else:
            score += 0
        
        # 可用资金评分
        if liquidity_report.available_fund < 100000:
            score += 30
        elif liquidity_report.available_fund < 500000:
            score += 15
        else:
            score += 0
        
        # 流出压力评分
        if liquidity_report.daily_outflow > liquidity_report.daily_inflow:
            score += 20
        
        # 周转率评分
        if liquidity_report.turnover_ratio < 0.5 or liquidity_report.turnover_ratio > 5.0:
            score += 20
        
        return score
```

---

## 6. 实施技术栈

### 6.1 语言与框架

| 类别 | 技术选型 | 版本要求 | 用途 |
|------|----------|----------|------|
| **编程语言** | Python | 3.9+ | 核心开发语言 |
| **异步框架** | asyncio | 内置 | 异步监控支持 |
| **数值计算** | numpy | 1.24+ | 数值计算 |
| **数据处理** | pandas | 2.0+ | 数据处理和分析 |

### 6.2 第三方依赖

| 依赖库 | 版本 | 用途 |
|--------|------|------|
| prophet | 1.1+ | 时间序列预测（可选） |
| scipy | 1.11+ | 统计计算 |

### 6.3 环境要求

| 环境 | 要求 |
|------|------|
| **操作系统** | Windows 10+ / Linux |
| **Python版本** | 3.9+ |
| **内存** | ≥8GB |
| **存储** | ≥5GB |

---

## 7. 测试策略

### 7.1 单元测试

```python
class TestTurnoverRatioCalculator:
    """周转率计算单元测试"""
    
    def test_turnover_ratio_calculation(self):
        """测试周转率计算"""
        pass
    
    def test_edge_cases(self):
        """测试边界情况"""
        pass

class TestCashFlowPredictor:
    """现金流预测单元测试"""
    
    def test_simple_prediction(self):
        """测试简单预测"""
        pass
    
    def test_prediction_accuracy(self):
        """测试预测准确度"""
        pass
```

### 7.2 集成测试

```python
class TestLiquidityManagementSystem:
    """流动性管理系统集成测试"""
    
    def test_end_to_end_monitoring(self):
        """测试端到端监控"""
        pass
    
    def test_warning_generation(self):
        """测试预警生成"""
        pass
    
    def test_optimization_suggestion(self):
        """测试优化建议"""
        pass
```

### 7.3 性能测试

| 测试场景 | 性能指标 | 目标值 |
|----------|----------|--------|
| **流动性计算速度** | 单次计算 | <50ms |
| **预测生成速度** | 30天预测 | <1秒 |
| **并发监控能力** | 同时监控账户数 | ≥10个 |

---

## 8. 风险与约束

### 8.1 技术风险

| 风险ID | 风险描述 | 影响程度 | 缓解措施 |
|--------|----------|----------|----------|
| TR-001 | 现金流预测不准确 | 中 | 使用多种预测方法，持续优化 |
| TR-002 | 数据延迟 | 低 | 使用实时数据源 |
| TR-003 | 预警误报 | 中 | 优化阈值，减少误报 |

### 8.2 实施约束

| 约束类型 | 约束描述 | 影响 |
|----------|----------|------|
| **数据约束** | 需要账户和交易数据 | 需要数据源支持 |
| **时间约束** | 开发时间80小时 | 需要合理规划 |
| **资源约束** | 个人开发，资源有限 | 采用简化方案 |

---

## 9. 验收标准

### 9.1 功能验收标准

| 功能 | 验收标准 | 测试方法 |
|------|----------|----------|
| **流动性监控** | 能够实时监控流动性 | 集成测试 |
| **现金流预测** | 预测误差≤30% | 回测验证 |
| **风险预警** | 风险超限时自动预警 | 集成测试 |
| **优化建议** | 能够生成优化建议 | 集成测试 |

### 9.2 性能验收标准

| 指标 | 目标值 | 验收方法 |
|------|--------|----------|
| **计算速度** | <50ms | 性能测试 |
| **预测准确度** | 误差≤30% | 回测验证 |
| **资金效率提升** | 提升20-30% | 效果评估 |

### 9.3 质量验收标准

| 标准 | 要求 | 验收方法 |
|------|------|----------|
| **代码覆盖率** | ≥80% | pytest-cov |
| **文档完整性** | 100% | 文档审查 |
| **代码规范** | 符合PEP8 | pylint |

---

## 10. 实施路线图

### 10.1 Phase 1: 流动性监控系统实现（1周）

**目标**: 实现流动性监控

**任务清单**:
1. ✅ 设计流动性指标体系
2. ✅ 实现资金数据采集
3. ✅ 实现流动性分析
4. ✅ 实现风险预警
5. ✅ 编写单元测试

**交付物**:
- 流动性监控实现代码
- 单元测试代码
- 技术文档

### 10.2 Phase 2: 预测和优化系统实现（1周）

**目标**: 实现现金流预测和资金优化

**任务清单**:
1. ✅ 实现现金流预测
2. ✅ 实现资金优化建议
3. ✅ 实现报告生成
4. ✅ 编写单元测试
5. ✅ 性能优化

**交付物**:
- 预测和优化实现代码
- 单元测试代码

### 10.3 Phase 3: 高级功能实现（可选）

**目标**: 实现高级预测模型和智能优化

**任务清单**:
1. 📝 实现机器学习预测模型
2. 📝 实现智能资金调配
3. 📝 实现多账户管理
4. 📝 性能评估和优化

**交付物**:
- 高级功能实现代码
- 性能评估报告

---

## 11. 相关文档

### 11.1 蓝图文档

- [LIQUIDITY_MANAGEMENT_SYSTEM_BLUEPRINT.md](../06_CONSTRUCTION_DOCS/01_BLUEPRINTS/LIQUIDITY_MANAGEMENT_SYSTEM_BLUEPRINT.md)

### 11.2 架构文档

- [PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md](../../01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md)

### 11.3 相关模块

- [REALTIME_RISK_HEDGE_ENGINE_TECHNICAL_SPECIFICATION.md](./REALTIME_RISK_HEDGE_ENGINE_TECHNICAL_SPECIFICATION.md) - 实时风险对冲引擎
- [ECONOMIC_REGIME_ENGINE_TECHNICAL_SPECIFICATION.md](./ECONOMIC_REGIME_ENGINE_TECHNICAL_SPECIFICATION.md) - 经济范式判断引擎

---

**技术规格书编写人**: 首席技术评审官
**技术规格书日期**: 2026-04-02
**技术规格书状态**: ✅ 已完成

---

**文档结束**
