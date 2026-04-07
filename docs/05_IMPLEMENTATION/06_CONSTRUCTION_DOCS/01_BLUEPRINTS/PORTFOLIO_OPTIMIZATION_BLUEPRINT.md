---
module_id: IMPL_PORTFOLIO_OPT_BP_001
version: 1.0.2
status: Active
created_date: 2026-04-01
last_updated: '2026-04-06'
owner: é¦å¸­ææ¡£æ¶æå¸?
standard_type: ä¸ä¸éåæºæèå¾
applicable_scope: å¨ç³»ç»æ¶æè®¾è®?
compliance_level: åå§æ å
parent_document: ../INDEX.md
implementation_status: è®¾è®¡é¶æ®µ
open_source_dependency: PyPortfolioOpt, CVXPY, Riskfolio-Lib
estimated_effort: 140å°æ¶
priority: P0
layer: Layer 5.2 (组合优化)
---



# ç­ç¥ç»åä¼åç³»ç»ææ¯è?

> æ¸é£éåäº¤æç³»ç» v5.3 - ç­ç¥ç»åä¼åç³»ç»è¯¦ç»ææ¯è®¾?
> **ç´¢å¼**: `PORTFOLIO_OPTIMIZATION_001`
> **å¼åå¨?*: 140å°æ¶ï¼è¶åä»£ç å¼åï¼
> **æ ¸å¿å®ä½**: ç­ç¥å·¥åæ ¸å¿ç»ä»¶ï¼æ¯æå¤ç­ç¥ç»åä¼åãèµéåéãé£é©é¢ç®ç®¡çãå¨æè°ä»çæºè½ç»åç³»ç»
> **åèå¼?*: PyPortfolioOpt + CVXPY + Riskfolio-Lib + æ¡¥æ°´å¨å¤©åç»åä¼åææ³
> **è¡¥åææ¡£**: æ¬èå¾æ¯[STRATEGY_SELECTION_BLUEPRINT.md](./STRATEGY_SELECTION_BLUEPRINT.md)çåç»­ç»ä»¶ï¼ä¸æ³¨äºå¤ç­ç¥ç»åæå»ºä¸ä¼?


## æ ¸å¿å®ä½

å®ç°PORTFOLIO OPTIMIZATIONçè®¾è®¡ä¸å®ç°ï¼åºäºBlack-Littermanææ¯ï¼è¯ä¼°æ ¸å¿åè½ï¼å®ç°æèµç®æ ã?

## 设计目标

### 主要目标

1. **功能完整性**: 确保PORTFOLIO OPTIMIZATION功能完整，满足业务需求
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

采用PORTFOLIO OPTIMIZATION化设计，分层架构实现。

### 关键技术

- 数据处理: 使用高效的数据处理框架
- 接口实现: RESTful API设计
- 性能优化: 缓存、异步处理

### 实施步骤

1. 需求分析与设计
2. 核心功能开发
3. 测试与优化
4. 部署与监控


## ä¸ãè®¾è®¡ç®æ ä¸çº¦æ

### 1.1 æ ¸å¿è®¾è®¡ç®æ 

| ç®æ  | ä¼å?| ææ¯å®?|
|------|--------|----------|
| **å¤ç­ç¥ç»åä¼?* | P0 | ï¿?æ¹å·®ä¼åãé£é©å¹³ä»·ãæå¤§å¤æ®æ¯çãæå°åæ¤ç­å¤ç§ä¼åç®æ  |
| **æºè½èµéåé** | P0 | åºäºç­ç¥ç»©æãç¸å³æ§ãé£é©è´¡ç®åº¦çå¨æèµéåéç®?|
| **é£é©é¢ç®ç®¡ç** | P1 | å¤å±æ¬¡é£é©é¢ç®ä½ç³»ï¼æ¯æç­ç¥å±ãèµäº§å±ãå å­å±é£é©æ§å¶ |
| **å¨æè°ä»é»è¾** | P1 | åºäºå¸åºç¶æãç­ç¥è¡¨ç°ãé£é©ææ çå¨æè°ä»å³ç­ç³»?|
| **å®æ¶ç»åçæ§** | P2 | ç»åé£é©æå£ãç»©æå½å ãé£æ ¼æ¼ç§»å®æ¶çæ§ä¸é¢è­¦ |
| **AIè¾å©ä¼å** | P2 | å©ç¨å¼ºåå­¦ä¹ ä¼åèµéåéï¼åºäºå¸åºç¯å¢èªéåºè°æ´ç»åæé |

### 1.2 ææ¯çº¦æä¸åå

1. **å¯è§£éæ§å?*ï¼ç»åæéè°æ´å¿é¡»ææç¡®çæ°å­¦é»è¾åä¸å¡è§£?
2. **é£é©å¯æ§åå**ï¼ç»åæ»é£é©ä¸è¶è¿é¢è®¾éå¼ï¼åç­ç¥é£é©è´¡ç®åº¦å¯æ§
3. **äº¤æææ¬æè¯**ï¼è°ä»å³ç­èèäº¤æææ¬ï¼é¿åé¢ç¹æ æè°?
4. **å®çåå¥½åå**ï¼ä¼åç»æå¿é¡»èèå®çæ§è¡å¯è¡æ§ï¼æµå¨æ§ãå²å»ææ¬ç­?
5. **å¼æºä¼åå?*ï¼ä¼åä½¿ç¨æçå¼æºä¼ååºï¼PyPortfolioOptãCVXPYãRiskfolio-Lib?

### 1.3 ä¸ç°æç³»ç»é?

| å·²ææ¨¡å | éææ¹å¼ | æ¥å£å®ä¹ |
|----------|----------|----------|
| **ç­ç¥æåä¸éæ©ç³»ç»** | è¾å¥?| æ¥æ¶å·²éæ©çç­ç¥åè¡¨åå¶ç»©ææ°?|
| **æ¹éè¯ä¼°ç³»ç»** | æ°æ®?| è·åç­ç¥åå²è¡¨ç°ãç¸å³æ§ç©éµãé£é©æ?|
| **é£é©ç®¡çç³»ç»** | è¾åºç®æ  | è¾åºç»åé£é©é¢ç®ãé£é©éé¢è¦?|
| **è®¢åæ§è¡ç³»ç»** | è¾åºç®æ  | è¾åºè°ä»æä»¤ãç®æ ä»?|


## äºãç³»ç»æ¶æè®¾?

### 2.1 æ¶ææ¦è§?

```mermaid
graph TB
    subgraph "è¾å¥?
        A[ç­ç¥æåç»æ] --> B(ç­ç¥ç»©ææ°æ®)
        C[é£é©é¢ç®éç½®] --> D(é£é©çº¦æ)
        E[å¸åºæ°æ®] --> F(ç¸å³æ§ç©?
    end
    
    subgraph "æ ¸å¿ä¼åå¼æ"
        G[ç»åä¼åæ§å¶å¨] --> H[åå¼æ¹å·®ä¼åå¨]
        G --> I[é£é©å¹³ä»·ä¼åå¨]
        G --> J[æå¤§å¤æ®ä¼åå¨]
        G --> K[æå°åæ¤ä¼åå¨]
        H --> L[çº¦æå¤çå¨]
        I --> L
        J --> L
        K --> L
    end
    
    subgraph "AIå¢å¼º?
        M[å¼ºåå­¦ä¹ è°ä»å¨] --> N(èªéåºæéè°æ´)
        O[å¸åºç¯å¢åç±»å¨] --> P(ç¶ææç¥ä¼?
    end
    
    subgraph "è¾åº?
        L --> Q[ç»åæéæ¹æ¡]
        N --> Q
        P --> Q
        Q --> R[é£é©å½å æ¥å]
        Q --> S[è°ä»æ§è¡æä»¤]
    end
    
    B --> G
    D --> L
    F --> H
```

### 2.2 æ¨¡ååå±æ¶æ

**Layer 1 - æ°æ®åå¤?*
- ç­ç¥ç»©ææ°æ®æå?
- ç¸å³æ§ç©éµè®¡ç®å¨
- é£é©é¢ç®è§£æ?

**Layer 2 - æ ¸å¿ä¼å?*
- ç»åä¼åæ§å¶å¨ï¼è°åº¦å¨ï¼
- å¤ç§ä¼åç®æ³å®ç°
- çº¦ææ¡ä»¶å¤ç?

**Layer 3 - AIå¢å¼º?*
- å¼ºåå­¦ä¹ èµéåé?
- å¸åºç¯å¢æç¥ä¼å?
- èªéåºè°ä»å³ç­?

**Layer 4 - ç»æè¾åº?*
- ç»åæéè¾åº?
- é£é©å½å åæ?
- è°ä»æä»¤çæ?


## ä¸ãæ ¸å¿ç»ä»¶è¯¦ç»è®¾?

### 3.1 ç»åä¼åæ§å¶å¨ï¼PortfolioOptimizationController?

```python
class PortfolioOptimizationController:
    """
    ç»åä¼åæ§å¶?- è´è´£è°åº¦ä¸åçä¼åç®æ³ï¼ç®¡çä¼åæµç¨
    """
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.optimizers = {
            'mean_variance': MeanVarianceOptimizer(),
            'risk_parity': RiskParityOptimizer(),
            'max_sharpe': MaxSharpeOptimizer(),
            'min_drawdown': MinDrawdownOptimizer(),
            'black_litterman': BlackLittermanOptimizer()
        }
        self.constraint_processor = ConstraintProcessor()
        self.risk_budget_manager = RiskBudgetManager()
        
    async def optimize_portfolio(self, optimization_request: OptimizationRequest) -> OptimizationResult:
        """
        æ§è¡ç»åä¼å
        
        Args:
            optimization_request: ä¼åè¯·æ±ï¼åå«ç­ç¥åè¡¨ãç»©ææ°æ®ãçº¦ææ¡ä»¶ç­
            
        Returns:
            OptimizationResult: ä¼åç»æï¼åå«æéåéãé¢ææ¶çãé£é©ææ ç­
        """
        # 1. æ°æ®åå¤ä¸éª?
        validated_data = await self._prepare_optimization_data(optimization_request)
        
        # 2. é£é©é¢ç®å¤ç
        risk_constraints = self.risk_budget_manager.process_budget(optimization_request.risk_budget)
        
        # 3. æ§è¡ä¼åç®æ³
        optimizer = self.optimizers.get(optimization_request.optimization_method)
        if not optimizer:
            raise ValueError(f"ä¸æ¯æçä¼åæ¹æ³: {optimization_request.optimization_method}")
            
        raw_weights = optimizer.optimize(
            returns=validated_data['returns'],
            cov_matrix=validated_data['cov_matrix'],
            constraints=risk_constraints
        )
        
        # 4. åºç¨äº¤æææ¬ä¸æµå¨æ§çº¦?
        adjusted_weights = self.constraint_processor.apply_real_world_constraints(
            raw_weights, 
            optimization_request.trading_constraints
        )
        
        # 5. çæä¼åæ¥å
        result = OptimizationResult(
            weights=adjusted_weights,
            expected_return=self._calculate_expected_return(adjusted_weights, validated_data['returns']),
            risk_metrics=self._calculate_risk_metrics(adjusted_weights, validated_data['cov_matrix']),
            risk_attribution=self._calculate_risk_attribution(adjusted_weights, validated_data['cov_matrix']),
            optimization_details={
                'method': optimization_request.optimization_method,
                'constraints_applied': risk_constraints,
                'iterations': optimizer.get_iteration_count()
            }
        )
        
        return result
    
    async def _prepare_optimization_data(self, request: OptimizationRequest) -> Dict:
        """
        åå¤ä¼åæéæ°æ®
        """
        # æåç­ç¥ç»©ææ°æ®
        returns_data = []
        for strategy in request.strategies:
            # ä»æ¹éè¯ä¼°ç»æä¸­è·åç­ç¥çåå²æ¶çåº?
            performance = await self._get_strategy_performance(strategy.strategy_id)
            returns_data.append(performance['returns_series'])
        
        # è®¡ç®ç¸å³æ§ç©éµååæ¹å·®ç©?
        returns_df = pd.DataFrame(returns_data).T
        cov_matrix = returns_df.cov()
        correlation_matrix = returns_df.corr()
        
        return {
            'returns': returns_df.mean(),
            'cov_matrix': cov_matrix,
            'correlation_matrix': correlation_matrix,
            'strategy_ids': [s.strategy_id for s in request.strategies]
        }
```

### 3.2 ï¿?æ¹å·®ä¼åå¨ï¼MeanVarianceOptimizer?

```python
class MeanVarianceOptimizer:
    """
    ï¿?æ¹å·®ä¼å?- åºäºé©¬ç§ç»´è¨ç°ä»£æèµç»åçè®º
    ä½¿ç¨PyPortfolioOptåºå®?
    """
    
    def __init__(self, risk_free_rate: float = 0.02):
        self.risk_free_rate = risk_free_rate
        
    def optimize(self, returns: pd.Series, cov_matrix: pd.DataFrame, 
                constraints: List[Constraint]) -> pd.Series:
        """
        æ§è¡ï¿?æ¹å·®ä¼å
        
        Args:
            returns: åç­ç¥é¢ææ¶çç
            cov_matrix: åæ¹å·®ç©?
            constraints: çº¦ææ¡ä»¶åè¡¨
            
        Returns:
            pd.Series: æä¼æéå?
        """
        # ä½¿ç¨PyPortfolioOpt?
        from pypfopt import EfficientFrontier
        
        # åå»ºææåæ²¿
        ef = EfficientFrontier(returns, cov_matrix)
        
        # åºç¨çº¦ææ¡ä»¶
        for constraint in constraints:
            if constraint.type == 'weight_bound':
                ef.add_constraint(lambda w: w[constraint.strategy_idx] <= constraint.max_weight)
            elif constraint.type == 'sector_limit':
                # è¡ä¸éå¶çº¦æ
                pass
        
        # ä¼åç®æ ï¼æå°åæ³¢å¨çææå¤§åå¤æ®æ¯ç
        if constraints.optimization_target == 'min_volatility':
            weights = ef.min_volatility()
        elif constraints.optimization_target == 'max_sharpe':
            weights = ef.max_sharpe()
        elif constraints.optimization_target == 'efficient_risk':
            weights = ef.efficient_risk(target_volatility=constraints.target_volatility)
        elif constraints.optimization_target == 'efficient_return':
            weights = ef.efficient_return(target_return=constraints.target_return)
        
        # æ¸çæéï¼åèäºå¥ï¼å¤çå¾®å°æé?
        cleaned_weights = ef.clean_weights()
        
        return pd.Series(cleaned_weights)
    
    def plot_efficient_frontier(self, returns: pd.Series, cov_matrix: pd.DataFrame):
        """
        ç»å¶ææåæ²¿?
        """
        from pypfopt import plotting
        
        ef = EfficientFrontier(returns, cov_matrix)
        fig, ax = plt.subplots()
        plotting.plot_efficient_frontier(ef, ax=ax, show_assets=True)
        
        # æ è®°æä¼ç»åç¹
        if hasattr(self, 'optimal_weights'):
            ret, vol, sharpe = ef.portfolio_performance(weights=self.optimal_weights)
            ax.scatter(vol, ret, marker='*', s=200, c='r', label='æä¼ç»?)
        
        ax.set_title('ï¿?æ¹å·®ææåæ²¿')
        ax.legend()
        return fig
```

### 3.3 é£é©å¹³ä»·ä¼åå¨ï¼RiskParityOptimizer?

```python
class RiskParityOptimizer:
    """
    é£é©å¹³ä»·ä¼å?- åºäºæ¡¥æ°´å¨å¤©åç»åææ³
    ä½¿ç¨Riskfolio-Libåºå®?
    """
    
    def __init__(self, risk_measure: str = 'CVaR', alpha: float = 0.05):
        self.risk_measure = risk_measure  # CVaR, VaR, CDaR, EDaR?
        self.alpha = alpha  # CVaRç½®ä¿¡æ°´å¹³
        
    def optimize(self, returns: pd.DataFrame, constraints: List[Constraint]) -> pd.Series:
        """
        æ§è¡é£é©å¹³ä»·ä¼å
        
        Args:
            returns: ç­ç¥æ¶çæ°æ®?
            constraints: çº¦ææ¡ä»¶
            
        Returns:
            pd.Series: é£é©å¹³ä»·æé
        """
        import riskfolio as rp
        
        # åå»ºæèµç»åå¯¹è±¡
        port = rp.Portfolio(returns=returns)
        
        # éæ©é£é©åº¦éæ¹æ³
        port.assets_stats(method_mu='hist', method_cov='hist')
        
        # è®¾ç½®ä¼åé®é¢
        model = 'Classic'  # ç»å¸é£é©å¹³ä»·æ¨¡å
        rm = self.risk_measure  # é£é©åº¦éæ¹æ³
        obj = 'Risk'  # ç®æ å½æ°ï¼æå°åé£é©
        hist = True  # ä½¿ç¨åå²æ°æ®
        
        # è®¾ç½®çº¦ææ¡ä»¶
        upper_bound = constraints.get('upper_bound', 1.0)
        lower_bound = constraints.get('lower_bound', 0.0)
        
        # æ§è¡é£é©å¹³ä»·ä¼å
        w = port.rp_optimization(
            model=model,
            rm=rm,
            rf=0,  # æ é£é©å©?
            b=None,  # é£é©é¢ç®ï¼Noneè¡¨ç¤ºç­é£é©è´¡ç®ï¼
            hist=hist,
            upper_bound=upper_bound,
            lower_bound=lower_bound
        )
        
        return w
    
    def calculate_risk_contribution(self, weights: pd.Series, cov_matrix: pd.DataFrame) -> pd.Series:
        """
        è®¡ç®åç­ç¥çé£é©è´¡ç®?
        """
        portfolio_variance = weights.T @ cov_matrix @ weights
        marginal_risk_contribution = cov_matrix @ weights
        risk_contribution = weights * marginal_risk_contribution / portfolio_variance
        
        return risk_contribution
    
    def plot_risk_contribution(self, weights: pd.Series, cov_matrix: pd.DataFrame):
        """
        ç»å¶é£é©è´¡ç®åº¦å¾
        """
        risk_contrib = self.calculate_risk_contribution(weights, cov_matrix)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # æéåå¸?
        weights.plot(kind='bar', ax=ax1, color='skyblue')
        ax1.set_title('ç»åæéåé')
        ax1.set_ylabel('æéæ¯ä¾')
        ax1.tick_params(axis='x', rotation=45)
        
        # é£é©è´¡ç®åº¦å¾
        risk_contrib.plot(kind='bar', ax=ax2, color='lightcoral')
        ax2.set_title('é£é©è´¡ç®åº¦å?)
        ax2.set_ylabel('é£é©è´¡ç®?)
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        return fig
```

### 3.4 çº¦æå¤çå¨ï¼ConstraintProcessor?

```python
class ConstraintProcessor:
    """
    çº¦æå¤ç?- å¤çåç§å®ççº¦ææ¡ä»¶
    """
    
    def __init__(self):
        self.constraint_handlers = {
            'position_limit': self._handle_position_limit,
            'turnover_limit': self._handle_turnover_limit,
            'liquidity_constraint': self._handle_liquidity_constraint,
            'transaction_cost': self._handle_transaction_cost,
            'sector_exposure': self._handle_sector_exposure,
            'factor_exposure': self._handle_factor_exposure
        }
        
    def apply_real_world_constraints(self, raw_weights: pd.Series, 
                                    constraints: Dict[str, Any]) -> pd.Series:
        """
        åºç¨å®ççº¦ææ¡ä»¶
        
        Args:
            raw_weights: çè®ºä¼åæé
            constraints: çº¦ææ¡ä»¶å­å¸
            
        Returns:
            pd.Series: è°æ´åçå®çå¯è¡æé
        """
        adjusted_weights = raw_weights.copy()
        
        # æä¼åçº§é¡ºåºåºç¨çº¦æ
        constraint_priority = [
            'position_limit',      # ä»ä½éå¶ï¼çç®¡è¦æ±ï¼
            'liquidity_constraint', # æµå¨æ§çº¦?
            'transaction_cost',    # äº¤æææ¬
            'turnover_limit',      # æ¢æçé?
            'sector_exposure',     # è¡ä¸æ´é²éå¶
            'factor_exposure'      # å å­æ´é²éå¶
        ]
        
        for constraint_type in constraint_priority:
            if constraint_type in constraints:
                handler = self.constraint_handlers.get(constraint_type)
                if handler:
                    adjusted_weights = handler(adjusted_weights, constraints[constraint_type])
        
        # ç¡®ä¿æéåä¸º1ï¼å½ä¸åï¼
        adjusted_weights = adjusted_weights / adjusted_weights.sum()
        
        return adjusted_weights
    
    def _handle_position_limit(self, weights: pd.Series, limit_config: Dict) -> pd.Series:
        """
        å¤çåç­ç¥ä»ä½é?
        """
        max_position = limit_config.get('max_position', 0.3)  # é»è®¤åç­ç¥æå¤§ä»?0%
        min_position = limit_config.get('min_position', 0.01) # é»è®¤æå°ä»?%
        
        # åºç¨ä¸ä¸?
        weights = weights.clip(lower=min_position, upper=max_position)
        
        return weights
    
    def _handle_transaction_cost(self, weights: pd.Series, cost_config: Dict) -> pd.Series:
        """
        å¤çäº¤æææ¬çº¦æ
        """
        current_positions = cost_config.get('current_positions', pd.Series(0, index=weights.index))
        transaction_costs = cost_config.get('transaction_costs', {})
        
        # è®¡ç®è°ä»æ¯ä¾
        rebalance_amount = abs(weights - current_positions)
        
        # ä¼°ç®äº¤æææ¬
        total_cost = 0
        for strategy_id in weights.index:
            if strategy_id in transaction_costs:
                cost_rate = transaction_costs[strategy_id]
                strategy_cost = rebalance_amount[strategy_id] * cost_rate
                total_cost += strategy_cost
        
        # å¦æäº¤æææ¬è¿é«ï¼åå°è°ä»å¹?
        cost_threshold = cost_config.get('cost_threshold', 0.005)  # é»è®¤0.5%
        if total_cost > cost_threshold:
            # ææ¯ä¾åå°è°ä»å¹?
            reduction_factor = cost_threshold / total_cost
            weights = current_positions + (weights - current_positions) * reduction_factor
        
        return weights
    
    def _handle_liquidity_constraint(self, weights: pd.Series, liquidity_config: Dict) -> pd.Series:
        """
        å¤çæµå¨æ§çº¦?
        """
        liquidity_data = liquidity_config.get('liquidity_data', {})
        portfolio_value = liquidity_config.get('portfolio_value', 1e6)  # é»è®¤ç»åè§æ¨¡100?
        
        adjusted_weights = weights.copy()
        
        for strategy_id, weight in weights.items():
            if strategy_id in liquidity_data:
                daily_volume = liquidity_data[strategy_id].get('daily_volume', 0)
                position_value = weight * portfolio_value
                
                # æ£æ¥æµå¨æ§æ¯å¦åè¶³ï¼åè®¾åæ¥äº¤æä¸è¶è¿æ¥æäº¤éç5%?
                max_daily_trade = daily_volume * 0.05
                if position_value > max_daily_trade * 3:  # ?å¤©å»º?
                    # è°æ´æéè³æµå¨æ§åè®¸è?
                    adjusted_weights[strategy_id] = (max_daily_trade * 3) / portfolio_value
        
        return adjusted_weights
```

### 3.5 å¼ºåå­¦ä¹ è°ä»å¨ï¼RLRebalancer?

```python
class RLRebalancer:
    """
    å¼ºåå­¦ä¹ è°ä»?- ä½¿ç¨å¼ºåå­¦ä¹ ä¼åå¨æè°ä»å³?
    """
    
    def __init__(self, state_dim: int = 20, action_dim: int = 10):
        self.state_dim = state_dim  # ç¶æç»´åº¦ï¼å¸åºï¿?+ ç­ç¥è¡¨ç° + é£é©ææ 
        self.action_dim = action_dim  # å¨ä½ç»´åº¦ï¼åç­ç¥æéè°æ´å¹åº¦
        
        # ä½¿ç¨Stable-Baselines3?
        self.model = None
        self.env = None
        
    def train(self, historical_data: pd.DataFrame, 
              training_episodes: int = 10000) -> None:
        """
        è®­ç»å¼ºåå­¦ä¹ æ¨¡å
        
        Args:
            historical_data: åå²å¸åºæ°æ®åç­ç¥è¡¨ç°æ°?
            training_episodes: è®­ç»è½®æ°
        """
        # åå»ºå¼ºåå­¦ä¹ ç¯å¢
        self.env = PortfolioRebalanceEnv(
            data=historical_data,
            initial_weights=np.ones(self.action_dim) / self.action_dim,
            transaction_cost=0.001,
            lookback_window=20
        )
        
        # ä½¿ç¨PPOç®æ³ï¼Proximal Policy Optimization?
        from stable_baselines3 import PPO
        
        self.model = PPO(
            'MlpPolicy',
            self.env,
            verbose=1,
            learning_rate=0.0003,
            n_steps=2048,
            batch_size=64,
            n_epochs=10,
            gamma=0.99,
            gae_lambda=0.95,
            clip_range=0.2,
            clip_range_vf=None,
            ent_coef=0.01,
            vf_coef=0.5,
            max_grad_norm=0.5,
            use_sde=False,
            sde_sample_freq=-1,
            target_kl=None,
            tensorboard_log="./rl_rebalancer_logs/"
        )
        
        # è®­ç»æ¨¡å
        self.model.learn(total_timesteps=training_episodes)
        
    def predict_rebalance_action(self, current_state: Dict) -> np.ndarray:
        """
        é¢æµè°ä»å¨ä½
        
        Args:
            current_state: å½åç¶æï¼å¸åºç¶æãç­ç¥è¡¨ç°ãé£é©ææ ç­?
            
        Returns:
            np.ndarray: æéè°æ´å¨ä½
        """
        if self.model is None:
            raise ValueError("æ¨¡åæªè®­ç»ï¼è¯·åè°ç¨trainæ¹æ³")
        
        # å°ç¶æè½¬æ¢ä¸ºæ¨¡åè¾å¥æ ¼å¼
        observation = self._format_state_to_observation(current_state)
        
        # é¢æµå¨ä½
        action, _ = self.model.predict(observation, deterministic=True)
        
        return action
    
    def _format_state_to_observation(self, state: Dict) -> np.ndarray:
        """
        å°ç¶æå­å¸è½¬æ¢ä¸ºè§å¯åé
        """
        # å¸åºç¶æç¹?
        market_features = [
            state.get('market_trend', 0),
            state.get('market_volatility', 0),
            state.get('market_liquidity', 0),
            state.get('economic_regime', 0)
        ]
        
        # ç­ç¥è¡¨ç°ç¹å¾
        strategy_features = []
        for strategy_id in state.get('strategy_performance', {}):
            perf = state['strategy_performance'][strategy_id]
            strategy_features.extend([
                perf.get('sharpe_ratio', 0),
                perf.get('max_drawdown', 0),
                perf.get('win_rate', 0),
                perf.get('profit_factor', 0)
            ])
        
        # é£é©ææ ç¹å¾
        risk_features = [
            state.get('portfolio_var', 0),
            state.get('portfolio_cvar', 0),
            state.get('concentration_risk', 0),
            state.get('liquidity_risk', 0)
        ]
        
        # ç»åæè§å¯å?
        observation = np.concatenate([
            market_features,
            strategy_features[:min(len(strategy_features), 8)],  # æ?ä¸ªç­ç¥ç¹?
            risk_features
        ])
        
        # å¡«åææªæ­è³åºå®ç»´åº¦
        if len(observation) < self.state_dim:
            observation = np.pad(observation, (0, self.state_dim - len(observation)))
        elif len(observation) > self.state_dim:
            observation = observation[:self.state_dim]
        
        return observation
```


## åãå¼æºæ¨¡åéææ¹?

### 4.1 PyPortfolioOptéæ

```yaml
# éç½®ç¤ºä¾ï¼PyPortfolioOptä¼åå¨é?
pypfopt_config:
  optimization_methods:
    - name: "mean_variance"
      description: "ï¿?æ¹å·®ä¼å"
      parameters:
        target_return: null
        target_volatility: null
        market_neutral: false
        risk_free_rate: 0.02
    
    - name: "efficient_risk"
      description: "ç»å®é£é©æ°´å¹³ä¸çæä¼æ¶?
      parameters:
        target_volatility: 0.15
    
    - name: "efficient_return"
      description: "ç»å®æ¶çæ°´å¹³ä¸çæå°é£?
      parameters:
        target_return: 0.10
  
  constraints:
    weight_bounds: [0.01, 0.3]  # åç­ç¥æéè?%-30%
    sector_exposure: null
    factor_exposure: null
  
  risk_model:
    covariance_estimator: "sample_cov"  # æ ·æ¬åæ¹?
    shrinkage_method: "ledoit_wolf"     # Ledoit-Wolfæ¶ç¼©ä¼°è®¡
```

### 4.2 Riskfolio-Libéæ

```yaml
# éç½®ç¤ºä¾ï¼Riskfolio-Libé£é©å¹³ä»·éç½®
riskfolio_config:
  risk_measures:
    - name: "CVaR"
      description: "æ¡ä»¶å¨é©ï¿?
      parameters:
        alpha: 0.05
        confidence_level: 0.95
    
    - name: "CDaR"
      description: "æ¡ä»¶å¨é©åæ¤"
      parameters:
        alpha: 0.05
    
    - name: "EDaR"
      description: "çµå¨é©ä»·?
      parameters:
        alpha: 0.05
  
  optimization_models:
    - name: "Classic"
      description: "ç»å¸é£é©å¹³ä»·æ¨¡å"
    
    - name: "BL"
      description: "Black-Littermanæ¨¡å"
      parameters:
        P: null  # è§ç¹ç©éµ
        Q: null  # è§ç¹æ¶çåé
        Omega: null  # è§ç¹ä¸ç¡®å®æ§ç©?
    
    - name: "FM"
      description: "å å­æ¨¡åé£é©å¹³ä»·"
  
  constraints:
    upper_bound: 0.3
    lower_bound: 0.01
    budget: 1.0
```

### 4.3 CVXPYéæï¼èªå®ä¹ä¼åé®é¢?

```python
# èªå®ä¹ä¼åé®é¢ç¤ºä¾ï¼æå°ååæ¤ä¼å
import cvxpy as cp

class MinDrawdownOptimizer:
    """
    æå°ååæ¤ä¼å?- ä½¿ç¨CVXPYæ±è§£èªå®ä¹ä¼åé®?
    """
    
    def optimize(self, returns: pd.DataFrame, max_positions: int = 10) -> pd.Series:
        n_assets = returns.shape[1]
        
        # å³ç­åéï¼æ?
        w = cp.Variable(n_assets)
        
        # è®¡ç®ç»åæ¶çåºå
        portfolio_returns = returns.values @ w
        
        # è®¡ç®ç´¯ç§¯æ¶çåå?
        cumulative_returns = cp.cumsum(portfolio_returns)
        running_max = cp.maximum.accumulate(cumulative_returns)
        drawdown = running_max - cumulative_returns
        
        # ç®æ å½æ°ï¼æå°åæå¤§å?
        objective = cp.Minimize(cp.max(drawdown))
        
        # çº¦ææ¡ä»¶
        constraints = [
            cp.sum(w) == 1,  # æéåä¸º1
            w >= 0,  # ä¸åè®¸å?
            w <= 0.3,  # åèµäº§æå¤§æ?0%
            cp.norm(w, 0) <= max_positions  # æå¤ææmax_positionsä¸ªç­?
        ]
        
        # æ±è§£ä¼åé®é¢
        problem = cp.Problem(objective, constraints)
        problem.solve(solver=cp.ECOS)
        
        return pd.Series(w.value, index=returns.columns)
```


## äºãéç½®ä¸ä½¿ç¨ç¤ºä¾

### 5.1 å®æ´ä¼åæµç¨ç¤ºä¾

```python
async def run_complete_portfolio_optimization():
    """
    å®æ´çç»åä¼åæµç¨ç¤º?
    """
    # 1. ä»ç­ç¥éæ©ç³»ç»è·åå·²éæ©çç­?
    selection_system = StrategySelectionSystem()
    selected_strategies = await selection_system.get_top_strategies(
        count=10,
        criteria=['sharpe_ratio', 'max_drawdown', 'win_rate']
    )
    
    # 2. ä»æ¹éè¯ä¼°ç³»ç»è·åç­ç¥ç»©ææ°?
    batch_evaluator = BatchEvaluationSystem()
    performance_data = await batch_evaluator.get_strategy_performance(
        strategy_ids=[s.id for s in selected_strategies],
        lookback_period=252  # ä¸å¹´æ°?
    )
    
    # 3. éç½®ä¼ååæ°
    optimization_config = {
        'optimization_method': 'mean_variance',
        'optimization_target': 'max_sharpe',
        'risk_budget': {
            'total_risk_limit': 0.15,  # ç»åå¹´åæ³¢å¨çä¸è¶è¿15%
            'max_drawdown_limit': 0.20,  # æå¤§åæ¤ä¸è¶è¿20%
            'var_limit': 0.05,  # 95% VaRä¸è¶?%
            'strategy_risk_limits': {
                strategy_id: {'max_risk_contribution': 0.25}
                for strategy_id in performance_data.keys()
            }
        },
        'trading_constraints': {
            'position_limit': {'max_position': 0.3, 'min_position': 0.01},
            'transaction_cost': {'cost_rate': 0.001, 'cost_threshold': 0.005},
            'liquidity_constraint': {
                'portfolio_value': 1000000,
                'liquidity_data': await get_liquidity_data()
            }
        }
    }
    
    # 4. åå»ºä¼åè¯·æ±
    optimization_request = OptimizationRequest(
        strategies=selected_strategies,
        performance_data=performance_data,
        config=optimization_config
    )
    
    # 5. æ§è¡ç»åä¼å
    optimizer = PortfolioOptimizationController(config=optimization_config)
    result = await optimizer.optimize_portfolio(optimization_request)
    
    # 6. è¾åºä¼åç»æ
    print("=" * 60)
    print("ç»åä¼åç»æ")
    print("=" * 60)
    
    print(f"\næéåé:")
    for strategy_id, weight in result.weights.items():
        print(f"  {strategy_id}: {weight:.2%}")
    
    print(f"\né¢æç»©æ:")
    print(f"  é¢æå¹´åæ¶ç: {result.expected_return:.2%}")
    print(f"  é¢æå¹´åæ³¢å¨: {result.risk_metrics['annual_volatility']:.2%}")
    print(f"  é¢æå¤æ®æ¯ç: {result.risk_metrics['sharpe_ratio']:.2f}")
    print(f"  é¢ææå¤§å? {result.risk_metrics['max_drawdown']:.2%}")
    
    print(f"\né£é©è´¡ç®?")
    for strategy_id, risk_contrib in result.risk_attribution['strategy_contributions'].items():
        print(f"  {strategy_id}: {risk_contrib:.2%}")
    
    # 7. çæå¯è§åæ¥?
    report_generator = OptimizationReportGenerator()
    report = report_generator.generate_report(result)
    
    # ä¿å­æ¥å
    report.save("portfolio_optimization_report.html")
    
    return result
```

### 5.2 å½ä»¤è¡æ¥å£ç¤º?

```bash
# æ¥çå¯ç¨çä¼åæ¹?
python portfolio_optimizer.py list-methods

# æ§è¡ï¿?æ¹å·®ä¼å
python portfolio_optimizer.py optimize \
  --method mean_variance \
  --target max_sharpe \
  --strategies strategy_001 strategy_002 strategy_003 \
  --lookback-days 252 \
  --risk-limit 0.15 \
  --output results/optimization_result.json

# æ§è¡é£é©å¹³ä»·ä¼å
python portfolio_optimizer.py optimize \
  --method risk_parity \
  --risk-measure CVaR \
  --alpha 0.05 \
  --strategies strategy_004 strategy_005 strategy_006 \
  --lookback-days 504 \
  --output results/risk_parity_result.json

# çæä¼åæ¥å
python portfolio_optimizer.py generate-report \
  --input results/optimization_result.json \
  --output reports/optimization_report.html

# æ¹éä¼åæµè¯
python portfolio_optimizer.py batch-optimize \
  --config configs/batch_optimization.yaml \
  --output-dir results/batch_optimization/
```

### 5.3 YAMLéç½®æä»¶ç¤ºä¾

```yaml
# configs/portfolio_optimization.yaml
portfolio_optimization:
  # è¾å¥éç½®
  input:
    strategy_source: "strategy_selection_system"
    top_strategy_count: 15
    selection_criteria: ["sharpe_ratio", "max_drawdown", "win_rate", "profit_factor"]
    lookback_period: 252  # äº¤æ?
  
  # ä¼åæ¹æ³éç½®
  optimization:
    primary_method: "mean_variance"
    alternative_methods: ["risk_parity", "max_sharpe", "min_drawdown"]
    optimization_target: "max_sharpe"
    risk_free_rate: 0.02
  
  # é£é©é¢ç®éç½®
  risk_budget:
    total_risk_limit: 0.15  # å¹´åæ³¢å¨çä¸è¶è¿15%
    max_drawdown_limit: 0.20  # æå¤§åæ¤ä¸è¶è¿20%
    var_95_limit: 0.05  # 95% VaRä¸è¶?%
    cvar_95_limit: 0.07  # 95% CVaRä¸è¶?%
    
    strategy_limits:
      max_single_strategy_risk: 0.25  # åç­ç¥é£é©è´¡ç®ä¸è¶è¿25%
      min_strategies: 5  # æå°æ?ä¸ªç­?
      max_strategies: 12  # æå¤æ?2ä¸ªç­?
  
  # äº¤æçº¦æéç½®
  trading_constraints:
    position_limits:
      max_single_position: 0.30  # åç­ç¥æå¤§ä»?0%
      min_position: 0.01  # æå°ä»?%
    
    turnover_limits:
      max_annual_turnover: 6.0  # å¹´åæ¢æçä¸è¶è¿6?
      max_single_rebalance: 0.10  # åæ¬¡è°ä»ä¸è¶?0%
    
    transaction_costs:
      default_cost_rate: 0.001  # é»è®¤äº¤æææ¬0.1%
      strategy_specific_costs:
        high_frequency_strategy: 0.002
        options_strategy: 0.003
  
  # è¾åºéç½®
  output:
    generate_report: true
    report_format: "html"
    save_weights: true
    weights_format: "json"
    visualize_results: true
    create_performance_charts: true
    
  # çæ§éç½®
  monitoring:
    rebalance_frequency: "weekly"  # æ¯å¨è°ä»
    performance_check_frequency: "daily"  # æ¯æ¥æ£æ¥ç»©?
    risk_monitoring_frequency: "intraday"  # æ¥åé£é©çæ§
    alert_thresholds:
      drawdown_alert: 0.08  # åæ¤è¶è¿8%é¢è­¦
      volatility_alert: 0.18  # æ³¢å¨çè¶?8%é¢è­¦
      concentration_alert: 0.35  # éä¸­åº¦è¶?5%é¢è­¦
```


## å­ãå¼åè·¯çº¿å¾ä¸éç¨ç¢

### 6.1 å¼åé¶æ®µå?

**é¶æ®µä¸ï¼åºç¡æ¡æ¶æ­å»º?å¨ï¼**
- åå»ºç»åä¼åæ§å¶å¨åº?
- éæPyPortfolioOptåºç¡ä¼ååè½
- å®ç°åºæ¬çº¦æå¤ç?
- å¼åæ°æ®åå¤æ¨¡?

**é¶æ®µäºï¼é«çº§ä¼åç®æ³?å¨ï¼**
- éæRiskfolio-Libé£é©å¹³ä»·ä¼å
- å®ç°CVXPYèªå®ä¹ä¼åé®?
- å¼åBlack-Littermanæ¨¡å
- æ·»å å å­æ¨¡åä¼å

**é¶æ®µä¸ï¼AIå¢å¼ºåè½?å¨ï¼**
- å®ç°å¼ºåå­¦ä¹ è°ä»?
- å¼åå¸åºç¯å¢æç¥ä¼åå¨
- æ·»å èªéåºæéè°æ´ç®æ³
- éææºå¨å­¦ä¹ é£é©é¢æµ

**é¶æ®µåï¼å®çéæä¸ä¼åï¼6å¨ï¼**
- ä¸è®¢åæ§è¡ç³»ç»é?
- å®ççº¦ææ¡ä»¶ç²¾ç»åå¤?
- æ§è½ä¼åä¸åå­ç®¡?
- å®¹éæºå¶ä¸çæ§å?

### 6.2 å³é®éç¨?

| éç¨?| é¢è®¡å®ææ¶é´ | äº¤ä»?| æåæ å |
|--------|--------------|--------|----------|
| **M1ï¼åºç¡ä¼åæ¡æ¶** | ?å¨ç»?| 1. ç»åä¼åæ§å¶?br>2. ï¿?æ¹å·®ä¼å?br>3. åºæ¬çº¦æå¤ç?| æ¯æ5ç§ç­ç¥ç»åä¼åï¼ç»æå¯å¤?|
| **M2ï¼é£é©å¹³ä»·å®?* | ?0å¨ç»?| 1. é£é©å¹³ä»·ä¼å?br>2. é£é©è´¡ç®åº¦å?br>3. å¤é£é©åº¦éæ¯?| å®ç°ç»å¸é£é©å¹³ä»·åé£é©é¢ç®æ¨¡?|
| **M3ï¼AIè°ä»ç³»ç»** | ?8å¨ç»?| 1. å¼ºåå­¦ä¹ è°ä»?br>2. å¸åºç¯å¢åç±»?br>3. èªéåºä¼åæ¡æ¶ | AIè°ä»ç­ç¥è¡¨ç°ä¼äºéæä¼?0% |
| **M4ï¼å®çå°±?* | ?4å¨ç»?| 1. å®æ´å®ççº¦æå¤ç<br>2. é«æ§è½ä¼åå¼æ<br>3. çæ§åè­¦ç³»ç» | éè¿3ä¸ªææ¨¡æçæµè¯ï¼å¹´åæ¢æ?8?|

### 6.3 é£é©è¯ä¼°ä¸åº?

| é£é©ç±»å | æ¦ç | å½±å | åºå¯¹æªæ½ |
|----------|------|------|----------|
| **ä¼åç»æè¿æ?* | ?| ?| 1. æ ·æ¬å¤æµè¯éª?br>2. æ­£ååææ¯åº?br>3. åæ°æææ§å?|
| **è®¡ç®æ§è½ç¶é¢** | ?| ?| 1. å¹¶è¡è®¡ç®ä¼å<br>2. ç¼å­æºå¶å®ç°<br>3. å¢éè®¡ç®ç®æ³ |
| **å®çæ§è¡åå·®** | ?| ?| 1. äº¤æææ¬ç²¾ç¡®å»ºæ¨¡<br>2. æµå¨æ§çº¦æå¤?br>3. æ»ç¹æ¨¡ææµè¯ |
| **æ¨¡åé£é©** | ?| ?| 1. å¤æ¨¡åå¯¹æ¯éª?br>2. ååæµè¯<br>3. äººå·¥å¹²é¢æºå¶ |


## ä¸ãéå½ï¼å¼æºé¡¹ç®å?

### 7.1 æ ¸å¿ä¼å?

1. **PyPortfolioOpt** - Pythonæèµç»åä¼å?
   - GitHub: https://github.com/robertmartin8/PyPortfolioOpt
   - ç¹ç¹ï¼å®ç°é©¬ç§ç»´è¨ç°ä»£æèµç»åçè®ºï¼æ¯æï¿?æ¹å·®ä¼åãé»å©ç¹æ¼æ¨¡åç­
   - éææ¹å¼ï¼ç´æ¥pipå®è£ï¼ä½ä¸ºæ ¸å¿ä¼åå¼?

2. **Riskfolio-Lib** - Pythoné£é©å¹³ä»·ä¸ç»åä¼ååº
   - GitHub: https://github.com/dcajasn/Riskfolio-Lib
   - ç¹ç¹ï¼ä¸ä¸é£é©å¹³ä»·å®ç°ï¼æ¯æå¤ç§é£é©åº¦éï¼CVaRãCDaRãEDaRç­ï¼
   - éææ¹å¼ï¼ä½ä¸ºé«çº§é£é©å¹³ä»·ä¼åæ¨¡?

3. **CVXPY** - Pythonå¸ä¼ååº
   - GitHub: https://github.com/cvxpy/cvxpy
   - ç¹ç¹ï¼å¼ºå¤§çå¸ä¼åæ±è§£å¨ï¼æ¯æèªå®ä¹ä¼åé®é¢
   - éææ¹å¼ï¼ç¨äºå®ç°ç¹æ®ä¼åç®æ ï¼å¦æå°ååæ¤?

### 7.2 è¾å©å·¥å·?

4. **Stable-Baselines3** - å¼ºåå­¦ä¹ ?
   - GitHub: https://github.com/DLR-RM/stable-baselines3
   - ç¹ç¹ï¼å®ç°å¤ç§å¼ºåå­¦ä¹ ç®æ³ï¼PPOãA2CãSACç­ï¼
   - éææ¹å¼ï¼ç¨äºå¼ºåå­¦ä¹ è°ä»å³?

5. **scikit-learn** - æºå¨å­¦ä¹ ?
   - GitHub: https://github.com/scikit-learn/scikit-learn
   - ç¹ç¹ï¼å¸åºç¯å¢åç±»ãç¹å¾å·¥ç¨ãæ¨¡åè¯?
   - éææ¹å¼ï¼ç¨äºå¸åºç¶æè¯å«åé¢æµ

6. **TA-Lib** - ææ¯åæåº
   - GitHub: https://github.com/mrjbq7/ta-lib
   - ç¹ç¹ï¼ææ¯ææ è®¡ç®ï¼ç¨äºç­ç¥ç¹å¾æå
   - éææ¹å¼ï¼ç¨äºå¸åºç¹å¾å·¥?

### 7.3 æ°æ®ä¸å¯è§å

7. **yfinance** - éèè´¢ç»æ°æ®æ¥å£
   - GitHub: https://github.com/ranaroussi/yfinance
   - ç¹ç¹ï¼åè´¹å¸åºæ°æ®è·?
   - éææ¹å¼ï¼ç¨äºè·åå®æ¶å¸åºæ°?

8. **Plotly/Dash** - äº¤äºå¼å¯è§å
   - GitHub: https://github.com/plotly/plotly.py
   - ç¹ç¹ï¼åå»ºäº¤äºå¼ä¼åç»æå¯è§?
   - éææ¹å¼ï¼ç¨äºWebæ¥åçæ

### 7.4 åèå®ç°é¡¹?

9. **Qlib** - å¾®è½¯éåæèµå¹³å°
   - GitHub: https://github.com/microsoft/qlib
   - ç¹ç¹ï¼å®æ´çéåç ç©¶æ¡æ¶ï¼åå«ç»åä¼åæ¨¡?
   - åèä»·å¼ï¼æ¶æè®¾è®¡ãæ¨¡åç»?

10. **QuantConnect** - å¼æºéåå¹³?
    - GitHub: https://github.com/QuantConnect/Lean
    - ç¹ç¹ï¼å®æ´çéåäº¤æç³»ç»ï¼åå«ç»åç®¡?
    - åèä»·å¼ï¼å®çéæãé£é©ç®¡?


## å«ãæ»ç»

æ¬èå¾è¯¦ç»è®¾è®¡äºç­ç¥ç»åä¼åç³»ç»çå®æ´ææ¯æ¹æ¡ï¼æ¶µçä»åºç¡ï¿?æ¹å·®ä¼åå°é«çº§é£é©å¹³ä»·æ¨¡åï¼åå°AIå¢å¼ºçå¨æè°ä»ç³»ç»ãç³»ç»è®¾è®¡éµå¾ªä»¥ä¸æ ¸å¿ååï¼

1. **å¼æºä¼åå?*ï¼æå¤§éåº¦å©ç¨æçå¼æºåºï¼åå°èªç ä»£ç é
2. **æ¨¡ååè®¾?*ï¼åä¼åç®æ³ç¬ç«å°è£ï¼æ¯æçµæ´»ç»ååæ©å±
3. **å®çåå¥½**ï¼ååèèäº¤æææ¬ãæµå¨æ§ãçç®¡éå¶ç­å®ççº¦æ
4. **é£é©å¯æ§**ï¼å¤å±æ¬¡é£é©é¢ç®ä½ç³»ï¼ç¡®ä¿ç»åé£é©å¨é¢è®¾èå´?
5. **AIå¢å¼º**ï¼å©ç¨å¼ºåå­¦ä¹ åæºå¨å­¦ä¹ ä¼åå¨æè°ä»å³?

å¯¹äºä¸ªäººå¼åèï¼ä¸æç¼ç¨ï¼èè¨ï¼æ¬ç³»ç»çä¸»è¦å¼åå·¥ä½å°æ¯ï¼
- **è¶åä»£ç ç¼å**ï¼å°åå¼æºæ¨¡åéæå°ç»ä¸æ¡æ¶ä¸­ï¼?0%å·¥ä½éï¼
- **éç½®ç®¡ç**ï¼è®¾è®¡çµæ´»çéç½®æä»¶ç³»ç»ï¼æ¯æä¸åä¼ååºæ¯ï¼?0%å·¥ä½éï¼
- **æµè¯éªè¯**ï¼éªè¯ä¼åç»æçæææ§åç¨³å®æ§ï¼?0%å·¥ä½éï¼
- **ææ¡£ä¸ç?*ï¼åå»ºç¨æ·åå¥½çå½ä»¤è¡åWebçé¢ï¼çº¦10%å·¥ä½éï¼

éè¿åé¶æ®µå®æ½ï¼24å¨å¼åå¨æï¼ï¼å¯ä»¥éæ­¥æå»ºåºä¸ä¸çº§çç­ç¥ç»åä¼åç³»ç»ï¼ä¸ºç­ç¥å·¥åæä¾å¼ºå¤§çç»åæå»ºè½åï¼æç»å®ç°å¤ç­ç¥ååä¼åãé£é©åæ£ãç»©ææåçæ ¸å¿ç®æ ?

*ææ¡£ç»æ - ç­ç¥ç»åä¼åç³»ç»ææ¯è?v1.0*

## åæ´åå²

| çæ¬ | æ¥æ | åæ´åå®¹ | åæ´äº?|
|------|------|----------|--------|
| v1.0.0 | 2026-04-01 | åå§çæ¬åå»º | é¦å¸­ææ¡£æ¶æå¸?|
| v1.0.1 | 2026-04-06 | è¡¥åYAMLå¤´é¨å­æ®µååæ´åå?| å®¡è®¡ç³»ç» |

---

**èå¾çæ¬**: v1.0.1 | **åå»ºæ¥æ**: 2026-04-01 | **ç¶æ?*: Active
