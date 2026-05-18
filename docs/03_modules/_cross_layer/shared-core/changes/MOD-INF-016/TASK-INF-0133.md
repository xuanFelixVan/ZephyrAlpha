---
task_id: "TASK-INF-0133"
source_blueprint: "MOD-INF-016"
source_section: "蓝图 §2.10 新增子模块 ProcessLifecycleGateway"

title: "创建 ProcessLifecycleGateway 统一进程入口"
description: "新建 shared/infra/process_lifecycle_gateway.py——组合 MCPProcessPool + DaemonRegistry 提供 launch()/launch_daemon()/terminate_all() 三接口。所有 subprocess.Popen/multiprocessing.Process 必须经过此网关。不持有业务逻辑，纯路由+生命周期管理。"
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\data\\asset_index\\DEP-GRAPH-process-lifecycle-001.yaml"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\infra\\process_pool.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\lifecycle\\daemon_registry.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\infra\\process_lifecycle_gateway.py"
    description: "ProcessLifecycleGateway 统一入口——launch()/launch_daemon()/terminate_all()"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\infra\\process_lifecycle_gateway.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\infra\\process_pool.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\lifecycle\\daemon_registry.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\runtime\\auto_runtime_core.py"
  - "D:\\ZephyrAlpha\\scripts\\mcp\\launcher.py"

applicable_rules:
  - module_id: "RULE-ZERO"
    section: "全篇"
    reason: "写入前锁文件"
  - module_id: "RULE-ONE"
    section: "全篇"
    reason: "原子写入模板"
  - module_id: "PS-STD-001"
    section: "§7 十字段"
    reason: "新文件必须包含十字段头部"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\infra\\process_pool.py"
    reason: "理解 MCPProcessPool 的 get_or_create / terminate_all 接口"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\lifecycle\\daemon_registry.py"
    reason: "理解 DaemonRegistry 的 register / unregister 接口"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\lifecycle\\hooks.py"
    reason: "理解 LifecycleAware Protocol 的 on_shutdown 钩子"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1", "M3"]
estimated_tokens: 12000
timeout_minutes: 30

acceptance_criteria:
  - "process_lifecycle_gateway.py 存在且包含十字段头部"
  - "ProcessLifecycleGateway.launch(name, cmd, idle_timeout_s) 方法返回 PooledProcess 或 None"
  - "ProcessLifecycleGateway.launch_daemon(name, target_fn) 方法通过 ProcessPool 启动进程并注册到 DaemonRegistry"
  - "ProcessLifecycleGateway.terminate_all() 调用 ProcessPool.terminate_all() + DaemonRegistry.stop_all()"
  - "Gateway 本身无业务逻辑——不 import ollama / MCP / 任何领域模块"

rollback_instructions: "删除 process_lifecycle_gateway.py 即可恢复"
depends_on: []
blocked_by: []
status: "created"

tags_fn: ["infra"]
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
  - "十字段头部完整包含 BLUEPRINT/MODULE/INVARIANTS/MODIFY-GUARD/CONSUMERS/STABILITY/SAFETY/AI_AUTONOMY/ERROR_CONTRACT/TESTS"
  - "所有 import 已验证存在（Grep 确认）"
  - "无 TODO/.../pass/NotImplementedError"
  - "类型注解完整"
  - "docstring 含 SSoT 声明"
---