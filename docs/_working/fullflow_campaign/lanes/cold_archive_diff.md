---
ttl: task_bound
completes_when: 冷库差集普查车道 st-ff-cold-20260918 —— 三态冷备逐件差集分类 + ③ 类恢复到磁盘 + 队列态孤儿第二路普查，全部产出交付总包
---

# 冷库差集普查报告（车道 st-ff-cold-20260918）

冷备源: `G:/zephyr_cold/30_corpus/fullflow_harvest/20260918-194729/`  ·  普查时 HEAD=4fb7bc162237e0c574f67c7472bfa82e4e1efb8d  ·  模式=write

> 判据：主冷备(worktree>index>untracked) 与 HEAD/磁盘/当前index 逐件 sha256 比对；
> ③ 方向以**去换行后字节严格超集 + 磁盘已回 HEAD 态或消失**双条件机械判定，不用时间戳。
> 本文只普查+救到磁盘，未 git add / 未 commit（落地由总包派工）。

## ① 四态计数（闭合=去重件数 683）

| 态 | 含义 | 件数 |
|----|------|------|
| ① landed | 已安全落地（增量已在 HEAD） | 72 |
| ② untouched | 仍在盘上未动（磁盘==冷备） | 86 |
| ③ wiped | 疑似被抹·需救回（磁盘回HEAD/消失且冷备带字节增量） | 121 |
| ④ disk_newer | 冷备更旧/无字节增量（磁盘前进或HEAD已更新，不动） | 404 |
| 合计 | | 683 |

检出 ③ 共 121 件；本次恢复 121 件；阻塞 0 件（逐件原因见下）。

## ② ③ 类逐件清单

归属车道=按路径前缀**推断**（R-018：推断级，非亲验）。行数=去 CR 后冷备较当前磁盘净增。

| path | 归属车道(推断) | 冷备层 | +行/+字节 | 已恢复 | 复解析 | 阻塞 |
|------|------|------|------|------|------|------|
| `scripts/governance/oneoff/data_domain_audit_report_db.md` | 治理脚本线 | worktree | +3632L/+541663B | 是 | skip(nono-code) | - |
| `docs/_working/2026-09-18-institutional-architecture-review.md` | 工作/交接文档线 | index | +213L/+22143B | 是 | skip(nono-code) | - |
| `docs/_working/2026-09-18-HANDOFF-PROMPT.md` | 工作/交接文档线 | index | +159L/+11826B | 是 | skip(nono-code) | - |
| `docs/_working/2026-09-18-issue-inventory-full.md` | 工作/交接文档线 | index | +103L/+11479B | 是 | skip(nono-code) | - |
| `scripts/governance/align_battle_map.py` | 全景图/战斗地图对齐线 | index | +233L/+11053B | 是 | py_compile=OK | - |
| `docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml` | 注册表生成器(可再生) | index | +182L/+10761B | 是 | yaml=OK | - |
| `scripts/governance/d5_architecture/generators/generate_battle_map_diagram.py` | 全景图/战斗地图对齐线 | index | +143L/+7392B | 是 | py_compile=OK | - |
| `docs/01_policies_and_standards/_registry/catalogs/battle_map_domain_policy.yaml` | 注册表生成器(可再生) | index | +102L/+7270B | 是 | yaml=OK | - |
| `src/zephyr/frontend/dashboard/web/features/resourceweek/rw-data.js` | 核心 src 线 | worktree | +247L/+6967B | 是 | skip(nono-code) | - |
| `scripts/governance/d5_architecture/generators/externalize_algo_flow.py` | 全景图/战斗地图对齐线 | worktree | +105L/+6722B | 是 | py_compile=OK | - |
| `scripts/governance/d3_metadata/check_registry_consistency.py` | 治理脚本线 | worktree | +102L/+5572B | 是 | py_compile=OK | - |
| `docs/_working/tdchain_mine/a0_master_ledger.md` | 工作/交接文档线 | index | +68L/+4546B | 是 | skip(nono-code) | - |
| `docs/_working/resource_schedule/morning_report/latest.md` | 工作/交接文档线 | worktree | +12L/+3395B | 是 | skip(nono-code) | - |
| `docs/01_policies_and_standards/_registry/catalogs/alert_threshold_registry.yaml` | 注册表生成器(可再生) | index | +76L/+3366B | 是 | yaml=OK | - |
| `src/zephyr/data/config/tasks.yaml` | 数据集成线 | index | +-4L/+2905B | 是 | yaml=OK | - |
| `data/crypto/universe_manifest.csv` | 数据资产线 | worktree | +50L/+2532B | 是 | skip(nono-code) | - |
| `src/zephyr/strategy_pipeline/pipeline_events.py` | residG/pf_alloc 危机闸线(接线宿主) | worktree | +32L/+2469B | 是 | py_compile=OK | - |
| `docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +1L/+2165B | 是 | skip(nono-code) | - |
| `docs/03_modules/_cross_layer/gate_engine/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+2001B | 是 | skip(nono-code) | - |
| `docs/_working/residual_construction/00_master_ledger.md` | 工作/交接文档线 | index | +8L/+1937B | 是 | skip(nono-code) | - |
| `tests/governance/rule_bridge/test_session_worktree_audit_wrapper.py` | 测试线 | index | +26L/+1706B | 是 | py_compile=OK | - |
| `docs/03_modules/_cross_layer/model_capability_exam/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+1447B | 是 | skip(nono-code) | - |
| `scripts/governance/d5_architecture/generators/generate_panorama_registry.py` | 全景图/战斗地图对齐线 | index | +21L/+1442B | 是 | py_compile=OK | - |
| `docs/registry_of_registries.yaml` | 文档线 | worktree | +28L/+1426B | 是 | yaml=OK | - |
| `docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+944B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_research/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+927B | 是 | skip(nono-code) | - |
| `scripts/governance/apply_resource_plan.py` | 治理脚本线 | index | +22L/+863B | 是 | py_compile=OK | - |
| `scripts/governance/d5_architecture/generators/generate_trading_map_diagram.py` | 全景图/战斗地图对齐线 | worktree | +10L/+826B | 是 | py_compile=OK | - |
| `tests/sell_decision/test_stop_loss_strategy.py` | 测试线 | index | +12L/+733B | 是 | py_compile=OK | - |
| `docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+715B | 是 | skip(nono-code) | - |
| `src/zephyr/gov_enforcement/rule_bridge/session_worktree.py` | 核心 src 线 | index | +8L/+704B | 是 | py_compile=OK | - |
| `src/zephyr/gov_enforcement/commit_gates/depgraph_write_path_gate.py` | 核心 src 线 | worktree | +6L/+678B | 是 | py_compile=OK | - |
| `docs/03_modules/_domain_signal/seat_pattern_analyzer/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+602B | 是 | skip(nono-code) | - |
| `src/zephyr/backtest/core/engine_base.py` | 核心 src 线 | worktree | +3L/+601B | 是 | py_compile=OK | - |
| `docs/03_modules/_domain_trading/trigger_registry/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+549B | 是 | skip(nono-code) | - |
| `src/zephyr/signal_ashare/ml_forecast/__init__.py` | 核心 src 线 | index | +2L/+513B | 是 | py_compile=OK | - |
| `docs/03_modules/_domain_regime/regime_detector/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+463B | 是 | skip(nono-code) | - |
| `scripts/governance/d5_architecture/validators/validate_strategy_production_map.py` | 全景图/战斗地图对齐线 | worktree | +4L/+402B | 是 | py_compile=OK | - |
| `src/zephyr/signal_ashare/sector/__init__.py` | 核心 src 线 | index | +2L/+362B | 是 | py_compile=OK | - |
| `scripts/governance/generators/generate_resource_profile_registry.py` | 治理脚本线 | index | +8L/+346B | 是 | py_compile=OK | - |
| `scripts/governance/generators/generate_skeleton_health.py` | 治理脚本线 | index | +7L/+343B | 是 | py_compile=OK | - |
| `docs/03_modules/_domain_reporting/ashare_performance_audit/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+307B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_reporting/risk_report_engine/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+298B | 是 | skip(nono-code) | - |
| `scripts/governance/generate_governance_map.py` | 治理脚本线 | index | +7L/+297B | 是 | py_compile=OK | - |
| `scripts/governance/generators/generate_resource_morning_report.py` | 治理脚本线 | index | +7L/+290B | 是 | py_compile=OK | - |
| `scripts/governance/d8_doc_sync/algo_flow_reverse_orphan_reconciler.py` | 治理脚本线 | index | +7L/+282B | 是 | py_compile=OK | - |
| `docs/03_modules/_domain_reporting/report_publisher/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+277B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_trading/settlement_reconciliation/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+270B | 是 | skip(nono-code) | - |
| `scripts/governance/split_coordination.py` | 治理脚本线 | index | +6L/+262B | 是 | py_compile=OK | - |
| `docs/03_modules/_domain_trading/corporate_action_processor/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+246B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_reporting/realtime_pnl_dashboard/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+245B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_simulation/risk_simulator/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+244B | 是 | skip(nono-code) | - |
| `src/zephyr/signal_ashare/intraday_t0/__init__.py` | 核心 src 线 | index | +2L/+243B | 是 | py_compile=OK | - |
| `src/zephyr/signal_ashare/limit_up/__init__.py` | 核心 src 线 | index | +2L/+243B | 是 | py_compile=OK | - |
| `docs/03_modules/_domain_simulation/parameter_robustness_tester/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+232B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_regime/regime_cycle_analyzer/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+228B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_simulation/deflated_sharpe_calculator/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+225B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_reporting/report_version_manager/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+224B | 是 | skip(nono-code) | - |
| `src/zephyr/signal_ashare/sentiment/__init__.py` | 核心 src 线 | index | +2L/+221B | 是 | py_compile=OK | - |
| `docs/03_modules/_domain_simulation/look_ahead_bias_detector/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+218B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_simulation/sharpe_calculator_fixer/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+218B | 是 | skip(nono-code) | - |
| `src/zephyr/signal_ashare/screening/__init__.py` | 核心 src 线 | index | +2L/+217B | 是 | py_compile=OK | - |
| `docs/03_modules/_cross_layer/cd_pipeline/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+215B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_risk/liquidity_crisis_manager/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+211B | 是 | skip(nono-code) | - |
| `scripts/governance/scan_offrepo_assets.py` | 治理脚本线 | index | +5L/+207B | 是 | py_compile=OK | - |
| `docs/03_modules/_domain_risk/alert_generator/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+202B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_risk/fhs_engine/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+201B | 是 | skip(nono-code) | - |
| `src/zephyr/backtest/core/__init__.py` | 核心 src 线 | index | +0L/+192B | 是 | py_compile=OK | - |
| `scripts/governance/commit_perf_report.py` | 治理脚本线 | index | +4L/+186B | 是 | py_compile=OK | - |
| `docs/03_modules/_domain_reporting/regulatory_report_generator/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+184B | 是 | skip(nono-code) | - |
| `scripts/governance/d3_metadata/batch_creation_tokens.py` | 治理脚本线 | index | +4L/+182B | 是 | py_compile=OK | - |
| `docs/03_modules/_domain_reporting/ashare_trade_record_template/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+181B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_reporting/report_watermark_tracker/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+175B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_risk/ashare_systemic_risk_detector/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+175B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_risk/crowding_monitor/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+175B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_risk/drawdown_tracker/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+175B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_risk/risk_budget_allocator/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+174B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_risk/tail_risk_monitor/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+174B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_risk/ashare_stop_loss_engine/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+171B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_risk/risk_decomposition/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+163B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_risk/liquidity_monitor/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+161B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_risk/var_calculator/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+161B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_trading/decision_map/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+158B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_risk/concentration_monitor/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+156B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_risk/strategy_deviation_monitor/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+156B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_reporting/review_orchestrator/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+155B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_regime/volatility_regime_alerter/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+150B | 是 | skip(nono-code) | - |
| `docs/03_modules/_cross_layer/resource_profile_registry/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+148B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_frontend/resource_week_view/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+143B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_signal/daily_condition_sensor/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+143B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_risk/operational_risk_monitor/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+141B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_risk/performance_attribution_degradation/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+141B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_risk/systemic_risk_alert_state_machine/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+141B | 是 | skip(nono-code) | - |
| `scripts/governance/commit_derived_sync.py` | 治理脚本线 | index | +3L/+139B | 是 | py_compile=OK | - |
| `docs/03_modules/_domain_risk/emergency_stop_confirmation/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+138B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_signal/tradability_preflight/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+138B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_risk/atr_stop_engine/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+137B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_risk/copula_garch_joint/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+137B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_risk/ai_agent_monitor/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+134B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_risk/model_risk_audit/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+134B | 是 | skip(nono-code) | - |
| `src/zephyr/strategy_factory/owner_band_t/__init__.py` | 核心 src 线 | index | +2L/+120B | 是 | py_compile=OK | - |
| `docs/03_modules/_domain_signal/pool_tier_maintenance/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+119B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_signal/environment_switch/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+118B | 是 | skip(nono-code) | - |
| `tests/sell_decision/test_take_profit_strategy.py` | 测试线 | index | +0L/+111B | 是 | py_compile=OK | - |
| `scripts/governance/upgrade_tdm_v13_metadata.py` | 治理脚本线 | index | +2L/+108B | 是 | py_compile=OK | - |
| `docs/03_modules/_domain_risk/drawdown_liquidation_guard/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+107B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_risk/drawdown_state_machine/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+107B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_signal/sector_conduction/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+107B | 是 | skip(nono-code) | - |
| `docs/03_modules/_domain_signal/sentiment_cycle/blueprint.md` | 蓝图生成器(可再生, 见§9.5) | worktree | +0L/+105B | 是 | skip(nono-code) | - |
| `scripts/governance/run_semantic_audit.py` | 治理脚本线 | index | +2L/+105B | 是 | py_compile=OK | - |
| `scripts/governance/standards/standards_lib.py` | 治理脚本线 | index | +2L/+102B | 是 | py_compile=OK | - |
| `scripts/governance/generators/generate_resource_week_view.py` | 治理脚本线 | index | +2L/+100B | 是 | py_compile=OK | - |
| `scripts/governance/d5_architecture/generators/report_algo_flow_author_debt.py` | 全景图/战斗地图对齐线 | index | +2L/+97B | 是 | py_compile=OK | - |
| `src/zephyr/risk/__init__.py` | 核心 src 线 | index | +2L/+75B | 是 | py_compile=OK | - |
| `data/asset_index/unified-asset-index.yaml` | 数据资产线 | worktree | +0L/+74B | 是 | yaml=OK | - |
| `scripts/governance/d3_metadata/pattern_code_fingerprint.py` | 治理脚本线 | index | +1L/+64B | 是 | py_compile=OK | - |
| `scripts/governance/registry_batch_edit.py` | 治理脚本线 | index | +1L/+64B | 是 | py_compile=OK | - |
| `src/zephyr/data/config/schedule.yaml` | 数据集成线 | index | +4L/+38B | 是 | yaml=OK | - |
| `scripts/governance/meta/validate_rules_integrity.py` | 治理脚本线 | index | +1L/+36B | 是 | py_compile=OK | - |
| `src/zephyr/strategy_factory/__init__.py` | 核心 src 线 | index | +2L/+25B | 是 | py_compile=OK | - |
| `architecture_model/index.yaml` | 未知 | index | +2L/+3B | 是 | yaml=OK | - |

## ③ 队列态孤儿（第二路普查：.runtime/commit_queue/blobs/ 全量扫）

扫 11722 个 blob，其中 3755 个带 [MODULE]/[BLUEPRINT] 注解头，81 个推断磁盘路径不存在=队列态孤儿。
（推断级别，非亲验：dotted 路径→文件路径映射可能有误；落地前须人工确认）

| blob(sha256 前12) | 字节 | [MODULE] dotted | 推断路径(候选) |
|------|------|------|------|
| 03331fd18efc… | 123417 | tests.test_git_commit_gateway | `tests/test_git_commit_gateway.py` |
| 68c47d33a58a… | 122708 | tests.test_git_commit_gateway | `tests/test_git_commit_gateway.py` |
| 1e8131e563c6… | 34097 | tests.test_create_guard | `tests/test_create_guard.py` |
| 6e164d8c5b2b… | 19972 | tests.red_blue.test_f18_governance_adversarial | `tests/red_blue/test_f18_governance_adversarial.py` |
| 2c587edd4a7c… | 19945 | tests.red_blue.test_f18_governance_adversarial | `tests/red_blue/test_f18_governance_adversarial.py` |
| 5cf0624dfa02… | 19141 | scripts.governance.d3_metadata.fix_n12_ke_naming | `scripts/governance/d3_metadata/fix_n12_ke_naming.py` |
| afee17458671… | 18533 | tests.infrastructure.test_git_batcher | `tests/infrastructure/test_git_batcher.py` |
| 93ade4494c61… | 17312 | schemas.categories.market_technical_indicator | `schemas/categories/market_technical_indicator.py` |
| c82fddda0219… | 17262 | schemas.categories.market_technical_indicator | `schemas/categories/market_technical_indicator.py` |
| cf34da2e41a2… | 17260 | scripts.migration.generate_path_migration_mapping | `scripts/migration/generate_path_migration_mapping.py` |
| 4dca33aeea28… | 17193 | scripts.governance.d3_metadata.fix_n06_module_id_prefix | `scripts/governance/d3_metadata/fix_n06_module_id_prefix.py` |
| 2117f14b4bec… | 15654 | schemas.categories.market_technical_indicator | `schemas/categories/market_technical_indicator.py` |
| 8128942cfdcd… | 14557 | schemas.categories.market_technical_indicator | `schemas/categories/market_technical_indicator.py` |
| dbf99f5cec9b… | 13062 | schemas.categories.market_technical_indicator | `schemas/categories/market_technical_indicator.py` |
| 005ee85e3cb2… | 12210 | schemas.categories.market_technical_indicator | `schemas/categories/market_technical_indicator.py` |
| 0f16b5bb63b8… | 10976 | scripts.migration.test_import_fix | `scripts/migration/test_import_fix.py` |
| d6da55c92b49… | 10966 | schemas.categories.market_technical_indicator | `schemas/categories/market_technical_indicator.py` |
| d91b9c961e41… | 8864 | scripts.migration.update_non_import_refs | `scripts/migration/update_non_import_refs.py` |
| a7a4981f5f52… | 8855 | tests.test_architecture_contracts | `tests/test_architecture_contracts.py` |
| be378495ac49… | 8845 | tests.test_architecture_principles | `tests/test_architecture_principles.py` |
| 586f92c87a9a… | 8806 | scripts.migration.domain_prefix_import_fix | `scripts/migration/domain_prefix_import_fix.py` |
| 24abbed64c90… | 8423 | scripts.migration.update_imports | `scripts/migration/update_imports.py` |
| 772c196d77c5… | 8375 | scripts.migration.execute_move | `scripts/migration/execute_move.py` |
| 71723765a22a… | 8312 | scripts.migration.verify_batch | `scripts/migration/verify_batch.py` |
| 7208baf1eac9… | 8178 | scripts.migration.shared_import_fix | `scripts/migration/shared_import_fix.py` |
| 1ec21063dde5… | 8107 | scripts.migration.comprehensive_import_fix | `scripts/migration/comprehensive_import_fix.py` |
| 6037978fc9c1… | 8046 | (仅BLUEPRINT) | `docs/_working/2026-09-15-pattern-certification-plan.md` |
| 0d6c72584436… | 7205 | schemas.categories.market_pattern_event | `schemas/categories/market_pattern_event.py` |
| 80cd947653af… | 7184 | schemas.categories.market_pattern_event | `schemas/categories/market_pattern_event.py` |
| f154ad971f8d… | 6889 | scripts.migration.preflight_check | `scripts/migration/preflight_check.py` |
| 48e13264bde3… | 6193 | scripts.migration.unnest_from_mcp_server | `scripts/migration/unnest_from_mcp_server.py` |
| 95976514402f… | 5434 | tests.test_data_source_reliability | `tests/test_data_source_reliability.py` |
| 2ae6588f3e67… | 5425 | tests.unit.db.test_dm400_stale_task_fix | `tests/unit/db/test_dm400_stale_task_fix.py` |
| 1de3388e660c… | 4961 | schemas.categories.backtest_strategy_screen | `schemas/categories/backtest_strategy_screen.py` |
| e9698658a88e… | 4882 | schemas.categories.backtest_node_verdict | `schemas/categories/backtest_node_verdict.py` |
| 9a78c03be271… | 4285 | schemas.categories.backtest_hypothesis_precheck | `schemas/categories/backtest_hypothesis_precheck.py` |
| d65709620876… | 4285 | schemas.categories.backtest_hypothesis_precheck | `schemas/categories/backtest_hypothesis_precheck.py` |
| 368b70f7ab23… | 4152 | scripts.migration.rollback_batch | `scripts/migration/rollback_batch.py` |
| 49d9ecece558… | 4000 | schemas.categories.market_pattern_win_rate | `schemas/categories/market_pattern_win_rate.py` |
| 8734d0d51a3a… | 3856 | tests.test_ba_dependency_manager | `tests/test_ba_dependency_manager.py` |
| b7797dc2cf3d… | 3653 | schemas.categories.market_alt_sz_marine_forecast | `schemas/categories/market_alt_sz_marine_forecast.py` |
| d829ea8e9d57… | 3492 | scripts.migration.create_target_dirs | `scripts/migration/create_target_dirs.py` |
| efb1ac1c5352… | 3251 | schemas.categories.market_alt_sz_house_presale | `schemas/categories/market_alt_sz_house_presale.py` |
| 6237b69d5fc6… | 3217 | schemas.categories.market_alt_stock_comment | `schemas/categories/market_alt_stock_comment.py` |
| e9cd3e3cc2ac… | 3212 | scripts.migration.lock_batch | `scripts/migration/lock_batch.py` |
| bd0c529410a0… | 3155 | tests.test_model_drift_monitor | `tests/test_model_drift_monitor.py` |
| 9fe42af57695… | 3147 | (仅BLUEPRINT) | `docs/03_modules/_cross_layer/gov_scripts/blueprint.md` |
| fa149cc547c0… | 3126 | schemas.categories.market_alt_sz_weather_warning | `schemas/categories/market_alt_sz_weather_warning.py` |
| 79610f3961e2… | 3110 | schemas.categories.market_alt_shipping_index | `schemas/categories/market_alt_shipping_index.py` |
| 4781097031e7… | 3038 | tests.signal_ashare.test_kronos_tsfm_predictor | `tests/signal_ashare/test_kronos_tsfm_predictor.py` |
| 2e13c309c0d8… | 3011 | schemas.categories.market_alt_sz_air_quality_region | `schemas/categories/market_alt_sz_air_quality_region.py` |
| 10e70461ed95… | 3007 | schemas.categories.market_alt_regime_signal | `schemas/categories/market_alt_regime_signal.py` |
| 26fda1c26e4a… | 2976 | schemas.categories.backtest_regime_state_anchored | `schemas/categories/backtest_regime_state_anchored.py` |
| 4445c4e52bd7… | 2949 | schemas.categories.market_alt_sz_enterprise_year | `schemas/categories/market_alt_sz_enterprise_year.py` |
| bcebaff5e61d… | 2883 | schemas.categories.market_alt_sz_market_subject | `schemas/categories/market_alt_sz_market_subject.py` |
| 8bd3459998e5… | 2816 | tests.test_ml_engineering | `tests/test_ml_engineering.py` |
| a3dc418467d2… | 2805 | schemas.categories.market_alt_sz_stat_monthly | `schemas/categories/market_alt_sz_stat_monthly.py` |
| 30a37ff61e5e… | 2735 | tests.test_cross_env_consistency | `tests/test_cross_env_consistency.py` |
| 39b9cff62732… | 2735 | schemas.categories.market_alt_sz_visibility | `schemas/categories/market_alt_sz_visibility.py` |
| ec3fd56fc7e0… | 2709 | schemas.categories.market_alt_sz_house_listing | `schemas/categories/market_alt_sz_house_listing.py` |
| 0c774bf73783… | 2708 | tests.test_data_lifecycle | `tests/test_data_lifecycle.py` |
| 9c90c9eaa9c0… | 2674 | schemas.categories.alt_sz_ground_obs | `schemas/categories/alt_sz_ground_obs.py` |
| 08d159733060… | 2654 | schemas.categories.alt_sz_env_meteor | `schemas/categories/alt_sz_env_meteor.py` |
| d16b49abd0fb… | 2650 | schemas.categories.market_alt_sz_air_quality_daily | `schemas/categories/market_alt_sz_air_quality_daily.py` |
| a29661c9371d… | 2606 | schemas.categories.market_sentiment_panel | `schemas/categories/market_sentiment_panel.py` |
| 6560bfacfd33… | 2518 | schemas.categories.alt_sz_climate_hist | `schemas/categories/alt_sz_climate_hist.py` |
| 5ddfb2bfeb7c… | 2517 | schemas.categories.market_typhoon_landfall_history | `schemas/categories/market_typhoon_landfall_history.py` |
| ab7b1f9e593d… | 2425 | schemas.categories.market_alt_sz_house_daily | `schemas/categories/market_alt_sz_house_daily.py` |
| abf85c57f37d… | 2333 | tests.test_ba_data_lifecycle | `tests/test_ba_data_lifecycle.py` |
| 97a8da7d872f… | 2271 | schemas.categories.alt_sz_reservoir_level | `schemas/categories/alt_sz_reservoir_level.py` |
| f89e96481859… | 2224 | schemas.categories.market_alt_sz_house_area | `schemas/categories/market_alt_sz_house_area.py` |
| 1d359967126b… | 2145 | schemas.categories.market_alt_sz_port_monthly | `schemas/categories/market_alt_sz_port_monthly.py` |
| 8833ed793813… | 2096 | schemas.categories.market_alt_sz_reservoir_rain_month | `schemas/categories/market_alt_sz_reservoir_rain_month.py` |
| 1a2b75b38243… | 2095 | schemas.categories.market_alt_sz_reservoir_rain_day | `schemas/categories/market_alt_sz_reservoir_rain_day.py` |
| a03a85c8258c… | 2090 | schemas.categories.market_typhoon_names | `schemas/categories/market_typhoon_names.py` |
| 716b8570c344… | 2086 | tests.signal_ashare.test_mamba_ssm_temporal_enhancer | `tests/signal_ashare/test_mamba_ssm_temporal_enhancer.py` |
| 0685a7b80035… | 2043 | tests.signal_ashare.test_xlstm_long_memory | `tests/signal_ashare/test_xlstm_long_memory.py` |
| 2f34f6edf7d2… | 2038 | schemas.categories.market_alt_sz_stat_analysis | `schemas/categories/market_alt_sz_stat_analysis.py` |
| cf681985071f… | 2017 | schemas.categories.market_alt_sz_reservoir_station | `schemas/categories/market_alt_sz_reservoir_station.py` |
| 0e8e3795bd13… | 1933 | MOD-AUTO-L3-001(暂编号) | `src/MOD-AUTO-L3-001(暂编号).py` |
| 63f33b5d0c4c… | 1147 | MOD-AUTO-L3-001(暂编号) | `src/MOD-AUTO-L3-001(暂编号).py` |

## ④ 普查件与可重跑性

- 脚本：`.runtime/tmp/st-ff-cold/census.py`（dry-run: `python census.py`；恢复: `--write`；重出报告: `--report`）
- 机读附表：`docs/_working/fullflow_campaign/lanes/cold_archive_diff.yaml`（本两件均由脚本产出，符合§9.5）
- 单件复跑：`python census.py --write --only <path>`

