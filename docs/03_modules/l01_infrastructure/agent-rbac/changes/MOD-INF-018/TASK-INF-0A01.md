---
task_id: "TASK-INF-0A01"
source_blueprint: "MOD-INF-018"
source_section: "蓝图 §1.1~§1.5 概述与模块定位"

title: "agent-rbac模块骨架搭建——目录结构、package初始化与配置基线"
description: |
  搭建agent-rbac模块的完整目录骨架、Python package初始化(__init__.py)、pyproject依赖声明、
  pytest配置、skyviva.yaml注册、script_manifest.yaml注册。
  落实§1.1模块身份(module_id=MOD-INF-018、代码落位=src/zephyr/agent_rbac/、运行时平面=Warm memory)、
  §1.2核心职能、§1.3运行场景约束(100%AI开发/多IDE/10+对话/1人+AI/零记忆重启)、
  §1.4痛点、§1.5责任范围的全部骨架文件。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\directory-structure-standard.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\task\\task-card-standard.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"
  - "D:\\ZephyrAlpha\\scripts\\governance\\script_manifest.yaml"
  - "D:\\ZephyrAlpha\\skyviva.yaml"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\__init__.py"
    description: "Package初始化——导出公共API"

  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\pyproject.toml"
    description: "依赖声明——pydantic>=2.0/hmac/cryptography/opentelemetry-api/pyyaml/ed25519"

  - path: "D:\\ZephyrAlpha\\tests\\agent_rbac\\__init__.py"
    description: "测试package初始化"

  - path: "D:\\ZephyrAlpha\\tests\\agent_rbac\\conftest.py"
    description: "pytest fixtures——test agent factory/permission config loader"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\__init__.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\pyproject.toml"
  - "D:\\ZephyrAlpha\\tests\\agent_rbac\\__init__.py"
  - "D:\\ZephyrAlpha\\tests\\agent_rbac\\conftest.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\script_manifest.yaml"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\**\\*.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"
  - "D:\\ZephyrAlpha\\skyviva.yaml"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号格式 TASK-INF-0A01"
  - module_id: "GOV-DOC-002"
    section: "§5.1.2"
    reason: "所有路径必须与路径映射一致——产出物放在src/zephyr/agent_rbac/和tests/agent_rbac/"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "目录结构标准——代码文件在src/zephyr/agent_rbac/，测试在tests/agent_rbac/"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
    reason: "本蓝图——§1确定模块骨架需求"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 8000
timeout_minutes: 30

acceptance_criteria:
  - "src/zephyr/agent_rbac/__init__.py存在，导出agent_rbac包"
  - "package安装后from zephyr.agent_rbac import PermissionGuard可成功导入(骨架)"
  - "pyproject.toml声明pydantic>=2.0/hmac/cryptography/pyyaml/ed25519依赖"
  - "tests/agent_rbac/conftest.py含test_agent fixture工厂函数"
  - "script_manifest.yaml注册本模块所有后续脚本"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\agent_rbac目录
  2. 删除 D:\ZephyrAlpha\tests\agent_rbac目录
  3. script_manifest.yaml中移除agent_rbac相关注册条目
  4. 确认skyviva.yaml未被修改(在forbidden_touch中保护)

depends_on: []
blocked_by: []

status: "done"

tags_fn:
  - "infra"
  - "security"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-018"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---
