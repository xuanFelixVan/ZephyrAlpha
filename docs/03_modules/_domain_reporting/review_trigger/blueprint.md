---
module_id: MOD-RPT-038
title: "复盘链事件触发入口蓝图 — 缺失的调用方 + CLI 一次性事件面（F115 R1 触发链薄刀）"
doc_type: blueprint
status: Active
version: "0.1.2"
ttl: permanent
layer: L07_reporting
layer_name: reporting
functional_domain: reporting
owner: ZephyrAlpha-Owner
created_by: st-c9-f115
date: "2026-09-29"
last_updated: "2026-09-29"
priority: P1
blueprint_level: module
responsibility_domain: 
design_maturity: production
build_status: stable
---

# MOD-RPT-038 Review Trigger — 复盘链事件触发入口 蓝图

> **module_id**: MOD-RPT-038 | **域**: D_REPORTING | **层**: L07 报告
> **优先级**: P1 | **成熟度**: experimental | **真源**: src/zephyr/reporting/review_trigger.py
> **SSoT**: depgraph MOD-RPT-038 | **断点真源**: 04_reporting.md §四-1 + 90_backfill_wave.md R1

## 1. 定位

F115 R1 触发链薄刀。04 册 §四-1 实证：review_orchestrator.py:48 铁律"run_daily/
run_weekly/run_monthly 由调用方在日终/周末/月末事件触发"——**该调用方全仓不存在**
（grep 穷尽复证，包外仅头注文字），三类报告生产＝空集。

本模块补**触发面**：trigger_daily_review()＝缺失的"调用方"函数——组装最小输入驱动
真实 ReviewOrchestrator.run_daily 全链（审计→日摘要→归档落盘）。宿主中立：R1 触发
宿主三选一（F74 汇总器/骨架体检班/api_server 侧班）为 Owner 待裁项，选定后宿主只需
一行 `trigger_daily_review(...)` 接线；CLI `python -m zephyr.reporting.review_trigger`
为人工/运维一次性事件面。**零定时器零计划任务**（事件驱动铁律）。

**不重复建设边界**：晨报摘要=strategy_pipeline.morning_digest（建议包承接面，在途袋
领地）；本模块=报告域复盘链触发面，零交集（测试钉扎回归）。

## 2. 输入 / 输出

| 方向 | 内容 | 契约 |
|------|------|------|
| 输入 | trading_date（YYYY-MM-DD）+ portfolio_id | CLI 参数/函数入参 |
| 输入 | orchestrator（可选注入；None=真实装配） | ReviewOrchestrator（Fake 友好） |
| 输出 | DailyReviewResult（审计+日摘要+归档件） | zephyr.reporting.review_orchestrator |
| 输出 | data/reports/report_archive.jsonl 追加行 | MOD-RPT-037 sink（默认装配） |

## 3. 核心规则

### 3.1 上游缺口显式标注（不伪装完整审计）

- AuditRequest：空持仓/空成交/零净值/空限额（同 scripts/tasks/run/run_post_settlement.py
  _build_audit_fn 先例——57 号文 GAP 族输入真源未接线，缺口由产出显式标注）。
- 契约快照/指标：RiskDashboardSnapshot/RiskMetricsReport 零值最小构造，
  calculation_method="upstream_gap_minimal"，portfolio_id 双契约一致。

### 3.2 事件驱动零定时器

- 无 cron/Timer/sleep-loop/计划任务——一次性函数调用 + CLI 单发；
- 触发时点由调用方事件决定（日终/人工/宿主侧班）。

### 3.3 真实装配（build_default_orchestrator）

- DailyAuditor + RiskReportEngine + ReportPublisher(archive_sink=JsonlArchiveSink)
  ——R1 触发→R2 归档→R3 投影三刀由此串成一条可验收生成链。

## 4. 依赖与消费者

- 依赖：review_orchestrator/report_publisher/report_archive_sink/risk_report_engine/
  risk.core.daily_auditor/shared.contracts（快照+指标）。
- 消费者：日终事件宿主（三选一待裁）+ CLI 人工触发。

## 5. 边界（不做什么）

- 不做周/月复盘触发（run_weekly/run_monthly 需日摘要序列供给，随宿主接线批扩面）；
- 不做上游输入真源接线（57 号 GAP 族）；不做分发渠道语义（R4，与 F114 同窗裁定）。

## 6. 施工指引

- 测试：tests/reporting/test_review_trigger.py（8 用例：真实全链/无发布/装配/
  非法日期/晨报边界/CLI 0-1 退出码/no-publish）。

---

## 7. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 7.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/reporting/attribution_meta_iteration.py` | ✅ 已实现 | |

### 7.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/reporting/test_attribution_meta_iteration.py` | ✅ 已实现 | |
| `tests/reporting/test_review_trigger.py` | ✅ 已实现 | |

### 7.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §7（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于仓库根目录（REPO_ROOT，不写死盘符绝对路径）
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RPT-038`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RPT-038` 的 4 个 file 节点 | production | `extract_depgraph.py --modules MOD-RPT-038` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RPT-038 | MOD-RPT-038 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 4 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
