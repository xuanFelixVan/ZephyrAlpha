---
module_id: UX_DOC_001
version: 0.1.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构师
standard_type: 专业量化机构文档
applicable_scope: 全系统
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 进行中
---


# NozyIO可视化编辑系统（归档）

> **状态**: ❌ 已归档
> **原因**: 可视化编辑器是巨大工程，单人不切实际
> **索引**: `ARC_002`


## 原设计概述

原计划设计一个类似Node-RED的可视化量化策略编辑器，支持拖拽式策略构建。


## 归档原因

| 问题 | 说明 |
|------|------|
| 工程量 | 可视化编辑器需要2-3个月专职开发 |
| 复杂度 | 状态管理、组件库、编辑器核心都是大坑 |
| 实际价值 | 核心是策略有效性，不是编辑器 |


## 替代方案

| 需求 | 推荐方案 |
|------|----------|
| 策略可视化 | 使用Grafana仪表板 |
| 流程可视化 | 使用Mermaid图表 |
| 数据可视化 | 使用Plotly/ECharts |
| 策略编辑 | 使用Jupyter Notebook |


## 实际建议

与其开发可视化编辑器，不如：

1. **专注策略有效性** - 好策略不需要可视化编辑器
2. **使用成熟工具** - Grafana + Jupyter足够
3. **渐进式改进** - 等系统产生稳定收益后再考虑UI


## 归档位置

如有需要，可在 `docs/06_ARCHIVE/` 中找到原始设计文档。


**维护者**: 清风量化系统
**状态**: 已归档
**归档时间**: 2026-03-28
