---
task_id: "TASK-INF-0136"
source_blueprint: "MOD-INF-016"
source_section: "蓝图 §2.10 Gate 门禁 + 测试"

title: "创建进程入口校验门禁 + 单元测试"
description: "新建 gates/invariants/en_process_lifecycle_gateway.py——AST 扫描检测裸 subprocess.Popen/multiprocessing.Process 调用。CI 阶段阻断绕过 ProcessLifecycleGateway 的代码。同时为 ProcessLifecycleGateway 和增强后的 ProcessPool 编写单元测试。"
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\infra\\process_lifecycle_gateway.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\infra\\process_pool.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\gates\\invariants\\en_001_circular_dependency.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\gates\\invariants\\en_process_lifecycle_gateway.py"
    description: "进程创建入口校验门禁——AST 扫描裸 Popen/Process + CI 阻断"
  - path: "D:\\ZephyrAlpha\\tests\\zephyr\\shared\\infra\\test_process_lifecycle_gateway.py"
    description: "ProcessLifecycleGateway 单元测试——launch/launch_daemon/terminate_all + 异常路径"
  - path: "D:\\ZephyrAlpha\\tests\\zephyr\\shared\\infra\\test_process_pool_enhanced.py"
    description: "ProcessPool 增强测试——idle_timeout 回收 + DaemonRegistry 注册/注销"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\gates\\invariants\\en_process_lifecycle_gateway.py"
  - "D:\\ZephyrAlpha\\tests\\zephyr\\shared\\infra\\test_process_lifecycle_gateway.py"
  - "D:\\ZephyrAlpha\\tests\\zephyr\\shared\\infra\\test_process_pool_enhanced.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\gates\\gate_pipeline.py"

applicable_rules:
  - module_id: "RULE-ZERO"
    section: "全篇"
    reason: "写入前锁文件"
  - module_id: "防幻觉#14"
    section: "新代码必测"
    reason: "新建模块必须有对应 test_ 文件"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\gates\\invariants\\en_001_circular_dependency.py"
    reason: "参考现有 Gate 实现模式（AST 扫描 + CI 集成）"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\gates\\_registry.yaml"
    reason: "确认 Gate 注册格式"
  - file_path: "D:\\ZephyrAlpha\\tests\\zephyr\\shared\\infra\\"
    reason: "确认现有测试目录结构和命名规范"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1", "M3"]
estimated_tokens: 10000
timeout_minutes: 25

acceptance_criteria:
  - "en_process_lifecycle_gateway.py: AST 扫描能检测 subprocess.Popen() 调用（非 from zephyr.shared.infra 的 import）"
  - "en_process_lifecycle_gateway.py: AST 扫描能检测 multiprocessing.Process() 调用"
  - "en_process_lifecycle_gateway.py: 不误报 ProcessLifecycleGateway 自身内部的 subprocess/multiprocessing 使用"
  - "Gate 注册到 _registry.yaml"
  - "test_process_lifecycle_gateway.py: 含 launch/terminate_all/异常路径 至少 5 个测试用例"
  - "test_process_pool_enhanced.py: 含 idle_timeout 回收/DaemonRegistry 集成 至少 3 个测试用例"
  - "python -m pytest tests/zephyr/shared/infra/ -v --timeout=30 → exit 0"

rollback_instructions: "删除新建的 gate 文件和 test 文件，git checkout 修改的 _registry.yaml"
depends_on: ["TASK-INF-0133", "TASK-INF-0134"]
blocked_by: []
status: "created"

tags_fn: ["gate", "test"]
tags_ly: "_cross_layer"
tags_md: "deepseek"
tags_st: "active"
tags_mo: ["MOD-INF-016"]

completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist:
  - "Gate 文件含十字段头部"
  - "测试文件不含十字段头部（测试豁免）"
  - "所有 import 已验证存在"
  - "Gate 注册到 _registry.yaml 的格式与现有 Gate 一致"
---