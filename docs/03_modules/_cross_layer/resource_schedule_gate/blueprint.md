---
module_id: MOD-RESCHED-GATE
submodule_path: "src/zephyr/gov_enforcement/commit_gates/resource_schedule_gate.py"
title: "排班冲突检测闸蓝图 — 三检查（互斥组/内存天花板/E0）+真源漂移·own-scope commit gate"
doc_type: blueprint
template_for: blueprint
status: Active
version: "1.0.5"
layer: L0_infrastructure
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-09-16"
ttl: permanent
actual_disk_path: "src/zephyr/gov_enforcement/commit_gates/resource_schedule_gate.py"
last_updated: "2026-09-16"
last_verified: "2026-09-16"
generation: 3
functional_domain: operations
summary: "排班冲突检测 commit gate（B2 闸，GATE RESOURCE-SCHEDULE priority=144）：三检查——互斥组窗档交叠（cron 展开+est_duration_min 区间数学）sched_overlap_group、同窗并发内存和超天花板（引用 reaper 10GB 红线）sched_mem_ceiling、交易敏感窗开工未过 E0（复用 classify_window 纯函数，异常 fail-closed）sched_e0_block；另真源漂移检测 sched_truth_drift（warn 防指针失效）。own-scope：staged 命中注册表才触发，外来 staged 降级 warn 不阻断（宪法 §3）。runtime_e0_decision 供 api_server backtest-run 端点同口径接闸。"
tags: [resource-schedule, conflict-gate, own-scope, e0-reuse, b2]
priority: P1
belongs_to: MOD-MASTER_BLUEPRINT
parent_module: MOD-GATE_ENGINE
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
depends_on:
  - target: MOD-BT-151
    at: "全篇"
    why: "E0 classify_window/gate_decision 纯函数最小 import 级复用（不改既有函数）"
references:
  - "docs/_working/resource_schedule/resource_schedule_panorama_plan_v1.md"
codification_level: L1
codification_at: "2026-09-16"
responsibility_domain: 
build_status: stable
design_maturity: production
---

# 排班冲突检测闸蓝图 — 三检查（互斥组/内存天花板/E0）+真源漂移·own-scope commit gate（MOD-RESCHED-GATE）

> module_id: MOD-RESCHED-GATE | version: 1.0.5 | status: active | layer: L0_infrastructure
> actual_disk_path: src/zephyr/gov_enforcement/commit_gates/resource_schedule_gate.py | 施工批次：资源排班全景 B2（闸）（方案 §8）

## 1. 背景与定位

- 母系统：资源排班全景四件套（库/器/闸/图，方案 docs/_working/resource_schedule/resource_schedule_panorama_plan_v1.md）。
- 病根：排班真源散落三处（register_*.ps1 / schedule.yaml / E0 日历），互不可见，靠人脑避坑
  （实证=schedule.yaml catchup_guard 注释自证"05:30 而非 03:30：周一凌晨已堆两件重活"）。
- 登记链：commit_gates 静态 import + in_process_gate_registry.yaml（113）+ gate_registry.yaml 机生条目（own_scope=true）。

## 2. 架构与职责

1. expand_windows：cron（'|'-多段）→28 天地平线区间集；6 段 cron 秒段剥离降级（结构粒度=分钟）。
2. 三检查纯函数（entities 注入可单测）：重叠=组内两两区间求交；内存=扫描线活跃集求和；
   E0=逐窗交易日判定（周末恒休市/工作日保守按交易日——节假日误报方向偏严=fail-closed）。
3. 漂移检测：生成器抽取函数复用（importlib 装载，单抽取真源防克隆），比对 window_expr/window_type。
4. runtime 快查 runtime_e0_decision：backtest-run 端点（远程重算入口纳管，裁定①提前执行）。

## 3. 不变量（INVARIANTS 摘录）

- 结构校验型闸（登记时/提交时），不是运行时调度器；
- E0 异常/日历未知 fail-closed（宁停不裸奔）；
- 阻断=block finding；warn（漂移/cron 坏）不阻断；
- 理由码沿用 E0 风格三码+漂移一码。

## 4. 消费方与边界

- 消费方：GitCommitGateway（own-scope 提交闸）/视图生成器（冲突标注同源）/告警桥（findings→ops 板）/api_server（E0 同口径）
- 边界：不做抢占/动态重排（v1 无运行时调度）；croniter 缺席=时间窗检查降级 warn（基础设施缺位不冒充冲突）。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RESCHED-GATE`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RESCHED-GATE` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-RESCHED-GATE` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RESCHED-GATE | MOD-RESCHED-GATE | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 5. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 5.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/gov_enforcement/commit_gates/resource_schedule_gate.py` | ✅ 已实现 | |

### 5.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/governance/commit_gates/test_resource_schedule_gate.py` | ✅ 已实现 | |

### 5.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §5（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于仓库根目录（REPO_ROOT，不写死盘符绝对路径）
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


