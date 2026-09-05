---
module_id: MOD-BT-026
title: "指标NaN处理器蓝图 — 智能填充+清洗"
doc_type: blueprint
status: retired
version: "0.1.3"
design_maturity: deprecated
build_status: retired
ttl: permanent
layer: L_BACKTEST
layer_name: backtest
functional_domain: backtest
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-09-06"
priority: P1
blueprint_level: module
responsibility_domain: 
---

# MOD-BT-026 NaN Processor — 指标NaN处理器 蓝图

> **⚠️ 已退役（2026-09-06 Owner 裁定，B13 退役 salvage）**
>
> - **裁定依据**：模块 6 种填充策略中 3 种（bfill/linear/mean）违反 15 号文 L112 前视偏差禁令（PIT 铁律）；合法语义（ffill 默认/预热剔除）已由 FactorSignal 契约承载，零生产消费方。
> - **15 号文指针**：docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/15_data_feature_layer_spec.md L112（FactorSignal NaN 填充裁定）。
> - **重评条件**：消费方要求差异化填充策略时重建（15 号文自带重评条件）。
> - 实现与测试（src/zephyr/backtest/services/nan_processor.py、tests/backtest/test_nan_processor.py）已删除；本蓝图保留为设计真源。

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

## 8. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 8.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/backtest/test_nan_processor.py` | ✅ 已实现 | |

### 8.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §8（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


