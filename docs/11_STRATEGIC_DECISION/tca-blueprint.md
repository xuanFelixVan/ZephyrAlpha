---
module_id: LAYER_TCA_001_3560
version: 1.0.0
status: Active
priority: P0
created_date: 2026-04-07
last_updated: '2026-04-07'
owner: 文档管理员
layer: layer_05
standard_type: 专业量化机构蓝图
applicable_scope: 全系统
compliance_level: 专业标准
responsibility:
- 系统架构蓝图设计与实施指导与实施方案
---

```
module_id: TCA_001_3560
```

version: 1.0.0

status: Active

created_date: 2026-04-06

last_updated: 2026-04-06

owner: 首席架构师

standard_type: 专业量化机构级蓝图

applicable_scope: Layer 11.9 - 交易成本分析系统

compliance_level: 顶级专业标准

reference_models: ["ITG TCA", "Bloomberg EMSX TCA", "Goldman Sachs TCA", "Morgan Stanley TCA"]

related_documents:

  - BLUEPRINT.md

  - ARCHITECTURE.md

  - LIQUIDITY_MANAGEMENT_BLUEPRINT.md

parent_document: BLUEPRINT.md

implementation_status: 设计阶段

open_source_solution: tcapy

```
```---
```



# Layer 11.9: 交易成本分析系统蓝图 (TCA)

> **核心职责**: 交易成本分析系统蓝图设计

> **职责边界**: 

> - ✅ 本文档负责：交易成本分析系统蓝图设计相关内容

> - ❌ 本文档不负责：其他模块内容



> **核心职责**: Tca蓝图设计

> **职责边界**: 

> - ✅ 本文档负责：Tca蓝图设计相关内容

> - ❌ 本文档不负责：其他模块内容





## 📋 文档职责说明



### 核心职责



本文档是**交易成本分析系统蓝图，负责交易成本测量和优化**。



### 职责边界



**负责**：

- ✅ 交易成本测量（显性/隐性成本）

- ✅ 成本归因分析（成本来源分析）

- ✅ 成本优化建议（成本优化方案）

- ✅ TCA报告生成（成本分析报告）



**不负责**：

- ❌ 资产配置决策（由战略资产配置模块负责）

- ❌ 风险预算分配（由风险预算分配模块负责）

- ❌ 具体交易执行（由Layer 6组合优化层负责）



### 对接模块



**上游模块**：

- Layer 6 组合优化层

- Layer 7 风险管理层



**下游模块**：

- Layer 8 报告层

- Layer 10 质量保证层



```
```---
```



> **版本**: v1.0  

> **创建日期**: 2026-04-06  

> **实施周期**: 2周（集成tcapy）  

> **目标**: 构建专业级交易成本分析体系，实现交易执行质量评估和成本优化



```
```---
```



## 📋 执行摘要



### 核心定位



Layer 11.9交易成本分析系统(TCA)是清风量化系统的**交易成本守护者**，负责：

- 滑点分析（实际成交价与理论价格的偏差）

- 市场冲击分析（交易对市场价格的影响）

- 执行基准比较（VWAP/TWAP/Arrival Price）

- 执行质量评估（经纪商排名、算法评估）



### 专业机构对标



| 机构 | TCA方案 | 年度投入 | 您的实现 |

|------|---------|---------|---------|

| **买方机构** | ITG/Bloomberg TCA | $225k/年 | ✅ tcapy开源方案 |

| **高盛** | 自研TCA系统 | $500k+/年 | ✅ 开源+自研结合 |

| **摩根士丹利** | 自研TCA系统 | $500k+/年 | ✅ 开源+自研结合 |

| **对冲基金** | 混合方案 | $100k+/年 | ✅ 完全开源 |



### 业务价值



| 价值维度 | 专业机构实践 | 个人实现方式 | 价值评级 |

|---------|-------------|------------|---------|

| **成本节省** | 识别高成本经纪商 | 自动化TCA分析 | ⭐⭐⭐⭐⭐ |

| **执行优化** | 算法执行评估 | AI辅助优化建议 | ⭐⭐⭐⭐⭐ |

| **合规要求** | MiFID II最佳执行 | 自动生成报告 | ⭐⭐⭐⭐ |

| **绩效提升** | 降低交易成本1-2% | 年化收益提升 | ⭐⭐⭐⭐⭐ |



**综合价值评级**: ⭐⭐⭐⭐⭐ (5/5) - **强烈推荐实施**



### 开源方案优势



**tcapy** 是业内首个开源TCA库，具有以下优势：

- ✅ **完全免费**：节省$225k/年

- ✅ **功能完整**：滑点、市场冲击、VWAP/TWAP基准

- ✅ **数据私有**：本地部署，交易数据不外泄

- ✅ **可定制**：完全开源，可添加自定义指标

- ✅ **多资产支持**：FX、股票、期货等



```
```---
```



## 一、架构设计



### 1.1 TCA系统整体架构



```

┌─────────────────────────────────────────────────────────────────┐

│           Layer 11.9: 交易成本分析系统架构                      │

├─────────────────────────────────────────────────────────────────┤

│                                                                 │

│  ┌───────────────────────────────────────────────────────────┐ │

│  │         11.9.1 滑点分析引擎 (核心)                       │ │

│  │  ├── 实际成交价分析 (Actual Execution Price Analysis)    │ │

│  │  ├── 理论价格计算 (Theoretical Price Calculation)        │ │

│  │  ├── 滑点分解 (Slippage Decomposition)                   │ │

│  │  └── 时间衰减分析 (Time Decay Analysis)                  │ │

│  └───────────────────────────────────────────────────────────┘ │

│                                                                 │

│  ┌───────────────────────────────────────────────────────────┐ │

│  │         11.9.2 市场冲击分析引擎                           │ │

│  │  ├── 临时冲击 (Temporary Impact)                         │ │

│  │  ├── 永久冲击 (Permanent Impact)                         │ │

│  │  ├── 冲击衰减曲线 (Impact Decay Curve)                   │ │

│  │  └── 冲击模型拟合 (Impact Model Fitting)                 │ │

│  └───────────────────────────────────────────────────────────┘ │

│                                                                 │

│  ┌───────────────────────────────────────────────────────────┐ │

│  │         11.9.3 执行基准系统                               │ │

│  │  ├── VWAP基准 (Volume Weighted Average Price)           │ │

│  │  ├── TWAP基准 (Time Weighted Average Price)             │ │

│  │  ├── Arrival Price基准 (Arrival Price Benchmark)        │ │

│  │  └── Implementation Shortfall (IS)                       │ │

│  └───────────────────────────────────────────────────────────┘ │

│                                                                 │

│  ┌───────────────────────────────────────────────────────────┐ │

│  │         11.9.4 执行质量评估系统                           │ │

│  │  ├── 经纪商排名 (Broker Ranking)                         │ │

│  │  ├── 算法执行评估 (Algorithm Execution Evaluation)       │ │

│  │  ├── 成本归因分析 (Cost Attribution Analysis)            │ │

│  │  └── 优化建议生成 (Optimization Suggestion Generation)   │ │

│  └───────────────────────────────────────────────────────────┘ │

│                                                                 │

│  ┌───────────────────────────────────────────────────────────┐ │

│  │         11.9.5 TCA报告系统                                │ │

│  │  ├── TCA报告生成 (TCA Report Generation)                 │ │

│  │  ├── 可视化展示 (Visualization)                           │ │

│  │  ├── 合规报告 (Compliance Report)                         │ │

│  │  └── 历史对比分析 (Historical Comparison)                │ │

│  └───────────────────────────────────────────────────────────┘ │

│                                                                 │

└─────────────────────────────────────────────────────────────────┘

```



### 1.2 模块职责边界



| 模块 | 核心职责 | 输入 | 输出 | 对接模块 |

|------|---------|------|------|---------|

| **滑点分析** | 计算滑点、分解成本 | 成交数据、市场数据 | 滑点报告 | Layer 5, 8 |

| **市场冲击** | 分析价格冲击 | 成交数据、Tick数据 | 冲击报告 | Layer 5 |

| **执行基准** | 计算基准价格 | 市场数据、订单数据 | 基准价格 | Layer 5, 7 |

| **质量评估** | 评估执行质量 | TCA结果 | 评估报告、排名 | Layer 8 |

| **TCA报告** | 生成报告 | 所有TCA数据 | 可视化报告 | Layer 8 |



```
```---
```



## 二、核心组件详细设计



### 2.1 滑点分析引擎



#### 2.1.1 核心原理



**滑点计算模型**：



```

滑点定义:

Slippage = 实际成交价 - 理论价格



滑点分解:

Total_Slippage = Market_Impact + Timing_Cost + Spread_Cost



其中:

- Market_Impact: 市场冲击成本

- Timing_Cost: 时机成本（延迟成本）

- Spread_Cost: 买卖价差成本



Implementation Shortfall (IS):

IS = (实际成交价 - 决策价格)  交易量

```



#### 2.1.2 技术实现



```python

from typing import Dict, List, Optional

from datetime import datetime, timedelta

from dataclasses import dataclass

import numpy as np

import pandas as pd



@dataclass

class SlippageResult:

    """滑点分析结果"""

    trade_id: str

    actual_price: float          # 实际成交价

    theoretical_price: float     # 理论价格

    total_slippage: float        # 总滑点

    market_impact: float         # 市场冲击

    timing_cost: float           # 时机成本

    spread_cost: float           # 价差成本

    slippage_bps: float          # 滑点(基点)

    timestamp: datetime



class SlippageAnalysisEngine:

    """滑点分析引擎"""

    

    def __init__(self):

        self.bps_multiplier = 10000  # 基点乘数

        

    def analyze_slippage(self, 

                        trade_data: Dict,

                        market_data: pd.DataFrame,

                        order_data: Dict) -> SlippageResult:

        """分析滑点"""

        

        actual_price = trade_data['execution_price']

        

        theoretical_price = self._calculate_theoretical_price(

            trade_data,

            market_data,

            order_data

        )

        

        total_slippage = actual_price - theoretical_price

        

        market_impact = self._calculate_market_impact(

            trade_data,

            market_data

        )

        

        timing_cost = self._calculate_timing_cost(

            trade_data,

            order_data,

            market_data

        )

        

        spread_cost = self._calculate_spread_cost(

            trade_data,

            market_data

        )

        

        slippage_bps = (total_slippage / theoretical_price) * self.bps_multiplier

        

        return SlippageResult(

            trade_id=trade_data['trade_id'],

            actual_price=actual_price,

            theoretical_price=theoretical_price,

            total_slippage=total_slippage,

            market_impact=market_impact,

            timing_cost=timing_cost,

            spread_cost=spread_cost,

            slippage_bps=slippage_bps,

            timestamp=datetime.now()

        )

    

    def _calculate_theoretical_price(self, 

                                    trade_data: Dict,

                                    market_data: pd.DataFrame,

                                    order_data: Dict) -> float:

        """计算理论价格"""

        trade_time = trade_data['execution_time']

        order_time = order_data['order_time']

        

        arrival_price = market_data.loc[order_time, 'mid_price']

        

        return arrival_price

    

    def _calculate_market_impact(self, 

                                trade_data: Dict,

                                market_data: pd.DataFrame) -> float:

        """计算市场冲击"""

        trade_time = trade_data['execution_time']

        trade_size = trade_data['quantity']

        

        pre_trade_price = market_data.loc[trade_time - timedelta(seconds=5), 'mid_price']

        post_trade_price = market_data.loc[trade_time + timedelta(seconds=5), 'mid_price']

        

        impact = (post_trade_price - pre_trade_price) / pre_trade_price

        

        return impact * trade_data['execution_price']

    

    def _calculate_timing_cost(self, 

                              trade_data: Dict,

                              order_data: Dict,

                              market_data: pd.DataFrame) -> float:

        """计算时机成本"""

        order_time = order_data['order_time']

        trade_time = trade_data['execution_time']

        

        order_price = market_data.loc[order_time, 'mid_price']

        trade_price = market_data.loc[trade_time, 'mid_price']

        

        timing_cost = (trade_price - order_price) / order_price

        

        return timing_cost * trade_data['execution_price']

    

    def _calculate_spread_cost(self, 

                              trade_data: Dict,

                              market_data: pd.DataFrame) -> float:

        """计算价差成本"""

        trade_time = trade_data['execution_time']

        

        bid = market_data.loc[trade_time, 'bid_price']

        ask = market_data.loc[trade_time, 'ask_price']

        

        spread = ask - bid

        half_spread = spread / 2

        

        return half_spread

    

    def analyze_slippage_distribution(self, 

                                     trades: List[SlippageResult]) -> Dict:

        """分析滑点分布"""

        slippages = [t.slippage_bps for t in trades]

        

        return {

            'mean_slippage_bps': np.mean(slippages),

            'median_slippage_bps': np.median(slippages),

            'std_slippage_bps': np.std(slippages),

            'max_slippage_bps': np.max(slippages),

            'min_slippage_bps': np.min(slippages),

            'percentile_95': np.percentile(slippages, 95),

            'percentile_5': np.percentile(slippages, 5),

            'trades_analyzed': len(trades),

            'timestamp': datetime.now()

        }

```



```
```---
```



### 2.2 市场冲击分析引擎



#### 2.2.1 核心原理



**市场冲击模型**：



```

临时冲击:

Temporary_Impact = α  (Trade_Size / ADV)^β  σ



永久冲击:

Permanent_Impact = γ  (Trade_Size / ADV)^δ  σ



总冲击:

Total_Impact = Temporary_Impact + Permanent_Impact



其中:

- ADV: 平均日成交量

- σ: 波动率

- α, β, γ, δ: 模型参数

```



#### 2.2.2 技术实现



```python

@dataclass

class MarketImpactResult:

    """市场冲击分析结果"""

    trade_id: str

    trade_size: float             # 交易规模

    adv: float                    # 平均日成交量

    participation_rate: float     # 参与率

    temporary_impact: float       # 临时冲击

    permanent_impact: float       # 永久冲击

    total_impact: float           # 总冲击

    impact_bps: float             # 冲击(基点)

    decay_half_life: float       # 衰减半衰期

    timestamp: datetime



class MarketImpactEngine:

    """市场冲击分析引擎"""

    

    def __init__(self):

        self.model_params = {

            'alpha': 0.142,   # 临时冲击系数

            'beta': 0.5,      # 临时冲击指数

            'gamma': 0.089,   # 永久冲击系数

            'delta': 0.5      # 永久冲击指数

        }

        

    def analyze_impact(self, 

                      trade_data: Dict,

                      market_data: pd.DataFrame,

                      lookback_days: int = 20) -> MarketImpactResult:

        """分析市场冲击"""

        

        trade_size = trade_data['quantity']

        adv = self._calculate_adv(market_data, lookback_days)

        volatility = self._calculate_volatility(market_data, lookback_days)

        

        participation_rate = trade_size / adv

        

        temporary_impact = self._calculate_temporary_impact(

            trade_size, adv, volatility

        )

        

        permanent_impact = self._calculate_permanent_impact(

            trade_size, adv, volatility

        )

        

        total_impact = temporary_impact + permanent_impact

        

        impact_bps = (total_impact / trade_data['execution_price']) * 10000

        

        decay_half_life = self._estimate_decay_half_life(

            trade_data,

            market_data

        )

        

        return MarketImpactResult(

            trade_id=trade_data['trade_id'],

            trade_size=trade_size,

            adv=adv,

            participation_rate=participation_rate,

            temporary_impact=temporary_impact,

            permanent_impact=permanent_impact,

            total_impact=total_impact,

            impact_bps=impact_bps,

            decay_half_life=decay_half_life,

            timestamp=datetime.now()

        )

    

    def _calculate_adv(self, 

                      market_data: pd.DataFrame,

                      lookback_days: int) -> float:

        """计算平均日成交量"""

        volumes = market_data['volume'].tail(lookback_days)

        return volumes.mean()

    

    def _calculate_volatility(self, 

                             market_data: pd.DataFrame,

                             lookback_days: int) -> float:

        """计算波动率"""

        returns = market_data['close'].pct_change().tail(lookback_days)

        return returns.std() * np.sqrt(252)

    

    def _calculate_temporary_impact(self, 

                                   trade_size: float,

                                   adv: float,

                                   volatility: float) -> float:

        """计算临时冲击"""

        alpha = self.model_params['alpha']

        beta = self.model_params['beta']

        

        participation = trade_size / adv

        

        return alpha * (participation ** beta) * volatility

    

    def _calculate_permanent_impact(self, 

                                   trade_size: float,

                                   adv: float,

                                   volatility: float) -> float:

        """计算永久冲击"""

        gamma = self.model_params['gamma']

        delta = self.model_params['delta']

        

        participation = trade_size / adv

        

        return gamma * (participation ** delta) * volatility

    

    def _estimate_decay_half_life(self, 

                                 trade_data: Dict,

                                 market_data: pd.DataFrame) -> float:

        """估算冲击衰减半衰期"""

        return 15.0  # 默认15分钟

    

    def fit_impact_model(self, 

                        historical_trades: List[Dict],

                        market_data: pd.DataFrame) -> Dict:

        """拟合冲击模型参数"""

        from scipy.optimize import minimize

        

        def objective(params):

            alpha, beta, gamma, delta = params

            

            total_error = 0

            for trade in historical_trades:

                predicted_impact = (

                    alpha * (trade['size'] / trade['adv']) ** beta +

                    gamma * (trade['size'] / trade['adv']) ** delta

                ) * trade['volatility']

                

                actual_impact = trade['actual_impact']

                

                total_error += (predicted_impact - actual_impact) ** 2

            

            return total_error

        

        initial_params = [0.142, 0.5, 0.089, 0.5]

        

        result = minimize(objective, initial_params, method='L-BFGS-B')

        

        return {

            'alpha': result.x[0],

            'beta': result.x[1],

            'gamma': result.x[2],

            'delta': result.x[3],

            'optimization_success': result.success,

            'timestamp': datetime.now()

        }

```



```
```---
```



### 2.3 执行基准系统



#### 2.3.1 核心原理



**执行基准模型**：



```

VWAP基准:

VWAP = Σ(Price_i  Volume_i) / Σ Volume_i



TWAP基准:

TWAP = Σ Price_i / N



Arrival Price基准:

Arrival_Price = 订单到达时的中间价



Implementation Shortfall:

IS = (Execution_Price - Decision_Price)  Quantity

   = Market_Impact + Timing_Cost + Opportunity_Cost

```



#### 2.3.2 技术实现



```python

@dataclass

class BenchmarkResult:

    """基准计算结果"""

    order_id: str

    vwap: float                   # VWAP价格

    twap: float                   # TWAP价格

    arrival_price: float          # 到达价格

    execution_price: float        # 实际成交价

    vwap_slippage: float          # 相对VWAP滑点

    twap_slippage: float          # 相对TWAP滑点

    is_cost: float                # Implementation Shortfall

    timestamp: datetime



class ExecutionBenchmarkSystem:

    """执行基准系统"""

    

    def __init__(self):

        pass

        

    def calculate_benchmarks(self, 

                           order_data: Dict,

                           trade_data: List[Dict],

                           market_data: pd.DataFrame) -> BenchmarkResult:

        """计算执行基准"""

        

        vwap = self._calculate_vwap(market_data, order_data)

        

        twap = self._calculate_twap(market_data, order_data)

        

        arrival_price = self._calculate_arrival_price(market_data, order_data)

        

        execution_price = self._calculate_execution_price(trade_data)

        

        vwap_slippage = (execution_price - vwap) / vwap * 10000

        

        twap_slippage = (execution_price - twap) / twap * 10000

        

        is_cost = self._calculate_implementation_shortfall(

            execution_price,

            arrival_price,

            order_data['quantity']

        )

        

        return BenchmarkResult(

            order_id=order_data['order_id'],

            vwap=vwap,

            twap=twap,

            arrival_price=arrival_price,

            execution_price=execution_price,

            vwap_slippage=vwap_slippage,

            twap_slippage=twap_slippage,

            is_cost=is_cost,

            timestamp=datetime.now()

        )

    

    def _calculate_vwap(self, 

                       market_data: pd.DataFrame,

                       order_data: Dict) -> float:

        """计算VWAP"""

        start_time = order_data['order_time']

        end_time = order_data['end_time']

        

        period_data = market_data.loc[start_time:end_time]

        

        vwap = (period_data['close'] * period_data['volume']).sum() / period_data['volume'].sum()

        

        return vwap

    

    def _calculate_twap(self, 

                       market_data: pd.DataFrame,

                       order_data: Dict) -> float:

        """计算TWAP"""

        start_time = order_data['order_time']

        end_time = order_data['end_time']

        

        period_data = market_data.loc[start_time:end_time]

        

        twap = period_data['close'].mean()

        

        return twap

    

    def _calculate_arrival_price(self, 

                                market_data: pd.DataFrame,

                                order_data: Dict) -> float:

        """计算到达价格"""

        order_time = order_data['order_time']

        

        bid = market_data.loc[order_time, 'bid']

        ask = market_data.loc[order_time, 'ask']

        

        return (bid + ask) / 2

    

    def _calculate_execution_price(self, 

                                  trade_data: List[Dict]) -> float:

        """计算实际成交价"""

        total_value = sum(t['price'] * t['quantity'] for t in trade_data)

        total_quantity = sum(t['quantity'] for t in trade_data)

        

        return total_value / total_quantity

    

    def _calculate_implementation_shortfall(self, 

                                           execution_price: float,

                                           arrival_price: float,

                                           quantity: float) -> float:

        """计算Implementation Shortfall"""

        return (execution_price - arrival_price) * quantity

    

    def compare_to_benchmark(self, 

                            result: BenchmarkResult,

                            benchmark_type: str = 'vwap') -> Dict:

        """与基准比较"""

        if benchmark_type == 'vwap':

            benchmark_price = result.vwap

            slippage = result.vwap_slippage

        elif benchmark_type == 'twap':

            benchmark_price = result.twap

            slippage = result.twap_slippage

        else:

            benchmark_price = result.arrival_price

            slippage = result.is_cost

        

        return {

            'benchmark_type': benchmark_type,

            'benchmark_price': benchmark_price,

            'execution_price': result.execution_price,

            'slippage_bps': slippage,

            'performance': 'outperformed' if slippage < 0 else 'underperformed',

            'timestamp': datetime.now()

        }

```



```
```---
```



### 2.4 执行质量评估系统



#### 2.4.1 核心原理



**执行质量评估模型**：



```

经纪商评分:

Broker_Score = w1  Cost_Score + w2  Fill_Rate + w3  Speed_Score



成本评分:

Cost_Score = 100 - (Average_Slippage_Bps / Max_Acceptable_Slippage)  100



成交率:

Fill_Rate = Filled_Quantity / Ordered_Quantity



执行速度:

Speed_Score = 100 - (Execution_Time / Max_Time)  100

```



#### 2.4.2 技术实现



```python

@dataclass

class ExecutionQualityResult:

    """执行质量评估结果"""

    broker_id: str

    total_trades: int

    total_volume: float

    avg_slippage_bps: float

    fill_rate: float

    avg_execution_time: float

    cost_score: float

    speed_score: float

    overall_score: float

    ranking: int

    timestamp: datetime



class ExecutionQualityEvaluator:

    """执行质量评估系统"""

    

    def __init__(self):

        self.weights = {

            'cost': 0.5,

            'fill_rate': 0.3,

            'speed': 0.2

        }

        

        self.max_acceptable_slippage = 50  # 最大可接受滑点50bps

        self.max_execution_time = 3600     # 最大执行时间1小时

        

    def evaluate_broker(self, 

                       broker_id: str,

                       trades: List[Dict],

                       benchmarks: List[BenchmarkResult]) -> ExecutionQualityResult:

        """评估经纪商"""

        

        total_trades = len(trades)

        total_volume = sum(t['quantity'] for t in trades)

        

        avg_slippage_bps = np.mean([b.vwap_slippage for b in benchmarks])

        

        fill_rate = self._calculate_fill_rate(trades)

        

        avg_execution_time = self._calculate_avg_execution_time(trades)

        

        cost_score = self._calculate_cost_score(avg_slippage_bps)

        

        speed_score = self._calculate_speed_score(avg_execution_time)

        

        overall_score = (

            cost_score * self.weights['cost'] +

            fill_rate * 100 * self.weights['fill_rate'] +

            speed_score * self.weights['speed']

        )

        

        return ExecutionQualityResult(

            broker_id=broker_id,

            total_trades=total_trades,

            total_volume=total_volume,

            avg_slippage_bps=avg_slippage_bps,

            fill_rate=fill_rate,

            avg_execution_time=avg_execution_time,

            cost_score=cost_score,

            speed_score=speed_score,

            overall_score=overall_score,

            ranking=0,  # 后续排名

            timestamp=datetime.now()

        )

    

    def _calculate_fill_rate(self, trades: List[Dict]) -> float:

        """计算成交率"""

        filled = sum(t['filled_quantity'] for t in trades)

        ordered = sum(t['ordered_quantity'] for t in trades)

        

        return filled / ordered if ordered > 0 else 0.0

    

    def _calculate_avg_execution_time(self, trades: List[Dict]) -> float:

        """计算平均执行时间"""

        execution_times = [

            (t['end_time'] - t['start_time']).total_seconds()

            for t in trades

        ]

        

        return np.mean(execution_times) if execution_times else 0.0

    

    def _calculate_cost_score(self, avg_slippage_bps: float) -> float:

        """计算成本评分"""

        score = 100 - (avg_slippage_bps / self.max_acceptable_slippage) * 100

        return max(0, min(100, score))

    

    def _calculate_speed_score(self, avg_execution_time: float) -> float:

        """计算速度评分"""

        score = 100 - (avg_execution_time / self.max_execution_time) * 100

        return max(0, min(100, score))

    

    def rank_brokers(self, 

                    broker_results: List[ExecutionQualityResult]) -> List[ExecutionQualityResult]:

        """经纪商排名"""

        sorted_results = sorted(

            broker_results,

            key=lambda x: x.overall_score,

            reverse=True

        )

        

        for i, result in enumerate(sorted_results):

            result.ranking = i + 1

        

        return sorted_results

    

    def generate_optimization_suggestions(self, 

                                         result: ExecutionQualityResult) -> List[Dict]:

        """生成优化建议"""

        suggestions = []

        

        if result.avg_slippage_bps > 20:

            suggestions.append({

                'type': 'cost',

                'priority': 'high',

                'suggestion': '考虑使用VWAP/TWAP算法降低滑点',

                'expected_improvement': '降低滑点5-10bps'

            })

        

        if result.fill_rate < 0.95:

            suggestions.append({

                'type': 'fill_rate',

                'priority': 'medium',

                'suggestion': '考虑放宽限价单价格或使用市价单',

                'expected_improvement': '提高成交率5%'

            })

        

        if result.avg_execution_time > 1800:

            suggestions.append({

                'type': 'speed',

                'priority': 'low',

                'suggestion': '考虑提高参与率或分批执行',

                'expected_improvement': '缩短执行时间30%'

            })

        

        return suggestions

```



```
```---
```



## 三、tcapy开源集成方案



### 3.1 tcapy核心功能



**tcapy** 是业内首个开源TCA库，提供：



| 功能模块 | 说明 | 状态 |

|---------|------|------|

| **滑点分析** | 多种滑点指标计算 | ✅ 支持 |

| **市场冲击** | 临时/永久冲击分析 | ✅ 支持 |

| **基准比较** | VWAP/TWAP/Arrival Price | ✅ 支持 |

| **多数据源** | Arctic/KDB/InfluxDB | ✅ 支持 |

| **可视化** | 自动生成TCA报告 | ✅ 支持 |

| **FX支持** | 外汇交易TCA | ✅ 支持 |



### 3.2 tcapy集成代码



```python

from tcapy import TCA

from tcapy.data import TradeData, MarketData

import pandas as pd



class TCAPyIntegration:

    """tcapy集成接口"""

    

    def __init__(self, 

                 market_data_db: str = 'arctic',

                 trade_data_db: str = 'mysql'):

        self.tca = TCA(

            market_data_db=market_data_db,

            trade_data_db=trade_data_db

        )

        

    def analyze_trades(self, 

                      trade_df: pd.DataFrame,

                      order_df: pd.DataFrame,

                      ticker: str,

                      start_date: str,

                      end_date: str) -> Dict:

        """分析交易成本"""

        

        results = self.tca.calculate_tca(

            trade_df=trade_df,

            order_df=order_df,

            ticker=ticker,

            start_date=start_date,

            end_date=end_date

        )

        

        return {

            'slippage_analysis': results['slippage'],

            'market_impact': results['impact'],

            'vwap_comparison': results['vwap'],

            'twap_comparison': results['twap'],

            'implementation_shortfall': results['is'],

            'timestamp': pd.Timestamp.now()

        }

    

    def generate_tca_report(self, 

                           results: Dict,

                           output_format: str = 'html') -> str:

        """生成TCA报告"""

        

        report = self.tca.generate_report(

            results=results,

            format=output_format

        )

        

        return report

    

    def compare_brokers(self, 

                       broker_trades: Dict[str, pd.DataFrame]) -> pd.DataFrame:

        """比较经纪商执行质量"""

        

        comparison = self.tca.compare_brokers(

            broker_trades=broker_trades

        )

        

        return comparison

```



### 3.3 tcapy安装配置



```bash

pip install tcapy



from tcapy import TCA



tca = TCA(

    market_data_db='arctic',

    trade_data_db='mysql'

)



results = tca.calculate_tca(

    trade_df=trade_data,

    order_df=order_data,

    ticker='000001.SZ',

    start_date='2026-01-01',

    end_date='2026-03-31'

)

```



```
```---
```



## 四、数据模型与接口设计



### 4.1 核心数据结构



```python

@dataclass

class TCAReport:

    """TCA报告"""

    report_id: str

    report_date: datetime

    portfolio_id: str

    slippage_results: List[SlippageResult]

    impact_results: List[MarketImpactResult]

    benchmark_results: List[BenchmarkResult]

    quality_results: List[ExecutionQualityResult]

    summary: Dict

    created_at: datetime

```



### 4.2 接口定义



```python

class TCAInterface:

    """TCA接口"""

    

    def analyze_trade_cost(self, 

                          trade_data: Dict,

                          market_data: pd.DataFrame) -> TCAReport:

        """分析交易成本"""

        pass

    

    def generate_tca_report(self, 

                           result: TCAReport,

                           format: str = 'html') -> str:

        """生成TCA报告"""

        pass

    

    def compare_execution_quality(self, 

                                 broker_ids: List[str],

                                 period: str) -> pd.DataFrame:

        """比较执行质量"""

        pass

```



```
```---
```



## 五、与其他模块的集成



### 5.1 与Layer 5策略执行的集成



```

Layer 5 策略执行

    ↓ 交易数据

Layer 11.9 TCA系统

    ├── 接收成交数据

    ├── 分析交易成本

    └── 返回成本报告

    ↓ 成本反馈

Layer 5 执行优化

```



### 5.2 与Layer 11.8流动性管理的集成



```

Layer 11.8 流动性管理

    ↓ 流动性约束

Layer 11.9 TCA系统

    ├── 考虑流动性成本

    ├── 优化执行策略

    └── 返回最优执行方案

    ↓ 执行方案

Layer 5 策略执行

```



### 5.3 与Layer 8监控报告的集成



```

Layer 11.9 TCA系统

    ↓ TCA报告

Layer 8 监控报告

    ├── 集成TCA报告

    ├── 可视化展示

    └── 异常预警

    ↓ 报告输出

用户界面

```



```
```---
```



## 六、实施路径



### 6.1 Phase 1: tcapy集成（1周）



**目标**: 集成tcapy开源库



| 任务 | 时间 | 交付成果 |

|------|------|---------|

| tcapy安装配置 | 1天 | tcapy环境搭建 |

| 数据接口开发 | 2天 | 数据获取接口 |

| 基础TCA功能 | 2天 | 基础TCA分析 |

| 测试验证 | 2天 | 单元测试通过 |



### 6.2 Phase 2: 自定义功能开发（1周）



**目标**: 开发A股特色功能



| 任务 | 时间 | 交付成果 |

|------|------|---------|

| A股滑点分析 | 2天 | A股滑点引擎 |

| 市场冲击模型 | 2天 | 冲击分析引擎 |

| 执行质量评估 | 2天 | 质量评估系统 |

| 报告生成 | 1天 | TCA报告系统 |



```
```---
```



## 七、A股市场特色功能



### 7.1 涨跌停板TCA



```python

class LimitUpDownTCA:

    """涨跌停板TCA分析"""

    

    def analyze_limit_impact(self, 

                            trade_data: Dict,

                            market_data: pd.DataFrame) -> Dict:

        """分析涨跌停对交易成本的影响"""

        

        limit_price = trade_data['limit_price']

        execution_price = trade_data['execution_price']

        

        if abs(execution_price - limit_price) / limit_price < 0.001:

            return {

                'at_limit': True,

                'impact_on_cost': 'high',

                'suggestion': '避免在涨跌停附近大额交易'

            }

        

        return {

            'at_limit': False,

            'impact_on_cost': 'normal'

        }

```



### 7.2 集合竞价TCA



```python

class CallAuctionTCA:

    """集合竞价TCA分析"""

    

    def analyze_auction_cost(self, 

                            trade_data: Dict,

                            auction_data: pd.DataFrame) -> Dict:

        """分析集合竞价成本"""

        

        auction_price = auction_data['auction_price']

        continuous_price = auction_data['continuous_price']

        

        auction_slippage = (trade_data['execution_price'] - auction_price) / auction_price

        

        return {

            'auction_slippage_bps': auction_slippage * 10000,

            'auction_vs_continuous': (auction_price - continuous_price) / continuous_price * 10000,

            'recommendation': '集合竞价适合大额订单' if auction_slippage < 0 else '考虑连续竞价'

        }

```



```
```---
```



## 八、风险评估



### 8.1 技术风险



| 风险 | 影响 | 缓解措施 |

|------|------|---------|

| **数据质量** | 高 | 数据清洗 + 异常检测 |

| **模型准确性** | 中 | 多模型验证 + 参数校准 |

| **计算性能** | 中 | 增量计算 + 缓存机制 |



### 8.2 实施风险



| 风险 | 影响 | 缓解措施 |

|------|------|---------|

| **tcapy学习曲线** | 中 | 文档学习 + 示例代码 |

| **数据源适配** | 中 | 数据适配器开发 |

| **A股特色** | 中 | 自定义功能开发 |



```
```---
```



## 九、质量保证



### 9.1 测试标准



| 测试类型 | 覆盖率要求 | 通过标准 |

|---------|-----------|---------|

| **单元测试** | ≥90% | 所有测试通过 |

| **集成测试** | ≥85% | 关键路径通过 |

| **数据验证** | 历史数据 | 滑点误差<5% |

| **性能测试** | 大数据集 | 计算时间<30秒 |



### 9.2 监控指标



| 指标 | 目标值 | 监控频率 |

|------|--------|---------|

| **TCA分析准确率** | >95% | 月频 |

| **报告生成时间** | <60秒 | 实时 |

| **滑点预测误差** | <10% | 月频 |

| **经纪商排名准确率** | >90% | 季频 |



```
```---
```



## 十、相关文档



| 文档 | 说明 |

|------|------|

| BLUEPRINT.md | Layer 11主蓝图 |

| [ARCHITECTURE.md](../01_FRAMEWORK/ARCHITECTURE.md) | 系统架构 |

| LIQUIDITY_MANAGEMENT_BLUEPRINT.md | 流动性管理系统 |

| [tcapy GitHub](https://github.com/cuemacro/tcapy) | tcapy开源项目 |



```
```---
```



## 十一、版本历史



| 版本 | 日期 | 变更说明 |

|------|------|---------|

| v1.0 | 2026-04-06 | 初始版本，完成TCA系统设计 |



```
```---
```



**文档状态**: ✅ 设计完成  

**开源方案**: tcapy  

**下一步**: 创建再平衡决策系统蓝图

```
```---
```



## 1. 文档治理



### 1.1 System_Manifest.md索引



```markdown

#### Layer 0: 系统架构

##### 0.001. Tca Blueprint

- **模块ID**: TCA_BLUEPRINT_001

- **蓝图文档**: TCA_BLUEPRINT.md

- **技术规格书**: 待创建

- **职责**: Layer 11.9 - 交易成本分析系统

- **状态**: Active

```



### 1.2 模块职责边界



| 模块 | 职责 | 边界 |

|------|------|------|

| **Tca Blueprint** | Layer 11.9 - 交易成本分析系统 | **核心模块** |



### 1.3 版本管理



| 版本 | 日期 | 变更内容 | 变更人 |

|------|------|----------|--------|

| v1.0.0 | 2026-04-06 | 初始版本创建 | 首席蓝图架构师 |



```
```---
```



**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-06 | **状态**: Active

