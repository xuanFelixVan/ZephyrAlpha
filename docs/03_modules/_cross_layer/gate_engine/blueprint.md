---
module_id: MOD-GATE_ENGINE
submodule_path: src/zephyr/feedback_loop/gates
title: "Gate Engine 蓝图 — G0-G7任务门禁 + G1-G5 KMS决策门 + 门禁域熔断器"
doc_type: blueprint
template_for: blueprint
status: Draft
version: "0.8.2"
layer: L1_foundation
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-10"
valid_from: "2026-05-10"
ttl: permanent
construction_progress: partially_implemented
actual_disk_path: "src/zephyr/gov_enforcement/rule_enforcement/ + src/zephyr/feedback_loop/gates/ + src/zephyr/gov_enforcement/commit_gates/"
belongs_to: "MOD-MASTER_BLUEPRINT"
parent_module: "MOD-MASTER_BLUEPRINT"
last_updated: "2026-05-18"
last_verified: "2026-05-14"
generation: 1
functional_domain: governance
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
codification_level: L1
summary: "G0-G7任务门禁+G1-G5 KMS决策门+门禁域熔断器+容量架构(10K脚本/100AI并发)+法证审计+自指硬化"
tags: [gate_engine, gates, g0-g7, g1-g5, circuit-breaker, pre-commit, admission-controller, task-gate, kms-gate, infrastructure, shadow-mode, emergency-override, observability, gate-pipeline, gate-context, gate-simulation, hash-chain, forensic-audit, integrity-guard, threat-model, stride, deep-compliance, capacity, scalability, concurrency, sharding, dependency-graph, capacity-upgrade]
priority: P0
runtime_plane: hot
depends_on:
  - {target: "MOD-MASTER_BLUEPRINT", at: "§2.8", why: "CT-SCRIPT-GATE-001 集成契约——脚本exit code→Gate判定"}
  - {target: "MOD-MASTER_BLUEPRINT", at: "§4", why: "全局状态传播链——Gate FAIL→Orc BLOCKED 传播"}
  - {target: "MOD-INF-005", at: "§6", why: "脚本系统——Gate判定输入源（脚本exit code）"}
  - {target: "MOD-TASK_SYSTEM", at: "§4", why: "任务系统——Gate判定输出目标（status→BLOCKED）"}
  - {target: "MOD-KB-001", at: "§3.2", why: "知识库——G1-G5 KMS门禁判定对象"}
  - {target: "architecture_model/layers/b_gates.yaml", at: "全篇", why: "Gates YAML SSoT——本蓝图真源"}
  - {target: "MOD-INF-030", at: "§2", why: "Red-Blue Validator——通过 DefenseRunner GATE_MAP 17门禁映射消费 Gate Engine 判定"}
  - {target: "MOD-INF-001", at: "§13", why: "容量 SLO 注册表——门禁容量指标对齐 CAP-001~013"}
  - {target: "MOD-INF-001", at: "§5", why: "容量风险注册表——R1(SQLite) + R19(资产膨胀) + R20(元盘点) 与门禁容量联动"}
references:
  - {path: "d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md", section: "REQUIRED_SECTIONS", why: "蓝图模板 v3.5 合规基准"}
  - {path: "d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml", section: "§0.5", why: "压缩工作流标准——Layer 1/2 执行规范"}
ssot_claims:
  - {claim: "G0-G7任务门禁规则SSoT", scope: "global"}
  - {claim: "G1-G5 KMS决策门规则SSoT", scope: "global"}
  - {claim: "门禁域熔断器参数SSoT", scope: "module"}
  - {claim: "门禁评估管线SSoT", scope: "global"}
  - {claim: "法证审计协议SSoT", scope: "module"}
  - {claim: "自指硬化协议SSoT", scope: "module"}
responsibility_domain: 
design_maturity: design
build_status: planned
---

# Gate Engine 蓝图 — G0-G7任务门禁 + G1-G5 KMS决策门 + 门禁域熔断器

## 概述
<!-- temporal_type: permanent -->

本蓝图描述 Gate Engine——ZephyrAlpha 的门禁引擎。它解决了任务执行和知识生命周期关键决策点的合规判定问题。核心职责包括：G0-G7 八门禁覆盖任务全生命周期、G1-G5 KMS 决策门覆盖知识生命周期、熔断器阻断异常传播、法证审计完整性。当前规模 ~268 脚本/51 模块，目标容量 10000 脚本/1500 模块/100 AI 并发。上游依赖脚本系统(MOD-INF-005)提供 exit code，下游被 Orchestrator(MOD-TASK_SYSTEM)消费判定结果。

> module_id: MOD-GATE_ENGINE | version: 0.8.2 | status: Draft | layer: cross_layer
> actual_disk_path: src/zephyr/gov_enforcement/rule_enforcement/ + src/zephyr/feedback_loop/gates/ | generation: 1 | construction_progress: partially_implemented
> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md)
> - AI 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

---

## §0 代码对齐验证
<!-- temporal_type: permanent -->

### §0.1 代码文件清单

<!-- AUTOGEN: source=depgraph.nodes, generator=extract_depgraph.py, reconciler=blueprint_frontmatter_reconciler.py -->
> **⚠️ 自动化提示**：文件清单真源在 PostgreSQL depgraph.nodes 表，本节手写内容可能过时。
> 查询最新文件清单：`python scripts/governance/extract_depgraph.py --modules MOD-GATE_ENGINE`
> 以下手写内容保留职责描述（depgraph 无此信息），文件列表以 depgraph 为准。

> **架构归属SSoT**：`data/asset_index/project-architecture-panorama.yaml`
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[DOMAIN]/[DEPENDENCIES]/[CONSUMERS]/[STARTUP]/[MATURITY]/[INVARIANTS]/[MODIFY-GUARD]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]/[TTL]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-GATE_ENGINE`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因（仅已阻塞） | 归属判定 |
|---|--------|------------|------|:-----:|-------------------|---------|
| 1 | gate_engine.py | §3.1 | 核心门禁引擎——加载配置→管线编排→执行判定→返回PASS/FAIL | 已实现 | | 本模块 |
| 2 | gate_context.py | §3.1 | 门禁上下文传播——GateContext构建/序列化/跨模块注入 | 已实现 | | 本模块 |
| 3 | gate_pipeline.py | §3.1 | 门禁评估管线——排序解析、组合逻辑(AND/OR/NOT)、并行调度 | 已实现 | | 本模块 |
| 4 | gate_simulator.py | §3.1 | 门禁模拟器——dry-run全链路演练，不修改任何状态 | 已实现 | | 本模块 |
| 5 | gate_override.py | §3.1 | Owner紧急旁路——时间限定的门禁临时绕过+审计追踪 | 已实现 | | 本模块 |
| 6 | gate_health.py | §3.1 | 门禁健康仪表板——per-gate SLI报告、误报率、延迟分布 | 已实现 | | 本模块 |
| 7 | task_completion_gate.py | §3.1 | G7交付前门禁——运行关联文件审计→判定 | 已实现 | | 本模块 |
| 8 | circuit_breaker.py | §3.1 | 熔断器——检测异常传播→切断故障链路+门禁自保熔断 | 已实现 | | ⚠️与MOD-INF-016重叠(已声明委托) |
| 9 | contract_template_manager.py | §3.1 | 契约模板管理——加载G1-G5 KMS门禁YAML配置 | 已实现 | | 本模块 |
| 10 | adaptive_threshold.py | §3.1 | 自适应阈值——从历史FAIL/PASS数据学习门禁参数调整 | 已实现 | | 本模块 |
| 11 | gate_integrity_guard.py | §3.1 | 门禁引擎完整性守卫——启动前自检SHA-256+信任根验证 | 已实现 | | 本模块 |
| 12 | audit_chain_verifier.py | §3.1 | 审计链验证工具——独立重放+哈希链完整性校验 | 已实现 | | 本模块 |
| 13 | ai_capability_guard.py | §3.1 | AI能力边界守卫——task操作在能力矩阵内 | 已实现 | | 本模块 |
| 14 | kms/ g1~g5.yaml (5个) | §A.2 | KMS入库/分拣/评估/激活/提取门禁配置 | 已实现 | | 本模块 |
| 15 | g6-blueprint-compliance.yaml | §A.1 | G6蓝图读取合规门禁 | 已实现 | | 本模块 |
| 16 | g6-ctr-compliance.yaml | §A.1 | G6 CTR合规门禁 | 已实现 | | 本模块 |
| 17 | g7d_depth_compliance.yaml | §A.1 | G7D深度合规——形式+实质双重验证 | 未实现 | | 本模块 |
| 18 | g7c_cross_gate_consistency.yaml | §A.1 | G7C跨门禁时序一致性 | 未实现 | | 本模块 |
| 19 | task/ g0-entry.yaml + g7-orc-gate_engine.yaml | §A.1 | G0准入+G7 Orc门禁 | 已实现 | | 本模块 |
| 20 | admission/ mad_001~004.yaml | §A.1 | MAD-001~004模块准入门禁 | 已实现 | | 本模块 |
| 21 | invariants/ en_001~003.yaml (3个) | §3.3 | EN-001循环依赖/EN-002执行模式/EN-003契约兼容 | 已实现 | | 本模块 |
| 22 | zero_residue.yaml | §3.4 | ZERO-RESIDUE零残留门禁 | 已实现 | | 本模块 |
| 23 | governance/ (8个: g9+gct_016~025) | §3.5 | G9跨蓝图集成+GCT-016~025集成门禁 | 已实现 | | 本模块 |
| 24 | infrastructure/ (4个: g8+sys_master+vms+observability) | §3.6 | G8 SSoT+系统蓝图合规+向量库健康+可观测性 | 已实现 | | 本模块 |
| 25 | trading/ (3个: position+leverage+correlation) | §3.7 | G10持仓限制+G11杠杆限制+G12策略相关性 | 已实现 | shadow | 本模块 |
| 26 | fle/ (43个FLE门禁) | §3.8 | FLE-ACTION-REVERSIBILITY~FLE-SCOPE-CREEP-MONITOR + FLE-SAFETY-GATE-L1~L67（归属MOD-FEEDBACK_LOOP） | 已实现 | | ⚠️建议迁移至MOD-FEEDBACK_LOOP |
| 27 | _registry.yaml | §3.1 | 全部门禁注册表SSoT | 已实现 | | 本模块 |
| 28 | _template.yaml | §3.1 | 门禁标准模板——11节完整字段 | 已实现 | | 本模块 |
| `anti_pattern_guard.py` | § — | — | 已实现 | | 本模块 |
| `breaking_change_detector.py` | § — | — | 已实现 | | 本模块 |
| `can_i_deploy.py` | § — | — | 已实现 | | 本模块 |
| `capability_checker.py` | § — | — | 已实现 | | 本模块 |
| `cbac_matrix.py` | § — | — | 已实现 | | 本模块 |
| `cdc_broker.py` | § — | — | 已实现 | | 本模块 |
| `drift_detector.py` | § — | — | 已实现 | | 本模块 |
| `end_to_end_walkthrough.py` | § — | — | 已实现 | | 本模块 |
| `gate_types.py` | § — | — | 已实现 | | 本模块 |
| `integration_test_runner.py` | § — | — | 已实现 | | 本模块 |
| `invariants/en_001_circular_dependency.py` | § — | — | 已实现 | | 本模块 |
| `invariants/en_002_enforcement_validator.py` | § — | — | 已实现 | | 本模块 |
| `invariants/en_003_contract_compatibility.py` | § — | — | 已实现 | | 本模块 |
| `invariants/en_process_lifecycle_gateway.py` | § — | — | 已实现 | | 本模块 |
| `invariants/zero_residue_check.py` | § — | — | 已实现 | | 本模块 |
| `kiss_enforcer.py` | § — | — | 已实现 | | 本模块 |
| `risk_ssot.py` | § — | — | 已实现 | | 本模块 |
| `secrets_guard.py` | § — | — | 已实现 | | 本模块 |
| `sys_master_compliance.py` | § — | — | 已实现 | | 本模块 |
| `task_types.py` | § — | — | 已实现 | | 本模块 |
| `triple_alignment.py` | § — | — | 已实现 | | 本模块 |
| **commit_gates/** | | | | | |
| `commit_gates/ttl_gate.py` | §0.1 | ttl字段校验门禁（TTL-METADATA） | 已实现 | | 本模块 |
| `commit_gates/directory_contract_gate.py` | §0.1 | 目录契约门禁（DIRECTORY-CONTRACT） | 已实现 | | 本模块 |
| `commit_gates/r5_digit_suffix_gate.py` | §0.1 | R5数字后缀目录禁止门禁 | 已实现 | | 本模块 |
| `commit_gates/ssot_redefinition_gate.py` | §0.1 | SSoT符号重复定义门禁 | 已实现 | | 本模块 |
| `commit_gates/vocab_hardcode_gate.py` | §0.1 | 词表硬编码门禁 | 已实现 | | 本模块 |
| `commit_gates/file_copy_gate.py` | §0.1 | 文件复制检测门禁 | 已实现 | | 本模块 |
| `commit_gates/id_uniqueness_gate.py` | §0.1 | pre-commit hook id唯一性门禁 | 已实现 | | 本模块 |
| `commit_gates/exempt_zone_frontmatter_gate.py` | §0.1 | 豁免区frontmatter门禁 | 已实现 | | 本模块 |
| `commit_gates/module_id_consistency_gate.py` | §0.1 | module_id 三声明轨道一致性门禁 | 已实现 | | 本模块 |
| `commit_gates/perm_trigger_gate.py` | §0.1 | 永久系统时间触发门禁 | 已实现 | | 本模块 |
| `commit_gates/empty_handler_gate.py` | §0.1 | 空handler门禁 | 已实现 | | 本模块 |
| `commit_gates/orphan_module_gate.py` | §0.1 | 孤儿模块门禁 | 已实现 | | 本模块 |
| `commit_gates/doc_ref_broken_gate.py` | §0.1 | 文档引用断裂门禁 | 已实现 | | 本模块 |
| `commit_gates/function_dup_gate.py` | §0.1 | 重复函数门禁 | 已实现 | | 本模块 |
| `commit_gates/bare_getenv_gate.py` | §0.1 | 裸getenv门禁 | 已实现 | | 本模块 |
| `commit_gates/held_overlap_gate.py` | §0.1 | held_files冲突门禁 | 已实现 | | 本模块 |
| `commit_gates/claim_required_gate.py` | §0.1 | claim_files前置检查门禁 | 已实现 | | 本模块 |
| `commit_gates/capability_overlap_gate.py` | §0.1 | capability重叠门禁 | 已实现 | | 本模块 |
| `commit_gates/create_guard.py` | §0.1 | 新建文件守卫门禁 | 已实现 | | 本模块 |
| `commit_gates/dangling_reference_gate.py` | §0.1 | 悬空引用门禁 | 已实现 | | 本模块 |
| `commit_gates/arch_reference_gate.py` | §0.1 | ARCH-NNN引用门禁（含 L1 编号空洞检测 ARCH_GAP_WARNING 不阻断 + L2 同提交原子性门禁 ARCH_ATOMICITY_VIOLATION 硬阻断） | 已实现 | | 本模块 |
| `commit_gates/session_required_gate.py` | §0.1 | session要求门禁 | 已实现 | | 本模块 |
| `commit_gates/file_placement_ttl_gate.py` | §0.1 | 文件放置与TTL一致性门禁（ARCH-049） | 已实现 | | 本模块 |
| `commit_gates/foreign_change_gate.py` | §0.1 | 外来变更检测门禁（ARCH-054） | 已实现 | | 本模块 |
| `commit_gates/msg_exposure_gate.py` | §0.1 | commit消息敏感信息暴露门禁 | 已实现 | | 本模块 |
| `commit_gates/msg_style_gate.py` | §0.1 | commit消息风格门禁 | 已实现 | | 本模块 |
| `commit_gates/rule_four_way_alignment_gate.py` | §0.1 | 规则四方对齐门禁（ARCH-020补建） | 已实现 | | 本模块 |
| `commit_gates/unsafe_dict_spread_gate.py` | §0.1 | 不安全字典展开门禁 | 已实现 | | 本模块 |
| `commit_gates/pure_shim_gate.py` | §0.1 | 纯re-export shim阻断门禁（PURE-SHIM，P6治本--no-verify绕过） | 已实现 | | 本模块 |
|`commit_gates/pure_assertion_gate.py` | §0.1 | 纟陈述原则阻断门禁（PURE-ASSERTION，GOV-DOC-016治本，subprocess调用check_pure_assertion --ci检测staged .md added行） | 已实现 | | 本模块 |
| `commit_gates/_diff_helpers.py` | §0.1 | gate共享diff解析工具模块（FUNCTION-DUP治本提取） | 已实现 | | 本模块 |
| `commit_gates/datetime_now_forbidden_gate.py` | §0.1 | 生成器代码datetime.now()硬阻断门禁（AGENTS.md §11.1.1） | 已实现 | | 本模块 |
| `commit_gates/import_direction_gate.py` | §0.1 | shared层向上依赖阻断门禁（NO-UPWARD-IMPORT，§5.152防复发） | 已实现 | | 本模块 |
| `commit_gates/hardcoded_url_gate.py` | §0.1 | 硬编码localhost URL阻断门禁（NO-HARDCODED-URL，§5.160.9防复发） | 已实现 | | 本模块 |
| `commit_gates/panorama_alignment_gate.py` | §0.1 | 三图模块对齐warn-only门禁（GATE-PANORAMA-ALIGNMENT，四图模块对齐Step 4） | 已实现 | | 本模块 |
| `commit_gates/long_param_list_gate.py` | §0.1 | 长参数列表阻断门禁（NO-LONG-PARAM-LIST，§5.150防复发，AST检测新增函数参数数>7） | 已实现 | | 本模块 |
| `commit_gates/bare_sql_gate.py` | §0.1 | 裸SQL字面量阻断门禁（NO-BARE-SQL，§5.160.2防复发，diff检测SELECT/INSERT/UPDATE/DELETE） | 已实现 | | 本模块 |
| `commit_gates/depgraph_write_path_gate.py` | §0.1 | depgraph写入路径白名单门禁（DEPGRAPH-WRITE-PATH，裁定#ARCH-DEPGRAPH_ACCESS_CONTROL，diff检测非白名单文件中的writable-params） | 已实现 | | 本模块 |
| `commit_gates/god_class_gate.py` | §0.1 | God Class阻断门禁（NO-GOD-CLASS，§5.150防复发，AST检测新增类方法数>20） | 已实现 | | 本模块 |
| `commit_gates/high_complexity_gate.py` | §0.1 | 高循环复杂度阻断门禁（NO-HIGH-COMPLEXITY，§5.158防复发，AST检测McCabe复杂度>15） | 已实现 | | 本模块 |
| `commit_gates/tests_coverage_gate.py` | §0.1 | Gate测试覆盖率校验meta-gate（META-TESTS-COVERAGE，#ARCH-057，守卫者的守卫者） | 已实现 | | 本模块 |
| `commit_gates/gate_repo.py` | §0.1 | gate仓库（已正确指向MOD-GATE_ENGINE） | 已实现 | | 本模块 |
| `commit_gates/blueprint_format_gate.py` | §0.1 | [BLUEPRINT]头部module_id格式阻断门禁（BLUEPRINT-FORMAT，裁定#214 Phase 0防蔓延，裁定#208双轨制MOD-/SH-前缀校验） | 已实现 | | 本模块 |
| `commit_gates/ch_batch_size_gate.py` | §0.1 | CH批量写入防回退门禁（CH-BATCH-SIZE，§18.4防复发，AST检测write_result在循环内直接调用） | 已实现 | | 本模块 |
| `commit_gates/ch_final_gate.py` | §0.1 | ch_writer.query()直接调用阻断门禁（CH-FINAL-GATE，裁定#ARCH-CH-007 B5防复发，强制走ch_reader.query()自动注入FINAL） | 已实现 | | 本模块 |
| `commit_gates/ch_version_col_gate.py` | §0.1 | CH version列语义误用阻断门禁（CH-VERSION-COL，裁定#ARCH-CH-009防复发，diff检测ReplacingMergeTree非DateTime列作version参数） | 已实现 | | 本模块 |
| `commit_gates/test_source_consistency_gate.py` | §0.1 | 测试-源码符号一致性门禁（TEST-SOURCE-CONSISTENCY，§5.178防复发，检测tests/中import的符号在源码是否存在） | 已实现 | | 本模块 |
| `commit_gates/data_task_completeness_gate.py` | §0.1 | 数据任务完整性warn级门禁（DATA-TASK-COMPLETENESS，提醒新增tasks.yaml任务配置fallback_sources，数据韧性三层机制） | 已实现 | | 本模块 |
| `commit_gates/capability_consistency_gate.py` | §0.1 | Provider路由-meta一致性门禁（CAP-CONSISTENCY，裁定#ARCH-CH-022 Phase 4.4，AST检测staged *_provider.py的路由能力集vs meta.capabilities声明集不一致，priority=101） | 已实现 | | 本模块 |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = partially_implemented → 已实现章节的代码存在 | `ls src/zephyr/gov_enforcement/rule_enforcement/*.py` 核对 | ☐ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" src/zephyr/gov_enforcement/rule_enforcement/gate_engine.py` | ☐ |
| 门禁YAML注册表 = _registry.yaml内容 | `cat src/zephyr/gov_enforcement/rule_enforcement/_registry.yaml` | ☐ |
| 测试文件覆盖核心模块 | `ls tests/test_gate_*.py` | ☐ |
| G0-G7 YAML规则与蓝图§A描述一致 | 逐文件核对entry_conditions | ☐ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v0.6.0 (基线) | gate_engine.py + circuit_breaker.py + 5个KMS YAML + task_completion_gate.py + contract_template_manager.py + ai_capability_guard.py + _registry.yaml + _template.yaml + G0/G6/G7 YAML + MAD YAML | gate_context/pipeline/simulator/override/health/integrity_guard/audit_chain_verifier/adaptive_threshold | 未实现(Beta/Experimental) |
| v0.7.0 (容量升级) | 同v0.6.0 | cold_start.py / script_cache.py / backpressure.py / agent_quota.py / degradation.py / hot_reload.py / metrics.py / bulkhead第5池 | Phase A/B/C 待施工 |

### §0.4 SSoT 与责任唯一性声明

| # | 声明维度 | 本蓝图是真源 | 真源在别处（委托） | 委托目标 |
|---|---------|:----------:|:---------------:|---------|
| 1 | G0-G7任务门禁规则 | ✅ | ❌ | — |
| 2 | G1-G5 KMS决策门规则 | ✅ | ❌ | — |
| 3 | 门禁域熔断器参数 | ✅ | ❌ | — |
| 4 | 熔断器基类(CircuitBreaker状态机) | ❌ | ✅ | MOD-INF-016 §2.4 |
| 5 | 门禁评估管线 | ✅ | ❌ | — |
| 6 | 容量架构(六大支柱+12缺口+SLO) | ✅ | ❌ | — |
| 7 | 法证审计协议(哈希链+决策快照) | ✅ | ❌ | — |
| 8 | 自指硬化协议(完整性守卫+信任根) | ✅ | ❌ | — |
| 9 | 容量SLO全局注册 | ❌ | ✅ | MOD-INF-001 §13 |
| 10 | 指标采集/聚合/Grafana | ❌ | ✅ | MOD-INF-015 |

### §0.5 代码目录唯一性声明

| # | 声明项 | 值 |
|---|--------|-----|
| 1 | 主代码目录 | `src/zephyr/gov_enforcement/rule_enforcement/`（MUST与 frontmatter.actual_disk_path 一致） |
| 2 | 已知副本目录 | `src/zephyr/gov_enforcement/rule_enforcement/` — re-export shim（1文件） |
| 3 | 副本处置状态 | shim保留——向后兼容导入路径 |

---

### §0.6 四图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从四图真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-GATE_ENGINE`

#### 四图位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-GATE_ENGINE` 的 217 个 file 节点 | design | `extract_depgraph.py --modules MOD-GATE_ENGINE` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Draft | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-GATE_ENGINE | MOD-GATE_ENGINE | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | planned | planned | ✅ |
| file_count | 217 文件 | 28 文件（§0.1） | ❌ |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## §1 设计背景与目标
<!-- temporal_type: permanent -->

### §1.1 背景

门禁引擎将脚本exit code转化为PASS/FAIL决策并阻断不合规操作——覆盖任务执行前/后、知识入库/激活、代码提交时。

### §1.2 目标范围

| # | 目标 | 类型 | 可验证标准 |
|---|------|:---:|----------|
| 1 | G0-G7 八门禁覆盖任务全生命周期 DRAFT→COMPLETED | ✅ | 每个TaskStatus迁移点有对应门禁 |
| 2 | G1-G5 KMS决策门覆盖知识生命周期 | ✅ | 入库→分拣→评估→激活→提取全链路 |
| 3 | 容量支撑 10,000 脚本 / 1,500 模块 / 100 AI 并发 | ✅ | 增量扫描 < 1min，门禁评估 P99 < 200ms |
| 4 | 法证审计完整性——SHA-256哈希链+决策快照 | ✅ | 外部取证专家可独立验证任意历史判定 |
| 5 | 自指硬化——GateEngineIntegrityGuard+信任根 | ✅ | AI修改gate_engine.py时被检测并阻断 |
| 6 | 威胁模型覆盖——STRIDE 8类威胁全缓解 | ✅ | 每类威胁有对应缓解措施 |
| 7 | 门禁判定的具体检测逻辑 | ❌ | 脚本系统 MOD-INF-005 |
| 8 | 知识入库的具体规则 | ❌ | 知识库 MOD-KB-001 |
| 9 | pre-commit钩子框架 | ❌ | `.pre-commit-config.yaml` |
| 10 | 熔断后的修复执行 | ❌ | Orchestrator MOD-TASK_SYSTEM |
| 11 | 容量SLO全局注册 | ❌ | MOD-INF-001 §13 |

### §1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| 施工轨道：T轨可施工 | 门禁引擎核心已实现，容量升级Phase A/B/C待施工 |
| 硬件：i7-12700KF + 64GB + 1TB NVMe + RTX 3090 | 单机部署，无分布式 |
| Python 3.12+ / Pydantic V2 | 数据模型强制BaseModel |
| SQLite WAL / 单写者 | 并发写入需分片 |
| subprocess执行脚本 | GIL不影响，但启动开销存在 |

### §1.5 利益相关者映射

| 角色 | 关注点 | 参与阶段 | 约束 |
|------|--------|---------|------|
| Owner | 架构决策+熔断器参数+override审批 | 设计+施工 | 审批权限 |
| AI Agent | 门禁评估触发+结果消费 | 执行 | 遵守门禁判定 |
| Task System | TaskCard.status迁移触发门禁 | 集成 | CT-ORC-GATE-001 |
| Script System | 脚本exit code→门禁输入 | 集成 | CT-SCRIPT-GATE-001 |

### §1.6 当前态/目标态差距

| 维度 | 当前态 | 目标态 | 差距 | 优先级 |
|------|--------|--------|------|:------:|
| 门禁自动触发 | 手动调用evaluate() | TaskCard.status迁移自动触发 | CT-ORC-GATE-001未落地 | P0 |
| 脚本exit code→Gate判定 | 未接通 | 自动映射PASS/FAIL | CT-SCRIPT-GATE-001未落地 | P0 |
| 容量支撑 | ~268脚本/1-3AI | 10K脚本/100AI | 12个容量缺口 | P1 |
| 门禁域熔断器全链路 | 未测试 | OPEN→HALF_OPEN→CLOSED循环 | 无自动化测试 | P1 |
| 法证审计 | 代码存在但未验证 | 外部取证专家可独立验证 | 哈希链未端到端测试 | P2 |

### §1.7 典型场景

| 场景 | 触发 | 处理流程 | 输出 |
|------|------|---------|------|
| 任务准入 | TaskCard DRAFT→TODO | G0字段校验→PASS/FAIL | 任务进入TODO或留在DRAFT |
| 蓝图合规 | TaskCard TODO→IN_PROGRESS | G1蓝图存在性→G2依赖完整→G3容量检查 | 任务进入IN_PROGRESS或BLOCKED |
| 交付前审计 | TaskCard REVIEW→COMPLETED | G7关联脚本全量审计→PASS/FAIL | 任务完成或BLOCKED |
| 熔断触发 | 连续5次门禁FAIL | CLOSED→OPEN→60s→HALF_OPEN→试探 | 请求拒绝或恢复 |
| Owner旁路 | 紧急情况 | override(gate_id, justification, 24h)→审计记录 | 门禁临时绕过 |

---

## §2 模块边界
<!-- temporal_type: permanent -->

### §2.1 职责范围

| 管什么 | 说明 |
|--------|------|
| G0-G7 任务门禁 | 任务执行前/后的合规判定 |
| G1-G5 KMS 决策门 | 知识生命周期的阶段性判定 |
| GATE-18 pre-commit | 提交时全量测试收集 |
| GATE-16 蓝图读取合规检查 | AI改代码前是否读了蓝图（P1-2强制合规） |
| 门禁域熔断器 circuit_breaker | SQLite持久化+门禁集成版，基类SSoT=MOD-INF-016 |
| 门禁评估管线 | 排序/组合/上下文传播 |
| 影子模式/渐进式激活 | 新门禁安全上线 |
| 法证审计完整性 | SHA-256哈希链+决策快照 |
| 自指硬化 | GateEngineIntegrityGuard+信任根 |
| 容量调度 | 三级调度+反压+降级 |

#### 职责唯一性声明

| 声明项 | 无重叠模块 | 验证方式 |
|--------|-----------|---------|
| G0-G7任务门禁判定 | MOD-TASK_SYSTEM(消费方,非判定方) | Task System蓝图声明"门禁判定委托MOD-GATE_ENGINE" |
| G1-G5 KMS决策门 | MOD-INF-013(消费方) | MCP Servers蓝图引用gate_engine_server.py |
| 门禁域熔断器(特化版) | MOD-INF-016(基类SSoT) | §0.4声明委托关系+§10.5登记重叠 |
| 门禁评估管线 | MOD-INF-009(执行流门控,非合规判定) | §10.5术语区分 |
| 法证审计哈希链 | MOD-INF-021(回滚后G0验证,消费方) | Rollback蓝图声明依赖MOD-GATE_ENGINE §2.3 |

### §2.2 不包含的职责

| 不管什么 | 去哪 |
|----------|------|
| 门禁判定的具体检测逻辑 | 脚本系统 MOD-INF-005 |
| 知识入库的具体规则 | 知识库 MOD-KB-001 |
| pre-commit钩子框架 | `.pre-commit-config.yaml` |
| 熔断后的修复执行 | Orchestrator MOD-TASK_SYSTEM |
| 全局容量SLO注册 | MOD-INF-001 §13 |
| 指标采集/聚合/Grafana | Telemetry MOD-INF-015 |

---

## §3 架构设计
<!-- temporal_type: permanent -->

### §3.1 组件架构

#### 双门禁体系

| 门禁体系 | 门禁ID | 触发点 | 核心检查 |
|---------|--------|--------|---------|
| G0-G7 任务门禁 | G0 任务准入 | DRAFT→TODO | TaskCard必填字段完整 |
| | G1 蓝图合规 | TODO→IN_PROGRESS | 目标模块有approved蓝图 |
| | G2 依赖完整 | → | depends_on模块已实现 |
| | G3 容量检查 | → | 在全局容量预算内 |
| | G4 沙箱合规 | 执行中 | sandbox_profile匹配task_type |
| | G5 模型合规 | → | execution_model在能力矩阵内 |
| | G6 安全合规 | → | tool_call白名单检查 |
| | G7 交付前 | REVIEW→COMPLETED | 关联脚本exit 0 |
| G1-G5 KMS决策门 | G1 Ingest | 入库 | 来源可追溯?内容可验证?格式合规? |
| | G2 Triage | 分拣 | 归档/激活/丢弃? |
| | G3 Evaluate | 评估 | 四模型审计流水线通过? |
| | G4 Activate | 激活 | 人工确认+新鲜度+冲突裁决 |
| | G5 Extract | 提取 | ≥3个同类KE存在?模式置信度? |

> 代码文件清单见 §0.1。

#### 熔断器模式

> 已实现——代码文件是SSoT。蓝图只保留状态转换约束。

| 转换 | 条件 |
|------|------|
| CLOSED→OPEN | 连续FAIL次数≥5 |
| OPEN→HALF_OPEN | OPEN状态持续≥60s |
| HALF_OPEN→CLOSED | 试探全部PASS |

### §3.2 数据流

| 输入 | 映射 | 输出 |
|------|------|------|
| 脚本 exit 0 | → GATE-n PASS | 任务状态不变 |
| 脚本 exit 1 | → GATE-n PASS_WITH_WARNINGS | 任务 ⚠️ |
| 脚本 exit 2 | → GATE-n FAIL | 关联任务 BLOCKED |
| 脚本 exit 3 | → GATE-n CRITICAL_FAIL | 全部活跃任务 BLOCKED |
| TaskCard.status transition | → 对应门禁评估 | → PASS/FAIL → TaskCard.status迁移 |
| 文件变更 | → 依赖图谱L1→L2→L3 | → 增量脚本列表 → 门禁评估 |

### §3.3 状态生命周期

#### 门禁生命周期

| 状态 | 说明 | 转换规则 |
|------|------|---------|
| draft | 初始 | — |
| shadow | 评估→记录→不阻断 | →active: Owner审批 + ≥7d + 误报率<5% |
| active | 评估→阻断 | →deprecated: 需替代门禁active≥14d |
| deprecated | 退役中 | →removed: 最后引用removed满30d |
| removed | 已清理 | — |

#### Shadow Mode 三级激活

| 阶段 | 行为 | 持续条件 | 退出标准 |
|------|------|---------|---------|
| shadow | 评估→记录→不阻断 | ≥50次评估 且 ≥7天 | 误报率<5% 且 P0漏检率<1% |
| beta_enforce | P0阻断→P1/P2仅告警 | ≥100次评估 且 ≥14天 | P0误报率<1% 且 override次数<3 |
| full_enforce | P0/P1阻断→P2告警 | — | 连续30天无override |

#### 降级生命周期

| 级别 | 负载 | 激活门禁 | 不可降级底线 |
|------|------|---------|------------|
| tier_0_full | <70% | ALL门禁 | — |
| tier_1_degraded | 70-90% | 暂停shadow + P2全量拒绝 | — |
| tier_2_severe | 90-150% | G7D/G7C暂停 + 缓存ttl延长 | — |
| tier_3_critical | >150% | 仅G0+G6+熔断器 | G0+G6+熔断器 |

---

## §4 接口契约
<!-- temporal_type: permanent -->

### §4.1 公共 API

```python
class GateEngine:
    def evaluate(self, task: Task, gate_id: str, *, force_reevaluate=False) -> GateResult: ...
    def evaluate_pipeline(self, task: Task, pipeline_mode: str = "sequential") -> PipelineResult: ...

class GateSimulator:
    def simulate_all(self, task: Task, session_context: dict) -> SimulationReport: ...

class GateOverride:
    def override(self, gate_id: str, justification: str, duration_hours: float=24.0) -> OverrideRecord: ...
    def list_active_overrides(self) -> list[OverrideRecord]: ...
    def revoke(self, gate_id: str) -> bool: ...

class GateEngineIntegrityGuard:
    def verify_before_load(self) -> IntegrityCheckResult: ...
    def bootstrap_known_good_state(self, git_commit_hash: str) -> bool: ...
    def seal_current_state(self, owner_pgp_signature: bytes) -> bool: ...

class AuditChainVerifier:
    def verify_chain_integrity(self, decisions: list[HashedGateDecision]) -> ChainVerificationReport: ...
    def verify_single_decision(self, snapshot: DecisionSnapshot) -> bool: ...

class ManualApprovalGate:
    def request_approval(self, ke_id: str, ctx: GateContext) -> ApprovalRequest: ...
    def approve(self, approval_id: str, approver: str, notes: str) -> ApprovalResult: ...
    def reject(self, approval_id: str, approver: str, reason: str) -> ApprovalResult: ...
```

### §4.2 数据模型

> 已实现——代码文件是SSoT，蓝图只保留字段清单。

**GateResult**: gate_id: str | status: GateStatus(PASS/PASS_WITH_WARNINGS/FAIL/CRITICAL_FAIL) | reasons: list[str] | affected_tasks: list[str] | timestamp: datetime

**GateContext**: task_id: str | task_type: str | priority: str | assigned_model: str | target_module_id: str | module_blueprint_version: str | module_dependencies: list[str] | session_id: str | blueprint_reads: list[str] | tool_calls_made: list[str] | recent_gate_results: dict[str, GateResult] | circuit_breaker_states: dict[str, str] | capability_level: str | global_token_usage: int

**HashedGateDecision**: decision_id: str | sequence_number: int | previous_hash: str | gate_id: str | gate_result: GateResult | context_hash: str | snapshot_hash: str | timestamp: datetime | signature: str | None

**DecisionSnapshot**: task_card_snapshot: dict | gate_yaml_snapshot: dict | gate_yaml_version: str | gate_context_snapshot: dict | external_inputs: dict | evaluation_timestamp: datetime | gate_engine_version: str | python_version: str | gate_result: GateResult | evaluation_duration_ms: int

### §4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| GateEngine.evaluate() | task: Task, gate_id: str | ✅ | gate_id MUST在_registry.yaml中注册 |
| GateEngine.evaluate_pipeline() | task: Task, pipeline_mode: str="sequential" | ✅ | pipeline_mode ∈ {sequential, parallel_and, parallel_or, weighted, conditional} |
| GateSimulator.simulate_all() | task: Task, session_context: dict | ✅ | — |
| GateOverride.override() | gate_id: str, justification: str, duration_hours: float=24.0 | ✅ | owner MUST在OWNER_IDS中；circuit_breaker OPEN时禁止 |
| GateOverride.revoke() | gate_id: str | ✅ | — |
| GateEngineIntegrityGuard.verify_before_load() | — | — | — |
| GateEngineIntegrityGuard.bootstrap_known_good_state() | git_commit_hash: str | ✅ | — |
| GateEngineIntegrityGuard.seal_current_state() | owner_pgp_signature: bytes | ✅ | — |
| AuditChainVerifier.verify_chain_integrity() | decisions: list[HashedGateDecision] | ✅ | — |
| AuditChainVerifier.verify_single_decision() | snapshot: DecisionSnapshot | ✅ | — |
| ManualApprovalGate.request_approval() | ke_id: str, ctx: GateContext | ✅ | — |
| ManualApprovalGate.approve() | approval_id: str, approver: str, notes: str | ✅ | — |
| ManualApprovalGate.reject() | approval_id: str, approver: str, reason: str | ✅ | — |

### §4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| GateEngine.evaluate() | GateResult(passed=True/False, gate_id, violations=[]) | GateEvaluationError(gate_id未注册/评估超时) |
| GateEngine.evaluate_pipeline() | PipelineResult(dict[gate_id, GateResult]) | GateEvaluationError(管线配置无效) |
| GateSimulator.simulate_all() | SimulationReport(dict[gate_id, SimulationResult]) | — |
| GateOverride.override() | OverrideRecord(gate_id, owner, expires_at) | OverrideDeniedError(非Owner/circuit_breaker OPEN) |
| GateOverride.revoke() | bool | — |
| GateEngineIntegrityGuard.verify_before_load() | IntegrityCheckResult(status, violations) | — |
| GateEngineIntegrityGuard.bootstrap_known_good_state() | bool | — |
| GateEngineIntegrityGuard.seal_current_state() | bool | — |
| AuditChainVerifier.verify_chain_integrity() | ChainVerificationReport(is_valid, broken_at) | — |
| AuditChainVerifier.verify_single_decision() | bool | — |
| ManualApprovalGate.request_approval() | ApprovalRequest | — |
| ManualApprovalGate.approve() | ApprovalResult | — |
| ManualApprovalGate.reject() | ApprovalResult | — |

### §4.5 MCP 接口

| Tool | API | 输入 | 输出 | 错误码 |
|------|-----|------|------|--------|
| gate_evaluate | gate_engine.evaluate | {task_id, gate_id} | GateResult | 404=gate未注册, 429=熔断器OPEN |
| gate_batch_evaluate | gate_engine.evaluate_pipeline | {task_id, pipeline_mode} | PipelineResult | 同上 |
| gate_health | gate_engine.health_summary | {} | HealthReport | — |
| gate_override | gate_engine.override | {gate_id, justification, owner} | OverrideRecord | 403=非Owner, 409=熔断OPEN |
| gate_simulate | gate_engine.simulate | {task_id, session_context} | SimulationReport | — |
| gate_integrity | gate_engine.integrity_check | {} | IntegrityCheckResult | 503=验证失败 |
| blueprint_search | blueprint_search_server.search | {keywords} | list[BlueprintMatch] | — |

### §4.6 契约版本

| 契约 | 版本 | 稳定性 | 兼容性 | 说明 |
|------|------|--------|--------|------|
| GateEngine.evaluate() | v1 | stable | ✅向后兼容 | 核心API不变 |
| GateResult | v1 | stable | ✅向后兼容 | Pydantic模型 |
| GateContext | v0.1 | evolving | ⚠️需通知 | 字段可能扩展 |
| CBGManager | v1 | evolving | ⚠️需通知 | 池配置可能扩展 |
| GateOverride | v1 | evolving | ⚠️需通知 | TTL策略可能调整 |
| HashedGateDecision | v0.1 | evolving | ⚠️需通知 | 哈希算法可能升级 |
| CT-SCRIPT-GATE-001 | v1.0 | stable | ✅向后兼容 | exit code映射契约 |
| CT-ORC-GATE-001 | v1.0 | stable | ✅向后兼容 | TaskCard状态迁移触发契约 |
| 门禁YAML schema | v1 | evolving | ❌破坏性 | 新增check_type需注册 |

### §4.7 OCP 扩展点

| 扩展点 | 基类/接口 | 默认实现 | 扩展契约 | 注册方式 |
|--------|----------|---------|---------|---------|
| CheckType | gate_engine.py _CHECK_DISPATCH | _handle_encoding/_handle_field_presence等26个handler函数 | MUST添加_handle_<type>函数+注册到_CHECK_DISPATCH dict | gate_engine.py手动注册 |
| 门禁YAML | _template.yaml | 11节完整字段 | MUST遵循_template.yaml schema+写入_registry.yaml | _registry.yaml手动注册 |
| Bulkhead池 | circuit_breaker.py CBGManager | 4池(quick/content_analysis/ai_generated/disruptive) | 新增池MUST声明workers+threshold+cooldown | CBGManager配置注入 |

---

## §5 约束条件
<!-- temporal_type: permanent -->

### §5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | Python 版本 + 数据校验 | Python 3.12+ / Pydantic V2 |
| 2 | 数据库模式 | SQLite WAL / 单写者 |
| 3 | 脚本执行方式 | subprocess（非线程内import） |
| 4 | YAML解析安全 | yaml.safe_load + 1MB/20层/5s |
| 5 | 门禁YAML完整性 | 11节完整字段（_template.yaml强制） |
| 6 | check字段格式 | 布尔表达式 |
| 7 | reject配fix_hint | 每条reject的entry_condition必须配fix_hint |
| 8 | 状态变更通道 | task_repo.transition()（绕过=跳过门禁） |

### §5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|------|------|------|:---:|------|
| 受管模块数 | ~51 | 1,500 | 4 shard × 375 = 1,500 | 刚好 | shard扩展至8(>500模块/shard时) |
| 治理脚本数 | 268 | 10,000 | 增量15-30脚本/次 | 需验证 | 增量扫描+脚本缓存+依赖图谱 |
| 并发 AI Agent | 1-3 | 100 | 50 worker(三级调度) | 不够 | 三级调度+反压+Bulkhead隔离 |
| 脚本并发执行 | 8-24 worker | 40-100 | 50 worker | 不够 | Bulkhead 4+1池+优先级队列 |
| 增量扫描耗时 | ~1min | < 1min | 增量15-30脚本 | 够 | 依赖图谱增量更新 |
| 门禁评估延迟 P99 | 未测量 | < 200ms(warm) / < 50ms(hot) | subprocess启动开销 | 需验证 | 脚本缓存+热路径优化 |

**资源预算**：

| 资源 | 分配 | 饱和阈值 |
|------|------|---------|
| CPU | subprocess 40-50 workers(~80%逻辑线程) + gate_eval 8-12 workers + background 4 workers | 80% |
| 内存 | subprocess 10GB峰值 + gate_engine 500MB + vector_models 8GB + OS 8GB + headroom 37GB | 85% (54.4GB) |
| 磁盘 | SQLite shards 200MB + WAL 16MB + audit ~10MB/d + logs ~100MB/30d | NVMe 3GB/s读/2GB/s写 |

### §5.3 迁移/废弃方案
<!-- temporal_type: construction_temporary -->

> ⚠️ 临时时态：迁移方案执行完毕后从蓝图删除。

| # | 废弃/迁移对象 | 当前位置 | 目标位置 | 处理方式 | 引用更新方案 | 执行状态 |
|---|------|------|------|------|------|:-------:|
| 1 | SQLite单库写入 | `data/audit/gate_chain.db`(单文件) | 4-way分片 `gate_chain_shard_{0-3}.db` | 激活ShardRouter——新数据按module_id写入对应shard | 100+并发写入触发 | 未执行 |
| 2 | 历史数据 | 单库 | 按module_id重新分配到4 shard | 一次性迁移脚本 | Phase 1完成后 | 未执行 |
| 3 | shard_count扩展 | 4 shard | 8 shard | 扩展shard_count至8 | 单shard > 500模块 | 未执行 |

### §5.4 非功能需求与服务水平

| 维度 | NFR指标 | NFR目标 | 测量方式 | SLI | SLO | Error Budget | 告警阈值 |
|------|--------|--------|---------|-----|-----|-------------|---------|
| 可用性 | 门禁评估可用率 | 99.9% | 门禁评估成功/总请求 | gate_eval_success_rate | 99.9% | 每月允许0.1%失败 | <99.5%告警 |
| 延迟 | 门禁评估P99 | hot<50ms/warm<200ms | 评估耗时直方图 | gate_latency_p99_ms | <200ms(warm) | 超SLO=预算消耗 | >500ms告警 |
| 吞吐 | 门禁评估QPS | 50 eval/s | 评估计数/秒 | gate_eval_qps | ≥50/s | — | <30/s告警 |
| 误报 | 门禁误报率 | <5% | override次数/总FAIL | gate_false_positive_rate | <5% | — | >10%告警 |

### §5.5 自动化触发机制

| 操作 | 触发方式 | 调度策略 | 当前状态 |
|------|---------|---------|---------|
| 门禁评估(TaskCard状态迁移) | auto_event | TaskCard.status transition→自动触发对应门禁 | ⚠️待实现(CT-ORC-GATE-001) |
| 门禁评估(脚本exit code) | auto_event | 脚本执行完成→exit code映射→Gate判定 | ⚠️待实现(CT-SCRIPT-GATE-001) |
| 门禁YAML热更新 | auto_event | 文件变更监控→原子替换→模拟验证 | ⚠️待实现(GAP-C12) |
| 依赖图谱增量更新 | auto_scheduled | 文件变更时增量+每日全量重建 | ⚠️待实现(GAP-C04) |
| 容量压测 | auto_scheduled | 每个设计里程碑跑BM-01~05 | ⚠️待实现(GAP-C08) |
| Owner紧急旁路 | on_demand | 手动调用GateOverride.override() | ✅已实现 |
| 门禁健康报告 | on_demand | 手动调用GateHealthDashboard.generate_report() | ✅已实现 |
| 门禁模拟 | on_demand | 手动调用GateSimulator.simulate_all() | ✅已实现 |

### §5.7 禁止模式与导入约束

| # | 类型 | 禁止项 | 替代/允许项 | 原因 |
|---|:----:|--------|-----------|------|
| 1 | 编码模式 | 绕过门禁直接修改TaskCard.status | task_repo.transition()→自动触发门禁 | AP1 |
| 2 | 编码模式 | 跳过KMS门禁直接写入知识库 | G1→G2→G3→G4→G5完整管道 | AP2 |
| 3 | 编码模式 | 熔断器OPEN时手动override | 等待cooldown到期 | AP4 |
| 4 | 编码模式 | 全量扫描作为默认模式 | 增量扫描默认 | AP9 |
| 5 | 导入源 | 从zephyr.shared.resilience.circuit_breaker导入CircuitBreaker在门禁域 | 从zephyr.gates.circuit_breaker导入CBGManager | 门禁域需SQLite持久化版 |
| 6 | 编码模式 | 创建门禁但不注册_registry.yaml | 新建=copy _template.yaml+写入_registry.yaml | AP5 |

---

## §6 错误处理
<!-- temporal_type: permanent -->

| 错误场景 | 处理方式 | 恢复 |
|----------|---------|------|
| 门禁YAML解析失败 | 保留旧配置 + P1告警 + 记录失败原因 | 修复YAML后热更 |
| 脚本执行超时 | SIGTERM→wait 5s→SIGKILL + 标记该脚本FAIL | 修复脚本后重新触发G7 |
| gate_engine.py未捕获异常 | 外部看门狗检测进程僵死→重启→从快照恢复 | 连续3次重启→fail-closed deny-all |
| 熔断器OPEN | 等待cooldown到期→HALF_OPEN自动试探 | 禁止手动reset(AP4) |
| 依赖图谱未就绪 | 返回503 Service Unavailable + 预估就绪时间 | Agent指数退避重试 |
| hash chain断裂 | P0 alert + 从JSONL副本重建SQLite+重建hash链 | Owner手动验证 |
| 跨分片写入Phase 2失败 | 定期扫描PENDING条目→重试Phase 2 | 自动恢复 |
| 热更新配置差异>20% | 拒绝热更 + P0告警 | Owner审查差异 |

### §6.1 可观测性规格

| 指标名 | 类型 | 采集方式 | 告警阈值 | 告警级别 |
|--------|------|---------|---------|---------|
| gate_eval_duration_ms | Histogram | 自动埋点 | P99>500ms | P1 |
| gate_eval_total | Counter | 自动埋点 | — | — |
| gate_eval_fail_total | Counter | 自动埋点 | 错误率>5%(3min) | P1 |
| circuit_breaker_state | Gauge | 自动埋点 | OPEN持续>5min | P0 |
| gate_override_active | Gauge | 自动埋点 | >3个同时active | P2 |
| gate_false_positive_rate | Gauge | 周期计算 | >10% | P2 |
| gate_cache_hit_rate | Gauge | 周期计算 | <60% | P2 |

### §6.2 退化矩阵

| 组件 | 失败后可用功能 | 不可用功能 | 降级策略 | 恢复条件 |
|------|-------------|-----------|---------|---------|
| GateEngine | — | 全部门禁评估 | 外部看门狗检测→重启→快照恢复 | 进程恢复健康 |
| circuit_breaker | 仅G0+G6评估 | G1-G5/G7评估 | tier_3_critical降级 | 负载<70% |
| 依赖图谱 | 全量扫描兜底(3.5h) | 增量扫描 | 返回503+预估就绪时间 | 图谱重建完成 |
| SQLite审计 | 从JSONL副本重建 | 实时写入 | P0 alert+重建hash链 | 重建完成+验证 |
| known_good_hashes | fail-closed deny-all | 所有AI操作 | Owner PGP重新签名 | 签名验证通过 |

---

## §8 安全考量
<!-- temporal_type: permanent -->

### 攻击面与缓解

| 威胁类型 | 具体攻击 | 缓解 |
|---------|---------|------|
| Spoofing | AI伪造blueprint_read记录 | §L hash chain + 来源验证 |
| Tampering | 修改gate_engine.py添加bypass | §M GateEngineIntegrityGuard |
| Tampering | 修改SQLite审计记录 | §L hash chain |
| Repudiation | AI否认执行过危险操作 | §L decision snapshot + hash chain |
| Information Disclosure | 读取其他模块蓝图(未授权) | 需新增模块级蓝图读取范围检查 |
| Denial of Service | 构造极端任务触发门禁递归评估 | §G meta CB + 门禁评估深度限制 |
| Denial of Service | YAML billion laughs attack | YAML size limit + 解析超时 + yaml.safe_load |
| Elevation of Privilege | AI通过override获得不该有的权限 | §E override仅限Owner + PGP验证 |

### YAML解析安全

| 约束 | 值 |
|------|-----|
| max_file_size | 1MB |
| parse_timeout_ms | 5000 |
| max_depth | 20 |
| max_aliases | 100 |
| forbidden_constructors | !!python/object, !!python/name |
| MUST使用 | yaml.safe_load |

### TOCTOU硬化

| 约束 | 值 |
|------|-----|
| gate_id | G7 |
| trigger | deploy action invoked |
| check | ALL scripts re-run exit_code==0 AND files_checksum==G7_snapshot.files_checksum AND elapsed_since_G7<300s |
| on_fail | 拒绝部署+任务回退到REVIEW |

### AI博弈防护

| 行为 | 检测 | 缓解 |
|------|------|------|
| AI修复仅满足形式不解决实质 | fix_hint_effectiveness持续下降 | 随机抽查10%已通过G7任务→Owner深度审查 |
| AI避开需读蓝图的修改 | 被修改文件分布偏离任务分配分布 | 不确定性注入——偶尔显示门禁可能更严 |

---

## §9 测试策略
<!-- temporal_type: permanent -->

| 测试类型 | 覆盖范围 | 位置 |
|----------|---------|------|
| 单元测试 | gate_engine / circuit_breaker / contract_template_manager / task_completion_gate | `tests/test_*.py` |
| 集成测试 | G0-G7端到端门禁评估链路 | `tests/integration/test_gate_e2e.py` |
| 门禁YAML校验 | 每条entry_condition的PASS/FAIL两路径 | `validate_gate_discipline.py` |
| 容量压测 | BM-01~05五场景(见§17) | `scripts/benchmark/gate_engine_load_gen.py` |
| 哈希链验证 | 全链完整性+单决策重放 | `audit_chain_verifier.py` |
| 完整性守卫 | gate_engine.py/circuit_breaker.py哈希校验 | `gate_integrity_guard.py` |
| 热更新安全 | 新配置模拟评估→差异>20%拒绝 | `gate_pipeline.py simulate mode` |

---

## §10 依赖关系
<!-- temporal_type: permanent -->

### §10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|------|------|------|------|------|
| MOD-TASK_SYSTEM (Task System) | runtime_call | 读取TaskCard 28字段→G0-G7判定 | v1.0+ | docs/03_modules/_cross_layer/task_system/blueprint.md |
| MOD-INF-005 (Script System) | runtime_call | 脚本exit code→GATE-n PASS/FAIL (CT-SCRIPT-GATE-001) | v1.0+ | docs/03_modules/_domain_governance/governance_automation/blueprint.md |
| MOD-KB-001 (Knowledge Base) | data_flow | KE→G1-G5 KMS门禁管道 | v1.0+ | docs/03_modules/_cross_layer/knowledge_base/blueprint.md |
| MOD-CONTEXT_ENGINE (Context Engine) | config_consume | blueprint_routing.yaml上下文范围 | v0.5+ | docs/03_modules/_cross_layer/context_engine/blueprint.md |
| MOD-LLM_SECURITY (LLM Security) | sibling_check | fail-closed模式双门禁互校验 | v0.1+ | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md |
| MOD-INF-015 (Telemetry) | emit_to | GATE-16 blueprint_read_check→BLUEPRINT-READ-FREQ SLI | v0.5+ | docs/03_modules/_cross_layer/telemetry/blueprint.md |
| MOD-INF-009 (Session) | data_flow | session_id→Agent身份+配额管理 | v1.0+ | docs/03_modules/_cross_layer/session/blueprint.md |
| MOD-INF-001 (Capacity) | data_consume | 容量SLO注册表+风险注册表 | v1.0+ | docs/03_modules/_master_blueprint/blueprint.md |
| `architecture_model/layers/b_gates.yaml` | ssot | Gates YAML canonical source | — | architecture_model/layers/b_gates.yaml |

### §10.2 依赖图对齐声明

> 蓝图 §10.1 声明的依赖 MUST 与全局依赖图一致。不一致 = 漂移。
> 全局依赖图 SSoT：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
> 机器 SSoT：[cross-module-dependency-registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/cross-module-dependency-registry.yaml)

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在 registry 中有对应条目 | ⚠️全局depgraph数据质量待修 | `python scripts/governance/d5_architecture/validators/validate_dependency_graph_template.py` |
| 2 | §11 产出物路径 ↔ 依赖图 path_mappings | 路径一致 | ✅已对齐 | 同上 |
| 3 | §0 代码文件清单 ↔ 依赖图节点 code_path | 节点存在 | ✅已对齐 | 同上 |

### §10.3 内部依赖图

#### 执行顺序依赖

| 上游脚本 | 下游脚本 | 依赖内容 | 验证方式 |
|---------|---------|---------|---------|
| validate_gate_discipline.py | gate_engine.py | 注册一致性校验是门禁评估前置条件 | 检查_registry.yaml一致性 |
| gate_engine.py | task_completion_gate.py | G7依赖核心引擎的evaluate() | 检查gate_engine.py可导入 |
| gate_integrity_guard.py | gate_engine.py | 启动前自检是评估前置条件 | 检查known_good_hashes.yaml |

#### 数据流依赖

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| gate_engine.py | circuit_breaker.py | GateResult(PASS/FAIL) | 函数调用 |
| circuit_breaker.py | gate_engine.py | 熔断器状态(CLOSED/OPEN/HALF_OPEN) | 函数调用 |
| gate_engine.py | audit_chain_verifier.py | HashedGateDecision | SQLite + JSONL |
| gate_integrity_guard.py | gate_engine.py | IntegrityCheckResult | 函数调用(启动前自检) |

### §10.4 自动化规格

#### 是否需要自动化

| # | 自动化项 | 是否需要 | 理由 |
|---|---------|:-------:|------|
| 1 | 依赖图自动生成 | 是 | 9个依赖模块+55个门禁文件 |
| 2 | 依赖对齐自动验证 | 是 | 有9个外部依赖需对齐 |
| 3 | 临时时态内容自动清理 | 是 | §5.3有3个迁移方案 |
| 4 | 施工步骤完成度自动检测 | 是 | 施工Phase A/B/C进行中 |

#### 如何自动化

| # | 自动化项 | 实现方式 | 现有工具/脚本 | 缺口 |
|---|---------|---------|-------------|------|
| 1 | 依赖图自动生成 | AST解析import + manifest字段 | asset-inventory/dependency.py | 不覆盖gates/目录 |
| 2 | 依赖对齐自动验证 | CI门禁 | validate_dependency_graph_template.py | validate_path_alignment.py未创建 |
| 3 | 临时时态内容自动清理 | 压缩工作流脚本 | 无 | 需新建 |
| 4 | 施工步骤完成度自动检测 | pytest+mypy+ruff + 产出物存在性检查 | 部分有 | 需整合 |

#### 触发方式

| # | 自动化项 | 触发方式 | 触发条件 |
|---|---------|---------|---------|
| 1 | 依赖图自动生成 | CI pipeline | 文件变更时 |
| 2 | 依赖对齐自动验证 | CI门禁 | PR提交时 |
| 3 | 临时时态内容自动清理 | 手动 | 压缩工作流执行时 |
| 4 | 施工步骤完成度自动检测 | CI pipeline | 代码提交时 |

### §10.5 概念重叠声明

| # | 重叠概念 | 重叠维度 | 对方模块 | 委托关系 | 处置状态 |
|---|---------|---------|---------|---------|---------|
| 1 | 熔断器状态机 | 基类实现 | MOD-INF-016 | 本模块委托对方提供基类；本模块在基类上叠加SQLite持久化+门禁集成 | 已处置 |
| 2 | 门禁vs门控 | 术语重叠 | MOD-INF-009 | 本模块=合规判定门禁(G0-G7)；MOD-INF-009=执行流门控(M1-M11)——语义不同 | 已处置 |
| 3 | Kill Switch vs 熔断器 | 术语重叠 | MOD-INF-001 | 本模块=门禁域熔断器(异常传播阻断)；MOD-INF-001=系统级紧急制动——不同概念 | 已处置 |
| 4 | GateLevel枚举 | 枚举定义位置 | MOD-TASK_SYSTEM | 枚举定义在Task System，门禁判定SSoT在本模块 | 已处置(Task System已声明委托) |

### §10.6 依赖链风险评级

| # | 依赖链 | 链深度 | 风险等级 | 熔断机制 | 处置状态 |
|---|--------|:-----:|---------|---------|---------|
| 1 | 本模块→MOD-TASK_SYSTEM→MOD-DATABASE | 3 | L2 | 有(circuit_breaker) | 已有熔断 |
| 2 | 本模块→MOD-INF-005→subprocess | 2 | L1 | 有(超时+SIGKILL) | 已有熔断 |
| 3 | 本模块→MOD-INF-016→SQLite | 2 | L1 | 有(fail-closed) | 已有熔断 |
| 4 | 本模块→MOD-INF-001→容量SLO | 2 | L1 | 无 | 不适用(只读) |

---

## §11 产出物存放目录
<!-- temporal_type: permanent -->

> 核心.py/.yaml文件清单见 §0.1（含存在性+归属判定）。本节只列出 §0.1 未覆盖的产出物。

| 产出物类型 | 存放完整路径 | 职责 | consumer_min | 注册位置 |
|-----------|------------|------|-------------|---------|
| 门禁注册表Catalogs副本 | docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml | 声明式注册表 | MOD-INF-015 | — |
| 门禁测试(单元) | tests/test_gate_*.py | 单元测试 | — | — |
| 门禁测试(集成) | tests/integration/test_gate_e2e.py | 集成测试 | — | — |
| 门禁治理脚本 | scripts/governance/d6_security/validate_gate_discipline.py | 注册一致性校验 | — | script-manifest.yaml |
| 审计数据 | data/audit/gate_chain.db + data/audit/gate_chain.jsonl | 哈希链持久化 | audit_chain_verifier.py | — |
| 决策快照 | data/audit/snapshots_hot/ → snapshots_warm/ → snapshots_archive/ | 快照生命周期 | audit_chain_verifier.py | — |
| 已知良好哈希 | config/known_good_hashes.yaml | 信任根 | gate_integrity_guard.py | — |
| 容量压测 | scripts/benchmark/gate_engine_load_gen.py | 容量压测 | — | script-manifest.yaml |
| Prometheus指标 | src/zephyr/shared/metrics.py | 指标采集 | MOD-INF-015 | gates/__init__.py |
| 门禁类型契约 | src/zephyr/shared/contracts/core/gate_types.py | 共享类型定义 | gate_engine.py | contracts/__init__.py |

---

## §12 集成目标
<!-- temporal_type: permanent -->

| 集成目标 | 状态 | 验证方式 |
|------|:--:|------|
| G6硬合规阻断P0 | ✅ 已实现 | session_simulator.py Phase 2验证 |
| G0-G7全部8门禁YAML规则化 | ✅ 已实现 | G5 YAML §A.1-§A.4 |
| CT-SCRIPT-GATE-001落地 | 📋 Backlog | 脚本exit code→Gate判定链路 |
| CT-ORC-GATE-001落地 | 📋 Backlog | TaskCard.status transition→Gate触发 |
| 熔断器全链路测试 | 📋 Backlog | OPEN→HALF_OPEN→CLOSED循环 |
| 容量Phase A(地基) | 📋 Backlog | GAP-C01/C04/C03/C06 |
| 容量Phase B(稳定) | 📋 Backlog | GAP-C02/C07/C05/C11/C09 |
| 容量Phase C(保障) | 📋 Backlog | GAP-C08/C10/C12 |

### §12.1 域契约锚点

| 契约ID | 方向 | 描述 |
|--------|------|------|
| CT-SCRIPT-GATE-001 | MOD-INF-005→MOD-GATE_ENGINE | 脚本exit code→Gate判定映射 |
| CT-ORC-GATE-001 | MOD-TASK_SYSTEM↔MOD-GATE_ENGINE | TaskCard.status transition→Gate触发→PASS/FAIL→status迁移 |

---

## §13 需要更新
<!-- temporal_type: permanent -->

当本蓝图变更时，同步更新：

| # | 目标 | 更新内容 |
|---|------|---------|
| 1 | `docs/03_modules/blueprint_registry.yaml` | 版本号和完整度 |
| 2 | `config/blueprint_routing.yaml` | R009路由项 keywords/path_patterns |
| 3 | `src/zephyr/integration/mcp/gate_engine_server.py` | MCP工具描述引用本蓝图 |
| 4 | `src/zephyr/integration/mcp/blueprint_search_server.py` | 若keyword变更 |
| 5 | `docs/03_modules/_master_blueprint/blueprint.md` | MOD-MASTER_BLUEPRINT §2.8 CT-SCRIPT-GATE-001 |
| 6 | `config/known_good_hashes.yaml` | 门禁文件哈希变更 |

---

## §14 已知风险与缓解
<!-- temporal_type: permanent -->

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|:---:|:---:|---------|------|
| R1 | 门禁过度阻断——合法任务被拒绝 | 中 | 高 | severity=error仅用于不可逆损失——可逆问题用warning | 风险 |
| R2 | 门禁规则漂移——YAML中check与代码实际检查逻辑不一致 | 高 | 高 | CI门禁validate_gate_yaml.py→交叉校验YAML vs gate_engine代码 | 风险 |
| R3 | 熔断器误触发——正常流量波动被判定为异常 | 低 | 中 | threshold=5+cooldown=60s | 风险 |
| R4 | 门禁目录碎片化——1500模块后管理混乱 | 中 | 高 | 统一category分类(6种)→module专属门禁放入modules/<MOD-XXX>/ | 风险 |
| R5 | AI博弈门禁——长期session中AI学会为过门禁而工作 | 中 | 高 | 随机抽查+不确定性注入+质量反馈回灌 | 风险 |
| R6 | hash chain跨分片断裂——写入非原子 | 中 | 高 | 全局序列号+两阶段写入(§17 GAP-C09) | 风险 |
| R7 | Gate Engine不可用——所有任务状态迁移被阻断→AI无法推进任务→系统停摆 | 低 | 高 | 外部看门狗+进程重启+快照恢复 | 负面后果 |
| R8 | 熔断器永久OPEN——门禁判定全部拒绝→所有任务BLOCKED→需Owner手动介入 | 低 | 高 | cooldown自动试探+禁止手动reset(AP4) | 负面后果 |
| R9 | 审计链断裂——历史判定不可验证→合规审计失败→取证证据无效 | 低 | 高 | JSONL副本+从副本重建SQLite+重建hash链 | 负面后果 |
| R10 | 依赖图谱损坏——增量扫描无法精确推导→全量扫描兜底(3.5h) | 中 | 中 | 每日全量重建自愈+CoW原子替换 | 负面后果 |
| R11 | known_good_hashes被篡改——完整性守卫误判→合法门禁被拒绝或非法修改不被检测 | 低 | 高 | Owner PGP签名+GATE-18自指防护 | 负面后果 |

---

## §16 施工指引
<!-- temporal_type: construction_temporary -->

### 添加新门禁

```
1. cp src/zephyr/gov_enforcement/rule_enforcement/_template.yaml → src/zephyr/gov_enforcement/rule_enforcement/<category>/<new_gate>.yaml
2. 按_template.yaml的11节填写全部字段（check必须是布尔表达式）
3. 写入_registry.yaml的gates列表
4. 在gate_engine.py的_GATE_FILES映射中添加
5. 写tests/test_<new_gate>.py——至少覆盖每条entry_condition的PASS/FAIL两路径
6. 运行validate_gate_discipline.py→确认注册一致
```

### 修改现有门禁规则

```
1. 修改YAML中的entry_conditions
2. bump change_log.version
3. 重新运行相关test_<gate>.py
4. CI校验validate_gate_yaml.py自动触发
```

### 门禁模板升级

```
1. 修改_template.yaml→bump schema_version
2. 归档当前模板→_template_v{N}.yaml（不删除）
3. 在gate_engine blueprint变更记录中登记
4. 通知所有门禁维护者评估是否需要迁移
```

### §16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 4个Phase（scaffold→experimental→beta→production） |
| 施工模式 | 扩展（核心已实现，容量升级+自动化待施工） |
| 核心风险 | CT-ORC-GATE-001未落地→门禁非自动触发→AI可能绕过 |
| 目标 generation | 2 — 本次施工将蓝图从 generation 1 升级到 generation 2 |

### §16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | MOD-TASK_SYSTEM TaskRepository.transition()可调用 | hard | ✅ | ✅ |
| 2 | MOD-INF-005 脚本exit code语义统一(0/1/2/3) | hard | ✅ | ✅ |
| 3 | MOD-INF-016 shared/resilience/circuit_breaker.py可用 | soft | ✅ | ✅ |
| 4 | 容量Phase A冷启动+缓存+增量更新完成 | hard | ❌ | ❌ |

### §16.3 实施步骤

#### 步骤 1：CT-ORC-GATE-001落地——TaskCard.status迁移自动触发门禁

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 GateEngine.evaluate() + §12.1 CT-ORC-GATE-001 |
| 产出位置 | `src/zephyr/gov_enforcement/rule_enforcement/gate_engine.py` + `src/zephyr/data/persistence/task_repo.py` |
| 验收标准 | TaskCard.status DRAFT→TODO自动触发G0；REVIEW→COMPLETED自动触发G7 |
| 验证命令 | `python -m pytest tests/integration/test_gate_e2e.py -k test_auto_trigger` |
| G7 检查项 | 上游task_repo.py已列出？下游GateResult消费方已适配？回滚方案可执行？ |
| AI 自治范围 | human_gated——修改TaskRepository需Owner审批 |
| 检查点 | task_repo.py中transition()调用gate_engine.evaluate()成功 |

#### 步骤 2：CT-SCRIPT-GATE-001落地——脚本exit code→Gate判定映射

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §3.2 数据流 + §12.1 CT-SCRIPT-GATE-001 |
| 产出位置 | `src/zephyr/gov_enforcement/rule_enforcement/gate_engine.py` |
| 验收标准 | exit 0→PASS / exit 1→PASS_WITH_WARNINGS / exit 2→FAIL / exit 3→CRITICAL_FAIL |
| 验证命令 | `python -m pytest tests/test_gate_engine.py -k test_exit_code_mapping` |
| G7 检查项 | 四种exit code全覆盖？CRITICAL_FAIL传播链正确？ |
| AI 自治范围 | ai_modifiable——门禁引擎内部逻辑 |
| 检查点 | 四种exit code映射测试全部PASS |

#### 步骤 3：容量Phase A——冷启动+缓存+增量更新+优先级队列

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §17.2 GAP-C01/C03/C04/C06 + §17.3 升级组件1/3/4 |
| 产出位置 | `src/zephyr/governance/audit-orchestrator/cold_start.py` + `script_cache.py` + `dep_graph.py` patch + `bulkhead.py` patch |
| 验收标准 | 重启GateEngine→503→5s后200；相同输入两次扫描→第二次cache hit；P0请求在P2饱和时仍<1s |
| 验证命令 | `python -m pytest tests/test_gate_capacity.py` |
| G7 检查项 | 4个GAP全部覆盖？资源预算不超限？ |
| AI 自治范围 | ai_modifiable |
| 检查点 | 4个GAP验证全部PASS |

### §16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 1 | TaskRepository.transition()调用gate_engine失败 | 移除transition()中的门禁调用，恢复手动触发 |
| 2 | exit code映射逻辑错误 | 恢复默认PASS行为 |
| 3 | 容量组件性能退化 | 移除新增组件，恢复基线行为 |

### §16.5 施工完成与生产就绪标准

| # | 检查项 | 通过标准 | 类型 | 状态 |
|---|--------|---------|:----:|:----:|
| 1 | gate_engine.py无BOM+可导入 | `python -c "from zephyr.gates.gate_engine import GateEngine"` exit 0 | 完成 | ✅ |
| 2 | CT-ORC-GATE-001测试通过 | `pytest tests/integration/test_gate_e2e.py` exit 0 | 完成 | ☐ |
| 3 | CT-SCRIPT-GATE-001测试通过 | `pytest tests/test_gate_engine.py -k test_exit_code` exit 0 | 完成 | ☐ |
| 4 | SLO已定义且可测量 | §5.4每项SLI有测量方式 | 就绪 | ☐ |
| 5 | 退化策略已实现 | §6.2每个组件有降级逻辑 | 就绪 | ☐ |
| 6 | 回滚方案已验证 | §16.4回滚操作可执行 | 就绪 | ☐ |

### §16.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | in_progress | 审查者 |
| verification_status | unverified | 审计者 |
| code_alignment_verified | no | 审计者 |

### §16.7 参考实现规格

| # | 规格名称 | 类型 | 规格内容 | 对应代码 |
|---|---------|------|---------|---------|
| 1 | exit code→GateResult映射 | 协议 | exit 0→PASS / exit 1→PASS_WITH_WARNINGS / exit 2→FAIL / exit 3→CRITICAL_FAIL | gate_engine.py |
| 2 | 熔断器状态机 | 协议 | CLOSED→(5次FAIL)→OPEN→(60s)→HALF_OPEN→(试探PASS)→CLOSED | circuit_breaker.py |
| 3 | 门禁YAML 11节schema | Schema | gate_id/gate_name/title/trigger/entry_conditions/change_log/... | _template.yaml |
| 4 | 哈希链审计 | 算法 | SHA-256(decision.to_canonical_bytes())→previous_hash链接 | audit_chain_verifier.py |

### §16.8 施工参考卡

| # | 类型 | 名称 | 用途/说明 | 参数/字段 | 输出/约束 |
|---|:----:|------|----------|----------|----------|
| 1 | 命令 | `python -m zephyr.gates.gate_health` | 门禁健康报告 | `--alerts`: 仅告警 | HealthReport JSON |
| 2 | 命令 | `python -m zephyr.gates.gate_health --export-json` | JSON格式报告 | — | JSON(供Telemetry) |
| 3 | 配置 | `_template.yaml` → `entry_conditions` | 门禁条件定义 | check:布尔表达式;severity:error/warning | MUST配fix_hint |
| 4 | 配置 | `_registry.yaml` → `gates` | 全部门禁注册 | gate_id+path+status | 新建门禁MUST注册 |

### §16.10 故障与操作手册

| # | 阶段 | 场景 | 触发条件 | 诊断/操作 | 恢复/产出 | 验证/回退 |
|---|:----:|------|---------|----------|----------|----------|
| 1 | 施工 | BOM字符导致SyntaxError | import失败 | `python -c "from zephyr.gates.gate_engine import GateEngine"` | 移除BOM字节 | import成功 |
| 2 | 施工 | §0.1与实际代码不对齐 | 蓝图标记"未实现"但文件存在 | `ls src/zephyr/gov_enforcement/rule_enforcement/` 逐文件核对 | 更新§0.1存在性 | 蓝图与磁盘一致 |
| 3 | 运行 | 熔断器永久OPEN | 连续FAIL触发OPEN后不恢复 | 检查cooldown配置+HALF_OPEN试探日志 | 等待cooldown→自动试探 | CLOSED状态恢复 |
| 4 | 运行 | 哈希链断裂 | audit_chain_verifier报错 | 从JSONL副本重建SQLite+重建hash链 | 链完整性恢复 | verify_chain_integrity PASS |

### §16.12 并发操作模型

| 冲突场景 | 检测方式 | 解决策略 | 合并规则 |
|---------|---------|---------|---------|
| 同一门禁YAML同时修改 | SHA256校验 | 后写者重试 | 字段级合并 |
| 同一TaskCard门禁评估竞争 | TaskRepository行锁 | 排队等待 | FIFO |
| 多AI同时触发门禁评估 | Semaphore限流 | PriorityQueue调度 | P0优先 |

### 容量施工路线图

**Phase A：地基补齐（v0.7.0-alpha）**

| 缺口 | 施工内容 | 预估产出 | 验证方式 |
|:---:|---------|---------|---------|
| GAP-C01 | 冷启动协议：DepGraph.preload_or_build() + /health/ready + 缓存文件 | src/zephyr/governance/audit-orchestrator/cold_start.py | 重启GateEngine→验证503→5s后200 |
| GAP-C04 | 增量更新：DepGraph.update_incremental(manifest_diff) + 每日全量重建cron | dep_graph.py增量patch | 新增1脚本→图谱更新<100ms |
| GAP-C03 | 脚本缓存：ScriptCache + SQLite cache表 + 跨Agent共享 | src/zephyr/gov_enforcement/rule_enforcement/script_cache.py | 相同输入两次扫描→第二次全是cache hit |
| GAP-C06 | 优先级队列：PriorityQueue + 20% P0预留worker | bulkhead.py patch | P0请求在P2饱和时仍<1s获得worker |

**Phase B：稳定性加固（v0.7.0-beta）**

| 缺口 | 施工内容 | 预估产出 | 验证方式 |
|:---:|---------|---------|---------|
| GAP-C02 | 反压传播：BackpressureController + credit-based流控 | src/zephyr/gov_enforcement/rule_enforcement/backpressure.py | 模拟L3饱和→L1 refill_rate自动降速 |
| GAP-C07 | 长尾池：第5个Bulkhead池+耗时自动分类 | bulkhead.py新增long_tail池 | S2占满long_tail→quick池S0/S1不受影响 |
| GAP-C05 | Agent身份：AgentQuotaManager + per-session TokenBucket | src/zephyr/gov_enforcement/rule_enforcement/agent_quota.py | Agent超配额→429+其他Agent正常 |
| GAP-C11 | 优雅降级：四级降级树+DegradationController+自动恢复 | src/zephyr/testing/code_dedup/degradation.py | 模拟150%负载→自动进入tier_2→负载降→tier_0 |
| GAP-C09 | 跨分片一致性：全局序列号+两阶段写入 | shard_router.py patch | 并发写4 shard→hash chain序列号无跳跃 |

**Phase C：生产级保障（v0.7.0-rc）**

| 缺口 | 施工内容 | 预估产出 | 验证方式 |
|:---:|---------|---------|---------|
| GAP-C08 | 压测框架：gate_engine_load_gen.py + 5场景+报告生成 | scripts/benchmark/gate_engine_load_gen.py | 跑BM-01~05全部通过 |
| GAP-C10 | 容量监控：Prometheus metrics + 7告警规则 + Grafana dashboard | src/zephyr/shared/metrics.py + config/grafana/ | /metrics端点输出+告警规则验证 |
| GAP-C12 | 热更新：YAML/manifest文件监控+原子替换+模拟验证 | src/zephyr/gov_enforcement/rule_enforcement/hot_reload.py | 修改G1 YAML→5s内生效+无重启 |

### 施工Phase规划

| Phase | 任务 | 状态 |
|:---:|------|:---:|
| scaffold | gate_engine.py + 5个KMS门禁YAML | ✅ implemented |
| experimental | G0-G7完整判定逻辑 + CT-SCRIPT-GATE-001落地 | 📋 Backlog |
| beta | 熔断器全链路测试 + CI门禁自动交叉校验 | 📋 Backlog |

---

## §17 容量升级附录
<!-- temporal_type: permanent -->

### §17.1 容量基线

**规模目标**

| 维度 | 当前(v0.5.0) | 目标(v1.0.0) |
|------|:---:|:---:|
| 受管模块数 | ~51 | 1,500 |
| 治理脚本数 | 268 | 10,000 |
| 并发AI Agent | 1-3 | 100 |
| 脚本并发执行 | 8-24 worker | 40-100 |

**容量SLO**

| ID | 指标 | 目标 |
|----|------|------|
| GATE-CAP-001 | 依赖图谱查询P99 | <500ms |
| GATE-CAP-002 | 增量扫描P99(15-30脚本) | <60s |
| GATE-CAP-003 | 全量扫描(10,000脚本) | <4h |
| GATE-CAP-004 | 门禁评估吞吐量 | 50 eval/s |
| GATE-CAP-005 | SQLite shard写锁等待P99 | <100ms |
| GATE-CAP-006 | 依赖图谱重建耗时 | <5s |
| GATE-CAP-007 | Bulkhead池利用率 | <0.85 |
| GATE-CAP-008 | 冷启动至phase_2_ready | <5s(全量) / <500ms(缓存) |
| GATE-CAP-009 | 脚本结果缓存命中率 | >60% |
| GATE-CAP-010 | 反压恢复时间 | <60s |
| GATE-CAP-011 | Agent配额拒绝比例 | <3% |
| GATE-CAP-012 | S0/S1在long_tail饱和时P99 | <30s |
| GATE-CAP-013 | 150%负载下G0/G6可用率 | >99% |
| GATE-CAP-014 | 容量压测通过率(BM-01~05) | 100% |

### §17.2 缺口分析

**六大支柱**

| 支柱 | 核心问题 | 严重度 |
|------|---------|:---:|
| ① 脚本注册表 | 10K脚本发现 | 🔴 |
| ② 依赖图谱 | 变更→精确脚本列表 | 🔴 |
| ③ 并发调度 | 100AI并发调度 | 🔴 |
| ④ 存储分片 | 100AI并发写SQLite | 🔴 |
| ⑤ 故障隔离 | 单AI故障隔离 | 🟡 |
| ⑥ 资源预算 | 并发资源预算 | 🟡 |

**缺口清单**

| # | 缺口 | 严重度 | 设计方向 |
|---|------|:---:|---------|
| GAP-C01 | 冷启动与预热协议 | 🔴 P0 | 三级phase + 缓存预构建 + 分级加载 |
| GAP-C02 | 反压传播机制 | 🔴 P0 | credit-based流控 + 死信队列 |
| GAP-C03 | 脚本结果缓存与跨Agent复用 | 🔴 P0 | content-addressable全局共享 + SQLite缓存表 |
| GAP-C04 | 依赖图谱增量更新 | 🔴 P0 | 增量实时+全量定时自愈+CoW原子替换 |
| GAP-C05 | Agent身份与配额管理 | 🟡 P1 | per-session TokenBucket + 信任分级动态调整 |
| GAP-C06 | 优先级反转防护 | 🟡 P1 | PriorityQueue + 每池20% P0预留worker |
| GAP-C07 | 长尾脚本调度策略 | 🟡 P1 | 第5池long_tail + 耗时自动分类 + 超时逃逸 |
| GAP-C08 | 容量压测与基准策略 | 🟡 P1 | 5场景BM-01~05 + synthetic load生成器 |
| GAP-C09 | 跨分片一致性协议 | 🟡 P1 | 全局序列号 + 两阶段写入 |
| GAP-C10 | 容量监控与告警闭环 | 🟢 P2 | Prometheus metrics + 告警规则 |
| GAP-C11 | 优雅降级策略 | 🟢 P2 | 四级降级树 tier_0→tier_3 |
| GAP-C12 | 门禁热更新协议 | 🟢 P2 | YAML/manifest热更 + gate_engine.py冷重启 |

### §17.3 升级版本矩阵

**升级组件清单**

| # | 组件 | 当前状态 | 升级目标 | 所属Phase | 依赖缺口 |
|---|------|------|------|:---:|------|
| 1 | cold_start.py | 未实现 | 三级phase+缓存预构建+分级加载 | A | GAP-C01 |
| 2 | dep_graph.py | 部分实现 | 增量更新+CoW原子替换 | A | GAP-C04 |
| 3 | script_cache.py | 未实现 | content-addressable全局共享+SQLite缓存表 | A | GAP-C03 |
| 4 | bulkhead.py | 已实现(4池) | 新增第5池long_tail+P0预留20%worker | A | GAP-C06 |
| 5 | backpressure.py | 未实现 | credit-based流控+死信队列 | B | GAP-C02 |
| 6 | agent_quota.py | 未实现 | per-session TokenBucket+信任分级 | B | GAP-C05 |
| 7 | degradation.py | 未实现 | 四级降级树+DegradationController+自动恢复 | B | GAP-C11 |
| 8 | shard_router.py | 部分实现 | 全局序列号+两阶段写入 | B | GAP-C09 |
| 9 | gate_engine_load_gen.py | 未实现 | 5场景压测+报告生成 | C | GAP-C08 |
| 10 | metrics.py | 未实现 | Prometheus指标+7告警规则+Grafana dashboard | C | GAP-C10 |
| 11 | hot_reload.py | 未实现 | YAML/manifest监控+原子替换+模拟验证 | C | GAP-C12 |

**三级调度模型**

| 层级 | 组件 | 参数 |
|------|------|------|
| L1_admission | TokenBucket | refill_rate=20, burst_size=100 |
| L1_admission | PriorityQueue | [P0, P1, P2] |
| L1_admission | rejection_policy | P2任务被拒绝时返回429+Retry-After |
| L2_dispatch | bulkhead: quick | workers=24, CB threshold=10, cooldown=30s |
| L2_dispatch | bulkhead: content_analysis | workers=12, CB threshold=5, cooldown=60s |
| L2_dispatch | bulkhead: ai_generated | workers=8, CB threshold=5, cooldown=120s |
| L2_dispatch | bulkhead: disruptive | workers=6, CB threshold=3, cooldown=180s |
| L2_dispatch | total_workers | 50 |
| L3_execution | timeout | S0=10s / S1=60s / S2=180s / S3=120s |
| L3_execution | isolation | 每个脚本独立subprocess——crash不影响其他 |

**依赖图谱三层索引**

| 层级 | 映射 | 规模 |
|------|------|------|
| L1_file_to_module | 文件路径→所属模块ID | ~50K映射, <5MB |
| L2_module_to_scripts | 模块ID→关联治理脚本列表 | ~50K映射, <10MB |
| L3_script_to_dependencies | 脚本间依赖→DAG edges | 从depends_on字段构建 |

查询路径：文件变更→L1→L2→L3→最终脚本列表(去重+拓扑排序)。预期输出：15-30脚本(增量) / 10,000脚本(全量)

**存储分片**

| 参数 | 值 |
|------|-----|
| shard_count | 4 |
| shard_strategy | hash(module_id) % shard_count |
| per_shard | ~375模块, ~25并发写入 |
| global_tables | module_registry, gate_registry, circuit_breaker_state |
| cross_shard_queries | 并发查询4 shard→内存合并→<500ms |

**容量压测场景**

| ID | 场景 | 负载 | 通过标准 |
|----|------|------|---------|
| BM-01 | 单脚本基准 | 0并发 | 记录P50/P99 |
| BM-02 | 增量峰值 | 100并发/20±5脚本 | P99<60s, error<1%, 429<5% |
| BM-03 | 持续负载 | 50并发/20min间隔/1h | 内存增长<100MB/h, WAL<50MB |
| BM-04 | 过载 | 150并发/5min | 不崩溃, G0/G6仍PASS, 恢复<60s |
| BM-05 | 全量扫描隔离 | 1全量/50worker | <4h, 增量P99<2s |

---

## §18 决策记录
<!-- temporal_type: permanent -->

> 本节同时覆盖原 §7 备选方案——"选项"列已包含备选方案信息。
> 本节同时覆盖原 §15 后果——负面后果合并到 §14 风险，正面后果与 §1 目标重复。
> 时态属性：决策记录属于永久时态——AI 修改设计时必读。

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | DD1 | 门禁数量 | 五门禁/G0-G7八门禁/十二门禁 | G0-G7八门禁 | 覆盖任务生命周期7个状态过渡点+1准入门 | 2026-05-03 |
| 2 | DD2 | 门禁执行模式 | Validating-only/Mutating/Validating+Mutating可选 | Validating-only(当前)，Mutating为可选 | experimental优先实现硬阻断 | 2026-05-03 |
| 3 | DD3 | 熔断器参数 | threshold∈{3,5,10}×cooldown∈{30,60,120}s | threshold=5,cooldown=60s | 连续5次FAIL=系统性问题；60s足够短暂恢复 | 2026-05-03 |
| 4 | DD4 | KMS与任务门禁引擎 | 共享gate_engine/独立引擎 | 共享gate_engine | 减少引擎碎片化——同一判定接口复用 | 2026-05-03 |
| 5 | DD5 | GATE-18与G0-G7关系 | 独立/统一 | 独立 | pre-commit是git层守卫(hot≤50ms)，G0-G7是任务层(warm) | 2026-05-03 |
| 6 | DD6 | 门禁目录组织 | 按category/按module_id | 按category | 按module_id会1500目录×2-3门禁=碎片化 | 2026-05-04 |
| 7 | DD7 | 门禁管线模式 | 单一par_and/五模式 | 五模式 | 不同stage需不同调度策略 | 2026-05-04 |
| 8 | DD8 | 门禁激活策略 | 一步激活/三级激活 | Shadow→Beta→Full三级激活 | shadow数据对升级决策至关重要 | 2026-05-04 |
| 9 | DD9 | Override时长 | 永久/24h限定 | 24h限定 | 永久=门禁形同虚设 | 2026-05-04 |
| 10 | DD10 | GateContext字段 | 最小集/含session_id+blueprint_reads | 含session_id+blueprint_reads | 门禁判定需跨模块上下文 | 2026-05-05 |
| 11 | DD11 | Meta CB降级策略 | 全降级/保持P0门禁 | 保持P0门禁 | G0/G6/G7是弹簧门——降级也不能跳过 | 2026-05-05 |
| 12 | DD12 | adaptive_threshold行为 | 自动改/仅建议 | 仅建议 | experimental阶段Owner保持完全控制 | 2026-05-05 |
| 13 | DD13 | 审计方式 | 纯SQLite/SHA-256哈希链 | SHA-256哈希链 | 取证专家必须能独立验证 | 2026-05-05 |
| 14 | DD14 | 决策记录方式 | 仅结果/全量快照 | 全量快照 | 无快照=不可重现=审计不可行 | 2026-05-05 |
| 15 | DD15 | 完整性校验时机 | 评估后/评估前 | 评估前 | 先度量再信任 | 2026-05-05 |
| 16 | DD16 | 信任根 | Git SHA-1+Owner PGP/其他 | Git SHA-1历史+Owner PGP | Git哈希链不可篡改——Python文件可以 | 2026-05-05 |
| 17 | DD17 | YAML安全策略 | 仅safe_load/safe_load+大小/深度/超时 | safe_load+大小/深度/超时 | safe_load只防代码执行不防DoS | 2026-05-05 |
| 18 | DD18 | G7D深度合规 | 不实现/experimental | experimental | 形式质量互补——否则质量信号在G7后完全断裂 | 2026-05-05 |
| 19 | DD19 | 调度模型 | 单级线程池/三级调度 | 三级调度 | 100AI无法用flat thread pool | 2026-05-10 |
| 20 | DD20 | 脚本执行方式 | 线程内import/subprocess | subprocess | Python GIL——线程内执行=串行 | 2026-05-10 |
| 21 | DD21 | Shard扩展策略 | 4shard固定/4→8渐进/16shard一开始 | 4→8渐进 | 4shard时写竞争可接受；>500模块/shard时扩展 | 2026-05-10 |
| 22 | DD22 | 依赖图谱存储 | 全内存/SQLite按需查询 | 全内存(~25MB) | 磁盘查询会拖慢>10× | 2026-05-10 |
| 23 | DD23 | G7扫描模式 | 全量/增量 | 增量 | 10,000脚本全量G7=3.5h | 2026-05-10 |
| 24 | DD24 | manifest覆盖率阻断阈值 | 无/95% | 95%硬阻断P0 | 未注册=隐形脚本=漏检黑洞 | 2026-05-10 |
| 25 | DD25 | 全量扫描触发 | 任意触发/仅Owner | 仅Owner | 全量3.5h是系统级事件 | 2026-05-10 |
| 26 | DD26 | Worker数调整 | 固定/动态(+5/-5) | 动态(+5/-5) | 固定worker浪费或不够 | 2026-05-10 |
| 27 | DD27 | Agent缓存策略 | 全局共享/per-Agent分区 | per-Agent缓存分区 | 多Agent场景下全局缓存会导致脏读 | 2026-05-10 |
| 28 | DD28 | 脚本上限 | 硬限制/设计约束 | 设计约束非硬限制 | 超过后性能降级但不崩溃 | 2026-05-10 |
| 29 | DD29 | 扫描默认模式 | 全量/增量 | 增量默认，全量周检可选 | 对齐日常<1min体验要求 | 2026-05-10 |
| 30 | DD30 | 容量瓶颈定位 | 门禁判定/脚本调度 | 脚本调度 | 容量瓶颈在脚本调度不在门禁判定 | 2026-05-10 |
| 31 | DD31 | 冷启动策略 | 同步阻塞/503+指数退避 | 503+指数退避 | 同步阻塞会耗尽AI Agent连接池 | 2026-05-10 |
| 32 | DD32 | 反压机制 | 速率限流/信用流控 | 信用流控(credit-based) | 速率限流不管下游能不能处理 | 2026-05-10 |
| 33 | DD33 | 脚本结果缓存范围 | per-Agent隔离/全局共享 | 全局共享 | 脚本是纯函数——与Gate判定不同 | 2026-05-10 |
| 34 | DD34 | 依赖图谱重建策略 | 每次全量/每日全量+增量日常 | 每日全量+增量日常 | 增量可能累积微小不一致——全量自愈 | 2026-05-10 |
| 35 | DD35 | Agent配额策略 | 固定配额/动态调整 | 动态调整(历史行为信任分级) | 固定配额要么太松要么太严 | 2026-05-10 |
| 36 | DD36 | P0优先保障 | 纯PriorityQueue/每池20%预留 | 每池20% worker预留P0 | 纯PriorityQueue在P0到达时仍需等当前P1执行完 | 2026-05-10 |
| 37 | DD37 | 长脚本调度 | 与短脚本同池/专用池 | 第5池long_tail(>60s) | quick池S0/S1被长脚本拖慢——HoL Blocking | 2026-05-10 |
| 38 | DD38 | 压测方式 | mock/真实subprocess | 真实subprocess | mock无法暴露subprocess启动/通信的真实开销 | 2026-05-10 |
| 39 | DD39 | 全局序列号分配 | 各shard独立/shard_0统一 | shard_0统一 | SQLite单写者天然保证唯一性和单调性 | 2026-05-10 |
| 40 | DD40 | 指标标准 | 自定义/Prometheus兼容 | Prometheus兼容+Telemetry集成 | OpenMetrics是CNCF标准 | 2026-05-10 |
| 41 | DD41 | 降级策略 | 二元开关/四级降级 | 四级降级(full→degraded→severe→critical) | 二元开关要么全开要么全关 | 2026-05-10 |
| 42 | DD42 | 更新策略 | 全部热更/YAML热更+代码冷重启 | YAML热更+代码冷重启 | Python模块热替换生产环境不可靠 | 2026-05-10 |

---

## ⚠️ Vibe Coding 蓝图编写铁律
<!-- temporal_type: permanent -->

> 时态属性：本节属于施工声明——AI 进入蓝图修改/施工时必读。不可改为链接引用。永久保留。

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | 所有路径必须是绝对路径（含盘符 `D:\`） | 文件创建到错误位置 |
| 2 | 必备链接不可省略——即使与前序文档重复也必须完整列出 | AI 跳过不读，施工时缺少关键信息 |
| 3 | 蓝图必须是最终设计结果——不记录决策过程、不保存未选方案 | 蓝图过厚，关键信息被噪音淹没 |
| 4 | 产出物路径必须与 GOV-DOC-002 一致 | 路径幻觉——文件放错位置 |
| 5 | 涉及文件范围必须明确列出 | 范围漂移——改了不该改的文件 |
| 6 | 蓝图 §4 文件清单 ↔ 代码 `[BLUEPRINT]` 字段 MUST 双向对齐 | 蓝图与代码漂移 |
| 7 | 每个章节 MUST 标注对应代码路径 | AI 找不到实现位置 |
| 8 | "待定"/"建议"/"按需"等模糊词禁止使用 | AI 自行决定，可能选错 |
| 9 | 蓝图必须自包含——关键信息不能只写"详见XX" | AI 缺少关键上下文 |
| 10 | 删除文件必须遵守安全删除协议——禁止直接删除任何文件 | 永久丢失——无法恢复 |
| 11 | construction_progress 必须与代码实际状态一致 | 重复造轮子或跳过施工 |
| 12 | actual_disk_path 必须与 §11 产出物路径一致 | 搜索失败、导入错误 |
| 13 | 已实现代码不在蓝图中重复——§0.1 标记`已实现`的模块，蓝图只保留接口签名（§4） | AI 改蓝图忘改代码，或改代码忘改蓝图 |
| 14 | 临时时态内容执行完毕后从蓝图删除——迁移方案、升级执行计划等，一旦执行完毕即从蓝图删除 | 蓝图膨胀，关键信息被历史噪音淹没 |
| 15 | 蓝图内容拆分判定——职责不同→拆分独立蓝图；职责相同→原地升级。判定标准见"蓝图拆分判定标准" | AI 不知道该读哪个蓝图，跨模块影响无法追踪 |

---

## 蓝图拆分判定标准
<!-- temporal_type: permanent -->

> 铁律 #15 的操作定义——当蓝图内容超过 ~800 行或包含多个独立职责域时，MUST 执行。

### 判定流程

```
STEP 1: 识别职责域
  蓝图中的内容是否属于同一职责域？
  判定标准：该内容的服务对象、变更频率、依赖关系是否与蓝图主体一致？

STEP 2: 职责域判定
  ├ 职责相同（同一模块的升级/扩展）→ 原地升级
  │   条件：服务对象相同 + 变更频率同步 + 依赖关系重叠
  │   操作：在 §17 容量升级附录中增量记录
  │
  └ 职责不同（独立子系统/独立能力域）→ 拆分独立蓝图
      条件（满足任一即触发）：
      a) 有独立的 module_id 前缀
      b) 有独立的 Phase 路线图和交付节奏
      c) 有独立的依赖关系图（与蓝图主体的 depends_on 交集 <50%）
      d) 内容超过 100 行且与蓝图主体无直接数据流
      操作：创建子蓝图，本蓝图 §10 依赖关系引用子蓝图

STEP 3: 拆分后验证
  - 拆分出的蓝图 MUST 有独立 frontmatter + 概述 + §0~§18
  - 拆分出的蓝图 belongs_to = 本蓝图 module_id
  - 本蓝图 §10 依赖关系新增子蓝图引用
  - blueprint_registry.yaml 同步更新
```

---

## ⚠️ 安全删除协议
<!-- temporal_type: permanent -->

> 时态属性：本节属于施工声明——AI 施工涉及删除时必读。永久保留。

| 步骤 | 操作 |
|------|------|
| 1 | 检查文件是否在 `_registry.yaml` / `__init__.py` / `script-manifest.yaml` 中被引用 |
| 2 | 检查是否有其他文件与它内容完全相同且已注册 |
| 3 | 逐行检查内容是否在其他地方存在——有唯一价值 → 重新安置并注册 |
| 4 | 全部冗余 → `python scripts/governance/d5_architecture/pre_write_gate.py <文件> --delete` |

---

## 必备链接
<!-- temporal_type: permanent -->

> 时态属性：本节属于施工声明——AI 进入蓝图时必读。永久保留。

| 链接 | 用途 |
|------|------|
| [project_rules.md](file:///d:/ZephyrAlpha/.trae/rules/project_rules.md) | 四条铁律 + 防幻觉十八条 |
| [registry_of_registries.yaml](file:///d:/ZephyrAlpha/docs/registry_of_registries.yaml) | 全项目注册表入口 |
| [blueprint-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md) | 蓝图模板 v3.5 |
| [trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml) | 压缩工作流标准 GOV-DOC-011 |
| [code-construction-standards.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md) | 代码构建标准 GOV-ENG-001 |
| [quality-standard.md](file:///d:/ZephyrAlpha/scripts/governance/quality-standard.md) | 脚本质量标准 SCRIPT-QUALITY-001 |
| [b_gates.yaml](file:///d:/ZephyrAlpha/architecture_model/layers/b_gates.yaml) | Gates YAML SSoT |
| [MOD-MASTER_BLUEPRINT blueprint](file:///d:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint.md) | 总蓝图——CT-SCRIPT-GATE-001 + CT-ORC-GATE-001 |
| [gate_engine.py](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_enforcement/gate_engine.py) | 核心门禁引擎实现 |
| [_registry.yaml](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_enforcement/_registry.yaml) | 全部门禁注册表 SSoT |

---

## 已有类似功能
<!-- temporal_type: permanent -->

| 功能 | 位置 | 覆盖度 | 复用决策 |
|------|------|:---:|---------|
| BulkheadExecutor 4池隔离 | `src/zephyr/gov_enforcement/rule_enforcement/circuit_breaker.py` | 80% | 扩展——新增第5池 long_tail |
| ShardingRouter | `src/zephyr/gov_enforcement/rule_enforcement/` | 40% | 扩展——激活+跨分片一致性 |
| DependencyGraph | `src/zephyr/gov_enforcement/rule_enforcement/` | 60% | 扩展——增量更新+预热协议 |
| GateEngine.evaluate() | `src/zephyr/gov_enforcement/rule_enforcement/gate_engine.py` | 70% | 扩展——管线化+上下文传播 |

---

## 涉及的文件范围
<!-- temporal_type: permanent -->

| 目录 | 文件数 | 说明 |
|------|:---:|------|
| `src/zephyr/gov_enforcement/rule_enforcement/` | 55 | 门禁引擎核心实现（.py + .yaml） |
| `src/zephyr/gov_enforcement/rule_enforcement/` | 1 | re-export shim |
| `tests/` | 5 | 门禁单元测试 |
| `tests/integration/` | 1 | 门禁端到端测试 |
| `scripts/governance/d6_security/` | 1 | validate_gate_discipline.py |
| `architecture_model/layers/` | 1 | b_gates.yaml SSoT |

---

## 1. 已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> 门禁引擎——gate_engine.py+5个KMS YAML门禁已实现

### 1.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/gov_enforcement/rule_enforcement/_registry.yaml` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/_template.yaml` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/adaptive_threshold.py` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/admission/mad-001-architecture-necessity.yaml` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/admission/mad-002-phase-relevance.yaml` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/admission/mad-003-dependency-compliance.yaml` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/admission/mad-004-interface-definability.yaml` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/admission/mad_005_dependency_graph_template.yaml` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/ai_capability_guard.py` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/anti_pattern_guard.py` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/audit_chain_verifier.py` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/breaking_change_detector.py` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/can_i_deploy.py` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/capability_checker.py` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/cbac_matrix.py` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/cdc_broker.py` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/circuit_breaker.py` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/contract_template_manager.py` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/drift-detector.py` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/end_to_end_walkthrough.py` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/g1-ingest.yaml` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/g2-triage.yaml` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/g3-evaluate.yaml` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/g4-activate.yaml` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/g5-extract.yaml` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/g6-blueprint-compliance.yaml` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/g6-ctr-compliance.yaml` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/g6-path-tree-freshness.yaml` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/g7-position-limits.yaml` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/g8.yaml` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/g8-leverage.yaml` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/g9.yaml` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/g9-strategy-correlation.yaml` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/g-asset-inventory.yaml` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/gate-dedup.yaml` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/gate_context.py` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/gate_engine.py` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/gate_health.py` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/gate_integrity_guard.py` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/gate_override.py` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/gate_pipeline.py` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/gate_simulator.py` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/gate_types.py` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/gct-024-budget-enforcer.yaml` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/integration_test_runner.py` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/invariants/en_001_circular_dependency.py` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/invariants/en-001-circular-dependency.yaml` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/invariants/en_002_enforcement_validator.py` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/invariants/en-002-enforcement-validator.yaml` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/invariants/en_003_contract_compatibility.py` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/invariants/en-003-contract-compatibility.yaml` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/invariants/en_process_lifecycle_gateway.py` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/invariants/zero_residue_check.py` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/kiss_enforcer.py` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/observability-baseline.yaml` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/risk_ssot.py` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/secrets_guard.py` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/sys_master_compliance.py` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/sys-master-compliance.yaml` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/task/g0-entry.yaml` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/task/g0-orc-gate_engine.yaml` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/task/g7-orc-gate_engine.yaml` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/task_completion_gate.py` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/task_types.py` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/triple_alignment.py` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/truth_source_validator.py` | ✅ 已实现 | |
| `src/zephyr/gov_enforcement/rule_enforcement/zero-residue.yaml` | ✅ 已实现 | |

### 1.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/test_gate_engine.py` | ✅ 已实现 | |
| `tests/test_task_completion_gate.py` | ✅ 已实现 | |
| `tests/test_circuit_breaker.py` | ✅ 已实现 | |
| `tests/test_contract_template_manager.py` | ✅ 已实现 | |
| `tests/integration/test_gate_e2e.py` | ✅ 已实现 | |

### 1.3 治理脚本

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `scripts/governance/d6_security/validate_gate_discipline.py` | ✅ 已实现 | |

### 1.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §1（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下

---

## 治理信息
<!-- temporal_type: permanent -->

### SSoT声明

本蓝图是以下领域的唯一真源（Single Source of Truth）：

| 领域 | SSoT范围 |
|------|---------|
| G0-G7任务门禁规则 | 门禁YAML配置 + 判定逻辑 |
| G1-G5 KMS决策门规则 | 门禁YAML配置 + 判定逻辑 |
| 门禁域熔断器参数(threshold/cooldown/状态机) |
| 门禁评估管线 | 排序/组合/上下文传播 |
| 容量架构 | 六大支柱 + 12缺口 + SLO |
| 法证审计协议 | 哈希链 + 决策快照 + 验证工具 |
| 自指硬化协议 | 完整性守卫 + 信任根 + GATE-18联动 |

### 消费者注册表

| 消费者 | 消费内容 | 修改影响 |
|--------|---------|---------|
| MOD-TASK_SYSTEM (Task System) | GateResult→TaskCard.status迁移 | 门禁判定结果格式变更→Task System需适配 |
| MOD-INF-005 (Script System) | CT-SCRIPT-GATE-001 exit code映射 | exit code语义变更→映射表需更新 |
| MOD-KB-001 (Knowledge Base) | G1-G5 KMS门禁管道 | 门禁条件变更→知识入库流程受影响 |
| MOD-INF-015 (Telemetry) | GATE-16 SLI指标 | 指标定义变更→监控告警需更新 |
| MOD-MASTER_BLUEPRINT (总蓝图) | §2.8 CT-SCRIPT-GATE-001 | 集成契约变更→总蓝图需同步 |
| `.pre-commit-config.yaml` | GATE-18 pre-commit钩子 | 钩子配置变更→pre-commit需更新 |
| `src/zephyr/integration/mcp/gate_engine_server.py` | MCP工具描述 | 蓝图描述变更→MCP工具需更新 |

### 变更同步规则

| 修改此文件 | 必须同步更新 |
|-----------|-------------|
| 门禁YAML配置 | `_registry.yaml` + `validate_gate_discipline.py` |
| GateResult schema | `gate_engine.py` + `MOD-TASK_SYSTEM` |
| 容量SLO | `MOD-INF-001 §13` |
| 集成契约 | `MOD-MASTER_BLUEPRINT §2.8` |
| 门禁文件哈希 | `config/known_good_hashes.yaml` |

### 修改条件

| 条件 | 允许修改 | 需Owner审批 |
|------|---------|------------|
| 新增门禁YAML | AI可执行(scaffold流程) | — |
| 修改门禁entry_conditions | — | ✅ 需审批 |
| 修改熔断器参数 | — | ✅ 需审批 |
| 修改容量SLO目标值 | — | ✅ 需审批 |
| 修改gate_engine.py | — | ✅ 需审批+GATE-18自检 |
| 修改known_good_hashes.yaml | — | ✅ 需Owner PGP签名 |
| 新增Anti-Pattern | AI可执行 | — |
| 修改信任根层次 | — | ✅ 需审批 |

---

## 术语表
<!-- temporal_type: permanent -->

| 术语 | 精确定义 | 易混淆术语 | 区别 |
|------|---------|-----------|------|
| 门禁(Gate) | 合规判定检查点——判定PASS/FAIL | 门控(Pipeline Gate Control) | 门禁=合规判定；门控=执行流控制(MOD-INF-009) |
| G0-G7 | 任务生命周期8个门禁 | G1-G5 KMS | G0-G7=任务域；G1-G5=知识域 |
| G1-G5 KMS | 知识生命周期5个决策门 | G0-G7任务门禁 | KMS门禁判定KE入库/激活/提取 |
| 门禁域熔断器 | gates/circuit_breaker.py——SQLite持久化+门禁集成版 | shared熔断器 | 门禁域=SQLite持久化；shared=内存轻量版(MOD-INF-016) |
| GateResult | 门禁评估结果(PASS/FAIL/WARNING/CRITICAL_FAIL) | Finding | Finding=脚本输出；GateResult=门禁判定 |
| GateContext | 门禁评估上下文(task_id/session_id/blueprint_reads等) | TaskCard | GateContext=门禁评估时快照；TaskCard=任务完整数据 |
| Shadow Mode | 门禁评估→记录结果→不阻断任务 | Full Enforce | Shadow=只记录；Full=阻断 |
| CT-SCRIPT-GATE-001 | 脚本exit code→Gate判定映射契约 | CT-ORC-GATE-001 | SCRIPT=脚本→门禁；ORC=任务→门禁 |

## 已知问题与盲点登记
<!-- temporal_type: operational_temporary -->

| # | 问题 | 严重性 | 根因 | 解决方案 | 约束编号 | 状态 |
|---|------|:------:|------|---------|---------|:----:|
| 1 | gate_engine.py曾有BOM字符导致SyntaxError | 极高 | 编辑器保存UTF-8 BOM编码 | 已移除BOM；需添加CI门禁检测BOM | §5.1 #1 | 已解决 |
| 2 | CT-ORC-GATE-001未落地——门禁非自动触发 | 高 | 集成契约在Backlog | 步骤1施工 | §12 | 待解决 |
| 3 | CT-SCRIPT-GATE-001未落地——exit code未映射 | 高 | 集成契约在Backlog | 步骤2施工 | §12 | 待解决 |
| 4 | §0.1与底部索引曾矛盾(8个文件标记未实现但已存在) | 中 | 压缩时未同步§0.1 | 已在本次审查中修正 | §0.1 | 已解决 |
| 5 | 熔断器三重声明(MOD-GATE_ENGINE/016/022) | 中 | 历史演进未声明关系 | 已在§10.5登记+§0.4声明委托 | §0.4 | 已处置 |

## 自检与闭合清单
<!-- temporal_type: permanent -->

| # | 阶段 | 检查项 | 确认方式 | 状态 |
|---|:----:|--------|---------|:----:|
| 1 | 设计 | §3每个组件在§4有对应接口 | 逐组件核对 | ✅ |
| 2 | 设计 | §4每个接口在§16有对应施工步骤 | 逐接口核对 | ✅ |
| 3 | 设计 | §5每个约束在§9有对应测试 | 逐约束核对 | ☐ |
| 4 | 设计 | §0.1每个代码文件在§11有对应产出物路径 | 逐文件核对 | ✅ |
| 5 | 设计 | §10每个依赖在cross-module-dependency-registry.yaml有对应条目 | 逐依赖核对 | ☐ |
| 6 | 前 | 已读取蓝图全文 | 逐节确认 | ✅ |
| 7 | 前 | 术语表中每个术语含义已理解 | 能回答区别 | ✅ |
| 8 | 前 | 成熟度声明中volatile/evolving的部分已标记 | 知道哪些可改 | ✅ |
| 9 | 前 | 已知问题中未解决的问题已知晓 | 知道哪些坑不能踩 | ✅ |
| 10 | 中 | 每步施工后执行验证命令 | exit 0才进下一步 | ☐ |
| 11 | 中 | 新代码文件头部十五字段完整 | 逐文件核对 | ☐ |
| 12 | 后 | §0代码对齐验证已更新 | construction_progress与实际一致 | ☐ |

## 成熟度声明
<!-- temporal_type: permanent -->

| 设计维度 | 成熟度 | 信心 | 升级标准 | 说明 |
|---------|:------:|:---:|---------|------|
| 核心架构(G0-G7+G1-G5双门禁) | stable | 高 | CT-ORC-GATE-001落地→frozen | 核心设计已验证 |
| 接口契约(§4) | evolving | 中 | CT-SCRIPT-GATE-001落地→stable | exit code映射待实现 |
| 数据模型(GateResult/GateContext) | stable | 高 | Pydantic V2迁移完成→frozen | 已实现 |
| 容量架构(§17) | volatile | 低 | Phase A完成→evolving | 12缺口待施工 |
| 法证审计(哈希链) | evolving | 中 | 端到端验证通过→stable | 代码存在未验证 |
| 自指硬化(完整性守卫) | evolving | 中 | GATE-18联动验证→stable | 代码存在未验证 |

---

## 版本演进路线图
<!-- temporal_type: permanent -->

| 版本 | 核心变更 | 前置版本 | 施工状态 |
|------|---------|---------|:-------:|
| v0.1.0 | 初始创建——双门禁体系+门禁域熔断器 | — | 已完成 |
| v0.5.0 | 两轮盲点审查——法证审计+自指硬化+威胁模型 | v0.1.0 | 已完成 |
| v0.7.0 | 容量架构升级——六大支柱+三级调度 | v0.5.0 | 已完成 |
| v0.8.0 | 模板合规+压缩 | v0.7.0 | 已完成 |
| v0.9.0 | CT-ORC-GATE-001+CT-SCRIPT-GATE-001落地 | v0.8.0 | 待施工 |
| v1.0.0 | 容量Phase A/B/C完成+全链路测试 | v0.9.0 | 待施工 |

---

---

## 蓝图特有章节
<!-- temporal_type: permanent -->

### §A 门禁规则 G0-G7 结构化YAML

> 已实现——YAML文件是SSoT。蓝图只保留路径+关键字段约束。

| 门禁 | 文件路径 | gate_id | 触发事件 | 关键check ID | severity |
|------|---------|---------|---------|-------------|----------|
| G0 任务准入 | `src/zephyr/gov_enforcement/rule_enforcement/task/g0-entry.yaml` | G0 | DRAFT→TODO | G0-C00 required_fields_present; G0-C01 task_type_valid | error |
| G1 蓝图合规 | `src/zephyr/gov_enforcement/rule_enforcement/g6-blueprint-compliance.yaml` | G1 | TODO→IN_PROGRESS | G1-C00 module_has_approved_blueprint | error |
| G2 依赖完整 | (同G1文件) | G2 | → | G2-C00 depends_on_modules_implemented | error |
| G3 容量检查 | (同G1文件) | G3 | → | G3-C00 within_global_token_budget | warning |
| G4 沙箱合规 | `src/zephyr/gov_enforcement/rule_enforcement/g6-ctr-compliance.yaml` | G4 | 执行中 | G4-C00 sandbox_profile_matches_task_type | error |
| G5 模型合规 | (同G4文件) | G5 | → | G5-C00 model_in_capability_matrix | error |
| G6 安全合规 | `src/zephyr/gov_enforcement/rule_enforcement/g6-ctr-compliance.yaml` | G6 | → | G6-C00 tool_call_whitelist | error |
| G7 交付前 | `src/zephyr/gov_enforcement/rule_enforcement/task/g7-orc-gate_engine.yaml` | G7 | REVIEW→COMPLETED | G7-C00 all_associated_scripts_audit_pass | error |

**YAML字段约束**：check必须是布尔表达式；每条reject必须配fix_hint；severity: error/warning；on_failure: reject/defer/warn

### §B Anti-Patterns

| # | Anti-Pattern | 违反后果 | 正确做法 |
|---|-------------|---------|---------|
| AP1 | 绕过门禁直接修改TaskCard.status | G0-G7全部门禁被跳过 | 状态变更必须通过task_repo.transition()→自动触发对应门禁 |
| AP2 | 跳过G1-G5 KMS门禁直接写入知识库 | 未审查的知识进入AI上下文 | KE入库必须经过G1→G2→G3→G4→G5完整管道 |
| AP3 | 门禁规则留问句 | AI无法直接执行 | check必须是布尔表达式 |
| AP4 | 熔断器触发后手动override | 连续故障被掩盖 | OPEN期间只能等待cooldown到期 |
| AP5 | 创建门禁但不注册 | 门禁成为孤儿 | 新建门禁=copy _template.yaml+写入_registry.yaml |
| AP6 | 废弃门禁直接删除 | 历史session回溯找不到 | 废弃=status:deprecated+移到_deprecated/ |
| AP7 | on_failure只有reject没有fix_hint | AI被拒绝后不知道怎么修复 | 每条reject必须配fix_hint |
| AP8 | 新增脚本不注册 | 增量扫描找不到→漏检 | 任何新治理脚本必须在script-manifest.yaml注册 |
| AP9 | 全量扫描作为默认模式 | 10,000脚本全量3.5h→系统瘫痪 | 增量扫描是默认 |
| AP10 | 绕过依赖图谱直接跑指定维度 | 可能漏维 | 依赖图谱自动推导 |
| AP11 | Worker数硬编码 | 换机器后worker数不匹配 | Worker数=min(cpu_count()*2, config.max_workers) |
| AP12 | 一个AI的故障阻塞全部AI | 99个AI等1个故障AI | Bulkhead隔离+超时+熔断 |
| AP13 | 启动即接受请求 | 前5s拿到空结果 | 启动后先完成phase_0_bootstrap再listen |
| AP14 | 忽略下游饱和度继续放行 | 队列无限堆积→OOM | 信用流控——L3→L2→L1反压传导 |
| AP15 | 每个Agent都重跑相同脚本 | 浪费99% CPU | 全局content-addressable脚本结果缓存 |
| AP16 | 每次manifest变更全量重建图谱 | 每次卡5s | 增量更新默认+每日全量重建自愈 |
| AP17 | Agent身份缺失 | 一个恶意Agent拖垮全部 | 每个Agent session_id绑定配额 |
| AP18 | FIFO队列不分优先级 | P0排在P2后面 | PriorityQueue+P0预留20% worker |
| AP19 | 长脚本短脚本同池 | S0 P99从3s飙到180s | 长尾专用池 |
| AP20 | 纸上设计不压测 | 上生产后崩溃 | 每个设计里程碑跑BM-01~05 |
| AP21 | hash chain跨分片无原子性 | hash chain断裂 | 两阶段写入 |
| AP22 | SLO定义了但没人看 | 容量退化不被发现 | Prometheus指标+告警规则+每周容量健康报告 |
| AP23 | 降级策略是"拒绝P2"一句话 | 不知道停什么保什么 | 四级降级树 |
| AP24 | 改个YAML就重启服务 | 所有AI中断+冷启动5s | YAML/数据层热更原子替换 |

### §C 门禁评估管线

| Stage | 模式 | 门禁 | 失败行为 |
|-------|------|------|---------|
| entry | single | G0 | 任务留在DRAFT |
| pre_exec | parallel_and | G1, G2, G3 | 任务→BLOCKED |
| during_exec | parallel_and | G4, G5, G6 | 中断执行 + status→FAILED |
| delivery | single | G7 | 任务→BLOCKED |

**门禁间依赖**：G6 must PASS before G7 evaluation；G1 rejected → skip G2

**组合表达式**：支持 AND / OR / NOT / 括号 / severity_weighted。示例：`(G0-C00 AND G0-C01) OR (admin_override == true)`

### §D Owner紧急旁路协议

| 约束 | 值 |
|------|-----|
| 最大时长 | 24h |
| 需要理由 | ✅ |
| 永久审计 | ✅ |
| 每月上限 | 10次 |
| 范围 | per_gate |
| 自动恢复 | ✅ |
| 禁止override | circuit_breaker OPEN(AP4) / GATE-18 pre-commit / 批量override |

### §E 可观测性与审计

> Per-Gate SLI指标见 §6.1 可观测性规格。本节补充审计扩展字段。

**审计扩展字段**：context_json TEXT | triggered_by TEXT | override_id TEXT | evaluation_duration_ms INTEGER | affected_artifacts TEXT | session_id TEXT

### §F 性能预算与幂等性

| 路径 | max_latency_ms | timeout行为 |
|------|:---:|---------|
| hot_path | 50 | PASS(fail-open) |
| warm_path | 200 | FAIL(fail-closed) |
| cold_path | 2000 | 标记+继续 |

**自保护约束**：总延迟>500ms持续10s→降级仅P0门禁评估；错误率>5%(3min窗口)→降级仅G0+G7评估；恢复正常(<200ms+错误率<1%)持续60s→自动恢复；per_gate_max_qps=20；global_max_concurrent=50

### §G 版本化与生命周期

> 门禁生命周期状态和转换规则见 §3.3。本节补充迁移策略和继承机制。

**版本迁移策略**：PATCH→in-flight任务用新规则重评(不阻塞)；MINOR→新任务用新规则，in-flight沿用旧规则；MAJOR→全部in-flight任务暂停+通知Owner

**门禁继承**：extends只追加，不删除/修改基类。示例：G1-MOD-TRADE-001 extends G1，追加G1-TRADE-C00 trade_data_format_valid

### §H 人机协同审批

| 约束 | 值 |
|------|-----|
| check_id | G4-C01 |
| type | manual_approval |
| severity | error |
| approval_timeout_h | 72 |
| required_review_dimensions | 准确性, 时效性, 冲突裁决, 可信度 |

### §I 自适应与状态记忆

> 已实现——代码文件是SSoT。蓝图只保留接口签名+约束。

```python
class AdaptiveThreshold:
    def learn_threshold(self, gate_id: str, check_id: str, lookback_days=30) -> ThresholdRecommendation: ...
    def apply_recommendation(self, gate_id, check_id, require_owner_approval=True) -> bool: ...
```

**反馈回路约束**：连续override≥5/30d→建议downgrade P0→P1；retry failure>50%→fix_hint需重写

**时态阈值**：G3容量检查——weekday 09-17 threshold=0.8(Owner在岗)；其余时段 threshold=0.5

### §J 健康仪表板

> 已实现——代码文件是SSoT。蓝图只保留接口签名。

```python
class GateHealthDashboard:
    def generate_report(self) -> HealthReport: ...
```

**HealthReport字段**：generated_at | summary: HealthSummary | per_gate: dict[str, GateHealthEntry] | alerts: list[HealthAlert] | owner_todos: list[OwnerTodo]

**CLI**：`python -m zephyr.gates.gate_health` / `--alerts` / `--export-json`

### §K 法证审计完整性

> 数据模型定义见 §4.2（HashedGateDecision / DecisionSnapshot）和 §4.1（AuditChainVerifier）。本节补充实现约束。

**哈希链约束**：current_hash = SHA-256(self.to_canonical_bytes())；verify_chain: previous_hash == previous.current_hash

**决策快照约束**：to_canonical_json() + replay()→GateResult

**ChainVerificationReport字段**：total_decisions | verified | tampered | skipped | inconsistent | first_violation_at | is_intact | attestation

**备份策略**：3-2-1(3份副本/2种介质/1份异地)；primary=gate_chain.db / replica=gate_chain.jsonl / daily_export=gate_chain_YYYY-MM-DD.tar.gz；integrity_check=SHA-256每周自动+每次导出前；corruption_recovery=从JSONL副本重建SQLite+重建hash链

**快照生命周期**：hot(7d, snapshots_hot/, ~10MB/d) → warm(30d, snapshots_warm/, gzip, ~3MB/d) → cold(permanent, snapshots_archive/, xz, ~1MB/d)；验证基准：1K<100ms / 10K<1s / 100K<10s / 1M<2min

### §L 自我指涉硬化

> 已实现——代码文件是SSoT。蓝图只保留接口签名+信任根层次+GATE-18约束。

```python
class GateEngineIntegrityGuard:
    def verify_before_load(self) -> IntegrityCheckResult: ...
    def bootstrap_known_good_state(self, git_commit_hash: str) -> bool: ...
    def seal_current_state(self, owner_pgp_signature: bytes) -> bool: ...
```

**verify_before_load约束**：SHA-256(gate_engine.py/circuit_breaker.py/每个门禁YAML) == known_good_hash → ANY FAIL → fail-closed: 禁止所有AI操作

**信任根层次**：

| 层级 | 校验对象 | 校验基准 |
|------|---------|---------|
| L0 可信计算基 | OS内核 + git commit历史 + Owner PGP密钥 | 假设未遭rootkit级攻破 |
| L1 启动验证 | gate_engine.py / circuit_breaker.py 哈希 | config/known_good_hashes.yaml (Owner PGP签名) |
| L2 评估验证 | 门禁YAML配置哈希 | L1中加载的known_good_hashes |
| L3 运行时 | Gate Engine正常执行 | — |

**L1验证失败→禁止一切AI操作；L2验证失败→该门禁自动降级到FAIL**

**GATE-18自指防护**：AI提交对gate_engine.py或circuit_breaker.py的修改时→检查①修改者引用了本蓝图(MOD-GATE_ENGINE) ②附带Owner审批签名 ③同时更新known_good_hashes.yaml → ANY FAIL → 拒绝提交

**自升级协议**：step_1 deploy shadow(新旧双版本同时评估100次) → step_2 divergence check(不一致>1%→暂停+Owner审查) → step_3 cutover(IntegrityGuard验证新版本哈希+更新known_good_hashes+Owner PGP签名) → step_4 rollback(新版本错误率>旧版本×2→自动回退)

### §M 深度合规——形式vs实质

> G7D YAML已实现于 `src/zephyr/gov_enforcement/rule_enforcement/g7d_depth_compliance.yaml`。蓝图只保留关键字段约束。

| check ID | 名称 | 类型 | severity | 核心check |
|----------|------|------|----------|----------|
| G7D-C00 | unit_test_coverage | coverage | warning | pytest --cov → coverage >= 80% |
| G7D-C01 | dependency_cve_check | security-scan | error | pip-audit → 零 CRITICAL CVE |
| G7D-C02 | regression_test_pass | script_execution | error | run_all_regression.py exit_code == 0 |
| G7D-C03 | lint_pass | script_execution | warning | ruff check → zero errors |

**质量反馈回路**：7d post-deploy bug count(阈值=平均值±2σ) + revert rate(<5%) → 门禁长期PASS但post-deploy质量下降→建议增强

### §N 跨门禁时序一致性

**G7C检测**：FOR EACH module_id IN task.affected_modules: G1_snapshot.blueprint_version == current_module_blueprint_version → WARNING: "blueprint X was v1.2.0 at G1 but is now v1.3.0 at G7"。severity: warning(不阻断——只告知)

### §O 密钥管理与灾难恢复

**PGP主密钥**：存储=硬件安全密钥(YubiKey)；备份=纸质恢复码→银行保险箱；轮换=每年1次；泄露响应=git commit hash回滚+重新签名known_good_hashes.yaml

**Git仓库**：primary=本地磁盘 / mirror_1=GitHub/GitLab private / mirror_2=加密外置硬盘(每月同步)；integrity_check=git fsck(每次备份前)；disaster_recovery_drill=每季度一次

---

## 施工落盘确认
<!-- temporal_type: permanent -->

| 维度 | 状态 |
|------|------|
| construction_progress | phase_1_partial（核心门禁8/16文件已实现，Phase 2 Beta/Experimental 8个文件规划中） |
| 源码路径 | `src/zephyr/gov_enforcement/rule_enforcement/` |
| 源码文件数 | 55个 .py/.yaml |
| 测试路径 | `tests/integration/ + tests/architecture/` |
| 配置文件 | `architecture_model/layers/b_gates.yaml` |
| 关键入口 | `gates.registry.GateRegistry + gates.evaluator.GateEvaluator` |
