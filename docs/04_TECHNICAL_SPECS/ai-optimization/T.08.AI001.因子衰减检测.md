# T.08.AI001.因子衰减检测

> 因子有效性衰减检测与预警
>
> **策略编号**：T.08.AI001
> **所属模块**：ai-optimization
> **文档类型**：AI监控
> **优先级**：P2
>
> **配套文档**：
> - [T.08.AI002.ICIR监控.md](./T.08.AI002.ICIR监控.md) - IC/IR监控
> - [self-optimization.md](./self-optimization.md) - AI自我优化框架

---

## 1. 因子衰减理论基础

```python
class FactorDecayDetector:
    """
    因子衰减检测器

    核心理论：
    - 因子有效性随时间逐渐衰减
    - 市场结构变化导致因子失效
    - 需定期检测并替换失效因子
    """

    DECAY_THRESHOLDS = {
        'IC衰减率': 0.30,
        'IR衰减率': 0.40,
        '换手率变化': 0.50,
        '波动率变化': 0.60
    }
```

---

## 2. IC衰减检测

```python
class ICDecayAnalyzer:
    """
    IC衰减分析器
    """

    def __init__(self):
        self.ic_history = []
        self.ir_history = []
        self.lookback_periods = [20, 60, 120]

    def calculate_ic_decay_rate(self, ic_series: pd.Series,
                               window: int = 60) -> dict:
        """
        计算IC衰减率

        参数:
            ic_series: IC序列
            window: 检测窗口

        返回:
            decay_analysis: 衰减分析
        """
        if len(ic_series) < window:
            return {'error': '数据不足'}

        recent_ic = ic_series.iloc[-window:].mean()
        historical_ic = ic_series.iloc[:-window].mean() if len(ic_series) > window else recent_ic

        if historical_ic == 0:
            return {'error': '历史IC为零，无法计算衰减率'}

        ic_decay_rate = (historical_ic - recent_ic) / abs(historical_ic)

        recent_std = ic_series.iloc[-window:].std()
        recent_mean = ic_series.iloc[-window:].mean()
        ir_recent = recent_mean / recent_std if recent_std > 0 else 0

        return {
            'recent_ic_mean': round(recent_ic, 4),
            'historical_ic_mean': round(historical_ic, 4),
            'ic_decay_rate': round(ic_decay_rate, 4),
            'ir_recent': round(ir_recent, 4),
            'is_decay_significant': ic_decay_rate > 0.30,
            'severity': self.get_decay_severity(ic_decay_rate)
        }

    def get_decay_severity(self, decay_rate: float) -> str:
        """
        衰减严重程度
        """
        if decay_rate > 0.50:
            return '严重衰减'
        elif decay_rate > 0.30:
            return '明显衰减'
        elif decay_rate > 0.15:
            return '轻微衰减'
        else:
            return '正常'

    def detect_ic_breakdown(self, ic_series: pd.Series,
                           threshold: float = 0.02) -> list:
        """
        检测IC失效点

        参数:
            ic_series: IC序列
            threshold: IC低于此值视为失效

        返回:
            breakdowns: 失效点列表
        """
        breakdowns = []

        rolling_ic = ic_series.rolling(5).mean()

        for i in range(20, len(rolling_ic)):
            if rolling_ic.iloc[i] < threshold:
                if i == 0 or rolling_ic.iloc[i-1] >= threshold:
                    breakdowns.append({
                        'index': i,
                        'date': ic_series.index[i] if hasattr(ic_series, 'index') else i,
                        'ic_value': round(ic_series.iloc[i], 4),
                        'rolling_ic_5': round(rolling_ic.iloc[i], 4)
                    })

        return breakdowns
```

---

## 3. 因子稳定性检测

```python
class FactorStabilityDetector:
    """
    因子稳定性检测器
    """

    def __init__(self):
        self.turnover_threshold = 0.50
        self.volatility_threshold = 0.60

    def calculate_turnover_rate(self, factor_quantiles: pd.DataFrame,
                               window: int = 20) -> pd.Series:
        """
        计算因子换手率

        参数:
            factor_quantiles: 因子分位数（每期排名）
            window: 计算窗口

        返回:
            turnover: 换手率序列
        """
        turnover = []

        for i in range(window, len(factor_quantiles)):
            prev_quantile = factor_quantiles.iloc[i-window]
            curr_quantile = factor_quantiles.iloc[i]

            turnover_rate = (prev_quantile != curr_quantile).mean()
            turnover.append(turnover_rate)

        return pd.Series(turnover, index=factor_quantiles.index[window:])

    def detect_turnover_spike(self, turnover: pd.Series,
                            threshold: float = 0.50) -> list:
        """
        检测换手率突变

        参数:
            turnover: 换手率序列
            threshold: 突变阈值

        返回:
            spikes: 突变点
        """
        turnover_ma = turnover.rolling(20).mean()
        turnover_std = turnover.rolling(20).std()

        spikes = []

        for i in range(20, len(turnover)):
            z_score = (turnover.iloc[i] - turnover_ma.iloc[i]) / turnover_std.iloc[i]

            if z_score > 2.5:
                spikes.append({
                    'index': i,
                    'turnover': round(turnover.iloc[i], 4),
                    'z_score': round(z_score, 2),
                    'severity': '严重' if z_score > 4 else '中等'
                })

        return spikes

    def calculate_factor_half_life(self, ic_series: pd.Series) -> dict:
        """
        计算因子半衰期

        参数:
            ic_series: IC序列

        返回:
            half_life: 半衰期估计
        """
        ic_values = ic_series.values
        initial_ic = ic_values[0]

        cumulative_decay = np.cumsum(np.abs(np.diff(ic_values)))

        total_decay = np.sum(np.abs(np.diff(ic_values)))

        half_decay_idx = np.argmax(cumulative_decay >= total_decay / 2)

        half_life_days = half_decay_idx + 1

        return {
            'half_life_days': half_life_days,
            'initial_ic': round(initial_ic, 4),
            'current_ic': round(ic_values[-1], 4),
            'total_decay': round(total_decay, 4),
            'decay_rate_per_day': round(total_decay / len(ic_values), 6)
        }
```

---

## 4. 多因子衰减分析

```python
class MultiFactorDecayAnalyzer:
    """
    多因子衰减分析器
    """

    def __init__(self):
        self.factor_ic_data = {}

    def analyze_all_factors(self, factor_returns: pd.DataFrame,
                          market_returns: pd.Series) -> dict:
        """
        分析所有因子衰减情况

        参数:
            factor_returns: 因子收益率矩阵
            market_returns: 市场收益率

        返回:
            analysis_results: 各因子分析结果
        """
        results = {}

        for factor_name in factor_returns.columns:
            ic_series = self.calculate_ic(
                factor_returns[factor_name],
                market_returns
            )

            ic_decay = ICDecayAnalyzer().calculate_ic_decay_rate(ic_series)

            turnover = self.calculate_factor_quantile_turnover(
                factor_returns[factor_name]
            )

            half_life = ICDecayAnalyzer().calculate_ic_decay_rate(ic_series)

            results[factor_name] = {
                'ic_decay_analysis': ic_decay,
                'avg_turnover': round(turnover.mean(), 4),
                'turnover_spikes': len(ICDecayAnalyzer().detect_turnover_spike(turnover)),
                'half_life_days': half_life.get('half_life_days', 'N/A'),
                'recommendation': self.get_factor_recommendation(ic_decay, turnover)
            }

        return results

    def calculate_ic(self, factor_returns: pd.Series,
                    market_returns: pd.Series) -> pd.Series:
        """
        计算IC序列
        """
        return factor_returns.rolling(20).corr(market_returns)

    def calculate_factor_quantile_turnover(self, factor_values: pd.Series) -> pd.Series:
        """
        计算因子分位数换手率
        """
        quantiles = factor_values.rank(pct=True)
        quantile_change = quantiles.diff().abs()
        return quantile_change.rolling(20).mean()

    def get_factor_recommendation(self, ic_decay: dict,
                                 turnover: pd.Series) -> str:
        """
        获取因子处置建议
        """
        if isinstance(ic_decay, dict) and ic_decay.get('is_decay_significant'):
            return '建议替换'

        if turnover.mean() > 0.6:
            return '高换手，谨慎使用'

        return '继续观察'
```

---

## 5. 衰减预警系统

```python
class FactorDecayWarningSystem:
    """
    因子衰减预警系统
    """

    def __init__(self):
        self.ic_decay_analyzer = ICDecayAnalyzer()
        self.stability_detector = FactorStabilityDetector()
        self.warning_levels = {
            'green': {'ic_decay': 0.15, 'turnover': 0.40},
            'yellow': {'ic_decay': 0.30, 'turnover': 0.55},
            'orange': {'ic_decay': 0.45, 'turnover': 0.70},
            'red': {'ic_decay': 0.60, 'turnover': 0.85}
        }

    def generate_warning_report(self, factor_name: str,
                              ic_series: pd.Series,
                              turnover: pd.Series) -> dict:
        """
        生成预警报告

        参数:
            factor_name: 因子名称
            ic_series: IC序列
            turnover: 换手率序列

        返回:
            warning_report: 预警报告
        """
        ic_decay = self.ic_decay_analyzer.calculate_ic_decay_rate(ic_series)

        avg_turnover = turnover.iloc[-20:].mean()

        warning_level = self.determine_warning_level(
            ic_decay.get('ic_decay_rate', 0),
            avg_turnover
        )

        warnings = self.generate_warnings(warning_level, ic_decay, avg_turnover)

        recommended_actions = self.get_recommended_actions(warning_level, factor_name)

        return {
            'factor_name': factor_name,
            'warning_level': warning_level,
            'ic_decay_rate': ic_decay.get('ic_decay_rate', 0),
            'avg_turnover': round(avg_turnover, 4),
            'warnings': warnings,
            'recommended_actions': recommended_actions,
            'timestamp': pd.Timestamp.now()
        }

    def determine_warning_level(self, ic_decay_rate: float,
                               avg_turnover: float) -> str:
        """
        确定预警级别
        """
        levels = self.warning_levels

        if ic_decay_rate >= levels['red']['ic_decay'] or avg_turnover >= levels['red']['turnover']:
            return 'red'
        elif ic_decay_rate >= levels['orange']['ic_decay'] or avg_turnover >= levels['orange']['turnover']:
            return 'orange'
        elif ic_decay_rate >= levels['yellow']['ic_decay'] or avg_turnover >= levels['yellow']['turnover']:
            return 'yellow'
        else:
            return 'green'

    def generate_warnings(self, level: str,
                         ic_decay: dict,
                         avg_turnover: float) -> list:
        """
        生成预警信息
        """
        warnings = []

        if level in ['orange', 'red']:
            warnings.append(f"IC衰减率{ic_decay.get('ic_decay_rate', 0)*100:.1f}%，超过阈值")

        if level in ['yellow', 'orange', 'red']:
            warnings.append(f"因子换手率{avg_turnover*100:.1f}%偏高")

        if ic_decay.get('is_decay_significant'):
            warnings.append("因子有效性显著下降")

        if ic_decay.get('severity') == '严重衰减':
            warnings.append("因子严重衰减，建议立即替换")

        return warnings

    def get_recommended_actions(self, level: str, factor_name: str) -> list:
        """
        获取推荐操作
        """
        actions = {
            'green': ['继续监控', '定期检查IC'],
            'yellow': ['降低该因子权重', '寻找替代因子'],
            'orange': ['暂停使用该因子', '启动因子替换流程'],
            'red': ['立即下架该因子', '启动AI因子挖掘', '人工审核']
        }
        return actions.get(level, actions['green'])
```

---

## 6. 使用示例

```python
def example_factor_decay_detection():
    """
    因子衰减检测示例
    """
    detector = FactorDecayDetector()
    warning_system = FactorDecayWarningSystem()

    factor_returns = pd.read_csv('factor_returns.csv', index_col=0)
    market_returns = pd.read_csv('market_returns.csv', index_col=0)['return']

    ic_series = detector.calculate_ic_series(factor_returns['SIZE'], market_returns)

    ic_decay = detector.calculate_ic_decay_rate(ic_series)

    print(f"因子: SIZE")
    print(f"IC衰减率: {ic_decay['ic_decay_rate']*100:.1f}%")
    print(f"严重程度: {ic_decay['severity']}")
    print(f"是否显著衰减: {ic_decay['is_decay_significant']}")

    turnover = detector.calculate_turnover_rate(factor_returns[['SIZE']])
    turnover_spikes = detector.detect_turnover_spike(turnover)
    print(f"换手率突变次数: {len(turnover_spikes)}")

    half_life = detector.calculate_factor_half_life(ic_series)
    print(f"因子半衰期: {half_life['half_life_days']}天")

    warning_report = warning_system.generate_warning_report(
        'SIZE', ic_series, turnover
    )
    print(f"\n预警级别: {warning_report['warning_level']}")
    print(f"建议操作: {warning_report['recommended_actions']}")
```

---

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 新建因子衰减检测文档 |
