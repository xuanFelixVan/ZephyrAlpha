---
module_id: MOD-SIM-005
title: "场景生成器蓝图 — 蒙特卡洛+历史场景+自定义场景"
doc_type: blueprint
status: Active
version: "0.1.2"
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

# MOD-SIM-005 Scenario Generator — 场景生成器 蓝图

> **module_id**: MOD-SIM-005 | **域**: D_SIMULATION | **层**: L_SIMULATION 仿真层
> **优先级**: P1 | **成熟度**: L1 🔵 骨架 → production | **建设标记**: ✅可建
> **SSoT**: depgraph MOD-SIM-005 | **设计真源**: D:\临时工作区\依赖图\19-D-SIMULATION-仿真域.md §1 D-SIMULATION-05

## 1. 定位

场景生成器——生成 what-if 市场场景(SimulationScenario), 供 SIM-01 市场仿真 / SIM-02 策略仿真 / SIM-04 压力测试 / SIM-06 蒙特卡洛引擎消费。是仿真流水线的起点(场景→市场→策略)。

三种生成模式:
- **蒙特卡洛**: 基于几何布朗运动(GBM)生成随机价格路径, 可配漂移率/波动率/期限/种子
- **历史场景**: 从真实历史数据切片封装为可重放场景(如 2008 危机/2015 股灾片段)
- **自定义场景**: 用户指定冲击序列(价格跳变)+趋势, 生成确定性 what-if 场景

属 A 类基础设施(确定性生成: GBM 公式+历史切片+冲击叠加), 阈值为 C 类可调参数。
核心 Aggregate: SimulationScenario。核心事件: E-SIM-02 ScenarioGenerated。

设计真源: D-SIMULATION-05 "场景生成器+蒙特卡洛+历史场景+自定义场景 | Monte Carlo"。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | 生成参数(MonteCarloParams/HistoricalParams/CustomParams) + Config | 调用方传入 |
| 输出 | SimulationScenario (含 market_data DataFrame + 元数据) | 供 SIM-01/02/04/06 消费, 触发 E-SIM-02 |

## 3. 核心规则 (设计真源 §1 D-SIMULATION-05)

### 3.1 蒙特卡洛场景 (GBM)

几何布朗运动价格路径:
- `S_t = S_{t-1} * exp((drift - 0.5*vol²)*dt + vol*sqrt(dt)*Z)`, Z~N(0,1)
- 参数: start_price, drift(年化漂移), volatility(年化波动率), n_bars, dt(年化时间步, 默认1/252), seed
- 生成 OHLCV: close=GBM 路径, open=前收, high/low 围绕 close, volume=常数

### 3.2 历史场景

- 从真实历史 DataFrame 切片 [start_idx : start_idx+n_bars] 封装为场景
- 保留原始 OHLCV, 附加场景元数据
- 参数: source_data, start_idx, n_bars

### 3.3 自定义场景

- 基础路径 + 用户指定冲击序列: 在指定 bar_idx 叠加 pct_shock (如 -10% 跳空)
- 可配 trend (线性漂移)
- 确定性(给定 seed 可复现)
- 参数: start_price, n_bars, shocks(list[(bar_idx, pct)]), trend, seed

### 3.4 SimulationScenario Aggregate

- scenario_id: 全局唯一 (类型+时间戳+短哈希)
- scenario_type: monte_carlo / historical / custom
- market_data: 生成的 OHLCV DataFrame
- params: 生成参数快照 (dict, 用于复现)
- generated_at: ISO8601 时间戳

## 4. 关键不变量 (INVARIANTS)

- 纯 numpy/pandas 生成, 不依赖外部数据库
- 全部数据模型 frozen 不可变
- 蒙特卡洛/自定义场景给定 seed 可精确复现
- 历史场景不修改源数据 (切片拷贝)
- n_bars<=0 或 start_price<=0 → ScenarioGenerationError
- 历史场景 start_idx+n_bars 越界 → ScenarioGenerationError

## 5. 错误契约

- `ScenarioGenerationError` (ZA-SIM-0005): 参数非法(n_bars<=0/start_price<=0/越界/源数据缺列)

## 6. 测试

- `tests/simulation/test_scenario_generator.py`
- 覆盖: 三种生成模式、GBM 可复现性(同 seed)、历史切片正确性、自定义冲击叠加、参数校验、scenario_id 唯一性、Aggregate frozen、空/越界输入

## 7. 依赖

- `numpy` (GBM 随机数), `pandas` (DataFrame)
- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 消费者: MOD-SIM-002 strategy_simulator / SIM-01 市场仿真 / SIM-04 压力测试 / SIM-06 蒙特卡洛引擎

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIM-005`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIM-005` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-SIM-005` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIM-005 | MOD-SIM-005 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 8. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 8.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/simulation/scenario_generator.py` | ✅ 已实现 | |

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


