---
module_id: IMPL_STRESS_TESTING_BP_001
version: 1.0.1
spec_version: 1.0
status: Active
parent_doc: ../01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md
last_updated: 2026-04-06
created_date: 2026-04-03
layer: "Layer 7 (风险控制层)"
index: STRESS_TESTING_SYSTEM_001
estimated_hours: 80h
estimated_effort: 2周
review_status: Pending
reviewer: 首席技术评审官
review_date: 2026-04-03
owner: 组合优化层负责人
standard_type: 专业量化机构蓝图文档
applicable_scope: 全系统
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
open_source_dependency: numpy, pandas, scipy
priority: P1
---
????---
module_id: STRESS_TESTING_SYSTEM_001
version: 1.0.0
spec_version: 1.0
status: Active
parent_doc: ../01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md
last_updated: 2026-04-03
created_date: 2026-04-03
layer: Layer 6 (����Ż�?? | ҵ��ܹ�: ����ʱ�����ںϼܹ�
index: STRESS_TESTING_SYSTEM_001
estimated_hours: 80h
review_status: Pending
reviewer: ��ϯ���������
review_date: 2026-04-03
owner: ����Ż��㸺����
standard_type: רҵ����������ͼ�ĵ�
applicable_scope: ȫϵ??compliance_level: רҵ��׼
parent_document: ../INDEX.md
implementation_status: ��ƽ׶�
personal_development: true
ai_maintenance: true
---

# ѹ���������龰����ϵͳ��??v1.0

> �������ϵͳ v5.3 - ѹ���������龰����ϵͳ�ܹ���??> **����**: `STRESS_TEST_001`
> **����ʱ??*: 80h��Լ2�ܣ�
> **���Ķ�λ**: ���������г��µ���Ϸ��գ��ṩ����Ӧ��Ԥ??> **���˿�������??*: ???? ��ȫ����
> **AIά���Ѷ�**: ??
---

## 1. ģ�����

### 1.1 ҵ�񱳾����ֵ��??
**ҵ����??*??- ��ǰϵͳȱ��ϵͳ��ѹ�����Կ�??- �޷����������г��µ���Ϸ���
- ȱ����ʷΣ���¼����龰�ط���??- �޷���Ӧ��Ԥ���ͷ��ջ����ʩ

**��ֵ��??*??- ʵ����ʷ�龰�ط�??008����Σ��??020����ȣ�
- �ṩ���ؿ���ѹ����������
- ���������г��µ���ϱ���
- ���ɷ���Ӧ��Ԥ���ͻ����ʩ

**���˿�����??*??- ??ʵ�ּ򵥣���ʷ�龰�ط� + ���ؿ���ģ��
- ??���ݹ�������ʷΣ���¼����ݹ����ɵ�
- ??ά���򵥣����ڸ����龰�⼴??- ??��ֵ��ȷ�����������ر�����

### 1.2 ������λ��ܹ����??
**Layer��λ**: Layer 6 - ����Ż��㣨���չ����㣩

**ģ�����**: ����ģ��

**�ܹ���ɫ**: 
- ��Ϊ���չ����ĺ�����������������г�����
- ��Ϊ����Ż������룬�ṩ����Լ��
- ��Ϊ����Ӧ��Ԥ���Ļ������ṩ����֧??
### 1.3 ���Ĺ����嵥

1. **��ʷ�龰�ط�**: �ط���ʷΣ���¼���������ϱ�??2. **���ؿ���ѹ������**: ģ�⼫���г��龰
3. **����ָ�����**: ����VaR��CVaR�����س��ȷ���ָ��
4. **Ӧ��Ԥ����??*: ���ɷ��ջ����ʩ��Ӧ��Ԥ??
---

## 2. �ܹ����

### 2.1 ϵͳ�ܹ�??
```
������������������������������������������������������������������������������������������������������������������������������������????                 ѹ���������龰����ϵͳ��??                      ??������������������������������������������������������������������������������������������������������������������������������������????                                                                ???? ����������������������������������������������������������������������������������������������������������������������?? ???? ??             ����??                                       ?? ???? ?? ����������������������?? ����������������������?? ����������������������?? ����������������������???? ???? ?? ??Ͷ����� ?? ??��ʷ���� ?? ??�龰??  ?? ??���ղ��� ???? ???? ?? ??����     ?? ??         ?? ??         ?? ??         ???? ???? ?? ����������������������?? ����������������������?? ����������������������?? ����������������������???? ???? ����������������������������������������������������������������������������������������������������������������������?? ????                         ??                                     ???? ����������������������������������������������������������������������������������������������������������������������?? ???? ??             ��ʷ�龰�ط�??                               ?? ???? ?? ����������������������������������������������������������������������������������������������������������?? ?? ???? ?? ?? Historical Scenario Replay                        ?? ?? ???? ?? ?? - 2008 Financial Crisis                          ?? ?? ???? ?? ?? - 2020 COVID-19 Pandemic                         ?? ?? ???? ?? ?? - 2022 Interest Rate Hike                        ?? ?? ???? ?? ����������������������������������������������������������������������������������������������������������?? ?? ???? ����������������������������������������������������������������������������������������������������������������������?? ????                         ??                                     ???? ����������������������������������������������������������������������������������������������������������������������?? ???? ??             ���ؿ���ģ��??                               ?? ???? ?? ����������������������������������������������������������������������������������������������������������?? ?? ???? ?? ?? Monte Carlo Simulation Engine                     ?? ?? ???? ?? ?? - ���˲�������??                                 ?? ?? ???? ?? ?? - �����ͻ����??                                 ?? ?? ???? ?? ?? - ������Σ����??                                 ?? ?? ???? ?? ����������������������������������������������������������������������������������������������������������?? ?? ???? ����������������������������������������������������������������������������������������������������������������������?? ????                         ??                                     ???? ����������������������������������������������������������������������������������������������������������������������?? ???? ??             ����ָ�����??                               ?? ???? ?? ����������������������?? ����������������������?? ����������������������?? ����������������������???? ???? ?? ??VaR����  ?? ??CVaR���� ?? ??����???? ??ѹ��VaR  ???? ???? ?? ??         ?? ??         ?? ??����     ?? ??����     ???? ???? ?? ����������������������?? ����������������������?? ����������������������?? ����������������������???? ???? ����������������������������������������������������������������������������������������������������������������������?? ????                         ??                                     ???? ����������������������������������������������������������������������������������������������������������������������?? ???? ??             ���??                                       ?? ???? ?? ����������������������?? ����������������������?? ����������������������?? ����������������������???? ???? ?? ??���ձ��� ?? ??Ӧ��Ԥ???? ??����Ԥ�� ?? ??�����ʩ ???? ???? ?? ??         ?? ??         ?? ??         ?? ??         ???? ???? ?? ����������������������?? ����������������������?? ����������������������?? ����������������������???? ???? ����������������������������������������������������������������������������������������������������������������������?? ??������������������������������������������������������������������������������������������������������������������������������������??```

### 2.2 ��������??
```
Ͷ���������
    ??ѡ��������ͣ���ʷ��??���ؿ���/�����龰??    ??ִ��ѹ������
    ??�������ָ�꣨VaR/CVaR/���س���
    ??���ɷ��ձ���
    ??���Ӧ��Ԥ���뻺���ʩ
```

---

## 3. ����ģ�����

### 3.1 ѹ������ϵͳ��StressTestingSystem??
```python
class StressTestingSystem:
    """
    ѹ������ϵͳ
    
    ����: STRESS_TEST_001-M01
    ְ��: ���������г��µ���Ϸ���
    ����: Ͷ����ϡ���ʷ���ݡ��龰��
    ���: ѹ�����Խ�������ձ��桢Ӧ��Ԥ??    """
    
    def __init__(self, config: StressTestConfig):
        self.config = config
        self.scenario_library = HistoricalScenarioLibrary(config.scenario_config)
        self.monte_carlo_engine = MonteCarloEngine(config.mc_config)
        self.risk_calculator = RiskCalculator()
        
    def run_stress_test(
        self,
        portfolio: Portfolio,
        test_type: str = 'historical',
        scenarios: Optional[List[str]] = None
    ) -> StressTestResult:
        """
        ִ��ѹ������
        
        Args:
            portfolio: Ͷ�����
            test_type: �������ͣ�historical/monte_carlo/extreme??            scenarios: ָ���龰�б�����ѡ��
            
        Returns:
            StressTestResult: ѹ�����Խ��
        """
        if test_type == 'historical':
            results = self._run_historical_scenarios(portfolio, scenarios)
        elif test_type == 'monte_carlo':
            results = self._run_monte_carlo_simulation(portfolio)
        elif test_type == 'extreme':
            results = self._run_extreme_scenarios(portfolio)
        else:
            raise ValueError(f"��֧�ֵĲ�������: {test_type}")
        
        # �������ָ��
        risk_metrics = self._calculate_risk_metrics(results)
        
        # ���ɷ��ձ���
        risk_report = self._generate_risk_report(results, risk_metrics)
        
        # ����Ӧ��Ԥ??        contingency_plan = self._generate_contingency_plan(results, risk_metrics)
        
        return StressTestResult(
            test_type=test_type,
            scenario_results=results,
            risk_metrics=risk_metrics,
            risk_report=risk_report,
            contingency_plan=contingency_plan,
            timestamp=datetime.now()
        )
    
    def run_historical_scenario(
        self,
        portfolio: Portfolio,
        scenario_name: str
    ) -> ScenarioResult:
        """
        ִ�е�����ʷ�龰�ط�
        
        Args:
            portfolio: Ͷ�����
            scenario_name: �龰���ƣ���'2008_crisis'??            
        Returns:
            ScenarioResult: �龰�طŽ��
        """
        # 1. ������ʷ�龰����
        scenario_data = self.scenario_library.load_scenario(scenario_name)
        
        # 2. Ӧ���龰����??        portfolio_impact = self._apply_scenario_to_portfolio(
            portfolio, scenario_data
        )
        
        # 3. �������ָ��
        risk_metrics = self.risk_calculator.calculate(
            portfolio_impact.returns
        )
        
        return ScenarioResult(
            scenario_name=scenario_name,
            portfolio_impact=portfolio_impact,
            risk_metrics=risk_metrics,
            worst_day=portfolio_impact.worst_day,
            recovery_period=portfolio_impact.recovery_period
        )
    
    def run_monte_carlo_simulation(
        self,
        portfolio: Portfolio,
        n_simulations: int = 10000,
        time_horizon: int = 252
    ) -> MonteCarloResult:
        """
        ִ�����ؿ���ģ��
        
        Args:
            portfolio: Ͷ�����
            n_simulations: ģ�����
            time_horizon: ʱ�䷶Χ����??            
        Returns:
            MonteCarloResult: ���ؿ���ģ����
        """
        # 1. ������ϲ���
        portfolio_params = self._estimate_portfolio_parameters(portfolio)
        
        # 2. ����ģ��·��
        simulated_paths = self.monte_carlo_engine.simulate(
            portfolio_params, n_simulations, time_horizon
        )
        
        # 3. �������ָ��
        risk_metrics = self._calculate_mc_risk_metrics(simulated_paths)
        
        # 4. ʶ�𼫶��龰
        extreme_scenarios = self._identify_extreme_scenarios(simulated_paths)
        
        return MonteCarloResult(
            simulated_paths=simulated_paths,
            risk_metrics=risk_metrics,
            extreme_scenarios=extreme_scenarios,
            confidence_intervals=self._calculate_confidence_intervals(simulated_paths)
        )
    
    def generate_var_report(
        self,
        portfolio: Portfolio,
        confidence_levels: List[float] = [0.95, 0.99]
    ) -> VaRReport:
        """
        ����VaR����
        
        Args:
            portfolio: Ͷ�����
            confidence_levels: ����ˮƽ�б�
            
        Returns:
            VaRReport: VaR����
        """
        var_results = {}
        
        for confidence in confidence_levels:
            var = self.risk_calculator.calculate_var(
                portfolio, confidence
            )
            cvar = self.risk_calculator.calculate_cvar(
                portfolio, confidence
            )
            
            var_results[confidence] = {
                'VaR': var,
                'CVaR': cvar
            }
        
        return VaRReport(
            var_results=var_results,
            historical_var=self._calculate_historical_var(portfolio),
            parametric_var=self._calculate_parametric_var(portfolio),
            monte_carlo_var=self._calculate_monte_carlo_var(portfolio)
        )
    
    def _run_historical_scenarios(
        self,
        portfolio: Portfolio,
        scenarios: Optional[List[str]]
    ) -> Dict[str, ScenarioResult]:
        """������ʷ�龰�ط�"""
        if scenarios is None:
            scenarios = self.scenario_library.get_default_scenarios()
        
        results = {}
        for scenario_name in scenarios:
            results[scenario_name] = self.run_historical_scenario(
                portfolio, scenario_name
            )
        
        return results
    
    def _run_monte_carlo_simulation(
        self,
        portfolio: Portfolio
    ) -> MonteCarloResult:
        """�������ؿ���ģ��"""
        return self.run_monte_carlo_simulation(
            portfolio,
            self.config.mc_config.n_simulations,
            self.config.mc_config.time_horizon
        )
    
    def _run_extreme_scenarios(
        self,
        portfolio: Portfolio
    ) -> Dict[str, ScenarioResult]:
        """���м����龰����"""
        extreme_scenarios = {
            'market_crash': self._simulate_market_crash(portfolio),
            'volatility_spike': self._simulate_volatility_spike(portfolio),
            'correlation_breakdown': self._simulate_correlation_breakdown(portfolio),
            'liquidity_crisis': self._simulate_liquidity_crisis(portfolio)
        }
        
        return extreme_scenarios
    
    def _generate_contingency_plan(
        self,
        results: Dict,
        risk_metrics: RiskMetrics
    ) -> ContingencyPlan:
        """����Ӧ��Ԥ??""
        # ʶ����Ҫ����
        main_risks = self._identify_main_risks(results, risk_metrics)
        
        # ���ɻ����ʩ
        mitigation_measures = self._generate_mitigation_measures(main_risks)
        
        # �����ж�����
        action_plan = self._generate_action_plan(mitigation_measures)
        
        return ContingencyPlan(
            main_risks=main_risks,
            mitigation_measures=mitigation_measures,
            action_plan=action_plan,
            trigger_conditions=self._define_trigger_conditions(risk_metrics)
        )
```

### 3.2 ��ʷ�龰�⣨HistoricalScenarioLibrary??
```python
class HistoricalScenarioLibrary:
    """
    ��ʷ�龰??    
    ����: STRESS_TEST_001-M02
    ְ��: ������ʷΣ���¼�����
    """
    
    def __init__(self, config: ScenarioLibraryConfig):
        self.config = config
        self.scenarios = self._load_scenario_definitions()
        
    def load_scenario(self, scenario_name: str) -> ScenarioData:
        """
        ������ʷ�龰����
        
        Args:
            scenario_name: �龰����
            
        Returns:
            ScenarioData: �龰����
        """
        scenario_def = self.scenarios.get(scenario_name)
        if not scenario_def:
            raise ValueError(f"δ�ҵ���?? {scenario_name}")
        
        # ������ʷ����
        market_data = self._load_market_data(scenario_def)
        
        return ScenarioData(
            name=scenario_name,
            start_date=scenario_def['start_date'],
            end_date=scenario_def['end_date'],
            market_data=market_data,
            description=scenario_def['description'],
            severity=scenario_def['severity']
        )
    
    def get_default_scenarios(self) -> List[str]:
        """��ȡĬ���龰�б�����չ��15����ʷ�龰��"""
        return [
            # ����Σ���龰��5����
            '2008_financial_crisis',
            '2020_covid_pandemic',
            '1987_black_monday',
            '1998_ltcm_crisis',
            '2010_flash_crash',
            # �߷����龰��5����
            '2022_interest_rate_hike',
            '2015_china_market_crash',
            '2011_european_debt_crisis',
            '2018_trade_war',
            '2023_banking_crisis',
            # �жȷ����龰��5����
            '2016_brexit',
            '2019_us_china_tension',
            '2021_evergrande_crisis',
            '2022_russia_ukraine_war',
            '2024_middle_east_tension'
        ]
    
    def _load_scenario_definitions(self) -> Dict:
        """�����龰����"""
        return {
            '2008_financial_crisis': {
                'start_date': '2008-09-01',
                'end_date': '2009-03-31',
                'description': '2008��ȫ�����Σ??,
                'severity': 'extreme',
                'key_events': [
                    '�����ֵ��Ʋ�',
                    'AIG����',
                    'ȫ����б���'
                ]
            },
            '2020_covid_pandemic': {
                'start_date': '2020-02-01',
                'end_date': '2020-04-30',
                'description': '2020���¹������??,
                'severity': 'extreme',
                'key_events': [
                    'ȫ������۶�',
                    'ԭ���ڻ�����??,
                    'ȫ�����'
                ]
            },
            '2022_interest_rate_hike': {
                'start_date': '2022-01-01',
                'end_date': '2022-12-31',
                'description': '2022��������������??,
                'severity': 'high',
                'key_events': [
                    '������������??,
                    'ծȯ�г�����',
                    '�Ƽ��ɻ�??
                ]
            }
        }
```

### 3.3 ���ؿ������棨MonteCarloEngine??
```python
class MonteCarloEngine:
    """
    ���ؿ���ģ������
    
    ����: STRESS_TEST_001-M03
    ְ��: �������ؿ���ģ��·��
    """
    
    def __init__(self, config: MonteCarloConfig):
        self.config = config
        
    def simulate(
        self,
        portfolio_params: PortfolioParameters,
        n_simulations: int,
        time_horizon: int
    ) -> np.ndarray:
        """
        �������ؿ���ģ��·��
        
        Args:
            portfolio_params: ��ϲ�������ֵ��Э����??            n_simulations: ģ�����
            time_horizon: ʱ�䷶Χ����??            
        Returns:
            np.ndarray: ģ��·����n_simulations �� time_horizon??        """
        # ʹ�ü��β����˶�ģ��
        mu = portfolio_params.expected_return
        sigma = portfolio_params.volatility
        
        # �������??        dt = 1 / 252  # �ն�����
        Z = np.random.standard_normal((n_simulations, time_horizon))
        
        # ����·��
        paths = np.zeros((n_simulations, time_horizon + 1))
        paths[:, 0] = 1.0  # ��ʼ??        
        for t in range(1, time_horizon + 1):
            paths[:, t] = paths[:, t-1] * np.exp(
                (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z[:, t-1]
            )
        
        return paths
    
    def simulate_with_jumps(
        self,
        portfolio_params: PortfolioParameters,
        n_simulations: int,
        time_horizon: int,
        jump_intensity: float = 0.1,
        jump_mean: float = -0.05,
        jump_std: float = 0.1
    ) -> np.ndarray:
        """
        ����Ծ�����ؿ���ģ��
        
        Args:
            portfolio_params: ��ϲ���
            n_simulations: ģ�����
            time_horizon: ʱ�䷶Χ
            jump_intensity: ��Ծǿ��
            jump_mean: ��Ծ��??            jump_std: ��Ծ��׼??            
        Returns:
            np.ndarray: ģ��·��
        """
        # ����·��
        paths = self.simulate(portfolio_params, n_simulations, time_horizon)
        
        # ������Ծ
        for i in range(n_simulations):
            for t in range(time_horizon):
                if np.random.random() < jump_intensity:
                    jump = np.random.normal(jump_mean, jump_std)
                    paths[i, t+1:] *= (1 + jump)
        
        return paths
```

### 3.4 ���ռ�������RiskCalculator??
```python
class RiskCalculator:
    """
    ����ָ�����??    
    ����: STRESS_TEST_001-M04
    ְ��: ����VaR��CVaR�ȷ���ָ??    """
    
    def calculate_var(
        self,
        portfolio: Portfolio,
        confidence: float = 0.95,
        method: str = 'historical'
    ) -> float:
        """
        ����VaR��Value at Risk??        
        Args:
            portfolio: Ͷ�����
            confidence: ����ˮƽ
            method: ���㷽����historical/parametric/monte_carlo??            
        Returns:
            float: VaR??        """
        if method == 'historical':
            returns = portfolio.get_historical_returns()
            var = np.percentile(returns, (1 - confidence) * 100)
        elif method == 'parametric':
            mu = portfolio.expected_return
            sigma = portfolio.volatility
            var = mu - sigma * norm.ppf(confidence)
        else:
            raise ValueError(f"��֧�ֵķ���: {method}")
        
        return abs(var)
    
    def calculate_cvar(
        self,
        portfolio: Portfolio,
        confidence: float = 0.95
    ) -> float:
        """
        ����CVaR��Conditional VaR??        
        Args:
            portfolio: Ͷ�����
            confidence: ����ˮƽ
            
        Returns:
            float: CVaR??        """
        returns = portfolio.get_historical_returns()
        var = self.calculate_var(portfolio, confidence)
        
        # CVaR��VaR֮���ƽ����??        cvar = returns[returns <= -var].mean()
        
        return abs(cvar)
    
    def calculate_max_drawdown(
        self,
        returns: pd.Series
    ) -> MaxDrawdownResult:
        """
        ��������??        
        Args:
            returns: ��������??            
        Returns:
            MaxDrawdownResult: ���س���??        """
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        
        max_dd = drawdown.min()
        max_dd_date = drawdown.idxmin()
        
        # ����س�����ʱ��
        dd_start, dd_end = self._find_drawdown_period(drawdown, max_dd_date)
        
        return MaxDrawdownResult(
            max_drawdown=max_dd,
            max_drawdown_date=max_dd_date,
            drawdown_start=dd_start,
            drawdown_end=dd_end,
            drawdown_duration=(dd_end - dd_start).days
        )
```

### 3.5 �����ඨ??
```python
@dataclass
class StressTestConfig:
    """ѹ����������"""
    scenario_config: ScenarioLibraryConfig
    mc_config: MonteCarloConfig
    risk_config: RiskCalculationConfig
    
@dataclass
class MonteCarloConfig:
    """���ؿ������ã���ǿ�棩"""
    n_simulations: int = 50000  # ģ���������10000������50000��
    time_horizon: int = 252  # ʱ�䷶Χ���죩
    include_jumps: bool = True  # �Ƿ������Ծ
    jump_intensity: float = 0.1  # ��Ծǿ��
    
    # �����龰���ã�������
    extreme_scenario_ratio: float = 0.20  # �����龰ռ�ȣ�20%��
    n_extreme_simulations: int = 10000  # �����龰ģ�����
    tail_distribution: str = 'student_t'  # β���ֲ����ͣ�student_t/stable��
    tail_dof: int = 5  # t�ֲ����ɶ�
    
    # ѹ���龰���ã�������
    stress_scenarios: List[str] = field(default_factory=lambda: [
        'market_crash_30pct',  # �г�����30%
        'volatility_spike_3x',  # ���������3��
        'correlation_breakdown',  # ����Ա���
        'liquidity_crisis',  # ������Σ��
        'flash_crash'  # ����
    ])
    
    # �����Ż����ã�������
    use_gpu: bool = False  # �Ƿ�ʹ��GPU����
    parallel_workers: int = 4  # ���й���������
    batch_size: int = 1000  # ��������С
    
@dataclass
class ScenarioLibraryConfig:
    """�龰����??""
    data_path: str = 'data/scenarios/'
    update_frequency: int = 90  # ����Ƶ�ʣ���??```

---

## 4. ����ģ�Ͷ���

### 4.1 ��������ģ��

```python
@dataclass
class Portfolio:
    """Ͷ�����"""
    weights: pd.Series  # �ʲ�Ȩ��
    assets: List[str]   # �ʲ��б�
    value: float        # ��ϼ�??    
    def get_historical_returns(self) -> pd.Series:
        """��ȡ��ʷ����??""
        pass

@dataclass
class ScenarioData:
    """�龰����"""
    name: str
    start_date: datetime
    end_date: datetime
    market_data: pd.DataFrame
    description: str
    severity: str  # low/medium/high/extreme
```

### 4.2 �������ģ��

```python
@dataclass
class StressTestResult:
    """ѹ�����Խ��"""
    test_type: str
    scenario_results: Dict[str, ScenarioResult]
    risk_metrics: RiskMetrics
    risk_report: RiskReport
    contingency_plan: ContingencyPlan
    timestamp: datetime
    
@dataclass
class ScenarioResult:
    """�龰�طŽ��"""
    scenario_name: str
    portfolio_impact: PortfolioImpact
    risk_metrics: RiskMetrics
    worst_day: datetime
    recovery_period: int  # �ָ�����
    
@dataclass
class ContingencyPlan:
    """Ӧ��Ԥ??""
    main_risks: List[str]
    mitigation_measures: List[str]
    action_plan: List[ActionItem]
    trigger_conditions: Dict[str, float]
```

---

## 5. ����ʵ��ϸ??
### 5.1 ��ʷ�龰�⹹??
**�龰ѡ��ԭ��**??1. ���ǲ�ͬ���͵�Σ���¼�������Σ�������顢���߳����
2. ������ͬ���س̶ȣ���ȡ��жȡ��ضȡ����ˣ�
3. ʱ��ֲ����ȣ����⼯����ĳһʱ��??
**�龰������Դ**??- �����г����ݣ�Yahoo Finance��iFind��Tushare??- ѧ���о���Σ���¼��о����棩
- ��ܻ������棨��������IMF??
### 5.2 ���ؿ���ģ���Ż�

**�����Ż�**??- ʹ��NumPy��������??- ���л�ģ��·����??- ʹ��GPU���٣���ѡ��

**ģ��ѡ��**??- ����ģ�ͣ����β����˶���GBM??- �߼�ģ�ͣ�����Ծ����ɢģ??- ����ģ�ͣ���β�ֲ���t�ֲ����ȶ��ֲ���

---

## 6. ���ɷ���

### 6.1 ������Ż�������

```python
class PortfolioOptimizer:
    """����Ż���������ѹ������??""
    
    def __init__(self, stress_tester: StressTestingSystem):
        self.stress_tester = stress_tester
        
    def optimize_with_stress_test(
        self,
        portfolio: Portfolio,
        constraints: OptimizationConstraints
    ) -> OptimizationResult:
        """ѹ�����Ը�֪�������??""
        # 1. ִ��ѹ������
        stress_result = self.stress_tester.run_stress_test(portfolio)
        
        # 2. ������Լ??        if stress_result.risk_metrics.max_drawdown > constraints.max_drawdown:
            # �������Ȩ��
            adjusted_portfolio = self._adjust_for_stress(
                portfolio, stress_result
            )
            return OptimizationResult(
                portfolio=adjusted_portfolio,
                stress_test_result=stress_result,
                status='ADJUSTED'
            )
        
        return OptimizationResult(
            portfolio=portfolio,
            stress_test_result=stress_result,
            status='ACCEPTED'
        )
```

### 6.2 �����Ԥ��ϵͳ��??
```python
class RiskAlertSystem:
    """����Ԥ��ϵͳ������ѹ�����ԣ�"""
    
    def __init__(self, stress_tester: StressTestingSystem):
        self.stress_tester = stress_tester
        
    def monitor_risk(
        self,
        portfolio: Portfolio,
        market_data: pd.DataFrame
    ) -> RiskAlert:
        """��ط���"""
        # 1. ִ�п���ѹ����??        stress_result = self.stress_tester.run_stress_test(
            portfolio, test_type='extreme'
        )
        
        # 2. ��������??        if stress_result.risk_metrics.var_99 > self.config.var_threshold:
            return RiskAlert(
                level='HIGH',
                message='VaR������??,
                recommendation=stress_result.contingency_plan.action_plan
            )
```

---

## 7. ���Բ���

### 7.1 ��Ԫ����

```python
def test_historical_scenario_loading():
    """������ʷ�龰����"""
    library = HistoricalScenarioLibrary(ScenarioLibraryConfig())
    scenario = library.load_scenario('2008_financial_crisis')
    
    assert scenario.name == '2008_financial_crisis'
    assert scenario.severity == 'extreme'
    assert len(scenario.market_data) > 0

def test_monte_carlo_simulation():
    """�������ؿ���ģ��"""
    engine = MonteCarloEngine(MonteCarloConfig())
    params = PortfolioParameters(expected_return=0.08, volatility=0.15)
    
    paths = engine.simulate(params, n_simulations=1000, time_horizon=252)
    
    assert paths.shape == (1000, 253)
    assert all(paths[:, 0] == 1.0)

def test_var_calculation():
    """����VaR����"""
    calculator = RiskCalculator()
    portfolio = create_test_portfolio()
    
    var_95 = calculator.calculate_var(portfolio, confidence=0.95)
    cvar_95 = calculator.calculate_cvar(portfolio, confidence=0.95)
    
    assert var_95 > 0
    assert cvar_95 >= var_95
```

---

## 8. ʵʩ·��??
### 8.1 �����׶Σ�2�ܣ�

**Week 1: ���Ĺ��ܿ�??*
- Day 1-2: ��ʷ�龰�⹹??- Day 3-4: ���ؿ������濪??- Day 5: ���ռ�������??
**Week 2: �������??*
- Day 1-2: Ӧ��Ԥ������ģ??- Day 3: ������ϵͳ��??- Day 4: ��Ԫ�����뼯�ɲ�??- Day 5: �ĵ���д�������??
### 8.2 ���??
| ���??| ʱ�� | ����??| ���ձ�׼ |
|--------|------|--------|----------|
| **M1: �龰����??* | Day 2 | ��ʷ�龰??| ����5����??|
| **M2: MC�������** | Day 4 | ���ؿ������� | ģ������ |
| **M3: ���ռ������** | Day 5 | ���ռ���??| VaR/CVaR׼ȷ |
| **M4: �������** | Day 7 | ����ϵͳ | ���нӿ���??|
| **M5: ����ͨ��** | Day 8 | ���Ա��� | ���в���ͨ�� |
| **M6: ��������** | Day 10 | ����ϵͳ | ϵͳ�ȶ����� |

---

## 9. AIά��ָ��

### 9.1 �Զ������ָ??
**ϵͳ������ָ??*??- �龰�����״??- ���ؿ���ģ��ɹ�??- ���ռ���׼ȷ??
**ҵ��ָ��**??- ѹ������ִ��Ƶ��
- ����Ԥ����ʱ??- Ӧ��Ԥ����Ч??
### 9.2 �Զ���ά����??
**ÿ������**??- ����г��쳣�¼�
- �����龰����

**ÿ������**??- ִ��ѹ������
- ���·��ձ���

**ÿ������**??- �����龰??- У׼���ؿ������
- �����¶ȷ��ձ���

---

## 10. Ԥ����������

### 10.1 ��������

| ָ�� | ��ǰˮƽ | Ŀ��ˮƽ | �������� |
|------|---------|---------|---------|
| **�����г�����ʶ��** | ??| ??| �������� |
| **����Ԥ����ǰ??* | ??| ��ǰ1-2??| �������� |
| **Ӧ��Ԥ���걸??* | ??| ??| ����3??|
| **���ձ�������** | ??| רҵ | ����2??|

### 10.2 ������??
- ??ʵ��רҵ��������������ѹ���������龰����
- ??���������г�����ʶ������
- ??�������Ƶķ���Ӧ��Ԥ����??- ??Ϊ����Ż��ṩ����Լ??
---

## 11. ������Լ??
### 11.1 ������??
| ����??| ���յȼ� | �����ʩ |
|--------|----------|----------|
| **��ʷ����ȱʧ** | P2 | ʹ��������ݡ���??|
| **���ؿ������??* | P3 | ���м��㡢GPU��??|
| **�龰���岻׼** | P2 | ���ڸ��¡�ר����??|

### 11.2 ʵʩԼ��

1. **����Լ��**: ��Ҫ��ʷΣ���¼���??2. **����Լ��**: ���ؿ���ģ����Ҫ������??3. **ʱ��Լ��**: ������????
---

## ��¼

### A. �ο���??
1. **ѹ�����Է���**:
   - Basel Committee on Banking Supervision. "Stress Testing Principles"

2. **���ؿ���ģ��**:
   - Glasserman, P. (2003). "Monte Carlo Methods in Financial Engineering"

### B. ��Դ��??
- ��ʷΣ���¼�����: data/scenarios/
- ���ؿ���ģ��ʾ��: docs/examples/monte_carlo_example.py

---

**��ͼ�汾**: v1.0 | **��������**: 2026-04-03 | **״??*: Final | **��һ??*: ����������д


