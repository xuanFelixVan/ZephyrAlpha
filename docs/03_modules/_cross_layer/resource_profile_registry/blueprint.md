---
module_id: MOD-RESCHED-PROFILE
submodule_path: "scripts/governance/generators/generate_resource_profile_registry.py"
title: "资源画像注册表+生成器蓝图 — 三源实体化（ps1/schedule.yaml/§3.C种子）18字段·合并保全再生"
doc_type: blueprint
template_for: blueprint
status: Active
version: "1.0.3"
layer: L0_infrastructure
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-09-16"
ttl: permanent
actual_disk_path: "scripts/governance/generators/generate_resource_profile_registry.py"
last_updated: "2026-09-16"
last_verified: "2026-09-16"
generation: 3
functional_domain: operations
summary: "资源画像注册表（config/resource_profile_registry.yaml，ROOR REG-RESCHED-001）+其生成器：解析 11 个 register_*.ps1 触发器+schedule.yaml 21 槽位+方案 §3.C 手动实体种子，产出 18 字段实体画像（§2.1 字段总表，生产者+消费者双证）；合并保全再生（人填字段/采样器 measured 字段再生不丢，时间值自真源重抽人禁填）；E0 compute_class→resource_class 映射层在本模块，E0 真源不动。"
tags: [resource-profile, registry, generator, merge-preserve, b1]
priority: P1
belongs_to: MOD-MASTER_BLUEPRINT
parent_module: MOD-INF-016
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
depends_on:
  - target: MOD-L00-004
    at: "全篇"
    why: "schedule.yaml 数据槽位真源（只读抽取）"
references:
  - "docs/_working/resource_schedule/resource_schedule_panorama_plan_v1.md"
codification_level: L1
codification_at: "2026-09-16"
responsibility_domain: 
build_status: generated
design_maturity: production
---

# 资源画像注册表+生成器蓝图 — 三源实体化（ps1/schedule.yaml/§3.C种子）18字段·合并保全再生（MOD-RESCHED-PROFILE）

> module_id: MOD-RESCHED-PROFILE | version: 1.0.3 | status: active | layer: L0_infrastructure
> actual_disk_path: scripts/governance/generators/generate_resource_profile_registry.py | 施工批次：资源排班全景 B1（库）（方案 §8）

## 1. 背景与定位

- 母系统：资源排班全景四件套（库/器/闸/图，方案 docs/_working/resource_schedule/resource_schedule_panorama_plan_v1.md）。
- 病根：排班真源散落三处（register_*.ps1 / schedule.yaml / E0 日历），互不可见，靠人脑避坑
  （实证=schedule.yaml catchup_guard 注释自证"05:30 而非 03:30：周一凌晨已堆两件重活"）。
- 产出=单一真源：57 实体（17 计划任务 sch_* + 21 数据槽位 data_slot_* + 19 手动/事件/动态实体）。

## 2. 架构与职责

1. 三源实体化：ps1 触发器→cron（'|'-多触发点集合）；schedule.yaml cron 原样抽取（人禁填时间值）；
   手动实体时间真源=方案文档（直至有更正式真源）。
2. 十八字段（§2.1）：task_id/module_id/map_node_id/resource_class/pool/peak_mem_gb/est_duration_min/
   exclusive_group/window_type/window_expr/schedule_truth_source/trading_sensitive/measured.*/samples_uri/status/notes_zh。
3. 合并保全再生（A2）：人填字段与采样器独占字段（measured.*/samples_uri）按 task_id 保全；真源消失实体标 orphaned_source 不静默删。
4. 互斥组枚举收口在注册表头部 groups:（ch_bulk_write/tick_drain/mine_vs_exam/repair_passport/gpu_default/llm_local）；
   mem_ceiling_gb 引用 process_reaper _DANGEROUS_MEM_GB=10 红线（不收编）。

## 3. 不变量（INVARIANTS 摘录）

- 静态清单生成器产出禁手工维护（条目增删只经再生）；
- 时间值不搬家（window_expr 从真源抽取，人禁填）；
- E0 映射层单向（local→light，local_gpu/mixed→heavy，api→llm_api_*），E0 真源 compute_window_gate.py 零改动；
- 落盘 safe_write_text CAS（热文件纪律）。

## 4. 消费方与边界

- 消费方：采样器（实体清单+观测模式推导）/排班冲突闸（三检查+漂移检测复用抽取函数）/周历视图生成器/晨审
- 边界：不做运行时调度；不收编三套压力阈值（resource_optimization/resource_guard/reaper，v2 议题挂起）；CH 并发护栏挂起（方案 §4）。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RESCHED-PROFILE`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RESCHED-PROFILE` 的 3 个 file 节点 | production | `extract_depgraph.py --modules MOD-RESCHED-PROFILE` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RESCHED-PROFILE | MOD-RESCHED-PROFILE | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | generated | generated | ✅ |
| file_count | 3 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 5. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 5.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/infrastructure/test_resource_schedule_e2e.py` | ✅ 已实现 | |
| `tests/scripts/test_generate_resource_profile_registry.py` | ✅ 已实现 | |

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


