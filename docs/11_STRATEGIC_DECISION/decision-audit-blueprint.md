---
module_id: DECISIONAUDITBLUEPRINT_001_3800
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: '2026-04-07'
owner: 文档管理员
layer: layer_11
standard_type: 专业量化机构蓝图
applicable_scope: 全系统
compliance_level: 专业标准
responsibility:
- 系统架构蓝图设计与实施指导与实施方案
---

```
module_id: DECISION_AUDIT_001_3800
```

version: 1.0.0

status: Active

created_date: 2026-04-06

last_updated: 2026-04-06

owner: 首席架构师

standard_type: 专业量化机构级蓝图

applicable_scope: Layer 11.21 - 投资决策审计系统

compliance_level: 专业标准

reference_models: ["SEC Audit Trail Requirements", "MiFID II Record Keeping", "CFA Ethics Standards"]

open_source_solution: "自研审计日志系统"

priority: P2

```
```---
```



# 投资决策审计系统蓝图

> **核心职责**: 投资决策审计系统蓝图设计

> **职责边界**: 

> - ✅ 本文档负责：投资决策审计系统蓝图设计相关内容

> - ❌ 本文档不负责：其他模块内容



> **核心职责**: Decision Audit蓝图设计

> **职责边界**: 

> - ✅ 本文档负责：Decision Audit蓝图设计相关内容

> - ❌ 本文档不负责：其他模块内容





## 📋 文档职责说明



### 核心职责



本文档是**模块蓝图，负责特定功能的实现**。



### 职责边界



**负责**：

- ✅ 核心功能实现

- ✅ 接口定义

- ✅ 数据模型设计



**不负责**：

- ❌ 其他模块职责

- ❌ 跨模块协调



### 对接模块



**上游模块**：

- 上游模块



**下游模块**：

- 下游模块



```
```---
```

> **版本**: v1.0

> **创建日期**: 2026-04-06

> **优先级**: 🟢 P2 - 可选

> **开源方案**: 自研审计日志系统

> **目标**: 构建投资决策审计系统，实现决策追溯、学习改进、合规记录



```
```---
```



## 📋 执行摘要



### 核心定位



投资决策审计系统是Layer 11战略决策层的**决策追溯与学习系统**，负责：

- 投资决策全流程记录

- 决策依据与上下文保存

- 决策结果与绩效追踪

- 决策质量分析与改进



### 专业价值



| 价值维度 | 专业机构实践 | 个人实现方式 | 价值评级 |

|---------|-------------|-------------|---------|

| **决策追溯** | 合规审计团队 | 自动化审计日志 | ⭐⭐⭐⭐ |

| **学习改进** | 投后分析团队 | 决策复盘分析 | ⭐⭐⭐⭐ |

| **合规记录** | 合规部门 | 自动化记录 | ⭐⭐⭐ |

| **绩效归因** | 绩效分析团队 | 决策绩效追踪 | ⭐⭐⭐⭐ |



**综合价值评级**: ⭐⭐⭐⭐ (4/5) - **建议实施**



```
```---
```



## 一、架构设计



### 1.1 系统整体架构



```

┌─────────────────────────────────────────────────────────────────┐

│          投资决策审计系统架构 (Decision Audit System)            │

├─────────────────────────────────────────────────────────────────┤

│                                                                 │

│  ┌───────────────────────────────────────────────────────────┐ │

│  │              11.21.1 决策记录层                            │ │

│  │  ┌─────────────────────────────────────────────────────┐  │ │

│  │  │ 决策捕获器 (Decision Capture)                       │  │ │

│  │  │ ├── 决策事件监听（决策事件触发）                     │  │ │

│  │  │ ├── 决策上下文捕获（市场环境、组合状态）             │  │ │

│  │  │ ├── 决策依据记录（信号、因子、模型输出）             │  │ │

│  │  │ └── 决策时间戳（精确时间记录）                       │  │ │

│  │  └─────────────────────────────────────────────────────┘  │ │

│  │  ┌─────────────────────────────────────────────────────┐  │ │

│  │  │ 决策存储器 (Decision Storage)                       │  │ │

│  │  │ ├── 结构化存储（决策数据结构化存储）                 │  │ │

│  │  │ ├── 索引建立（快速查询索引）                         │  │ │

│  │  │ ├── 压缩归档（历史数据压缩归档）                     │  │ │

│  │  │ └── 备份机制（数据备份保护）                         │  │ │

│  │  └─────────────────────────────────────────────────────┘  │ │

│  └───────────────────────────────────────────────────────────┘ │

│                                                                 │

│  ┌───────────────────────────────────────────────────────────┐ │

│  │              11.21.2 决策追踪层                            │ │

│  │  ┌─────────────────────────────────────────────────────┐  │ │

│  │  │ 执行追踪器 (Execution Tracker)                      │  │ │

│  │  │ ├── 执行状态追踪（订单执行状态）                     │  │ │

│  │  │ ├── 执行成本记录（交易成本记录）                     │  │ │

│  │  │ ├── 执行偏差分析（计划vs实际）                       │  │ │

│  │  │ └── 执行时间记录（执行耗时）                         │  │ │

│  │  └─────────────────────────────────────────────────────┘  │ │

│  │  ┌─────────────────────────────────────────────────────┐  │ │

│  │  │ 绩效追踪器 (Performance Tracker)                    │  │ │

│  │  │ ├── 持仓绩效追踪（持仓盈亏追踪）                     │  │ │

│  │  │ ├── 决策绩效计算（决策收益计算）                     │  │ │

│  │  │ ├── 风险调整绩效（风险调整收益）                     │  │ │

│  │  │ └── 绩效归因（绩效来源分析）                         │  │ │

│  │  └─────────────────────────────────────────────────────┘  │ │

│  └───────────────────────────────────────────────────────────┘ │

│                                                                 │

│  ┌───────────────────────────────────────────────────────────┐ │

│  │              11.21.3 决策分析层                            │ │

│  │  ┌─────────────────────────────────────────────────────┐  │ │

│  │  │ 决策质量分析 (Decision Quality Analysis)            │  │ │

│  │  │ ├── 决策准确率（正确决策比例）                       │  │ │

│  │  │ ├── 决策效率（决策时间效率）                         │  │ │

│  │  │ ├── 决策一致性（决策逻辑一致性）                     │  │ │

│  │  │ └── 决策偏差分析（常见决策偏差）                     │  │ │

│  │  └─────────────────────────────────────────────────────┘  │ │

│  │  ┌─────────────────────────────────────────────────────┐  │ │

│  │  │ 模式识别分析 (Pattern Recognition Analysis)         │  │ │

│  │  │ ├── 成功模式识别（成功决策模式）                     │  │ │

│  │  │ ├── 失败模式识别（失败决策模式）                     │  │ │

│  │  │ ├── 市场环境关联（环境与决策关联）                   │  │ │

│  │  │ └── 改进建议生成（决策改进建议）                     │  │ │

│  │  └─────────────────────────────────────────────────────┘  │ │

│  └───────────────────────────────────────────────────────────┘ │

│                                                                 │

│  ┌───────────────────────────────────────────────────────────┐ │

│  │              11.21.4 决策复盘层                            │ │

│  │  ┌─────────────────────────────────────────────────────┐  │ │

│  │  │ 复盘报告生成 (Review Report Generator)              │  │ │

│  │  │ ├── 定期复盘报告（周/月/季度复盘）                   │  │ │

│  │  │ ├── 事件复盘报告（重大事件复盘）                     │  │ │

│  │  │ ├── 策略复盘报告（策略绩效复盘）                     │  │ │

│  │  │ └── 自定义复盘（用户定义复盘）                       │  │ │

│  │  └─────────────────────────────────────────────────────┘  │ │

│  │  ┌─────────────────────────────────────────────────────┐  │ │

│  │  │ 经验库管理 (Experience Library Management)          │  │ │

│  │  │ ├── 经验提取（从决策中提取经验）                     │  │ │

│  │  │ ├── 经验分类（经验分类存储）                         │  │ │

│  │  │ ├── 经验检索（经验检索应用）                         │  │ │

│  │  │ └── 经验更新（经验迭代更新）                         │  │ │

│  │  └─────────────────────────────────────────────────────┘  │ │

│  └───────────────────────────────────────────────────────────┘ │

│                                                                 │

│  ┌───────────────────────────────────────────────────────────┐ │

│  │              11.21.5 合规报告层                            │ │

│  │  ┌─────────────────────────────────────────────────────┐  │ │

│  │  │ 审计日志管理 (Audit Log Management)                 │  │ │

│  │  │ ├── 日志完整性（日志不可篡改）                       │  │ │

│  │  │ ├── 日志查询（快速日志查询）                         │  │ │

│  │  │ ├── 日志导出（合规报告导出）                         │  │ │

│  │  │ └── 日志保留（日志保留策略）                         │  │ │

│  │  └─────────────────────────────────────────────────────┘  │ │

│  │  ┌─────────────────────────────────────────────────────┐  │ │

│  │  │ 合规报告生成 (Compliance Report Generator)          │  │ │

│  │  │ ├── 交易报告（交易记录报告）                         │  │ │

│  │  │ ├── 决策报告（决策记录报告）                         │  │ │

│  │  │ ├── 风险报告（风险记录报告）                         │  │ │

│  │  │ └── 综合报告（综合审计报告）                         │  │ │

│  │  └─────────────────────────────────────────────────────┘  │ │

│  └───────────────────────────────────────────────────────────┘ │

│                                                                 │

└─────────────────────────────────────────────────────────────────┘

```



### 1.2 模块职责边界



| 模块 | 核心职责 | 输入 | 输出 | 对接模块 |

|------|---------|------|------|---------|

| **决策记录层** | 记录决策全流程 | 决策事件 | 决策记录 | 所有模块 |

| **决策追踪层** | 追踪执行与绩效 | 执行数据 | 追踪结果 | 分析层 |

| **决策分析层** | 分析决策质量 | 决策记录 | 分析报告 | 复盘层 |

| **决策复盘层** | 生成复盘报告 | 分析结果 | 复盘报告 | 报告层 |

| **合规报告层** | 生成合规报告 | 审计日志 | 合规报告 | 外部 |



```
```---
```



## 二、核心组件详细设计



### 2.1 决策记录层



```python

from typing import Dict, List, Optional, Any

from datetime import datetime, date

from dataclasses import dataclass, field

from enum import Enum

import json

import hashlib

import pandas as pd



class DecisionType(Enum):

    """决策类型"""

    ENTRY = "entry"             # 入场决策

    EXIT = "exit"               # 出场决策

    ADJUST = "adjust"           # 调仓决策

    REBALANCE = "rebalance"     # 再平衡决策

    HEDGE = "hedge"             # 对冲决策

    CASH_MANAGE = "cash_manage" # 现金管理决策



class DecisionSource(Enum):

    """决策来源"""

    MANUAL = "manual"           # 人工决策

    AUTO = "auto"               # 自动决策

    HYBRID = "hybrid"           # 混合决策



@dataclass

class MarketContext:

    """市场环境上下文"""

    timestamp: datetime

    market_regime: str          # 市场状态

    volatility_level: float     # 波动率水平

    trend_direction: str        # 趋势方向

    sector_performance: Dict[str, float]  # 行业表现

    key_events: List[str]       # 关键事件



@dataclass

class PortfolioContext:

    """组合状态上下文"""

    timestamp: datetime

    total_value: float

    cash_ratio: float

    position_count: int

    current_risk: float

    current_drawdown: float

    sector_allocation: Dict[str, float]



@dataclass

class DecisionRationale:

    """决策依据"""

    signals: Dict[str, Any]     # 信号数据

    factors: Dict[str, float]   # 因子数据

    model_outputs: Dict[str, Any]  # 模型输出

    constraints: List[str]      # 约束条件

    risk_assessment: Dict       # 风险评估

    alternative_options: List[Dict]  # 备选方案



@dataclass

class DecisionRecord:

    """决策记录"""

    decision_id: str

    decision_type: DecisionType

    decision_source: DecisionSource

    timestamp: datetime

    strategy_id: str

    asset_code: str

    action: str                 # 'buy', 'sell', 'hold'

    target_weight: float

    target_price: Optional[float]

    

    market_context: MarketContext

    portfolio_context: PortfolioContext

    rationale: DecisionRationale

    

    expected_return: float

    expected_risk: float

    confidence: float

    

    status: str = 'pending'

    execution_result: Optional[Dict] = None

    performance_result: Optional[Dict] = None

    

    created_at: datetime = field(default_factory=datetime.now)

    updated_at: datetime = field(default_factory=datetime.now)



class DecisionCapture:

    """决策捕获器"""

    

    def __init__(self):

        self.decision_counter = 0

    

    def capture_market_context(self) -> MarketContext:

        """捕获市场环境"""

        return MarketContext(

            timestamp=datetime.now(),

            market_regime="normal",

            volatility_level=0.2,

            trend_direction="neutral",

            sector_performance={},

            key_events=[]

        )

    

    def capture_portfolio_context(self,

                                  portfolio_data: Dict) -> PortfolioContext:

        """捕获组合状态"""

        return PortfolioContext(

            timestamp=datetime.now(),

            total_value=portfolio_data.get('total_value', 0),

            cash_ratio=portfolio_data.get('cash_ratio', 0),

            position_count=portfolio_data.get('position_count', 0),

            current_risk=portfolio_data.get('current_risk', 0),

            current_drawdown=portfolio_data.get('current_drawdown', 0),

            sector_allocation=portfolio_data.get('sector_allocation', {})

        )

    

    def capture_rationale(self,

                         signals: Dict,

                         factors: Dict,

                         model_outputs: Dict) -> DecisionRationale:

        """捕获决策依据"""

        return DecisionRationale(

            signals=signals,

            factors=factors,

            model_outputs=model_outputs,

            constraints=[],

            risk_assessment={},

            alternative_options=[]

        )

    

    def create_decision_record(self,

                              decision_type: DecisionType,

                              decision_source: DecisionSource,

                              strategy_id: str,

                              asset_code: str,

                              action: str,

                              target_weight: float,

                              market_context: MarketContext,

                              portfolio_context: PortfolioContext,

                              rationale: DecisionRationale,

                              expected_return: float = 0,

                              expected_risk: float = 0,

                              confidence: float = 0.5) -> DecisionRecord:

        """创建决策记录"""

        self.decision_counter += 1

        

        return DecisionRecord(

            decision_id=f"DEC_{self.decision_counter:08d}",

            decision_type=decision_type,

            decision_source=decision_source,

            timestamp=datetime.now(),

            strategy_id=strategy_id,

            asset_code=asset_code,

            action=action,

            target_weight=target_weight,

            target_price=None,

            market_context=market_context,

            portfolio_context=portfolio_context,

            rationale=rationale,

            expected_return=expected_return,

            expected_risk=expected_risk,

            confidence=confidence

        )



class DecisionStorage:

    """决策存储器"""

    

    def __init__(self, storage_path: str = "data/audit/decisions"):

        self.storage_path = storage_path

        self.decisions: List[DecisionRecord] = []

        self.index: Dict[str, int] = {}

    

    def store(self, decision: DecisionRecord):

        """存储决策"""

        idx = len(self.decisions)

        self.decisions.append(decision)

        

        self.index[decision.decision_id] = idx

        self.index[f"strategy_{decision.strategy_id}"] = idx

        self.index[f"asset_{decision.asset_code}"] = idx

        self.index[f"date_{decision.timestamp.date()}"] = idx

    

    def get_by_id(self, decision_id: str) -> Optional[DecisionRecord]:

        """按ID获取"""

        idx = self.index.get(decision_id)

        if idx is not None:

            return self.decisions[idx]

        return None

    

    def get_by_strategy(self, strategy_id: str) -> List[DecisionRecord]:

        """按策略获取"""

        return [d for d in self.decisions if d.strategy_id == strategy_id]

    

    def get_by_date_range(self,

                         start_date: date,

                         end_date: date) -> List[DecisionRecord]:

        """按日期范围获取"""

        return [

            d for d in self.decisions

            if start_date <= d.timestamp.date() <= end_date

        ]

    

    def get_by_type(self, decision_type: DecisionType) -> List[DecisionRecord]:

        """按类型获取"""

        return [d for d in self.decisions if d.decision_type == decision_type]

    

    def compute_hash(self, decision: DecisionRecord) -> str:

        """计算决策哈希（防篡改）"""

        data = json.dumps({

            'decision_id': decision.decision_id,

            'timestamp': decision.timestamp.isoformat(),

            'action': decision.action,

            'target_weight': decision.target_weight

        }, sort_keys=True)

        

        return hashlib.sha256(data.encode()).hexdigest()

```



### 2.2 决策追踪层



```python

@dataclass

class ExecutionResult:

    """执行结果"""

    decision_id: str

    executed_at: datetime

    execution_status: str       # 'success', 'partial', 'failed'

    filled_quantity: float

    filled_price: float

    execution_cost: float

    slippage: float

    execution_time_ms: int

    broker_order_id: str



@dataclass

class PerformanceResult:

    """绩效结果"""

    decision_id: str

    entry_price: float

    exit_price: Optional[float]

    holding_days: int

    realized_pnl: float

    realized_pnl_pct: float

    annualized_return: float

    max_drawdown_during: float

    sharpe_ratio: float

    exit_reason: Optional[str] = None

    exited_at: Optional[datetime] = None



class ExecutionTracker:

    """执行追踪器"""

    

    def __init__(self):

        self.executions: Dict[str, ExecutionResult] = {}

    

    def record_execution(self,

                        decision_id: str,

                        execution_data: Dict) -> ExecutionResult:

        """记录执行结果"""

        result = ExecutionResult(

            decision_id=decision_id,

            executed_at=datetime.now(),

            execution_status=execution_data.get('status', 'success'),

            filled_quantity=execution_data.get('filled_quantity', 0),

            filled_price=execution_data.get('filled_price', 0),

            execution_cost=execution_data.get('cost', 0),

            slippage=execution_data.get('slippage', 0),

            execution_time_ms=execution_data.get('execution_time_ms', 0),

            broker_order_id=execution_data.get('order_id', '')

        )

        

        self.executions[decision_id] = result

        return result

    

    def analyze_execution_quality(self,

                                 decision: DecisionRecord,

                                 execution: ExecutionResult) -> Dict:

        """分析执行质量"""

        planned_weight = decision.target_weight

        executed_weight = execution.filled_quantity

        

        weight_deviation = abs(planned_weight - executed_weight) / planned_weight if planned_weight > 0 else 0

        

        return {

            'weight_deviation': weight_deviation,

            'slippage': execution.slippage,

            'execution_cost': execution.execution_cost,

            'execution_time_ms': execution.execution_time_ms,

            'quality_score': 1 - (weight_deviation + execution.slippage / 100)

        }



class PerformanceTracker:

    """绩效追踪器"""

    

    def __init__(self):

        self.performances: Dict[str, PerformanceResult] = {}

        self.active_positions: Dict[str, Dict] = {}

    

    def start_tracking(self,

                      decision_id: str,

                      entry_price: float,

                      entry_date: date):

        """开始追踪"""

        self.active_positions[decision_id] = {

            'entry_price': entry_price,

            'entry_date': entry_date,

            'max_price': entry_price,

            'min_price': entry_price

        }

    

    def update_tracking(self,

                       decision_id: str,

                       current_price: float):

        """更新追踪"""

        if decision_id in self.active_positions:

            pos = self.active_positions[decision_id]

            pos['max_price'] = max(pos['max_price'], current_price)

            pos['min_price'] = min(pos['min_price'], current_price)

    

    def end_tracking(self,

                    decision_id: str,

                    exit_price: float,

                    exit_date: date,

                    exit_reason: str = 'signal') -> PerformanceResult:

        """结束追踪"""

        pos = self.active_positions.get(decision_id)

        if not pos:

            return None

        

        entry_price = pos['entry_price']

        entry_date = pos['entry_date']

        

        holding_days = (exit_date - entry_date).days

        

        realized_pnl = exit_price - entry_price

        realized_pnl_pct = realized_pnl / entry_price if entry_price > 0 else 0

        

        annualized_return = (1 + realized_pnl_pct) ** (365 / max(holding_days, 1)) - 1

        

        max_drawdown = (pos['max_price'] - pos['min_price']) / pos['max_price'] if pos['max_price'] > 0 else 0

        

        result = PerformanceResult(

            decision_id=decision_id,

            entry_price=entry_price,

            exit_price=exit_price,

            holding_days=holding_days,

            realized_pnl=realized_pnl,

            realized_pnl_pct=realized_pnl_pct,

            annualized_return=annualized_return,

            max_drawdown_during=max_drawdown,

            sharpe_ratio=annualized_return / max_drawdown if max_drawdown > 0 else 0,

            exit_reason=exit_reason,

            exited_at=datetime.now()

        )

        

        self.performances[decision_id] = result

        del self.active_positions[decision_id]

        

        return result

    

    def get_performance_summary(self,

                               decision_ids: List[str]) -> Dict:

        """获取绩效汇总"""

        results = [self.performances[did] for did in decision_ids if did in self.performances]

        

        if not results:

            return {}

        

        return {

            'total_decisions': len(results),

            'winning_decisions': sum(1 for r in results if r.realized_pnl > 0),

            'win_rate': sum(1 for r in results if r.realized_pnl > 0) / len(results),

            'avg_return': sum(r.realized_pnl_pct for r in results) / len(results),

            'avg_holding_days': sum(r.holding_days for r in results) / len(results),

            'total_pnl': sum(r.realized_pnl for r in results),

            'avg_sharpe': sum(r.sharpe_ratio for r in results) / len(results)

        }

```



### 2.3 决策分析层



```python

@dataclass

class DecisionQualityMetrics:

    """决策质量指标"""

    analysis_date: date

    total_decisions: int

    correct_decisions: int

    accuracy_rate: float

    avg_decision_time_ms: float

    consistency_score: float

    bias_analysis: Dict[str, float]



@dataclass

class DecisionPattern:

    """决策模式"""

    pattern_id: str

    pattern_type: str       # 'success', 'failure'

    conditions: Dict        # 触发条件

    outcome: Dict           # 结果特征

    frequency: int          # 出现频率

    avg_return: float       # 平均收益



class DecisionQualityAnalyzer:

    """决策质量分析器"""

    

    def __init__(self):

        self.quality_history: List[DecisionQualityMetrics] = []

    

    def calculate_accuracy(self,

                          decisions: List[DecisionRecord],

                          performances: Dict[str, PerformanceResult]) -> float:

        """计算决策准确率"""

        correct = 0

        total = 0

        

        for decision in decisions:

            if decision.decision_id in performances:

                perf = performances[decision.decision_id]

                total += 1

                

                if decision.action == 'buy' and perf.realized_pnl > 0:

                    correct += 1

                elif decision.action == 'sell' and perf.realized_pnl < 0:

                    correct += 1

        

        return correct / total if total > 0 else 0

    

    def analyze_consistency(self,

                           decisions: List[DecisionRecord]) -> float:

        """分析决策一致性"""

        if len(decisions) < 2:

            return 1.0

        

        similar_contexts = 0

        total_pairs = 0

        

        for i, d1 in enumerate(decisions):

            for d2 in decisions[i+1:]:

                if self._similar_context(d1, d2):

                    total_pairs += 1

                    if d1.action == d2.action:

                        similar_contexts += 1

        

        return similar_contexts / total_pairs if total_pairs > 0 else 1.0

    

    def _similar_context(self,

                        d1: DecisionRecord,

                        d2: DecisionRecord,

                        threshold: float = 0.8) -> bool:

        """判断上下文相似"""

        same_regime = d1.market_context.market_regime == d2.market_context.market_regime

        

        vol_diff = abs(d1.market_context.volatility_level - d2.market_context.volatility_level)

        similar_vol = vol_diff < 0.1

        

        return same_regime and similar_vol

    

    def detect_biases(self,

                     decisions: List[DecisionRecord],

                     performances: Dict[str, PerformanceResult]) -> Dict[str, float]:

        """检测决策偏差"""

        biases = {}

        

        disposition_effect = self._calculate_disposition_effect(decisions, performances)

        biases['disposition_effect'] = disposition_effect

        

        overconfidence = self._calculate_overconfidence(decisions, performances)

        biases['overconfidence'] = overconfidence

        

        herding = self._calculate_herding(decisions)

        biases['herding'] = herding

        

        return biases

    

    def _calculate_disposition_effect(self,

                                     decisions: List[DecisionRecord],

                                     performances: Dict[str, PerformanceResult]) -> float:

        """计算处置效应"""

        early_profit_close = 0

        late_loss_close = 0

        total_profit = 0

        total_loss = 0

        

        for decision in decisions:

            if decision.decision_id not in performances:

                continue

            

            perf = performances[decision.decision_id]

            

            if perf.realized_pnl > 0:

                total_profit += 1

                if perf.holding_days < 5:

                    early_profit_close += 1

            else:

                total_loss += 1

                if perf.holding_days > 20:

                    late_loss_close += 1

        

        profit_close_rate = early_profit_close / total_profit if total_profit > 0 else 0

        loss_hold_rate = late_loss_close / total_loss if total_loss > 0 else 0

        

        return profit_close_rate - loss_hold_rate

    

    def _calculate_overconfidence(self,

                                 decisions: List[DecisionRecord],

                                 performances: Dict[str, PerformanceResult]) -> float:

        """计算过度自信"""

        high_confidence_correct = 0

        high_confidence_total = 0

        

        for decision in decisions:

            if decision.decision_id not in performances:

                continue

            

            if decision.confidence > 0.8:

                high_confidence_total += 1

                perf = performances[decision.decision_id]

                if perf.realized_pnl > 0:

                    high_confidence_correct += 1

        

        if high_confidence_total == 0:

            return 0

        

        actual_accuracy = high_confidence_correct / high_confidence_total

        expected_accuracy = 0.8

        

        return max(0, expected_accuracy - actual_accuracy)

    

    def _calculate_herding(self, decisions: List[DecisionRecord]) -> float:

        """计算羊群效应"""

        if len(decisions) < 2:

            return 0

        

        same_day_decisions = {}

        for d in decisions:

            date_key = d.timestamp.date()

            if date_key not in same_day_decisions:

                same_day_decisions[date_key] = []

            same_day_decisions[date_key].append(d)

        

        herding_score = 0

        for date_key, day_decisions in same_day_decisions.items():

            if len(day_decisions) > 1:

                actions = [d.action for d in day_decisions]

                same_action_ratio = max(actions.count(a) for a in set(actions)) / len(actions)

                herding_score += same_action_ratio

        

        return herding_score / len(same_day_decisions) if same_day_decisions else 0



class PatternRecognizer:

    """模式识别器"""

    

    def __init__(self):

        self.patterns: List[DecisionPattern] = []

    

    def identify_success_patterns(self,

                                 decisions: List[DecisionRecord],

                                 performances: Dict[str, PerformanceResult]) -> List[DecisionPattern]:

        """识别成功模式"""

        successful = []

        

        for decision in decisions:

            if decision.decision_id not in performances:

                continue

            

            perf = performances[decision.decision_id]

            if perf.realized_pnl_pct > 0.1:

                successful.append((decision, perf))

        

        patterns = []

        

        regime_groups = {}

        for decision, perf in successful:

            regime = decision.market_context.market_regime

            if regime not in regime_groups:

                regime_groups[regime] = []

            regime_groups[regime].append((decision, perf))

        

        for regime, group in regime_groups.items():

            if len(group) >= 3:

                avg_return = sum(p.realized_pnl_pct for _, p in group) / len(group)

                

                pattern = DecisionPattern(

                    pattern_id=f"PATTERN_SUCCESS_{regime}",

                    pattern_type='success',

                    conditions={'market_regime': regime},

                    outcome={'avg_return': avg_return},

                    frequency=len(group),

                    avg_return=avg_return

                )

                patterns.append(pattern)

        

        self.patterns.extend(patterns)

        return patterns

    

    def identify_failure_patterns(self,

                                 decisions: List[DecisionRecord],

                                 performances: Dict[str, PerformanceResult]) -> List[DecisionPattern]:

        """识别失败模式"""

        failed = []

        

        for decision in decisions:

            if decision.decision_id not in performances:

                continue

            

            perf = performances[decision.decision_id]

            if perf.realized_pnl_pct < -0.05:

                failed.append((decision, perf))

        

        patterns = []

        

        high_vol_failures = [

            (d, p) for d, p in failed

            if d.market_context.volatility_level > 0.3

        ]

        

        if len(high_vol_failures) >= 3:

            avg_loss = sum(p.realized_pnl_pct for _, p in high_vol_failures) / len(high_vol_failures)

            

            pattern = DecisionPattern(

                pattern_id="PATTERN_FAILURE_HIGH_VOL",

                pattern_type='failure',

                conditions={'volatility_level': '>0.3'},

                outcome={'avg_loss': avg_loss},

                frequency=len(high_vol_failures),

                avg_return=avg_loss

            )

            patterns.append(pattern)

        

        self.patterns.extend(patterns)

        return patterns

    

    def generate_improvement_suggestions(self,

                                        patterns: List[DecisionPattern]) -> List[str]:

        """生成改进建议"""

        suggestions = []

        

        success_patterns = [p for p in patterns if p.pattern_type == 'success']

        failure_patterns = [p for p in patterns if p.pattern_type == 'failure']

        

        for pattern in success_patterns:

            suggestions.append(

                f"在{pattern.conditions}条件下，历史成功率较高，可增加此类决策权重"

            )

        

        for pattern in failure_patterns:

            suggestions.append(

                f"在{pattern.conditions}条件下，历史失败率较高，建议减少此类决策"

            )

        

        return suggestions

```



### 2.4 决策复盘层



```python

@dataclass

class ReviewReport:

    """复盘报告"""

    report_id: str

    report_type: str           # 'weekly', 'monthly', 'quarterly', 'event'

    period_start: date

    period_end: date

    generated_at: datetime

    

    decision_summary: Dict

    performance_summary: Dict

    quality_analysis: Dict

    patterns_identified: List[Dict]

    improvement_suggestions: List[str]

    lessons_learned: List[str]



@dataclass

class Experience:

    """经验记录"""

    experience_id: str

    category: str              # 'success', 'failure', 'insight'

    title: str

    description: str

    context: Dict

    applicable_conditions: Dict

    created_at: datetime = field(default_factory=datetime.now)

    usage_count: int = 0



class ReviewReportGenerator:

    """复盘报告生成器"""

    

    def __init__(self):

        self.reports: List[ReviewReport] = []

        self.report_counter = 0

    

    def generate_weekly_review(self,

                              decisions: List[DecisionRecord],

                              performances: Dict[str, PerformanceResult],

                              quality_metrics: DecisionQualityMetrics,

                              patterns: List[DecisionPattern]) -> ReviewReport:

        """生成周度复盘报告"""

        self.report_counter += 1

        

        decision_summary = {

            'total': len(decisions),

            'by_type': {},

            'by_strategy': {}

        }

        

        for d in decisions:

            type_key = d.decision_type.value

            decision_summary['by_type'][type_key] = decision_summary['by_type'].get(type_key, 0) + 1

            

            strategy_key = d.strategy_id

            decision_summary['by_strategy'][strategy_key] = decision_summary['by_strategy'].get(strategy_key, 0) + 1

        

        performance_summary = {

            'total_pnl': sum(p.realized_pnl for p in performances.values()),

            'win_rate': sum(1 for p in performances.values() if p.realized_pnl > 0) / len(performances) if performances else 0,

            'avg_return': sum(p.realized_pnl_pct for p in performances.values()) / len(performances) if performances else 0

        }

        

        quality_analysis = {

            'accuracy_rate': quality_metrics.accuracy_rate,

            'consistency_score': quality_metrics.consistency_score,

            'biases': quality_metrics.bias_analysis

        }

        

        patterns_identified = [

            {

                'type': p.pattern_type,

                'conditions': p.conditions,

                'avg_return': p.avg_return,

                'frequency': p.frequency

            }

            for p in patterns

        ]

        

        improvement_suggestions = self._generate_suggestions(quality_metrics, patterns)

        lessons_learned = self._extract_lessons(decisions, performances)

        

        report = ReviewReport(

            report_id=f"REVIEW_{self.report_counter:06d}",

            report_type='weekly',

            period_start=date.today(),

            period_end=date.today(),

            generated_at=datetime.now(),

            decision_summary=decision_summary,

            performance_summary=performance_summary,

            quality_analysis=quality_analysis,

            patterns_identified=patterns_identified,

            improvement_suggestions=improvement_suggestions,

            lessons_learned=lessons_learned

        )

        

        self.reports.append(report)

        return report

    

    def _generate_suggestions(self,

                             quality_metrics: DecisionQualityMetrics,

                             patterns: List[DecisionPattern]) -> List[str]:

        """生成改进建议"""

        suggestions = []

        

        if quality_metrics.accuracy_rate < 0.5:

            suggestions.append("决策准确率较低，建议审查决策逻辑和信号质量")

        

        if quality_metrics.consistency_score < 0.7:

            suggestions.append("决策一致性较低，建议标准化决策流程")

        

        for bias_type, bias_value in quality_metrics.bias_analysis.items():

            if abs(bias_value) > 0.3:

                suggestions.append(f"检测到{bias_type}偏差({bias_value:.2f})，建议针对性改进")

        

        return suggestions

    

    def _extract_lessons(self,

                        decisions: List[DecisionRecord],

                        performances: Dict[str, PerformanceResult]) -> List[str]:

        """提取经验教训"""

        lessons = []

        

        big_wins = [

            (d, p) for d in decisions

            if d.decision_id in performances

            for p in [performances[d.decision_id]]

            if p.realized_pnl_pct > 0.15

        ]

        

        for decision, perf in big_wins[:3]:

            lessons.append(

                f"成功案例：{decision.asset_code}在{decision.market_context.market_regime}环境下"

                f"获得{perf.realized_pnl_pct:.2%}收益"

            )

        

        big_losses = [

            (d, p) for d in decisions

            if d.decision_id in performances

            for p in [performances[d.decision_id]]

            if p.realized_pnl_pct < -0.10

        ]

        

        for decision, perf in big_losses[:3]:

            lessons.append(

                f"失败教训：{decision.asset_code}在{decision.market_context.market_regime}环境下"

                f"亏损{perf.realized_pnl_pct:.2%}，需注意类似情况"

            )

        

        return lessons



class ExperienceLibrary:

    """经验库管理"""

    

    def __init__(self):

        self.experiences: List[Experience] = []

        self.experience_counter = 0

        self.category_index: Dict[str, List[int]] = {}

    

    def add_experience(self,

                      category: str,

                      title: str,

                      description: str,

                      context: Dict,

                      applicable_conditions: Dict) -> Experience:

        """添加经验"""

        self.experience_counter += 1

        

        experience = Experience(

            experience_id=f"EXP_{self.experience_counter:06d}",

            category=category,

            title=title,

            description=description,

            context=context,

            applicable_conditions=applicable_conditions

        )

        

        self.experiences.append(experience)

        

        if category not in self.category_index:

            self.category_index[category] = []

        self.category_index[category].append(len(self.experiences) - 1)

        

        return experience

    

    def search_by_conditions(self,

                            current_conditions: Dict) -> List[Experience]:

        """按条件检索经验"""

        relevant = []

        

        for exp in self.experiences:

            match_score = self._calculate_match_score(

                current_conditions, 

                exp.applicable_conditions

            )

            

            if match_score > 0.5:

                relevant.append((exp, match_score))

        

        relevant.sort(key=lambda x: x[1], reverse=True)

        return [exp for exp, _ in relevant[:10]]

    

    def _calculate_match_score(self,

                              conditions1: Dict,

                              conditions2: Dict) -> float:

        """计算条件匹配度"""

        if not conditions1 or not conditions2:

            return 0

        

        common_keys = set(conditions1.keys()) & set(conditions2.keys())

        if not common_keys:

            return 0

        

        matches = sum(

            1 for k in common_keys

            if conditions1[k] == conditions2[k]

        )

        

        return matches / len(common_keys)

    

    def increment_usage(self, experience_id: str):

        """增加使用计数"""

        for exp in self.experiences:

            if exp.experience_id == experience_id:

                exp.usage_count += 1

                break

```



### 2.5 合规报告层



```python

@dataclass

class AuditLog:

    """审计日志"""

    log_id: str

    log_type: str

    timestamp: datetime

    user_id: str

    action: str

    resource: str

    details: Dict

    ip_address: str = ""

    session_id: str = ""

    hash: str = ""



@dataclass

class ComplianceReport:

    """合规报告"""

    report_id: str

    report_type: str

    period_start: date

    period_end: date

    generated_at: datetime

    total_decisions: int

    total_trades: int

    compliance_status: str

    violations: List[Dict]

    summary: Dict



class AuditLogManager:

    """审计日志管理"""

    

    def __init__(self):

        self.logs: List[AuditLog] = []

        self.log_counter = 0

    

    def log_decision(self,

                    decision: DecisionRecord,

                    user_id: str = "system"):

        """记录决策日志"""

        self.log_counter += 1

        

        log = AuditLog(

            log_id=f"LOG_{self.log_counter:08d}",

            log_type='decision',

            timestamp=datetime.now(),

            user_id=user_id,

            action=decision.action,

            resource=decision.asset_code,

            details={

                'decision_id': decision.decision_id,

                'strategy_id': decision.strategy_id,

                'target_weight': decision.target_weight,

                'confidence': decision.confidence

            }

        )

        

        log.hash = self._compute_hash(log)

        self.logs.append(log)

    

    def log_trade(self,

                 trade_data: Dict,

                 user_id: str = "system"):

        """记录交易日志"""

        self.log_counter += 1

        

        log = AuditLog(

            log_id=f"LOG_{self.log_counter:08d}",

            log_type='trade',

            timestamp=datetime.now(),

            user_id=user_id,

            action=trade_data.get('action'),

            resource=trade_data.get('stock_code'),

            details=trade_data

        )

        

        log.hash = self._compute_hash(log)

        self.logs.append(log)

    

    def _compute_hash(self, log: AuditLog) -> str:

        """计算日志哈希"""

        data = json.dumps({

            'log_id': log.log_id,

            'timestamp': log.timestamp.isoformat(),

            'action': log.action,

            'resource': log.resource

        }, sort_keys=True)

        

        return hashlib.sha256(data.encode()).hexdigest()

    

    def verify_integrity(self) -> bool:

        """验证日志完整性"""

        for log in self.logs:

            expected_hash = self._compute_hash(log)

            if log.hash != expected_hash:

                return False

        return True

    

    def query_logs(self,

                  log_type: str = None,

                  start_date: date = None,

                  end_date: date = None,

                  resource: str = None) -> List[AuditLog]:

        """查询日志"""

        results = self.logs

        

        if log_type:

            results = [l for l in results if l.log_type == log_type]

        

        if start_date:

            results = [l for l in results if l.timestamp.date() >= start_date]

        

        if end_date:

            results = [l for l in results if l.timestamp.date() <= end_date]

        

        if resource:

            results = [l for l in results if l.resource == resource]

        

        return results

    

    def export_logs(self,

                   start_date: date,

                   end_date: date,

                   format: str = 'json') -> str:

        """导出日志"""

        logs = self.query_logs(start_date=start_date, end_date=end_date)

        

        if format == 'json':

            return json.dumps([

                {

                    'log_id': l.log_id,

                    'log_type': l.log_type,

                    'timestamp': l.timestamp.isoformat(),

                    'action': l.action,

                    'resource': l.resource,

                    'details': l.details

                }

                for l in logs

            ], indent=2)

        

        return ""



class ComplianceReportGenerator:

    """合规报告生成器"""

    

    def __init__(self):

        self.reports: List[ComplianceReport] = []

        self.report_counter = 0

    

    def generate_monthly_report(self,

                               decisions: List[DecisionRecord],

                               audit_logs: List[AuditLog],

                               violations: List[Dict]) -> ComplianceReport:

        """生成月度合规报告"""

        self.report_counter += 1

        

        total_decisions = len(decisions)

        total_trades = len([l for l in audit_logs if l.log_type == 'trade'])

        

        compliance_status = 'compliant' if len(violations) == 0 else 'non_compliant'

        

        summary = {

            'decision_count': total_decisions,

            'trade_count': total_trades,

            'violation_count': len(violations),

            'compliance_rate': 1 - (len(violations) / max(total_decisions, 1))

        }

        

        report = ComplianceReport(

            report_id=f"COMPLIANCE_{self.report_counter:06d}",

            report_type='monthly',

            period_start=date.today(),

            period_end=date.today(),

            generated_at=datetime.now(),

            total_decisions=total_decisions,

            total_trades=total_trades,

            compliance_status=compliance_status,

            violations=violations,

            summary=summary

        )

        

        self.reports.append(report)

        return report

```



```
```---
```



## 三、实施路径



### Phase 1: 核心记录功能（1周）



| 任务 | 预计时间 | 交付物 |

|------|---------|--------|

| 决策捕获器 | 2天 | DecisionCapture |

| 决策存储器 | 1天 | DecisionStorage |

| 执行追踪器 | 2天 | ExecutionTracker |



### Phase 2: 分析与复盘（1周）



| 任务 | 预计时间 | 交付物 |

|------|---------|--------|

| 绩效追踪器 | 1天 | PerformanceTracker |

| 决策质量分析 | 2天 | DecisionQualityAnalyzer |

| 模式识别 | 1天 | PatternRecognizer |

| 复盘报告生成 | 1天 | ReviewReportGenerator |



### Phase 3: 合规与经验库（3天）



| 任务 | 预计时间 | 交付物 |

|------|---------|--------|

| 审计日志管理 | 1天 | AuditLogManager |

| 合规报告生成 | 1天 | ComplianceReportGenerator |

| 经验库管理 | 1天 | ExperienceLibrary |



```
```---
```



## 四、相关文档



| 文档 | 说明 |

|------|------|

| BLUEPRINT.md | Layer 11主蓝图 |

| IPS_MANAGEMENT_BLUEPRINT.md | 投资政策声明管理 |

| PERFORMANCE_ATTRIBUTION_BLUEPRINT.md | 业绩归因系统 |



```
```---
```



**版本**: v1.0 | **更新**: 2026-04-06 | **状态**: ✅ 活跃

```
```---
```



## 1. 文档治理



### 1.1 System_Manifest.md索引



```markdown

#### Layer 0: 系统架构

##### 0.001. Decision Audit

- **模块ID**: DECISION_AUDIT_001

- **蓝图文档**: DECISION_AUDIT_BLUEPRINT.md

- **技术规格书**: 待创建

- **职责**: Layer 11.21 - 投资决策审计系统

- **状态**: Active

```



### 1.2 模块职责边界



| 模块 | 职责 | 边界 |

|------|------|------|

| **Decision Audit** | Layer 11.21 - 投资决策审计系统 | **核心模块** |



### 1.3 版本管理



| 版本 | 日期 | 变更内容 | 变更人 |

|------|------|----------|--------|

| v1.0.0 | 2026-04-06 | 初始版本创建 | 首席蓝图架构师 |



```
```---
```



**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-06 | **状态**: Active

