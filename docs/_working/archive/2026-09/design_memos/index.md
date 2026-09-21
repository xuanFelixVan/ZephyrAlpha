---
status: active
title: "design_memos — 目录索引"
module_id: ""
blueprint_id: ""
version: "1.0.0"
created: "2026-09-19"
updated: "2026-09-19"
ttl: "permanent"
---

# design_memos

> 本文件由 `generate_missing_index_md.py` 自动生成
> 生成日期：2026-09-19

## 目录内容

| 文件/目录 | 类型 | 说明 |
|-----------|------|------|
| [00_index_trading_decision.md](00_index_trading_decision.md) | Markdown | 交易决策架构主题全集（总索引） |
| [01_design_memo_management_spec.md](01_design_memo_management_spec.md) | Markdown | 设计备忘管理规范 |
| [10_regime_detector_spec.md](10_regime_detector_spec.md) | Markdown | regime 检测器完整 spec |
| [13_regime_phase3_engineering_plan.md](13_regime_phase3_engineering_plan.md) | Markdown | Phase 3 工程规划——降态数 + 两阶段校准 + NLP 管道 + S2/T3 数据激活 |
| [14_regime_s2_diagnosis.md](14_regime_s2_diagnosis.md) | Markdown | S2 评分算法时点错配诊断与治本方案——capitulation 过程化 + valuation 基本面化 + V 反转通路 |
| [15_data_feature_layer_spec.md](15_data_feature_layer_spec.md) | Markdown | 数据与特征层规范 |
| [16_technical_indicator_catalog.md](16_technical_indicator_catalog.md) | Markdown | 技术指标目录 |
| [2026-08-28-industry-graph-frontend.md](2026-08-28-industry-graph-frontend.md) | Markdown | 产业链/供应链图谱前端功能设计 |
| [21_stock_selection_engine.md](21_stock_selection_engine.md) | Markdown | 选股引擎架构 |
| [22_sector_rotation_spec.md](22_sector_rotation_spec.md) | Markdown | 板块轮动 spec |
| [24_daban_strategy_detail.md](24_daban_strategy_detail.md) | Markdown | 打板策略细节 |
| [25_multifactor_strategy_detail.md](25_multifactor_strategy_detail.md) | Markdown | 多因子策略细节 |
| [26_event_driven_strategy_detail.md](26_event_driven_strategy_detail.md) | Markdown | 事件驱动策略细节 |
| [27_second_batch_strategies.md](27_second_batch_strategies.md) | Markdown | 第二批次策略·价值反转与动量趋势 |
| [28_sentiment_cycle_trading.md](28_sentiment_cycle_trading.md) | Markdown | 情绪周期×交易决策 |
| [30_multi_strategy_concurrency.md](30_multi_strategy_concurrency.md) | Markdown | 多策略并发架构 |
| [31_position_sizing.md](31_position_sizing.md) | Markdown | 仓位算法（分层裁定落地） |
| [32_firm_risk_aggregator.md](32_firm_risk_aggregator.md) | Markdown | FirmRiskAggregator 逻辑（组合层风险聚合） |
| [33_budget_change_handler.md](33_budget_change_handler.md) | Markdown | BudgetChangeHandler 三级升级 |
| [34_regime_meta_allocator.md](34_regime_meta_allocator.md) | Markdown | RegimeMetaAllocator 参数 |
| [35_drawdown_protocol_impl.md](35_drawdown_protocol_impl.md) | Markdown | 回撤 Protocol 落地 spec |
| [36_var_es_monitoring.md](36_var_es_monitoring.md) | Markdown | VaR/ES 与波动率监控 |
| [37_liquidity_crisis_protocol.md](37_liquidity_crisis_protocol.md) | Markdown | 流动性危机处理 |
| [40_execution_broker.md](40_execution_broker.md) | Markdown | 下单对接与撮合（执行层） |
| [41_buy_flow.md](41_buy_flow.md) | Markdown | 买入流 spec |
| [42_sell_flow.md](42_sell_flow.md) | Markdown | 卖出流 spec |
| [43_compliance_discipline.md](43_compliance_discipline.md) | Markdown | 合规与交易纪律体系 |
| [45_warroom_playbook.md](45_warroom_playbook.md) | Markdown | 作战手册体系（作战室）施工设计——预案/验证/执行跟踪三位一体 |
| [53_simulation_live_path.md](53_simulation_live_path.md) | Markdown | 模拟与实盘验证路径 |
| [54_reconciliation_attribution.md](54_reconciliation_attribution.md) | Markdown | 对账归因 |
| [55_monitoring_review.md](55_monitoring_review.md) | Markdown | 监控告警与复盘 |
| [61_lifecycle_multi_ai.md](61_lifecycle_multi_ai.md) | Markdown | 策略生命周期与多 AI 协作 |
| [63_data_utilization_audit.md](63_data_utilization_audit.md) | Markdown | 业务数据资产利用率审查与施工计划 |
| [64_data_source_download_spec.md](64_data_source_download_spec.md) | Markdown | 数据源与下载体系规范 |
| [65_git_safety_governance.md](65_git_safety_governance.md) | Markdown | Git 安全治理体系——alias 失效修复与多层防护施工总案（Trae IDE 专用） |
| [66_commit_queue_serialization.md](66_commit_queue_serialization.md) | Markdown | 提交队列串行化——多 AI 并发施工的集成层总案（三层防护：队列串行 + worktree 隔离 + plumbing 拦截） |
| [67_news_data_dedup_design.md](67_news_data_dedup_design.md) | Markdown | news_data 引擎级去重设计 |
| [68_code_algorithm_review_pipeline.md](68_code_algorithm_review_pipeline.md) | Markdown | 代码与算法多模型审查流水线 |
| [69_trading_decision_map.md](69_trading_decision_map.md) | Markdown | 交易决策地图（Trading Decision Map）——决策内容索引层设计备忘 |
| [90_methodology_open_questions.md](90_methodology_open_questions.md) | Markdown | 方法论约束遗留提案 |
| [91_density_prediction.md](91_density_prediction.md) | Markdown | 密度预测与 QNN 远期愿景 |
| [93_qmt_file_bridge_playbook.md](93_qmt_file_bridge_playbook.md) | Markdown | 大QMT文件桥双向通道操作手册（miniQMT 替代方案） |
| [94_crypto_quant_expansion.md](94_crypto_quant_expansion.md) | Markdown | 数字货币量化扩展设计 |
| [95_crypto_system_blueprint.md](95_crypto_system_blueprint.md) | Markdown | 数字货币交易系统建设总览（一级→二级→三级结构） |
| [96_tdm_v13_validation_metadata.md](96_tdm_v13_validation_metadata.md) | Markdown | TDM v1.3——节点验证元数据、衰减联动与重要性分级（SR 11-7 对齐） |
| [construction_progress_tracker.md](construction_progress_tracker.md) | Markdown | 施工进度总跟踪表（并发施工队分配/进度/反馈/核验） |
| [handoff_construction_coordinator.md](handoff_construction_coordinator.md) | Markdown | 施工统筹会话交接包（新统筹会话上下文恢复入口） |
| [observability_contract_todo.md](observability_contract_todo.md) | Markdown | Observability Contract Todo |
| [pre_expiry_full_backlog_roadmap.md](pre_expiry_full_backlog_roadmap.md) | Markdown | pre_expiry_full_backlog_roadmap.md |

## 导航

- [上级目录](../index.md)
