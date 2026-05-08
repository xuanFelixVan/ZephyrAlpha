---
task_id: "TASK-MST-0019"
source_blueprint: "MOD-MASTER-001"
source_section: "蓝图 §二十 数据生命周期 + 多环境 + Chaos + Codegen + Breaking Change——CT-DATA-LIFECYCLE-001/CT-CHAOS-001/GATE-CDC-2"

title: "实现数据生命周期 + 多环境隔离 + Chaos Engineering + Contract→Codegen + Breaking Change Detection"
description: |
  实现 §二十 定义的数据与运维基础设施：
  (1)CT-DATA-LIFECYCLE-001 数据保留策略——8类数据各自生命周期（hot/cold/archive/purge）；
  (2)多环境隔离——dev(chromadb:dev/, sqlite:dev.db, token:4000, models:haiku) vs prod(8000, opus/gpt-5.2)；
  (3)CT-CHAOS-001 Chaos Engineering 故障注入——4个注入点(VMS延迟/VMS错误/LSG Cr a s h/Script exit 3)×月度执行；
  (4)Contract→Codegen——变更 CT-* YAML 自动生成 Python Protocol class+dataclass；
  (5)GATE-CDC-2 Breaking Change Detector——字段删除/类型变更→BREAKING→CI FAIL；新增optional字段→OK。

priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\contract_registry.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\data_lifecycle.py"
    description: "数据生命周期管理器——CT-DATA-LIFECYCLE-001——8类数据保留策略+每日GC"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\chaos_engine.py"
    description: "Chaos 故障注入引擎——CT-CHAOS-001——4注入点×月度执行"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\gates\\breaking_change_detector.py"
    description: "Breaking Change 检测器——GATE-CDC-2——5条规则"
  - path: "D:\\ZephyrAlpha\\scripts\\governance\\generators\\generate_contracts.py"
    description: "契约代码生成器——CT-* YAML→Python Protocol + Schema YAML→dataclass"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_data_lifecycle.py"
    description: "数据生命周期单元测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\data_lifecycle.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\chaos_engine.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\gates\\breaking_change_detector.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\generators\\generate_contracts.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_data_lifecycle.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\contract_registry.py"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号格式"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径架构合规创建"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
    reason: "§二十——数据生命周期+多环境+Chaos+Codegen+Breaking Change 完整定义"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 15000
timeout_minutes: 60

acceptance_criteria:
  - "data_lifecycle.py 实现 8 类数据的各自保留策略——Finding 30d hot/365d cold, KE 90d DRAFT→ARCHIVED, audit_log 7y immutable"
  - "每日 06:00 GC 扫描 → 按 retention_policies 清理 → 写 GC summary audit_log"
  - "chaos_engine.py 支持 4 个注入点 × 对应 expect 行为验证（dev 环境月度执行）"
  - "generate_contracts.py 读取 CT-* YAML → 生成 Python Protocol class → CI 对比 diff → FAIL 如不一致"
  - "breaking_change_detector.py 字段删除→BREAKING CI WARN+Owner确认 / 类型变更→BREAKING CI FAIL / 新增optional→OK"
  - "Pydantic V2 BaseModel 实现"

rollback_instructions: |
  1. 删除新增的 4 个源码文件
  2. 删除新增的测试文件
  3. 删除 generate_contracts.py 生成的 Python Protocol 文件（如有）

depends_on: ["TASK-MST-0004"]
blocked_by: []

status: "done"

tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-MASTER-001"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---
