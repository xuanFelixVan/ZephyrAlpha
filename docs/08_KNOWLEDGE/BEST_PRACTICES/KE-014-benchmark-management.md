---
module_id: KE-014
title: "基准管理系统：业绩对比与归因分析（pyfolio + empyrical）"
category: blueprint_decision
source_file: "docs/01_FRAMEWORK/BENCHMARK_MANAGEMENT_BLUEPRINT.md (deleted in git history)"
extracted_date: "2026-04-16"
version: "1.0.0"
status: Active
layer: L10
owner: ZephyrAlpha-Owner
source_git_deleted: true
original_path: "docs/01_FRAMEWORK/BENCHMARK_MANAGEMENT_BLUEPRINT.md"
deleted_in_commit: "d73e28c0c868b5a5101f01882e76789ed748c830"
recovery_date: "2026-04-16"
---

# 基准管理系统设计

## 核心定位

从 git 历史恢复的文档定义了基准管理系统的完整架构，作为清风量化系统的**业绩对比基准**。

## Module ID
- `BENCHMARK_MANAGEMENT_FRAMEWORK_001`
- Layer 10 (治理与合规层)

## 专业机构参考模型

### 1. Bridgewater Benchmark Management
- **核心特点**: 多基准对比、风险调整收益
- **应用场景**: 组合业绩评估、风险归因

### 2. Citadel Performance Analytics
- **核心特点**: 实时业绩分析、多维度归因
- **应用场景**: 策略绩效评估、风险监控

## 核心职责

### 1. 基准定义
- **基准指数定义**: 定义合适的基准指数
- **基准组合定义**: 定义基准组合构成
- **自定义基准**: 支持用户自定义基准

### 2. 基准对比
- **策略与基准对比**: 对比策略与基准的表现
- **超额收益计算**: 计算超额收益（Alpha）
- **风险调整收益**: 计算风险调整后的收益

### 3. 基准归因
- **基准归因分析**: 分析收益来源
- **收益来源分解**: 分解策略收益来源
- **风险归因**: 分析风险来源

### 4. 基准报告
- **基准报告生成**: 生成基准对比报告
- **报告展示**: 可视化展示对比结果
- **定期报告**: 支持定期生成报告

## 技术选型

### 开源方案

| 项目 | 功能 | 链接 |
|------|------|------|
| **pyfolio** | 基准对比、基准归因、绩效分析 | https://github.com/quantopian/pyfolio |
| **empyrical** | 基准指标计算、风险指标、收益指标 | https://github.com/quantopian/empyrical |

### pyfolio 功能
-  tearsheet 生成
-  收益归因
-  风险分析
-  换手率分析
-  持仓分析

### empyrical 功能
-  夏普比率
-  索提诺比率
-  最大回撤
-  年化收益
-  波动率

## 关键指标

### 收益指标
- **年化收益率**: Annual Return
- **累计收益率**: Cumulative Return
- **超额收益**: Excess Return (vs Benchmark)

### 风险指标
- **波动率**: Volatility
- **最大回撤**: Max Drawdown
- **下行风险**: Downside Risk

### 风险调整指标
- **夏普比率**: Sharpe Ratio
- **索提诺比率**: Sortino Ratio
- **信息比率**: Information Ratio
- **卡玛比率**: Calmar Ratio

## 个人量化系统适用性

### 最小可行方案
1. **基准定义**: 选择沪深300或中证500作为基准
2. **收益对比**: 计算策略与基准的收益对比
3. **风险分析**: 计算夏普比率、最大回撤等
4. **简单报告**: 生成简单的对比图表

### 实施建议
- **工具**: pyfolio + empyrical
- **周期**: 每周生成一次报告
- **重点**: 关注超额收益和最大回撤
