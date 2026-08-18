---
ttl: permanent
doc_type: architecture_view
title: 数据源集成与下载机制 / Data Sources
owner: ZephyrAlpha-Owner
language: zh
---

# 04 · 数据源集成与下载机制

> 大白话项目现状。数据源 + 任务清单 + 七大韧性机制 + AUTO 任务计数。

## 1. 模块定位

**位置**：`src/zephyr/data/` | **CLI**：`integrator` | **蓝图**：MOD-L00-004

统一管理多数据源（miniQMT / AKShare / tushare 等）的自动下载、调度与 ClickHouse 持久化。

**数据流**：`CLI → get_integrator() → IntegratorScheduler → IngestProviderBase providers → ch_writer.write_result() → ClickHouse`

## 2. 数据源清单

| Provider | 数据源 | 用途 |
|----------|--------|------|
| miniQMT | 迅投 QMT | 实时行情/持仓（fallback） |
| AKShare | 开源金融数据 | 演示/回退（免费） |
| tushare | 新闻/基本面/行业分类（积分制） | 免费源主力 |

> iFind（同花顺）已于 2026-08-14 全项目退役删除（#ARCH-DATA-IFIND-RETIRE-001），能力已全部迁移免费源，留痕见 `data_sources_registry.yaml` DS-IFIND（deprecated）。

> 真源：`architecture_model/data/data_sources_registry.yaml`（规则数据，改后 `sync_yaml_to_depgraph.py` 同步到 DB）。

## 3. 任务清单结构

`src/zephyr/data/config/tasks.yaml`（或 `architecture_model/data/data_sources_registry.yaml`）定义任务，每个任务声明 `task_id/table/source/schedule/incremental/dependencies/capability`。调度由 `IntegratorScheduler`（APScheduler BackgroundScheduler，5 cron 时段 + DAG 依赖 + 断点续传）编排。

## 4. 七大韧性机制

| 机制 | 说明 |
|------|------|
| Provider 抽象 | `IngestProviderBase` 策略注入（connect/health_check/fetch/disconnect） |
| 限流与重试 | per-source 策略 |
| 断点续传 | `ProgressStore` 记录进度 |
| 熔断 | 失败累积触发熔断 + fallback 源 |
| 质量门 | `quality_gate` 字段断言（PIT/Schema/Range） |
| 去重与幂等写入 | `ch_writer` 攒批 + 去重 |
| 回填与巡检 | `backfill_checker` + `integrity_checker` |

告警：`Alerter`（飞书 webhook / SMTP，已修复中文主机名 SMTP 静默失败）。

## 5. 调度机制

事件驱动 + 定时混合：盘中实时（intraday_realtime，如港股 K 线/期货持仓）+ 盘后批量。Windows 计划任务 `ZephyrAlpha_DataScheduler`（AtStartup，SYSTEM）守护。

## 6. 任务计数

<!-- AUTO-START:task_counts -->
<!-- 数据源：data_sources_registry.yaml | 最后同步：2026-08-17 -->

| Provider ID | 名称 | 类型 | 状态 |
|-------------|------|------|------|
| `DS-IFIND` | 同花顺iFind | commercial | deprecated |
| `DS-MINIQMT` | miniQMT | commercial | active |
| `DS-AKSHARE` | AKShare | open_source | active |
| `DS-BAOSTOCK` | Baostock | open_source | active |
| `DS-TUSHARE` | Tushare | commercial | active |
| `DS-TICKFLOW` | TickFlow | open_source | active |
| `DS-TDX` | 通达信 | open_source | active |
| `DS-RSS` | RSS | open_source | active |
| `DS-CLS` | 财联社电报 | open_source | active |
| `DS-EASTMONEY_NEWS` | 东方财富新闻 | open_source | active |
| `DS-BAIDUYUN` | 百度云 | commercial | active |
| `DS-NEWSAPI` | NewsAPI | commercial | planned |
| `DS-YFINANCE` | yfinance | open_source | deprecated |
| `DS-STOOQ` | Stooq | open_source | deprecated |
| `DS-TQCENTER` | tqcenter | commercial | active |
| `DS-FRED` | FRED/世界银行 宏观数据 | open_source | active |
| `DS-EIA` | EIA 能源数据 | open_source | active |
| `DS-QWEATHER` | 和风天气 | open_source | active |
| **合计 / Total providers** | | | **18** |
<!-- AUTO-END:task_counts -->

## 7. CLI 子命令

```bash
integrator status [task_id]              # 今日任务 / 单任务详情
integrator list [--source <src>]          # 列出任务
integrator run <task_id>                  # 手动触发单任务
integrator rerun-failed                   # 重跑今日失败
integrator pause <source> | resume <source>
integrator start                          # 启动常驻调度
integrator speed-test [--source] [--capability]
```
