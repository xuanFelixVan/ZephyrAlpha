---
ttl: task_bound
completes_when: 孤儿分诊战役终裁落地（chief 终审+处置执行）后本册随 30/31 号转归档
title: 孤儿分诊证据包：src.zephyr.autonomy_core（103 台）
owner: st-orphtriage-20261004
---

# 41 号·分诊证据包：src.zephyr.autonomy_core（103 台）

> 宇宙口径=裁定#481；数据真源=30_attribution_table.yaml（join checker 机生）；处置=证据班建议，终裁归 GLM-5.3 chief，退役执行归 Owner 门位。
>
> tier 分布：suspect_orphan=2，wired=22，wired_by_header=79；初判汇总：dispute=2，mount=101

## 逐台证据（四字段+初判）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/autonomy_core/context/__init__.py` | [A_module] module_id=MOD-AUTONOMY_CORE_context \| layer=infrastructure \| stability=evolving \| safety=L \| ai_autonomy=ai_m | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→GOMAP（自治核心域） ②retire→Owner 门位） |
| `src/zephyr/autonomy_core/skills/__init__.py` | [A_module] module_id=MOD-AUTONOMY_CORE_skills \| layer=infrastructure \| stability=evolving \| safety=L \| ai_autonomy=ai_mo | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→GOMAP（自治核心域） ②retire→Owner 门位） |
| `src/zephyr/autonomy_core/__init__.py` | [A_module] module_id=MOD-AUTONOMY_CORE \| layer=infrastructure \| stability=evolving \| safety=L \| ai_autonomy=ai_modifiabl | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/__main__.py` | agent-spec MOD-INF-019 CLI — 蓝图->Skill 升级引擎入口. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/agent_observability.py` | MOD-INF-019: Agent Spec — Agent Observability | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/agents/__init__.py` | AI 执行层四类 Agent 薄入口包（14号文 §3.0 role façade，§4 Phase 0 手动形态）. | 2026-09-16（18天） | in=3/out=0·wired | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/agents/_g04_ops_check.py` | S1.3 业务 Agent U7 深化：G04 三策略运营核对件（14号文 §4-S1.3）. | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/agents/_registration_status.py` | B16 治本拆分（长城审计 §6#18，2026-09-05）：自 business_agent_entry.py（原 304 行，超 | 2026-09-05（29天） | in=1/out=0·wired | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/agents/_run_store.py` | 四类 Agent 薄入口共享落盘纪律件（组装用内部件，非角色入口）. | 2026-09-16（18天） | in=7/out=0·wired | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/agents/_self_iteration_review.py` | B16 治本拆分（长城审计 §6#18，2026-09-05）：自 self_iteration_agent_entry.py（原 284 | 2026-09-05（29天） | in=1/out=0·wired | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/agents/business_agent_entry.py` | 业务 Agent 薄入口（14号文 §3.2 因子/策略/组合运营，§4 S0.3 手动形态 + S1.3 G04 核对）. | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/agents/ticket_queue.py` | S1.2 工单队列落盘化（14号文 §4-S1.2，61号文 §3.6 人调度多会话交接载体）. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/all_skill_modules.py` | MOD-INF-019: Agent Spec — All Skill Modules | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/context/atomic_injector.py` | atomic_injector.py — 原子注入 (DD101, TASK-019) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/context/ce_bootstrap.py` | ce_bootstrap.py — CE 自举架构 (B1, DD75, TASK-015 beta v) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/context/ce_explain_cli.py` | ce_explain_cli.py — KE inclusion rationale 解释 CLI (TASK-016) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/context/ce_file_lister.py` | list_ce_files.py — CE 文件清单生成器 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/context/ce_playground_v2.py` | ce_playground_v2.py — V2 Playground with full decision chain (TASK-016) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/context/ce_vibe_shortcuts.py` | ce_vibe_shortcuts.py — Vibe/Strict 模式切换 (TASK-016) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/context/checkpoint_manager.py` | checkpoint_manager.py — Inject 前快照 (DD100, TASK-019) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/context/cold_start_booster.py` | cold_start_booster.py — 冷启动 (DD107, TASK-019) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/context/context_debt_score.py` | context_debt_score.py — 上下文债务评分 (B19, DD93, TASK-017) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/context/context_evaluator.py` | context_evaluator.py — AI 引用率评估 (TASK-014 beta b) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/context/context_evictor.py` | context_evictor.py — 三维逐出器 (DD9, TASK-014 beta a) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/context/context_model_strategy.py` | context_model_strategy.py — 模型选择策略 (DD118, TASK-020) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/context/context_outcome_tracker.py` | context_outcome_tracker.py — 因果链追踪 (B14, DD88, TASK-017) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/context/context_playground.py` | context_playground.py — 上下文沙箱 dry-run (B5, DD79, TASK-015 beta v) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/context/context_rot_model.py` | context_rot_model.py — Context Rot 注意力衰减数学模型 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/context/context_rule_registry.py` | （无文档头，按文件名语义：context_rule_registry） | 2026-09-16（18天） | in=3/out=0·wired | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/context/context_value_attribution.py` | context_value_attribution.py — KE 级 ROI 归因 (B2, DD76, TASK-015 beta v) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/context/contextual_fetch_api.py` | contextual_fetch_api.py — HTTP FE 对外 API (DD115, TASK-020) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/context/curation_loop.py` | curation_loop.py — Per-Turn Curation 策展 (DD10, TASK-014 beta b) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/context/diff_injector.py` | diff_injector.py — 增量注入 (DD98, TASK-019) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/context/diversity_constraint.py` | diversity_constraint.py — 多样性约束 (DD119, TASK-020) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/context/domain_decay_config.py` | domain_decay_config.py — 每领域半衰期 (DD105, TASK-019) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/context/fallback_staleness_gate.py` | fallback_staleness_gate.py — 兜底层自腐检测 (B13, DD87, TASK-017) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/context/integrity_check.py` | integrity_check.py — 注入后完整性 (DD106, TASK-019) | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/context/memory_bank.py` | memory_bank.py — AI 读写结构化持久上下文 (DD: memory_bank, TASK-014 beta c) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/context/mode_manager.py` | mode_manager.py — 模式管理器 (DD102, TASK-019) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/context/position_optimizer.py` | position_optimizer.py — 位置优化 (DD104, TASK-019) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/context/shadow_canary.py` | shadow_canary.py — 金丝雀部署 (B4, DD78, TASK-015 beta w) | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/context/staleness_manager.py` | staleness_manager.py — 全局过期检测 (DD112, TASK-019) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/context/vector_bridge.py` | VectorBridge — CE↔VMS 检索桥接 (Connect CT-CE-VMS-001) | 2026-09-16（18天） | in=3/out=0·wired | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/drift_semantic_reviewer.py` | DriftSemanticReviewer — Agentic Drift 深度语义复核批量件（MOD-AU-003，15号文 §4.2 S1.3）. | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/file_autoregister.py` | （无文档头，按文件名语义：file_autoregister） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/ide_watcher.py` | MOD-INF-019: Agent Spec — IDE Watcher | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/integration/__init__.py` | Agent Spec -> Pipeline 集成桥接层 | 2026-09-18（16天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/integration/pipeline_bridge.py` | PipelineSkillBridge — Agent Spec -> Pipeline 双向桥接 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/phase_planner.py` | MOD-INF-019: Agent Spec — Phase Planner | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/progressive_disclosure_injector.py` | progressive_disclosure_injector.py — 渐进式披露 (B7, DD81, TASK-015 beta w) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/self_evolution_fidelity_gate.py` | MOD-INF-019: Agent Spec — Self Evolution Fidelity Gate | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skill_rbac_registry.py` | G-CT-003: Agent Spec -> RBAC capability check. | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_attention.py` | MOD-INF-019: Agent Spec — Skill Attention Management | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_breakage_checker.py` | MOD-INF-019: Agent Spec — Skill Breakage Checker | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_cache_provider.py` | MOD-INF-019: Agent Spec — Skill Cache Provider | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_calibration.py` | MOD-INF-019: Agent Spec — Skill Calibration | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_canary.py` | MOD-INF-019: Agent Spec — Skill Canary | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_cognitive_preservation.py` | MOD-INF-019: Agent Spec — Skill Cognitive Preservation | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_compliance.py` | MOD-INF-019: Agent Spec — Skill Compliance | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_consensus.py` | MOD-INF-019: Agent Spec — Skill Consensus | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_constructor.py` | MOD-INF-019: Agent Spec — Skill Constructor | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_context_isolation.py` | MOD-INF-019: Agent Spec — Context Isolation | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_contract.py` | MOD-INF-019: Agent Spec — Skill Contract | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_cross_model.py` | MOD-INF-019: Agent Spec — Skill Cross-Model | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_di.py` | MOD-INF-019: Agent Spec — Skill Dependency Injection | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_discovery.py` | MOD-INF-019: Agent Spec — Skill Discovery | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_durable.py` | MOD-INF-019: Agent Spec — Durable Execution | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_economics.py` | MOD-INF-019: Agent Spec — Skill Economics | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_efficacy_calibrator.py` | MOD-INF-019: Agent Spec — Skill Efficacy Calibrator | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_evaluator.py` | MOD-INF-019: Agent Spec — Skill Evaluator | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_explain.py` | MOD-INF-019: Agent Spec — XAI Explainable Skill Engine | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_factory.py` | （无文档头，按文件名语义：skill_factory） | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_feature_flags.py` | MOD-INF-019: Agent Spec — Skill Feature Flags | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_freshness.py` | MOD-INF-019: Agent Spec — Skill Freshness Decay | 2026-09-16（18天） | in=6/out=0·wired | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_gitops.py` | MOD-INF-019: Agent Spec — Skill GitOps | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_guardrails.py` | MOD-INF-019: Agent Spec — Skill Guardrails | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_idempotency.py` | MOD-INF-019: Agent Spec — Skill Idempotency | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_kya.py` | MOD-INF-019: Agent Spec — Skill KYA | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_learning.py` | MOD-INF-019: Agent Spec — Skill Self-Learning Engine | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_lineage.py` | MOD-INF-019: Agent Spec — Skill Lineage | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_loader.py` | （无文档头，按文件名语义：skill_loader） | 2026-09-16（18天） | in=14/out=0·wired | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_locking.py` | MOD-INF-019: Agent Spec — Skill Locking (Production Hardening) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_model.py` | （无文档头，按文件名语义：skill_model） | 2026-09-16（18天） | in=4/out=0·wired | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_model_evolution.py` | MOD-INF-019: Agent Spec — Skill Model Evolution | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_observability.py` | MOD-INF-019: Agent Spec — Skill Observability | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_ontology.py` | MOD-INF-019: Agent Spec — Skill Ontology | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_postmortem.py` | MOD-INF-019: Agent Spec — Skill Postmortem (追问到底) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_prompt_cache.py` | MOD-INF-019: Agent Spec — Skill Prompt Cache | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_prompt_opt.py` | MOD-INF-019: Agent Spec — Skill Prompt Optimizer | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_registry.py` | skill-registry.py —— Skill 注册基座（Phase 14 \| 盲点 B34） | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_resilience.py` | MOD-INF-019: Agent Spec — Skill Resilience | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_risk_mitigator.py` | MOD-INF-019: Agent Spec — Skill Risk Mitigator | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_schema_registry.py` | MOD-INF-019: Agent Spec — Skill Schema Registry | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_security.py` | MOD-INF-019: Agent Spec — Skill Security | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_shadow.py` | MOD-INF-019: Agent Spec — Skill Shadow Deployment | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_silent_failure.py` | MOD-INF-019: Agent Spec — Silent Failure Detector | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_team_optimizer.py` | MOD-INF-019: Agent Spec — Skill Team Optimizer | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_temperature.py` | MOD-INF-019: Agent Spec — Skill Temperature | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_tokenomics.py` | MOD-INF-019: Agent Spec — Skill Tokenomics | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_translator.py` | MOD-INF-019: Agent Spec — Skill Translator | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/skills/skill_workflow.py` | MOD-INF-019: Agent Spec — Skill Workflow Orchestrator | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/trigger_router.py` | （无文档头，按文件名语义：trigger_router） | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
| `src/zephyr/autonomy_core/vibe_coding_quality_gate.py` | VibeCodingQualityGate — 代码质量门禁（stub, tests 待实装后补全实现） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（自治核心域）（活线在身未挂线） |
