# 数据下载执行清单（2026-07-04 修订版）

> **用途**：两个AI对话分别执行"指令1"和"指令2"，完成数据下载与导入。
> **下载策略**：
> - 指令1（百度云）：正常顺序下载（从最早到最新），空间不足时停止。百度云无配额限制。
> - 指令2（数据源）：从2026-07往前倒着下载，能下载多少下载多少。iFind/QMT有日配额限制。
> **表生命周期**：所有新建表均为临时表，回测完手动删除。

---

## 指令1：百度云网盘下载（AI对话1执行）

### 1.1 任务概述

从bdpan网盘下载**7类分笔成交Tick数据**（大单统计除外）+ 更新基础CSV。

**网盘14个目录状态**：
| # | 网盘目录 | 状态 |
|---|---------|------|
| 1 | A股分钟数据 | ✅已下载 |
| 2 | A股数据 | 重复(与zip)，不下 |
| 3 | A股数据_zip | ✅已下载 |
| 4 | A股数据_分笔成交_指数 | ❌**需下载** |
| 5 | A股数据_分笔数据 | ❌**需下载**(大单统计除外) |
| 6 | 复权因子 | ✅已下载 |
| 7 | 复权因子_tushare | ✅已下载(重复) |
| 8 | 港股_分笔成交 | ❌**需下载** |
| 9 | 基金_分笔成交 | ❌**需下载** |
| 10 | 基金_分钟数据 | ✅已下载 |
| 11 | 可转债_分笔成交 | ❌**需下载** |
| 12 | 上市公司财务信息 | ✅已下载 |
| 13 | 通达信板块_分笔成交 | ❌**需下载** |
| 14 | 新闻文本数据 | ✅已下载 |

### 1.2 下载清单（7类分笔成交 + 基础CSV更新）

#### 分笔成交Tick数据（7类，大单统计除外）

| # | 数据 | 网盘路径 | 导入market_type | 下载策略 |
|---|------|---------|----------------|---------|
| 1 | **A股分笔成交(沪深)** | 量化交易数据/A股数据_分笔数据/分笔成交_按月归档_沪深/ | stock | **正常顺序下载**（从最早到最新），空间不足时停止 |
| 2 | **A股分笔成交(京市)** | 量化交易数据/A股数据_分笔数据/分笔成交_按月归档_京市/ | stock_bj | 全量下载（北交所股票少，数据量小）|
| 3 | **指数分笔成交(沪深京)** | 量化交易数据/A股数据_分笔成交_指数/指数分笔成交_沪深京_按月归档/ | index | 全量下载（数据量小）|
| 4 | **港股分笔成交** | 量化交易数据/港股_分笔成交/港股_分笔成交_按月归档/ | hk | 全量下载 |
| 5 | **ETF分笔成交** | 量化交易数据/基金_分笔成交/ETF分笔成交_按月归档/ | etf | 全量下载 |
| 6 | **LOF分笔成交** | 量化交易数据/基金_分笔成交/LOF分笔成交_按月归档/ | lof | 全量下载 |
| 7 | **可转债分笔成交** | 量化交易数据/可转债_分笔成交/可转债_分笔成交_按月归档/ | cb | 全量下载 |
| 8 | **通达信板块分笔成交** | 量化交易数据/通达信板块_分笔成交/通达信板块_分笔成交_按月归档/ | sector | 全量下载 |
| 9 | **通达信市场统计指数分笔成交** | 量化交易数据/通达信板块_分笔成交/通达信_市场统计指数_分笔成交_按月归档/ | mkt_index | 全量下载 |

> **不下载**：A股数据_分笔数据/分笔成交_大单统计（分笔成交子集，可SQL派生：`WHERE 价×量×100>20万`）

#### 基础CSV更新（网盘附带，可能比数据库更全）

| # | CSV文件 | 网盘路径 | 大小 | 数据库现状 | 操作 |
|---|--------|---------|------|-----------|------|
| 1 | 可转债基础信息列表.csv | 港股_分笔成交目录外 | 510.8KB | convertible_bond_list 1,142行 | 下载对比，如更全则更新 |
| 2 | 指数列表_沪深京.csv | A股数据_分笔成交_指数/ | 51.9KB | index_list 532行 | 下载对比 |
| 3 | ETF基础信息列表.csv | 基金_分笔成交/ | 445KB | etf_list 1,764行 | 下载对比 |
| 4 | ETF基准指数列表.csv | 基金_分笔成交/ | 181.5KB | etf_benchmark 1,492行 | 下载对比 |
| 5 | 港股股票列表.csv | 港股_分笔成交/ | 109.1KB | hk_stock_list 4,688行 | 下载对比 |
| 6 | LOF基金列表.csv | 基金_分笔成交/ | 9.4KB | lof_list 361行 | 下载对比 |
| 7 | 板块信息_通达信.csv | 通达信板块_分笔成交/ | 47.7KB | tdx_sector_info 608行 | 下载对比 |
| 8 | 市场统计指数_通达信.csv | 通达信板块_分笔成交/ | 1.2KB | tdx_market_index 50行 | 下载对比 |

> 这些CSV很小（合计~1.3MB），全部下载，与数据库对比后更新更全的。

### 1.3 前置准备：新建ClickHouse表

> **设计**：统一用 `tick_history` 一张表，`market_type` 字段区分市场。临时表，回测完手动删除。
> **注意**：TTL枚举值问题待确认（见独立指令），暂不加ClickHouse TTL表达式。

```sql
CREATE TABLE IF NOT EXISTS c1_market.tick_history (
    trade_date Date COMMENT '交易日期',
    timestamp DateTime COMMENT '时间戳(3秒粒度)',
    symbol String COMMENT '证券代码',
    market_type LowCardinality(String) COMMENT '市场类型(stock/stock_bj/index/hk/etf/lof/cb/sector/mkt_index)',
    price Decimal(18,4) COMMENT '成交价',
    volume UInt64 COMMENT '成交量(股)',
    amount Decimal(18,2) COMMENT '成交额(元)',
    direction LowCardinality(String) COMMENT '买卖方向(买盘/卖盘/中性盘)',
    data_source LowCardinality(String) DEFAULT 'bdpan',
    INDEX idx_ts timestamp TYPE minmax GRANULARITY 1
) ENGINE = MergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (market_type, symbol, trade_date, timestamp)
SETTINGS index_granularity = 8192
COMMENT '历史3秒Tick分笔成交(回测临时用,手动删除,bdpan导入)';
```

### 1.4 数据格式与字段映射

**分笔成交CSV格式**（实测样本）：
```csv
时间,成交价,手数,买卖方向
2026-07-01 09:15:00,10.05,0,
2026-07-01 09:15:03,10.06,5,买盘
```

**字段映射**（CSV → tick_history表）：

| CSV字段 | 表字段 | 转换规则 |
|---------|--------|---------|
| 时间 (2026-07-01 09:15:00) | trade_date + timestamp | trade_date=toDate(时间), timestamp=时间 |
| 成交价 (10.05) | price | 直接映射 |
| 手数 (5) | volume | 手数 × 100 |
| (计算) | amount | 成交价 × 手数 × 100 |
| 买卖方向 | direction | 直接映射，空值填"中性盘" |
| CSV文件名 (000001.csv) | symbol | 文件名去掉.csv |
| (按数据来源设置) | market_type | stock/stock_bj/index/hk/etf/lof/cb/sector/mkt_index |
| (固定) | data_source | 'bdpan' |

### 1.5 下载与导入策略

#### A股分笔成交(沪深) — 正常顺序下载

**原因**：百度云无配额限制，正常顺序下载（从最早到最新），空间不足时停止。

**月份顺序列表**（从最早开始）：
```
2000-06, 2000-07, ..., 2000-12,
2001-01, ..., 2001-12,
...
2026-01, ..., 2026-07
（从最早到最新，空间不足时停止）
```

**每月流程**：
1. `bdpan ls` 列出月份目录内所有日zip
2. 逐个下载日zip到本地
3. 解压 → 合并CSV为TSV（添加symbol/market_type列）
4. `clickhouse-client` 导入TSV
5. **删除本地zip和TSV**（释放空间）
6. 验证行数
7. 检查D盘空间，不足50GB时停止

#### 其他6类分笔成交 — 全量下载

**原因**：数据量较小（合计<30GB），全量下载。

**流程**：同上，但无需空间检查，从最早月份开始往后下载。

#### 基础CSV — 下载对比

下载8个CSV文件，与数据库对比，更全的则更新。

### 1.6 导入脚本框架

> **参考**：`d:\ZephyrAlpha\tmp\_import_5min.py`（K线导入脚本）
> **需新建**：`d:\ZephyrAlpha\tmp\_import_tick.py`

**核心函数**：
```python
def process_month(year_month, market_type, bdpan_path):
    """处理一个月的分笔成交数据"""
    # 1. bdpan ls 列出日zip
    # 2. 逐个下载日zip
    # 3. 解压 → 合并TSV
    # 4. 导入ClickHouse
    # 5. 删除本地zip/TSV
    # 6. 验证行数
    # 7. 检查磁盘空间
```

### 1.7 验证方法

```sql
-- 各市场类型行数
SELECT market_type, count(), uniq(symbol), min(trade_date), max(trade_date)
FROM c1_market.tick_history
GROUP BY market_type;

-- 验证某天数据
SELECT count() FROM c1_market.tick_history
WHERE trade_date = '2026-07-01' AND market_type = 'stock';
```

### 1.8 空间管理

- D盘仅300GB可用（460GB - 100GB预留）
- 每月zip约1-2GB，TSV约6-12GB
- **逐月下载→导入→删除**，不堆积
- 定期检查：`Get-PSDrive D`
- 空间<50GB时暂停A股沪深分笔成交下载

### 1.9 执行顺序

1. 建表（tick_history）
2. 先下载小数据（指数/港股/ETF/LOF/可转债/板块/京市），验证流程
3. 再下载A股沪深分笔成交（从最早到最新正常顺序下载，空间不足时停止）
4. 下载基础CSV，对比更新
5. 全部完成后更新文档

---

## 指令2：数据源下载13类缺失数据（AI对话2执行）

### 2.1 任务概述

从iFind/QMT/AKShare/TickFlow获取**13类缺失数据**。

> **现状**：iFind/QMT获取脚本均未实现，AKShare仅实现K线。需新建获取脚本。
> **下载策略**：从2026-07往前倒着下载，能下载多少下载多少。

### 2.2 完整数据清单（13类）

| # | 数据类型 | 目标表 | 获取方式 | 时间策略 | 优先级 | 状态 |
|---|---------|--------|---------|---------|--------|------|
| 1 | 估值PE/PB | daily_valuation(已有) | iFind THS_BasicData | 从2026-07往前，每年一批 | P0 | 补数据 |
| 2 | 资金流向 | money_flow(已有) | iFind i问财 | 从2026-07往前 | P0 | 重建 |
| 3 | 龙虎榜 | dragon_tiger(新建) | iFind i问财 | 从2026-07往前 | P1 | 新建 |
| 4 | 融资融券 | margin_trading(新建) | iFind i问财 | 从2026-07往前 | P1 | 新建 |
| 5 | 大宗交易 | block_trade(新建) | iFind i问财 | 从2026-07往前 | P1 | 新建 |
| 6 | 沪深港通资金 | hk_connect_flow(新建) | iFind(试用不可用) | — | P2 | 暂不执行 |
| 7 | 行业分类 | industry_class(新建) | iFind THS_DataPool | 全量(静态) | P1 | 新建 |
| 8 | 指数成分股 | index_constituent(新建) | iFind THS_DataPool | 从2026-07往前 | P1 | 新建 |
| 9 | 期货行情K线 | futures_kline(新建) | QMT xtquant | 从2026-07往前，能下多少下多少 | P1 | 新建 |
| 10 | 美股指数 | us_index(新建) | TickFlow ETF替代 | 从2026-07往前 | P1 | 新建 |
| 11 | 港股日K线 | hk_daily_kline(新建) | QMT xtquant | 从2026-07往前，能下多少下多少 | P1 | 新建 |
| 12 | 宏观经济 | macro_data(新建) | AKShare | 全量历史 | P1 | 新建 |
| 13 | 分析师预期 | analyst_forecast(新建) | AKShare | 从2026-07往前 | P1 | 新建 |

> **补充说明**：
> - #6 沪深港通资金：iFind试用账号不可用(-4001)，需正式账号，本次暂不执行
> - #10 美股指数：TickFlow免费源无真实指数，用ETF替代(SPY/DIA/QQQ)

### 2.3 详细获取方法

#### #1 估值PE/PB → daily_valuation（P0，已有表补数据）

- **API**：iFind `THS_BasicData('600000.SH', 'ths_pe_stock;ths_pb_stock', '2025-06-30,100;2025-06-30,100')`
- **当前状态**：7,934,378行/3,943股/截至2025-11-11
- **目标**：5,876只股票全量，从2026-07往前倒着下载
- **限制**：iFind试用5min限1年，分批下载
- **脚本**：需新建 `tmp/_fetch_valuation.py`

#### #2 资金流向 → money_flow（P0，全量重建）

- **API**：iFind i问财 `THS_iwencai('主力资金流向')`
- **当前状态**：仅13,200行/98只/2025-04~11
- **目标**：全量重建，从2026-07往前倒着下载
- **脚本**：需新建 `tmp/_fetch_money_flow.py`

#### #3 龙虎榜 → dragon_tiger（P1，新建表）

- **API**：iFind i问财（已验证5536行）
- **策略**：从2026-07往前倒着下载
- **DDL**：
```sql
CREATE TABLE IF NOT EXISTS c1_market.dragon_tiger (
    trade_date Date, symbol String, name String,
    reason String, net_buy Decimal(18,2), buy_amount Decimal(18,2), sell_amount Decimal(18,2),
    data_source LowCardinality(String) DEFAULT 'ifind'
) ENGINE = MergeTree PARTITION BY toYYYYMM(trade_date) ORDER BY (trade_date, symbol);
```

#### #4 融资融券 → margin_trading（P1，新建表）

- **API**：iFind i问财（已验证10行）
- **策略**：从2026-07往前倒着下载
- **DDL**：
```sql
CREATE TABLE IF NOT EXISTS c1_market.margin_trading (
    trade_date Date, symbol String,
    margin_balance Decimal(18,2), margin_buy Decimal(18,2), margin_repay Decimal(18,2),
    short_balance Decimal(18,2),
    data_source LowCardinality(String) DEFAULT 'ifind'
) ENGINE = MergeTree PARTITION BY toYYYYMM(trade_date) ORDER BY (trade_date, symbol);
```

#### #5 大宗交易 → block_trade（P1，新建表）

- **API**：iFind i问财（已验证1340行）
- **策略**：从2026-07往前倒着下载
- **DDL**：
```sql
CREATE TABLE IF NOT EXISTS c1_market.block_trade (
    trade_date Date, symbol String,
    price Decimal(18,4), volume UInt64, amount Decimal(18,2),
    buyer String, seller String,
    data_source LowCardinality(String) DEFAULT 'ifind'
) ENGINE = MergeTree PARTITION BY toYYYYMM(trade_date) ORDER BY (trade_date, symbol);
```

#### #6 沪深港通资金 → hk_connect_flow（P2，暂不执行）

- **API**：iFind i问财（试用不可用-4001，需正式账号或淘宝）
- **状态**：本次暂不执行

#### #7 行业分类 → industry_class（P1，新建表）

- **API**：iFind `THS_DataPool`（已验证30行申万行业）
- **策略**：全量（静态数据，无时间范围）
- **DDL**：
```sql
CREATE TABLE IF NOT EXISTS c1_market.industry_class (
    symbol String, industry_sw String, industry_zsi String,
    industry_level UInt8,
    data_source LowCardinality(String) DEFAULT 'ifind'
) ENGINE = MergeTree ORDER BY (symbol);
```

#### #8 指数成分股 → index_constituent（P1，新建表）

- **API**：iFind `THS_DataPool`（已验证300行沪深300成分）
- **策略**：从2026-07往前倒着下载（成分变动历史）
- **DDL**：
```sql
CREATE TABLE IF NOT EXISTS c1_market.index_constituent (
    trade_date Date, index_code String, symbol String,
    weight Decimal(8,4), action String,
    data_source LowCardinality(String) DEFAULT 'ifind'
) ENGINE = MergeTree PARTITION BY toYYYYMM(trade_date) ORDER BY (index_code, trade_date);
```

#### #9 期货行情K线 → futures_kline（P1，新建表）

- **API**：QMT `xtquant`（已验证上期所6982/大商所9559/郑商所7281/中金所88）
- **QMT配置三要素**：
  ```python
  sys.path.append(r'D:\国金证券QMT交易端\bin.x64\Lib\site-packages')
  os.chdir(r'D:\国金证券QMT交易端\bin.x64')
  # 禁止修改xtdata.data_dir
  # 必须用py -3.11运行
  ```
- **策略**：从2026-07往前倒着下载日K线，能下多少下多少
- **DDL**：
```sql
CREATE TABLE IF NOT EXISTS c1_market.futures_kline (
    trade_date Date, timestamp DateTime, symbol String,
    open Decimal(18,4), high Decimal(18,4), low Decimal(18,4), close Decimal(18,4),
    volume UInt64, amount Decimal(18,2), open_interest UInt64,
    period String,
    data_source LowCardinality(String) DEFAULT 'qmt'
) ENGINE = MergeTree PARTITION BY toYYYYMM(trade_date) ORDER BY (symbol, period, trade_date);
```

#### #10 美股指数 → us_index（P1，新建表）

- **API**：TickFlow（免费，无Key，`SPY.US/DIA.US/QQQ.US`已验证）
- **策略**：从2026-07往前倒着下载（用ETF替代真实指数）
- **DDL**：
```sql
CREATE TABLE IF NOT EXISTS c1_market.us_index (
    trade_date Date, symbol String,
    open Decimal(18,4), high Decimal(18,4), low Decimal(18,4), close Decimal(18,4),
    volume UInt64,
    data_source LowCardinality(String) DEFAULT 'tickflow'
) ENGINE = MergeTree PARTITION BY toYYYYMM(trade_date) ORDER BY (symbol, trade_date);
```

#### #11 港股日K线 → hk_daily_kline（P1，新建表）

- **API**：QMT `xtquant`（已验证957只港股）
- **策略**：从2026-07往前倒着下载，能下多少下多少
- **DDL**：
```sql
CREATE TABLE IF NOT EXISTS c1_market.hk_daily_kline (
    trade_date Date, symbol String, name String,
    open Decimal(18,4), high Decimal(18,4), low Decimal(18,4), close Decimal(18,4),
    volume UInt64, amount Decimal(18,2),
    data_source LowCardinality(String) DEFAULT 'qmt'
) ENGINE = MergeTree PARTITION BY toYYYYMM(trade_date) ORDER BY (symbol, trade_date);
```

#### #12 宏观经济 → macro_data（P1，新建表）

- **API**：AKShare（已验证9/10通过）
  ```python
  # 使用时必须断开VPN
  ak.macro_china_gdp()  # GDP
  ak.macro_china_cpi()  # CPI
  ak.macro_china_pmi()  # PMI
  ak.macro_china_money_supply()  # M2
  ```
- **策略**：全量历史（数据量小）
- **DDL**：
```sql
CREATE TABLE IF NOT EXISTS c1_market.macro_data (
    report_date Date, indicator_name String, indicator_value Decimal(18,4),
    unit String, frequency String,
    data_source LowCardinality(String) DEFAULT 'akshare'
) ENGINE = MergeTree PARTITION BY toYYYYMM(report_date) ORDER BY (indicator_name, report_date);
```

#### #13 分析师预期 → analyst_forecast（P1，新建表）

- **API**：AKShare `stock_profit_forecast_ths`（已验证一致预期EPS）
- **策略**：从2026-07往前倒着下载
- **DDL**：
```sql
CREATE TABLE IF NOT EXISTS c1_market.analyst_forecast (
    report_date Date, symbol String,
    forecast_year String, forecast_eps Decimal(18,4), forecast_pe Decimal(18,4),
    rating String, analyst_count UInt16,
    data_source LowCardinality(String) DEFAULT 'akshare'
) ENGINE = MergeTree PARTITION BY toYYYYMM(report_date) ORDER BY (symbol, report_date);
```

### 2.4 执行顺序

1. **P0优先**：#1估值 + #2资金流（已有表，补数据/重建）
2. **P1 iFind批**：#3龙虎榜 + #4融资融券 + #5大宗交易 + #7行业分类 + #8指数成分股
3. **P1 QMT批**：#9期货K线 + #11港股日K线（需QMT环境，py -3.11）
4. **P1免费源**：#10美股指数(TickFlow) + #12宏观(AKShare) + #13分析师预期(AKShare)
5. **P2暂不执行**：#6沪深港通资金（需iFind正式账号）

### 2.5 验证方法

```sql
-- 每类数据验证
SELECT count(), min(trade_date), max(trade_date), uniq(symbol)
FROM c1_market.<table_name>;
```

### 2.6 完成后更新文档

- `data_acquisition_plan.md`（§2.1表数 + §2.3未建表状态）
- `data_source_capability_map.md`（§5.6数据库填充状态）

---

## 附录：环境配置

### bdpan CLI
```bash
# WSL /root/.local/bin/bdpan
/root/.local/bin/bdpan ls '量化交易数据/...'
/root/.local/bin/bdpan download '网盘路径' '本地路径'
```

### ClickHouse
```bash
wsl -d Ubuntu -- clickhouse-client --query "SQL"
# 数据库: c1_market, host=localhost port=9000 user=default
```

### iFind
```python
# 试用账号: werty017
# 限制: 5min限1年/EDB月度配额/CFFEX拒绝
from iFinDPy import *
THS_iFinDLogin('werty017', 'xxx')
```

### QMT
```python
# 必须用py -3.11运行
sys.path.append(r'D:\国金证券QMT交易端\bin.x64\Lib\site-packages')
os.chdir(r'D:\国金证券QMT交易端\bin.x64')
from xtquant import xtdata
```

### AKShare
```python
# 使用时必须断开VPN
import akshare as ak
```

### TickFlow
```python
# 纯免费无Key Python库
# 已验证: SPY.US/DIA.US/QQQ.US 12/12通过
```
