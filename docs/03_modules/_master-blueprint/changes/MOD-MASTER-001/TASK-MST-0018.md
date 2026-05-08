---
task_id: "TASK-MST-0018"
source_blueprint: "MOD-MASTER-001"
source_section: "蓝图 §十九 配置/FeatureFlag/安全——CT-CONFIG-001/CT-FEATUREFLAG-001/CT-SECRETS-001/CT-KISS-001"

title: "实现统一配置管理 + FeatureFlag + Secrets + AI施工KISS约束"
description: |
  实现 §十九 定义的配置、FeatureFlag、安全、KISS 四契约：
  (1)CT-CONFIG-001 12系统共享配置统一管理——config/system_config.yaml 集中管理；
  (2)CT-FEATUREFLAG-001 跨系统能力运行时开关——每条CT-*可运行时禁用 → NOT_AVAILABLE + degrade；
  (3)CT-SECRETS-001 API Key与密钥统一管理——.env本地存储 + 禁止出现在git/源码/蓝图/日志；
  (4)CT-KISS-001 AI施工Keep It Simple约束——每CT-*实现≤3类 + 方法≤30行 + 继承层次≤2。
  Config validation on startup: 校验各系统config引用与CT-CONFIG-001一致性。
  FeatureFlag toggle持久化到db.feature_flags表。
  Secrets startup check: 遍历.env必需key列表 + git log scan API key检测。
  KISS AI self check: "这个实现能否删掉一半代码仍然功能完整？"。

priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
  - "D:\\ZephyrAlpha\\config\\system_config.yaml"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\config_manager.py"
    description: "统一配置管理器——CT-CONFIG-001——12系统共享配置读写+启动时校验"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\feature_flag.py"
    description: "FeatureFlag 管理器——CT-FEATUREFLAG-001——CT-*运行时开关+audit_log"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\gates\\secrets_guard.py"
    description: "Secrets 守护——CT-SECRETS-001——.env校验+git log扫描+日志脱敏"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\gates\\kiss_enforcer.py"
    description: "KISS 约束执行器——CT-KISS-001——AI产出复杂度检测+bloat check"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_config_manager.py"
    description: "Config 管理器单元测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\config_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\feature_flag.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\gates\\secrets_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\gates\\kiss_enforcer.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_config_manager.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\config\\system_config.yaml"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

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
    reason: "§十九——CT-CONFIG-001/CT-FEATUREFLAG-001/CT-SECRETS-001/CT-KISS-001 完整定义"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 15000
timeout_minutes: 60

acceptance_criteria:
  - "config_manager.py 集中管理 12 系统的 chromadb/sqlite/ce/lsg/fle 共享配置项"
  - "启动时遍历 12 系统 → 校验 config 引用与 CT-CONFIG-001 一致性 → 不一致=启动失败"
  - "feature_flag.py 实现 POST /_admin/toggle/{CT-ID} → runtime_enabled=false → NOT_AVAILABLE+degrade"
  - "feature_flag toggle 变更写入 audit_log（who/when/why）→ persist to db.feature_flags"
  - "secrets_guard.py 检测 API key 硬编码 → CI FAIL + git log scan → 发现历史 key→ALERT+rotate"
  - "kiss_enforcer.py 检测每CT-*实现超过3类/方法>30行/继承>2级 → CI WARN"
  - "Pydantic V2 BaseModel 实现"

rollback_instructions: |
  1. 删除新增的 4 个源码文件
  2. 删除新增的测试文件
  3. 如有创建 db.feature_flags 表 → DROP TABLE feature_flags

depends_on: []
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
