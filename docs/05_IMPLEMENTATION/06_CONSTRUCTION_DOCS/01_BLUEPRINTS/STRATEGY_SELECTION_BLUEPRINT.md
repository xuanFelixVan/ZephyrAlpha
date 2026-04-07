---
responsibility:
  - ç­ç¥éæ©
  - ç­ç¥æå
  - ç­ç¥è¯ä¼°
  - ç­ç¥å³ç­

module_id: STRATEGY_SELECTION_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: å®æ½å¢é
standard_type: ä¸ä¸éåæºæèå¾
applicable_scope: Layer 3 ç­ç¥å±?
compliance_level: ä¸ä¸æ å
layer: "Layer 3 (ç­ç¥å±?"
---

# ç­ç¥æåä¸éæ©ç³»ç»ææ¯èå?

## 核心定位

负责策略选择，基于策略评估和预测，选择最优策略组合，提升投资决策质量。



> **æ ¸å¿èè´£**: æ ¹æ®å¸åºç¯å¢å¨æéæ©æä¼ç­ç¥ç»å?
> **èè´£è¾¹ç**: 
> - â?æ¬ææ¡£è´è´£ï¼ç­ç¥è¯åãæºè½æåãå¨æéæ©
> - â?æ¬ææ¡£ä¸è´è´£ï¼å å­è®¡ç®ï¼ç±å å­æ¨¡åè´è´£ï¼


## ä¸ãè®¾è®¡ç®æ ä¸çº¦æ

### 1.1 æ ¸å¿è®¾è®¡ç®æ 

| ç®æ  | ä¼å?| ææ¯å®?|
|------|--------|----------|
| **å¤ç»´åº¦è¯åä½?* | P0 | æ¶çãé£é©ãç¨³å®æ§ãéåºæ§ç­20+ç»´åº¦è¯å |
| **å¨ææéè°?* | P0 | åºäºå¸åºç¶æãé£é©åå¥½å¨æè°æ´è¯åæ?|
| **ç­ç¥ç¸å³æ§å?* | P1 | æ¶çç¸å³æ§ç©éµãé£é©åæ£åº¦è®¡ç® |
| **AIè¾å©å³ç­** | P1 | AIæ¨èç­ç¥ç»åãé£é©è¯ä¼°ãå¸åºå¹éåº¦åæ |
| **å®æ¶æ§è½çæ§** | P2 | ç­ç¥è¿è¡ç¶æçæ§ãæ§è½è¡°åæ£?|
| **ç¨æ·åå¥½çé¢** | P2 | å¯è§åæåä»ªè¡¨çãèªç¶è¯­è¨ç­ç¥æ¨è |

### 1.2 ææ¯çº¦æä¸åå

1. **å®¢è§å¬æ­£åå**ï¼è¯åæ åéæå¯è§£éï¼é¿åé»ç®±å³ç­
2. **å¨æéåºæ§å?*ï¼è¯åæééå¸åºç¶æãç¨æ·é£é©åå¥½å¨æè°?
3. **é£é©åæ£åå**ï¼é¿åéæ©é«åº¦ç¸å³çç­ç¥ç»?
4. **æç»­ä¼ååå**ï¼åºäºå®çè¡¨ç°æç»­æ´æ°ç­ç¥è¯?
5. **ç¨æ·åå¥½åå**ï¼ä¸æç¼ç¨çç¨æ·ä¹è½çè§£è¯åé»è¾åæ¨èç?

### 1.3 ä¸ç°æç³»ç»é?

| å·²ææ¨¡å | éææ¹å¼ | æ¥å£å®ä¹ |
|----------|----------|----------|
| **BatchEvaluationç³»ç»** | ç»©ææ°æ®?| è·åç­ç¥åå²ç»©ææ°æ® |
| **ParameterOptimizationç³»ç»** | åæ°ä¼åç»æ | è·åæä¼åæ°é?|
| **StrategyEngineæ ¸å¿** | ç­ç¥åæ°?| è·åç­ç¥ç±»åãåæ°ç©ºé´ç­ä¿¡æ¯ |
| **MarketStateDetector** | å¸åºç¶æè¾?| è·åå½åå¸åºç¶æï¼çå¸/çå¸/éè¡å¸ï¼ |

## äºãç³»ç»æ¶æè®¾?

### 2.1 æ´ä½æ¶æ?

```
ç­ç¥æåä¸éæ©ç³»ç»åå±æ¶æ?
ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
?                  ç¨æ·äº¤äº?(User Interaction)          ?
ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
?1. RankingDashboard - æåä»ªè¡¨?                       ?
?2. RecommendationEngine - æ¨èå¼æ                       ?
?3. NaturalLanguageExplainer - èªç¶è¯­è¨è§£é?            ?
ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
                              ?
ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
?               å³ç­é»è¾?(Decision Logic)               ?
ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
?1. MultiCriteriaEvaluator - å¤ååè¯ä¼°å¨                 ?
?2. WeightOptimizer - æéä¼å?                         ?
?3. PortfolioConstructor - ç»åæå»º?                    ?
?4. RiskDiversifier - é£é©åæ£?                         ?
ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
                              ?
ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
?               è¯åè®¡ç®?(Scoring Layer)                ?
ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
?1. PerformanceScorer - ç»©æè¯å?                       ?
?2. RiskScorer - é£é©è¯å?                              ?
?3. StabilityScorer - ç¨³å®æ§è¯åå¨                        ?
?4. AdaptabilityScorer - éåºæ§è¯åå¨                     ?
?5. ComplexityScorer - å¤æåº¦è¯åå¨                       ?
ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
                              ?
ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
?               æ°æ®æºå± (Data Sources)                   ?
ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
?1. BatchEvaluationResults - æ¹éè¯ä¼°ç»æ                 ?
?2. RealTimePerformance - å®æ¶ç»©ææ°æ®                    ?
?3. MarketStateData - å¸åºç¶ææ°?                       ?
?4. UserPreferences - ç¨æ·åå¥½æ°æ®                        ?
ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
```

### 2.2 æ ¸å¿ç»ä»¶èè´£

**MultiCriteriaEvaluator (å¤ååè¯ä¼°å¨)**
- æ´ååç»´åº¦è¯åï¼è®¡ç®ç»¼åå¾å
- å®ç°TOPSISãAHPç­å¤ååå³ç­ç®æ³
- å¤çè¯åæ åååå½ä¸?

**WeightOptimizer (æéä¼å?**
- åºäºå¸åºç¶æå¨æè°æ´è¯åæ?
- èèç¨æ·é£é©åå¥½ä¸ªæ§åæé
- ä½¿ç¨ä¼åç®æ³å¯»æ¾æä¼æéå?

**PerformanceScorer (ç»©æè¯å?**
- è®¡ç®æ¶çç±»ææ è¯åï¼å¤æ®æ¯çãå¹´åæ¶çãèçç­?
- æ¶é´è¡°åå æï¼è¿æç»©ææéæ´é«ï¼
- ç»è®¡æ¾èæ§æ£?

**RiskScorer (é£é©è¯å?**
- è®¡ç®é£é©ç±»ææ è¯åï¼æå¤§åæ¤ãæ³¢å¨çãä¸è¡é£é©ç­?
- æç«¯é£é©äºä»¶æ£?
- é£é©è°æ´æ¶çè®¡ç®

**StabilityScorer (ç¨³å®æ§è¯åå¨)**
- è¯ä¼°ç­ç¥ç»©æç¨³å®?
- æ¶çåºåèªç¸å³æ§å?
- åæ°æææ§æµ?

**AdaptabilityScorer (éåºæ§è¯åå¨)**
- è¯ä¼°ç­ç¥å¯¹ä¸åå¸åºç¶æçéåº?
- å¸åºç¶æåæ¢æ£?
- ç­ç¥é²æ£æ§å?

## ä¸ãæ ¸å¿ç»ä»¶è®¾?

### 3.1 MultiCriteriaEvaluator è¯¦ç»è®¾è®¡

```python
class TOPSISEvaluator:
    """TOPSISå¤ååå³ç­è¯ä¼°å¨
    
    ç´¢å¼: STRAT.SELECTION.001-M01
    èè´£: ä½¿ç¨TOPSISç®æ³è¿è¡å¤ç»´åº¦ç­ç¥æ?
    ç¹ç¹: å®¢è§æéåéï¼é¿åä¸»è§å?
    """
    
    def __init__(self, criteria_weights: Dict[str, float] = None):
        self.criteria_weights = criteria_weights or self._default_weights()
        self.normalizer = MinMaxNormalizer()
        
    def evaluate(self, strategies: List[Strategy], 
                criteria_matrix: pd.DataFrame) -> RankingResult:
        """ä½¿ç¨TOPSISç®æ³è¯ä¼°ç­ç¥
        
        TOPSISï¼Technique for Order Preference by Similarity to Ideal Solutionï¼ï¼
        1. æå»ºå³ç­ç©éµ
        2. æ ååå³ç­ç©?
        3. è®¡ç®å ææ ååç©?
        4. ç¡®å®æ­£çæ³è§£åè´çæ³?
        5. è®¡ç®åæ¹æ¡å°çæ³è§£çè·ç¦»
        6. è®¡ç®ç¸å¯¹æ¥è¿åº¦å¹¶æåº
        """
        
        # 1. æå»ºå³ç­ç©éµï¼ç­?Ã åå?
        decision_matrix = self._build_decision_matrix(strategies, criteria_matrix)
        
        # 2. æ ååå³ç­ç©éµï¼æ¶é¤éçº²å½±å?
        normalized_matrix = self.normalizer.normalize(decision_matrix)
        
        # 3. è®¡ç®å ææ ååç©?
        weighted_matrix = self._apply_weights(normalized_matrix)
        
        # 4. ç¡®å®æ­£çæ³è§£åè´çæ³?
        positive_ideal, negative_ideal = self._calculate_ideal_solutions(weighted_matrix)
        
        # 5. è®¡ç®è·ç¦»
        distances_to_positive = self._calculate_distances(weighted_matrix, positive_ideal)
        distances_to_negative = self._calculate_distances(weighted_matrix, negative_ideal)
        
        # 6. è®¡ç®ç¸å¯¹æ¥è¿?
        closeness_scores = distances_to_negative / (distances_to_positive + distances_to_negative)
        
        # 7. æåºå¹¶çæç»?
        ranking = self._create_ranking(strategies, closeness_scores, criteria_matrix)
        
        return RankingResult(
            ranking=ranking,
            closeness_scores=closeness_scores,
            decision_matrix=decision_matrix,
            weighted_matrix=weighted_matrix,
            ideal_solutions={
                'positive': positive_ideal,
                'negative': negative_ideal
            }
        )
        
    def _default_weights(self) -> Dict[str, float]:
        """é»è®¤è¯åæéåé"""
        return {
            'sharpe_ratio': 0.25,      # å¤æ®æ¯çï¼æ¶çé£é©å¹³?
            'max_drawdown': 0.20,       # æå¤§åæ¤ï¼é£é©æ§å¶
            'annual_return': 0.15,      # å¹´åæ¶çï¼çå©è½?
            'win_rate': 0.10,           # èçï¼äº¤æè´¨?
            'stability_score': 0.10,    # ç¨³å®æ§ï¼ç»©æä¸?
            'adaptability_score': 0.10, # éåºæ§ï¼å¸åºç¯å¢éåºè½å
            'complexity_score': 0.05,   # å¤æåº¦ï¼ç­ç¥ç®?
            'turnover': 0.05           # æ¢æçï¼äº¤æææ¬èè
        }
        
    def _apply_weights(self, normalized_matrix: pd.DataFrame) -> pd.DataFrame:
        """åºç¨æéå°æ ååç©éµ"""
        weighted_matrix = normalized_matrix.copy()
        
        for criterion in weighted_matrix.columns:
            if criterion in self.criteria_weights:
                weighted_matrix[criterion] *= self.criteria_weights[criterion]
                
        return weighted_matrix
        
    def _calculate_ideal_solutions(self, weighted_matrix: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """è®¡ç®æ­£çæ³è§£åè´çæ³?
        
        å¯¹äºæçåææ ï¼è¶å¤§è¶å¥½ï¼ï¼æ­£çæ³è§£åæå¤§å¼ï¼è´çæ³è§£åæ?
        å¯¹äºææ¬åææ ï¼è¶å°è¶å¥½ï¼ï¼æ­£çæ³è§£åæå°å¼ï¼è´çæ³è§£åæ?
        """
        # å®ä¹ææ ç±»å
        benefit_criteria = ['sharpe_ratio', 'annual_return', 'win_rate', 
                          'stability_score', 'adaptability_score']
        cost_criteria = ['max_drawdown', 'complexity_score', 'turnover']
        
        positive_ideal = pd.Series()
        negative_ideal = pd.Series()
        
        for criterion in weighted_matrix.columns:
            if criterion in benefit_criteria:
                positive_ideal[criterion] = weighted_matrix[criterion].max()
                negative_ideal[criterion] = weighted_matrix[criterion].min()
            elif criterion in cost_criteria:
                positive_ideal[criterion] = weighted_matrix[criterion].min()
                negative_ideal[criterion] = weighted_matrix[criterion].max()
            else:
                # é»è®¤ææçåææ å¤ç
                positive_ideal[criterion] = weighted_matrix[criterion].max()
                negative_ideal[criterion] = weighted_matrix[criterion].min()
                
        return positive_ideal, negative_ideal
```

### 3.2 WeightOptimizer è¯¦ç»è®¾è®¡

```python
class DynamicWeightOptimizer:
    """å¨ææéä¼åå¨
    
    ç´¢å¼: STRAT.SELECTION.001-M02
    èè´£: åºäºå¸åºç¶æåç¨æ·åå¥½å¨æè°æ´è¯åæ?
    ç¹ç¹: èªéåºæéåéï¼æé«ç­ç¥éæ©åç¡®?
    """
    
    def __init__(self, market_state_detector: MarketStateDetector,
                user_preference_store: UserPreferenceStore):
        self.market_state_detector = market_state_detector
        self.user_preference_store = user_preference_store
        self.weight_history = []
        
    def optimize_weights(self, strategies: List[Strategy], 
                        historical_performance: pd.DataFrame) -> Dict[str, float]:
        """ä¼åè¯åæé
        
        åºäºä»¥ä¸å ç´ å¨æè°æ´æéï¼
        1. å½åå¸åº?
        2. ç¨æ·é£é©åå¥½
        3. ç­ç¥åå²è¡¨ç°
        4. ç»æµå¨æé¶æ®µ
        """
        
        # 1. è·åå½åå¸åº?
        market_state = self.market_state_detector.get_current_state()
        
        # 2. è·åç¨æ·é£é©åå¥½
        user_prefs = self.user_preference_store.get_preferences()
        
        # 3. è®¡ç®åºç¡æéï¼åºäºå¸åºç¶æï¼
        base_weights = self._calculate_base_weights(market_state)
        
        # 4. è°æ´æéï¼åºäºç¨æ·åå¥½ï¼
        adjusted_weights = self._adjust_for_user_preferences(base_weights, user_prefs)
        
        # 5. å­¦ä¹ è°æ´ï¼åºäºåå²è¡¨ç°ï¼
        learned_weights = self._learn_from_history(adjusted_weights, historical_performance)
        
        # 6. å½ä¸åç¡®ä¿æéå?
        final_weights = self._normalize_weights(learned_weights)
        
        # è®°å½æéåå²
        self.weight_history.append({
            'timestamp': datetime.now(),
            'market_state': market_state,
            'weights': final_weights.copy()
        })
        
        return final_weights
        
    def _calculate_base_weights(self, market_state: MarketState) -> Dict[str, float]:
        """åºäºå¸åºç¶æè®¡ç®åºç¡æé"""
        
        # ä¸åå¸åºç¶æçæéåå¥½
        weight_templates = {
            'bull_market': {
                'sharpe_ratio': 0.20,
                'max_drawdown': 0.15,
                'annual_return': 0.25,  # çå¸æ´çéæ¶?
                'win_rate': 0.10,
                'stability_score': 0.10,
                'adaptability_score': 0.10,
                'complexity_score': 0.05,
                'turnover': 0.05
            },
            'bear_market': {
                'sharpe_ratio': 0.25,
                'max_drawdown': 0.25,   # çå¸æ´çéé£é©æ§?
                'annual_return': 0.10,
                'win_rate': 0.10,
                'stability_score': 0.15,
                'adaptability_score': 0.10,
                'complexity_score': 0.05,
                'turnover': 0.00       # çå¸åå°äº¤æé¢ç
            },
            'range_market': {
                'sharpe_ratio': 0.20,
                'max_drawdown': 0.20,
                'annual_return': 0.15,
                'win_rate': 0.15,      # éè¡å¸æ´çéèç
                'stability_score': 0.15,
                'adaptability_score': 0.10,
                'complexity_score': 0.05,
                'turnover': 0.00
            },
            'high_volatility': {
                'sharpe_ratio': 0.25,
                'max_drawdown': 0.30,   # é«æ³¢å¨å¸åºç¹å«éè§é£é©æ§?
                'annual_return': 0.10,
                'win_rate': 0.10,
                'stability_score': 0.15,
                'adaptability_score': 0.05,
                'complexity_score': 0.05,
                'turnover': 0.00
            }
        }
        
        # æ ¹æ®å¸åºç¶æéæ©æéæ¨¡æ¿
        template = weight_templates.get(market_state.name, weight_templates['range_market'])
        
        # æ ¹æ®å¸åºç¶æå¼ºåº¦è°æ´æ?
        strength_factor = market_state.strength  # 0-1ä¹é´çå¼º?
        adjusted_weights = {}
        
        for criterion, base_weight in template.items():
            if criterion in ['max_drawdown', 'stability_score']:
                # é£é©ç¸å³ææ éå¸åºæ³¢å¨å¼ºåº¦å¢å èå¢?
                adjusted = base_weight * (1 + strength_factor * 0.5)
            elif criterion == 'annual_return':
                # æ¶çææ å¨å¼ºè¶å¿å¸åºå¢å æé
                if market_state.name in ['bull_market', 'bear_market']:
                    adjusted = base_weight * (1 + strength_factor * 0.3)
                else:
                    adjusted = base_weight
            else:
                adjusted = base_weight
                
            adjusted_weights[criterion] = min(adjusted, 0.5)  # éå¶åææ æå¤§æ?
            
        return adjusted_weights
        
    def _adjust_for_user_preferences(self, base_weights: Dict[str, float],
                                   user_prefs: UserPreferences) -> Dict[str, float]:
        """æ ¹æ®ç¨æ·åå¥½è°æ´æé"""
        
        adjusted = base_weights.copy()
        
        # é£é©åå¥½è°æ´
        risk_tolerance = user_prefs.risk_tolerance  # 1-5?ä¸ºæåº¦ä¿å®ï¼5ä¸ºæåº¦æ¿?
        
        if risk_tolerance <= 2:  # ä¿å®?
            adjusted['max_drawdown'] *= 1.5
            adjusted['stability_score'] *= 1.3
            adjusted['annual_return'] *= 0.7
            adjusted['sharpe_ratio'] *= 0.9
            
        elif risk_tolerance >= 4:  # æ¿è¿å
            adjusted['max_drawdown'] *= 0.7
            adjusted['annual_return'] *= 1.5
            adjusted['sharpe_ratio'] *= 1.2
            adjusted['stability_score'] *= 0.8
            
        # æèµæéè°æ´
        investment_horizon = user_prefs.investment_horizon  # ç­æ/ä¸­æ/é¿æ
        
        if investment_horizon == 'short_term':
            adjusted['win_rate'] *= 1.3
            adjusted['turnover'] *= 0.5  # ç­æåå°æ¢æçèè
            
        elif investment_horizon == 'long_term':
            adjusted['stability_score'] *= 1.3
            adjusted['adaptability_score'] *= 1.2
            adjusted['turnover'] *= 1.2  # é¿æå¯æ¥åä¸å®æ¢æç
            
        return adjusted
        
    def _learn_from_history(self, weights: Dict[str, float],
                          historical_performance: pd.DataFrame) -> Dict[str, float]:
        """ä»åå²è¡¨ç°ä¸­å­¦ä¹ ä¼åæé
        
        åºäºåå²æ°æ®éªè¯ä¸åæéçæææ§ï¼ä¼åæéåé
        """
        
        if len(self.weight_history) < 10:
            return weights  # åå²æ°æ®ä¸è¶³ï¼è¿ååå§æ?
            
        # åæåå²æéè¡¨ç°
        performance_by_weight = self._analyze_weight_performance()
        
        # æ¾åºè¡¨ç°æå¥½çæéæ¨¡å¼
        best_pattern = self._find_best_weight_pattern(performance_by_weight)
        
        # æ··åå½åæéååå²æä½³æ?
        learning_rate = 0.3  # å­¦ä¹ ?
        learned_weights = {}
        
        for criterion in weights.keys():
            if criterion in best_pattern:
                learned = (1 - learning_rate) * weights[criterion] + \
                         learning_rate * best_pattern[criterion]
                learned_weights[criterion] = learned
            else:
                learned_weights[criterion] = weights[criterion]
                
        return learned_weights
```

### 3.3 PerformanceScorer è¯¦ç»è®¾è®¡

```python
class TimeWeightedPerformanceScorer:
    """æ¶é´å æç»©æè¯å?
    
    ç´¢å¼: STRAT.SELECTION.001-M03
    èè´£: è®¡ç®ç»©æææ è¯åï¼è¿æè¡¨ç°æéæ´?
    ç¹ç¹: ææ°è¡°åå æï¼éè§è¿æè¡¨?
    """
    
    def __init__(self, decay_factor: float = 0.9, min_periods: int = 20):
        self.decay_factor = decay_factor  # è¡°åå å­ï¼è¶å¤§è¡¨ç¤ºåå²æéè¶?
        self.min_periods = min_periods     # æå°è®¡ç®å¨?
        
    def calculate_scores(self, strategy: Strategy, 
                        performance_data: pd.DataFrame) -> PerformanceScores:
        """è®¡ç®æ¶é´å æç»©æè¯å"""
        
        scores = {}
        
        # 1. è®¡ç®åºç¡ææ 
        returns = performance_data['returns']
        equity_curve = performance_data['equity']
        
        # 2. è®¡ç®æ¶é´å æææ 
        scores['sharpe_ratio'] = self._time_weighted_sharpe(returns)
        scores['annual_return'] = self._time_weighted_annual_return(equity_curve)
        scores['max_drawdown'] = self._time_weighted_max_drawdown(equity_curve)
        scores['win_rate'] = self._time_weighted_win_rate(returns)
        scores['profit_factor'] = self._time_weighted_profit_factor(returns)
        
        # 3. è®¡ç®ç»¼åç»©æè¯å
        scores['composite_performance'] = self._composite_performance_score(scores)
        
        return PerformanceScores(**scores)
        
    def _time_weighted_sharpe(self, returns: pd.Series) -> float:
        """æ¶é´å æå¤æ®æ¯ç
        
        è¿ææ¶çç»äºæ´é«æéï¼åæ ç­ç¥ææ°è¡¨?
        """
        if len(returns) < self.min_periods:
            return 0
            
        # è®¡ç®ææ°è¡°åæé
        weights = self._exponential_decay_weights(len(returns))
        
        # å ææ¶çåæ³¢å¨ç
        weighted_returns = (returns * weights).sum() / weights.sum()
        weighted_volatility = np.sqrt(((returns - weighted_returns) ** 2 * weights).sum() / weights.sum())
        
        if weighted_volatility == 0:
            return 0
            
        # å¹´åå¤çï¼åè®¾æ¥æ¶ç?
        annualized_sharpe = weighted_returns / weighted_volatility * np.sqrt(252)
        
        return annualized_sharpe
        
    def _time_weighted_annual_return(self, equity_curve: pd.Series) -> float:
        """æ¶é´å æå¹´åæ¶ç"""
        if len(equity_curve) < self.min_periods:
            return 0
            
        # å°æçæ²çº¿åæ®µè®¡ç®æ¶?
        n_segments = min(10, len(equity_curve) // 30)  # æ¯æ®µ?0ä¸ªäº¤ææ¥
        segment_returns = []
        
        for i in range(n_segments):
            start_idx = i * len(equity_curve) // n_segments
            end_idx = (i + 1) * len(equity_curve) // n_segments - 1
            
            if end_idx > start_idx:
                segment_return = (equity_curve.iloc[end_idx] / equity_curve.iloc[start_idx]) - 1
                # è¿ææ®µæéæ´?
                weight = self.decay_factor ** (n_segments - i - 1)
                segment_returns.append(segment_return * weight)
                
        if not segment_returns:
            return 0
            
        # å æå¹³åå¹¶å¹´?
        weighted_return = sum(segment_returns) / sum(self.decay_factor ** i for i in range(n_segments))
        annualized_return = (1 + weighted_return) ** (252 / (len(equity_curve) / n_segments)) - 1
        
        return annualized_return
        
    def _time_weighted_max_drawdown(self, equity_curve: pd.Series) -> float:
        """æ¶é´å ææå¤§å?
        
        è¿æåæ¤ç»äºæ´é«æéï¼åæ ææ°é£é©ç¶?
        """
        if len(equity_curve) < self.min_periods:
            return 0
            
        # è®¡ç®æ»å¨æå¤§å?
        rolling_dd = self._rolling_drawdown(equity_curve, window=60)  # 60æ¥æ»å¨çª?
        
        if rolling_dd.empty:
            return 0
            
        # è®¡ç®æ¶é´å æå¹³åæå¤§å?
        weights = self._exponential_decay_weights(len(rolling_dd))
        weighted_dd = (rolling_dd * weights).sum() / weights.sum()
        
        return abs(weighted_dd)  # è¿å?
        
    def _exponential_decay_weights(self, n_periods: int) -> np.ndarray:
        """çæææ°è¡°åæéåé"""
        weights = np.array([self.decay_factor ** i for i in range(n_periods)])
        # åè½¬ä½¿æè¿ææéæ?
        weights = weights[::-1]
        # å½ä¸?
        weights = weights / weights.sum()
        return weights
```

### 3.4 StrategyCorrelationAnalyzer è¯¦ç»è®¾è®¡

```python
class StrategyCorrelationAnalyzer:
    """ç­ç¥ç¸å³æ§åæå¨
    
    ç´¢å¼: STRAT.SELECTION.001-M04
    èè´£: åæç­ç¥é´æ¶çç¸å³æ§ï¼æ¯æé£é©åæ£
    ç¹ç¹: å¤ç»´åº¦ç¸å³æ§åæï¼å¨æç¸å³æ§æ£?
    """
    
    def __init__(self, correlation_threshold: float = 0.7):
        self.correlation_threshold = correlation_threshold
        
    def analyze(self, strategies: List[Strategy], 
               returns_data: Dict[str, pd.Series]) -> CorrelationAnalysis:
        """åæç­ç¥ç¸å³?""
        
        # 1. è®¡ç®æ¶çç¸å³æ§ç©?
        corr_matrix = self._calculate_correlation_matrix(returns_data)
        
        # 2. è¯å«é«åº¦ç¸å³ç­ç¥?
        high_corr_groups = self._find_high_correlation_groups(corr_matrix)
        
        # 3. è®¡ç®é£é©åæ£æ½å
        diversification_potential = self._calculate_diversification_potential(corr_matrix)
        
        # 4. å¨æç¸å³æ§åæï¼æ»å¨çªå£?
        dynamic_corr = self._analyze_dynamic_correlation(returns_data)
        
        # 5. å¸åºç¶æç¸å³æ§å?
        market_state_corr = self._analyze_market_state_correlation(returns_data)
        
        return CorrelationAnalysis(
            correlation_matrix=corr_matrix,
            high_correlation_groups=high_corr_groups,
            diversification_potential=diversification_potential,
            dynamic_correlation=dynamic_corr,
            market_state_correlation=market_state_corr,
            recommendations=self._generate_recommendations(
                corr_matrix, high_corr_groups, diversification_potential
            )
        )
        
    def _calculate_correlation_matrix(self, returns_data: Dict[str, pd.Series]) -> pd.DataFrame:
        """è®¡ç®æ¶çç¸å³æ§ç©?""
        # å¯¹é½æ°æ®æ¶é´
        aligned_returns = self._align_returns_data(returns_data)
        
        if aligned_returns.empty:
            return pd.DataFrame()
            
        # è®¡ç®Pearsonç¸å³ç³»æ°
        corr_matrix = aligned_returns.corr()
        
        return corr_matrix
        
    def _find_high_correlation_groups(self, corr_matrix: pd.DataFrame) -> List[List[str]]:
        """è¯å«é«åº¦ç¸å³ç­ç¥ç»ï¼èç±»åæ?""
        
        groups = []
        strategies = corr_matrix.columns.tolist()
        visited = set()
        
        for i, strategy1 in enumerate(strategies):
            if strategy1 in visited:
                continue
                
            group = [strategy1]
            visited.add(strategy1)
            
            for j, strategy2 in enumerate(strategies):
                if i != j and strategy2 not in visited:
                    corr = abs(corr_matrix.iloc[i, j])
                    if corr >= self.correlation_threshold:
                        group.append(strategy2)
                        visited.add(strategy2)
                        
            if len(group) > 1:
                groups.append(group)
                
        return groups
        
    def _calculate_diversification_potential(self, corr_matrix: pd.DataFrame) -> pd.DataFrame:
        """è®¡ç®é£é©åæ£æ½å
        
        è¡¡éæ·»å æ°ç­ç¥å°ç°æç»åä¸­çé£é©åæ£ææ
        """
        n_strategies = len(corr_matrix)
        diversification = pd.DataFrame(index=corr_matrix.index, columns=['diversification_score'])
        
        for strategy in corr_matrix.index:
            # è®¡ç®è¯¥ç­ç¥ä¸å¶ä»ç­ç¥çå¹³åç¸?
            other_correlations = [corr_matrix.loc[strategy, other] 
                                for other in corr_matrix.index if other != strategy]
            
            if other_correlations:
                avg_correlation = np.mean(other_correlations)
                # å¹³åç¸å³æ§è¶ä½ï¼åæ£æ½åè¶é«
                diversification.loc[strategy, 'diversification_score'] = 1 - abs(avg_correlation)
            else:
                diversification.loc[strategy, 'diversification_score'] = 1.0
                
        return diversification
        
    def _generate_recommendations(self, corr_matrix: pd.DataFrame,
                                high_corr_groups: List[List[str]],
                                diversification: pd.DataFrame) -> List[Recommendation]:
        """çæç­ç¥éæ©æ¨è"""
        
        recommendations = []
        
        # æ¨è1ï¼é¿åéæ©é«åº¦ç¸å³çç­?
        for group in high_corr_groups:
            if len(group) > 1:
                recommendations.append(
                    Recommendation(
                        type='warning',
                        message=f"ç­ç¥ {', '.join(group)} é«åº¦ç¸å³ï¼å»ºè®®æå¤éæ©å¶ä¸­ä¸?,
                        priority='high',
                        action='avoid_high_correlation'
                    )
                )
                
        # æ¨è2ï¼ä¼åéæ©åæ£æ½åé«çç­ç¥
        top_diversifiers = diversification.nlargest(3, 'diversification_score').index.tolist()
        if top_diversifiers:
            recommendations.append(
                Recommendation(
                    type='suggestion',
                    message=f"ç­ç¥ {', '.join(top_diversifiers)} å·æé«åæ£æ½?,
                    priority='medium',
                    action='prioritize_diversification'
                )
            )
            
        # æ¨è3ï¼å¹³è¡¡æ¶çç¸å³æ§åé£é©ç¸å³?
        risk_corr_matrix = self._calculate_risk_correlation(corr_matrix)
        balanced_strategies = self._find_balanced_strategies(corr_matrix, risk_corr_matrix)
        
        if balanced_strategies:
            recommendations.append(
                Recommendation(
                    type='suggestion',
                    message=f"ç­ç¥ {', '.join(balanced_strategies)} æä¾è¯å¥½çæ¶?é£é©å¹³è¡¡",
                    priority='medium',
                    action='select_balanced'
                )
            )
            
        return recommendations
```

## åãAIè¾å©å³ç­ç³»ç»

### 4.1 AIç­ç¥æ¨èå¼æ

```python
class AIStrategyRecommender:
    """AIç­ç¥æ¨èå¼æ
    
    ç´¢å¼: STRAT.SELECTION.001-M05
    èè´£: åºäºAIæ¨¡åæ¨èç­ç¥ç»å
    ç¹ç¹: èèå¸åºç¶æãç¨æ·åå¥½ãåå²è¡¨ç°ç­å¤ç»´åº¦å ?
    """
    
    def __init__(self, model_type: str = "ensemble"):
        self.model_type = model_type
        self.feature_engineer = StrategyFeatureEngineer()
        self.model = self._load_model(model_type)
        
    def recommend(self, strategies: List[Strategy],
                 market_state: MarketState,
                 user_prefs: UserPreferences,
                 historical_data: pd.DataFrame) -> AIRecommendation:
        """çæAIç­ç¥æ¨è"""
        
        # 1. ç¹å¾å·¥ç¨
        features = self.feature_engineer.extract_features(
            strategies, market_state, user_prefs, historical_data
        )
        
        # 2. AIæ¨¡åé¢æµ
        predictions = self.model.predict(features)
        
        # 3. çææ¨èç»å
        portfolio = self._construct_ai_portfolio(strategies, predictions, user_prefs)
        
        # 4. é£é©è¯ä¼°
        risk_assessment = self._assess_portfolio_risk(portfolio, historical_data)
        
        # 5. çæèªç¶è¯­è¨è§£é
        explanation = self._generate_explanation(portfolio, predictions, risk_assessment)
        
        return AIRecommendation(
            portfolio=portfolio,
            predictions=predictions,
            risk_assessment=risk_assessment,
            explanation=explanation,
            confidence_scores=self.model.get_confidence_scores()
        )
        
    def _construct_ai_portfolio(self, strategies: List[Strategy],
                              predictions: pd.DataFrame,
                              user_prefs: UserPreferences) -> Portfolio:
        """æå»ºAIæ¨èçç­ç¥ç»?""
        
        # åºäºé¢æµå¾åæåº
        sorted_strategies = sorted(
            zip(strategies, predictions['expected_return']),
            key=lambda x: x[1],
            reverse=True
        )
        
        # æ ¹æ®ç¨æ·é£é©åå¥½ç¡®å®ç»åè§æ¨¡
        if user_prefs.risk_tolerance <= 2:  # ä¿å®?
            n_strategies = min(5, len(strategies))
            diversification_weight = 0.7
        elif user_prefs.risk_tolerance >= 4:  # æ¿è¿å
            n_strategies = min(3, len(strategies))
            diversification_weight = 0.3
        else:  # å¹³è¡¡?
            n_strategies = min(4, len(strategies))
            diversification_weight = 0.5
            
        # éæ©ç­ç¥å¹¶åéæ?
        selected = []
        weights = []
        
        for i, (strategy, score) in enumerate(sorted_strategies[:n_strategies * 2]):
            if len(selected) >= n_strategies:
                break
                
            # æ£æ¥ç¸?
            if self._is_diversified(selected, strategy, diversification_weight):
                selected.append(strategy)
                # åºäºé¢æµå¾ååéæé
                weight = score / sum(s for _, s in sorted_strategies[:n_strategies * 2])
                weights.append(weight)
                
        # å½ä¸åæ?
        if weights:
            total_weight = sum(weights)
            weights = [w / total_weight for w in weights]
            
        return Portfolio(strategies=selected, weights=weights)
        
    def _generate_explanation(self, portfolio: Portfolio,
                            predictions: pd.DataFrame,
                            risk_assessment: RiskAssessment) -> str:
        """çæèªç¶è¯­è¨æ¨èè§£é"""
        
        explanations = []
        
        # æ¶çé¢æè§£é
        expected_return = predictions.loc[portfolio.strategy_ids, 'expected_return'].mean()
        explanations.append(
            f"æ¨èç»åé¢æå¹´åæ¶ç: {expected_return:.1%}?
            f"åºäºåå²è¡¨ç°åå½åå¸åºç¶æé¢?
        )
        
        # é£é©ç¹å¾è§£é
        if risk_assessment.overall_risk <= 0.3:
            risk_level = "ä½é£?
        elif risk_assessment.overall_risk <= 0.6:
            risk_level = "ä¸­é£?
        else:
            risk_level = "é«é£?
            
        explanations.append(
            f"ç»åé£é©ç­çº§: {risk_level}ï¼æå¤§åæ¤é¢? {risk_assessment.expected_max_dd:.1%}"
        )
        
        # åæ£åè§£?
        diversification_score = risk_assessment.diversification_score
        if diversification_score >= 0.7:
            div_explanation = "é«åº¦åæ£"
        elif diversification_score >= 0.4:
            div_explanation = "éåº¦åæ£"
        else:
            div_explanation = "éä¸­åº¦è¾?
            
        explanations.append(f"é£é©åæ£ææ: {div_explanation}")
        
        # å¸åºéåºæ§è§£?
        market_adaptability = risk_assessment.market_adaptability
        if market_adaptability >= 0.7:
            adapt_explanation = "éåºæ§å¼º"
        elif market_adaptability >= 0.4:
            adapt_explanation = "éåºæ§ä¸­?
        else:
            adapt_explanation = "éåºæ§æ?
            
        explanations.append(f"å¸åºéåº? {adapt_explanation}")
        
        # ç­ç¥éæ©çç±
        top_strategy = portfolio.strategies[0]
        explanations.append(
            f"é¦éç­?{top_strategy.name}ï¼å ä¸ºå¶å¨å½å{risk_assessment.current_market_state}å¸åºç¯å¢ä¸è¡¨ç°ç¨³?
        )
        
        return "?.join(explanations)
```

## äºãç¨æ·æ¥å£è®¾?

### 5.1 éç½®æä»¶ç¤ºä¾

```yaml
# config/strategy_selection.yaml
> **æ ¸å¿èè´£**: Strategy Selectionèå¾è®¾è®¡
> **èè´£è¾¹ç**: 
> - â?æ¬ææ¡£è´è´£ï¼Strategy Selectionèå¾è®¾è®¡ç¸å³åå®¹
> - â?æ¬ææ¡£ä¸è´è´£ï¼å¶ä»æ¨¡ååå®?


## æ ¸å¿èè´£

ç­ç¥éæ©ï¼è´è´£äº¤æç­ç¥çè¯ä¼°åéæ©


---

## ð æ¦è¿°

æ¬ææ¡£å®ä¹äºSTRATEGY SELECTIONçæ ¸å¿åè½åææ¯å®ç°ã?

strategy_selection:
  # ç¨æ·åå¥½éç½®
  user_preferences:
    risk_tolerance: 3  # 1-5?ä¸ºä¸­?
    investment_horizon: "medium_term"  # short_term, medium_term, long_term
    max_drawdown_tolerance: 0.15  # æå¤§å¯æ¥ååæ¤
    target_annual_return: 0.20    # ç®æ å¹´åæ¶ç
    
  # æåç®æ³éç½®
  ranking:
    algorithm: "topsis"  # topsis, ahp, electre
    criteria_weights:
      sharpe_ratio: 0.25
      max_drawdown: 0.20
      annual_return: 0.15
      win_rate: 0.10
      stability_score: 0.10
      adaptability_score: 0.10
      complexity_score: 0.05
      turnover: 0.05
      
    time_weighting:
      enabled: true
      decay_factor: 0.9  # è¿æè¡¨ç°æé
    
  # ç¸å³æ§åæé?
  correlation:
    threshold: 0.7
    analysis_period: "1y"  # 1m, 3m, 6m, 1y, 3y
    dynamic_analysis: true
    rolling_window: 60
    
  # AIæ¨èéç½®
  ai_recommendation:
    enabled: true
    model_type: "ensemble"  # random_forest, gradient_boosting, neural_network, ensemble
    confidence_threshold: 0.7
    explainability: true
    
  # è¾åºéç½®
  output:
    format: "html"  # json, html, pdf
    include_visualizations: true
    include_ai_explanation: true
    save_selection_history: true
```

### 5.2 å½ä»¤è¡æ¥?

```bash
# çæç­ç¥æå
python strategy_selector.py rank \
  --strategies "strategies/*.yaml" \
  --period "2020-01-01:2023-12-31" \
  --algorithm "topsis" \
  --weights "config/weights.yaml" \
  --output "ranking_results/"

# AIç­ç¥æ¨è
python strategy_selector.py recommend \
  --user-prefs "config/user_preferences.yaml" \
  --market-state "current" \
  --ai-model "ensemble" \
  --output "recommendations/"

# ç¸å³æ§å?
python strategy_selector.py analyze-correlation \
  --strategies "strategies/*.yaml" \
  --period "1y" \
  --threshold 0.7 \
  --output "correlation_analysis/"

# ç»åæå»º
python strategy_selector.py construct-portfolio \
  --ranking "ranking_results/rankings.json" \
  --correlation "correlation_analysis/correlation.json" \
  --constraints "max_drawdown<0.2,sharpe_ratio>1.0" \
  --output "portfolio/"

# èªç¶è¯­è¨æ¥è¯¢
python strategy_selector.py query \
  --question "è¯·ä¸ºææ¨èä¸ä¸ªéåçå¸çä½é£é©ç­ç¥ç»åï¼æå¤§åæ¤ä¸è¶è¿15%" \
  --ai-model "gpt-4" \
  --output "nlp_recommendation/"
```

### 5.3 Webä»ªè¡¨çå?

**æ ¸å¿åè½æ¨¡å**?
1. **å®æ¶æåçæ¿**ï¼ç­ç¥ç»¼åè¯åå¨æå±?
2. **ç¸å³æ§ç­åå¾**ï¼ç­ç¥é´æ¶çç¸å³æ§å¯è§å
3. **AIæ¨èé¢æ¿**ï¼AIçæçç­ç¥ç»åæ¨?
4. **ç»©æå¯¹æ¯å¾è¡¨**ï¼å¤ç­ç¥ç»©æå¯¹æ¯åæ
5. **é£é©åæä»ªè¡¨**ï¼ç»åé£é©ææ ç?
6. **èªç¶è¯­è¨é®ç­**ï¼ç¨æ·é®é¢AIè§£ç­

**ææ¯æ å»ºè®®**?
- åç«¯ï¼Streamlitï¼å¿«éååï¼?Vue.js + D3.jsï¼çäº§ç¯å¢ï¼
- åç«¯ï¼FastAPI + å¼æ­¥ä»»å¡éå
- æ°æ®åºï¼SQLiteï¼å¼åï¼?PostgreSQLï¼çäº§ï¼
- å¯è§åï¼PlotlyãEChartsãHighcharts

## å­ãå¼åéç¨ç¢

### Phase 1: åºç¡æåç³»ç»?å¨ï¼
- [ ] MultiCriteriaEvaluator TOPSISå®ç°
- [ ] PerformanceScorer åºç¡è¯åè®¡ç®
- [ ] ç­ç¥æ°æ®æ¥å£åé¢å¤ç
- [ ] åºç¡å½ä»¤è¡æ¥?

### Phase 2: é«çº§åæåè½?å¨ï¼
- [ ] WeightOptimizer å¨ææéè°?
- [ ] StrategyCorrelationAnalyzer ç¸å³æ§å?
- [ ] æ¶é´å æè¯åç®æ³
- [ ] å¯è§åæåæ¥?

### Phase 3: AIå³ç­æ¯æ?å¨ï¼
- [ ] AIStrategyRecommender AIæ¨èå¼æ
- [ ] èªç¶è¯­è¨è§£éçæ
- [ ] ç¨æ·åå¥½å­¦ä¹ 
- [ ] é¢æµæ¨¡åéæ

### Phase 4: çäº§å°±ç»ª?å¨ï¼
- [ ] Webä»ªè¡¨çå¼?
- [ ] å®æ¶æ°æ®éæ
- [ ] æ§è½ä¼ååç¼?
- [ ] å®æ´ææ¡£åç¤º?

## ä¸ãç¸å³ææ¡?

### ä¸æ¸¸ä¾èµ

| ææ¡£åç§° | module_id | ä¾èµç±»å | è¯´æ |
|---------|-----------|---------|------|
| [æ°æ®è´¨éçæ§èå¾](./DATA_QUALITY_MONITORING_BLUEPRINT.md) | DATA_QUALITY_MONITORING_001 | å¼ºä¾èµ?| æä¾æ°æ®è´¨éææ  |
| [æ°æ®ç®å½èå¾](./DATA_CATALOG_BLUEPRINT.md) | DATA_CATALOG_001 | å¼ºä¾èµ?| æä¾ç­ç¥åæ°æ?|
| [ç»åä¼åå¼æéæèå¾](./PORTFOLIO_OPTIMIZER_INTEGRATION_BLUEPRINT.md) | PORTFOLIO_OPTIMIZER_INTEGRATION_001 | ä¸­ä¾èµ?| æä¾ä¼åå¨åºç¡æ¥å£ |

### ä¸æ¸¸ä¾èµ

| ææ¡£åç§° | module_id | ä¾èµç±»å | è¯´æ |
|---------|-----------|---------|------|
| [æç¥æéåéèå¾](./STRATEGIC_WEIGHTING_BLUEPRINT.md) | STRATEGIC_WEIGHTING_001 | å¼ºä¾èµ?| æç¥æéåé |
| [å­£åº¦è°ä»èå¾](./QUARTERLY_REBALANCE_BLUEPRINT.md) | QUARTERLY_REBALANCE_001 | ä¸­ä¾èµ?| å­£åº¦è°ä»å³ç­ |
| [ç»ååå¹³è¡¡èå¾](./PORTFOLIO_REBALANCING_BLUEPRINT.md) | PORTFOLIO_REBALANCING_001 | ä¸­ä¾èµ?| ç»ååå¹³è¡?|

### ææ¯ä¾èµ?

| ææ¯ç»ä»?| çæ¬ | ç¨é?| ææ¡£ |
|---------|------|------|------|
| **NumPy** | 1.24+ | æ°å¼è®¡ç®?| [å®æ¹ææ¡£](https://numpy.org/) |
| **Pandas** | 2.0+ | æ°æ®å¤ç | [å®æ¹ææ¡£](https://pandas.pydata.org/) |
| **SciPy** | 1.10+ | ç§å­¦è®¡ç® | [å®æ¹ææ¡£](https://scipy.org/) |

### å¼ç¨å³ç³»å?

```mermaid
graph LR
    A[æ°æ®è´¨éçæ§] --> B[ç­ç¥éæ©ç³»ç»]
    C[æ°æ®ç®å½] --> B
    D[ç»åä¼åå¼æ] --> B
    
    B --> E[æç¥æéåé]
    B --> F[å­£åº¦è°ä»]
    B --> G[ç»ååå¹³è¡¡]
    
    style B fill:#ff6b6b
    style A fill:#4ecdc4
    style C fill:#45b7d1
```

### ç¸å³èå¾ææ¡£

| ææ¡£ | è¯´æ |
|------|------|
| STRATEGY_ENGINE_CORE_BLUEPRINT.md | ç­ç¥å¼ææ ¸å¿èå¾ |
| BATCH_EVALUATION_BLUEPRINT.md | æ¹éè¯ä¼°èå¾ |
| PARAMETER_OPTIMIZATION_BLUEPRINT.md | åæ°ä¼åèå¾ |
| PORTFOLIO_OPTIMIZATION_BLUEPRINT.md | ç»åä¼åèå¾ |

**ææ¡£çæ¬**: v1.0  
**æåæ´æ?*: 2026-04-01  
**ç»´æ¤è?*: ç­ç¥ç åä¸­å¿  
**é¢è®¡å¼åæ¶é?*: 80å°æ¶ï¼?å¨å¨èå¼åï¼

## åæ´åå²

| çæ¬ | æ¥æ | åæ´åå®¹ | åæ´äº?|
|------|------|----------|--------|
| v1.0.0 | 2026-04-01 | åå§çæ¬åå»º | é¦å¸­ææ¡£æ¶æå¸?|

## 1. ææ¡£æ²»ç

### 1.1 System_Manifest.mdç´¢å¼

```markdown
#### Layer 6: ç»åä¼åå±?
##### 6.001. Strategy Selection
- **æ¨¡åID**: STRATEGY_SELECTION_001
- **èå¾ææ¡£**: STRATEGY_SELECTION_BLUEPRINT.md
- **ææ¯è§æ ¼ä¹¦**: å¾åå»?
- **èè´£**: å¨ç³»ç»æ¶æè®¾è®?
- **ç¶æ?*: Active
```

### 1.2 æ¨¡åèè´£è¾¹ç

| æ¨¡å | èè´£ | è¾¹ç |
|------|------|------|
| **Strategy Selection** | å¨ç³»ç»æ¶æè®¾è®?| **æ ¸å¿æ¨¡å** |

### 1.3 çæ¬ç®¡ç

| çæ¬ | æ¥æ | åæ´åå®¹ | åæ´äº?|
|------|------|----------|--------|
| v1.0.0 | 2026-04-01 | åå§çæ¬åå»º | é¦å¸­èå¾æ¶æå¸?|

---

**èå¾çæ¬**: v1.0.0 | **åå»ºæ¥æ**: 2026-04-01 | **ç¶æ?*: Active
