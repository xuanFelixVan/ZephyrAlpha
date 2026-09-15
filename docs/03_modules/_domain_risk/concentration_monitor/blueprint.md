---
module_id: MOD-RK-07
title: "集中度风险监控器蓝图 — HHI+行业暴露+个股集中度"
doc_type: blueprint
status: Active
version: "0.1.3"
ttl: permanent
layer: L02_risk
layer_name: risk
functional_domain: risk
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P0
blueprint_level: module
responsibility_domain: 
design_maturity: production
build_status: production
---

# MOD-RK-07 Concentration Risk Monitor — 集中度风险监控器 蓝图

> **module_id**: MOD-RK-07 | **域**: D_RISK | **层**: L1 Pre-Trade + L2 盘中监控
> **优先级**: P0 | **成熟度**: production | **对标能力**: C-004●
> **SSoT**: depgraph MOD-RK-07 | **设计真源**: D:\临时工作区\依赖图\11-D-RISK-风控域.md §1.2 RK-07, §7.5 行业集中度

## 1. 定位

集中度风险监控器——计算持仓集中度三大指标(HHI/个股/行业), 三级告警,
供 RK-02 Pre-Trade Hard Block + RK-03 实时监控。Pre-Trade 阶段拦截超限仓位, 盘中监控集中度漂移。

属 A 类基础设施(权重归一化+平方和+分组聚合, 数学逻辑明确), 阈值为 C 类可调参数。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | 权重字典 {symbol: weight} + 可选行业映射 | — |
| 输出 | ConcentrationSnapshot(hhi/max_single/max_industry/level/breach_reasons) | 联动 RK-02, RK-03 |
| 事件 | ConcentrationAlertedEvent (级别变化时发射) | → D-FRONTEND, D-AUTONOMY |

## 3. 核心规则 (设计真源 §1.2 RK-07, §7.4/§7.5)

### 3.1 三大指标

| 指标 | 计算 | 阈值 |
|------|------|------|
| HHI | Σ w_i² ∈ [1/N, 1] | warning 0.10 / critical 0.18 |
| 个股集中度 | max(w_i) | limit 0.10(10%NAV), warning 8% |
| 行业暴露 | max(Σ w_i by industry) | limit 0.30, warning 24% |

### 3.2 三级告警

| 级别 | 触发条件 | 执行动作 |
|------|----------|---------|
| NONE | 所有指标在 warning 内 | 放行 |
| WARNING | 达 warning 阈值 | 告警, RK-02 可 Soft Block |
| CRITICAL | 超硬上限 | RK-02 Hard Block |

### 3.3 事件去抖

- 仅告警级别*变化*时发射 ConcentrationAlertedEvent (含升级/降级/恢复)

## 4. 关键不变量 (INVARIANTS)

- 权重自动归一化 (Σw=1); 拒绝负权重
- HHI ∈ [1/N, 1]; max_single_weight ≤ 1
- 告警级别取所有指标最严重级别
- 无行业映射时跳过行业检查 (避免误报)
- 事件去抖: 连续相同级别不重复发射

## 5. 错误契约

- `InvalidConcentrationInputError` (ZA-RK-0007): 权重为负/权重和为零/配置非法

## 6. 测试

- `tests/risk/test_concentration_monitor.py`
- 覆盖: HHI计算、个股/行业集中度、三级告警、事件去抖、权重归一化、行业映射、监听器隔离

## 7. 依赖

- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 消费者: RK-02 Pre-Trade Checker (Hard Block), RK-03 Portfolio Risk Monitor, RK-13 Crowding Monitor

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RK-07`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RK-07` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-RK-07` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RK-07 | MOD-RK-07 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | production | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 8. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 8.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/risk/test_concentration_monitor.py` | ✅ 已实现 | |

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


