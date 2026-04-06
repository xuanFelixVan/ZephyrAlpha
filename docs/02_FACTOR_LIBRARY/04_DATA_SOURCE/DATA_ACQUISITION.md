---
module_id: DATA_ACQUISITION_001
version: 1.0.1
status: Active
created_date: 2026-04-01
last_updated: 2026-04-05
owner: 首席文档架构师
standard_type: 数据处理文档
applicable_scope: 数据采集系统
compliance_level: 专业标准
parent_document: ./INDEX.md
implementation_status: 进行中
responsibility: 数据采集策略制定与数据源管理
---

# 数据采集蓝图

## 文档职责说明

**本文档职责**: 数据采集技术实现
- 定义数据采集架构和实现方案
- 规划数据源接入和调度系统
- 设计数据存储架构

**相关文档引用**:
| 文档 | 路径 | 关系 | 说明 |
|------|------|------|------|
| 数据需求清单 | [DATA_REQUIREMENTS.md](./DATA_REQUIREMENTS.md) | 上游规格 | 定义需要采集的数据规格 |
| 数据清洗引擎 | [03_CLEANING/](./03_CLEANING/) | 下游处理 | 数据清洗和质量检查 |
| 数据源索引 | [INDEX.md](./INDEX.md) | 上级索引 | 数据源模块总索引 |

**职责边界**:
- ✅ 本文档负责: 定义"如何获取数据"
- ❌ 本文档不负责: 定义需要什么数据（由 DATA_REQUIREMENTS.md 负责）

> 清风量化系统 v5.0 - 数据采集与清洗系统
> **索引**: `DATA.001`
> **开发时间**: 35h
> **核心定位**: 实现"多数据源 → 自动采集 → 智能清洗 → 统一存储"的完整数据Pipeline


## 1. 设计原则

| 原则 | 说明 |
|------|------|
| **AkShare主力** | AkShare + Tushare为主，备用其他数据源 |
| **Prefect调度** | 使用Prefect自动调度数据采集任务 |
| **异常自动处理** | 数据异常自动检测和处理 |
| **断点可续** | 采集失败后从断点继续 |


## 2. 数据源架构

### 2.1 数据源矩阵

| 数据源 | 类型 | 数据范围 | 更新频率 | 优先级 |
|--------|------|----------|----------|--------|
| **AkShare** | 免费 | 行情/财务/宏观 | 5分钟 | ⭐⭐⭐⭐⭐ |
| **Tushare** | 免费/付费 | 全量A股 | 5分钟 | ⭐⭐⭐⭐ |
| **Wind** | 付费 | 全量 | 实时 | ⭐⭐⭐ |
| **聚宽** | 免费/付费 | 全量 | 5分钟 | ⭐⭐⭐ |

### 2.2 数据类型

```python
DATA_TYPES = {
    'ohlcv': {
        'description': 'K线数据',
        'frequency': ['1m', '5m', '15m', '30m', '1h', '1d'],
        'fields': ['open', 'high', 'low', 'close', 'volume']
    },
    'fundamental': {
        'description': '财务数据',
        'frequency': ['quarterly', 'annual'],
        'fields': ['revenue', 'profit', 'assets', 'debt']
    },
    'market_data': {
        'description': '市场数据',
        'frequency': ['realtime', 'daily'],
        'fields': ['bid', 'ask', 'vwap', 'turnover']
    },
    'index': {
        'description': '指数数据',
        'frequency': ['1m', '5m', '1d'],
        'fields': ['open', 'high', 'low', 'close', 'volume']
    }
}
```


## 3. 核心实现

### 3.1 数据采集器

```python
from akshare import stock_zh_a_hist, tushare_api
from prefect import task

class DataAcquisitor:
    """数据采集器

    索引: DATA.001-M01
    上游: 数据源API
    下游: DataCleaner, DataStorage
    """

    def __init__(self):
        self.sources = {
            'akshare': AkShareAdapter(),
            'tushare': TushareAdapter()
        }

    @task(name="采集日线数据", retries=3)
    def fetch_daily_ohlcv(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        source: str = 'akshare'
    ) -> pd.DataFrame:
        """采集日线数据

        参数:
            symbol: 股票代码 (如 '000001')
            start_date: 开始日期
            end_date: 结束日期
            source: 数据源

        返回:
            OHLCV DataFrame
        """
        adapter = self.sources.get(source, self.sources['akshare'])

        try:
            data = adapter.get_ohlcv(symbol, start_date, end_date)
            logger.info(f"采集成功: {symbol} {len(data)}条数据")
            return data
        except Exception as e:
            logger.error(f"采集失败: {symbol} {e}")
            # 尝试备用数据源
            return self._try_backup_source(symbol, start_date, end_date)

    def _try_backup_source(
        self,
        symbol: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """尝试备用数据源"""
        for source_name, adapter in self.sources.items():
            if source_name == 'akshare':
                continue
            try:
                return adapter.get_ohlcv(symbol, start_date, end_date)
            except:
                continue
        raise DataSourceError(f"所有数据源都失败: {symbol}")
```

### 3.2 数据清洗器

```python
class DataCleaner:
    """数据清洗器

    索引: DATA.001-M02
    上游: DataAcquisitor
    下游: DataStorage
    """

    def clean_ohlcv(self, data: pd.DataFrame) -> pd.DataFrame:
        """清洗OHLCV数据

        参数:
            data: 原始OHLCV数据

        返回:
            清洗后的数据
        """
        cleaned = data.copy()

        # 1. 列名标准化
        cleaned.columns = cleaned.columns.str.lower()

        # 2. 日期格式
        if 'date' in cleaned.columns:
            cleaned['date'] = pd.to_datetime(cleaned['date'])
        elif 'trade_date' in cleaned.columns:
            cleaned['date'] = pd.to_datetime(cleaned['trade_date'])

        # 3. 缺失值处理
        cleaned = self._handle_missing_values(cleaned)

        # 4. 异常值处理
        cleaned = self._handle_outliers(cleaned)

        # 5. 复权处理
        cleaned = self._handle_adjustment(cleaned)

        # 6. 排序
        cleaned = cleaned.sort_values('date')

        return cleaned

    def _handle_missing_values(self, data: pd.DataFrame) -> pd.DataFrame:
        """处理缺失值"""
        # 前向填充 (开盘价/收盘价用前值)
        price_cols = ['open', 'high', 'low', 'close']
        data[price_cols] = data[price_cols].fillna(method='ffill')

        # 成交量用0填充
        data['volume'] = data['volume'].fillna(0)

        # 删除仍有缺失的行
        data = data.dropna(subset=['close', 'volume'])

        return data

    def _handle_outliers(self, data: pd.DataFrame) -> pd.DataFrame:
        """处理异常值"""
        # 价格异常: 最高<最低
        invalid = data['high'] < data['low']
        data = data[~invalid]

        # 价格异常: 收盘价超出高低范围
        invalid = (data['close'] > data['high']) | (data['close'] < data['low'])
        data = data[~invalid]

        # 成交量异常: 负数
        data = data[data['volume'] >= 0]

        return data

    def _handle_adjustment(self, data: pd.DataFrame) -> pd.DataFrame:
        """处理复权"""
        # 默认前复权(qfq)
        if 'adj_close' in data.columns and 'close' not in data.columns:
            data['close'] = data['adj_close']

        return data
```

### 3.3 数据质量检查

```python
class DataQualityChecker:
    """数据质量检查

    索引: DATA.001-M03
    """

    QUALITY_RULES = {
        'ohlcv': [
            ('no_missing_close', '收盘价不能为空'),
            ('no_negative_price', '价格不能为负'),
            ('no_invalid_hl', '最高价>=最低价'),
            ('no_zero_volume_days', '成交量不能连续为0')
        ]
    }

    def check(self, data: pd.DataFrame, data_type: str) -> QualityReport:
        """执行质量检查

        参数:
            data: 数据
            data_type: 数据类型

        返回:
            QualityReport
        """
        rules = self.QUALITY_RULES.get(data_type, [])
        results = []

        for rule_name, rule_desc in rules:
            rule_func = getattr(self, rule_name, None)
            if rule_func:
                passed, details = rule_func(data)
                results.append({
                    'rule': rule_name,
                    'description': rule_desc,
                    'passed': passed,
                    'details': details
                })

        score = sum(1 for r in results if r['passed']) / len(results) * 100

        return QualityReport(
            data_type=data_type,
            score=score,
            passed=score >= 90,
            details=results
        )
```


## 4. Prefect调度

### 4.1 调度配置

```python
from prefect import flow, schedule
from prefect.schedules import CronSchedule

@flow(
    name="日线数据采集",
    schedule=CronSchedule(cron="0 18 * * 1-5"),  # 收盘后18:00
    log_prints=True
)
def daily_data_collection_flow():
    """日线数据采集Flow

    索引: DATA.001-F01
    """
    # 1. 获取股票列表
    stocks = get_stock_list()

    # 2. 批量采集
    for symbol in stocks:
        data = fetch_daily_ohlcv(
            symbol=symbol,
            start_date=get_last_trading_date(),
            end_date=get_today_date()
        )

        # 3. 清洗
        cleaned = clean_ohlcv(data)

        # 4. 质量检查
        report = DataQualityChecker().check(cleaned, 'ohlcv')

        if report.passed:
            # 5. 存储
            save_to_storage(cleaned, symbol)
        else:
            # 记录问题
            log_quality_issue(symbol, report)

@flow(
    name="分钟数据采集",
    schedule=CronSchedule(cron="*/30 9-15 * * 1-5"),  # 交易时段每30分钟
    log_prints=True
)
def minute_data_collection_flow():
    """分钟数据采集Flow"""
    pass
```

### 4.2 调度时间表

| Flow | 时间 | 频率 | 说明 |
|------|------|------|------|
| 日线采集 | 18:00 | 每日 | 收盘后采集 |
| 分钟采集 | 9:00-15:00 | 30分钟 | 盘中实时 |
| 财务采集 | 20:00 | 每日 | 盘后财务数据 |
| 指数采集 | 18:30 | 每日 | 收盘后指数 |


## 5. 数据存储

### 5.1 存储架构

```
存储层级:
├── Redis (热数据)
│   └── 最近一个月分钟数据
├── PostgreSQL (温数据)
│   └── 最近一年日线数据
└── Parquet (冷数据)
    └── 历史全部数据
```

### 5.2 存储配置

```python
class DataStorage:
    """数据存储

    索引: DATA.001-M04
    """

    def __init__(self):
        self.redis = RedisClient()
        self.pg = PostgresClient()
        self.s3 = S3Client()

    def save(self, data: pd.DataFrame, symbol: str, freq: str):
        """存储数据

        参数:
            data: 数据
            symbol: 股票代码
            freq: 频率 (1m/5m/1d)
        """
        if freq.endswith('m'):
            # 分钟数据存Redis
            self.redis.save(f"ohlcv:{symbol}:{freq}", data, ttl=86400*30)
        elif freq == '1d':
            # 日线存PostgreSQL
            self.pg.save(f"ohlcv_{freq}", data, symbol)
            # 超过2年转Parquet
            if data['date'].min() < (datetime.now() - relativedelta(years=2)):
                self.s3.save(data, f"ohlcv/{symbol}/{freq}")
```


## 6. API接口

### 6.1 数据查询API

```python
# API: /api/v1/data

class DataAPI:
    """数据API

    索引: API_DATA_001
    """

    @router.get("/ohlcv/{symbol}")
    def get_ohlcv(
        symbol: str,
        freq: str = "1d",
        start_date: str = None,
        end_date: str = None
    ) -> DataResponse:
        """获取OHLCV数据

        参数:
            symbol: 股票代码
            freq: 频率 (1m/5m/15m/1h/1d)
            start_date: 开始日期
            end_date: 结束日期
        """
        # 优先从缓存获取
        cache_key = f"ohlcv:{symbol}:{freq}:{start_date}:{end_date}"
        cached = self.redis.get(cache_key)
        if cached:
            return cached

        # 从存储获取
        data = self.storage.load(symbol, freq, start_date, end_date)

        # 缓存
        self.redis.set(cache_key, data, ttl=3600)

        return data

    @router.get("/stock_list")
    def get_stock_list(
        exchange: str = None,
        market: str = "A股"
    ) -> List[str]:
        """获取股票列表"""
        pass
```


## 7. 监控指标

| 指标 | 说明 | 阈值 |
|------|------|------|
| data_fetch_success_rate | 采集成功率 | >98% |
| data_quality_score | 数据质量评分 | >90% |
| data_freshness | 数据新鲜度 | <30min |
| storage_usage | 存储使用率 | <80% |


## 8. 开发任务分解

### 8.1 任务分解 (35h)

| 任务 | 时间 | 说明 |
|------|------|------|
| AkShare适配器 | 6h | AkShare数据获取封装 |
| Tushare适配器 | 4h | Tushare数据获取封装 |
| 数据清洗模块 | 8h | 缺失值/异常值/复权 |
| 质量检查模块 | 4h | QualityChecker |
| Prefect调度 | 6h | Flow定义+调度配置 |
| 存储模块 | 4h | Redis/PostgreSQL/Parquet |
| API层 | 3h | REST API |


## 9. 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-29 | 初始版本 |
| v1.1 | 2026-04-05 | 添加文档职责说明章节，明确与DATA_REQUIREMENTS.md的职责边界 |


**维护者**: 清风量化系统
**索引**: `DATA.001`

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
