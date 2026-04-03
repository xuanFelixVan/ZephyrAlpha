---
module_id: STANDARDS_CALC_FRAMEWORK_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构�?
standard_type: 专业量化机构因子标准
applicable_scope: 因子研究与管�?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行�?
---

# 因子计算框架

> **版本**: v1.0
> **创建日期**: 2026-03-30
> **Layer**: Layer 2 (因子计算�?
> **专业机构标准**: 完整因子生命周期管理

---

## 1. 框架概述

```
┌─────────────────────────────────────────────────────────────────────�?
�?             专业机构因子计算框架                                       �?
├─────────────────────────────────────────────────────────────────────�?
�?                                                                    �?
�? ┌─────────────────────────────────────────────────────────────�?  �?
�? �?                   Factor Registry (因子注册�?               �?  �?
�? �? ├── 因子ID/名称/分类                                      �?  �?
�? �? ├── 计算公式/依赖关系                                     �?  �?
�? �? ├── 更新频率/数据�?                                      �?  �?
�? �? └── 负责�?状�?                                          �?  �?
�? └─────────────────────────────────────────────────────────────�?  �?
�?                             �?                                     �?
�? ┌─────────────────────────────────────────────────────────────�?  �?
�? �?                   Factor Scheduler (调度�?                  �?  �?
�? �? ├── 依赖拓扑排序                                          �?  �?
�? �? ├── 并行计算优化                                          �?  �?
�? �? └── 失败重试/报警                                         �?  �?
�? └─────────────────────────────────────────────────────────────�?  �?
�?                             �?                                     �?
�? ┌─────────────────────────────────────────────────────────────�?  �?
�? �?                   Factor Engine (计算引擎)                  �?  �?
�? �? ├── 日频计算 (盘后批量)                                   �?  �?
�? �? ├── 分钟计算 (盘中增量)                                   �?  �?
�? �? └── 因子验证 (IC/IR)                                     �?  �?
�? └─────────────────────────────────────────────────────────────�?  �?
�?                             �?                                     �?
�? ┌─────────────────────────────────────────────────────────────�?  �?
�? �?                   Factor Storage (存储)                     �?  �?
�? �? ├── ClickHouse (历史)                                     �?  �?
�? �? └── Redis (实时)                                          �?  �?
�? └─────────────────────────────────────────────────────────────�?  �?
�?                                                                    �?
└─────────────────────────────────────────────────────────────────────�?
```

---

## 2. 核心组件

> **注意**: 因子定义和分类请参考以下文档：
> - **因子分类�?*: [FACTOR_TAXONOMY.md](FACTOR_TAXONOMY.md) - 因子分类体系和参数配�?
> - **因子注册�?*: [../06_REGISTRY/FACTOR_CATALOG.md](../06_REGISTRY/FACTOR_CATALOG.md) - 因子清单和元数据

### 2.1 因子依赖管理

因子计算采用分层依赖架构，确保计算顺序正确性和并行优化�?

### 3.1 分层架构

```
┌─────────────────────────────────────────────────────────────────────�?
�?                   因子依赖拓扑�?                                     �?
├─────────────────────────────────────────────────────────────────────�?
�?                                                                    �?
�?   原始数据 (Layer 0)                                              �?
�?   ├── close_price (收盘�?                                   �?
�?   ├── volume (成交�?                                          �?
�?   ├── float_share (流通股�?                                   �?
�?   └── financial_data (财务数据)                               �?
�?                                                                    �?
�?        �?                                                         �?
�?   Layer 1: 基础因子 (可直接计�?                                 �?
�?   ├── price_return (收益�? �?close_price                       �?
�?   ├── log_volume (对数成交�? �?volume                         �?
�?   ├── market_cap (市�? �?close_price * share_count           �?
�?   └── turnover_rate (换手�? �?volume / float_share          �?
�?                                                                    �?
�?        �?                                                         �?
�?   Layer 2: 技术因�?(依赖Layer 1)                                �?
�?   ├── ma_5 (5日均�? �?price_return                           �?
�?   ├── ma_20 (20日均�? �?price_return                         �?
�?   ├── volatility_20 (波动�? �?price_return                   �?
�?   └── rsi_14 (RSI) �?price_return                             �?
�?                                                                    �?
�?        �?                                                         �?
�?   Layer 3: 复合因子 (依赖Layer 2)                               �?
�?   ├── momentum_score �?ma_5, ma_20, volatility_20            �?
�?   ├── value_score �?pe, pb, pc                              �?
�?   └── combined_score �?momentum_score + value_score           �?
�?                                                                    �?
└─────────────────────────────────────────────────────────────────────�?
```

### 3.2 DAG构建代码

```python
import networkx as nx

class FactorDependencyGraph:
    """因子依赖�?""

    def __init__(self, registry):
        self.registry = registry
        self.graph = nx.DiGraph()

    def build(self):
        """构建因子依赖DAG"""
        for factor in self.registry.get_all_factors():
            self.graph.add_node(factor.factor_id)

            for dep in factor.dependencies:
                self.graph.add_node(dep)
                self.graph.add_edge(dep, factor.factor_id)

        return self.graph

    def get_layers(self) -> List[List[str]]:
        """获取分层执行顺序

        同一层内因子可并行计�?
        """
        return list(nx.topological_generations(self.graph))

    def get_dependencies(self, factor_id: str) -> List[str]:
        """获取因子的所有依�?""
        return list(nx.ancestors(self.graph, factor_id))

    def validate_no_cycle(self) -> bool:
        """验证无循环依�?""
        return nx.is_directed_acyclic_graph(self.graph)
```

---

## 4. 因子调度�?(Factor Scheduler)

### 4.1 调度器代�?

```python
class FactorScheduler:
    """因子调度�?- 专业机构标准"""

    def __init__(self, registry: FactorRegistry, dag: FactorDependencyGraph):
        self.registry = registry
        self.dag = dag

    def get_execution_order(self) -> List[List[str]]:
        """获取分层执行顺序

        返回: [[layer1_factors], [layer2_factors], ...]
        """
        return self.dag.get_layers()

    def schedule_daily(self) -> Dict:
        """日频因子调度计划"""
        order = self.get_execution_order()

        return {
            '18:00': {
                'task': 'fetch_raw_data',
                'description': '获取原始行情数据',
                'factors': ['close_price', 'volume', 'financial_data'],
                'parallel': True
            },
            '18:30': {
                'task': 'calculate_layer1',
                'description': '计算基础因子',
                'factors': order[0] if len(order) > 0 else [],
                'parallel': True
            },
            '19:00': {
                'task': 'calculate_layer2',
                'description': '计算技术因�?,
                'factors': order[1] if len(order) > 1 else [],
                'parallel': True
            },
            '19:30': {
                'task': 'calculate_layer3',
                'description': '计算复合因子',
                'factors': order[2] if len(order) > 2 else [],
                'parallel': True
            },
            '20:00': {
                'task': 'validate_factors',
                'description': '因子验证与存�?,
                'factors': 'all',
                'parallel': False
            }
        }

    def schedule_minute(self) -> Dict:
        """分钟因子调度计划"""
        minute_factors = self.registry.get_factors_by_freq('minute')

        return {
            '09:30': {'task': 'market_open_init', 'factors': minute_factors},
            '10:00': {'task': 'hourly_update', 'factors': minute_factors},
            '11:00': {'task': 'hourly_update', 'factors': minute_factors},
            '13:00': {'task': 'hourly_update', 'factors': minute_factors},
            '14:00': {'task': 'hourly_update', 'factors': minute_factors},
            '14:30': {'task': 'pre_close_update', 'factors': minute_factors},
            '15:00': {'task': 'market_close', 'factors': minute_factors}
        }
```

---

## 5. 因子计算引擎 (Factor Engine)

### 5.1 计算引擎代码

```python
class FactorEngine:
    """因子计算引擎 - 专业机构标准"""

    def __init__(self, scheduler: FactorScheduler, registry: FactorRegistry):
        self.scheduler = scheduler
        self.registry = registry
        self.cache = RedisClient()
        self.storage = ClickHouseClient()

    def calculate_factor(self, factor_id: str, date: str,
                        symbols: List[str] = None) -> pd.DataFrame:
        """计算单个因子

        参数:
            factor_id: 因子ID
            date: 计算日期
            symbols: 股票列表 (None = 全市�?

        返回:
            DataFrame: columns = [symbol, value, timestamp]
        """
        factor_def = self.registry.get_factor(factor_id)

        # 检查缓�?
        cached = self.cache.get(f"factor:{factor_id}:{date}")
        if cached is not None:
            return cached

        # 递归计算依赖
        for dep in factor_def.dependencies:
            if not self._factor_exists(dep, date):
                self.calculate_factor(dep, date, symbols)

        # 执行计算
        result = self._execute_formula(factor_def, date, symbols)

        # 存储
        self.cache.set(f"factor:{factor_id}:{date}", result, ttl=86400)
        self.storage.insert('factors', factor_id, date, result)

        return result

    def batch_calculate(self, date: str, layer: str = None,
                        max_workers: int = 8) -> Dict:
        """批量计算某日所有因�?

        参数:
            date: 计算日期
            layer: 指定Layer (None = 全部)
            max_workers: 并行线程�?
        """
        results = {}
        order = self.scheduler.get_execution_order()

        for layer_idx, factor_batch in enumerate(order):
            # 跳过非指定layer
            if layer is not None and layer_idx + 1 != int(layer.replace('layer', '')):
                continue

            print(f"计算 Layer {layer_idx + 1}: {len(factor_batch)} 个因�?)

            # 并行计算同层因子
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(self.calculate_factor, f, date): f
                    for f in factor_batch
                }

                for future in as_completed(futures):
                    factor_id = futures[future]
                    try:
                        results[factor_id] = future.result()
                    except Exception as e:
                        print(f"因子 {factor_id} 计算失败: {e}")
                        results[factor_id] = None

        return results

    def _execute_formula(self, factor_def: FactorDefinition,
                        date: str, symbols: List[str]) -> pd.DataFrame:
        """执行因子计算公式"""
        # 根据因子类型选择计算方法
        if factor_def.category == 'technical':
            return self._calculate_technical_factor(factor_def, date, symbols)
        elif factor_def.category == 'momentum':
            return self._calculate_momentum_factor(factor_def, date, symbols)
        elif factor_def.category == 'valuation':
            return self._calculate_valuation_factor(factor_def, date, symbols)
        else:
            return self._calculate_generic_factor(factor_def, date, symbols)
```

### 5.2 技术因子计算示�?

```python
def _calculate_technical_factor(self, factor_def, date, symbols):
    """计算技术因�?""
    close = self._get_data('close_price', date, symbols)

    if 'ma' in factor_def.factor_id.lower():
        # 移动平均�?
        window = int(factor_def.factor_id.split('_')[1])
        return close.rolling(window).mean()

    elif 'rsi' in factor_def.factor_id.lower():
        # RSI
        delta = close.diff()
        gain = delta.where(delta > 0, 0)
        loss = (-delta).where(delta < 0, 0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    elif 'volatility' in factor_def.factor_id.lower():
        # 波动�?
        returns = close.pct_change()
        return returns.rolling(20).std() * np.sqrt(252)

    return close
```

---

## 6. 因子验证 (Factor Validation)

### 6.1 验证器代�?

```python
class FactorValidator:
    """因子验证 - 专业机构标准"""

    def __init__(self, storage: ClickHouseClient):
        self.storage = storage

    def validate(self, factor_id: str, start_date: str,
                end_date: str) -> Dict:
        """因子验证

        返回:
            Dict: 验证结果
        """
        results = {
            'factor_id': factor_id,
            'date_range': f"{start_date} ~ {end_date}",
            'checks': {},
            'status': 'pass'
        }

        # 1. 完整性检�?
        completeness = self._check_completeness(factor_id, start_date, end_date)
        results['checks']['completeness'] = completeness

        # 2. IC/IR分析
        ic_ir = self._calculate_ic_ir(factor_id, start_date, end_date)
        results['checks']['ic_ir'] = ic_ir

        # 3. 因子自相�?
        autocorr = self._check_autocorrelation(factor_id, start_date, end_date)
        results['checks']['autocorr'] = autocorr

        # 4. 分位数分�?
        distribution = self._check_distribution(factor_id, start_date, end_date)
        results['checks']['distribution'] = distribution

        # 判断状�?
        if ic_ir['ICIR'] < 0.3 or completeness['missing_ratio'] > 0.1:
            results['status'] = 'warning'

        if ic_ir['ICIR'] < 0.1:
            results['status'] = 'fail'

        return results

    def _check_completeness(self, factor_id, start, end) -> Dict:
        """检查数据完整�?""
        factor_data = self.storage.get_factor(factor_id, start, end)
        total_expected = len(self.storage.get_symbols()) * len(self.storage.get_dates(start, end))
        total_actual = len(factor_data.dropna())

        return {
            'total_expected': total_expected,
            'total_actual': total_actual,
            'missing_ratio': 1 - total_actual / total_expected,
            'pass': (1 - total_actual / total_expected) < 0.05
        }

    def _calculate_ic_ir(self, factor_id, start, end) -> Dict:
        """计算IC/IR"""
        factor_data = self.storage.get_factor(factor_id, start, end)
        return_data = self.storage.get_returns(factor_data.symbols, start, end)

        # 计算日频IC
        ic_series = []
        for date in factor_data.index:
            if date in return_data.index:
                ic = factor_data.loc[date].corr(return_data.loc[date])
                ic_series.append(ic)

        ic_series = pd.Series(ic_series)

        return {
            'IC_mean': ic_series.mean(),
            'IC_std': ic_series.std(),
            'ICIR': ic_series.mean() / ic_series.std() if ic_series.std() > 0 else 0,
            'IC_positive_ratio': (ic_series > 0).mean(),
            'pass': ic_series.mean() / ic_series.std() > 0.3 if ic_series.std() > 0 else False
        }

    def _check_autocorrelation(self, factor_id, start, end) -> Dict:
        """检查因子自相关"""
        factor_data = self.storage.get_factor(factor_id, start, end)
        avg_autocorr = factor_data.apply(lambda x: x.autocorr(lag=1)).mean()

        return {
            'avg_autocorr_lag1': avg_autocorr,
            'pass': avg_autocorr < 0.95  # 自相关过高说明因子冗�?
        }

    def _check_distribution(self, factor_id, start, end) -> Dict:
        """检查分位数分布"""
        factor_data = self.storage.get_factor(factor_id, start, end)

        # 计算横截面分位数
        quantile_25 = factor_data.quantile(0.25, axis=1).mean()
        quantile_50 = factor_data.quantile(0.50, axis=1).mean()
        quantile_75 = factor_data.quantile(0.75, axis=1).mean()

        return {
            'avg_q25': quantile_25,
            'avg_q50': quantile_50,
            'avg_q75': quantile_75,
            'q75_q25_ratio': quantile_75 / quantile_25 if quantile_25 != 0 else None,
            'pass': True  # 分布检查主观性较�?
        }
```

---

## 7. 专业机构日频因子计算流程

```
┌─────────────────────────────────────────────────────────────────────�?
�?             专业机构日频因子计算流程                                   �?
├─────────────────────────────────────────────────────────────────────�?
�?                                                                    �?
�? ══════════════════════════════════════════════════════════════�?  �?
�? 18:00 - 数据获取阶段                                             ══�?
�? ══════════════════════════════════════════════════════════════�?  �?
�?                                                                    �?
�? ├── 连接iFinD获取今日行情数据                                      �?
�? ├── 获取AkShare资金流数�?                                       �?
�? └── 下载财务数据 (如需)                                          �?
�?                             �?                                     �?
�? ══════════════════════════════════════════════════════════════�?  �?
�? 18:30 - Layer 1 基础因子 (可并�?                                ══�?
�? ══════════════════════════════════════════════════════════════�?  �?
�?                                                                    �?
�? ├── price_return (收益�?                                        �?
�? ├── log_price (对数价格)                                         �?
�? ├── volume_ratio (量比)                                         �?
�? ├── market_cap (市�?                                           �?
�? └── turnover (换手�?                                           �?
�?                             �?                                     �?
�? ══════════════════════════════════════════════════════════════�?  �?
�? 19:00 - Layer 2 技术因�?(可并�?                                ══�?
�? ══════════════════════════════════════════════════════════════�?  �?
�?                                                                    �?
�? ├── ma_5, ma_10, ma_20 (均线)                                   �?
�? ├── volatility_20 (波动�?                                       �?
�? ├── rsi_14 (RSI)                                                �?
�? └── macd (MACD)                                                  �?
�?                             �?                                     �?
�? ══════════════════════════════════════════════════════════════�?  �?
�? 19:30 - Layer 3 复合因子 (可并�?                                 ══�?
�? ══════════════════════════════════════════════════════════════�?  �?
�?                                                                    �?
�? ├── momentum_score (动量得分)                                    �?
�? ├── value_score (价值得�?                                      �?
�? ├── quality_score (质量得分)                                     �?
�? └── combined_score (综合得分)                                     �?
�?                             �?                                     �?
�? ══════════════════════════════════════════════════════════════�?  �?
�? 20:00 - 因子验证与存�?                                          ══�?
�? ══════════════════════════════════════════════════════════════�?  �?
�?                                                                    �?
�? ├── IC/IR计算                                                    �?
�? ├── 异常值检�?                                                  �?
�? ├── 存储ClickHouse                                              �?
�? └── 发送日�?(如有异常)                                           �?
�?                                                                    �?
└─────────────────────────────────────────────────────────────────────�?
```

---

## 8. 因子管理系统总结

| 组件 | 功能 | 专业机构标准 |
|------|------|-------------|
| **注册�?* | 因子元数据管�?| 完整字段+版本控制 |
| **依赖�?* | 拓扑排序+并行优化 | DAG+分层执行 |
| **调度�?* | 计算任务调度 | 定时任务+失败重试 |
| **计算引擎** | 因子计算执行 | 多线�?缓存 |
| **验证�?* | 因子质量检�?| IC/IR+分布检�?|

---

## 9. 与现有系统的关系

```
┌─────────────────────────────────────────────────────────────────────�?
�?                   因子计算框架与现有文档关�?                          �?
├─────────────────────────────────────────────────────────────────────�?
�?                                                                    �?
�? 本文�?(FACTOR_CALCULATION_FRAMEWORK.md)                          �?
�? ├── 定义: 因子注册表、依赖图、调度器、引擎、验证器                   �?
�? └── 位置: 02_FACTOR_LIBRARY/01_STANDARDS/                      �?
�?                                                                    �?
�? 相关文档:                                                          �?
�? ├── NEWS_SENTIMENT_DATA_SOURCE.md - 新闻舆情数据源定�?                             �?
�? ├── TECHNICAL_INDICATORS.md - 技术指标计算公�?                    �?
�? ├── FACTOR_TAXONOMY.md - 因子注册表格�?                         �?
�? ├── IC_ANALYSIS.md - IC/IR分析方法                                �?
�? └── FACTOR_PREPROCESSING.md - 因子预处理方�?                     �?
�?                                                                    �?
└─────────────────────────────────────────────────────────────────────�?
```

---

## 索引

- 父目�? [01_STANDARDS/README.md](./README.md)
- 相关: [FACTOR_TAXONOMY.md](./FACTOR_TAXONOMY.md)
- 相关: [TECHNICAL_INDICATORS.md](./TECHNICAL_INDICATORS.md)
- 相关: [IC_ANALYSIS.md](./IC_ANALYSIS.md)
