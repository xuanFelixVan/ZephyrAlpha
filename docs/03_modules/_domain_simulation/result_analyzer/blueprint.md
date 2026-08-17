---
module_id: MOD-SIM-012
title: "仿真结果分析器蓝图 — 聚合统计+分布检验+可视化数据"
doc_type: blueprint
status: Active
version: "0.1.1"
design_maturity: production
build_status: stable
ttl: permanent
layer: L_SIMULATION
layer_name: simulation
functional_domain: simulation
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P1
blueprint_level: module
responsibility_domain: 
---

# MOD-SIM-012 Simulation Result Analyzer — 仿真结果分析器 蓝图

> **module_id**: MOD-SIM-012 | **域**: D_SIMULATION | **层**: L_SIMULATION 仿真层
> **优先级**: P1 | **成熟度**: L1 🔵 骨架 → production | **建设标记**: ✅可建
> **SSoT**: depgraph MOD-SIM-012 | **设计真源**: D:\临时工作区\依赖图\19-D-SIMULATION-仿真域.md §1 D-SIMULATION-12

## 1. 定位

仿真结果分析器——对多个 SimulationResult(跨场景, 来自 SIM-02 策略仿真)执行聚合统计分析+分布检验+可视化数据准备, 输出 SimulationAnalysisReport。是仿真流水线的分析终点(策略仿真→结果分析)。

消费 SIM-02/SIM-03/SIM-04 的仿真结果, 跨场景聚合回答"策略在 N 个 what-if 场景下的整体表现如何"——均值/标准差/分位数/置信区间 + 收益分布正态性检验 + 可视化数据。

属 A 类基础设施(纯统计计算+numpy, 逻辑明确), 阈值为 C 类可调参数。
自包含不跨域依赖 D_BACKTEST metrics (避免仿真↔回测耦合)。

设计真源: D-SIMULATION-12 "仿真结果分析+统计检验+可视化 | 与D-FRONTEND联动"。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | list[SimulationResult] (跨场景) + AnalysisConfig | 来自 SIM-02 strategy_simulator |
| 输出 | SimulationAnalysisReport (聚合统计+分布+可视化数据+摘要) | 供 D_FRONTEND 可视化 / 人工审查 |

## 3. 核心规则 (设计真源 §1 D-SIMULATION-12)

### 3.1 单场景指标 (ScenarioMetrics)

从每个 SimulationResult 提取:
- total_return: 总收益率
- annualized_return: 年化收益(按 annualization_factor 折算)
- volatility: 收益波动率(年化)
- sharpe: Sharpe 比率 ((annualized_return - rf) / volatility)
- max_drawdown: 最大回撤
- win_rate: 胜率(盈利交易占比)
- trades_count: 交易次数

### 3.2 跨场景聚合 (AggregateAnalysis)

对每个指标跨 N 场景计算:
- mean / std / min / max
- percentiles: p5 / p25 / p50 / p75 / p95
- confidence_interval: 均值的 (1-α) 置信区间 [mean ± z*std/√N]

### 3.3 分布检验 (DistributionAnalysis)

- 收益率直方图分桶 (return_histogram: bins + counts)
- 正态性检验: 基于偏度/峰度的 Jarque-Bera 统计量 (JB = N/6 * (S² + K²/4)), JB > 临界值 → 非正态
- 提供偏度(skewness)/峰度(kurtosis)

### 3.4 可视化数据 (VisualizationData)

- equity_curve_ensemble: 各场景净值曲线(供 D_FRONTEND 绘制)
- metric_distributions: 各指标分布(分位数)供箱线图
- summary: 文本摘要(场景数/均值收益/95%CI/正态性结论)

## 4. 关键不变量 (INVARIANTS)

- 纯 numpy 统计计算, 不依赖外部数据库/scipy
- 全部数据模型 frozen 不可变
- 空列表 → SimulationAnalysisReport 含空聚合 (不报错)
- 单场景 → std/CI 退化为 0/None
- 不修改输入 SimulationResult

## 5. 错误契约

- `SimulationAnalysisError` (ZA-SIM-0012): 输入非 list / 元素非 SimulationResult

## 6. 测试

- `tests/simulation/test_result_analyzer.py`
- 覆盖: 单场景指标计算、多场景聚合(mean/std/分位数/CI)、分布直方图、Jarque-Bera 正态性、可视化数据、空列表、输入校验、frozen

## 7. 依赖

- `numpy` (统计计算)
- `zephyr.simulation.strategy_simulator` (SimulationResult 类型, 仅类型引用)
- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 消费者: D_FRONTEND 可视化 / 人工审查 / C-007 AI自治进化闭环

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIM-012`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIM-012` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-SIM-012` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIM-012 | MOD-SIM-012 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 8. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 8.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

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
