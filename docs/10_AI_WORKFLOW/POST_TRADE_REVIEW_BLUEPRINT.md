---
module_id: POST_TRADE_REVIEW_BLUEPRINT
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
---

﻿---
module_id: POST_TRADE_REVIEW_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: 首席架构师
layer: Layer 7 (AI报告层)
standard_type: 专业机构级蓝图
applicable_scope: 交易复盘分析
compliance_level: 专业标准
parent_document: INDEX.md
implementation_status: 设计阶段
reference_models:
  - Professional Trading Review
  - Performance Attribution
  - Risk Analysis Framework
related_documents:
  - AI_WORKFLOW_LOGGER_BLUEPRINT.md
  - FULL_PROCESS_DATA_PERSISTENCE_BLUEPRINT.md
  - QUALITY_MONITORING_BLUEPRINT.md
responsibility:
  - 系统架构蓝图设计与实施指导与实施方案
---


## 文档职责说明

**本文档职责**: 复盘模块蓝图
- 回测复盘、实盘复盘、因子复盘、策略复盘、风险复盘

# 复盘模块蓝图

> **版本**: v1.0
> **创建日期**: 2026-04-02
> **实施周期**: 2
> **核心定位**: 交易决策的质量保障机
> **技术栈**: Pandas + NumPy + Matplotlib

---

## 一、概

### 1.1 蓝图定位

本文档是清风量化系统*复盘模块蓝图**,旨在实现:

- ✅ **回测复盘**: 分析回测结果,提取经验教训
- ✅ **实盘复盘**: 分析实盘交易,优化策略参数
- ✅ **因子复盘**: 分析因子表现,优化因子组合
- ✅ **策略复盘**: 分析策略表现,改进策略逻辑
- ✅ **风险复盘**: 分析风险事件,完善风控体系

### 1.2 核心价值

**对个人开发者的价值:
1. **经验积累**: 从历史交易中学习
2. **策略优化**: 基于数据优化策略
3. **风险规避**: 识别并规避风
4. **持续改进**: 建立持续改进机制

**对系统的价值:
1. **质量保障**: 提升策略质量
2. **风险控制**: 完善风控体系
3. **知识沉淀**: 积累交易知识
4. **AI训练**: 为AI提供训练数据

### 1.3 Layer定位

```
Layer 7: AI报告(AI Reporting Layer)
    ├── 回测复盘子系
    ├── 实盘复盘子系
    ├── 因子复盘子系
    ├── 策略复盘子系
    └── 风险复盘子系
```

**架构位置**: 位于Layer 7(AI报告,是交易决策质量保障的核心模块

---

## 二、架构设

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────
                   复盘模块架构                              
├─────────────────────────────────────────────────────────────
                                                            
 ┌─────────────────────────────────────────────────────  
          回测复盘(Backtest Review)                  
  ├─ 回测结果分析                                       
  ├─ 交易明细分析                                       
  ├─ 策略表现评估                                       
  └─ 优化建议生成                                       
 └─────────────────────────────────────────────────────  
                                                          
 ┌─────────────────────────────────────────────────────  
          实盘复盘(Live Trading Review)              
  ├─ 实盘交易分析                                       
  ├─ 滑点成本分析                                       
  ├─ 执行效率评估                                       
  └─ 实盘优化建议                                       
 └─────────────────────────────────────────────────────  
                                                          
 ┌─────────────────────────────────────────────────────  
          因子复盘(Factor Review)                    
  ├─ 因子表现分析                                       
  ├─ IC值趋势分                                      
  ├─ 因子衰减分析                                       
  └─ 因子优化建议                                       
 └─────────────────────────────────────────────────────  
                                                          
 ┌─────────────────────────────────────────────────────  
          策略复盘(Strategy Review)                  
  ├─ 策略表现分析                                       
  ├─ 参数敏感性分                                    
  ├─ 市场适应性分                                    
  └─ 策略改进建议                                       
 └─────────────────────────────────────────────────────  
                                                          
 ┌─────────────────────────────────────────────────────  
          风险复盘(Risk Review)                      
  ├─ 风险事件分析                                       
  ├─ 回撤分析                                           
  ├─ 风险因子识别                                       
  └─ 风控优化建议                                       
 └─────────────────────────────────────────────────────  
                                                            
└─────────────────────────────────────────────────────────────
```

### 2.2 数据流设

```
交易数据 数据清洗 指标计算 分析建模 报告生成 知识沉淀
                                                           
    └────────────────── 策略优化 ←───────────────────────────
```

**数据流说*:
1. **交易数据**: 从回测引擎或实盘系统获取交易数据
2. **数据清洗**: 清洗和标准化交易数据
3. **指标计算**: 计算各种绩效指标
4. **分析建模**: 分析交易模式,建立模型
5. **报告生成**: 生成复盘报告
6. **知识沉淀**: 提取经验教训,沉淀知识
7. **策略优化**: 基于复盘结果优化策略

### 2.3 核心组件设计

#### 组件1: BacktestReviewer (回测复盘

**职责**: 分析回测结果,提取经验教训

**输入**:
- backtest_result: 回测结果

**输出**:
- PostTradeReview对象

**接口**:
```python
def review_backtest(backtest_result: dict) -> PostTradeReview:
    """回测复盘"""
    pass
```

#### 组件2: LiveTradingReviewer (实盘复盘

**职责**: 分析实盘交易,优化策略参数

**输入**:
- live_trading_data: 实盘交易数据

**输出**:
- PostTradeReview对象

**接口**:
```python
def review_live_trading(live_trading_data: dict) -> PostTradeReview:
    """实盘复盘"""
    pass
```

#### 组件3: FactorReviewer (因子复盘

**职责**: 分析因子表现,优化因子组合

**输入**:
- factor_data: 因子数据

**输出**:
- FactorReview对象

**接口**:
```python
def review_factor(factor_data: dict) -> FactorReview:
    """因子复盘"""
    pass
```

#### 组件4: StrategyReviewer (策略复盘

**职责**: 分析策略表现,改进策略逻辑

**输入**:
- strategy_data: 策略数据

**输出**:
- StrategyReview对象

**接口**:
```python
def review_strategy(strategy_data: dict) -> StrategyReview:
    """策略复盘"""
    pass
```

#### 组件5: RiskReviewer (风险复盘

**职责**: 分析风险事件,完善风控体系

**输入**:
- risk_data: 风险数据

**输出**:
- RiskReview对象

**接口**:
```python
def review_risk(risk_data: dict) -> RiskReview:
    """风险复盘"""
    pass
```

---

## 三、数据模

### 3.1 复盘报告(post_trade_reviews)

| 字段| 类型 | 说明 | 示例 |
|--------|------|------|------|
| review_id | VARCHAR(64) | 复盘ID (主键) | review_20260402_001 |
| review_type | VARCHAR(32) | 复盘类型 | backtest_review |
| strategy_name | VARCHAR(128) | 策略名称 | momentum_strategy_v1 |
| period_start | DATE | 复盘开始日| 2026-03-01 |
| period_end | DATE | 复盘结束日期 | 2026-03-31 |
| total_trades | INTEGER | 总交易次| 150 |
| win_rate | FLOAT | 胜率 | 0.65 |
| sharpe_ratio | FLOAT | 夏普比率 | 1.85 |
| max_drawdown | FLOAT | 最大回| -0.12 |
| good_trades | TEXT | 好的交易 | "..." |
| bad_trades | TEXT | 差的交易 | "..." |
| lessons_learned | TEXT | 经验教训 | "..." |
| improvements | TEXT | 改进建议 | "..." |
| created_at | DATETIME | 创建时间 | 2026-04-02 18:00:00 |

**索引**:
- PRIMARY KEY: review_id
- INDEX: review_type
- INDEX: period_start

### 3.2 交易分析(trade_analysis)

| 字段| 类型 | 说明 | 示例 |
|--------|------|------|------|
| analysis_id | VARCHAR(64) | 分析ID (主键) | analysis_20260402_001 |
| review_id | VARCHAR(64) | 复盘ID (外键) | review_20260402_001 |
| trade_id | VARCHAR(64) | 交易ID | trade_20260301_001 |
| entry_time | DATETIME | 入场时间 | 2026-03-01 09:30:00 |
| exit_time | DATETIME | 出场时间 | 2026-03-01 15:00:00 |
| entry_price | FLOAT | 入场价格 | 10.50 |
| exit_price | FLOAT | 出场价格 | 10.80 |
| position_size | INTEGER | 持仓数量 | 1000 |
| pnl | FLOAT | 盈亏 | 300.0 |
| pnl_pct | FLOAT | 盈亏百分| 0.0286 |
| holding_period | INTEGER | 持仓时长(分钟) | 330 |
| trade_quality | VARCHAR(16) | 交易质量 | good |
| analysis_notes | TEXT | 分析备注 | "趋势明确,入场时机 |

**索引**:
- PRIMARY KEY: analysis_id
- FOREIGN KEY: review_id post_trade_reviews.review_id
- INDEX: trade_quality

### 3.3 经验教训(lessons_learned)

| 字段| 类型 | 说明 | 示例 |
|--------|------|------|------|
| lesson_id | VARCHAR(64) | 教训ID (主键) | lesson_20260402_001 |
| review_id | VARCHAR(64) | 复盘ID (外键) | review_20260402_001 |
| category | VARCHAR(32) | 类别 | entry_timing |
| lesson_type | VARCHAR(16) | 类型 | success |
| description | TEXT | 描述 | "趋势明确时入场效果更 |
| frequency | INTEGER | 出现频率 | 15 |
| impact_score | FLOAT | 影响评分 | 0.85 |
| created_at | DATETIME | 创建时间 | 2026-04-02 18:00:00 |

**索引**:
- PRIMARY KEY: lesson_id
- FOREIGN KEY: review_id post_trade_reviews.review_id
- INDEX: category

---

## 四、技术实

### 4.1 技术栈选择

| 技术组| 选择方案 | 理由 |
|---------|---------|------|
| **数据分析** | Pandas + NumPy | 专业数据分析|
| **可视* | Matplotlib + Seaborn | 专业可视化库 |
| **报告生成** | Markdown + Jinja2 | 灵活模板,易于定制 |
| **数据存储** | SQLite | 轻量易于管理 |
| **编程语言** | Python 3.10+ | 与现有系统一|

### 4.2 核心代码实现

#### 4.2.1 PostTradeReviewer

```python
import sqlite3
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import matplotlib.pyplot as plt
import seaborn as sns

class PostTradeReviewer:
    """复盘系统"""
    
    def __init__(self, db_path: str = "data/ai_workflow.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS post_trade_reviews (
                review_id TEXT PRIMARY KEY,
                review_type TEXT,
                strategy_name TEXT,
                period_start DATE,
                period_end DATE,
                total_trades INTEGER,
                win_rate REAL,
                sharpe_ratio REAL,
                max_drawdown REAL,
                good_trades TEXT,
                bad_trades TEXT,
                lessons_learned TEXT,
                improvements TEXT,
                created_at DATETIME
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trade_analysis (
                analysis_id TEXT PRIMARY KEY,
                review_id TEXT,
                trade_id TEXT,
                entry_time DATETIME,
                exit_time DATETIME,
                entry_price REAL,
                exit_price REAL,
                position_size INTEGER,
                pnl REAL,
                pnl_pct REAL,
                holding_period INTEGER,
                trade_quality TEXT,
                analysis_notes TEXT,
                FOREIGN KEY (review_id) REFERENCES post_trade_reviews(review_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lessons_learned (
                lesson_id TEXT PRIMARY KEY,
                review_id TEXT,
                category TEXT,
                lesson_type TEXT,
                description TEXT,
                frequency INTEGER,
                impact_score REAL,
                created_at DATETIME,
                FOREIGN KEY (review_id) REFERENCES post_trade_reviews(review_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def review_backtest(self, backtest_result: dict) -> dict:
        """回测复盘"""
        
        trades = backtest_result.get('trades', [])
        metrics = backtest_result.get('metrics', {})
        
        good_trades = self._analyze_good_trades(trades)
        bad_trades = self._analyze_bad_trades(trades)
        
        lessons = self._extract_lessons(good_trades, bad_trades)
        
        improvements = self._generate_improvements(lessons)
        
        review_id = f"review_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        review = {
            "review_id": review_id,
            "review_type": "backtest_review",
            "strategy_name": backtest_result.get('strategy_name', 'unknown'),
            "period_start": backtest_result.get('start_date', ''),
            "period_end": backtest_result.get('end_date', ''),
            "total_trades": len(trades),
            "win_rate": metrics.get('win_rate', 0),
            "sharpe_ratio": metrics.get('sharpe_ratio', 0),
            "max_drawdown": metrics.get('max_drawdown', 0),
            "good_trades": json.dumps(good_trades[:10], ensure_ascii=False),
            "bad_trades": json.dumps(bad_trades[:10], ensure_ascii=False),
            "lessons_learned": json.dumps(lessons, ensure_ascii=False),
            "improvements": json.dumps(improvements, ensure_ascii=False),
            "created_at": datetime.now()
        }
        
        self._save_review(review)
        
        return review
    
    def review_live_trading(self, live_trading_data: dict) -> dict:
        """实盘复盘"""
        
        trades = live_trading_data.get('trades', [])
        metrics = live_trading_data.get('metrics', {})
        
        slippage_analysis = self._analyze_slippage(trades)
        
        execution_analysis = self._analyze_execution(trades)
        
        good_trades = self._analyze_good_trades(trades)
        bad_trades = self._analyze_bad_trades(trades)
        
        lessons = self._extract_lessons(good_trades, bad_trades)
        
        improvements = self._generate_improvements(lessons)
        
        review_id = f"review_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        review = {
            "review_id": review_id,
            "review_type": "live_trading_review",
            "strategy_name": live_trading_data.get('strategy_name', 'unknown'),
            "period_start": live_trading_data.get('start_date', ''),
            "period_end": live_trading_data.get('end_date', ''),
            "total_trades": len(trades),
            "win_rate": metrics.get('win_rate', 0),
            "sharpe_ratio": metrics.get('sharpe_ratio', 0),
            "max_drawdown": metrics.get('max_drawdown', 0),
            "good_trades": json.dumps(good_trades[:10], ensure_ascii=False),
            "bad_trades": json.dumps(bad_trades[:10], ensure_ascii=False),
            "lessons_learned": json.dumps(lessons, ensure_ascii=False),
            "improvements": json.dumps(improvements, ensure_ascii=False),
            "created_at": datetime.now()
        }
        
        self._save_review(review)
        
        return review
    
    def generate_review_report(self, review: dict) -> str:
        """生成复盘报告"""
        
        report = f"""
# 交易复盘报告

**复盘ID**: {review['review_id']}
**复盘类型**: {review['review_type']}
**策略名称**: {review['strategy_name']}
**复盘周期**: {review['period_start']} {review['period_end']}

---

## 一、交易概

- **总交易次*: {review['total_trades']}
- **胜率**: {review['win_rate']:.2%}
- **夏普比率**: {review['sharpe_ratio']:.2f}
- **最大回*: {review['max_drawdown']:.2%}

---

## 二、好的交易分

{self._format_trades(json.loads(review['good_trades']))}

---

## 三、差的交易分

{self._format_trades(json.loads(review['bad_trades']))}

---

## 四、经验教

{self._format_lessons(json.loads(review['lessons_learned']))}

---

## 五、改进建

{self._format_improvements(json.loads(review['improvements']))}

---

**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        return report
    
    def _analyze_good_trades(self, trades: list) -> list:
        """分析好的交易"""
        good_trades = []
        
        for trade in trades:
            pnl_pct = trade.get('pnl_pct', 0)
            
            if pnl_pct > 0.02:
                good_trades.append({
                    "trade_id": trade.get('trade_id', ''),
                    "entry_time": trade.get('entry_time', ''),
                    "exit_time": trade.get('exit_time', ''),
                    "pnl_pct": pnl_pct,
                    "holding_period": trade.get('holding_period', 0),
                    "reason": "盈利超过2%"
                })
        
        return sorted(good_trades, key=lambda x: x['pnl_pct'], reverse=True)
    
    def _analyze_bad_trades(self, trades: list) -> list:
        """分析差的交易"""
        bad_trades = []
        
        for trade in trades:
            pnl_pct = trade.get('pnl_pct', 0)
            
            if pnl_pct < -0.01:
                bad_trades.append({
                    "trade_id": trade.get('trade_id', ''),
                    "entry_time": trade.get('entry_time', ''),
                    "exit_time": trade.get('exit_time', ''),
                    "pnl_pct": pnl_pct,
                    "holding_period": trade.get('holding_period', 0),
                    "reason": "亏损超过1%"
                })
        
        return sorted(bad_trades, key=lambda x: x['pnl_pct'])
    
    def _extract_lessons(self, good_trades: list, bad_trades: list) -> list:
        """提取经验教训"""
        lessons = []
        
        if good_trades:
            avg_holding_good = np.mean([t['holding_period'] for t in good_trades])
            lessons.append({
                "category": "holding_period",
                "lesson_type": "success",
                "description": f"盈利交易平均持仓时长: {avg_holding_good:.0f}分钟",
                "frequency": len(good_trades),
                "impact_score": 0.8
            })
        
        if bad_trades:
            avg_holding_bad = np.mean([t['holding_period'] for t in bad_trades])
            lessons.append({
                "category": "holding_period",
                "lesson_type": "failure",
                "description": f"亏损交易平均持仓时长: {avg_holding_bad:.0f}分钟",
                "frequency": len(bad_trades),
                "impact_score": 0.7
            })
        
        return lessons
    
    def _generate_improvements(self, lessons: list) -> list:
        """生成改进建议"""
        improvements = []
        
        for lesson in lessons:
            if lesson['category'] == 'holding_period' and lesson['lesson_type'] == 'success':
                improvements.append({
                    "category": "strategy_optimization",
                    "suggestion": "优化持仓时长,参考盈利交易的平均持仓时长",
                    "priority": "high"
                })
        
        return improvements
    
    def _analyze_slippage(self, trades: list) -> dict:
        """分析滑点"""
        return {
            "avg_slippage": 0.001,
            "max_slippage": 0.005
        }
    
    def _analyze_execution(self, trades: list) -> dict:
        """分析执行效率"""
        return {
            "avg_execution_time": 1.5,
            "success_rate": 0.98
        }
    
    def _save_review(self, review: dict):
        """保存复盘结果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO post_trade_reviews 
            (review_id, review_type, strategy_name, period_start, period_end, 
             total_trades, win_rate, sharpe_ratio, max_drawdown, good_trades, 
             bad_trades, lessons_learned, improvements, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            review['review_id'], review['review_type'], review['strategy_name'],
            review['period_start'], review['period_end'], review['total_trades'],
            review['win_rate'], review['sharpe_ratio'], review['max_drawdown'],
            review['good_trades'], review['bad_trades'], review['lessons_learned'],
            review['improvements'], review['created_at']
        ))
        
        conn.commit()
        conn.close()
    
    def _format_trades(self, trades: list) -> str:
        """格式化交易列""
        if not trades:
            return "暂无数据"
        
        formatted = []
        for trade in trades[:5]:
            formatted.append(
                f"- **交易ID**: {trade['trade_id']}\n"
                f"  - **盈亏**: {trade['pnl_pct']:.2%}\n"
                f"  - **持仓时长**: {trade['holding_period']}分钟\n"
                f"  - **原因**: {trade['reason']}"
            )
        
        return "\n\n".join(formatted)
    
    def _format_lessons(self, lessons: list) -> str:
        """格式化经验教""
        if not lessons:
            return "暂无数据"
        
        formatted = []
        for lesson in lessons:
            formatted.append(
                f"- **类别**: {lesson['category']}\n"
                f"  - **类型**: {lesson['lesson_type']}\n"
                f"  - **描述**: {lesson['description']}\n"
                f"  - **频率**: {lesson['frequency']}\n"
                f"  - **影响评分**: {lesson['impact_score']}"
            )
        
        return "\n\n".join(formatted)
    
    def _format_improvements(self, improvements: list) -> str:
        """格式化改进建""
        if not improvements:
            return "暂无数据"
        
        formatted = []
        for improvement in improvements:
            formatted.append(
                f"- **类别**: {improvement['category']}\n"
                f"  - **建议**: {improvement['suggestion']}\n"
                f"  - **优先*: {improvement['priority']}"
            )
        
        return "\n\n".join(formatted)
```

---

## 五、实施路径

### 5.1 Phase 1: 核心复盘功能 (Week 1)

**目标**: 实现回测复盘和实盘复盘功

**任务清单**:
- [ ] 设计数据库表结构
- [ ] 实现BacktestReviewer组件
- [ ] 实现LiveTradingReviewer组件
- [ ] 集成到现有系
- [ ] 编写单元测试

**验收标准**:
- 能够分析回测结果
- 能够分析实盘交易
- 能够生成复盘报告

### 5.2 Phase 2: 深度分析与优(Week 2)

**目标**: 实现因子复盘、策略复盘和风险复盘功能

**任务清单**:
- [ ] 实现FactorReviewer组件
- [ ] 实现StrategyReviewer组件
- [ ] 实现RiskReviewer组件
- [ ] 集成到现有系
- [ ] 编写集成测试

**验收标准**:
- 能够分析因子表现
- 能够分析策略表现
- 能够分析风险事件

---

## 六、文档治理

### 6.1 System_Manifest.md索引

```markdown
| 蓝图文档 | 路径 | 模块ID | 版本 | 状| 职责概要 |
|----------|------|--------|------|------|----------|
| [复盘模块蓝图](../10_AI_WORKFLOW/POST_TRADE_REVIEW_BLUEPRINT.md) | `docs/10_AI_WORKFLOW/POST_TRADE_REVIEW_BLUEPRINT.md` | POST_TRADE_REVIEW_001 | 1.0 | Active | 回测复盘、实盘复盘、因子复盘、策略复盘、风险复|
```

### 6.2 模块职责边界

**核心职责**:
- 回测复盘
- 实盘复盘
- 因子复盘
- 策略复盘
- 风险复盘

**非职*:
- AI工作记录 (由AI_WORKFLOW_LOGGER模块负责)
- AI工作汇报 (由AI_WORK_REPORTER模块负责)
- 数据持久(由FULL_PROCESS_DATA_PERSISTENCE模块负责)

### 6.3 版本管理策略

- **v1.0**: 初始版本,实现核心功能
- **v1.1**: 增强分析算法
- **v1.2**: 增加可视化功
- **v2.0**: 集成AI辅助分析

---

## 七、风险评

### 7.1 技术风

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| **数据质量* | | | 建立数据质量检查机|
| **分析结果主观** | | | 建立客观评估指标 |
| **报告内容空洞** | | | 建立报告模板,丰富内容来源 |

### 7.2 实施风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| **集成复杂度高** | | | 分阶段实逐步集成 |
| **用户不重* | | | 提供价值证逐步引导 |

---

## 八、相关文档

| 文档 | 说明 |
|------|------|
| [AI工作记录与优化模块蓝图](./AI_WORKFLOW_LOGGER_BLUEPRINT.md) | AI工作记录数据|
| [全流程数据保存机制蓝图](./FULL_PROCESS_DATA_PERSISTENCE_BLUEPRINT.md) | 数据持久化基础设施 |
| [质量监控蓝图](../09_AUDIT/QUALITY_MONITORING_BLUEPRINT.md) | 质量监控体系 |

---

**版本**: v1.0 | **更新**: 2026-04-02 | **状*: 活跃
