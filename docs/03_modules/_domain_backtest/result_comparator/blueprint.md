---
module_id: MOD-BT-024
title: "回测结果比较器蓝图 — 多次回测差异分析+显著性检验"
doc_type: blueprint
status: Active
version: "0.1.0"
design_maturity: production
build_status: stable
ttl: permanent
layer: L_BACKTEST
layer_name: backtest
functional_domain: backtest
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P2
blueprint_level: module
responsibility_domain: 
---

# MOD-BT-024 Result Comparator — 回测结果比较器 蓝图

> **module_id**: MOD-BT-024 | **域**: D_BACKTEST | **层**: L_BACKTEST 回测引擎层
> **优先级**: P2 | **成熟度**: L1 🔵 骨架 → production | **建设标记**: ✅可建
> **SSoT**: depgraph MOD-BT-024 | **设计真源**: D:\临时工作区\依赖图\19-D-SIMULATION-仿真域.md §1 D-SIMULATION-53/64

## 1. 定位

回测结果比较器——对两组(或多组)回测结果执行差异分析, 输出结构化比较报告。
覆盖三大维度: 绝对指标比较(年化/总收益/Sharpe/最大回撤/胜率/交易次数) + 相对差异计算 + 统计显著性检验。

属 A 类基础设施(纯统计比较+阈值判定+报告生成, 逻辑明确), 阈值为 C 类可调参数。
纯工具模块, 不依赖外部数据库, 结果由调用方传入。
设计真源: D-SIMULATION-53/64 "回测结果对比：多次回测结果的对比分析与差异展示+对比报告"。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | baseline 回测结果 dict + candidate 回测结果 dict + 比较配置 | 来自 BT-21 param_analyzer / BT-17 scheduler 或直接传入 |
| 输出 | ComparisonReport (比较结果+摘要+HTML表格+显著性说明) | 供人工审查 / BT-19 report_generator 消费 |

## 3. 核心规则 (设计真源 §1 D-SIMULATION-53)

### 3.1 绝对指标比较 (Absolute)

| 指标 | 字段键 | 方向 |
|------|--------|------|
| 年化收益 | annual_return | 越高越好 |
| 总收益 | total_return | 越高越好 |
| Sharpe比率 | sharpe_ratio | 越高越好 |
| 最大回撤 | max_drawdown | 越高越好(存为负值, -0.15>-0.20=回撤更小) |
| 胜率 | win_rate | 越高越好 |
| 交易次数 | trades_count | 中性(不判好坏) |

### 3.2 相对差异 (Relative)

- `absolute_diff = candidate_value - baseline_value`
- `relative_diff = (candidate - baseline) / |baseline|` (baseline=0 时为 None)

### 3.3 统计显著性检验 (Significance)

- 交易次数 < `min_trades_for_significance`(默认30) → 跳过检验, `is_significant=False`
- 交易次数足够时, 基于均值检验: 若 `|absolute_diff| > z * sqrt(std_b²/n_b + std_c²/n_c)`(z=1.96, 95%置信) → 显著
- 缺失 std 字段时退化为不显著

### 3.4 报告生成

- 文本摘要: better/worse/significant 计数
- HTML 表格: 每行一个指标, 列含 baseline/candidate/abs_diff/rel_diff/significant/better
- 显著性说明列表

## 4. 关键不变量 (INVARIANTS)

- 纯标准库实现, 不依赖外部数据库 (结果由调用方传入)
- 比较不修改输入数据 (只读)
- Config/ComparativeMetric/ResultComparison/ComparisonReport 均 frozen 不可变
- 缺失字段 → 对应指标 value/diff 为 None, 不报错
- baseline 与 candidate 均为空 dict → 返回全 None 指标的空比较

## 5. 错误契约

- `ResultComparisonError` (ZA-BT-0024): baseline/candidate 非 dict

## 6. 测试

- `tests/backtest/test_result_comparator.py`
- 覆盖: 配置校验、指标比较(better/worse/中性)、相对差异、显著性检验(交易不足/足够/缺std)、报告生成(摘要+HTML)、空输入、输入校验

## 7. 依赖

- 标准库 `math` (显著性检验)
- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 可选消费: MOD-BT-021 param_analyzer / MOD-BT-017 scheduler (结果来源)
- 消费者: 人工审查 / MOD-BT-019 report_generator

### §0.6 四图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从四图真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-BT-024`

#### 四图位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-BT-024` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-BT-024` |
| 数据流图 (dataflow) | 1 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | （无节点） | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-BT-024 | MOD-BT-024 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
