---
responsibility:
  - 组合绩效评估
  - 绩效指标计算
  - 绩效归因分析
  - 绩效报告生成

module_id: PORTFOLIO_PERFORMANCE_EVALUATION_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 实施团队
standard_type: 专业量化机构蓝图
applicable_scope: Layer 6 ç»åä¼åå±?
compliance_level: 专业标准
layer: Layer 5.2 (组合优化)
---


## 核心定位

负责投资组合业绩评估的设计与实现，基于业绩评估指标，提供组合业绩分析和评估报告，支持投资决策。

# 组合绩效评估模块蓝图
## 设计目标

### 主要目标

1. **功能完整性**: 确保PORTFOLIO PERFORMANCE EVALUATION功能完整，满足业务需求
2. **性能优化**: 提升系统性能，降低资源消耗
3. **可维护性**: 提高代码质量，便于后续维护
4. **可扩展性**: 支持功能扩展，适应业务变化

### 质量目标

- 代码覆盖率: ≥80%
- 性能指标: 满足设计要求
- 文档完整性: 100%


## 核心功能

### 功能清单

1. **数据管理**: 提供数据存储、查询、更新功能
2. **业务逻辑**: 实现核心业务逻辑处理
3. **接口服务**: 提供标准化的API接口
4. **监控告警**: 实时监控系统状态

### 功能特性

- 高可用性设计
- 自动故障恢复
- 灵活配置管理


## 实现方案

### 技术架构

采用PORTFOLIO PERFORMANCE EVALUATION化设计，分层架构实现。

### 关键技术

- 数据处理: 使用高效的数据处理框架
- 接口实现: RESTful API设计
- 性能优化: 缓存、异步处理

### 实施步骤

1. 需求分析与设计
2. 核心功能开发
3. 测试与优化
4. 部署与监控


## 核心定位

æå»ºæèµç»åç»©æè¯ä¼°çè®¾è®¡ä¸å®ç°ï¼åºäºå¤ç»´åº¦ç»©æå½å ææ¯ï¼è¯ä¼°æèµç»åæ¶çæ¥æºåé£é©æ´é²ï¼æ¯ææèµå³ç­ä¼åã?

---


> **核心职责**: 计算和评估投资组合的风险调整收益
> **职责边界**: 
> - â?æ¬ææ¡£è´è´£ï¼ç»©æè¯ä¼°ãé£é©è°æ´æ¶çãåºåå¯¹æ¯?
> - â?æ¬ææ¡£ä¸è´è´£ï¼å å­è®¡ç®ï¼ç±å å­æ¨¡åè´è´£ï¼


## 1. 概述

### 1.1 æ¨¡åå®ä½ä¸ç®æ ?

**Layerå®ä½**: Layer 6 - ç»åä¼åå±ï¼ç»©æè¯ä¼°æ¨¡åï¼?

**æ ¸å¿ä»·å?*:
- æä¾ä¸ä¸çº§ç»åç»©æè¯ä¼°ææ ?
- æ¯æå¤ç»´åº¦é£é©è°æ´æ¶çåæ?
- åºåå¯¹æ¯åç»©æå½å?
- 滚动绩效指标计算
- å¯è§åç»©ææ¥åçæ?

**ä¸å¡ä»·å?*:
- 量化评估策略表现
- 支持投资决策
- 满足合规报告要求
- æåæèµéæåº?

### 1.2 版本信息

| é¡¹ç® | å
å®¹ |
|------|------|
| **模块ID** | PORTFOLIO_PERFORMANCE_EVALUATION_001 |
| **版本** | v1.0.0 |
| **ç¶æ?* | Active |
| **创建日期** | 2026-04-06 |
| **æåæ´æ?* | 2026-04-06 |
| **å¼æºä¾èµ?* | pyfolio, QuantStats |
| **é¢è®¡å·¥æ¶** | 2-3å¤?|

### 1.3 ä¸ç°ææ¨¡åå
³ç³?

| å
³ç³»ç±»å | æ¨¡ååç§° | module_id | éææ¹å¼ |
|---------|---------|-----------|---------|
| **è¾å
¥ä¾èµ** | ç­ç¥å¼æ | STRAT_ENGINE_001 | è·åç­ç¥æ¶çç?|
| **è¾å
¥ä¾èµ** | åæµæ§è¡æ¨¡å | Backtraderéæ | è·ååæµç»æ |
| **è¾åºç®æ ** | AIæ¥åå±?| Layer 7 | æä¾ç»©ææ¥å |
| **协同工作** | 组合归因分析 | PORTFOLIO_ATTRIBUTION_001 | 绩效归因分析 |

---
## ð ç¸å
³ææ¡£

### 上游依赖

| 文档名称 | module_id | 依赖类型 | 说明 |
|---------|-----------|---------|------|
| [ç»åå½å åæèå¾](./PORTFOLIO_ATTRIBUTION_BLUEPRINT.md) | PORTFOLIO_ATTRIBUTION_001 | å¼ºä¾èµ?| æä¾å½å åæç»æ |
| [VaR/ESçæ§èå¾](./VAR_ES_MONITORING_BLUEPRINT.md) | VAR_ES_MONITORING_001 | å¼ºä¾èµ?| æä¾é£é©ææ æ°æ® |
| [ç»åä¼åå¼æéæèå¾](./PORTFOLIO_OPTIMIZER_INTEGRATION_BLUEPRINT.md) | PORTFOLIO_OPTIMIZER_INTEGRATION_001 | å¼ºä¾èµ?| æä¾ç»åæéæ°æ® |

### 下游依赖

| 文档名称 | module_id | 依赖类型 | 说明 |
|---------|-----------|---------|------|
| [SYSTEM_INTEGRATION_BLUEPRINT.md](./SYSTEM_INTEGRATION_BLUEPRINT.md) | SYSTEM_INTEGRATION_001 | å¼ºä¾èµ?| ç³»ç»éææ¥å |
| [MONITORING_DASHBOARD_ENHANCEMENT_BLUEPRINT.md](./MONITORING_DASHBOARD_ENHANCEMENT_BLUEPRINT.md) | MONITORING_DASHBOARD_ENHANCEMENT_001 | ä¸­ä¾èµ?| çæ§ä»ªè¡¨æ¿å¢å¼?|
| [QUALITY_REPORT_AUTOMATION_BLUEPRINT.md](./QUALITY_REPORT_AUTOMATION_BLUEPRINT.md) | QUALITY_REPORT_AUTOMATION_001 | ä¸­ä¾èµ?| è´¨éæ¥åèªå¨å?|

### ææ¯ä¾èµ?

| ææ¯ç»ä»?| çæ¬ | ç¨é?| ææ¡£ |
|---------|------|------|------|
| **pyfolio** | 0.9+ | 组合分析 | [GitHub](https://github.com/quantopian/pyfolio) |
| **QuantStats** | 0.0.62+ | 绩效分析 | [GitHub](https://github.com/ranaroussi/quantstats) |
| **NumPy** | 1.24+ | æ°å¼è®¡ç®?| [å®æ¹ææ¡£](https://numpy.org/) |
| **Pandas** | 2.0+ | 数据处理 | [官方文档](https://pandas.pydata.org/) |

### å¼ç¨å
³ç³»å?

```mermaid
graph LR
    A[组合归因分析] --> B[组合绩效评估]
    C[VaR/ES监控] --> B
    D[组合优化引擎] --> B
    
    B --> E[系统集成]
    B --> F[监控仪表板]
    B --> G[质量报告自动化]
    
    style B fill:#ff6b6b
    style A fill:#4ecdc4
    style C fill:#45b7d1
```

---

## 2. 架构设计

### 2.1 Layerå®ä½ä¸èè´£è¾¹ç?

**Layer 6 - ç»åä¼åå±æ¶æ?*:

```
Layer 6: ç»åä¼åå±?
├── 6.1 组合构建模块
â?  âââ ç»åä¼åå?(PORTFOLIO_OPTIMIZATION_001)
â?  âââ Black-Littermanæ¨¡å (BLACK_LITTERMAN_MODEL_001)
â?  âââ é£é©å¹³ä»·ç­ç¥ (RISK_PARITY_STRATEGY_001)
├── 6.2 约束求解模块
â?  âââ çº¦ææ±è§£å?(CONSTRAINT_SOLVER_001)
├── 6.3 风险预算模块
â?  âââ é£é©é¢ç®ç³»ç» (SIMPLIFIED_RISK_BUDGET_SYSTEM_001)
âââ 6.4 ç»©æè¯ä¼°æ¨¡å â?æ¬æ¨¡å?
â?  âââ ç»åç»©æè¯ä¼° (PORTFOLIO_PERFORMANCE_EVALUATION_001)
└── 6.5 归因分析模块
    └── 组合归因分析 (PORTFOLIO_ATTRIBUTION_001)
```

**职责边界**:
- â?**è´è´£**: ç»©æææ è®¡ç®ãåºåå¯¹æ¯ãå¯è§åæ¥å
- â?**ä¸è´è´?*: å½å åæï¼å½å åææ¨¡åè´è´£ï¼ãé£é©é¢ç®ï¼é£é©é¢ç®æ¨¡åè´è´£ï¼?

### 2.2 核心组件架构

```mermaid
graph TB
    subgraph "æ°æ®è¾å
¥"
        A[策略收益率] --> D[绩效评估引擎]
        B[基准收益率] --> D
        C[无风险利率] --> D
    end
    
    subgraph "pyfolio核心"
        D --> E[风险指标计算]
        E --> F[夏普比率]
        E --> G[最大回撤]
        E --> H[波动率]
        E --> I[Alpha/Beta]
    end
    
    subgraph "QuantStats扩展"
        D --> J[高级指标]
        J --> K[Sortino比率]
        J --> L[Calmar比率]
        J --> M[信息比率]
        J --> N[滚动指标]
    end
    
    subgraph "å¯è§åæ¥å?
        F --> O[绩效报告生成]
        G --> O
        H --> O
        I --> O
        K --> O
        L --> O
        M --> O
        N --> O
        O --> P[HTML报告]
        O --> Q[PDF报告]
        O --> R[交互式仪表板]
    end
```

### 2.3 æ°æ®æµè®¾è®?

**æ ¸å¿æ°æ®æµ?*:

```
ç­ç¥æ¶ççåºå?â?pyfolio/QuantStats â?ç»©æææ è®¡ç®
                                            â?
                                    基准对比分析
                                            â?
                                    滚动指标计算
                                            â?
                                    å¯è§åæ¥åçæ?
```

---

## 3. ææ¯å®ç?

### 3.1 pyfolio集成（核心）

**核心API**:

```python
import pyfolio as pf
import pandas as pd
import numpy as np

class PortfolioPerformanceEvaluator:
    """
    ç»åç»©æè¯ä¼°å?
    
    索引: PORTFOLIO_PERF_001-M01
    èè´£: åºäºpyfolioå®ç°ä¸ä¸çº§ç»©æè¯ä¼?
    è¾å
¥: ç­ç¥æ¶ççãåºåæ¶ççãæ é£é©å©ç
    输出: 绩效指标、风险指标、可视化报告
    """
    
    def __init__(self, risk_free_rate: float = 0.02):
        self.risk_free_rate = risk_free_rate
        
    def calculate_performance_metrics(
        self,
        returns: pd.Series,
        benchmark_returns: pd.Series = None
    ) -> dict:
        """
        计算绩效指标
        
        Args:
            returns: ç­ç¥æ¶ççåºå?
            benchmark_returns: åºåæ¶ççåºå?
            
        Returns:
            ç»©æææ å­å
¸
        """
        perf_stats = pf.timeseries.perf_stats(
            returns,
            factor_returns=benchmark_returns
        )
        
        return {
            'annual_return': perf_stats['Annual return'],
            'annual_volatility': perf_stats['Annual volatility'],
            'sharpe_ratio': perf_stats['Sharpe ratio'],
            'max_drawdown': perf_stats['Max drawdown'],
            'sortino_ratio': perf_stats['Sortino ratio'],
            'calmar_ratio': perf_stats['Calmar ratio'],
            'omega_ratio': perf_stats['Omega ratio']
        }
    
    def calculate_risk_metrics(
        self,
        returns: pd.Series
    ) -> dict:
        """
        计算风险指标
        
        Args:
            returns: ç­ç¥æ¶ççåºå?
            
        Returns:
            é£é©ææ å­å
¸
        """
        return {
            'volatility': pf.timeseries.annual_volatility(returns),
            'max_drawdown': pf.timeseries.max_drawdown(returns),
            'downside_risk': pf.timeseries.downside_risk(returns),
            'value_at_risk_95': np.percentile(returns, 5),
            'conditional_var_95': returns[returns < np.percentile(returns, 5)].mean()
        }
    
    def calculate_alpha_beta(
        self,
        returns: pd.Series,
        benchmark_returns: pd.Series
    ) -> dict:
        """
        计算Alpha和Beta
        
        Args:
            returns: ç­ç¥æ¶ççåºå?
            benchmark_returns: åºåæ¶ççåºå?
            
        Returns:
            AlphaåBetaå­å
¸
        """
        alpha, beta = pf.timeseries.alpha_beta(
            returns,
            benchmark_returns,
            risk_free=self.risk_free_rate
        )
        
        return {
            'alpha': alpha,
            'beta': beta,
            'information_ratio': pf.timeseries.information_ratio(
                returns,
                benchmark_returns
            )
        }
    
    def generate_tearsheet(
        self,
        returns: pd.Series,
        benchmark_returns: pd.Series = None,
        positions: pd.DataFrame = None,
        transactions: pd.DataFrame = None
    ):
        """
        çæå®æ´ç»©ææ¥åï¼Tearsheetï¼?
        
        Args:
            returns: ç­ç¥æ¶ççåºå?
            benchmark_returns: åºåæ¶ççåºå?
            positions: 持仓数据
            transactions: 交易数据
            
        Returns:
            å®æ´çç»©æåææ¥å?
        """
        pf.create_full_tear_sheet(
            returns,
            benchmark_rets=benchmark_returns,
            positions=positions,
            transactions=transactions
        )
```

### 3.2 QuantStats集成（扩展）

**核心API**:

```python
import quantstats as qs

class QuantStatsEvaluator:
    """
    QuantStatsç»©æè¯ä¼°å?
    
    索引: PORTFOLIO_PERF_001-M02
    èè´£: ä½¿ç¨QuantStatsæä¾æ©å±çç»©æè¯ä¼°åè?
    """
    
    def calculate_extended_metrics(
        self,
        returns: pd.Series,
        benchmark_returns: pd.Series = None
    ) -> dict:
        """
        计算扩展绩效指标
        
        Args:
            returns: ç­ç¥æ¶ççåºå?
            benchmark_returns: åºåæ¶ççåºå?
            
        Returns:
            æ©å±ç»©æææ å­å
¸
        """
        return {
            'sharpe': qs.stats.sharpe(returns),
            'sortino': qs.stats.sortino(returns),
            'calmar': qs.stats.calmar(returns),
            'max_drawdown': qs.stats.max_drawdown(returns),
            'volatility': qs.stats.volatility(returns),
            'win_rate': qs.stats.win_rate(returns),
            'profit_factor': qs.stats.profit_factor(returns),
            'expected_return': qs.stats.expected_return(returns),
            'kelly_criterion': qs.stats.kelly_criterion(returns)
        }
    
    def generate_html_report(
        self,
        returns: pd.Series,
        benchmark_returns: pd.Series = None,
        output_path: str = 'performance_report.html'
    ):
        """
        生成HTML绩效报告
        
        Args:
            returns: ç­ç¥æ¶ççåºå?
            benchmark_returns: åºåæ¶ççåºå?
            output_path: 输出文件路径
        """
        qs.reports.html(
            returns,
            benchmark=benchmark_returns,
            output=output_path,
            title='Portfolio Performance Report'
        )
```

### 3.3 滚动绩效指标

```python
def calculate_rolling_metrics(
    returns: pd.Series,
    window: int = 252
) -> pd.DataFrame:
    """
    计算滚动绩效指标
    
    Args:
        returns: ç­ç¥æ¶ççåºå?
        window: 滚动窗口（天数）
        
    Returns:
        滚动指标DataFrame
    """
    rolling_sharpe = returns.rolling(window).apply(
        lambda x: np.sqrt(252) * np.mean(x) / np.std(x)
    )
    
    rolling_volatility = returns.rolling(window).std() * np.sqrt(252)
    
    rolling_max_drawdown = returns.rolling(window).apply(
        lambda x: (x.cumsum().cummax() - x.cumsum()).max()
    )
    
    return pd.DataFrame({
        'rolling_sharpe': rolling_sharpe,
        'rolling_volatility': rolling_volatility,
        'rolling_max_drawdown': rolling_max_drawdown
    })
```

### 3.4 性能要求

| æ§è½ææ  | ç®æ å?| è¯´æ |
|---------|--------|------|
| **指标计算时间** | <500ms | 单次计算 |
| **报告生成时间** | <5s | 完整Tearsheet |
| **å
存占用** | <100MB | 单次分析 |
| **å¹¶åæ¯æ** | 10 QPS | æ¯æå¤ç­ç¥å¹¶è¡åæ?|

---

## 4. 数据模型

### 4.1 è¾å
¥æ°æ®ç»æ

```python
@dataclass
class PerformanceInput:
    """ç»©æè¯ä¼°è¾å
¥æ°æ®"""
    returns: pd.Series
    benchmark_returns: Optional[pd.Series] = None
    risk_free_rate: float = 0.02
    positions: Optional[pd.DataFrame] = None
    transactions: Optional[pd.DataFrame] = None
```

### 4.2 输出数据结构

```python
@dataclass
class PerformanceResult:
    """绩效评估结果"""
    performance_metrics: Dict[str, float]
    risk_metrics: Dict[str, float]
    alpha_beta: Optional[Dict[str, float]]
    rolling_metrics: pd.DataFrame
    tearsheet_path: Optional[str]
    timestamp: datetime
```

### 4.3 数据库表设计

```sql
CREATE TABLE IF NOT EXISTS performance_metrics (
    metric_id VARCHAR(50) PRIMARY KEY,
    strategy_id VARCHAR(50) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(20, 10),
    calculation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_strategy (strategy_id),
    INDEX idx_date (calculation_date)
);

CREATE TABLE IF NOT EXISTS performance_history (
    history_id VARCHAR(50) PRIMARY KEY,
    strategy_id VARCHAR(50) NOT NULL,
    metrics_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_strategy (strategy_id),
    INDEX idx_created (created_at)
);
```

---

## 5. 接口定义

### 5.1 API接口

```python
class PerformanceAPI:
    """绩效评估API接口"""
    
    @endpoint("/api/v1/performance/calculate")
    async def calculate_metrics(
        self,
        request: PerformanceRequest
    ) -> PerformanceResponse:
        """
        计算绩效指标
        
        Args:
            request: 绩效计算请求
            
        Returns:
            绩效指标结果
        """
        pass
    
    @endpoint("/api/v1/performance/tearsheet")
    async def generate_tearsheet(
        self,
        strategy_id: str,
        start_date: str,
        end_date: str
    ) -> TearsheetResponse:
        """
        生成完整绩效报告
        
        Args:
            strategy_id: 策略ID
            start_date: å¼å§æ¥æ?
            end_date: 结束日期
            
        Returns:
            绩效报告路径
        """
        pass
    
    @endpoint("/api/v1/performance/compare")
    async def compare_strategies(
        self,
        strategy_ids: List[str],
        start_date: str,
        end_date: str
    ) -> ComparisonResponse:
        """
        对比多个策略绩效
        
        Args:
            strategy_ids: 策略ID列表
            start_date: å¼å§æ¥æ?
            end_date: 结束日期
            
        Returns:
            策略对比结果
        """
        pass
```

---

## 6. 实施路径

### 6.1 Phase 1: æ ¸å¿åè½å®ç°ï¼?å¨ï¼

| ä»»å¡ | å·¥æ¶ | äº¤ä»ç?|
|------|------|--------|
| pyfolioéæ | 4h | éæä»£ç ãåå
æµè¯?|
| QuantStats集成 | 4h | 扩展功能 |
| 指标计算模块 | 4h | 计算模块 |
| 数据库表创建 | 2h | SQL脚本 |

### 6.2 Phase 2: åè½å¢å¼ºï¼?.5å¨ï¼

| ä»»å¡ | å·¥æ¶ | äº¤ä»ç?|
|------|------|--------|
| 滚动指标计算 | 4h | 滚动分析模块 |
| APIæ¥å£å¼å?| 4h | REST API |
| å¯è§åæ¥å?| 4h | HTMLæ¥åçæ |

### 6.3 Phase 3: 测试与文档（0.5周）

| ä»»å¡ | å·¥æ¶ | äº¤ä»ç?|
|------|------|--------|
| åå
æµè¯ | 4h | æµè¯ä»£ç  |
| 集成测试 | 4h | 测试报告 |
| 文档编写 | 4h | 用户手册、API文档 |

---

## 7. 文档治理

### 7.1 System_Manifest.md索引

**ç´¢å¼ä½ç½®**: Layer 6 - ç»åä¼åå±?- ç»©æè¯ä¼°æ¨¡å

### 7.2 模块职责边界

**ä¸ç»åå½å åæè¾¹ç?*:
- 绩效评估负责计算绩效指标
- 归因分析负责分解收益来源

**ä¸AIæ¥åå±è¾¹ç?*:
- 绩效评估负责生成绩效数据
- AI报告层负责生成自然语言报告

---

## 8. 风险评估

### 8.1 ææ¯é£é?

| é£é©é¡?| é£é©ç­çº§ | å½±åèå´ | ç¼è§£æªæ½ |
|--------|---------|---------|---------|
| pyfolioä¾èµå²çª | P2 | éæå¤±è´¥ | èæç¯å¢ãçæ¬éå®?|
| æ°æ®æ ¼å¼ä¸å
¼å®?| P1 | è®¡ç®éè¯¯ | æ°æ®éªè¯ãæ ¼å¼è½¬æ?|
| æ§è½ç¶é¢ | P2 | ååºæ
?| å¼æ­¥å¤çãç¼å­?|

### 8.2 实施风险

| é£é©é¡?| é£é©ç­çº§ | å½±åèå´ | ç¼è§£æªæ½ |
|--------|---------|---------|---------|
| å¼æºé¡¹ç®APIåæ´ | P2 | éæå¤±è´¥ | éå®çæ¬ãå®ææ´æ?|
| æ°æ®è´¨éé®é¢ | P1 | è®¡ç®éè¯¯ | æ°æ®æ¸
æ´ãå¼å¸¸æ£æµ?|

---

## 9. 质量保证

### 9.1 测试策略

| æµè¯ç±»å | è¦ççç®æ ?| æµè¯å·¥å
· |
|---------|-----------|---------|
| åå
æµè¯ | â?0% | pytest |
| éææµè¯ | â?0% | pytest + mock |
| æ§è½æµè¯ | å
³é®è·¯å¾ | pytest-benchmark |

### 9.2 验收标准

| éªæ¶é¡?| æ å | éªè¯æ¹æ³ |
|--------|------|---------|
| åè½å®æ´æ?| ææAPIæ­£å¸¸å·¥ä½ | åå
æµè¯ |
| 性能达标 | 指标计算<500ms | 性能测试 |
| æ¥åè´¨é | æ¥åæ¸
晰完整 | 人工审查 |

---

## 10. åèèµæ?

### 10.1 学术论文

1. Sharpe, W. F. (1966). "Mutual Fund Performance". Journal of Business.
2. Sortino, F. A., & Price, L. N. (1994). "Performance Measurement in a Downside Risk Framework". Journal of Investing.

### 10.2 å¼æºé¡¹ç®ææ¡?

1. pyfolio Documentation: https://pyfolio.ml4trading.io/
2. QuantStats Documentation: https://github.com/ranaroussi/quantstats
3. Quantopian Lectures: https://www.quantopian.com/lectures

### 10.3 ç¸å
³èå¾

- [组合归因分析蓝图](./PORTFOLIO_ATTRIBUTION_BLUEPRINT.md)
- [风险贡献分析蓝图](./RISK_CONTRIBUTION_ANALYSIS_BLUEPRINT.md)

---

**èå¾çæ¬**: v1.0.0 | **åå»ºæ¥æ**: 2026-04-06 | **ç¶æ?*: Active | **åè§ç?*: 100% â?

## 变更历史

| çæ¬ | æ¥æ | åæ´å
å®¹ | åæ´äº?|
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | åå§çæ¬åå»º | é¦å¸­èå¾æ¶æå¸?|
| v1.0.1 | 2026-04-06 | è¡¥å

YAMLå¤´é¨å­æ®µååæ´åå?| å®¡è®¡ç³»ç» |

---

**èå¾çæ¬**: v1.0.1 | **åå»ºæ¥æ**: 2026-04-06 | **ç¶æ?*: Active
