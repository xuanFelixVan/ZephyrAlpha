---
ttl: task_bound
completes_when: 孤儿分诊战役终裁落地（chief 终审+处置执行）后本册随 30/31 号转归档
title: 孤儿分诊总册（2023 台四处置索引）
owner: st-orphtriage-20261004
---

# 40 号·孤儿分诊总册（覆盖账本 v2·四处置分诊索引）

> 会话=st-orphtriage-20261004（证据班长）；靶单=31_orphan_clusters.md（74 簇 2023 台）；数据真源=30_attribution_table.yaml（机生禁手改）。
> 立法原句（Owner 2026-10-04）：**「存在就要有用，或者有结论」**——四态必居其一；本册=给真孤儿定态的证据包+建议，终裁归 GLM-5.3 chief，退役执行归 Owner 门位（裁定#375 族谱系）。

## 0. 方法与判据

初判决策表（按序首中即止，总包令 §任务2 机械判据）：

| # | 条件 | 处置 | 依据 |
|---|---|---|---|
| 1 | `scripts/_archive/**` | exempt | 归档区（退役保留区），复查=季度退役审计 |
| 2 | 路径含 crypto | exempt | 币圈暂停令 crypto-dev-paused-20261004 |
| 3 | `src/zephyr/frontend/**` | newmap | 簇级评估（横轴功能面漏挂，见 41 册簇级节） |
| 4 | tier∈{wired,wired_by_header,wired_dynamic} | mount | 活线在身但六图无认领=活着但没挂线；图建议按域规则（41 册逐台标注） |
| 5 | last_commit=untracked | dispute | 未入库新件无落地史 |
| 6 | suspect_orphan 且 >180 天无 commit | retire 候选 | 零线零引+陈旧；执行归 Owner 门位 |
| 7 | 其余（suspect_orphan 且 ≤180 天） | dispute | 活着但零线零引，两可 |

**三条口径 caveat（判读必读）**：
1. **imported_by 判据的适应**：总包令判据「近 90 天有 commit 且 imported_by>0 → mount」——孤儿集合的定义属性即 imported_by=0（被引即非孤），该分支在 2023 台宇宙内为空集；故 mount 倾向改用 tier 信号（wired*=import/header/dynamic 三型活线在身，语义即"活着但没挂线"）。
2. **last_commit 大面积同日**：多数台 last_commit=2026-09-15/16（全仓格式化波），日期龄对这批**不反映真实陈旧度**；retire 判据（>180 天）只对 genuinely 旧文件可信，对格式化波台面自动降权（它们落在 dispute/mount 不落 retire）。
3. **untracked 8 台**（scripts.data 簇 pattern_* 族）：无 commit 史，不进任何日期判据。

## 1. 簇优先级序与分诊进度（74 簇全分诊）

> 序=孤儿数×战略价值（frontend 置顶、scripts/_archive 次之）；进度列=证据册（已全部产出，29 册覆盖 2023/2023）。

| 序 | 簇 | 孤儿数 | 战略价值带 | 初判分布 | 证据册 |
|---|---|---|---|---|---|
| 1 | src.zephyr.frontend | 166 | 中（AI/前端/报告） | newmap=166 | [41_src_zephyr_frontend_triage.md](41_src_zephyr_frontend_triage.md) |
| 2 | scripts._archive | 35 | 低（归档区） | exempt=35 | [41_scripts__archive_triage.md](41_scripts__archive_triage.md) |
| 3 | src.zephyr.signal_ashare | 78 | 高（核心业务链） | dispute=7，mount=71 | [41_src_zephyr_signal_ashare_triage.md](41_src_zephyr_signal_ashare_triage.md) |
| 4 | src.zephyr.factor | 38 | 高（核心业务链） | dispute=4，mount=34 | [41_src_zephyr_factor_triage.md](41_src_zephyr_factor_triage.md) |
| 5 | src.zephyr.trading | 29 | 高（核心业务链） | dispute=7，mount=22 | [41_src_zephyr_trading_triage.md](41_src_zephyr_trading_triage.md) |
| 6 | src.zephyr.risk | 27 | 高（核心业务链） | dispute=5，mount=22 | [41_src_zephyr_risk_triage.md](41_src_zephyr_risk_triage.md) |
| 7 | src.zephyr.signal_fundamental | 24 | 高（核心业务链） | dispute=10，mount=14 | [41_src_zephyr_signal_fundamental_triage.md](41_src_zephyr_signal_fundamental_triage.md) |
| 8 | src.zephyr.regime | 14 | 高（核心业务链） | mount=14 | [41_misc_core_triage.md](41_misc_core_triage.md) |
| 9 | src.zephyr.simulation | 13 | 高（核心业务链） | dispute=6，mount=7 | [41_misc_core_triage.md](41_misc_core_triage.md) |
| 10 | src.zephyr.position | 12 | 高（核心业务链） | dispute=4，mount=8 | [41_misc_core_triage.md](41_misc_core_triage.md) |
| 11 | src.zephyr.backtest | 11 | 高（核心业务链） | dispute=4，mount=7 | [41_misc_core_triage.md](41_misc_core_triage.md) |
| 12 | src.zephyr.sell_decision | 9 | 高（核心业务链） | mount=9 | [41_misc_core_triage.md](41_misc_core_triage.md) |
| 13 | src.zephyr.execution_simulation | 8 | 高（核心业务链） | mount=8 | [41_misc_core_triage.md](41_misc_core_triage.md) |
| 14 | src.zephyr.pf_alloc | 8 | 高（核心业务链） | dispute=5，mount=3 | [41_misc_core_triage.md](41_misc_core_triage.md) |
| 15 | src.zephyr.pf_core | 8 | 高（核心业务链） | dispute=4，mount=4 | [41_misc_core_triage.md](41_misc_core_triage.md) |
| 16 | src.zephyr.research | 8 | 高（核心业务链） | mount=8 | [41_misc_core_triage.md](41_misc_core_triage.md) |
| 17 | src.zephyr.signal_quality | 8 | 高（核心业务链） | dispute=6，mount=2 | [41_misc_core_triage.md](41_misc_core_triage.md) |
| 18 | src.zephyr.cross_asset | 7 | 高（核心业务链） | mount=7 | [41_misc_core_triage.md](41_misc_core_triage.md) |
| 19 | src.zephyr.strategy_factory | 7 | 高（核心业务链） | mount=7 | [41_misc_core_triage.md](41_misc_core_triage.md) |
| 20 | src.zephyr.plan_engine | 4 | 高（核心业务链） | mount=4 | [41_misc_core_triage.md](41_misc_core_triage.md) |
| 21 | scripts.backtest | 1 | 高（核心业务链） | mount=1 | [41_misc_core_triage.md](41_misc_core_triage.md) |
| 22 | src.zephyr.governance | 158 | 中高（治理族） | dispute=3，mount=155 | [41_src_zephyr_governance_triage.md](41_src_zephyr_governance_triage.md) |
| 23 | src.zephyr.gov_code_quality | 61 | 中高（治理族） | dispute=1，mount=60 | [41_src_zephyr_gov_code_quality_triage.md](41_src_zephyr_gov_code_quality_triage.md) |
| 24 | src.zephyr.gov_drift | 46 | 中高（治理族） | dispute=1，mount=45 | [41_src_zephyr_gov_drift_triage.md](41_src_zephyr_gov_drift_triage.md) |
| 25 | scripts.governance | 42 | 中高（治理族） | dispute=7，mount=35 | [41_scripts_governance_triage.md](41_scripts_governance_triage.md) |
| 26 | src.zephyr.gov_audit | 40 | 中高（治理族） | mount=40 | [41_src_zephyr_gov_audit_triage.md](41_src_zephyr_gov_audit_triage.md) |
| 27 | src.zephyr.compliance | 25 | 中高（治理族） | dispute=6，mount=19 | [41_src_zephyr_compliance_triage.md](41_src_zephyr_compliance_triage.md) |
| 28 | src.zephyr.data_governance | 19 | 中高（治理族） | mount=19 | [41_misc_gov_triage.md](41_misc_gov_triage.md) |
| 29 | src.zephyr.security | 19 | 中高（治理族） | dispute=6，mount=13 | [41_misc_gov_triage.md](41_misc_gov_triage.md) |
| 30 | src.zephyr.gov_enforcement | 14 | 中高（治理族） | mount=14 | [41_misc_gov_triage.md](41_misc_gov_triage.md) |
| 31 | src.zephyr.clone_guard | 11 | 中高（治理族） | mount=11 | [41_misc_gov_triage.md](41_misc_gov_triage.md) |
| 32 | src.zephyr.data_security | 9 | 中高（治理族） | mount=9 | [41_misc_gov_triage.md](41_misc_gov_triage.md) |
| 33 | scripts.audit | 2 | 中高（治理族） | mount=2 | [41_misc_gov_triage.md](41_misc_gov_triage.md) |
| 34 | src.zephyr.gov_rule | 2 | 中高（治理族） | dispute=1，mount=1 | [41_misc_gov_triage.md](41_misc_gov_triage.md) |
| 35 | src.zephyr.shared | 210 | 中（基础设施） | dispute=28，mount=182 | [41_src_zephyr_shared_triage.md](41_src_zephyr_shared_triage.md) |
| 36 | src.zephyr.infrastructure | 160 | 中（基础设施） | dispute=5，mount=155 | [41_src_zephyr_infrastructure_triage.md](41_src_zephyr_infrastructure_triage.md) |
| 37 | src.zephyr.integration | 24 | 中（基础设施） | mount=24 | [41_src_zephyr_integration_triage.md](41_src_zephyr_integration_triage.md) |
| 38 | src.zephyr.ex_core | 22 | 中（基础设施） | dispute=4，mount=18 | [41_src_zephyr_ex_core_triage.md](41_src_zephyr_ex_core_triage.md) |
| 39 | src.zephyr.ex_sor | 15 | 中（基础设施） | mount=15 | [41_misc_infra_triage.md](41_misc_infra_triage.md) |
| 40 | src.zephyr.data | 12 | 中（基础设施） | dispute=2，mount=10 | [41_misc_infra_triage.md](41_misc_infra_triage.md) |
| 41 | src.zephyr.alt_data | 11 | 中（基础设施） | mount=11 | [41_misc_infra_triage.md](41_misc_infra_triage.md) |
| 42 | src.zephyr.library | 8 | 中（基础设施） | mount=8 | [41_misc_infra_triage.md](41_misc_infra_triage.md) |
| 43 | src.zephyr.market_data | 7 | 中（基础设施） | mount=7 | [41_misc_infra_triage.md](41_misc_infra_triage.md) |
| 44 | scripts.data | 5 | 中（基础设施） | mount=5 | [41_misc_infra_triage.md](41_misc_infra_triage.md) |
| 45 | src.zephyr.infra_runtime | 3 | 中（基础设施） | mount=3 | [41_misc_infra_triage.md](41_misc_infra_triage.md) |
| 46 | src.zephyr.infra_ops | 1 | 中（基础设施） | mount=1 | [41_misc_infra_triage.md](41_misc_infra_triage.md) |
| 47 | src.zephyr.feedback_loop | 227 | 中 | mount=227 | [41_src_zephyr_feedback_loop_triage.md](41_src_zephyr_feedback_loop_triage.md) |
| 48 | src.zephyr.autonomy_core | 103 | 中 | dispute=2，mount=101 | [41_src_zephyr_autonomy_core_triage.md](41_src_zephyr_autonomy_core_triage.md) |
| 49 | src.zephyr.intelligence | 53 | 中（AI/前端/报告） | dispute=7，mount=46 | [41_src_zephyr_intelligence_triage.md](41_src_zephyr_intelligence_triage.md) |
| 50 | src.zephyr.orchestrator | 47 | 中 | dispute=3，mount=44 | [41_src_zephyr_orchestrator_triage.md](41_src_zephyr_orchestrator_triage.md) |
| 51 | src.zephyr.ml_train | 41 | 中（AI/前端/报告） | dispute=9，mount=32 | [41_src_zephyr_ml_train_triage.md](41_src_zephyr_ml_train_triage.md) |
| 52 | src.zephyr.reporting | 27 | 中（AI/前端/报告） | dispute=6，mount=21 | [41_src_zephyr_reporting_triage.md](41_src_zephyr_reporting_triage.md) |
| 53 | src.zephyr.ai_layer | 22 | 中（AI/前端/报告） | dispute=1，mount=21 | [41_src_zephyr_ai_layer_triage.md](41_src_zephyr_ai_layer_triage.md) |
| 54 | scripts.industry_graph | 10 | 中 | mount=10 | [41_misc_general_triage.md](41_misc_general_triage.md) |
| 55 | src.zephyr.experiment_tracking | 9 | 中（AI/前端/报告） | mount=9 | [41_misc_ai_report_triage.md](41_misc_ai_report_triage.md) |
| 56 | src.zephyr.digital_twin | 8 | 中（AI/前端/报告） | mount=8 | [41_misc_ai_report_triage.md](41_misc_ai_report_triage.md) |
| 57 | src.zephyr.ml_serve | 7 | 中（AI/前端/报告） | mount=7 | [41_misc_ai_report_triage.md](41_misc_ai_report_triage.md) |
| 58 | src.zephyr.knowledge | 5 | 中（AI/前端/报告） | mount=5 | [41_misc_ai_report_triage.md](41_misc_ai_report_triage.md) |
| 59 | src.zephyr.nlp | 5 | 中（AI/前端/报告） | mount=5 | [41_misc_ai_report_triage.md](41_misc_ai_report_triage.md) |
| 60 | scripts.ch | 4 | 中 | mount=4 | [41_misc_general_triage.md](41_misc_general_triage.md) |
| 61 | scripts.__init__.py | 1 | 中 | mount=1 | [41_misc_general_triage.md](41_misc_general_triage.md) |
| 62 | scripts.ai_layer | 1 | 中（AI/前端/报告） | mount=1 | [41_misc_ai_report_triage.md](41_misc_ai_report_triage.md) |
| 63 | scripts.check_naming_convention.py | 1 | 中 | mount=1 | [41_misc_general_triage.md](41_misc_general_triage.md) |
| 64 | scripts.clone_guard_audit.py | 1 | 中 | mount=1 | [41_misc_general_triage.md](41_misc_general_triage.md) |
| 65 | scripts.compute_signals.py | 1 | 中 | mount=1 | [41_misc_general_triage.md](41_misc_general_triage.md) |
| 66 | scripts.estimate_pit_backfill_cost.py | 1 | 中 | mount=1 | [41_misc_general_triage.md](41_misc_general_triage.md) |
| 67 | scripts.ml | 1 | 中 | mount=1 | [41_misc_general_triage.md](41_misc_general_triage.md) |
| 68 | scripts.post_checkout_guard.py | 1 | 中 | mount=1 | [41_misc_general_triage.md](41_misc_general_triage.md) |
| 69 | scripts.print_exam_summary.py | 1 | 中 | dispute=1 | [41_misc_general_triage.md](41_misc_general_triage.md) |
| 70 | scripts.scan_forward_days.py | 1 | 中 | mount=1 | [41_misc_general_triage.md](41_misc_general_triage.md) |
| 71 | scripts.serve_docs.py | 1 | 中 | mount=1 | [41_misc_general_triage.md](41_misc_general_triage.md) |
| 72 | scripts.setup_dev_env.py | 1 | 中 | mount=1 | [41_misc_general_triage.md](41_misc_general_triage.md) |
| 73 | scripts.setup_git_guard_aliases.py | 1 | 中 | mount=1 | [41_misc_general_triage.md](41_misc_general_triage.md) |
| 74 | scripts.verify_sentiment_hidden_driver.py | 1 | 中 | mount=1 | [41_misc_general_triage.md](41_misc_general_triage.md) |

## 2. 四处置计数表

| 处置 | 台数 | 语义 |
|---|---|---|
| mount | 1667 | 建议挂既有六图（图建议见 41 册逐台列；挂载执行走各图车道既定流程，本班未动图） |
| exempt | 35 | 有结论第三合法态（归档区/币圈暂停令）；入豁免册须 chief/Owner 批 |
| retire | 0 | 退役候选（证据在册）；执行归 Owner 门位 |
| newmap | 166 | frontend 簇级评估（结论=不立新图，走挂载面补登，见 41 册簇级节） |
| dispute | 155 | 争议待 chief 终裁（清单见 §3） |

**合计 2023/2023，分诊覆盖率 100%。**

## 3. 争议件清单（155 件，每件一行，chief 终审输入）

| file | 争议点 | 两选项 |
|---|---|---|
| `scripts/governance/_shared/registry_batch_edit.py` | suspect_orphan 但 21 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（GOMAP（治理/安全域）） ②retire（Owner 门位） |
| `scripts/governance/_tasks/__init__.py` | suspect_orphan 但 94 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（GOMAP（治理/安全域）） ②retire（Owner 门位） |
| `scripts/governance/d11_compliance/__init__.py` | suspect_orphan 但 105 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（GOMAP（治理/安全域）） ②retire（Owner 门位） |
| `scripts/governance/fullflow/__init__.py` | suspect_orphan 但 6 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（GOMAP（治理/安全域）） ②retire（Owner 门位） |
| `scripts/governance/query_candidate_registry.py` | suspect_orphan 但 45 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（GOMAP（治理/安全域）） ②retire（Owner 门位） |
| `scripts/governance/scan_offrepo_assets.py` | suspect_orphan 但 16 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（GOMAP（治理/安全域）） ②retire（Owner 门位） |
| `scripts/governance/vms/__init__.py` | suspect_orphan 但 94 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（GOMAP（治理/安全域）） ②retire（Owner 门位） |
| `scripts/print_exam_summary.py` | suspect_orphan 但 44 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 print_exam_summary.py 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/ai_layer/__init__.py` | suspect_orphan 但 15 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（GOMAP（治理/安全域）） ②retire（Owner 门位） |
| `src/zephyr/autonomy_core/context/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（GOMAP（自治核心域）） ②retire（Owner 门位） |
| `src/zephyr/autonomy_core/skills/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（GOMAP（自治核心域）） ②retire（Owner 门位） |
| `src/zephyr/backtest/_extensions/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（策略工厂）） ②retire（Owner 门位） |
| `src/zephyr/backtest/api/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（策略工厂）） ②retire（Owner 门位） |
| `src/zephyr/backtest/infrastructure/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（策略工厂）） ②retire（Owner 门位） |
| `src/zephyr/backtest/models/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（策略工厂）） ②retire（Owner 门位） |
| `src/zephyr/compliance/_extensions/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（GOMAP（治理/安全域）） ②retire（Owner 门位） |
| `src/zephyr/compliance/api/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（GOMAP（治理/安全域）） ②retire（Owner 门位） |
| `src/zephyr/compliance/core/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（GOMAP（治理/安全域）） ②retire（Owner 门位） |
| `src/zephyr/compliance/infrastructure/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（GOMAP（治理/安全域）） ②retire（Owner 门位） |
| `src/zephyr/compliance/models/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（GOMAP（治理/安全域）） ②retire（Owner 门位） |
| `src/zephyr/compliance/services/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（GOMAP（治理/安全域）） ②retire（Owner 门位） |
| `src/zephyr/data/connectors/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（图12（数据供给链）） ②retire（Owner 门位） |
| `src/zephyr/data/normalizers/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（图12（数据供给链）） ②retire（Owner 门位） |
| `src/zephyr/ex_core/_extensions/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（图12（数据供给链）） ②retire（Owner 门位） |
| `src/zephyr/ex_core/api/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（图12（数据供给链）） ②retire（Owner 门位） |
| `src/zephyr/ex_core/core/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（图12（数据供给链）） ②retire（Owner 门位） |
| `src/zephyr/ex_core/infrastructure/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（图12（数据供给链）） ②retire（Owner 门位） |
| `src/zephyr/factor/_extensions/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（策略工厂）） ②retire（Owner 门位） |
| `src/zephyr/factor/api/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（策略工厂）） ②retire（Owner 门位） |
| `src/zephyr/factor/infrastructure/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（策略工厂）） ②retire（Owner 门位） |
| `src/zephyr/factor/services/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（策略工厂）） ②retire（Owner 门位） |
| `src/zephyr/gov_code_quality/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（GOMAP（治理/安全域）） ②retire（Owner 门位） |
| `src/zephyr/gov_drift/detector_core/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（GOMAP（治理/安全域）） ②retire（Owner 门位） |
| `src/zephyr/gov_rule/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（GOMAP（治理/安全域）） ②retire（Owner 门位） |
| `src/zephyr/governance/architecture_governance/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（GOMAP（治理/安全域）） ②retire（Owner 门位） |
| `src/zephyr/governance/services/__init__.py` | suspect_orphan 但 15 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（GOMAP（治理/安全域）） ②retire（Owner 门位） |
| `src/zephyr/governance/strategies/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（GOMAP（治理/安全域）） ②retire（Owner 门位） |
| `src/zephyr/infrastructure/_extensions/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 infrastructure 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/infrastructure/api/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 infrastructure 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/infrastructure/core/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 infrastructure 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/infrastructure/models/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 infrastructure 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/infrastructure/services/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 infrastructure 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/intelligence/_extensions/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 intelligence 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/intelligence/api/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 intelligence 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/intelligence/core/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 intelligence 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/intelligence/infrastructure/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 intelligence 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/intelligence/model_evaluation/target_lib/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 intelligence 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/intelligence/models/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 intelligence 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/intelligence/services/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 intelligence 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/ml_train/_extensions/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（策略工厂）） ②retire（Owner 门位） |
| `src/zephyr/ml_train/ai_operator/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（策略工厂）） ②retire（Owner 门位） |
| `src/zephyr/ml_train/api/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（策略工厂）） ②retire（Owner 门位） |
| `src/zephyr/ml_train/core/__init__.py` | suspect_orphan 但 17 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（策略工厂）） ②retire（Owner 门位） |
| `src/zephyr/ml_train/infrastructure/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（策略工厂）） ②retire（Owner 门位） |
| `src/zephyr/ml_train/models/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（策略工厂）） ②retire（Owner 门位） |
| `src/zephyr/ml_train/services/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（策略工厂）） ②retire（Owner 门位） |
| `src/zephyr/ml_train/training_dataset_manager/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（策略工厂）） ②retire（Owner 门位） |
| `src/zephyr/ml_train/training_pipeline/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（策略工厂）） ②retire（Owner 门位） |
| `src/zephyr/orchestrator/fault_tolerance/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（GOMAP（编排域）） ②retire（Owner 门位） |
| `src/zephyr/orchestrator/governance/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（GOMAP（编排域）） ②retire（Owner 门位） |
| `src/zephyr/orchestrator/quality/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（GOMAP（编排域）） ②retire（Owner 门位） |
| `src/zephyr/pf_alloc/_extensions/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（策略工厂）） ②retire（Owner 门位） |
| `src/zephyr/pf_alloc/api/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（策略工厂）） ②retire（Owner 门位） |
| `src/zephyr/pf_alloc/infrastructure/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（策略工厂）） ②retire（Owner 门位） |
| `src/zephyr/pf_alloc/models/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（策略工厂）） ②retire（Owner 门位） |
| `src/zephyr/pf_alloc/services/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（策略工厂）） ②retire（Owner 门位） |
| `src/zephyr/pf_core/_extensions/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（策略工厂）） ②retire（Owner 门位） |
| `src/zephyr/pf_core/api/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（策略工厂）） ②retire（Owner 门位） |
| `src/zephyr/pf_core/infrastructure/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（策略工厂）） ②retire（Owner 门位） |
| `src/zephyr/pf_core/services/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（策略工厂）） ②retire（Owner 门位） |
| `src/zephyr/position/_extensions/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（TDM（交易日夜循环）） ②retire（Owner 门位） |
| `src/zephyr/position/api/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（TDM（交易日夜循环）） ②retire（Owner 门位） |
| `src/zephyr/position/infrastructure/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（TDM（交易日夜循环）） ②retire（Owner 门位） |
| `src/zephyr/position/models/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（TDM（交易日夜循环）） ②retire（Owner 门位） |
| `src/zephyr/reporting/_extensions/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（图11（交付流水线）） ②retire（Owner 门位） |
| `src/zephyr/reporting/api/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（图11（交付流水线）） ②retire（Owner 门位） |
| `src/zephyr/reporting/core/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（图11（交付流水线）） ②retire（Owner 门位） |
| `src/zephyr/reporting/infrastructure/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（图11（交付流水线）） ②retire（Owner 门位） |
| `src/zephyr/reporting/models/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（图11（交付流水线）） ②retire（Owner 门位） |
| `src/zephyr/reporting/services/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（图11（交付流水线）） ②retire（Owner 门位） |
| `src/zephyr/risk/_extensions/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（TDM（交易日夜循环）） ②retire（Owner 门位） |
| `src/zephyr/risk/api/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（TDM（交易日夜循环）） ②retire（Owner 门位） |
| `src/zephyr/risk/cross_asset/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（TDM（交易日夜循环）） ②retire（Owner 门位） |
| `src/zephyr/risk/infrastructure/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（TDM（交易日夜循环）） ②retire（Owner 门位） |
| `src/zephyr/risk/services/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（TDM（交易日夜循环）） ②retire（Owner 门位） |
| `src/zephyr/security/_extensions/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（GOMAP（治理/安全域）） ②retire（Owner 门位） |
| `src/zephyr/security/api/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（GOMAP（治理/安全域）） ②retire（Owner 门位） |
| `src/zephyr/security/core/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（GOMAP（治理/安全域）） ②retire（Owner 门位） |
| `src/zephyr/security/infrastructure/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（GOMAP（治理/安全域）） ②retire（Owner 门位） |
| `src/zephyr/security/models/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（GOMAP（治理/安全域）） ②retire（Owner 门位） |
| `src/zephyr/security/services/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（GOMAP（治理/安全域）） ②retire（Owner 门位） |
| `src/zephyr/shared/adaptation/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 shared 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/shared/alerts/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 shared 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/shared/api/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 shared 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/shared/blueprint_tools/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 shared 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/shared/compensation/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 shared 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/shared/context/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 shared 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/shared/contracts/core/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 shared 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/shared/contracts/execution/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 shared 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/shared/contracts/experiment/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 shared 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/shared/contracts/external/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 shared 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/shared/contracts/market/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 shared 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/shared/contracts/portfolio/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 shared 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/shared/contracts/risk/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 shared 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/shared/database/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 shared 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/shared/dependency/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 shared 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/shared/draft/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 shared 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/shared/foundation/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 shared 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/shared/maintenance/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 shared 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/shared/observability/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 shared 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/shared/queue/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 shared 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/shared/reliability/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 shared 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/shared/schema/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 shared 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/shared/security/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 shared 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/shared/session/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 shared 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/shared/shared_util/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 shared 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/shared/utils/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 shared 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/shared/versioning/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 shared 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/shared/vocab/__init__.py` | suspect_orphan 但 5 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（chief 判（域 shared 无预设映射）） ②retire（Owner 门位） |
| `src/zephyr/signal_ashare/intraday_t0/__init__.py` | suspect_orphan 但 16 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（原料端）/图12 备选） ②retire（Owner 门位） |
| `src/zephyr/signal_ashare/limit_up/__init__.py` | suspect_orphan 但 16 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（原料端）/图12 备选） ②retire（Owner 门位） |
| `src/zephyr/signal_ashare/ml_forecast/__init__.py` | suspect_orphan 但 16 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（原料端）/图12 备选） ②retire（Owner 门位） |
| `src/zephyr/signal_ashare/screening/__init__.py` | suspect_orphan 但 16 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（原料端）/图12 备选） ②retire（Owner 门位） |
| `src/zephyr/signal_ashare/sector/__init__.py` | suspect_orphan 但 16 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（原料端）/图12 备选） ②retire（Owner 门位） |
| `src/zephyr/signal_ashare/sentiment/__init__.py` | suspect_orphan 但 16 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（原料端）/图12 备选） ②retire（Owner 门位） |
| `src/zephyr/signal_ashare/strategy_signal/__init__.py` | suspect_orphan 但 20 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（原料端）/图12 备选） ②retire（Owner 门位） |
| `src/zephyr/signal_fundamental/_extensions/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（原料端）/图12 备选） ②retire（Owner 门位） |
| `src/zephyr/signal_fundamental/api/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（原料端）/图12 备选） ②retire（Owner 门位） |
| `src/zephyr/signal_fundamental/core/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（原料端）/图12 备选） ②retire（Owner 门位） |
| `src/zephyr/signal_fundamental/gen/__init__.py` | suspect_orphan 但 16 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（原料端）/图12 备选） ②retire（Owner 门位） |
| `src/zephyr/signal_fundamental/infrastructure/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（原料端）/图12 备选） ②retire（Owner 门位） |
| `src/zephyr/signal_fundamental/models/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（原料端）/图12 备选） ②retire（Owner 门位） |
| `src/zephyr/signal_fundamental/services/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（原料端）/图12 备选） ②retire（Owner 门位） |
| `src/zephyr/signal_fundamental/strategy/__init__.py` | suspect_orphan 但 16 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（原料端）/图12 备选） ②retire（Owner 门位） |
| `src/zephyr/signal_fundamental/strategy/implementations/__init__.py` | suspect_orphan 但 16 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（原料端）/图12 备选） ②retire（Owner 门位） |
| `src/zephyr/signal_fundamental/synth/__init__.py` | suspect_orphan 但 16 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（原料端）/图12 备选） ②retire（Owner 门位） |
| `src/zephyr/signal_quality/_extensions/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（原料端）） ②retire（Owner 门位） |
| `src/zephyr/signal_quality/api/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（原料端）） ②retire（Owner 门位） |
| `src/zephyr/signal_quality/core/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（原料端）） ②retire（Owner 门位） |
| `src/zephyr/signal_quality/infrastructure/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（原料端）） ②retire（Owner 门位） |
| `src/zephyr/signal_quality/models/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（原料端）） ②retire（Owner 门位） |
| `src/zephyr/signal_quality/services/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（原料端）） ②retire（Owner 门位） |
| `src/zephyr/simulation/_extensions/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（模拟段）） ②retire（Owner 门位） |
| `src/zephyr/simulation/api/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（模拟段）） ②retire（Owner 门位） |
| `src/zephyr/simulation/core/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（模拟段）） ②retire（Owner 门位） |
| `src/zephyr/simulation/infrastructure/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（模拟段）） ②retire（Owner 门位） |
| `src/zephyr/simulation/models/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（模拟段）） ②retire（Owner 门位） |
| `src/zephyr/simulation/services/__init__.py` | suspect_orphan 但 18 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（FACTORY（模拟段）） ②retire（Owner 门位） |
| `src/zephyr/trading/_extensions/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（TDM（交易日夜循环）） ②retire（Owner 门位） |
| `src/zephyr/trading/api/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（TDM（交易日夜循环）） ②retire（Owner 门位） |
| `src/zephyr/trading/core/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（TDM（交易日夜循环）） ②retire（Owner 门位） |
| `src/zephyr/trading/infrastructure/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（TDM（交易日夜循环）） ②retire（Owner 门位） |
| `src/zephyr/trading/models/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（TDM（交易日夜循环）） ②retire（Owner 门位） |
| `src/zephyr/trading/services/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（TDM（交易日夜循环）） ②retire（Owner 门位） |
| `src/zephyr/trading/trading_contracts/market/__init__.py` | suspect_orphan 但 19 天内有 commit（活着但零线零引） | ①两可：可能是入口/生成器目标/未完成——chief 判 mount 或 retire→mount（TDM（交易日夜循环）） ②retire（Owner 门位） |

## 4. 悬空键清账附节（任务3，证据+修复建议，未动图）

30 号报 dangling_keys 两条，原文位置均在 config/strategy_production_map.yaml（FACTORY 机制节点 module_ref）：

- `MOD-BT-006`（FACTORY）
- `MOD-BT-215`（FACTORY）

### MOD-BT-006（FAC-E4-M-003「data_handler 数据来源手」，home_map=图12）

- 键型判定：**已存在模块+depgraph 基表 blueprint_id 错盖**（非笔误、非已删模块）。
- 证据：①目标文件在位=src/zephyr/backtest/core/data_handler.py（33KB，last_commit 2026-09-21）；
  ②PG nodes 表该文件节点的 blueprint_id=**MOD-BT-001**（错号，MOD-BT-006 零行）；
  ③跨册互证=docs/03_modules/_domain_backtest/data_quality_checker/blueprint.md:96「可选消费: MOD-BT-006 data_handler（数据来源）」；
  ④fac9_03_facts.yaml 该 id py_paths=[]（"证据无 py 路径指针，未扫"——与错盖互洽）。
- 修复建议（两行，架构数据走 DB 道，本班未执行）：
  1. `apply_depgraph.py` 修正节点 src/zephyr/backtest/core/data_handler.py 的 blueprint_id：MOD-BT-001→MOD-BT-006（RULE-SSOT 架构数据直写 DB）。
  2. 修后重跑 generate_map_coverage_attribution.py 验 dangling_keys 清零；F2 facts 册（fac9_03_facts.yaml）py_paths 随下批回填。

### MOD-BT-215（FAC-E9-M-003「E2 收益归因 sim_attribution_report」）

- 键型判定：**已存在模块+depgraph 基表 blueprint_id 错盖**（同族根因）。
- 证据：①目标文件在位=scripts/backtest/sim_attribution_report.py（26KB，last_commit 2026-10-04）；
  ②PG nodes 表该文件节点的 blueprint_id=**MOD-BT-084**（错号，MOD-BT-215 零行）；
  ③跨册互证=fullflow_mining/b2_f28_e9_live_attribution.md:35「MOD-BT-215 sim_attribution_report … scripts/backtest/sim_attribution_report.py docstring 实核」+fullconnect_campaign/c_exam_pipeline/06 同引。
- 修复建议（两行，同上）：
  1. `apply_depgraph.py` 修正节点 scripts/backtest/sim_attribution_report.py 的 blueprint_id：MOD-BT-084→MOD-BT-215。
  2. 修后重跑归因生成器验清零；同波建议顺查 MOD-BT-001 的 80 路径超宽映射是否同族错盖（80 台共享一 blueprint_id 异常宽，疑批量盖章事故）。

## 5. 盘面异常呈报（本班未碰，提请持窗会话注意）

- config/coverage_exemption_registry.yaml：暂存区=**删除态**（staged D）而盘面=untracked 新版（含 9 条币圈豁免，与 31 号一致）。判定=他会话在途状态（删除-重建或 token 先行拆批），本班按"他会话在途不代修"铁律未碰；**风险提示=若删除态先落 HEAD 而新盘面未跟上，31 号引用的豁免册将悬空**，请持窗会话收口时保证两态同批或先萷新版。

## 6. 纪律自检

- [x] 禁执行退役删除——retire 全部止于"候选+证据"
- [x] 豁免结论皆有真实依据（归档区=总包令授权判据；币圈=暂停令原文号），无自造
- [x] 六图 YAML 零改动（悬空键修复=建议两行，未执行）
- [x] 30/31 号零手改；本班产出全为 40+ 号新文件
- [x] 覆盖 2023/2023（74 簇 29 册）；处置计数=dispute=155，exempt=35，mount=1667，newmap=166
