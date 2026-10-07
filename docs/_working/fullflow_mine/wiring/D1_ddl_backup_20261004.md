---
ttl: task_bound
title: "D1 净删批A CH表DDL存档（删前SHOW CREATE全量+行数）"
owner: st-datasop-20260930
language: zh
status: active
version: "1.0.0"
date: 2026-10-04
created: 2026-10-04
---

# D1 DDL 备份（原定 .sql 名，因 DIRECTORY-CONTRACT docs/_working 仅许 md/csv/yaml/html 改存 .md，内容零改动）

-- D1_ddl_backup_20261004.sql
-- EXEC-D1 net-deletion batch 0-1: CH backup/quarantine tables DROP pre-archive
-- Ruling: Owner-approved net deletion 2026-10-04 (verbal ruling, batch 0-1/0-2/0-4)
-- Session: st-datasop-20260930 | Database: c1_market
-- NOTE: index_valuation_daily_quar_20260920 already absent (dropped elsewhere), skipped.
## ===== kline_daily_hfq_legacy_20260924 | rows_at_drop_time = 8426036 =====

```sql
CREATE TABLE c1_market.kline_daily_hfq_legacy_20260924
(
    `trade_date` Date,
    `symbol` String,
    `open` Decimal(18, 4),
    `close` Decimal(18, 4),
    `high` Decimal(18, 4),
    `low` Decimal(18, 4),
    `volume` UInt64,
    `amount` Decimal(18, 2),
    `amplitude` Decimal(18, 4) DEFAULT 0,
    `pct_change` Decimal(18, 4) DEFAULT 0,
    `change` Decimal(18, 4) DEFAULT 0,
    `turnover` Decimal(18, 4) DEFAULT 0,
    `data_source` LowCardinality(String) DEFAULT 'bdpan_hfq',
    `ingest_ts` DateTime64(3, 'UTC') DEFAULT now(),
    `exchange` LowCardinality(String) MATERIALIZED multiIf((substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 3) IN ('110', '113', '204', '900', '901', '902', '903')), 'SH', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 3) IN ('123', '128')), 'SZ', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 2) IN ('43', '83', '87', '92', '93', '94')), 'BJ', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 1) IN ('4', '8')), 'BJ', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 1) IN ('5', '6', '9')), 'SH', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 1) IN ('0', '1', '2', '3')), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    `symbol_canonical` String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date)
SETTINGS index_granularity = 8192;
```
## ===== kline_daily_hfq_preversion_20260925 | rows_at_drop_time = 10079242 =====

```sql
CREATE TABLE c1_market.kline_daily_hfq_preversion_20260925
(
    `trade_date` Date,
    `symbol` String,
    `open` Decimal(18, 4),
    `close` Decimal(18, 4),
    `high` Decimal(18, 4),
    `low` Decimal(18, 4),
    `volume` UInt64,
    `amount` Decimal(18, 2),
    `amplitude` Decimal(18, 4) DEFAULT 0,
    `pct_change` Decimal(18, 4) DEFAULT 0,
    `change` Decimal(18, 4) DEFAULT 0,
    `turnover` Decimal(18, 4) DEFAULT 0,
    `data_source` LowCardinality(String) DEFAULT 'bdpan_hfq',
    `ingest_ts` DateTime64(3, 'UTC') DEFAULT now(),
    `exchange` LowCardinality(String) MATERIALIZED multiIf((substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 3) IN ('110', '113', '204', '900', '901', '902', '903')), 'SH', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 3) IN ('123', '128')), 'SZ', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 2) IN ('43', '83', '87', '92', '93', '94')), 'BJ', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 1) IN ('4', '8')), 'BJ', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 1) IN ('5', '6', '9')), 'SH', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 1) IN ('0', '1', '2', '3')), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    `symbol_canonical` String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date)
SETTINGS index_granularity = 8192;
```
## ===== kline_daily_hfq_quarantine_20260925 | rows_at_drop_time = 10475 =====

```sql
CREATE TABLE c1_market.kline_daily_hfq_quarantine_20260925
(
    `trade_date` Date,
    `symbol` String,
    `open` Decimal(18, 4),
    `close` Decimal(18, 4),
    `high` Decimal(18, 4),
    `low` Decimal(18, 4),
    `volume` UInt64,
    `amount` Decimal(18, 2),
    `amplitude` Decimal(18, 4) DEFAULT 0,
    `pct_change` Decimal(18, 4) DEFAULT 0,
    `change` Decimal(18, 4) DEFAULT 0,
    `turnover` Decimal(18, 4) DEFAULT 0,
    `data_source` LowCardinality(String) DEFAULT 'bdpan_hfq',
    `ingest_ts` DateTime64(3, 'UTC') DEFAULT now(),
    `exchange` LowCardinality(String) MATERIALIZED multiIf((substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 3) IN ('110', '113', '204', '900', '901', '902', '903')), 'SH', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 3) IN ('123', '128')), 'SZ', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 2) IN ('43', '83', '87', '92', '93', '94')), 'BJ', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 1) IN ('4', '8')), 'BJ', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 1) IN ('5', '6', '9')), 'SH', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 1) IN ('0', '1', '2', '3')), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    `symbol_canonical` String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date)
SETTINGS index_granularity = 8192;
```
## ===== kline_daily_hfq_recalc | rows_at_drop_time = 100054 =====

```sql
CREATE TABLE c1_market.kline_daily_hfq_recalc
(
    `trade_date` Date,
    `symbol` String,
    `open` Decimal(18, 4),
    `close` Decimal(18, 4),
    `high` Decimal(18, 4),
    `low` Decimal(18, 4),
    `volume` UInt64,
    `amount` Decimal(18, 2),
    `amplitude` Decimal(18, 4) DEFAULT 0,
    `pct_change` Decimal(18, 4) DEFAULT 0,
    `change` Decimal(18, 4) DEFAULT 0,
    `turnover` Decimal(18, 4) DEFAULT 0,
    `data_source` LowCardinality(String) DEFAULT 'bdpan_hfq',
    `ingest_ts` DateTime64(3, 'UTC') DEFAULT now(),
    `exchange` LowCardinality(String) MATERIALIZED multiIf((substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 3) IN ('110', '113', '204', '900', '901', '902', '903')), 'SH', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 3) IN ('123', '128')), 'SZ', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 2) IN ('43', '83', '87', '92', '93', '94')), 'BJ', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 1) IN ('4', '8')), 'BJ', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 1) IN ('5', '6', '9')), 'SH', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 1) IN ('0', '1', '2', '3')), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    `symbol_canonical` String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date)
SETTINGS index_granularity = 8192;
```
## ===== kline_weekly_hfq_legacy_20260924 | rows_at_drop_time = 2127400 =====

```sql
CREATE TABLE c1_market.kline_weekly_hfq_legacy_20260924
(
    `trade_date` Date,
    `symbol` String,
    `open` Decimal(18, 4),
    `close` Decimal(18, 4),
    `high` Decimal(18, 4),
    `low` Decimal(18, 4),
    `volume` UInt64,
    `amount` Decimal(18, 2),
    `amplitude` Decimal(18, 4) DEFAULT 0,
    `pct_change` Decimal(18, 4) DEFAULT 0,
    `change` Decimal(18, 4) DEFAULT 0,
    `turnover` Decimal(18, 4) DEFAULT 0,
    `data_source` LowCardinality(String) DEFAULT 'bdpan_hfq',
    `ingest_ts` DateTime64(3, 'UTC') DEFAULT now(),
    `exchange` LowCardinality(String) MATERIALIZED multiIf((substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 3) IN ('110', '113', '204', '900', '901', '902', '903')), 'SH', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 3) IN ('123', '128')), 'SZ', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 2) IN ('43', '83', '87', '92', '93', '94')), 'BJ', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 1) IN ('4', '8')), 'BJ', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 1) IN ('5', '6', '9')), 'SH', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 1) IN ('0', '1', '2', '3')), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    `symbol_canonical` String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date)
SETTINGS index_granularity = 8192;
```
## ===== kline_weekly_hfq_legacy_r1_20260924 | rows_at_drop_time = 1856391 =====

```sql
CREATE TABLE c1_market.kline_weekly_hfq_legacy_r1_20260924
(
    `trade_date` Date,
    `symbol` String,
    `open` Decimal(18, 4),
    `close` Decimal(18, 4),
    `high` Decimal(18, 4),
    `low` Decimal(18, 4),
    `volume` UInt64,
    `amount` Decimal(18, 2),
    `amplitude` Decimal(18, 4) DEFAULT 0,
    `pct_change` Decimal(18, 4) DEFAULT 0,
    `change` Decimal(18, 4) DEFAULT 0,
    `turnover` Decimal(18, 4) DEFAULT 0,
    `data_source` LowCardinality(String) DEFAULT 'bdpan_hfq',
    `ingest_ts` DateTime64(3, 'UTC') DEFAULT now(),
    `exchange` LowCardinality(String) MATERIALIZED multiIf((substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 3) IN ('110', '113', '204', '900', '901', '902', '903')), 'SH', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 3) IN ('123', '128')), 'SZ', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 2) IN ('43', '83', '87', '92', '93', '94')), 'BJ', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 1) IN ('4', '8')), 'BJ', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 1) IN ('5', '6', '9')), 'SH', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 1) IN ('0', '1', '2', '3')), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    `symbol_canonical` String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date)
SETTINGS index_granularity = 8192;
```
## ===== kline_monthly_hfq_legacy_20260924 | rows_at_drop_time = 502496 =====

```sql
CREATE TABLE c1_market.kline_monthly_hfq_legacy_20260924
(
    `trade_date` Date,
    `symbol` String,
    `open` Decimal(18, 4),
    `close` Decimal(18, 4),
    `high` Decimal(18, 4),
    `low` Decimal(18, 4),
    `volume` UInt64,
    `amount` Decimal(18, 2),
    `amplitude` Decimal(18, 4) DEFAULT 0,
    `pct_change` Decimal(18, 4) DEFAULT 0,
    `change` Decimal(18, 4) DEFAULT 0,
    `turnover` Decimal(18, 4) DEFAULT 0,
    `data_source` LowCardinality(String) DEFAULT 'bdpan_hfq',
    `ingest_ts` DateTime64(3, 'UTC') DEFAULT now(),
    `exchange` LowCardinality(String) MATERIALIZED multiIf((substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 3) IN ('110', '113', '204', '900', '901', '902', '903')), 'SH', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 3) IN ('123', '128')), 'SZ', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 2) IN ('43', '83', '87', '92', '93', '94')), 'BJ', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 1) IN ('4', '8')), 'BJ', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 1) IN ('5', '6', '9')), 'SH', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 1) IN ('0', '1', '2', '3')), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    `symbol_canonical` String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date)
SETTINGS index_granularity = 8192;
```
## ===== kline_monthly_hfq_legacy_r1_20260924 | rows_at_drop_time = 524474 =====

```sql
CREATE TABLE c1_market.kline_monthly_hfq_legacy_r1_20260924
(
    `trade_date` Date,
    `symbol` String,
    `open` Decimal(18, 4),
    `close` Decimal(18, 4),
    `high` Decimal(18, 4),
    `low` Decimal(18, 4),
    `volume` UInt64,
    `amount` Decimal(18, 2),
    `amplitude` Decimal(18, 4) DEFAULT 0,
    `pct_change` Decimal(18, 4) DEFAULT 0,
    `change` Decimal(18, 4) DEFAULT 0,
    `turnover` Decimal(18, 4) DEFAULT 0,
    `data_source` LowCardinality(String) DEFAULT 'bdpan_hfq',
    `ingest_ts` DateTime64(3, 'UTC') DEFAULT now(),
    `exchange` LowCardinality(String) MATERIALIZED multiIf((substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 3) IN ('110', '113', '204', '900', '901', '902', '903')), 'SH', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 3) IN ('123', '128')), 'SZ', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 2) IN ('43', '83', '87', '92', '93', '94')), 'BJ', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 1) IN ('4', '8')), 'BJ', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 1) IN ('5', '6', '9')), 'SH', (substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 1) IN ('0', '1', '2', '3')), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    `symbol_canonical` String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date)
SETTINGS index_granularity = 8192;
```
## ===== _tmp_mat_test | rows_at_drop_time = 0 =====

```sql
CREATE TABLE c1_market._tmp_mat_test
(
    `symbol` String,
    `exchange` LowCardinality(String) MATERIALIZED multiIf((substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), 1, 3) IN ('110', '113')), 'SH', ''),
    `symbol_canonical` String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(symbol, '.', exchange))
)
ENGINE = MergeTree
ORDER BY tuple()
SETTINGS index_granularity = 8192;
```

---

# --- 批B: governance.db 空表 3 张（SQLite DDL 存档，2026-10-04 DROP 前提取） ---

## audit_trail | rows_at_drop_time = 0

```sql
CREATE TABLE audit_trail (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_date TEXT NOT NULL,
    stage TEXT NOT NULL,                    -- raw_event / match_decision / attribution
    event_type TEXT NOT NULL,               -- system_fill / broker_settlement / match_verdict / brinson_result ...
    payload_json TEXT NOT NULL,             -- 事件负载（canonical JSON）
    prev_hash TEXT NOT NULL,                -- 哈希链（首条空串）
    record_hash TEXT NOT NULL UNIQUE,       -- SHA-256 记录指纹
    recorded_at TEXT NOT NULL,              -- UTC ISO8601
    read_only_after TEXT,                   -- 30 天 read-only 触发器口径（到期日，§3.3）
    schema_version TEXT NOT NULL DEFAULT '1.0'
);
```

## costs | rows_at_drop_time = 0

```sql
CREATE TABLE costs (
        cost_id INTEGER PRIMARY KEY AUTOINCREMENT,
        cost_type TEXT NOT NULL,
        amount REAL NOT NULL,
        currency TEXT DEFAULT 'CNY',
        description TEXT,
        recorded_at TEXT NOT NULL,
        session_id TEXT,
        task_id TEXT,
        FOREIGN KEY (task_id) REFERENCES tasks(task_id)
    );
```

## report_archive | rows_at_drop_time = 0

```sql
CREATE TABLE report_archive (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    archive_id TEXT NOT NULL UNIQUE,        -- ARCH-xxxxxxxxxx（ReportPublisher 口径）
    report_id TEXT NOT NULL,                -- 报告逻辑标识
    source TEXT NOT NULL,                   -- ReportSource 枚举值
    report_type TEXT NOT NULL,
    archived_at TEXT NOT NULL,              -- UTC ISO8601
    content_json TEXT NOT NULL,             -- canonical JSON
    content_hash TEXT NOT NULL,             -- SHA-256(content)
    prev_hash TEXT NOT NULL,                -- 哈希链（首条空串）
    record_hash TEXT NOT NULL UNIQUE,       -- SHA-256(链指纹)
    schema_version TEXT NOT NULL DEFAULT '1.0'
);
```
