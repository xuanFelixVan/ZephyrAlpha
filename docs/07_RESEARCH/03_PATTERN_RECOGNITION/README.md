# 模式识别算法库

> 技术分析图形模式识别

**版本**: v1.0
**更新**: 2026-03-29
**Layer**: Layer -1 / Layer 3
**索引**: 07_RESEARCH/03_PATTERN_RECOGNITION

---

## 1. 图形形态分类

### 反转形态

| 形态 | 说明 | 识别难度 |
|------|------|----------|
| 头肩顶/底 | 经典反转形态 | 中 |
| 双顶/双底 | W顶/M底形态 | 低 |
| 三重顶/底 | 更强阻力确认 | 中 |
| 圆弧顶/底 | 弧形反转 | 高 |
| V形反转 | 尖锐顶部/底部 | 高 |

### 持续形态

| 形态 | 说明 | 识别难度 |
|------|------|----------|
| 对称三角形 | 收敛整理 | 低 |
| 上升三角形 | 上升收敛 | 低 |
| 下降三角形 | 下降收敛 | 低 |
| 旗形整理 | 小矩形通道 | 中 |
| 矩形整理 | 箱体震荡 | 低 |

---

## 2. 模式识别接口

```python
class PatternRecognizer:
    """模式识别基类"""

    def recognize(self, ohlcv: pd.DataFrame) -> List[PatternSignal]:
        """识别模式"""
        raise NotImplementedError

    def validate(self, pattern: PatternSignal) -> bool:
        """验证模式有效性"""
        raise NotImplementedError


@dataclass
class PatternSignal:
    """模式信号"""
    pattern_type: str           # 'head_shoulder', 'double_top', etc.
    direction: str              # 'bullish', 'bearish'
    confidence: float           # 0-1
    start_idx: int
    end_idx: int
    key_levels: dict            # 关键价位
```

---

## 3. 头肩形态识别

```python
class HeadShoulderRecognizer(PatternRecognizer):
    """头肩形态识别器"""

    def __init__(self, tolerance: float = 0.02):
        self.tolerance = tolerance

    def recognize(self, highs: pd.Series, lows: pd.Series) -> List[PatternSignal]:
        """识别头肩形态"""
        swing_highs = self._find_swing_points(highs, lookback=20)
        signals = []

        for i in range(2, len(swing_highs) - 1):
            left_shoulder = swing_highs[i - 2]
            head = swing_highs[i - 1]
            right_shoulder = swing_highs[i]

            if self._is_valid_head_shoulder(left_shoulder, head, right_shoulder):
                signals.append(PatternSignal(
                    pattern_type='head_shoulder',
                    direction='bearish',
                    confidence=self._calculate_confidence(head, left_shoulder, right_shoulder),
                    start_idx=left_shoulder.index,
                    end_idx=right_shoulder.index,
                    key_levels={'neckline': self._find_neckline(left_shoulder, right_shoulder)}
                ))
        return signals
```

---

## 4. 蜡烛图模式

```python
class CandlestickPatternRecognizer:
    """蜡烛图模式识别"""

    PATTERNS = {
        'doji': lambda o, h, l, c: abs(o - c) / (h - l) < 0.1,
        'hammer': lambda o, h, l, c: (c > o) and ((h - c) > 3 * (c - l)),
        'engulfing_bullish': ...,
        'engulfing_bearish': ...,
        'morning_star': ...,
        'evening_star': ...
    }

    def recognize(self, ohlcv: pd.DataFrame) -> Dict[str, List[PatternSignal]]:
        """识别蜡烛图模式"""
        patterns = {}
        for name, condition in self.PATTERNS.items():
            signals = []
            for i in range(len(ohlcv)):
                if condition(ohlcv.iloc[i]):
                    signals.append(PatternSignal(
                        pattern_type=name,
                        direction='bullish' if 'bullish' in name else 'bearish',
                        confidence=0.6,
                        start_idx=i,
                        end_idx=i
                    ))
            patterns[name] = signals
        return patterns
```

---

## 5. 缠论识别

```python
class ChanTheoryRecognizer:
    """缠论笔、段、中枢识别"""

    def find_bi(self, prices: pd.Series, threshold: float = 0.03) -> List[Bi]:
        """识别笔"""
        direction = None
        bi_list = []
        start_idx = 0

        for i in range(1, len(prices)):
            change = (prices.iloc[i] - prices.iloc[start_idx]) / prices.iloc[start_idx]

            if direction is None and abs(change) >= threshold:
                direction = 'up' if change > 0 else 'down'
                start_idx = i
            elif direction == 'up' and prices.iloc[i] < prices.iloc[start_idx]:
                bi_list.append(Bi(start=start_idx, end=i-1, direction='up'))
                direction = 'down'
                start_idx = i - 1
            elif direction == 'down' and prices.iloc[i] > prices.iloc[start_idx]:
                bi_list.append(Bi(start=start_idx, end=i-1, direction='down'))
                direction = 'up'
                start_idx = i - 1

        return bi_list

    def find_duan(self, bi_list: List[Bi]) -> List[Duan]:
        """识别段 - 至少3笔重叠"""
        # 段识别逻辑
        pass

    def find_zhongshu(self, duan_list: List[Duan]) -> List[Zhongshu]:
        """识别中枢 - 至少3段重叠"""
        # 中枢识别逻辑
        pass
```

---

## 6. 人机交互研究循环

```
算法初筛 → 人工确认 → 反馈学习 → 批量验证 → 规则固化
```

```python
class InteractivePatternLearning:
    """人机交互模式学习"""

    def __init__(self, recognizer: PatternRecognizer):
        self.recognizer = recognizer
        self.confirmed_patterns = []
        self.rejected_patterns = []

    def present_for_confirmation(self, signal: PatternSignal) -> bool:
        """展示给用户确认"""
        # 返回True表示确认，False表示拒绝
        pass

    def learn_from_feedback(self, signal: PatternSignal, confirmed: bool):
        """从反馈中学习"""
        if confirmed:
            self.confirmed_patterns.append(signal)
        else:
            self.rejected_patterns.append(signal)

    def update_recognizer(self):
        """更新识别器参数"""
        # 基于确认/拒绝的模式调整识别参数
        pass
```

---

## 索引

- 父目录: [07_RESEARCH/README.md](../README.md)
- 相关文档: [statistical_tools.md](../02_EXPLORATORY_ANALYSIS/statistical_tools.md)
