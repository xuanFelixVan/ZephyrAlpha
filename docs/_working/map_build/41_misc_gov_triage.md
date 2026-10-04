---
ttl: task_bound
completes_when: 孤儿分诊战役终裁落地（chief 终审+处置执行）后本册随 30/31 号转归档
title: 孤儿分诊证据包：小簇合并册 misc_gov（7 簇 76 台）
owner: st-orphtriage-20261004
---

# 41 号·小簇合并册：misc_gov（7 簇 76 台）

> 宇宙口径=裁定#481；数据真源=30_attribution_table.yaml；处置=建议非终裁。
>
> 合并初判汇总：dispute=7，mount=69

### 簇 scripts.audit（2 台；初判 mount=2）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `scripts/audit/cost_trio_exam.py` | cost_trio_exam.py — 做T 配对成本三件套判据（TC-06 R4 卡 A 选项重建版，裁定#399 二授权） | 2026-09-24（10天） | in=7/out=0·wired | **mount**→chief 判（域 audit 无预设映射）（活线在身未挂线） |
| `scripts/audit/t0_six_phase_materialize.py` | t0_six_phase_materialize.py — TDM 六段情绪相位历史物化件（做 T 双门前置 data 线） | 2026-09-28（6天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 audit 无预设映射）（活线在身未挂线） |

### 簇 src.zephyr.clone_guard（11 台；初判 mount=11）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/clone_guard/aggregator.py` | FindingAggregator — 多引擎结果聚合器（Phase B）。 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/clone_guard/config.py` | CloneGuard 配置加载器——从 clone_guard.yml 读取统一配置。 | 2026-09-16（18天） | in=9/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/clone_guard/engines/__init__.py` | CloneGuard 引擎适配器子包。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/clone_guard/engines/ast_grep_adapter.py` | AstGrepAdapter — ast-grep 规则引擎适配器（Phase B）。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/clone_guard/engines/echo_guard_adapter.py` | EchoGuardAdapter — Echo-Guard 引擎适配器（Phase A MVP）。 | 2026-09-16（18天） | in=8/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/clone_guard/engines/mcrit_adapter.py` | McritAdapter —— 已废弃降级占位（Phase C 引擎核实裁定）。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/clone_guard/engines/redup_adapter.py` | RedupAdapter — reDUP 深度分析引擎适配器（Phase B 补齐）。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/clone_guard/engines/relate_adapter.py` | RelateAdapter — relate 快速预筛适配器（Phase C L2/L3 加速器，Path B: datasketch MinHash LSH）。 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/clone_guard/engines/vendetect_adapter.py` | VendetectAdapter — Vendetect 跨仓库合规审计适配器（Phase C L3）。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/clone_guard/orchestrator.py` | CloneGuard 统一编排器——Phase B（多引擎并发 + 结果聚合）。 | 2026-09-16（18天） | in=4/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/clone_guard/strategy_fingerprint.py` | D_GOV_CODE_QUALITY — 退役策略指纹库（90 号 Phase2 项，#20 工程细节 B-010） | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |

### 簇 src.zephyr.data_governance（19 台；初判 mount=19）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/data_governance/__init__.py` | （无文档头，按文件名语义：__init__） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/data_governance/_extensions/__init__.py` | data_gov/_extensions | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/data_governance/api/__init__.py` | data_gov/api | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/data_governance/asset_auto_discovery.py` | asset_auto_discovery — 数据资产自动发现器（MOD-DATA_GOV-014）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/data_governance/column_lineage_tracker.py` | column_lineage_tracker — 列级血缘追踪器（MOD-DATA_GOV-012）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/data_governance/core/__init__.py` | data_gov/core | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/data_governance/core/column_lineage_analyzer.py` | M8-NEW-02 Column-Level Lineage Analyzer（MOD-DATA_GOV-007）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/data_governance/core/lineage_parser.py` | M8-S01 血缘解析器（MOD-DATA_GOV-004）。 | 2026-09-16（18天） | in=3/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/data_governance/core/lineage_tracker.py` | D-DATA-GOV Lineage Tracker——数据血缘追踪。 | 2026-09-16（18天） | in=5/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/data_governance/core/metadata_registry.py` | D-DATA-GOV Metadata Registry——元数据管理。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/data_governance/core/runtime_lineage_collector.py` | M8-S03 动态采集器（MOD-DATA_GOV-006）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/data_governance/core/schema_registry.py` | D-DATA-GOV Schema Registry——表结构注册与查询。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/data_governance/core/static_lineage_analyzer.py` | M8-S02 静态分析器（MOD-DATA_GOV-005）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/data_governance/infrastructure/__init__.py` | data_gov/infrastructure | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/data_governance/lineage_change_detector.py` | lineage_change_detector — 血缘变更检测器（MOD-DATA_GOV-010）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/data_governance/ml_lineage_tracker.py` | ml_lineage_tracker — AI-ML 管线血缘追踪器（MOD-DATA_GOV-013）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/data_governance/models/__init__.py` | data_gov/models | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/data_governance/openlineage_exporter.py` | openlineage_exporter — OpenLineage 事件导出器（MOD-DATA_GOV-011）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/data_governance/services/__init__.py` | data_gov/services | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |

### 簇 src.zephyr.data_security（9 台；初判 mount=9）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/data_security/_extensions/__init__.py` | data_sec/_extensions | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/data_security/ai_masking_pipeline.py` | AiMaskingPipeline — AI 分级脱敏管道（MOD-DATSEC-001）。 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/data_security/api/__init__.py` | data_sec/api | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/data_security/core/__init__.py` | data_sec/core | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/data_security/data_masking_engine.py` | DataMaskingEngine — 数据脱敏引擎（MOD-DATSEC-003）。 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/data_security/infrastructure/__init__.py` | data_sec/infrastructure | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/data_security/models/__init__.py` | data_sec/models | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/data_security/services/__init__.py` | data_sec/services | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/data_security/wiring/audit_sink.py` | JsonlAuditSink — F128 接线统一审计落盘 sink（MOD-DATSEC-004）。 | untracked（未入库） | in=3/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |

### 簇 src.zephyr.gov_enforcement（14 台；初判 mount=14）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/gov_enforcement/behavioral_admission/admission_controller.py` | class-name-alias: migrated from governance/behavioral_admission; pre-existing same-name class in trading/integration (AR | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_enforcement/behavioral_admission/protection_index.py` | class-name-alias: migrated from governance/behavioral_admission; pre-existing same-name class in trading/integration (AR | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_enforcement/behavioral_admission/verdict_engine.py` | class-name-alias: migrated from governance/behavioral_admission; pre-existing same-name class in trading/integration (AR | 2026-09-05（29天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_enforcement/rule_bridge/__init__.py` | gov_enforcement.rule_bridge — auto-generated package init. | 2026-09-18（16天） | in=3/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_enforcement/rule_enforcement/approval.py` | G-CT-004 — Backward-compat re-export of ApprovalRequest from shared.contracts.approval_types. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_enforcement/rule_enforcement/compliance_rule.py` | Re-export shim — ComplianceRule 真源已合并至 zephyr.shared.contracts.compliance_rule。 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_enforcement/rule_enforcement/dlq_retry_policy.py` | DLQ 重试策略 — 对接 shared/events/dlq.DeadLetterQueue 的真重试。 | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_enforcement/rule_enforcement/output_quality_gate.py` | ── Stage 4 公共化（2026-07-29）：只读 properties ── | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_enforcement/rule_enforcement/rule_engine/__init__.py` | rule_engine package — 规则引擎模块集合（ARCH-042 阶段1 拆分产物）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_enforcement/rule_enforcement/rule_engine/rule_canary_manager.py` | Rule Canary Manager — v0.10.0 规则金丝雀: 1%用户先上新规则->A/B对比->rollback。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_enforcement/rule_enforcement/rule_engine/rule_debt_auditor.py` | Rule Debt Auditor — v0.7.0 规则债务审计器: 分析escalation_rules.yaml维护债务指标。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_enforcement/rule_enforcement/rule_engine/rule_shadow_runner.py` | Rule Shadow Runner — v0.10.0 规则影子模式: 新规则shadow运行3天->diff old vs new->promote。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_enforcement/rule_enforcement/slo_contract.py` | SLO-Driven Escalation Contract — D-022-12. | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_enforcement/rule_enforcement/threshold_split_detector.py` | Threshold Split Detector — 阈值拆分检测器 (MOD-GOV-050, CAND-GOVENFOR-001 MVP) | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |

### 簇 src.zephyr.gov_rule（2 台；初判 dispute=1，mount=1）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/gov_rule/__init__.py` | gov_rule domain package — rule governance (D_GOV_RULE). | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→GOMAP（治理/安全域） ②retire→Owner 门位） |
| `src/zephyr/gov_rule/standards_manager.py` | StandardsManager — 硬边界标准管理器（MOD-GOV-057）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |

### 簇 src.zephyr.security（19 台；初判 dispute=6，mount=13）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/security/_extensions/__init__.py` | security/_extensions | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→GOMAP（治理/安全域） ②retire→Owner 门位） |
| `src/zephyr/security/api/__init__.py` | security/api | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→GOMAP（治理/安全域） ②retire→Owner 门位） |
| `src/zephyr/security/core/__init__.py` | security/core | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→GOMAP（治理/安全域） ②retire→Owner 门位） |
| `src/zephyr/security/infrastructure/__init__.py` | security/infrastructure | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→GOMAP（治理/安全域） ②retire→Owner 门位） |
| `src/zephyr/security/models/__init__.py` | security/models | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→GOMAP（治理/安全域） ②retire→Owner 门位） |
| `src/zephyr/security/services/__init__.py` | security/services | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→GOMAP（治理/安全域） ②retire→Owner 门位） |
| `src/zephyr/security/adversarial_validation/ai_attack_generator.py` | （无文档头，按文件名语义：ai_attack_generator） | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/security/adversarial_validation/attack_registry.py` | （无文档头，按文件名语义：attack_registry） | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/security/adversarial_validation/blast_radius.py` | （无文档头，按文件名语义：blast_radius） | 2026-09-16（18天） | in=3/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/security/adversarial_validation/bypass_recorder.py` | （无文档头，按文件名语义：bypass_recorder） | 2026-09-16（18天） | in=3/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/security/adversarial_validation/cleanup.py` | （无文档头，按文件名语义：cleanup） | 2026-09-16（18天） | in=3/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/security/adversarial_validation/cold_start.py` | （无文档头，按文件名语义：cold_start） | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/security/adversarial_validation/constitution_engine.py` | （无文档头，按文件名语义：constitution_engine） | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/security/adversarial_validation/convergence_checker.py` | （无文档头，按文件名语义：convergence_checker） | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/security/adversarial_validation/injection_engine.py` | 5.79.1 修复：原模块级 os.makedirs 在 import 时执行，在只读文件系统/受限沙箱中 import 直接抛 PermissionError。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/security/adversarial_validation/models.py` | （无文档头，按文件名语义：models） | 2026-09-19（15天） | in=16/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/security/adversarial_validation/scenario_loader.py` | （无文档头，按文件名语义：scenario_loader） | 2026-09-16（18天） | in=4/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/security/llm_defense/spectral_guard.py` | SpectralGuard — Spectral 注意力谱幻觉检测器（MOD-SECLLM-002）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/security/ops/ops_maturity.py` | 自治运维成熟度 A-L0→A-L2 状态机（16号文 §4.4 P2-2 + §3.7）。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
