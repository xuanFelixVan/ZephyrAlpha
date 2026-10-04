---
ttl: task_bound
completes_when: 孤儿分诊战役终裁落地（chief 终审+处置执行）后本册随 30/31 号转归档
title: 孤儿分诊证据包：src.zephyr.governance（158 台）
owner: st-orphtriage-20261004
---

# 41 号·分诊证据包：src.zephyr.governance（158 台）

> 宇宙口径=裁定#481；数据真源=30_attribution_table.yaml（join checker 机生）；处置=证据班建议，终裁归 GLM-5.3 chief，退役执行归 Owner 门位。
>
> tier 分布：suspect_orphan=3，wired=41，wired_by_header=77，wired_dynamic=37；初判汇总：dispute=3，mount=155

## 逐台证据（四字段+初判）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/governance/architecture_governance/__init__.py` | （无文档头，按文件名语义：__init__） | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→GOMAP（治理/安全域） ②retire→Owner 门位） |
| `src/zephyr/governance/services/__init__.py` | governance/services | 2026-09-19（15天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 15 天内有 commit（活着但零线零引）；①mount→GOMAP（治理/安全域） ②retire→Owner 门位） |
| `src/zephyr/governance/strategies/__init__.py` | Re-export wrapper: true source is zephyr.pf_core.default_equity_strategy. | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→GOMAP（治理/安全域） ②retire→Owner 门位） |
| `src/zephyr/governance/a2a/__init__.py` | Phase 1 gate marker（a2a 为 trae_028 grandfathered 缩写目录，非 kebab-case）。Implementation in zephyr.infrastructure.a2a_protocol | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/agent_spec/__init__.py` | Agent Spec — MOD-INF-019 | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/agent_spec/registry.py` | G-CT-003 契约：Agent Spec -> RBAC 能力检查. | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/architecture_governance/blueprint_code_consistency.py` | Blueprint-Code Consistency Gate — MOD-INF-022. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/architecture_governance/construction_verifier.py` | Construction Verifier — 施工验证器: 任务卡完成度+蓝图一致性检查。 | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/architecture_governance/formal_verifier.py` | Formal Verifier — v0.6.0 形式验证器: 升级规则形式化验证->一致性+完备性检测。 | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/architecture_governance/gap_analyzer.py` | Gap Analyzer — v0.8.0 间隙分析器: escalation覆盖缺口扫描+新操作类型识别。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/audit/default_attribution_engine.py` | Re-export wrapper: default_attribution_engine canonical at zephyr.reporting.default_attribution_engine. | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/audit/default_tca_engine.py` | Re-export wrapper: default_tca_engine canonical at zephyr.reporting.default_tca_engine. | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/audit/snapshot_manager.py` | SnapshotManager — Event Sourcing 快照管理（DW-0005） | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/compliance_gate_a6/__init__.py` | D_COMPLIANCE — Compliance Concrete Implementations | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/compliance_gate_a6/compliance_manager.py` | ZephyrAlpha — D_COMPLIANCE Compliance Layer — 合规规则管理器接口 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/compliance_gate_a6/compliance_mapper.py` | Compliance Mapper — D-022-13 合规映射器: 操作->法规(SOX/GDPR/MiFID)映射+审计迹。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/consumption/__init__.py` | governance.consumption — 消费面（有没有人真用）自动化件的包。 | 2026-09-29（5天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/consumption/scan_scope_converged.py` | scan_scope_converged — 波 13 §3.4 单一扫描口径的唯一定义处（壬道收敛版）。 | 2026-09-29（5天） | in=3/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/context_governance/command_chain_length_gate.py` | Command Chain Length Gate — v0.13.0 命令体积Deny退化防御器。 | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/context_governance/context_manager.py` | （无文档头，按文件名语义：context_manager） | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/context_governance/context_package.py` | Context Package — D-022-08 委托上下文包: 升级原因+证据链+历史try_trace。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/context_governance/context_recycling.py` | （无文档头，按文件名语义：context_recycling） | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/context_governance/context_switch_governor.py` | Context Switch Governor — v0.11.0 Owner上下文切换预算管理器。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/context_governance/context_waste_detector.py` | （无文档头，按文件名语义：context_waste_detector） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/context_governance/conversation_tax_detector.py` | 5.50.2 修复：原 == 0 浮点精确比较，older 含浮点求和产生 1e-17 残差时 == 0 失败， | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/context_governance/instruction_bloat_detector.py` | InstructionBloatDetector — 指令膨胀检测 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/context_governance/multi_turn_intent_analyzer.py` | Multi-Turn Intent Analyzer — v0.13.0 多轮分布式意图分析器。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/context_governance/protocol_self_context.py` | Protocol Self Context — v0.10.0 协议自维护上下文管理器。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/context_governance/think_time_model.py` | （无文档头，按文件名语义：think_time_model） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/data_governance/data_pipeline_guard.py` | Data Pipeline Guard — v0.10.0 数据管道完整性防护: schema validation+row count check+checksum verify。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/data_governance/exchange_partition_detector.py` | Exchange Partition Detector — v0.12.0 交易所网络分区检测器。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/data_governance/pricing_sync.py` | （无文档头，按文件名语义：pricing_sync） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/docs/api_doc_version_syncer.py` | ApiDocVersionSyncer — API 文档版本同步器（MOD-GOV-054）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/engine/__init__.py` | 实验管线 — Experimentation Pipeline Package | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/engine/pipeline_base.py` | 实验 — Experimentation Pipeline Layer | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/escalation/alternative_path_blocker.py` | Alternative Path Blocker — v0.13.0 替代工具路径拦截器。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/escalation/consequence_manager.py` | 清除已解决状态，使 activate 语义为"重新激活" | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/escalation/escalation_api.py` | Escalation API — v0.7.0 Service Account API: 外部系统安全触发升级，不绕过引擎。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/escalation/escalation_fatigue_manager.py` | Escalation Fatigue Manager — v0.11.0 升级疲劳管理器。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/escalation/escalation_loop_detector.py` | Escalation Loop Detector — v0.10.0 跨模块升级循环: escalate->block->auto_guard->escalate循环检测。 | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/escalation/escalation_metrics.py` | Escalation Metrics — D-022-07 指标收集器: 升级率/误升级率/响应延迟。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/escalation/escalation_models.py` | Escalation Protocol data models — MOD-INF-022 | 2026-09-16（18天） | in=10/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/escalation/escalation_smoke_tests.py` | Escalation Smoke Tests — v0.11.0 升级协议烟雾测试。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/escalation/git_hook_pre_scanner.py` | Git Hook Pre-Scanner — v0.14.0 Git操作Hook预扫描器。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/escalation/human_factors.py` | Human Factors — v0.7.0 人因工程: 通知疲劳管理+上下文简洁性+多通道notifications。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/escalation/identity_verifier.py` | Identity Verifier — D-022-12 Agent身份验证器: session_id+role+capability三元组验证。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/escalation/incident_response.py` | （无文档头，按文件名语义：incident_response） | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/escalation/order_state_escalator.py` | Order State Escalator — v0.10.0 订单状态机升级器。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/escalation/owner_absent.py` | Owner Absent — 人力缺席分级处置。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/escalation/result_types.py` | [BLUEPRINT] MOD-INF-021 \| docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/escalation/spof_checker.py` | （无文档头，按文件名语义：spof_checker） | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/evidence_pack.py` | （无文档头，按文件名语义：evidence_pack） | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/financial_governance/arbitrage_asymmetry_detector.py` | Arbitrage Asymmetry Detector — v0.11.0 跨交易所套利不对称检测器。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/financial_governance/flash_crash_guard.py` | Flash Crash Guard — v0.12.0 闪崩双轨熔断器。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/financial_governance/instrument.py` | （无文档头，按文件名语义：instrument） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/financial_governance/risk_matrix.py` | （无文档头，按文件名语义：risk_matrix） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/financial_governance/strategy_scoper.py` | Strategy Scoper — v0.6.0 策略范围隔离器: SIG/Strat/Capital多层策略隔离。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/gov_policy_manager.py` | GovPolicyManager — 治理策略管理器（MOD-GOV-052）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/indicator_usage_audit.py` | indicator_usage_audit — 指标消费活性台账（MOD-GOV-INDUSAGE，协议 v2.0 指标域落地）。 | 2026-09-29（5天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/intelligence_governance/aisg_sandbox.py` | AISG Sandbox Testing — AI Security Gateway 沙箱验证 (INV-015 升级) | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/intelligence_governance/autonomy_dashboard.py` | Autonomy Dashboard — AI 自主感知健康仪表。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/intelligence_governance/confidence_estimator.py` | Confidence Estimator — D-022-05 置信度评估器: certainty×evidence×risk三维评估。 | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/intelligence_governance/confidence_quantifier.py` | ConfidenceQuantifier — AI 置信度量化。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/intelligence_governance/continuous_trust.py` | Continuous Trust Ledger — 持续信任评估引擎。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/intelligence_governance/cross_assistant_adapter.py` | Cross-Assistant Adapter — v0.6.0 Trae/Cursor/Windsurf/Codex/Wedata统一升级接口。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/intelligence_governance/delegation_manager.py` | Delegation Manager — D-022-02 自动委托协议。 | 2026-08-31（34天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/intelligence_governance/meta_confidence.py` | Meta-Confidence — D-022-10 Agent对自身判定置信度的自评+历史校准。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/intelligence_governance/model_version_detector.py` | Model Version Detector — v0.10.0 模型版本突变检测: model version change->degraded auto_guard。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/intelligence_governance/mvep_orchestrator.py` | MVEP Orchestrator — v0.11.0 Minimum Viable Escalation Protocol调度器。 | 2026-08-31（34天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/intelligence_governance/self_benchmark.py` | Self-Benchmark (W3-7) — 5 组已知对自验证 + 引擎退化告警. | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/intelligence_governance/self_validator.py` | Self Validator — v0.10.0 升级协议自验证器: protocol自身规则+代码一致性自检。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/intelligence_governance/subagent_hook_propagator.py` | Subagent Hook Propagator — v0.13.0 子Agent Hook旁路防护器。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/meta_question/exam_loop/arbitration.py` | arbitration — 考试矛盾机械检测（C1-C3）与三取二裁定（13§2 仲裁链的计算核）。 | 2026-09-26（8天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/meta_question/exam_loop/event_codes.py` | event_codes — 考试循环簇审计事件码扩展册加载器与落账载体选择器（WO-B1）。 | 2026-09-26（8天） | in=6/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/meta_question/exam_loop/exam_plan.py` | exam_plan — 预注册考卷结构化（OSF 预注册对标）+ 功效核验 + 时间分层机检。 | 2026-09-26（8天） | in=4/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/meta_question/exam_ops.py` | exam_ops — MetaQuestionRegistry 考试生命周期簇 Mixin（状态流转/认领/考试记账 + 审计双轨）。 | 2026-09-26（8天） | in=7/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/observability_governance/analytics_base.py` | Re-export wrapper: analytics_base canonical at zephyr.reporting.analytics_base. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/observability_governance/objective_tracker.py` | Objective Tracker — v0.9.0 目标漂移检测器: agent目标函数稳定性+变更检测+rollback。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/observability_governance/projection_engine.py` | ProjectionEngine — 事件折叠为当前状态（DW-0003） | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/observability_governance/query_metrics.py` | QueryMetrics — SQL 查询性能监控装饰器（SH-DB-001 v2.0） | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/ops_governance/bandwidth_optimizer.py` | （无文档头，按文件名语义：bandwidth_optimizer） | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/ops_governance/clock_guard.py` | Clock Guard — v0.8.0 时钟完整性防御: NTP漂移检测+wall clock monotonic验证。 | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/ops_governance/coldstart_manager.py` | Coldstart Manager — v0.7.0 冷启动管理器: escalation rules加载+引擎初始化+健康检查。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/ops_governance/cost_router.py` | （无文档头，按文件名语义：cost_router） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/ops_governance/daily_ops.py` | （无文档头，按文件名语义：daily_ops） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/ops_governance/event_hook.py` | EventHook — 声明式任务系统事件订阅 | 2026-09-16（18天） | in=5/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/ops_governance/interrupt_handler.py` | Interrupt Handler — D-022-06 硬中断处理器: Owner紧急中断+优雅停止+状态保存。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/ops_governance/maintenance_window_adapter.py` | Maintenance Window Adapter — v0.10.0 计划维护窗口适配器。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/ops_governance/meta_observability.py` | Meta Observability — v0.10.0 协议自身可观测性: self loop latency+p99+edge case rate。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/ops_governance/ops_foundation.py` | （无文档头，按文件名语义：ops_foundation） | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/ops_governance/parent_child_attributor.py` | ── Stage 4 公共化（2026-07-29）：只读 properties ── | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/ops_governance/roi_calculator.py` | （无文档头，按文件名语义：roi_calculator） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/ops_governance/tco_model.py` | （无文档头，按文件名语义：tco_model） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/ops_governance/time_sync.py` | （无文档头，按文件名语义：time_sync） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/ops_governance/timeout_guard.py` | ── Stage 4 公共化（2026-07-29）：只读 properties ── | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/persistence/base_repo.py` | [BLUEPRINT] SH-DB-001 \| docs/03_modules/_cross_layer/database/blueprint.md | 2026-09-05（29天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/persistence/database_manager.py` | DatabaseManager — 连接池 + 健康检查 + 自动备份 + WAL checkpoint（SH-DB-001 v2.0） | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/persistence/intent_keyword_mapper.py` | IntentKeywordMapper - Stage 1 of three-stage intent parsing ( | 2026-09-16（18天） | in=3/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/persistence/intent_parser.py` | IntentParser · 意图三阶段级联解析器（V-09） | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/persistence/pg_wrapper.py` | pg_wrapper.py — psycopg2 connection 的 sqlite3 兼容 execute() 包装器（单一规范副本）。 | 2026-09-16（18天） | in=4/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/persistence/protocol_state_store.py` | Protocol State Store — v0.10.0 协议运行时状态持久化: JSON snapshot+recovery state+crash恢复。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/persistence/sqlite_schema.py` | SQLite 元数据层 Schema DDL + 版本化迁移框架（T-1-02 + SH-DB-001 v2.0） | 2026-09-16（18天） | in=31/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/registry_ledger/registry_ledger_ddl.py` | registry_ledger DDL 聚合与 _schema_version 台账（真源=schemas/categories/registry_ledger/）。 | 2026-09-25（9天） | in=3/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/registry_projection/model.py` | model.py — 投影快照模型与提取器（capability_canonical_file_registry 先行）。 | 2026-09-25（9天） | in=4/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/registry_projection/renderer.py` | renderer.py — YAML := render(snapshot) 纯函数投影器。 | 2026-10-03（1天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/resilience_governance/__init__.py` | （无文档头，按文件名语义：__init__） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/resilience_governance/account_isolator.py` | Account Isolator — v0.10.0 多账户升级隔离器。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/resilience_governance/blast_radius.py` | blast_radius — MOD-INF-028 §3.1 Stage 9 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/resilience_governance/broker_resilience.py` | （无文档头，按文件名语义：broker_resilience） | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/resilience_governance/deadlock_detector.py` | Deadlock Detector — D-022-04 多Agent死锁+循环依赖检测+超时破解。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/resilience_governance/decision_fatigue.py` | （无文档头，按文件名语义：decision_fatigue） | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/resilience_governance/decision_fatigue_cli.py` | （无文档头，按文件名语义：decision_fatigue_cli） | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/resilience_governance/engine_sandbox.py` | EngineSandbox — D-022-08 OS-level sandboxing for the escalation engine. | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/resilience_governance/fail_mode_manager.py` | ── Stage 4 公共化（2026-07-29）：只读 properties ── | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/resilience_governance/policy_sandbox.py` | 项目根 = src/zephyr/governance/resilience_governance -> 上溯 4 级 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/resilience_governance/process_isolator.py` | Process Isolator — v0.6.0 进程隔离器: engine运行在独立进程+资源限制+crash恢复。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/resilience_governance/witness_isolation.py` | Witness Isolation — v0.8.0 Witness隔离: N版本decision验证+投票机制+majority判定。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/rollback/__init__.py` | rollback module — Phase 1 governance module. | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/rollback/contracts.py` | rollback/contracts.py — G-CT-002 Rollback 契约（re-export）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/rule_patterns.py` | rule_patterns.py — 治理规则正则 + 安全审计模式唯一真源 (SSoT) | 2026-09-16（18天） | in=5/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/security_governance/__init__.py` | （无文档头，按文件名语义：__init__） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/security_governance/anti_automation_bias.py` | Anti-Automation Bias — D-022-09 mandatory human oversight enforcement. | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/security_governance/api_response_sanitizer.py` | API Response Sanitizer — v0.9.0 API响应清洗器: 外部API返回内容清洗+injection检测。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/security_governance/bare_repo_scanner.py` | Bare Repo Scanner — v0.14.0 嵌入式裸仓库检测器。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/security_governance/compositional_safety_tester.py` | Compositional Safety Tester — v0.14.0 组合性不安全测试器。 | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/security_governance/config_scanner.py` | Config Scanner — v0.9.0 AI配置文件注入扫描器: 检测AI修改的配置+注入攻击。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/security_governance/credential_guard.py` | Credential Guard — v0.7.0 密钥泄露防护: env检测+git log扫描+运行时脱敏。 | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/security_governance/github_api_guard.py` | GitHub API Guard — v0.9.0 Comment and Control防御: PR评论命令注入检测+限制。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/security_governance/hooks_integrity_guard.py` | Hooks Integrity Guard — v0.11.0 Hooks自编辑防护器。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/security_governance/ipi_defense.py` | ── Stage 4 公共化（2026-07-29）：只读 properties ── | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/security_governance/memory_poison_guard.py` | Memory Poison Guard — v0.9.0 记忆投毒防护: Memory写入内容审计+恶意注入检测。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/security_governance/persuasion_detector.py` | Persuasion Detector — D-022-09 心理说服检测: 对抗语气+恳求+绕过指令。 | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/security_governance/poison_cascade_detector.py` | ── Stage 4 公共化（2026-07-29）：只读 properties ── | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/security_governance/sbom_guard.py` | SBOM Guard — v0.8.0 SBOM供应链防护: 依赖版本锁定+脆弱性扫描+cve告警。 | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/security_governance/security_config_scanner.py` | Security Config Scanner — v0.13.0 缺失安全配置扫描器。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/security_governance/security_gateway_base.py` | D_COMPLIANCE — Governance & Compliance Layer | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/security_governance/vibe_security_verify.py` | Vibe Security Verifier — v0.9.0 Vibe Coding安全验证器: AI生成代码安全基线检查。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/security_governance/vibe_verify_integration.py` | VibeVerify Integration — v0.9.0 VibeVerify集成器: auto_guard级别+增量修复+confidence回传。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/semantic_audit/__init__.py` | 治本（AI-AUDIT12 门面断裂修复）：原 __init__ 仅声明 __all__（65项）而零导入—— | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/semantic_audit/alignment_engine.py` | [BLUEPRINT] MOD-INF-028 — 对齐引擎 Stage 4 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/semantic_audit/compliance_map.py` | compliance_map — re-export shim for zephyr.gov_audit.compliance_map (MOD-INF-020 canonical). | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/semantic_audit/feedback_self_audit.py` | feedback_self_audit — re-export shim for zephyr.gov_audit.feedback_self_audit (MOD-INF-020 canonical). | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/semantic_audit/fix_prioritizer.py` | [BLUEPRINT] MOD-INF-028 — 修复优先级排序 Stage 8 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/semantic_audit/fix_result_prioritizer.py` | fix_prioritizer — MOD-INF-028 §3.1 Stage 8 | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/semantic_audit/issue_aggregator.py` | [BLUEPRINT] MOD-INF-028 — 问题聚合器 Stage 5 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/semantic_audit/kb_gate.py` | kb_gate — re-export shim for zephyr.gov_audit.kb_gate (MOD-INF-020 canonical). | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/semantic_audit/llm_bridge.py` | [BLUEPRINT] MOD-INF-028 — LLM 桥接 Stage 6 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/semantic_audit/models.py` | 语义审计管线数据模型 — MOD-INF-028 §4.2 | 2026-09-16（18天） | in=12/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/semantic_audit/privacy.py` | privacy — re-export shim for zephyr.gov_audit.privacy (MOD-INF-020 canonical). | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/semantic_audit/reference_extractor.py` | [BLUEPRINT] MOD-INF-028 — 引用提取器 Stage 1 | 2026-09-16（18天） | in=3/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/semantic_audit/safety_boundary.py` | [BLUEPRINT] MOD-INF-028 — 安全边界 Stage 3 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/semantic_audit/semantic_cache.py` | 5.47.2 修复：per-key single-flight 锁，防止 get miss 时 thundering herd | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/semantic_audit/spec_auditor.py` | spec_auditor — re-export shim for zephyr.gov_audit.spec_auditor (MOD-INF-020 canonical). | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/semantic_audit/trigger_engine.py` | [BLUEPRINT] MOD-INF-028 — 触发器引擎 Stage 2 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/services/cross_session_correlator.py` | Cross-Session Correlator — v0.9.0 跨会话Coreset关联器: 多session行为模式+异常跨session模式检测。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/services/memory_provenance.py` | Memory Provenance — v0.9.0 记忆溯源追踪: 每条memory record的来源agent+timestamp+hash链。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/strategies/strategy_base.py` | D_PORTFOLIO_CORE — StrategyBase + StrategyMeta + StrategyRegistry | 2026-09-16（18天） | in=14/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/governance/strategies/strategy_registry.py` | StrategyRegistry 卫星模块（OCP-002） | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
