# T.00.MR004.宏观策略量化

> 宏观经济周期与跨资产配置策略量化
>
> **策略编号**：T.00.MR004
> **所属模块**：01_MARKET_REGIME
> **文档类型**：市场状态
> **优先级**：P2
>
> **配套文档**：
> - [T.00.MR001.市场趋势识别.md](./T.00.MR001.市场趋势识别.md) - 五维市场状态
> - [T.00.MR002.量能周期体系.md](./T.00.MR002.量能周期体系.md) - 量能周期
> - [T.00.MR003.市场结构博弈.md](./T.00.MR003.市场结构博弈.md) - 市场结构博弈

---

## 1. 宏观策略理论基础

```python
class MacroStrategyAnalyzer:
    """
    宏观策略分析器

    核心理论：
    - 美林投资时钟：经济周期决定资产配置
    - 货币政策周期：流动性影响市场
    - 外部冲击：地缘政治、疫情等
    - 汇率传导：人民币汇率影响外资流向
    """

    def __init__(self):
        self.economic_indicators = {}
        self.policy_indicators = {}
        self.external_shocks = []
```

---

## 2. 美林时钟周期量化

### 2.1 经济周期四阶段

```python
class EconomicCycleClassifier:
    """
    经济周期分类器
    基于美林时钟理论
    """

    CYCLE_STAGES = ['复苏期', '过热期', '滞胀期', '衰退期']

    def classify_economic_cycle(self, gdp_data: pd.Series,
                               cpi_data: pd.Series,
                               pmi_data: pd.Series = None) -> dict:
        """
        分类经济周期阶段

        参数:
            gdp_data: GDP同比增速
            cpi_data: CPI同比增速
            pmi_data: PMI数据（可选）

        返回:
            cycle_stage: 周期阶段
        """
        gdp_trend = self.calc_trend(gdp_data)
        cpi_trend = self.calc_trend(cpi_data)

        if gdp_trend > 0 and cpi_trend < 0.03:
            stage = '复苏期'
            asset_preference = ['股票', '商品', '现金']
        elif gdp_trend > 0 and cpi_trend > 0.03:
            stage = '过热期'
            asset_preference = ['商品', '股票', '现金']
        elif gdp_trend < 0 and cpi_trend > 0.03:
            stage = '滞胀期'
            asset_preference = ['现金', '商品', '债券']
        else:
            stage = '衰退期'
            asset_preference = ['债券', '现金', '股票']

        return {
            'stage': stage,
            'gdp_trend': gdp_trend,
            'cpi_trend': cpi_trend,
            'asset_preference': asset_preference,
            'recommended_position': self.get_stage_position(stage)
        }

    def calc_trend(self, data: pd.Series) -> float:
        """
        计算趋势（一阶导数）
        """
        if len(data) < 2:
            return 0
        return (data.iloc[-1] - data.iloc[-4]) / abs(data.iloc[-4]) if len(data) >= 4 else 0

    def get_stage_position(self, stage: str) -> dict:
        """
        各周期阶段推荐仓位
        """
        positions = {
            '复苏期': {
                'stock': 0.60,
                'bond': 0.20,
                'commodity': 0.10,
                'cash': 0.10
            },
            '过热期': {
                'stock': 0.40,
                'bond': 0.10,
                'commodity': 0.40,
                'cash': 0.10
            },
            '滞胀期': {
                'stock': 0.20,
                'bond': 0.30,
                'commodity': 0.20,
                'cash': 0.30
            },
            '衰退期': {
                'stock': 0.20,
                'bond': 0.50,
                'commodity': 0.10,
                'cash': 0.20
            }
        }
        return positions.get(stage, positions['衰退期'])
```

---

## 3. 货币政策周期量化

```python
class MonetaryPolicyAnalyzer:
    """
    货币政策周期分析器
    """

    def __init__(self):
        self.policy_rate_history = []
        self.mlfs_history = []

    def analyze_policy_cycle(self, interest_rate_data: pd.Series,
                           rrr_data: pd.Series,
                           mlf_data: pd.Series = None) -> dict:
        """
        分析货币政策周期

        参数:
            interest_rate_data: 政策利率（MLF/LPR）
            rrr_data: 存款准备金率
            mlf_data: 中期借贷便利（可选）

        返回:
            policy_cycle: 政策周期状态
        """
        rate_trend = self.calc_rate_trend(interest_rate_data)
        rrr_trend = self.calc_rrr_trend(rrr_data)

        if rate_trend < 0 and rrr_trend < 0:
            cycle = '宽松周期'
            market_impact = '积极'
            equity_impact = '利好'
        elif rate_trend > 0 and rrr_trend > 0:
            cycle = '紧缩周期'
            market_impact = '消极'
            equity_impact = '利空'
        elif rate_trend == 0 and rrr_trend == 0:
            cycle = '中性周期'
            market_impact = '观望'
            equity_impact = '中性'
        else:
            cycle = '试探周期'
            market_impact = '不确定'
            equity_impact = '观察'

        return {
            'cycle': cycle,
            'rate_trend': rate_trend,
            'rrr_trend': rrr_trend,
            'market_impact': market_impact,
            'equity_impact': equity_impact,
            'policy_direction': self.get_policy_direction(rate_trend, rrr_trend)
        }

    def calc_rate_trend(self, data: pd.Series) -> float:
        """
        计算利率趋势
        """
        if len(data) < 3:
            return 0
        recent = data.iloc[-1]
        prev = data.iloc[-3]
        return recent - prev

    def calc_rrr_trend(self, data: pd.Series) -> float:
        """
        计算准备金率趋势
        """
        if len(data) < 2:
            return 0
        return data.iloc[-1] - data.iloc[-2]

    def get_policy_direction(self, rate_trend: float, rrr_trend: float) -> str:
        """
        获取政策方向
        """
        if rate_trend < 0 or rrr_trend < 0:
            return '宽松'
        elif rate_trend > 0 or rrr_trend > 0:
            return '紧缩'
        else:
            return '中性'

    def predict_rate_change(self, policy_data: pd.DataFrame) -> dict:
        """
        预测利率变动

        参数:
            policy_data: 历史政策数据

        返回:
            prediction: 预测结果
        """
        current_rate = policy_data['rate'].iloc[-1]
        current_rrr = policy_data['rrr'].iloc[-1]

        inflation = policy_data.get('cpi', pd.Series([2.0])).iloc[-1]
        gdp_growth = policy_data.get('gdp', pd.Series([5.0])).iloc[-1]

        if inflation < 1.5 and gdp_growth < 4:
            recommended_rate_change = -0.10
            recommended_rrr_change = -0.05
            confidence = '高'
        elif inflation > 5 or gdp_growth > 7:
            recommended_rate_change = 0.10
            recommended_rrr_change = 0.05
            confidence = '高'
        else:
            recommended_rate_change = 0
            recommended_rrr_change = 0
            confidence = '中'

        return {
            'predicted_rate_change': recommended_rate_change,
            'predicted_rrr_change': recommended_rrr_change,
            'confidence': confidence,
            'current_conditions': {
                'inflation': inflation,
                'gdp_growth': gdp_growth
            }
        }
```

---

## 4. 汇率传导机制

```python
class ExchangeRateTransmitter:
    """
    汇率传导分析器
    """

    def __init__(self):
        self.usd_cny_threshold = 7.0
        self.risk_threshold = 0.15

    def analyze_rmb_impact(self, usd_cny: float,
                          sp500_change: float,
                          bond_yield_diff: float) -> dict:
        """
        分析人民币汇率对市场的影响

        参数:
            usd_cny: 美元兑人民币汇率
            sp500_change: 标普500涨跌幅
            bond_yield_diff: 中美利差

        返回:
            impact_analysis: 影响分析
        """
        depreciation_pressure = self.calc_depreciation_pressure(usd_cny)

        if usd_cny > 7.2:
            fx_signal = '大幅贬值'
            capital_impact = '资金外流压力'
        elif usd_cny > 7.0:
            fx_signal = '温和贬值'
            capital_impact = '关注资金流向'
        elif usd_cny > 6.8:
            fx_signal = '基本稳定'
            capital_impact = '双向流动'
        else:
            fx_signal = '升值'
            capital_impact = '资金流入'

        equity_impact = self.calc_equity_impact(depreciation_pressure, sp500_change)

        return {
            'usd_cny': usd_cny,
            'fx_signal': fx_signal,
            'depreciation_pressure': depreciation_pressure,
            'capital_flow': capital_impact,
            'equity_impact': equity_impact,
            'north_money_flow': self.predict_north_flow(usd_cny, bond_yield_diff)
        }

    def calc_depreciation_pressure(self, usd_cny: float) -> str:
        """
        计算贬值压力
        """
        if usd_cny > 7.5:
            return '极大'
        elif usd_cny > 7.2:
            return '较大'
        elif usd_cny > 7.0:
            return '中等'
        else:
            return '较小'

    def calc_equity_impact(self, depreciation_pressure: str,
                          sp500_change: float) -> str:
        """
        计算对股市影响
        """
        if depreciation_pressure in ['极大', '较大']:
            if sp500_change < -2:
                return '双重利空'
            else:
                return '汇率利空'
        elif depreciation_pressure == '中等':
            return '边际影响'
        else:
            if sp500_change > 1:
                return '外部利好'
            else:
                return '中性'

    def predict_north_flow(self, usd_cny: float,
                         bond_yield_diff: float) -> dict:
        """
        预测北向资金流向
        """
        if bond_yield_diff > 0.02 and usd_cny < 7.0:
            predicted_flow = '大幅流入'
            confidence = '高'
        elif bond_yield_diff > 0 and usd_cny < 7.2:
            predicted_flow = '温和流入'
            confidence = '中'
        elif bond_yield_diff < -0.02 or usd_cny > 7.5:
            predicted_flow = '大幅流出'
            confidence = '高'
        else:
            predicted_flow = '观望'
            confidence = '低'

        return {
            'predicted_flow': predicted_flow,
            'confidence': confidence,
            'bond_yield_diff': bond_yield_diff
        }
```

---

## 5. 外部冲击评估

```python
class ExternalShockEvaluator:
    """
    外部冲击评估器
    """

    SHOCK_TYPES = ['地缘政治', '疫情', '金融危机', '自然灾害', '贸易摩擦']

    def __init__(self):
        self.shock_history = []
        self.risk_off_indicators = ['VIX', '黄金', '美元']

    def evaluate_shock_impact(self, shock_type: str,
                             shock_intensity: float,
                             market_data: pd.DataFrame) -> dict:
        """
        评估外部冲击影响

        参数:
            shock_type: 冲击类型
            shock_intensity: 冲击强度 (0-10)
            market_data: 市场数据

        返回:
            impact_assessment: 冲击评估
        """
        if shock_intensity >= 8:
            severity = '严重'
            market_reaction = '大幅下跌'
            recommended_action = '减仓/清仓'
        elif shock_intensity >= 5:
            severity = '中等'
            market_reaction = '震荡下跌'
            recommended_action = '降低仓位'
        elif shock_intensity >= 3:
            severity = '轻度'
            market_reaction = '短暂调整'
            recommended_action = '观望'
        else:
            severity = '可忽略'
            market_reaction = '影响有限'
            recommended_action = '持仓'

        affected_sectors = self.get_affected_sectors(shock_type)
        safe_havens = self.get_safe_havens(shock_type)

        historical_shocks = self.get_historical_similar_shocks(shock_type)

        return {
            'shock_type': shock_type,
            'shock_intensity': shock_intensity,
            'severity': severity,
            'market_reaction': market_reaction,
            'recommended_action': recommended_action,
            'affected_sectors': affected_sectors,
            'safe_havens': safe_havens,
            'historical_similar': historical_shocks,
            'recovery_probability': self.calc_recovery_prob(shock_type, shock_intensity)
        }

    def get_affected_sectors(self, shock_type: str) -> list:
        """
        获取受冲击行业
        """
        sector_map = {
            '地缘政治': ['航空', '旅游', '石油', '半导体'],
            '疫情': ['航空', '旅游', '影院', '消费'],
            '金融危机': ['银行', '地产', '消费', '金融'],
            '贸易摩擦': ['出口', '科技', '农业', '港口'],
            '自然灾害': ['保险', '农业', '基建']
        }
        return sector_map.get(shock_type, [])

    def get_safe_havens(self, shock_type: str) -> list:
        """
        获取避险资产
        """
        return ['黄金', '美元', '国债', '日元']

    def get_historical_similar_shocks(self, shock_type: str) -> list:
        """
        获取历史类似冲击
        """
        historical = {
            '地缘政治': [
                {'name': '俄乌冲突2022', 'duration': 365, 'market_impact': -15},
                {'name': '中东局势', 'duration': 60, 'market_impact': -8}
            ],
            '疫情': [
                {'name': '新冠疫情2020', 'duration': 90, 'market_impact': -30},
            ],
            '金融危机': [
                {'name': '2008次贷危机', 'duration': 500, 'market_impact': -50},
                {'name': '2015股灾', 'duration': 60, 'market_impact': -40}
            ]
        }
        return historical.get(shock_type, [])

    def calc_recovery_prob(self, shock_type: str, intensity: float) -> dict:
        """
        计算恢复概率
        """
        base_recovery_time = {
            '地缘政治': 180,
            '疫情': 120,
            '金融危机': 365,
            '自然灾害': 60,
            '贸易摩擦': 90
        }

        base = base_recovery_time.get(shock_type, 90)
        adjusted_time = base * (1 + intensity / 10)

        return {
            'estimated_recovery_days': int(adjusted_time),
            'full_recovery_probability': max(0, 1 - intensity / 20),
            'permanent_loss_probability': max(0, intensity / 50)
        }
```

---

## 6. 宏观策略综合配置

```python
class MacroAssetAllocator:
    """
    宏观资产配置器
    """

    def __init__(self):
        self.cycle_classifier = EconomicCycleClassifier()
        self.policy_analyzer = MonetaryPolicyAnalyzer()
        self.fx_transmitter = ExchangeRateTransmitter()
        self.shock_evaluator = ExternalShockEvaluator()

    def generate_macro_allocation(self, macro_data: pd.DataFrame) -> dict:
        """
        生成宏观资产配置

        参数:
            macro_data: 宏观数据，包含：
                - gdp: GDP增速
                - cpi: CPI增速
                - rate: 政策利率
                - rrr: 存款准备金率
                - usd_cny: 汇率
                - sp500: 标普500涨跌

        返回:
            allocation: 配置建议
        """
        gdp = macro_data['gdp']
        cpi = macro_data['cpi']
        rate = macro_data['rate']
        rrr = macro_data['rrr']
        usd_cny = macro_data.get('usd_cny', 6.5)
        sp500 = macro_data.get('sp500_change', 0)

        economic_cycle = self.cycle_classifier.classify_economic_cycle(gdp, cpi)

        policy_cycle = self.policy_analyzer.analyze_policy_cycle(rate, rrr)

        fx_impact = self.fx_transmitter.analyze_rmb_impact(
            usd_cny, sp500,
            macro_data.get('bond_yield_diff', 0)
        )

        stock_weight = economic_cycle['recommended_position']['stock']
        if policy_cycle['equity_impact'] == '利空':
            stock_weight *= 0.8
        elif policy_cycle['equity_impact'] == '利好':
            stock_weight *= 1.1

        if fx_impact['equity_impact'] == '双重利空':
            stock_weight *= 0.7

        stock_weight = max(0.1, min(0.9, stock_weight))

        bond_weight = economic_cycle['recommended_position']['bond']
        if policy_cycle['cycle'] == '宽松周期':
            bond_weight *= 1.2

        commodity_weight = economic_cycle['recommended_position']['commodity']
        cash_weight = 1 - stock_weight - bond_weight - commodity_weight

        return {
            'economic_cycle': economic_cycle,
            'policy_cycle': policy_cycle,
            'fx_impact': fx_impact,
            'allocation': {
                'stock': round(stock_weight, 2),
                'bond': round(bond_weight, 2),
                'commodity': round(commodity_weight, 2),
                'cash': round(max(0, cash_weight), 2)
            },
            'sector_recommendation': self.get_sector_recommendation(
                economic_cycle, policy_cycle
            ),
            'risk_warning': self.check_risk_warning(macro_data)
        }

    def get_sector_recommendation(self, economic_cycle: dict,
                                 policy_cycle: dict) -> dict:
        """
        行业配置建议
        """
        stage = economic_cycle['stage']

        sector_map = {
            '复苏期': {
                '超配': ['金融', '可选消费', '信息技术'],
                '标配': ['周期', '工业'],
                '低配': ['公用事业', '能源']
            },
            '过热期': {
                '超配': ['能源', '原材料', '信息技术'],
                '标配': ['可选消费', '工业'],
                '低配': ['金融', '公用事业']
            },
            '滞胀期': {
                '超配': ['能源', '医疗', '现金'],
                '标配': ['公用事业', '必需消费'],
                '低配': ['金融', '信息技术', '可选消费']
            },
            '衰退期': {
                '超配': ['债券', '医疗', '公用事业'],
                '标配': ['必需消费'],
                '低配': ['可选消费', '金融', '信息技术']
            }
        }

        policy_bias = {
            '宽松周期': '金融 + 地产',
            '紧缩周期': '防御 + 消费',
            '中性周期': '均衡配置'
        }

        return {
            'by_cycle': sector_map.get(stage, sector_map['衰退期']),
            'by_policy': policy_bias.get(policy_cycle['cycle'], '均衡配置')
        }

    def check_risk_warning(self, macro_data: pd.DataFrame) -> list:
        """
        检查风险预警
        """
        warnings = []

        if 'cpi' in macro_data.columns:
            cpi = macro_data['cpi'].iloc[-1]
            if cpi > 5:
                warnings.append('通胀风险：CPI高于5%')
            elif cpi < 0:
                warnings.append('通缩风险：CPI负增长')

        if 'gdp' in macro_data.columns:
            gdp = macro_data['gdp'].iloc[-1]
            if gdp < 3:
                warnings.append('经济衰退风险：GDP增速低于3%')

        if 'usd_cny' in macro_data.columns:
            usd_cny = macro_data['usd_cny'].iloc[-1]
            if usd_cny > 7.5:
                warnings.append('汇率风险：人民币大幅贬值')

        return warnings
```

---

## 7. 宏观因子监测

```python
class MacroFactorMonitor:
    """
    宏观因子监测器
    """

    def __init__(self):
        self.factor_weights = {
            '经济增长': 0.30,
            '通胀': 0.20,
            '货币政策': 0.20,
            '信用环境': 0.15,
            '外部环境': 0.15
        }

    def calc_macro_score(self, factor_values: dict) -> dict:
        """
        计算宏观综合得分

        参数:
            factor_values: 各因子值

        返回:
            macro_score: 宏观得分
        """
        scores = {}

        scores['经济增长'] = self.score_growth(factor_values.get('gdp', 5))
        scores['通胀'] = self.score_inflation(factor_values.get('cpi', 2))
        scores['货币政策'] = self.score_monetary(factor_values.get('rate_change', 0))
        scores['信用环境'] = self.score_credit(factor_values.get('社融增速', 10))
        scores['外部环境'] = self.score_external(factor_values.get('usd_cny', 6.5))

        total_score = sum(scores[k] * self.factor_weights[k] for k in scores)

        return {
            'total_score': round(total_score, 2),
            'factor_scores': {k: round(v, 2) for k, v in scores.items()},
            'signal': self.score_to_signal(total_score)
        }

    def score_growth(self, gdp: float) -> float:
        """
        经济增长评分
        """
        if gdp >= 6:
            return 80 + min(gdp - 6, 2) * 10
        elif gdp >= 4:
            return 50 + (gdp - 4) / 2 * 30
        else:
            return max(0, gdp / 4 * 50)

    def score_inflation(self, cpi: float) -> float:
        """
        通胀评分（合理通胀为中性）
        """
        if cpi < 0:
            return 30 + cpi * 5
        elif cpi < 2:
            return 50 + cpi * 15
        elif cpi < 4:
            return 80 - (cpi - 2) * 10
        elif cpi < 6:
            return 60 - (cpi - 4) * 15
        else:
            return max(0, 30 - (cpi - 6) * 10)

    def score_monetary(self, rate_change: float) -> float:
        """
        货币政策评分
        """
        if rate_change < 0:
            return 70 + abs(rate_change) * 100
        elif rate_change > 0:
            return 70 - rate_change * 100
        else:
            return 60

    def score_credit(self, credit_growth: float) -> float:
        """
        信用环境评分
        """
        if credit_growth >= 12:
            return 75
        elif credit_growth >= 8:
            return 60 + (credit_growth - 8) * 3.75
        elif credit_growth >= 5:
            return 45 + (credit_growth - 5) * 5
        else:
            return max(0, 30 + credit_growth * 3)

    def score_external(self, usd_cny: float) -> float:
        """
        外部环境评分
        """
        if usd_cny <= 6.5:
            return 80
        elif usd_cny <= 7.0:
            return 70 - (usd_cny - 6.5) / 0.5 * 10
        elif usd_cny <= 7.5:
            return 60 - (usd_cny - 7.0) / 0.5 * 20
        else:
            return max(0, 40 - (usd_cny - 7.5) * 20)

    def score_to_signal(self, score: float) -> str:
        """
        得分转信号
        """
        if score >= 70:
            return '积极做多'
        elif score >= 55:
            return '谨慎看多'
        elif score >= 45:
            return '中性观望'
        elif score >= 30:
            return '谨慎看空'
        else:
            return '规避风险'
```

---

## 8. 使用示例

```python
def example_macro_strategy():
    """
    宏观策略示例
    """
    allocator = MacroAssetAllocator()
    monitor = MacroFactorMonitor()

    macro_data = pd.DataFrame({
        'gdp': [5.5, 5.3, 5.2, 5.1],
        'cpi': [2.1, 2.0, 1.8, 1.9],
        'rate': [2.5, 2.5, 2.5, 2.5],
        'rrr': [10.5, 10.5, 10.5, 10.5],
        'usd_cny': [6.8, 6.9, 7.0, 6.95],
        'sp500_change': [0.5, -0.3, 1.2, 0.8],
        'bond_yield_diff': [0.01, 0.015, 0.02, 0.018]
    })

    allocation = allocator.generate_macro_allocation(macro_data)

    print(f"经济周期: {allocation['economic_cycle']['stage']}")
    print(f"政策周期: {allocation['policy_cycle']['cycle']}")
    print(f"汇率影响: {allocation['fx_impact']['fx_signal']}")

    print("\n配置建议:")
    print(f"  股票: {allocation['allocation']['stock']*100:.0f}%")
    print(f"  债券: {allocation['allocation']['bond']*100:.0f}%")
    print(f"  商品: {allocation['allocation']['commodity']*100:.0f}%")
    print(f"  现金: {allocation['allocation']['cash']*100:.0f}%")

    print("\n行业建议:")
    print(f"  超配: {allocation['sector_recommendation']['by_cycle']['超配']}")

    factor_values = {
        'gdp': macro_data['gdp'].iloc[-1],
        'cpi': macro_data['cpi'].iloc[-1],
        'rate_change': 0,
        'usd_cny': macro_data['usd_cny'].iloc[-1]
    }

    score = monitor.calc_macro_score(factor_values)
    print(f"\n宏观得分: {score['total_score']:.1f}")
    print(f"信号: {score['signal']}")
```

---

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 新建宏观策略量化文档 |
