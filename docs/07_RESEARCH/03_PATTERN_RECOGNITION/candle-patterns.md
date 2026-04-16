---
module_id: CANDLE_PATTERNS_5495
version: 1.0.0
status: Active
created_date: 2026-04-13
last_updated: 2026-04-13
owner: 首席文档架构师
layer: layer_00
responsibility: 03_PATTERN_RECOGNITION
standard_type: 专业量化机构研究标准
applicable_scope: 量化研究实验
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行?
---
## 1. 系统概述











### 1.1 目标





提供专业的蜡烛图模式识别能力，识别单根蜡烛和多根蜡烛组合形态，输出可交易的量化信号?











### 1.2 识别范围











| 类别 | 形?| 交易方向 |





|------|------|----------|





| **单根蜡烛** | 锤子线、吊颈线、射击之星、十字星、纺锤线 | 趋势反转 |





| **两根组合** | 吞没形?看涨/看跌)、乌云盖顶、刺透形?| 趋势反转 |





| **三根组合** | 早晨之星、黄昏之星、三兵形??? | 趋势反转/延续 |





| **持续形?* | 跳空缺口、上升三法、下降三?| 趋势持续 |











```
```---
```











## 2. 蜡烛图基础定义











### 2.1 蜡烛结构











```python





@dataclass





class Candle:





    """蜡烛图数据单?""





    open: float       # 开盘价





    high: float       # 最高价





    low: float        # 最低价





    close: float      # 收盘?





    volume: float     # 成交?可?





    date: datetime    # 日期











    @property





    def body(self) -> float:





        """蜡烛实体"""





        return abs(self.close - self.open)











    @property





    def body_ratio(self) -> float:





        """实体占比 = 实体 / 全幅"""





        full_range = self.high - self.low





        return self.body / full_range if full_range > 0 else 0











    @property





    def upper_shadow(self) -> float:





        """上影?""





        return self.high - max(self.open, self.close)











    @property





    def lower_shadow(self) -> float:





        """下影?""





        return min(self.open, self.close) - self.low











    @property





    def direction(self) -> str:





        """方向: bullish/bearish/neutral"""





        if self.close > self.open:





            return "bullish"





        elif self.close < self.open:





            return "bearish"





        return "neutral"





```











```
```---
```











## 3. 单根蜡烛模式











### 3.1 锤子?(Hammer)











**定义**: 出现在下跌趋势底部的小实体蜡烛，下影线长度至少是实体?倍，上影线很短?











**识别参数**:





```python





@dataclass





class HammerConfig:





    min_lower_shadow_ratio: float = 2.0  # 下影?实体 最小比?





    max_upper_shadow_ratio: float = 0.5    # 上影?实体 最大比?





    min_body_ratio: float = 0.1           # 最小实体占?





    max_body_ratio: float = 0.4          # 最大实体占?





```











**识别逻辑**:





```python





def recognize_hammer(self, candle: Candle, prev_candle: Candle = None) -> Optional[Signal]:





    """





    识别锤子?





    条件:





    1. 当前趋势: 下跌(可?通过prev_candle判断)





    2. 下影?>= 实体 * 2





    3. 上影?<= 实体 * 0.5





    4. 实体位于价格区间的上?





    """





    # 条件1: 下影线足够长





    if candle.lower_shadow < candle.body * self.config.min_lower_shadow_ratio:





        return None











    # 条件2: 上影线足够短





    if candle.upper_shadow > candle.body * self.config.max_upper_shadow_ratio:





        return None











    # 条件3: 实体不能太大





    if candle.body_ratio < self.config.min_body_ratio:





        return None





    if candle.body_ratio > self.config.max_body_ratio:





        return None











    # 条件4: 实体位于上端(收盘价接近最高价)





    candle_position = (candle.close - candle.low) / (candle.high - candle.low)





    if candle_position < 0.7:  # 收盘价在区间70%以下





        return None











    # 计算置信?





    confidence = self._calculate_hammer_confidence(candle)











    return Signal(





        pattern="hammer",





        direction="bullish",





        confidence=confidence,





        entry_price=candle.close,





        stop_loss=candle.low,





        target=self._calculate_target(candle, "bullish")





    )





```











**置信度计?*:





```python





def _calculate_hammer_confidence(self, candle: Candle) -> float:





    """计算锤子线置信度"""





    score = 0.0











    # 下影线越长越?(0-0.4)





    lower_ratio = candle.lower_shadow / candle.body if candle.body > 0 else 3





    score += min(lower_ratio / 5, 0.4)  # 下影线是实体?倍以上给0.4?











    # 实体越小越好 (0-0.2)





    score += (1 - candle.body_ratio) * 0.2











    # 上影线越短越?(0-0.2)





    upper_ratio = candle.upper_shadow / candle.body if candle.body > 0 else 0





    score += (1 - min(upper_ratio, 1)) * 0.2











    # 收盘位置越高越好 (0-0.2)





    position = (candle.close - candle.low) / (candle.high - candle.low)





    score += position * 0.2











    return min(score, 1.0)





```











### 3.2 吊颈?(Hanging Man)











**定义**: 与锤子线形态相同，但出现在上涨趋势顶部，是看跌反转信号?











**与锤子线的区?*:





```python





def recognize_hanging_man(self, candle: Candle, prev_trend: str) -> Optional[Signal]:





    """





    吊颈线识?





    关键区别:





    1. 出现在上涨趋势中(prev_trend == "uptrend")





    2. 看跌信号





    3. 实体可以是阴线或阳线





    """





    # 必须出现在上涨趋势中





    if prev_trend != "uptrend":





        return None











    # 形态条件与锤子线相?





    if not self._is_similar_to_hammer(candle):





        return None











    # 吊颈线是看跌信号





    return Signal(





        pattern="hanging_man",





        direction="bearish",





        confidence=self._calculate_hanging_man_confidence(candle),





        entry_price=candle.close,





        stop_loss=candle.high,  # 止损在最高价上方





        target=self._calculate_target(candle, "bearish")





    )





```











### 3.3 射击之星 (Shooting Star)











**定义**: 出现在上涨趋势顶部，上影线长度至少是实体?倍，下影线很短?











**识别参数**:





```python





@dataclass





class ShootingStarConfig:





    min_upper_shadow_ratio: float = 2.0   # 上影?实体 最小比?





    max_lower_shadow_ratio: float = 0.3  # 下影?实体 最大比?





    min_body_ratio: float = 0.1           # 最小实体占?





    max_body_ratio: float = 0.4           # 最大实体占?





```











**识别逻辑**:





```python





def recognize_shooting_star(self, candle: Candle, prev_trend: str) -> Optional[Signal]:





    """





    识别射击之星





    条件:





    1. 出现在上涨趋势中





    2. 上影?>= 实体 * 2





    3. 下影?<= 实体 * 0.3





    4. 实体位于价格区间的下?





    """





    if prev_trend != "uptrend":





        return None











    # 上影线足够长





    if candle.upper_shadow < candle.body * self.config.min_upper_shadow_ratio:





        return None











    # 下影线足够短





    if candle.lower_shadow > candle.body * self.config.max_lower_shadow_ratio:





        return None











    # 实体位于下端(开盘价或收盘价接近最低价)





    candle_position = (candle.close - candle.low) / (candle.high - candle.low)





    if candle_position > 0.4:  # 收盘价在区间40%以上





        return None











    return Signal(





        pattern="shooting_star",





        direction="bearish",





        confidence=self._calculate_shooting_star_confidence(candle),





        entry_price=candle.close,





        stop_loss=candle.high,





        target=self._calculate_target(candle, "bearish")





    )





```











### 3.4 十字?(Doji)











**定义**: 开盘价与收盘价相同或非常接近，实体几乎为零?











**识别参数**:





```python





@dataclass





class DojiConfig:





    max_body_ratio: float = 0.05      # 最大实体占?5%)





    min_shadow_ratio: float = 0.3     # 最小影线占?影线要比较明?





```











**识别逻辑**:





```python





def recognize_doji(self, candle: Candle) -> Optional[Signal]:





    """





    识别十字?





    类型:





    1. 普通十字星





    2. 长腿十字?影线很长)





    3. 墓碑十字?主要是上影线)





    4. 蜻蜓十字?主要是下影线)





    """





    # 实体必须很小





    if candle.body_ratio > self.config.max_body_ratio:





        return None











    full_range = candle.high - candle.low





    if full_range == 0:





        return None











    # 影线要比较明?





    total_shadow = candle.upper_shadow + candle.lower_shadow





    if total_shadow / full_range < self.config.min_shadow_ratio:





        return None











    # 判断十字星类?





    doji_type = self._classify_doji(candle)











    return Signal(





        pattern="doji",





        pattern_type=doji_type,  # 长腿/墓碑/蜻蜓/普?





        direction="neutral",      # 十字星本身是中性的





        confidence=self._calculate_doji_confidence(candle),





        metadata={





            "upper_shadow_ratio": candle.upper_shadow / full_range,





            "lower_shadow_ratio": candle.lower_shadow / full_range,





        }





    )











def _classify_doji(self, candle: Candle) -> str:





    """分类十字星类?""





    full_range = candle.high - candle.low





    upper_ratio = candle.upper_shadow / full_range





    lower_ratio = candle.lower_shadow / full_range











    if upper_ratio > 0.4 and lower_ratio > 0.4:





        return "long_leg"  # 长腿十字?





    elif upper_ratio > 0.9:





        return "gravestone"  # 墓碑十字?





    elif lower_ratio > 0.9:





        return "dragonfly"  # 蜻蜓十字?





    return "common"  # 普通十字星





```











```
```---
```











## 4. 两根蜡烛组合











### 4.1 吞没形?(Engulfing Pattern)











**定义**: 第二根蜡烛的实体完全"吞没"第一根蜡烛的实体系











**看涨吞没 (Bullish Engulfing)**:





```python





def recognize_bullish_engulfing(self, c1: Candle, c2: Candle) -> Optional[Signal]:





    """





    识别看涨吞没





    条件:





    1. 第一根蜡烛是阴线(下跌趋势)





    2. 第二根蜡烛是阳线





    3. 第二根的开盘价 < 第一根的收盘?





    4. 第二根的收盘?> 第一根的开盘价





    """





    # 条件1: 第一根是阴线





    if c1.direction != "bearish":





        return None











    # 条件2: 第二根是阳线





    if c2.direction != "bullish":





        return None











    # 条件3: 第二根开盘价低于第一根收盘价





    if c2.open >= c1.close:





        return None











    # 条件4: 第二根收盘价高于第一根开盘价





    if c2.close <= c1.open:





        return None











    # 计算置信?





    confidence = self._calculate_engulfing_confidence(c1, c2, "bullish")











    return Signal(





        pattern="bullish_engulfing",





        direction="bullish",





        confidence=confidence,





        entry_price=c2.close,





        stop_loss=min(c1.low, c2.low),





        target=self._calculate_target(c2, "bullish", c1)





    )





```











**看跌吞没 (Bearish Engulfing)**:





```python





def recognize_bearish_engulfing(self, c1: Candle, c2: Candle) -> Optional[Signal]:





    """





    识别看跌吞没





    条件:





    1. 第一根蜡烛是阳线(上涨趋势)





    2. 第二根蜡烛是阴线





    3. 第二根的开盘价 > 第一根的收盘?





    4. 第二根的收盘?< 第一根的开盘价





    """





    if c1.direction != "bullish":





        return None





    if c2.direction != "bearish":





        return None





    if c2.open <= c1.close:





        return None





    if c2.close >= c1.open:





        return None











    return Signal(





        pattern="bearish_engulfing",





        direction="bearish",





        confidence=self._calculate_engulfing_confidence(c1, c2, "bearish"),





        entry_price=c2.close,





        stop_loss=max(c1.high, c2.high),





        target=self._calculate_target(c2, "bearish", c1)





    )





```











**置信度计?*:





```python





def _calculate_engulfing_confidence(self, c1: Candle, c2: Candle, direction: str) -> float:





    """计算吞没形态置信度"""





    score = 0.5  # 基础?











    # 吞没程度 (0-0.3)





    if direction == "bullish":





        engulf_ratio = min((c2.close - c1.open) / c1.body, 2) if c1.body > 0 else 0





    else:





        engulf_ratio = min((c1.open - c2.close) / c1.body, 2) if c1.body > 0 else 0





    score += min(engulf_ratio * 0.15, 0.3)











    # 趋势长度 (0-0.1)





    if c1.body > 0:





        trend_persistence = c1.body / (c1.high - c1.low)





        score += trend_persistence * 0.1











    # 成交量确?(如果? (0-0.1)





    if hasattr(c1, 'volume') and hasattr(c2, 'volume'):





        if c2.volume > c1.volume * 1.5:





            score += 0.1











    return min(score, 1.0)





```











### 4.2 乌云盖顶 (Dark Cloud Cover)











**定义**: 出现在上涨趋势中，第一根阳线后出现一根高开低走的阴线，开盘价高于第一根收盘价，收盘价深入到第一根阳线实体内部?











**识别逻辑**:





```python





def recognize_dark_cloud_cover(self, c1: Candle, c2: Candle) -> Optional[Signal]:





    """





    识别乌云盖顶





    条件:





    1. 第一根是阳线(上涨趋势)





    2. 第二根是阴线





    3. 第二根开盘价 > 第一根最高价





    4. 第二根收盘价 < 第一根收盘价





    5. 第二根收盘价 >= 第一根开盘价 + 实体中点(至少50%乌云)





    """





    if c1.direction != "bullish":





        return None





    if c2.direction != "bearish":





        return None





    if c2.open <= c1.high:





        return None





    if c2.close >= c1.close:





        return None











    # 计算乌云程度





    c1_midpoint = (c1.open + c1.close) / 2





    cloud_penetration = (c1.close - c2.close) / c1.body











    # 至少50%乌云





    if cloud_penetration < 0.5:





        return None











    return Signal(





        pattern="dark_cloud_cover",





        direction="bearish",





        confidence=0.6 + cloud_penetration * 0.2,  # 乌云越深置信度越?





        entry_price=c2.close,





        stop_loss=c2.high,





        target=self._calculate_target(c2, "bearish", c1),





        metadata={"cloud_penetration": cloud_penetration}





    )





```











### 4.3 刺透形?(Piercing Pattern)











**定义**: 与乌云盖顶相反，是看涨反转型态?











**识别逻辑**:





```python





def recognize_piercing_pattern(self, c1: Candle, c2: Candle) -> Optional[Signal]:





    """





    识别刺透形?





    条件:





    1. 第一根是阴线(下跌趋势)





    2. 第二根是阳线





    3. 第二根开盘价 < 第一根最低价





    4. 第二根收盘价 > 第一根收盘价





    5. 第二根收盘价 <= 第一根开盘价 - 实体中点(至少50%刺?





    """





    if c1.direction != "bearish":





        return None





    if c2.direction != "bullish":





        return None





    if c2.open >= c1.low:





        return None





    if c2.close <= c1.close:





        return None











    c1_midpoint = (c1.open + c1.close) / 2





    penetration = (c2.close - c1_midpoint) / c1.body











    if penetration < 0.5:





        return None











    return Signal(





        pattern="piercing_pattern",





        direction="bullish",





        confidence=0.6 + penetration * 0.2,





        entry_price=c2.close,





        stop_loss=c2.low,





        target=self._calculate_target(c2, "bullish", c1),





        metadata={"penetration": penetration}





    )





```











```
```---
```











## 5. 三根蜡烛组合











### 5.1 早晨之星 (Morning Star)











**定义**: 下跌趋势中出现的三根蜡烛组合，中间一根为小实?星线)，第三根阳线向上深入第一根阴线内部?











**识别逻辑**:





```python





def recognize_morning_star(self, c1: Candle, c2: Candle, c3: Candle) -> Optional[Signal]:





    """





    识别早晨之星





    条件:





    1. 第一根是阴线(下跌趋势确认)





    2. 第二根是小实体星线，开盘价与收盘价接近





    3. 第二根与第一根有跳空缺口(可选但推荐)





    4. 第三根是阳线，收盘价深入第一根阴线内?超过50%)





    """





    # 条件1: 第一根阴?





    if c1.direction != "bearish" or c1.body_ratio < 0.3:





        return None











    # 条件2: 第二根是小实?





    if c2.body_ratio > 0.2:





        return None











    # 条件3: 第三根是阳线





    if c3.direction != "bullish" or c3.body_ratio < 0.3:





        return None











    # 条件4: 第三根深入第一根内?





    penetration = (c3.close - (c1.open + c1.close) / 2) / c1.body





    if penetration < 0.5:





        return None











    # 可? 跳空缺口





    has_gap_down = c2.high < c1.low











    return Signal(





        pattern="morning_star",





        direction="bullish",





        confidence=self._calculate_morning_star_confidence(c1, c2, c3),





        entry_price=c3.close,





        stop_loss=min(c1.low, c2.low),





        target=self._calculate_target(c3, "bullish", c1),





        metadata={





            "has_gap_down": has_gap_down,





            "star_body_ratio": c2.body_ratio,





            "penetration": penetration





        }





    )





```











### 5.2 黄昏之星 (Evening Star)











**定义**: 与早晨之星相反，是看跌反转型态?











**识别逻辑**:





```python





def recognize_evening_star(self, c1: Candle, c2: Candle, c3: Candle) -> Optional[Signal]:





    """





    识别黄昏之星





    条件:





    1. 第一根是阳线(上涨趋势确认)





    2. 第二根是小实体星?





    3. 第三根是阴线，收盘价深入第一根阳线内?超过50%)





    """





    if c1.direction != "bullish" or c1.body_ratio < 0.3:





        return None





    if c2.body_ratio > 0.2:





        return None





    if c3.direction != "bearish" or c3.body_ratio < 0.3:





        return None











    penetration = ((c1.open + c1.close) / 2 - c3.close) / c1.body





    if penetration < 0.5:





        return None











    has_gap_up = c2.low > c1.high











    return Signal(





        pattern="evening_star",





        direction="bearish",





        confidence=self._calculate_evening_star_confidence(c1, c2, c3),





        entry_price=c3.close,





        stop_loss=max(c1.high, c2.high),





        target=self._calculate_target(c3, "bearish", c1),





        metadata={





            "has_gap_up": has_gap_up,





            "star_body_ratio": c2.body_ratio,





            "penetration": penetration





        }





    )





```











### 5.3 三兵形?(Three Soldiers/Crows)











**三白?(Three White Soldiers)** - 看涨:





```python





def recognize_three_white_soldiers(self, c1: Candle, c2: Candle, c3: Candle) -> Optional[Signal]:





    """





    识别三白?





    条件:





    1. 三根连续阳线





    2. 每根收盘价逐步上升





    3. 每根开盘价在前一根实体内?





    4. 每根影线较短





    """





    if not all(c.direction == "bullish" for c in [c1, c2, c3]):





        return None





    if not (c2.close > c1.close and c3.close > c2.close):





        return None











    # 开盘价在前一根实体内?





    if not (c2.open > c1.low and c2.open < c1.close):





        return None





    if not (c3.open > c2.low and c3.open < c2.close):





        return None











    # 影线较短





    for c in [c1, c2, c3]:





        if c.upper_shadow > c.body * 0.3:





            return None











    return Signal(





        pattern="three_white_soldiers",





        direction="bullish",





        confidence=0.85,





        entry_price=c3.close,





        stop_loss=c1.low,





        target=self._calculate_target(c3, "bullish", c1)





    )





```











**三黑?(Three Black Crows)** - 看跌:





```python





def recognize_three_black_crows(self, c1: Candle, c2: Candle, c3: Candle) -> Optional[Signal]:





    """





    识别三黑?





    条件:





    1. 三根连续阴线





    2. 每根收盘价逐步下降





    3. 每根开盘价在前一根实体内?





    4. 每根影线较短





    """





    if not all(c.direction == "bearish" for c in [c1, c2, c3]):





        return None





    if not (c2.close < c1.close and c3.close < c2.close):





        return None











    if not (c2.open < c1.high and c2.open > c1.close):





        return None





    if not (c3.open < c2.high and c3.open > c2.close):





        return None











    for c in [c1, c2, c3]:





        if c.lower_shadow > c.body * 0.3:





            return None











    return Signal(





        pattern="three_black_crows",





        direction="bearish",





        confidence=0.85,





        entry_price=c3.close,





        stop_loss=c1.high,





        target=self._calculate_target(c3, "bearish", c1)





    )





```











```
```---
```











## 6. 持续形?











### 6.1 跳空缺口 (Gap)











```python





def recognize_gap(self, c1: Candle, c2: Candle) -> Optional[Signal]:





    """





    识别跳空缺口





    类型:





    1. 向上跳空(看涨)





    2. 向下跳空(看跌)





    3. 岛型反转(非常?





    """





    if c2.high < c1.low:  # 向上跳空





        return Signal(





            pattern="gap_up",





            direction="bullish",





            confidence=0.7,





            entry_price=c2.low,





            stop_loss=c1.low,





            target=self._calculate_target(c2, "bullish", c1),





            metadata={"gap_size": c1.low - c2.high}





        )











    if c2.low > c1.high:  # 向下跳空





        return Signal(





            pattern="gap_down",





            direction="bearish",





            confidence=0.7,





            entry_price=c2.high,





            stop_loss=c1.high,





            target=self._calculate_target(c2, "bearish", c1),





            metadata={"gap_size": c2.low - c1.high}





        )











    return None





```











### 6.2 上升三法/下降三法 (Three Methods)











```python





def recognize_three_methods(self, candles: List[Candle]) -> Optional[Signal]:





    """





    识别三法形?





    上升三法: 上涨趋势中出现回调，然后继续上涨





    下降三法: 下跌趋势中出现反弹，然后继续下跌





    """





    if len(candles) < 5:





        return None











    c1, c2, c3, c4, c5 = candles[0], candles[1], candles[2], candles[3], candles[4]











    # 上升三法





    if c1.direction == "bullish" and c5.direction == "bullish":





        # 中间3根在第一根范围内





        if all(c1.low <= c.low <= c1.high for c in [c2, c3, c4]):





            return Signal(





                pattern="rising_three_methods",





                direction="bullish",





                confidence=0.8,





                entry_price=c5.close,





                stop_loss=c1.low,





                target=self._calculate_target(c5, "bullish", c1)





            )











    # 下降三法





    if c1.direction == "bearish" and c5.direction == "bearish":





        if all(c1.low <= c.low <= c1.high for c in [c2, c3, c4]):





            return Signal(





                pattern="falling_three_methods",





                direction="bearish",





                confidence=0.8,





                entry_price=c5.close,





                stop_loss=c1.high,





                target=self._calculate_target(c5, "bearish", c1)





            )











    return None





```











```
```---
```











## 7. 统一信号输出格式











### 7.1 Signal 数据结构











```python





@dataclass





class CandlestickSignal:





    """蜡烛图信?""





    pattern: str                    # 形态名?





    direction: str                 # bullish/bearish/neutral





    confidence: float              # 置信?0-1











    # 交易点位





    entry_price: float             # 入场价格





    stop_loss: float               # 止损价格





    target: float                  # 目标价格











    # 上下?





    bar_index: int                 # 信号所在bar索引





    timestamp: datetime             # 信号时间











    # 元数?





    metadata: Dict = None          # 附加信息











    @property





    def risk_reward_ratio(self) -> float:





        """风险收益?""





        risk = abs(self.entry_price - self.stop_loss)





        reward = abs(self.target - self.entry_price)





        return reward / risk if risk > 0 else 0











    @property





    def pattern_type(self) -> str:





        """形态类? reversal / continuation"""





        if self.pattern in ["morning_star", "evening_star",





                           "hammer", "shooting_star",





                           "bullish_engulfing", "bearish_engulfing",





                           "dark_cloud_cover", "piercing_pattern"]:





            return "reversal"





        elif self.pattern in ["three_white_soldiers", "three_black_crows",





                              "gap_up", "gap_down",





                              "rising_three_methods", "falling_three_methods"]:





            return "continuation"





        return "neutral"





```











### 7.2 批量识别接口











```python





class CandlestickRecognizer:





    """蜡烛图模式识别器"""











    def __init__(self, config: CandlestickConfig = None):





        self.config = config or CandlestickConfig()





        self.recognizers = {





            "hammer": self.recognize_hammer,





            "shooting_star": self.recognize_shooting_star,





            "doji": self.recognize_doji,





            "bullish_engulfing": self.recognize_bullish_engulfing,





            "bearish_engulfing": self.recognize_bearish_engulfing,





            "morning_star": self.recognize_morning_star,





            "evening_star": self.recognize_evening_star,





            "three_white_soldiers": self.recognize_three_white_soldiers,





            "three_black_crows": self.recognize_three_black_crows,





        }











    def recognize_all(self, df: pd.DataFrame) -> List[CandlestickSignal]:





        """





        批量识别所有蜡烛图形?











        参数:





            df: 包含 OHLCV ?DataFrame











        返回:





            识别到的所有信号列?





        """





        signals = []





        candles = self._df_to_candles(df)











        for i in range(len(candles)):





            # 单根蜡烛





            signal = self._recognize_single(candles[i])





            if signal:





                signals.append(signal)











            # 两根组合





            if i >= 1:





                signals.extend(self._recognize_two(candles[i-1], candles[i]))











            # 三根组合





            if i >= 2:





                signals.extend(self._recognize_three(candles[i-2], candles[i-1], candles[i]))











        return signals











    def get_latest_signals(self, df: pd.DataFrame,





                           n: int = 5) -> List[CandlestickSignal]:





        """获取最近N个信?""





        return self.recognize_all(df)[-n:]





```











```
```---
```











## 8. 与策略系统集成











### 8.1 接口设计











```python





# 输入接口





def recognize_candlestick(df: pd.DataFrame,





                          patterns: List[str] = None) -> List[CandlestickSignal]:





    """





    蜡烛图识别主入口





    """





    recognizer = CandlestickRecognizer()





    all_signals = recognizer.recognize_all(df)











    if patterns:





        all_signals = [s for s in all_signals if s.pattern in patterns]











    return all_signals











# 输出到信号系?





# SignalOutput = {





#     "signal_id": "CS_001",





#     "source": "candlestick",





#     "pattern": "bullish_engulfing",





#     "direction": "bullish",





#     "confidence": 0.8,





#     "entry_price": 10.5,





#     "stop_loss": 9.8,





#     "target": 11.5,





#     "risk_reward": 2.5,





#     "timestamp": "2026-03-28"





# }





```











### 8.2 在策略中使用











```python





class CandlestickStrategy:





    """基于蜡烛图模式的策略"""











    def __init__(self, min_confidence: float = 0.6):





        self.min_confidence = min_confidence





        self.recognizer = CandlestickRecognizer()











    def on_bar(self, df: pd.DataFrame) -> Optional[Signal]:





        """每根K线调用一?""





        signals = self.recognizer.get_latest_signals(df, n=1)











        for signal in signals:





            if signal.confidence >= self.min_confidence:





                if signal.direction == "bullish":





                    return self._create_long_signal(signal)





                elif signal.direction == "bearish":





                    return self._create_short_signal(signal)











        return None





```











```
```---
```











## 9. 完整识别模式清单











| 模式名称 | 方向 | 类型 | 蜡烛?| 置信度基?|





|----------|------|------|--------|------------|





| hammer | bullish | reversal | 1 | 0.7 |





| hanging_man | bearish | reversal | 1 | 0.65 |





| shooting_star | bearish | reversal | 1 | 0.7 |





| doji | neutral | reversal | 1 | 0.5 |





| bullish_engulfing | bullish | reversal | 2 | 0.75 |





| bearish_engulfing | bearish | reversal | 2 | 0.75 |





| dark_cloud_cover | bearish | reversal | 2 | 0.7 |





| piercing_pattern | bullish | reversal | 2 | 0.7 |





| morning_star | bullish | reversal | 3 | 0.8 |





| evening_star | bearish | reversal | 3 | 0.8 |





| three_white_soldiers | bullish | continuation | 3 | 0.85 |





| three_black_crows | bearish | continuation | 3 | 0.85 |





| gap_up | bullish | continuation | 2 | 0.7 |





| gap_down | bearish | continuation | 2 | 0.7 |





| rising_three_methods | bullish | continuation | 5 | 0.8 |





| falling_three_methods | bearish | continuation | 5 | 0.8 |











```
```---
```











**版本**: 1.0





**更新**: 2026-03-28





**状?*: 草稿
