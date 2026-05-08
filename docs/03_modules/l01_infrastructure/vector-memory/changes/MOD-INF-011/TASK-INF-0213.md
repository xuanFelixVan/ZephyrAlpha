---
task_id: "TASK-INF-0213"
source_blueprint: "MOD-INF-011"
source_section: "§11 后果 (Consequences) + §12.1 施工策略 + §12.2 前置条件"

title: "后果追踪登记板 + 施工策略与前置条件校验"
description: |
  建立 VMS 后果追踪与施工准入校验机制：
  1. 后果追踪登记板（§11 正面/负面后果）：
     - 正面（7 条）：语义检索能力 / 跨 session 记忆 / 统一向量存储 / 双嵌入帕累托最优 / WriteTrace 可审计 / FLE 检索质量闭环 / 索引自愈
     - 负面（4 条）：三依赖部署复杂度增加 / 语义相似≠语义相同不确定性 / BGE-M3 2GB+bge-small 300MB 双模型内存 / 8>5 Collection 复杂度增加 50%
     - 每条后果有 status (expected/observed/mitigated) + observed_at 时间戳 + actual_impact 描述
  2. 施工策略登记（§12.1）：4 Phase 施工模式 / 继承+新建 / 核心风险 ChromaDB+BGE-M3 集成兼容性 / 关键约束不中断 kb/ 现有服务
  3. 前置条件校验器（§12.2）：5 项依赖的运行时检查——ChromaDB 已安装 / bge-small 模型已下载 / BGE-M3 ONNX 模型已下载 / CE 蓝图 §2.1 Build 阶段已定义 / WriteTrace 契约理解
  创建 MOD-INF-011 后果追踪 YAML 文件。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"

downstream_outputs:
  - path: "D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\vector-memory\changes\consequences-tracker.yaml"
    description: "VMS 后果追踪登记板——11 条后果（7正面+4负面）的 status/observations/mitigation 记录"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"
    description: "追加 preconditions_check()——启动时校验 5 项前置条件 + fail-fast 报告缺失项"

allowed_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\consequences-tracker.yaml"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
  - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_vector_memory.yaml"

applicable_rules:
  - module_id: "GOV-DOC-002"
    section: "§5.1.2"
    reason: "consequences-tracker.yaml 路径合规——必须在 vector-memory/ 蓝图目录下"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
    reason: "§11 后果完整列表 + §12.1 施工策略 + §12.2 前置条件——所有登记项真源"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"
    reason: "当前 InProcessVectorMemory 实现——追加 preconditions_check()"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 6000
timeout_minutes: 30

acceptance_criteria:
  - "consequences-tracker.yaml 存在且包含 11 条后果条目——每条含 status/observed_at/actual_impact"
  - "正面后果 status 初始值 observed: false"
  - "负面后果 status 初始值 expected: true + observed: false"
  - "preconditions_check() 返回 PreconditionReport——列出通过/未通过/警告项"
  - "BGE-M3 ONNX 模型不存在时 preconditions_check() 返回 '⚠ NOT_FOUND: models/bge-m3/' + blocking=False（软约束）"
  - "ChromaDB 未安装时 preconditions_check() 返回 '✗ FAIL: ChromaDB not importable' + 阻止启动"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\vector-memory\consequences-tracker.yaml
  2. 从 InProcessVectorMemory.__init__() 中移除 preconditions_check() 调用（不改变模块其他初始化逻辑）
  3. 如果 preconditions_check 阻止了正常启动 → 临时设置 VMS_SKIP_PRECHECKS=1 环境变量绕过

depends_on:
  - "TASK-INF-0208"
blocked_by: []
status: "done"

tags_fn:
  - "infra"
  - "governance"
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
