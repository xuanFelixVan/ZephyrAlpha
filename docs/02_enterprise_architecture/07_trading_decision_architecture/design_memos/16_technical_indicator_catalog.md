---
ttl: permanent
doc_type: architecture_view
title: 技术指标目录
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.1.0"
date: 2026-08-10
topic: technical_indicator_catalog
scope: 07_trading_decision_architecture
---

# 技术指标目录

> **性质**：architecture_view / 骨架清单文档。记录系统支持的所有传统技术指标（MA/MACD/KDJ/RSI/BOLL 等）的目录、计算规范和周期覆盖。
> **代码真源**：`src/zephyr/factor/technical_indicators/` + `schemas/categories/market_technical_indicator.py`

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G01 数据与特征层（地基层·1x 段位） |
| 依赖 | 15_data_feature_layer_spec（特征层规范） |
| 正交性 | ✅ 纯数据计算，与 regime/alpha/组合/风控正交 |
| 优先级 | P1（技术指标是因子工程和策略层的基础输入） |
| 状态 | 🟧 draft v0.1.0（骨架清单，内容待补充完整） |

## 2. 技术指标计算规范

- 传统技术指标（MA/MACD/KDJ/RSI/BOLL 等）全部基于 OHLCV K 线计算
- 覆盖 1min~月线 9 个周期（1min/5min/15min/30min/60min/120min/日/周/月）
- 其中 120min 周期通过 60min K 线两根聚合生成

## 3. 技术指标存储架构

- 采用单表设计，新增 period 列区分 9 个周期
- 按 (period, toYYYYMM(trade_date)) 分区
- 新增 trade_time 列解决日内多根 K 线去重问题
- ORDER BY (symbol, period, trade_time) 确保与 K 线表对齐

## 4. 调度策略

- 增量调度（technical_indicator_incremental）：每日盘后处理日线周期数据
- 全量回算（technical_indicator_full_refresh）：周末执行，覆盖所有 9 个周期数据

## 5. 三级时间框架栈映射

| 层级 | 周期 | 用途 | 指标组合 |
|---|---|---|---|
| 趋势层 | 月线/周线 | 大趋势判断 | MA/MACD |
| 交易层 | 日线 | 交易信号 | KDJ/RSI/MACD |
| 入场层 | 60min/30min | 精准入场 | BOLL/RSI |
| 微调层 | 15min/5min | 微调时机 | KDJ/RSI |
| 剥头皮 | 1min | 超短线 | MA/VOL |

## 6. 指标清单

> 待补充完整指标清单（MA/MACD/KDJ/RSI/BOLL/ATR/OBV 等），每项含计算公式/参数/周期覆盖/存储字段。

## 7. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-10 | 0.1.0 | 初稿骨架 | 技术指标目录文档。**注意**：本文件曾因未 git commit 丢失，后从代码引用和 architecture_issue_registry 描述重建骨架 |
