---
ttl: permanent
doc_type: architecture_view
title: 技术指标施工计划
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.1.0"
date: 2026-08-10
topic: technical_indicator_build_plan
scope: 07_trading_decision_architecture
---

# 技术指标施工计划

> **性质**：architecture_view / 施工计划。技术指标落地的施工步骤与验证计划。
> **配套**：[16_technical_indicator_catalog.md](16_technical_indicator_catalog.md)（指标目录——what，本文是 how）

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G01 数据与特征层（地基层·1x 段位） |
| 依赖 | 16_technical_indicator_catalog（指标目录） |
| 状态 | 🟧 draft v0.1.0（骨架，§3-§4 待补充） |

## 2. 施工范围

覆盖传统技术指标（MA/MACD/KDJ/RSI/BOLL/ATR/OBV 等）的：
- 计算逻辑实现（`src/zephyr/factor/technical_indicators/`）
- 存储表设计（ClickHouse 单表 + period 列）
- 调度任务（增量 + 全量回算）
- 验证测试（`tests/zephyr/factor/technical_indicators/`）

## 3. 施工步骤

> 待补充完整施工步骤。

## 4. 验证计划

> 待补充完整验证计划。

## 5. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-10 | 0.1.0 | 初稿骨架 | 施工计划骨架。**注意**：本文件曾因未 git commit 丢失，后从代码引用重建骨架 |
