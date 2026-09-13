---
module_id: MOD-INF-065
title: "Hot 平面（<10ms）蓝图 — Tick→风控→下单 10ms 端到端预算（2/3/5ms 分解）+资源独占声明+超限熔断告警"
doc_type: blueprint
status: Active
version: "0.1.2"
ttl: permanent
layer: L00_infrastructure
layer_name: infrastructure_runtime
functional_domain: infrastructure_runtime
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-25"
last_updated: "2026-08-25"
priority: P0
blueprint_level: module
design_maturity: production
build_status: production
responsibility_domain: 
---

# MOD-INF-065 Hot Plane Budget — Hot 平面（<10ms）落地 蓝图

> **module_id**: MOD-INF-065 | **域**: D_INFRA_RUNTIME | **层**: L00 基础设施运行时
> **优先级**: P0 | **来源**: CAND-H1FS-005（B14-04542，AUD-DRAFT-001 裁定=做）
> **SSoT**: depgraph MOD-INF-065

## 1. 定位

Hot 平面是风控执行生命线。平面标记契约（runtime_plane_tag，MOD-INF-002）
与 warm_hot_gate 已有，但 **10ms 端到端预算分解 / 资源独占 / 禁 IO 隔离措施
未落地**。本模块收口 A9 §2.2 为可校验真源：

- 端到端预算 10ms = 2ms（Tick→风控触发，Redis 订阅+回调）
  + 3ms（风控规则评估，预编译规则+零 GC 路径）
  + 5ms（订单构建+下单，miniQMT 连接池复用+预构建订单模板）；累计 2/5/10ms。
- 资源独占声明（§2.2 资源表）：核 8-11 独占绑定 P3（与 MOD-INF-064 规格对齐）、
  P3 禁磁盘 IO（除日志）、miniQMT 连接独占、Redis 本地读路径。
- 预算超限 → 熔断告警判定（纯数据判定，告警执行归 P4 编排）。

> 注（§2.2 表注）：10ms 是 Tick 到达后的处理延迟；miniQMT Tick 间隔 3s 是
> 采样周期，两者不矛盾。

## 2. 输入 / 输出

- 输入：各阶段实测时延 dict（ms）。
- 输出：`HOT_PLANE_BUDGET` 预算声明；`check_budget()` → BudgetVerdict
  （逐阶段超限标记+端到端判定+超限动作声明）；`render_hot_plane_declaration()`
  配置就绪件声明 dict（**仅声明不执行**——核独占/禁 IO 系统级设置属 Owner 窗口）。

## 3. 核心规则

1. 预算真源=A9 §2.2 表（2/3/5ms 分解与累计 2/5/10ms）；任何字段不得放宽总量 10ms。
2. Fail-Closed：未知阶段/负时延/缺阶段 → 抛 HotPlaneBudgetError。
3. 端到端判定：任一阶段超限或总和 >10ms → within_budget=False，
   动作=circuit_alert（熔断告警声明，执行归 P4）。
4. 硬边界：核独占/禁磁盘 IO/连接独占等系统级应用属 Owner 窗口，AI 不执行。

## 4. 依赖前置

- MOD-INF-064 trading_core_process_spec（核 8-11 独占规格对齐，不重复声明）。
- MOD-INF-063 redis_state_layer_ssot（Redis 本地读路径的命名空间真源）。
- 契约对齐：runtime_plane_tag（MOD-INF-002，HOT 平面枚举/10ms 常量）、warm_hot_gate。

## 5. 验收标准

- 单测全绿（预算分解真源值/资源声明/超限判定与熔断告警动作/畸形输入
  Fail-Closed/核规格与 MOD-INF-064 对齐）；相关域集成零回归。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-INF-065`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-INF-065` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-INF-065` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-INF-065 | MOD-INF-065 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | production | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 6. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 6.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/infrastructure/test_hot_plane_budget.py` | ✅ 已实现 | |

### 6.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §6（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


