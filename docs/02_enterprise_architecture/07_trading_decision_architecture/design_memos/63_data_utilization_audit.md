---
ttl: permanent
doc_type: architecture_view
title: 数据利用审计
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.1.0"
date: 2026-08-10
topic: data_utilization_audit
scope: 07_trading_decision_architecture
---

# 数据利用审计

> **性质**：design_memo / 审查底稿。审计数据下载体系产出的数据被消费层利用的情况，识别闲置表和数据缺口。
> **配套**：[64_data_source_download_spec.md](64_data_source_download_spec.md)（数据源与下载体系规范——64 号审"数据下得怎么样"，本文审"数据用得怎么样"）

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G29 数据利用审计（跨切治理层·6x 段位） |
| 依赖 | 64_data_source_download_spec（数据下载产出是审计输入） |
| 正交性 | ✅ 纯审计，不修改下载/消费逻辑 |
| 优先级 | P2（先有64号下载规范，再审计利用情况） |
| 状态 | 🟧 draft v0.1.0（43张闲置表已识别，施工计划待讨论） |

## 2. 审计范围

- ClickHouse c1_market / c3_fundamental / c0_meta 三库共 ~100 表
- 审计维度：表是否被代码消费（rg 搜索 SELECT 引用）/ 表是否有数据（行数检测）/ 表是否在 tasks.yaml 有采集任务

## 3. 闲置表清单（43张）

> 待补充完整清单。v0.1.0 落档时已识别43张闲置表，分三类：
> - **有数据无消费**：表有数据但代码无 SELECT 引用
> - **有消费无数据**：代码有引用但表为空（如 iFind 配额耗尽的 edb_data）
> - **无任务无数据**：tasks.yaml 无采集任务且表为空

## 4. 施工计划

> 待讨论定夺后补充。

## 5. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-10 | 0.1.0 | 初稿 | 43张闲置表已识别，审查底稿落档。**注意**：本文件曾因未 git commit 丢失，后从引用记录重建骨架 |
