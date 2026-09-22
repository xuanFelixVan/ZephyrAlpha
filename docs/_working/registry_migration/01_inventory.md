---
ttl: task_bound
title: "W-M1 注册表迁PG前盘点 — 车道甲 (st-wm1-mineA-20260923)"
date: 2026-09-23
session: st-wm1-mineA-20260923
status: final
owner: ZephyrAlpha-Owner
---

# W-M1 车道甲：注册表迁 PG 前盘点（只读矿）

> 派单=W-M1 挖矿·车道甲。纪律=只读零改（本册为唯一新文件，creation_token 随批登记）；一切提交走队列。
> 方法=ROOR 驱动全量拉单（数量以文件实测为准勿背数）→ 74 张文件表机械扫描（YAML 解析取主容器/条目数/身份键）→ git grep -F 消费方分桶（src/gate/scripts/docs/tests 五面）→ 211 个 gate/执法 .py 逐表定位门禁加载者 → 近 30 天 git log churn 判多写者 → 生成器映射判单写者。
> 证据落盘=.runtime/tmp/wm1a_{roor_rows,scan_out,orphans_gates,churn,orphan_facts}.json + 三脚本 wm1a_{scan,orphans,churn}.py（可重跑复现）。

## §1 总量口径与双向核对

- ROOR（docs/registry_of_registries.yaml v1.1.0）在册 **77 个 registry_id**：tier0=12 / tier1=30 / tier2=35。ROOR 自带 summary 字段写 total_registries=76（tier2=34）——**与实体差 1，summary 陈旧**（check_registry_consistency.py --refresh-summary 未随最近一次登记刷新，见发现 F1）。
- 77 ID 按介质分：**74 个文件实体指针 + 2 个已在 PG（REG-ARCH-PANORAMA-001 / REG-DEPGRAPH-001，postgresql://localhost:5432/depgraph）+ 1 个 PG 真源机生快照（REG-METAQ-001，schema meta_question 三表；ROOR 所指 YAML 快照路径只存在于未合并的 .worktrees/st-chainpile-20260922，主区无此文件）**。
- 同文件多 ID 重复登记 2 簇（内收候选）：①REG-CAPCAN-001 ≡ REG-GEN-001（同一 capability_canonical_file_registry.yaml）；②REG-STD-005/006/007/008 → 同一 trae_048_ops_vibe_coding_session.yaml（4 ID 一文件）。故 74 个文件指针实际对应 **70 个实体文件**。
- 磁盘孤儿（在盘未册，ROOR RULE-FOUR 违规面）：`docs/01_policies_and_standards/_registry/catalogs/` 目录 75 个 YAML 中 **35 个不在 ROOR**（B 表全录，含全仓最大条目表 module_translation_registry 7194 条）；其他目录 registry/manifest/glossary/ledger 命名孤儿 10 个。
- 完成判据自检：A 表 77 行 = ROOR 77 ID 一一对应；B 表 45 行 = 磁盘实测孤儿一一对应；每文件行均附 git grep 证据（分桶计数+门禁加载者路径）。

## §2 判级规则（PG 迁移适配，机械可判）

| 级 | 判据 | 处置 |
|---|---|---|
| R0 | 介质已是 PG（ROOR physical_path=postgresql://） | 无动作（先例：depgraph 双表） |
| R2 | 多写者实证：DEFAULT_HOT_FILES 词表成员（file_utils.py:410）∨ churn30d≥40 | **迁 PG 第一波**——整文件覆盖/CAS 拉锯/死信事故全部集中于此 |
| R3 | manual ∧ churn30d 5..39 ∧ 有机器读者（gate/runtime） | 迁 PG 第二波（行级原子写收益） |
| R4 | manual ∧ churn30d<5 | 留 git（低频人工表，diff 可读性>并发收益，观察） |
| R5 | 单写者=生成器（auto/script_generated） | 留 git（可再生工件，git diff 即审计） |
| R6b | 文档型注册表（注册表内容嵌于 .md） | 留 git；迁 PG 须先结构化改造（超出本战役） |
| R7 | 密钥册 | 留 git（RULE-SECRETS；迁 PG=风险集中，明令不迁） |

## §3 A 表：ROOR 在册 77 ID 逐表盘点

列说明：实测条目=YAML 主容器(键:条数)；身份键=条目身份字段（机械猜测+dict键名）；churn=近30天提交数；gate加载者=commit_gates/gov_enforcement 内 grep 命中文件（全表机器读者证据=分桶列）；判级按§2。

| tier | registry_id | 路径 | 实测主容器 | 身份键 | ROOR计数→实测 | 写者 | 门禁加载者 | 机器读者分桶 | churn | 判级 |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | REG-GATE-001 | `src/zephyr/gov_enforcement/rule_enforcement/_registry.yaml` | gates:91(list) | gate_id,file | 91→91 | manual(ROOR)：GateEngine 91 gate canonical，会话直改+三向校验 | triple_alignment.py | src_runtime:504 gate_enforcement:273 scripts:333 docs:1217 tests:401 generator:42 config:24 data:12 architecture_model:14 | 1 | R4留git(低频人工表,观察) |
| 0 | REG-SCRIPT-001 | `scripts/script-manifest.yaml` | scripts:1037(list) | path,name | 991⚠→1037 | auto：generate_manifest.py | protection_index.py | src_runtime:11 gate_enforcement:1 scripts:6 docs:58 tests:6 generator:1 config:1 data:2 | 53 | R5留git(生成器工件) |
| 0 | REG-SCRIPT-002 | `scripts/governance/script_manifest.yaml` | scripts:445(list) | name | 434⚠→445 | auto：generators/generate_script_manifest.py | registry_mass_deletion_gate.py；git_commit_gateway.py | src_runtime:6 gate_enforcement:3 scripts:48 docs:36 tests:10 generator:6 data:1 | 52 | R5留git(生成器工件) |
| 0 | REG-PIPE-001 | `config/blueprint_routing.yaml` | routes:30(list) | - | 30→30 | manual | - | src_runtime:7 docs:16 tests:1 config:2 data:1 architecture_model:1 | 1 | R4留git(低频人工表,观察) |
| 0 | REG-CAP-001 | `config/tech_stack_manifest.yaml` | decisions:16(list) | - | 16→16 | manual | - | src_runtime:1 docs:2 data:1 architecture_model:1 | 0 | R4留git(低频人工表,观察) |
| 0 | REG-EMBED-001 | `config/embedding_model_registry.yaml` | models:5(list) | name | 5→5 | manual | - | src_runtime:1 scripts:4 docs:16 config:1 | 0 | R4留git(低频人工表,观察) |
| 0 | REG-DRIFT-001 | `src/zephyr/gov_drift/_detector_registry.yaml` | detectors:2(dict) | <dict-key:existing> | 30⚠→2 | manual | - | src_runtime:12 docs:3 tests:7 data:1 | 0 | R4留git(低频人工表,观察) |
| 0 | REG-SKILL-001 | `data/capability_cards/` | 目录型:34yaml | - | 22→ | manual | - | src_runtime:4 scripts:3 docs:32 tests:1 data:1 | 2 | R4留git(低频人工表,观察) |
| 0 | REG-DOMAIN-GOV-001 | `docs/03_modules/_domain_governance/blueprint.md` | 文档内嵌 | - | 8→ | manual+生成器混合(align_all/align_panoramas回写节) | __init__.py；admission_response.py；ai_code_standards.py；code_review_ai.py…+8 | src_runtime:505 gate_enforcement:14 scripts:50 docs:410 tests:545 generator:12 config:18 data:1 architecture_model:14 | 61 | R6b文档型(迁PG需先结构化) |
| 0 | REG-AFX-FIXER-001 | `src/zephyr/infrastructure/auto_fix_engine/engine.py` | code_inline | - | 11→ | code_inline (AutoFixEngine 启动时从 fixer_map 字典加载) | - | scripts:1 docs:2 tests:1 data:1 | 3 | R4留git(低频人工表,观察) |
| 0 | REG-AFX-PATTERN-001 | `data/fix_patterns/pattern_index.yaml` | patterns:15(list) | - | 15→15 | auto (FixPatternLearner → PatternLibraryUpdater) | - | src_runtime:2 scripts:1 docs:12 tests:2 | 2 | R4留git(低频人工表,观察) |
| 0 | REG-RESCHED-001 | `config/resource_profile_registry.yaml` | entities:89(list) | module_id | 74⚠→89 | auto：generators/generate_resource_profile_registry.py | resource_schedule_gate.py | src_runtime:11 gate_enforcement:4 scripts:9 docs:52 tests:10 generator:4 | 11 | R5留git(生成器工件) |
| 1 | REG-CATALOG-001 | `…_policies_and_standards/_registry/catalogs/registry_master_index.yaml` | registries:58(list) | registry_id,name | 55⚠→58 | auto：generators/generate_registry_master_index.py | - | src_runtime:3 scripts:9 docs:41 tests:4 generator:4 architecture_model:1 | 71 | R5留git(生成器工件) |
| 1 | REG-STD-001 | `…s/01_policies_and_standards/rules/trae_024_methodology_diagnosis.yaml` | sections:19(dict) | <dict-key:professional_framework_mapping> | 14⚠→19 | manual | - | docs:57 tests:1 config:1 data:3 | 1 | R4留git(低频人工表,观察) |
| 1 | REG-STD-002 | `…1_policies_and_standards/rules/trae_010_code_naming_organization.yaml` | sections:11(dict) | <dict-key:code_001> | 4⚠→11 | manual | - | docs:15 tests:1 generator:1 data:3 | 0 | R4留git(低频人工表,观察) |
| 1 | REG-STD-003 | `scripts/governance/quality_standard.md` | 文档内嵌 | - | 41→ | manual | - | src_runtime:1 scripts:22 docs:15 config:1 data:1 | 1 | R6b文档型(迁PG需先结构化) |
| 1 | REG-STD-004 | `…/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml` | sections:20(dict) | <dict-key:doc_011> | 7⚠→20 | manual | post_doc_review_check.py | gate_enforcement:2 scripts:3 docs:71 tests:1 data:5 | 1 | R4留git(低频人工表,观察) |
| 1 | REG-STD-005 | `…01_policies_and_standards/rules/trae_048_ops_vibe_coding_session.yaml` | sections:22(dict) | <dict-key:vc_scope> | 3⚠→22 | manual | - | docs:15 tests:1 data:5 | 0 | R4留git(低频人工表,观察) |
| 1 | REG-STD-006 | `…01_policies_and_standards/rules/trae_048_ops_vibe_coding_session.yaml` | sections:22(dict) | <dict-key:vc_scope> | 12⚠→22 | manual | - | docs:15 tests:1 data:5 | 0 | R4留git(低频人工表,观察) |
| 1 | REG-STD-007 | `…01_policies_and_standards/rules/trae_048_ops_vibe_coding_session.yaml` | sections:22(dict) | <dict-key:vc_scope> | 3⚠→22 | manual | - | docs:15 tests:1 data:5 | 0 | R4留git(低频人工表,观察) |
| 1 | REG-STD-008 | `…01_policies_and_standards/rules/trae_048_ops_vibe_coding_session.yaml` | sections:22(dict) | <dict-key:vc_scope> | 4⚠→22 | manual | - | docs:15 tests:1 data:5 | 0 | R4留git(低频人工表,观察) |
| 1 | REG-CROSS-001 | `…s_and_standards/_registry/catalogs/registry_consistency_contract.yaml` | registries:15(list) | id,path,name | 15→15 | manual | - | src_runtime:1 scripts:5 docs:12 tests:1 architecture_model:1 | 2 | R4留git(低频人工表,观察) |
| 1 | REG-CROSS-002 | `…nd_standards/_registry/catalogs/cross_module_dependency_registry.yaml` | dependencies:132(list) | - | 132→132 | manual | module_id_consistency_gate.py | src_runtime:2 gate_enforcement:2 scripts:3 docs:24 tests:1 generator:1 architecture_model:1 | 0 | R4留git(低频人工表,观察) |
| 1 | REG-STATE-VOCAB-001 | `…icies_and_standards/_registry/catalogs/state_vocabulary_registry.yaml` | vocabularies:29(list) | - | 29→29 | manual | state_vocab_registry_gate.py | src_runtime:1 gate_enforcement:4 docs:11 tests:1 | 0 | R4留git(低频人工表,观察) |
| 1 | REG-DIR-001 | `…/01_policies_and_standards/_registry/catalogs/directory_registry.yaml` | directories:87(list) | path,module_id | 87→87 | manual | - | src_runtime:2 scripts:1 docs:15 tests:1 data:1 architecture_model:1 | 3 | R4留git(低频人工表,观察) |
| 1 | REG-DOC-001 | `…_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml` | files:282(list) | path,module_id | 256⚠→282 | manual+生成器混合：d3_metadata/generate_rule_catalog.py | rule_four_way_alignment_gate.py | src_runtime:3 gate_enforcement:2 scripts:10 docs:49 tests:7 generator:1 config:1 architecture_model:1 | 166 | R2迁PG-P0(多写者热表) |
| 1 | REG-GATE-CAT-001 | `docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml` | gates:171(list) | gate_id,name | 169⚠→171 | auto：generators/generate_gate_registry.py(own_scope机生勿手改) | algo_flow_link_gate.py；algo_note_sync_gate.py；arch_reference_gate.py；asyncio_run_in_context_gate.py…+124 | src_runtime:13 gate_enforcement:213 scripts:24 docs:150 tests:12 generator:7 config:2 architecture_model:2 | 20 | R5留git(生成器工件) |
| 1 | REG-INFRA-001 | `…olicies_and_standards/_registry/catalogs/infrastructure_registry.yaml` | infrastructure:17(list) | name | 16⚠→17 | manual | git_commit_gateway.py | src_runtime:2 gate_enforcement:1 scripts:4 docs:41 tests:2 generator:2 architecture_model:2 | 2 | R4留git(低频人工表,观察) |
| 1 | REG-INTF-001 | `…tandards/_registry/catalogs/_archive/interface_contract_registry.yaml` | interfaces:5(list) | module_id | 5→5 | frozen | - | scripts:2 docs:7 tests:1 | 1 | R4留git(低频人工表,观察) |
| 1 | REG-KB-001 | `…standards/_registry/catalogs/_archive/knowledge_article_registry.yaml` | reserved_ranges:4(list) +_schema:3 | - | 0⚠→4 | frozen | - | src_runtime:2 docs:9 tests:1 architecture_model:1 | 1 | R4留git(低频人工表,观察) |
| 1 | REG-TASK-META-001 | `…olicies_and_standards/_registry/catalogs/task_card_meta_registry.yaml` | migration_rules:5(list) +systems:4 | rule_id | 4⚠→5 | manual | - | src_runtime:1 docs:7 tests:1 architecture_model:1 | 0 | R4留git(低频人工表,观察) |
| 1 | REG-FRONTMATTER-001 | `…cies_and_standards/_registry/catalogs/frontmatter_field_registry.yaml` | fields:58(list) | - | 58→58 | manual | - | src_runtime:1 scripts:5 docs:17 tests:2 generator:1 config:1 architecture_model:1 | 0 | R4留git(低频人工表,观察) |
| 1 | REG-INV-001 | `data/asset_index/unified-asset-index.yaml` | by_category:8(dict) | <dict-key:python_source> | 33249注:ROOR数=资产总行数,实测=类目数→8 | auto：generate_asset_index.py | - | src_runtime:12 gate_enforcement:2 scripts:1 docs:27 tests:4 generator:2 data:1 | 27 | R5留git(生成器工件) |
| 1 | REG-STD-FAMILY-001 | `…licies_and_standards/_registry/catalogs/standard_family_registry.yaml` | family_unassigned_std_ids:4(list) | - | →4 | auto：standards_governance/generate_standard_family_registry. | - | scripts:2 docs:18 tests:1 generator:1 | 1 | R5留git(生成器工件) |
| 1 | REG-FUNC-DOMAIN-001 | `…cies_and_standards/_registry/catalogs/functional_domain_registry.yaml` | entries:94(list) | - | 83⚠→94 | manual(ROOR) | commit_scope_gate.py；domain_fk_gate.py | src_runtime:2 gate_enforcement:3 scripts:8 docs:70 tests:6 generator:4 config:1 data:2 | 3 | R4留git(低频人工表,观察) |
| 1 | REG-ARCH-PANORAMA-001 | postgresql://localhost:5432/depgraph | （PG） | - | - | postgresql://localhost:5432/depgraph | depgraph 全链 | - | - | R0已在PG |
| 1 | REG-DEPGRAPH-001 | postgresql://localhost:5432/depgraph | （PG） | - | - | postgresql://localhost:5432/depgraph | depgraph 全链 | - | - | R0已在PG |
| 1 | REG-MIGRATION-001 | `…/01_policies_and_standards/_registry/catalogs/migration_registry.yaml` | entries:37(list) | - | 37→37 | frozen | - | scripts:8 docs:9 tests:1 generator:2 data:2 | 0 | R4留git(低频人工表,观察) |
| 1 | REG-ARCH-ISSUE-001 | `…ies_and_standards/_registry/catalogs/architecture_issue_registry.yaml` | entries:802(list) | - | 761⚠→802 | manual | registry_alignment.py；arch_reference_gate.py；depgraph_write_path_gate.py；derived_file_deletion_gate.py…+7 | src_runtime:10 gate_enforcement:15 scripts:4 docs:119 tests:9 generator:2 | 114 | R2迁PG-P0(多写者热表) |
| 1 | REG-CAPCAN-001 | `…_standards/_registry/catalogs/capability_canonical_file_registry.yaml` | creation_tokens:9841(list) | token,file | 378⚠→9841 | manual+扫描(semi)：写=batch_creation_tokens.py(CREATE-GUARD通道)；扫 | create_guard.py；derivation_annotation_gate.py；derived_file_deletion_gate.py；registry_yaml_parse_gate.py…+5 | src_runtime:6 gate_enforcement:11 scripts:14 docs:184 tests:10 generator:1 config:1 data:1 architecture_model:1 | 512 | R2迁PG-P0(多写者热表) |
| 1 | REG-GEN-001 | `…_standards/_registry/catalogs/capability_canonical_file_registry.yaml` | creation_tokens:9841(list) | token,file | 5520⚠→9841 | manual+扫描(semi)：写=batch_creation_tokens.py(CREATE-GUARD通道)；扫 | create_guard.py；derivation_annotation_gate.py；derived_file_deletion_gate.py；registry_yaml_parse_gate.py…+5 | src_runtime:6 gate_enforcement:11 scripts:14 docs:184 tests:10 generator:1 config:1 data:1 architecture_model:1 | 512 | R2迁PG-P0(多写者热表) |
| 1 | REG-ERRCODE-001 | `architecture_model/contracts/error_code_registry.yaml` | error_codes:789(list) | file | 788⚠→789 | manual | errcode_consistency_gate.py | src_runtime:8 gate_enforcement:2 docs:32 tests:1 | 78 | R2迁PG-P0(多写者热表) |
| 2 | REG-SYS-MASTER-001 | `docs/03_modules/_system_master/blueprint.md` | 文档内嵌 | - | 1→ | manual+生成器混合(align_all/align_panoramas回写节) | sys_master_compliance.py | src_runtime:4 gate_enforcement:2 scripts:3 docs:43 tests:5 generator:1 data:1 | 2 | R6b文档型(迁PG需先结构化) |
| 2 | REG-MOD-MASTER_BLUEPRINT | `docs/03_modules/_master_blueprint/blueprint.md` | 文档内嵌 | - | 1→ | manual+生成器混合(align_all/align_panoramas回写节) | - | docs:29 tests:2 data:1 | 2 | R6b文档型(迁PG需先结构化) |
| 2 | REG-TEMPLATE-001 | `docs/03_modules/template_registry.yaml` | templates:11(list) | path,name | 11→11 | manual | module_id_consistency_gate.py | src_runtime:3 gate_enforcement:2 docs:17 tests:1 config:1 data:1 architecture_model:1 | 0 | R4留git(低频人工表,观察) |
| 2 | REG-MOD-ID-001 | `architecture_model/module_id_registry.yaml` | registered_ids:74(list) | path,module_id | 74→74 | manual | module_id_consistency_gate.py | src_runtime:1 gate_enforcement:2 scripts:4 docs:68 tests:1 generator:3 config:1 data:2 architecture_model:1 | 0 | R4留git(低频人工表,观察) |
| 2 | REG-ARCH-001 | `architecture_model/index.yaml` | domains:74(list) | id,name | 75⚠→74 | manual(架构数据，apply_*.py 直写DB侧) | - | src_runtime:523 gate_enforcement:85 scripts:318 docs:2127 tests:407 generator:45 config:12 data:17 architecture_model:10 | 12 | R3迁PG-P1(次波) |
| 2 | REG-FREEZE-001 | `src/zephyr/shared/contracts/freeze_manifest.yaml` | p1_blueprint_contracts:15(list) | name | 38⚠→15 | manual | - | src_runtime:6 scripts:2 docs:11 tests:1 data:1 | 1 | R4留git(低频人工表,观察) |
| 2 | REG-RB-001 | `src/zephyr/security/adversarial_validation/_scenario_registry.yaml` | scenarios:53(list) | name | 53→53 | auto （red_blue_validator 场景加载器） | - | src_runtime:4 docs:2 tests:2 | 0 | R4留git(低频人工表,观察) |
| 2 | REG-RB-002 | `src/zephyr/security/adversarial_validation/_constitution_registry.yaml` | articles:44(list) | name | 44→44 | auto （ConstitutionEngine 绕过学习） | - | src_runtime:2 docs:3 tests:2 | 0 | R4留git(低频人工表,观察) |
| 2 | REG-SM-001 | `src/zephyr/shared/_state_machine_registry.yaml` | state_machines:2(list) | - | 2→2 | manual | - | src_runtime:3 docs:3 data:1 | 0 | R4留git(低频人工表,观察) |
| 2 | REG-UNI-001 | `…s/01_policies_and_standards/_registry/catalogs/universe_registry.yaml` | entry_schema:33(dict) +universes:7 | <dict-key:universe_id> | 7⚠→33 | manual | registry_alignment.py；registry_code_anchor_gate.py | src_runtime:4 gate_enforcement:3 scripts:3 docs:28 tests:3 | 2 | R4留git(低频人工表,观察) |
| 2 | REG-BMK-001 | `…/01_policies_and_standards/_registry/catalogs/benchmark_registry.yaml` | entry_schema:31(dict) +benchmarks:9 | <dict-key:benchmark_id> | 9⚠→31 | manual | registry_alignment.py；registry_code_anchor_gate.py | src_runtime:2 gate_enforcement:2 scripts:3 docs:18 tests:1 | 2 | R4留git(低频人工表,观察) |
| 2 | REG-CST-001 | `…01_policies_and_standards/_registry/catalogs/cost_model_registry.yaml` | entry_schema:25(dict) +cost_models:6 | <dict-key:cost_model_id> | 6⚠→25 | manual | registry_alignment.py；registry_code_anchor_gate.py | src_runtime:2 gate_enforcement:2 scripts:3 docs:26 tests:2 generator:1 | 4 | R4留git(低频人工表,观察) |
| 2 | REG-FCT-001 | `docs/01_policies_and_standards/_registry/catalogs/factor_registry.yaml` | factors:175(list) | name | 175→175 | manual | registry_alignment.py；decision_map_gate.py；registry_code_anchor_gate.py；git_commit_gateway.py…+1 | src_runtime:16 gate_enforcement:8 scripts:62 docs:140 tests:17 generator:1 config:3 | 19 | R3迁PG-P1(次波:manual+机器读者) |
| 2 | REG-STR-001 | `…s/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml` | strategies:161(list) | name | 161→161 | manual | registry_alignment.py；decision_map_gate.py；registry_code_anchor_gate.py | src_runtime:17 gate_enforcement:3 scripts:9 docs:99 tests:15 generator:1 config:1 architecture_model:1 | 15 | R3迁PG-P1(次波:manual+机器读者) |
| 2 | REG-RLM-001 | `…01_policies_and_standards/_registry/catalogs/risk_limit_registry.yaml` | risk_limits:117(list) | name | 117→117 | manual | registry_alignment.py；registry_code_anchor_gate.py | src_runtime:4 gate_enforcement:2 scripts:4 docs:30 tests:3 | 7 | R3迁PG-P1(次波:manual+机器读者) |
| 2 | REG-TECHNICAL-INDICATOR-001 | `…es_and_standards/_registry/catalogs/technical_indicator_registry.yaml` | indicators:143(list) | module_id,name | 102⚠→143 | auto（scripts/governance/_shared/algo_flow_translation_sync.p | registry_alignment.py；registry_code_anchor_gate.py | src_runtime:4 gate_enforcement:2 scripts:6 docs:50 tests:3 | 14 | R3迁PG-P1(次波:manual+机器读者) |
| 2 | REG-PAT-001 | `…policies_and_standards/_registry/catalogs/chart_pattern_registry.yaml` | chart_patterns:287(list) | name | 297⚠→287 | manual | registry_alignment.py；registry_code_anchor_gate.py | src_runtime:5 gate_enforcement:2 scripts:5 docs:33 tests:4 | 12 | R3迁PG-P1(次波:manual+机器读者) |
| 2 | REG-EXA-001 | `…olicies_and_standards/_registry/catalogs/execution_algo_registry.yaml` | entry_schema:46(dict) +execution_algos:7 | <dict-key:execution_algo_id> | 7⚠→46 | manual | registry_alignment.py；registry_code_anchor_gate.py | src_runtime:3 gate_enforcement:2 scripts:3 docs:13 tests:2 | 0 | R4留git(低频人工表,观察) |
| 2 | REG-DATAFLOW-001 | `…01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml` | datasets:293(list) | - | 342⚠→293 | manual | registry_alignment.py；decision_map_gate.py；registry_code_anchor_gate.py；registry_yaml_parse_gate.py | src_runtime:7 gate_enforcement:6 scripts:5 docs:101 tests:3 generator:2 config:1 | 32 | R3迁PG-P1(次波:manual+机器读者) |
| 2 | REG-FLD-001 | `…cs/01_policies_and_standards/_registry/catalogs/field_dictionary.yaml` | fields:262(list) | - | 262→262 | manual | registry_alignment.py；industry_chain_map_gate.py；registry_code_anchor_gate.py | src_runtime:3 gate_enforcement:4 scripts:6 docs:51 tests:4 generator:2 config:1 | 1 | R4留git(低频人工表,观察) |
| 2 | REG-EXP-001 | `…01_policies_and_standards/_registry/catalogs/experiment_registry.yaml` | entry_schema:68(dict) +experiments:11 | <dict-key:experiment_id> | 11⚠→68 | manual | registry_alignment.py；registry_code_anchor_gate.py | src_runtime:2 gate_enforcement:2 scripts:4 docs:37 tests:1 | 4 | R4留git(低频人工表,观察) |
| 2 | REG-VALM-001 | `…cies_and_standards/_registry/catalogs/validation_method_registry.yaml` | discipline:7(dict) +derivation_rules:6 | <dict-key:holdout_months> | 5⚠→7 | manual | - | src_runtime:1 scripts:3 docs:24 tests:1 generator:1 | 1 | R4留git(低频人工表,观察) |
| 2 | REG-DAL-001 | `…policies_and_standards/_registry/catalogs/decision_algo_registry.yaml` | algorithms:32(list) | - | 27⚠→32 | manual | panorama_alignment_gate.py | src_runtime:2 gate_enforcement:1 docs:11 tests:1 | 5 | R3迁PG-P1(次波:manual+机器读者) |
| 2 | REG-RISK-TIER-001 | `…/01_policies_and_standards/_registry/catalogs/risk_tier_registry.yaml` | domain_tiers:18(list) | - | 18→18 | manual | - | src_runtime:2 scripts:1 docs:46 tests:2 | 1 | R4留git(低频人工表,观察) |
| 2 | REG-BTB-001 | `…cs/01_policies_and_standards/_registry/catalogs/backtest_backlog.yaml` | objects:142(list) | - | 137⚠→142 | script_generated | - | src_runtime:3 scripts:5 docs:40 tests:1 generator:1 | 11 | R5留git(生成器工件) |
| 2 | REG-SEAT-001 | `docs/01_policies_and_standards/_registry/catalogs/seat_registry.yaml` | entry_schema:27(dict) +seats:16 | <dict-key:seat_id> | 16⚠→27 | manual | registry_alignment.py | src_runtime:4 gate_enforcement:1 scripts:1 docs:23 tests:2 | 1 | R4留git(低频人工表,观察) |
| 2 | REG-CYCLE-001 | `…_policies_and_standards/_registry/catalogs/regime_cycle_registry.yaml` | entry_schema:33(dict) +cycles:13 | <dict-key:cycle_id> | 13⚠→33 | manual | registry_alignment.py；registry_code_anchor_gate.py | src_runtime:2 gate_enforcement:2 scripts:3 docs:15 tests:1 | 0 | R4留git(低频人工表,观察) |
| 2 | REG-ML-001 | `docs/01_policies_and_standards/_registry/catalogs/model_registry.yaml` | entry_schema:36(dict) +models:8 | <dict-key:model_id> | 8⚠→36 | manual | registry_alignment.py；registry_code_anchor_gate.py | src_runtime:14 gate_enforcement:2 scripts:8 docs:63 tests:7 generator:1 config:2 architecture_model:1 | 1 | R4留git(低频人工表,观察) |
| 2 | REG-EVT-001 | `…olicies_and_standards/_registry/catalogs/event_calendar_registry.yaml` | entry_schema:27(dict) +event_types:14 | <dict-key:event_type_id> | 14⚠→27 | manual | registry_alignment.py | src_runtime:4 gate_enforcement:1 scripts:1 docs:10 tests:1 | 1 | R4留git(低频人工表,观察) |
| 2 | REG-MAC-001 | `…licies_and_standards/_registry/catalogs/macro_indicator_registry.yaml` | entry_schema:28(dict) +indicators:16 | <dict-key:indicator_id> | 16⚠→28 | manual | registry_alignment.py | src_runtime:2 gate_enforcement:1 scripts:1 docs:11 tests:1 | 1 | R4留git(低频人工表,观察) |
| 2 | REG-PFM-001 | `…licies_and_standards/_registry/catalogs/portfolio_model_registry.yaml` | entry_schema:34(dict) +portfolio_models:11 | <dict-key:model_id> | 11⚠→34 | manual | registry_alignment.py；registry_code_anchor_gate.py | src_runtime:1 gate_enforcement:2 scripts:3 docs:12 | 0 | R4留git(低频人工表,观察) |
| 2 | REG-FEATURE-ADJ-001 | `…s_and_standards/_registry/catalogs/feature_adjudication_registry.yaml` | features:19(list) | - | 19→19 | manual | - | src_runtime:1 scripts:1 docs:11 tests:1 | 0 | R4留git(低频人工表,观察) |
| 2 | REG-CMP-REPORT-001 | `…cies_and_standards/_registry/catalogs/compliance_report_registry.yaml` | report_item_schema:7(dict) +report_items:6 | <dict-key:item_id> | 6⚠→7 | manual | - | src_runtime:7 scripts:1 docs:27 tests:4 architecture_model:1 | 0 | R4留git(低频人工表,观察) |
| 2 | REG-ATH-001 | `…licies_and_standards/_registry/catalogs/alert_threshold_registry.yaml` | thresholds:45(list) | threshold_id,module_id,name | 38⚠→45 | manual | registry_alignment.py | src_runtime:17 gate_enforcement:1 scripts:4 docs:52 tests:10 | 7 | R3迁PG-P1(次波:manual+机器读者) |
| 2 | REG-METAQ-001 | docs/_working/chain_piling_campaign/snapshots/registry_latest.yaml | 主区缺文件（快照在 .worktrees/st-chainpile-20260922） | row_count | 0→PG真源 | auto(snapshot.py机生) | - | - | - | R0已在PG(真源=PG schema meta_question 三表) |

## §4 B 表：磁盘孤儿（在盘未册）

### B1 catalogs 目录 35 个（ROOR RULE-FOUR 违规面）

| 路径 | 实测主容器 | 条数 | 大小 | 门禁加载者 | 机器读者分桶 | churn | 判级 |
|---|---|---|---|---|---|---|---|
| `_index.yaml` | None | None | 1513 | - | scripts:2 docs:3 | 0 | R4留git(低频人工表,观察)(未册) |
| `ai_autonomy_authority_registry.yaml` | permission_table | 11 | 27982 | circuit_breaker.py | src_runtime:9 scripts:3 docs:57 tests:3 config:2 | 0 | R4留git(低频人工表,观察)(未册) |
| `ai_risk_register.yaml` | risks | 11 | 10275 | - | docs:7 tests:1 | 0 | R4留git(低频人工表,观察)(未册) |
| `battle_map_domain_policy.yaml` | flow_stage_allowed_domains | 11 | 34056 | battle_map_alignment_gate.py | src_runtime:1 scripts:4 docs:31 tests:3 | 3 | R4留git(低频人工表,观察)(未册) |
| `candidate_module_registry.yaml` | entries | 623 | 1055258 | registry_alignment.py | src_runtime:7 scripts:16 docs:74 tests:5 | 69 | R2迁PG-P0(多写者热表)(未册) |
| `dataflow_graph_registry.yaml` | datasets | 75 | 68096 | panorama_alignment_gate.py | src_runtime:2 scripts:5 docs:19 tests:2 | 2 | R4留git(低频人工表,观察)(未册) |
| `depgraph_scan_exclusions.yaml` | depgraph | 5 | 5091 | - | scripts:2 docs:14 tests:1 | 0 | R4留git(低频人工表,观察)(未册) |
| `derived_identifier_registry.yaml` | entry_schema | 9 | 4023 | - | scripts:6 docs:9 tests:1 | 0 | R4留git(低频人工表,观察)(未册) |
| `domain_naming_rules.yaml` | entry_schema | 8 | 4472 | - | scripts:10 docs:10 tests:1 | 0 | R4留git(低频人工表,观察)(未册) |
| `domain_responsibility_layer_mapping.yaml` | entries | 84 | 17949 | - | src_runtime:1 scripts:2 docs:22 tests:2 | 1 | R4留git(低频人工表,观察)(未册) |
| `external_contract_verification_registry.yaml` | entries | 2 | 4600 | - | docs:5 tests:1 | 0 | R4留git(低频人工表,观察)(未册) |
| `fail_open_register.yaml` | by_stage | 13 | 268180 | gate_auto_registrar.py | src_runtime:1 scripts:3 docs:32 tests:1 | 2 | R5留git(生成器工件)(未册) |
| `gate_tracked_write_allowlist.yaml` | entries | 12 | 5597 | git_commit_gateway.py；worktree_drift_watchdog.py | src_runtime:2 scripts:3 docs:12 tests:3 | 6 | R3迁PG-P1(次波:manual+机器读者)(未册) |
| `generator_registry.yaml` | generators | 28 | 21031 | - | scripts:5 docs:14 tests:2 | 2 | R4留git(低频人工表,观察)(未册) |
| `governance_convergence_map.yaml` | meta | 6 | 10278 | - | scripts:1 docs:7 tests:2 | 0 | R4留git(低频人工表,观察)(未册) |
| `hard_boundaries_registry.yaml` | boundaries | 8 | 3613 | - | scripts:2 docs:6 tests:1 | 1 | R4留git(低频人工表,观察)(未册) |
| `in_process_gate_registry.yaml` | gates | 117 | 41076 | algo_flow_link_gate.py；algo_note_sync_gate.py；battle_map_alignment_gate.py…+18 | src_runtime:19 scripts:1 docs:43 tests:2 | 16 | R3迁PG-P1(次波:manual+机器读者)(未册) |
| `industry_graph_field_dictionary.yaml` | vocab | 21 | 46485 | registry_alignment.py；industry_chain_map_gate.py | src_runtime:2 scripts:4 docs:10 tests:3 config:1 | 7 | R3迁PG-P1(次波:manual+机器读者)(未册) |
| `io_sector_sws_map.yaml` | mappings | 153 | 12668 | - | scripts:1 docs:6 tests:1 config:1 | 1 | R4留git(低频人工表,观察)(未册) |
| `library_tag_vocabulary.yaml` | values | 181 | 14159 | tag_vocab_gate.py | src_runtime:1 docs:3 | 0 | R4留git(低频人工表,观察)(未册) |
| `module_translation_registry.yaml` | entries | 7194 | 3346134 | battle_map_alignment_gate.py；translation_coverage_gate.py；library_blood_flesh_gate.py | src_runtime:7 scripts:18 docs:91 tests:9 | 200 | R2迁PG-P0(多写者热表)(未册) |
| `noqa_exempt_registry.yaml` | markers | 30 | 25778 | asyncio_run_in_context_gate.py；bare_sql_gate.py；datetime_now_forbidden_gate.py…+5 | src_runtime:8 scripts:5 docs:32 tests:3 config:1 | 2 | R4留git(低频人工表,观察)(未册) |
| `panorama_exempt_list.yaml` | exempt_module_ids | 175 | 6962 | - | scripts:1 docs:10 tests:2 | 1 | R4留git(低频人工表,观察)(未册) |
| `registry_master_index_exemptions.yaml` | exemptions | 14 | 3480 | - | docs:6 tests:1 | 1 | R4留git(低频人工表,观察)(未册) |
| `registry_of_logs.yaml` | logs | 98 | 44579 | vocab_chain_gate.py | src_runtime:2 scripts:6 docs:26 tests:1 | 4 | R4留git(低频人工表,观察)(未册) |
| `rule_ai_perception_index.yaml` | rules | 86 | 52087 | capability_lookup_required_gate.py | src_runtime:4 scripts:7 docs:32 tests:1 config:1 | 37 | R5留git(生成器工件)(未册) |
| `rule_enforcement_registry.yaml` | items | 82 | 34317 | sys_master_compliance.py | src_runtime:1 scripts:1 docs:9 tests:1 | 0 | R4留git(低频人工表,观察)(未册) |
| `rule_registry_collection.yaml` | items | 267 | 36742 | - | scripts:3 docs:13 tests:1 | 3 | R4留git(低频人工表,观察)(未册) |
| `ruling_registry.yaml` | entries | 220 | 376186 | registry_alignment.py；ruling_reference_gate.py；_reference_helpers.py…+1 | src_runtime:6 scripts:5 docs:188 tests:8 | 68 | R2迁PG-P0(多写者热表)(未册) |
| `scripts_registry.yaml` | items | 430 | 59143 | - | scripts:1 docs:11 tests:1 | 2 | R4留git(低频人工表,观察)(未册) |
| `terminology_glossary.yaml` | entries | 279 | 35695 | - | scripts:8 docs:25 tests:1 config:1 | 3 | R4留git(低频人工表,观察)(未册) |
| `test_suite_registry.yaml` | items | 1580 | 200092 | - | src_runtime:1 scripts:1 docs:10 tests:1 | 5 | R3迁PG-P1(次波)(未册) |
| `trial_ledger_registry.yaml` | batch_records | 8 | 2741 | - | src_runtime:1 docs:14 tests:2 | 4 | R4留git(低频人工表,观察)(未册) |
| `trust_boundary_surface_registry.yaml` | surfaces | 2 | 2388 | - | scripts:1 docs:7 tests:1 | 0 | R4留git(低频人工表,观察)(未册) |
| `wiring_registry.yaml` | modules | 313 | 70074 | - | scripts:2 docs:13 tests:2 | 4 | R4留git(低频人工表,观察)(未册) |

### B2 其他目录 registry/manifest/glossary/ledger 命名孤儿 10 个

| 路径 | 实测主容器 | 条数 | 机器读者分桶 | 判级 |
|---|---|---|---|---|
| `architecture_model/governance_systems_registry.yaml` | systems | 46 | scripts:1 docs:5 | R4留git(低频人工表,观察)(未册) |
| `config/league_registry.yaml` | review_policy | 6 | docs:7 | R4留git(低频人工表,观察)(未册) |
| `config/sli_registry.yaml` | slis | 6 | src_runtime:2 docs:4 | R4留git(低频人工表,观察)(未册) |
| `config/secret_registry.yaml` | secrets | 106 | src_runtime:10 docs:45 tests:3 config:1 | R7留git(密钥不迁)(未册) |
| `config/risk_register.yaml` | risks | 21 | src_runtime:1 scripts:1 docs:20 tests:1 config:1 | R4留git(低频人工表,观察)(未册) |
| `data/cache/grandfather-registry.yaml` | entries | 1 | src_runtime:2 | R4留git(低频人工表,观察)(未册) |
| `data/capability_cards/daemon_registry.yaml` | tags | 3 | src_runtime:5 scripts:1 docs:18 tests:2 config:1 | R4留git(低频人工表,观察)(未册) |
| `data/capability_cards/meta_question_registry.yaml` | tags | 5 | docs:13 | R4留git(低频人工表,观察)(未册) |
| `data/fix_patterns/_fixer-registry.yaml` | fixers | 3 | src_runtime:17 docs:9 tests:4 | R4留git(低频人工表,观察)(未册) |
| `config/asset_inventory.yaml` | offrepo_assets | 15 | src_runtime:33 scripts:10 docs:105 tests:40 config:3 | R4留git(低频人工表,观察)(未册) |

## §5 P0 迁移候选卡片（谁写谁读·grep 证据全路径）

### REG-DOC-001 — docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml

- 体量：112169 B；主容器 `files` 282 条；身份键 path,module_id
- churn30d=166；热文件词表成员=否
- 写者：manual+生成器混合：d3_metadata/generate_rule_catalog.py
- 门禁加载者（grep 实证 1 个文件）：src/zephyr/gov_enforcement/commit_gates/rule_four_way_alignment_gate.py
- src_runtime 读者（前3）：src/zephyr/governance/audit/reconciliation_registry.py；src/zephyr/governance/audit/workspace_hygiene_reconciler.py；src/zephyr/shared/security/ssot_guard.py
- scripts 读者（前4）：scripts/governance/commit_derived_sync.py；scripts/governance/d1_structure/batch_create_index_md.py；scripts/governance/d1_structure/sync_policies_index.py；scripts/governance/d5_architecture/checkers/check_rule_four_way_alignment.py
- generator 读者（前1）：scripts/governance/d3_metadata/generate_rule_catalog.py
- config 读者（前1）：config/nav_table_mapping.yaml

### REG-ARCH-ISSUE-001 — docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml

- 体量：1764428 B；主容器 `entries` 802 条；身份键 -
- churn30d=114；热文件词表成员=是
- 写者：manual
- 门禁加载者（grep 实证 11 个文件）：src/zephyr/gov_enforcement/registry_alignment.py；src/zephyr/gov_enforcement/commit_gates/arch_reference_gate.py；src/zephyr/gov_enforcement/commit_gates/depgraph_write_path_gate.py；src/zephyr/gov_enforcement/commit_gates/derived_file_deletion_gate.py；src/zephyr/gov_enforcement/commit_gates/issue_resolved_integrity_gate.py；src/zephyr/gov_enforcement/commit_gates/protected_paths_gate.py；src/zephyr/gov_enforcement/commit_gates/ruling_commit_verified_gate.py；src/zephyr/gov_enforcement/commit_gates/ruling_reference_gate.py；src/zephyr/gov_enforcement/commit_gates/_reference_helpers.py；src/zephyr/gov_enforcement/rule_bridge/commit_preflight.py；src/zephyr/gov_enforcement/rule_bridge/worktree_drift_watchdog.py
- src_runtime 读者（前4）：src/zephyr/governance/audit/blueprint_status_transition_reconciler.py；src/zephyr/governance/audit/dead_public_wrapper_reconciler.py；src/zephyr/governance/audit/reconciliation_registry.py；src/zephyr/governance/audit/remediation_progress_reconciler.py
- scripts 读者（前4）：scripts/governance/d11_compliance/validate_exit_codes.py；scripts/governance/d11_compliance/validate_script_naming.py；scripts/governance/d6_security/detect_git_dangerous.py；scripts/governance/reconcile_generators.py
- generator 读者（前2）：scripts/governance/d5_architecture/generators/generate_panorama_registry.py；scripts/governance/generate_project_depgraph.py

### REG-CAPCAN-001 — docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml

- 体量：2357752 B；主容器 `creation_tokens` 9841 条；身份键 token,file
- churn30d=512；热文件词表成员=是
- 写者：manual+扫描(semi)：写=batch_creation_tokens.py(CREATE-GUARD通道)；扫=CapabilityLookup.__init__
- 门禁加载者（grep 实证 9 个文件）：src/zephyr/gov_enforcement/commit_gates/create_guard.py；src/zephyr/gov_enforcement/commit_gates/derivation_annotation_gate.py；src/zephyr/gov_enforcement/commit_gates/derived_file_deletion_gate.py；src/zephyr/gov_enforcement/commit_gates/registry_yaml_parse_gate.py；src/zephyr/gov_enforcement/commit_gates/secret_hardcode_gate.py；src/zephyr/gov_enforcement/commit_gates/ssot_redefinition_gate.py；src/zephyr/gov_enforcement/commit_gates/vocab_chain_gate.py；src/zephyr/gov_enforcement/rule_bridge/batched_auto_committer.py；src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py
- src_runtime 读者（前4）：src/zephyr/gov_code_quality/code_dedup/__init__.py；src/zephyr/gov_code_quality/code_dedup/trackers/__init__.py；src/zephyr/governance/audit/reconciliation_registry.py；src/zephyr/governance/capability_lookup.py
- scripts 读者（前4）：scripts/git_commit.py；scripts/governance/_shared/frontmatter.py；scripts/governance/architecture_health_dashboard.py；scripts/governance/d11_compliance/validate_script_naming.py
- generator 读者（前1）：scripts/governance/generate_project_depgraph.py
- config 读者（前1）：config/llm_security_gateway.yaml

### REG-GEN-001 — docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml

- 体量：2357752 B；主容器 `creation_tokens` 9841 条；身份键 token,file
- churn30d=512；热文件词表成员=是
- 写者：manual+扫描(semi)：写=batch_creation_tokens.py(CREATE-GUARD通道)；扫=CapabilityLookup.__init__
- 门禁加载者（grep 实证 9 个文件）：src/zephyr/gov_enforcement/commit_gates/create_guard.py；src/zephyr/gov_enforcement/commit_gates/derivation_annotation_gate.py；src/zephyr/gov_enforcement/commit_gates/derived_file_deletion_gate.py；src/zephyr/gov_enforcement/commit_gates/registry_yaml_parse_gate.py；src/zephyr/gov_enforcement/commit_gates/secret_hardcode_gate.py；src/zephyr/gov_enforcement/commit_gates/ssot_redefinition_gate.py；src/zephyr/gov_enforcement/commit_gates/vocab_chain_gate.py；src/zephyr/gov_enforcement/rule_bridge/batched_auto_committer.py；src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py
- src_runtime 读者（前4）：src/zephyr/gov_code_quality/code_dedup/__init__.py；src/zephyr/gov_code_quality/code_dedup/trackers/__init__.py；src/zephyr/governance/audit/reconciliation_registry.py；src/zephyr/governance/capability_lookup.py
- scripts 读者（前4）：scripts/git_commit.py；scripts/governance/_shared/frontmatter.py；scripts/governance/architecture_health_dashboard.py；scripts/governance/d11_compliance/validate_script_naming.py
- generator 读者（前1）：scripts/governance/generate_project_depgraph.py
- config 读者（前1）：config/llm_security_gateway.yaml

### REG-ERRCODE-001 — architecture_model/contracts/error_code_registry.yaml

- 体量：204249 B；主容器 `error_codes` 789 条；身份键 file
- churn30d=78；热文件词表成员=否
- 写者：manual
- 门禁加载者（grep 实证 1 个文件）：src/zephyr/gov_enforcement/commit_gates/errcode_consistency_gate.py
- src_runtime 读者（前4）：src/zephyr/autonomy_core/agentic_drift_guard.py；src/zephyr/autonomy_core/drift_semantic_reviewer.py；src/zephyr/data/alert_webhook_dispatch.py；src/zephyr/intelligence/gguf_model_manager.py

### ORPHAN — docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml

- 体量：1055258 B；主容器 `entries` 623 条
- churn30d=69；热文件词表成员=是
- 写者：manual(ROOR)
- 门禁加载者（grep 实证 1 个文件）：src/zephyr/gov_enforcement/registry_alignment.py

### ORPHAN — docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml

- 体量：3346134 B；主容器 `entries` 7194 条
- churn30d=200；热文件词表成员=是
- 写者：manual：写=scripts/governance/d3_metadata/add_module_translation.py + algo_flow_translation_sync.py
- 门禁加载者（grep 实证 3 个文件）：src/zephyr/gov_enforcement/commit_gates/battle_map_alignment_gate.py；src/zephyr/gov_enforcement/commit_gates/translation_coverage_gate.py；src/zephyr/gov_enforcement/commit_gates/library/library_blood_flesh_gate.py

### ORPHAN — docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml

- 体量：376186 B；主容器 `entries` 220 条
- churn30d=68；热文件词表成员=否
- 写者：manual：裁定登记流(RULE-RULING，同commit原子，gateway校验)
- 门禁加载者（grep 实证 4 个文件）：src/zephyr/gov_enforcement/registry_alignment.py；src/zephyr/gov_enforcement/commit_gates/ruling_reference_gate.py；src/zephyr/gov_enforcement/commit_gates/_reference_helpers.py；src/zephyr/gov_enforcement/rule_bridge/commit_preflight.py

## §6 关键发现（挖矿产出，供乙/丙车道与 Owner 决策）

- **F1 ROOR 自身漂移**：summary.total_registries=76 vs 实体 77（差 1）；entry_count 陈旧样例：REG-SCRIPT-001 991→实测 1037、REG-DOC-001 256→282、REG-GATE-CAT-001 169→171、REG-SKILL-001 22→目录实存 34 个 yaml（计数口径待澄清）。ROOR 是"注册表的注册表"，其自身计数纪律是迁 PG 后 row-count 一致性门的前身。
- **F2 册外孤儿面 = 事故高频面**：35 个未册 catalogs 恰含三个 DEFAULT_HOT_FILES 成员（module_translation_registry 7194 条 / candidate_module_registry 623 条）与 ruling_registry（220 条裁定，RULE-RULING 真源）。未册=无 ROOR 一致性校验覆盖=迁移盘点最易漏的暗区。
- **F3 同文件多 ID**：REG-CAPCAN≡REG-GEN（同文件两 ID 两套 counting_rule）、REG-STD-005..008 四 ID 一文件——宪法 w5_1 内收判据（同真源可派生→必并）的直接命中，迁 PG 前应先并 ID，否则一张 PG 表挂四个 registry_id。
- **F4 官方热文件词表与 churn 榜互证**：file_utils.py DEFAULT_HOT_FILES 四张注册表全部落在 churn 前 8（512/200/166/114 次/30d），"多写者 contested"判据双源确认，R2 名单可信。
- **F5 门禁直读面 = 迁移硬依赖**：capability_canonical_file_registry 被 6 个 commit gate 直读（create_guard/derivation_annotation/derived_file_deletion/registry_yaml_parse/secret_hardcode/ssot_redefinition）+ CapabilityLookup；gate_registry.yaml 被 20+ gate 读 own_scope；module_id_consistency_gate 同时读 module_id/template/cross_module 三表。迁 PG 必须同步改这些 loader 或先做只读适配层，否则 commit 链当场断。
- **F6 PG 先例已在**：depgraph 双表（REG-ARCH-PANORAMA/REG-DEPGRAPH）+ meta_question 三表已在 postgresql://localhost:5432/depgraph——迁移不是开荒，ROOR 介质字段已有 postgresql:// 先例格式。
- **F7 计数器形态三分**：list-of-dicts（多数治理表，身份键=id/registry_id/…）、dict-keyed（capability_canonical_file_registry.creation_tokens 以 token 为键 9841 条、fail_open_register.by_stage）、文档内嵌（blueprint 三件）。PG 表设计需按形态分型，不能一张宽表通吃。
- **F9 R5 残余风险注记**：生成器工件并非零并发——gate_registry（churn20）、script-manifest（53/52）、registry_master_index（71）的"单写者"是生成器本身，而生成器被多会话各自触发；现有防线=safe_write CAS+队列 serializer 串行落地。迁 PG 不解决生成器读态陈旧（读 HEAD 期间他人落地），此项与介质无关，留观。
- **F8 快照型"注册表"勿迁**：REG-METAQ-001 的 YAML 快照与 REG-INV-001（unified-asset-index，33249 资产）均为生成器产物，真源在他处——迁 PG 只迁真源，快照/工件留 git（R5 已判）。

## §7 观察项与越界登记

- 本车道零越界（未动任何既有文件；唯一写面=本册+creation_token 登记）。
- 观察 O1：`scripts/governance/d3_metadata/batch_creation_tokens.py.tmp.21732.1992a99bc44d` 原子写残尸在盘（非本车道产物，留 Owner/写者处置）。
- 观察 O2：`data/capability_cards/meta_question_registry.yaml` 处于 staged-deleted + 磁盘 untracked 双态（git status `D ` + `??`），与能力卡 ttl 批（d08f752d77）相关，归属链待其 Owner 收口。
- 观察 O3：REG-SKILL-001 physical_path 是目录而非文件，且目录内混有非能力卡 yaml（daemon_registry/meta_question_registry/_fixer-registry 同目录）——ROOR 口径"目录=注册表"使计数规则（22 vs 34）无法机械复核。

## §8 验收对照

| 派单判据 | 结果 |
|---|---|
| 表内清单与实际文件一一对应 | A 表 77/77 ROOR ID 全录（含 2 PG+1 快照漂移定案）；B 表 45 孤儿全录；自检=生成脚本断言行数 |
| 每表消费方有 grep 证据 | 每行附 git grep -F 分桶计数；gate 加载者给到文件级路径（211 个执法 .py 全扫）；P0 卡片给全路径 |
| 适合迁PG/留git 标注 | §2 判级规则 + 每行判级列 + §5 P0 卡片 |
| 只读零改 | 除本册与 token 登记外零写；无既有文件改动 |
