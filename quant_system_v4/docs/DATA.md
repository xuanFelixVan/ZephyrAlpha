# DATA.md - 数据规格

> **版本**：v4.0
> **日期**：2026-03-28
> **状态**：设计阶段

---

## 1. 数据类型

| 类型 | 说明 | 更新频率 | 存储 |
|------|------|----------|------|
| 日线数据 | OHLCV | 每日收盘后 | SQLite + Parquet |
| 分钟数据 | 1/5/15/30/60分钟 | 每日收盘后 | Parquet |
| Tick数据 | 逐笔交易 | 盘中实时 | Parquet |
| 财务数据 | 财报、指标 | 季度 | SQLite |
| 因子数据 | 因子值 | 每日计算 | Parquet |
| 信号数据 | 策略信号 | 每日 | SQLite |
| 订单数据 | 交易订单 | 实时 | SQLite |
| 回测结果 | 回测绩效 | 按需 | SQLite |

---

## 2. 数据存储结构

```
data/
├── raw/                          # 原始数据（Parquet）
│   └── {data_type}/
│       └── {year}/
│           └── {month}/
│               └── {date}.parquet
│
├── processed/                    # 处理后数据
│   ├── daily_price.parquet      # 日线行情
│   ├── minute_{period}.parquet  # 分钟行情
│   └── financial.parquet        # 财务数据
│
├── factors/                      # 因子数据
│   └── {factor_id}/
│       └── {year}/
│           └── {factor_id}_{date}.parquet
│
├── signals/                     # 信号数据
│   └── {date}_signals.parquet
│
├── orders/                      # 订单数据
│   └── {date}_orders.parquet
│
├── backtest_results/            # 回测结果
│   └── {strategy_id}/
│       └── {backtest_id}/
│
└── quant.db                    # SQLite元数据库
```

---

## 3. 数据字典

### 3.1 日线数据 (daily_price)

| 字段 | 类型 | 说明 |
|------|------|------|
| date | DATE | 交易日期 |
| code | VARCHAR | 股票代码 |
| open | FLOAT | 开盘价 |
| high | FLOAT | 最高价 |
| low | FLOAT | 最低价 |
| close | FLOAT | 收盘价 |
| volume | FLOAT | 成交量 |
| amount | FLOAT | 成交额 |
| change | FLOAT | 涨跌幅 |
| turnover | FLOAT | 换手率 |
| pe | FLOAT | 市盈率 |
| pb | FLOAT | 市净率 |

### 3.2 因子数据 (factor_data)

| 字段 | 类型 | 说明 |
|------|------|------|
| date | DATE | 日期 |
| code | VARCHAR | 股票代码 |
| factor_id | VARCHAR | 因子ID |
| value | FLOAT | 因子值 |
| rank | INT | 因子排名 |

### 3.3 信号数据 (signal_data)

| 字段 | 类型 | 说明 |
|------|------|------|
| signal_id | VARCHAR | 信号ID |
| date | DATE | 日期 |
| strategy_id | VARCHAR | 策略ID |
| code | VARCHAR | 股票代码 |
| direction | VARCHAR | 方向 long/short |
| strength | FLOAT | 强度 0-1 |
| price | FLOAT | 信号价格 |
| status | VARCHAR | 状态 |

---

## 4. 数据源规格

### 4.1 AkShare

```yaml
akshare:
  stocks:
    daily: "stock_zh_a_hist"
    minute: "stock_zh_a_minute"
    realtime: "stock_zh_a_spot_em"
  indices:
    daily: "index_zh_a_hist"
  futures:
    daily: "futures_zh_hist"
```

### 4.2 Tushare

```yaml
tushare:
  stocks:
    daily: "daily"
    financial: " fina_indicator"
  indices:
    daily: "index_daily"
```

---

## 5. 数据质量标准

| 标准 | 要求 |
|------|------|
| 完整性 | 缺失率 < 1% |
| 准确性 | 错误率 < 0.1% |
| 时效性 | 更新延迟 < 1小时 |
| 一致性 | 跨数据源一致 |

---

## 6. 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v4.0 | 2026-03-28 | 初始版本，数据规格设计 |
