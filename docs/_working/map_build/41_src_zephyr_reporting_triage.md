---
ttl: task_bound
completes_when: 孤儿分诊战役终裁落地（chief 终审+处置执行）后本册随 30/31 号转归档
title: 孤儿分诊证据包：src.zephyr.reporting（27 台）
owner: st-orphtriage-20261004
---

# 41 号·分诊证据包：src.zephyr.reporting（27 台）

> 宇宙口径=裁定#481；数据真源=30_attribution_table.yaml（join checker 机生）；处置=证据班建议，终裁归 GLM-5.3 chief，退役执行归 Owner 门位。
>
> tier 分布：suspect_orphan=6，wired=10，wired_by_header=11；初判汇总：dispute=6，mount=21

## 逐台证据（四字段+初判）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/reporting/_extensions/__init__.py` | reporting/_extensions | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→图11（交付流水线） ②retire→Owner 门位） |
| `src/zephyr/reporting/api/__init__.py` | reporting/api | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→图11（交付流水线） ②retire→Owner 门位） |
| `src/zephyr/reporting/core/__init__.py` | reporting/core | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→图11（交付流水线） ②retire→Owner 门位） |
| `src/zephyr/reporting/infrastructure/__init__.py` | reporting/infrastructure | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→图11（交付流水线） ②retire→Owner 门位） |
| `src/zephyr/reporting/models/__init__.py` | reporting/models | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→图11（交付流水线） ②retire→Owner 门位） |
| `src/zephyr/reporting/services/__init__.py` | reporting/services | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→图11（交付流水线） ②retire→Owner 门位） |
| `src/zephyr/reporting/ai_review_summary.py` | AI 复盘结语生成器（GAP-F-40，MOD-RPT-009 复盘族扩展）。 | 2026-08-24（41天） | in=0/out=0·wired_by_header | **mount**→图11（交付流水线）（活线在身未挂线） |
| `src/zephyr/reporting/alert_aggregator.py` | MOD-RPT-030 — 告警聚合器（GAP-F-28，总览页"今日告警"统一告警流）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图11（交付流水线）（活线在身未挂线） |
| `src/zephyr/reporting/analytics_base.py` | D_REPORTING — Post-Trade Analytics Layer | 2026-09-16（18天） | in=5/out=0·wired | **mount**→图11（交付流水线）（活线在身未挂线） |
| `src/zephyr/reporting/ashare_performance_audit.py` | D_REPORTING — A-Share Performance Audit & Optimization Trigger | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图11（交付流水线）（活线在身未挂线） |
| `src/zephyr/reporting/ashare_trade_record_template.py` | D_REPORTING — A股交易记录模板引擎 (ASHare Trade Record Template) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图11（交付流水线）（活线在身未挂线） |
| `src/zephyr/reporting/attribution_calculator.py` | D_REPORTING — 绩效归因计算器（54 号 BM-REC-02-B，memo §3.2 施工算法落码）。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→图11（交付流水线）（活线在身未挂线） |
| `src/zephyr/reporting/attribution_registry_mapper.py` | D_REPORTING — 归因结果 → experiment_registry.attribution_result 字段映射（62 号未施工清单 #4）。 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→图11（交付流水线）（活线在身未挂线） |
| `src/zephyr/reporting/decision_trace_chain.py` | DecisionTraceChain — 决策溯源链（MOD-RPT-033）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图11（交付流水线）（活线在身未挂线） |
| `src/zephyr/reporting/default_attribution_engine.py` | D_REPORTING — Default Attribution Engine | 2026-09-16（18天） | in=1/out=0·wired | **mount**→图11（交付流水线）（活线在身未挂线） |
| `src/zephyr/reporting/default_tca_engine.py` | D_REPORTING — Default TCA Engine | 2026-09-17（17天） | in=1/out=0·wired | **mount**→图11（交付流水线）（活线在身未挂线） |
| `src/zephyr/reporting/deviation_attribution_decomposer.py` | MOD-RPT-031 — 回测-实盘偏离归因分解器（battle_map BM-BT-05-H 四因子汇总点）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图11（交付流水线）（活线在身未挂线） |
| `src/zephyr/reporting/prediction_log_writer.py` | prediction_log_writer — 每日预测类输出统一落库写入器（92号 §7.13 M4-②） | 2026-09-16（18天） | in=11/out=0·wired | **mount**→图11（交付流水线）（活线在身未挂线） |
| `src/zephyr/reporting/regulatory_report_generator.py` | D_REPORTING — Regulatory Report Generator (监管报告生成器) | 2026-09-16（18天） | in=1/out=0·wired | **mount**→图11（交付流水线）（活线在身未挂线） |
| `src/zephyr/reporting/report_archive_sink.py` | D_REPORTING — Report Archive Sink (报告归档持久化出口，MOD-RPT-037) | 2026-09-30（4天） | in=2/out=0·wired | **mount**→图11（交付流水线）（活线在身未挂线） |
| `src/zephyr/reporting/report_publisher.py` | D_REPORTING — Report Publisher (报告发布器) | 2026-09-30（4天） | in=4/out=0·wired | **mount**→图11（交付流水线）（活线在身未挂线） |
| `src/zephyr/reporting/report_version_manager.py` | D_REPORTING — Report Version Manager (报告版本管理器) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图11（交付流水线）（活线在身未挂线） |
| `src/zephyr/reporting/report_watermark_tracker.py` | D_REPORTING — Report Watermark Tracker (报告水印追踪器) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图11（交付流水线）（活线在身未挂线） |
| `src/zephyr/reporting/review_template_registry.py` | MOD-RPT-032 — 复盘模板注册表（55 号 §6 模板引擎固化外化，GAP-F-40 模板迁出）。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→图11（交付流水线）（活线在身未挂线） |
| `src/zephyr/reporting/risk_report_engine.py` | D_REPORTING — Risk Report Engine (风险报告引擎) | 2026-09-16（18天） | in=2/out=0·wired | **mount**→图11（交付流水线）（活线在身未挂线） |
| `src/zephyr/reporting/strategy_explainability_reporter.py` | StrategyExplainabilityReporter — 策略可解释性报告器（MOD-RPT-035）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图11（交付流水线）（活线在身未挂线） |
| `src/zephyr/reporting/trading_review_engine.py` | TradingReviewEngine — A股交易审查引擎（MOD-RPT-034）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图11（交付流水线）（活线在身未挂线） |
