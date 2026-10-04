---
ttl: task_bound
completes_when: 孤儿分诊战役终裁落地（chief 终审+处置执行）后本册随 30/31 号转归档
title: 孤儿分诊证据包：src.zephyr.compliance（25 台）
owner: st-orphtriage-20261004
---

# 41 号·分诊证据包：src.zephyr.compliance（25 台）

> 宇宙口径=裁定#481；数据真源=30_attribution_table.yaml（join checker 机生）；处置=证据班建议，终裁归 GLM-5.3 chief，退役执行归 Owner 门位。
>
> tier 分布：suspect_orphan=6，wired=9，wired_by_header=10；初判汇总：dispute=6，mount=19

## 逐台证据（四字段+初判）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/compliance/_extensions/__init__.py` | compliance/_extensions | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→GOMAP（治理/安全域） ②retire→Owner 门位） |
| `src/zephyr/compliance/api/__init__.py` | D_COMPLIANCE 公共 API 面。 | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→GOMAP（治理/安全域） ②retire→Owner 门位） |
| `src/zephyr/compliance/core/__init__.py` | compliance/core | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→GOMAP（治理/安全域） ②retire→Owner 门位） |
| `src/zephyr/compliance/infrastructure/__init__.py` | compliance/infrastructure | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→GOMAP（治理/安全域） ②retire→Owner 门位） |
| `src/zephyr/compliance/models/__init__.py` | compliance/models | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→GOMAP（治理/安全域） ②retire→Owner 门位） |
| `src/zephyr/compliance/services/__init__.py` | compliance/services | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→GOMAP（治理/安全域） ②retire→Owner 门位） |
| `src/zephyr/compliance/__init__.py` | D_COMPLIANCE Compliance — 包标记（DM-291 迁移后） | 2026-09-18（16天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/compliance/async_intercept_queue.py` | Async Intercept Queue — 合规异步拦截队列 (MOD-L10-001, GAP-L10-001) | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/compliance/compliance_continuous_ops.py` | Compliance Continuous Ops — 合规持续运营 (MOD-CMP-004) | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/compliance/compliance_drift_detector.py` | ComplianceDriftDetector — 合规漂移检测器（MOD-CMP-016）。 | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/compliance/compliance_log.py` | 合规日志 JSONL 落库（43_compliance_discipline §3.2/§7.6）。 | 2026-09-15（19天） | in=10/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/compliance/compliance_policy_engine.py` | CompliancePolicyEngine — 合规策略即代码引擎（MOD-CMP-015）。 | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/compliance/compliance_report_registry.py` | 程序化交易报告 6 项义务登记 + 报送门禁（43_compliance_discipline §7.4）。 | 2026-09-15（19天） | in=5/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/compliance/compliance_rule_engine.py` | ComplianceRuleEngine — §10.8.1.2 合规引擎 (MOD-CMP-012) | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/compliance/compliance_tech_enabler.py` | Compliance Tech Enabler — 合规技术使能器 (MOD-CMP-003) | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/compliance/discipline_must_do_checker.py` | 四项必做清单完成度检测（43_compliance_discipline §3，BM-BUY-08-A）。 | 2026-09-15（19天） | in=4/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/compliance/discipline_prohibition_checker.py` | 四项严禁自动化检测 + Kill Switch 轻量版（43_compliance_discipline §4，BM-BUY-08-B）。 | 2026-09-15（19天） | in=4/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/compliance/evidence_chain_generator.py` | EvidenceChainGenerator — 合规证据链生成器（MOD-CMP-013）。 | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/compliance/hard_boundary_adjudicator.py` | 硬边界功能裁定 + 上线门禁（43_compliance_discipline §6，BM-BUY-12）。 | 2026-09-15（19天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/compliance/info_asymmetry_manipulation_detector.py` | InfoAsymmetryManipulationDetector — 信息不对称期与操纵检测器（MOD-CMP-014）。 | 2026-09-15（19天） | in=3/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/compliance/intraday_manipulation_detector.py` | D_COMPLIANCE — 盘中操纵检测三规则离线批处理口径 MVP（43 号 §7.3，BM-BUY-15 补强残余）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/compliance/license_usage_auditor.py` | 数据源授权条款合规审计（43_compliance_discipline §5，BM-BUY-09 信息合规）。 | 2026-09-15（19天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/compliance/manipulation_stream_driver.py` | D_COMPLIANCE — 市场操纵盘中实时检测流驱动适配（43 号 §10 边界项施工）。 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/compliance/regulatory_change_tracker.py` | RegulatoryChangeTracker — 监管变更追踪器（MOD-CMP-017）。 | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/compliance/trading_compliance_detector.py` | 交易合规检测（43_compliance_discipline §7，BM-BUY-15 补强）。 | 2026-09-15（19天） | in=5/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
