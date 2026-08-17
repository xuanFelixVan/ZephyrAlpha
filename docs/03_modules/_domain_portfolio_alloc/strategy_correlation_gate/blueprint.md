---
module_id: MOD-PA-004
title: "策略相关性门禁蓝图 — 多维度相关性检查+5级裁决"
doc_type: blueprint
status: Active
version: "0.1.1"
design_maturity: design
build_status: stable
ttl: permanent
layer: L02_pf_alloc
layer_name: pf_alloc
functional_domain: pf_alloc
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P0
blueprint_level: module
responsibility_domain: 
---

# MOD-PA-004 Strategy Correlation Gate — 策略相关性门禁 蓝图

> **module_id**: MOD-PA-004 | **域**: D_PF_ALLOC | **层**: L02 组合分配
> **优先级**: P0 | **成熟度**: L1 🔵 骨架 → production | **建设标记**: ✅可建设
> **SSoT**: depgraph MOD-PA-004 | **设计真源**: D:\临时工作区\依赖图\06-D-PF-ALLOC-组合分配域.md §1 PA-04, §7.1, §7.2

## 1. 定位

G12 策略相关性门禁——在策略上线/资金分配前, 检查策略两两之间的相关性、因子重叠、
股票池重叠、行业集中度、尾部相关性, 超阈值产出 PA-E03 CorrelationGateTriggered 事件,
阻止过度同质化的策略组合上线。

属 A 类基础设施(阈值判定+多维度门禁, 逻辑明确), 阈值为 C 类可调参数。
相关性矩阵/因子重叠率的*计算*属数据层职责, 本模块只消费已计算好的指标做门禁判定。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | 策略两两指标(相关性/因子重叠/股票池重叠/行业集中度/尾部相关) | 来自 PA-03 分配器或离线计算 |
| 输出 | CorrelationGateResult (整体裁决 PASS/WARN/REJECT/HARD_REJECT + 违规明细) | 联动 PA-03, PA-05 |
| 事件 | PA-E03 CorrelationGateTriggered | → D-PF-CORE |

## 3. 门禁规则 (设计真源 §1 PA-04, §7.1, §7.2)

| 维度 | 阈值 | 裁决 |
|------|------|------|
| Pearson 相关性 | > 0.90 | HARD_REJECT (硬否决) |
| Pearson 相关性 | > 0.85 | REJECT (否决) |
| 因子重叠率 | > 80% | REJECT (否决上线) |
| 因子重叠率 | > 60% | WARN |
| 股票池重叠 > 70% 且 行业集中度 > 50% | — | WARN |
| 尾部相关性 (EVT) | > 0.7 | REJECT (否决新增同方向策略, 仅 same_direction=True 时) |

整体裁决取所有 pair 中最严重级别: HARD_REJECT > REJECT > WARN > PASS。

## 4. 关键不变量 (INVARIANTS)

- 所有输入指标 ∈ [0, 1] (相关性取绝对值)
- 整体裁决 = max(各 pair 裁决) 按严重度排序
- 尾部相关 REJECT 仅对 same_direction=True 的 pair 生效
- 门禁不修改策略, 只产出裁决 (无副作用)

## 5. 错误契约

- `InvalidCorrelationInputError` (ZA-PA-0004): 指标越界、策略自相关、pair 字段非法

## 6. 测试

- `tests/pf_alloc/test_strategy_correlation_gate.py`
- 覆盖: 各维度阈值边界、整体裁决聚合、尾部相关方向约束、事件触发、输入校验

## 7. 依赖

- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 消费者: MOD-PA-003 (资金分配器), MOD-PA-005 (策略生命周期)

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-PA-004`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-PA-004` 的 2 个 file 节点 | design | `extract_depgraph.py --modules MOD-PA-004` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-PA-004 | MOD-PA-004 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

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
