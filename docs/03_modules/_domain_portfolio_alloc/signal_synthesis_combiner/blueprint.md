---
module_id: MOD-PA-002
title: "信号合成器蓝图 — 多策略加权投票+共振融合"
doc_type: blueprint
status: Active
version: "0.1.3"
design_maturity: design
build_status: generated
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

# MOD-PA-002 Signal Synthesis Combiner — 信号合成器 蓝图

> **module_id**: MOD-PA-002 | **域**: D_PF_ALLOC | **层**: L02 组合分配
> **优先级**: P0 | **成熟度**: L1 🔵 骨架 → production | **建设标记**: ✅可建
> **SSoT**: depgraph MOD-PA-002 | **设计真源**: D:\临时工作区\依赖图\06-D-PF-ALLOC-组合分配域.md §1.1 PA-02

## 1. 定位

信号合成器——多策略信号→加权投票→输出合成信号给 PF-CORE。多策略产出的 StrategySignal
列表(每策略每标的一条)→ 每标的一条 SynthesizedSignal(合成方向+综合得分+共振级别+冲突标记)。

属 A 类基础设施(投票+共振+去重+冲突检测逻辑明确)，不涉及"策略权重怎么定"(PA-01 B类)。
calibrator 为可选注入，不注入时直接用原始 confidence。
依据: 06-D-PF-ALLOC §1.1 PA-02

## 2. 不变量 (INVARIANTS)

- **合成方向由加权投票决定**: 综合得分 = Σ(策略权重 × 方向 × 置信度 × 敏感度)，正→LONG/负→SHORT/零→NEUTRAL
- **同 symbol 同方向去重**: 多策略同向重复信号合并为一条指令
- **反向冲突按策略优先级裁决**: 高优先级策略方向胜出，标记冲突
- **合成置信度 ∈ [0,1]**: 由投票一致性+共振级别计算
- **仓位合并不超上限**: 同标的多策略合并 sum 按策略优先级截断至 cap

## 3. 错误契约 (ERROR_CONTRACT)

| 错误类 | error_code | 触发条件 |
|--------|-----------|---------|
| InvalidStrategySignalError | ZA-PA-0001 | 信号方向非法/权重非正/置信度越界 |
| PositionCapExceededError | ZA-PA-0002 | 合并后仓位超上限且无优先级截断空间 |

## 4. 依赖关系

| 方向 | 模块 | 契约/事件 | 说明 |
|------|------|---------|------|
| 消费 | MOD-PA-01 策略权重 | StrategySignal | 多策略信号(含方向/置信度/权重) |
| 产出 | MOD-PA-003 资金分配 | SynthesizedSignal | 合成信号→权重分配 |
| 产出 | D-PF-CORE | TargetPortfolio | 合成信号→目标组合 |
| 产出 | D-POSITION | SynthesizedSignal | 仓位裁决依据 |

## 5. 六项功能 (PA-02)

| # | 功能 | 说明 |
|---|------|------|
| ① | 多策略投票 | 综合得分 = Σ(策略权重 × 方向 × 置信度 × 敏感度) |
| ② | 共振融合 | 全部同向→STRONG / 多数同向(≥2/3)→MODERATE / 分歧→WEAK |
| ③ | 决策去重 | 同标的同方向多策略重复信号→合并为一条指令 |
| ④ | 跨策略仓位合并 | 同标的多策略合并→取 sum 不超上限(按策略优先级截断) |
| ⑤ | 信号冲突检测 | 同标的反向信号→语义冲突+优先级裁决 |
| ⑥ | 信号置信度校准 | 预留 calibrator 接口(Platt/Isotonic, R-96 后续接入) |

## 6. 关键数据模型

- **SignalDirection**: LONG (+1) / SHORT (-1) / NEUTRAL (0)
- **ResonanceLevel**: STRONG (全部同向) / MODERATE (≥2/3同向) / WEAK (分歧)
- **StrategySignal**: strategy_id / symbol / direction / confidence / weight / sensitivity
- **SynthesizedSignal**: symbol / direction / score / resonance / conflict / contributing_strategies

## 7. 接口

```python
combiner = SignalSynthesisCombiner()
signals = [
    StrategySignal("TREND", "000001.SZ", SignalDirection.LONG, 0.8, weight=0.6),
    StrategySignal("MR", "000001.SZ", SignalDirection.LONG, 0.7, weight=0.4),
]
result = combiner.combine(signals, position_cap=0.05)
# result["000001.SZ"] → SynthesizedSignal(direction=LONG, score=..., resonance=STRONG)
```

## 8. 设计决策

| 决策 | 理由 |
|------|------|
| 加权投票决定方向 | 策略权重反映策略历史表现，加权投票平衡多策略意见 |
| 共振三级 | 全同向=最高置信，分歧=需因子直通裁决 |
| calibrator 可选注入 | 置信度校准是学习系统(R-96)职责，本模块只提供接口 |
| 冲突按优先级裁决 | 避免反向信号同时执行，优先级=策略权重代理 |
| 仓位合并按优先级截断 | 高优先级策略先满足，低优先级截断，防超 cap |

## 9. 测试计划

- 全同向→STRONG 共振
- 多数同向(≥2/3)→MODERATE
- 分歧→WEAK + 冲突标记
- 同方向去重合并
- 反向冲突优先级裁决
- 仓位合并超 cap 截断
- calibrator 注入生效 / 不注入用原始 confidence
- 输入校验(方向非法/权重非正/置信度越界抛错)

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-PA-002`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-PA-002` 的 3 个 file 节点 | design | `extract_depgraph.py --modules MOD-PA-002` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-PA-002 | MOD-PA-002 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | generated | generated | ✅ |
| file_count | 3 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 10. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 10.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/pf_alloc/core/__init__.py` | ⚠️ 骨架 | |
| `src/zephyr/pf_alloc/core/signal_synthesis_combiner.py` | ✅ 已实现 | |

### 10.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §10（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


