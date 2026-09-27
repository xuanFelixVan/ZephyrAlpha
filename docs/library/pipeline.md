---
asset_id: "DOC:docs/library/pipeline.md"
ttl: "permanent"
doc_type: "index"
---

# 管线馆（生成视图，构建于总账 lib_assets；真源在资产本体）

- 条目数（本页列出）：83｜馆内总数：83
- 索书号使用法：本页 asset_id 即本页身份；查任意资产用 `python -m zephyr.library.lookup <关键词>`

| asset_id | kind | status | home |
|---|---|---|---|
| FILE:scripts/construction/finalize_tasks.py | file | active | scripts/construction/finalize_tasks.py |
| FILE:scripts/governance/_tasks/__init__.py | file | active | scripts/governance/_tasks/__init__.py |
| FILE:scripts/governance/_tasks/list_phase0_tasks.py | file | active | scripts/governance/_tasks/list_phase0_tasks.py |
| FILE:scripts/governance/_tasks/task_show.py | file | active | scripts/governance/_tasks/task_show.py |
| FILE:scripts/governance/_tasks/task_summary.py | file | active | scripts/governance/_tasks/task_summary.py |
| FILE:scripts/register_aux_tasks.ps1 | file | active | scripts/register_aux_tasks.ps1 |
| FILE:scripts/register_counter_trend_feeder_tasks.ps1 | file | active | scripts/register_counter_trend_feeder_tasks.ps1 |
| FILE:scripts/register_guard_tasks.ps1 | file | active | scripts/register_guard_tasks.ps1 |
| FILE:src/zephyr/data/config/tasks.yaml | file | active | src/zephyr/data/config/tasks.yaml |
| TOOL:mcp:_base_server | mcp_tool | active | mcp:_base_server |
| TOOL:mcp:base_server | mcp_tool | active | mcp:base_server |
| TOOL:mcp:blueprint_search | mcp_tool | active | mcp:blueprint_search |
| TOOL:mcp:blueprint_search_server | mcp_tool | active | mcp:blueprint_search_server |
| TOOL:mcp:clone_guard | mcp_tool | active | mcp:clone_guard |
| TOOL:mcp:definitions | mcp_tool | active | mcp:definitions |
| TOOL:mcp:doc_guard_server | mcp_tool | active | mcp:doc_guard_server |
| TOOL:mcp:gate_engine | mcp_tool | active | mcp:gate_engine |
| TOOL:mcp:gate_engine_server | mcp_tool | active | mcp:gate_engine_server |
| TOOL:mcp:gateway_server | mcp_tool | active | mcp:gateway_server |
| TOOL:mcp:global_conventions | mcp_tool | active | mcp:global_conventions |
| TOOL:mcp:governance | mcp_tool | active | mcp:governance |
| TOOL:mcp:governance_server | mcp_tool | active | mcp:governance_server |
| TOOL:mcp:intent_router | mcp_tool | active | mcp:intent_router |
| TOOL:mcp:mcp_gateway | mcp_tool | active | mcp:mcp_gateway |
| TOOL:mcp:red_blue_validator | mcp_tool | active | mcp:red_blue_validator |
| TOOL:mcp:resource_optimization | mcp_tool | active | mcp:resource_optimization |
| TOOL:mcp:rule_discovery | mcp_tool | active | mcp:rule_discovery |
| TOOL:mcp:rule_discovery_server | mcp_tool | active | mcp:rule_discovery_server |
| TOOL:mcp:sandbox | mcp_tool | active | mcp:sandbox |
| TOOL:mcp:sandbox_server | mcp_tool | active | mcp:sandbox_server |
| TOOL:mcp:sentinel_server | mcp_tool | active | mcp:sentinel_server |
| TOOL:mcp:session_handoff | mcp_tool | active | mcp:session_handoff |
| TOOL:mcp:task_manager | mcp_tool | active | mcp:task_manager |
| TOOL:mcp:task_manager_server | mcp_tool | active | mcp:task_manager_server |
| TOOL:mcp:telemetry | mcp_tool | active | mcp:telemetry |
| TOOL:mcp:telemetry_server | mcp_tool | active | mcp:telemetry_server |
| TOOL:mcp:vector_memory | mcp_tool | active | mcp:vector_memory |
| TOOL:mcp:vector_memory_server | mcp_tool | active | mcp:vector_memory_server |
| MOD:src/zephyr/library/collectors/schtasks_collector.py | module | active | src/zephyr/library/collectors/schtasks_collector.py |
| TASK:schtasks:/ZephyrAlpha-AI-Wrapper-Inject | task | active | schtasks:\ZephyrAlpha-AI-Wrapper-Inject |
| TASK:schtasks:/ZephyrAlpha-CH-OptimizeMerge-Weekly | task | active | schtasks:\ZephyrAlpha-CH-OptimizeMerge-Weekly |
| TASK:schtasks:/ZephyrAlpha-DailyBackup | task | active | schtasks:\ZephyrAlpha-DailyBackup |
| TASK:schtasks:/ZephyrAlpha-IOCheck-Monthly | task | active | schtasks:\ZephyrAlpha-IOCheck-Monthly |
| TASK:schtasks:/ZephyrAlpha-WeeklyVMBackup | task | active | schtasks:\ZephyrAlpha-WeeklyVMBackup |
| TASK:schtasks:/ZephyrAlpha_AltFxECB | task | active | schtasks:\ZephyrAlpha_AltFxECB |
| TASK:schtasks:/ZephyrAlpha_BdpanTickWatch | task | active | schtasks:\ZephyrAlpha_BdpanTickWatch |
| TASK:schtasks:/ZephyrAlpha_BoardIndexRealtime | task | active | schtasks:\ZephyrAlpha_BoardIndexRealtime |
| TASK:schtasks:/ZephyrAlpha_C4Exam | task | active | schtasks:\ZephyrAlpha_C4Exam |
| TASK:schtasks:/ZephyrAlpha_C4Exam_Full0916 | task | active | schtasks:\ZephyrAlpha_C4Exam_Full0916 |
| TASK:schtasks:/ZephyrAlpha_C4Exam_OneShot0915 | task | active | schtasks:\ZephyrAlpha_C4Exam_OneShot0915 |
| TASK:schtasks:/ZephyrAlpha_CHHealthProbe | task | active | schtasks:\ZephyrAlpha_CHHealthProbe |
| TASK:schtasks:/ZephyrAlpha_ConfigCheck | task | active | schtasks:\ZephyrAlpha_ConfigCheck |
| TASK:schtasks:/ZephyrAlpha_DataScheduler | task | active | schtasks:\ZephyrAlpha_DataScheduler |
| TASK:schtasks:/ZephyrAlpha_DeadmanSwitch | task | active | schtasks:\ZephyrAlpha_DeadmanSwitch |
| TASK:schtasks:/ZephyrAlpha_F06Grid | task | active | schtasks:\ZephyrAlpha_F06Grid |
| TASK:schtasks:/ZephyrAlpha_FactoryLaneC | task | active | schtasks:\ZephyrAlpha_FactoryLaneC |
| TASK:schtasks:/ZephyrAlpha_FactoryLaneC_Full0916 | task | active | schtasks:\ZephyrAlpha_FactoryLaneC_Full0916 |
| TASK:schtasks:/ZephyrAlpha_FactoryLaneC_OneShot0915 | task | active | schtasks:\ZephyrAlpha_FactoryLaneC_OneShot0915 |
| TASK:schtasks:/ZephyrAlpha_GateFullTreeAudit | task | active | schtasks:\ZephyrAlpha_GateFullTreeAudit |
| TASK:schtasks:/ZephyrAlpha_IndexMinuteEOD | task | active | schtasks:\ZephyrAlpha_IndexMinuteEOD |
| TASK:schtasks:/ZephyrAlpha_IntradayFundFlow | task | active | schtasks:\ZephyrAlpha_IntradayFundFlow |
| TASK:schtasks:/ZephyrAlpha_MeasureCalibration | task | active | schtasks:\ZephyrAlpha_MeasureCalibration |
| TASK:schtasks:/ZephyrAlpha_NightlySentiment | task | active | schtasks:\ZephyrAlpha_NightlySentiment |
| TASK:schtasks:/ZephyrAlpha_OllamaServe | task | active | schtasks:\ZephyrAlpha_OllamaServe |
| TASK:schtasks:/ZephyrAlpha_PaperSession | task | active | schtasks:\ZephyrAlpha_PaperSession |
| TASK:schtasks:/ZephyrAlpha_PatternMining | task | active | schtasks:\ZephyrAlpha_PatternMining |
| TASK:schtasks:/ZephyrAlpha_PostSettlement | task | active | schtasks:\ZephyrAlpha_PostSettlement |
| TASK:schtasks:/ZephyrAlpha_ProcessReaper | task | active | schtasks:\ZephyrAlpha_ProcessReaper |
| TASK:schtasks:/ZephyrAlpha_QMTWatchdog | task | active | schtasks:\ZephyrAlpha_QMTWatchdog |
| TASK:schtasks:/ZephyrAlpha_RSSHub | task | active | schtasks:\ZephyrAlpha_RSSHub |
| TASK:schtasks:/ZephyrAlpha_ResourceMorningReport | task | active | schtasks:\ZephyrAlpha_ResourceMorningReport |
| TASK:schtasks:/ZephyrAlpha_ResourceRegenCheck | task | active | schtasks:\ZephyrAlpha_ResourceRegenCheck |
| TASK:schtasks:/ZephyrAlpha_ResourceSamplerScan | task | active | schtasks:\ZephyrAlpha_ResourceSamplerScan |
| TASK:schtasks:/ZephyrAlpha_ResourceSamplerWriteback | task | active | schtasks:\ZephyrAlpha_ResourceSamplerWriteback |
| TASK:schtasks:/ZephyrAlpha_ResourceViewPublish | task | active | schtasks:\ZephyrAlpha_ResourceViewPublish |
| TASK:schtasks:/ZephyrAlpha_SectorSnapshot | task | active | schtasks:\ZephyrAlpha_SectorSnapshot |
| TASK:schtasks:/ZephyrAlpha_TTLRejudgeDaily | task | active | schtasks:\ZephyrAlpha_TTLRejudgeDaily |
| TASK:schtasks:/ZephyrAlpha_TickSubscriber | task | active | schtasks:\ZephyrAlpha_TickSubscriber |
| TASK:schtasks:/ZephyrAlpha_TradingWatchdog | task | active | schtasks:\ZephyrAlpha_TradingWatchdog |
| TASK:schtasks:/ZephyrAlpha_TraeCacheCleanup | task | active | schtasks:\ZephyrAlpha_TraeCacheCleanup |
| TASK:schtasks:/ZephyrAlpha_WeeklyRest | task | active | schtasks:\ZephyrAlpha_WeeklyRest |
| TASK:schtasks:/ZephyrAlpha_WorktreeDriftWatchdog | task | active | schtasks:\ZephyrAlpha_WorktreeDriftWatchdog |
| TASK:schtasks:/tilib_indicator_backfill_nightly | task | active | schtasks:\tilib_indicator_backfill_nightly |
