---
module_id: MOD-RPT-009
title: "复盘编排器蓝图 — 日/周/月三频复盘链路编排+四段式周报模板（55 号 G26 §3.6）"
doc_type: blueprint
status: Active
version: "0.1.7"
ttl: permanent
layer: L07_reporting
layer_name: reporting
functional_domain: reporting
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-15"
last_updated: "2026-08-15"
priority: P1
blueprint_level: module
responsibility_domain: 
design_maturity: production
build_status: stable
---

# MOD-RPT-009 Review Orchestrator — 复盘编排器 蓝图

> **module_id**: MOD-RPT-009 | **域**: D_REPORTING | **层**: L07 报告
> **优先级**: P1 | **成熟度**: production | **设计真源**: 55_monitoring_review.md §3.6（G26 决策五）

## 1. 定位

D_REPORTING 域编排层——把已 production 的复盘零件（DailyAuditor 五件套 / RiskReportEngine 四类报告 / ReportPublisher 归档）串成"监控-告警-复盘"闭环。只编排不新造分析。

频率分层（55 号 §3.6，自动化分层化解三频过重）：日复盘=机器自动（人只看 FAIL 项）/ 周复盘=人读（四段式唯一固定议程）/ 月复盘=轻量治理汇总（+退役判据扫描聚合）。

## 2. 输入 / 输出

| 方向 | 契约 | 类型 |
|------|------|------|
| 输入 | DailyAuditor / RiskReportEngine / ReportPublisher（构造注入） | 实例 |
| 输入 | StrategyDeviationMonitor / StrategyRetirementEvaluator（可选注入） | 实例 |
| 输入 | 日：AuditRequest + snapshot + metrics；周：daily_summaries + 四段素材；月：daily_summaries + retirement_inputs | 各契约 |
| 输出 | DailyReviewResult / WeeklyReviewResult / MonthlyReviewResult | frozen dataclass |
| 输出 | 归档报告（RISK 源日报 / TRADING_REVIEW 源周报·月报） | ArchivedReport |

## 3. 核心规则

- **日复盘机器自动**：DailyAuditor.audit + generate_daily + 归档；overall_status≠PASS 时提取 IssueRecord 为 human_attention（人只看 FAIL 项——告警驱动）
- **周复盘四段模板**（结构固定=决策内容）：①本周盈亏与归因（54 号供给）②偏离与告警事件（MOD-RK-23 verdict 快照渲染表+告警清单）③阈值与参数变更（真源 alert_threshold_registry）④下周 action items（经 action_item_sink 外送 IncidentManager/候选库，调用方接线）
- **月复盘轻量**：generate_monthly + 退役判据扫描聚合（retirement_inputs 逐项过 evaluator，报告计数归档）
- **事件驱动铁律**：无定时器无 daemon——run_daily/run_weekly/run_monthly 由调用方在日终/周末/月末事件触发

## 4. 关键不变量 (INVARIANTS)

- ReportPublisher 唯一归档出口（D-RPT-D05）；content 仅原始类型（datetime 一律 isoformat）
- 评审制：退役扫描只聚合 RetirementEvaluationReport（status=pending_human_review），本模块无策略状态写接口
- 可选依赖未注入时对应段落留空标注，不阻断主链路
- 周模板四段标题常量 WEEKLY_REVIEW_SECTIONS 唯一真源；人工维护模板资产=同目录 weekly_review_template.md

## 5. 错误契约

| 异常 | 触发 |
|------|------|
| InvalidReviewInputError | daily_summaries 空列表 |

下游零件异常（auditor/engine/publisher）不吞——编排层不掩盖源故障。

## 6. 数据模型

- `DailyReviewResult`：trading_date / audit_report / daily_summary / human_attention / deviation_verdicts / archived_report
- `WeeklyReviewResult`：period / weekly_deep / markdown / action_items / archived_report
- `MonthlyReviewResult`：month / monthly_governance / retirement_report_count / retirement_strategy_ids / archived_report

## 7. API

- `ReviewOrchestrator(auditor, report_engine, publisher, deviation_monitor=None, retirement_evaluator=None, action_item_sink=None)`
- `run_daily(trading_date, audit_request, snapshot, metrics, *, publish=True) -> DailyReviewResult`
- `run_weekly(period, daily_summaries, *, pnl_attribution=None, alert_events=(), threshold_changes=(), action_items=(), publish=True) -> WeeklyReviewResult`
- `run_monthly(month, daily_summaries, *, retirement_inputs=(), publish=True) -> MonthlyReviewResult`

## 8. 依赖

- MOD-RK-20 DailyAuditor / MOD-RPT-008 RiskReportEngine / MOD-RPT-003 ReportPublisher（生产依赖，复用不新造）
- MOD-RK-23 StrategyDeviationMonitor（可选，偏离段数据源）
- strategy_retirement_evaluator（MOD-GOVERNANCE 伞，可选，月退役扫描）

## 9. 测试

tests/reporting/test_review_orchestrator.py——日 PASS/FAIL 两态/周模板四段/偏离表渲染/action sink/月退役扫描聚合/可选依赖降级/空输入拒绝，44 项三件套全绿（2026-08-15）。

## 10. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。

### 10.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/reporting/test_review_orchestrator.py` | ✅ 已实现 | |

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


