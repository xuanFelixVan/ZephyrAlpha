???---
module_id: SIMPLIFIED_RISK_BUDGET_SYSTEM_001
version: 1.0.0
spec_version: 1.0
status: Active
parent_doc: ../01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md
last_updated: 2026-04-03
created_date: 2026-04-03
layer: Layer 6 (����Ż�?? | ҵ��ܹ�: ����ʱ�����ںϼܹ�
index: SIMPLIFIED_RISK_BUDGET_SYSTEM_001
estimated_hours: 60h
review_status: Pending
reviewer: ��ϯ���������
review_date: 2026-04-03
owner: ����Ż��㸺����
standard_type: רҵ����������ͼ�ĵ����򻯰�??applicable_scope: ȫϵ??compliance_level: רҵ��׼
parent_document: ../INDEX.md
implementation_status: ��ƽ׶�
personal_development: true
ai_maintenance: true
simplified_version: true
---

# �򻯰涯̬����Ԥ��ϵͳ��??v1.0

> �������ϵͳ v5.3 - �򻯰涯̬����Ԥ��ϵͳ�ܹ���??> **����**: `RISK_BUDGET_001`
> **����ʱ??*: 60h��Լ1.5�ܣ�
> **���Ķ�λ**: �������Ԥ�� + VaR��أ�ʵ�ַ���Ԥ�㶯̬��??> **���˿�������??*: ????���ֿ��У��򻯰�??> **AIά���Ѷ�**: ??
---

## 1. ģ�����

### 1.1 ��˵??
**ԭ�����**����ˮʵ�֣�??- �������Ԥ����ϵ����ϲ� ??����????�ʲ��㣩
- ����VaR/CVaR�Ķ�̬���շ�??- ʵʱ���ռ������ƽ�����
- ����ʱ�䣺100h

**�򻯰����**�����˿�����??- ??**����**: �������Ԥ�㣨��ϲ�??- ??**����**: VaR�����Ԥ??- ??**����**: ��̬����Ԥ���??- ??**����**: ���η���Ԥ�㣨���Բ㡢�ʲ���??- ??**����**: ���ӵķ��մ��ݻ�??
**����??*??- ���˿�����Դ���ޣ�����ʵ�ֺ��Ĺ���
- �������Ԥ����������������տ�����??- ����ϵͳ���Ӷȣ�������ά��??
### 1.2 ҵ�񱳾����ֵ��??
**ҵ����??*??- ��ǰϵͳ���о�̬����Լ�����޷���̬��������Ԥ??- ȱ������Ԥ���ػ��ƣ����ռ��жȹ���
- ��Ҫʵ�ֻ���VaR�ķ���Ԥ�㶯̬��??
**��ֵ��??*??- ʵ�ֵ������Ԥ�㶯̬��??- ����VaR�ķ��ռ����Ԥ��
- ���տ��ƾ�ϸ����??0%
- ���ͼ����г����ռ���??
### 1.3 ������λ��ܹ����??
**Layer��λ**: Layer 6 - ����Ż��㣨���չ����㣩

**ģ�����**: ����ģ�飨�򻯰�??
**�ܹ���ɫ**: 
- ��Ϊ���չ����ĺ����������̬�������Ԥ??- ��Ϊ����Ż������룬�ṩ����Լ��
- ��Ϊ����Ԥ��ϵͳ����ط���ʹ����??
### 1.4 ���Ĺ����嵥

1. **VaR�������??*: �������VaR��ʵʱ��ط���ˮ??2. **����Ԥ�����**: ���ڲ��Ա��ַ������Ԥ��
3. **����ʹ�ü��**: ��ظ����Եķ���ʹ�����
4. **����Ԥ������**: �����ճ���ʱ����Ԥ��

---

## 2. �ܹ����

### 2.1 ϵͳ�ܹ�??
```
������������������������������������������������������������������������������������������������������������������������������������????               �򻯰涯̬����Ԥ��ϵͳ��??                        ??������������������������������������������������������������������������������������������������������������������������������������????                                                                ???? ����������������������������������������������������������������������������������������������������������������������?? ???? ??             ����??                                       ?? ???? ?? ����������������������?? ����������������������?? ����������������������?? ����������������������???? ???? ?? ??��ϼ�???? ??���Լ�Ч ?? ??�г����� ?? ??���ղ��� ???? ???? ?? ??         ?? ??����     ?? ??         ?? ??         ???? ???? ?? ����������������������?? ����������������������?? ����������������������?? ����������������������???? ???? ����������������������������������������������������������������������������������������������������������������������?? ????                         ??                                     ???? ����������������������������������������������������������������������������������������������������������������������?? ???? ??             VaR����??                                    ?? ???? ?? ����������������������������������������������������������������������������������������������������������?? ?? ???? ?? ?? Value at Risk Calculation                         ?? ?? ???? ?? ?? - Historical VaR                                  ?? ?? ???? ?? ?? - Parametric VaR                                  ?? ?? ???? ?? ?? - Confidence Level: 95%, 99%                      ?? ?? ???? ?? ����������������������������������������������������������������������������������������������������������?? ?? ???? ����������������������������������������������������������������������������������������������������������������������?? ????                         ??                                     ???? ����������������������������������������������������������������������������������������������������������������������?? ???? ??             ����Ԥ�����??                               ?? ???? ?? ����������������������������������������������������������������������������������������������������������?? ?? ???? ?? ?? Risk Budget Allocation                            ?? ?? ???? ?? ?? ���ڲ������ձ��ʡ������ʷ������Ԥ��               ?? ?? ???? ?? ����������������������������������������������������������������������������������������������������������?? ?? ???? ����������������������������������������������������������������������������������������������������������������������?? ????                         ??                                     ???? ����������������������������������������������������������������������������������������������������������������������?? ???? ??             ���ռ����Ԥ����                              ?? ???? ?? ����������������������?? ����������������������?? ����������������������??              ?? ???? ?? ??����ʹ�� ?? ??����Ԥ�� ?? ??���ձ��� ??              ?? ???? ?? ??���     ?? ??         ?? ??         ??              ?? ???? ?? ����������������������?? ����������������������?? ����������������������??              ?? ???? ����������������������������������������������������������������������������������������������������������������������?? ????                         ??                                     ???? ����������������������������������������������������������������������������������������������������������������������?? ???? ??             ���??                                       ?? ???? ?? ����������������������?? ����������������������?? ����������������������??              ?? ???? ?? ??����Ԥ�� ?? ??����Ԥ�� ?? ??���ձ��� ??              ?? ???? ?? ??���䷽�� ?? ??�ź�     ?? ??         ??              ?? ???? ?? ����������������������?? ����������������������?? ����������������������??              ?? ???? ����������������������������������������������������������������������������������������������������������������������?? ??������������������������������������������������������������������������������������������������������������������������������������??```

### 2.2 ��������??
```
��ϼ�??+ ���Լ�Ч����
    ??�������VaR
    ??�������Ԥ�㣨���ڲ��Ա��֣�
    ??��ط���ʹ�����
    ??���ɷ���Ԥ�����糬��??    ??������ձ����������??```

---

## 3. ����ģ�����

### 3.1 �򻯰����Ԥ��ϵͳ��SimplifiedRiskBudgetSystem??
```python
class SimplifiedRiskBudgetSystem:
    """
    �򻯰涯̬����Ԥ��ϵ??    
    ����: RISK_BUDGET_001-M01
    ְ��: �������Ԥ�㶯̬��������
    ����: ��ϼ�ֵ�����Լ�Ч��??    ���: ����Ԥ����䷽��������Ԥ??    """
    
    def __init__(self, config: RiskBudgetConfig):
        self.config = config
        self.var_calculator = VaRCalculator(config.var_config)
        self.risk_allocator = RiskAllocator(config.allocation_config)
        self.risk_monitor = RiskMonitor(config.monitor_config)
        
    def allocate_risk_budget(
        self,
        portfolio_value: float,
        target_risk: float,
        strategy_performances: Dict[str, StrategyPerformance]
    ) -> RiskBudgetAllocation:
        """
        �������Ԥ��
        
        Args:
            portfolio_value: ����ܼ�??            target_risk: Ŀ�����ˮƽ���껯������??            strategy_performances: �����Լ�Ч��??            
        Returns:
            RiskBudgetAllocation: ����Ԥ����䷽��
        """
        # 1. ������ϲ����Ԥ??        portfolio_risk_budget = self._calculate_portfolio_risk_budget(
            portfolio_value, target_risk
        )
        
        # 2. ������Է���Ԥ�㣨�򻯣��������ձ���??        strategy_risk_budgets = self.risk_allocator.allocate(
            portfolio_risk_budget, strategy_performances
        )
        
        # 3. �������Ԥ��ʹ�����
        risk_usage = self._calculate_risk_usage(
            strategy_risk_budgets, strategy_performances
        )
        
        return RiskBudgetAllocation(
            portfolio_budget=portfolio_risk_budget,
            strategy_budgets=strategy_risk_budgets,
            risk_usage=risk_usage,
            timestamp=datetime.now()
        )
    
    def monitor_risk_usage(
        self,
        current_allocation: RiskBudgetAllocation,
        current_positions: Dict[str, Position]
    ) -> RiskUsageReport:
        """
        ��ط���ʹ�����
        
        Args:
            current_allocation: ��ǰ����Ԥ�����
            current_positions: ��ǰ�ֲ�
            
        Returns:
            RiskUsageReport: ����ʹ�ñ���
        """
        # 1. ��������Ե�ǰ��??        current_risks = self._calculate_current_risks(current_positions)
        
        # 2. �������ʹ��??        risk_usage_rates = {
            strategy: current_risks[strategy] / budget
            for strategy, budget in current_allocation.strategy_budgets.items()
        }
        
        # 3. ʶ����ճ��޲���
        exceeded_strategies = [
            strategy for strategy, usage in risk_usage_rates.items()
            if usage > self.config.risk_usage_threshold
        ]
        
        # 4. ����Ԥ��
        alerts = []
        if exceeded_strategies:
            alerts.append(RiskAlert(
                level='WARNING',
                message=f'���ճ��޲���: {", ".join(exceeded_strategies)}',
                affected_strategies=exceeded_strategies
            ))
        
        return RiskUsageReport(
            current_risks=current_risks,
            risk_usage_rates=risk_usage_rates,
            exceeded_strategies=exceeded_strategies,
            alerts=alerts,
            timestamp=datetime.now()
        )
    
    def calculate_var(
        self,
        portfolio: Portfolio,
        confidence: float = 0.95,
        method: str = 'historical'
    ) -> VaRResult:
        """
        ����VaR
        
        Args:
            portfolio: Ͷ�����
            confidence: ����ˮƽ
            method: ���㷽��
            
        Returns:
            VaRResult: VaR������
        """
        return self.var_calculator.calculate(portfolio, confidence, method)
    
    def _calculate_portfolio_risk_budget(
        self,
        portfolio_value: float,
        target_risk: float
    ) -> float:
        """������ϲ����Ԥ??""
        # ����Ԥ�� = ��ϼ�??�� Ŀ�겨��??        return portfolio_value * target_risk
    
    def _calculate_risk_usage(
        self,
        strategy_budgets: Dict[str, float],
        strategy_performances: Dict[str, StrategyPerformance]
    ) -> Dict[str, float]:
        """�������ʹ�����"""
        risk_usage = {}
        for strategy, budget in strategy_budgets.items():
            current_risk = strategy_performances[strategy].current_volatility
            risk_usage[strategy] = current_risk / budget if budget > 0 else 0
        
        return risk_usage
```

### 3.2 VaR��������VaRCalculator??
```python
class VaRCalculator:
    """
    VaR����??    
    ����: RISK_BUDGET_001-M02
    ְ��: ����VaR��CVaR
    """
    
    def __init__(self, config: VaRConfig):
        self.config = config
        
    def calculate(
        self,
        portfolio: Portfolio,
        confidence: float = 0.95,
        method: str = 'historical'
    ) -> VaRResult:
        """
        ����VaR
        
        Args:
            portfolio: Ͷ�����
            confidence: ����ˮƽ
            method: ���㷽����historical/parametric??            
        Returns:
            VaRResult: VaR������
        """
        if method == 'historical':
            var = self._historical_var(portfolio, confidence)
        elif method == 'parametric':
            var = self._parametric_var(portfolio, confidence)
        else:
            raise ValueError(f"��֧�ֵķ���: {method}")
        
        # ����CVaR
        cvar = self._calculate_cvar(portfolio, confidence)
        
        return VaRResult(
            var=var,
            cvar=cvar,
            confidence=confidence,
            method=method,
            timestamp=datetime.now()
        )
    
    def _historical_var(
        self,
        portfolio: Portfolio,
        confidence: float
    ) -> float:
        """��ʷģ�ⷨVaR"""
        returns = portfolio.get_historical_returns()
        var = np.percentile(returns, (1 - confidence) * 100)
        return abs(var)
    
    def _parametric_var(
        self,
        portfolio: Portfolio,
        confidence: float
    ) -> float:
        """������VaR"""
        mu = portfolio.expected_return
        sigma = portfolio.volatility
        var = mu - sigma * norm.ppf(confidence)
        return abs(var)
    
    def _calculate_cvar(
        self,
        portfolio: Portfolio,
        confidence: float
    ) -> float:
        """����CVaR"""
        returns = portfolio.get_historical_returns()
        var = self._historical_var(portfolio, confidence)
        cvar = returns[returns <= -var].mean()
        return abs(cvar)
```

### 3.3 ���շ�������RiskAllocator??
```python
class RiskAllocator:
    """
    ���շ���??    
    ����: RISK_BUDGET_001-M03
    ְ��: ���ڲ��Ա��ַ������Ԥ��
    """
    
    def __init__(self, config: AllocationConfig):
        self.config = config
        
    def allocate(
        self,
        total_budget: float,
        strategy_performances: Dict[str, StrategyPerformance]
    ) -> Dict[str, float]:
        """
        �������Ԥ��
        
        Args:
            total_budget: �ܷ���Ԥ??            strategy_performances: �����Լ�Ч��??            
        Returns:
            Dict[str, float]: �����Է���Ԥ??        """
        # �򻯷������������ձ��ʷ���
        sharpe_ratios = {
            strategy: perf.sharpe_ratio
            for strategy, perf in strategy_performances.items()
        }
        
        # ��һ�����ձ�??        total_sharpe = sum(max(sr, 0) for sr in sharpe_ratios.values())
        
        if total_sharpe == 0:
            # ����������ձ��ʶ�Ϊ����ƽ����??            n_strategies = len(strategy_performances)
            return {s: total_budget / n_strategies for s in strategy_performances}
        
        # �������Ԥ��
        allocations = {}
        for strategy, sharpe in sharpe_ratios.items():
            if sharpe > 0:
                allocations[strategy] = total_budget * (sharpe / total_sharpe)
            else:
                allocations[strategy] = 0  # ���ձ���Ϊ���Ĳ��Բ��������Ԥ��
        
        return allocations
```

### 3.4 �����ඨ??
```python
@dataclass
class RiskBudgetConfig:
    """����Ԥ��ϵͳ����"""
    var_config: VaRConfig
    allocation_config: AllocationConfig
    monitor_config: MonitorConfig
    risk_usage_threshold: float = 0.9  # ����ʹ������??    rebalance_threshold: float = 0.2  # ��ƽ����??    
@dataclass
class VaRConfig:
    """VaR��������"""
    confidence_levels: List[float] = [0.95, 0.99]
    default_method: str = 'historical'
    lookback_period: int = 252  # �ؿ��ڣ��죩
    
@dataclass
class AllocationConfig:
    """���շ�������"""
    allocation_method: str = 'sharpe_ratio'  # ���䷽��
    min_budget_ratio: float = 0.05  # ��СԤ���??    max_budget_ratio: float = 0.40  # ���Ԥ���??```

---

## 4. ����ģ�Ͷ���

### 4.1 ��������ģ��

```python
@dataclass
class StrategyPerformance:
    """���Լ�Ч����"""
    strategy_id: str
    returns: pd.Series
    sharpe_ratio: float
    volatility: float
    max_drawdown: float
    current_volatility: float  # ��ǰ����??```

### 4.2 �������ģ��

```python
@dataclass
class RiskBudgetAllocation:
    """����Ԥ����䷽��"""
    portfolio_budget: float
    strategy_budgets: Dict[str, float]
    risk_usage: Dict[str, float]
    timestamp: datetime
    
@dataclass
class RiskUsageReport:
    """����ʹ�ñ���"""
    current_risks: Dict[str, float]
    risk_usage_rates: Dict[str, float]
    exceeded_strategies: List[str]
    alerts: List[RiskAlert]
    timestamp: datetime
    
@dataclass
class VaRResult:
    """VaR������"""
    var: float
    cvar: float
    confidence: float
    method: str
    timestamp: datetime
```

---

## 5. ���ɷ���

### 5.1 ������Ż�������

```python
class PortfolioOptimizer:
    """����Ż��������ɷ���Ԥ��??""
    
    def __init__(self, risk_budget_system: SimplifiedRiskBudgetSystem):
        self.risk_budget_system = risk_budget_system
        
    def optimize_with_risk_budget(
        self,
        portfolio: Portfolio,
        target_risk: float
    ) -> OptimizationResult:
        """����Ԥ��Լ���������??""
        # 1. �������Ԥ��
        budget_allocation = self.risk_budget_system.allocate_risk_budget(
            portfolio.value, target_risk, portfolio.strategy_performances
        )
        
        # 2. �ڷ���Ԥ��Լ�����Ż�
        optimized_weights = self._optimize_under_budget_constraint(
            budget_allocation
        )
        
        return OptimizationResult(
            weights=optimized_weights,
            risk_budget=budget_allocation
        )
```

---

## 6. ʵʩ·��??
### 6.1 �����׶Σ�1.5�ܣ�

**Week 1: ���Ĺ��ܿ�??*
- Day 1-2: VaR����??- Day 3-4: ���շ���??- Day 5: ���ռ��ģ��

**Week 2: �������??*
- Day 1-2: ϵͳ����
- Day 3: ��Ԫ����
- Day 4: ���ɲ���
- Day 5: �ĵ���д

### 6.2 ���??
| ���??| ʱ�� | ����??| ���ձ�׼ |
|--------|------|--------|----------|
| **M1: VaR�������** | Day 2 | VaR����??| VaR����׼ȷ |
| **M2: ���շ������** | Day 4 | ���շ���??| ������� |
| **M3: ������** | Day 5 | ���ռ��ģ�� | ������� |
| **M4: �������** | Day 7 | ����ϵͳ | ���нӿ���??|
| **M5: ����ͨ��** | Day 8 | ���Ա��� | ���в���ͨ�� |

---

## 7. Ԥ����������

### 7.1 ��������

| ָ�� | ��ǰˮƽ | Ŀ��ˮƽ | �������� |
|------|---------|---------|---------|
| **���տ��ƾ�ϸ??* | 70% | 90% | +20% |
| **����Ԥ�㶯̬��??* | ??| ??| �������� |
| **����Ԥ����ʱ??* | ??| ??| ����2??|

### 7.2 ������??
- ??ʵ����ˮ�����������򻯰棩����̬����Ԥ??- ??�������տ��ƾ�ϸ??- ??��������Ԥ������
- ??Ϊ����Ż��ṩ����Լ??
---

## 8. ��ԭ���??
| ��??| ԭ�棨��ˮ�� | �򻯰� | ˵�� |
|------|------------|--------|------|
| **����Ԥ����** | ���� | ���� | �򻯼�??|
| **���ն���** | VaR/CVaR | VaR/CVaR | �������� |
| **��̬��??* | ʵʱ | �ն� | ����Ƶ�� |
| **����ʱ??* | 100h | 60h | ����40% |
| **ά������??* | ??| ??| �����Ѷ� |

---

## ��¼

### A. �ο���??
1. **����Ԥ������**:
   - Qian, E. (2005). "Risk Parity Portfolios"

2. **VaR����**:
   - Jorion, P. (2006). "Value at Risk: The New Benchmark for Managing Financial Risk"


---

## 9. ���η���Ԥ����չ��ƣ���ǿ�棩

### 9.1 �������Ԥ����ϵ�ܹ�

`

                 ���η���Ԥ����ϵ�ܹ�                          

                                                                 
     
    Layer 1: ��ϲ����Ԥ�㣨Portfolio Risk Budget��          
    - �ܷ���Ԥ�����                                           
    - ����Է���Э��                                           
    - ��ϼ�VaR���                                            
     
                           ���մ���                             
     
    Layer 2: ���Բ����Ԥ�㣨Strategy Risk Budget��           
    - ���Է���Ԥ�����                                         
    - ���Լ����ת��                                           
    - ���Լ�VaR���                                            
     
                           ���մ���                             
     
    Layer 3: �ʲ������Ԥ�㣨Asset Risk Budget��              
    - ���ʲ���������                                           
    - �ʲ������ռ��                                           
    - �ֲַ��տ���                                             
     
                                                                 

`

### 9.2 ������չģ��

#### 9.2.1 ���η���Ԥ�������

`python
class MultiLayerRiskBudgetManager:
    """
    ���η���Ԥ�������
    
    ����: RISK_BUDGET_001-M04����չ��
    ְ��: �����������Ԥ����ϵ
    """
    
    def __init__(self, config: MultiLayerRiskBudgetConfig):
        self.config = config
        self.portfolio_budget_manager = PortfolioBudgetManager(config.portfolio_config)
        self.strategy_budget_manager = StrategyBudgetManager(config.strategy_config)
        self.asset_budget_manager = AssetBudgetManager(config.asset_config)
        self.risk_cascading_engine = RiskCascadingEngine(config.cascading_config)
        
    def allocate_multi_layer_budget(
        self,
        portfolio_value: float,
        target_risk: float,
        strategies: Dict[str, StrategyInfo],
        assets: Dict[str, AssetInfo]
    ) -> MultiLayerBudgetAllocation:
        """
        ������η���Ԥ��
        
        Args:
            portfolio_value: ����ܼ�ֵ
            target_risk: Ŀ�����ˮƽ
            strategies: ������Ϣ�ֵ�
            assets: �ʲ���Ϣ�ֵ�
            
        Returns:
            MultiLayerBudgetAllocation: ����Ԥ�������
        """
        # Layer 1: ��ϲ����Ԥ��
        portfolio_budget = self.portfolio_budget_manager.calculate_budget(
            portfolio_value, target_risk
        )
        
        # Layer 2: ���Բ����Ԥ�㣨���մ��ݣ�
        strategy_budgets = self.risk_cascading_engine.cascade_to_strategies(
            portfolio_budget, strategies
        )
        
        # Layer 3: �ʲ������Ԥ�㣨���մ��ݣ�
        asset_budgets = self.risk_cascading_engine.cascade_to_assets(
            strategy_budgets, assets
        )
        
        return MultiLayerBudgetAllocation(
            portfolio_budget=portfolio_budget,
            strategy_budgets=strategy_budgets,
            asset_budgets=asset_budgets,
            cascading_log=self.risk_cascading_engine.get_cascading_log(),
            timestamp=datetime.now()
        )
    
    def monitor_multi_layer_risk(
        self,
        allocation: MultiLayerBudgetAllocation,
        current_positions: Dict[str, Position]
    ) -> MultiLayerRiskReport:
        """
        ��ض��η���ʹ�����
        
        Args:
            allocation: ��ǰԤ�����
            current_positions: ��ǰ�ֲ�
            
        Returns:
            MultiLayerRiskReport: ���η��ձ���
        """
        # ��ظ������ʹ��
        portfolio_usage = self._monitor_portfolio_risk(allocation, current_positions)
        strategy_usage = self._monitor_strategy_risk(allocation, current_positions)
        asset_usage = self._monitor_asset_risk(allocation, current_positions)
        
        # ���ɶ���Ԥ��
        alerts = self._generate_multi_layer_alerts(
            portfolio_usage, strategy_usage, asset_usage
        )
        
        return MultiLayerRiskReport(
            portfolio_usage=portfolio_usage,
            strategy_usage=strategy_usage,
            asset_usage=asset_usage,
            alerts=alerts,
            timestamp=datetime.now()
        )
`

#### 9.2.2 ���մ�������

`python
class RiskCascadingEngine:
    """
    ���մ�������
    
    ����: RISK_BUDGET_001-M05����չ��
    ְ��: ʵ�ַ���Ԥ���ڲ�ͬ��μ�Ĵ���
    """
    
    def __init__(self, config: CascadingConfig):
        self.config = config
        self.cascading_log = []
        
    def cascade_to_strategies(
        self,
        portfolio_budget: PortfolioBudget,
        strategies: Dict[str, StrategyInfo]
    ) -> Dict[str, StrategyBudget]:
        """
        ����ϲ����Ԥ�㴫�ݵ����Բ�
        
        Args:
            portfolio_budget: ��ϲ�Ԥ��
            strategies: ������Ϣ
            
        Returns:
            Dict[str, StrategyBudget]: ���Բ�Ԥ��
        """
        # ���ڲ��Է��չ��׶ȷ���
        total_risk_contribution = sum(s.risk_contribution for s in strategies.values())
        
        strategy_budgets = {}
        for strategy_id, strategy_info in strategies.items():
            # ������Է���Ԥ��
            risk_share = strategy_info.risk_contribution / total_risk_contribution
            strategy_budget = portfolio_budget.total_risk * risk_share
            
            # Ӧ��Լ��
            strategy_budget = np.clip(
                strategy_budget,
                self.config.min_strategy_budget,
                self.config.max_strategy_budget
            )
            
            strategy_budgets[strategy_id] = StrategyBudget(
                strategy_id=strategy_id,
                risk_budget=strategy_budget,
                risk_contribution=strategy_info.risk_contribution,
                sharpe_ratio=strategy_info.sharpe_ratio
            )
            
            # ��¼������־
            self.cascading_log.append({
                'from': 'portfolio',
                'to': f'strategy_{strategy_id}',
                'budget': strategy_budget,
                'timestamp': datetime.now()
            })
        
        return strategy_budgets
    
    def cascade_to_assets(
        self,
        strategy_budgets: Dict[str, StrategyBudget],
        assets: Dict[str, AssetInfo]
    ) -> Dict[str, AssetBudget]:
        """
        �����Բ����Ԥ�㴫�ݵ��ʲ���
        
        Args:
            strategy_budgets: ���Բ�Ԥ��
            assets: �ʲ���Ϣ
            
        Returns:
            Dict[str, AssetBudget]: �ʲ���Ԥ��
        """
        asset_budgets = {}
        
        for asset_id, asset_info in assets.items():
            # �ҵ��ʲ���������
            strategy_id = asset_info.strategy_id
            if strategy_id not in strategy_budgets:
                continue
                
            strategy_budget = strategy_budgets[strategy_id]
            
            # �����ʲ�Ȩ�ط������Ԥ��
            asset_weight = asset_info.weight
            asset_budget_value = strategy_budget.risk_budget * asset_weight
            
            # Ӧ�õ��ʲ�����
            asset_budget_value = min(
                asset_budget_value,
                self.config.max_single_asset_risk
            )
            
            asset_budgets[asset_id] = AssetBudget(
                asset_id=asset_id,
                strategy_id=strategy_id,
                risk_budget=asset_budget_value,
                position_limit=self._calculate_position_limit(asset_budget_value, asset_info)
            )
            
            # ��¼������־
            self.cascading_log.append({
                'from': f'strategy_{strategy_id}',
                'to': f'asset_{asset_id}',
                'budget': asset_budget_value,
                'timestamp': datetime.now()
            })
        
        return asset_budgets
`

#### 9.2.3 ���η��ռ����

`python
class MultiLayerRiskMonitor:
    """
    ���η��ռ����
    
    ����: RISK_BUDGET_001-M06����չ��
    ְ��: ����������Ԥ��ʹ�����
    """
    
    def __init__(self, config: MultiLayerMonitorConfig):
        self.config = config
        self.alert_generator = MultiLayerAlertGenerator(config.alert_config)
        
    def monitor_all_layers(
        self,
        allocation: MultiLayerBudgetAllocation,
        positions: Dict[str, Position],
        market_data: pd.DataFrame
    ) -> MultiLayerMonitoringResult:
        """
        ������в�εķ���ʹ��
        
        Args:
            allocation: Ԥ�����
            positions: �ֲ���Ϣ
            market_data: �г�����
            
        Returns:
            MultiLayerMonitoringResult: ��ؽ��
        """
        # Layer 1: ��ϲ���
        portfolio_metrics = self._monitor_portfolio_layer(
            allocation.portfolio_budget, positions, market_data
        )
        
        # Layer 2: ���Բ���
        strategy_metrics = self._monitor_strategy_layer(
            allocation.strategy_budgets, positions, market_data
        )
        
        # Layer 3: �ʲ�����
        asset_metrics = self._monitor_asset_layer(
            allocation.asset_budgets, positions, market_data
        )
        
        # ���ɶ���Ԥ��
        alerts = self.alert_generator.generate_alerts(
            portfolio_metrics, strategy_metrics, asset_metrics
        )
        
        return MultiLayerMonitoringResult(
            portfolio_metrics=portfolio_metrics,
            strategy_metrics=strategy_metrics,
            asset_metrics=asset_metrics,
            alerts=alerts,
            risk_efficiency=self._calculate_risk_efficiency(
                portfolio_metrics, strategy_metrics, asset_metrics
            ),
            timestamp=datetime.now()
        )
    
    def _monitor_portfolio_layer(
        self,
        portfolio_budget: PortfolioBudget,
        positions: Dict[str, Position],
        market_data: pd.DataFrame
    ) -> PortfolioRiskMetrics:
        """�����ϲ����"""
        # ���㵱ǰ���VaR
        current_var = self._calculate_portfolio_var(positions, market_data)
        
        # �������ʹ����
        risk_usage_rate = current_var / portfolio_budget.total_risk
        
        return PortfolioRiskMetrics(
            current_var=current_var,
            budget_var=portfolio_budget.total_risk,
            risk_usage_rate=risk_usage_rate,
            status=self._determine_status(risk_usage_rate)
        )
    
    def _monitor_strategy_layer(
        self,
        strategy_budgets: Dict[str, StrategyBudget],
        positions: Dict[str, Position],
        market_data: pd.DataFrame
    ) -> Dict[str, StrategyRiskMetrics]:
        """��ز��Բ����"""
        strategy_metrics = {}
        
        for strategy_id, budget in strategy_budgets.items():
            # ������Ե�ǰ����
            strategy_positions = {
                k: v for k, v in positions.items() 
                if v.strategy_id == strategy_id
            }
            current_risk = self._calculate_strategy_risk(
                strategy_positions, market_data
            )
            
            # �������ʹ����
            risk_usage_rate = current_risk / budget.risk_budget
            
            strategy_metrics[strategy_id] = StrategyRiskMetrics(
                strategy_id=strategy_id,
                current_risk=current_risk,
                budget_risk=budget.risk_budget,
                risk_usage_rate=risk_usage_rate,
                status=self._determine_status(risk_usage_rate)
            )
        
        return strategy_metrics
    
    def _monitor_asset_layer(
        self,
        asset_budgets: Dict[str, AssetBudget],
        positions: Dict[str, Position],
        market_data: pd.DataFrame
    ) -> Dict[str, AssetRiskMetrics]:
        """����ʲ������"""
        asset_metrics = {}
        
        for asset_id, budget in asset_budgets.items():
            if asset_id not in positions:
                continue
                
            position = positions[asset_id]
            
            # �����ʲ���ǰ����
            current_risk = self._calculate_asset_risk(position, market_data)
            
            # �������ʹ����
            risk_usage_rate = current_risk / budget.risk_budget
            
            asset_metrics[asset_id] = AssetRiskMetrics(
                asset_id=asset_id,
                current_risk=current_risk,
                budget_risk=budget.risk_budget,
                position_value=position.market_value,
                risk_usage_rate=risk_usage_rate,
                status=self._determine_status(risk_usage_rate)
            )
        
        return asset_metrics
`

### 9.3 ��չ������

`python
@dataclass
class MultiLayerRiskBudgetConfig:
    """���η���Ԥ������"""
    portfolio_config: PortfolioBudgetConfig
    strategy_config: StrategyBudgetConfig
    asset_config: AssetBudgetConfig
    cascading_config: CascadingConfig
    monitor_config: MultiLayerMonitorConfig
    
    # ȫ��Լ��
    max_portfolio_var: float = 0.15  # ������VaR���껯��
    max_strategy_var: float = 0.05  # ���������VaR
    max_asset_var: float = 0.02  # ���ʲ����VaR
    
    # ���մ��ݲ���
    cascading_method: str = 'risk_contribution'  # ���ݷ���
    cascading_frequency: str = 'daily'  # ����Ƶ��

@dataclass
class CascadingConfig:
    """���մ�������"""
    min_strategy_budget: float = 0.01  # ��С����Ԥ�㣨ռ��Ԥ�������
    max_strategy_budget: float = 0.30  # ������Ԥ��
    max_single_asset_risk: float = 0.02  # ���ʲ�������
    cascading_smoothing: float = 0.3  # ����ƽ��ϵ��
`

### 9.4 ��չ����ģ��

`python
@dataclass
class MultiLayerBudgetAllocation:
    """����Ԥ�������"""
    portfolio_budget: PortfolioBudget
    strategy_budgets: Dict[str, StrategyBudget]
    asset_budgets: Dict[str, AssetBudget]
    cascading_log: List[Dict]
    timestamp: datetime

@dataclass
class PortfolioBudget:
    """��ϲ�Ԥ��"""
    total_risk: float  # �ܷ���Ԥ��
    target_var: float  # Ŀ��VaR
    risk_contribution: Dict[str, float]  # �����Է��չ���

@dataclass
class StrategyBudget:
    """���Բ�Ԥ��"""
    strategy_id: str
    risk_budget: float  # ����Ԥ��
    risk_contribution: float  # ���չ��׶�
    sharpe_ratio: float  # ���ձ���

@dataclass
class AssetBudget:
    """�ʲ���Ԥ��"""
    asset_id: str
    strategy_id: str
    risk_budget: float  # ����Ԥ��
    position_limit: float  # �ֲ�����

@dataclass
class MultiLayerRiskReport:
    """���η��ձ���"""
    portfolio_usage: PortfolioRiskMetrics
    strategy_usage: Dict[str, StrategyRiskMetrics]
    asset_usage: Dict[str, AssetRiskMetrics]
    alerts: List[MultiLayerAlert]
    timestamp: datetime
`

### 9.5 Ԥ�����棨��չ�棩

| ָ�� | �򻯰� | ��չ�� | �������� |
|------|--------|--------|---------|
| **���տ��ƾ�ϸ��** | 90% | 95% | +5% |
| **����Ԥ����** | ���� | ���� | +200% |
| **���մ��ݻ���** | �� | �� | �������� |
| **���ռ��ά��** | 1�� | 3�� | +200% |
| **����Ԥ��׼ȷ��** | 85% | 95% | +10% |
---

**��ͼ�汾**: v1.0 | **��������**: 2026-04-03 | **״??*: Final | **�򻯰�**: ??| **��һ??*: ����������д


