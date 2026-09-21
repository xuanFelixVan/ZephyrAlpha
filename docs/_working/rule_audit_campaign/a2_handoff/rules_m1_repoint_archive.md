---
ttl: task_bound
completes_when: 载体随 a2_handoff 批落 HEAD 后转 archived
---

# rules M1 repoint 载体（裁定#392（D-1） 方案a：.patch/.json 转 .md 附录）

> 出处：st-final3-20260919 产出的 rule_audit M1 repoint 交付件，staged 未提交 48h+。
> 实质已落地：rules 批统一入库 48acb99c46（裁定#372 确认 M1 三分 rules 统一批），
> 本 patch apply 会报 already applied——仅存历史证据，勿再 apply。
> 2026-09-21 st-taskcards-exec-20260921 按 裁定#392（D-1） 方案a 转载体：.patch/.json 删原文件，
> 内容本文件保真；工具坐标=a2_genpatch_archived_20260920.py（.runtime/tmp，TTL 易失如实注记）。

## 附录一：rules_m1_repoint.patch 原文

```diff
--- a/docs/01_policies_and_standards/rules/trae_003_task_granularity_threshold.yaml
+++ b/docs/01_policies_and_standards/rules/trae_003_task_granularity_threshold.yaml
@@ -80,7 +80,7 @@
       change: '建卡路径规则变更：四指标→八指标机械门(新增depgraph操作/消费者影响>50/跨域操作/多步骤>3)；RULE-ZERO-TASK从"蓝图拆解唯一路径"改为"TaskRepository.create()唯一入口+双触发(用户主动OR阈值)"；建卡来源扩展(蓝图/Bug/债务/扫描/重构)'
     - version: '1.1.0'
       date: '2026-06-19'
-      change: 'RQ审查修复: references.modules路径修正(src/zephyr/data/persistence→src/zephyr/governance/task_repo.py); provenance哈希同步; 修复内部矛盾(prohibitions阈值>3/>5→>1/>3与conditions对齐); 新增change_history(RQ-14)'
+      change: 'RQ审查修复: references.modules路径修正(src/zephyr/data/persistence→src/zephyr/governance/persistence/task_repo.py); provenance哈希同步; 修复内部矛盾(prohibitions阈值>3/>5→>1/>3与conditions对齐); 新增change_history(RQ-14)'
     - version: '1.0.0'
       date: '2026-06-13'
       change: '从project_rules.md(RULE-SIX/RULE-THIRTEEN)+onboarding_detail.md(§四)提取初始版本'
@@ -88,7 +88,7 @@
   rule_ids: []
   scripts: []
   modules:
-  - src/zephyr/governance/task_repo.py
+  - src/zephyr/governance/persistence/task_repo.py
   blueprints:
   - GOV-TASK-001
 enforcement:
--- a/docs/01_policies_and_standards/rules/trae_005_modification_governance.yaml
+++ b/docs/01_policies_and_standards/rules/trae_005_modification_governance.yaml
@@ -88,7 +88,7 @@
   scripts:
   - scripts/governance/generate_project_depgraph.py
   - scripts/governance/generate_project_path_tree.py
-  - scripts/governance/diagnose_depgraph.py
+  - scripts/governance/d5_architecture/diagnose_depgraph.py
   modules: []
   blueprints: []
 enforcement:
--- a/docs/01_policies_and_standards/rules/trae_013_arch_cross_package_dep.yaml
+++ b/docs/01_policies_and_standards/rules/trae_013_arch_cross_package_dep.yaml
@@ -57,7 +57,7 @@
       fail: 产生新循环依赖(跨层循环 OR 同层循环)
     actions:
     - type: mandatory
-      step: 移动模块/拆包/改标签前MUST执行依赖图推演(STEP 1)；推演发现新循环→BLOCKED，必须先解决循环再执行；验证命令python scripts/governance/diagnose_depgraph.py确认无循环
+      step: 移动模块/拆包/改标签前MUST执行依赖图推演(STEP 1)；推演发现新循环→BLOCKED，必须先解决循环再执行；验证命令python scripts/governance/d5_architecture/diagnose_depgraph.py确认无循环
     - type: clarification
       step: 同层间允许单向依赖(如F2→F4门禁校验预算)，但禁止同层循环依赖(如F2→F4→F2禁止)。同层协作对标K8s/Conductor同层组件协作模式
     prohibitions:
@@ -160,7 +160,7 @@
 references:
   rule_ids: []
   scripts:
-  - scripts/governance/diagnose_depgraph.py
+  - scripts/governance/d5_architecture/diagnose_depgraph.py
   - scripts/governance/generate_project_depgraph.py
   modules: []
   blueprints: []
@@ -168,7 +168,7 @@
   paired_gate_id: "GATE-ARCH"  # Phase 3.5 规则-执行配对
   type: code
   executors:
-  - scripts/governance/diagnose_depgraph.py
+  - scripts/governance/d5_architecture/diagnose_depgraph.py
   bypass_allowed: false
 metadata:
   change_policy: stable
--- a/docs/01_policies_and_standards/rules/trae_016_arch_drift_detection.yaml
+++ b/docs/01_policies_and_standards/rules/trae_016_arch_drift_detection.yaml
@@ -126,7 +126,7 @@
   rule_ids:
   - TRAE-017
   scripts:
-  - scripts/governance/diagnose_depgraph.py
+  - scripts/governance/d5_architecture/diagnose_depgraph.py
   - scripts/governance/d5_architecture/checkers/check_contract_code_drift.py
   - scripts/governance/d5_architecture/validators/validate_load_path_integrity.py
   - scripts/governance/d1_structure/validate_config_integrity.py
@@ -137,7 +137,7 @@
   paired_gate_id: "GATE-DRIFT"  # Phase 3.5 规则-执行配对
   type: code
   executors:
-  - scripts/governance/diagnose_depgraph.py
+  - scripts/governance/d5_architecture/diagnose_depgraph.py
   - scripts/governance/d5_architecture/checkers/check_contract_code_drift.py
   - scripts/governance/d5_architecture/validators/validate_load_path_integrity.py
   - scripts/governance/d1_structure/validate_config_integrity.py
--- a/docs/01_policies_and_standards/rules/trae_017_arch_governance_order.yaml
+++ b/docs/01_policies_and_standards/rules/trae_017_arch_governance_order.yaml
@@ -76,7 +76,7 @@
   - TRAE-016
   scripts:
   - scripts/governance/generate_project_depgraph.py
-  - scripts/governance/diagnose_depgraph.py
+  - scripts/governance/d5_architecture/diagnose_depgraph.py
   - scripts/governance/generate_project_path_tree.py
   - scripts/governance/d11_compliance/audit_registration.py
   modules: []
@@ -86,7 +86,7 @@
   type: code
   executors:
   - scripts/governance/generate_project_depgraph.py
-  - scripts/governance/diagnose_depgraph.py
+  - scripts/governance/d5_architecture/diagnose_depgraph.py
   - scripts/governance/generate_project_path_tree.py
   - scripts/governance/d11_compliance/audit_registration.py
   bypass_allowed: false
--- a/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml
+++ b/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml
@@ -436,7 +436,7 @@
       expected_exit: depends_on与实际引用一致
       on_fail: 引用不一致→补充或移除
     - step: 同步规则注册表
-      command: python scripts/governance/sync_rule_registry.py
+      command: python scripts/governance/d8_doc_sync/sync_rule_registry.py
       expected_exit: exit 0
       on_fail: 注册表不同步→修复后重新运行
     - step: 标记规格化成熟度
@@ -629,7 +629,7 @@
       details: P1修复;脚本名错误修正(generate_project_ownership_map.py→generate_path_ownership_map.py,后者为真实存在的脚本);kebab-case文件名引用修正为snake_case(project-path-tree.yaml→project_path_tree.yaml/path-ownership-map.yaml→path_ownership_map.yaml)
 references:
   rule_ids: [TRAE-010, TRAE-011, TRAE-012, TRAE-028, TRAE-048]
-  scripts: [scripts/governance/generate_project_path_tree.py, scripts/governance/generators/generate_path_ownership_map.py, scripts/governance/sync_rule_registry.py]
+  scripts: [scripts/governance/generate_project_path_tree.py, scripts/governance/generators/generate_path_ownership_map.py, scripts/governance/d8_doc_sync/sync_rule_registry.py]
   modules: []
   blueprints: []
 enforcement:
--- a/docs/01_policies_and_standards/rules/trae_033_module_registration_sync.yaml
+++ b/docs/01_policies_and_standards/rules/trae_033_module_registration_sync.yaml
@@ -250,7 +250,7 @@
 references:
   rule_ids: []
   scripts:
-  - scripts/governance/check_registry_consistency.py
+  - scripts/governance/d3_metadata/check_registry_consistency.py
   - scripts/governance/d3_metadata/check_frontmatter_metadata.py
   - scripts/governance/d5_architecture/checkers/check_architecture_gates.py
   - scripts/governance/d5_architecture/validators/validate_directory_structure.py
@@ -262,7 +262,7 @@
   paired_gate_id: "MODULE-ID-CONSISTENCY"  # Phase 3.5 规则-执行配对
   type: code
   executors:
-  - scripts/governance/check_registry_consistency.py
+  - scripts/governance/d3_metadata/check_registry_consistency.py
   bypass_allowed: false
 metadata:
   change_policy: stable
--- a/docs/01_policies_and_standards/rules/trae_034_task_card_standard.yaml
+++ b/docs/01_policies_and_standards/rules/trae_034_task_card_standard.yaml
@@ -1206,7 +1206,7 @@
       - consumer: src/zephyr/gov_enforcement/rule_enforcement/task_completion_gate.py
         dependency: 残留物分类规则、退出码定义
         sync_requirement: 分类规则变更必须同commit更新
-      - consumer: src/zephyr/governance/task_repo.py
+      - consumer: src/zephyr/governance/persistence/task_repo.py
         dependency: COMPLETED/VERIFIED状态转换条件
         sync_requirement: 转换条件变更必须同commit更新
       - consumer: scripts/governance/check_handoff_protocol.py
@@ -1344,10 +1344,10 @@
   - scripts/governance/d11_compliance/audit_registration.py
   - scripts/governance/generate_project_depgraph.py
   - scripts/governance/generate_project_path_tree.py
-  - scripts/governance/diagnose_depgraph.py
+  - scripts/governance/d5_architecture/diagnose_depgraph.py
   modules:
   - src/zephyr/gov_enforcement/rule_enforcement/task_completion_gate.py
-  - src/zephyr/governance/task_repo.py
+  - src/zephyr/governance/persistence/task_repo.py
   blueprints:
   - 03_modules/_domain_infrastructure_runtime/task_system/blueprint.md
 enforcement:
--- a/docs/01_policies_and_standards/rules/trae_035_task_construction_verification.yaml
+++ b/docs/01_policies_and_standards/rules/trae_035_task_construction_verification.yaml
@@ -152,7 +152,7 @@
     - type: mandatory
       step: 重新生成路径树——python D:/ZephyrAlpha/scripts/governance/generate_project_path_tree.py --write
     - type: mandatory
-      step: 运行诊断——python D:/ZephyrAlpha/scripts/governance/diagnose_depgraph.py
+      step: 运行诊断——python D:/ZephyrAlpha/scripts/governance/d5_architecture/diagnose_depgraph.py
     - type: mandatory
       step: 全景图和路径树中无旧层名/旧路径引用→对齐通过
     - type: mandatory
@@ -171,7 +171,7 @@
     - type: mandatory
       step: G6依赖全景图生成——python D:/ZephyrAlpha/scripts/governance/generate_project_depgraph.py --output-db depgraph --force（⚠️架构升级期间禁止运行——会覆盖depgraph全景图；正常期方可运行。--output-yaml不支持，使用--output-db写入PostgreSQL）
     - type: mandatory
-      step: G6依赖图诊断——python D:/ZephyrAlpha/scripts/governance/diagnose_depgraph.py
+      step: G6依赖图诊断——python D:/ZephyrAlpha/scripts/governance/d5_architecture/diagnose_depgraph.py
     - type: mandatory
       step: 路径树刷新——python D:/ZephyrAlpha/scripts/governance/generate_project_path_tree.py --write
     prohibitions: []
@@ -284,7 +284,7 @@
       expected_exit: 0
       on_fail: 结构未同步
     - step: G6依赖图诊断
-      command: python D:/ZephyrAlpha/scripts/governance/diagnose_depgraph.py
+      command: python D:/ZephyrAlpha/scripts/governance/d5_architecture/diagnose_depgraph.py
       expected_exit: 0
       on_fail: 有错误需修复
     - step: 路径树刷新
@@ -335,10 +335,10 @@
   - scripts/governance/d11_compliance/audit_registration.py
   - scripts/governance/generate_project_depgraph.py
   - scripts/governance/generate_project_path_tree.py
-  - scripts/governance/diagnose_depgraph.py
+  - scripts/governance/d5_architecture/diagnose_depgraph.py
   modules:
   - src/zephyr/gov_enforcement/rule_enforcement/task_completion_gate.py
-  - src/zephyr/governance/task_repo.py
+  - src/zephyr/governance/persistence/task_repo.py
   blueprints:
   - 03_modules/_domain_infrastructure_runtime/task_system/blueprint.md
 enforcement:
--- a/docs/01_policies_and_standards/rules/trae_036_arch_gate_transition.yaml
+++ b/docs/01_policies_and_standards/rules/trae_036_arch_gate_transition.yaml
@@ -312,7 +312,7 @@
       expected_exit: 无冲突
       on_fail: 必须先废弃或修改KB决策记录
     - step: 检查无循环——变更是否引入循环依赖（跨层循环 OR 同层循环）
-      command: python D:/ZephyrAlpha/scripts/governance/diagnose_depgraph.py
+      command: python D:/ZephyrAlpha/scripts/governance/d5_architecture/diagnose_depgraph.py
       expected_exit: 无新循环依赖（跨层无循环 AND 同层无循环）
       on_fail: 必须重新设计消除循环
     - step: 检查有明确回滚步骤
@@ -805,7 +805,7 @@
     impact_on_rules: 参考文件是门禁策略的上下游依赖
     key_decisions:
     - 架构决策记录——门禁策略定义/严重级别映射/YAML Schema规范/豁免机制/知识管道（KB系统退役前KBG-0030/0038/0040/0041/0013，决策内容内联于blueprint.md）
-    - 代码模块——src/zephyr/gov_enforcement/rule_enforcement/gate_engine.py(GateEngine)/src/zephyr/governance/task_repo.py(task_repo)
+    - 代码模块——src/zephyr/gov_enforcement/rule_enforcement/gate_engine/gate_engine.py(GateEngine)/src/zephyr/governance/persistence/task_repo.py(task_repo)
     - YAML文件——src/zephyr/gov_enforcement/rule_enforcement/下门禁YAML(g1_ingest.yaml~g5_extract.yaml)+phase_manager配置+schema定义
   gov_arch_006_change_history:
     section_type: examples
@@ -856,11 +856,11 @@
   scripts:
   - scripts/governance/d5_architecture/validators/lifecycle/validate_phase_transition.py
   - scripts/governance/d5_architecture/validators/validate_ssot.py
-  - scripts/governance/diagnose_depgraph.py
+  - scripts/governance/d5_architecture/diagnose_depgraph.py
   modules:
-  - src/zephyr/gov_enforcement/rule_enforcement/gate_engine.py
-  - src/zephyr/governance/task_repo.py
-  - src/zephyr/governance/phase_manager.py
+  - src/zephyr/gov_enforcement/rule_enforcement/gate_engine/gate_engine.py
+  - src/zephyr/governance/persistence/task_repo.py
+  - src/zephyr/governance/ops_governance/phase_manager.py
   - src/zephyr/gov_enforcement/rule_enforcement/g1_ingest.yaml
   - src/zephyr/gov_enforcement/rule_enforcement/g2_triage.yaml
   - src/zephyr/gov_enforcement/rule_enforcement/g3_evaluate.yaml
@@ -875,9 +875,9 @@
   executors:
   - scripts/governance/d5_architecture/validators/lifecycle/validate_phase_transition.py
   - scripts/governance/d5_architecture/validators/validate_ssot.py
-  - scripts/governance/diagnose_depgraph.py
-  - src/zephyr/gov_enforcement/rule_enforcement/gate_engine.py
-  - src/zephyr/governance/phase_manager.py
+  - scripts/governance/d5_architecture/diagnose_depgraph.py
+  - src/zephyr/gov_enforcement/rule_enforcement/gate_engine/gate_engine.py
+  - src/zephyr/governance/ops_governance/phase_manager.py
   bypass_allowed: false
 metadata:
   change_policy: stable
@@ -890,7 +890,7 @@
     by: session-20260619-001
     changes:
     - RQ审查修复——填充references(enforcement)空字段
-    - 修正gate_engine.py路径(src/zephyr/governance/gate_engine.py→src/zephyr/gov_enforcement/rule_enforcement/gate_engine.py)
+    - 修正gate_engine.py路径(src/zephyr/governance/gate_engine.py→src/zephyr/gov_enforcement/rule_enforcement/gate_engine/gate_engine.py)
     - 修正门禁YAML路径(src/zephyr/gov_enforcement/rule_enforcement/→src/zephyr/gov_enforcement/rule_enforcement/)
     - 标注validate_phase_exit/entry.py为计划中脚本
     - 修复g1_g5_check_items的section_type(verification→rule)
--- a/docs/01_policies_and_standards/rules/trae_044_compliance_audit.yaml
+++ b/docs/01_policies_and_standards/rules/trae_044_compliance_audit.yaml
@@ -417,7 +417,7 @@
       expected_exit: 0
       on_fail: 修复门禁违规
     - step: 环境就绪检查
-      command: python scripts/governance/env_check.py --install
+      command: python scripts/governance/meta/env_check.py --install
       expected_exit: 0
       on_fail: 安装缺失依赖
     - step: 索引自动校验/修复
@@ -869,7 +869,7 @@
   rule_ids: []
   scripts:
   - scripts/governance/run_all.py
-  - scripts/governance/env_check.py
+  - scripts/governance/meta/env_check.py
   - scripts/governance/score_architecture.py
   - scripts/governance/status.py
   modules: []
--- a/docs/01_policies_and_standards/rules/trae_054_depgraph_access_protocol.yaml
+++ b/docs/01_policies_and_standards/rules/trae_054_depgraph_access_protocol.yaml
@@ -121,7 +121,7 @@
   - scripts/governance/extract_depgraph.py
   - scripts/governance/apply_depgraph.py
   - scripts/governance/generate_project_depgraph.py
-  - scripts/governance/diagnose_depgraph.py
+  - scripts/governance/d5_architecture/diagnose_depgraph.py
   modules: []
   blueprints: []
 enforcement:
--- a/docs/01_policies_and_standards/rules/trae_055_arch_domain_capacity.yaml
+++ b/docs/01_policies_and_standards/rules/trae_055_arch_domain_capacity.yaml
@@ -353,7 +353,7 @@
   - scripts/governance/extract_depgraph.py
   - scripts/governance/apply_depgraph.py
   - scripts/governance/generate_project_depgraph.py
-  - scripts/governance/diagnose_depgraph.py
+  - scripts/governance/d5_architecture/diagnose_depgraph.py
   modules: []
   blueprints: []
 enforcement:
--- a/docs/01_policies_and_standards/rules/trae_056_module_creation_workflow.yaml
+++ b/docs/01_policies_and_standards/rules/trae_056_module_creation_workflow.yaml
@@ -648,7 +648,7 @@
       action: 运行校验
       rule_ref: MRS-003
       commands:
-      - "python scripts/governance/check_registry_consistency.py"
+      - "python scripts/governance/d3_metadata/check_registry_consistency.py"
       - "python scripts/governance/check_frontmatter_metadata.py"
       - "python scripts/governance/check_architecture_gates.py"
       - "python scripts/governance/validate_directory_registry.py"
@@ -683,7 +683,7 @@
       fail: exit 1 (有孤儿) → 必须修复
     - order: 4
       action: 关键模块导入测试
-      command: "python scripts/governance/verify_key_imports.py"
+      command: "python scripts/governance/d11_compliance/verify_key_imports.py"
       pass: 导入成功
       fail: 导入失败 → 修复import
     - order: 5
@@ -803,9 +803,9 @@
   - scripts/governance/extract_depgraph.py
   - scripts/governance/generate_project_path_tree.py
   - scripts/governance/d3_metadata/check_naming_convention.py
-  - scripts/governance/check_registry_consistency.py
+  - scripts/governance/d3_metadata/check_registry_consistency.py
   - scripts/governance/d11_compliance/audit_registration.py
-  - scripts/governance/verify_key_imports.py
+  - scripts/governance/d11_compliance/verify_key_imports.py
   - scripts/governance/d5_architecture/checkers/check_contract_code_drift.py
   modules: []
   blueprints: []
--- a/docs/01_policies_and_standards/rules/trae_065_capability_lookup_required.yaml
+++ b/docs/01_policies_and_standards/rules/trae_065_capability_lookup_required.yaml
@@ -140,7 +140,7 @@
   - src/zephyr/governance/capability_lookup.py
   - src/zephyr/integration/mcp/rule_discovery_server.py
   - src/zephyr/gov_enforcement/rule_bridge/session_worktree.py
-  - src/zephyr/gov_enforcement/git_commit_gateway.py
+  - src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py
   - scripts/git_commit.py
   - scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py
   - scripts/governance/generators/generate_rule_ai_perception_index.py
--- a/docs/01_policies_and_standards/rules/trae_079_commit_serialization.yaml
+++ b/docs/01_policies_and_standards/rules/trae_079_commit_serialization.yaml
@@ -188,7 +188,7 @@
   - src/zephyr/security/access_control/session_concurrency.py
   - src/zephyr/gov_enforcement/commit_gates/held_overlap_gate.py
   - scripts/governance/git_hooks/post_commit_guard.sh
-  - tests/governance/rule_bridge/test_git_commit_gateway.py
+  - tests/git/test_git_commit_gateway.py
   modules:
   - MOD-GOV-SESSION_WORKTREE
   - MOD-GOV-GIT_COMMIT_GATEWAY
```

## 附录二：rules_repoint_rows.json 原文

```json
[
 {
  "file": "trae_003_task_granularity_threshold.yaml",
  "keypath": "references.modules",
  "line": 91,
  "old": "src/zephyr/governance/task_repo.py",
  "new": "src/zephyr/governance/persistence/task_repo.py",
  "occurrences_in_file": 2
 },
 {
  "file": "trae_005_modification_governance.yaml",
  "keypath": "references.scripts",
  "line": 91,
  "old": "scripts/governance/diagnose_depgraph.py",
  "new": "scripts/governance/d5_architecture/diagnose_depgraph.py",
  "occurrences_in_file": 1
 },
 {
  "file": "trae_013_arch_cross_package_dep.yaml",
  "keypath": "enforcement.executors",
  "line": 163,
  "old": "scripts/governance/diagnose_depgraph.py",
  "new": "scripts/governance/d5_architecture/diagnose_depgraph.py",
  "occurrences_in_file": 0
 },
 {
  "file": "trae_013_arch_cross_package_dep.yaml",
  "keypath": "references.scripts",
  "line": 163,
  "old": "scripts/governance/diagnose_depgraph.py",
  "new": "scripts/governance/d5_architecture/diagnose_depgraph.py",
  "occurrences_in_file": 3
 },
 {
  "file": "trae_016_arch_drift_detection.yaml",
  "keypath": "enforcement.executors",
  "line": 129,
  "old": "scripts/governance/diagnose_depgraph.py",
  "new": "scripts/governance/d5_architecture/diagnose_depgraph.py",
  "occurrences_in_file": 0
 },
 {
  "file": "trae_016_arch_drift_detection.yaml",
  "keypath": "references.scripts",
  "line": 129,
  "old": "scripts/governance/diagnose_depgraph.py",
  "new": "scripts/governance/d5_architecture/diagnose_depgraph.py",
  "occurrences_in_file": 2
 },
 {
  "file": "trae_017_arch_governance_order.yaml",
  "keypath": "enforcement.executors",
  "line": 79,
  "old": "scripts/governance/diagnose_depgraph.py",
  "new": "scripts/governance/d5_architecture/diagnose_depgraph.py",
  "occurrences_in_file": 0
 },
 {
  "file": "trae_017_arch_governance_order.yaml",
  "keypath": "references.scripts",
  "line": 79,
  "old": "scripts/governance/diagnose_depgraph.py",
  "new": "scripts/governance/d5_architecture/diagnose_depgraph.py",
  "occurrences_in_file": 2
 },
 {
  "file": "trae_030_doc_numbering_metadata.yaml",
  "keypath": "references.scripts",
  "line": 439,
  "old": "scripts/governance/sync_rule_registry.py",
  "new": "scripts/governance/d8_doc_sync/sync_rule_registry.py",
  "occurrences_in_file": 2
 },
 {
  "file": "trae_033_module_registration_sync.yaml",
  "keypath": "enforcement.executors",
  "line": 253,
  "old": "scripts/governance/check_registry_consistency.py",
  "new": "scripts/governance/d3_metadata/check_registry_consistency.py",
  "occurrences_in_file": 0
 },
 {
  "file": "trae_033_module_registration_sync.yaml",
  "keypath": "references.scripts",
  "line": 253,
  "old": "scripts/governance/check_registry_consistency.py",
  "new": "scripts/governance/d3_metadata/check_registry_consistency.py",
  "occurrences_in_file": 2
 },
 {
  "file": "trae_034_task_card_standard.yaml",
  "keypath": "references.modules",
  "line": 1209,
  "old": "src/zephyr/governance/task_repo.py",
  "new": "src/zephyr/governance/persistence/task_repo.py",
  "occurrences_in_file": 2
 },
 {
  "file": "trae_034_task_card_standard.yaml",
  "keypath": "references.scripts",
  "line": 1347,
  "old": "scripts/governance/diagnose_depgraph.py",
  "new": "scripts/governance/d5_architecture/diagnose_depgraph.py",
  "occurrences_in_file": 1
 },
 {
  "file": "trae_035_task_construction_verification.yaml",
  "keypath": "references.modules",
  "line": 341,
  "old": "src/zephyr/governance/task_repo.py",
  "new": "src/zephyr/governance/persistence/task_repo.py",
  "occurrences_in_file": 1
 },
 {
  "file": "trae_035_task_construction_verification.yaml",
  "keypath": "references.scripts",
  "line": 338,
  "old": "scripts/governance/diagnose_depgraph.py",
  "new": "scripts/governance/d5_architecture/diagnose_depgraph.py",
  "occurrences_in_file": 4
 },
 {
  "file": "trae_036_arch_gate_transition.yaml",
  "keypath": "enforcement.executors",
  "line": 859,
  "old": "scripts/governance/diagnose_depgraph.py",
  "new": "scripts/governance/d5_architecture/diagnose_depgraph.py",
  "occurrences_in_file": 0
 },
 {
  "file": "trae_036_arch_gate_transition.yaml",
  "keypath": "enforcement.executors",
  "line": 861,
  "old": "src/zephyr/gov_enforcement/rule_enforcement/gate_engine.py",
  "new": "src/zephyr/gov_enforcement/rule_enforcement/gate_engine/gate_engine.py",
  "occurrences_in_file": 0
 },
 {
  "file": "trae_036_arch_gate_transition.yaml",
  "keypath": "enforcement.executors",
  "line": 863,
  "old": "src/zephyr/governance/phase_manager.py",
  "new": "src/zephyr/governance/ops_governance/phase_manager.py",
  "occurrences_in_file": 0
 },
 {
  "file": "trae_036_arch_gate_transition.yaml",
  "keypath": "references.modules",
  "line": 861,
  "old": "src/zephyr/gov_enforcement/rule_enforcement/gate_engine.py",
  "new": "src/zephyr/gov_enforcement/rule_enforcement/gate_engine/gate_engine.py",
  "occurrences_in_file": 4
 },
 {
  "file": "trae_036_arch_gate_transition.yaml",
  "keypath": "references.modules",
  "line": 862,
  "old": "src/zephyr/governance/task_repo.py",
  "new": "src/zephyr/governance/persistence/task_repo.py",
  "occurrences_in_file": 2
 },
 {
  "file": "trae_036_arch_gate_transition.yaml",
  "keypath": "references.modules",
  "line": 863,
  "old": "src/zephyr/governance/phase_manager.py",
  "new": "src/zephyr/governance/ops_governance/phase_manager.py",
  "occurrences_in_file": 2
 },
 {
  "file": "trae_036_arch_gate_transition.yaml",
  "keypath": "references.scripts",
  "line": 859,
  "old": "scripts/governance/diagnose_depgraph.py",
  "new": "scripts/governance/d5_architecture/diagnose_depgraph.py",
  "occurrences_in_file": 3
 },
 {
  "file": "trae_044_compliance_audit.yaml",
  "keypath": "references.scripts",
  "line": 872,
  "old": "scripts/governance/env_check.py",
  "new": "scripts/governance/meta/env_check.py",
  "occurrences_in_file": 2
 },
 {
  "file": "trae_054_depgraph_access_protocol.yaml",
  "keypath": "references.scripts",
  "line": 124,
  "old": "scripts/governance/diagnose_depgraph.py",
  "new": "scripts/governance/d5_architecture/diagnose_depgraph.py",
  "occurrences_in_file": 1
 },
 {
  "file": "trae_055_arch_domain_capacity.yaml",
  "keypath": "references.scripts",
  "line": 356,
  "old": "scripts/governance/diagnose_depgraph.py",
  "new": "scripts/governance/d5_architecture/diagnose_depgraph.py",
  "occurrences_in_file": 1
 },
 {
  "file": "trae_056_module_creation_workflow.yaml",
  "keypath": "references.scripts",
  "line": 806,
  "old": "scripts/governance/check_registry_consistency.py",
  "new": "scripts/governance/d3_metadata/check_registry_consistency.py",
  "occurrences_in_file": 2
 },
 {
  "file": "trae_056_module_creation_workflow.yaml",
  "keypath": "references.scripts",
  "line": 808,
  "old": "scripts/governance/verify_key_imports.py",
  "new": "scripts/governance/d11_compliance/verify_key_imports.py",
  "occurrences_in_file": 2
 },
 {
  "file": "trae_065_capability_lookup_required.yaml",
  "keypath": "references.scripts",
  "line": 143,
  "old": "src/zephyr/gov_enforcement/git_commit_gateway.py",
  "new": "src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py",
  "occurrences_in_file": 1
 },
 {
  "file": "trae_079_commit_serialization.yaml",
  "keypath": "references.scripts",
  "line": 191,
  "old": "tests/governance/rule_bridge/test_git_commit_gateway.py",
  "new": "tests/git/test_git_commit_gateway.py",
  "occurrences_in_file": 1
 }
]
```
