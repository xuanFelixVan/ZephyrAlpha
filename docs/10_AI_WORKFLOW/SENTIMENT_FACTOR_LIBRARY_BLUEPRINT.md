﻿---
module_id: AIWF_SFL_001
version: 1.0.0
status: Active
created_date: 2026-04-05
last_updated: 2026-04-05
owner: 首席架构师
standard_type: 专业机构级蓝图
applicable_scope: 舆情因子库模块
compliance_level: 专业标准
parent_document: INDEX.md
layer: Layer 3 (舆情分析层)
priority: P0
estimated_effort: 50h
responsibility:
  - 蓝图设计、架构规划

---
---


## 文档职责说明

**本文档职责**: 舆情因子库模块蓝图
- 因子定义、因子计算、因子评估、因子优化

# 舆情因子库模块蓝图 (Sentiment Factor Library Blueprint)

> **核心职责**: 蓝图设计和架构规划
> **职责边界**: 
> - ✅ 本文档负责：蓝图设计和架构规划相关内容
> - ❌ 本文档不负责：其他模块内容


> **模块ID**: AIWF_SFL_001
> **版本**: v1.0
> **创建日期**: 2026-04-05
> **Layer定位**: 舆情分析层
> **优先级**: P0 (阻断性)
> **预计工作量**: 50小时

---

## 一、模块概述

### 1.1 设计背景

**业务需求**:
- 构建系统化的舆情因子体系，为量化策略提供信号输入
- 实现舆情因子的自动化计算、存储和评估
- 支持因子组合优化和权重调整
- 提供因子回测和验证能力

**技术痛点**:
- 当前缺少系统化的舆情因子定义和计算框架
- 缺少因子评估体系（IC/IR、单调性、稳定性）
- 缺少因子组合和权重优化机制
- 缺少因子回测验证能力

**预期价值**:
- 构建完整的舆情因子库（20+因子）
- 因子IC均值 > 0.05
- 因子IR > 1.5
- 策略收益提升10-15%

### 1.2 模块定位

**Layer归属**: 舆情分析层
**模块类别**: 核心分析模块
**架构角色**: 因子计算引擎，为策略执行层提供因子信号

---

## 二、详细架构设计

### 2.1 系统架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                      舆情因子库模块架构                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │         FactorDefinitionEngine (因子定义引擎)                 │   │
│  │  - 因子类型定义                                               │   │
│  │  - 因子计算逻辑                                               │   │
│  │  - 因子参数配置                                               │   │
│  │  - 因子依赖管理                                               │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                          ↓                                           │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │         FactorCalculationEngine (因子计算引擎)                │   │
│  │  - 实时因子计算                                               │   │
│  │  - 批量因子计算                                               │   │
│  │  - 增量因子更新                                               │   │
│  │  - 因子计算优化                                               │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                          ↓                                           │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │         FactorStorageEngine (因子存储引擎)                    │   │
│  │  - 因子时序存储                                               │   │
│  │  - 因子元数据管理                                             │   │
│  │  - 因子版本控制                                               │   │
│  │  - 因子数据压缩                                               │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                          ↓                                           │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │         FactorEvaluationEngine (因子评估引擎)                 │   │
│  │  - IC/IR计算                                                  │   │
│  │  - 单调性检验                                                 │   │
│  │  - 稳定性检验                                                 │   │
│  │  - 因子有效性评估                                             │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                          ↓                                           │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │         FactorOptimizationEngine (因子优化引擎)               │   │
│  │  - 因子组合优化                                               │   │
│  │  - 因子权重优化                                               │   │
│  │  - 因子正交化                                                 │   │
│  │  - 因子筛选                                                   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                          ↓                                           │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │         FactorBacktestEngine (因子回测引擎)                   │   │
│  │  - 因子历史回测                                               │   │
│  │  - 因子绩效分析                                               │   │
│  │  - 因子风险分析                                               │   │
│  │  - 因子归因分析                                               │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 核心组件设计

#### 2.2.1 因子定义引擎 (FactorDefinitionEngine)

**功能**:
- 定义舆情因子类型和计算逻辑
- 管理因子参数配置
- 管理因子依赖关系

**舆情因子定义体系**:

| 因子类别 | 因子名称 | 因子ID | 计算逻辑 | 更新频率 |
|---------|---------|--------|---------|---------|
| **动量因子** | 舆情动量因子 | SENT_MOM_001 | 过去N天情感得分变化率 | 日频 |
| **动量因子** | 舆情加速度因子 | SENT_ACC_001 | 舆情动量的变化率 | 日频 |
| **反转因子** | 舆情反转因子 | SENT_REV_001 | 情感得分极端值后的反转 | 日频 |
| **反转因子** | 舆情过度反应因子 | SENT_OVR_001 | 情感得分偏离均值程度 | 日频 |
| **离散度因子** | 舆情离散度因子 | SENT_DISP_001 | 情感得分标准差 | 日频 |
| **离散度因子** | 舆情极化因子 | SENT_POL_001 | 极端情感占比 | 日频 |
| **关注度因子** | 舆情关注度因子 | SENT_ATTN_001 | 舆情数量/总舆情数量 | 日频 |
| **关注度因子** | 舆情热度因子 | SENT_HEAT_001 | 舆情数量时间加权 | 日频 |
| **一致性因子** | 舆情一致性因子 | SENT_CONS_001 | 多源情感得分一致性 | 日频 |
| **一致性因子** | 舆情共识因子 | SENT_AGREE_001 | 情感得分众数占比 | 日频 |

**因子计算逻辑示例**:

```python
class SentimentMomentumFactor:
    """舆情动量因子"""
    
    factor_id = "SENT_MOM_001"
    factor_name = "舆情动量因子"
    factor_category = "动量因子"
    update_frequency = "daily"
    
    def __init__(self, lookback_period: int = 5):
        self.lookback_period = lookback_period
    
    def calculate(self, sentiment_scores: pd.Series) -> float:
        """
        计算舆情动量因子
        
        Args:
            sentiment_scores: 过去N天的情感得分序列
        
        Returns:
            舆情动量因子值
        """
        if len(sentiment_scores) < self.lookback_period:
            return np.nan
        
        # 计算情感得分变化率
        current_score = sentiment_scores.iloc[-1]
        past_score = sentiment_scores.iloc[-self.lookback_period]
        
        momentum = (current_score - past_score) / (abs(past_score) + 1e-6)
        
        return momentum
```

#### 2.2.2 因子计算引擎 (FactorCalculationEngine)

**功能**:
- 实时计算因子值
- 批量计算历史因子
- 增量更新因子值
- 优化因子计算性能

**实现要点**:

```python
class FactorCalculationEngine:
    def __init__(self):
        self.factor_definitions = {}
        self.calculation_cache = {}
        self.parallel_executor = ParallelExecutor()
    
    def register_factor(self, factor: Factor):
        """注册因子"""
        self.factor_definitions[factor.factor_id] = factor
    
    async def calculate_factors(
        self, 
        factor_ids: List[str], 
        data: pd.DataFrame,
        mode: str = "batch"
    ) -> pd.DataFrame:
        """
        计算因子
        
        Args:
            factor_ids: 因子ID列表
            data: 输入数据
            mode: 计算模式 (batch/realtime/incremental)
        
        Returns:
            因子值DataFrame
        """
        results = {}
        
        for factor_id in factor_ids:
            factor = self.factor_definitions[factor_id]
            
            if mode == "batch":
                # 批量计算
                result = await self._calculate_batch(factor, data)
            elif mode == "realtime":
                # 实时计算
                result = await self._calculate_realtime(factor, data)
            elif mode == "incremental":
                # 增量更新
                result = await self._calculate_incremental(factor, data)
            
            results[factor_id] = result
        
        return pd.DataFrame(results)
    
    async def _calculate_batch(self, factor: Factor, data: pd.DataFrame):
        """批量计算"""
        # 使用并行计算优化性能
        return await self.parallel_executor.execute(
            factor.calculate, 
            data
        )
```

#### 2.2.3 因子存储引擎 (FactorStorageEngine)

**功能**:
- 存储因子时序数据
- 管理因子元数据
- 控制因子版本
- 压缩因子数据

**数据库设计**:

```sql
-- 因子定义表
CREATE TABLE factor_definitions (
    factor_id VARCHAR(50) PRIMARY KEY,
    factor_name VARCHAR(100),
    factor_category VARCHAR(50),
    factor_description TEXT,
    calculation_logic TEXT,
    update_frequency VARCHAR(20),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- 因子值表 (时序数据)
CREATE TABLE factor_values (
    id BIGSERIAL PRIMARY KEY,
    factor_id VARCHAR(50) REFERENCES factor_definitions(factor_id),
    asset_symbol VARCHAR(20),
    factor_value DECIMAL(20, 10),
    timestamp TIMESTAMP,
    created_at TIMESTAMP,
    UNIQUE(factor_id, asset_symbol, timestamp)
);

-- 创建时序索引
CREATE INDEX idx_factor_values_timestamp ON factor_values(timestamp);
CREATE INDEX idx_factor_values_factor_asset ON factor_values(factor_id, asset_symbol);

-- 因子元数据表
CREATE TABLE factor_metadata (
    factor_id VARCHAR(50) REFERENCES factor_definitions(factor_id),
    version VARCHAR(20),
    parameters JSONB,
    dependencies JSONB,
    created_at TIMESTAMP,
    PRIMARY KEY(factor_id, version)
);
```

**实现要点**:

```python
class FactorStorageEngine:
    def __init__(self, db_connection):
        self.db = db_connection
        self.cache = RedisCache()
    
    async def store_factors(
        self, 
        factor_values: pd.DataFrame, 
        timestamp: datetime
    ):
        """存储因子值"""
        # 批量插入
        records = []
        for factor_id in factor_values.columns:
            for asset_symbol, value in factor_values[factor_id].items():
                records.append({
                    'factor_id': factor_id,
                    'asset_symbol': asset_symbol,
                    'factor_value': value,
                    'timestamp': timestamp
                })
        
        await self.db.batch_insert('factor_values', records)
        
        # 更新缓存
        await self.cache.set(
            f"factors:{timestamp.strftime('%Y%m%d')}", 
            factor_values.to_json()
        )
    
    async def get_factors(
        self, 
        factor_ids: List[str], 
        start_date: datetime, 
        end_date: datetime
    ) -> pd.DataFrame:
        """获取因子值"""
        # 先查缓存
        cache_key = f"factors:{start_date.strftime('%Y%m%d')}:{end_date.strftime('%Y%m%d')}"
        cached_data = await self.cache.get(cache_key)
        
        if cached_data:
            return pd.read_json(cached_data)
        
        # 查数据库
        query = """
        SELECT factor_id, asset_symbol, factor_value, timestamp
        FROM factor_values
        WHERE factor_id IN %s
        AND timestamp BETWEEN %s AND %s
        ORDER BY timestamp
        """
        
        results = await self.db.execute(query, (factor_ids, start_date, end_date))
        
        # 转换为DataFrame
        df = pd.DataFrame(results)
        df = df.pivot(index='timestamp', columns=['factor_id', 'asset_symbol'], values='factor_value')
        
        return df
```

#### 2.2.4 因子评估引擎 (FactorEvaluationEngine)

**功能**:
- 计算因子IC/IR
- 检验因子单调性
- 检验因子稳定性
- 评估因子有效性

**评估指标**:

| 指标 | 计算方法 | 目标值 | 意义 |
|------|---------|--------|------|
| **IC** | Rank Correlation(因子值, 未来收益) | > 0.05 | 因子预测能力 |
| **IR** | IC均值 / IC标准差 | > 1.5 | 因子稳定性 |
| **单调性** | 分组收益率单调递增/递减 | 显著 | 因子有效性 |
| **稳定性** | IC时间序列标准差 | < 0.1 | 因子可靠性 |

**实现要点**:

```python
class FactorEvaluationEngine:
    def __init__(self):
        self.ic_calculator = ICCalculator()
        self.monotonicity_tester = MonotonicityTester()
        self.stability_tester = StabilityTester()
    
    async def evaluate_factor(
        self, 
        factor_values: pd.Series, 
        returns: pd.Series,
        evaluation_period: int = 252
    ) -> FactorEvaluation:
        """评估因子"""
        # 计算IC
        ic_series = await self.ic_calculator.calculate(
            factor_values, 
            returns, 
            evaluation_period
        )
        
        # 计算IR
        ic_mean = ic_series.mean()
        ic_std = ic_series.std()
        ir = ic_mean / (ic_std + 1e-6)
        
        # 单调性检验
        monotonicity = await self.monotonicity_tester.test(
            factor_values, 
            returns
        )
        
        # 稳定性检验
        stability = await self.stability_tester.test(ic_series)
        
        return FactorEvaluation(
            ic_mean=ic_mean,
            ic_std=ic_std,
            ir=ir,
            monotonicity=monotonicity,
            stability=stability,
            is_effective=ic_mean > 0.05 and ir > 1.5
        )
```

#### 2.2.5 因子优化引擎 (FactorOptimizationEngine)

**功能**:
- 优化因子组合
- 优化因子权重
- 因子正交化
- 因子筛选

**实现要点**:

```python
class FactorOptimizationEngine:
    def __init__(self):
        self.orthogonalizer = FactorOrthogonalizer()
        self.weight_optimizer = WeightOptimizer()
        self.factor_selector = FactorSelector()
    
    async def optimize_factors(
        self, 
        factor_values: pd.DataFrame, 
        returns: pd.Series,
        method: str = "max_sharpe"
    ) -> OptimizedFactors:
        """优化因子组合"""
        # 因子正交化
        orthogonal_factors = await self.orthogonalizer.orthogonalize(
            factor_values
        )
        
        # 因子筛选
        selected_factors = await self.factor_selector.select(
            orthogonal_factors, 
            returns
        )
        
        # 权重优化
        weights = await self.weight_optimizer.optimize(
            selected_factors, 
            returns, 
            method
        )
        
        return OptimizedFactors(
            factors=selected_factors,
            weights=weights,
            combined_factor=(selected_factors * weights).sum(axis=1)
        )
```

#### 2.2.6 因子回测引擎 (FactorBacktestEngine)

**功能**:
- 回测因子历史表现
- 分析因子绩效
- 分析因子风险
- 归因分析

**实现要点**:

```python
class FactorBacktestEngine:
    def __init__(self):
        self.backtest_runner = BacktestRunner()
        self.performance_analyzer = PerformanceAnalyzer()
        self.risk_analyzer = RiskAnalyzer()
        self.attribution_analyzer = AttributionAnalyzer()
    
    async def backtest_factor(
        self, 
        factor_values: pd.Series, 
        price_data: pd.DataFrame,
        backtest_period: Tuple[datetime, datetime]
    ) -> BacktestResult:
        """回测因子"""
        # 运行回测
        backtest_result = await self.backtest_runner.run(
            factor_values, 
            price_data, 
            backtest_period
        )
        
        # 绩效分析
        performance = await self.performance_analyzer.analyze(
            backtest_result
        )
        
        # 风险分析
        risk = await self.risk_analyzer.analyze(
            backtest_result
        )
        
        # 归因分析
        attribution = await self.attribution_analyzer.analyze(
            backtest_result
        )
        
        return BacktestResult(
            backtest_result=backtest_result,
            performance=performance,
            risk=risk,
            attribution=attribution
        )
```

---

## 三、技术选型

### 3.1 开源项目评估

| 项目 | 功能 | Stars | 成熟度 | 推荐度 | 成本 |
|------|------|-------|--------|--------|------|
| **Qlib** | 因子库框架 | 15k | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 免费 |
| **Alphalens** | 因子评估 | 3k | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 免费 |
| **Backtrader** | 回测框架 | 12k | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 免费 |
| **Zipline** | 回测引擎 | 17k | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 免费 |
| **TimescaleDB** | 时序数据库 | 17k | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 开源版免费 |

### 3.2 技术栈选择

**因子计算层**:
- Python 3.10+
- NumPy (数值计算)
- Pandas (数据处理)
- Numba (性能优化)

**因子存储层**:
- TimescaleDB (时序数据)
- PostgreSQL (元数据)
- Redis (缓存)

**因子评估层**:
- Alphalens (因子评估)
- SciPy (统计分析)
- scikit-learn (机器学习)

### 3.3 成本分析

| 组件 | 计算成本 | 存储成本 | 总成本 |
|------|---------|---------|--------|
| 因子计算引擎 | $200/月 | $50/月 | $250/月 |
| 因子存储引擎 | $50/月 | $150/月 | $200/月 |
| 因子评估引擎 | $100/月 | $30/月 | $130/月 |
| 因子优化引擎 | $80/月 | $20/月 | $100/月 |
| 因子回测引擎 | $150/月 | $50/月 | $200/月 |
| **总计** | **$580/月** | **$300/月** | **$880/月** |

---

## 四、实施路径

### Phase 1: 核心因子构建（2周）

**目标**: 完成核心因子定义和计算

**任务清单**:
- [ ] 因子定义引擎开发
- [ ] 因子计算引擎开发
- [ ] 因子存储引擎开发
- [ ] 核心因子实现（动量、反转、离散度）

**验收标准**:
- 核心因子数量 > 5个
- 因子计算成功率 > 95%
- 因子存储可用

### Phase 2: 因子评估与优化（2周）

**目标**: 完成因子评估和优化

**任务清单**:
- [ ] 因子评估引擎开发
- [ ] 因子优化引擎开发
- [ ] 因子有效性验证
- [ ] 因子组合优化

**验收标准**:
- 因子IC均值 > 0.05
- 因子IR > 1.5
- 因子组合优化可用

### Phase 3: 因子回测与生产化（1周）

**目标**: 完成因子回测和生产部署

**任务清单**:
- [ ] 因子回测引擎开发
- [ ] 因子历史回测
- [ ] 性能优化
- [ ] 生产环境部署

**验收标准**:
- 因子回测可用
- 系统可用性 > 99.9%
- 文档完整

---

## 五、风险与挑战

### 5.1 技术风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| 因子IC低 | 高 | 中 | 多因子组合和优化 |
| 因子过拟合 | 高 | 中 | 样本外验证和正则化 |
| 因子失效 | 中 | 中 | 持续监控和动态调整 |
| 计算性能瓶颈 | 中 | 低 | 并行计算和缓存优化 |

### 5.2 业务风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| 市场环境变化 | 高 | 中 | 因子动态调整 |
| 数据质量问题 | 中 | 中 | 数据验证和清洗 |
| 因子拥挤 | 中 | 低 | 因子独特性分析 |

### 5.3 挑战

1. **因子有效性**
   - 挑战: 因子IC不稳定
   - 解决方案: 多因子组合和动态调整

2. **因子过拟合**
   - 挑战: 历史表现好但实盘差
   - 解决方案: 样本外验证和正则化

3. **因子计算性能**
   - 挑战: 大规模因子计算耗时
   - 解决方案: 并行计算和增量更新

---

## 六、验收标准

### 6.1 功能验收标准

| 功能 | 验收标准 | 测试方法 |
|------|---------|---------|
| 因子定义 | 因子数量 > 20个 | 人工审查 |
| 因子计算 | 成功率 > 95% | 自动化测试 |
| 因子评估 | IC均值 > 0.05 | 历史数据测试 |
| 因子优化 | IR > 1.5 | 回测验证 |
| 因子回测 | 回测可用 | 功能测试 |

### 6.2 性能验收标准

| 指标 | 目标值 | 测试方法 |
|------|--------|---------|
| 因子计算延迟 | < 30秒 | 性能测试 |
| 因子查询延迟 | < 1秒 | 性能测试 |
| 因子回测速度 | < 5分钟/年 | 性能测试 |
| 系统可用性 | > 99.9% | 监控统计 |

### 6.3 质量验收标准

| 指标 | 目标值 | 测试方法 |
|------|--------|---------|
| 代码覆盖率 | > 80% | 单元测试 |
| 文档完整性 | 100% | 人工审查 |
| 安全漏洞 | 0个高危 | 安全扫描 |

---

## 七、依赖关系

### 7.1 上游依赖

| 依赖模块 | 依赖类型 | 说明 |
|---------|---------|------|
| 数据源扩展模块 | 数据依赖 | 提供舆情数据 |
| 深度学习情感分析模块 | 分析依赖 | 提供情感得分 |
| 事件驱动分析模块 | 事件依赖 | 提供事件因子 |

### 7.2 下游依赖

| 依赖模块 | 依赖类型 | 说明 |
|---------|---------|------|
| 策略执行层 | 因子依赖 | 提供因子信号 |
| 实时预警系统模块 | 预警依赖 | 提供因子预警 |

---

## 八、参考资源

### 8.1 开源项目

- **Qlib**: https://github.com/microsoft/qlib
- **Alphalens**: https://github.com/quantopian/alphalens
- **Backtrader**: https://github.com/mementum/backtrader
- **Zipline**: https://github.com/quantopian/zipline
- **TimescaleDB**: https://github.com/timescale/timescaledb

### 8.2 学术论文

- **因子投资**: "Factor Investing" by Andrew Ang
- **因子评估**: "Evaluation of Factor Models"
- **因子组合**: "Factor Combination Methods"

### 8.3 最佳实践

- **因子构建**: docs/09_BEST_PRACTICES/FACTOR_CONSTRUCTION.md
- **因子评估**: docs/09_BEST_PRACTICES/FACTOR_EVALUATION.md
- **因子优化**: docs/09_BEST_PRACTICES/FACTOR_OPTIMIZATION.md

---

**版本**: v1.0 | **更新**: 2026-04-05 | **状态**: 活跃
---

## 1. 文档治理

### 1.1 System_Manifest.md索引

```markdown
#### Layer 0: 系统架构
##### 0.001. Aiwf Sfl
- **模块ID**: AIWF_SFL_001
- **蓝图文档**: [SENTIMENT_FACTOR_LIBRARY_BLUEPRINT.md](./SENTIMENT_FACTOR_LIBRARY_BLUEPRINT.md)
- **技术规格书**: 待创建
- **职责**: 舆情因子库模块
- **状态**: Active
```

### 1.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **Aiwf Sfl** | 舆情因子库模块 | **核心模块** |

### 1.3 版本管理

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-05 | 初始版本创建 | 首席蓝图架构师 |

---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-05 | **状态**: Active
