---
module_id: FACTOR_DOC_001
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


# 数据需求清�?

> 清风量化系统 v4.0 的完整数据需求规�?


## 1. 市场数据需�?

### 1.1 OHLCV数据

**数据�?*: 交易所、数据服务商(THS_BD、Wind、Bloomberg)

**数据字段**:
```
symbol: 股票代码 (e.g., "000001.SZ")
date: 交易日期
open: 开盘价
high: 最高价
low: 最低价
close: 收盘�?
volume: 成交�?(�?
amount: 成交�?(�?
adj_close: 复权收盘�?
```

**数据频率**:
- 日线: 每个交易�?1�?
- 周线: 每周�?1�?
- 月线: 每月最后一个交易日 1�?
- 分钟�? 每分�?1�?(可�?

**数据范围**:
- 历史数据: 5�?(2021-01-01 至今)
- 实时数据: 每日更新
- 股票数量: A股全市场 (4000+�?

**数据质量要求**:
- 缺失�? < 0.1%
- 异常�? < 0.01%
- 延迟: < 1�?


### 1.2 财务数据

**数据�?*: 上市公司公告、数据服务商

**数据字段**:
```
symbol: 股票代码
report_date: 报告�?
revenue: 营业收入
net_income: 净利润
eps: 每股收益
roe: 净资产收益�?
pe_ratio: 市盈�?
pb_ratio: 市净�?
dividend_yield: 股息�?
debt_ratio: 负债率
```

**数据频率**:
- 季度: 每季度末 1�?
- 年度: 每年�?1�?

**数据范围**:
- 历史数据: 5�?
- 股票数量: A股全市场

**数据质量要求**:
- 准确�? 与官方公告一�?
- 完整�? > 95%


### 1.3 行业数据

**数据�?*: 行业分类、指数数�?

**数据字段**:
```
symbol: 股票代码
industry: 行业分类 (申万一级、二级、三�?
sector: 板块分类
index_code: 所属指�?
```

**数据频率**:
- 静态数�? 每月更新
- 动态数�? 每日更新


## 2. 因子数据需�?

### 2.1 Alpha因子数据

**因子数量**: 87�?

**因子分类**:
- 趋势�? 14�?
- 均值回归类: 12�?
- value_factors: 15�?
- 成长�? 12�?
- 质量�? 18�?
- 技术面�? 10�?
- 情绪�? 6�?

**数据需�?*:
```
symbol: 股票代码
date: 交易日期
factor_id: 因子ID (e.g., "ALPHA_001")
factor_value: 因子�?(float)
factor_rank: 因子排名 (1-4000)
factor_zscore: 因子Z-score标准化�?
```

**数据频率**: 每个交易�?1�?

**数据范围**: 5年历�?+ 实时更新

**计算方式**:
- 基于OHLCV数据计算
- 支持自定义参�?
- 支持滚动窗口计算


### 2.2 风险因子数据

**因子数量**: 46�?

**因子分类**:
- Barra风格因子: 10�?
- 行业因子: 30�?
- 尾部风险因子: 6�?

**数据需�?*:
```
symbol: 股票代码
date: 交易日期
risk_factor_id: 风险因子ID
risk_factor_value: 风险因子�?
risk_score: 综合风险评分
```

**数据频率**: 每个交易�?1�?


## 3. 交易数据需�?

### 3.1 成交数据

**数据字段**:
```
symbol: 股票代码
date: 交易日期
time: 交易时间
price: 成交�?
volume: 成交�?
amount: 成交�?
bid_price: 买价
ask_price: 卖价
bid_volume: 买量
ask_volume: 卖量
```

**数据频率**: 实时 (每笔成交)

**数据范围**: 当日交易数据


### 3.2 持仓数据

**数据字段**:
```
symbol: 股票代码
date: 交易日期
quantity: 持仓数量
cost_price: 成本�?
market_price: 市场�?
market_value: 市�?
profit_loss: 浮动盈亏
profit_loss_pct: 浮动盈亏�?
```

**数据频率**: 每个交易�?1�?


## 4. 宏观数据需�?

### 4.1 经济指标

**数据字段**:
```
date: 数据日期
gdp: 国内生产总�?
inflation: 通货膨胀�?
unemployment: 失业�?
interest_rate: 利率
exchange_rate: 汇率
```

**数据频率**: 月度或季�?

**数据范围**: 5年历�?


### 4.2 市场指数

**数据字段**:
```
index_code: 指数代码 (e.g., "000001.SH" 上证指数)
date: 交易日期
open: 开盘价
high: 最高价
low: 最低价
close: 收盘�?
volume: 成交�?
```

**指数列表**:
- 上证指数 (000001.SH)
- 深证成指 (399001.SZ)
- 沪深300 (000300.SH)
- 中证500 (000905.SH)
- 创业板指 (399006.SZ)

**数据频率**: 每个交易�?1�?


## 5. 新闻和舆情数据需�?

### 5.1 新闻数据

**数据字段**:
```
symbol: 股票代码
date: 发布日期
title: 新闻标题
content: 新闻内容
source: 新闻来源
sentiment: 情绪分类 (正面/中�?负面)
```

**数据频率**: 实时

**数据范围**: 1年历�?


### 5.2 舆情数据

**数据字段**:
```
symbol: 股票代码
date: 数据日期
sentiment_score: 舆情评分 (-1 to 1)
mention_count: 提及次数
positive_count: 正面提及
negative_count: 负面提及
```

**数据频率**: 每日


## 6. 数据存储规格

### 6.1 数据库设�?

**主要�?*:
```sql
-- OHLCV数据�?
CREATE TABLE market_data (
    id BIGINT PRIMARY KEY,
    symbol VARCHAR(20),
    date DATE,
    open DECIMAL(10,2),
    high DECIMAL(10,2),
    low DECIMAL(10,2),
    close DECIMAL(10,2),
    volume BIGINT,
    amount BIGINT,
    INDEX idx_symbol_date (symbol, date)
);

-- 因子数据�?
CREATE TABLE factor_data (
    id BIGINT PRIMARY KEY,
    symbol VARCHAR(20),
    date DATE,
    factor_id VARCHAR(20),
    factor_value DECIMAL(15,6),
    INDEX idx_symbol_date_factor (symbol, date, factor_id)
);

-- 财务数据�?
CREATE TABLE financial_data (
    id BIGINT PRIMARY KEY,
    symbol VARCHAR(20),
    report_date DATE,
    revenue DECIMAL(15,2),
    net_income DECIMAL(15,2),
    eps DECIMAL(10,4),
    roe DECIMAL(10,4),
    INDEX idx_symbol_date (symbol, report_date)
);
```

### 6.2 数据分区

**按日期分�?*:
```
market_data_2026_03_28
market_data_2026_03_27
...
```

**按股票分�?* (可�?:
```
market_data_000001
market_data_000002
...
```

### 6.3 数据备份

**备份策略**:
- 每日全量备份
- 每小时增量备�?
- 保留�? 30�?

**备份位置**:
- 本地: `/backup/local/`
- 异地: `/backup/remote/`


## 7. 数据获取方式

### 7.1 API接口

**数据�?*: THS_BD (同花�?

```python
# 获取OHLCV数据
from ths_api import THSClient

client = THSClient(api_key='your_api_key')
data = client.get_ohlcv(
    symbol='000001.SZ',
    start_date='2021-01-01',
    end_date='2026-03-28',
    frequency='daily'
)
```

### 7.2 文件导入

**格式**: CSV、Parquet、HDF5

```python
import pandas as pd

# 从CSV导入
df = pd.read_csv('market_data.csv')

# 从Parquet导入
df = pd.read_parquet('market_data.parquet')
```

### 7.3 实时推�?

**协议**: WebSocket

```python
import websocket

def on_message(ws, message):
    # 处理实时数据
    print(message)

ws = websocket.WebSocketApp(
    "wss://api.example.com/realtime",
    on_message=on_message
)
ws.run_forever()
```


## 8. 数据质量检�?

### 8.1 完整性检�?

```python
# 检查缺失�?
missing_rate = df.isnull().sum() / len(df)
assert missing_rate < 0.001, "缺失率过�?

# 检查数据覆�?
assert len(df) > 1000, "数据不足"
```

### 8.2 准确性检�?

```python
# 检查价格逻辑
assert (df['low'] <= df['close']).all(), "最低价 > 收盘�?
assert (df['close'] <= df['high']).all(), "收盘�?> 最高价"

# 检查成交量
assert (df['volume'] > 0).all(), "成交量为0"
```

### 8.3 一致性检�?

```python
# 检查时间序列连续�?
dates = pd.date_range(start_date, end_date, freq='D')
trading_dates = df['date'].unique()
assert len(trading_dates) > len(dates) * 0.95, "交易日期不连�?
```


## 9. 数据成本估算

| 数据类型 | 数量 | 频率 | 月成�?|
|---------|------|------|--------|
| OHLCV数据 | 4000�?| �?| ¥5,000 |
| 财务数据 | 4000�?| �?| ¥2,000 |
| 因子数据 | 87�?| �?| ¥3,000 |
| 新闻数据 | 全市�?| 实时 | ¥2,000 |
| 宏观数据 | 20�?| �?| ¥1,000 |
| **总计** | - | - | **¥13,000** |


## 10. 数据获取时间�?

| 阶段 | 任务 | 时间 |
|------|------|------|
| �?�?| 获取5年历史OHLCV数据 | 2026-03-28 ~ 2026-04-04 |
| �?�?| 获取财务数据和行业数�?| 2026-04-05 ~ 2026-04-11 |
| �?�?| 计算因子数据 | 2026-04-12 ~ 2026-04-18 |
| �?�?| 数据质量检查和优化 | 2026-04-19 ~ 2026-04-25 |


**最后更�?*: 2026-03-28  
**维护�?*: 清风量化系统
