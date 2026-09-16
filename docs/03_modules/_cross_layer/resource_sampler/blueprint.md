---
module_id: MOD-RESCHED-SAMPLER
submodule_path: "src/zephyr/infrastructure/system_telemetry/resource_sampler.py"
title: "资源实测采样器蓝图 — reaper 兄弟式零侵入 cmdline 匹配·样本 JSONL·实测回写"
doc_type: blueprint
template_for: blueprint
status: Active
version: "1.0.0"
layer: L0_infrastructure
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-09-16"
ttl: permanent
actual_disk_path: "src/zephyr/infrastructure/system_telemetry/resource_sampler.py"
last_updated: "2026-09-16"
last_verified: "2026-09-16"
generation: 3
functional_domain: operations
summary: "资源实测采样器（B1 器）：与 process_reaper 同款 cmdline 模式匹配观察进程表，零侵入（不改脚本调用点/不杀进程）；观测模式自 schedule_truth_source 推导（ps1 抽被调脚本基名/静态表/共享宿主槽位跳过）；样本 append-only JSONL 落 .runtime/logs/resource_samples/（Prometheus 命名字段，GNU time 口径）；实测回写注册表 measured 段（memory=实测 max+15% margin 防尖刺失真，duration=P90，VPA 口径）。"
tags: [resource-sampler, zero-intrusion, cmdline-match, jsonl, measured-writeback, b1]
priority: P1
belongs_to: MOD-MASTER_BLUEPRINT
parent_module: MOD-RESOURCE_OPTIMIZATION_ENGINE
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
depends_on:
  - target: MOD-RESOURCE_OPTIMIZATION_ENGINE
    at: "全篇"
    why: "reaper 母本：cmdline 匹配技术+轻导入纪律同款（只读引用，禁改母本）"
references:
  - "docs/_working/resource_schedule/resource_schedule_panorama_plan_v1.md"
codification_level: L1
codification_at: "2026-09-16"
responsibility_domain: 
build_status: generated
design_maturity: production
---

# 资源实测采样器蓝图 — reaper 兄弟式零侵入 cmdline 匹配·样本 JSONL·实测回写（MOD-RESCHED-SAMPLER）

> module_id: MOD-RESCHED-SAMPLER | version: 1.0.0 | status: active | layer: L0_infrastructure
> actual_disk_path: src/zephyr/infrastructure/system_telemetry/resource_sampler.py | 施工批次：资源排班全景 B1（器）（方案 §8）

## 1. 背景与定位

- 母系统：资源排班全景四件套（库/器/闸/图，方案 docs/_working/resource_schedule/resource_schedule_panorama_plan_v1.md）。
- 病根：排班真源散落三处（register_*.ps1 / schedule.yaml / E0 日历），互不可见，靠人脑避坑
  （实证=schedule.yaml catchup_guard 注释自证"05:30 而非 03:30：周一凌晨已堆两件重活"）。
- 验收：对 ≥2 个重活实测回写（B1）；psutil 缺席降级空扫描（fail-safe）。

## 2. 架构与职责

1. scan_once：注册表 active 实体→观测正则→进程表扫描→命中记样本（process_resident_bytes/
   process_cpu_ratio 生存期均值/process_elapsed_seconds）→append JSONL。
2. writeback：读样本流→max+15% margin/P90→CAS 只动 measured 四键（人填字段零触碰）。
3. run_loop：显式调用的周期模式（无常驻自拉起——四要素由 Task Scheduler/调用方承担）。
4. 路径三注入点：registry_path/samples_dir/scanner（测试 stub 主通道，禁真启重活进程）。

## 3. 不变量（INVARIANTS 摘录）

- 零侵入：只读进程表，永不 kill（收割=reaper）；
- 样本 append-only；回写只动 measured.*；
- 共享宿主槽位（schedule.yaml 21 槽跑单进程）v1 不做槽位级归因（防 N 倍计数），摘要记 host_shared_skipped；
- Prometheus 命名纪律：zephyr_resource_ 前缀+base unit 后缀，禁手工 _count。

## 4. 消费方与边界

- 消费方：闸（内存天花板实测口径）/视图生成器（measured 入图）/晨审（样本流）
- 边界：不做水位门（process_incubator SpawnWaterGate）；不做阈值判定（闸）；全局压力阈值真源 resource_optimization.yaml 不收编。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RESCHED-SAMPLER`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RESCHED-SAMPLER` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-RESCHED-SAMPLER` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RESCHED-SAMPLER | MOD-RESCHED-SAMPLER | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | generated | generated | ✅ |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
