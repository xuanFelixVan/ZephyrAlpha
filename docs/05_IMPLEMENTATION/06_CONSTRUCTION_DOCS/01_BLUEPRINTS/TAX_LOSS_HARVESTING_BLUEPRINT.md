---
responsibility:
  - 税收优化
  - 税损收割
  - 税务筹划
  - 成本优化

module_id: TAX_LOSS_HARVESTING_001
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

# 税收优化（税损收割）蓝图

> **æ ¸å¿èè´£**: å®ç°ç¨ææ¶å²ç­ç¥ï¼ä¼åç¨åæ¶ç?
> **职责边界**: 
> - â?æ¬ææ¡£è´è´£ï¼ç¨æè¯å«ãæ¶å²ç­ç¥ãwash saleè§é¿
> - â?æ¬ææ¡£ä¸è´è´£ï¼å å­è®¡ç®ï¼ç±å å­æ¨¡åè´è´£ï¼


## 核心定位

è´è´£Tax Loss Harvestingçè®¾è®¡ãå®ç°åç»´æ¤ï¼æä¾æ ¸å¿åè½æ¯æï¼ç¡®ä¿ç³»ç»æ¨¡åçç¨³å®è¿è¡åé«ææ§è¡ã?

## 设计目标

### 主要目标

1. **功能完整性**: 确保TAX LOSS HARVESTING功能完整，满足业务需求
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

采用TAX LOSS HARVESTING化设计，分层架构实现。

### 关键技术

- 数据处理: 使用高效的数据处理框架
- 接口实现: RESTful API设计
- 性能优化: 缓存、异步处理

### 实施步骤

1. 需求分析与设计
2. 核心功能开发
3. 测试与优化
4. 部署与监控


## 1. 模块概述

### 1.1 核心职责

**单一职责**: 识别和执行税损收割机会，最大化税后收益

**职责边界**:
- â?è´è´£: æªå®ç°æçè®¡ç®ãæ´å®è§åæ£æµãç¨ææ¶å²æºä¼è¯å«ãæ¿ä»£è¯å¸éæ©
- â?ä¸è´è´? åºç¡ç»åä¼åï¼ç±MEAN_VARIANCE_OPTIMIZATIONè´è´£ï¼?
- â?ä¸è´è´? åå¹³è¡¡å³ç­ï¼ç±PORTFOLIO_REBALANCINGè´è´£ï¼?

### 1.2 适用场景

**ä¸ªäººæèµè
ä¸å±åè?*:
- 降低年度税负
- å»¶è¿èµæ¬å©å¾ç¨?
- 提高税后收益
- 符合税务合规

### 1.3 å¼æºä¾èµ?

| åºå | ç¨é?| è¯´æ |
|------|------|------|
| rebalancer | åè?| ç¨ææ¶å²é»è¾åè?|
| 自研核心 | 主要 | 针对中国/美国税法 |

---

## 2. 功能设计

### 2.1 核心功能

#### 2.1.1 æªå®ç°æçè®¡ç®?

```python
class UnrealizedGainLossCalculator:
    """
    未实现损益计算器
    """
    
    def calculate_unrealized_pnl(
        self,
        positions: Dict[str, float],
        cost_basis: Dict[str, float],
        current_prices: Dict[str, float]
    ) -> pd.DataFrame:
        """
        è®¡ç®æªå®ç°æç?
        
        参数:
            positions: 持仓数量
            cost_basis: 成本基础
            current_prices: 当前价格
            
        返回:
            æªå®ç°æçæç»?
        """
        pass
    
    def identify_harvest_candidates(
        self,
        unrealized_pnl: pd.DataFrame,
        min_loss_threshold: float = 1000.0
    ) -> List[Dict]:
        """
        è¯å«ç¨ææ¶å²åé?
        
        参数:
            unrealized_pnl: æªå®ç°æç?
            min_loss_threshold: æå°æå¤±éå?
            
        返回:
            åéåè¡?
        """
        pass
```

#### 2.1.2 æ´å®è§åæ£æµ?

```python
class WashSaleDetector:
    """
    洗售规则检测器
    
    ç¾å½: 30å¤©å
ä¸è½ä¹°å
¥ç¸åæå®è´¨ç¸åè¯å?
    ä¸­å½: æ æ´å®è§åéå?
    """
    
    def check_wash_sale(
        self,
        security: str,
        trade_date: datetime,
        lookback_days: int = 30,
        forward_days: int = 30
    ) -> bool:
        """
        æ£æ¥æ¯å¦è¿åæ´å®è§å?
        
        返回:
            True: 违反洗售规则
            False: 可以执行
        """
        pass
    
    def find_wash_sale_period(
        self,
        security: str,
        trade_date: datetime
    ) -> Tuple[datetime, datetime]:
        """
        æ¥æ¾æ´å®è§åç¦æ­¢æ?
        """
        pass
```

#### 2.1.3 替代证券选择

```python
class SubstituteSecuritySelector:
    """
    æ¿ä»£è¯å¸éæ©å?
    
    éæ©ä¸åè¯å¸é«åº¦ç¸å
³ä½ä¸è¿åæ´å®è§åçæ¿ä»£å
    """
    
    def find_substitutes(
        self,
        security: str,
        correlation_threshold: float = 0.9,
        exclude_list: List[str] = None
    ) -> List[Dict]:
        """
        查找替代证券
        
        参数:
            security: åè¯å?
            correlation_threshold: ç¸å
³æ§éå?
            exclude_list: æé¤åè¡¨ï¼æ´å®è§åç¸å
³ï¼
            
        返回:
            æ¿ä»£è¯å¸åè¡¨ï¼æç¸å
³æ§æåºï¼
        """
        pass
```

#### 2.1.4 税后收益优化

```python
class AfterTaxReturnOptimizer:
    """
    ç¨åæ¶çä¼åå?
    """
    
    def optimize_after_tax(
        self,
        expected_returns: np.ndarray,
        short_term_tax_rate: float = 0.35,
        long_term_tax_rate: float = 0.15,
        holding_periods: Dict[str, int] = None
    ) -> Dict:
        """
        税后收益优化
        
        参数:
            expected_returns: 税前预期收益
            short_term_tax_rate: 短期资本利得税率
            long_term_tax_rate: 长期资本利得税率
            holding_periods: æä»å¨æï¼å¤©ï¼?
            
        返回:
            税后优化结果
        """
        pass
    
    def calculate_tax_savings(
        self,
        harvest_amount: float,
        tax_rate: float
    ) -> float:
        """
        计算税收节省
        """
        pass
```

---

## 3. ææ¯è§æ ?

### 3.1 接口设计

```python
class TaxLossHarvester:
    """
    ç¨ææ¶å²å?
    
    ä¸»è¦æ¥å£ç±?
    """
    
    def __init__(
        self,
        tax_jurisdiction: str = 'US',  # US, CN
        wash_sale_days: int = 30
    ):
        self.jurisdiction = tax_jurisdiction
        self.pnl_calculator = UnrealizedGainLossCalculator()
        self.wash_detector = WashSaleDetector()
        self.substitute_selector = SubstituteSecuritySelector()
        self.tax_optimizer = AfterTaxReturnOptimizer()
    
    def scan_harvest_opportunities(
        self,
        portfolio: Dict,
        market_data: Dict
    ) -> List[Dict]:
        """
        扫描税损收割机会
        """
        pass
    
    def execute_harvest(
        self,
        opportunity: Dict,
        auto_substitute: bool = True
    ) -> Dict:
        """
        执行税损收割
        """
        pass
```

### 3.2 é
ç½®åæ°

```yaml
tax_loss_harvesting:
  # 税务管辖
  jurisdiction: 'US'  # US, CN
  
  # 税率
  tax_rates:
    short_term: 0.35  # 短期资本利得
    long_term: 0.15   # 长期资本利得
    
  # 洗售规则
  wash_sale:
    enabled: true
    lookback_days: 30
    forward_days: 30
    
  # æ¶å²éå?
  harvest:
    min_loss_amount: 1000  # æå°æå¤±éé¢?
    min_tax_savings: 150   # æå°ç¨æ¶èç?
    
  # 替代证券
  substitute:
    correlation_threshold: 0.9
    max_tracking_error: 0.02
```

---

## ð ç¸å
³ææ¡£

### 上游依赖

| 文档名称 | module_id | 依赖类型 | 说明 |
|---------|-----------|---------|------|
| [ç»åä¼åå¼æéæèå¾](./PORTFOLIO_OPTIMIZER_INTEGRATION_BLUEPRINT.md) | PORTFOLIO_OPTIMIZER_INTEGRATION_001 | å¼ºä¾èµ?| æä¾ä¼åå¨åºç¡æ¥å£ |
| [æ°æ®è´¨éçæ§èå¾](./DATA_QUALITY_MONITORING_BLUEPRINT.md) | DATA_QUALITY_MONITORING_001 | å¼ºä¾èµ?| æä¾æ°æ®è´¨éææ  |
| [äº¤æææ¬åæå¼æèå¾](./TRANSACTION_COST_ANALYSIS_ENGINE_BLUEPRINT.md) | TRANSACTION_COST_ANALYSIS_ENGINE_001 | ä¸­ä¾èµ?| æä¾ææ¬åæ |

### 下游依赖

| 文档名称 | module_id | 依赖类型 | 说明 |
|---------|-----------|---------|------|
| [ç»ååå¹³è¡¡èå¾](./PORTFOLIO_REBALANCING_BLUEPRINT.md) | PORTFOLIO_REBALANCING_001 | å¼ºä¾èµ?| ç»ååå¹³è¡?|
| [å¨è½¬çæ§å¶èå¾](./TURNOVER_CONTROL_BLUEPRINT.md) | TURNOVER_CONTROL_001 | ä¸­ä¾èµ?| å¨è½¬çæ§å?|
| [å­£åº¦è°ä»èå¾](./QUARTERLY_REBALANCE_BLUEPRINT.md) | QUARTERLY_REBALANCE_001 | ä¸­ä¾èµ?| å­£åº¦è°ä»å³ç­ |

### ææ¯ä¾èµ?

| ææ¯ç»ä»?| çæ¬ | ç¨é?| ææ¡£ |
|---------|------|------|------|
| **NumPy** | 1.24+ | æ°å¼è®¡ç®?| [å®æ¹ææ¡£](https://numpy.org/) |
| **Pandas** | 2.0+ | 数据处理 | [官方文档](https://pandas.pydata.org/) |
| **SciPy** | 1.10+ | 科学计算 | [官方文档](https://scipy.org/) |

### å¼ç¨å
³ç³»å?

```mermaid
graph LR
    A[组合优化引擎] --> B[税损收割]
    C[数据质量监控] --> B
    D[交易成本分析引擎] --> B
    
    B --> E[组合再平衡]
    B --> F[周转率控制]
    B --> G[季度调仓]
    
    style B fill:#ff6b6b
    style A fill:#4ecdc4
    style C fill:#45b7d1
```

---

## 4. 变更历史

| çæ¬ | æ¥æ | åæ´å
å®¹ | åæ´äº?|
|------|------|----------|--------|
| v1.0.0 | 2026-04-07 | åå§çæ¬åå»º | é¦å¸­èå¾æ¶æå¸?|

---

**èå¾çæ¬**: v1.0.0 | **åå»ºæ¥æ**: 2026-04-07 | **ç¶æ?*: Active

## 5. 文档治理

### 5.1 文档索引

**本文档在系统中的位置**:
- **æå±å±çº?*: Layer 6 (ç»åä¼åå±?
- **模块索引**: 001
- **模块名称**: TAX_LOSS_HARVESTING
- **文档路径**: docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/

### 5.2 版本管理

**版本历史**:
- v1.0.0 (2026-04-07): 初始版本

### 5.3 维护责任

**文档维护**:
- **责任模块**: TAX_LOSS_HARVESTING
- **ç»´æ¤å¨æ**: æ¯å­£åº¦å®¡æ?
- **åæ´æµç¨**: æäº¤åæ´ç³è¯· â?ææ¯è¯å®?â?æ´æ°ææ¡£

---

**èå¾çæ¬**: v1.0.0 | **åå»ºæ¥æ**: 2026-04-07 | **ç¶æ?*: Active
