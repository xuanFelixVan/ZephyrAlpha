---
module_id: DATA_PIPELINE_BLUEPRINT_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-06
owner: 首席文档架构师
standard_type: 数据处理文档
applicable_scope: 数据流水线架构
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
implementation_progress: 0%
responsibility:
  - 扩展功能、辅助模块
---
---

# 数据流水线蓝图

## 文档职责说明

**本文档职责**: 数据流水线架构设计
- 定义数据流水线的整体架构和设计原则
- 设计数据流转和处理流程
- 规划数据存储和缓存策略

**相关文档引用**:
| 文档 | 路径 | 关系 | 说明 |
|------|------|------|------|
| 数据采集实现 | [../DATA_ACQUISITION.md](../DATA_ACQUISITION.md) | 实现层 | 数据采集的具体实现 |
| 数据清洗引擎 | [../03_CLEANING/BLUEPRINT.md](../03_CLEANING/BLUEPRINT.md) | 下游处理 | 数据清洗规则和流程 |
| 数据质量管理 | [../QUALITY_MANAGEMENT/](../QUALITY_MANAGEMENT/) | 下游检查 | 数据质量控制体系 |

**职责边界**:
- ✅ 本文档负责: 定义数据流水线的整体架构和设计原则
- ❌ 本文档不负责: 具体的数据采集实现（由 DATA_ACQUISITION.md 负责）
- ❌ 本文档不负责: 具体的数据清洗规则（由 03_CLEANING/BLUEPRINT.md 负责）

> 清风量化系统 v5.0 的数据流水线架构
> **索引**: `DAT_001`

**相关文档**:
| 文档 | 路径 | 关系 | 说明 |
|------|------|------|------|
| 数据采集实现 | [../DATA_ACQUISITION.md](../DATA_ACQUISITION.md) | 实现层 | 数据采集的具体实现 |
| 数据清洗引擎 | [../03_CLEANING/BLUEPRINT.md](../03_CLEANING/BLUEPRINT.md) | 下游处理 | 数据清洗规则和流程 |
| 数据质量管理 | [../QUALITY_MANAGEMENT/](../QUALITY_MANAGEMENT/) | 下游检查 | 数据质量控制体系 |

**职责边界**:
- ✅ 本文档负责: 定义数据流水线的整体架构和设计原则
- ❌ 本文档不负责: 具体的数据采集实现（由 DATA_ACQUISITION.md 负责）
- ❌ 本文档不负责: 具体的数据清洗规则（由 03_CLEANING/BLUEPRINT.md 负责）


## 1. 设计原则

| 原则 | 说明 |
|------|------|
| 数据质量第一 | 不干净的数据不如没有数�?|
| 可追�?| 每个数据都有来源记录 |
| 可重�?| 支持历史数据重新处理 |
| 分层缓存 | �?�?冷数据分级存�?|


## 2. 数据流水线架�?

### 2.1 流水线层�?

```
┌─────────────────────────────────────────────────────────────�?
�?│                   数据基础设施层                             │�?
├─────────────────────────────────────────────────────────────�?
�? ┌───────────�? ┌───────────�? ┌───────────�? ┌───────────┐│
�? �?交易所API  �? �?财务数据�?�? �? 新闻�?  �? �?宏观数据  ││
�? └─────┬─────�? └─────┬─────�? └─────┬─────�? └─────┬─────┘│
�?       �?             �?             �?             �?      �?
�?       └──────────────┴──────────────┴──────────────�?      �?
�?                          �?                                 �?
�?                          �?                                 �?
�? ┌───────────────────────────────────────────────────────────�?
�? �?             数据接入�?(Data Ingestion)                  �?
�? �? - 实时流接�? - 批量导入  - API拉取  - 文件上传         �?
�? └───────────────────────────────────────────────────────────�?
�?                          �?                                 �?
�?                          �?                                 �?
�? ┌───────────────────────────────────────────────────────────�?
�? �?             数据清洗�?(Data Cleaning)                   �?
�? �? - 缺失值处�? - 异常值检�? - 数据对齐  - 复权处理       �?
�? └───────────────────────────────────────────────────────────�?
�?                          �?                                 �?
�?                          �?                                 �?
�? ┌───────────────────────────────────────────────────────────�?
�? �?             数据存储�?(Data Storage)                    �?
�? �? - Redis(热数�?  - PostgreSQL(温数�?  - 文件(冷数�?   �?
�? └───────────────────────────────────────────────────────────�?
�?                          �?                                 �?
�?                          �?                                 �?
�? ┌───────────────────────────────────────────────────────────�?
�? �?             数据服务�?(Data Service)                   �?
�? �? - 统一查询接口  - 数据订阅  - 缓存管理  - 权限控制       �?
�? └───────────────────────────────────────────────────────────�?
└─────────────────────────────────────────────────────────────�?
```

### 2.2 数据类型分类

| 数据类型 | 更新频率 | 存储方式 | 保留期限 | 示例 |
|----------|----------|----------|----------|------|
| OHLCV | 实时/日级 | Redis+DB | 10�?| 股价、成交量 |
| 财务数据 | 季级 | DB | 永久 | 营收、利�?|
| 因子数据 | 日级 | DB | 5�?| Alpha因子�?|
| 风险数据 | 实时 | Redis | 1�?| VaR、波动率 |
| 新闻文本 | 实时 | 文件+DB | 2�?| 财经新闻 |
| 宏观数据 | 日级 | DB | 永久 | GDP、CPI |


## 3. 核心模块设计

### 3.1 数据接入�?(DataIngestor)

```python
class DataIngestor:
    """数据接入�?

    索引: DAT_001-M01
    上游: 各数据源API
    下游: DataCleaner
    """

    def __init__(self):
        self.sources = {}
        self.reader_factory = ReaderFactory()

    def register_source(self, source_id: str, source_config: dict):
        """注册数据�?

        参数:
            source_id: 数据源ID
            source_config: 数据源配�?
        """
        reader = self.reader_factory.create(source_config['type'])
        self.sources[source_id] = {
            'reader': reader,
            'config': source_config,
            'last_sync': None
        }

    def ingest(self, source_id: str, date_range: tuple) -> DataBatch:
        """接入数据

        参数:
            source_id: 数据源ID
            date_range: 日期范围 (start_date, end_date)

        返回:
            DataBatch: 数据批次
        """
        source = self.sources[source_id]
        reader = source['reader']

        data = reader.read(date_range)

        batch = DataBatch(
            source_id=source_id,
            data=data,
            timestamp=datetime.now(),
            metadata={
                'record_count': len(data),
                'date_range': date_range
            }
        )

        source['last_sync'] = datetime.now()
        return batch

    def ingest_realtime(self, source_id: str, callback: Callable):
        """实时数据接入

        参数:
            source_id: 数据源ID
            callback: 数据回调函数
        """
        source = self.sources[source_id]
        reader = source['reader']

        reader.subscribe(callback)
```

### 3.2 数据清洗�?(DataCleaner)

```python
class DataCleaner:
    """数据清洗�?

    索引: DAT_001-M02
    上游: DataIngestor
    下游: DataStorage
    """

    def __init__(self):
        self.cleaning_rules = {}
        self.pipeline = CleaningPipeline()

    def add_cleaning_rule(self, rule: CleaningRule):
        """添加清洗规则

        参数:
            rule: 清洗规则
        """
        self.pipeline.add_rule(rule)

    def clean(self, data: DataFrame, data_type: str) -> DataFrame:
        """清洗数据

        参数:
            data: 原始数据
            data_type: 数据类型

        返回:
            清洗后的数据
        """
        rules = self.cleaning_rules.get(data_type, [])

        cleaned = data.copy()
        for rule in rules:
            cleaned = rule.apply(cleaned)

        return cleaned

    def validate(self, data: DataFrame, schema: Schema) -> ValidationResult:
        """验证数据

        参数:
            data: 数据
            schema: 数据schema

        返回:
            验证结果
        """
        errors = []

        for field, constraints in schema.fields.items():
            if field not in data.columns:
                errors.append(f"Missing field: {field}")
                continue

            if constraints.required and data[field].isna().any():
                errors.append(f"Null values in required field: {field}")

            if constraints.dtype and data[field].dtype != constraints.dtype:
                errors.append(f"Invalid dtype for {field}")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors
        )
```

### 3.3 数据存储�?(DataStorage)

```python
class DataStorage:
    """数据存储�?

    索引: DAT_001-M03
    上游: DataCleaner
    下游: DataService
    """

    def __init__(self):
        self.stores = {
            'hot': RedisStore(),      # 热数�? Redis
            'warm': PostgresStore(),   # 温数�? PostgreSQL
            'cold': FileStore()       # 冷数�? 文件
        }
        self.router = StorageRouter()

    def save(self, data: DataFrame, data_type: str, tier: str = 'warm'):
        """存储数据

        参数:
            data: 数据
            data_type: 数据类型
            tier: 存储层级
        """
        store = self.stores[tier]
        store.write(data_type, data)

    def load(self, data_type: str, query: dict, tier: str = None) -> DataFrame:
        """加载数据

        参数:
            data_type: 数据类型
            query: 查询条件
            tier: 存储层级(None则自动选择)

        返回:
            数据
        """
        if tier is None:
            tier = self.router.select_tier(data_type, query)

        store = self.stores[tier]
        return store.read(data_type, query)

    def delete(self, data_type: str, date_range: tuple):
        """删除过期数据

        参数:
            data_type: 数据类型
            date_range: 日期范围
        """
        for tier, store in self.stores.items():
            if store.exists(data_type):
                store.delete(data_type, date_range)
```

### 3.4 数据服务 (DataService)

```python
class DataService:
    """数据服务

    索引: DAT_001-M04
    上游: DataStorage
    下游: FactorCalculator, StrategyEngine�?
    """

    def __init__(self):
        self.cache = CacheManager()
        self.api = DataAPI()

    def get_ohlcv(self, symbol: str, start_date: str, end_date: str) -> DataFrame:
        """获取OHLCV数据

        参数:
            symbol: 股票代码
            start_date: 开始日�?
            end_date: 结束日期

        返回:
            OHLCV数据
        """
        cache_key = f"ohlcv:{symbol}:{start_date}:{end_date}"

        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        data = self.storage.load(
            'ohlcv',
            {'symbol': symbol, 'date_range': (start_date, end_date)}
        )

        self.cache.set(cache_key, data, ttl=3600)
        return data

    def subscribe_realtime(self, symbol: str, callback: Callable):
        """订阅实时数据

        参数:
            symbol: 股票代码
            callback: 回调函数
        """
        channel = f"realtime:{symbol}"
        self.event_bus.subscribe(channel, callback)

    def batch_get(self, symbols: List[str], data_type: str,
                  start_date: str, end_date: str) -> Dict[str, DataFrame]:
        """批量获取数据

        参数:
            symbols: 股票代码列表
            data_type: 数据类型
            start_date: 开始日�?
            end_date: 结束日期

        返回:
            {symbol: DataFrame}
        """
        results = {}
        for symbol in symbols:
            results[symbol] = self.get_ohlcv(symbol, start_date, end_date)
        return results
```


## 4. 数据质量监控

### 4.1 质量检查规�?

```python
class DataQualityChecker:
    """数据质量检查器

    索引: DAT_001-Q01
    """

    CHECK_RULES = {
        'ohlcv': [
            ('no_null_ohlcv', 'OHLCV不能为空'),
            ('price_positive', '价格必须为正'),
            ('volume_non_negative', '成交量必须非�?),
            ('high_low_valid', '最高价>=最低价'),
            ('open_in_range', '开盘价在高低之�?),
            ('close_in_range', '收盘价在高低之间'),
        ],
        'financial': [
            ('no_null_required', '必填字段不能为空'),
            ('values_non_negative', '财务指标非负'),
            ('reasonableness_check', '值在合理范围�?),
        ]
    }

    def check(self, data: DataFrame, data_type: str) -> QualityReport:
        """执行质量检�?

        参数:
            data: 数据
            data_type: 数据类型

        返回:
            质量报告
        """
        rules = self.CHECK_RULES.get(data_type, [])
        results = []

        for rule_name, rule_desc in rules:
            rule_func = getattr(self, rule_name)
            passed, details = rule_func(data)
            results.append({
                'rule': rule_name,
                'description': rule_desc,
                'passed': passed,
                'details': details
            })

        return QualityReport(
            data_type=data_type,
            total_rules=len(results),
            passed_rules=sum(1 for r in results if r['passed']),
            failed_rules=[r for r in results if not r['passed']],
            quality_score=sum(1 for r in results if r['passed']) / len(results)
        )
```

### 4.2 质量指标

| 指标 | 目标�?| 告警阈�?|
|------|--------|----------|
| 数据完整�?| >99.9% | <99% |
| 数据准确�?| >99.9% | <99.5% |
| 数据时效�?| <5min | >15min |
| 缺失值比�?| <0.1% | >1% |
| 异常值比�?| <0.01% | >0.1% |


## 5. 数据API接口

### 5.1 统一查询接口

```python
# API: /api/v1/data

class DataAPI:
    """数据API

    索引: API_DAT_001
    Layer: 数据源层
    """

    @router.get("/ohlcv/{symbol}")
    def get_ohlcv(
        symbol: str,
        start_date: str,
        end_date: str,
        adjust: str = "qfq"
    ) -> DataResponse:
        """获取OHLCV数据

        参数:
            symbol: 股票代码
            start_date: 开始日�?
            end_date: 结束日期
            adjust: 复权类型 (qfq/hfq/none)
        """

    @router.get("/financial/{symbol}")
    def get_financial(
        symbol: str,
        report_type: str = "annual"
    ) -> DataResponse:
        """获取财务数据

        参数:
            symbol: 股票代码
            report_type: 报表类型 (annual/quarterly)
        """

    @router.get("/factors/{symbol}")
    def get_factors(
        symbol: str,
        factor_ids: List[str],
        start_date: str,
        end_date: str
    ) -> DataResponse:
        """获取因子数据

        参数:
            symbol: 股票代码
            factor_ids: 因子ID列表
            start_date: 开始日�?
            end_date: 结束日期
        """

    @router.post("/batch/ohlcv")
    def batch_get_ohlcv(
        symbols: List[str],
        start_date: str,
        end_date: str
    ) -> BatchDataResponse:
        """批量获取OHLCV数据"""
```


## 6. 存储策略

### 6.1 分层存储配置

```yaml
# config/data_pipeline/storage.yaml

storage:
  hot_tier:
    backend: redis
    ttl: 3600  # 1小时
    max_size: 10GB
    data_types:
      - realtime_quote
      - intraday_ohlcv

  warm_tier:
    backend: postgresql
    retention: 2years
    max_size: 100GB
    data_types:
      - daily_ohlcv
      - financial_data
      - factor_data

  cold_tier:
    backend: file
    retention: 10years
    path: /data/cold
    format: parquet
    data_types:
      - historical_ohlcv
      - archived_financial
```

### 6.2 数据保留策略

```yaml
retention:
  ohlcv:
    realtime: 1day
    daily: 10years
   分钟K: 1year
    5分钟K: 3years

  financial:
    quarterly: permanent
    annual: permanent

  factors:
    alpha_factors: 5years
    risk_factors: 5years
```


## 7. 集成接口

### 7.1 上游接口

| 数据�?| 接口 | 说明 |
|--------|------|------|
| 交易所API | REST/WebSocket | 实时行情、历史K�?|
| 财务数据�?| SQL | 财报数据 |
| 财经新闻 | API + 爬虫 | 资讯数据 (iFind + 东方财富/新浪) |
| 宏观数据 | CSV/API | 经济指标 |
| 本地LLM | GLM-4-Flash API | 新闻情感分析 |
| 本地LLM | Qwen2.5-7B | 事件分类 |
| 本地LLM | ChatGLM3-6B | 实体识别 |

### 7.2 下游接口

| 模块 | 接口 | 说明 |
|------|------|------|
| FactorCalculator | get_factor_data() | 获取计算因子所需数据 |
| StrategyEngine | get_market_data() | 获取市场数据 |
| RiskManager | get_risk_data() | 获取风险数据 |
| BacktestEngine | get_historical_data() | 获取历史数据 |
| PerformanceAnalyzer | get_trading_data() | 获取交易数据 |


## 8. 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.1 | 2026-03-29 | 新增新闻舆情LLM处理方案 |
| v1.0 | 2026-03-28 | 初始版本 |


**维护�?*: 清风量化系统
**索引**: `DAT_001`

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
---

## 9. 文档治理

### 9.1 System_Manifest.md索引

```markdown
#### Layer 0: 系统架构
##### 0.001. Data Pipeline Blueprint
- **模块ID**: DATA_PIPELINE_BLUEPRINT_001
- **蓝图文档**: [BLUEPRINT.md](./02_FACTOR_LIBRARY\04_DATA_SOURCE\07_DATA_PIPELINE\BLUEPRINT.md)
- **技术规格书**: 待创建
- **职责**: 数据流水线架构
- **状态**: Active
```

### 9.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **Data Pipeline Blueprint** | 数据流水线架构 | **核心模块** |

### 9.3 版本管理

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-01 | 初始版本创建 | 首席蓝图架构师 |

---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-01 | **状态**: Active
