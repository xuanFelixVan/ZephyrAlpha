---
module_id: SCENARIO_ANALYZER_001
version: 1.0.0
spec_version: 1.0
status: Active
parent_doc: ../ARCHITECTURE.md
last_updated: 2026-04-02
created_date: 2026-04-02
layer: Layer 7 (贯穿支撑层) | 业务架构: 三级时间框架融合架构
index: L7.RPT.SCE.001
estimated_hours: 40
review_status: Approved
reviewer: 首席技术评审官
review_date: 2026-04-02
owner: 首席技术评审官
standard_type: 专业量化机构技术规格书
applicable_scope: Layer 7 AI报告层 | 业务架构: 三级时间框架融合架构
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 进行中
reference_models: ["Bridgewater Scenario Analysis", "Renaissance Stress Testing"]
---

# ScenarioAnalyzer情景分析器技术规格书 v1.0

> 清风量化系统 v5.2 - ScenarioAnalyzer情景分析器详细技术设计
> **模块ID**: `SCENARIO_ANALYZER_001`
> **索引**: `L7.RPT.SCE.001`
> **开发时间**: 40h
> **核心定位**: 专业量化机构级情景分析器，对标桥水基金情景分析体系

---

## 1. 概述

### 1.1 设计背景与业务目标

**业务需求**：
- 当前系统完全缺失情景分析能力，无法评估极端市场条件下的风险敞口
- 专业量化机构（桥水、文艺复兴）均具备完整的情景分析和压力测试体系
- 监管机构要求量化基金必须进行定期压力测试

**技术痛点**：
- 无法模拟2008金融危机、COVID-19等极端事件的影响
- 无法制定应急预案和风险对冲策略
- 风险管理存在重大盲点

**预期价值**：
- 建立完整的情景分析体系，覆盖5种预设情景 + 自定义情景
- 提供压力测试能力，评估极端市场条件下的组合表现
- 为风险管理和投资决策提供科学依据

### 1.2 技术定位与架构层归属

- **Layer定位**: Layer 7 - AI报告层 (符合ARCHITECTURE.md定义)
- **模块类别**: 核心风险分析模块
- **架构角色**: Layer 7情景分析核心，为风险管理提供情景模拟支持

### 1.3 版本信息与变更记录

| 版本 | 日期 | 作者 | 变更说明 | 状态 |
|------|------|------|----------|------|
| v1.0 | 2026-04-02 | 首席技术评审官 | 初始版本 | Active |

---

## 2. 详细架构设计

### 2.1 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    Layer 7: AI报告层                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │        ScenarioAnalyzer (情景分析器主模块)            │  │
│  │  - 情景定义与管理                                      │  │
│  │  - 情景模拟引擎                                        │  │
│  │  - 影响评估与报告                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          核心组件                                      │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │ScenarioLib  │ │ImpactEngine │ │ReportGener  │  │  │
│  │  │情景库管理    │  │影响评估引擎 │  │报告生成器   │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │MarketShock │ │AssetImpact  │ │RiskMetrics  │  │  │
│  │  │市场冲击模型 │  │资产影响模型 │  │风险指标计算 │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          预设情景库                                    │  │
│  │  - 2008金融危机 (financial_crisis)                    │  │
│  │  - COVID-19冲击 (covid_crash)                         │  │
│  │  - 加息周期 (rate_hike)                               │  │
│  │  - 贸易战 (trade_war)                                 │  │
│  │  - 流动性危机 (liquidity_crisis)                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Layer定位详细说明

- **Layer归属**: Layer 7 - AI报告层
- **职责范围**: 情景定义、情景模拟、影响评估、报告生成
- **上下层接口**: 
  - 上层依赖: Layer 6 PortfolioOptimizer (提供组合数据)
  - 下层依赖: Layer 8 人机交互层 (接收情景分析报告)

### 2.3 模块职责与边界定义

- **核心职责**: 情景分析、压力测试、影响评估、报告生成
- **职责边界**: 
  - ✅ 本模块负责: 情景定义、情景模拟、影响评估、报告生成
  - ❌ 本模块不负责: 实时风险监控、交易执行、组合优化
- **接口契约**: 提供统一的Python API接口

### 2.4 依赖关系与集成点

| 依赖模块 | 依赖类型 | 接口方式 | 版本要求 | 备注 |
|----------|----------|----------|----------|------|
| pandas | 强依赖 | Python库 | >=2.0.0 | 数据处理 |
| numpy | 强依赖 | Python库 | >=1.24.0 | 数值计算 |
| scipy | 强依赖 | Python库 | >=1.10.0 | 统计计算 |
| matplotlib | 强依赖 | Python库 | >=3.7.0 | 可视化 |
| empyrical | 强依赖 | Python库 | >=0.5.5 | 绩效指标 |

---

## 3. 接口定义

### 3.1 API接口规范

#### 3.1.1 主接口类

```python
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import numpy as np
import pandas as pd


class ScenarioType(Enum):
    """情景类型枚举"""
    FINANCIAL_CRISIS = "financial_crisis"
    COVID_CRASH = "covid_crash"
    RATE_HIKE = "rate_hike"
    TRADE_WAR = "trade_war"
    LIQUIDITY_CRISIS = "liquidity_crisis"
    CUSTOM = "custom"


@dataclass
class MarketShock:
    """市场冲击参数"""
    equity_shock: float
    bond_shock: float
    commodity_shock: float
    currency_shock: float
    volatility_spike: float
    liquidity_drop: float


@dataclass
class AssetImpact:
    """资产影响结果"""
    asset_id: str
    asset_name: str
    original_value: float
    shocked_value: float
    impact_pct: float
    impact_amount: float


@dataclass
class ScenarioResult:
    """情景分析结果"""
    scenario_name: str
    scenario_type: ScenarioType
    shock_params: MarketShock
    asset_impacts: List[AssetImpact]
    portfolio_impact: float
    risk_metrics: Dict[str, float]
    recommendations: List[str]


class ScenarioAnalyzer:
    """情景分析器主类"""
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化情景分析器
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        self.scenario_library = self._load_scenario_library()
    
    def analyze_scenario(
        self,
        portfolio: pd.DataFrame,
        scenario_type: ScenarioType,
        custom_shock: Optional[MarketShock] = None
    ) -> ScenarioResult:
        """分析特定情景下的组合表现
        
        Args:
            portfolio: 投资组合数据 (columns: asset_id, asset_name, weight, value)
            scenario_type: 情景类型
            custom_shock: 自定义冲击参数 (仅用于custom类型)
            
        Returns:
            情景分析结果
        """
        pass
    
    def analyze_multiple_scenarios(
        self,
        portfolio: pd.DataFrame,
        scenario_types: List[ScenarioType]
    ) -> Dict[str, ScenarioResult]:
        """分析多个情景下的组合表现
        
        Args:
            portfolio: 投资组合数据
            scenario_types: 情景类型列表
            
        Returns:
            多个情景的分析结果字典
        """
        pass
    
    def generate_scenario_report(
        self,
        results: Dict[str, ScenarioResult],
        output_format: str = "markdown"
    ) -> str:
        """生成情景分析报告
        
        Args:
            results: 情景分析结果
            output_format: 输出格式 (markdown/html/pdf)
            
        Returns:
            报告内容
        """
        pass
```

### 3.2 数据格式与协议定义

#### 3.2.1 投资组合数据格式

```json
{
  "portfolio": [
    {
      "asset_id": "600519.SH",
      "asset_name": "贵州茅台",
      "asset_type": "equity",
      "weight": 0.08,
      "value": 800000,
      "sector": "食品饮料",
      "beta": 1.2
    }
  ],
  "total_value": 10000000,
  "benchmark": "000300.SH"
}
```

#### 3.2.2 情景定义格式

```json
{
  "scenario_name": "2008金融危机",
  "scenario_type": "financial_crisis",
  "description": "2008年全球金融危机情景模拟",
  "shock_params": {
    "equity_shock": -0.45,
    "bond_shock": -0.05,
    "commodity_shock": -0.30,
    "currency_shock": 0.10,
    "volatility_spike": 3.0,
    "liquidity_drop": 0.60
  },
  "duration_days": 180,
  "recovery_days": 720
}
```

### 3.3 性能指标与SLA要求

| 指标 | 目标值 | 测量方法 | 备注 |
|------|--------|----------|------|
| **单情景分析时间** | ≤5秒 | 端到端延迟 | 100资产组合 |
| **多情景分析时间** | ≤30秒 | 并行处理 | 5个预设情景 |
| **报告生成时间** | ≤10秒 | Markdown输出 | 完整报告 |
| **内存占用** | ≤500MB | 峰值内存 | 1000资产组合 |

### 3.4 安全与认证机制

- **数据安全**: 情景分析数据仅存储在本地，不上传云端
- **访问控制**: 基于角色的访问控制（RBAC）
- **审计日志**: 记录所有情景分析操作

---

## 4. 数据模型与存储

### 4.1 情景库数据结构

```python
SCENARIO_LIBRARY = {
    "financial_crisis": {
        "name": "2008金融危机",
        "description": "2008年全球金融危机情景模拟",
        "shock_params": MarketShock(
            equity_shock=-0.45,
            bond_shock=-0.05,
            commodity_shock=-0.30,
            currency_shock=0.10,
            volatility_spike=3.0,
            liquidity_drop=0.60
        ),
        "historical_reference": "2008-09-15 Lehman Brothers破产",
        "duration_days": 180,
        "recovery_days": 720
    },
    "covid_crash": {
        "name": "COVID-19冲击",
        "description": "2020年COVID-19疫情冲击情景模拟",
        "shock_params": MarketShock(
            equity_shock=-0.35,
            bond_shock=0.05,
            commodity_shock=-0.40,
            currency_shock=0.05,
            volatility_spike=4.0,
            liquidity_drop=0.50
        ),
        "historical_reference": "2020-03-09 全球股市熔断",
        "duration_days": 30,
        "recovery_days": 180
    },
    "rate_hike": {
        "name": "加息周期",
        "description": "美联储加息周期情景模拟",
        "shock_params": MarketShock(
            equity_shock=-0.15,
            bond_shock=-0.20,
            commodity_shock=-0.10,
            currency_shock=0.15,
            volatility_spike=1.5,
            liquidity_drop=0.20
        ),
        "historical_reference": "2022年美联储激进加息",
        "duration_days": 365,
        "recovery_days": 365
    },
    "trade_war": {
        "name": "贸易战",
        "description": "中美贸易摩擦情景模拟",
        "shock_params": MarketShock(
            equity_shock=-0.20,
            bond_shock=-0.05,
            commodity_shock=-0.25,
            currency_shock=-0.10,
            volatility_spike=2.0,
            liquidity_drop=0.30
        ),
        "historical_reference": "2018-03-22 特朗普签署贸易备忘录",
        "duration_days": 180,
        "recovery_days": 365
    },
    "liquidity_crisis": {
        "name": "流动性危机",
        "description": "市场流动性枯竭情景模拟",
        "shock_params": MarketShock(
            equity_shock=-0.25,
            bond_shock=-0.15,
            commodity_shock=-0.30,
            currency_shock=0.20,
            volatility_spike=5.0,
            liquidity_drop=0.80
        ),
        "historical_reference": "2020-03-23 美股流动性危机",
        "duration_days": 14,
        "recovery_days": 90
    }
}
```

### 4.2 数据流与ETL流程

```
投资组合数据 → 情景参数加载 → 市场冲击模拟 → 资产影响计算 → 风险指标计算 → 报告生成
```

---

## 5. 算法实现说明

### 5.1 核心算法原理

#### 5.1.1 市场冲击模拟算法

```python
def apply_market_shock(
    asset_value: float,
    asset_type: str,
    shock_params: MarketShock,
    beta: float = 1.0
) -> float:
    """应用市场冲击
    
    算法原理:
    1. 根据资产类型选择对应的冲击参数
    2. 考虑资产的Beta系数调整冲击幅度
    3. 添加随机扰动模拟真实市场情况
    
    Args:
        asset_value: 资产原始价值
        asset_type: 资产类型 (equity/bond/commodity/currency)
        shock_params: 市场冲击参数
        beta: 资产Beta系数
        
    Returns:
        冲击后的资产价值
    """
    shock_map = {
        'equity': shock_params.equity_shock,
        'bond': shock_params.bond_shock,
        'commodity': shock_params.commodity_shock,
        'currency': shock_params.currency_shock
    }
    
    base_shock = shock_map.get(asset_type, 0)
    adjusted_shock = base_shock * beta
    
    shocked_value = asset_value * (1 + adjusted_shock)
    
    return shocked_value
```

#### 5.1.2 风险指标计算算法

```python
def calculate_scenario_risk_metrics(
    portfolio: pd.DataFrame,
    shocked_portfolio: pd.DataFrame
) -> Dict[str, float]:
    """计算情景下的风险指标
    
    计算指标:
    1. 组合价值损失 (Portfolio Loss)
    2. 最大单资产损失 (Max Single Asset Loss)
    3. 流动性风险 (Liquidity Risk)
    4. 集中度风险 (Concentration Risk)
    
    Args:
        portfolio: 原始投资组合
        shocked_portfolio: 冲击后的投资组合
        
    Returns:
        风险指标字典
    """
    metrics = {}
    
    original_value = portfolio['value'].sum()
    shocked_value = shocked_portfolio['value'].sum()
    
    metrics['portfolio_loss'] = original_value - shocked_value
    metrics['portfolio_loss_pct'] = (original_value - shocked_value) / original_value
    
    asset_losses = portfolio['value'] - shocked_portfolio['value']
    metrics['max_single_asset_loss'] = asset_losses.max()
    metrics['max_single_asset_loss_pct'] = (asset_losses / portfolio['value']).max()
    
    metrics['liquidity_risk'] = shocked_portfolio['liquidity_drop'].mean()
    
    weights = shocked_portfolio['value'] / shocked_value
    metrics['concentration_risk'] = (weights ** 2).sum()
    
    return metrics
```

### 5.2 时间复杂度与空间复杂度分析

| 操作 | 时间复杂度 | 空间复杂度 | 说明 |
|------|------------|------------|------|
| 单情景分析 | O(n) | O(n) | n为资产数量 |
| 多情景分析 | O(n*m) | O(n*m) | m为情景数量 |
| 报告生成 | O(n) | O(1) | 线性扫描 |

---

## 6. 实施技术栈

### 6.1 语言框架

- **Python版本**: 3.10+
- **核心库**: pandas, numpy, scipy, matplotlib
- **绩效库**: empyrical
- **可视化**: matplotlib, seaborn

### 6.2 第三方依赖

```txt
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.10.0
matplotlib>=3.7.0
empyrical>=0.5.5
seaborn>=0.12.0
```

---

## 7. 测试策略

### 7.1 单元测试

```python
def test_apply_market_shock():
    """测试市场冲击算法"""
    shock_params = MarketShock(
        equity_shock=-0.45,
        bond_shock=-0.05,
        commodity_shock=-0.30,
        currency_shock=0.10,
        volatility_spike=3.0,
        liquidity_drop=0.60
    )
    
    asset_value = 1000000
    shocked_value = apply_market_shock(asset_value, 'equity', shock_params, beta=1.0)
    
    assert shocked_value == 550000  # 1000000 * (1 - 0.45)
```

### 7.2 集成测试

- 测试完整的情景分析流程
- 测试多情景并行分析
- 测试报告生成功能

### 7.3 性能测试

- 测试1000资产组合的分析性能
- 测试内存占用
- 测试并发处理能力

---

## 8. 风险与约束

### 8.1 技术风险

| 风险项 | 风险等级 | 缓解措施 |
|--------|----------|----------|
| 情景参数不准确 | P1 | 基于历史数据校准，定期更新 |
| 模型假设过于简化 | P2 | 引入更复杂的市场冲击模型 |
| 计算性能瓶颈 | P2 | 使用并行计算优化 |

### 8.2 实施约束

- 情景参数需要定期更新（季度）
- 需要历史市场数据支持
- 需要资产Beta系数数据

---

## 9. 验收标准

### 9.1 功能验收标准

- ✅ 支持5种预设情景分析
- ✅ 支持自定义情景分析
- ✅ 支持多情景并行分析
- ✅ 支持Markdown/HTML/PDF报告生成

### 9.2 性能验收标准

- ✅ 单情景分析时间 ≤5秒
- ✅ 多情景分析时间 ≤30秒
- ✅ 报告生成时间 ≤10秒

### 9.3 质量验收标准

- ✅ 单元测试覆盖率 ≥80%
- ✅ 集成测试通过率 100%
- ✅ 代码质量检查通过

---

## 10. 实施路线图

### 10.1 Phase 1: 核心功能开发（Week 1-2）

- Day 1-3: 情景库管理和参数定义
- Day 4-6: 市场冲击模拟引擎
- Day 7-10: 影响评估和风险指标计算

### 10.2 Phase 2: 报告生成（Week 3）

- Day 11-13: 报告生成器开发
- Day 14-15: 可视化图表生成

### 10.3 Phase 3: 测试与优化（Week 4）

- Day 16-18: 单元测试和集成测试
- Day 19-20: 性能优化和文档完善

---

**版本**: v1.0 | **更新**: 2026-04-02 | **状态**: ✅ 活跃
