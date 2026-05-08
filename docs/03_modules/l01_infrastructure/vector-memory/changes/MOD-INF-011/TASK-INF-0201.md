---
task_id: "TASK-INF-0201"
source_blueprint: "MOD-INF-011"
source_section: "§1 概述 + §7 产出物存放目录"

title: "VMS 模块骨架搭建——产出物目录创建 + 核心入口文件就位"
description: |
  创建 VMS 模块的全部产出物目录结构和核心入口文件。
  §1 定义了 VMS 的三重核心职能（可审计/可自愈/可持续）和代码落位 `src/zephyr/vector_memory/`。
  §7 定义了全部 9 个产出物存放目录的完整绝对路径。
  本项目创建以下目录：
  - `D:\ZephyrAlpha\src\zephyr\vector_memory\`（业务代码根目录——已存在 skeleton `__init__.py`）
  - `D:\ZephyrAlpha\data\vector_db\`（ChromaDB 持久化数据目录）
  - `D:\ZephyrAlpha\data\vector_db\_embedding_cache\`（嵌入缓存持久化）
  - `D:\ZephyrAlpha\data\vector_db\_snapshots\`（ChromaDB snapshot 备份）
  - `D:\ZephyrAlpha\models\bge-m3\`（BGE-M3 ONNX 模型文件目录）
  - `D:\ZephyrAlpha\models\bge-small-zh-v1.5\`（512d 轻量嵌入模型目录）
  更新 `D:\ZephyrAlpha\src\zephyr\vector_memory\__init__.py` docstring：明确声明 8 Collection + 双嵌入维度 + 四 Phase 施工规划。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\directory-structure-standard.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\__init__.py"
  - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_vector_memory.yaml"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\__init__.py"
    description: "更新 docstring——8 Collection + 双嵌入维度(BGE-M3 1024d + bge-small 512d) + Phase 0-4 规划"
  - path: "D:\\ZephyrAlpha\\data\\vector_db\\"
    description: "ChromaDB 持久化目录（如不存在则创建）"
  - path: "D:\\ZephyrAlpha\\data\\vector_db\\_embedding_cache\\"
    description: "嵌入缓存目录"
  - path: "D:\\ZephyrAlpha\\data\\vector_db\\_snapshots\\"
    description: "索引快照备份目录"
  - path: "D:\\ZephyrAlpha\\models\\bge-m3\\"
    description: "BGE-M3 ONNX 模型文件目录"
  - path: "D:\\ZephyrAlpha\\models\\bge-small-zh-v1.5\\"
    description: "bge-small-zh-v1.5 轻量嵌入模型目录"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\__init__.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\**\\*.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\**\\*.md"
  - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_vector_memory.yaml"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "task_id 格式 TASK-INF-XXXX"
  - module_id: "GOV-DOC-002"
    section: "§5.1.2"
    reason: "路径映射——产出物存放必须符合目录结构标准"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径架构合规创建——目录创建前执行合规检查"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
    reason: "§1 VMS 核心职能 + §7 产出物目录定义——所有目录路径真源"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\__init__.py"
    reason: "当前 docstring 状态——需更新为 8 Collection + 双嵌入维度声明"
  - file_path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\directory-structure-standard.md"
    reason: "目录结构标准——验证所有目录路径符合规范"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 5000
timeout_minutes: 15

acceptance_criteria:
  - "D:\\ZephyrAlpha\\data\\vector_db\\ 目录存在且可写"
  - "D:\\ZephyrAlpha\\data\\vector_db\\_embedding_cache\\ 目录存在"
  - "D:\\ZephyrAlpha\\data\\vector_db\\_snapshots\\ 目录存在"
  - "D:\\ZephyrAlpha\\models\\bge-m3\\ 目录存在"
  - "D:\\ZephyrAlpha\\models\\bge-small-zh-v1.5\\ 目录存在"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\__init__.py docstring 明确声明 8 Collection: decisions/code_context/lessons/knowledge/rules/blueprints/session_snapshots/execution_traces"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\__init__.py docstring 明确声明双嵌入维度：BGE-M3 ONNX 1024d + bge-small-zh-v1.5 512d"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\__init__.py docstring 明确声明四 Phase 施工规划"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\data\vector_db\_embedding_cache\ 目录（如为空）
  2. 删除 D:\ZephyrAlpha\data\vector_db\_snapshots\ 目录（如为空）
  3. 恢复 D:\ZephyrAlpha\src\zephyr\vector_memory\__init__.py 到修改前的版本（git checkout 或手动还原）
  4. data\vector_db\ 和 models\ 目录保留（它们本身不造成破坏，仅回滚 __init__.py 即可）

depends_on: []
blocked_by: []
status: "done"

tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-011"

completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
