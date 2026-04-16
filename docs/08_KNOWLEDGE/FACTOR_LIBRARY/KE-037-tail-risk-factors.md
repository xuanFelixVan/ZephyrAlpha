---
module_id: KE-037
title: "尾部风险因子设计"
category: factor
source_file: "docs/02_FACTOR_LIBRARY/03_RISK_FACTORS/TAIL_RISK_FACTORS.md"
source_git_deleted: true
original_path: "docs/02_FACTOR_LIBRARY/03_RISK_FACTORS/TAIL_RISK_FACTORS.md"
deleted_in_commit: "0efa4d760cebc0f91d137341565cd4cfa82cb339"
recovery_date: "2026-04-16"
extracted_date: "2026-04-16"
version: "1.0.0"
status: Active
layer: L03
owner: ZephyrAlpha-Owner
---

# 尾部风险因子设计

## 核心内容摘要

尾部风险因子用于衡量和预测极端市场事件对投资组合的潜在影响。该文档定义了尾部风险因子的计算方法和应用场景，包括VaR（风险价值）、CVaR（条件风险价值）、偏度、峰度等统计指标，以及基于极值理论(EVT)的尾部风险度量。

尾部风险因子在风险管理和组合构建中具有重要作用，可以帮助识别在极端市场条件下可能遭受重大损失的头寸，从而进行针对性的风险对冲或头寸调整。

## 关键设计要点

1. **尾部风险度量指标**：
   - VaR (Value at Risk): 给定置信水平下的最大预期损失
   - CVaR/ES (Expected Shortfall): 超过VaR时的平均损失
   - 偏度(Skewness): 收益率分布的不对称性
   - 峰度(Kurtosis): 收益率分布的尾部厚度

2. **极值理论(EVT)应用**：使用POT(Peaks Over Threshold)方法建模极端事件

3. **动态尾部风险**：基于GARCH族模型估计时变尾部风险

4. **因子暴露计算**：将尾部风险指标转化为可交易的因子暴露

## 适用场景

- L03因子引擎的尾部风险因子实现
- L07风险管理层的压力测试模块
- 组合风险预算和归因分析
- 极端市场条件下的风险预警

## 原始文件

- 恢复命令：`git show 0efa4d760cebc0f91d137341565cd4cfa82cb339^:docs/02_FACTOR_LIBRARY/03_RISK_FACTORS/TAIL_RISK_FACTORS.md`
