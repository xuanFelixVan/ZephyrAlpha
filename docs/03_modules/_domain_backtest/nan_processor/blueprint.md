---
module_id: MOD-BT-026
title: "指标NaN处理器蓝图 — 智能填充+清洗"
doc_type: blueprint
status: Active
version: "0.1.0"
design_maturity: design
build_status: stable
ttl: permanent
layer: L_BACKTEST
layer_name: backtest
functional_domain: backtest
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P1
blueprint_level: module
responsibility_domain: 
---

# MOD-BT-026 NaN Processor — 指标NaN处理器 蓝图

> **module_id**: MOD-BT-026 | **域**: D_BACKTEST | **层**: L_BACKTEST
> **优先级**: P1 | **成熟度**: L1 → production | **建设标记**: ✅可建
> **SSoT**: depgraph MOD-BT-026 | **设计真源**: 32-D-BACKTEST §1 BT-26 + blueprint.md L253

## 1. 定位

指标计算NaN处理器——回测指标计算中产生的NaN值进行智能填充与清洗。
提供6种填充策略(ffill/bfill/mean/median/linear/zero) + 按比例清洗高NaN行/列。
纯pandas工具, 不修改原始数据。

## 2. 输入 / 输出

| 方向 | 内容 |
|------|------|
| 输入 | 含NaN的 DataFrame + 处理配置 |
| 输出 | (处理后的DataFrame, NaNProcessReport) |

## 3. 填充策略

| 策略 | 说明 | 适用场景 |
|------|------|---------|
| ffill | 前向填充 | 时间序列 |
| bfill | 后向填充 | 时间序列 |
| mean | 均值填充 | 截面数据 |
| median | 中位数填充 | 有异常值 |
| linear | 线性插值 | 时间序列 |
| zero | 零填充 | 指标计算 |

## 4. 清洗策略

- drop_all_nan_rows: 删除全NaN行
- drop_all_nan_cols: 删除全NaN列
- max_nan_ratio: 行/列NaN比例超阈值则删除

## 5. 不变量

- 不修改输入数据(返回副本)
- 报告中 filled_count + dropped_rows + remaining_nan = original_nan
- fill_limit>0时限制连续填充数量

## 6. 测试

`tests/backtest/test_nan_processor.py`

## 7. 依赖

- pandas, numpy
- zephyr.shared.foundation.errors
