---
module_id: MARKET_PARTICIPANT_SIMULATION_INTEGRATION_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: å®æ½å¢é
standard_type: ä¸ä¸éåæºæèå¾
applicable_scope: Layer 6 ç»åä¼åå±?
compliance_level: ä¸ä¸æ å
responsibility:
  - å¸åºåä¸èæ¨¡æéæ?
  - åä¸èè¡ä¸ºå»ºæ¨?
  - å¤å±æ¬¡éæ?
  - æ¨¡æç»æåºç¨
layer: "Layer 6 (ç»åä¼åå±?"
---

# å¸åºåä¸èè¡ä¸ºæ¨¡æéæèå?

## 核心定位

负责市场参与者模拟集成。基于ABM技术，模拟市场参与者行为，支持策略测试。


## æ ¸å¿å®ä½

æå»ºå¸åºåä¸èæ¨¡æéæçè®¾è®¡ä¸å®ç°ï¼åºäºAgent-Based Modelingææ¯ï¼æ¨¡æä¸åå¸åºåä¸èè¡ä¸ºï¼æ¯æå¸åºå¾®è§ç»æç ç©¶åç­ç¥æµè¯ã?

---


> **æ ¸å¿èè´£**: å¸åºåä¸èè¡ä¸ºæ¨¡æéæï¼å¤å±æ¬¡éææ¶æ?
> **èè´£è¾¹ç**: 
> - â?æ¬ææ¡£è´è´£ï¼å¸åºåä¸èæ¨¡æéæãåä¸èè¡ä¸ºå»ºæ¨¡ãå¤å±æ¬¡éæãæ¨¡æç»æåºç?
> - â?æ¬ææ¡£ä¸è´è´£ï¼å å­è®¡ç®ãç­ç¥æ§è¡ãé£é©æ§å?
ï»? å¸åºåä¸èè¡ä¸ºæ¨¡æç³»?- å¤å±æ¬¡éææ¶ææ¹?

> **æ ¸å¿å®ä½**: å¸åºåä¸èè¡ä¸ºæ¨¡æç³»?- å¤å±æ¬¡éææ¶ææ¹?çæ ¸å¿åè½å®ç?

> **çæ¬**: v1.0
> **åå»ºæ¥æ**: 2026-04-02
> **ææ¯è¯å®¡å®**: Spec-Approver (å®¡æ¹æºè½?
> **æ ¸å¿é®é¢**: å¸åºåä¸èæ¨¡æï¼å½å®¶éãä¸»åãæ£æ·ï¼å¦ä½éæå°ç°æç³»ç»ï¼
> **ç­æ¡**: å¤å±æ¬¡é?- åæ¶ä½ä¸ºå å­ãä¿¡å·ãå³ç­ä¸ç§å½¢å¼ä»?
## ð?äºãè¯¦ç»éææ¶æè®¾?
### 2.1 Layer 2.5 æ°å¢å±ï¼å¸åºåä¸èæ¨¡æå±

**æ¶æå®ä½**: å¨Layer 2 (Alphaå å­? ?Layer 3 (èæåæ? ä¹é´æ°å¢

```
Layer 0: æ°æ®æºå±
    ?Layer 1: æ°æ®é¢å¤çå±
    ?Layer 2: Alphaå å­?(ç°æ5700+å å­)
    ?Layer 2.5: å¸åºåä¸èæ¨¡æå± ð (æ°å¢æ ¸å¿?
    ââ å½å®¶éæºè½ä½ (NationalTeamAgent)
    ââ ä¸»åæºè½?(InstitutionalAgent)
    ââ æ£æ·æºè½?(RetailAgent)
    ââ å¸åºæ¨¡æå¼æ (MarketSimulationEngine)
    ?Layer 3: èæåæ?    ?Layer 4: æºå¨å­¦ä¹ ?    ?Layer 5: ç­ç¥æ§è¡?    ?Layer 6: ç»åä¼å?    ?Layer 7: AIæ¥å?    ?Layer 8: äººæºäº¤äº?```

**ä¸ºä»ä¹éè¦Layer 2.5?*
1. **æ°æ®å±é¢**: éè¦æ´åé¾èæ¦ãèµéæµåãèæç­å¤æºæ°æ®
2. **è®¡ç®å±é¢**: éè¦è¿è¡RLæ¨¡åãè¡ä¸ºéèå­¦æ¨¡åç­å¤æè®¡?3. **äº¤äºå±é¢**: éè¦æ¨¡ææºè½ä½ä¹é´çåå¼åäº¤äº
4. **è¾åºå±é¢**: éè¦åæ¶è¾åºå å­ãä¿¡å·ãå³ç­ä¸ç§å½¢?
---

### 2.2 å å­è¾åºå±éææ¹?
#### 2.2.1 å å­å®ä¹

**ä¸»åå¨åå å­** (InstitutionalActivityFactor)

```python
class InstitutionalActivityFactor(BaseFactor):
    """ä¸»åå¨åå å­
    
    ç´¢å¼: FACTOR.INSTITUTIONAL.001
    Layer: Layer 2 (Alphaå å­?
    æ°æ®? Layer 2.5 ä¸»åæºè½ä½è¾?    
    å å­ææ:
    1. èµéæµåå¼ºåº¦ (CapitalFlowIntensity)
    2. è®¢åç°¿ä¸å¹³è¡¡?(OrderBookImbalance)
    3. ä¸»åæä»åå (InstitutionalHoldingChange)
    4. æçé¶æ®µè¯å« (ManipulationPhase)
    """
    
    def __init__(self, institutional_agent: InstitutionalAgent):
        self.agent = institutional_agent
        
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """è®¡ç®ä¸»åå¨åå å­
        
        è¾å¥:
            data: åå«ä»·æ ¼ãæäº¤éãè®¢åç°¿ç­æ°?            
        è¾åº:
            pd.Series: ä¸»åå¨åå å­?(èå´[-1, 1])
            - æ­? ä¸»åèµéæµå¥
            - è´? ä¸»åèµéæµåº
            - ç»å¯¹å¼è¶?å¼ºåº¦è¶å¤§
        """
        # 1. è·åä¸»åæºè½ä½çå¸åºå¾®è§ç»æåæ
        microstructure = self.agent.market_microstructure_analyzer.analyze(
            order_book=data['order_book'],
            trade_flow=data['trade_flow'],
            liquidity=data['liquidity']
        )
        
        # 2. è®¡ç®èµéæµåå¼ºåº¦
        capital_flow_intensity = self._calculate_capital_flow_intensity(
            microstructure.trade_flow
        )
        
        # 3. è®¡ç®è®¢åç°¿ä¸å¹³è¡¡?        order_book_imbalance = self._calculate_order_book_imbalance(
            microstructure.order_book
        )
        
        # 4. è®¡ç®ä¸»åæä»åå
        holding_change = self._calculate_holding_change(
            data['institutional_holdings']
        )
        
        # 5. è¯å«æçé¶æ®µ
        manipulation_phase = self.agent._identify_manipulation_phase(
            microstructure
        )
        
        # 6. åææç»å ?        factor_value = (
            0.3 * capital_flow_intensity +
            0.3 * order_book_imbalance +
            0.2 * holding_change +
            0.2 * manipulation_phase
        )
        
        return factor_value
```

**æ£æ·æç»ªå å­** (RetailSentimentFactor)

```python
class RetailSentimentFactor(BaseFactor):
    """æ£æ·æç»ªå å­
    
    ç´¢å¼: FACTOR.RETAIL.001
    Layer: Layer 2 (Alphaå å­?
    æ°æ®? Layer 2.5 æ£æ·æºè½ä½è¾?    
    å å­ææ:
    1. å¸åºæç»ªææ° (MarketSentimentIndex)
    2. ç¾ç¾¤æåºå¼ºåº¦ (HerdingIntensity)
    3. æ£æ·æä»åå (RetailHoldingChange)
    4. è¿½æ¶¨æè·ç¨?(ChaseTrendDegree)
    """
    
    def __init__(self, retail_agent: RetailAgent):
        self.agent = retail_agent
        
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """è®¡ç®æ£æ·æç»ªå å­
        
        è¾åº:
            pd.Series: æ£æ·æç»ªå å­?(èå´[-1, 1])
            - æ­? æ£æ·æç»ªä¹è§(å¯è½è§é¡¶)
            - è´? æ£æ·æç»ªæ²è§(å¯è½è§åº)
            - ç»å¯¹å¼è¶?æç»ªè¶æ?        """
        # 1. è·åæ£æ·æºè½ä½çæç»ªåæ
        sentiment_score = self.agent.sentiment_analyzer.analyze(
            news=data['news'],
            social_media=data['social_media'],
            market_data=data['prices']
        )
        
        # 2. è®¡ç®ç¾ç¾¤æåºå¼ºåº¦
        herding_intensity = self.agent.herding_model.evaluate(
            market_state=data,
            sentiment_score=sentiment_score
        )
        
        # 3. è®¡ç®æ£æ·æä»åå
        holding_change = self._calculate_holding_change(
            data['retail_holdings']
        )
        
        # 4. è®¡ç®è¿½æ¶¨æè·ç¨?        chase_trend_degree = self._calculate_chase_trend_degree(
            data['prices'], data['retail_holdings']
        )
        
        # 5. åææç»å ?        factor_value = (
            0.4 * sentiment_score +
            0.3 * herding_intensity +
            0.2 * holding_change +
            0.1 * chase_trend_degree
        )
        
        return factor_value
```

**æ¿ç­ä¿¡å·å å­** (PolicySignalFactor)

```python
class PolicySignalFactor(BaseFactor):
    """æ¿ç­ä¿¡å·å å­
    
    ç´¢å¼: FACTOR.POLICY.001
    Layer: Layer 2 (Alphaå å­?
    æ°æ®? Layer 2.5 å½å®¶éæºè½ä½è¾åº
    
    å å­ææ:
    1. æ¿ç­æ¯æ?(PolicySupportLevel)
    2. å¸åºç¨³å®?(MarketStability)
    3. å½å®¶éæä»å?(NationalTeamHoldingChange)
    4. å¹²é¢æ¦ç (InterventionProbability)
    """
    
    def __init__(self, national_team_agent: NationalTeamAgent):
        self.agent = national_team_agent
        
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """è®¡ç®æ¿ç­ä¿¡å·å å­
        
        è¾åº:
            pd.Series: æ¿ç­ä¿¡å·å å­?(èå´[-1, 1])
            - æ­? æ¿ç­å©å¥½,å½å®¶éå¯è½ä¹°?            - è´? æ¿ç­å©ç©º,å½å®¶éå¯è½å?            - ç»å¯¹å¼è¶?ä¿¡å·è¶å¼º
        """
        # 1. è·åå½å®¶éæºè½ä½çæ¿ç­ä¿¡?        policy_signals = self.agent.policy_signal_detector.detect(
            news_data=data['news'],
            macro_data=data['macro_indicators']
        )
        
        # 2. è¯ä¼°å¸åºç¨³å®?        stability_score = self.agent.market_stability_monitor.evaluate(
            price_data=data['prices'],
            volatility=data['volatility'],
            sentiment=data['sentiment']
        )
        
        # 3. è®¡ç®å½å®¶éæä»å?        holding_change = self._calculate_holding_change(
            data['national_team_holdings']
        )
        
        # 4. è®¡ç®å¹²é¢æ¦ç
        intervention_probability = self.agent._calculate_intervention_probability(
            policy_signals, stability_score
        )
        
        # 5. åææç»å ?        factor_value = (
            0.4 * policy_signals.composite_score +
            0.3 * stability_score +
            0.2 * holding_change +
            0.1 * intervention_probability
        )
        
        return factor_value
```

#### 2.2.2 å å­åºé?
```python
class AgentBasedFactorLibrary:
    """åºäºæºè½ä½çå å­?    
    ç´¢å¼: FACTOR.LIBRARY.AGENT.001
    Layer: Layer 2 (Alphaå å­?
    èè´£: ç®¡çåè®¡ç®æææºè½ä½çæçå ?    """
    
    def __init__(self, 
                 national_team_agent: NationalTeamAgent,
                 institutional_agent: InstitutionalAgent,
                 retail_agent: RetailAgent):
        self.agents = {
            'national_team': national_team_agent,
            'institutional': institutional_agent,
            'retail': retail_agent
        }
        
        # åå§åå ?        self.factors = {
            'policy_signal': PolicySignalFactor(national_team_agent),
            'institutional_activity': InstitutionalActivityFactor(institutional_agent),
            'retail_sentiment': RetailSentimentFactor(retail_agent)
        }
        
    def calculate_all_factors(self, data: pd.DataFrame) -> pd.DataFrame:
        """è®¡ç®æææºè½ä½å å­
        
        è¾åº:
            pd.DataFrame: åå«ææå å­å¼çDataFrame
        """
        factor_values = {}
        
        for factor_name, factor in self.factors.items():
            try:
                factor_values[factor_name] = factor.calculate(data)
            except Exception as e:
                logger.error(f"Failed to calculate factor {factor_name}: {e}")
                factor_values[factor_name] = np.nan
        
        return pd.DataFrame(factor_values)
    
    def integrate_with_existing_factors(self, 
                                       agent_factors: pd.DataFrame,
                                       existing_factors: pd.DataFrame) -> pd.DataFrame:
        """å°æºè½ä½å å­ä¸ç°æå å­åºéæ
        
        éææ¹å¼:
        1. ç´æ¥æ¼æ¥ (æ°å¢3ä¸ªå å­å)
        2. å å­æ­£äº¤?(å»é¤ä¸ç°æå å­çå±çº¿?
        3. å å­æ å?(ç»ä¸éçº²)
        """
        # 1. ç´æ¥æ¼æ¥
        integrated_factors = pd.concat([existing_factors, agent_factors], axis=1)
        
        # 2. å å­æ­£äº¤?(å?
        if self.config.orthogonalize:
            integrated_factors = self._orthogonalize_factors(integrated_factors)
        
        # 3. å å­æ å?        integrated_factors = self._standardize_factors(integrated_factors)
        
        return integrated_factors
```

---

### 2.3 ä¿¡å·è¾åºå±éææ¹?
#### 2.3.1 ä¿¡å·çæ?
```python
class AgentBasedSignalGenerator:
    """åºäºæºè½ä½çä¿¡å·çæ?    
    ç´¢å¼: SIGNAL.GENERATOR.AGENT.001
    Layer: Layer 5 (ç­ç¥æ§è¡?
    èè´£: å°æºè½ä½å³ç­è½¬æ¢ä¸ºäº¤æä¿¡?    """
    
    def __init__(self, agents: Dict[str, BaseAgent]):
        self.agents = agents
        self.signal_combiner = SignalCombiner()
        
    def generate_signals(self, market_state: MarketState) -> TradingSignals:
        """çæäº¤æä¿¡å·
        
        æµç¨:
        1. åæºè½ä½ç¬ç«çæå³ç­
        2. å¸åºæ¨¡æå¼ææ¨¡æåå¼
        3. ä¿¡å·åæå¨æ´åä¿¡?        4. è¿åæç»äº¤æä¿¡?        """
        # 1. åæºè½ä½ç¬ç«çæå³ç­
        agent_decisions = {}
        for agent_name, agent in self.agents.items():
            decision = agent.generate_trading_decision(market_state)
            agent_decisions[agent_name] = decision
        
        # 2. å¸åºæ¨¡æå¼ææ¨¡æåå¼ (å?
        if self.config.enable_simulation:
            simulation_result = self._simulate_market(agent_decisions, market_state)
            market_impact = simulation_result.market_impact
        else:
            market_impact = None
        
        # 3. ä¿¡å·åæå¨æ´åä¿¡?        final_signals = self.signal_combiner.combine(
            agent_decisions=agent_decisions,
            market_impact=market_impact,
            risk_budget=self.config.risk_budget
        )
        
        return final_signals


class SignalCombiner:
    """ä¿¡å·åæ?    
    ç´¢å¼: SIGNAL.COMBINER.001
    èè´£: æ´åå¤ä¸ªæºè½ä½çä¿¡å·
    """
    
    def combine(self,
               agent_decisions: Dict[str, AgentDecision],
               market_impact: Optional[float] = None,
               risk_budget: Optional[Dict] = None) -> TradingSignals:
        """åæä¿¡å·
        
        åæç­ç¥:
        1. å æå¹³å (æ ¹æ®æºè½ä½ç½®ä¿¡åº¦å æ)
        2. å¸åºå²å»è°æ´ (èèå¸åºå²å»ææ¬)
        3. é£é©é¢ç®çº¦æ (ç¡®ä¿é£é©å¯æ§)
        """
        # 1. æååæºè½ä½çä¿¡?        signals = {}
        for agent_name, decision in agent_decisions.items():
            signals[agent_name] = {
                'action': decision.action,
                'position_size': decision.position_size,
                'confidence': decision.confidence,
                'target_stocks': decision.target_stocks
            }
        
        # 2. å æå¹³ååæ
        combined_signal = self._weighted_average_combine(signals)
        
        # 3. å¸åºå²å»è°æ´
        if market_impact is not None:
            combined_signal = self._adjust_for_market_impact(
                combined_signal, market_impact
            )
        
        # 4. é£é©é¢ç®çº¦æ
        if risk_budget is not None:
            combined_signal = self._apply_risk_budget(
                combined_signal, risk_budget
            )
        
        return combined_signal
    
    def _weighted_average_combine(self, signals: Dict) -> TradingSignals:
        """å æå¹³ååæ
        
        æéè®¡ç®:
        - å½å®¶? æé = ç½®ä¿¡?* 0.3 (é¿æç¨³å®)
        - ä¸»å: æé = ç½®ä¿¡?* 0.5 (å¸åºä¸»å¯¼)
        - æ£æ·: æé = ç½®ä¿¡?* 0.2 (ååææ )
        """
        total_weight = 0
        weighted_position = {}
        
        for agent_name, signal in signals.items():
            # æ ¹æ®æºè½ä½ç±»åè®¾ç½®åºç¡æé
            if agent_name == 'national_team':
                base_weight = 0.3
            elif agent_name == 'institutional':
                base_weight = 0.5
            elif agent_name == 'retail':
                base_weight = 0.2  # æ£æ·ä½ä¸ºååææ 
                signal['position_size'] = -signal['position_size']  # åè½¬
            else:
                base_weight = 0.1
            
            # è®¡ç®æç»æ?            weight = base_weight * signal['confidence']
            total_weight += weight
            
            # å æç´¯å 
            for stock, size in signal['position_size'].items():
                if stock not in weighted_position:
                    weighted_position[stock] = 0
                weighted_position[stock] += weight * size
        
        # å½ä¸?        if total_weight > 0:
            for stock in weighted_position:
                weighted_position[stock] /= total_weight
        
        return TradingSignals(
            action='BUY' if sum(weighted_position.values()) > 0 else 'SELL',
            position_size=weighted_position,
            confidence=total_weight / len(signals),
            timestamp=datetime.now()
        )
```

#### 2.3.2 ä¸ç°æç­ç¥é?
```python
class StrategyWithAgentSignals(BaseStrategy):
    """éææºè½ä½ä¿¡å·çç­ç¥åºç±»
    
    ç´¢å¼: STRATEGY.AGENT.001
    Layer: Layer 5 (ç­ç¥æ§è¡?
    
    ä½¿ç¨æ¹å¼:
    1. ç»§æ¿æ­¤ç±»
    2. å¨generate_signalsæ¹æ³ä¸­ä½¿ç¨agent_signals
    """
    
    def __init__(self, 
                 config: StrategyConfig,
                 agent_signal_generator: AgentBasedSignalGenerator):
        super().__init__(config)
        self.agent_signal_generator = agent_signal_generator
        
    def generate_signals(self, data: pd.DataFrame) -> List[Signal]:
        """çæäº¤æä¿¡å·
        
        æµç¨:
        1. è·åä¼ ç»å å­ä¿¡å·
        2. è·åæºè½ä½ä¿¡?        3. èåä¸¤ç±»ä¿¡å·
        4. è¿åæç»ä¿¡?        """
        # 1. è·åä¼ ç»å å­ä¿¡å·
        traditional_signals = self._generate_traditional_signals(data)
        
        # 2. è·åæºè½ä½ä¿¡?        market_state = self._build_market_state(data)
        agent_signals = self.agent_signal_generator.generate_signals(market_state)
        
        # 3. èåä¿¡å·
        final_signals = self._fuse_signals(traditional_signals, agent_signals)
        
        return final_signals
    
    def _fuse_signals(self, 
                     traditional_signals: List[Signal],
                     agent_signals: TradingSignals) -> List[Signal]:
        """èåä¼ ç»ä¿¡å·åæºè½ä½ä¿¡å·
        
        èåç­ç¥:
        1. ä¿¡å·æ¹åä¸??å¢å¼ºä¿¡å·å¼ºåº¦
        2. ä¿¡å·æ¹åå²çª ?éä½ä¿¡å·å¼ºåº¦ææ¾?        3. æºè½ä½ä¿¡å·ç¬??ä½ä¸ºæ°ä¿¡å·æ·»?        """
        fused_signals = []
        
        for trad_signal in traditional_signals:
            # æ£æ¥æºè½ä½æ¯å¦æç¸åè¡ç¥¨çä¿¡å·
            if trad_signal.symbol in agent_signals.position_size:
                agent_position = agent_signals.position_size[trad_signal.symbol]
                
                # ä¿¡å·æ¹åä¸?                if (trad_signal.direction == 'BUY' and agent_position > 0) or \
                   (trad_signal.direction == 'SELL' and agent_position < 0):
                    # å¢å¼ºä¿¡å·å¼ºåº¦
                    fused_signal = Signal(
                        symbol=trad_signal.symbol,
                        direction=trad_signal.direction,
                        strength=trad_signal.strength * 1.5,
                        reason=f"Traditional + Agent signal aligned"
                    )
                # ä¿¡å·æ¹åå²çª
                else:
                    # éä½ä¿¡å·å¼ºåº¦
                    fused_signal = Signal(
                        symbol=trad_signal.symbol,
                        direction=trad_signal.direction,
                        strength=trad_signal.strength * 0.5,
                        reason=f"Traditional + Agent signal conflict"
                    )
                
                fused_signals.append(fused_signal)
            else:
                # ä¼ ç»ä¿¡å·ç¬ç«
                fused_signals.append(trad_signal)
        
        # æ·»å æºè½ä½ç¬ç«ä¿¡?        for symbol, position in agent_signals.position_size.items():
            if not any(s.symbol == symbol for s in fused_signals):
                fused_signals.append(Signal(
                    symbol=symbol,
                    direction='BUY' if position > 0 else 'SELL',
                    strength=abs(position),
                    reason=f"Agent signal only"
                ))
        
        return fused_signals
```

---

### 2.4 å³ç­è¾åºå±éææ¹?
#### 2.4.1 å¤æºè½ä½æç¥¨æºå¶

```python
class MultiAgentVotingSystem:
    """å¤æºè½ä½æç¥¨ç³»ç»
    
    ç´¢å¼: VOTING.AGENT.001
    Layer: Layer 6 (ç»åä¼å?
    èè´£: éè¿æç¥¨æºå¶æ´åæºè½ä½å³?    """
    
    def __init__(self, agents: Dict[str, BaseAgent]):
        self.agents = agents
        
    def vote_on_portfolio(self, 
                         market_state: MarketState,
                         current_portfolio: Portfolio) -> PortfolioDecision:
        """å¯¹ç»åè°æ´è¿è¡æ?        
        æç¥¨æºå¶:
        1. åæºè½ä½ç¬ç«æç¥¨
        2. æ ¹æ®æç¥¨ç»æè®¡ç®æé
        3. èèé£é©é¢ç®çº¦æ
        4. è¿åæç»ç»åå³?        """
        # 1. åæºè½ä½ç¬ç«æç¥¨
        votes = {}
        for agent_name, agent in self.agents.items():
            decision = agent.generate_trading_decision(market_state)
            votes[agent_name] = {
                'decision': decision,
                'voting_power': self._calculate_voting_power(agent_name, decision)
            }
        
        # 2. æ ¹æ®æç¥¨ç»æè®¡ç®æé
        target_weights = self._calculate_target_weights(votes)
        
        # 3. èèé£é©é¢ç®çº¦æ
        target_weights = self._apply_risk_budget(target_weights, current_portfolio)
        
        # 4. è¿åæç»ç»åå³?        return PortfolioDecision(
            target_weights=target_weights,
            rebalance_reasons=self._generate_rebalance_reasons(votes),
            confidence=self._calculate_confidence(votes),
            timestamp=datetime.now()
        )
    
    def _calculate_voting_power(self, agent_name: str, decision: AgentDecision) -> float:
        """è®¡ç®æç¥¨æé
        
        æç¥¨æéå ç´ :
        1. æºè½ä½ç±»åæ?(å½å®¶?.3, ä¸»å0.5, æ£æ·0.2)
        2. å³ç­ç½®ä¿¡?(0-1)
        3. åå²åç¡®?(åºäºåå²è¡¨ç°)
        """
        # åºç¡æé
        base_weights = {
            'national_team': 0.3,
            'institutional': 0.5,
            'retail': 0.2
        }
        
        base_weight = base_weights.get(agent_name, 0.1)
        
        # ç½®ä¿¡åº¦è°?        confidence_adjusted = base_weight * decision.confidence
        
        # åå²åç¡®çè°?(å¦æ?
        historical_accuracy = self._get_historical_accuracy(agent_name)
        final_weight = confidence_adjusted * historical_accuracy
        
        return final_weight
    
    def _calculate_target_weights(self, votes: Dict) -> Dict[str, float]:
        """æ ¹æ®æç¥¨ç»æè®¡ç®ç®æ æé
        
        è®¡ç®æ¹æ³:
        1. å¯¹æ¯åªè¡?ç´¯å åæºè½ä½çæç¥¨æ?        2. å½ä¸åæ?        3. åºç¨æééå¶ (ååªè¡ç¥¨æéä¸è¶?0%)
        """
        stock_weights = {}
        total_voting_power = 0
        
        # ç´¯å æç¥¨æé
        for agent_name, vote in votes.items():
            decision = vote['decision']
            voting_power = vote['voting_power']
            
            for stock, position in decision.position_size.items():
                if stock not in stock_weights:
                    stock_weights[stock] = 0
                
                # æ£æ·ä½ä¸ºååææ 
                if agent_name == 'retail':
                    stock_weights[stock] -= voting_power * position
                else:
                    stock_weights[stock] += voting_power * position
            
            total_voting_power += voting_power
        
        # å½ä¸?        if total_voting_power > 0:
            for stock in stock_weights:
                stock_weights[stock] /= total_voting_power
        
        # åºç¨æééå¶
        max_weight = 0.2
        for stock in stock_weights:
            if abs(stock_weights[stock]) > max_weight:
                stock_weights[stock] = max_weight if stock_weights[stock] > 0 else -max_weight
        
        return stock_weights
```

#### 2.4.2 ä¸ç°æç»åä¼åé?
```python
class PortfolioOptimizerWithAgents:
    """éææºè½ä½çç»åä¼å?    
    ç´¢å¼: OPTIMIZER.PORTFOLIO.AGENT.001
    Layer: Layer 6 (ç»åä¼å?
    
    éææ¹å¼:
    1. æºè½ä½æç¥¨ç»æä½ä¸ºç®æ æéçåéª
    2. å å­æ¨¡åä½ä¸ºæ¶çé¢æµ
    3. é£é©æ¨¡åä½ä¸ºé£é©çº¦æ
    4. ä¼åæ±è§£æç»æ?    """
    
    def __init__(self,
                 voting_system: MultiAgentVotingSystem,
                 factor_model: FactorModel,
                 risk_model: RiskModel):
        self.voting_system = voting_system
        self.factor_model = factor_model
        self.risk_model = risk_model
        
    def optimize(self,
                market_state: MarketState,
                current_portfolio: Portfolio) -> PortfolioDecision:
        """ä¼åç»å
        
        ä¼åæµç¨:
        1. æºè½ä½æç¥¨çæåéªæ?        2. å å­æ¨¡åé¢æµæ¶ç
        3. é£é©æ¨¡åè®¡ç®é£é©
        4. ä¼åæ±è§£æç»æ?        """
        # 1. æºè½ä½æç¥¨çæåéªæ?        voting_result = self.voting_system.vote_on_portfolio(
            market_state, current_portfolio
        )
        prior_weights = voting_result.target_weights
        
        # 2. å å­æ¨¡åé¢æµæ¶ç
        expected_returns = self.factor_model.predict_returns(
            market_state.factors
        )
        
        # 3. é£é©æ¨¡åè®¡ç®é£é©
        risk_matrix = self.risk_model.calculate_risk_matrix(
            market_state.prices
        )
        
        # 4. ä¼åæ±è§£æç»æ?        optimal_weights = self._solve_optimization(
            prior_weights=prior_weights,
            expected_returns=expected_returns,
            risk_matrix=risk_matrix,
            constraints=self._build_constraints(current_portfolio)
        )
        
        return PortfolioDecision(
            target_weights=optimal_weights,
            rebalance_reasons=voting_result.rebalance_reasons,
            confidence=voting_result.confidence,
            timestamp=datetime.now()
        )
    
    def _solve_optimization(self,
                           prior_weights: Dict[str, float],
                           expected_returns: pd.Series,
                           risk_matrix: pd.DataFrame,
                           constraints: Dict) -> Dict[str, float]:
        """æ±è§£ä¼åé®é¢
        
        ä¼åç®æ :
        max: w'Î¼ - Î» * w'Î£w - Î³ * ||w - w_prior||^2
        
        å¶ä¸­:
        - w: ç»åæé
        - Î¼: é¢ææ¶ç
        - Î£: åæ¹å·®ç©?        - w_prior: åéªæé (æºè½ä½æç¥¨ç»?
        - Î»: é£é©åæ¶ç³»æ°
        - Î³: åéªæéåç¦»æ©ç½ç³»æ°
        """
        import cvxpy as cp
        
        # æå»ºä¼ååé
        stocks = list(expected_returns.index)
        n = len(stocks)
        w = cp.Variable(n)
        
        # æå»ºç®æ å½æ°
        mu = expected_returns.values
        Sigma = risk_matrix.values
        w_prior = np.array([prior_weights.get(stock, 0) for stock in stocks])
        
        # ç®æ å½æ°
        lambda_risk = self.config.risk_aversion  # é£é©åæ¶ç³»æ°
        gamma_prior = self.config.prior_deviation_penalty  # åéªåç¦»æ©ç½
        
        objective = cp.Maximize(
            mu @ w - 
            lambda_risk * cp.quad_form(w, Sigma) - 
            gamma_prior * cp.norm(w - w_prior, 2)**2
        )
        
        # çº¦ææ¡ä»¶
        constraints_list = [
            cp.sum(w) == 1,  # æéåä¸º1
            w >= 0,  # ä¸åè®¸å?            w <= self.config.max_weight  # ååªè¡ç¥¨æå¤§æ?        ]
        
        # æ±è§£
        problem = cp.Problem(objective, constraints_list)
        problem.solve()
        
        # è¿åç»æ
        optimal_weights = {}
        for i, stock in enumerate(stocks):
            optimal_weights[stock] = w.value[i]
        
        return optimal_weights
```

---

## ð ä¸ãéæææå¯¹?
### 3.1 åä¸éææ¹å¼ vs å¤å±æ¬¡é?
| ç»´åº¦ | åä¸å å­éæ | åä¸ç­ç¥éæ | å¤å±æ¬¡é?(æ¨è) |
|------|------------|------------|-----------------|
| **ä¿¡æ¯å©ç¨** | â­â­ ä»å©ç¨å å­ä¿¡?| â­â­?ä»å©ç¨ä¿¡å·ä¿¡?| â­â­â­â­?å¨æ¹ä½å©?|
| **åå¼æ¨¡æ** | ?æ æ³æ¨¡æ | ?æ æ³æ¨¡æ | ?å®æ´æ¨¡æ |
| **å³ç­è´¨é** | â­â­?ä¸­ç­ | â­â­â­â­ è¾å¥½ | â­â­â­â­?ä¼ç§ |
| **å¼åé¾?* | ??| â­â­ ?| â­â­â­â­ ?|
| **ç»´æ¤ææ¬** | ??| â­â­ ?| â­â­?ä¸­é« |
| **æ©å±?* | â­â­ ä¸?| â­â­?è¾å¥½ | â­â­â­â­?ä¼ç§ |

### 3.2 å¤å±æ¬¡éæçä¼å¿

1. **ä¿¡æ¯æå¤§åå©ç¨**:
   - å å­? æåæºè½ä½è¡ä¸ºçéåç¹å¾
   - ä¿¡å·? çæå·ä½çä¹°åä¿¡?   - å³ç­? éè¿æç¥¨æºå¶ä¼åç»å

2. **åå¼è¿ç¨å®æ´ä¿ç**:
   - å¸åºæ¨¡æå¼ææ¨¡ææºè½ä½äº¤?   - ä»·æ ¼åç°æºå¶åæ ä¾éåå¼
   - å¸åºå²å»æ¨¡åè¯ä¼°äº¤æå½±å

3. **çµæ´»æ§å¼º**:
   - å¯ä»¥åç¬ä½¿ç¨æä¸å±çè¾åº
   - å¯ä»¥ç»åä½¿ç¨å¤å±è¾åº
   - å¯ä»¥æ ¹æ®å¸åºç¶æå¨æè°æ´æ?
4. **å¯è§£éæ§å¥½**:
   - æ¯ä¸ªæºè½ä½çå³ç­é½ææç¡®çç±
   - æç¥¨è¿ç¨éæå¯è¿½?   - å å­è´¡ç®åº¦å¯éååæ

---

## ð åãå®æ½å»º?
### 4.1 åé¶æ®µå®æ½è·¯?
**Phase 1: å å­éæ** (Month 1-2)
- å®ç°ä¸ä¸ªæºè½ä½å ?(æ¿ç­ä¿¡å·ãä¸»åå¨åãæ£æ·æ?
- éæå°ç°æå å­åº
- éªè¯å å­ææ?
**Phase 2: ä¿¡å·éæ** (Month 3-4)
- å®ç°ä¿¡å·çæå¨åä¿¡å·åæ?- éæå°ç°æç­ç¥æ¡?- åæµéªè¯ä¿¡å·è´¨é

**Phase 3: å³ç­éæ** (Month 5-6)
- å®ç°å¤æºè½ä½æç¥¨ç³»ç»
- éæå°ç»åä¼åå¨
- å®çéªè¯å³ç­ææ

### 4.2 ä¼åçº§å»º?
**é«ä¼åçº§** (å¿é¡»å®ç°):
1. ?å å­è¾åºå±é?(æç®?æç´æ¥)
2. ?ä¿¡å·è¾åºå±é?(æ ¸å¿åè½)

**ä¸­ä¼åçº§** (æ¨èå®ç°):
3. ?å³ç­è¾åºå±é?(é«çº§åè½)

**ä½ä¼åçº§** (å¯éå®?:
4. â¸ï¸ å¸åºæ¨¡æå¼æ (è®¡ç®å¯é,å¯åæä¼?

### 4.3 ææ¯éåå»ºè®®

| åè½æ¨¡å | æ¨èæ?| çç± |
|---------|---------|------|
| **å å­è®¡ç®** | Pandas + NumPy | æçç¨³å®,æ§è½?|
| **ä¿¡å·çæ** | äºä»¶é©±å¨æ¶æ | çµæ´»,ææ©?|
| **ç»åä¼å** | CVXPY + Barraæ¨¡å | ä¸ä¸,å¯è§£?|
| **æºè½ä½éä¿¡** | æ¶æ¯éå (Redis/RabbitMQ) | å¼æ­¥,è§?|

---

## ð äºãæ»ç»

### æ ¸å¿ç­æ¡

**å¸åºåä¸èè¡ä¸ºæ¨¡æåºè¯¥éç¨å¤å±æ¬¡éææ¶æï¼åæ¶ä½ä¸ºå å­ãä¿¡å·ãå³ç­ä¸ç§å½¢å¼ä»å¥ç³»ç»ï¼**

1. **ä½ä¸ºå å­ä»å¥** (Layer 2):
   - çææ¿ç­ä¿¡å·å å­ãä¸»åå¨åå å­ãæ£æ·æç»ªå ?   - ä¸ç°?700+å å­æ ç¼éæ
   - ä¾å¤å å­æ¨¡åä½¿ç¨

2. **ä½ä¸ºä¿¡å·ä»å¥** (Layer 5):
   - çæä¹°åä¿¡å·ãä»ä½å»ºè®®ãé£é©é¢?   - ä¸ç°æç­ç¥æ¡æ¶ååå·¥?   - å¢å¼ºç­ç¥ä¿¡å·è´¨é

3. **ä½ä¸ºå³ç­ä»å¥** (Layer 6):
   - éè¿å¤æºè½ä½æç¥¨æºå¶ä¼åç»å
   - ä¸ç°æç»åä¼åå¨éæ
   - æåå³ç­è´¨é

### å³é®ä¼å¿

- ?**ä¿¡æ¯æå¤§åå©ç¨**: å¨æ¹ä½æåæºè½ä½è¡ä¸ºä¿¡æ¯
- ?**åå¼å®æ´ä¿ç**: æ¨¡æå¸åºåä¸èä¹é´çäº¤äº
- ?**çµæ´»å¯æ©?*: å¯åç¬æç»åä½¿ç¨åå±è¾åº
- ?**å¯è§£éæ§å¼º**: æ¯ä¸ªå³ç­é½ææç¡®çç±

### ä¸ä¸æ­¥è¡?
**ç«å³å¼?*:
1. å®ç°ä¸ä¸ªæºè½ä½å ?(Week 1-2)
2. éæå°ç°æå å­åº (Week 3)
3. éªè¯å å­ææ?(Week 4)

**åå¤å°±ç»ª**:
- ?éææ¶æè®¾è®¡å®æ
- ?å å­å®ä¹æç¡®
- ?ä¿¡å·çææ¹æ¡æ¸æ°
- ?å³ç­éæè·¯å¾æç¡®

**ç°å¨å¯ä»¥å¼å§ç¼ç å®ç°äº!** ð

---

**çæ¬**: v1.0 | **æ´æ°**: 2026-04-02 | **ç?*: ?å·²å®?

## 1. ææ¡£æ²»ç

### 1.1 ææ¡£ç´¢å¼

**æ¬ææ¡£å¨ç³»ç»ä¸­çä½ç½®**:
- **æå±å±çº?*: Layer 0 (ç³»ç»æ¶æ)
- **æ¨¡åç´¢å¼**: 001
- **æ¨¡ååç§°**: MARKET_PARTICIPANT_SIMULATION
- **ææ¡£è·¯å¾**: docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/

### 1.2 çæ¬ç®¡ç

**çæ¬åå²**:
- v1.0.0 (2026-04-02): åå§çæ¬

### 1.3 ç»´æ¤è´£ä»»

**ææ¡£ç»´æ¤**:
- **è´£ä»»æ¨¡å**: MARKET_PARTICIPANT_SIMULATION
- **ç»´æ¤å¨æ**: æ¯å­£åº¦å®¡æ?
- **åæ´æµç¨**: æäº¤åæ´ç³è¯· â?ææ¯è¯å®?â?æ´æ°ææ¡£

---

**èå¾çæ¬**: v1.0.0 | **åå»ºæ¥æ**: 2026-04-02 | **ç¶æ?*: Active


---

## ð ææ¡£æ²»ç

### åæ´è®°å½

| çæ¬ | æ¥æ | åæ´åå®¹ | åæ´äº?|
|------|------|----------|--------|
| v1.0.0 | 2026-04-07 | åå§çæ¬åå»º | å®æ½å¢é |

---
