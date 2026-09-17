---
module_id: MOD-INF-OPS-ALERT-FEED
submodule_path: src/zephyr/infrastructure/system_telemetry/alerts/ops_alert_feed.py
title: "运营告警供给线蓝图 — OOM critical 水位探针→通知板→前端 promotion 页横幅"
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
actual_disk_path: "src/zephyr/infrastructure/system_telemetry/alerts/ops_alert_feed.py"
last_updated: "2026-09-16"
last_verified: "2026-09-16"
generation: 3
functional_domain: operations
summary: "运营告警供给线——补 ALERT-SYS-002（OOM>8GB critical）断链：psutil 项目进程 RSS 探针 30s 评估 config/alert_rules.yaml 内存规则，critical 触发落盘通知板（.runtime/ops_notifications/notifications.jsonl，静默窗口去重+滞回解除），api_server GET /api/ops-notifications 只读投影，前端 promotion 页横幅轮询渲染（2026-09-15 裁定后通知唯一出口）。"
tags: [ops-alert, oom, alert-rules, notification-board, promotion-page, system-telemetry, a2]
priority: P1
belongs_to: MOD-MASTER_BLUEPRINT
parent_module: MOD-INF-015
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
depends_on:
  - target: MOD-INF-015
    at: "全篇"
    why: "System Telemetry——复用 AlertSubsystem 条件解析与 alert_rules.yaml 规则真源"
  - target: MOD-INF-066
    at: "§3"
    why: "promotion 页（C5/S13）为通知唯一出口的承载页"
references: []
codification_level: L1
codification_at: "2026-09-16"
responsibility_domain: 
build_status: stable
design_maturity: production
---

# 运营告警供给线蓝图（MOD-INF-OPS-ALERT-FEED）

> module_id: MOD-INF-OPS-ALERT-FEED | version: 1.0.3 | status: active | layer: L0_infrastructure
> actual_disk_path: src/zephyr/infrastructure/system_telemetry/alerts/ops_alert_feed.py | generation: 3 | construction_progress: completed

## 1. 背景与动因（治理战役 A2，2026-09-16）

- 挖矿地图发现 3：`config/alert_rules.yaml` ALERT-SYS-002（OOM>8GB critical）自 2026-05 起无
  指标生产者——facade 定时 `evaluate("__scheduled__")` 空转，规则引擎在、触发链断。
- 2026-09-15 Owner 裁定：飞书/SMTP 告警通道彻底删除，通知唯一出口=前端 promotion 页。
- 9-15 内存耗尽事故（9 孤儿 llama-server ≈12GB，commit 71.2/79.9GB 触顶）为直接动因。

## 2. 架构（三段供给线）

1. **探针** `probe_project_rss_bytes()`：psutil 当前进程树（self+后代递归）∪ cmdline/exe
   引用仓根的进程 RSS 求和；fail-safe 绝不抛出。8GB 语义=项目衍生内存即将失控。
2. **通知板** `OpsAlertFeed.publish/list_active/resolve`：JSONL 落盘
   `.runtime/ops_notifications/notifications.jsonl`（safe_write_text CAS）；同 dedup key
   静默窗口内只刷新 count/last_seen；解除打 resolved_at（前端 1h 灰显）。
3. **周期 tick** `OpsAlertFeed.tick()`：探针→按内存规则评估（复用 AlertSubsystem 条件解析）→
   critical 发布（silence_window 取规则值）→ 无触发且回落阈值*0.9（滞回）→ resolve。

## 3. 接线

- api_server（告警段）：daemon 线程 `ops-alert-feed` 5s 首延+30s 一 tick；只读端点
  `GET /api/ops-notifications`（异常降级空态不 500）。
- 前端：`services/api.js fetchOpsNotifications` + `features/promotion/promotion.js` 横幅
  `#promo-alert-banner`（注入于 #promo-body 之前，30s 同拍轮询，拉取失败静默）。
- 板目录重定向：环境变量 `ZEPHYR_OPS_NOTIFICATION_DIR`（测试隔离主通道）。

## 4. 边界（不做什么）

- 不投递外部通道（飞书/SMTP 已裁撤）；不碰 facade 调度器；不做收割（reaper=M3 另线）；
  非 critical 告警暂不落板（供给线首期只承 OOM critical，后续按需扩 severity 通道）。

## 5. 测试与验收

- `tests/frontend/test_ops_alert_feed.py`：板发布/静默/解除/清单单测（tmp_path）；
  tick 假探针端到端（9GB→发布、回落→解除）；api 端点投影（板目录重定向）；
  前端横幅渲染（playwright 注入假 OOM critical 事件断言可见）。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-INF-OPS-ALERT-FEED`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-INF-OPS-ALERT-FEED` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-INF-OPS-ALERT-FEED` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-INF-OPS-ALERT-FEED | MOD-INF-OPS-ALERT-FEED | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 6. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 6.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

### 6.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §6（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于仓库根目录（REPO_ROOT，不写死盘符绝对路径）
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


