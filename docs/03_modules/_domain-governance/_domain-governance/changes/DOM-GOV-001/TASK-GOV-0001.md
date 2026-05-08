---
task_id: "TASK-GOV-0001"
source_blueprint: "DOM-GOV-001"
source_section: "蓝图 §1 域定位 + §2 域内模块清单 + frontmatter submodule_path"

# ===== 内容 =====
title: "创建治理域模块骨架——目录结构 + __init__.py + 模块清单初始化"
description: |
  根据 DOM-GOV-001 §1 域定位和 §2 模块清单，创建治理域的基础骨架：
  1. 在 src/zephyr/governance/ 下创建目录结构和 __init__.py（声明 B 轨归属与架构真源）
  2. 创建 governance/ 目录下各模块的骨架文件（agent_rbac/、agent_spec/、audit_trail/、rollback/、escalation/、drift_detector/、budget_enforcer/、a2a/）
  3. 在 docs/03_modules/_domain-governance/ 下创建域级 index.md（列出 8 个模块的蓝图路径和施工进度）
  4. 确保与 MOD-MASTER-001 的基建域和 SYS-MASTER-001 的系统总蓝图层级关系清晰
priority: "P0"

# ===== 上游：执行前必须读取的文件 =====
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\directory-structure-standard.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"

# ===== 下游：执行后必须产出的文件 =====
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\__init__.py"
    description: "治理域入口——声明 B 轨归属、MOD-MASTER-001 和 SYS-MASTER-001 架构真源"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_rbac\\__init__.py"
    description: "MOD-INF-018 Agent RBAC 骨架"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_spec\\__init__.py"
    description: "MOD-INF-019 Agent Spec 骨架"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\audit_trail\\__init__.py"
    description: "MOD-INF-020 Audit Trail 骨架"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\rollback\\__init__.py"
    description: "MOD-INF-021 Rollback System 骨架"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\escalation\\__init__.py"
    description: "MOD-INF-022 Escalation Protocol 骨架"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\drift_detector\\__init__.py"
    description: "MOD-INF-023 Drift Detector 骨架"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\budget_enforcer\\__init__.py"
    description: "MOD-INF-024 Budget Enforcer 骨架"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\a2a\\__init__.py"
    description: "MOD-INF-025 A2A Protocol 骨架"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\index.md"
    description: "域级模块导航表——8 个模块的蓝图路径和施工进度"

# ===== 范围：允许和禁止触碰的文件 =====
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\**\\__init__.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\index.md"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\*.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\**\\*.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\**\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"

# ===== 规则：必须遵守的治理规则 =====
applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "module_id 命名规范——治理域模块使用 DOM-GOV 前缀"
  - module_id: "GOV-DOC-002"
    section: "§三 + §四"
    reason: "LPC 双轨架构——治理域属于 B 轨横切平台能力；新模块归属决策树"
  - module_id: "ADR-0022"
    section: "§3"
    reason: "B 轨新包创建门槛——BC 边界明确 + ADR + 接口合同 + Phase 路线"

# ===== 上下文：执行前必须装配进上下文的所有文件 =====
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
    reason: "本蓝图 §1~§2——域定位与模块清单"
  - file_path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\directory-structure-standard.md"
    reason: "§5.1.2——路径映射表与防幻觉规则"

# ===== 执行 =====
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 5000
timeout_minutes: 15

# ===== 验收标准 =====
acceptance_criteria:
  - "src/zephyr/governance/__init__.py 存在且含 docstring 声明 B 轨归属 + SYS-MASTER-001/MOD-MASTER-001 架构真源"
  - "src/zephyr/governance/ 下存在 8 个子目录：agent_rbac/、agent_spec/、audit_trail/、rollback/、escalation/、drift_detector/、budget_enforcer/、a2a/"
  - "每个子目录均含 __init__.py，含 docstring 标注对应 module_id"
  - "docs/03_modules/_domain-governance/index.md 存在且列出 8 模块的蓝图路径、module_id、优先级、施工进度"
  - "所有文件 UTF-8 无 BOM + LF 换行"

# ===== 回滚 =====
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\governance\ 整个目录
  2. 删除 D:\ZephyrAlpha\docs\03_modules\_domain-governance\index.md
  3. 确认 D:\ZephyrAlpha\docs\03_modules\_domain-governance\blueprint.md 未被修改

# ===== 依赖 =====
depends_on: []
blocked_by: []

# ===== 状态 =====
status: "done"

# ===== 五轴标签 =====
tags_fn:
  - "security"
  - "observability"
tags_ly: "cross_layer"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "DOM-GOV-001"

# ===== 门禁 =====
completed_gates: []
blocked_gates: {}

# ===== 产物 =====
artifact_paths: []

# ===== 审计 =====
audit_findings: []

# ===== 知识 =====
ke_entries: []

# ===== AI 自治 =====
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
