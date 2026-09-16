---
module_id: MOD-RESCHED-VIEW
submodule_path: "scripts/governance/generators/generate_resource_week_view.py"
title: "周历全景视图蓝图 — 生成器产出 rw-data.js·只读前端页·冲突同源标注"
doc_type: blueprint
template_for: blueprint
status: Active
version: "1.0.1"
layer: L2_domain
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-09-16"
ttl: permanent
actual_disk_path: "scripts/governance/generators/generate_resource_week_view.py"
last_updated: "2026-09-16"
last_verified: "2026-09-16"
generation: 3
functional_domain: operations
summary: "周历全景视图（B3 图）：生成器把注册表投影为周历网格数据（左=实体泳道，横=周一→周日 0-24h），窗档复用闸 expand_windows（跨日切分+同 lane 区间合并），冲突=闸 run_all_checks 同源标注（block 红/warn 黄）；产出 features/resourceweek/rw-data.js（机生禁手改，window.RW_VIEW_DATA）+只读引擎 rw-engine.js（零 fetch 零写路径）；前端照抄 TDM/工厂页范式（页面片段+拆件引擎+loader 接线+manifest/frontend_map 登记，dashboard 体系内加页免 alignment_checklist §3 登记）。"
tags: [resource-schedule, week-view, gantt, read-only, b3]
priority: P1
belongs_to: MOD-MASTER_BLUEPRINT
parent_module: MOD-L08-001
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
depends_on:
  - target: MOD-RESCHED-GATE
    at: "全篇"
    why: "窗档展开+冲突检查同源复用（expand_windows/run_all_checks，零二次判定）"
references:
  - "docs/_working/resource_schedule/resource_schedule_panorama_plan_v1.md"
codification_level: L1
codification_at: "2026-09-16"
responsibility_domain: 
build_status: generated
design_maturity: production
---

# 周历全景视图蓝图 — 生成器产出 rw-data.js·只读前端页·冲突同源标注（MOD-RESCHED-VIEW）

> module_id: MOD-RESCHED-VIEW | version: 1.0.1 | status: active | layer: L2_domain
> actual_disk_path: scripts/governance/generators/generate_resource_week_view.py | 施工批次：资源排班全景 B3（图）（方案 §8）

## 1. 背景与定位

- 母系统：资源排班全景四件套（库/器/闸/图，方案 docs/_working/resource_schedule/resource_schedule_panorama_plan_v1.md）。
- 病根：排班真源散落三处（register_*.ps1 / schedule.yaml / E0 日历），互不可见，靠人脑避坑
  （实证=schedule.yaml catchup_guard 注释自证"05:30 而非 03:30：周一凌晨已堆两件重活"）。
- 验收：渲染全部实体（排程泳道块+常驻/无窗清单段）；数据全部来自生成器；视图禁手改。

## 2. 架构与职责

1. build_week_slots：本周一起 8 天地平线展开→裁剪周窗→跨日切分→(dow,ranges)；常驻/无窗实体
   入 unscheduled 清单段（不渲染时间块）。
2. build_conflicts：run_all_checks findings→简洁结构（真源=闸，零复制语义）。
3. render_js：GENERATED 头+window.RW_VIEW_DATA 赋值（--output 注入测试/E2E）。
4. 引擎 rwInit/rwFilter：全局函数族（页面 onclick 绑定），零依赖零 fetch。

## 3. 不变量（INVARIANTS 摘录）

- 数据全部来自生成器（rw-data.js 禁手改，刷新=重跑）；
- 视图只读（无写端点/写路径）；
- retired/orphaned_source 实体不渲染（与闸 _eligible 同口径）。

## 4. 消费方与边界

- 消费方：dashboard 资源排班周历页（sys 组导航）/晨审（截图/人工看板）
- 边界：不做交互式拖拽改排班（视图禁手改铁律）；不做服务端渲染/新 API 端点（api_server 只动 backtest-run 段）。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RESCHED-VIEW`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RESCHED-VIEW` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-RESCHED-VIEW` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RESCHED-VIEW | MOD-RESCHED-VIEW | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | generated | generated | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 5. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（AUTOGEN 模板原带 AGENTS 编号引用已失效，本批改为无编号引用，记录于 st-resource-20260916 汇报）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 5.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/scripts/test_generate_resource_week_view.py` | ✅ 已实现 | |

### 5.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §5（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
