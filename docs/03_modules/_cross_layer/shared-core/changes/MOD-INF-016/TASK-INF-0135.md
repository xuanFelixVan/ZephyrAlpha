---
task_id: "TASK-INF-0135"
source_blueprint: "MOD-INF-016"
source_section: "蓝图 §2.10 消费者改造"

title: "重构消费者：AutoRuntimeCore + MCPLauncher 改用 Gateway，废弃 start_all.py"
description: "修改 AutoRuntimeCore 中 ollama 启动逻辑：裸 subprocess.Popen → ProcessLifecycleGateway.launch()。修改 MCPLauncher：裸 multiprocessing.Process → ProcessLifecycleGateway.launch_daemon()。同时接管 start_all.py 的 MCP Server 启动职责。start_all.py 标记为 deprecated。"
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\src\\zephyr\\runtime\\auto_runtime_core.py"
  - "D:\\ZephyrAlpha\\scripts\\mcp\\launcher.py"
  - "D:\\ZephyrAlpha\\scripts\\mcp\\start_all.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\infra\\process_lifecycle_gateway.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\runtime\\auto_runtime_core.py"
    description: "修改：_ensure_ollama_running() 改用 Gateway"
  - path: "D:\\ZephyrAlpha\\scripts\\mcp\\launcher.py"
    description: "修改：multiprocessing.Process → Gateway.launch_daemon() + 接管 start_all.py 职责"
  - path: "D:\\ZephyrAlpha\\scripts\\mcp\\start_all.py"
    description: "标记为 deprecated：文件头添加 DEPRECATED 注释 + 文档引用到 launcher.py"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\runtime\\auto_runtime_core.py"
  - "D:\\ZephyrAlpha\\scripts\\mcp\\launcher.py"
  - "D:\\ZephyrAlpha\\scripts\\mcp\\start_all.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\runtime\\lifecycle_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\runtime\\finalizer.py"

applicable_rules:
  - module_id: "RULE-ZERO"
    section: "全篇"
    reason: "修改前逐个锁文件"
  - module_id: "防幻觉#8"
    section: "编辑优先"
    reason: "SearchReplace 精确替换"
  - module_id: "防幻觉#9"
    section: "最小变更"
    reason: "只改进程启动方式，不顺手重构"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\runtime\\auto_runtime_core.py"
    reason: "定位 _ensure_ollama_running() 方法 (L148-L168)"
  - file_path: "D:\\ZephyrAlpha\\scripts\\mcp\\launcher.py"
    reason: "定位 multiprocessing.Process 创建和 _shutdown 清理逻辑"
  - file_path: "D:\\ZephyrAlpha\\scripts\\mcp\\start_all.py"
    reason: "理解现有 SERVER_SCRIPTS 列表，迁移到 launcher.py"
  - file_path: "D:\\ZephyrAlpha\\scripts\\mcp\\stop_all.py"
    reason: "确认 stop_all 不受影响——停止逻辑不变"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1", "M3"]
estimated_tokens: 10000
timeout_minutes: 25

acceptance_criteria:
  - "auto_runtime_core.py: _ensure_ollama_running() 不再使用裸 subprocess.Popen"
  - "auto_runtime_core.py: 使用 ProcessLifecycleGateway.launch('ollama', ['ollama', 'serve'], idle_timeout_s=3600)"
  - "launcher.py: multiprocessing.Process(daemon=True) 改为 Gateway.launch_daemon()"
  - "launcher.py: 接管 start_all.py 的 SERVER_SCRIPTS 列表（含 7 个 MCP Server）"
  - "start_all.py: 文件头添加 # DEPRECATED: 合并到 launcher.py，进程生命周期由 ProcessLifecycleGateway 管理"
  - "所有修改不改变现有 shutdown/logging 行为"

rollback_instructions: "git checkout src/zephyr/runtime/auto_runtime_core.py scripts/mcp/launcher.py scripts/mcp/start_all.py"
depends_on: ["TASK-INF-0133", "TASK-INF-0134"]
blocked_by: []
status: "created"

tags_fn: ["infra", "refactor"]
tags_ly: "_cross_layer"
tags_md: "deepseek"
tags_st: "active"
tags_mo: ["MOD-INF-016", "MOD-INF-013", "MOD-INF-015"]

completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist:
  - "Edit-only: 每个文件 SearchReplace 精确替换，不删+建"
  - "最小变更: 只改进程启动方式，不修改日志/监控/其他逻辑"
  - "shutdown 路径: 确认 Gateway.terminate_all() 在 AutoRuntimeCore.shutdown() 中被调用"
---