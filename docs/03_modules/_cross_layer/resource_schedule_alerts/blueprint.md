---
module_id: MOD-RESCHED-ALERT
submodule_path: "src/zephyr/infrastructure/system_telemetry/alerts/resource_schedule_alerts.py"
title: "排班冲突告警桥蓝图 — findings→OpsAlertFeed 唯一通道·静默窗口去重·晨审可见"
doc_type: blueprint
template_for: blueprint
status: Active
version: "1.0.4"
layer: L0_infrastructure
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-09-16"
ttl: permanent
actual_disk_path: "src/zephyr/infrastructure/system_telemetry/alerts/resource_schedule_alerts.py"
last_updated: "2026-09-16"
last_verified: "2026-09-16"
generation: 3
functional_domain: operations
summary: "排班冲突告警桥（B4）：闸 findings→OpsAlertFeed.publish（.runtime/ops_notifications/notifications.jsonl，飞书/SMTP 已裁撤后唯一出口）——block→critical/warn→warning，dedup key=理由码+排序 task_ids，同 key 30min 静默窗口只刷新；本轮消失的冲突自动 resolve（promotion 页灰显解除）；晨审挂接=同一 JSONL 板机器可读（晨审直读或 GET /api/ops-notifications），零额外接口。"
tags: [resource-schedule, alert-bridge, ops-alert-feed, dedup, b4]
priority: P1
belongs_to: MOD-MASTER_BLUEPRINT
parent_module: MOD-INF-OPS-ALERT-FEED
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
depends_on:
  - target: MOD-INF-OPS-ALERT-FEED
    at: "全篇"
    why: "唯一通知出口（板+去重+滞回语义照抄；本模块零通道自建，禁改其本体）"
references:
  - "docs/_working/resource_schedule/resource_schedule_panorama_plan_v1.md"
codification_level: L1
codification_at: "2026-09-16"
responsibility_domain: 
build_status: stable
design_maturity: production
---

# 排班冲突告警桥蓝图 — findings→OpsAlertFeed 唯一通道·静默窗口去重·晨审可见（MOD-RESCHED-ALERT）

> module_id: MOD-RESCHED-ALERT | version: 1.0.4 | status: active | layer: L0_infrastructure
> actual_disk_path: src/zephyr/infrastructure/system_telemetry/alerts/resource_schedule_alerts.py | 施工批次：资源排班全景 B4（告警）（方案 §8）

## 1. 背景与定位

- 母系统：资源排班全景四件套（库/器/闸/图，方案 docs/_working/resource_schedule/resource_schedule_panorama_plan_v1.md）。
- 病根：排班真源散落三处（register_*.ps1 / schedule.yaml / E0 日历），互不可见，靠人脑避坑
  （实证=schedule.yaml catchup_guard 注释自证"05:30 而非 03:30：周一凌晨已堆两件重活"）。
- 送达链：notifications.jsonl → api_server 既有 /api/ops-notifications → promotion 页横幅（治理线已建，零改动复用）。

## 2. 架构与职责

1. publish_findings：findings 映射→publish（fail-safe 单条失败不抛）；
2. resolve_cleared：活动板中本闸 key 不在本轮触发集→resolve；
3. 板目录可注入（测试隔离禁写生产 .runtime）。

## 3. 不变量（INVARIANTS 摘录）

- 唯一出口纪律：只经 OpsAlertFeed，禁另起通道/禁碰飞书；
- 告警线自身不得成为故障源（发布失败降级记日志）；
- key 稳定（理由码+task_ids 排序）保证跨轮去重。

## 4. 消费方与边界

- 消费方：promotion 页横幅/晨审/视图生成器 --publish-alerts 接线
- 边界：不做通知规则评估（复用 alert_rules 评估在 OpsAlertFeed.tick）；不做外部投递。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RESCHED-ALERT`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RESCHED-ALERT` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-RESCHED-ALERT` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RESCHED-ALERT | MOD-RESCHED-ALERT | ✅ |
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
| — | — | 本模块尚无已实现代码 |

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


