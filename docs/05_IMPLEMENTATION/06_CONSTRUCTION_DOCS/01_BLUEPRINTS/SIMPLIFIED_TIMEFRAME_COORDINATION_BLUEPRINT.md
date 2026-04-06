???---
module_id: SIMPLIFIED_TIMEFRAME_COORDINATION_001
version: 1.0.0
spec_version: 1.0
status: Active
parent_doc: ../01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md
last_updated: 2026-04-03
created_date: 2026-04-03
layer: Layer 6 (����Ż�? | ҵ��ܹ�: ����ʱ�����ںϼܹ�
index: SIMPLIFIED_TIMEFRAME_COORDINATION_001
estimated_hours: 80h
review_status: Pending
reviewer: ��ϯ���������
review_date: 2026-04-03
owner: ����Ż��㸺����
standard_type: רҵ����������ͼ�ĵ����򻯰�?applicable_scope: ȫϵ?compliance_level: רҵ��׼
parent_document: ../INDEX.md
implementation_status: ��ƽ׶�
personal_development: true
ai_maintenance: true
simplified_version: true
---

# �򻯰��ʱ����Эͬ�Ż���?v1.0

> �������ϵͳ v5.3 - �򻯰��ʱ����Эͬ�Ż��ܹ���?> **����**: `TIMEFRAME_COORD_001`
> **����ʱ?*: 80h��Լ2�ܣ�
> **���Ķ�λ**: ˫ʱ����Эͬ����ۼ��� + �й��նȣ���ʵ���ź��ں����ͻ��?> **���˿�������?*: ???���ֿ��У��򻯰�?> **AIά���Ѷ�**: ?
---

## 1. ģ�����

### 1.1 ��˵?
**ԭ�����**��Two Sigmaʵ�֣���
- ����ʱ����Эͬ����ۼ�?+ �й��ն� + ΢�۷���?- ���ӵ��ź��ںϻ�?- ʱ���ܼ�ķ��մ��ݿ�?- ����ʱ�䣺120h

**�򻯰����**�����˿�����?- ?**����**: ˫ʱ����Эͬ����ۼ��� + �й��ն�?- ?**����**: �ź��ںϻ���
- ?**����**: ��ͻ�������
- ?**����**: ΢�۷��Ӽ�ʱ���?- ?**����**: ���ӵķ��մ��ݻ�?
**����?*?- ���˿�����Դ���ޣ�����ʵ�ֺ��Ĺ���
- ˫ʱ���������������Эͬ��?- ����ϵͳ���Ӷȣ�������ά��?
### 1.2 ҵ�񱳾����ֵ��?
**ҵ����?*?- ��ǰϵͳ��ʱ���ܶ����Ż����źų�ͻƵ��
- ȱ����ʱ���ܵ�Эͬ����
- �޷���Ч�ںϲ�ͬʱ���ܵ���?
**��ֵ��?*?- ʵ��˫ʱ�����ź���?- �źų�ͻ�ʽ�?0%
- ��������Ż�Ч��20%
- ΪTwo Sigmaģʽ�ṩ��������֧��

### 1.3 ������λ��ܹ����?
**Layer��λ**: Layer 6 - ����Ż��㣨Эͬ�Ż��㣩

**ģ�����**: ����ģ�飨�򻯰�?
**�ܹ���ɫ**: 
- ��Ϊ��ʱ���ܵ�Эͬ���ģ��ںϲ�ͬʱ���ܵ��ź�
- ��Ϊ�źų�ͻ�������Э����ͬʱ���ܵľ�?- ��Ϊ����Ż������룬�ṩЭͬ����ź�

### 1.4 ���Ĺ����嵥

1. **�ź��ں�**: �ںϺ�ۺ��й�ʱ���ܵ��ź�
2. **��ͻ��?*: ��ⲻͬʱ���ܵ��źų�ͻ
3. **��ͻ���**: ����źų�ͻ���������վ�?4. **Ȩ�ص���**: ��̬����ʱ����Ȩ?
---

## 2. �ܹ����

### 2.1 ϵͳ�ܹ�?
```
������������������������������������������������������������������������������������������������������������������������������������??             �򻯰��ʱ����Эͬ�Ż�ϵͳ��?                     ?������������������������������������������������������������������������������������������������������������������������������������??                                                                ?? ����������������������������������������������������������������������������������������������������������������������? ?? ?             ����?                                       ? ?? ? ����������������������������������������������? ����������������������������������������������?    ? ?? ? ?����źţ����ȣ�      ? ?�й��źţ��նȣ�      ?    ? ?? ? ?- ���÷�ʽ�ж�        ? ?- �����ź�           ?    ? ?? ? ?- ս���ʲ�����        ? ?- �����ź�           ?    ? ?? ? ?- ����Ԥ�����        ? ?- �����ź�           ?    ? ?? ? ����������������������������������������������? ����������������������������������������������?    ? ?? ����������������������������������������������������������������������������������������������������������������������? ??                         ?                                     ?? ����������������������������������������������������������������������������������������������������������������������? ?? ?             �ź��ں�?                                   ? ?? ? ����������������������������������������������������������������������������������������������������������? ? ?? ? ? Signal Fusion Engine                              ? ? ?? ? ? - �źű�׼?                                      ? ? ?? ? ? - �źż�Ȩ                                         ? ? ?? ? ? - �ź����                                         ? ? ?? ? ����������������������������������������������������������������������������������������������������������? ? ?? ����������������������������������������������������������������������������������������������������������������������? ??                         ?                                     ?? ����������������������������������������������������������������������������������������������������������������������? ?? ?             ��ͻ�������?                             ? ?? ? ����������������������? ����������������������? ����������������������?              ? ?? ? ?��ͻ��?? ?��ͻ���� ? ?��ͻ��� ?              ? ?? ? ?         ? ?         ? ?         ?              ? ?? ? ����������������������? ����������������������? ����������������������?              ? ?? ����������������������������������������������������������������������������������������������������������������������? ??                         ?                                     ?? ����������������������������������������������������������������������������������������������������������������������? ?? ?             Ȩ�ص���?                                   ? ?? ? ����������������������������������������������������������������������������������������������������������? ? ?? ? ? Dynamic Timeframe Weight Adjustment               ? ? ?? ? ? �����г�״̬��̬����ʱ����Ȩ?                  ? ? ?? ? ����������������������������������������������������������������������������������������������������������? ? ?? ����������������������������������������������������������������������������������������������������������������������? ??                         ?                                     ?? ����������������������������������������������������������������������������������������������������������������������? ?? ?             ���?                                       ? ?? ? ����������������������? ����������������������? ����������������������?              ? ?? ? ?Эͬ�ź� ? ?��ͻ���� ? ?Ȩ�ط��� ?              ? ?? ? ?         ? ?         ? ?         ?              ? ?? ? ����������������������? ����������������������? ����������������������?              ? ?? ����������������������������������������������������������������������������������������������������������������������? ?������������������������������������������������������������������������������������������������������������������������������������?```

### 2.2 ��������?
```
����źţ����ȣ� + �й��źţ��նȣ�
    ?�źű�׼�������
    ?�ź��ںϣ���Ȩ��ϣ�
    ?��ͻ��?    ?��ͻ��������г�ͻ��
    ?��̬Ȩ�ص�?    ?���Эͬ�ź�
```

---

## 3. ����ģ�����

### 3.1 �򻯰�ʱ����Эͬ����SimplifiedTimeframeCoordinator?
```python
class SimplifiedTimeframeCoordinator:
    """
    �򻯰��ʱ����Эͬ��
    
    ����: TIMEFRAME_COORD_001-M01
    ְ��: Э����ۺ��й�ʱ���ܵ��ź�
    ����: ����źš��й���?    ���: Эͬ����źš���ͻ��?    """
    
    def __init__(self, config: TimeframeConfig):
        self.config = config
        self.signal_fusion_engine = SignalFusionEngine(config.fusion_config)
        self.conflict_resolver = ConflictResolver(config.conflict_config)
        self.weight_adjuster = TimeframeWeightAdjuster(config.weight_config)
        
    def coordinate_signals(
        self,
        macro_signals: Dict[str, Signal],
        meso_signals: Dict[str, Signal],
        market_state: MarketState
    ) -> CoordinatedDecision:
        """
        Эͬ��ʱ������?        
        Args:
            macro_signals: ��۲��źţ�����?            meso_signals: �й۲��źţ��ն�?            market_state: �г�״?            
        Returns:
            CoordinatedDecision: Эͬ��ľ���
        """
        # 1. �źű�׼?        normalized_macro = self._normalize_signals(macro_signals)
        normalized_meso = self._normalize_signals(meso_signals)
        
        # 2. ��̬Ȩ�ص�?        timeframe_weights = self.weight_adjuster.adjust_weights(market_state)
        
        # 3. �ź��ں�
        fused_signals = self.signal_fusion_engine.fuse(
            normalized_macro, normalized_meso, timeframe_weights
        )
        
        # 4. ��ͻ��?        conflicts = self.conflict_resolver.detect_conflicts(
            normalized_macro, normalized_meso, fused_signals
        )
        
        # 5. ��ͻ���
        if conflicts:
            resolved_signals = self.conflict_resolver.resolve(conflicts, fused_signals)
        else:
            resolved_signals = fused_signals
        
        return CoordinatedDecision(
            signals=resolved_signals,
            timeframe_weights=timeframe_weights,
            conflicts=conflicts,
            conflict_resolution=self.conflict_resolver.get_resolution_log(),
            timestamp=datetime.now()
        )
    
    def fuse_signals(
        self,
        macro_signals: Dict[str, Signal],
        meso_signals: Dict[str, Signal],
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Signal]:
        """
        �ں��ź�
        
        Args:
            macro_signals: ����ź�
            meso_signals: �й��ź�
            weights: ʱ����Ȩ�أ���ѡ��
            
        Returns:
            Dict[str, Signal]: �ںϺ���ź�
        """
        if weights is None:
            weights = {'macro': 0.3, 'meso': 0.7}  # Ĭ��Ȩ��
        
        return self.signal_fusion_engine.fuse(
            macro_signals, meso_signals, weights
        )
    
    def detect_conflicts(
        self,
        macro_signals: Dict[str, Signal],
        meso_signals: Dict[str, Signal]
    ) -> List[SignalConflict]:
        """
        ����źų�?        
        Args:
            macro_signals: ����ź�
            meso_signals: �й��ź�
            
        Returns:
            List[SignalConflict]: ��ͻ�б�
        """
        return self.conflict_resolver.detect_conflicts(
            macro_signals, meso_signals
        )
    
    def _normalize_signals(
        self,
        signals: Dict[str, Signal]
    ) -> Dict[str, NormalizedSignal]:
        """�źű�׼?""
        normalized = {}
        for signal_name, signal in signals.items():
            normalized[signal_name] = NormalizedSignal(
                name=signal_name,
                value=signal.value,
                confidence=signal.confidence,
                direction=self._get_signal_direction(signal.value),
                strength=abs(signal.value)
            )
        return normalized
    
    def _get_signal_direction(self, value: float) -> str:
        """��ȡ�źŷ���"""
        if value > 0.1:
            return 'bullish'
        elif value < -0.1:
            return 'bearish'
        else:
            return 'neutral'
```

### 3.2 �ź��ں����棨SignalFusionEngine?
```python
class SignalFusionEngine:
    """
    �ź��ں�����
    
    ����: TIMEFRAME_COORD_001-M02
    ְ��: �ںϲ�ͬʱ���ܵ���?    """
    
    def __init__(self, config: FusionConfig):
        self.config = config
        
    def fuse(
        self,
        macro_signals: Dict[str, NormalizedSignal],
        meso_signals: Dict[str, NormalizedSignal],
        weights: Dict[str, float]
    ) -> Dict[str, Signal]:
        """
        �ں��ź�
        
        Args:
            macro_signals: ����ź�
            meso_signals: �й��ź�
            weights: ʱ����Ȩ��
            
        Returns:
            Dict[str, Signal]: �ںϺ���ź�
        """
        fused_signals = {}
        
        # ��ȡ�����ź���?        all_signal_names = set(macro_signals.keys()) | set(meso_signals.keys())
        
        for signal_name in all_signal_names:
            macro_signal = macro_signals.get(signal_name)
            meso_signal = meso_signals.get(signal_name)
            
            # ��Ȩ�ں�
            if macro_signal and meso_signal:
                fused_value = (
                    weights['macro'] * macro_signal.value +
                    weights['meso'] * meso_signal.value
                )
                fused_confidence = (
                    weights['macro'] * macro_signal.confidence +
                    weights['meso'] * meso_signal.confidence
                )
            elif macro_signal:
                fused_value = macro_signal.value
                fused_confidence = macro_signal.confidence
            elif meso_signal:
                fused_value = meso_signal.value
                fused_confidence = meso_signal.confidence
            else:
                continue
            
            fused_signals[signal_name] = Signal(
                name=signal_name,
                value=fused_value,
                confidence=fused_confidence,
                source='fusion'
            )
        
        return fused_signals
```

### 3.3 ��ͻ�������ConflictResolver?
```python
class ConflictResolver:
    """
    ��ͻ���?    
    ����: TIMEFRAME_COORD_001-M03
    ְ��: ���ͽ���źų�ͻ
    """
    
    def __init__(self, config: ConflictConfig):
        self.config = config
        self.resolution_log = []
        
    def detect_conflicts(
        self,
        macro_signals: Dict[str, NormalizedSignal],
        meso_signals: Dict[str, NormalizedSignal],
        fused_signals: Optional[Dict[str, Signal]] = None
    ) -> List[SignalConflict]:
        """
        ����źų�?        
        Args:
            macro_signals: ����ź�
            meso_signals: �й��ź�
            fused_signals: �ںϺ���źţ���ѡ��
            
        Returns:
            List[SignalConflict]: ��ͻ�б�
        """
        conflicts = []
        
        # ��鷽���?        for signal_name in set(macro_signals.keys()) & set(meso_signals.keys()):
            macro = macro_signals[signal_name]
            meso = meso_signals[signal_name]
            
            # �����෴
            if macro.direction != meso.direction and macro.direction != 'neutral' and meso.direction != 'neutral':
                conflicts.append(SignalConflict(
                    signal_name=signal_name,
                    conflict_type='direction',
                    macro_signal=macro,
                    meso_signal=meso,
                    severity='high' if abs(macro.value - meso.value) > 0.5 else 'medium'
                ))
            
            # ǿ�Ȳ������
            elif abs(macro.strength - meso.strength) > self.config.strength_threshold:
                conflicts.append(SignalConflict(
                    signal_name=signal_name,
                    conflict_type='strength',
                    macro_signal=macro,
                    meso_signal=meso,
                    severity='low'
                ))
        
        return conflicts
    
    def resolve(
        self,
        conflicts: List[SignalConflict],
        fused_signals: Dict[str, Signal]
    ) -> Dict[str, Signal]:
        """
        �����ͻ
        
        Args:
            conflicts: ��ͻ�б�
            fused_signals: �ںϺ���ź�
            
        Returns:
            Dict[str, Signal]: �����ͻ����ź�
        """
        resolved_signals = fused_signals.copy()
        
        for conflict in conflicts:
            if conflict.conflict_type == 'direction':
                # �����ͻ������ʹ�ú���źţ���������?                resolved_signals[conflict.signal_name] = Signal(
                    name=conflict.signal_name,
                    value=conflict.macro_signal.value * 0.6 + conflict.meso_signal.value * 0.4,
                    confidence=min(conflict.macro_signal.confidence, conflict.meso_signal.confidence) * 0.8,
                    source='resolution'
                )
                
                self.resolution_log.append({
                    'signal': conflict.signal_name,
                    'type': 'direction',
                    'resolution': 'weighted_average_with_macro_priority',
                    'timestamp': datetime.now()
                })
            
            elif conflict.conflict_type == 'strength':
                # ǿ�ȳ�ͻ��ʹ��ƽ��?                resolved_signals[conflict.signal_name] = Signal(
                    name=conflict.signal_name,
                    value=(conflict.macro_signal.value + conflict.meso_signal.value) / 2,
                    confidence=(conflict.macro_signal.confidence + conflict.meso_signal.confidence) / 2,
                    source='resolution'
                )
        
        return resolved_signals
    
    def get_resolution_log(self) -> List[Dict]:
        """��ȡ��ͻ�����־"""
        return self.resolution_log
```

### 3.4 ʱ����Ȩ�ص�������TimeframeWeightAdjuster?
```python
class TimeframeWeightAdjuster:
    """
    ʱ����Ȩ�ص���?    
    ����: TIMEFRAME_COORD_001-M04
    ְ��: �����г�״̬��̬����ʱ����Ȩ?    """
    
    def __init__(self, config: WeightConfig):
        self.config = config
        
    def adjust_weights(
        self,
        market_state: MarketState
    ) -> Dict[str, float]:
        """
        ����ʱ����Ȩ��
        
        Args:
            market_state: �г�״?            
        Returns:
            Dict[str, float]: ʱ����Ȩ��
        """
        # ����Ȩ��
        base_weights = {'macro': 0.3, 'meso': 0.7}
        
        # �����г�״̬��?        if market_state.volatility == 'high':
            # �߲����г������Ӻ��Ȩ�أ��������Ƹ��ɿ�?            weights = {'macro': 0.5, 'meso': 0.5}
        elif market_state.trend == 'strong':
            # ǿ�����г��������й�Ȩ�أ��������Ƹ�����?            weights = {'macro': 0.2, 'meso': 0.8}
        elif market_state.regime == 'crisis':
            # Σ���г������Ӻ��Ȩ�أ��������ø���Ҫ��
            weights = {'macro': 0.6, 'meso': 0.4}
        else:
            # �����г���ʹ�û���Ȩ��
            weights = base_weights
        
        return weights
```

### 3.5 �����ඨ?
```python
@dataclass
class TimeframeConfig:
    """ʱ����Эͬ����"""
    fusion_config: FusionConfig
    conflict_config: ConflictConfig
    weight_config: WeightConfig
    
@dataclass
class FusionConfig:
    """�ź��ں�����"""
    default_macro_weight: float = 0.3
    default_meso_weight: float = 0.7
    confidence_threshold: float = 0.5
    
@dataclass
class ConflictConfig:
    """��ͻ�����?""
    strength_threshold: float = 0.3  # ǿ�Ȳ�����?    direction_threshold: float = 0.1  # ���������?    
@dataclass
class WeightConfig:
    """Ȩ�ص�������"""
    adjustment_frequency: str = 'daily'  # ����Ƶ��
    min_weight: float = 0.1  # ��СȨ?    max_weight: float = 0.9  # ���Ȩ?```

---

## 4. ����ģ�Ͷ���

### 4.1 ��������ģ��

```python
@dataclass
class Signal:
    """�ź�"""
    name: str
    value: float  # �ź�ֵ��-1??    confidence: float  # ���Ŷȣ�0??    source: str  # �ź���Դ
    
@dataclass
class NormalizedSignal:
    """��׼����?""
    name: str
    value: float
    confidence: float
    direction: str  # bullish/bearish/neutral
    strength: float  # �ź�ǿ��
    
@dataclass
class MarketState:
    """�г�״?""
    volatility: str  # low/medium/high
    trend: str  # weak/strong
    regime: str  # normal/stress/crisis
```

### 4.2 �������ģ��

```python
@dataclass
class CoordinatedDecision:
    """Эͬ����"""
    signals: Dict[str, Signal]
    timeframe_weights: Dict[str, float]
    conflicts: List[SignalConflict]
    conflict_resolution: List[Dict]
    timestamp: datetime
    
@dataclass
class SignalConflict:
    """�źų�ͻ"""
    signal_name: str
    conflict_type: str  # direction/strength
    macro_signal: NormalizedSignal
    meso_signal: NormalizedSignal
    severity: str  # low/medium/high
```

---

## 5. ���ɷ���

### 5.1 ������Ż�������

```python
class PortfolioOptimizer:
    """����Ż���������ʱ����Эͬ?""
    
    def __init__(self, coordinator: SimplifiedTimeframeCoordinator):
        self.coordinator = coordinator
        
    def optimize_with_coordination(
        self,
        macro_signals: Dict[str, Signal],
        meso_signals: Dict[str, Signal],
        market_state: MarketState
    ) -> OptimizationResult:
        """Эͬ�Ż��������?""
        # 1. Эͬ�ź�
        coordinated = self.coordinator.coordinate_signals(
            macro_signals, meso_signals, market_state
        )
        
        # 2. ʹ��Эͬ�źŽ����Ż�
        optimized_weights = self._optimize_using_signals(coordinated.signals)
        
        return OptimizationResult(
            weights=optimized_weights,
            coordinated_signals=coordinated.signals,
            conflicts=coordinated.conflicts
        )
```

---

## 6. ʵʩ·��?
### 6.1 �����׶Σ�2�ܣ�

**Week 1: ���Ĺ��ܿ�?*
- Day 1-2: �ź��ں�����
- Day 3-4: ��ͻ�������?- Day 5: Ȩ�ص���?
**Week 2: �������?*
- Day 1-2: ϵͳ����
- Day 3: ��Ԫ����
- Day 4: ���ɲ���
- Day 5: �ĵ���д

### 6.2 ���?
| ���?| ʱ�� | ����?| ���ձ�׼ |
|--------|------|--------|----------|
| **M1: �ں��������** | Day 2 | �ź��ں����� | �ں����� |
| **M2: ��ͻ������** | Day 4 | ��ͻ���?| �����Ч |
| **M3: Ȩ�ص������** | Day 5 | Ȩ�ص���?| �������� |
| **M4: �������** | Day 7 | ����ϵͳ | ���нӿ���?|
| **M5: ����ͨ��** | Day 8 | ���Ա��� | ���в���ͨ�� |

---

## 7. Ԥ����������

### 7.1 ��������

| ָ�� | ��ǰˮƽ | Ŀ��ˮƽ | �������� |
|------|---------|---------|---------|
| **�źų�ͻ?* | ?| ?| -60% |
| **����Ż�Ч��** | ?| ?| +20% |
| **Эͬ��������** | ?| ?| ����2?|

### 7.2 ������?
- ?ʵ��Two Sigma�����������򻯰棩����ʱ����Э?- ?�����źų�ͻ?- ?��������Ż�Ч��
- ?����Эͬ���߻���

---

## 8. ��ԭ���?
| ��?| ԭ�棨Two Sigma?| �򻯰� | ˵�� |
|------|-----------------|--------|------|
| **ʱ��������** | ���� | ˫�� | �򻯼�?|
| **�ź��ںϷ���** | ���� | ��Ȩƽ�� | ����?|
| **��ͻ�������** | ���?| ����?| ���߼� |
| **����ʱ?* | 120h | 80h | ����33% |
| **ά������?* | ?| ?| �����Ѷ� |

---

## ��¼

### A. �ο���?
1. **��ʱ���ܷ�?*:
   - Murphy, J. (1999). "Technical Analysis of the Financial Markets"

2. **�ź��ں�����**:
   - Hall, D.L. and Llinas, J. (1997). "An Introduction to Multisensor Data Fusion"


---

## 9. �źų�ͻ���������ǿ���

### 9.1 ��ͻ������ϵ

`

                 �źų�ͻ������ϵ                                

                                                                 
     
    Level 1: �����ͻ��Direction Conflict��                   
    - ��ͷ vs ��ͷ                                            
    - ���س̶ȣ���                                            
    - ������ԣ��г�״̬���� + ���Ŷȼ�Ȩ                     
     
                                                                 
     
    Level 2: ǿ�ȳ�ͻ��Strength Conflict��                    
    - ǿ�ź� vs ���ź�                                        
    - ���س̶ȣ���                                            
    - ������ԣ���̬Ȩ�ص��� + ��ʷ���ֲο�                   
     
                                                                 
     
    Level 3: ���Ŷȳ�ͻ��Confidence Conflict��                
    - ������ vs ������                                        
    - ���س̶ȣ���                                            
    - ������ԣ����Ŷȼ�Ȩ + �ź���������                     
     
                                                                 
     
    Level 4: ʱ����ͻ��Timing Conflict��                      
    - �����ж� vs �ȴ��۲�                                    
    - ���س̶ȣ���                                            
    - ������ԣ��ֽ׶�ִ�� + ��̬���                         
     
                                                                 

`

### 9.2 ��ǿ�ͳ�ͻ�����

`python
class EnhancedConflictResolver:
    """
    ��ǿ�ͳ�ͻ�����
    
    ����: TIMEFRAME_COORD_001-M05����ǿ��
    ְ��: ��ά�ȳ�ͻ��������ܽ��
    """
    
    def __init__(self, config: EnhancedConflictConfig):
        self.config = config
        self.conflict_classifier = ConflictClassifier(config.classifier_config)
        self.priority_engine = ConflictPriorityEngine(config.priority_config)
        self.resolution_strategy_library = ResolutionStrategyLibrary()
        self.resolution_log = []
        
    def detect_all_conflicts(
        self,
        macro_signals: Dict[str, NormalizedSignal],
        meso_signals: Dict[str, NormalizedSignal],
        market_state: MarketState
    ) -> List[EnhancedSignalConflict]:
        """
        ����������͵ĳ�ͻ
        
        Args:
            macro_signals: ����ź�
            meso_signals: �й��ź�
            market_state: �г�״̬
            
        Returns:
            List[EnhancedSignalConflict]: ��ǿ�ͳ�ͻ�б�
        """
        all_conflicts = []
        
        # ��ⷽ���ͻ
        direction_conflicts = self._detect_direction_conflicts(
            macro_signals, meso_signals
        )
        all_conflicts.extend(direction_conflicts)
        
        # ���ǿ�ȳ�ͻ
        strength_conflicts = self._detect_strength_conflicts(
            macro_signals, meso_signals
        )
        all_conflicts.extend(strength_conflicts)
        
        # ������Ŷȳ�ͻ
        confidence_conflicts = self._detect_confidence_conflicts(
            macro_signals, meso_signals
        )
        all_conflicts.extend(confidence_conflicts)
        
        # ���ʱ����ͻ
        timing_conflicts = self._detect_timing_conflicts(
            macro_signals, meso_signals, market_state
        )
        all_conflicts.extend(timing_conflicts)
        
        # ��������ȼ�����
        classified_conflicts = self.conflict_classifier.classify(all_conflicts)
        prioritized_conflicts = self.priority_engine.prioritize(
            classified_conflicts, market_state
        )
        
        return prioritized_conflicts
    
    def resolve_with_strategy(
        self,
        conflicts: List[EnhancedSignalConflict],
        fused_signals: Dict[str, Signal],
        market_state: MarketState,
        historical_performance: Optional[Dict] = None
    ) -> ConflictResolutionResult:
        """
        ʹ�ò��Կ�����ͻ
        
        Args:
            conflicts: ��ͻ�б�
            fused_signals: �ں��ź�
            market_state: �г�״̬
            historical_performance: ��ʷ��������
            
        Returns:
            ConflictResolutionResult: ��ͻ������
        """
        resolved_signals = fused_signals.copy()
        resolution_details = []
        
        for conflict in conflicts:
            # ѡ��������
            strategy = self.resolution_strategy_library.select_strategy(
                conflict, market_state, historical_performance
            )
            
            # Ӧ�ò��Խ����ͻ
            resolved_signal = strategy.resolve(
                conflict, market_state, historical_performance
            )
            
            resolved_signals[conflict.signal_name] = resolved_signal
            
            # ��¼�������
            resolution_details.append({
                'signal_name': conflict.signal_name,
                'conflict_type': conflict.conflict_type,
                'severity': conflict.severity,
                'strategy_used': strategy.name,
                'resolution_value': resolved_signal.value,
                'timestamp': datetime.now()
            })
            
            self.resolution_log.append(resolution_details[-1])
        
        return ConflictResolutionResult(
            resolved_signals=resolved_signals,
            resolution_details=resolution_details,
            total_conflicts=len(conflicts),
            resolution_efficiency=self._calculate_resolution_efficiency(
                conflicts, resolution_details
            ),
            timestamp=datetime.now()
        )
    
    def _detect_direction_conflicts(
        self,
        macro_signals: Dict[str, NormalizedSignal],
        meso_signals: Dict[str, NormalizedSignal]
    ) -> List[EnhancedSignalConflict]:
        """��ⷽ���ͻ"""
        conflicts = []
        
        for signal_name in set(macro_signals.keys()) & set(meso_signals.keys()):
            macro = macro_signals[signal_name]
            meso = meso_signals[signal_name]
            
            # �жϷ���
            macro_direction = self._get_signal_direction(macro.value)
            meso_direction = self._get_signal_direction(meso.value)
            
            # �����෴�Ҷ���Ϊ����
            if (macro_direction != meso_direction and 
                macro_direction != 'neutral' and 
                meso_direction != 'neutral'):
                
                severity = self._calculate_direction_severity(
                    macro.value, meso.value
                )
                
                conflicts.append(EnhancedSignalConflict(
                    signal_name=signal_name,
                    conflict_type='direction',
                    macro_signal=macro,
                    meso_signal=meso,
                    severity=severity,
                    direction_info={
                        'macro_direction': macro_direction,
                        'meso_direction': meso_direction,
                        'value_diff': abs(macro.value - meso.value)
                    }
                ))
        
        return conflicts
    
    def _detect_strength_conflicts(
        self,
        macro_signals: Dict[str, NormalizedSignal],
        meso_signals: Dict[str, NormalizedSignal]
    ) -> List[EnhancedSignalConflict]:
        """���ǿ�ȳ�ͻ"""
        conflicts = []
        
        for signal_name in set(macro_signals.keys()) & set(meso_signals.keys()):
            macro = macro_signals[signal_name]
            meso = meso_signals[signal_name]
            
            strength_diff = abs(macro.strength - meso.strength)
            
            if strength_diff > self.config.strength_threshold:
                severity = 'medium' if strength_diff > 0.5 else 'low'
                
                conflicts.append(EnhancedSignalConflict(
                    signal_name=signal_name,
                    conflict_type='strength',
                    macro_signal=macro,
                    meso_signal=meso,
                    severity=severity,
                    strength_info={
                        'macro_strength': macro.strength,
                        'meso_strength': meso.strength,
                        'strength_diff': strength_diff
                    }
                ))
        
        return conflicts
    
    def _detect_confidence_conflicts(
        self,
        macro_signals: Dict[str, NormalizedSignal],
        meso_signals: Dict[str, NormalizedSignal]
    ) -> List[EnhancedSignalConflict]:
        """������Ŷȳ�ͻ"""
        conflicts = []
        
        for signal_name in set(macro_signals.keys()) & set(meso_signals.keys()):
            macro = macro_signals[signal_name]
            meso = meso_signals[signal_name]
            
            confidence_diff = abs(macro.confidence - meso.confidence)
            
            if confidence_diff > self.config.confidence_threshold:
                severity = 'medium' if confidence_diff > 0.4 else 'low'
                
                conflicts.append(EnhancedSignalConflict(
                    signal_name=signal_name,
                    conflict_type='confidence',
                    macro_signal=macro,
                    meso_signal=meso,
                    severity=severity,
                    confidence_info={
                        'macro_confidence': macro.confidence,
                        'meso_confidence': meso.confidence,
                        'confidence_diff': confidence_diff
                    }
                ))
        
        return conflicts
    
    def _detect_timing_conflicts(
        self,
        macro_signals: Dict[str, NormalizedSignal],
        meso_signals: Dict[str, NormalizedSignal],
        market_state: MarketState
    ) -> List[EnhancedSignalConflict]:
        """���ʱ����ͻ"""
        conflicts = []
        
        for signal_name in set(macro_signals.keys()) & set(meso_signals.keys()):
            macro = macro_signals[signal_name]
            meso = meso_signals[signal_name]
            
            # �ж�ʱ�����죨�����źű仯�ʣ�
            macro_urgency = self._calculate_signal_urgency(macro, market_state)
            meso_urgency = self._calculate_signal_urgency(meso, market_state)
            
            urgency_diff = abs(macro_urgency - meso_urgency)
            
            if urgency_diff > self.config.timing_threshold:
                conflicts.append(EnhancedSignalConflict(
                    signal_name=signal_name,
                    conflict_type='timing',
                    macro_signal=macro,
                    meso_signal=meso,
                    severity='low',
                    timing_info={
                        'macro_urgency': macro_urgency,
                        'meso_urgency': meso_urgency,
                        'urgency_diff': urgency_diff
                    }
                ))
        
        return conflicts
`

### 9.3 ��ͻ���ȼ�����

`python
class ConflictPriorityEngine:
    """
    ��ͻ���ȼ�����
    
    ����: TIMEFRAME_COORD_001-M06����ǿ��
    ְ��: ���ڶ�ά������ȷ����ͻ������ȼ�
    """
    
    def __init__(self, config: PriorityConfig):
        self.config = config
        
    def prioritize(
        self,
        conflicts: List[EnhancedSignalConflict],
        market_state: MarketState
    ) -> List[EnhancedSignalConflict]:
        """
        ȷ����ͻ���ȼ�
        
        Args:
            conflicts: ��ͻ�б�
            market_state: �г�״̬
            
        Returns:
            List[EnhancedSignalConflict]: �����ȼ�����ĳ�ͻ�б�
        """
        # ����ÿ����ͻ�����ȼ�����
        for conflict in conflicts:
            priority_score = self._calculate_priority_score(
                conflict, market_state
            )
            conflict.priority_score = priority_score
        
        # �����ȼ�����
        return sorted(
            conflicts, 
            key=lambda c: c.priority_score, 
            reverse=True
        )
    
    def _calculate_priority_score(
        self,
        conflict: EnhancedSignalConflict,
        market_state: MarketState
    ) -> float:
        """�������ȼ�����"""
        # �����������������س̶ȣ�
        severity_scores = {'high': 1.0, 'medium': 0.6, 'low': 0.3}
        base_score = severity_scores.get(conflict.severity, 0.5)
        
        # �г�״̬����
        market_adjustment = self._get_market_adjustment(market_state)
        
        # ��ͻ����Ȩ��
        type_weights = {
            'direction': 1.0,
            'confidence': 0.8,
            'strength': 0.6,
            'timing': 0.4
        }
        type_weight = type_weights.get(conflict.conflict_type, 0.5)
        
        # �ۺ����ȼ�����
        priority_score = base_score * market_adjustment * type_weight
        
        return priority_score
    
    def _get_market_adjustment(self, market_state: MarketState) -> float:
        """��ȡ�г�״̬����ϵ��"""
        # �߲����г�������ȼ�
        if market_state.volatility_regime == 'high':
            return 1.3
        # �����г��е����ȼ�
        elif market_state.trend_strength > 0.7:
            return 1.1
        # ���г��������ȼ�
        else:
            return 0.9
`

### 9.4 ������Կ�

`python
class ResolutionStrategyLibrary:
    """
    ��ͻ������Կ�
    
    ����: TIMEFRAME_COORD_001-M07����ǿ��
    ְ��: �ṩ���ֳ�ͻ�������
    """
    
    def __init__(self):
        self.strategies = {
            'direction': {
                'market_state_priority': MarketStatePriorityStrategy(),
                'confidence_weighted': ConfidenceWeightedStrategy(),
                'historical_performance': HistoricalPerformanceStrategy()
            },
            'strength': {
                'dynamic_weight': DynamicWeightStrategy(),
                'average_fusion': AverageFusionStrategy()
            },
            'confidence': {
                'quality_weighted': QualityWeightedStrategy(),
                'risk_adjusted': RiskAdjustedStrategy()
            },
            'timing': {
                'phased_execution': PhasedExecutionStrategy(),
                'monitor_and_act': MonitorAndActStrategy()
            }
        }
    
    def select_strategy(
        self,
        conflict: EnhancedSignalConflict,
        market_state: MarketState,
        historical_performance: Optional[Dict] = None
    ) -> ResolutionStrategy:
        """
        ѡ����ѽ������
        
        Args:
            conflict: ��ͻ����
            market_state: �г�״̬
            historical_performance: ��ʷ����
            
        Returns:
            ResolutionStrategy: �������
        """
        conflict_type = conflict.conflict_type
        available_strategies = self.strategies.get(conflict_type, {})
        
        # �����г�״̬ѡ�����
        if conflict_type == 'direction':
            if market_state.volatility_regime == 'high':
                return available_strategies['market_state_priority']
            elif historical_performance and historical_performance.get('accuracy', 0) > 0.7:
                return available_strategies['historical_performance']
            else:
                return available_strategies['confidence_weighted']
        
        elif conflict_type == 'strength':
            return available_strategies['dynamic_weight']
        
        elif conflict_type == 'confidence':
            return available_strategies['quality_weighted']
        
        elif conflict_type == 'timing':
            return available_strategies['phased_execution']
        
        # Ĭ�ϲ���
        return DefaultResolutionStrategy()


class MarketStatePriorityStrategy(ResolutionStrategy):
    """�г�״̬���Ȳ���"""
    
    name = 'market_state_priority'
    
    def resolve(
        self,
        conflict: EnhancedSignalConflict,
        market_state: MarketState,
        historical_performance: Optional[Dict] = None
    ) -> Signal:
        """�����г�״̬���ȼ���������ͻ"""
        # �������г������Ⱥ���ź�
        if market_state.trend_strength > 0.6:
            primary_signal = conflict.macro_signal
            secondary_signal = conflict.meso_signal
            primary_weight = 0.7
        # �����г��������й��ź�
        else:
            primary_signal = conflict.meso_signal
            secondary_signal = conflict.macro_signal
            primary_weight = 0.6
        
        resolved_value = (
            primary_weight * primary_signal.value +
            (1 - primary_weight) * secondary_signal.value
        )
        
        resolved_confidence = min(
            primary_signal.confidence,
            secondary_signal.confidence
        ) * 0.85
        
        return Signal(
            name=conflict.signal_name,
            value=resolved_value,
            confidence=resolved_confidence,
            source='market_state_priority_resolution'
        )


class ConfidenceWeightedStrategy(ResolutionStrategy):
    """���Ŷȼ�Ȩ����"""
    
    name = 'confidence_weighted'
    
    def resolve(
        self,
        conflict: EnhancedSignalConflict,
        market_state: MarketState,
        historical_performance: Optional[Dict] = None
    ) -> Signal:
        """�������Ŷȼ�Ȩ�����ͻ"""
        total_confidence = (
            conflict.macro_signal.confidence + 
            conflict.meso_signal.confidence
        )
        
        if total_confidence == 0:
            # ������Ŷȶ�Ϊ0��ƽ������
            macro_weight = 0.5
            meso_weight = 0.5
        else:
            macro_weight = conflict.macro_signal.confidence / total_confidence
            meso_weight = conflict.meso_signal.confidence / total_confidence
        
        resolved_value = (
            macro_weight * conflict.macro_signal.value +
            meso_weight * conflict.meso_signal.value
        )
        
        resolved_confidence = (
            macro_weight * conflict.macro_signal.confidence +
            meso_weight * conflict.meso_signal.confidence
        )
        
        return Signal(
            name=conflict.signal_name,
            value=resolved_value,
            confidence=resolved_confidence,
            source='confidence_weighted_resolution'
        )
`

### 9.5 ��ǿ������

`python
@dataclass
class EnhancedConflictConfig:
    """��ǿ�ͳ�ͻ�������"""
    classifier_config: ConflictClassifierConfig
    priority_config: PriorityConfig
    
    # ��ͻ�����ֵ
    strength_threshold: float = 0.3  # ǿ�Ȳ�����ֵ
    confidence_threshold: float = 0.3  # ���ŶȲ�����ֵ
    timing_threshold: float = 0.4  # ʱ��������ֵ
    
    # �����������
    default_strategy: str = 'confidence_weighted'
    enable_adaptive_strategy: bool = True  # ����Ӧ����ѡ��
    
    # ��ʷ����Ȩ��
    historical_weight: float = 0.3  # ��ʷ�����ڲ���ѡ���е�Ȩ��

@dataclass
class ConflictClassifierConfig:
    """��ͻ����������"""
    enable_multi_level: bool = True  # ���ö��η���
    severity_thresholds: Dict[str, float] = field(default_factory=lambda: {
        'high': 0.7,
        'medium': 0.4,
        'low': 0.2
    })
`

### 9.6 ��ǿ����ģ��

`python
@dataclass
class EnhancedSignalConflict:
    """��ǿ���źų�ͻ"""
    signal_name: str
    conflict_type: str  # direction/strength/confidence/timing
    macro_signal: NormalizedSignal
    meso_signal: NormalizedSignal
    severity: str  # high/medium/low
    priority_score: float = 0.0
    
    # ��ͻ��ϸ��Ϣ
    direction_info: Optional[Dict] = None
    strength_info: Optional[Dict] = None
    confidence_info: Optional[Dict] = None
    timing_info: Optional[Dict] = None

@dataclass
class ConflictResolutionResult:
    """��ͻ������"""
    resolved_signals: Dict[str, Signal]
    resolution_details: List[Dict]
    total_conflicts: int
    resolution_efficiency: float  # ���Ч������
    timestamp: datetime
`

### 9.7 Ԥ�����棨��ǿ�棩

| ָ�� | �򻯰� | ��ǿ�� | �������� |
|------|--------|--------|---------|
| **��ͻ���ά��** | 2�� | 4�� | +100% |
| **��ͻ�������** | 2�� | 8�� | +300% |
| **��ͻ���׼ȷ��** | 75% | 90% | +15% |
| **�źų�ͻ��** | 30% | 15% | -50% |
| **Эͬ��������** | ���� | ���� | ����1���ȼ� |
---

**��ͼ�汾**: v1.0 | **��������**: 2026-04-03 | **״?*: Final | **�򻯰�**: ?| **��һ?*: ����������д

