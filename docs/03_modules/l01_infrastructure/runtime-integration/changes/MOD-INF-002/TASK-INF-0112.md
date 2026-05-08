---
task_id: "TASK-INF-0112"
source_blueprint: "MOD-INF-002"
source_section: "蓝图 §2.1-L 模块通信模式 B5-L01~L08 + §2.1-M 确定性复现 B5-M01~M06 + §2.1-N 长期演进 B5-N01~N06 + §2.1-O AI施工模式库 B5-O01~O08 + §5.3 ModuleTemplate代码骨架"
title: "盲点关闭——L.通信模式+L03~L08 + M.确定性复现 B5-M01~M06 + N.生命周期 B5-N01~N06 + O.AI模式库 B5-O01~O08"
description: |
  关闭四类盲点共 28 项。
  L.通信模式（B5-L01~L08）：Request-Reply + Scatter-Gather + Pipeline/Chain + CompetingConsumers +
  Content-Based Router + Message Filter/Enrichment + Aggregation/Batching + Return Address/Callback——Enterprise Integration Patterns 全目录。
  M.确定性复现（B5-M01~M06）：DeterministicRandom（§5.3代码骨架已实现于 TASK-INF-0111）+
  SimulatedClock（已实现）+ Event Replay with Exact Timing + Snapshot→Restore for Debugging +
  Execution Log Verbosity Control + Non-Intrusive Debugging Hooks（DTrace/eBPF对标）。
  N.长期演进（B5-N01~N06）：Module Deprecation Lifecycle（5阶段：标记→警告→隔离→归档→删除）+
  Breaking Change Management（2版本共存+路由+N月移除）+ Backward Compatibility Window+
  Module Migration Path Documentation + Dead Code Detection（vulture/coverage）+
  Cyclomatic Complexity Guard（McCabe >15→简化；>25→CI拒绝merge）。
  O.AI施工模式库（B5-O01~O08）：ModuleTemplate System（§5.3 Jinja2模板代码骨架）+
  Anti-Patterns Catalog（"在这个系统中绝对不要做什么"）+
  Design Decision Tree（EventBus vs 直接调用决策流程）+
  Error Handling Patterns by Module Type + Module Naming Convention Enforcer+
  Code Ownership Manifest（AI施工% vs Owner手动% vs AI自修复%）+
  AI Confidence Annotation（0-1信心分数→REVIEW_NEEDED标记）+
  Progressive Code Review Depth（3级审查深度——>0.9轻审/0.5-0.9中审/<0.5重审）。
priority: "P2"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\events\\comm_patterns.py"
    description: "8种通信模式目录——RequestReply/ScatterGather/Pipeline/CompetingConsumers/ContentRouter/MessageFilter/Aggregator/ReturnAddress"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\module_lifecycle_manager.py"
    description: "ModuleLifecycleManager——5阶段模块废弃生命周期+Breaking Change管理+后向兼容窗口"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\cyclomatic_guard.py"
    description: "CyclomaticComplexityGuard——McCabe圈复杂度检测+CI门禁"
  - path: "D:\\ZephyrAlpha\\templates\\module_template.py.j2"
    description: "模块模板骨架——Jinja2模板：abc→lifecycle→event_handler→config→tests"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\ai_annotations.py"
    description: "AI Confidence Annotation + Code Ownership Manifest + Progressive Review Depth"
  - path: "D:\\ZephyrAlpha\\config\\anti_patterns_catalog.yaml"
    description: "反模式目录——"绝对不要做什么"：不绕过EventBus/不直接import内部函数等"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\events\\comm_patterns.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\module_lifecycle_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\cyclomatic_guard.py"
  - "D:\\ZephyrAlpha\\templates\\module_template.py.j2"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\ai_annotations.py"
  - "D:\\ZephyrAlpha\\config\\anti_patterns_catalog.yaml"
forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"
applicable_rules:
  - module_id: "MOD-INF-002"
    section: "§5.3 ModuleTemplate 代码骨架"
    reason: "Jinja2模板：module_id + capabilities + LifecycleAware + EventConsumer + Configurable"
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "模块命名规范：lXX_function_module_name 强制一致——B5-O05 落地"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
    reason: "§2.1-L通信模式/§2.1-M确定性复现/§2.1-N长期演进/§2.1-O AI模式库 + §5.3 ModuleTemplate代码骨架"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
estimated_tokens: 28000
timeout_minutes: 90
acceptance_criteria:
  - "L. 8种通信模式全部有 type-safe 接口定义——RequestReply/ScatterGather/Pipeline/CompetingConsumers/ContentRouter/MessageFilter/Aggregator/ReturnAddress（B5-L01~L08）"
  - "M. EventReplay: 从EventStore读取事件→按记录时间戳精确重放→同序同果（B5-M03）"
  - "M. ExecutionLog: DEBUG_MODULE=l06 环境变量控制详细度（B5-M05）"
  - "N. ModuleDeprecation: 标记→警告→隔离→归档→删除 5阶段完整生命周期（B5-N01）"
  - "N. CyclomaticComplexityGuard: >15→CI警告；>25→CI拒绝merge（B5-N06）"
  - "O. ModuleTemplate: AI创建新模块时自动从 Jinja2 模板生成骨架（B5-O01）"
  - "O. AntiPatternsCatalog: "绝对不要做什么"清单——至少10条（B5-O02）"
  - "O. AI Confidence: 信心>0.9→轻审；0.5-0.9→中审；<0.5→重审+Owner review（B5-O07/O08）"
rollback_instructions: |
  1. 删除 shared/events/comm_patterns.py
  2. 删除 shared/production/module_lifecycle_manager.py / cyclomatic_guard.py / ai_annotations.py
  3. 删除 templates/module_template.py.j2
  4. 删除 config/anti_patterns_catalog.yaml
  5. 如 templates/ 目录变为空→删除目录
depends_on: []
blocked_by: []
status: "created"
tags_fn:
  - "infra"
  - "biz"
  - "security"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "experimental"
tags_mo:
  - "MOD-INF-002"
  - "MOD-INF-016"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
